# Insumos para el artículo (Juan Arias)

Solo hechos y cifras. Cada cifra indica su archivo de origen (rutas desde la raíz del repo).

## 1. Limpieza del CSV de metadatos

Datos: `data/PanTEon_Database_metadata_v1.6.1.csv`, 2.790 filas y 13 columnas; se conservan 9
(Kingdom, Phylum, Class, Order, Family, Species, Source, Source 2, Notes).
Origen: `notebooks/00_exploracion_csv.ipynb` (sección 1).

| Problema | Ejemplo | Filas afectadas | Decisión | Origen |
| --- | --- | --- | --- | --- |
| Espacios al inicio/final en la taxonomía | `'Rosales '`, `' Ascomycota'` | 13 | `strip` en todas las columnas de texto | `resultados/reporte_calidad_csv.md` |
| Taxonomía con algún valor faltante | Family vacía | 122 | Se cargan como `null` (vacíos → `null`) | `resultados/reporte_calidad_csv.md` |
| Rellenos de texto en `Order` (11 variantes en catalán, español e inglés) | `No trobat`, `Not order identified Mamalia` | 26 | → `null` | `resultados/reporte_calidad_csv.md`; `notebooks/01_pipeline_csv_especies.ipynb` |
| `Species` que no es una especie (marcada en `Notes`) | `Afrotheria` | 44 | Se cargan con `is_species: false` | `resultados/reporte_calidad_csv.md` |
| Grupo taxonómico sin marca en `Notes` | `Muroidea` | 1 | `is_species: false` | `notebooks/00_exploracion_csv.ipynb` (sección 5b) |
| `Species` no binomial sin marca (subespecies, cepas, f. sp., híbridos, nombre común) | `Antilocapra americana peninsularis` | 52 | Se aceptan tal cual | `resultados/reporte_calidad_csv.md` |
| `Source 2` con comentarios en lugar de fuentes | `Genero y familia repetido` | 4 | → `null` | `resultados/reporte_calidad_csv.md`; `resultados/reporte_cruce.md` |
| Taxonomía sospechosa (taxón bajo un padre minoritario) | `Passeriformes` en Holothuroidea | 11 | Se cargan tal cual; solo se documentan | `resultados/reporte_calidad_csv.md` |
| `Species` duplicada tras normalizar | — | 0 | `species` con índice único | `resultados/reporte_calidad_csv.md` |

Faltantes por columna (NaN en el CSV original): Phylum 3, Class 49, Order 29, Family 76, Notes 6,
Source 2 2.740 (98,2 %). Kingdom, Species y Source completas.
Origen: `notebooks/00_exploracion_csv.ipynb` (sección 3).

Valores de `Source`: `RM2+MCH` 2.404, `Dfam` 386. Origen: `notebooks/00_exploracion_csv.ipynb` (sección 5c).

Resultado de la carga en `panteon.especies`:

| Medida | Valor | Origen |
| --- | --- | --- |
| Documentos | 2.790 | `notebooks/01_pipeline_csv_especies.ipynb` (sección 4) |
| `is_species: true` / `false` | 2.745 / 45 | `notebooks/01_pipeline_csv_especies.ipynb` (sección 4) |
| Reinos | Fungi 1.559, Animalia 780, Plantae 451 | `notebooks/01_pipeline_csv_especies.ipynb` (sección 4) |
| `taxonomy.order` nulo (faltantes + rellenos) | 55 | `notebooks/01_pipeline_csv_especies.ipynb` (sección 4) |
| Validación `$jsonSchema` | `species`, `taxonomy`, `taxonomy.kingdom`, `is_species` obligatorios; `kingdom` ∈ {Animalia, Plantae, Fungi}; `is_species` bool | `notebooks/01_pipeline_csv_especies.ipynb` (sección 2); `MODELO.md` |
| Índice | `{species: 1}` único | `notebooks/01_pipeline_csv_especies.ipynb` (sección 3) |

## 2. Cruce FASTA–CSV

Origen de todo el apartado: `resultados/reporte_cruce.md` (generado por `notebooks/01_pipeline_csv_especies.ipynb`).
Llave de cruce: `normalize_species` en `src/normalizacion.py`.

| Medida | Valor |
| --- | --- |
| TEs en el FASTA | 239.946 |
| Especies en el FASTA | 2.790 |
| Especies en `especies` | 2.790 |

Resultado inicial (llave: strip, espacios dobles a uno, minúsculas): 4 especies sin pareja, 533 TEs sin `species_id`.

| FASTA | CSV | TEs |
| --- | --- | --- |
| Beta vulgaris subsp. vulgaris | Beta vulgaris subsp vulgaris | 296 |
| Abrus pulchellus subsp. cantoniensis | Abrus pulchellus subsp cantoniensis | 178 |
| Marchantia polymorpha subsp. montivagans | Marchantia polymorpha subsp montivagans | 48 |
| Coccomyxa sp. obi | Coccomyxa sp obi | 11 |

- Causa: el FASTA abrevia los rangos infraespecíficos con punto (`subsp.`, `sp.`) y el CSV sin punto.
- Solución: `normalize_species` también elimina los puntos. Ningún nombre del CSV tiene punto; la nueva llave da 0 duplicados en el CSV.
- Resultado final: 0 especies del FASTA sin pareja, 0 especies del CSV sin TEs, 0 TEs sin `species_id`.
- En la base se guarda el nombre original del CSV; la llave normalizada solo se usa para comparar.

