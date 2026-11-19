# Utilidades del proyecto

- `generate_proto.py`: generacion del contrato implementada. Desde la raiz:
  `python scripts/generate_proto.py`. Requiere instalar `requirements.txt`;
  ver `proto/README.md` para instalacion, salidas e imports.
- capture_environment: SO, CPU, RAM, Python, versiones y modalidad de nodos.
- checksums: generar y verificar SHA-256 de todos los CSV crudos, con rutas relativas a data.

No crear SHA256SUMS vacío como evidencia. Generarlo cuando existan los CSV definitivos;
una suma comprueba integridad frente al manifiesto, no demuestra por sí sola autoría ni fecha.
