# Implementación gRPC pendiente

Contrato definido en `../../proto/messaging.proto`; instrucciones y significado
de campos en `../../proto/README.md`. Generar desde la raiz con
`python scripts/generate_proto.py` e importar con
`from src.grpc.generated import messaging_pb2, messaging_pb2_grpc`.

Pendiente: crear server_grpc.py y client_grpc.py.
Contrato equivalente a TCP, incluido acuse e identificación trazable; mismo comportamiento Lamport.
La salida de generacion es `src/grpc/generated`; los imports se comprueban desde la raiz.
No mantener dos contratos editados independientemente.
