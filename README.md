# Mortalidad en Colombia, 2019

## Introducción

Proyecto académico de Aplicaciones I de la Maestría en Inteligencia Artificial de la Universidad de La Salle. Se desarrollará una aplicación web interactiva con Python, Plotly y Dash.

## Objetivo

Explorar la mortalidad en Colombia durante 2019 mediante visualizaciones de su distribución territorial, evolución mensual, causas de muerte, sexo y grupos de edad.

## Estado del proyecto

En desarrollo. La aplicación local muestra siete vistas: evolución mensual, mapa departamental, barras por sexo y departamento, distribución por edad, tabla de diez causas, barras de cinco municipios por X95 y circular municipal.

La base contiene 244.355 registros, incluidos 93 de sexo indeterminado y 23 de edad desconocida. Las vistas de principales causas y municipios muestran los subconjuntos indicados en sus títulos.

Están pendientes la organización del dashboard, los filtros mediante callbacks, el despliegue público y la documentación final con capturas, interpretaciones e instrucciones de instalación.

## Entorno de desarrollo

Python 3.14.0. Las versiones de los paquetes están registradas en requirements.txt.

## Estructura actual

- `app.py`: conexión de los datos y las figuras con la interfaz de Dash.
- `src/datos.py`: lectura de mortalidad y catálogos, validaciones, resúmenes y selección de municipios.
- `src/graficos.py`: construcción del mapa, barras por sexo y por X95, distribución de edad, tabla de causas y circular municipal; adaptación de la cartografía para Plotly.
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

## Criterios de causas y municipios

Las causas se agrupan por categorías CIE-10 de tres caracteres. En memoria se ajustan un espacio final del catálogo, las variantes textuales de T81/X16 y cinco correspondencias de aterosclerosis a I70, contrastadas con la [CIE-10 de OPS](https://ais.paho.org/classifications/chapters/CAP09.html). Los Excel originales se conservan.

Los territorios se relacionan mediante COD_DANE completo. Mapiripana conserva su código histórico 94663 y se completa su tipo como área no municipalizada, según la [nota de DANE](https://microdatos.dane.gov.co/index.php/catalog/743/variable/F48/V4740?name=NPCEP9B).

El ranking X95 incluye ese código y sus subcódigos: 9.273 registros en total. Representa ese subconjunto de causas, sin equipararlo al total de homicidios.

Para la circular, ante la ausencia de una fórmula en el enunciado, se adopta el menor conteo absoluto de todas las causas entre municipios con registros positivos. Se ordena por casos y se desempata por código DANE. Los diez seleccionados reúnen once registros; los porcentajes corresponden a esa selección.

Guataquí, Pulí, Busbanzá y Jordán se informan aparte como municipios sin registros en esta base. Nuevo Belén de Bajirá se excluye de esa referencia de 2019 por su [creación en 2023](https://www.registraduria.gov.co/8-972-ciudadanos-estan-habilitados-para-votar-en-las-primeras-elecciones-de.html). Estos resultados describen registros de los anexos y no constituyen tasas de mortalidad.