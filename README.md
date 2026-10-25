# PanTEon en MongoDB

Proyecto del segundo corte de Bases de Datos II (Universidad Autónoma de Manizales).
Diseño, implementación y evaluación de una base de datos en MongoDB que integra las
secuencias de elementos transponibles (TEs) de PanTEon Database v1.6.1, la taxonomía
de cada especie y sus perfiles de k-mers (k = 1 a 6).

## Equipo y responsabilidades

| Integrante | Responsabilidad principal |
| --- | --- |
| Thomas | Modelo de datos, entorno y repositorio, limpieza del FASTA, carga de `tes` y `secuencias`, benchmark de consultas e índices |
| Juan Arias | Exploración del CSV en `00_exploracion_csv.ipynb` y, con la lista de especies del FASTA (`resultados/especies_fasta.csv`), el cruce | Solo para el cruce |
| Juan Hernandez | Consultas 1–9, 12–15 y las dos consultas propias |
| Isabela Murillo | Figuras, bibliotecas `.fasta` (consultas 10 y 11) y base del artículo |

## Primeros pasos de cada integrante

Todos: aceptar la invitación de colaborador en GitHub, instalar los requisitos, seguir la
**Instalación**, descargar los **Datos** y leer `MODELO.md`. Si están de acuerdo con el modelo
o cambiarían algo, avísenle a Thomas: debe quedar acordado antes de cargar los datos reales.

| Integrante | Qué hacer ahora | ¿Depende de alguien? |
| --- | --- | --- |
| Thomas | Exploración del FASTA en `00_exploracion.ipynb` y compartir la lista de especies con Juan Arias | No |
| Juan Arias | Exploración del CSV en `00_exploracion_csv.ipynb` (crearlo como copia de `00_exploracion.ipynb`) y, con la lista de especies del FASTA, el cruce | Solo para el cruce |
| Juan Hernandez | Escribir las consultas en `04_consultas.ipynb` usando los **datos de prueba** (ver abajo) | No |
| Isabela Murillo | Elegir la revista, llenar `JOURNAL.md` y montar la plantilla LaTeX en Overleaf | No |

## Datos de prueba (para no esperar la carga real)

La carga real (`especies`, `tes`, `secuencias`, `kmers`) depende de la exploración, la limpieza y el
cruce que hacen Thomas y Juan Arias, y puede tardar varios días. Para que nadie se quede esperando,
`scripts/datos_prueba.py` crea una base **`panteon_prueba`** con exactamente la misma estructura de
`MODELO.md`:

- 7 especies reales del CSV (taxonomía y Source reales), de los tres reinos.
- 25 TEs, secuencias y perfiles de k-mers **inventados** (identificadores `PDB99…`). Los k-mers se
  calculan de verdad a partir de esas secuencias.
- Casos especiales a propósito: una especie sin TEs, secuencias con N y una secuencia de 5
  nucleótidos sin 6-mers.

Como las consultas dependen de la **estructura** de los documentos y no de los datos en sí, las
consultas escritas sobre `panteon_prueba` funcionarán igual sobre la base real. Con la carga real
solo se cambia el nombre de la base.

Para crearla (se puede ejecutar las veces que quieran; siempre borra y recrea `panteon_prueba`):

```
conda activate panteon
python scripts/datos_prueba.py
```

En el notebook se conectan así:

```python
from pymongo import MongoClient

client = MongoClient("mongodb://localhost:27017")
db = client["panteon_prueba"]   # cambiar a client["panteon"] cuando llegue la carga real
```

Cada integrante ejecuta el script en su propio computador: la base queda en su MongoDB local,
no se comparte por Git. Con los datos de prueba se pueden escribir todas las consultas; los
resultados reales y su interpretación se completan cuando llegue el dump de la base real.

## Requisitos

Cada integrante instala en su computador:

1. **Miniconda** (recomendado, ocupa ~0,5 GB) o **Anaconda** (~5 GB, incluye Anaconda Navigator).
   Cualquiera de los dos sirve: el entorno se crea igual con `environment.yml`.
2. **MongoDB 7.0** (todo el equipo usa la misma versión para que los dumps sean compatibles):
   - **Windows:** instalar MongoDB Community Server **7.0** desde la página de descargas de MongoDB,
     eligiendo la versión 7.0 (no la 8.x), y marcar la opción de instalarlo como servicio.
   - **Linux:** usar Docker (ver abajo). MongoDB 8.x no arranca en kernels de Linux entre 6.19 y 7.0.13
     ([SERVER-125742](https://jira.mongodb.org/browse/SERVER-125742)); la 7.0 funciona en cualquier kernel.
3. **MongoDB Database Tools** (`mongodump` y `mongorestore`). En Windows se instalan aparte y hay que
   agregar su carpeta `bin` al PATH.
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

`db.version()` debe empezar por `7.0`.

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

En Linux o macOS, desde la carpeta del proyecto:

```
cd data
wget -O PanTEon_Database_v1.6.1.fasta "https://zenodo.org/records/19372616/files/PanTEon_Database_v1.6.1.fasta?download=1"
wget -O PanTEon_Database_metadata_v1.6.1.csv "https://zenodo.org/records/19372616/files/PanTEon_Database_metadata_v1.6.1.csv?download=1"
cd ..
```

En Windows, descárguenlos desde la página de Zenodo y muévanlos a `data/`. Después de copiarlos,
`git status` no debe mostrarlos (el `.gitignore` los excluye).

## Orden de ejecución

Este orden aplica para reconstruir el proyecto completo desde cero, una vez terminados los notebooks
(por ejemplo, para verificar la reproducibilidad antes de entregar). Mientras se trabaja no hace falta
seguirlo: cada integrante avanza en su notebook en paralelo, usando los datos de prueba o los dumps.

| # | Notebook | Qué hace | Responsable |
| --- | --- | --- | --- |
| 00 | `00_exploracion.ipynb` | Exploración del FASTA y registro de inconsistencias | Thomas |
| 00 | `00_exploracion_csv.ipynb` | Exploración del CSV y registro de inconsistencias | Juan Arias |
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
├── scripts/           ← datos_prueba.py (base de prueba con la estructura del modelo)
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
- `README.md` y `MODELO.md` los edita Thomas. Si necesitan un cambio, avísenle.
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
