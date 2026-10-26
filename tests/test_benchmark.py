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


def test_distingue_repeticiones(tmp_path):
    ruta = tmp_path / "b.csv"
    # CSV antiguo sin columna repeticion: sus filas cuentan como repetición 1
    pd.DataFrame([{"estrategia": "a", "base": "real", "t": 1}]).to_csv(ruta, index=False)
    guardar_benchmark([{"estrategia": "a", "base": "real", "repeticion": 2, "t": 2},
                       {"estrategia": "a", "base": "real", "repeticion": 3, "t": 3}], ruta)
    guardar_benchmark([{"estrategia": "a", "base": "real", "repeticion": 1, "t": 4}], ruta)
    df = pd.read_csv(ruta).set_index("repeticion")
    assert len(df) == 3
    assert df.loc[1, "t"] == 4 and df.loc[2, "t"] == 2 and df.loc[3, "t"] == 3
