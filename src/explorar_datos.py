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
    usecols=["AÑO","MES", "SEXO","GRUPO_EDAD1","COD_MUERTE","MANERA_MUERTE"],
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
