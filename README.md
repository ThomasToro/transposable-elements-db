# PanTEon en MongoDB

Proyecto del segundo corte de Bases de Datos II (Universidad Autónoma de Manizales).
Diseño, implementación y evaluación de una base de datos en MongoDB que integra las
secuencias de elementos transponibles (TEs) de PanTEon Database v1.6.1, la taxonomía
de cada especie y sus perfiles de k-mers (k = 1 a 6).

## Equipo y responsabilidades

| Integrante | Responsabilidad principal |
| --- | --- |
| Thomas | Modelo de datos, entorno y repositorio, limpieza del FASTA, carga de `tes` y `secuencias`, benchmark de consultas e índices |
| Juan Arias | Limpieza del CSV, carga de `especies`, cruce FASTA–CSV, cálculo y carga de k-mers, benchmark de carga y espacio |
| Juan Hernandez | Consultas 1–9, 12–15 y las dos consultas propias |
| Isabela Murillo | Figuras, bibliotecas `.fasta` (consultas 10 y 11) y base del artículo |

## Requisitos

Cada integrante instala en su computador:

1. **Anaconda o Miniconda**
2. **MongoDB Community Server** (en Windows, instalarlo como servicio)
3. **MongoDB Database Tools** (`mongodump` y `mongorestore`; agregar su carpeta `bin` al PATH)
4. **Git**
5. **MongoDB Compass** (opcional, para revisar los datos)

Espacio libre recomendado: 30 GB. RAM: 8 GB mínimo, 16 GB recomendado para el cálculo de k-mers.

Para verificar la instalación:

```
conda --version
git --version
mongod --version
mongodump --version
```

## Instalación

```
git clone git@github.com:ThomasToro/transposable-elements-db.git
cd transposable-elements-db
conda env create -f environment.yml
conda activate panteon
jupyter notebook
```

## Datos

Los datos no se suben al repositorio por su tamaño. Descárguenlos de Zenodo
(https://zenodo.org/records/19372616) y guárdenlos en la carpeta `data/`:

- `PanTEon_Database_v1.6.1.fasta` (~990 MB)
- `PanTEon_Database_metadata_v1.6.1.csv` (~370 kB)

## Orden de ejecución

Para reconstruir la base desde cero, ejecuten los notebooks en este orden:

| # | Notebook | Qué hace | Responsable |
| --- | --- | --- | --- |
| 00 | `00_exploracion.ipynb` | Exploración de ambos archivos y registro de inconsistencias | Thomas y Juan Arias |
| 01 | `01_pipeline_csv_especies.ipynb` | Limpieza del CSV y carga de `especies` | Juan Arias |
| 02 | `02_pipeline_fasta_tes.ipynb` | Limpieza del FASTA, cruce y carga de `tes` y `secuencias` | Thomas |
| 03 | `03_pipeline_kmers.ipynb` | Cálculo y carga de k-mers | Juan Arias |
| 04 | `04_consultas.ipynb` | Consultas 1–9, 12–15 y propias | Juan Hernandez |
| 05 | `05_bibliotecas_y_figuras.ipynb` | Consultas 10 y 11, bibliotecas `.fasta` y figuras | Isabela Murillo |
| 06 | `06_benchmark.ipynb` | Evaluación experimental del diseño | Thomas y Juan Arias |

`especies` se carga antes que `tes` porque cada TE guarda el `_id` de su especie.

## Respaldo de la base (dump)

Los dumps no van en el repositorio; se comparten por Google Drive.

- **Dump base:** `especies`, `tes` y `secuencias`.
- **Dump con k-mers:** agrega `kmers`.

Enlaces: _(pendiente)_

Para restaurarlo:

```
mongorestore --gzip --drop --db panteon <carpeta-del-dump>/panteon
```

Para generarlo:

```
mongodump --gzip --db panteon --out dump/
```

Como alternativa al dump, los notebooks 01 a 03 regeneran la base completa desde los archivos originales.

## Estructura del repositorio

```
transposable-elements-db/
├── README.md
├── MODELO.md          ← modelo de datos acordado (el contrato del equipo)
├── JOURNAL.md         ← revista elegida y normas aplicadas
├── environment.yml
├── data/              ← FASTA y CSV (no se suben)
├── notebooks/
├── bibliotecas/       ← archivos .fasta generados con las consultas 10 y 11
├── figuras/
├── resultados/        ← reportes de calidad, tablas del benchmark
└── articulo/          ← .tex, .bib y PDF
```

## Reglas de trabajo en equipo

- Cada integrante trabaja en sus propios notebooks; no editen el notebook de otra persona sin avisar,
  porque Git maneja mal los conflictos en archivos `.ipynb`.
- Antes de hacer commit de un notebook, limpien las salidas pesadas (`Kernel → Restart & Clear Output`).
- Nunca suban el FASTA, el CSV ni los dumps. GitHub rechaza archivos de más de 100 MB.
- Si una biblioteca `.fasta` supera los 100 MB, súbanla comprimida o usen Git LFS.
- Cualquier cambio en nombres de colecciones o campos se discute antes y se actualiza en `MODELO.md`.

## Datos y licencia

Datos de PanTEon Database (licencia CC BY 4.0):

1. Orozco-Arias S, Ferrer-Pomer I, Rodrigues de Goes F, Gaviria-Orrego S, Gómiz-Fernández J, Llatser-Torres J,
   Paschoal AR, Guyot R, Gabaldón T. (2026). PanTEon: a cross-kingdom framework to guide the design of
   transposable element classifiers. bioRxiv. https://doi.org/10.64898/2026.04.01.715927
2. PanTEon Database v1.6.1. Zenodo. https://zenodo.org/records/19372616