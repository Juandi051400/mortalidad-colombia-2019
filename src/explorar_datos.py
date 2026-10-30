import pandas as pd

rutas = [
    "data/raw/Anexo1.NoFetal2019_CE_15-03-23.xlsx",
    "data/raw/Anexo2.CodigosDeMuerte_CE_15-03-23.xlsx",
    "data/raw/Divipola_CE_.xlsx",
]

for ruta in rutas:
    archivo = pd.ExcelFile(ruta, engine="openpyxl")
    print(ruta)
    print(archivo.sheet_names)
    archivo.close()

print("Primeras filas del archivo de mortalidad:")

# Inspecciona encabezados y códigos sin convertirlos a números.
muestra = pd.read_excel(
    rutas[0],
    sheet_name="No_Fetales_2019",
    header=None,
    nrows=6,
    dtype=str,
    keep_default_na=False,
    engine="openpyxl",
)

print(muestra.to_string(index=False, header=False))

print("Comparación de códigos del catálogo:")

# El encabezado está en la fila 9 de Excel; header=8 cuenta desde cero.
muestra_causas = pd.read_excel(
    rutas[1],
    sheet_name="Final",
    header=8,
    nrows=3,
    usecols=[
        "Código de la CIE-10 tres caracteres",
        "Código de la CIE-10 cuatro caracteres",
    ],
    dtype=str,
    keep_default_na=False,
    engine="openpyxl",
)

print(muestra_causas.to_string(index=False))

# Revisa ambas hojas: sus encabezados tienen estructuras diferentes.
for hoja in ["Hoja1", "Hoja3"]:
    print()
    print("Primeras filas de Divipola:", hoja)

    muestra_divipola = pd.read_excel(
        rutas[2],
        sheet_name=hoja,
        header=None,
        nrows=4,
        dtype=str,
        keep_default_na=False,
        engine="openpyxl",
    )

    print(muestra_divipola.to_string(index=True, header=False))

# Revisa todas las filas, con códigos como texto y vacíos conservados.
revision = pd.read_excel(
    rutas[0],
    sheet_name="No_Fetales_2019",
    header=0,
    usecols=[
        "AÑO",
        "MES",
        "SEXO",
        "GRUPO_EDAD1",
        "COD_MUERTE",
        "MANERA_MUERTE",
        "COD_DEPARTAMENTO",
        "COD_DANE",
        "COD_MUNICIPIO",
    ],
    dtype=str,
    keep_default_na=False,
    engine="openpyxl",
)

print("MES:", revision["MES"].unique().tolist())
print("SEXO:", revision["SEXO"].unique().tolist())
print("AÑO:", revision["AÑO"].unique().tolist())
print("GRUPO_EDAD1:", revision["GRUPO_EDAD1"].unique().tolist())


# Comprueba que mes y sexo contabilicen todas las filas leídas.
filas_leidas = len(revision)
conteo_mes = revision["MES"].value_counts(dropna=False)
conteo_sexo = revision["SEXO"].value_counts(dropna=False)

print("Filas leídas:", filas_leidas)

print("Filas por mes:")
print(conteo_mes)
print("Suma por mes:", conteo_mes.sum())

print("Filas por sexo:")
print(conteo_sexo)
print("Suma por sexo:", conteo_sexo.sum())

print("MANERA_MUERTE:", revision["MANERA_MUERTE"].unique().tolist())

# Incluye subcódigos X95; no se interpreta como el total de homicidios.
es_x95 = revision["COD_MUERTE"].str.startswith("X95", na=False)
revision_x95 = revision[es_x95]

print("Códigos que comienzan por X95:")
print(revision_x95["COD_MUERTE"].value_counts(dropna=False))

print("MANERA_MUERTE en esas filas:")
print(revision_x95["MANERA_MUERTE"].value_counts(dropna=False))

print("\nRegistros de 2019 por código de departamento:")

revision_2019 = revision[revision["AÑO"] == "2019"]
conteo_departamento = (
    revision_2019["COD_DEPARTAMENTO"]
    .value_counts(dropna=False)
    .sort_index()
)

print(conteo_departamento.to_string())
print("Total contado:", conteo_departamento.sum())
print(
    "Códigos observados:",
    sorted(revision_2019["COD_DEPARTAMENTO"].unique()),
)

