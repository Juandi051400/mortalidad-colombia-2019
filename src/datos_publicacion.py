"""Lee los resúmenes estadísticos preparados para el dashboard.

Los CSV de data/processed se generan con src/preparar_publicacion.py.
Sus filas representan grupos o referencias territoriales.
Conserva los códigos como texto y convierte MES/CASOS a enteros.
"""

from pathlib import Path

import pandas as pd


def cargar_resumen(nombre):
    """Carga un CSV de data/processed mediante su nombre sin extensión."""
    raiz = Path(__file__).resolve().parent.parent
    ruta = raiz / "data" / "processed" / f"{nombre}.csv"

    tabla = pd.read_csv(
        ruta,
        dtype=str,
        keep_default_na=False,
        encoding="utf-8",
    )

    # Convierte solo las cantidades y los meses; conserva los códigos.
    for columna in ["MES", "CASOS"]:
        if columna in tabla.columns:
            tabla[columna] = tabla[columna].astype(int)

    return tabla