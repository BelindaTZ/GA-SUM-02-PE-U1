"""Cliente TCP persistente, con un intercambio en curso por conexión."""

import socket
import threading
import time
from dataclasses import dataclass

from src.common.config import get_node
from .protocol import ProtocolError, encode_frame, receive_frame, remaining
from .server import validate_timeout


@dataclass(frozen=True)
class ExchangeResult:
    message_id: str
    status: str
    rtt_ms: float | None
    ack: dict | None = None
    error: str | None = None


class TCPClient:
    def __init__(self, node, clock, logger, *, timeout=5.0, addresses=None):
        get_node(node)
        if logger.node != node or logger.mechanism != "sockets":
            raise ValueError("El logger del cliente debe corresponder a su nodo y a sockets.")
        self.node, self.clock, self.logger = node, clock, logger
        self.timeout = validate_timeout(timeout)
        self._addresses = addresses or {}
        self._connections = {}
        self._locks = {peer: threading.Lock() for peer in ("nodo-A", "nodo-B", "nodo-C") if peer != node}
        self._closed = False

    def _peer_lock(self, peer):
        get_node(peer)
        if peer == self.node:
            raise ValueError("El destinatario debe ser otro nodo.")
        return self._locks[peer]

    def _connect(self, peer):
        if self._closed:
            raise RuntimeError("El cliente está cerrado.")
        if peer not in self._connections:
            address = self._addresses.get(peer, get_node(peer).address)
            connection = socket.create_connection(address, timeout=self.timeout)
            connection.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
            self._connections[peer] = connection
        return self._connections[peer]

    def prepare(self, peer):
        """Establece la conexión antes del tramo medido; no envía un mensaje."""
        with self._peer_lock(peer):
            self._connect(peer)

    def _discard(self, peer):
        connection = self._connections.pop(peer, None)
        if connection is not None:
            connection.close()

    def exchange(self, peer, message_id, payload, *, mode="sequential", warmup=False,
                 measure=True):
        """Sin reintentos automáticos: un intento produce como máximo una solicitud.

        Los errores de programación/argumentos se propagan. Los errores de red o
        protocolo producen un resultado fallido, registrado con RTT vacío.
        """
        lock = self._peer_lock(peer)
        payload_bytes = len(payload.encode("utf-8")) if isinstance(payload, str) else 0
        self.logger.validate_event(message_id, peer, "request", "send")
        self.logger._conditions(payload_bytes, mode, warmup)
        # Validar longitud y contrato antes de alterar el reloj.
        encode_frame({"message_id": message_id, "sender": self.node,
                      "timestamp": self.clock.value + 1, "message": payload})
        with lock:
            try:
                connection = self._connect(peer)
                start = time.perf_counter()
                timestamp = self.clock.send_event(self.logger, message_id, peer)
                frame = encode_frame({"message_id": message_id, "sender": self.node,
                                      "timestamp": timestamp, "message": payload})
                connection.settimeout(remaining(start + self.timeout))
                connection.sendall(frame)
                ack = receive_frame(connection, start + self.timeout)
                if (ack is None or ack["message_id"] != message_id or ack["sender"] != peer
                        or ack["message"] != "ACK" or ack["timestamp"] <= timestamp):
                    raise ProtocolError("Acuse ausente, no correspondiente o con reloj inválido.")
                self.clock.receive_event(ack["timestamp"], self.logger, message_id, peer, "ack")
                result = ExchangeResult(message_id, "ok", (time.perf_counter() - start) * 1000, ack)
            except (ProtocolError, OSError) as exc:
                self._discard(peer)
                result = ExchangeResult(message_id, "timeout" if isinstance(exc, TimeoutError) else "error",
                                        None, error=str(exc))
            if measure:
                self.logger.latency(message_id, payload_bytes, mode, warmup,
                                    result.rtt_ms, result.status)
            return result

    def close(self):
        # El coordinador debe esperar a que terminen sus hilos de envío.
        self._closed = True
        for peer in self._locks:
            with self._locks[peer]:
                self._discard(peer)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, traceback):
        self.close()