divipola = pd.read_excel(
    rutas[2],
    sheet_name="Hoja1",
    usecols=["COD_DEPARTAMENTO", "DEPARTAMENTO"],
    dtype=str,
    keep_default_na=False,
    engine="openpyxl",
)

# Una pareja código/nombre puede repetirse por los municipios de Divipola.
pares_departamento = divipola.drop_duplicates().sort_values("COD_DEPARTAMENTO")

print("\nCódigos y nombres de departamento en Divipola:")
print(pares_departamento.to_string(index=False))

tabla_conteos = conteo_departamento.reset_index(name="CASOS")

# Cada código contado debe corresponder a un único nombre.
resumen_departamental = tabla_conteos.merge(
    pares_departamento,
    on="COD_DEPARTAMENTO",
    how="left",
    validate="one_to_one",
)

print("\nResumen departamental con nombres:")
print(resumen_departamental.to_string(index=False))

print("Filas antes:", len(tabla_conteos))
print("Filas después:", len(resumen_departamental))
print("Total antes:", tabla_conteos["CASOS"].sum())
print("Total después:", resumen_departamental["CASOS"].sum())
print(
    "Códigos sin nombre:",
    resumen_departamental["DEPARTAMENTO"].isna().sum(),
)

# Prepara las cantidades que formarán los segmentos de cada barra.
conteo_departamento_sexo = (
    revision_2019.groupby(["COD_DEPARTAMENTO", "SEXO"], dropna=False)
    .size()
    .reset_index(name="CASOS")
)

print("\nMuestra del conteo por departamento y sexo:")
print(conteo_departamento_sexo.head(10).to_string(index=False))

print("\nTotales por sexo después de agrupar:")
print(conteo_departamento_sexo.groupby("SEXO")["CASOS"].sum().to_string())
print("Total de la tabla:", conteo_departamento_sexo["CASOS"].sum())

# Comprueba que cada departamento conserve su total ya validado.
sumas_por_departamento = (
    conteo_departamento_sexo.groupby("COD_DEPARTAMENTO")["CASOS"].sum()
)
print(
    "Coincide con los totales departamentales:",
    sumas_por_departamento.equals(conteo_departamento),
)

# Agrupación de GRUPO_EDAD1 exigida en el enunciado de la actividad.
# Los valores son códigos como texto, no edades individuales en años.
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

# Asigna a cada código el nombre de su grupo para aplicar map.
etiquetas_edad = {}
for grupo, codigos in grupos_edad.items():
    for codigo in codigos:
        etiquetas_edad[codigo] = grupo

grupo_por_registro = revision_2019["GRUPO_EDAD1"].map(etiquetas_edad)

# Detiene el cálculo si hay códigos sin clasificar antes de ordenar.
if grupo_por_registro.isna().any():
    raise ValueError("Hay códigos de edad sin grupo. Revisa la clasificación.")

conteos_edad = grupo_por_registro.value_counts()

# Mantiene el orden docente y muestra cero si un grupo no tiene registros.
conteos_edad = conteos_edad.reindex(list(grupos_edad), fill_value=0)
resumen_edad = conteos_edad.rename_axis("GRUPO_EDAD").reset_index(name="CASOS")

print("\nResumen por grupos de edad:")
print(resumen_edad.to_string(index=False))
print("Grupos:", len(resumen_edad))
print("Total agrupado:", resumen_edad["CASOS"].sum())
print("Registros sin grupo:", grupo_por_registro.isna().sum())

# Comprueba que el código 29 siga representado como edad desconocida.
edad_desconocida_original = revision_2019["GRUPO_EDAD1"].eq("29").sum()
print(
    "Edad desconocida conservada:",
    conteos_edad["Edad desconocida"] == edad_desconocida_original,
)

# Inspecciona los códigos completos antes de elegir una clave del catálogo.
codigos_muerte = revision_2019["COD_MUERTE"]
print("\nLongitudes de COD_MUERTE:")
print(codigos_muerte.str.len().value_counts().sort_index().to_string())
print("Códigos vacíos en la base:", codigos_muerte.eq("").sum())

