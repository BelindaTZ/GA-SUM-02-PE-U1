"""Servidor de un nodo; cada conexión puede transportar varios intercambios."""

import logging
import math
import socket
import socketserver
import threading
import time

from src.common.config import get_node
from .protocol import ProtocolError, receive_frame, send_frame

LOG = logging.getLogger(__name__)


def validate_timeout(timeout):
    if isinstance(timeout, bool) or not isinstance(timeout, (int, float)) or not math.isfinite(timeout) or timeout <= 0:
        raise ValueError("timeout debe ser un número finito positivo.")
    return timeout


class _Handler(socketserver.BaseRequestHandler):
    def handle(self):
        owner = self.server.owner
        if not owner._register(self.request):
            return
        try:
            self.request.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
            while not owner._stopping.is_set():
                message = receive_frame(self.request, time.perf_counter() + owner.timeout)
                if message is None:
                    return
                peer = message["sender"]
                if peer == owner.node:
                    raise ProtocolError("Un nodo no puede enviarse solicitudes a sí mismo.")
                owner.clock.receive_event(message["timestamp"], owner.logger,
                                          message["message_id"], peer)
                timestamp = owner.clock.send_event(owner.logger, message["message_id"], peer, "ack")
                ack = {"message_id": message["message_id"], "sender": owner.node,
                       "timestamp": timestamp, "message": "ACK"}
                send_frame(self.request, ack, time.perf_counter() + owner.timeout)
        except (ProtocolError, OSError) as exc:
            if not owner._stopping.is_set():
                LOG.warning("%s: conexión cerrada: %s", owner.node, exc)
        finally:
            owner._unregister(self.request)


class _Server(socketserver.ThreadingTCPServer):
    allow_reuse_address = True
    daemon_threads = False
    block_on_close = True


class TCPServer:
    def __init__(self, node, clock, logger, *, timeout=30.0, address=None):
        config = get_node(node)
        if logger.node != node or logger.mechanism != "sockets":
            raise ValueError("El logger del servidor debe corresponder a su nodo y a sockets.")
        self.node, self.clock, self.logger = node, clock, logger
        self.timeout = validate_timeout(timeout)
        self._stopping = threading.Event()
        self._lock = threading.Lock()
        self._connections = set()
        self._thread = None
        self._server = _Server(config.address if address is None else address, _Handler)
        self._server.owner = self

    @property
    def address(self):
        return self._server.server_address

    def _register(self, connection):
        with self._lock:
            if self._stopping.is_set():
                return False
            self._connections.add(connection)
            return True

    def _unregister(self, connection):
        with self._lock:
            self._connections.discard(connection)

    def start(self):
        if self._thread is not None or self._stopping.is_set():
            raise RuntimeError("El servidor no puede reiniciarse.")
        self._thread = threading.Thread(target=self._server.serve_forever,
                                        kwargs={"poll_interval": 0.05}, name=f"tcp-{self.node}")
        self._thread.start()
        return self

    def close(self):
        if self._stopping.is_set():
            return
        self._stopping.set()
        if self._thread is not None:
            self._server.shutdown()
        with self._lock:
            connections = list(self._connections)
        for connection in connections:
            try:
                connection.shutdown(socket.SHUT_RDWR)
            except OSError:
                pass
            connection.close()
        self._server.server_close()
        if self._thread is not None:
            self._thread.join()

    def __enter__(self):
        return self.start()

    def __exit__(self, exc_type, exc, traceback):
        self.close()
