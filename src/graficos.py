"""Construye las figuras de la aplicación a partir de datos preparados."""

from copy import deepcopy

import plotly.express as px
import plotly.graph_objects as go

def orientar_limites_para_plotly(limites):
    """Adapta una copia de los anillos departamentales a la convención de D3."""
    copia = deepcopy(limites)

    for elemento in copia["features"]:
        geometria = elemento["geometry"]
        if geometria["type"] == "Polygon":
            poligonos = [geometria["coordinates"]]
        elif geometria["type"] == "MultiPolygon":
            poligonos = geometria["coordinates"]
        else:
            raise ValueError("Se esperaban geometrías Polygon o MultiPolygon.")

        for poligono in poligonos:
            # El primer anillo es exterior; los siguientes representan huecos.
            for posicion, anillo in enumerate(poligono):
                area_doble = sum(
                    inicio[0] * fin[1] - fin[0] * inicio[1]
                    for inicio, fin in zip(anillo, anillo[1:])
                )

                # D3 requiere exteriores horarios y huecos antihorarios.
                invertir = (
                    (posicion == 0 and area_doble > 0)
                    or (posicion > 0 and area_doble < 0)
                )
                if invertir:
                    anillo.reverse()

    return copia


def crear_mapa_departamental(resumen, limites):
    """Devuelve un mapa de conteos por código departamental.

    Recibe la tabla con COD_DEPARTAMENTO, DEPARTAMENTO y CASOS,
    y el GeoJSON local con las formas de los territorios.
    """
    # Comprueba la correspondencia antes de asignar cantidades a las formas.
    codigos_datos = set(resumen["COD_DEPARTAMENTO"])
    codigos_mapa = {
        elemento["properties"]["DPTO_CCDGO"]
        for elemento in limites["features"]
    }
    if codigos_datos != codigos_mapa:
        raise ValueError("Los códigos de los datos y la cartografía no coinciden.")

    figura = px.choropleth(
        resumen,
        # Adapta el dibujo y conserva intacta la cartografía descargada.
        geojson=orientar_limites_para_plotly(limites),
        locations="COD_DEPARTAMENTO",
        # Enlaza el código de cada fila con el atributo de su geometría.
        featureidkey="properties.DPTO_CCDGO",
        color="CASOS",
        hover_name="DEPARTAMENTO",
        color_continuous_scale="Blues",
        labels={"CASOS": "Registros"},
    )

    # Ajusta la vista a los territorios incluidos, también los insulares.
    figura.update_geos(fitbounds="locations", visible=False)
    figura.update_layout(
        separators=",.",
        coloraxis_colorbar={"tickformat": ",.0f"},
        margin={"l": 0, "r": 0, "t": 10, "b": 0},
        height=600,
    )
    figura.update_traces(
        hovertemplate="%{hovertext}<br>Registros: %{z:,.0f}<extra></extra>"
    )
    return figura


def crear_barras_sexo_departamento(resumen):
    """Devuelve barras apiladas de registros por departamento y sexo.

    Espera las columnas DEPARTAMENTO, SEXO_NOMBRE y CASOS.
    Conserva los conteos absolutos y la categoría Indeterminado.
    """
    # La orientación horizontal facilita leer los nombres departamentales.
    figura = px.bar(
        resumen,
        x="CASOS",
        y="DEPARTAMENTO",
        color="SEXO_NOMBRE",
        orientation="h",
        barmode="stack",
        category_orders={
            "SEXO_NOMBRE": ["Masculino", "Femenino", "Indeterminado"]
        },
        color_discrete_map={
            "Masculino": "#3B82F6",
            "Femenino": "#F59E0B",
            "Indeterminado": "#64748B",
        },
        custom_data=["SEXO_NOMBRE"],
        labels={
            "CASOS": "Registros",
            "DEPARTAMENTO": "Departamento",
            "SEXO_NOMBRE": "Sexo",
        },
    )

    # Coloca los mayores totales arriba para facilitar la comparación.
    figura.update_yaxes(categoryorder="total ascending", automargin=True)
    figura.update_xaxes(tickformat=",.0f", rangemode="tozero")
    figura.update_layout(
        separators=",.",
        height=1050,
        legend={"orientation": "h", "x": 0, "y": 1.02},
    )
    figura.update_traces(
        hovertemplate=(
            "%{y}<br>Sexo: %{customdata[0]}<br>"
            "Registros: %{x:,.0f}<extra></extra>"
        )
    )
    return figura


