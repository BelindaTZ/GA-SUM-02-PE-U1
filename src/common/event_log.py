"""Productores por nodo y un único escritor de CSV en el coordinador."""

import csv
import math
from contextlib import ExitStack
from datetime import datetime
from pathlib import Path
from threading import Thread

from .config import DATA_DIR, MECHANISMS, MODES, get_node, require_int

EVENT_COLUMNS = ("run_id", "message_id", "mechanism", "node", "peer",
                 "message_kind", "event_type", "lamport", "physical_time")
LATENCY_COLUMNS = ("run_id", "message_id", "mechanism", "payload_bytes", "mode",
                   "warmup", "client_id", "rtt_ms", "status")
RUN_COLUMNS = ("run_id", "mechanism", "payload_bytes", "mode", "warmup", "clients",
               "attempted", "completed", "failed", "elapsed_s")
SCHEMAS = {"events": EVENT_COLUMNS, "latency": LATENCY_COLUMNS, "runs": RUN_COLUMNS}


def _text(value, name):
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{name} debe ser texto no vacío.")


def _choice(value, choices, name):
    if value not in choices:
        raise ValueError(f"{name} debe pertenecer a {choices}.")


def _number(value, name, *, positive=False):
    if (isinstance(value, bool) or not isinstance(value, (int, float))
            or not math.isfinite(value) or value < 0 or (positive and value == 0)):
        raise ValueError(f"{name} debe ser un número finito {'positivo' if positive else 'no negativo'}.")


class EventLogger:
    """Una instancia por nodo y corrida; la cola puede cruzar procesos.

    Utilizar LamportClock.send_event/receive_event para registrar el reloj
    atómicamente con cada evento. El productor no abre archivos.
    """

    def __init__(self, queue, run_id: str, mechanism: str, node: str):
        _text(run_id, "run_id")
        _choice(mechanism, MECHANISMS, "mechanism")
        get_node(node)
        self.queue = queue
        self.run_id = run_id
        self.mechanism = mechanism
        self.node = node

    def _put(self, kind, **fields):
        self.queue.put((kind, {"run_id": self.run_id, "mechanism": self.mechanism, **fields}))

    def validate_event(self, message_id, peer, message_kind, event_type):
        _text(message_id, "message_id")
        get_node(peer)
        if peer == self.node:
            raise ValueError("El otro extremo debe ser un nodo diferente.")
        _choice(message_kind, ("request", "ack"), "message_kind")
        _choice(event_type, ("send", "receive"), "event_type")

    def event(self, message_id, peer, message_kind, event_type, lamport):
        self.validate_event(message_id, peer, message_kind, event_type)
        require_int(lamport, "lamport", 1)
        self._put("events", message_id=message_id, node=self.node, peer=peer,
                  message_kind=message_kind, event_type=event_type, lamport=lamport,
                  physical_time=datetime.now().astimezone().isoformat(timespec="microseconds"))

    def latency(self, message_id, payload_bytes, mode, warmup, rtt_ms=None, status="ok"):
        _text(message_id, "message_id")
        self._conditions(payload_bytes, mode, warmup)
        _choice(status, ("ok", "timeout", "error"), "status")
        if status == "ok":
            _number(rtt_ms, "rtt_ms")
        elif rtt_ms is not None:
            raise ValueError("Un intento fallido debe tener rtt_ms=None.")
        self._put("latency", message_id=message_id, payload_bytes=payload_bytes,
                  mode=mode, warmup=int(warmup), client_id=self.node,
                  rtt_ms=rtt_ms, status=status)

    def run(self, payload_bytes, mode, warmup, clients, attempted, completed, failed, elapsed_s):
        """Llamar una sola vez por lote, desde el coordinador."""
        self._conditions(payload_bytes, mode, warmup)
        require_int(clients, "clients", 1)
        if clients > 3:
            raise ValueError("Hay como máximo tres clientes.")
        for name, value in (("attempted", attempted), ("completed", completed), ("failed", failed)):
            require_int(value, name)
        if attempted != completed + failed:
            raise ValueError("attempted debe ser completed + failed.")
        _number(elapsed_s, "elapsed_s", positive=True)
        self._put("runs", payload_bytes=payload_bytes, mode=mode, warmup=int(warmup),
                  clients=clients, attempted=attempted, completed=completed,
                  failed=failed, elapsed_s=elapsed_s)

    @staticmethod
    def _conditions(payload_bytes, mode, warmup):
        require_int(payload_bytes, "payload_bytes", 1)
        _choice(mode, MODES, "mode")
        if not isinstance(warmup, (bool, int)) or warmup not in (0, 1):
            raise ValueError("warmup debe ser 0 o 1.")


class CSVLogWriter:
    """Un hilo escritor en el coordinador, alimentado mediante una cola.

    Crear antes de los productores. Cerrar DESPUÉS de terminar y unir todos los
    productores. No reutilizar archivos existentes: evita sobrescribir evidencia.
    Los archivos se crean solo cuando llega su primera fila.
    """

    def __init__(self, queue, directory: Path = DATA_DIR):
        self.queue = queue
        self.directory = Path(directory)
        self._error = None
        self._closed = False
        self._thread = None

    def __enter__(self):
        if self._thread is not None or self._closed:
            raise RuntimeError("El escritor no puede reutilizarse.")
        self.directory.mkdir(parents=True, exist_ok=True)
        expected = ["runs.csv"] + [f"{kind}_{m}.csv" for kind in ("events", "latency") for m in MECHANISMS]
        if any((self.directory / name).exists() for name in expected):
            raise FileExistsError("La carpeta ya contiene registros. Use otra carpeta o conserve sus archivos antes de ejecutar.")
        self._thread = Thread(target=self._consume, name="csv-writer", daemon=False)
        self._thread.start()
        return self

    def _consume(self):
        try:
            self._write_rows()
        except Exception as exc:
            # Incluye errores al vaciar buffers o cerrar los archivos.
            self._error = exc

    def _write_rows(self):
        with ExitStack() as stack:
            writers = {}
            while True:
                item = self.queue.get()
                if item is None:
                    return
                if self._error is not None:
                    continue
                try:
                    kind, row = item
                    columns = SCHEMAS[kind]
                    if set(row) != set(columns):
                        raise ValueError(f"Columnas incorrectas para {kind}.")
                    _choice(row["mechanism"], MECHANISMS, "mechanism")
                    filename = "runs.csv" if kind == "runs" else f"{kind}_{row['mechanism']}.csv"
                    if filename not in writers:
                        stream = stack.enter_context((self.directory / filename).open("x", encoding="utf-8", newline=""))
                        writer = csv.DictWriter(stream, fieldnames=columns)
                        writer.writeheader()
                        writers[filename] = writer
                    writers[filename].writerow(row)
                except Exception as exc:
                    # Seguir drenando la cola permite que los procesos terminen.
                    self._error = exc

    def close(self):
        if not self._closed and self._thread is not None:
            self.queue.put(None)
            self._thread.join()
            self._closed = True
        if self._error is not None:
            raise RuntimeError("Falló la escritura CSV; la corrida no debe considerarse completa.") from self._error

    def __exit__(self, exc_type, exc, traceback):
        self.close()
