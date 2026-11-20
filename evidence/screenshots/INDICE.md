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

## Experimento final

Pendiente: capturas de las ejecuciones TCP/gRPC y del análisis bajo el protocolo
experimental completo, con identificación de integrante, equipo y fecha.
