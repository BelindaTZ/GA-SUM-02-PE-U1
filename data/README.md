# Datos crudos reales

Pendiente: latency_sockets.csv, latency_grpc.csv, events_sockets.csv, events_grpc.csv,
exportación JSON de eventos (compatibilidad con guía), entorno y SHA256SUMS.
Se pueden conservar archivos separados por corrida en subcarpetas, documentando el esquema.

Esquema propuesto de latencias: run_id, mechanism, payload_bytes, mode, warmup,
client_id, message_id, rtt_ms, status. Registrar además duración de cada lote para throughput.
Esquema propuesto de eventos: run_id, message_id, node, peer, event_type,
lamport, physical_time, mechanism. Distinguir solicitud y acuse con IDs/dirección.

No editar, redondear ni reemplazar CSV crudos. Filtrar y transformar en analysis.
No hay mediciones realizadas en esta estructura inicial.
