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
            "COD_DANE",
            "SEXO",
            "GRUPO_EDAD1",
            "COD_MUERTE",
        ],
        dtype={
            "AÑO": int,
            "MES": int,
            "COD_DEPARTAMENTO": str,
            "COD_DANE": str,
            "SEXO": str,
            "GRUPO_EDAD1": str,
            "COD_MUERTE": str,
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


def contar_por_categoria_causa(datos):
    """Cuenta registros por categoría CIE-10 de tres caracteres.

    Requiere COD_MUERTE de texto con códigos de tres o cuatro caracteres.
    La jerarquía del anexo se contrastó durante la exploración.
    Devuelve todas las categorías en columnas COD_CAUSA y CASOS.
    """
    categorias = datos["COD_MUERTE"].str[:3]
    conteo = categorias.value_counts(dropna=False)
    return conteo.rename_axis("COD_CAUSA").reset_index(name="CASOS")


def cargar_catalogo_causas(ruta_catalogo):
    """Devuelve las categorías del anexo como COD_CAUSA y CAUSA.

    Conserva el Excel original y aplica los ajustes documentados.
    Comprueba la coherencia de los códigos y la unicidad de los nombres.
    """

    # El encabezado está en la fila 9 de Excel; pandas cuenta desde cero.
    catalogo = pd.read_excel(
        ruta_catalogo,
        sheet_name="Final",
        header=8,
        dtype=str,
        keep_default_na=False,
        engine="openpyxl",
    )

    # Prepara columnas de trabajo conservando el catálogo leído.
    columna_categoria = "Código de la CIE-10 tres caracteres"
    columna_nombre = "Descripción  de códigos mortalidad a tres caracteres"
    columna_detalle = "Código de la CIE-10 cuatro caracteres"
    categorias = catalogo[columna_categoria].copy()
    nombres = catalogo[columna_nombre].copy()
    codigos_detallados = catalogo[columna_detalle].str.strip()

    # Unifica únicamente las variantes de presentación ya comprobadas.
    etiquetas_elegidas = {
        "T81": "Complicaciones De Procedimientos, No Clasificadas En Otra Parte",
        "X16": (
            "Contacto Con Radiadores, Cañerias Y Artefactos "
            "Para Calefaccion, Calientes"
        ),
    }
    nombres = categorias.map(etiquetas_elegidas).fillna(nombres)

    # Corrige las cinco correspondencias contrastadas con la CIE-10 de OPS.
    # Fuente: https://ais.paho.org/classifications/chapters/CAP09.html
    codigos_i70 = ["I700", "I701", "I702", "I708", "I709"]
    filas_i70 = codigos_detallados.isin(codigos_i70)
    categorias.loc[filas_i70] = "I70"
    nombres.loc[filas_i70] = "Aterosclerosis"

    if (codigos_detallados.str.len() != 4).any():
        raise ValueError("Hay códigos detallados de longitud distinta de cuatro.")

    if (categorias != codigos_detallados.str[:3]).any():
        raise ValueError("Hay categorías que no coinciden con su código detallado.")

    # Conserva una fila por cada pareja de categoría y nombre.
    consulta = pd.DataFrame(
        {"COD_CAUSA": categorias, "CAUSA": nombres}
    ).drop_duplicates()

    if consulta["COD_CAUSA"].duplicated(keep=False).any():
        raise ValueError("Una categoría del catálogo tiene varios nombres.")

    if (consulta["CAUSA"].fillna("").str.strip() == "").any():
        raise ValueError("El catálogo contiene categorías sin nombre.")

    return consulta


def resumir_por_causa(datos, catalogo_categorias):
    """Cuenta causas y añade el nombre de cada categoría CIE-10.

    Recibe el catálogo preparado por cargar_catalogo_causas.
    Devuelve las categorías observadas por frecuencia descendente.
    """
    conteos = contar_por_categoria_causa(datos)
    resumen = conteos.merge(
        catalogo_categorias,
        on="COD_CAUSA",
        how="left",
        validate="one_to_one",
    )

    if resumen["CAUSA"].isna().any():
        raise ValueError("Hay categorías de causa sin nombre en el catálogo.")

    return resumen


def cargar_catalogo_municipios(ruta_divipola):
    """Lee nombres de Hoja1 y el tipo territorial de Hoja3.

    Conserva los códigos de Hoja1 y deja visibles los tipos no encontrados.
    """
    catalogo = pd.read_excel(
        ruta_divipola,
        sheet_name="Hoja1",
        usecols=["COD_DANE", "DEPARTAMENTO", "MUNICIPIO"],
        dtype=str,
        keep_default_na=False,
        engine="openpyxl",
    )

    # Hoja3 tiene encabezados repetidos; C y E contienen código y tipo.
    tipos = pd.read_excel(
        ruta_divipola,
        sheet_name="Hoja3",
        header=1,
        usecols=[2, 4],
        dtype=str,
        keep_default_na=False,
        engine="openpyxl",
    )
    tipos.columns = ["COD_DANE", "TIPO_TERRITORIO"]

    catalogo = catalogo.merge(
        tipos,
        on="COD_DANE",
        how="left",
        validate="one_to_one",
    )

    # Referencia histórica: DANE, EM 2021, nota de la variable NPCEP9B.
    tipos_historicos = catalogo["COD_DANE"].map(
        {"94663": "Área no municipalizada"}
    )
    catalogo["TIPO_TERRITORIO"] = catalogo["TIPO_TERRITORIO"].fillna(
        tipos_historicos
    )
    return catalogo


def resumir_por_municipio(datos, catalogo_municipal):
    """Cuenta los registros recibidos por municipio, de mayor a menor.

    Admite la base completa o un subconjunto previamente seleccionado.
    """
    conteo = datos["COD_DANE"].value_counts(dropna=False)
    tabla = conteo.rename_axis("COD_DANE").reset_index(name="CASOS")
    resumen = tabla.merge(
        catalogo_municipal,
        on="COD_DANE",
        how="left",
        validate="one_to_one",
    )

    nombres = resumen["MUNICIPIO"].fillna("").str.strip()
    if (nombres == "").any():
        raise ValueError("Hay municipios sin correspondencia o sin nombre.")

    return resumen


def seleccionar_menores_municipios(resumen):
    """Elige hasta diez municipios con registros, ordenados por casos.

    El código DANE resuelve los empates de forma reproducible.
    """
    if resumen["TIPO_TERRITORIO"].isna().any():
        raise ValueError("Hay territorios sin tipo antes de la selección.")

    municipios = resumen[resumen["TIPO_TERRITORIO"] == "Municipio"]
    municipios = municipios[municipios["CASOS"] > 0]
    return municipios.sort_values(["CASOS", "COD_DANE"]).head(10).copy()