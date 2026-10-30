"""Construye las figuras de la aplicación a partir de datos preparados."""

from copy import deepcopy

import plotly.express as px


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