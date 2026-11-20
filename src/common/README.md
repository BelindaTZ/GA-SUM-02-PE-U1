# Código compartido

Implementado con la biblioteca estándar de Python 3.11 o superior. Importar desde
la raíz del repositorio; los mismos componentes sirven para TCP y gRPC.

- `config.py`: nodos y puertos, tamaños de carga, cantidades mínimas de la actividad
  e identificadores de corrida y mensaje. No reparte los envíos entre clientes.
- `lamport.py`: reloj independiente por nodo, protegido con un bloqueo entre hilos.
- `event_log.py`: productores de registros y un único escritor de CSV.

## Configuración

`get_node("nodo-A").address` devuelve `("127.0.0.1", 5000)` para sockets;
`.target` devuelve `"127.0.0.1:5000"` para gRPC. Los demás puertos son 5001 y 5002.
TCP y gRPC se ejecutan en momentos separados.

`make_payload(100)` y `make_payload(10240)` producen los tamaños exactos en UTF-8.
El tamaño se refiere solo al campo `message`, no al mensaje serializado.
El coordinador crea un `new_run_id()` por lote y cada cliente utiliza
`make_message_id(run_id, node, sequence)`, con secuencia positiva y sin repetir
dentro del mismo cliente y lote. El acuse conserva el ID de la solicitud.
Los timeouts y la distribución de los envíos los fijará el protocolo experimental.

## Integración con los nodos

El coordinador crea una cola `multiprocessing.get_context("spawn").Queue()` y abre
`CSVLogWriter(queue, directory)`. Pasa esa cola a los tres procesos. Dentro de cada
proceso se crea **un** `LamportClock()` y un
`EventLogger(queue, run_id, mechanism, node)`, compartidos por cliente y servidor.
`mechanism` admite `sockets` o `grpc`. El reloj se conserva mientras viva el nodo;
al cambiar de lote, el logger utiliza el nuevo `run_id`.

Antes de enviar, `clock.send_event(logger, message_id, peer)` devuelve el reloj que
se coloca en `timestamp`. Al recibir y validar el mensaje,
`clock.receive_event(timestamp, logger, message_id, peer)` actualiza el reloj y
registra la recepción. Para los acuses se añade `message_kind="ack"` en ambos
métodos. La actualización y el envío del registro a la cola se hacen bajo el mismo
bloqueo. `tick()` y `update()` también están disponibles, pero no registran eventos;
no combinarlos con los métodos anteriores para un mismo envío o recepción.

Los eventos de envío representan el intento de enviar un mensaje de aplicación;
si el transporte falla, puede quedar un envío sin recepción. El análisis de fallos
y la verificación deben distinguir esos casos de los intercambios completos.

Cada cliente mide con `time.perf_counter()` y registra el resultado mediante
`logger.latency(message_id, payload_bytes, mode, warmup, rtt_ms, status="ok")`.
El intervalo comienza antes del envío y termina tras validar y registrar el acuse;
la diferencia de segundos se multiplica por 1000 para obtener `rtt_ms`.
Para errores o timeouts se usa `rtt_ms=None` y `status="error"` o `"timeout"`.
Los modos son `sequential` y `concurrent`; `warmup` es 0/1 o booleano.

Al terminar el lote, el coordinador registra **una sola fila** mediante
`logger.run(payload_bytes, mode, warmup, clients, attempted, completed, failed,
elapsed_s)`. `elapsed_s` mide la duración total del lote, no la suma de RTT.
El campo `node` del logger no se incluye en esta fila de lote.

## Cierre y conservación

Primero terminar y unir (`join`) todos los procesos productores; después salir
del contexto del escritor. Así el escritor recibe todos los registros antes del
marcador de cierre. Finalmente cerrar la cola y hacer `queue.join_thread()`.
En Windows, el arranque de procesos debe estar dentro de `if __name__ == "__main__":`.

Se generan con UTF-8, coma y punto decimal los archivos que reciban registros:
`events_sockets.csv`, `events_grpc.csv`, `latency_sockets.csv`,
`latency_grpc.csv` y `runs.csv`. No se crean CSV vacíos. Las columnas coinciden
con el esquema común y los errores de escritura se propagan al cerrar el escritor.
La hora de los eventos es ISO 8601 con zona horaria; no demuestra causalidad.

El escritor rechaza una carpeta que ya contenga esos archivos para evitar perder
datos. Un mismo contexto puede recibir múltiples corridas y ambos mecanismos;
mantenerlo abierto durante toda la sesión experimental. Para nuevas sesiones usar
otra carpeta y conservar los originales. La integración de datos de sesiones
distintas corresponde al coordinador experimental.

## Verificación del código

Desde la raíz, también en `cmd.exe`:

```text
python -m unittest discover -s tests -v
```

Las pruebas comprueban reglas de Lamport, concurrencia entre hilos y procesos,
esquemas CSV, errores y conservación de archivos. Usan datos de prueba en carpetas
temporales: no constituyen corridas reales ni evidencia de la actividad.
