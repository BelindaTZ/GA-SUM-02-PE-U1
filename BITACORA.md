# Bitácora del equipo

Registrar únicamente trabajo realizado y participantes reales.

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

## Plantilla para próximas sesiones

## Sesión: AAAA-MM-DD, HH:MM a HH:MM (America/Guayaquil)

- Presentes:
- Objetivo:
- Trabajo realizado:
- Problemas encontrados:
- Solución aplicada:
- Corridas/archivos obtenidos:
- Commits o PR relacionados:
- Próximos pasos:
