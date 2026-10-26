# Reporte de calidad del CSV de metadatos

Generado por `notebooks/00_exploracion_csv.ipynb`. No se modificó ningún dato.

| Problema | Ejemplo | Filas afectadas |
| --- | --- | --- |
| Espacios al inicio/final en la taxonomía | `'Rosales '` | 13 |
| Taxonomía con algún NaN | `Family vacía` | 122 |
| Rellenos 'No …' en Order | `No trobat` | 26 |
| Species que no es especie (marcada en Notes) | `Afrotheria` | 44 |
| Species no binomial sin marca | `Antilocapra americana peninsularis` | 52 |
| Source 2 con texto que no es fuente | `Genero y familia repetido` | 4 |
| Taxonomía sospechosa (padre minoritario) | `Passeriformes en Holothuroidea` | 11 |
| Género con Class/Order/Family contradictoria | `Beta vulgaris: Amaranthaceae / Chenopodiaceae` | 18 |
| Species duplicada tras normalizar | `-` | 0 |

## Inconsistencias reales por género

21 géneros tienen especies con distinta Class, Order o Family; 10 son inconsistencias reales (18 filas). Las demás son reclasificaciones o géneros polifiléticos (Athelia, Agrocybe, Candida) o solo un valor faltante (Aphanomyces, Aquilegia, Citrus, Eragrostis, Eucalyptus, Juglans, Ustilago, Zopfia).

| Género | Problema |
| --- | --- |
| Beta | Misma especie con dos familias (Amaranthaceae / Chenopodiaceae, sinónimos en APG) y Class vacía en una |
| Andrena | Order = Neoptera (infraclase), debería ser Hymenoptera |
| Trichogramma | Order = Neoptera (infraclase), debería ser Hymenoptera |
| Chironomus | Order = Neoptera (infraclase), debería ser Diptera |
| Coelopa | Order = Neoptera (infraclase), debería ser Diptera |
| Sarcophaga | Order = Neoptera (infraclase), debería ser Diptera |
| Yponomeuta | Order = Neoptera (infraclase), debería ser Lepidoptera |
| Ypsolopha | Order = Neoptera (infraclase), debería ser Lepidoptera |
| Aspergillus | A. latus con Family = Eurotiomycetidae (subclase), las demás Aspergillaceae |
| Exophiala | E. sp hkrs030 con Family = Chaetothyriomycetidae (subclase), las demás Herpotrichiellaceae |
