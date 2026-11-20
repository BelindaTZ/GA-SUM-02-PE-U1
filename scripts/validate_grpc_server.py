"""Validación manual del servidor con tres procesos y la base compartida."""

import argparse
import csv
from datetime import datetime
import getpass
import json
import multiprocessing as mp
import os
from pathlib import Path
import socket
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import grpc

from src.common.config import NODES, get_node, make_message_id, make_payload, new_run_id
from src.common.event_log import CSVLogWriter, EventLogger
from src.common.lamport import LamportClock
from src.grpc.generated import messaging_pb2 as pb
from src.grpc.generated import messaging_pb2_grpc as rpc
from src.grpc.server_grpc import GRPCServer


def worker(node, run_id, events, commands, results, barrier):
    clock = LamportClock()
    logger = EventLogger(events, run_id, "grpc", node)
    try:
        with GRPCServer(node, clock, logger) as server:
            results.put({"stage": "ready", "node": node, "address": server.address,
                         "pid": os.getpid()})
            while True:
                command = commands.get()
                if command["op"] == "stop":
                    break
                if command["op"] == "clock":
                    results.put({"stage": "clock", "node": node, "value": clock.value})
                    continue
                peer = command["peer"]
                invalid = command["op"] == "invalid"
                message_id = "" if invalid else make_message_id(run_id, node, command["sequence"])
                with grpc.insecure_channel(get_node(peer).target) as channel:
                    grpc.channel_ready_future(channel).result(timeout=10)
                    stub = rpc.MessagingServiceStub(channel)
                    if command.get("concurrent"):
                        barrier.wait(timeout=10)
                    timestamp = clock.value if invalid else clock.send_event(logger, message_id, peer)
                    request = pb.Mensaje(message_id=message_id, sender=node,
                                         timestamp=timestamp, message=make_payload(100))
                    try:
                        reply = stub.EnviarMensaje(request, timeout=5)
                    except grpc.RpcError as exc:
                        if invalid and exc.code() == grpc.StatusCode.INVALID_ARGUMENT:
                            results.put({"stage": "invalid", "node": node,
                                         "status": exc.code().name})
                            continue
                        raise
                    if invalid:
                        raise AssertionError("El servidor aceptó un ID vacío")
                    if (reply.message_id != message_id or reply.sender != peer
                            or reply.message != "ACK" or reply.timestamp < timestamp + 2):
                        raise AssertionError("Acuse incorrecto")
                    received = clock.receive_event(reply.timestamp, logger, message_id, peer, "ack")
                    results.put({"stage": "exchange", "node": node, "peer": peer,
                                 "message_id": message_id, "sent": timestamp,
                                 "ack": reply.timestamp, "received": received})
        results.put({"stage": "stopped", "node": node})
    except Exception as exc:
        results.put({"stage": "error", "node": node, "error": repr(exc)})
        raise


def collect(results, count, stage):
    items = []
    for _ in range(count):
        item = results.get(timeout=30)
        if item["stage"] == "ready":
            print(f"{item['node']} escuchando en {item['address']} (PID {item['pid']})", flush=True)
        elif item["stage"] == "exchange":
            print(f"{item['node']} -> {item['peer']} | id={item['message_id']} | "
                  f"envío={item['sent']} acuse={item['ack']} recepción={item['received']}",
                  flush=True)
        elif item["stage"] == "clock":
            print(f"Reloj de {item['node']}: {item['value']}", flush=True)
        elif item["stage"] == "invalid":
            print(f"Solicitud rechazada: {item['status']}", flush=True)
        elif item["stage"] == "stopped":
            print(f"{item['node']} detenido", flush=True)
        else:
            print(json.dumps(item, ensure_ascii=False), flush=True)
        if item["stage"] != stage:
            raise RuntimeError(f"Resultado inesperado: {item}")
        items.append(item)
    return items


def pause(enabled, text):
    print(f"\n{text}", flush=True)
    if enabled:
        input("Enter para continuar: ")


