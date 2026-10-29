# PanTEon en MongoDB

Proyecto del segundo corte de Bases de Datos II (Universidad Autónoma de Manizales).
Diseño, implementación y evaluación de una base de datos en MongoDB que integra las
secuencias de elementos transponibles (TEs) de PanTEon Database v1.6.1, la taxonomía
de cada especie y sus perfiles de k-mers (k = 1 a 6).

## Equipo y responsabilidades

| Integrante | Responsabilidad principal |
| --- | --- |
| Thomas Alejandro Toro Herrera | Modelo de datos, entorno y repositorio, exploración del FASTA, revisión del notebook 02, benchmark de consultas e índices |
| Juan Sebastián Arias Rueda | Exploración y limpieza del CSV, carga de `especies`, cruce FASTA–CSV, carga de `tes` y `secuencias`, cálculo y carga de k-mers, benchmark de carga y espacio |
| Juan Esteban Hernández Martínez | Consultas 1–9, 12–15 y las dos consultas propias |
| Isabela Quintero Murillo | Revista y plantilla LaTeX, `JOURNAL.md`, introducción, trabajo relacionado, referencias, bibliotecas `.fasta` (consultas 10 y 11) y las cuatro figuras |

## Estado del proyecto

| Parte | Notebook o archivo | Responsable | Estado |
| --- | --- | --- | --- |
| Exploración del FASTA | `00_exploracion.ipynb` | Thomas Alejandro Toro Herrera | Terminado |
| Exploración del CSV | `00_exploracion_csv.ipynb` | Juan Sebastián Arias Rueda | Terminado |
| Pipeline: `especies` y cruce | `01_pipeline_csv_especies.ipynb` | Juan Sebastián Arias Rueda | Terminado |
| Pipeline: `tes` y `secuencias` | `02_pipeline_fasta_tes.ipynb` | Juan Sebastián Arias Rueda | Terminado |
| Pipeline: k-mers | `03_pipeline_kmers.ipynb` | Juan Sebastián Arias Rueda | Terminado |
| Benchmark de carga y espacio | `06_benchmark_carga_espacio.ipynb` | Juan Sebastián Arias Rueda | Terminado |
| Benchmark de consultas | `06_benchmark_consultas.ipynb` | Thomas Alejandro Toro Herrera | Terminado |
| Consultas 1–9, 12–15 y propias | `04_consultas.ipynb` | Juan Esteban Hernández Martínez | Terminado |
| Bibliotecas `.fasta` (consultas 10 y 11) y figuras | `05_bibliotecas_y_figuras.ipynb` | Isabela Quintero Murillo | Terminado |
| Revista y artículo | `JOURNAL.md`, `articulo/` | Isabela Quintero Murillo | Terminado |

## Datos de prueba

`scripts/datos_prueba.py` crea la base `panteon_prueba` (7 especies reales y 25 TEs inventados), útil solo
para pruebas rápidas: borra y recrea la base cada vez que se ejecuta. Ya no cumple el modelo final (le falta
`is_species`), así que para trabajar se usa la base real `panteon` restaurada del dump (ver
**Respaldo de la base**).

## Requisitos

Cada integrante instala en su computador:

1. **Miniconda** (recomendado, ocupa ~0,5 GB) o **Anaconda** (~5 GB, incluye Anaconda Navigator).
   Cualquiera de los dos sirve: el entorno se crea igual con `environment.yml`.
