import pandas as pd


def cargar_mortalidad_2019(ruta_excel):
    """Lee las columnas necesarias y devuelve los registros de 2019."""
    datos = pd.read_excel(
        ruta_excel,
        sheet_name="No_Fetales_2019",
        usecols=[
            "AÑO",
            "MES",
            "COD_DEPARTAMENTO",
            "SEXO",
            "GRUPO_EDAD1",
        ],
        dtype={
            "AÑO": int,
            "MES": int,
            "COD_DEPARTAMENTO": str,
            "SEXO": str,
            "GRUPO_EDAD1": str,
        },
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


def resumir_por_grupo_edad(datos):
    """Cuenta registros en los once grupos de edad del enunciado.

    Recibe registros de 2019 con GRUPO_EDAD1 como texto, no edades en años.
    Devuelve GRUPO_EDAD y CASOS, conservando la edad desconocida.
    """
    # Reproduce la clasificación docente y su orden de presentación.
    grupos_edad = {
        "Mortalidad neonatal": ["0", "1", "2", "3", "4"],
        "Mortalidad infantil": ["5", "6"],
        "Primera infancia": ["7", "8"],
        "Niñez": ["9", "10"],
        "Adolescencia": ["11"],
        "Juventud": ["12", "13"],
        "Adultez temprana": ["14", "15", "16"],
        "Adultez intermedia": ["17", "18", "19"],
        "Vejez": ["20", "21", "22", "23", "24"],
        "Longevidad / Centenarios": ["25", "26", "27", "28"],
        "Edad desconocida": ["29"],
    }
    etiquetas_edad = {}
    for grupo, codigos in grupos_edad.items():
        for codigo in codigos:
            etiquetas_edad[codigo] = grupo

    grupo_por_registro = datos["GRUPO_EDAD1"].map(etiquetas_edad)

    # Impide perder registros sin clasificar al ordenar las categorías.
    if grupo_por_registro.isna().any():
        raise ValueError("Hay códigos de edad sin grupo. Revisa la clasificación.")

    conteos_edad = grupo_por_registro.value_counts()

    # Incluye las once categorías, también si alguna tiene cero registros.
    conteos_edad = conteos_edad.reindex(list(grupos_edad), fill_value=0)
    return conteos_edad.rename_axis("GRUPO_EDAD").reset_index(name="CASOS")