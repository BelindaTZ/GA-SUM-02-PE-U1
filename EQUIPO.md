# Equipo y reparto acordado

Estado: propuesta aceptada por los cuatro integrantes, según confirmación del equipo.

Integrantes y bloques confirmados por el equipo. Completar las cuentas GitHub de los integrantes 2, 3 y 4 y el escenario del PFC antes de implementar.
Los mensajes y CSV se definen en `ACUERDOS_TECNICOS.md`.
Los roles distribuyen responsabilidad; los cuatro deben entender y poder demostrar ambos mecanismos.

## Modalidad: cuatro bloques con entregas consecutivas

Flujo principal: 1 (base y TCP) -> 2 (gRPC) -> 3 (experimentos) -> 4 (análisis).
No exige esperar sin trabajar: una vez acordadas las interfaces, pueden adelantarse tareas.
Las mediciones finales requieren ambos mecanismos funcionando; el análisis real requiere los CSV.

| Integrante | Nombre / GitHub | Bloque principal | Informe que debe entregar escrito |
|---|---|---|---|
| 1 | TOAQUIZA ZAMBRANO BELINDA BETZABETH / BelindaTZ | Base compartida y TCP | Objetivo, hipótesis previa, arquitectura e implementación TCP |
| 2 | PIGUAVE MONTAÑO NIXON ANTONIO / GitHub pendiente | gRPC equivalente a TCP | Comunicación RPC/gRPC, contrato proto e implementación gRPC |
| 3 | EMANUEL PINO JULIANA ROMINA / GitHub pendiente | Corridas y verificación Lamport | Protocolo experimental, entorno y verificación de Lamport |
| 4 | HERRERA BARCO HUMBERTO ALDAIR / GitHub pendiente | Análisis estadístico y salidas LaTeX | Resultados y primera versión de la comparación cuantitativa |

### Bloque 1: Belinda prepara la base y TCP

- Implementar los nodos y respetar los campos de mensajes y CSV de `ACUERDOS_TECNICOS.md`. Documentar los comandos públicos y registrar la hipótesis antes de medir.
- Implementar reloj Lamport y registro compartido en src/common; configuración de tres nodos.
- Implementar servidor y cliente TCP: framing, JSON, acuses, timeouts y errores.
- Entregar una ejecución funcional de tres nodos con un intercambio trazable; documentar instalación y comandos TCP.
- Escribir las secciones asignadas, sin asumir resultados de rendimiento.

Entrega al integrante 2: TCP funcional, utilidades compartidas e interfaces documentadas.
Tres aportes posibles: reloj/registro; servidor TCP y framing; cliente e integración de nodos.

### Bloque 2: Nixon implementa gRPC

- Definir proto/messaging.proto y generación reproducible de los módulos Python.
- Implementar servidor y cliente gRPC reutilizando reloj y registro del bloque 1.
- Igualar carga útil, acuses, comportamiento Lamport y parámetros de conexión documentados para una comparación justa.
- Comprobar tres nodos e intercambio trazable; añadir dependencias compatibles y comandos gRPC al README.
- Escribir las secciones asignadas e incluir el contrato en el informe.

Entrega al integrante 3: ambos mecanismos ejecutables y procedimiento de arranque/parada.
Tres aportes posibles: contrato y generación; servidor gRPC; cliente e integración equivalente.

### Bloque 3: Emanuel ejecuta los experimentos

- Crear runner y plan común: 20 intercambios por mecanismo, tamaños de aproximadamente 100 B y 10 KB, calentamiento, cinco corridas de 100 envíos y concurrencia.
- Registrar el entorno y duración de lotes, conservar CSV sin editar e identificar fallos y calentamiento.
- Implementar verify_lamport.py y demostrar causalidad y un caso concurrente real.
- Generar y verificar SHA256SUMS de los CSV definitivos; documentar cómo repetir las corridas.
- Escribir protocolo, condiciones y comprobación Lamport.

Entrega al integrante 4: CSV completos y documentados, entorno, manifiesto y verificación real.
Tres aportes posibles: runner común; concurrencia y entorno; verificación de Lamport y validación de trazas.

