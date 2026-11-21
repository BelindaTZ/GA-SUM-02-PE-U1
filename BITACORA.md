# Bitácora del equipo

Actividad: GA-SUM-02 / PE-U1.
Cada integrante registra sus sesiones con fecha, participantes, trabajo realizado,
problemas, soluciones y enlaces a sus commits. Horarios en America/Guayaquil.

## Sesión: 2026-11-18 (America/Guayaquil), preparación y organización

- Presentes: Belinda Toaquiza
- Objetivo: preparar el repositorio y organizar el trabajo de los cuatro integrantes.
- Trabajo realizado: revisión de la guía, creación y publicación de las plantillas,
  registro del reparto aceptado y acuerdos de mensajes y CSV. División del informe
  por integrante y compilación del PDF de trabajo, con asistencia de Codex.
- Problemas encontrados: diferencias de numeración, requisitos y organización
  entre el enunciado y las aclaraciones recibidas.
- Solución aplicada: corregir el código y plazo de la actividad y ajustar
  la estructura del repositorio y del informe.
- Corridas/archivos obtenidos: README.md, EQUIPO.md, ACUERDOS_TECNICOS.md,
  PLAN_ACTIVIDAD.md, CHECKLIST_ENTREGA.md y plantillas LaTeX. Sin corridas experimentales.
