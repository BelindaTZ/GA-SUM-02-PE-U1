"""Validación del transporte; salidas temporales separadas de las corridas reales."""

import csv
import logging
import queue
import socket
import struct
import tempfile
import threading
import time
import unittest
from concurrent.futures import ThreadPoolExecutor
from contextlib import ExitStack, contextmanager
from pathlib import Path

from src.common.config import NODES, make_payload
from src.common.event_log import CSVLogWriter, EventLogger
from src.common.lamport import LamportClock
from src.sockets.client import TCPClient
from src.sockets.protocol import MAX_FRAME_BYTES, ProtocolError, encode_frame, receive_frame, send_frame
from src.sockets.server import TCPServer


def message(identifier="test-1", payload="hola áé\n🙂"):
    return {"message_id": identifier, "sender": "nodo-A", "timestamp": 1, "message": payload}


@contextmanager
def connected_pair():
    left, right = socket.socketpair()
    try:
        yield left, right
    finally:
        left.close()
        right.close()


class ProtocolTests(unittest.TestCase):
    def test_fragmented_frame_and_unicode(self):
        expected = message(payload=make_payload(10240) + "á🙂\n")
        frame = encode_frame(expected)
        with connected_pair() as (left, right):
            def produce():
                for index in range(0, len(frame), 7):
                    left.sendall(frame[index:index + 7])
            worker = threading.Thread(target=produce)
            worker.start()
            actual = receive_frame(right, time.perf_counter() + 5)
            worker.join()
            self.assertEqual(actual, expected)

    def test_coalesced_frames_remain_separate(self):
        with connected_pair() as (left, right):
            left.sendall(encode_frame(message("one")) + encode_frame(message("two")))
            self.assertEqual(receive_frame(right, time.perf_counter() + 1)["message_id"], "one")
            self.assertEqual(receive_frame(right, time.perf_counter() + 1)["message_id"], "two")
            left.shutdown(socket.SHUT_WR)
            self.assertIsNone(receive_frame(right, time.perf_counter() + 1))

    def test_invalid_and_truncated_frames(self):
        invalid = [struct.pack("!I", 0), struct.pack("!I", MAX_FRAME_BYTES + 1),
                   b"\x00\x00", struct.pack("!I", 3) + b"{x}",
                   struct.pack("!I", 5) + b"{}", struct.pack("!I", 1) + b"\xff"]
        for frame in invalid:
            with self.subTest(frame=frame), connected_pair() as (left, right):
                left.sendall(frame)
                left.shutdown(socket.SHUT_WR)
                with self.assertRaises(ProtocolError):
                    receive_frame(right, time.perf_counter() + 1)

    def test_contract_and_duplicate_fields(self):
        for update in ({"timestamp": True}, {"timestamp": -1}, {"timestamp": 2**63},
                       {"sender": "unknown"}, {"message_id": ""}, {"message": 1}):
            with self.subTest(update=update), self.assertRaises(ProtocolError):
                encode_frame({**message(), **update})
        body = b'{"message_id":"one","message_id":"two","sender":"nodo-A","timestamp":1,"message":"x"}'
        with connected_pair() as (left, right):
            left.sendall(struct.pack("!I", len(body)) + body)
            with self.assertRaises(ProtocolError):
                receive_frame(right, time.perf_counter() + 1)

    def test_deadline_expires(self):
        with connected_pair() as (left, right):
            with self.assertRaises(TimeoutError):
                receive_frame(right, time.perf_counter() + 0.03)