### Bloque 4: Herrera analiza los datos

- Implementar analyze.py con media, mediana, desviación estándar, p95 y mensajes/segundo; separar tamaños y modos.
- Generar boxplot a 300 DPI, barras con intervalos definidos y tablas LaTeX desde los CSV reales.
- Incorporar resultados al informe y redactar comparación cuantificada e interpretación inicial de la hipótesis.
- Documentar comandos de análisis; comprobar reproducción desde los datos conservados.

Entrega al equipo: análisis reproducible, tablas, gráficos y sección de resultados integrada.
Tres aportes posibles: métricas y rendimiento; gráficos e intervalos; tablas LaTeX e integración del análisis.

## Reparto de los apartados del informe

La matriz completa de redacción se conserva en `docs/organizacion/reparto_informe.tex`.
Cada integrante edita exclusivamente sus fragmentos y bibliografía en `docs/secciones/`,
según las instrucciones de `docs/README.md`. El principal solo une las secciones.
Nixon coordina resumen y abstract al finalizar; todos revisan su contenido.
Belinda integra y compila los textos ya escritos por cada responsable.

## Trabajo repartido para no sobrecargar el último bloque

- Cada integrante escribe su sección directamente en LaTeX y su conclusión individual de al menos 150 palabras.
- Bibliografía: cada uno busca y verifica dos fuentes de su tema; el equipo selecciona al menos seis sin duplicados y comprueba requisitos de actualidad, indexación y DOI.
- Fundamento U1: integrante 1, sistemas distribuidos/ANSA/CAP; 2, comunicaciones y RMI; 3, Lamport/vectoriales; 4, fallos y seguridad.
- Integrante 1 coordina integración y compilación del informe y PDF SGA, con textos ya escritos por todos.
- Integrante 2 coordina guion y montaje del video; los cuatro aportan rostro y voz.
- Integrante 3 organiza índice de capturas y datos; cada persona toma su captura en su propio equipo.
- Integrante 4 coordina la revisión de cifras y enlaces a tablas/gráficos; todos revisan discusión, aplicación al PFC y amenazas a validez.
- Cada persona registra sus sesiones en BITACORA.md, sus aportes y enlaces a commits.

## Qué pueden adelantar mientras esperan la entrega anterior

- Integrante 2: contrato gRPC después del acuerdo inicial de mensajes y acuses.
- Integrante 3: runner y verificador usando el esquema acordado; las pruebas finales requieren los mecanismos reales.
- Integrante 4: análisis y generación de tablas a partir del esquema acordado; los resultados finales requieren mediciones reales.
- Todos: fundamento, referencias verificadas, instalación local y preparación de evidencias.

No crear datos de prueba dentro de data ni presentarlos como mediciones.

## Calendario sugerido para el cierre del sábado 21/11/2026 a las 23:59

- 18/11: acuerdo inicial y bloque 1; los demás adelantan tareas independientes.
- 19/11: cerrar bloque 2 e integración; bloque 3 prepara y comienza corridas cuando ambos funcionen.
- 20/11: completar corridas y bloque 3; bloque 4 analiza; todos terminan sus secciones y capturas.
- 21/11: integrar resultados, reproducir, compilar, grabar video y entregar con margen.

Ajustar horarios reales entre los cuatro: no son sesiones ya realizadas.
Cada integrante hace al menos tres commits significativos propios; el historial del equipo debe abarcar al menos tres días reales distintos.
No dejar todo el trabajo del integrante 4 para el último día. Si una entrega falla, su responsable la corrige con apoyo del siguiente.
Todos deben entender y poder demostrar ambos mecanismos, independientemente del reparto.

## Aportes reales (completar al realizarlos)

| Integrante | Aporte comprobable | URL del commit |
|---|---|---|

## Hipótesis previa a medir

PENDIENTE: mecanismo esperado, tamaño de carga y justificación. Registrar fecha y commit antes de las corridas.

## PFC del equipo

PENDIENTE: describir el proyecto y los escenarios concretos para TCP y gRPC.
