# Práctica experimental U1: TCP, gRPC y Lamport

Estado: estructura inicial; implementación, mediciones e informe pendientes.

Equipo de cuatro integrantes con nombres y bloques confirmados en `EQUIPO.md`.
Código de la actividad: GA-SUM-02 / PE-U1 (renumeración confirmada por el equipo).
Repositorio público: https://github.com/BelindaTZ/GA-SUM-02-PE-U1. Video de 3 a 5 minutos: PENDIENTE.
Fecha límite: sábado 21 de noviembre de 2026, 23:59 (America/Guayaquil).

## Empezar aquí

1. Leer `PLAN_ACTIVIDAD.md`. No hay actividades formativas previas exigidas para esta práctica.
2. Consultar el reparto aceptado en `EQUIPO.md` y los formatos comunes en `ACUERDOS_TECNICOS.md`. Completar las cuentas GitHub pendientes y registrar la hipótesis antes de medir.
3. Implementar los módulos indicados en los README de cada carpeta.
4. Preparar Python 3.11 o superior y fijar versiones exactas en `requirements.txt` tras validar el entorno.
5. Ejecutar experimentos reales, análisis y verificación de Lamport; conservar los CSV sin editar.
6. Completar el informe, las evidencias y `CHECKLIST_ENTREGA.md`.

## Estructura

```text
src/
  common/           # Reloj Lamport, configuración y registro compartidos
  sockets/          # Servidor y cliente TCP con JSON
  grpc/             # Servidor y cliente gRPC
proto/              # Contrato messaging.proto
experiments/        # Plan común, mediciones y concurrencia
scripts/            # Generación proto, entorno y hashes
data/              # CSV reales y SHA256SUMS
analysis/           # Análisis y verificación de eventos reales
  figures/          # Gráficos generados
  tables/           # Tablas generadas para LaTeX
docs/               # Informe, bibliografía y figuras
  secciones/        # Fragmentos y bibliografía por integrante
  organizacion/     # Planificación del informe
evidence/
  screenshots/      # Capturas reales de los cuatro integrantes
  video/            # Guion e información del video
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

## Ejecución experimental (pendiente de integrar)

Antes de entregar, completar los comandos comprobados para la comparación con
gRPC desde un clon limpio, usando cmd.exe en Windows:

- Crear y activar `.venv`; instalar `requirements.txt`.
- Generar los módulos Python desde `proto/messaging.proto`.
- Iniciar nodo-A, nodo-B y nodo-C en localhost:5000, :5001 y :5002.
- Ejecutar TCP y gRPC por separado para reutilizar los mismos puertos.
- Ejecutar intercambios Lamport, calentamiento, corridas secuenciales y concurrentes.
- Analizar CSV, verificar causalidad y generar tablas y gráficos.
- Generar y verificar `data/SHA256SUMS` sobre los CSV conservados.

Cada comando final debe indicar su directorio de ejecución, argumentos y salidas.

## Compilación del informe

Archivo principal previsto: `docs/guia1_practica.tex`. Es una plantilla por completar.
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
El informe está dividido por responsable en `docs/secciones/`. Consultar `docs/README.md` antes de editar. El archivo principal incorpora los fragmentos y `configuracion.tex` reúne paquetes y bibliografías. El PDF compilado es una vista previa con contenido y fuentes pendientes; todavía no cumple los requisitos del informe final. La planificación de `docs/organizacion/` se muestra después de la portada del PDF de trabajo, para que todos vean el reparto; se retirará de la entrega final.

## Autoría e inteligencia artificial

Registrar aportes reales y enlaces a commits en `EQUIPO.md` y en el informe.
La organización inicial y las plantillas fueron preparadas con asistencia de IA;
el equipo debe revisar y declarar su uso. No atribuir esta preparación a commits
personales de los integrantes ni presentar plantillas como resultados.