## 3. K-mers

| Hecho | Detalle | Origen |
| --- | --- | --- |
| k calculados | 1 a 6, ventana deslizante de 1 | `src/kmers.py` |
| Mayúsculas | La secuencia se pasa a mayúsculas antes de contar | `src/kmers.py` |
| N y códigos IUPAC | Se descarta toda ventana con un carácter distinto de A, C, G, T | `src/kmers.py`; `MODELO.md` (Pendientes) |
| `valid_windows` | Número de ventanas válidas; frecuencia = `counts / valid_windows` | `src/kmers.py`; `MODELO.md` |
| Formato | Diccionario disperso: solo k-mers presentes (sin ceros) | `MODELO.md` (decisión 5) |
| TEs más cortos que k | Se guardan con `valid_windows = 0` y `counts = {}`; cada TE tiene siempre 6 documentos | `MODELO.md`; `notebooks/03_pipeline_kmers.ipynb` (sección 6) |
| Método | Codificación numpy (A, C, G, T → 0..3; resto → marca de inválido), índice base 4 vectorizado, ventanas inválidas enmascaradas con suma acumulada de inválidos, conteo con `np.bincount`, conversión a dict al final | `src/kmers.py` |
| Validación del método | Igual a una implementación ingenua en Python puro en 50 secuencias aleatorias (con N, R, Y y minúsculas), k = 1..6 | `tests/test_kmers.py` |

Rendimiento (primeras 2.000 secuencias del FASTA, 6.276.825 nt). Origen: `resultados/rendimiento_kmers.csv`
(generado por `scripts/bench_kmers.py`).

| Modo | Procesos | Segundos | Secuencias/s | Estimado para 239.946 (min) |
| --- | --- | --- | --- | --- |
| 1 proceso | 1 | 0,727 | 2.749,6 | 1,45 |
| multiprocessing | 10 | 0,271 | 7.378,4 | 0,54 |

La estimación supone que el resto del FASTA tiene una longitud media similar a la de la muestra.

## 4. Carga y espacio

**Pendiente: ejecutar sobre `panteon`.** Las cifras actuales (`panteon_prueba`, 25 TEs) solo validan los
notebooks y no se usan en el artículo.

Tiempos de carga. Origen: `resultados/benchmark_carga.csv` (`notebooks/03_pipeline_kmers.ipynb`).

| Estrategia | Base | n_tes | n_docs | t_calculo_s | t_insercion_s | t_indices_s |
| --- | --- | --- | --- | --- | --- | --- |
| coleccion_kmers | panteon | | | | | |
| embebido_en_tes | panteon_bench | | | | | |

Espacio. Origen: `resultados/benchmark_espacio.csv` (`notebooks/06_benchmark_carga_espacio.ipynb`).

| Estrategia | Colección | count | size | avgObjSize | storageSize | totalIndexSize |
| --- | --- | --- | --- | --- | --- | --- |
| coleccion_kmers | kmers | | | | | |
| embebido_en_tes | tes_embebidos | | | | | |
| referencia_tes | tes | | | | | |

Figuras: `figuras/benchmark_carga_panteon.png`, `figuras/benchmark_espacio_panteon.png` (por generar).

## 5. Decisiones de diseño (parte de Juan Arias)

| Decisión | Elección | Alternativa descartada | Origen |
| --- | --- | --- | --- |
| Rellenos `No …` en `Order` | → `null` | Conservarlos como texto | `MODELO.md` (Pendientes) |
| Grupos taxonómicos en `Species` | Cargar con `is_species: false` (tienen TEs) | Excluirlos de `especies` | `MODELO.md` (`especies`) |
| Nombres no binomiales | Aceptar tal cual | Recortarlos a binomio | `notebooks/01_pipeline_csv_especies.ipynb` (sección 1) |
| Comentarios en `Source 2` | → `null` | Moverlos a `notes` | `notebooks/01_pipeline_csv_especies.ipynb` (sección 1) |
| Errores taxonómicos | Cargar tal cual y documentar | Corregirlos a mano | `notebooks/00_exploracion_csv.ipynb` (sección 5d) |
| Llave del cruce | `normalize_species` con eliminación de puntos | Mapeo explícito de los 4 casos | `resultados/reporte_cruce.md` |
| Validación de `especies` | `$jsonSchema` con enum de reinos | Sin validación | `MODELO.md` (Validación de esquema) |
| Ventanas con N o IUPAC | Descartar la ventana completa | Contar el k-mer con la letra ambigua | `MODELO.md` (Pendientes) |
| Formato de k-mers | Conteos dispersos + `valid_windows` | Arreglo denso; frecuencias | `MODELO.md` (decisión 5) |
| TEs más cortos que k | Documento con `valid_windows = 0`, `counts = {}` | No guardar el documento | `MODELO.md` (`kmers`) |
| Cálculo de k-mers | numpy vectorizado, 1 proceso | Python puro (`Counter`); multiprocessing | `src/kmers.py`; `resultados/rendimiento_kmers.csv` |
| Estrategia alternativa del benchmark | k-mers embebidos en `tes_embebidos` (mismo formato disperso) | — (en discusión) | `MODELO.md` (Pendientes, abierto) |
