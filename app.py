import json
from pathlib import Path

import plotly.express as px
from dash import Dash, dcc, html

from src.datos_publicacion import cargar_resumen
from src.graficos import (
    crear_barras_sexo_departamento,
    crear_distribucion_edad,
    crear_mapa_departamental,
    crear_tabla_causas,
    crear_barras_x95,
    crear_circular_menores_municipios,
)

# Lee los resúmenes generados localmente con preparar_publicacion.py.
raiz = Path(__file__).resolve().parent
ruta_limites = raiz / "data" / "geo" / "departamentos_mgn_2018.geojson"

mensual = cargar_resumen("mensual_2019")
departamental = cargar_resumen("departamental_2019")
sexo_departamental = cargar_resumen("sexo_departamental_2019")
resumen_edad = cargar_resumen("edad_2019")
resumen_causas = cargar_resumen("causas_2019")
resumen_x95 = cargar_resumen("x95_municipal_2019")
menores_municipios = cargar_resumen("menores_municipios_2019")
municipios_sin_registros = cargar_resumen("municipios_sin_registros_2019")

# Conserva las figuras y sus criterios usando las tablas ya preparadas.
barras_sexo = crear_barras_sexo_departamento(sexo_departamental)
figura_edad = crear_distribucion_edad(resumen_edad)
figura_causas = crear_tabla_causas(resumen_causas)
figura_x95 = crear_barras_x95(resumen_x95)
figura_circular = crear_circular_menores_municipios(menores_municipios)

# Reutiliza la cartografía y la adaptación existente para dibujarla.
limites = json.loads(ruta_limites.read_text(encoding="utf-8"))
mapa = crear_mapa_departamental(departamental, limites)

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
    # Agrupa el título y el total como encabezado del dashboard.
    html.Div(
        children=[
            html.H1("Mortalidad en Colombia, 2019"),
            html.P(f"Filas representadas: {total_formateado}"),
        ],
        className="encabezado",
    ),
    # Mantiene juntos el encabezado mensual y su figura.
    html.Div(
        children=[
            html.H2("Registros por mes"),
            dcc.Graph(figure=figura),
        ],
        className="tarjeta",
    ),
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
    # Evita repetir la carga al iniciar el servidor de desarrollo.
    app.run(debug=True, use_reloader=False)