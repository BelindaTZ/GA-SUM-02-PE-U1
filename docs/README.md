# Cómo trabajar en el informe

Compilar desde docs, siempre el archivo guia1_practica.tex. Los archivos de secciones
son fragmentos: no llevan documentclass, preámbulo ni begin/end document.
No compilar cada fragmento de forma independiente.

| Integrante | Edita sus textos y referencias en |
|---|---|
| Belinda Toaquiza | secciones/belinda/ |
| Nixon Piguave | secciones/nixon/ |
| Emanuel Pino | secciones/emanuel/ |
| Humberto Herrera | secciones/herrera/ |

## Qué redacta cada integrante

| Integrante | Su parte del fundamento | Otras secciones principales |
|---|---|---|
| Belinda | 2.1: sistemas distribuidos, centralizados/paralelos, ANSA y CAP | 1, 3.1, 4.1 y 9.1: objetivo/hipótesis, arquitectura y diagrama, implementación TCP y pregunta ANSA. |
| Nixon | 2.2: TCP/UDP, RPC, gRPC, Protobuf, RMI y secuencias | 3.2 y 4.2: contrato e implementación gRPC; coordina resumen y abstract. |
| Emanuel | 2.3: sincronización, Lamport, causalidad y relojes vectoriales | 5, 8, 9.2 y 9.3: protocolo, verificación Lamport y preguntas sobre nodos. |
| Herrera | 2.4: fallos, recuperación y seguridad JWT/OAuth 2.0 | 6, 7 y 10: resultados, discusión y conclusiones cuantificadas. |

La teoría de TCP la explica Nixon; su código y la explicación de ese código corresponden a Belinda.
La teoría de Lamport y el verificador corresponden a Emanuel; el reloj compartido lo programa Belinda.
Todos redactan conclusión individual y aportes, verifican sus fuentes y contribuyen a la discusión y al PFC.

El archivo principal solo ordena e incorpora las secciones con input.
configuracion.tex reúne los paquetes y los archivos bibliográficos.
Belinda coordina cambios en esos dos archivos; los demás editan su carpeta y
solicitan la integración de nuevas secciones o paquetes para evitar conflictos.
La separación reduce conflictos, pero un error de LaTeX en un fragmento puede
impedir compilar el conjunto: comprobar la compilación antes de subir cambios.

Cada carpeta tiene conclusion_individual.tex, aportes.tex y referencias.bib propios.
Usar claves bibliográficas con el prefijo del responsable (belinda_, nixon_,
emanuel_ o herrera_). La configuración carga únicamente las cuatro bibliografías
de los integrantes. Una obra debe tener una sola entrada, en la carpeta de quien
la incorpora; los demás pueden citar su clave sin volver a agregarla.

## Compilación desde esta carpeta

```bat
pdflatex -interaction=nonstopmode -halt-on-error guia1_practica.tex
biber guia1_practica
pdflatex -interaction=nonstopmode -halt-on-error guia1_practica.tex
pdflatex -interaction=nonstopmode -halt-on-error guia1_practica.tex
```

Requiere los paquetes indicados en el README raíz, incluidos csquotes y biblatex-ieee.
El PDF es un borrador: contiene objetivos, el fundamento de Belinda con citas y el contrato de Nixon; los resultados experimentales y las demás secciones siguen pendientes.
Las dos páginas de organización están visibles justo después de la portada del PDF de trabajo.
Su fuente es organizacion/reparto_informe.tex. Se retirará de la entrega final
quitando su input y el clearpage siguiente del archivo principal.

## Entrega SGA

El documento identificativo de una página para el SGA se prepara aparte, fuera
de esta carpeta y del repositorio. Aquí se mantiene únicamente el informe de la práctica.

Los .aux, .bcf, .bbl, .blg, .log, .out y .run.xml son auxiliares locales ignorados por Git.
Las imágenes temporales de revisión no forman parte del repositorio.
