import pandas as pd

from src.benchmark import guardar_benchmark


def test_reemplaza_solo_la_misma_estrategia_y_base(tmp_path):
    ruta = tmp_path / "b.csv"
    guardar_benchmark([{"estrategia": "a", "base": "prueba", "t": 1},
                       {"estrategia": "a", "base": "real", "t": 2}], ruta)
    guardar_benchmark([{"estrategia": "a", "base": "real", "t": 3}], ruta)
    df = pd.read_csv(ruta)
    assert len(df) == 2
    assert df.set_index("base").loc["prueba", "t"] == 1
    assert df.set_index("base").loc["real", "t"] == 3
