"""Validación TCP con tres procesos reales; no sustituye el protocolo final.

Desde la raíz: python -m scripts.demo_tcp --messages 20 --payload-bytes 100
"""

import argparse
import json
import multiprocessing
import platform
import sys
import time
import traceback
from pathlib import Path

from src.common.config import DATA_DIR, NODES, make_message_id, make_payload, new_run_id
from src.common.event_log import CSVLogWriter, EventLogger
from src.common.lamport import LamportClock
from src.sockets.client import TCPClient
from src.sockets.server import TCPServer


def node_worker(node, run_id, shared_queue, pipe, timeout):
    try:
        clock = LamportClock()
        logger = EventLogger(shared_queue, run_id, "sockets", node)
        with TCPServer(node, clock, logger, timeout=max(30, timeout * 2)):
            with TCPClient(node, clock, logger, timeout=timeout) as client:
                pipe.send({"ready": node, "address": list(NODES[node].address)})
                while True:
                    command = pipe.recv()
                    if command["action"] == "stop":
                        break
                    if command["action"] == "prepare":
                        for peer in NODES:
                            if peer != node:
                                client.prepare(peer)
                        pipe.send({"prepared": node})
                    elif command["action"] == "send":
                        result = client.exchange(command["peer"], command["message_id"],
                                                 make_payload(command["payload_bytes"]))
                        pipe.send({"message_id": result.message_id, "status": result.status,
                                   "rtt_ms": result.rtt_ms, "error": result.error})
    except Exception:
        try:
            pipe.send({"fatal": traceback.format_exc()})
        except (BrokenPipeError, OSError):
            pass
    finally:
        pipe.close()


def receive(pipe, timeout):
    if not pipe.poll(timeout):
        raise TimeoutError("El proceso de nodo no respondió al coordinador.")
    result = pipe.recv()
    if "fatal" in result:
        raise RuntimeError(result["fatal"])
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--messages", type=int, default=20)
    parser.add_argument("--payload-bytes", type=int, choices=(100, 10240), default=100)
    parser.add_argument("--timeout", type=float, default=5.0)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    if args.messages < 1:
        parser.error("--messages debe ser positivo.")
    if not 0 < args.timeout <= 60:
        parser.error("--timeout debe ser positivo y como máximo 60 segundos.")
    run_id = new_run_id()
    directory = args.output or DATA_DIR / f"tcp_validacion_{run_id}"
    ctx = multiprocessing.get_context("spawn")
    shared_queue = ctx.Queue()
    processes, pipes = [], {}
    failed = 0
    try:
        with CSVLogWriter(shared_queue, directory):
            try:
                for node in NODES:
                    parent, child = ctx.Pipe()
                    process = ctx.Process(target=node_worker, args=(node, run_id, shared_queue, child, args.timeout), name=node)
                    process.start()
                    child.close()
                    processes.append(process)
                    pipes[node] = parent
                for node, pipe in pipes.items():
                    print(receive(pipe, 15), flush=True)
                for pipe in pipes.values():
                    pipe.send({"action": "prepare"})
                for pipe in pipes.values():
                    receive(pipe, 15)
                nodes = list(NODES)
                completed = 0
                start = time.perf_counter()
                for sequence in range(1, args.messages + 1):
                    sender = nodes[(sequence - 1) % 3]
                    # Alterna destinatarios para cubrir las seis direcciones.
                    peer = nodes[((sequence - 1) % 3 + 1 + ((sequence - 1) // 3) % 2) % 3]
                    message_id = make_message_id(run_id, sender, sequence)
                    pipes[sender].send({"action": "send", "peer": peer,
                                        "message_id": message_id, "payload_bytes": args.payload_bytes})
                    result = receive(pipes[sender], args.timeout + 5)
                    completed += result["status"] == "ok"
                    if result["status"] != "ok":
                        print(result, flush=True)
                elapsed = time.perf_counter() - start
                failed = args.messages - completed
                logger = EventLogger(shared_queue, run_id, "sockets", "nodo-A")
                logger.run(args.payload_bytes, "sequential", False, 3,
                           args.messages, completed, failed, elapsed)
                print(f"TCP real: {completed}/{args.messages} intercambios correctos; {failed} fallos.", flush=True)
            finally:
                for pipe in pipes.values():
                    try:
                        pipe.send({"action": "stop"})
                    except (BrokenPipeError, OSError):
                        pass
                shutdown_errors = []
                for process in processes:
                    process.join(timeout=10)
                    if process.is_alive():
                        process.terminate()
                        process.join()
                        shutdown_errors.append("Un nodo no terminó correctamente; descartar esta validación.")
                    if process.exitcode != 0:
                        shutdown_errors.append(f"{process.name} terminó con código {process.exitcode}.")
                for pipe in pipes.values():
                    pipe.close()
                if shutdown_errors:
                    raise RuntimeError("; ".join(shutdown_errors))
    finally:
        shared_queue.close()
        shared_queue.join_thread()
    metadata = {"purpose": "Validación funcional TCP, no experimento comparativo final",
                "run_id": run_id, "python": sys.version, "platform": platform.platform(),
                "deployment": "tres procesos localhost", "payload_bytes": args.payload_bytes,
                "messages": args.messages, "timeout_s": args.timeout,
                "connections": "persistentes, preparadas fuera de RTT",
                "batch_elapsed": "incluye coordinación local por Pipe; no usar como rendimiento final"}
    (directory / "validation.json").write_text(json.dumps(metadata, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"CSV reales y condiciones: {directory.resolve()}")
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
