import json
from pathlib import Path

import plotly.express as px
from dash import Dash, dcc, html

from src.datos import (
    cargar_mortalidad_2019,
    resumir_por_mes,
    resumir_por_departamento,
    resumir_por_departamento_y_sexo,
    resumir_por_grupo_edad,
    cargar_catalogo_causas,
    resumir_por_causa,
    cargar_catalogo_municipios,
    resumir_por_municipio,
    seleccionar_menores_municipios,
)
from src.graficos import (
    crear_barras_sexo_departamento,
    crear_distribucion_edad,
    crear_mapa_departamental,
    crear_tabla_causas,
    crear_barras_x95,
    crear_circular_menores_municipios,
)

# Localiza las entradas desde este archivo, sin depender de la terminal.
raiz = Path(__file__).resolve().parent
ruta_excel = raiz / "data" / "raw" / "Anexo1.NoFetal2019_CE_15-03-23.xlsx"
ruta_divipola = raiz / "data" / "raw" / "Divipola_CE_.xlsx"
ruta_catalogo = raiz / "data" / "raw" / "Anexo2.CodigosDeMuerte_CE_15-03-23.xlsx"
ruta_limites = raiz / "data" / "geo" / "departamentos_mgn_2018.geojson"

datos = cargar_mortalidad_2019(ruta_excel)
mensual = resumir_por_mes(datos)

# Carga el catálogo una vez y prepara los conteos con sus nombres.
catalogo_categorias = cargar_catalogo_causas(ruta_catalogo)
resumen_causas = resumir_por_causa(datos, catalogo_categorias)
figura_causas = crear_tabla_causas(resumen_causas)

# Precarga la consulta municipal para reutilizarla en los resúmenes.
catalogo_municipal = cargar_catalogo_municipios(ruta_divipola)
es_x95 = datos["COD_MUERTE"].str.startswith("X95", na=False)
datos_x95 = datos[es_x95]
resumen_x95 = resumir_por_municipio(datos_x95, catalogo_municipal)
figura_x95 = crear_barras_x95(resumen_x95)

# Prepara todas las causas para revisar el criterio de la circular.
resumen_municipal_completo = resumir_por_municipio(datos, catalogo_municipal)
menores_observados = resumen_municipal_completo.sort_values(
    ["CASOS", "COD_DANE"]
)

# Identifica territorios del catálogo sin registros en esta base.
sin_registros = catalogo_municipal[
    ~catalogo_municipal["COD_DANE"].isin(
        resumen_municipal_completo["COD_DANE"]
    )
]

print("\nRevisión de municipios para la circular:")
print("Municipios con registros:", len(resumen_municipal_completo))
print("Total contado:", resumen_municipal_completo["CASOS"].sum())
print(
    "Total conservado:",
    resumen_municipal_completo["CASOS"].sum() == len(datos),
)
print("Territorios del catálogo sin registros:", len(sin_registros))
print(sin_registros.to_string(index=False))

print("\nQuince menores conteos observados:")
print(menores_observados.head(15).to_string(index=False))

frecuencias_menores = (
    resumen_municipal_completo["CASOS"].value_counts().sort_index().head(10)
)
print("\nFrecuencias de los menores conteos:")
print(frecuencias_menores.to_string())

print("\nTipos territoriales del catálogo:")
frecuencia_tipos = catalogo_municipal["TIPO_TERRITORIO"].value_counts(
    dropna=False
)
print(frecuencia_tipos.to_string())

sin_tipo = resumen_municipal_completo[
    resumen_municipal_completo["TIPO_TERRITORIO"].fillna("").str.strip() == ""
]
print("\nTerritorios observados sin tipo:")
print(sin_tipo.to_string(index=False))

menores_municipios = seleccionar_menores_municipios(resumen_municipal_completo)
figura_circular = crear_circular_menores_municipios(menores_municipios)

municipios_sin_registros = sin_registros[
    sin_registros["TIPO_TERRITORIO"] == "Municipio"
]

# Nuevo Belén de Bajirá fue creado en 2023, después del año analizado.
municipios_sin_registros = municipios_sin_registros[
    municipios_sin_registros["COD_DANE"] != "27493"
]

print("\nSelección final para la circular:")
print(menores_municipios.to_string(index=False))
print("Municipios seleccionados:", len(menores_municipios))
print("Casos seleccionados:", menores_municipios["CASOS"].sum())

print("\nMunicipios de referencia sin registros en esta base:")
print(municipios_sin_registros.to_string(index=False))
print("Municipios de referencia:", len(municipios_sin_registros))

print("\nResumen municipal X95 desde la aplicación:")
print(resumen_x95.head(5).to_string(index=False))
print("Casos X95:", resumen_x95["CASOS"].sum())
print("Total conservado:", resumen_x95["CASOS"].sum() == len(datos_x95))

