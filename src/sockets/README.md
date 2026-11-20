# Sockets TCP

- `server.py`: `TCPServer`, servidor con un hilo por conexión y reloj compartido
  entre sus manejadores. Responde con un acuse de aplicación.
- `client.py`: `TCPClient`, conexiones persistentes, medición RTT y estados
  `ok`, `timeout` y `error` mediante `ExchangeResult`.
- `protocol.py`: validación y delimitación de JSON UTF-8.

## Mensajes y delimitación

Solicitud y acuse contienen exactamente `message_id`, `sender`, `timestamp` y
`message`. El acuse conserva el ID, identifica al nodo receptor como emisor,
lleva un nuevo reloj y usa `message="ACK"`. Se comprueban los tipos, el nombre
del nodo y el rango int64 no negativo del reloj. Se rechazan campos duplicados.

Cada trama consta de cuatro bytes de longitud **sin signo, en orden de red**
(`struct.pack("!I", ...)`) y el cuerpo JSON. La longitud cuenta los bytes UTF-8
del JSON y no incluye la cabecera. El máximo es 1 MiB. La lectura acumula bytes
hasta completar cabecera y cuerpo, por lo que admite datos fragmentados y varios
mensajes seguidos en una conexión. EOF sin cabecera significa cierre normal;
EOF con una trama incompleta es un error.

## Integración

Crear un `LamportClock` y un `EventLogger` por nodo, compartidos por servidor y
cliente. Ambos aceptan `timeout` explícito. Las direcciones predeterminadas son
las de la configuración común; `address` y `addresses` permiten puertos locales
efímeros en las pruebas.

```python
from src.sockets.server import TCPServer
from src.sockets.client import TCPClient

# clock y logger pertenecen al mismo nodo y usan la cola del escritor común.
with TCPServer("nodo-A", clock, logger, timeout=30):
    with TCPClient("nodo-A", clock, logger, timeout=5) as client:
        client.prepare("nodo-B")  # nodo-B debe estar listo
        result = client.exchange("nodo-B", message_id, payload)
```

`prepare` abre la conexión fuera de RTT. `exchange` también conecta si hace falta,
antes de iniciar su cronómetro. Un bloqueo por destinatario permite un solo
intercambio pendiente en cada conexión; conexiones hacia distintos destinatarios
pueden usarse a la vez. El servidor atiende concurrentemente distintas conexiones.
Se utiliza `TCP_NODELAY` en ambos extremos.

El cliente incrementa y registra su reloj antes de enviar. Valida ID, emisor,
confirmación y reloj del acuse antes de registrar su recepción. RTT incluye
preparación final, serialización, envío, recepción, validación y registro del acuse;
excluye conexión inicial y espera por el bloqueo del destinatario. El plazo de
envío/recepción se calcula con un deadline monotónico común por intento.

Los errores de red o de protocolo cierran la conexión afectada y producen un
estado fallido con RTT vacío. No se reintenta automáticamente el mismo mensaje.
Una llamada posterior puede abrir una conexión nueva. Los argumentos inválidos
se rechazan antes de enviar. Un envío fallido puede dejar un evento `send` sin
`receive`; esos casos deben tratarse como fallos al verificar las trazas.

El servidor cierra una conexión inválida, incompleta o inactiva más allá de su
timeout y mantiene disponible el listener. Al cerrar el servidor se interrumpen
sus conexiones y se espera a los hilos. El cliente debe cerrarse después de que
terminen sus tareas de envío.

## Validación funcional comprobada

Desde la raíz, en `cmd.exe` o PowerShell:

```text
python -m unittest discover -s tests -v
python -m scripts.demo_tcp --messages 20 --payload-bytes 100
python -m scripts.demo_tcp --messages 100 --payload-bytes 100
python -m scripts.demo_tcp --messages 100 --payload-bytes 10240
```

`demo_tcp` crea tres procesos reales en los puertos 5000, 5001 y 5002, espera su
disponibilidad, prepara conexiones y distribuye los envíos secuenciales entre
las seis direcciones posibles. Recoge eventos, RTT y condiciones del lote, y
cierra los procesos antes del escritor. Cada ejecución conserva una carpeta
nueva `data/tcp_validacion_<run_id>/` con CSV y `validation.json`.

Los tres comandos se ejecutaron correctamente el 19 de noviembre de 2026 con
Python 3.13.7: 20/20, 100/100 y 100/100 intercambios completos. Son validaciones
funcionales, sin calentamiento ni cinco repeticiones. El tiempo total del lote
incluye coordinación por Pipe; **no utilizarlo como rendimiento experimental
final**. El runner final y la comparación con gRPC corresponden al protocolo
experimental común. Las carpetas de validación no se mezclan con los CSV finales
que lee `analysis/analyze.py` desde la raíz de `data/`.
