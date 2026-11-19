# Análisis de la actividad y plan de trabajo

## Fuentes revisadas y diferencias

Se revisaron el texto adjunto de la tarea y el PDF local REPORTEPDF (4 páginas).
Son requisitos de la actividad; no autorizan fabricar evidencias ni sustituir el trabajo personal.

| Tema | Texto de la tarea | Guía PDF | Criterio de preparación |
|---|---|---|---|
| Código | Numeración anterior del enunciado | Sin ese código en los datos generales | GA-SUM-02 / PE-U1: renumeración del docente confirmada por el equipo |
| Python | 3.11+ | 3.10+ | Usar 3.11+ |
| Bibliografía | >=5 recientes, últimos 5 años; >=2 artículos indexados con DOI verificable | >=6 referencias; procedimiento pide referencias IEEE con DOI, pero lista libros y obras antiguas | Preparar >=6 fuentes recientes, >=2 artículos indexados y verificar todos los DOI; consultar alcance de DOI y uso de clásicos |
| Eventos | CSV | JSON para los 20 intercambios | CSV como base; exportar también JSON desde eventos reales |
| Contrato proto | /proto/ | Anexo: /src/grpc/messaging.proto | Fuente única en /proto/; documentar ruta; confirmar si exigen una copia en el anexo |
| Informe | 12 apartados sin extensión mínima explícita | >=10 páginas de contenido, resumen bilingüe de 200 palabras, conclusiones individuales >=150 palabras | Incorporar ambos; aclarar si las 200 palabras son por idioma |

Según la aclaración del equipo, las actividades formativas previas fueron eliminadas y no son requisitos de esta práctica. La arquitectura se elaborará directamente para esta actividad.

No validar ni copiar automáticamente los datos bibliográficos de la guía: comprobar cada obra y DOI en su fuente.

## Qué hay que construir

Un mismo sistema de mensajería en dos implementaciones: TCP/JSON y gRPC/Protocol Buffers.
Tres procesos identificados como nodo-A, nodo-B y nodo-C, en localhost:5000/5001/5002.
Cada nodo podrá enviar y recibir; definir cómo se coordinan servidor y cliente de cada nodo.
Elegir procesos locales inicialmente; Docker es opcional y exige docker-compose.yml si se usa.

Compartir reloj Lamport, plan de mensajes y registro para comparar en condiciones equivalentes.
Para TCP definir framing (longitud o delimitador): una lectura recv no equivale necesariamente a un mensaje.
Incrementar el reloj antes de enviar y actualizar a max(local, recibido)+1 al recibir.
Proteger reloj y escritura de logs frente a acceso concurrente; registrar también los acuses si transportan reloj.

## Experimento mínimo

- 20 intercambios entre los tres nodos por mecanismo, con el mismo plan; conservar envío y recepción.
- Identificar cada mensaje y su corrida para enlazar sus eventos sin ambigüedad.
- RTT con time.perf_counter(): 100 envíos por corrida.
- Dos tamaños de carga: aproximadamente 100 bytes y 10 KB; fijar bytes exactos y distinguir carga útil del tamaño serializado.
- Por mecanismo y tamaño: una corrida previa de calentamiento descartada del análisis y al menos cinco corridas válidas de 100 envíos.
- Base secuencial mínima: 2 mecanismos x 2 tamaños x 5 corridas x 100 = 2000 RTT válidos, más calentamiento.
- Añadir una prueba con los tres clientes simultáneos para ambos mecanismos; se recomienda repetir la misma matriz en modo concurrente.
- Definir si los 100 envíos concurrentes son totales o por cliente y documentarlo sin mezclar denominadores.
- Registrar SO, CPU, RAM, Python, dependencias, modalidad de despliegue y condiciones de conexión, acuses, errores y timeouts.
- Usar tiempo total del lote para mensajes/segundo; no derivarlo de la suma de RTT superpuestos en concurrencia.
- Conservar calentamiento y fallos identificados en crudo; excluirlos con criterios explícitos del análisis.

## Análisis que debe salir de scripts

Agrupar por mecanismo, tamaño y modo de ejecución. Calcular media, mediana, desviación estándar,
p95 y mensajes/segundo; explicar cómo se agregan las corridas y qué representan los intervalos.
Generar boxplot y barras con intervalos; PNG a 300 DPI y tablas LaTeX reproducibles.
Verificar para cada mensaje C(recepción)>C(envío), con IDs y datos reales.
Mostrar dos eventos concurrentes de distintos nodos con igual reloj y explicar la limitación:
igualdad de relojes por sí sola no demuestra concurrencia; justificar ausencia de relación causal con el plan y trazas.
Si no aparece ese caso, ejecutar un escenario real controlado con envíos independientes, sin alterar logs.

## Contenido del informe

1. Portada: cuatro integrantes, código GA-SUM-02 / PE-U1, fecha y URL pública.
2. Resumen bilingüe; objetivo e hipótesis registrada antes de medir.
3. Fundamento U1: sistemas distribuidos, ocho transparencias ANSA, comparación con centralizados/paralelos,
   CAP, TCP/UDP, RPC/gRPC, RMI, secuencias, Lamport, relojes vectoriales, fallos y seguridad JWT/OAuth 2.0.
4. Arquitectura de los tres nodos, diagrama TikZ y contrato .proto.
5. Implementación y fragmentos breves de código real.
6. Protocolo y máquina, tamaños, repeticiones, calentamiento y concurrencia.
7. Resultados mediante tablas y gráficos generados.
8. Discusión: latencia, variabilidad, rendimiento, desarrollo, tipado, errores, hipótesis, PFC y amenazas a validez.
9. Verificación Lamport con evidencia real y explicación matemática.
10. Conclusiones cuantificadas y cuatro conclusiones individuales de >=150 palabras.
11. Aportes con enlaces a commits, declaración IA y bibliografía verificada.
12. Preguntas obligatorias: ANSA y transparencias faltantes; fallo de un nodo y relojes restantes;
    elección TCP/gRPC para el PFC desde CAP; efecto del número de nodos sobre el ordenamiento.
    La pregunta de “convergencia” requiere aclarar que Lamport no sincroniza relojes físicos ni garantiza igualdad;
    si se comparan números de nodos, obtener datos adicionales reales.

Mínimo 10 páginas de contenido, excluyendo portada y bibliografía. No rellenar con resultados inventados.

## Organización y calendario sugerido

- 18/11: acordar arquitectura, hipótesis, campos CSV y responsabilidades; comenzar código.
- 19/11: completar TCP/gRPC y ejecutar integración con tres nodos; registrar avances propios.
- 20/11: corridas reales y concurrentes, verificación Lamport, análisis, capturas en las cuatro máquinas y avance del informe y bibliografía.
- 21/11: terminar informe y video con todos; clonar, reproducir análisis y compilar; revisar repositorio público, URL y PDF SGA. Entregar antes de las 23:59 del sábado 21 de noviembre de 2026 (America/Guayaquil).

Es una propuesta, no un registro de trabajo. Cada integrante necesita >=3 commits significativos;
el historial del equipo debe abarcar >=3 días reales distintos. No retrofechar commits.
