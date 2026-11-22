# Práctica experimental U1: TCP, gRPC y Lamport

Estado: implementación TCP/gRPC, mediciones y análisis disponibles. Informe en
revisión de cierre, con el enlace del video de respaldo disponible.

Equipo: Belinda Toaquiza, Nixon Piguave, Emanuel Pino y Humberto Herrera.
Código de la actividad: GA-SUM-02 / PE-U1 (renumeración confirmada por el equipo).
Repositorio público: https://github.com/BelindaTZ/GA-SUM-02-PE-U1.

Video de respaldo: https://youtu.be/WcDUWUDQjY4?si=yCHKAwJTiAjj3RB_
Fecha límite: sábado 21 de noviembre de 2026, 23:59 (America/Guayaquil).

## Empezar aquí

1. Preparar el entorno con las instrucciones siguientes.
2. Consultar los comandos de [ejecución experimental](experiments/README.md).
3. Reproducir el análisis con los CSV de
   `data/comparativa_procesos_20261121_150936/`, separando sockets y gRPC.
4. Consultar el [índice de evidencias](evidence/screenshots/INDICE.md) y compilar
   el informe desde `docs/`.

## Preparación del entorno

Se requiere Python 3.11 o superior. Desde la raíz, en `cmd.exe` de Windows:

```bat
python -m venv .venv
.venv\Scripts\activate.bat
python -m pip install -r requirements.txt
python -m scripts.generate_proto
```

Las versiones están fijadas en `requirements.txt`; el entorno utilizado para las
mediciones se registra en `environment.json` de cada mecanismo. La generación
Protobuf es necesaria antes de ejecutar las pruebas o los nodos gRPC.

## Estructura

```text
src/
  common/           # Reloj Lamport, configuración y registro compartidos
  sockets/          # Servidor y cliente TCP con JSON
  grpc/             # Servidor y cliente gRPC
proto/              # Contrato messaging.proto
experiments/        # Plan común, mediciones y concurrencia
scripts/            # Generación Protobuf y validaciones TCP/gRPC
data/              # CSV reales y SHA256SUMS
analysis/           # Análisis y verificación de eventos reales
  figures/          # Gráficos generados
  tables/           # Tablas generadas para LaTeX
docs/               # Informe, bibliografía y figuras
  secciones/        # Fragmentos y bibliografía por integrante
evidence/
  screenshots/      # Capturas reales de los cuatro integrantes
  video/            # Enlace al video de respaldo
```

## Validación TCP disponible

Desde la raíz, con Python 3.11 o superior, ejecutar:

```bat
python -m unittest discover -s tests -v
python -m scripts.demo_tcp --messages 20 --payload-bytes 100
python -m scripts.demo_tcp --messages 100 --payload-bytes 100
python -m scripts.demo_tcp --messages 100 --payload-bytes 10240
```

La validación TCP utiliza la biblioteca estándar y crea tres procesos en localhost,
puertos 5000, 5001 y 5002. Cada ejecución guarda sus CSV en una carpeta nueva
`data/tcp_validacion_<run_id>/`. El detalle de mensajes, integración, errores y
cierre está en `src/sockets/README.md`. Estas comprobaciones no sustituyen las
corridas del protocolo experimental final.

## Ejecución experimental

El ejecutor arranca tres procesos independientes en localhost para cada mecanismo. Los comandos de instalación, corridas, verificación de Lamport y análisis están en [Ejecución experimental](experiments/README.md). Los datos de los lotes que sustentan el informe están en [la comparativa con tres procesos](data/comparativa_procesos_20261121_150936).

## Compilación del informe

Archivo principal: `docs/guia1_practica.tex`.
Usar pdfLaTeX y Biber (TeX Live o MiKTeX). Desde `docs`:

```bat
pdflatex guia1_practica.tex
biber guia1_practica
pdflatex guia1_practica.tex
pdflatex guia1_practica.tex
```

Paquetes: babel (español e inglés), fontenc, inputenc, geometry, amsmath,
booktabs, listings, graphicx, tikz, longtable, biblatex (estilo ieee), csquotes y hyperref.
Incorporar la plantilla institucional del LMS si es obligatoria.
El PDF compilado final debe quedar en `docs/guia1_practica.pdf`.
El informe está dividido por responsable en `docs/secciones/`. El archivo
principal incorpora los fragmentos y `configuracion.tex` reúne paquetes y
bibliografías. El resumen bilingüe está incorporado y el documento incluye las
secciones y los resultados de la práctica. Las guías internas de coordinación
se conservan localmente y están excluidas de Git y del PDF.

## Autoría e inteligencia artificial

Los aportes y sus commits se documentan en el informe; las sesiones se registran
en `BITACORA.md`. Los usos de asistencia de IA se declaran en el documento y en
los apartados de los integrantes que la utilizaron. Cada integrante revisa y
comprende los contenidos y las ejecuciones que presenta.
