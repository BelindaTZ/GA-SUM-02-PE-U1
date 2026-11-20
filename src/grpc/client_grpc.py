"""Cliente gRPC con canales reutilizables y registro compartido."""

from dataclasses import dataclass
import math
from threading import Lock
import time

import grpc

from src.common.config import NODES, get_node
from src.grpc.generated import messaging_pb2 as pb
from src.grpc.generated import messaging_pb2_grpc as rpc


MAX_CLOCK = 2**63 - 1


class AcuseError(ValueError):
    pass


@dataclass(frozen=True)
class ExchangeResult:
    message_id: str
    status: str
    rtt_ms: float | None
    ack: dict | None = None
    error: str | None = None


class GRPCClient:
    def __init__(self, node, clock, logger, *, timeout=5.0, addresses=None):
        get_node(node)
        if logger.node != node or logger.mechanism != "grpc":
            raise ValueError("El logger debe corresponder al nodo y a grpc")
        if (isinstance(timeout, bool) or not isinstance(timeout, (int, float))
                or not math.isfinite(timeout) or timeout <= 0):
            raise ValueError("timeout debe ser un número finito positivo")
        self.node, self.clock, self.logger = node, clock, logger
        self.timeout = timeout
        self._addresses = dict(addresses or {})
        self._channels = {}
        self._stubs = {}
        self._locks = {peer: Lock() for peer in NODES if peer != node}
        self._closed = False

    def _peer_lock(self, peer):
        get_node(peer)
        if peer == self.node:
            raise ValueError("El destinatario debe ser otro nodo")
        return self._locks[peer]

    def _discard(self, peer):
        self._stubs.pop(peer, None)
        channel = self._channels.pop(peer, None)
        if channel is not None:
            channel.close()

    def _connect(self, peer):
        if self._closed:
            raise RuntimeError("El cliente está cerrado")
        if peer not in self._channels:
            target = self._addresses.get(peer, get_node(peer).target)
            if isinstance(target, tuple) and len(target) == 2:
                target = f"{target[0]}:{target[1]}"
            if not isinstance(target, str) or not target.strip():
                raise ValueError("La dirección debe ser host:puerto")
            channel = grpc.insecure_channel(target, options=(("grpc.enable_retries", 0),))
            try:
                grpc.channel_ready_future(channel).result(timeout=self.timeout)
                stub = rpc.MessagingServiceStub(channel)
            except Exception:
                channel.close()
                raise
            self._channels[peer] = channel
            self._stubs[peer] = stub
        return self._stubs[peer]

    def prepare(self, peer):
        with self._peer_lock(peer):
            self._connect(peer)

    def exchange(self, peer, message_id, payload, *, mode="sequential", warmup=False,
                 measure=True):
        lock = self._peer_lock(peer)
        self.logger.validate_event(message_id, peer, "request", "send")
        if not isinstance(payload, str):
            raise ValueError("payload debe ser texto UTF-8")
        payload_bytes = len(payload.encode("utf-8"))
        self.logger._conditions(payload_bytes, mode, warmup)
        if not 0 <= self.clock.value < MAX_CLOCK - 2:
            raise ValueError("El reloj no permite completar otro intercambio int64")
        with lock:
            try:
                stub = self._connect(peer)
                start = time.perf_counter()
                timestamp = self.clock.send_event(self.logger, message_id, peer)
                if timestamp > MAX_CLOCK - 2:
                    raise AcuseError("El reloj alcanzó el límite del contrato")
                request = pb.Mensaje(message_id=message_id, sender=self.node,
                                     timestamp=timestamp, message=payload)
                remaining = self.timeout - (time.perf_counter() - start)
                if remaining <= 0:
                    raise TimeoutError("Se agotó el plazo del intercambio")
                reply = stub.EnviarMensaje(request, timeout=remaining)
                if (reply.message_id != message_id or reply.sender != peer
                        or reply.message != "ACK" or reply.timestamp <= timestamp):
                    raise AcuseError("El acuse no corresponde a la solicitud")
                self.clock.receive_event(reply.timestamp, self.logger, message_id, peer, "ack")
                ack = {"message_id": reply.message_id, "sender": reply.sender,
                       "timestamp": reply.timestamp, "message": reply.message}
                result = ExchangeResult(message_id, "ok", (time.perf_counter() - start) * 1000, ack)
            except (grpc.RpcError, grpc.FutureTimeoutError, TimeoutError, AcuseError) as exc:
                timed_out = isinstance(exc, (grpc.FutureTimeoutError, TimeoutError))
                if isinstance(exc, grpc.RpcError):
                    timed_out = exc.code() == grpc.StatusCode.DEADLINE_EXCEEDED
                self._discard(peer)
                result = ExchangeResult(message_id, "timeout" if timed_out else "error",
                                        None, error=str(exc))
            if measure:
                self.logger.latency(message_id, payload_bytes, mode, warmup,
                                    result.rtt_ms, result.status)
            return result

    def close(self):
        self._closed = True
        for peer, lock in self._locks.items():
            with lock:
                self._discard(peer)

    def __enter__(self):
        if self._closed:
            raise RuntimeError("El cliente está cerrado")
        return self

    def __exit__(self, exc_type, exc, traceback):
        self.close()
