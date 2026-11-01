"""Organiza las siete vistas en secciones con alcances explícitos.

Este módulo construye componentes de Dash; no lee archivos ni transforma datos.
La consulta territorial mantiene sus identificadores para el callback de app.py.
"""

from dash import dcc, html


CONFIG_GRAFICOS = {"displaylogo": False}


def crear_tarjeta(titulo, contenido):
    """Reúne el encabezado y los componentes de una visualización."""
    return html.Section(
        [html.H2(titulo, className="titulo-tarjeta")] + contenido,
        className="tarjeta",
    )


def crear_grafico(grafico_id, clase, figura=None):
    """Reserva una altura estable antes de dibujar o actualizar la figura.

    El CSS dimensiona el marco exterior; Graph ocupa el 100 % de ese marco.
    Dash añade una altura porcentual con responsive=True, por lo que el marco
    evita depender de la altura automática de la tarjeta y evita superposición.
    Las figuras dinámicas comienzan vacías hasta la respuesta de su callback.
    """
    return html.Div(
        dcc.Graph(
            id=grafico_id,
            figure=figura if figura is not None else {},
            responsive=True,
            config=CONFIG_GRAFICOS,
            style={"height": "100%", "width": "100%"},
        ),
        id=f"marco-{grafico_id}",
        className=f"grafico {clase}",
    )


def crear_indicador(etiqueta, valor):
    """Presenta un dato nacional con una etiqueta que identifica su alcance."""
    return html.Div(
        [
            html.Span(etiqueta, className="etiqueta-indicador"),
            html.Strong(valor, className="valor-indicador"),
        ],
        className="indicador-nacional",
    )


def crear_panel_departamental(
    opciones_departamentos,
    total_texto,
    *,
    selector_id,
    indicador_id,
    nota_alcance,
):
    """Crea un selector independiente y su indicador con alcance explícito.

    Los identificadores distinguen las dos secciones; la persistencia recuerda
    cada selección al cambiar de pestaña, sin vincular ambos controles.
    """
    return html.Section(
        [
            html.Div(
                [
                    html.Label("Departamento", htmlFor=selector_id),
                    dcc.Dropdown(
                        id=selector_id,
                        options=opciones_departamentos,
                        value="TODOS",
                        clearable=False,
                        persistence=True,
                        persistence_type="memory",
                    ),
                ],
                className="control-departamento",
            ),
            html.Div(
                [
                    html.Span(
                        "REGISTROS DE LA SELECCIÓN", className="etiqueta-metrica"
                    ),
                    html.P(
                        f"Colombia: {total_texto} registros, 2019.",
                        id=indicador_id,
                        className="metrica-seleccion",
                    ),
                ],
                className="resumen-seleccion",
            ),
            html.P(nota_alcance, className="nota-alcance"),
        ],
        className="tarjeta panel-consulta",
    )


def crear_consulta_departamental(opciones_departamentos, total_texto):
    """Agrupa el selector y las dos vistas que responden a su selección."""
    return html.Div(
        [
            html.Div(
                [
                    html.P("EXPLORACIÓN TERRITORIAL", className="ceja-seccion"),
                    html.H2("Consulta por departamento", className="titulo-seccion"),
                    html.P(
                        "Compara la evolución mensual y la distribución por edad "
                        "de Colombia o de un departamento.",
                        className="descripcion-seccion",
                    ),
                ],
                className="cabecera-seccion",
            ),
            crear_panel_departamental(
                opciones_departamentos,
                total_texto,
                selector_id="filtro-departamento",
                indicador_id="indicador-departamento",
                nota_alcance=(
                    "El selector actualiza únicamente las dos gráficas y "
                    "el indicador de esta sección."
                ),
            ),
            html.Div(
                [
                    crear_tarjeta(
                        "Registros por mes",
                        [
                            crear_grafico("grafico-mensual", "grafico-consulta")
                        ],
                    ),
                    crear_tarjeta(
                        "Distribución por grupos de edad, 2019",
                        [
                            html.P(
                                "Agrupación de edad definida en el enunciado. "
                                "Se incluyen los registros de edad desconocida.",
                                className="nota-tarjeta",
                            ),
                            crear_grafico("grafico-edad", "grafico-consulta"),
                        ],
                    ),
                ],
                className="rejilla-dos rejilla-consulta",
            ),
        ],
        className="seccion-dashboard",
    )


def crear_panorama_nacional(opciones_departamentos, total_texto):
    """Muestra mapa y sexo a todo el ancho, con filtro territorial propio."""
    return html.Div(
        [
            html.Div(
                [
                    html.P("COLOMBIA · 2019", className="ceja-seccion"),
                    html.H2("Panorama nacional", className="titulo-seccion"),
                    html.P(
                        "Recorre el panorama de Colombia o enfoca un departamento "
                        "para consultar su mapa y sus registros por sexo.",
                        className="descripcion-seccion",
                    ),
                ],
                className="cabecera-seccion",
            ),
            crear_panel_departamental(
                opciones_departamentos,
                total_texto,
                selector_id="filtro-panorama",
                indicador_id="indicador-panorama",
                nota_alcance=(
                    "Colombia muestra los 33 territorios departamentales. "
                    "El filtro enfoca el mapa y las barras de esta sección; "
                    "es independiente de Consulta departamental."
                ),
            ),
            html.Div(
                [
                    crear_tarjeta(
                        "Registros por departamento, 2019",
                        [
                            html.P(
                                "Agrupación territorial de los anexos de clase. "
                                "Cartografía: DANE MGN 2018, simplificada.",
                                className="nota-tarjeta",
                            ),
                            crear_grafico("grafico-mapa", "grafico-mapa"),
                        ],
                    ),
                    crear_tarjeta(
                        "Registros por sexo y departamento, 2019",
                        [
                            html.P(
                                "Barras apiladas: cada segmento representa un sexo "
                                "y la longitud total suma los registros del territorio.",
                                className="nota-tarjeta",
                            ),
                            crear_grafico("grafico-sexo", "grafico-sexo"),
                        ],
                    ),
                ],
                className="rejilla-nacional",
            ),
        ],
        className="seccion-dashboard",
    )


