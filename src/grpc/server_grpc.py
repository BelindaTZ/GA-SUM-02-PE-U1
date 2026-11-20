"""Recepción de mensajes gRPC y validación de solicitudes y acuses."""

from collections.abc import Callable
from concurrent.futures import ThreadPoolExecutor
import logging
from threading import Lock

import grpc

from src.common.config import NODES, get_node
from src.grpc.generated import messaging_pb2 as pb
from src.grpc.generated import messaging_pb2_grpc as rpc


MAX_CLOCK = 2**63 - 1


class MessagingService(rpc.MessagingServiceServicer):
    def __init__(self, node: str, process_message: Callable[[pb.Mensaje], pb.Acuse]):
        if node not in NODES:
            raise ValueError("Nombre de nodo inválido")
        self.node = node
        self.process_message = process_message

    def EnviarMensaje(self, request, context):
        if not request.message_id.strip():
            context.abort(grpc.StatusCode.INVALID_ARGUMENT, "message_id está vacío")
        if request.sender not in NODES:
            context.abort(grpc.StatusCode.INVALID_ARGUMENT, "sender no identifica un nodo")
        if request.sender == self.node:
            context.abort(grpc.StatusCode.INVALID_ARGUMENT, "El emisor debe ser otro nodo")
        if request.timestamp < 0:
            context.abort(grpc.StatusCode.INVALID_ARGUMENT, "timestamp debe ser no negativo")
        if request.timestamp > MAX_CLOCK - 2:
            context.abort(grpc.StatusCode.OUT_OF_RANGE, "No hay espacio para actualizar el reloj")

        try:
            reply = self.process_message(request)
        except OverflowError:
            context.abort(grpc.StatusCode.OUT_OF_RANGE, "El reloj alcanzó el límite de int64")
        except Exception:
            logging.exception("No se pudo procesar la solicitud %s", request.message_id)
            context.abort(grpc.StatusCode.INTERNAL, "No se pudo completar la solicitud")

        if (
            not isinstance(reply, pb.Acuse)
            or reply.message_id != request.message_id
            or reply.sender != self.node
            or reply.timestamp < request.timestamp + 2
            or not reply.message.strip()
        ):
            context.abort(grpc.StatusCode.INTERNAL, "El procesamiento produjo un acuse inválido")
        return reply


def _start_server(
    node: str,
    address: str,
    process_message: Callable[[pb.Mensaje], pb.Acuse],
    workers: int = 4,
):
    if workers < 1:
        raise ValueError("workers debe ser mayor que cero")
    service = MessagingService(node, process_message)
    executor = ThreadPoolExecutor(max_workers=workers)
    server = grpc.server(executor, options=(("grpc.so_reuseport", 0),))
    rpc.add_MessagingServiceServicer_to_server(service, server)
    try:
        if server.add_insecure_port(address) == 0:
            raise RuntimeError(f"No se pudo escuchar en {address}")
        server.start()
    except Exception:
        executor.shutdown(wait=True)
        raise
    return server, executor


class GRPCServer:
    def __init__(self, node, clock, logger, *, workers=4, address=None):
        config = get_node(node)
        if logger.node != node or logger.mechanism != "grpc":
            raise ValueError("El logger debe corresponder al nodo y a grpc")
        self.node, self.clock, self.logger = node, clock, logger
        self.address = config.target if address is None else address
        self.workers = workers
        self._server = None
        self._executor = None
        self._closed = False
        self._processing = Lock()

    def _process_message(self, request):
        with self._processing:
            if max(self.clock.value, request.timestamp) > MAX_CLOCK - 2:
                raise OverflowError
            self.clock.receive_event(request.timestamp, self.logger,
                                     request.message_id, request.sender)
            timestamp = self.clock.send_event(self.logger, request.message_id,
                                              request.sender, "ack")
            if timestamp > MAX_CLOCK:
                raise OverflowError
            return pb.Acuse(message_id=request.message_id, sender=self.node,
                            timestamp=timestamp, message="ACK")

    def start(self):
        if self._server is not None or self._closed:
            raise RuntimeError("El servidor no puede reiniciarse")
        self._server, self._executor = _start_server(
            self.node, self.address, self._process_message, self.workers)
        return self

    def close(self):
        if self._closed:
            return
        self._closed = True
        if self._server is not None:
            self._server.stop(grace=3).wait()
            self._executor.shutdown(wait=True)

    def __enter__(self):
        return self.start()

    def __exit__(self, exc_type, exc, traceback):
        self.close()
