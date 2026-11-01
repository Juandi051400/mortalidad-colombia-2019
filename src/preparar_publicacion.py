"""Prepara resúmenes estadísticos para publicar el dashboard.

Fuentes: anexos de mortalidad, causas y Divipola de la actividad.
Reutiliza la lectura y las agrupaciones definidas en src.datos.
Exporta conteos nacionales y departamentales, sin registros individuales.
"""

from pathlib import Path

from src.datos import (
    cargar_catalogo_causas,
    cargar_catalogo_municipios,
    cargar_mortalidad_2019,
    resumir_por_causa,
    resumir_por_departamento,
    resumir_por_departamento_y_sexo,
    resumir_por_grupo_edad,
    resumir_por_mes,
    resumir_por_municipio,
    resumir_para_filtro_departamental,
    seleccionar_menores_municipios,
)


def guardar_resumen(tabla, nombre, carpeta_salida, total_esperado):
    """Guarda un resumen si sus casos suman el total de referencia.

    La referencia corresponde a la base completa o al subconjunto analizado.
    """
    total_obtenido = tabla["CASOS"].sum()
    if total_obtenido != total_esperado:
        raise ValueError(f"El resumen {nombre} no conserva su total.")

    ruta_salida = carpeta_salida / f"{nombre}.csv"
    tabla.to_csv(ruta_salida, index=False, encoding="utf-8")
    print(
        f"{nombre}.csv: {len(tabla)} filas, "
        f"{total_obtenido} registros"
    )


def preparar_publicacion():
    """Prepara y exporta los resúmenes estadísticos del dashboard."""
    raiz = Path(__file__).resolve().parent.parent
    ruta_excel = (
        raiz / "data" / "raw" / "Anexo1.NoFetal2019_CE_15-03-23.xlsx"
    )
    carpeta_salida = raiz / "data" / "processed"
    carpeta_salida.mkdir(parents=True, exist_ok=True)

    datos = cargar_mortalidad_2019(ruta_excel)
    ruta_divipola = raiz / "data" / "raw" / "Divipola_CE_.xlsx"

    # Reutiliza los nombres departamentales en el resumen por sexo.
    departamental = resumir_por_departamento(datos, ruta_divipola)
    sexo_departamental = resumir_por_departamento_y_sexo(
        datos, departamental
    )

    ruta_catalogo = (
        raiz / "data" / "raw" / "Anexo2.CodigosDeMuerte_CE_15-03-23.xlsx"
    )

    # Reutiliza los ajustes documentados del catálogo de causas.
    catalogo_categorias = cargar_catalogo_causas(ruta_catalogo)
    resumen_causas = resumir_por_causa(datos, catalogo_categorias)

    # Prepara los conteos departamentales para las vistas filtrables.
    tablas_filtro = resumir_para_filtro_departamental(datos, departamental)

    # Aplica el criterio acordado: X95 y todos sus subcódigos.
    catalogo_municipal = cargar_catalogo_municipios(ruta_divipola)
    es_x95 = datos["COD_MUERTE"].str.startswith("X95", na=False)
    datos_x95 = datos[es_x95]
    resumen_x95 = resumir_por_municipio(datos_x95, catalogo_municipal)

    # Conserva la selección de municipios ya definida para la circular.
    resumen_municipal_completo = resumir_por_municipio(
        datos, catalogo_municipal
    )
    menores_municipios = seleccionar_menores_municipios(
        resumen_municipal_completo
    )

    # Identifica las referencias del catálogo ausentes de esta base.
    sin_registros = catalogo_municipal[
        ~catalogo_municipal["COD_DANE"].isin(
            resumen_municipal_completo["COD_DANE"]
        )
    ]
    municipios_sin_registros = sin_registros[
        sin_registros["TIPO_TERRITORIO"] == "Municipio"
    ]

    # Mantiene la exclusión histórica documentada en el README:
    # Nuevo Belén de Bajirá fue creado en 2023.
    municipios_sin_registros = municipios_sin_registros[
        municipios_sin_registros["COD_DANE"] != "27493"
    ]
    tablas = {
        "mensual_2019": resumir_por_mes(datos),
        "edad_2019": resumir_por_grupo_edad(datos),
        "departamental_2019": departamental,
        "sexo_departamental_2019": sexo_departamental,
        "causas_2019": resumen_causas,
        "mensual_departamental_2019": tablas_filtro["mensual"],
        "edad_departamental_2019": tablas_filtro["edad"],
    }

    for nombre, tabla in tablas.items():
        guardar_resumen(tabla, nombre, carpeta_salida, len(datos))

    # Comprueba X95 contra sus registros seleccionados.
    guardar_resumen(
        resumen_x95, "x95_municipal_2019", carpeta_salida, len(datos_x95)
    )

    # Referencia de la selección ya comprobada para estos anexos de 2019.
    guardar_resumen(
        menores_municipios, "menores_municipios_2019", carpeta_salida, 11
    )

    ruta_referencias = carpeta_salida / "municipios_sin_registros_2019.csv"
    municipios_sin_registros.to_csv(
        ruta_referencias,
        columns=["COD_DANE", "DEPARTAMENTO", "MUNICIPIO"],
        index=False,
        encoding="utf-8",
    )
    print(
        "municipios_sin_registros_2019.csv: "
        f"{len(municipios_sin_registros)} municipios de referencia"
    )


if __name__ == "__main__":
    preparar_publicacion()