print("\nResumen de causas desde la aplicación:")
print(resumen_causas.head(3).to_string(index=False))
print("Categorías del catálogo:", len(catalogo_categorias))
print("Categorías observadas:", len(resumen_causas))
print("Casos por causa:", resumen_causas["CASOS"].sum())
print("Total conservado:", resumen_causas["CASOS"].sum() == len(datos))

departamental = resumir_por_departamento(datos, ruta_divipola)
sexo_departamental = resumir_por_departamento_y_sexo(datos, departamental)
barras_sexo = crear_barras_sexo_departamento(sexo_departamental)

resumen_edad = resumir_por_grupo_edad(datos)
figura_edad = crear_distribucion_edad(resumen_edad)

print("\nResumen de edad preparado por la aplicación:")
print(resumen_edad.to_string(index=False))
print("Grupos de edad:", len(resumen_edad))
print("Total por edad:", resumen_edad["CASOS"].sum())
print(
    "Coincide con las filas leídas:",
    resumen_edad["CASOS"].sum() == len(datos),
)

print("\nTotales por sexo desde la aplicación:")
print(sexo_departamental.groupby("SEXO")["CASOS"].sum().to_string())
print("Total de la tabla por sexo:", sexo_departamental["CASOS"].sum())

sumas_por_departamento = (
    sexo_departamental.groupby("COD_DEPARTAMENTO")["CASOS"].sum()
)
referencia_departamental = departamental.set_index("COD_DEPARTAMENTO")["CASOS"]
print(
    "Coinciden los totales departamentales:",
    sumas_por_departamento.equals(referencia_departamental),
)

# Reutiliza la cartografía descargada al iniciar la aplicación.
limites = json.loads(ruta_limites.read_text(encoding="utf-8"))
mapa = crear_mapa_departamental(departamental, limites)

print("\nResumen departamental preparado por la aplicación:")
print(departamental.to_string(index=False))
print("Filas departamentales:", len(departamental))
print("Total departamental:", departamental["CASOS"].sum())
print(
    "Códigos sin nombre:",
    departamental["DEPARTAMENTO"].isna().sum(),
)

figura = px.line(
    mensual,
    x="MES",
    y="CASOS",
    markers=True,
    labels={"MES": "Mes", "CASOS": "Registros"},
)
figura.update_xaxes(dtick=1)

# Facilita la lectura de cantidades completas en español.
figura.update_layout(separators=",.")
figura.update_yaxes(tickformat=",.0f")
figura.update_traces(
    hovertemplate="Mes: %{x}<br>Registros: %{y:,.0f}<extra></extra>"
)

app = Dash(__name__)

# Aplica formato al texto mostrado sin cambiar los conteos numéricos.
total_formateado = f"{mensual['CASOS'].sum():,}".replace(",", ".")

app.layout = [
    html.H1("Mortalidad en Colombia, 2019"),
    html.P(f"Filas representadas: {total_formateado}"),
    html.H2("Registros por mes"),
    dcc.Graph(figure=figura),
    html.H2("Registros por departamento, 2019"),
    html.P(
        "Agrupación territorial de los anexos de clase. "
        "Cartografía: DANE MGN 2018, simplificada."
    ),
    dcc.Graph(figure=mapa),
    html.H2("Registros por sexo y departamento, 2019"),
    dcc.Graph(figure=barras_sexo),
    html.H2("Distribución por grupos de edad, 2019"),
    html.P(
        "Agrupación de edad definida en el enunciado. "
        "Se incluyen los registros de edad desconocida."
    ),
    dcc.Graph(figure=figura_edad),
    html.H2("Diez principales causas de mortalidad, 2019"),
    html.P(
        "Categorías CIE-10 de tres caracteres, "
        "ordenadas de mayor a menor número de registros."
    ),
    dcc.Graph(figure=figura_causas),
    html.H2("Cinco municipios con más casos X95, 2019"),
    html.P(
        "Conteo de la categoría X95 y sus subcódigos, "
        "agrupado por el municipio registrado en los anexos."
    ),
    dcc.Graph(figure=figura_x95),
    html.H2("Diez municipios con menor conteo positivo, 2019"),
    html.P(
        f"Porcentajes sobre los {menores_municipios['CASOS'].sum()} "
        "registros de esta selección. Se consideran todas las causas "
        "y se desempata por código DANE."
    ),
    dcc.Graph(figure=figura_circular),
    html.P(
        "Municipios sin registros en esta base, informados aparte: "
        + ", ".join(municipios_sin_registros["MUNICIPIO"])
        + "."
    ),
]

if __name__ == "__main__":
    # Evita leer el Excel dos veces al iniciar el servidor de desarrollo.
    app.run(debug=True, use_reloader=False)