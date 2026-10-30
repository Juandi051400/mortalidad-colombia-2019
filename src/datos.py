import pandas as pd


def cargar_mortalidad_2019(ruta_excel):
    """Lee las columnas necesarias y devuelve los registros de 2019."""
    datos = pd.read_excel(
        ruta_excel,
        sheet_name="No_Fetales_2019",
        usecols=["AÑO", "MES", "COD_DEPARTAMENTO"],
        dtype={"AÑO": int, "MES": int, "COD_DEPARTAMENTO": str},
        keep_default_na=False,
        engine="openpyxl",
    )

    return datos[datos["AÑO"] == 2019]


def resumir_por_mes(datos):
    """Devuelve los conteos mensuales de los registros recibidos."""
    conteo = datos["MES"].value_counts().sort_index()
    return conteo.reset_index(name="CASOS")

def resumir_por_departamento(datos, ruta_divipola):
    """Cuenta registros por código departamental y añade su nombre."""
    conteo = datos["COD_DEPARTAMENTO"].value_counts(dropna=False).sort_index()
    tabla_conteos = conteo.reset_index(name="CASOS")

    divipola = pd.read_excel(
        ruta_divipola,
        sheet_name="Hoja1",
        usecols=["COD_DEPARTAMENTO", "DEPARTAMENTO"],
        dtype=str,
        keep_default_na=False,
        engine="openpyxl",
    )

    # Obtiene las parejas código/nombre del catálogo municipal.
    pares_departamento = divipola.drop_duplicates()

    return tabla_conteos.merge(
        pares_departamento,
        on="COD_DEPARTAMENTO",
        how="left",
        validate="one_to_one",
    )