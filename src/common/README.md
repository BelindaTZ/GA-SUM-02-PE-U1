# Componentes compartidos previstos

- lamport.py: reloj lógico seguro ante concurrencia.
- config.py: nodos, puertos, tamaños y parámetros.
- event_log.py: eventos con message_id, run_id, nodo, tipo, reloj y hora real.

Respetar los campos y unidades definidos en ../../ACUERDOS_TECNICOS.md para TCP y gRPC. Evitar paquetes llamados socket o grpc
que oculten los módulos instalados; usar imports desde src y comandos desde la raíz.
