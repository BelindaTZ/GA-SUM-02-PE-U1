# Utilidades ejecutables

Desde la raíz, con el entorno del proyecto activo:

- `python -m scripts.generate_proto`: genera los módulos Python del contrato
  `proto/messaging.proto`. Requiere `requirements.txt`; los archivos generados
  se guardan en `src/grpc/generated/` y se regeneran después de clonar.
- `python -m scripts.demo_tcp --messages 20 --payload-bytes 100`: valida TCP con
  tres procesos y conserva sus CSV en una carpeta nueva dentro de `data/`.
- `python -m scripts.demo_grpc --plan experiments/plan_intercambios.csv`:
  ejecuta la validación gRPC con el plan común de veinte intercambios.
- `python -m scripts.validate_grpc_server`: comprueba el servidor gRPC,
  sus acuses y el rechazo de solicitudes inválidas.

Los programas de demostración y validación admiten `--help`. Los detalles del contrato y los transportes se
encuentran en [proto](../proto/README.md), [TCP](../src/sockets/README.md) y
[gRPC](../src/grpc/README.md). Para la comparativa completa se utiliza el
[ejecutor experimental](../experiments/README.md), no los programas de validación.

Los datos y el significado de `SHA256SUMS` se documentan en
[Datos y esquema CSV](../data/README.md).
