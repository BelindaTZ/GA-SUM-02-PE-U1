# Fuentes seleccionadas para las secciones de Belinda

Fecha de consulta: 18 de noviembre de 2026 (America/Guayaquil).
Estado: seis fuentes incorporadas al referencias.bib de esta carpeta; cinco se citan en el fundamento.
El fundamento teórico incluye citas a apartados efectivamente consultados. El RFC queda reservado para la sección de implementación TCP.

## Método y alcance de la comprobación

Se utilizó SciSpace para localizar y preseleccionar artículos y búsqueda web para
contrastar registros editoriales, institucionales y de estándares. Consensus y Elicit
no están disponibles como conectores en esta sesión; no se afirma haberlos usado.
En la búsqueda inicial se consultaron fichas y metadatos. Para redactar el fundamento
se obtuvieron textos completos y se leyeron los apartados indicados en LECTURA_FUNDAMENTO.md.
No se declara haber leído íntegramente todas las obras ni las 685 páginas del libro.

Los cinco DOI (cuatro artículos y un RFC) se verificaron con Crossref; el registro de
la consulta está en ../../organizacion/verificacion_fuentes_belinda.json.
El libro se verificó en la página del autor/editor y no se le asignó un DOI inexistente.
Las evidencias de indexación siguientes son de las revistas, no una exportación individual
certificada desde una sesión de Scopus. Un DOI por sí solo no demuestra indexación.

## 1. Sistemas distribuidos y transparencia: libro académico

**M. van Steen y A. S. Tanenbaum, Distributed Systems, 4.ª edición, 2023;
ejemplar consultado: versión 4.03x, febrero de 2025.**

