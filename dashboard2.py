from sqlalchemy import create_engine
import pandas as pd
import plotly.express as px
import dash
from dash import dcc, html

# PostgreSQL credentials
username = 'postgres'
password = '2112'
host = 'localhost'  # or your PostgreSQL server IP
port = '5432'       # default PostgreSQL port
database = 'notas'

# PostgreSQL connection string
connection_string = f"postgresql+psycopg2://{username}:{password}@{host}:{port}/{database}"

# Create the SQLAlchemy engine
engine = create_engine(connection_string)

# Query the database
query = "SELECT * FROM COMPRA_2019_01"
df = pd.read_sql(query, engine)

# Data processing to match the second code
df_sorted = df.sort_values(by='total_bruto', ascending=False)  
df = df.dropna(subset=['estado_origem', 'total_bruto'])
df = df.sort_values(by='total_bruto', ascending=False)

# Create visualizations
bar_fig = px.bar(
    df,
    x='estado_origem',
    y=df['total_bruto'] / 1000,  # Converte para milhares
    title=' Quais estados ultrapassaram o valor de um milhão no total bruto? ',
    labels={'estado_origem': 'Estado', 'y': 'Valor Total Bruto (milhares)'},
    text_auto=True  
)

line_fig = px.line(
    df.sort_values(by='total_bruto', ascending=False),
    x='codigo_ibge_municipio_destino',
    y='total_bruto',
    color='estado_origem',
    title='Quais municípios dentro de cada estado têm os maiores valores totais brutos?',
    labels={
        'total_bruto': 'Valor Total Bruto',
        'codigo_ibge_municipio_destino': 'Código IBGE Municipio ',
        'estado_origem': 'Estados'
    }
)


df_pie_sorted = df.sort_values(by='icms', ascending=False)
pie_fig = px.pie(
    df_pie_sorted,
    names='estado_origem',
    values='total_bruto',
    title='Qual estado contribiu mais para o valor do ICMS?',
    labels={'estado_origem': 'Estado de Origem', 'total_bruto': 'Valor Total Bruto'}
)

hist_fig = px.histogram(
    df,
    x=df['total_bruto'] / 1000,
    title='A maioria dos valores está concentrada em qual faixa?',
    nbins=30,  
    log_y=True,  
    labels={'x': 'Valor Total Bruto'}
)

df_heat_sorted = df.sort_values(by=['descricao_cnae', 'estado_origem'], ascending=[False, False])
heat_fig = px.density_heatmap(
    df_heat_sorted,
    x='descricao_cnae',
    y='estado_origem',
    z='total_bruto',
    title='Qual Valor Total Bruto por Setor Econômico e Estado?',
    labels={'descricao_cnae': 'Setor Econômico', 'estado_origem': 'Estado de Origem', 'total_bruto': 'Valor Total Bruto'}
)

# Create the Dash app
app = dash.Dash(__name__)

app.layout = html.Div([
    html.H1("Dashboard"),
    dcc.Graph(figure=bar_fig),
    dcc.Graph(figure=line_fig),
    dcc.Graph(figure=pie_fig),
    dcc.Graph(figure=hist_fig),
    dcc.Graph(figure=heat_fig)
])

if __name__ == '__main__':
    app.run_server(debug=True)
