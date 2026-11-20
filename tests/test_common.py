"""Pruebas de software; sus datos no son evidencia experimental."""

import csv
import multiprocessing
import queue
import tempfile
import unittest
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
from pathlib import Path

from src.common.config import NODES, get_node, make_message_id, make_payload, new_run_id
from src.common.event_log import CSVLogWriter, EVENT_COLUMNS, LATENCY_COLUMNS, RUN_COLUMNS, EventLogger
from src.common.lamport import LamportClock


def produce_events(shared_queue, node, peer):
    clock = LamportClock()
    logger = EventLogger(shared_queue, "test-process", "grpc", node)
    for sequence in range(1, 31):
        clock.send_event(logger, make_message_id("test-process", node, sequence), peer)


def read_rows(directory, name):
    with (Path(directory) / name).open(encoding="utf-8", newline="") as stream:
        reader = csv.DictReader(stream)
        return reader.fieldnames, list(reader)


class ConfigTests(unittest.TestCase):
    def test_addresses_and_payload_bytes(self):
        self.assertEqual([n.port for n in NODES.values()], [5000, 5001, 5002])
        self.assertEqual(get_node("nodo-B").target, "127.0.0.1:5001")
        for size in (100, 10240):
            self.assertEqual(len(make_payload(size).encode("utf-8")), size)

    def test_identifiers_unique_between_clients_and_runs(self):
        run = new_run_id()
        ids = {make_message_id(run, n, s) for n in NODES for s in range(1, 101)}
        self.assertEqual(len(ids), 300)
        self.assertNotEqual(run, new_run_id())

    def test_invalid_configuration(self):
        for value in (0, -1, True, 1.5):
            with self.assertRaises(ValueError):
                make_payload(value)
        with self.assertRaises(ValueError):
            get_node("otro")
        with self.assertRaises(ValueError):
            make_message_id("", "nodo-A", 1)


class ClockTests(unittest.TestCase):
    def test_rules_and_invalid_timestamps(self):
        clock = LamportClock()
        self.assertEqual(clock.tick(), 1)
        self.assertEqual(clock.update(8), 9)
        self.assertEqual(clock.update(2), 10)
        for value in (-1, True, 1.5, "3"):
            with self.assertRaises(ValueError):
                clock.update(value)
        self.assertEqual(clock.value, 10)

    def test_thread_updates_are_not_lost(self):
        clock = LamportClock()
        with ThreadPoolExecutor(max_workers=8) as pool:
            values = list(pool.map(lambda _: clock.tick(), range(2000)))
        self.assertEqual(clock.value, 2000)
        self.assertEqual(set(values), set(range(1, 2001)))

    def test_event_emission_preserves_per_node_order(self):
        messages = queue.Queue()
        clock = LamportClock()
        logger = EventLogger(messages, "test-threads", "sockets", "nodo-A")
        with ThreadPoolExecutor(max_workers=8) as pool:
            list(pool.map(lambda s: clock.send_event(logger, f"test:{s}", "nodo-B"), range(500)))
        recorded = [messages.get_nowait()[1]["lamport"] for _ in range(500)]
        self.assertEqual(recorded, list(range(1, 501)))


