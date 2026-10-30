"""Descarga límites departamentales del DANE para preparar el mapa.

El servicio se publica como MGN2019, pero DPTO_NANO indica versión 2018.
La copia se simplifica para visualización y se guarda en data/geo/.
"""

import json
from pathlib import Path

import requests


def descargar_limites(ruta_salida):
    """Descarga, valida y guarda los límites en un Path de destino.

    Devuelve el GeoJSON para mostrar las comprobaciones de la descarga.
    """
    url_servicio = (
        "https://geoportal.dane.gov.co/mparcgis/rest/services/"
        "MGN2019/Serv_CapasMGN_2019/FeatureServer/319/query"
    )

    parametros = {
        # Son identificadores internos comprobados; no son códigos DANE.
        "objectIds": ",".join(str(numero) for numero in range(1, 34)),
        "outFields": "DPTO_CCDGO,DPTO_CNMBRE,DPTO_NANO",
        "returnGeometry": "true",
        # En longitud/latitud, la tolerancia de simplificación va en grados.
        "outSR": 4326,
        "maxAllowableOffset": 0.005,
        "geometryPrecision": 5,
        "f": "geojson",
    }

    respuesta = requests.get(url_servicio, params=parametros, timeout=60)
    respuesta.raise_for_status()
    limites = respuesta.json()

    # Comprueba el contenido antes de crear el archivo local.
    if limites.get("type") != "FeatureCollection":
        raise ValueError("El servicio no devolvió una colección GeoJSON.")

    elementos = limites["features"]
    codigos = [elemento["properties"]["DPTO_CCDGO"] for elemento in elementos]

    if len(elementos) != 33 or len(set(codigos)) != 33:
        raise ValueError("Se esperaban 33 territorios con códigos únicos.")

    if any(elemento["geometry"] is None for elemento in elementos):
        raise ValueError("La descarga contiene territorios sin geometría.")

    # Verifica el año que justifica el nombre del archivo de salida.
    versiones = {elemento["properties"]["DPTO_NANO"] for elemento in elementos}
    if versiones != {2018}:
        raise ValueError("La versión cartográfica cambió; revisa la fuente.")

    ruta_salida.parent.mkdir(parents=True, exist_ok=True)
    ruta_salida.write_text(
        json.dumps(limites, ensure_ascii=False),
        encoding="utf-8",
    )
    return limites


if __name__ == "__main__":
    # Localiza el proyecto desde este archivo, sin depender de la terminal.
    raiz = Path(__file__).resolve().parent.parent
    salida = raiz / "data" / "geo" / "departamentos_mgn_2018.geojson"

    limites = descargar_limites(salida)
    elementos = limites["features"]
    codigos = [elemento["properties"]["DPTO_CCDGO"] for elemento in elementos]
    versiones = {elemento["properties"]["DPTO_NANO"] for elemento in elementos}

    print("Archivo guardado:", salida)
    print("Territorios:", len(elementos))
    print("Códigos:", sorted(codigos))
    print("Versión cartográfica:", sorted(versiones))