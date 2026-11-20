"""Parámetros comunes; no inicia procesos ni conexiones al importar."""

from dataclasses import dataclass
from pathlib import Path
from types import MappingProxyType
from uuid import uuid4

ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = ROOT / "data"
MECHANISMS = ("sockets", "grpc")
MODES = ("sequential", "concurrent")
PAYLOAD_SIZES = (100, 10240)
LAMPORT_EXCHANGES = 20
LATENCY_SENDS = 100
MIN_VALID_RUNS = 5


@dataclass(frozen=True)
class NodeConfig:
    name: str
    host: str
    port: int

    @property
    def address(self) -> tuple[str, int]:
        return self.host, self.port

    @property
    def target(self) -> str:
        return f"{self.host}:{self.port}"


NODES = MappingProxyType({
    name: NodeConfig(name, "127.0.0.1", port)
    for name, port in (("nodo-A", 5000), ("nodo-B", 5001), ("nodo-C", 5002))
})


def require_int(value: int, name: str, minimum: int = 0) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value < minimum:
        raise ValueError(f"{name} debe ser entero >= {minimum}.")
    return value


def get_node(name: str) -> NodeConfig:
    try:
        return NODES[name]
    except KeyError:
        raise ValueError(f"Nodo desconocido: {name!r}.") from None


def make_payload(size: int) -> str:
    """Carga ASCII: cada carácter ocupa exactamente un byte UTF-8."""
    require_int(size, "size", 1)
    return "x" * size


def new_run_id() -> str:
    return uuid4().hex


def make_message_id(run_id: str, sender: str, sequence: int) -> str:
    if not isinstance(run_id, str) or not run_id.strip() or ":" in run_id:
        raise ValueError("run_id debe ser texto no vacío sin ':'.")
    get_node(sender)
    require_int(sequence, "sequence", 1)
    return f"{run_id}:{sender}:{sequence}"
