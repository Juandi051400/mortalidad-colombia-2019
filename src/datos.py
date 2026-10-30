import pandas as pd


def cargar_resumen_mensual(ruta_excel):
    """Lee el Excel y devuelve los conteos de 2019 en columnas MES y CASOS."""
    datos = pd.read_excel(
        ruta_excel,
        sheet_name="No_Fetales_2019",
        usecols=["AÑO", "MES"],
        dtype=int,
        engine="openpyxl",
    )

    # Cuenta 2019 y ordena los meses como enteros, del 1 al 12.
    datos = datos[datos["AÑO"] == 2019]
    conteo = datos["MES"].value_counts().sort_index()

    return conteo.reset_index(name="CASOS")