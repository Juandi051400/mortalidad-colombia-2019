# Mortalidad en Colombia, 2019

## Introducción

Proyecto académico de Aplicaciones I de la Maestría en Inteligencia Artificial de la Universidad de La Salle. Se desarrollará una aplicación web interactiva con Python, Plotly y Dash.

## Objetivo

Explorar la mortalidad en Colombia durante 2019 mediante visualizaciones de su distribución territorial, evolución mensual, causas de muerte, sexo y grupos de edad.

## Estado del proyecto

En desarrollo.

## Entorno de desarrollo

Python 3.14.0. Las versiones de los paquetes están registradas en requirements.txt.

## Estructura actual

- `data/raw/`: copias sin modificar de los Excel de la actividad, excluidas de Git.
- `data/processed/`: archivos derivados de la preparación de datos.
- `src/explorar_datos.py`: inspección de hojas y muestras iniciales.

## Datos de entrada

Se utilizan los tres archivos Excel proporcionados para la actividad:

- `Anexo1.NoFetal2019_CE_15-03-23.xlsx`: base de defunciones.
- `Anexo2.CodigosDeMuerte_CE_15-03-23.xlsx`: catálogo de códigos y nombres de causas de muerte.
- `Divipola_CE_.xlsx`: códigos y nombres de departamentos y municipios.

Los archivos se ubican en `data/raw/`.

Documentación de referencia: [DANE — Estadísticas Vitales 2019](https://microdatos.dane.gov.co/index.php/catalog/696).

Fuente: Departamento Administrativo Nacional de Estadística: www.dane.gov.co .