conteo_causas = codigos_muerte.value_counts(dropna=False)
print("\nDiez códigos de muerte más frecuentes:")
print(conteo_causas.head(10).to_string())
print("Total contado por código:", conteo_causas.sum())

# El encabezado del catálogo está en la fila 9 de Excel: header=8.
catalogo_causas = pd.read_excel(
    rutas[1],
    sheet_name="Final",
    header=8,
    dtype=str,
    keep_default_na=False,
    engine="openpyxl",
)
print("\nColumnas del catálogo:")
print(catalogo_causas.columns.tolist())

# Revisa ambas claves antes de decidir cómo unir códigos con nombres.
for columna in [
    "Código de la CIE-10 tres caracteres",
    "Código de la CIE-10 cuatro caracteres",
]:
    codigos_catalogo = catalogo_causas[columna]
    codigos_no_vacios = codigos_catalogo[codigos_catalogo != ""]
    print("\nClave del catálogo:", columna)
    print("Filas del catálogo:", len(catalogo_causas))
    print("Códigos vacíos:", codigos_catalogo.eq("").sum())
    print("Longitudes de códigos no vacíos:")
    print(codigos_no_vacios.str.len().value_counts().sort_index().to_string())
    print(
        "Filas con código repetido (sin vacíos):",
        codigos_no_vacios.duplicated(keep=False).sum(),
    )

# Inspecciona la longitud excepcional antes de decidir cómo unir el catálogo.
codigos_detallados = catalogo_causas["Código de la CIE-10 cuatro caracteres"]
es_codigo_de_cinco = codigos_detallados.str.len() == 5
fila_codigo_de_cinco = catalogo_causas[es_codigo_de_cinco]

print("\nEntrada de cinco caracteres del catálogo:")
print(fila_codigo_de_cinco.to_string(index=False))

# Revela los caracteres antes de decidir si el código requiere una transformación.
for codigo in fila_codigo_de_cinco["Código de la CIE-10 cuatro caracteres"]:
    print("Código exacto:", repr(codigo))
    print("Caracteres:", list(codigo))

# Comprueba cambios y posibles claves repetidas antes de unir nombres.
codigos_detallados_limpios = codigos_detallados.str.strip()
cambiaron = codigos_detallados != codigos_detallados_limpios
repetidos = codigos_detallados_limpios.duplicated(keep=False)

print("\nCódigos modificados:", cambiaron.sum())
print("Filas con código repetido después:", repetidos.sum())

# Detecta códigos de tres caracteres asociados con distintas descripciones.
clave_tres = "Código de la CIE-10 tres caracteres"
descripcion_tres = "Descripción  de códigos mortalidad a tres caracteres"
nombres_por_codigo = (
    catalogo_causas.groupby(clave_tres)[descripcion_tres].nunique(dropna=False)
)
conflictos = nombres_por_codigo[nombres_por_codigo > 1]

print("\nCódigos con varias descripciones:", len(conflictos))
print(conflictos.to_string())

# Muestra las variantes textuales antes de decidir cómo resolverlas.
for codigo in conflictos.index:
    filas_codigo = catalogo_causas[catalogo_causas[clave_tres] == codigo]
    print("\nCódigo:", codigo)
    for descripcion in filas_codigo[descripcion_tres].unique():
        print(repr(descripcion))

# Unifica las variantes observadas de coma (T81) y n/ñ (X16).
etiquetas_elegidas = {
    "T81": "Complicaciones De Procedimientos, No Clasificadas En Otra Parte",
    "X16": "Contacto Con Radiadores, Cañerias Y Artefactos Para Calefaccion, Calientes",
}

# Conserva el texto original para los códigos sin etiqueta elegida.
descripciones_revisadas = catalogo_causas[clave_tres].map(etiquetas_elegidas)
descripciones_revisadas = descripciones_revisadas.fillna(
    catalogo_causas[descripcion_tres]
)

revision_nombres = descripciones_revisadas.groupby(
    catalogo_causas[clave_tres]
).nunique(dropna=False)
print("\nCódigos con varias descripciones después:", (revision_nombres > 1).sum())