class LogTests(unittest.TestCase):
    def test_request_ack_and_csv_schemas(self):
        messages = queue.Queue()
        a = EventLogger(messages, "test-exchange", "sockets", "nodo-A")
        b = EventLogger(messages, "test-exchange", "sockets", "nodo-B")
        ca, cb = LamportClock(), LamportClock()
        with tempfile.TemporaryDirectory() as directory:
            with CSVLogWriter(messages, Path(directory)):
                sent = ca.send_event(a, "request-1", "nodo-B")
                received = cb.receive_event(sent, b, "request-1", "nodo-A")
                ack = cb.send_event(b, "request-1", "nodo-A", "ack")
                done = ca.receive_event(ack, a, "request-1", "nodo-B", "ack")
                a.latency("request-1", 100, "sequential", False, 1.25)
                a.latency("request-2", 100, "sequential", False, status="timeout")
                a.run(100, "sequential", False, 1, 2, 1, 1, 0.5)
            self.assertGreater(received, sent)
            self.assertGreater(done, ack)
            headers, events = read_rows(directory, "events_sockets.csv")
            self.assertEqual(headers, list(EVENT_COLUMNS))
            self.assertEqual(len(events), 4)
            self.assertEqual([r["message_kind"] for r in events], ["request", "request", "ack", "ack"])
            self.assertTrue(all(datetime.fromisoformat(r["physical_time"]).tzinfo for r in events))
            headers, latencies = read_rows(directory, "latency_sockets.csv")
            self.assertEqual(headers, list(LATENCY_COLUMNS))
            self.assertEqual(latencies[0]["rtt_ms"], "1.25")
            self.assertEqual(latencies[1]["rtt_ms"], "")
            headers, runs = read_rows(directory, "runs.csv")
            self.assertEqual(headers, list(RUN_COLUMNS))
            self.assertEqual(runs[0]["completed"], "1")
            self.assertFalse((Path(directory) / "events_grpc.csv").exists())

    def test_rejects_bad_measurements(self):
        logger = EventLogger(queue.Queue(), "test", "grpc", "nodo-A")
        for rtt in (-1, float("nan"), float("inf"), None):
            with self.assertRaises(ValueError):
                logger.latency("x", 100, "sequential", 0, rtt)
        with self.assertRaises(ValueError):
            logger.latency("x", 100, "concurrent", 0, 2, "error")
        with self.assertRaises(ValueError):
            logger.run(100, "concurrent", 0, 3, 100, 99, 0, 1)
        with self.assertRaises(ValueError):
            logger.run(100, "sequential", 0, 1, 100, 100, 0, 0)
        clock = LamportClock()
        with self.assertRaises(ValueError):
            clock.send_event(logger, "x", "nodo-A")
        self.assertEqual(clock.value, 0)

    def test_existing_evidence_is_not_overwritten(self):
        with tempfile.TemporaryDirectory() as directory:
            existing = Path(directory) / "runs.csv"
            existing.write_text("original", encoding="utf-8")
            with self.assertRaises(FileExistsError):
                with CSVLogWriter(queue.Queue(), Path(directory)):
                    pass
            self.assertEqual(existing.read_text(encoding="utf-8"), "original")

    def test_writer_error_is_reported(self):
        messages = queue.Queue()
        with tempfile.TemporaryDirectory() as directory:
            with self.assertRaises(RuntimeError):
                with CSVLogWriter(messages, Path(directory)):
                    messages.put(("events", {"bad_column": 1}))

    def test_spawned_processes_share_one_writer(self):
        ctx = multiprocessing.get_context("spawn")
        messages = ctx.Queue()
        processes = []
        try:
            with tempfile.TemporaryDirectory() as directory:
                with CSVLogWriter(messages, Path(directory)):
                    for node, peer in (("nodo-A", "nodo-B"), ("nodo-B", "nodo-C"), ("nodo-C", "nodo-A")):
                        process = ctx.Process(target=produce_events, args=(messages, node, peer))
                        process.start()
                        processes.append(process)
                    for process in processes:
                        process.join(timeout=15)
                        self.assertFalse(process.is_alive())
                        self.assertEqual(process.exitcode, 0)
                _, events = read_rows(directory, "events_grpc.csv")
                self.assertEqual(len(events), 90)
                self.assertEqual(len({r["message_id"] for r in events}), 90)
                for node in NODES:
                    clocks = [int(r["lamport"]) for r in events if r["node"] == node]
                    self.assertEqual(clocks, list(range(1, 31)))
        finally:
            for process in processes:
                if process.is_alive():
                    process.terminate()
                    process.join()
            messages.close()
            messages.join_thread()


if __name__ == "__main__":
    unittest.main()
