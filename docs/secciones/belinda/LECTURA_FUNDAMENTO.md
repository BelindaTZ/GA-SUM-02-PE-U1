# Registro de lectura para el fundamento de Belinda

Fecha de consulta: 18/11/2026. Este registro identifica apartados consultados;
no es una bitácora de sesiones ni una afirmación de lectura integral de todas las obras.
Las copias de consulta permanecen fuera del repositorio y no se redistribuyen con él.

| Fuente | Apartados efectivamente consultados | Uso en el borrador |
|---|---|---|
| van Steen y Tanenbaum, cuarta edición, revisión 4.03x (febrero de 2025) | Sección 1.1, pp. 3–8; sección 1.2.2, pp. 11–15 y Figura 1.3; nota sobre paralelismo y clústeres, pp. 33–34; linealizabilidad, p. 400 | Concepto, centralización lógica/física, fallos parciales, comparación de modelos y siete transparencias |
| Lee et al., 2023, DOI 10.1145/3609119 | Introducción y discusión inicial, pp. 138:2–138:4 | CAP, prioridades por aplicación y ejemplos ciberfísicos |
| Ahmed et al., 2023, DOI 10.32620/reks.2023.2.14 | Secciones sobre replicación, CAP, PACELC y compromisos, pp. 172–173 | Coordinación de réplicas y relación con latencia |
| Blinowski et al., 2022, DOI 10.1109/ACCESS.2022.3152803 | Introducción y fundamento, pp. 20357–20359; amenazas y conclusiones, pp. 20371–20372 | Cautela al generalizar resultados de arquitecturas y plataformas |
| Soiland-Reyes et al., 2024, DOI 10.7717/peerj-cs.1781 | Infraestructuras middleware y Tabla 4, pp. 15–17 del artículo | Transparencia de persistencia |

## Acceso a los textos

- Libro: [copia pública consultada](https://fan1x.github.io/data/2025-26/pds/Distributed_Systems_4.pdf),
  contrastada con la [página oficial de la cuarta edición](https://www.distributed-systems.net/index.php/books/ds4/).
  El ejemplar se identifica como 4.03x, febrero de 2025; se corrigió la nota del .bib.
- Lee: [depósito de NSF PAR](https://par.nsf.gov/servlets/purl/10473653).
- Ahmed: [PDF editorial](https://nti.khai.edu/index.php/reks/article/download/reks.2023.2.14/2075/3849).
  Se utilizó esta ruta porque el repositorio alternativo presentó un error de certificado;
  no se desactivó la comprobación TLS.
- Blinowski: [PDF de IEEE Xplore](https://ieeexplore.ieee.org/ielx7/6287639/9668973/09717259.pdf).
- Soiland-Reyes: [versión publicada en UvA-DARE](https://pure.uva.nl/ws/files/177495031/peerj-cs-1781.pdf).

## Criterios de redacción

El texto es una síntesis con citas, no una reproducción de párrafos del libro.
Las tablas son comparaciones adaptadas para la actividad, con sus fuentes indicadas.
El ejemplo de inventario es conceptual y no se presenta como ejecución o medición.
No se atribuye al libro la categoría de persistencia que no aparece en su Figura 1.3.
La clasificación pedida por la guía combina categorías que no son idénticas en todos
los marcos consultados; por eso se identifica el origen de cada parte de la síntesis.
Los resultados de monolitos/microservicios no se trasladan a TCP/gRPC. La discusión
sobre CAP tampoco se presenta como una propiedad demostrada por medir RTT.

La redacción fue asistida por Codex y requiere revisión y comprensión por el equipo;
la declaración de uso de IA del documento fue actualizada para reflejar este apoyo.