def verify_events(path, run_id):
    with path.open(encoding="utf-8", newline="") as stream:
        rows = list(csv.DictReader(stream))
    if len(rows) != 12 or any(row["run_id"] != run_id or row["mechanism"] != "grpc" for row in rows):
        raise AssertionError("Se esperaban doce eventos de tres intercambios válidos")
    pairs = {}
    clocks = {}
    for row in rows:
        key = (row["message_id"], row["message_kind"])
        pair = pairs.setdefault(key, {})
        if row["event_type"] in pair:
            raise AssertionError("Evento duplicado")
        pair[row["event_type"]] = row
        value = int(row["lamport"])
        if value <= clocks.get(row["node"], 0):
            raise AssertionError("El reloj local no aumentó")
        clocks[row["node"]] = value
    if len(pairs) != 6:
        raise AssertionError("Cantidad incorrecta de parejas")
    for pair in pairs.values():
        if set(pair) != {"send", "receive"}:
            raise AssertionError("Falta un evento")
        sent, received = pair["send"], pair["receive"]
        if (sent["node"] != received["peer"] or sent["peer"] != received["node"]
                or int(received["lamport"]) <= int(sent["lamport"])):
            raise AssertionError("Pareja causal incorrecta")
    return {"events": len(rows), "messages": len(pairs), "lamport_pairs_valid": True}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--pauses", action="store_true")
    args = parser.parse_args()
    run_id = new_run_id()
    directory = ROOT / "data" / f"grpc_validacion_{run_id}"
    context = mp.get_context("spawn")
    events, results = context.Queue(), context.Queue()
    barrier = context.Barrier(2)
    commands = {node: context.Queue() for node in NODES}
    processes = []
    print(f"Usuario={getpass.getuser()} Equipo={socket.gethostname()}")
    print(f"Fecha={datetime.now().astimezone().isoformat()}")
    print(f"Python={sys.version.split()[0]} run_id={run_id}")
    print("Validación del servidor gRPC")
    try:
        with CSVLogWriter(events, directory):
            try:
                for node in NODES:
                    process = context.Process(target=worker,
                                              args=(node, run_id, events, commands[node], results, barrier))
                    process.start()
                    processes.append(process)
                collect(results, 3, "ready")
                pause(args.pauses, "Nodos iniciados.")
                commands["nodo-A"].put({"op": "send", "peer": "nodo-B", "sequence": 1})
                collect(results, 1, "exchange")
                pause(args.pauses, "Intercambio completado.")
                commands["nodo-A"].put({"op": "send", "peer": "nodo-B", "sequence": 2,
                                         "concurrent": True})
                commands["nodo-C"].put({"op": "send", "peer": "nodo-B", "sequence": 1,
                                         "concurrent": True})
                collect(results, 2, "exchange")
                commands["nodo-B"].put({"op": "clock"})
                before = collect(results, 1, "clock")[0]["value"]
                commands["nodo-A"].put({"op": "invalid", "peer": "nodo-B"})
                collect(results, 1, "invalid")
                commands["nodo-B"].put({"op": "clock"})
                after = collect(results, 1, "clock")[0]["value"]
                if before != after:
                    raise AssertionError("La solicitud inválida modificó el reloj")
                print("Solicitud inválida rechazada sin modificar el reloj de nodo-B.")
                pause(args.pauses, "Concurrencia y rechazo comprobados.")
                for queue in commands.values():
                    queue.put({"op": "stop"})
                collect(results, 3, "stopped")
                for process in processes:
                    process.join(timeout=10)
                    if process.is_alive() or process.exitcode != 0:
                        raise RuntimeError("Un proceso no terminó correctamente")
            finally:
                for process in processes:
                    if process.is_alive():
                        process.terminate()
                        process.join()
        summary = verify_events(directory / "events_grpc.csv", run_id)
        summary.update(run_id=run_id, processes_closed=True, invalid_rejected=True,
                       concurrent_senders=2, experiment_final=False)
        (directory / "validation.json").write_text(
            json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        print(f"Eventos registrados: {summary['events']}")
        print(f"Parejas Lamport verificadas: {summary['messages']}")
        print(f"Registros: {directory}")
        pause(args.pauses, "Validación terminada.")
    finally:
        for queue in [events, results, *commands.values()]:
            queue.close()
            queue.join_thread()


if __name__ == "__main__":
    main()
