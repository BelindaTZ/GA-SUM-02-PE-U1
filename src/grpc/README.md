# Implementación gRPC

Contrato: `proto/messaging.proto`. Campos e instrucciones de generación:
`proto/README.md`. Desde la raíz del repositorio:

```bat
python scripts\generate_proto.py
```

Los módulos se importan con
`from src.grpc.generated import messaging_pb2, messaging_pb2_grpc`.
No editar los archivos generados ni mantener otra copia del contrato.

## Servidor

`MessagingService` en `server_grpc.py` recibe `Mensaje` y comprueba ID, emisor
y timestamp. Devuelve `INVALID_ARGUMENT` para campos inválidos y `OUT_OF_RANGE`
cuando el reloj no puede avanzar dentro de int64.

`GRPCServer(node, clock, logger)` utiliza la configuración de `src/common` y
los métodos `receive_event` y `send_event` de `LamportClock`. Devuelve `ACK`,
igual que TCP. Se utiliza con `start()`/`close()` o como contexto `with`.
El reloj y el logger deben ser los mismos que usará el cliente de ese nodo;
el logger debe identificar el nodo y el mecanismo `grpc`.
El servidor no crea otro reloj permanente ni escribe directamente los CSV.
`GRPCClient` en `client_grpc.py` comparte esas mismas instancias de reloj y logger.

## Validación con la base compartida

Detener cualquier servidor anterior que use 5000, 5001 o 5002. Desde la raíz:

Con un entorno Python 3.11 o superior y las dependencias gRPC instaladas:

```text
python scripts/generate_proto.py
python scripts/validate_grpc_server.py --pauses
```

El script inicia tres procesos con sus propios relojes, compartidos por cliente
de comprobación y servidor de cada nodo. Todos usan EventLogger y una sola cola
y escritor CSV en el coordinador. Se realiza un intercambio, luego dos emisores
sincronizados hacia B y un rechazo por ID vacío. La opción `--pauses` permite
revisar los resultados entre etapas.

Al cerrar, si se cumplen las comprobaciones, guarda `events_grpc.csv` y
`validation.json` en una carpeta nueva `data/grpc_validacion_<run_id>/`.
Se esperan 12 eventos y seis parejas envío/recepción. No genera latencias ni
reemplaza los 20 intercambios, cinco repeticiones o tres clientes concurrentes
del experimento final. Si falla, conservar la salida y no registrar éxito.

Nixon ejecutó la validación el 19/11/2026. Corrida:
`5633183742e244a4a19616c10d0214f7`. Resultado: tres intercambios correctos,
doce eventos, seis parejas Lamport válidas y cierre de los tres procesos.
El ID vacío fue rechazado con `INVALID_ARGUMENT`, sin modificar el reloj del
receptor. Capturas y rutas están en `evidence/screenshots/INDICE.md`.

Explicación del código: `docs/secciones/nixon/implementacion_grpc.tex`.
## Cliente

`GRPCClient(node, clock, logger, timeout=5.0, addresses=None)` mantiene un canal
por destino. `prepare(peer)` espera que el canal esté listo antes de medir.
`exchange(peer, message_id, payload, mode="sequential", warmup=False, measure=True)`
devuelve `ExchangeResult` con message_id, status, rtt_ms, ack y error.

El envío y la recepción actualizan Lamport mediante los métodos de common.
Se comprueba que el acuse conserve el ID, provenga del destinatario, diga ACK
y tenga un reloj mayor al enviado. El RTT se mide con perf_counter desde antes
del envío hasta validar y registrar el acuse. Se guarda en milisegundos con el
esquema común. Los estados son ok, timeout y error; los fallos tienen RTT vacío.
`measure=False` conserva eventos y resultado, pero no añade una fila de latencia.

No se añade una política de reintentos. Hay un intercambio en curso por destino,
como en TCP. `close()` cierra los canales; también se admite `with GRPCClient(...)`.
El coordinador debe esperar a que terminen los hilos antes de cerrar el cliente.

## Comprobaciones del cliente

Con Python 3.11+ y las dependencias gRPC instaladas, desde la raíz:

```text
python scripts/generate_proto.py
python -m unittest discover -s tests -p test_grpc.py -v
python scripts/demo_grpc.py --payload-bytes 100 --pauses
python scripts/demo_grpc.py --payload-bytes 10240 --pauses
python scripts/demo_grpc.py --payload-bytes 100 --mode concurrent --pauses
```

El demo usa las veinte filas de `experiments/plan_intercambios.csv`. En modo
concurrente cada emisor conserva el orden de sus propias filas y los tres se
inician con una barrera. Se espera a que los canales estén preparados antes de
cronometrar. Cada ejecución crea una carpeta `data/grpc_cliente_<run_id>` con
eventos, latencias, resumen del lote y condiciones de validación, sin sobrescribir
archivos existentes.

El tiempo del lote incluye coordinación local por Pipe: no se usa como rendimiento
del experimento final. Estas comprobaciones no sustituyen el calentamiento y las
cinco repeticiones por mecanismo/tamaño. El runner final debe ejecutar el mismo
plan con TCP y gRPC. Los comandos de validación TCP anteriores no cargan este CSV.
Nixon ejecutó las seis pruebas del cliente el 20/11/2026: todas terminaron con OK.
También ejecutó estas tres validaciones, cada una con 20 intercambios correctos
y cero fallos:

| Corrida | Carga | Modo |
|---|---|---|
| c11049550eaa4897909000b30a0a8a03 | 100 bytes | sequential |
| c9ad5e94dae640458af6eca9ef109c25 | 10240 bytes | sequential |
| 00210d1abe034b3da66d06dfdf9ad2e6 | 100 bytes | concurrent |

Cada carpeta contiene 80 eventos, 20 latencias, una fila de lote y validation.json.
Se comprobaron 40 parejas envío/recepción válidas por corrida. En modo concurrente
participaron los tres emisores. Las capturas originales están indexadas en
`evidence/screenshots/INDICE.md` y los CSV se incluyen en `data/SHA256SUMS`.
