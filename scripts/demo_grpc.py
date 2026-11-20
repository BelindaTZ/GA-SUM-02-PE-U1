"""Validación funcional del cliente gRPC con el plan de intercambios del equipo."""

import argparse
import csv
from datetime import datetime
import getpass
import json
import math
import multiprocessing as mp
import os
from pathlib import Path
import platform
import socket
import sys
import time
import traceback

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.common.config import DATA_DIR, NODES, get_node, make_message_id, make_payload, new_run_id
from src.common.event_log import CSVLogWriter, EventLogger
from src.common.lamport import LamportClock
from src.grpc.client_grpc import GRPCClient
from src.grpc.server_grpc import GRPCServer


def load_plan(path):
    with path.open(encoding="utf-8-sig", newline="") as stream:
        reader = csv.DictReader(stream)
        if reader.fieldnames != ["sequence", "sender", "receiver"]:
            raise ValueError("El plan debe tener sequence,sender,receiver")
        rows = list(reader)
    if len(rows) != 20:
        raise ValueError("El plan debe contener veinte intercambios")
    for sequence, row in enumerate(rows, 1):
        if int(row["sequence"]) != sequence:
            raise ValueError("La secuencia del plan debe ir de 1 a 20")
        get_node(row["sender"])
        get_node(row["receiver"])
        if row["sender"] == row["receiver"]:
            raise ValueError("El emisor y receptor deben ser distintos")
    return rows


def worker(node, run_id, events, pipe, barrier, timeout):
    try:
        clock = LamportClock()
        logger = EventLogger(events, run_id, "grpc", node)
        with GRPCServer(node, clock, logger) as server:
            with GRPCClient(node, clock, logger, timeout=timeout) as client:
                pipe.send({"ready": node, "address": server.address, "pid": os.getpid()})
                while True:
                    command = pipe.recv()
                    if command["action"] == "stop":
                        break
                    if command["action"] == "prepare":
                        for peer in NODES:
                            if peer != node:
                                client.prepare(peer)
                        pipe.send({"prepared": node})
                        continue
                    if command["mode"] == "concurrent":
                        barrier.wait(timeout=30)
                    results = []
                    for row in command["rows"]:
                        message_id = make_message_id(run_id, node, int(row["sequence"]))
                        result = client.exchange(row["receiver"], message_id,
                                                 make_payload(command["payload_bytes"]),
                                                 mode=command["mode"])
                        results.append({"sender": node, "peer": row["receiver"],
                                        "message_id": result.message_id, "status": result.status,
                                        "rtt_ms": result.rtt_ms, "error": result.error})
                    pipe.send({"results": results})
        pipe.send({"stopped": node})
    except Exception:
        try:
            pipe.send({"fatal": traceback.format_exc()})
        except (BrokenPipeError, OSError):
            pass
        raise
    finally:
        pipe.close()


def receive(pipe, timeout=30):
    if not pipe.poll(timeout):
        raise TimeoutError("El nodo no respondió al coordinador")
    result = pipe.recv()
    if "fatal" in result:
        raise RuntimeError(result["fatal"])
    return result


