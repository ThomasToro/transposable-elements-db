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
| Género con `Class`/`Order`/`Family` contradictoria (inconsistencia real) | Beta vulgaris (Amaranthaceae, Class vacía) / Beta vulgaris subsp vulgaris (Chenopodiaceae, Magnoliopsida) | 18 (10 géneros) | Se cargan tal cual; solo se documentan | `resultados/reporte_calidad_csv.md`; `notebooks/00_exploracion_csv.ipynb` (sección 5e) |
| `Species` duplicada tras normalizar | — | 0 | `species` con índice único | `resultados/reporte_calidad_csv.md` |

Faltantes por columna (NaN en el CSV original): Phylum 3, Class 49, Order 29, Family 76, Notes 6,
Source 2 2.740 (98,2 %). Kingdom, Species y Source completas.
Origen: `notebooks/00_exploracion_csv.ipynb` (sección 3).

Consistencia por género (primera palabra de `Species`): 21 géneros tienen especies con distinta `Class`,
`Order` o `Family`. 10 son inconsistencias reales: Beta (misma especie con dos familias, sinónimas, y
`Class` vacía en una), 7 géneros de insectos con `Order = Neoptera` (infraclase) en una especie
(Andrena, Trichogramma, Chironomus, Coelopa, Sarcophaga, Yponomeuta, Ypsolopha), y Aspergillus latus y
Exophiala sp hkrs030 con una subclase en `Family`. Las otras 11 no son errores: 3 por reclasificación o
géneros polifiléticos (Athelia, Agrocybe, Candida) y 8 por un valor faltante.
Origen: `resultados/reporte_calidad_csv.md`; `notebooks/00_exploracion_csv.ipynb` (sección 5e).

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
- `TE_count` del CSV (solo para validar, no se guarda) coincide exactamente con el número de TEs del FASTA
  en las 2.790 especies; 0 especies con conteo distinto.

## 3. K-mers

| Hecho | Detalle | Origen |
| --- | --- | --- |
| k calculados | 1 a 6, ventana deslizante de 1 | `src/kmers.py` |
| Mayúsculas | La secuencia se pasa a mayúsculas antes de contar | `src/kmers.py` |
| N y códigos IUPAC | Se descarta toda ventana con un carácter distinto de A, C, G, T | `src/kmers.py`; `MODELO.md` (Pendientes) |
| `valid_windows` | Número de ventanas válidas; frecuencia = `counts / valid_windows` | `src/kmers.py`; `MODELO.md` |
| Formato | Diccionario disperso: solo k-mers presentes (sin ceros) | `MODELO.md` (decisión 5) |
| TEs más cortos que k | Se guardan con `valid_windows = 0` y `counts = {}`; cada TE tiene siempre 6 documentos | `MODELO.md`; `notebooks/03_pipeline_kmers.ipynb` (sección 6) |
| Longitud mínima real | 81 nt, así que ningún TE queda con `valid_windows = 0`; el caso anterior es solo defensivo | `resultados/reporte_calidad_fasta.md` |
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

Base `panteon` (239.946 TEs). Estrategia principal: `panteon.kmers`; alternativa: `panteon_bench.tes_embebidos`.

Máquina de las mediciones. Origen: `resultados/especificaciones_maquina_juan.md` (generado por
`scripts/specs_maquina.py`).

| Componente | Valor |
| --- | --- |
| CPU | Apple M5, 10 núcleos (4 de rendimiento + 6 de eficiencia) |
| RAM | 24 GB |
| Sistema operativo | macOS 27.0.1 |
| Disco | SSD interno (APFS), 460,4 GB |
| MongoDB | 7.0.45, WiredTiger, caché máxima 11,5 GB (valor por defecto) |
| Python | 3.11.17; pymongo 4.19.0, numpy 2.4.6, pandas 3.1.0 |

Repeticiones: la carga completa de ambas estrategias se repitió 3 veces (`REPETICIONES = 3` en
`notebooks/03_pipeline_kmers.ipynb`), con el portátil conectado al cargador, otras aplicaciones cerradas
(incluido Docker) y `caffeinate` activo. Cada repetición borra y recrea las colecciones. Se reporta la media ±
desviación estándar muestral (n = 3). Las colecciones medidas en espacio son las de la última repetición.

Validación: ambas estrategias se cargaron con validación de esquema (`$jsonSchema`, `validationLevel: strict`,
`validationAction: error`): `kmers` con `ESQUEMA_KMERS` y `tes_embebidos` con el validador de `tes` más el
perfil `kmers.k1`–`k6` (`ESQUEMA_TES_EMBEBIDOS`). Una serie anterior de 3 repeticiones se descartó porque
`tes_embebidos` se había creado sin validador.

Tiempos de carga por repetición (s). Origen: `resultados/benchmark_carga.csv`.

