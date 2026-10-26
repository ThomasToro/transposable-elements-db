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
| Species duplicada tras normalizar | `-` | 0 |
