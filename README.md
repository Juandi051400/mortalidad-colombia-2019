# Mortalidad en Colombia, 2019

## Introducción

Proyecto académico de Aplicaciones I de la Maestría en Inteligencia Artificial de la Universidad de La Salle. Se desarrollará una aplicación web interactiva con Python, Plotly y Dash.

## Objetivo

Explorar la mortalidad en Colombia durante 2019 mediante visualizaciones de su distribución territorial, evolución mensual, causas de muerte, sexo y grupos de edad.

## Estado del proyecto

En desarrollo. La aplicación local muestra cuatro vistas de los registros de 2019: evolución mensual, mapa departamental, barras apiladas por sexo y departamento, y distribución por grupos de edad. Cada vista representa 244.355 registros. Se conservan los 93 registros de sexo indeterminado y los 23 de edad desconocida. Están pendientes las otras tres vistas y el despliegue público.

## Entorno de desarrollo

Python 3.14.0. Las versiones de los paquetes están registradas en requirements.txt.

## Estructura actual

- `app.py`: conexión de los datos y las figuras con la interfaz de Dash.
- `src/datos.py`: lectura de mortalidad y preparación de los resúmenes mensual, departamental, por departamento y sexo, y por grupo de edad.
- `src/graficos.py`: construcción del mapa, las barras apiladas por sexo y la distribución por grupos de edad, con adaptación de la cartografía para Plotly.
- `src/descargar_geografia.py`: descarga y comprobación de los límites departamentales.
- `src/explorar_datos.py`: exploración de hojas, categorías, conteos y correspondencias.
- `data/geo/`: cartografía departamental del DANE, versión 2018, descargada con simplificación.
- `data/raw/`: copias sin modificar de los Excel, excluidas de Git.
- `data/processed/`: carpeta destinada a futuros archivos derivados.
- `requirements.txt`: paquetes y versiones del entorno.

## Datos de entrada

Se utilizan los tres archivos Excel proporcionados para la actividad:

- `Anexo1.NoFetal2019_CE_15-03-23.xlsx`: base de defunciones.
- `Anexo2.CodigosDeMuerte_CE_15-03-23.xlsx`: catálogo de códigos y nombres de causas de muerte.
- `Divipola_CE_.xlsx`: códigos y nombres de departamentos y municipios.

Los archivos se ubican en `data/raw/`.

Documentación de referencia: [DANE — Estadísticas Vitales 2019](https://microdatos.dane.gov.co/index.php/catalog/696).

Fuente: Departamento Administrativo Nacional de Estadística: www.dane.gov.co .

## Cartografía del mapa

Fuente: Departamento Administrativo Nacional de Estadística (DANE), capa Departamento del [servicio geográfico MGN2019](https://geoportal.dane.gov.co/mparcgis/rest/services/MGN2019/Serv_CapasMGN_2019/FeatureServer/319).

El atributo DPTO_NANO identifica la versión cartográfica como 2018. Los registros de mortalidad analizados corresponden a 2019.

La descarga solicita coordenadas geográficas EPSG:4326, una tolerancia de simplificación de 0.005 grados y cinco decimales para facilitar la visualización web.

El GeoJSON guardado conserva esa descarga simplificada. Para dibujarlo, src/graficos.py adapta la orientación de los contornos sobre una copia en memoria, conservando el archivo descargado y los conteos.

Consulta las [condiciones de uso del Geoportal DANE](https://geoportal.dane.gov.co/acerca-del-geoportal/licencia-y-condiciones-de-uso/).

## Agrupación por edad

Se utilizan las once categorías definidas en el enunciado. Se conserva «Edad desconocida» (código 29), con 23 registros. La gráfica presenta conteos absolutos por categoría; los grupos de edad conocida abarcan intervalos de distinta duración.