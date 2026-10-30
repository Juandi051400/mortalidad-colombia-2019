from pathlib import Path

import pandas as pd
import plotly.express as px
from dash import Dash, dcc, html

# Localiza los datos desde este archivo, sin depender de la terminal.
raiz = Path(__file__).resolve().parent
ruta_excel = raiz / "data" / "raw" / "Anexo1.NoFetal2019_CE_15-03-23.xlsx"

datos = pd.read_excel(
    ruta_excel,
    sheet_name="No_Fetales_2019",
    usecols=["AÑO", "MES"],
    dtype=int,
    engine="openpyxl",
)

# Cuenta 2019 y ordena los meses como enteros, del 1 al 12.
datos = datos[datos["AÑO"] == 2019]
conteo = datos["MES"].value_counts().sort_index()
mensual = conteo.reset_index(name="CASOS")

figura = px.line(
    mensual,
    x="MES",
    y="CASOS",
    markers=True,
    labels={"MES": "Mes", "CASOS": "Registros"},
)
figura.update_xaxes(dtick=1)

# Facilita la lectura de cantidades completas en español.
figura.update_layout(separators=",.")
figura.update_yaxes(tickformat=",.0f")
figura.update_traces(
    hovertemplate="Mes: %{x}<br>Registros: %{y:,.0f}<extra></extra>"
)

app = Dash(__name__)

# Aplica formato al texto mostrado sin cambiar los conteos numéricos.
total_formateado = f"{mensual['CASOS'].sum():,}".replace(",", ".")

app.layout = [
    html.H1("Mortalidad en Colombia, 2019"),
    html.P(f"Filas representadas: {total_formateado}"),
    dcc.Graph(figure=figura),
]

if __name__ == "__main__":
    # Evita leer el Excel dos veces al iniciar el servidor de desarrollo.
    app.run(debug=True, use_reloader=False)