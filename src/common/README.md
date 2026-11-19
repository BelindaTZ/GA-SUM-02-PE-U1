# Componentes compartidos previstos

- lamport.py: reloj lógico seguro ante concurrencia.
- config.py: nodos, puertos, tamaños y parámetros.
- event_log.py: eventos con message_id, run_id, nodo, tipo, reloj y hora real.

Acordar interfaz con TCP y gRPC antes de implementar. Evitar paquetes llamados socket o grpc
que oculten los módulos instalados; usar imports desde src y comandos desde la raíz.
