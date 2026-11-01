"""Conecta los resúmenes de 2019, las figuras y la interfaz de Dash.

El arranque utiliza diez CSV estadísticos y la cartografía local.
Los Excel originales solo son necesarios para regenerar esos resúmenes.
Dos controles independientes actualizan mensual/edad y mapa/sexo.
Las vistas de causas y municipios conservan sus criterios documentados.
"""

import json
from pathlib import Path

from dash import Dash, Input, Output

from src.datos_publicacion import cargar_resumen
from src.graficos import (
    crear_barras_sexo_departamento,
    crear_barras_x95,
    crear_circular_menores_municipios,
    crear_distribucion_edad,
    crear_linea_mensual,
    crear_mapa_departamental,
    crear_tabla_causas,
)
from src.interfaz import crear_interfaz


def preparar_opciones_departamentales(resumen):
    """Devuelve las opciones del selector y la relación código/nombre.

    Recibe el resumen departamental validado, con códigos de texto.
    TODOS identifica la consulta nacional; el resto conserva el código DANE.
    """
    opciones = [{"label": "Colombia", "value": "TODOS"}]
    nombres = {"TODOS": "Colombia"}

    for departamento in resumen.to_dict("records"):
        codigo = departamento["COD_DEPARTAMENTO"]
        nombre = departamento["DEPARTAMENTO"]
        opciones.append({"label": nombre, "value": codigo})
        nombres[codigo] = nombre

    return opciones, nombres


# Lee los mismos resúmenes que produce preparar_publicacion.py.
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

opciones_departamentos, nombres_departamentos = preparar_opciones_departamentales(
    departamental
)
limites = json.loads(ruta_limites.read_text(encoding="utf-8"))

# Estas tres figuras conservan sus selecciones y se construyen una sola vez.
figuras_nacionales = {
    "causas": crear_tabla_causas(resumen_causas),
    "x95": crear_barras_x95(resumen_x95),
    "circular": crear_circular_menores_municipios(menores_municipios),
}

app = Dash(
    __name__,
    title="Mortalidad en Colombia · 2019",
    update_title="Actualizando…",
)
app.layout = crear_interfaz(
    figuras=figuras_nacionales,
    opciones_departamentos=opciones_departamentos,
    total_nacional=int(mensual["CASOS"].sum()),
    numero_departamentos=len(departamental),
    nota_circular=(
        f"Porcentajes sobre los {menores_municipios['CASOS'].sum()} "
        "registros de esta selección. Se consideran todas las causas "
        "y se desempata por código DANE."
    ),
    nota_sin_registros=(
        "Municipios sin registros en esta base, informados aparte: "
        + ", ".join(municipios_sin_registros["MUNICIPIO"])
        + "."
    ),
)


@app.callback(
    Output("grafico-mensual", "figure"),
    Output("grafico-edad", "figure"),
    Output("indicador-departamento", "children"),
    Input("filtro-departamento", "value"),
)
def actualizar_consulta_departamental(codigo):
    """Actualiza las dos figuras y el indicador según el territorio.

    Recibe TODOS o un código del selector y usa los CSV preparados.
    Crea figuras nuevas sin cambiar las tablas ni las otras secciones.
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
    nueva_mensual = crear_linea_mensual(mensual_seleccionado)
    nueva_edad = crear_distribucion_edad(edad_seleccionada)
    nueva_mensual.update_layout(title_text=f"{nombre}, 2019")
    nueva_edad.update_layout(title_text=f"{nombre}, 2019")

    # Suma registros; las filas de esta tabla representan meses.
    total_texto = f"{mensual_seleccionado['CASOS'].sum():,}".replace(",", ".")
    indicador = f"{nombre}: {total_texto} registros, 2019."
    return nueva_mensual, nueva_edad, indicador


@app.callback(
    Output("grafico-mapa", "figure"),
    Output("grafico-sexo", "figure"),
    Output("indicador-panorama", "children"),
    Output("marco-grafico-sexo", "style"),
    Input("filtro-panorama", "value"),
)
def actualizar_panorama_territorial(codigo):
    """Enfoca mapa, barras apiladas e indicador con el filtro de Panorama.

    TODOS conserva los 33 territorios. Un código selecciona sus conteos y
    geometría sin modificar los originales ni el filtro de mensual/edad.
    La altura del marco evita comprimir 33 barras o estirar una única barra.
    """
    if codigo == "TODOS":
        territorio_seleccionado = departamental
        sexo_seleccionado = sexo_departamental
        limites_seleccionados = limites
        # Retira la altura de detalle y recupera la altura nacional del CSS.
        estilo_marco_sexo = {}
    else:
        territorio_seleccionado = departamental[
            departamental["COD_DEPARTAMENTO"] == codigo
        ]
        sexo_seleccionado = sexo_departamental[
            sexo_departamental["COD_DEPARTAMENTO"] == codigo
        ]

        # Empareja el mapa con las mismas claves que el resumen seleccionado.
        limites_seleccionados = dict(limites)
        limites_seleccionados["features"] = [
            elemento
            for elemento in limites["features"]
            if elemento["properties"]["DPTO_CCDGO"] == codigo
        ]
        estilo_marco_sexo = {"height": "340px"}

    nombre = nombres_departamentos[codigo]
    nuevo_mapa = crear_mapa_departamental(
        territorio_seleccionado, limites_seleccionados
    )
    nuevo_sexo = crear_barras_sexo_departamento(sexo_seleccionado)
    nuevo_mapa.update_layout(
        title_text=f"{nombre}, 2019",
        margin={"l": 0, "r": 0, "t": 44, "b": 0},
    )

    # Conserva la misma escala de color al comparar país y departamento.
    nuevo_mapa.update_coloraxes(cmin=0, cmax=int(departamental["CASOS"].max()))
    nuevo_sexo.update_layout(title_text=f"{nombre}, 2019")

    total_texto = f"{territorio_seleccionado['CASOS'].sum():,}".replace(",", ".")
    indicador = f"{nombre}: {total_texto} registros, 2019."
    return nuevo_mapa, nuevo_sexo, indicador, estilo_marco_sexo


if __name__ == "__main__":
    # La comprobación local conserva los mensajes de error y evita doble carga.
    app.run(debug=True, use_reloader=False)
