import json
from pathlib import Path

from dash import Dash, Input, Output, dcc, html

from src.datos_publicacion import cargar_resumen
from src.graficos import (
    crear_barras_sexo_departamento,
    crear_distribucion_edad,
    crear_mapa_departamental,
    crear_tabla_causas,
    crear_barras_x95,
    crear_circular_menores_municipios,
    crear_linea_mensual,
)


def crear_tarjeta(titulo, contenido):
    """Agrupa un título y una lista de componentes en una tarjeta visual."""
    return html.Div(
        children=[html.H2(titulo)] + contenido,
        className="tarjeta",
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
mensual_departamental = cargar_resumen("mensual_departamental_2019")
edad_departamental = cargar_resumen("edad_departamental_2019")

# Relaciona los nombres visibles con los códigos usados para filtrar.
opciones_departamentos = [{"label": "Colombia", "value": "TODOS"}]
nombres_departamentos = {"TODOS": "Colombia"}

for departamento in departamental.to_dict("records"):
    codigo = departamento["COD_DEPARTAMENTO"]
    nombre = departamento["DEPARTAMENTO"]
    opciones_departamentos = opciones_departamentos + [
        {"label": nombre, "value": codigo}
    ]
    nombres_departamentos[codigo] = nombre

# Conserva las figuras y sus criterios usando las tablas ya preparadas.
barras_sexo = crear_barras_sexo_departamento(sexo_departamental)
figura_edad = crear_distribucion_edad(resumen_edad)
figura_causas = crear_tabla_causas(resumen_causas)
figura_x95 = crear_barras_x95(resumen_x95)
figura_circular = crear_circular_menores_municipios(menores_municipios)

# Reutiliza la cartografía y la adaptación existente para dibujarla.
limites = json.loads(ruta_limites.read_text(encoding="utf-8"))
mapa = crear_mapa_departamental(departamental, limites)

figura = crear_linea_mensual(mensual)

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
    crear_tarjeta(
        "Consulta por departamento",
        [
            html.Label("Departamento", htmlFor="filtro-departamento"),
            dcc.Dropdown(
                id="filtro-departamento",
                options=opciones_departamentos,
                value="TODOS",
                clearable=False,
            ),
            html.P(
                f"Colombia: {total_formateado} registros, 2019.",
                id="indicador-departamento",
            ),
            html.P(
                "Alcance del filtro: línea mensual, distribución por edad "
                "e indicador. Las otras cinco vistas conservan su alcance "
                "nacional de 2019 y sus criterios propios."
            ),
        ],
    ),
    # Reúne el panorama mensual y territorial en una fila adaptable.
    html.Div(
        children=[
            crear_tarjeta(
                "Registros por mes",
                [dcc.Graph(id="grafico-mensual", figure=figura)],
            ),
            crear_tarjeta(
                "Registros por departamento, 2019",
                [
                    html.P(
                        "Agrupación territorial de los anexos de clase. "
                        "Cartografía: DANE MGN 2018, simplificada."
                    ),
                    dcc.Graph(figure=mapa),
                ],
            ),
        ],
        className="fila-resumen",
    ),
    crear_tarjeta(
        "Registros por sexo y departamento, 2019",
        [dcc.Graph(figure=barras_sexo)],
    ),
    crear_tarjeta(
        "Distribución por grupos de edad, 2019",
        [
            html.P(
                "Agrupación de edad definida en el enunciado. "
                "Se incluyen los registros de edad desconocida."
            ),
            dcc.Graph(id="grafico-edad", figure=figura_edad),
        ],
    ),
    crear_tarjeta(
        "Diez principales causas de mortalidad, 2019",
        [
            html.P(
                "Categorías CIE-10 de tres caracteres, "
                "ordenadas de mayor a menor número de registros."
            ),
            dcc.Graph(figure=figura_causas),
        ],
    ),
    crear_tarjeta(
        "Cinco municipios con más casos X95, 2019",
        [
            html.P(
                "Conteo de la categoría X95 y sus subcódigos, "
                "agrupado por el municipio registrado en los anexos."
            ),
            dcc.Graph(figure=figura_x95),
        ],
    ),
    crear_tarjeta(
        "Diez municipios con menor conteo positivo, 2019",
        [
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
        ],
    ),
]


@app.callback(
    Output("grafico-mensual", "figure"),
    Output("grafico-edad", "figure"),
    Output("indicador-departamento", "children"),
    Input("filtro-departamento", "value"),
)
def actualizar_consulta_departamental(codigo):
    """Actualiza las dos figuras y el indicador según el territorio.

    Recibe TODOS o un código del selector y usa los CSV preparados.
    Conserva las tablas originales y el alcance de las otras cinco vistas.
    """
    if codigo == "TODOS":
        mensual_seleccionado = mensual
        edad_seleccionada = resumen_edad
    else:
        mensual_seleccionado = mensual_departamental[
            mensual_departamental["COD_DEPARTAMENTO"] == codigo
        ]
        edad_seleccionada = edad_departamental[
            edad_departamental["COD_DEPARTAMENTO"] == codigo
        ]

    nombre = nombres_departamentos[codigo]

    # Crea figuras nuevas y deja visible el territorio consultado.
    nueva_mensual = crear_linea_mensual(mensual_seleccionado)
    nueva_edad = crear_distribucion_edad(edad_seleccionada)
    nueva_mensual.update_layout(title_text=f"{nombre}, 2019")
    nueva_edad.update_layout(title_text=f"{nombre}, 2019")

    # Suma registros; las filas de esta tabla representan meses.
    total_texto = f"{mensual_seleccionado['CASOS'].sum():,}".replace(",", ".")
    indicador = f"{nombre}: {total_texto} registros, 2019."

    return nueva_mensual, nueva_edad, indicador

if __name__ == "__main__":
    # Evita repetir la carga al iniciar el servidor de desarrollo.
    app.run(debug=True, use_reloader=False)