# Comprueba por separado ausencias y textos sin contenido en ambos niveles.
descripcion_cuatro = "Descripcion  de códigos mortalidad a cuatro caracteres"
descripciones_detalladas = catalogo_causas[descripcion_cuatro]
vacias_tres = descripciones_revisadas.str.strip().eq("")
vacias_cuatro = descripciones_detalladas.str.strip().eq("")

print("\nAusentes (tres caracteres):", descripciones_revisadas.isna().sum())
print("En blanco (tres caracteres):", vacias_tres.sum())
print("Ausentes (cuatro caracteres):", descripciones_detalladas.isna().sum())
print("En blanco (cuatro caracteres):", vacias_cuatro.sum())

# Comprueba cada código completo contra el nivel correspondiente del catálogo.
codigos_tres_base = codigos_muerte[codigos_muerte.str.len() == 3]
codigos_cuatro_base = codigos_muerte[codigos_muerte.str.len() == 4]

sin_catalogo_tres = codigos_tres_base[
    ~codigos_tres_base.isin(catalogo_causas[clave_tres])
]
sin_catalogo_cuatro = codigos_cuatro_base[
    ~codigos_cuatro_base.isin(codigos_detallados_limpios)
]

print("\nRegistros sin correspondencia (tres):", len(sin_catalogo_tres))
print("Registros sin correspondencia (cuatro):", len(sin_catalogo_cuatro))

# Verifica la relación del catálogo antes de agrupar causas a tres caracteres.
categorias_por_prefijo = codigos_detallados_limpios.str[:3]
diferencias_categoria = categorias_por_prefijo != catalogo_causas[clave_tres]
print("\nCategorías distintas del prefijo:", diferencias_categoria.sum())

# Inspecciona ambas clasificaciones antes de decidir cómo agrupar las causas.
columnas_revision = [
    clave_tres,
    descripcion_tres,
    "Código de la CIE-10 cuatro caracteres",
    descripcion_cuatro,
]
discrepancias_catalogo = catalogo_causas.loc[diferencias_categoria, columnas_revision]
print("\nCorrespondencias del catálogo distintas del prefijo:")
print(discrepancias_catalogo.to_string(index=False))

# Cuantifica el efecto de las cinco correspondencias I70/I69 del anexo.
codigos_en_revision = codigos_detallados_limpios[diferencias_categoria]
registros_en_revision = codigos_muerte[codigos_muerte.isin(codigos_en_revision)]
print("\nRegistros con los cinco códigos revisados:", len(registros_en_revision))
print(registros_en_revision.value_counts().to_string())

# Fuente: https://ais.paho.org/classifications/chapters/CAP09.html
# Corrige solo las cinco correspondencias I70 contrastadas con la OPS.
codigos_i70 = ["I700", "I701", "I702", "I708", "I709"]
filas_i70 = codigos_detallados_limpios.isin(codigos_i70)
categorias_revisadas = catalogo_causas[clave_tres].copy()
nombres_categorias = descripciones_revisadas.copy()
categorias_revisadas.loc[filas_i70] = "I70"
nombres_categorias.loc[filas_i70] = "Aterosclerosis"

diferencias_restantes = categorias_revisadas != categorias_por_prefijo
print("\nDiferencias de categoría después:", diferencias_restantes.sum())

# Reúne categorías y nombres revisados para la consulta posterior.
catalogo_categorias = pd.DataFrame({
    "COD_CAUSA": categorias_revisadas,
    "CAUSA": nombres_categorias,
})

catalogo_categorias = catalogo_categorias.drop_duplicates()
categorias_repetidas = catalogo_categorias["COD_CAUSA"].duplicated(keep=False)
print("\nFilas con categoría repetida:", categorias_repetidas.sum())
print("Categorías del catálogo:", len(catalogo_categorias))
print(catalogo_categorias.head(3).to_string(index=False))

# Agrupa a tres caracteres tras validar y corregir la relación del catálogo.
categorias_base = codigos_muerte.str[:3]
sin_categoria = categorias_base[
    ~categorias_base.isin(catalogo_categorias["COD_CAUSA"])
]
conteo_categorias = categorias_base.value_counts(dropna=False)

print("\nRegistros sin correspondencia de categoría:", len(sin_categoria))
print("Total contado por categoría:", conteo_categorias.sum())
print("Coincide con la base:", conteo_categorias.sum() == len(codigos_muerte))
print(conteo_categorias.head(10).to_string())

