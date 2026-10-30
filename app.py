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
)
from src.graficos import (
    crear_barras_sexo_departamento,
    crear_distribucion_edad,
    crear_mapa_departamental,
)

# Localiza las entradas desde este archivo, sin depender de la terminal.
raiz = Path(__file__).resolve().parent
ruta_excel = raiz / "data" / "raw" / "Anexo1.NoFetal2019_CE_15-03-23.xlsx"
ruta_divipola = raiz / "data" / "raw" / "Divipola_CE_.xlsx"
ruta_limites = raiz / "data" / "geo" / "departamentos_mgn_2018.geojson"

datos = cargar_mortalidad_2019(ruta_excel)
mensual = resumir_por_mes(datos)
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
]

if __name__ == "__main__":
    # Evita leer el Excel dos veces al iniciar el servidor de desarrollo.
    app.run(debug=True, use_reloader=False)