- Commits o PR relacionados:
  [inicio](https://github.com/BelindaTZ/GA-SUM-02-PE-U1/commit/c05f42e99e44f982b2035ee84f8af80f2186b8de),
  [plantillas](https://github.com/BelindaTZ/GA-SUM-02-PE-U1/commit/705a71fa4d5666edf5c5f5ea52dbc1f577717082),
  [acuerdos](https://github.com/BelindaTZ/GA-SUM-02-PE-U1/commit/33e3f8b2ffe4396254b570280f8ec2127950936c),
  [división del informe](https://github.com/BelindaTZ/GA-SUM-02-PE-U1/commit/469680162cc3d4ba2cd4142e1cceddcae59bc9f1),
  [organización de archivos](https://github.com/BelindaTZ/GA-SUM-02-PE-U1/commit/734689f89b78ded242464ac5f114ba10921c5f9e),
  [reparto visible](https://github.com/BelindaTZ/GA-SUM-02-PE-U1/commit/882c95215ba3d2850f2334f888fba78957bbf507).
- Próximos pasos: desarrollar las secciones asignadas y la base compartida del sistema.

## Sesión: 2026-11-18 (America/Guayaquil), objetivos, hipótesis y fuentes

- Presentes: Belinda Toaquiza
- Objetivo: definir el propósito del experimento y reunir fuentes para sus secciones.
- Trabajo realizado: redacción de objetivos e hipótesis, compilación del PDF y
  selección de cinco fuentes con verificación de datos bibliográficos, DOI e ISBN.
- Problemas encontrados: autores incompletos en una ficha y formato incompatible
  de una entrada bibliográfica.
- Solución aplicada: contrastar los datos con fuentes primarias y Crossref,
  corregir las entradas y validar el archivo con Biber.
- Corridas/archivos obtenidos: objetivo_hipotesis.tex, referencias.bib, FUENTES.md,
  registro de verificación bibliográfica y PDF actualizado. Sin mediciones experimentales.
- Commits o PR relacionados:
  [objetivos, fuentes y bitácora integrada](https://github.com/BelindaTZ/GA-SUM-02-PE-U1/commit/3e1dbcff0d064f13749f42692e449332727e959d).
- Próximos pasos: redactar el fundamento con citas y preparar la arquitectura.

## Sesión: 2026-11-18 (America/Guayaquil), contrato gRPC

- Presentes: Nixon Piguave
- Objetivo: definir el contrato gRPC respetando los mensajes acordados con TCP.
- Trabajo realizado: creación de Mensaje, Acuse y EnviarMensaje; script de
  generación, dependencias gRPC, instrucciones e inclusión del contrato en la
  sección de Nixon del informe. Revisión de los cambios publicados por el equipo.
- Problemas encontrados: no estaban instaladas las dependencias gRPC. Durante
  el trabajo se dividió el informe por integrante y hubo diferencias al integrar
  README y el archivo principal del informe.
- Solución aplicada: instalar grpcio 1.76.0, grpcio-tools 1.76.0 y protobuf 6.33.0
  en un entorno aislado con Python 3.12.14; combinar las instrucciones y las reglas
  de exclusión; conservar el principal del equipo y trasladar el contrato a
  docs/secciones/nixon/contrato_proto.tex.
- Corridas/archivos obtenidos: proto/messaging.proto, scripts/generate_proto.py,
  src/grpc/generated/__init__.py y documentación. Se generaron e importaron los
  módulos Python; se comprobó que conservan los campos, UTF-8 y cargas de
  100/10240 bytes. No se ejecutaron nodos ni corridas experimentales.
- Commits o PR relacionados: [contrato gRPC y generación Python](https://github.com/BelindaTZ/GA-SUM-02-PE-U1/commit/f550d0867ea31248a5ce76f064eab3ef250b8324).
- Próximos pasos: revisar el contrato e implementar el servidor gRPC usando
  el reloj y el registro compartidos de Belinda cuando estén disponibles.

## Sesión: 2026-11-18 (America/Guayaquil), fundamento teórico y aclaración del reparto

- Presentes: Belinda Toaquiza
- Objetivo: desarrollar el fundamento asignado y aclarar las responsabilidades del equipo.
- Trabajo realizado: lectura de apartados de las fuentes y redacción asistida por Codex
  sobre sistemas distribuidos, comparación de modelos, transparencias y CAP.
  Incorporación de citas, tablas y una fuente adicional de 2024; ajuste del reparto
  de teoría, código y redacción. Compilación y revisión del PDF.
- Problemas encontrados: el libro no incluía persistencia en su tabla de transparencias
  y el reparto anterior no distinguía claramente teoría e implementación.
- Solución aplicada: respaldar persistencia con una fuente específica, precisar
  la revisión del libro consultada y separar las responsabilidades en la organización.
- Corridas/archivos obtenidos: fundamento.tex, referencias.bib, LECTURA_FUNDAMENTO.md,
  organización actualizada y PDF compilado. Sin mediciones experimentales.
- Commits o PR relacionados:
  [fundamento y reparto aclarado](https://github.com/BelindaTZ/GA-SUM-02-PE-U1/commit/b4662e5cc14dbd407fc1e2a205636fb088bde736).
- Próximos pasos: elaborar la arquitectura y su diagrama, y desarrollar la base TCP.

## Sesión: 2026-11-19 (America/Guayaquil), arquitectura del sistema

- Presentes: Belinda Toaquiza
- Objetivo: definir la arquitectura de tres nodos y su funcionamiento común para TCP y gRPC.
- Trabajo realizado: redacción de la arquitectura y elaboración del diagrama en TikZ,
  con apoyo de Codex. Descripción del intercambio de mensajes, relojes y registros CSV.
  Compilación, revisión del PDF y publicación del avance.
- Problemas encontrados: la redacción mencionaba responsables individuales y documentos
  temporales de organización.
- Solución aplicada: presentar las decisiones como acuerdos del equipo despues de acuerdos dialogados y conservar
  referencias a los archivos técnicos de la entrega.
- Corridas/archivos obtenidos: arquitectura.tex, arquitectura_tres_nodos.tex y PDF
  actualizado. Sin corridas experimentales.
- Commits o PR relacionados:
  [arquitectura y diagrama](https://github.com/BelindaTZ/GA-SUM-02-PE-U1/commit/3aa884ab78f46509769b4ccaa4522ce5278bf389).
- Próximos pasos: implementar el reloj, el registro compartido y los nodos TCP.

## Sesión: 2026-11-19 (America/Guayaquil), código compartido y sockets TCP

- Presentes: Belinda Toaquiza
- Objetivo: implementar la base común y comprobar el intercambio TCP entre tres nodos.
- Trabajo realizado: configuración, reloj Lamport y registro CSV compartidos;
  servidor y cliente TCP con JSON, delimitación, acuses y manejo de errores,
  con apoyo de Codex. Redacción de la implementación y revisión del PDF.
- Problemas encontrados: lectura parcial de mensajes y riesgo de desordenar registros
  al atender varios hilos; conexiones locales bloqueadas en el entorno restringido.
- Solución aplicada: cabecera de longitud, lectura completa, reloj protegido y escritor
  único; ejecución de las pruebas locales fuera de esa restricción.
- Corridas/archivos obtenidos: 21 pruebas correctas y validaciones TCP de 20, 100
  y 100 intercambios, con cargas de 100 y 10240 bytes, sin fallos. Código, CSV reales,
  PDF y evidencias en screenshots/preliminares. No son las corridas comparativas finales.
- Commits o PR relacionados: [base compartida, TCP y validaciones](https://github.com/BelindaTZ/GA-SUM-02-PE-U1/commit/4f6eda35ac8bb6306dc2cb202c6036ce1b79d637).
- Próximos pasos: integrar la base compartida con gRPC y ejecutar el protocolo
  experimental completo con el equipo.

## Sesión: 2026-11-19 (America/Guayaquil), servidor gRPC

- Presentes: Nixon Piguave
- Objetivo: implementar el servidor gRPC con la base compartida y comprobar su funcionamiento.
- Trabajo realizado: servidor con validación de mensajes, acuses ACK y uso de
  LamportClock y EventLogger. Código preparado con asistencia de Codex; ejecución
  manual en PowerShell con tres procesos, intercambio, concurrencia, rechazo de ID
  vacío y cierre.
- Problemas encontrados: PowerShell utilizaba un Python sin grpc_tools al ejecutar
  activate.bat; era necesario usar el mismo reloj y registro que TCP.
- Solución aplicada: invocar el Python del entorno correcto e integrar los
  componentes de src/common sin modificarlos.
- Corridas/archivos obtenidos: validación con tres intercambios correctos,
  doce eventos y seis parejas Lamport válidas.
  Dos emisores concurrentes; ID vacío rechazado sin cambiar el reloj de B (9).
  Los tres procesos terminaron. CSV, validation.json y cuatro capturas originales
  conservados; esta validación no corresponde al protocolo comparativo final.
- Commits o PR relacionados: [servidor gRPC con Lamport y registro compartido](https://github.com/BelindaTZ/GA-SUM-02-PE-U1/commit/e74e9196242ebde24689ba9ed4e9c9e7d0ca1b69).
- Próximos pasos: implementar el cliente gRPC definitivo y ejecutar el plan común
  de intercambios y las mediciones con el equipo.

## Sesión: 2026-11-20 (America/Guayaquil), cliente gRPC

- Presentes: Nixon Piguave
- Objetivo: completar el cliente gRPC y comprobarlo con el plan de intercambios del equipo.
- Trabajo realizado: cliente con canales reutilizables, RTT, validación de acuses
  y manejo de errores; script de demostración y seis pruebas. Ejecución manual en
  PowerShell con los tres nodos, mensajes de 100 y 10240 bytes y modo concurrente.
- Problemas encontrados: el entorno anterior dependía de una versión del runtime
  que ya no estaba disponible; el envío de prueba del servidor no era todavía
  un cliente reutilizable para las mediciones.
- Solución aplicada: preparar un entorno con Python 3.11.9 y las dependencias
  gRPC fijadas; implementar prepare, exchange y close usando el reloj y registro
  compartidos, con canales preparados antes del tramo medido.
- Corridas/archivos obtenidos: seis pruebas correctas y tres validaciones de veinte
  intercambios: 100 bytes secuencial, 10240 bytes secuencial y 100 bytes concurrente
  con tres emisores. En total, 60 intercambios correctos, cero fallos, 240 eventos
  y 120 parejas Lamport válidas. CSV, condiciones y capturas originales conservados.
- Commits o PR relacionados: [cliente gRPC y validación con tres nodos](https://github.com/BelindaTZ/GA-SUM-02-PE-U1/commit/3cd968bb3f04634f590dd557766cddafa71bb57b).
- Próximos pasos: entregar el cliente al responsable de experimentos para el
  protocolo completo y terminar las secciones y referencias personales del informe.

## Sesión: 2026-11-19, 00:00 a 00:30 (America/Guayaquil), script de análisis

- Presentes: Humberto Herrera
- Objetivo: preparar el análisis estadístico del bloque 4 a partir del esquema acordado,
  sin esperar las mediciones finales.
- Trabajo realizado: creación de analysis/analyze.py según ACUERDOS_TECNICOS.md:
  exclusión de calentamiento, separación por modo, mecanismo y tamaño, RTT solo con
  status=ok, media, mediana, desviación, p95, IC 95 % t de Student entre corridas,
  rendimiento con completed/elapsed_s, boxplot, barras con intervalos y tablas LaTeX.
  Dependencias de análisis fijadas en requirements.txt.
- Problemas encontrados: todavía no había CSV reales en data.
- Solución aplicada: el script termina con un mensaje de error si faltan datos y no
  genera resultados con datos de ejemplo. Se probó fuera del repositorio.
- Corridas/archivos obtenidos: analysis/analyze.py y requirements.txt. Sin mediciones.
- Commits o PR relacionados:
  [analyze.py](https://github.com/BelindaTZ/GA-SUM-02-PE-U1/commit/61fe5a331c1f7344a141e6620e44c408affe0e51),
  [requerimientos](https://github.com/BelindaTZ/GA-SUM-02-PE-U1/commit/149722e525bd43abbe8aec9439b90a81d6d25913).
- Próximos pasos: redactar el fundamento 2.4 y reunir las fuentes.

## Sesión: 2026-11-19, 22:40 a 23:20 (America/Guayaquil), fundamento 2.4 y fuentes

- Presentes: Humberto Herrera
- Objetivo: redactar el fundamento sobre fallos y seguridad.
- Trabajo realizado: redacción de falla, error y avería; clasificación de fallos;
  detección con heartbeats y timeouts; recuperación; JWT y OAuth 2.0; relación con
  los estados ok, timeout y error del CSV de latencias.
- Problemas encontrados: las primeras fuentes candidatas no eran de acceso abierto o
  no fue posible verificar todos sus datos bibliográficos.
- Solución aplicada: seleccionar dos artículos de acceso abierto de IEEE Access con
  DOI verificable y que no se repiten con las fuentes del equipo.
- Corridas/archivos obtenidos: docs/secciones/herrera/fundamento.tex y referencias.bib.
- Commits o PR relacionados:
  [referencias](https://github.com/BelindaTZ/GA-SUM-02-PE-U1/commit/885a863a06a22915a02c46cd3abf7fdfded32e81),
  [fundamento](https://github.com/BelindaTZ/GA-SUM-02-PE-U1/commit/45b85e63588e7fd218c4d049d06ef9c54653d968).
- Próximos pasos: adaptar el análisis a la estructura de datos que use el equipo.

## Sesión: 2026-11-20, 21:00 a 22:40 (America/Guayaquil), lectura por carpetas y prueba del análisis

- Presentes: Humberto Herrera
- Objetivo: preparar analyze.py para leer las corridas reales del repositorio.
- Trabajo realizado: revisión de data; las corridas se guardan en una carpeta por
  run_id, por lo que el script ahora recibe las carpetas a analizar con --input y
  no mezcla validaciones con corridas finales. README de analysis actualizado.
  Prueba con dos validaciones: TCP 8398cba5… y gRPC c1104955…, 100 bytes, secuencial.
- Problemas encontrados: Python no estaba en el PATH del equipo y pip avisó conflictos
  con paquetes ajenos al proyecto instalados en el entorno global.
- Solución aplicada: uso del lanzador py (Python 3.13.3). Las salidas generadas en la
  prueba se eliminaron porque no corresponden al experimento final.
- Corridas/archivos obtenidos: sin corridas propias. Captura preliminar de la ejecución
  en evidence/screenshots/preliminares/Herrera/. IC no calculable: una corrida por grupo.
- Commits o PR relacionados:
  [lectura por carpetas](https://github.com/BelindaTZ/GA-SUM-02-PE-U1/commit/8dda8bb4a8c886883d87039e964bb6f02efca582),
  [README del análisis](https://github.com/BelindaTZ/GA-SUM-02-PE-U1/commit/28050e577c37830a9533a02ba3a7d0d0dadc6a15),
  [carpeta de evidencias](https://github.com/BelindaTZ/GA-SUM-02-PE-U1/commit/04d4c6871c932d161dd64c2378715b696eced793).
- Próximos pasos: ejecutar el análisis con los lotes finales de TCP y gRPC y redactar
  resultados, discusión y conclusiones cuantificadas.

## Sesión: 2026-11-21 (America/Guayaquil), cierre de apartados del informe

- Presentes: Belinda Toaquiza
- Objetivo: completar los apartados individuales y su relación con el PFC.
- Trabajo realizado: redacción del análisis de transparencias ANSA y aplicación de
  TCP, gRPC y CAP a SGRA, tras revisar sus repositorios. Conclusión individual y
  aportes con commits; retiro de Estado de referencias.
- Problemas encontrados: faltaba concretar el PFC y ajustar la extensión y presentación
  de los apartados.
- Solución aplicada: usar SGRA como caso, distinguir su funcionamiento actual de las
  posibles extensiones y ajustar textos, tabla y referencias.
- Corridas/archivos obtenidos: apartados LaTeX, bibliografía y PDF actualizados.
  Sin nuevas corridas experimentales.
- Commits o PR relacionados:
  [ANSA, SGRA y cierre individual](https://github.com/BelindaTZ/GA-SUM-02-PE-U1/commit/720520fdcc023921532ccc73253bf3b39110d6a7).
- Próximos pasos: revisar la integración final del informe y participar en el video.

## Sesión: 2026-11-21 (America/Guayaquil), fundamento y conclusión de comunicación

- Presentes: Nixon Piguave.
- Objetivo: completar el fundamento 2.2, sus referencias y la conclusión individual de la implementación gRPC.
- Trabajo realizado: redacción sobre TCP/UDP, RPC, gRPC, Protocol Buffers y RMI;
  elaboración de una comparación conceptual y dos diagramas de secuencia en TikZ (se utilizo codex para estos dos diagramas en TikZ, y para la estructura en el documento de latex).
  Incorporación de dos trabajos académicos con DOI contrastados con las publicaciones
  y Crossref, y de documentación oficial. Conclusión apoyada en las validaciones
  propias y en las tablas de la comparativa con tres procesos. Sustitución del
  enlace pendiente del cliente en el apartado de aportes. Se utilizó Codex como
  apoyo para la mejora de redacción de mis borradores, la verificación de referencias fue realizado personalmente.
- Problemas encontrados: los símbolos de flechas de TikZ entraban en conflicto con la configuración de español; algunas etiquetas quedaban demasiado juntas. Biber no aceptó la ruta absoluta con el carácter del nombre de la carpeta.
- Solución aplicada: desactivar localmente los caracteres activos en las figuras, aumentar las separaciones y ejecutar Biber con rutas relativas, conservando la configuración compartida del informe.
- Corridas/archivos obtenidos: fundamento.tex, referencias.bib, conclusion_individual.tex y aportes.tex de Nixon; PDF regenerado mediante pdflatex, biber y dos pasadas finales de pdflatex, con revisión de las páginas nuevas. 
- Commits o PR relacionados:
  [fundamento de comunicación, referencias y conclusión individual](https://github.com/BelindaTZ/GA-SUM-02-PE-U1/commit/338b4d613c2348d98c57fedbaa07d4e3f7cac92f).
- Próximos pasos: participar en la grabación y montaje del video del equipo.

## Plantilla para próximas sesiones — todos los integrantes

Copiar este bloque para registrar cada sesión de trabajo real.

## Sesión: AAAA-MM-DD, HH:MM a HH:MM (America/Guayaquil)

- Presentes:
- Objetivo:
- Trabajo realizado:
- Problemas encontrados:
- Solución aplicada:
- Corridas/archivos obtenidos:
- Commits o PR relacionados:
- Próximos pasos:
