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