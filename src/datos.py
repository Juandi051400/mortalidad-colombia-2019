import pandas as pd


def cargar_mortalidad_2019(ruta_excel):
    """Lee las columnas necesarias y devuelve los registros de 2019."""
    datos = pd.read_excel(
        ruta_excel,
        sheet_name="No_Fetales_2019",
        usecols=["AÑO", "MES", "COD_DEPARTAMENTO","SEXO"],
        dtype={"AÑO": int, "MES": int, "COD_DEPARTAMENTO": str, "SEXO": str},
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


def resumir_por_departamento_y_sexo(datos, resumen_departamental):
    """Agrupa los registros de 2019 por departamento y sexo.

    Usa el resumen departamental para incorporar nombres sin releer Divipola.
    """
    conteo = (
        datos.groupby(["COD_DEPARTAMENTO", "SEXO"], dropna=False)
        .size()
        .reset_index(name="CASOS")
    )
    etiquetas_sexo = {
        "1": "Masculino",
        "2": "Femenino",
        "3": "Indeterminado",
    }

    # Conserva Indeterminado como categoría y detecta códigos sin etiqueta.
    conteo["SEXO_NOMBRE"] = conteo["SEXO"].map(etiquetas_sexo)
    if conteo["SEXO_NOMBRE"].isna().any():
        raise ValueError("Hay códigos de sexo sin etiqueta; revisa la base.")

    # Toma solo código y nombre para conservar CASOS del nuevo conteo.
    nombres_departamento = resumen_departamental[
        ["COD_DEPARTAMENTO", "DEPARTAMENTO"]
    ]
    resumen = conteo.merge(
        nombres_departamento,
        on="COD_DEPARTAMENTO",
        how="left",
        validate="many_to_one",
    )
    if resumen["DEPARTAMENTO"].isna().any():
        raise ValueError("Hay códigos departamentales sin nombre.")

    return resumen