def pause(enabled, message):
    print(message, flush=True)
    if enabled:
        input("Enter para continuar: ")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--plan", type=Path, default=ROOT / "experiments/plan_intercambios.csv")
    parser.add_argument("--payload-bytes", type=int, choices=(100, 10240), default=100)
    parser.add_argument("--mode", choices=("sequential", "concurrent"), default="sequential")
    parser.add_argument("--timeout", type=float, default=5.0)
    parser.add_argument("--pauses", action="store_true")
    args = parser.parse_args()
    if not math.isfinite(args.timeout) or not 0 < args.timeout <= 60:
        parser.error("timeout debe ser positivo y como máximo 60 segundos")
    try:
        plan = load_plan(args.plan)
    except (OSError, ValueError) as exc:
        parser.error(str(exc))
    if set(row["sender"] for row in plan) != set(NODES):
        parser.error("El plan debe incluir envíos de los tres nodos")
    run_id = new_run_id()
    directory = DATA_DIR / f"grpc_cliente_{run_id}"
    context = mp.get_context("spawn")
    events = context.Queue()
    barrier = context.Barrier(3)
    pipes, processes = {}, []
    results = []
    print(f"Usuario={getpass.getuser()} Equipo={socket.gethostname()}")
    print(f"Fecha={datetime.now().astimezone().isoformat()}")
    print(f"Python={platform.python_version()} run_id={run_id}")
    print(f"gRPC: {len(plan)} intercambios, {args.payload_bytes} bytes, {args.mode}")
    try:
        with CSVLogWriter(events, directory):
            try:
                for node in NODES:
                    parent, child = context.Pipe()
                    process = context.Process(target=worker, args=(node, run_id, events, child,
                                                                  barrier, args.timeout), name=node)
                    process.start()
                    child.close()
                    pipes[node] = parent
                    processes.append(process)
                for pipe in pipes.values():
                    info = receive(pipe)
                    print(f"{info['ready']} escuchando en {info['address']} (PID {info['pid']})")
                for pipe in pipes.values():
                    pipe.send({"action": "prepare"})
                for pipe in pipes.values():
                    if "prepared" not in receive(pipe):
                        raise RuntimeError("No se prepararon los canales")
                pause(args.pauses, "Nodos y canales preparados.")
                start = time.perf_counter()
                if args.mode == "sequential":
                    for row in plan:
                        pipe = pipes[row["sender"]]
                        pipe.send({"action": "send", "rows": [row], "mode": args.mode,
                                   "payload_bytes": args.payload_bytes})
                        results.extend(receive(pipe, args.timeout + 5)["results"])
                else:
                    for node, pipe in pipes.items():
                        rows = [row for row in plan if row["sender"] == node]
                        pipe.send({"action": "send", "rows": rows, "mode": args.mode,
                                   "payload_bytes": args.payload_bytes})
                    for node, pipe in pipes.items():
                        count = sum(row["sender"] == node for row in plan)
                        results.extend(receive(pipe, 35 + count * (args.timeout + 1))["results"])
                elapsed = time.perf_counter() - start
                completed = sum(row["status"] == "ok" for row in results)
                failed = len(results) - completed
                if len(results) != len(plan):
                    raise RuntimeError("No hay un resultado por solicitud del plan")
                EventLogger(events, run_id, "grpc", "nodo-A").run(
                    args.payload_bytes, args.mode, False, 3, len(plan), completed, failed, elapsed)
                for row in results:
                    rtt = "--" if row["rtt_ms"] is None else f"{row['rtt_ms']:.3f} ms"
                    print(f"{row['sender']} -> {row['peer']} | {row['message_id']} | "
                          f"{row['status']} | RTT={rtt}")
                    if row["error"]:
                        print(row["error"])
                pause(args.pauses, f"Intercambios terminados: {completed}/{len(plan)} correctos, {failed} fallos.")
            finally:
                for pipe in pipes.values():
                    try:
                        pipe.send({"action": "stop"})
                    except (BrokenPipeError, OSError):
                        pass
                errors = []
                for node, pipe in pipes.items():
                    try:
                        info = receive(pipe, 10)
                        if info.get("stopped") != node:
                            raise RuntimeError("Cierre sin confirmación")
                        print(f"{node} detenido")
                    except (EOFError, OSError, RuntimeError, TimeoutError) as exc:
                        errors.append(f"{node}: {exc}")
                for process in processes:
                    process.join(timeout=10)
                    if process.is_alive():
                        process.terminate()
                        process.join()
                        errors.append(f"{process.name} no terminó correctamente")
                    elif process.exitcode != 0:
                        errors.append(f"{process.name}: código {process.exitcode}")
                for pipe in pipes.values():
                    pipe.close()
                if errors:
                    raise RuntimeError("; ".join(errors))
    finally:
        events.close()
        events.join_thread()
    metadata = {"purpose": "Validación funcional del cliente gRPC",
                "experiment_final": False, "run_id": run_id, "python": sys.version,
                "platform": platform.platform(), "deployment": "tres procesos localhost",
                "plan": str(args.plan), "payload_bytes": args.payload_bytes, "mode": args.mode,
                "messages": len(plan), "completed": completed, "failed": failed,
                "timeout_s": args.timeout, "connections": "canales persistentes preparados fuera de RTT",
                "batch_elapsed": "incluye coordinación por Pipe; no usar como rendimiento final"}
    (directory / "validation.json").write_text(json.dumps(metadata, ensure_ascii=False, indent=2) + "\n",
                                              encoding="utf-8")
    print(f"Registros: {directory}")
    pause(args.pauses, "Validación terminada.")
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
