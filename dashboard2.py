import os
from sqlalchemy import create_engine
import pandas as pd
import plotly.express as px
import dash
from dash import dcc, html

# PostgreSQL credentials
"""
username = 'postgres'
password = '2112'
host = 'localhost'  # or your PostgreSQL server IP
port = '5432'       # default PostgreSQL port
database = 'notas'
"""

# Use environment variables for sensitive info
username = os.getenv('DB_USERNAME')
password = os.getenv('DB_PASSWORD')
host = os.getenv('DB_HOST')
port = os.getenv('DB_PORT')  # Default PostgreSQL port
database = os.getenv('DB_NAME')

# PostgreSQL connection string
connection_string = f"postgresql+psycopg2://{username}:{password}@{host}:{port}/{database}"

# Create the SQLAlchemy engine
engine = create_engine(connection_string)

# Query the database (fetch a single row)
query = "SELECT * FROM COMPRA_2019_01 LIMIT 1"
df = pd.read_sql(query, engine)

# Data processing (if needed)
df_sorted = df.sort_values(by='total_bruto', ascending=False)  
df = df.dropna(subset=['estado_origem', 'total_bruto'])
df = df.sort_values(by='total_bruto', ascending=False)

# Create visualizations (keep the same as before)
bar_fig = px.bar(
    df,
    x='estado_origem',
    y=df['total_bruto'] / 1000,  # Converte para milhares
    title=' Quais estados ultrapassaram o valor de um milh├úo no total bruto? ',
    labels={'estado_origem': 'Estado', 'y': 'Valor Total Bruto (milhares)'},
    text_auto=True  
)

line_fig = px.line(
    df.sort_values(by='total_bruto', ascending=False),
    x='codigo_ibge_municipio_destino',
    y='total_bruto',
    color='estado_origem',
    title='Quais munic├¡pios dentro de cada estado t├¬m os maiores valores totais brutos?',
    labels={
        'total_bruto': 'Valor Total Bruto',
        'codigo_ibge_municipio_destino': 'C├│digo IBGE Municipio ',
        'estado_origem': 'Estados'
    }
)

# Other visualizations like pie_fig, hist_fig, and heat_fig remain the same...

# Create the Dash app
app = dash.Dash(__name__)

app.layout = html.Div([
    html.H1("Dashboard"),
    # Display the first row of data
    html.Div([
        html.H3(f"First Row from COMPRA_2019_01: {df.iloc[0].to_dict()}")
    ]),
    dcc.Graph(figure=bar_fig),
    dcc.Graph(figure=line_fig),
    # other dcc.Graphs as before...
])

if __name__ == '__main__':
    app.run_server(debug=True, host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))
