"""Mide lotes TCP o gRPC con tres nodos locales y conexiones persistentes."""

import argparse
import json
from importlib.metadata import version
import platform
import sys
import time
from concurrent.futures import ThreadPoolExecutor
from contextlib import ExitStack
from itertools import cycle, islice
from pathlib import Path
from queue import Queue
from threading import Barrier

from experiments.exchange_plan import load_plan
from src.common.config import NODES, make_message_id, make_payload, new_run_id
from src.common.event_log import CSVLogWriter, EventLogger
from src.common.lamport import LamportClock
from src.sockets.client import TCPClient
from src.sockets.server import TCPServer


class BatchLogger(EventLogger):
    """Asocia cada evento con el lote del ID, incluso si llega tras un timeout."""

    def _put(self, kind, **fields):
        if "message_id" in fields:
            fields["run_id"] = fields["message_id"].split(":", 1)[0]
        super()._put(kind, **fields)


def run_batch(clients, queue, plan, size, mode, warmup, mechanism):
    run_id = new_run_id()
    payload = make_payload(size)
    exchanges = [
        (sequence, sender, receiver)
        for sequence, (_, sender, receiver) in enumerate(islice(cycle(plan), 100), 1)
    ]

    def exchange(item):
        sequence, sender, receiver = item
        return clients[sender].exchange(
            receiver, make_message_id(run_id, sender, sequence),
            payload, mode=mode, warmup=warmup,
        ).status == "ok"

    if mode == "concurrent":
        gate = Barrier(len(clients) + 1)

        def run_client(sender):
            gate.wait()
            return sum(exchange(item) for item in exchanges if item[1] == sender)

        with ThreadPoolExecutor(max_workers=len(clients)) as pool:
            tasks = [pool.submit(run_client, sender) for sender in clients]
            start = time.perf_counter()
            gate.wait()
            completed = sum(task.result() for task in tasks)
            elapsed = time.perf_counter() - start
    else:
        start = time.perf_counter()
        completed = sum(map(exchange, exchanges))
        elapsed = time.perf_counter() - start

    failed = len(exchanges) - completed
    logger = EventLogger(queue, run_id, mechanism, next(iter(clients)))
    logger.run(size, mode, warmup, len(clients), len(exchanges), completed, failed, elapsed)
    print(f"{run_id} {size} B {mode} warmup={int(warmup)}: {completed}/{len(exchanges)}")
    return failed


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--mechanism", choices=("sockets", "grpc"), default="sockets")
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--plan", type=Path, default=Path(__file__).with_name("plan_intercambios.csv"))
    parser.add_argument("--repetitions", type=int, default=5)
    parser.add_argument("--timeout", type=float, default=5.0)
    args = parser.parse_args()
    if args.repetitions < 1 or not 0 < args.timeout <= 60:
        parser.error("Se requiere al menos una repetición y un timeout entre 0 y 60 s.")
    plan = load_plan(args.plan)
    if len(plan) != 20 or {sender for _, sender, _ in plan} != set(NODES):
        parser.error("El plan debe tener 20 intercambios y los tres emisores.")

    server_type, client_type = TCPServer, TCPClient
    server_options = {"timeout": max(30, args.timeout * 2)}
    if args.mechanism == "grpc":
        from src.grpc.client_grpc import GRPCClient
        from src.grpc.server_grpc import GRPCServer

        server_type, client_type = GRPCServer, GRPCClient
        server_options = {}

    queue = Queue()
    failure_count = 0
    with CSVLogWriter(queue, args.output), ExitStack() as stack:
        clients = {}
        for node in NODES:
            clock = LamportClock()
            logger = BatchLogger(queue, "initial", args.mechanism, node)
            stack.enter_context(server_type(node, clock, logger, **server_options))
            clients[node] = stack.enter_context(client_type(node, clock, logger, timeout=args.timeout))
        for node, client in clients.items():
            for peer in NODES:
                if peer != node:
                    client.prepare(peer)
        for size in (100, 10240):
            for mode in ("sequential", "concurrent"):
                for repetition in range(args.repetitions + 1):
                    failure_count += run_batch(
                        clients, queue, plan, size, mode, repetition == 0, args.mechanism,
                    )

    metadata = {
        "python": sys.version,
        "platform": platform.platform(),
        "mechanism": args.mechanism,
        "deployment": "tres nodos, hilos en un proceso local",
        "dependencies": (
            {name: version(name) for name in ("grpcio", "grpcio-tools", "protobuf")}
            if args.mechanism == "grpc" else {}
        ),
        "timeout_s": args.timeout,
        "repetitions": args.repetitions,
        "plan": str(args.plan),
        "connections": "persistentes, abiertas antes del primer lote",
        "concurrent_attempts": "100 en total, repartidos según los emisores del plan",
        "elapsed_s": "tiempo de pared del lote, incluida la coordinación local",
    }
    (args.output / "environment.json").write_text(
        json.dumps(metadata, ensure_ascii=False, indent=2) + "\n", encoding="utf-8",
    )
    return int(bool(failure_count))


if __name__ == "__main__":
    raise SystemExit(main())
