"""Tramas: longitud uint32 en orden de red seguida de JSON UTF-8."""

import json
import socket
import struct
import time

from src.common.config import get_node, require_int

MAX_FRAME_BYTES = 1024 * 1024
FIELDS = {"message_id", "sender", "timestamp", "message"}


class ProtocolError(ValueError):
    """Trama o mensaje que no respeta el contrato de aplicación."""


def validate_message(message):
    if not isinstance(message, dict) or set(message) != FIELDS:
        raise ProtocolError("El JSON debe contener exactamente los cuatro campos acordados.")
    for field in ("message_id", "sender", "message"):
        if not isinstance(message[field], str):
            raise ProtocolError(f"{field} debe ser texto.")
        try:
            message[field].encode("utf-8")
        except UnicodeError as exc:
            raise ProtocolError(f"{field} no es texto UTF-8 válido.") from exc
    if not message["message_id"].strip():
        raise ProtocolError("message_id no puede estar vacío.")
    try:
        get_node(message["sender"])
        require_int(message["timestamp"], "timestamp")
    except ValueError as exc:
        raise ProtocolError(str(exc)) from exc
    if message["timestamp"] > 2**63 - 1:
        raise ProtocolError("timestamp debe poder representarse como int64.")
    return message


def encode_frame(message):
    validate_message(message)
    body = json.dumps(message, ensure_ascii=False, separators=(",", ":"),
                      allow_nan=False).encode("utf-8")
    if not 0 < len(body) <= MAX_FRAME_BYTES:
        raise ProtocolError("La longitud del mensaje supera el máximo permitido.")
    return struct.pack("!I", len(body)) + body


def _pairs(items):
    result = {}
    for key, value in items:
        if key in result:
            raise ProtocolError(f"Campo JSON repetido: {key}.")
        result[key] = value
    return result


def _invalid_constant(value):
    raise ProtocolError(f"Constante JSON inválida: {value}.")


def remaining(deadline):
    duration = deadline - time.perf_counter()
    if duration <= 0:
        raise socket.timeout("Se agotó el plazo del intercambio.")
    return duration


def recv_exact(connection, length, deadline, *, allow_eof=False):
    data = bytearray()
    while len(data) < length:
        connection.settimeout(remaining(deadline))
        chunk = connection.recv(length - len(data))
        if not chunk:
            if allow_eof and not data:
                return None
            raise ProtocolError("La conexión se cerró con una trama incompleta.")
        data.extend(chunk)
    return bytes(data)


def receive_frame(connection, deadline):
    header = recv_exact(connection, 4, deadline, allow_eof=True)
    if header is None:
        return None
    length = struct.unpack("!I", header)[0]
    if not 0 < length <= MAX_FRAME_BYTES:
        raise ProtocolError("Longitud de trama inválida.")
    body = recv_exact(connection, length, deadline)
    try:
        message = json.loads(body.decode("utf-8"), object_pairs_hook=_pairs,
                             parse_constant=_invalid_constant)
    except (UnicodeError, json.JSONDecodeError, RecursionError) as exc:
        raise ProtocolError("Cuerpo JSON o codificación UTF-8 inválidos.") from exc
    return validate_message(message)


def send_frame(connection, message, deadline):
    frame = encode_frame(message)
    connection.settimeout(remaining(deadline))
    connection.sendall(frame)