def crear_causas_y_municipios(figuras, nota_circular, nota_sin_registros):
    """Conserva los rankings y la selección municipal con sus notas propias."""
    return html.Div(
        [
            html.Div(
                [
                    html.P("CAUSAS Y SUBCONJUNTOS", className="ceja-seccion"),
                    html.H2("Causas y municipios", className="titulo-seccion"),
                    html.P(
                        "Consulta las principales causas y los subconjuntos "
                        "municipales. Cada título y nota identifica la selección.",
                        className="descripcion-seccion",
                    ),
                ],
                className="cabecera-seccion",
            ),
            crear_tarjeta(
                "Diez principales causas de mortalidad, 2019",
                [
                    html.P(
                        "Categorías CIE-10 de tres caracteres, ordenadas de "
                        "mayor a menor número de registros.",
                        className="nota-tarjeta",
                    ),
                    html.Div(
                        crear_grafico(
                            "grafico-causas", "grafico-tabla", figuras["causas"]
                        ),
                        className="desplazamiento-tabla",
                    ),
                ],
            ),
            html.Div(
                [
                    crear_tarjeta(
                        "Cinco municipios con más casos X95, 2019",
                        [
                            html.P(
                                "Conteo de la categoría X95 y sus subcódigos, "
                                "agrupado por el municipio registrado en los anexos.",
                                className="nota-tarjeta",
                            ),
                            crear_grafico(
                                "grafico-x95", "grafico-x95", figuras["x95"]
                            ),
                        ],
                    ),
                    crear_tarjeta(
                        "Diez municipios con menor conteo positivo, 2019",
                        [
                            html.P(nota_circular, className="nota-tarjeta"),
                            crear_grafico(
                                "grafico-circular",
                                "grafico-circular",
                                figuras["circular"],
                            ),
                            html.P(nota_sin_registros, className="nota-tarjeta"),
                        ],
                    ),
                ],
                className="rejilla-dos rejilla-municipal",
            ),
        ],
        className="seccion-dashboard",
    )


def crear_interfaz(
    *,
    figuras,
    opciones_departamentos,
    total_nacional,
    numero_departamentos,
    nota_circular,
    nota_sin_registros,
):
    """Construye el dashboard con navegación y siete vistas conservadas.

    Recibe tres figuras en las claves causas, x95 y circular; opciones de los
    selectores; total nacional entero; número de territorios y las dos notas
    de la selección municipal ya preparada. Los callbacks entregan las otras
    cuatro figuras; esta función no recalcula sus conteos.
    """
    total_texto = f"{total_nacional:,}".replace(",", ".")

    return html.Div(
        [
            html.Header(
                [
                    html.Div(
                        [
                            html.P("APLICACIONES I · LA SALLE", className="ceja"),
                            html.H1("Mortalidad en Colombia, 2019"),
                            html.P(
                                "Exploración de los registros de defunciones",
                                className="subtitulo-dashboard",
                            ),
                        ],
                        className="identidad-dashboard",
                    ),
                    html.Div(
                        [
                            crear_indicador("Base nacional · registros", total_texto),
                            crear_indicador(
                                "Territorios departamentales",
                                str(numero_departamentos),
                            ),
                            crear_indicador("Año observado", "2019"),
                        ],
                        className="indicadores-nacionales",
                    ),
                ],
                className="encabezado",
            ),
            dcc.Tabs(
                id="secciones-dashboard",
                value="consulta",
                vertical=True,
                mobile_breakpoint=900,
                parent_className="dashboard-navegacion",
                className="dashboard-menu",
                content_className="dashboard-contenido",
                colors={
                    "border": "transparent",
                    "primary": "#35c1b2",
                    "background": "#142b49",
                },
                children=[
                    dcc.Tab(
                        label="Consulta departamental",
                        value="consulta",
                        className="opcion-seccion",
                        selected_className="opcion-seccion-activa",
                        children=crear_consulta_departamental(
                            opciones_departamentos, total_texto
                        ),
                    ),
                    dcc.Tab(
                        label="Panorama nacional",
                        value="nacional",
                        className="opcion-seccion",
                        selected_className="opcion-seccion-activa",
                        children=crear_panorama_nacional(
                            opciones_departamentos, total_texto
                        ),
                    ),
                    dcc.Tab(
                        label="Causas y municipios",
                        value="causas-municipios",
                        className="opcion-seccion",
                        selected_className="opcion-seccion-activa",
                        children=crear_causas_y_municipios(
                            figuras, nota_circular, nota_sin_registros
                        ),
                    ),
                ],
            ),
            html.Footer(
                "Fuente: anexos de la actividad y cartografía DANE. "
                "Las visualizaciones presentan conteos de registros.",
                className="pie-dashboard",
            ),
        ],
        className="dashboard",
    )
