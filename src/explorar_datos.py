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
    usecols=["AÑO","MES", "SEXO","GRUPO_EDAD1","COD_MUERTE","MANERA_MUERTE","COD_DEPARTAMENTO",],
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

