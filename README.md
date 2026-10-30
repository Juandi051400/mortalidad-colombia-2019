# Mortalidad en Colombia, 2019

## Introducción

Proyecto académico de Aplicaciones I de la Maestría en Inteligencia Artificial de la Universidad de La Salle. Se desarrollará una aplicación web interactiva con Python, Plotly y Dash.

## Objetivo

Explorar la mortalidad en Colombia durante 2019 mediante visualizaciones de su distribución territorial, evolución mensual, causas de muerte, sexo y grupos de edad.

## Estado del proyecto

En desarrollo. La aplicación local muestra la gráfica mensual de 2019 con doce meses y 244.355 registros. La lectura y el resumen mensual están separados de la pantalla. Están pendientes las otras seis vistas y el despliegue público.

## Entorno de desarrollo

Python 3.14.0. Las versiones de los paquetes están registradas en requirements.txt.

## Estructura actual

- `app.py`: interfaz de Dash y gráfica mensual.
- `src/datos.py`: lectura de la base y preparación del resumen mensual.
- `src/explorar_datos.py`: exploración de hojas, categorías y conteos.
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