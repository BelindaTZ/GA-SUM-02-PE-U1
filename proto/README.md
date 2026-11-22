# Contrato gRPC

`messaging.proto` define los datos que intercambian los nodos. La relación de
sus campos con los registros está en [Datos y esquema CSV](../data/README.md).
El servicio `MessagingService` tiene una función:
`EnviarMensaje` recibe un `Mensaje` y devuelve un `Acuse` como respuesta.

## Campos

Los dos mensajes tienen estos campos. `string` significa texto e `int64`
es un número entero de 64 bits.

| Campo | Numero | Tipo proto | Solicitud | Acuse |
|---|---|---|---|---|
| message_id | 1 | string | ID unico que combina corrida, nodo y secuencia | El mismo ID de la solicitud |
| sender | 2 | string | Nodo que inicia el intercambio | Nodo que responde |
| timestamp | 3 | int64 | Lamport al enviar la solicitud | Lamport al enviar el acuse |
| message | 4 | string | Carga util UTF-8 | Texto de confirmacion |

Los números del 1 al 4 identifican los campos; no son los valores que se envían.
`timestamp` lleva el reloj de Lamport, no la fecha ni la hora de la computadora.

El cliente y el servidor deberán comprobar que el ID no esté vacío, el nodo
sea `nodo-A`, `nodo-B` o `nodo-C`, y el reloj esté entre 0 y 2^63-1.
También deberán comprobar que el acuse corresponda a la solicitud.
El `.proto` define los tipos, pero no realiza esas comprobaciones.

Los tamaños de 100 y 10240 bytes corresponden solo al texto de `message`:
`len(solicitud.message.encode("utf-8"))`. En las pruebas se utiliza texto ASCII.
El acuse lleva un texto de confirmación y no devuelve todo el mensaje.
En ambos mecanismos, ese texto es `ACK`.

## Uso del reloj en el intercambio

1. El emisor incrementa su reloj y lo coloca en `Mensaje.timestamp` al enviar.
2. El receptor aplica `max(local, recibido) + 1` al recibir la solicitud.
3. El receptor vuelve a incrementar al enviar `Acuse` e incluye ese reloj.
4. El emisor aplica `max(local, recibido) + 1` al recibir el acuse.

Son cuatro eventos por intercambio. Comparten `message_id`, pero se distinguen
en CSV con `message_kind=request` o `ack` y `event_type=send` o `receive`.
El reloj y los registros se reutilizan desde `src/common`. Las implementaciones
del servidor y cliente están documentadas en `src/grpc/README.md`.

## Generacion reproducible en Windows (cmd.exe)

Desde la raiz del repositorio, con Python 3.11 o superior:

```bat
python -m venv .venv
.venv\Scripts\activate.bat
python -m pip install -r requirements.txt
python scripts\generate_proto.py
python -c "from src.grpc.generated import messaging_pb2, messaging_pb2_grpc; print(messaging_pb2.DESCRIPTOR.services_by_name['MessagingService'].full_name)"
```

El ultimo comando debe imprimir `pe_u1.MessagingService`. Los comandos tambien
sirven en Linux/macOS cambiando la activacion a `source .venv/bin/activate`.

Se generan `src/grpc/generated/messaging_pb2.py` (mensajes) y
`src/grpc/generated/messaging_pb2_grpc.py` (stub y base del servicio).
Se excluyen de Git porque se regeneran desde la fuente y versiones fijadas.
El script deja los imports preparados para usar `src.grpc.generated`.
No hay que editar los archivos generados. El cliente y el servidor se ejecutarán
desde la raíz del repositorio; el generador también admite su ruta completa.

No renumerar campos existentes ni reutilizar sus numeros con otro significado.
El informe ya incluye el contrato desde `docs/secciones/nixon/contrato_proto.tex`.
Para compilarlo se usa el principal `docs/guia1_practica.tex`, como indica
`docs/README.md`.

Documentacion oficial de apoyo:
- https://grpc.io/docs/languages/python/basics/#generating-grpc-interfaces-with-custom-package-name
- https://protobuf.dev/programming-guides/proto3/