def crear_distribucion_edad(resumen):
    """Dibuja las frecuencias de los once grupos docentes de edad.

    Recibe GRUPO_EDAD y CASOS, incluida la edad desconocida.
    El eje horizontal contiene categorías, no una escala uniforme de años.
    """
    # Suma las frecuencias preparadas para cada categoría del enunciado.
    figura = px.histogram(
        resumen,
        x="GRUPO_EDAD",
        y="CASOS",
        histfunc="sum",
        orientation="v",
        category_orders={"GRUPO_EDAD": resumen["GRUPO_EDAD"].tolist()},
        labels={"GRUPO_EDAD": "Grupo de edad", "CASOS": "Registros"},
        color_discrete_sequence=["#2563EB"],
        text_auto=",.0f",
    )
    figura.update_xaxes(type="category", tickangle=-35, automargin=True)
    figura.update_yaxes(
        title_text="Registros",
        tickformat=",.0f",
        rangemode="tozero",
    )
    figura.update_layout(separators=",.", height=550, bargap=0.15)

    # Permite leer también cantidades pequeñas sin alterar la escala.
    figura.update_traces(
        textposition="outside",
        cliponaxis=False,
        hovertemplate="Grupo: %{x}<br>Registros: %{y:,.0f}<extra></extra>",
    )
    return figura


def crear_tabla_causas(resumen):
    """Muestra las diez categorías CIE-10 con más registros.

    Recibe el resumen ordenado por CASOS de mayor a menor.
    Formatea las cantidades solo para su presentación.
    """
    principales = resumen.head(10)

    # Conserva CASOS numérico y prepara el texto con puntos de miles.
    casos_texto = principales["CASOS"].map("{:,}".format)
    casos_texto = casos_texto.str.replace(",", ".", regex=False)

    tabla = go.Table(
        columnwidth=[1, 7, 2],
        header={
            "values": ["Código", "Causa", "Casos"],
            "fill_color": "#2563EB",
            "font": {"color": "white", "size": 14},
            "align": ["left", "left", "right"],
            "height": 34,
        },
        cells={
            "values": [
                principales["COD_CAUSA"],
                principales["CAUSA"],
                casos_texto,
            ],
            "align": ["left", "left", "right"],
            "font": {"size": 12},
            "height": 44,
        },
    )
    figura = go.Figure(data=[tabla])
    figura.update_layout(
        height=550,
        margin={"l": 10, "r": 10, "t": 10, "b": 10},
    )
    return figura


def crear_barras_x95(resumen):
    """Dibuja los cinco mayores conteos municipales de X95.

    Recibe el resumen X95 ordenado por CASOS de mayor a menor.
    Identifica cada municipio junto con su departamento.
    """
    principales = resumen.head(5).copy()

    # Distingue municipios homónimos sin modificar el resumen original.
    principales["LUGAR"] = (
        principales["MUNICIPIO"] + " (" + principales["DEPARTAMENTO"] + ")"
    )

    figura = px.bar(
        principales,
        x="CASOS",
        y="LUGAR",
        orientation="h",
        custom_data=["COD_DANE"],
        text_auto=",.0f",
        color_discrete_sequence=["#2563EB"],
        labels={"CASOS": "Casos X95", "LUGAR": "Municipio"},
    )
    figura.update_yaxes(categoryorder="total ascending", automargin=True)
    figura.update_xaxes(tickformat=",.0f", rangemode="tozero")
    figura.update_layout(separators=",.", height=450)
    figura.update_traces(
        textposition="outside",
        cliponaxis=False,
        hovertemplate=(
            "%{y}<br>Código DANE: %{customdata[0]}<br>"
            "Casos X95: %{x:,.0f}<extra></extra>"
        ),
    )
    return figura


def crear_circular_menores_municipios(seleccion):
    """Representa los conteos de los municipios seleccionados.

    Los porcentajes corresponden a la suma de CASOS de esta selección.
    """
    tabla = seleccion.copy()
    tabla["LUGAR"] = (
        tabla["MUNICIPIO"] + " (" + tabla["DEPARTAMENTO"] + ")"
    )

    figura = px.pie(
        tabla,
        names="LUGAR",
        values="CASOS",
        custom_data=["COD_DANE"],
        labels={"LUGAR": "Municipio", "CASOS": "Registros"},
    )
    figura.update_traces(
        sort=False,
        textposition="inside",
        texttemplate="%{value}<br>%{percent:.1%}",
        hovertemplate=(
            "%{label}<br>Código DANE: %{customdata[0]}<br>"
            "Registros: %{value}<br>"
            "Porcentaje de la selección: %{percent:.1%}<extra></extra>"
        ),
    )

    # Mantiene la selección visible para conservar el denominador indicado.
    figura.update_layout(
        separators=",.",
        height=520,
        margin={"l": 10, "r": 10, "t": 10, "b": 10},
        legend={"itemclick": False, "itemdoubleclick": False},
    )
    return figura