class TransportTests(unittest.TestCase):
    def test_three_nodes_twenty_exchanges_and_reused_connections(self):
        messages = queue.Queue()
        with tempfile.TemporaryDirectory() as directory:
            with CSVLogWriter(messages, Path(directory)), ExitStack() as stack:
                clocks = {node: LamportClock() for node in NODES}
                loggers = {node: EventLogger(messages, "tcp-integration", "sockets", node) for node in NODES}
                servers = {node: stack.enter_context(TCPServer(node, clocks[node], loggers[node], address=("127.0.0.1", 0))) for node in NODES}
                addresses = {node: server.address for node, server in servers.items()}
                clients = {node: stack.enter_context(TCPClient(node, clocks[node], loggers[node], addresses=addresses)) for node in NODES}
                nodes = list(NODES)
                for sequence in range(20):
                    sender, peer = nodes[sequence % 3], nodes[(sequence + 1) % 3]
                    clients[sender].prepare(peer)
                    connection = clients[sender]._connections[peer]
                    result = clients[sender].exchange(peer, f"integration-{sequence}", make_payload(100 if sequence % 2 else 10240))
                    self.assertEqual(result.status, "ok", result.error)
                    self.assertGreaterEqual(result.rtt_ms, 0)
                    self.assertEqual(result.ack["message_id"], f"integration-{sequence}")
                    self.assertIs(clients[sender]._connections[peer], connection)
            with (Path(directory) / "events_sockets.csv").open(encoding="utf-8", newline="") as stream:
                events = list(csv.DictReader(stream))
            self.assertEqual(len(events), 80)
            for sequence in range(20):
                rows = [r for r in events if r["message_id"] == f"integration-{sequence}"]
                for kind in ("request", "ack"):
                    sent = next(r for r in rows if r["message_kind"] == kind and r["event_type"] == "send")
                    received = next(r for r in rows if r["message_kind"] == kind and r["event_type"] == "receive")
                    self.assertGreater(int(received["lamport"]), int(sent["lamport"]))

    def test_concurrent_clients_share_server_clock(self):
        messages = queue.Queue()
        with ExitStack() as stack:
            server_clock = LamportClock()
            server_logger = EventLogger(messages, "concurrent", "sockets", "nodo-B")
            server = stack.enter_context(TCPServer("nodo-B", server_clock, server_logger, address=("127.0.0.1", 0)))
            clients = [stack.enter_context(TCPClient(node, LamportClock(), EventLogger(messages, "concurrent", "sockets", node), addresses={"nodo-B": server.address})) for node in ("nodo-A", "nodo-C")]
            def send(index):
                return clients[index % 2].exchange("nodo-B", f"concurrent-{index}", "prueba")
            with ThreadPoolExecutor(max_workers=6) as pool:
                results = list(pool.map(send, range(30)))
            self.assertTrue(all(r.status == "ok" for r in results))
        events = []
        while not messages.empty():
            kind, row = messages.get_nowait()
            if kind == "events" and row["node"] == "nodo-B":
                events.append(row["lamport"])
        self.assertEqual(len(events), 60)
        self.assertEqual(events, sorted(set(events)))

    def _bad_peer(self, behavior):
        messages = queue.Queue()
        listener = socket.socket()
        listener.bind(("127.0.0.1", 0))
        listener.listen()
        def serve():
            with listener:
                connection, _ = listener.accept()
                with connection:
                    request = receive_frame(connection, time.perf_counter() + 2)
                    if behavior == "timeout":
                        time.sleep(0.15)
                    else:
                        ack = {**request, "sender": "nodo-B", "timestamp": 99, "message": "ACK"}
                        ack["message_id"] = "wrong-id"
                        send_frame(connection, ack, time.perf_counter() + 1)
        address = listener.getsockname()
        worker = threading.Thread(target=serve)
        worker.start()
        logger = EventLogger(messages, "errors", "sockets", "nodo-A")
        try:
            with TCPClient("nodo-A", LamportClock(), logger, timeout=0.05, addresses={"nodo-B": address}) as client:
                result = client.exchange("nodo-B", "error-request", "payload")
                self.assertEqual(result.status, behavior)
                self.assertIsNone(result.rtt_ms)
                self.assertNotIn("nodo-B", client._connections)
            rows = []
            while not messages.empty():
                rows.append(messages.get_nowait())
            self.assertEqual([r[1]["event_type"] for r in rows if r[0] == "events"], ["send"])
            self.assertIsNone(next(r[1]["rtt_ms"] for r in rows if r[0] == "latency"))
        finally:
            worker.join(timeout=3)
            self.assertFalse(worker.is_alive())

    def test_timeout_leaves_empty_rtt(self):
        self._bad_peer("timeout")

    def test_wrong_ack_is_rejected(self):
        self._bad_peer("error")

    def test_bad_connection_does_not_stop_server(self):
        messages = queue.Queue()
        logger = EventLogger(messages, "recovery", "sockets", "nodo-B")
        with TCPServer("nodo-B", LamportClock(), logger, address=("127.0.0.1", 0)) as server:
            with self.assertLogs("src.sockets.server", level=logging.WARNING):
                with socket.create_connection(server.address, timeout=1) as connection:
                    connection.sendall(struct.pack("!I", 0))
                    self.assertEqual(connection.recv(1), b"")
            client_logger = EventLogger(messages, "recovery", "sockets", "nodo-A")
            with TCPClient("nodo-A", LamportClock(), client_logger, addresses={"nodo-B": server.address}) as client:
                self.assertEqual(client.exchange("nodo-B", "valid", "correcto").status, "ok")


if __name__ == "__main__":
    unittest.main()
