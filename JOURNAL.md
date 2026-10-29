# Revista elegida

_Responsable: Isabela Quintero Murillo_

- **Revista:** *Bioinformatics* (Oxford University Press), tipo de artículo **Original Paper**
- **Guía de autores:** https://academic.oup.com/bioinformatics/pages/author-guidelines
- **Plantilla LaTeX:** OUP General Template (oficial de Oxford University Press, clase `oup-authoring-template`):
  https://www.overleaf.com/latex/templates/template-for-oxford-bioinformatics-journal-new-version/zjrmbrmtrytg
- **Proyecto en Overleaf:** https://www.overleaf.com/project/6ae06e5f2414bfdc8838fd2a
  (para entrar, cada integrante necesita invitación desde el botón Share)
- **Fuentes del artículo en el repositorio:** `articulo/main.tex` y `articulo/references.bib`
- **Idioma del artículo:** español (el enunciado lo permite)

## Por qué esta revista

- Está en la lista de revistas sugeridas en el enunciado, que la describe como la revista de referencia del área.
- Su alcance incluye explícitamente artículos sobre bases de datos y software para biología molecular
  computacional, y exige usar datos biológicos reales (usamos PanTEon Database).
- Exige que los datos estén en repositorios públicos estables y que el código esté disponible en una URL
  estable (por ejemplo GitHub): coincide con cómo está organizado este proyecto (datos en Zenodo, código en GitHub).
- Su formato *Original Paper* se ajusta a lo que presenta el artículo: un modelo de datos, sus decisiones de
  diseño, las consultas y el benchmark. Su límite es de 7 páginas; en este ejercicio el docente autorizó
  superarlo (ver la norma "Extensión máxima").
- Tiene plantilla oficial en Overleaf, lo que permite que los cuatro integrantes escriban en el mismo documento.

## Normas aplicadas

| Norma | Requisito de la revista | Cómo se aplicó |
| --- | --- | --- |
| Plantilla | Plantilla oficial de OUP | Se usa la clase `oup-authoring-template` sin modificarla, con las opciones `unnumsec, namedate, webpdf, contemporary, large`. Para el español se carga `babel` (`spanish, es-tabla, es-noshorthands`) y se cambian los títulos fijos "Abstract" y "Keywords" por "Resumen" y "Palabras clave" desde `main.tex` |
| Estructura del artículo | Original Paper. La guía propone Introducción, *System and methods*, *Algorithm*, *Implementation* y *Discussion*, con flexibilidad | Se usa Introducción, Trabajo relacionado, Materiales y métodos, Resultados, Discusión y Conclusiones, que es compatible con la guía y sigue la sección 5.2 del enunciado |
| Resumen estructurado | Apartados Motivation, Results, Availability and Implementation, Contact y Supplementary Information | Los cinco apartados van en español: Motivación, Resultados, Disponibilidad e implementación, Contacto e Información suplementaria |
| Extensión del resumen | Máximo recomendado: 150 palabras. Sin citas ni ecuaciones | Menos de 150 palabras, sin citas ni ecuaciones |
| Estilo de citas | Autor-año (`oup-abbrvnat` con BibTeX) | Opción `namedate` de la clase, `\bibliographystyle{oup-abbrvnat}` y `references.bib`. En el texto se usa `\citet` ("Autor et al. (2026)") y `\citep` ("(Autor et al., 2026)") |
| Citas de datos | Los conjuntos de datos van en la lista de referencias con la información de DataCite (autores, año, título, repositorio, identificador/DOI) | PanTEon Database v1.6.1 se cita con sus autores, año, título, versión, repositorio (Zenodo), DOI `10.5281/zenodo.19372616` y la etiqueta [dataset] |
| Citas obligatorias del enunciado | Artículo de PanTEon y repositorio de Zenodo | Ambas están en `references.bib` con DOI verificado |
| Formato de figuras | Embebidas en el texto, con su leyenda al lado. Ancho de una columna (86 mm) o de dos (178 mm). Fondo blanco. Nada de capturas de pantalla | Las figuras van dentro del texto con `figure` (una columna, `\columnwidth`) o `figure*` (dos columnas, como el diagrama del modelo). Todas se generan con Python (matplotlib/seaborn) o draw.io sobre fondo blanco, ninguna es una captura |
| Texto alternativo de las figuras | Cada figura lleva debajo de la leyenda un texto alternativo que empieza con "Texto alternativo:" | Comando `\textoalternativo{}` en `main.tex`, usado en todas las figuras |
| Formato de tablas | Embebidas, numeradas, con un título breve y autoexplicativas. Notas al pie con letras minúsculas. Las anchas van en `table*` | Todas las tablas son `tabular` reales (nunca imágenes), con título y número automático. Las tablas anchas (decisiones de diseño, tiempos del benchmark, resumen de consultas) van en `table*` |
| Especificaciones del equipo | Pedido del docente: los benchmarks deben documentar la máquina | Tabla "Equipo en el que se ejecutaron todos los experimentos" en Diseño de los experimentos (procesador, RAM, disco, sistema operativo, MongoDB y versiones de Python) |
| Cifras | — (convención del equipo) | Coma decimal y punto de miles (0,114; 239.946), como en los resultados del repositorio |
| Extensión máxima | Hasta 7 páginas en la plantilla de la revista (aprox. 5.000 palabras sin contar figuras) | El artículo final ocupa 12 páginas. El docente autorizó superar el límite de la revista en este ejercicio (mensaje del 29 de octubre), así que todas las tablas y figuras van en el texto principal |
| Disponibilidad de datos y código | Declaración obligatoria. El software en una URL estable (GitHub) y archivado (Zenodo, Figshare o Software Heritage), con la URL en el apartado de disponibilidad del resumen | Sección "Disponibilidad de datos y código" con el enlace al repositorio, a Zenodo y los pasos para reproducir. La URL del repositorio también está en el resumen. Pendiente del equipo: archivar el repositorio en Zenodo y agregar su DOI |
| Declaraciones obligatorias | Financiación, conflicto de intereses, contribuciones de los autores (taxonomía CRediT) y agradecimientos | Secciones "Contribuciones de los autores" (roles CRediT según la tabla de responsabilidades), "Financiación", "Conflicto de intereses" y "Agradecimientos" al final del artículo |
| Material suplementario | Un solo archivo aparte, citado en el texto | No se usa un archivo aparte: como se pudo superar la extensión, todo va en el artículo. El apartado "Información suplementaria" del resumen remite a los notebooks del repositorio, que tienen el código y el resultado de cada consulta |
