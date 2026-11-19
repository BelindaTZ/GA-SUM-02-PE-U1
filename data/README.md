# Datos crudos reales

El formato común está definido en ../ACUERDOS_TECNICOS.md: archivos,
columnas, unidades y responsabilidades de generación y análisis.

Salidas previstas: events_sockets.csv, events_grpc.csv, latency_sockets.csv,
latency_grpc.csv y runs.csv; además entorno, exportación JSON de eventos y SHA256SUMS.

Los scripts deben preservar todas las corridas con run_id únicos, identificar
calentamiento y fallos y no sobrescribir resultados anteriores.
No editar, redondear ni reemplazar CSV crudos. Filtrar y transformar en analysis.
No hay mediciones realizadas en esta estructura inicial.