2. **MongoDB 7.0** (todo el equipo usa la misma versión para que los dumps sean compatibles):
   - **Windows:** instalar MongoDB Community Server **7.0** desde la página de descargas de MongoDB,
     eligiendo la versión 7.0 (no la 8.x), y marcar la opción de instalarlo como servicio.
   - **macOS:** con Homebrew: `brew tap mongodb/brew`, `brew install mongodb-community@7.0` y
     `brew services start mongodb-community@7.0`.
   - **Linux:** usar Docker (ver abajo). MongoDB 8.x no arranca en kernels de Linux entre 6.19 y 7.0.13
     ([SERVER-125742](https://jira.mongodb.org/browse/SERVER-125742)); la 7.0 funciona en cualquier kernel.
3. **MongoDB Database Tools** (`mongodump` y `mongorestore`) y **MongoDB Shell** (`mongosh`, solo para
   verificar la instalación). En Windows se instalan aparte y hay que agregar su carpeta `bin` al PATH; en
   macOS, `brew install mongodb-database-tools mongosh`.
4. **Git**
5. **MongoDB Compass** (opcional, para revisar los datos). Se conecta con `mongodb://localhost:27017`.

Espacio libre recomendado: 30 GB. RAM: 8 GB mínimo, 16 GB recomendado para el cálculo de k-mers.

### MongoDB 7.0 con Docker (Linux)

```
docker run -d --name mongo7 --restart unless-stopped -p 27017:27017 -v mongo7data:/data/db mongo:7.0
```

El contenedor arranca solo al encender el computador y los datos se guardan en el volumen `mongo7data`.
Comandos útiles: `docker ps` (ver si corre), `docker start mongo7`, `docker stop mongo7`,
`docker logs mongo7 --tail 50`. No ejecuten `docker volume rm mongo7data`: borra la base.

Si tenían un MongoDB 8 instalado como servicio, desactívenlo para liberar el puerto:
`sudo systemctl disable --now mongod`.

### Verificar la instalación

```
conda --version
git --version
mongosh --eval "db.version()"
mongodump --version
```

`db.version()` debe empezar por `7.0`. Con Docker, `mongosh` está dentro del contenedor:
`docker exec mongo7 mongosh --eval "db.version()"`.

## Instalación

```
git clone git@github.com:ThomasToro/transposable-elements-db.git
cd transposable-elements-db
conda env create -f environment.yml
conda activate panteon
python -c "import pandas, numpy, Bio, pymongo, matplotlib, seaborn; print('Todo bien')"
```

Si usan HTTPS en vez de SSH, clonen con `https://github.com/ThomasToro/transposable-elements-db.git`.

Cada vez que vayan a trabajar: entrar a la carpeta del proyecto, `conda activate panteon` y `jupyter notebook`.
Se abre el navegador en `http://localhost:8888`; los notebooks están en `notebooks/`.

Si aparece `ModuleNotFoundError: No module named 'pymongo'` (o pandas, etc.), el entorno no está
activo en esa terminal: ejecuten `conda activate panteon` y vuelvan a intentarlo. Hay que activarlo
en cada terminal nueva; el nombre `panteon` aparece en el prompt cuando está activo.

### Prueba de conexión

En un notebook, ejecuten:

```python
from pymongo import MongoClient

client = MongoClient("mongodb://localhost:27017")
print(client.server_info()["version"])
print(client.list_database_names())
```

Debe mostrar la versión `7.0.x` y una lista como `['admin', 'config', 'local']`.

## Datos

Los datos no se suben al repositorio por su tamaño. Se descargan de Zenodo
(https://zenodo.org/records/19372616) y se guardan en la carpeta `data/`:

- `PanTEon_Database_v1.6.1.fasta` (~990 MB)
- `PanTEon_Database_metadata_v1.6.1.csv` (~370 kB)

En Linux o macOS, desde la carpeta del proyecto (macOS no trae `wget`; `curl` viene en ambos):

```
cd data
curl -L -o PanTEon_Database_v1.6.1.fasta "https://zenodo.org/records/19372616/files/PanTEon_Database_v1.6.1.fasta?download=1"
curl -L -o PanTEon_Database_metadata_v1.6.1.csv "https://zenodo.org/records/19372616/files/PanTEon_Database_metadata_v1.6.1.csv?download=1"
cd ..
```

En Windows, descárguenlos desde la página de Zenodo y muévanlos a `data/`. Después de copiarlos,
`git status` no debe mostrarlos (el `.gitignore` los excluye).

### Verificar la descarga

Comparen el tamaño y el MD5 de cada archivo con estos valores:

| Archivo | Tamaño (bytes) | MD5 |
| --- | --- | --- |
| `PanTEon_Database_v1.6.1.fasta` | 992.180.168 | `222bfd9899d866ca06cda062fc3c52ff` |
| `PanTEon_Database_metadata_v1.6.1.csv` | 371.391 | `7f4ea0ef9c242d2ccf4c0ee723c9f08c` |

Desde la carpeta del proyecto:

```
# macOS
md5 data/PanTEon_Database_v1.6.1.fasta data/PanTEon_Database_metadata_v1.6.1.csv
ls -l data/

# Linux
md5sum data/PanTEon_Database_v1.6.1.fasta data/PanTEon_Database_metadata_v1.6.1.csv
ls -l data/

# Windows (PowerShell)
Get-FileHash -Algorithm MD5 data\PanTEon_Database_v1.6.1.fasta, data\PanTEon_Database_metadata_v1.6.1.csv
Get-ChildItem data | Select-Object Name, Length
```

Windows muestra el hash en mayúsculas (`222BFD98…`); es el mismo valor, la comparación no distingue
mayúsculas. Si el tamaño o el MD5 no coinciden, la descarga quedó incompleta: bórrenla y vuelvan a descargar.

## Orden de ejecución

Para reproducir el proyecto desde cero:

1. **Obtener la base**, de una de dos formas:
   - **A. Restaurar el dump** (unos minutos): ver **Respaldo de la base (dump)**.
   - **B. Reconstruirla con el pipeline** (necesita los datos de `data/`): ejecutar `01` → `02` → `03`.
     El 03 crea `panteon.kmers` y también `panteon_bench.tes_embebidos` (estrategia alternativa del benchmark).
2. **Consultas y figuras:** `04` y `05` (solo necesitan la base `panteon`).
3. **Benchmarks:** los dos `06`. Necesitan además `panteon_bench`: con la opción A hay que restaurar también
   `panteon_bench.tar`. El `06_benchmark_carga_espacio` lee los tiempos que el 03 guardó en
   `resultados/benchmark_carga.csv`.

Los `00` son exploración de los archivos de `data/` y no cargan nada en MongoDB; se pueden saltar.
Ejecuten cada notebook con *Kernel → Restart & Run All* desde la carpeta `notebooks/` (las rutas son
relativas, como `../data/`).

Si vuelven a ejecutar el 03 o los 06 en otro equipo, cambien antes `MAQUINA` en la primera celda de código
(por ejemplo `"pc_windows"`): los resultados se agregan a los CSV de `resultados/` por máquina, y con el
mismo valor (`mac_m5`) reemplazarían las mediciones del artículo.

| # | Notebook | Qué hace | Responsable |
| --- | --- | --- | --- |
| 00 | `00_exploracion.ipynb` | Exploración del FASTA y registro de inconsistencias | Thomas Alejandro Toro Herrera |
| 00 | `00_exploracion_csv.ipynb` | Exploración del CSV y registro de inconsistencias | Juan Sebastián Arias Rueda |
| 01 | `01_pipeline_csv_especies.ipynb` | Limpieza del CSV y carga de `especies` | Juan Sebastián Arias Rueda |
| 02 | `02_pipeline_fasta_tes.ipynb` | Limpieza del FASTA, cruce y carga de `tes` y `secuencias` | Juan Sebastián Arias Rueda |
| 03 | `03_pipeline_kmers.ipynb` | Cálculo y carga de k-mers | Juan Sebastián Arias Rueda |
| 04 | `04_consultas.ipynb` | Consultas 1–9, 12–15 y propias | Juan Esteban Hernández Martínez |
| 05 | `05_bibliotecas_y_figuras.ipynb` | Consultas 10 y 11, bibliotecas `.fasta` y figuras | Isabela Quintero Murillo |
| 06 | `06_benchmark_carga_espacio.ipynb` | Benchmark de carga y espacio (`collStats`) | Juan Sebastián Arias Rueda |
| 06 | `06_benchmark_consultas.ipynb` | Benchmark de consultas con y sin índices (`explain`) | Thomas Alejandro Toro Herrera |

`especies` se carga antes que `tes` porque cada TE guarda el `_id` de su especie.

## Respaldo de la base (dump)

Los dumps no van en el repositorio; se comparten por Google Drive como `.tar` (los `.bson.gz` de adentro ya
van comprimidos). Detalle de tamaños, verificación y comandos: `resultados/dump_info.md`.

Carpeta de Google Drive: https://drive.google.com/drive/folders/1dralHzwDjck0lAboxCMs4UODyhWXVpbY

| Archivo | Tamaño | Contenido |
| --- | --- | --- |
| `panteon_kmers.tar` | ~2,1 GB | Base `panteon`: `especies`, `tes`, `secuencias` y `kmers` |
| `panteon_bench.tar` | ~1,9 GB | Base `panteon_bench`: `tes_embebidos` (solo para el benchmark) |

La mayoría solo necesita `panteon_kmers.tar` (notebooks 04 y 05). `panteon_bench.tar` solo hace falta para
los notebooks 06.

Para restaurarlos, descarguen los `.tar` en la raíz del repositorio y ejecuten desde ahí. `--drop` borra antes
las colecciones que ya existan con el mismo nombre.

macOS y Linux:

```
mkdir -p dump
tar -xf panteon_kmers.tar -C dump/
mongorestore --gzip --drop dump/panteon_kmers
# solo para el benchmark:
tar -xf panteon_bench.tar -C dump/
mongorestore --gzip --drop dump/panteon_bench
```

Windows (PowerShell; `tar` viene incluido desde Windows 10):

```
New-Item -ItemType Directory -Force dump
tar -xf panteon_kmers.tar -C dump
mongorestore --gzip --drop dump\panteon_kmers
# solo para el benchmark:
tar -xf panteon_bench.tar -C dump
mongorestore --gzip --drop dump\panteon_bench
```

Para comprobar que quedó bien, el notebook 05 cuenta los documentos de cada colección al empezar:
`especies` 2.790, `tes` 239.946, `secuencias` 239.946 y `kmers` 1.439.676.

Para generarlos:

```
mongodump --gzip --db panteon --out dump/panteon_kmers
mongodump --gzip --db panteon_bench --out dump/panteon_bench
cd dump && tar -cf panteon_kmers.tar panteon_kmers && tar -cf panteon_bench.tar panteon_bench
```

**Reconstruir desde cero (sin dump):** ejecutar en orden `01_pipeline_csv_especies.ipynb` →
`02_pipeline_fasta_tes.ipynb` (con `RECONSTRUIR_TODO = True`) → `03_pipeline_kmers.ipynb`. El 02 se detiene
si `kmers` o `tes_embebidos` ya tienen datos, porque recargar `tes` cambia sus `_id`.

## Pruebas

Las funciones de `src/` (k-mers, normalización de especies y registro de benchmarks) tienen pruebas con
pytest. No necesitan MongoDB ni los datos. Desde la raíz del repositorio, con el entorno activo:

```
python -m pytest -q
```

## Artículo

El artículo (revista *Bioinformatics*, en español) está en `articulo/`: `main.pdf` compilado y sus fuentes
`main.tex` y `references.bib`, con la clase y el estilo de citas de OUP. Usa las figuras de `figuras/`.
La revista elegida y las normas aplicadas están en `JOURNAL.md`.

## Estructura del repositorio

```
transposable-elements-db/
├── README.md
├── MODELO.md          ← modelo de datos acordado (el contrato del equipo)
├── JOURNAL.md         ← revista elegida y normas aplicadas
├── environment.yml
├── data/              ← FASTA y CSV (no se suben)
├── notebooks/
├── src/               ← funciones reutilizables: k-mers (kmers.py), normalización de especies
│                        (normalizacion.py) y registro de benchmarks (benchmark.py)
├── tests/             ← pruebas de src/ con pytest (`python -m pytest tests/`)
├── scripts/           ← datos_prueba.py (base panteon_prueba), bench_kmers.py (rendimiento del
│                        cálculo de k-mers) y specs_maquina.py (especificaciones de la máquina)
├── bibliotecas/       ← archivos .fasta generados con las consultas 10 y 11
├── figuras/
├── resultados/        ← reportes de calidad, tablas del benchmark
└── articulo/          ← .tex, .bib y PDF
```

## Flujo de trabajo con Git

Todos trabajamos en la rama `main`. Como cada uno edita archivos distintos, Git une los cambios sin conflictos.

**Al empezar a trabajar**, traer lo que subieron los demás:

```
git pull
```

**Al terminar**, subir solo sus propios archivos:

```
git status
git add notebooks/04_consultas.ipynb        # sus archivos, por nombre (no usen "git add .")
git commit -m "Descripción corta de lo que hicieron"
git pull
git push
```

- El `git pull` antes del `push` integra lo que otros subieron mientras tanto. Si el `push` se
  rechaza con un mensaje como *rejected… fetch first*, hagan `git pull` y luego `git push`.
- Revisen con `git status` que no se estén colando archivos ajenos ni datos.
- Hagan commits pequeños y frecuentes, no uno gigante al final.
- Si algo sale raro (un conflicto, un error de Git), no fuercen nada (`--force`) y avisen en el grupo.

## Reglas de trabajo en equipo

- Cada integrante trabaja en sus propios notebooks; no editen el notebook de otra persona sin avisar,
  porque Git maneja mal los conflictos en archivos `.ipynb`.
- `README.md` y `MODELO.md` los edita Thomas Alejandro Toro Herrera. Si necesitan un cambio, avísenle.
- Antes de hacer commit de un notebook, ejecútenlo completo (Kernel → Restart & Run All) y conserven las salidas: el enunciado pide mostrar el resultado de cada consulta.
- Nunca suban el FASTA, el CSV ni los dumps. GitHub rechaza archivos de más de 100 MB.
- Si una biblioteca `.fasta` supera los 100 MB, súbanla comprimida o usen Git LFS.
- Cualquier cambio en nombres de colecciones o campos se discute antes y se actualiza en `MODELO.md`.

## Datos y licencia

Datos de PanTEon Database (licencia CC BY 4.0):

1. Orozco-Arias S, Ferrer-Pomer I, Rodrigues de Goes F, Gaviria-Orrego S, Gómiz-Fernández J, Llatser-Torres J,
   Paschoal AR, Guyot R, Gabaldón T. (2026). PanTEon: a cross-kingdom framework to guide the design of
   transposable element classifiers. bioRxiv. https://doi.org/10.64898/2026.04.01.715927
2. PanTEon Database v1.6.1. Zenodo. https://zenodo.org/records/19372616