| Estrategia | Repetición | t_calculo_s | t_insercion_s | t_indices_s | Total |
| --- | --- | --- | --- | --- | --- |
| coleccion_kmers | 1 | 123,129 | 49,927 | 22,374 | 195,430 |
| coleccion_kmers | 2 | 126,995 | 50,252 | 21,590 | 198,837 |
| coleccion_kmers | 3 | 126,352 | 50,351 | 22,098 | 198,801 |
| embebido_en_tes | 1 | 125,410 | 47,953 | 11,696 | 185,059 |
| embebido_en_tes | 2 | 126,150 | 47,948 | 14,596 | 188,694 |
| embebido_en_tes | 3 | 125,877 | 47,833 | 13,015 | 186,725 |

Media ± desviación estándar (s, n = 3). Origen: `notebooks/06_benchmark_carga_espacio.ipynb` (sección 1).

| Estrategia | n_docs | Cálculo | Inserción | Índices | Total |
| --- | --- | --- | --- | --- | --- |
| coleccion_kmers (`panteon`) | 1.439.676 | 125,5 ± 2,1 | 50,2 ± 0,2 | 22,0 ± 0,4 | 197,7 ± 2,0 |
| embebido_en_tes (`panteon_bench`) | 239.946 | 125,8 ± 0,4 | 47,9 ± 0,1 | 13,1 ± 1,5 | 186,8 ± 1,8 |

Carga previa de `tes` y `secuencias` (una sola corrida, `notebooks/02_pipeline_fasta_tes.ipynb`): 479.892
documentos; cálculo 2,131 s, inserción 3,875 s, índices 0,559 s, total 6,565 s.

Espacio (bytes, `collStats`). Origen: `resultados/benchmark_espacio.csv` (`notebooks/06_benchmark_carga_espacio.ipynb`).

| Estrategia | Colección | count | size | avgObjSize | storageSize | totalIndexSize |
| --- | --- | --- | --- | --- | --- | --- |
| coleccion_kmers | `panteon.kmers` | 1.439.676 | 8.144.577.956 | 5.657 | 3.177.865.216 | 60.469.248 |
| embebido_en_tes | `panteon_bench.tes_embebidos` | 239.946 | 8.104.036.854 | 33.774 | 3.184.594.944 | 5.435.392 |
| referencia_tes | `panteon.tes` | 239.946 | 73.969.252 | 308 | 12.718.080 | 10.919.936 |

Tamaño por índice (bytes). Origen: `resultados/benchmark_espacio.csv`.

| Colección | Índice | Tamaño |
| --- | --- | --- |
| `kmers` | `_id` | 15.781.888 |
| `kmers` | `{te_id: 1, k: 1}` único | 16.445.440 |
| `kmers` | `{pdb_id: 1, k: 1}` | 20.344.832 |
| `kmers` | `{k: 1, te_order: 1}` | 7.897.088 |
| `tes_embebidos` | `_id` | 2.490.368 |
| `tes_embebidos` | `{pdb_id: 1}` único | 2.945.024 |

Cifras derivadas (calculadas de las tablas anteriores):

- `storageSize`: `tes_embebidos` / `kmers` = 1,002 (6.729.728 bytes más en la embebida, que incluye una copia de `tes` de 12.718.080 bytes).
- `totalIndexSize`: `kmers` / `tes_embebidos` = 11,1.
- Tiempo total de carga: `kmers` 197,7 ± 2,0 s frente a embebida 186,8 ± 1,8 s (la embebida es 5,5 % más rápida).
- De la diferencia (10,9 s), 8,9 s están en los índices y 2,3 s en la inserción; el cálculo es igual (125,5 frente a 125,8 s).
- Respecto a la carga anterior, `size` y `count` son idénticos; `storageSize` y los índices `_id` varían unos pocos MB entre cargas.

Figuras: `figuras/benchmark_carga_panteon.png` (media ± DE, barra de error sobre el total) y
`figuras/benchmark_espacio_panteon.png` (300 dpi).
Interpretación: última celda de `notebooks/06_benchmark_carga_espacio.ipynb`.

Observaciones sobre la estimación previa:

- El piloto con los primeros 5.000 TEs estimó 79 s de cálculo para la estrategia `kmers` (1,64 s × 239.946 / 5.000);
  el real fue 125,5 ± 2,1 s, porque los TEs posteriores son más largos que los primeros 5.000.
- La estimación del piloto (4,1 min para ambas estrategias) no incluía la creación de índices ni la verificación;
  la ejecución completa de `notebooks/03_pipeline_kmers.ipynb` tardó unos 7 minutos por repetición (19 min 59 s para las 3).

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
| Estrategia alternativa del benchmark | k-mers embebidos en `tes_embebidos` (mismo formato disperso) | Un documento por TE con los 6 k; una colección por k | `MODELO.md` (decisión 4; Pendientes, cerrado) |
