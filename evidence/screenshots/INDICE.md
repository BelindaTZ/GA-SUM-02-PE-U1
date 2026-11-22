# Índice de evidencias

## Validaciones preliminares

Estas evidencias se conservan en `preliminares/` y documentan el desarrollo del
código. Se distinguen de las capturas del experimento comparativo final.

| Archivo | Integrante | Equipo / usuario Git | Fecha y hora de ejecución | Qué acredita |
|---|---|---|---|---|
| preliminares/20261119_215302_belinda_pruebas_common.jpg | Belinda Toaquiza | DESKTOP-OCH81AB / BelindaTZ | 2026-11-19 21:53:02, America/Guayaquil | Captura original de la transcripción de PowerShell abierta en el editor: identificación, Python 3.13.7 y once pruebas correctas del código compartido. |
| preliminares/20261119_221554_belinda_validacion_tcp.txt | Belinda Toaquiza | DESKTOP-OCH81AB / BelindaTZ | 2026-11-19 22:15:54, America/Guayaquil | Registro inicial del entorno de validación TCP; no conservó la salida de los comandos nativos. |
| preliminares/20261119_223532_belinda_validacion_tcp.txt | Belinda Toaquiza | DESKTOP-OCH81AB / BelindaTZ | 2026-11-19 22:35:32, America/Guayaquil | Registro completo de las 21 pruebas correctas y comprobación de los CSV de 20, 100 y 100 intercambios: 80, 400 y 400 eventos, sin fallos y con parejas Lamport válidas. |

La transcripción íntegra se conserva en
`preliminares/20261119_215302_belinda_pruebas_common.txt`. Se ejecutó primero
`Get-Date; git config user.name; hostname` y después
`python --version` y `python -m unittest discover -s tests`.
Resultado: 11 pruebas en 0.276 segundos, `OK`, código de salida 0.

La imagen se capturó al visualizar el archivo original después de la ejecución;
no es una captura directa de la terminal ni una reconstrucción de su salida.
Se conserva sin edición. Acredita pruebas de software con datos temporales;
las capturas del experimento final se añadirán al ejecutar su protocolo completo.

## Servidor gRPC de Nixon: 19 de noviembre

Capturas originales de ejecución manual en PowerShell, conservadas sin edición
en `preliminares/nixon/`. Usuario: `user`; equipo: `Nixon`; Python 3.12.14.
La ejecución comenzó el 19/11/2026 a las 22:57:25, America/Guayaquil.
ID de corrida: `5633183742e244a4a19616c10d0214f7`.

| Número | Archivo dentro de preliminares/nixon/ | Qué acredita |
|---|---|---|
| 01 | 20261119_nixon_01_nodos_grpc.png | Tres procesos con PID distintos, nodos A/B/C y puertos 5000/5001/5002. |
| 02 | 20261119_nixon_02_intercambio_grpc.png | Solicitud A hacia B y acuse, con relojes de envío 1, acuse 3 y recepción 4. |
| 03 | 20261119_nixon_03_concurrencia_rechazo_grpc.png | Intercambios de A y C hacia B; INVALID_ARGUMENT por ID vacío y reloj de B sin cambio, 9 antes y después. |
| 04 | 20261119_nixon_04_cierre_csv_grpc.png | Tres procesos detenidos, doce eventos, seis parejas Lamport verificadas y ruta de los registros. |

Los archivos originales están en
`data/grpc_validacion_5633183742e244a4a19616c10d0214f7/`.
Esta validación utiliza `src/common`; no es una corrida de latencia ni reemplaza
los 20 intercambios o el protocolo completo de repeticiones. La concurrencia
comprobada aquí corresponde a dos emisores.

## Cliente gRPC de Nixon: 20 de noviembre

Capturas originales en `preliminares/nixon/`, sin editar. Equipo: `Nixon`;
usuario: `nixon\user` (`user` en el script); Python 3.11.9.
Las seis pruebas terminaron con OK en 1.070 segundos.

| Número | Archivo dentro de preliminares/nixon/ | Qué acredita |
|---|---|---|
| 01 | 20261120_nixon_01_pruebas_cliente_grpc.png | Fecha, equipo, usuario y seis pruebas correctas del cliente. |
| 02 | 20261120_nixon_02_nodos_cliente_grpc.png | Arranque de tres procesos y canales para la carga de 100 bytes. |
| 03 | 20261120_nixon_03_cliente_grpc_100bytes.png | Veinte intercambios secuenciales con RTT, 20 correctos y cero fallos. |
| 04 | 20261120_nixon_04_cliente_grpc_100bytes_csv.png | Cierre de los tres nodos y ruta de los registros de 100 bytes. |
| 05 | 20261120_nixon_05_arranque_10240bytes_grpc.png | Identificación, fecha, carga de 10240 bytes y arranque de los tres nodos. |
| 06 | 20261120_nixon_06_resultados_10240bytes_grpc.png | Veinte intercambios correctos de 10240 bytes, cierre y ruta de los registros. |
| 07 | 20261120_nixon_07_arranque_concurrente_grpc.png | Identificación, fecha y arranque en modo concurrent con 100 bytes. |
| 08 | 20261120_nixon_08_resultados_concurrentes_grpc.png | Tres emisores, veinte intercambios correctos, cierre y ruta de los registros. |

Corridas conservadas bajo `data/grpc_cliente_<run_id>/`:

| run_id | Carga | Modo | Inicio visible |
|---|---|---|---|
| c11049550eaa4897909000b30a0a8a03 | 100 bytes | sequential | 20/11/2026 16:54:17 -05:00 |
| c9ad5e94dae640458af6eca9ef109c25 | 10240 bytes | sequential | 20/11/2026 16:57:37 -05:00 |
| 00210d1abe034b3da66d06dfdf9ad2e6 | 100 bytes | concurrent | 20/11/2026 16:59:18 -05:00 |

Las horas corresponden al arranque visible, no a la hora exacta de cada captura.
Cada corrida produjo 80 eventos y 20 latencias; se verificaron 40 parejas causales.
Son validaciones funcionales del cliente, no la matriz comparativa final.

## Experimento final

Capturas de las ejecuciones y del análisis bajo el protocolo experimental completo.

| Archivo | Integrante | Equipo / usuario Git | Fecha y hora de ejecución | Qué acredita |
|---|---|---|---|---|
| 20261121_2033_herrera_analisis_final.png | Humberto Herrera | DESKTOP-3I23BEK / aldair xd | 2026-11-21 20:33:00, America/Guayaquil | Ejecución de `analyze.py --input` con la comparativa final de tres procesos (`data/comparativa_procesos_20261121_150936`, sockets y gRPC): 5 corridas y 500 RTT por combinación, estadísticas de latencia, rendimiento, IC 95 % y cero fallos. Las cifras coinciden con las tablas del informe. |
