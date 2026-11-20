"""Un reloj por nodo, compartido por sus hilos de cliente y servidor."""

from threading import Lock
from typing import TYPE_CHECKING

from .config import require_int

if TYPE_CHECKING:
    from .event_log import EventLogger


class LamportClock:
    def __init__(self, initial: int = 0):
        self._value = require_int(initial, "initial")
        self._lock = Lock()

    @property
    def value(self) -> int:
        with self._lock:
            return self._value

    def tick(self) -> int:
        """Evento local o envío sin registro; devuelve el nuevo valor."""
        with self._lock:
            self._value += 1
            return self._value

    def update(self, received: int) -> int:
        require_int(received, "received")
        with self._lock:
            self._value = max(self._value, received) + 1
            return self._value

    def send_event(self, logger: "EventLogger", message_id: str,
                   peer: str, message_kind: str = "request") -> int:
        return self._record(logger, message_id, peer, message_kind, "send", None)

    def receive_event(self, received: int, logger: "EventLogger", message_id: str,
                      peer: str, message_kind: str = "request") -> int:
        require_int(received, "received")
        return self._record(logger, message_id, peer, message_kind, "receive", received)

    def _record(self, logger, message_id, peer, message_kind, event_type, received):
        logger.validate_event(message_id, peer, message_kind, event_type)
        with self._lock:
            self._value = max(self._value, received) + 1 if received is not None else self._value + 1
            # El siguiente hilo no puede adelantar el registro de este evento.
            logger.event(message_id, peer, message_kind, event_type, self._value)
            return self._value
