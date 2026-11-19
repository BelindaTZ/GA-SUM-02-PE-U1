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

El archivo principal solo ordena e incorpora las secciones con input.
configuracion.tex reúne los paquetes y los archivos bibliográficos.
Belinda coordina cambios en esos dos archivos; los demás editan su carpeta y
solicitan la integración de nuevas secciones o paquetes para evitar conflictos.
La separación reduce conflictos, pero un error de LaTeX en un fragmento puede
impedir compilar el conjunto: comprobar la compilación antes de subir cambios.

Cada carpeta tiene conclusion_individual.tex, aportes.tex y referencias.bib propios.
Usar claves bibliográficas con el prefijo del responsable (belinda_, nixon_,
emanuel_ o herrera_). El principal carga las cuatro bibliografías y referencias.bib,
reservado para fuentes compartidas verificadas. Una obra debe tener una sola entrada;
los demás pueden citar su clave sin volver a agregarla.

## Compilación desde esta carpeta

```bat
pdflatex -interaction=nonstopmode -halt-on-error guia1_practica.tex
biber guia1_practica
pdflatex -interaction=nonstopmode -halt-on-error guia1_practica.tex
pdflatex -interaction=nonstopmode -halt-on-error guia1_practica.tex
```

Requiere los paquetes indicados en el README raíz, incluidos csquotes y biblatex-ieee.
El PDF actual es una vista previa sin contenido experimental ni bibliografía verificada.
La tabla de reparto se conserva como planificación en organizacion/reparto_informe.tex;
no se incorpora al informe académico.

## Entrega SGA

entrega_sga/ contiene un documento independiente de UNA página con los cuatro
integrantes y la URL pública completa en una línea. No es una segunda versión del informe.
Compilar desde entrega_sga con pdflatex entrega_sga.tex. No requiere Biber.
Subir al SGA ese PDF identificativo; el informe completo se conserva aquí y en GitHub.

Los .aux, .bcf, .bbl, .blg, .log, .out y .run.xml son auxiliares locales ignorados por Git.
Las imágenes temporales de revisión no forman parte del repositorio.
