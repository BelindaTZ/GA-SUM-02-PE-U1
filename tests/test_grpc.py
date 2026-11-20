"""Pruebas del cliente; no generan datos experimentales."""

from concurrent.futures import ThreadPoolExecutor
from queue import Queue
import time
import unittest

import grpc

from src.common.event_log import EventLogger
from src.common.lamport import LamportClock
from src.grpc.client_grpc import GRPCClient
from src.grpc.generated import messaging_pb2 as pb
from src.grpc.generated import messaging_pb2_grpc as rpc


class ClientTests(unittest.TestCase):
    def setUp(self):
        self.queue = Queue()
        self.clock = LamportClock()
        self.server_clock = LamportClock()
        self.logger = EventLogger(self.queue, "test", "grpc", "nodo-A")
        self.server_logger = EventLogger(self.queue, "test", "grpc", "nodo-B")
        self.payloads = []
        self.handler = self.reply
        owner = self

        class Service(rpc.MessagingServiceServicer):
            def EnviarMensaje(self, request, context):
                return owner.handler(request, context)

        self.executor = ThreadPoolExecutor(max_workers=4)
        self.server = grpc.server(self.executor)
        rpc.add_MessagingServiceServicer_to_server(Service(), self.server)
        port = self.server.add_insecure_port("127.0.0.1:0")
        self.server.start()
        self.client = GRPCClient("nodo-A", self.clock, self.logger,
                                 addresses={"nodo-B": f"127.0.0.1:{port}"})

    def tearDown(self):
        self.client.close()
        self.server.stop(0).wait()
        self.executor.shutdown(wait=True)

    def reply(self, request, context):
        self.payloads.append(request.message)
        self.server_clock.receive_event(request.timestamp, self.server_logger,
                                        request.message_id, "nodo-A")
        timestamp = self.server_clock.send_event(self.server_logger, request.message_id,
                                                 "nodo-A", "ack")
        return pb.Acuse(message_id=request.message_id, sender="nodo-B", timestamp=timestamp, message="ACK")

    def records(self, kind):
        rows = []
        while not self.queue.empty():
            current, row = self.queue.get_nowait()
            if current == kind:
                rows.append(row)
        return rows

    def test_reuses_channel_and_records_clock(self):
        self.client.prepare("nodo-B")
        channel = self.client._channels["nodo-B"]
        a = self.client.exchange("nodo-B", "test:nodo-A:1", "hola")
        b = self.client.exchange("nodo-B", "test:nodo-A:2", "otra")
        self.assertIs(channel, self.client._channels["nodo-B"])
        self.assertEqual((a.status, b.status), ("ok", "ok"))
        self.assertEqual((a.ack["timestamp"], b.ack["timestamp"], self.clock.value), (3, 7, 8))
        self.assertGreaterEqual(a.rtt_ms, 0)
        events = self.records("events")
        self.assertEqual(len(events), 8)

    def test_payload_sizes_and_utf8(self):
        for sequence, payload in enumerate(["á" * 50, "x" * 10240], 1):
            result = self.client.exchange("nodo-B", f"test:nodo-A:{sequence}", payload, warmup=True)
            self.assertEqual(result.status, "ok")
            self.assertEqual(self.payloads[-1], payload)
        rows = self.records("latency")
        self.assertEqual([row["payload_bytes"] for row in rows], [100, 10240])
        self.assertTrue(all(row["warmup"] == 1 for row in rows))

    def test_invalid_arguments_do_not_change_clock(self):
        for peer, message_id, payload in [("nodo-A", "id", "x"),
                                          ("nodo-B", "", "x"),
                                          ("nodo-B", "id", b"x")]:
            with self.assertRaises(ValueError):
                self.client.exchange(peer, message_id, payload)
        self.assertEqual(self.clock.value, 0)
        self.assertTrue(self.queue.empty())
        with self.assertRaises(ValueError):
            GRPCClient("nodo-A", self.clock, self.logger, timeout=float("nan"))

    def test_wrong_ack_is_error_with_empty_rtt(self):
        self.handler = lambda request, context: pb.Acuse(
            message_id="otro", sender="nodo-B", timestamp=3, message="ACK")
        result = self.client.exchange("nodo-B", "test:nodo-A:1", "x")
        self.assertEqual(result.status, "error")
        self.assertIsNone(result.rtt_ms)
        self.assertEqual(self.clock.value, 1)
        self.assertIsNone(self.records("latency")[0]["rtt_ms"])

    def test_deadline_is_timeout_with_empty_rtt(self):
        self.client.prepare("nodo-B")
        self.client.timeout = 0.05

        def slow(request, context):
            time.sleep(0.2)
            return pb.Acuse(message_id=request.message_id, sender="nodo-B", timestamp=3, message="ACK")

        self.handler = slow
        result = self.client.exchange("nodo-B", "test:nodo-A:1", "x")
        self.assertEqual(result.status, "timeout")
        self.assertIsNone(result.rtt_ms)
        self.assertIsNone(self.records("latency")[0]["rtt_ms"])

    def test_close_and_measure_false(self):
        result = self.client.exchange("nodo-B", "test:nodo-A:1", "x", measure=False)
        self.assertEqual(result.status, "ok")
        self.assertEqual(self.records("latency"), [])
        self.client.close()
        self.assertEqual(self.client._channels, {})
        with self.assertRaises(RuntimeError):
            self.client.prepare("nodo-B")
        with self.assertRaises(RuntimeError):
            self.client.exchange("nodo-B", "test:nodo-A:2", "x")


if __name__ == "__main__":
    unittest.main()