- Clave: `belinda_vansteen2023_distributed`.
- ISBN digital: `978-90-815406-4-3` (incluido en el .bib). ISBN impreso: `978-90-815406-3-6`.
- Ambos identificadores corresponden a la cuarta edición, versión 4.03, en el [catálogo de la biblioteca KIT](https://katalog.bibliothek.kit.edu/bib/1499492).
- [Página oficial del autor/editor](https://www.distributed-systems.net/index.php/books/ds4/).
- La página oficial pide citar la cuarta edición con año 2023; la revisión 2025
  del ejemplar consultado se registra como nota y no se presenta como una nueva edición.
- Uso previsto: definición y objetivos de sistemas distribuidos, transparencia,
  arquitecturas y comunicación. Sirve como base conceptual de fundamento.tex y arquitectura.tex.
- Es un libro académico, no uno de los tres artículos de revista seleccionados.
- Se comprobó que su Figura 1.3 presenta siete transparencias. Para la persistencia
  exigida por la guía se añadió el artículo de Soiland-Reyes et al. (2024).
- La copia digital personalizada se solicita en la página del autor; no se enviaron
  datos personales ni se solicitó una copia en nombre del equipo.

## 2. CAP y decisiones de diseño: artículo de ACM, 2023

**E. A. Lee, R. Akella, S. Bateni, S. Lin, M. Lohstroh y C. Menard,
“Consistency vs. Availability in Distributed Cyber-Physical Systems”,
ACM Transactions on Embedded Computing Systems, vol. 22, n.º 5s,
art. 138, pp. 1–24, 2023.**

- Clave: `belinda_lee2023_cap`.
- DOI verificado: [10.1145/3609119](https://doi.org/10.1145/3609119).
- [SciSpace](https://scispace.com/papers/consistency-vs-availability-in-distributed-cyber-physical-cygkju0qck).
- [Ficha del grupo de investigación de los autores](https://www.icyphy.org/publications/2023_LeeEtAl_CAL_CPS/).
- [Texto depositado en NSF PAR](https://par.nsf.gov/servlets/purl/10473653).
- Uso previsto: relación entre consistencia, disponibilidad y latencia; apoyo para
  fundamento.tex y discusión de decisiones del PFC. Su contexto es ciberfísico:
  no trasladar resultados o garantías automáticamente a nuestra práctica en localhost.
- Indexación: la [ficha institucional de la revista en TU Dresden](https://fis.tu-dresden.de/portal/en/journals/transactions-on-embedded-computing-systems%280c97faf3-e054-4aaa-b8a6-ebfd4df3bad0%29.html)
  informa métricas Scopus y clasifica el trabajo como artículo con revisión por pares.
- Usar el título de la versión publicada, distinto del preprint “Distributed Real-Time Systems”.

## 3. CAP/PACELC y replicación: revisión científica, 2023

**J. Ahmed, A. Karpenko, O. Tarasyuk, A. Gorbenko y A. Sheikh-Akbari,
“Consistency issue and related trade-offs in distributed replicated systems and
databases: a review”, Radioelectronic and Computer Systems, n.º 2, pp. 171–179, 2023.**

- Clave: `belinda_ahmed2023_consistency`.
- DOI verificado: [10.32620/reks.2023.2.14](https://doi.org/10.32620/reks.2023.2.14).
- [Artículo y PDF en la revista](https://nti.khai.edu/index.php/reks/article/view/reks.2023.2.14).
- [SciSpace](https://scispace.com/papers/consistency-issue-and-related-trade-offs-in-distributed-8m3ps1en).
- Uso previsto: explicar CAP y PACELC, compromisos entre coordinación, consistencia
  y latencia, y limitaciones de diseños replicados. Es complemento conceptual;
  el sistema de mensajería de esta práctica no es una base de datos replicada.
- Indexación: la [revista declara Scopus desde 2019](https://nti.khai.edu/index.php/reks/index).
- Corrección importante: SciSpace devolvió una lista incompleta de tres autores.
  La editorial y Crossref identifican cinco; el .bib conserva los cinco correctos.

## 4. Arquitectura y mediciones: artículo de IEEE Access, 2022

**G. Blinowski, A. Ojdowska y A. Przybyłek, “Monolithic vs. Microservice
Architecture: A Performance and Scalability Evaluation”, IEEE Access,
vol. 10, pp. 20357–20374, 2022.**

- Clave: `belinda_blinowski2022_architecture`.
- DOI verificado: [10.1109/ACCESS.2022.3152803](https://doi.org/10.1109/ACCESS.2022.3152803).
- [IEEE Xplore](https://ieeexplore.ieee.org/document/9717259/).
- [SciSpace](https://scispace.com/papers/monolithic-vs-microservice-architecture-a-performance-and-30ky9e6p).
- Uso previsto: justificar que distribuir componentes puede introducir costes de
  comunicación y que el rendimiento debe medirse bajo condiciones controladas.
- Límite: compara monolitos y microservicios; no demuestra que TCP sea más rápido
  que gRPC, ni equivale a comparar sistemas centralizados y paralelos.
- Indexación: [IEEE Access declara Scopus, SCIE y Web of Science](https://ieeeaccess.ieee.org/about/bibliometrics/).

## 5. Implementación TCP: estándar primario de IETF, 2022

**W. M. Eddy, editor, “Transmission Control Protocol (TCP)”, RFC 9293,
STD 7, agosto de 2022.**

- Clave: `belinda_eddy2022_tcp`.
- DOI verificado: [10.17487/RFC9293](https://doi.org/10.17487/RFC9293).
- [Texto oficial](https://www.rfc-editor.org/rfc/rfc9293.html).
- Uso previsto: propiedades del transporte TCP, flujo de bytes, establecimiento y
  cierre de conexiones y comportamiento de envío/recepción. Consultar especialmente
  los conceptos de TCP y las secciones de comunicación de datos e interfaces.
- Justifica tratar TCP como flujo: el framing de mensajes JSON corresponde a nuestra
  aplicación. Distinguir el acuse de aplicación del ACK de transporte TCP.
- Es un estándar técnico con revisión pública; no se cuenta como artículo de revista indexada.

## 6. Transparencia de persistencia: artículo de PeerJ, 2024

**S. Soiland-Reyes, C. Goble y P. Groth, “Evaluating FAIR Digital Object and Linked
Data as distributed object systems”, PeerJ Computer Science, vol. 10, art. e1781, 2024.**

- Clave: `belinda_soiland2024_transparency`.
- DOI verificado con Crossref: [10.7717/peerj-cs.1781](https://doi.org/10.7717/peerj-cs.1781).
- [Texto completo en el repositorio de la Universidad de Ámsterdam](https://pure.uva.nl/ws/files/177495031/peerj-cs-1781.pdf).
- Consultados el apartado sobre infraestructuras middleware y la Tabla 4,
  páginas impresas 15–17 (páginas 16–18 del PDF con cubierta institucional).
- Uso: respaldar persistencia como ocultación de la desactivación/reactivación
  de elementos. No se presenta su marco completo como una taxonomía idéntica a la guía.
- Se añadió para cubrir una propiedad que no figura en la tabla de siete
  transparencias de la revisión del libro consultada.

## Cómo usarlas en el informe

- fundamento.tex: libro para conceptos y siete transparencias; Soiland-Reyes para
  persistencia; Lee y Ahmed para CAP; Blinowski para el contexto de medición de arquitecturas.
- arquitectura.tex: libro y Blinowski como apoyo conceptual; el diagrama del equipo
  debe describir el sistema realmente diseñado, sin copiar una arquitectura ajena.
- implementacion_tcp.tex: RFC 9293 para TCP y libro para comunicación por procesos.
- pregunta_ansa.tex: clasificar las propiedades observables de nuestro código y citar
  la fuente conceptual realmente consultada; no atribuir transparencias no implementadas.
- pfc.tex: adaptar los compromisos discutidos por Lee y Ahmed al PFC real del equipo.

Ejemplo de cita, al redactar una afirmación que la fuente efectivamente respalde:
`\cite{belinda_vansteen2023_distributed}`. Para varias fuentes:
`\cite{belinda_lee2023_cap,belinda_ahmed2023_consistency}`.

Estas fuentes no prueban la hipótesis de rendimiento de la práctica. Su contraste
requiere las mediciones propias de TCP/JSON y gRPC/Protobuf en condiciones equivalentes.
