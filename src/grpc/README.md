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
El cliente definitivo todavía está pendiente.

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
El cliente experimental se documentará al implementarlo en el siguiente aporte.
