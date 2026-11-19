"""Genera los archivos Python a partir de messaging.proto."""

from pathlib import Path
import subprocess
import sys


def main() -> int:
    root = Path(__file__).resolve().parents[1]
    if sys.version_info < (3, 11):
        print("Se requiere Python 3.11 o superior.", file=sys.stderr)
        return 1

    # Generar imports desde src.grpc.generated.
    command = [
        sys.executable,
        "-m",
        "grpc_tools.protoc",
        f"--proto_path=src/grpc/generated={root / 'proto'}",
        f"--python_out={root}",
        f"--grpc_python_out={root}",
        "src/grpc/generated/messaging.proto",
    ]
    result = subprocess.run(command, cwd=root, check=False)
    if result.returncode:
        print(
            "No se pudo generar el contrato. Instala requirements.txt "
            "con este mismo interprete y revisa el error anterior.",
            file=sys.stderr,
        )
        return result.returncode

    print("Generados src/grpc/generated/messaging_pb2.py y messaging_pb2_grpc.py")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
