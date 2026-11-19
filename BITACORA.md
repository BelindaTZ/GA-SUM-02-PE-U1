# Bitácora del equipo

Actividad: GA-SUM-02 / PE-U1.
Cada integrante registra sus sesiones con fecha, participantes, trabajo realizado,
problemas, soluciones y enlaces a sus commits. Horarios en America/Guayaquil.

## 2026-11-18 — Preparación y organización del trabajo

- **Responsable:** Belinda Toaquiza, con asistencia de Codex.
- **Trabajo realizado:** revisión de la guía, preparación y publicación de la
  estructura inicial del repositorio. Registro del reparto aceptado por el equipo,
  acuerdos de mensajes y CSV, y división del informe LaTeX por integrante.
- **Problemas y solución:** se corrigieron diferencias del enunciado según las
  aclaraciones recibidas y se ajustó la organización del documento.
- **Commits:** [plantillas](https://github.com/BelindaTZ/GA-SUM-02-PE-U1/commit/705a71fa4d5666edf5c5f5ea52dbc1f577717082),
  [acuerdos](https://github.com/BelindaTZ/GA-SUM-02-PE-U1/commit/33e3f8b2ffe4396254b570280f8ec2127950936c),
  [división del informe](https://github.com/BelindaTZ/GA-SUM-02-PE-U1/commit/469680162cc3d4ba2cd4142e1cceddcae59bc9f1).

## 2026-11-18 — Objetivos, hipótesis y fuentes

- **Responsable:** Belinda Toaquiza.
- **Trabajo realizado:** redacción de objetivos e hipótesis y compilación del PDF.
  Selección de cinco fuentes para sus secciones; verificación de datos bibliográficos,
  DOI e ISBN e incorporación al archivo referencias.bib individual.
- **Problemas y solución:** se corrigieron autores incompletos y el formato de
  una entrada bibliográfica; se validó el archivo con Biber.
- **Estado:** objetivos y fuentes incorporados al repositorio en esta actualización.
- **Próximos pasos:** redactar el fundamento con citas y preparar la arquitectura.

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
- Commits o PR relacionados: pendiente de registrar el primer commit y su enlace.
- Próximos pasos: revisar el contrato e implementar el servidor gRPC usando
  el reloj y el registro compartidos de Belinda cuando estén disponibles.

## Plantilla para nuevas sesiones — todos los integrantes

Copiar este bloque para registrar cada sesión de trabajo real.

### Sesión: AAAA-MM-DD, HH:MM a HH:MM (America/Guayaquil)

- **Integrantes presentes:**
- **Objetivo:**
- **Trabajo realizado:**
- **Problemas encontrados:**
- **Solución aplicada:**
- **Archivos o corridas obtenidas:**
- **Commits o PR relacionados:**
- **Próximos pasos:**
