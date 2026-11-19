# Acuerdos para integrar las cuatro partes

## Estado y alcance

El usuario confirmó que los cuatro integrantes aceptaron la propuesta de reparto,
mensajes y CSV. Este documento concreta esa propuesta para que el código de cada
bloque sea compatible. Los detalles de representación siguientes son la base técnica
de implementación; no constituyen mediciones ni una sesión de trabajo acreditada.

Reparto aceptado: 1, Belinda Toaquiza, base y TCP; 2, Nixon Piguave, gRPC;
3, Emanuel Pino, experimentos y verificación Lamport; 4, Humberto Herrera,
análisis, tablas y gráficos. Los nombres completos están en EQUIPO.md.
Cada uno redacta su parte del informe y su conclusión. Las cuentas GitHub de
los integrantes 2, 3 y 4 están pendientes.

## Nodos e interfaces comunes

- nodo-A: 127.0.0.1:5000; nodo-B: 127.0.0.1:5001; nodo-C: 127.0.0.1:5002.
- TCP y gRPC se ejecutan por separado para reutilizar los puertos.
- Ambos mecanismos reutilizan reloj, configuración y registro de src/common.
- Los comandos concretos se documentarán cuando exista una implementación comprobada.

## Mensajes: campos aceptados

| Campo | Representación común | Significado |
|---|---|---|
| message_id | Texto no vacío | Identificador único de la solicitud en la corrida |
| sender | Texto | nodo-A, nodo-B o nodo-C |
| timestamp | Entero no negativo | Reloj Lamport del emisor en el envío |
| message | Texto UTF-8 | Carga útil |

TCP transportará un objeto JSON con estos campos. gRPC tendrá campos equivalentes
en Mensaje, con tipos string, string, int64 y string respectivamente. El orden de
serialización no tiene que coincidir; sí los valores y el significado.
El identificador debe seguir siendo único entre clientes concurrentes: combinar
run_id, nodo emisor y secuencia. run_id viaja dentro de ese identificador y queda
además como columna explícita en los registros.

Base técnica para el acuse: message_id de la solicitud, sender del nodo que responde,
timestamp de su envío y message como texto de confirmación. El acuse corresponde
a una respuesta real y también actualiza Lamport. En eventos se distingue mediante
message_kind=request o ack; no se confunden sus pares envío/recepción.

Reloj: incrementar antes de cada envío; al recibir, max(local, recibido)+1.
Proteger actualizaciones y registro cuando varios hilos comparten un nodo.

Para tamaños comparables se utilizará texto ASCII de 100 y 10240 bytes UTF-8 en
message. payload_bytes mide solo esa carga, sin JSON, Protobuf, cabeceras ni IDs.
La prueba del contrato y del tamaño debe hacerse en ambos mecanismos antes de medir.

## CSV: archivos comunes

Todos se generan automáticamente dentro de data, con cabecera, codificación UTF-8,
coma como separador y punto decimal. Los nombres de columnas se escriben tal como
aparecen aquí, en inglés y sin tildes; el informe puede presentar etiquetas en español.
No crear archivos CSV vacíos o con ejemplos como supuesta evidencia.

| Archivo | Contenido |
|---|---|
| events_sockets.csv | Eventos Lamport de TCP |
| events_grpc.csv | Eventos Lamport de gRPC |
| latency_sockets.csv | Un registro por intento de solicitud TCP |
| latency_grpc.csv | Un registro por intento de solicitud gRPC |
| runs.csv | Condiciones y duración real de cada lote para calcular rendimiento |

### Columnas de eventos (en este orden)

```text
run_id,message_id,mechanism,node,peer,message_kind,event_type,lamport,physical_time
```

- run_id: identificador único del lote de ejecución.
- message_id: el mismo valor en solicitud, acuse y sus registros asociados.
- mechanism: sockets o grpc.
- node: nodo que registra el evento; peer: otro nodo de la comunicación.
- message_kind: request o ack.
- event_type: send o receive.
- lamport: entero del reloj después de aplicar la regla del evento.
- physical_time: hora real ISO 8601 con zona horaria, para contextualizar la ejecución.

Emparejar eventos por run_id, message_id y message_kind, comprobando nodos y dirección.
La hora real no reemplaza al reloj lógico ni demuestra causalidad.

### Columnas de latencia (en este orden)

```text
run_id,message_id,mechanism,payload_bytes,mode,warmup,client_id,rtt_ms,status
```

- payload_bytes: tamaño UTF-8 de message, en bytes.
- mode: sequential o concurrent.
- warmup: 1 para calentamiento, 0 para corrida válida para análisis.
- client_id: nodo que inicia la solicitud.
- rtt_ms: milisegundos, calculados con time.perf_counter desde antes del envío de
  la solicitud hasta recibir y validar el acuse completo. Vacío en intentos fallidos.
- status: ok, timeout o error; conservar fallos sin inventar una latencia exitosa.

### Columnas de lotes (en este orden)

```text
run_id,mechanism,payload_bytes,mode,warmup,clients,attempted,completed,failed,elapsed_s
```

clients es el número de clientes activos. attempted=completed+failed.
elapsed_s es la duración del lote medida con reloj monotónico: desde el inicio
hasta que terminan todos sus intentos. Rendimiento: completed/elapsed_s.
En concurrencia no dividir por la suma de RTT, porque los intervalos se superponen.
Cada lote tiene un run_id distinto y una fila en runs.csv; los CSV detallados se
relacionan con esa fila mediante run_id.

## Responsabilidades y conservación

- Integrante 1 implementa el registro común y lo demuestra con TCP.
- Integrante 2 usa exactamente el mismo esquema desde gRPC.
- Integrante 3 genera las corridas finales, registra entorno y parámetros adicionales,
  conserva CSV originales, exporta eventos JSON si corresponde y genera SHA256SUMS.
- Integrante 4 lee los CSV, separa mecanismos/tamaños/modos, excluye warmup=1 de
  las estadísticas finales y reporta fallos. Genera tablas y gráficos sin editar crudos.
- Los identificadores de corrida deben ser únicos para conservar todas las ejecuciones;
  no sobrescribir corridas previas al repetir una prueba.
- Cualquier cambio de campos se documenta aquí y se comunica a los responsables
  del productor de datos y del análisis antes de aplicarlo.

## Pendientes que no quedan resueltos con esta aceptación

Cuentas GitHub de los integrantes 2, 3 y 4, horarios personales, escenario del PFC, hipótesis previa,
versiones exactas de dependencias y decisiones experimentales adicionales del plan
(conexiones, timeouts, distribución de envíos concurrentes e intervalos estadísticos).
Estos parámetros deben documentarse antes de las corridas finales.
