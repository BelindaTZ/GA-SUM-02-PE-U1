"""Mide lotes TCP o gRPC con tres nodos locales y conexiones persistentes."""

import argparse
import json
from importlib.metadata import version
import multiprocessing
import os
import platform
import sys
import time
from contextlib import ExitStack
from itertools import cycle, islice
from pathlib import Path

from experiments.exchange_plan import load_plan
from scripts.demo_tcp import receive
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


def node_worker(node, mechanism, queue, pipe, gate, timeout):
    with pipe, ExitStack() as stack:
        if mechanism == "grpc":
            from src.grpc.client_grpc import GRPCClient
            from src.grpc.server_grpc import GRPCServer

            server_type, client_type = GRPCServer, GRPCClient
            server_options = {}
        else:
            server_type, client_type = TCPServer, TCPClient
            server_options = {"timeout": max(30, timeout * 2)}

        clock = LamportClock()
        logger = BatchLogger(queue, "initial", mechanism, node)
        stack.enter_context(server_type(node, clock, logger, **server_options))
        client = stack.enter_context(client_type(node, clock, logger, timeout=timeout))
        pipe.send({"ready": node, "pid": os.getpid(), "port": NODES[node].address[1]})
        while True:
            command = pipe.recv()
            action = command["action"]
            if action == "stop":
                return
            if action == "prepare":
                for peer in NODES:
                    if peer != node:
                        client.prepare(peer)
                pipe.send({"prepared": node})
                continue

            payload = make_payload(command["size"])
            mode = command["mode"]
            if mode == "concurrent":
                gate.wait(timeout=30)
            completed = 0
            for sequence, peer in command["exchanges"]:
                result = client.exchange(
                    peer, make_message_id(command["run_id"], node, sequence),
                    payload, mode=mode, warmup=command["warmup"],
                )
                completed += result.status == "ok"
            pipe.send({"completed": completed})


def stop_node(process, pipe):
    with pipe:
        if process.is_alive():
            try:
                pipe.send({"action": "stop"})
            except (BrokenPipeError, OSError):
                pass
        process.join(timeout=10)
        if process.is_alive():
            process.terminate()
            process.join()
            raise RuntimeError(f"{process.name} no cerró normalmente.")
        if process.exitcode != 0:
            raise RuntimeError(f"{process.name} terminó con código {process.exitcode}.")


def run_batch(pipes, gate, queue, plan, size, mode, warmup, mechanism, timeout):
    run_id = new_run_id()
    command = {"action": "exchange", "run_id": run_id, "size": size,
               "mode": mode, "warmup": warmup}
    exchanges = [
        (sequence, sender, receiver)
        for sequence, (_, sender, receiver) in enumerate(islice(cycle(plan), 100), 1)
    ]

    if mode == "concurrent":
        for sender, pipe in pipes.items():
            rows = [(sequence, receiver) for sequence, node, receiver in exchanges if node == sender]
            pipe.send({**command, "exchanges": rows})
        start = time.perf_counter()
        gate.wait(timeout=30)
        completed = sum(receive(pipe, 100 * timeout + 5)["completed"] for pipe in pipes.values())
    else:
        completed = 0
        start = time.perf_counter()
        for sequence, sender, receiver in exchanges:
            pipe = pipes[sender]
            pipe.send({**command, "exchanges": [(sequence, receiver)]})
            completed += receive(pipe, timeout + 5)["completed"]
    elapsed = time.perf_counter() - start

    failed = len(exchanges) - completed
    logger = EventLogger(queue, run_id, mechanism, next(iter(pipes)))
    logger.run(size, mode, warmup, len(pipes), len(exchanges), completed, failed, elapsed)
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

    ctx = multiprocessing.get_context("spawn")
    queue = ctx.Queue()
    gate = ctx.Barrier(len(NODES) + 1)
    failure_count = 0
    try:
        with CSVLogWriter(queue, args.output), ExitStack() as stack:
            pipes = {}
            for node in NODES:
                parent, child = ctx.Pipe()
                with child:
                    process = ctx.Process(
                        target=node_worker, name=node,
                        args=(node, args.mechanism, queue, child, gate, args.timeout),
                    )
                    try:
                        process.start()
                    except BaseException:
                        parent.close()
                        raise
                stack.callback(stop_node, process, parent)
                pipes[node] = parent
            nodes = [receive(pipe, 30) for pipe in pipes.values()]
            for node in nodes:
                print(f"{node['ready']} en localhost:{node['port']} (PID {node['pid']})")
            for pipe in pipes.values():
                pipe.send({"action": "prepare"})
            for pipe in pipes.values():
                receive(pipe, 30)
            for size in (100, 10240):
                for mode in ("sequential", "concurrent"):
                    for repetition in range(args.repetitions + 1):
                        failure_count += run_batch(
                            pipes, gate, queue, plan, size, mode, repetition == 0,
                            args.mechanism, args.timeout,
                        )
    finally:
        queue.close()
        queue.join_thread()

    metadata = {
        "python": sys.version,
        "platform": platform.platform(),
        "mechanism": args.mechanism,
        "deployment": "tres procesos independientes en localhost",
        "nodes": nodes,
        "dependencies": (
            {name: version(name) for name in ("grpcio", "grpcio-tools", "protobuf")}
            if args.mechanism == "grpc" else {}
        ),
        "timeout_s": args.timeout,
        "repetitions": args.repetitions,
        "plan": os.path.relpath(args.plan),
        "connections": "persistentes, abiertas antes del primer lote",
        "concurrent_attempts": "100 en total, repartidos según los emisores del plan",
        "elapsed_s": "tiempo de pared del lote, incluida la coordinación local por Pipe",
    }
    (args.output / "environment.json").write_text(
        json.dumps(metadata, ensure_ascii=False, indent=2) + "\n", encoding="utf-8",
    )
    return int(bool(failure_count))


if __name__ == "__main__":
    raise SystemExit(main())