# Prepara columnas de código y casos para añadir los nombres posteriormente.
tabla_conteos_causas = (
    conteo_categorias.rename_axis("COD_CAUSA").reset_index(name="CASOS")
)
print("\nConteo convertido en tabla:")
print(tabla_conteos_causas.head(3).to_string(index=False))
print("Categorías observadas:", len(tabla_conteos_causas))
print("Total de casos:", tabla_conteos_causas["CASOS"].sum())

# Añade nombres mediante una correspondencia única por categoría.
resumen_causas = tabla_conteos_causas.merge(
    catalogo_categorias,
    on="COD_CAUSA",
    how="left",
    validate="one_to_one",
)

print("\nFilas antes:", len(tabla_conteos_causas))
print("Filas después:", len(resumen_causas))
print("Total después:", resumen_causas["CASOS"].sum())
print("Categorías sin nombre:", resumen_causas["CAUSA"].isna().sum())
print(resumen_causas.head(10).to_string(index=False))

# Lee las claves municipales y sus nombres sin modificar los originales.
divipola_municipal = pd.read_excel(
    rutas[2],
    sheet_name="Hoja1",
    usecols=[
        "COD_DANE", "COD_DEPARTAMENTO", "DEPARTAMENTO",
        "COD_MUNICIPIO", "MUNICIPIO",
    ],
    dtype=str,
    keep_default_na=False,
    engine="openpyxl",
)


def inspeccionar_claves_municipales(tabla, origen):
    """Muestra el formato y la coherencia de las claves sin modificarlas."""
    columnas = ["COD_DANE", "COD_DEPARTAMENTO", "COD_MUNICIPIO"]
    print(f"\nClaves municipales en {origen}:")
    print(tabla[columnas].head(3).to_string(index=False))

    for columna in columnas:
        codigos = tabla[columna]
        print(f"\nLongitudes de {columna}:")
        print(codigos.str.len().value_counts(dropna=False).sort_index())
        print("Vacíos o espacios:", (codigos.str.strip() == "").sum())

    compuesta = tabla["COD_DEPARTAMENTO"] + tabla["COD_MUNICIPIO"]
    print(
        "Diferencias frente a departamento + municipio:",
        (tabla["COD_DANE"] != compuesta).sum(),
    )


inspeccionar_claves_municipales(revision_2019, "mortalidad 2019")
inspeccionar_claves_municipales(divipola_municipal, "Divipola")

print("\nFilas del catálogo con COD_DANE repetido:")
print(divipola_municipal["COD_DANE"].duplicated(keep=False).sum())

print("\nCobertura en Divipola (True = código encontrado):")
en_catalogo = revision_2019["COD_DANE"].isin(divipola_municipal["COD_DANE"])
print(en_catalogo.value_counts(dropna=False).to_string())

# Selecciona X95 y sus subcódigos únicamente en los registros de 2019.
es_x95_2019 = revision_2019["COD_MUERTE"].str.startswith("X95", na=False)
registros_x95_2019 = revision_2019[es_x95_2019]

conteo_x95_municipal = (
    registros_x95_2019["COD_DANE"]
    .value_counts(dropna=False)
    .rename_axis("COD_DANE")
    .reset_index(name="CASOS")
)

# Añade nombres por la clave completa, conservando el orden del conteo.
resumen_x95_municipal = conteo_x95_municipal.merge(
    divipola_municipal[["COD_DANE", "DEPARTAMENTO", "MUNICIPIO"]],
    on="COD_DANE",
    how="left",
    validate="one_to_one",
)

nombres_x95 = resumen_x95_municipal["MUNICIPIO"].fillna("").str.strip()

print("\nCinco municipios con más registros X95:")
print(resumen_x95_municipal.head(5).to_string(index=False))
print("Registros X95:", len(registros_x95_2019))
print("Total contado:", resumen_x95_municipal["CASOS"].sum())
print(
    "Total conservado:",
    resumen_x95_municipal["CASOS"].sum() == len(registros_x95_2019),
)
print("Municipios sin nombre:", (nombres_x95 == "").sum())