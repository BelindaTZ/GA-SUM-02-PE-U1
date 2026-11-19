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
