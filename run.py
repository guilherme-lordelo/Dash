from sqlalchemy import create_engine
import pandas as pd
import plotly.express as px
import dash
from dash import dcc, html

# PostgreSQL connection parameters
username = 'postgres'  # Replace with your PostgreSQL username
password = '2112'  # Replace with your PostgreSQL password
host = 'localhost'  # Replace with your PostgreSQL host (e.g., 'localhost' or an IP address)
port = '5432'  # Default PostgreSQL port
database = 'notas'  # Replace with your PostgreSQL database name

# PostgreSQL connection string
connection_string = f"postgresql+psycopg2://{username}:{password}@{host}:{port}/{database}"

# Create the SQLAlchemy engine
engine = create_engine(connection_string)

# Query to fetch data from your PostgreSQL table
query = "SELECT * FROM compra_2019_01"  # Replace with your table name
df = pd.read_sql(query, engine)

# Create visualizations
bar_fig = px.bar(df, x='estado_origem', y='total_bruto', title='Valor por Estado de Origem')  # Replace with your column names

line_fig = px.line(df, x='codigo_ibge_municipio_destino', y='total_bruto', title='Tendência ao Longo do Tempo')  # Replace with your column names

pie_fig = px.pie(df, names='estado_origem', values='total_bruto', title='Distribuição por Estado de Origem')  # Replace with your column names

hist_fig = px.histogram(df, x='total_bruto', title='Distribuição de Valores')  # Replace with your column names

heat_fig = px.density_heatmap(df, x='estado_origem', y='estado_destino', title='Mapa de Calor')  # Replace with your column names

# Create the Dash app
app = dash.Dash(__name__)

# Define the app layout
app.layout = html.Div([
    html.H1("Dashboard"),
    dcc.Graph(figure=bar_fig),
    dcc.Graph(figure=line_fig),
    dcc.Graph(figure=pie_fig),
    dcc.Graph(figure=hist_fig),
    dcc.Graph(figure=heat_fig)
])

# Run the app
if __name__ == '__main__':
    app.run_server(debug=True)
