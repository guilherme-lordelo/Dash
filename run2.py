import psycopg2
import pandas as pd
import plotly.express as px
import dash
from dash import dcc, html

# Configurações de conexão com PostgreSQL
host = 'localhost'
database = 'Tableau'
user = 'sa'
password = '895623'
port = '5432'

# Conectar ao banco de dados
conn = psycopg2.connect(
    host=host,
    database=database,
    user=user,
    password=password,
    port=port
)

# Carregar dados
query = "SELECT * FROM COM_COMPRA_2019_01"
df = pd.read_sql(query, conn)
conn.close()

# Ordenar o DataFrame pela coluna 'com_total_bruto' em ordem decrescente
df_sorted = df.sort_values(by='com_total_bruto', ascending=False)

# Criar gráficos
bar_fig = px.bar(
    df_sorted,
    x='com_estado_origem',
    y='com_total_bruto',
    title='Existe algum estado que se destaca significativamente em relação aos outros?',
    labels={'com_estado_origem': 'Estado', 'com_total_bruto': 'Valor Total Bruto'}
)

# Verificar valores únicos na coluna 'com_estado_destino'
print(df['com_cod_ibge_munic_destino'])

df['com_cod_ibge_munic_destino'] = df['com_cod_ibge_munic_destino'].astype(str)

line_fig = px.line(
    df.sort_values(by='com_total_bruto', ascending=False),
    x='com_cod_ibge_munic_destino',
    y='com_total_bruto',
    color='com_estado_origem',
    title='Quais municípios dentro de cada estado têm os maiores valores totais brutos?',
    labels={
        'com_total_bruto': 'Valor Total Bruto',
        'com_cod_ibge_munic_destino': 'Código IBGE Municipio',
        'com_estado_origem': 'Estados'
    }
)

df_pie_sorted = df.sort_values(by='com_icms', ascending=False)
pie_fig = px.pie(
    df_pie_sorted,
    names='com_estado_origem',
    values='com_total_bruto',
    title='Qual estado contribuiu mais para o valor do ICMS?',
    labels={'com_estado_origem': 'Estado de Origem', 'com_total_bruto': 'Valor Total Bruto'}
)

hist_fig = px.histogram(
    df,
    x=df['com_total_bruto'] / 1000,
    title='Distribuição dos Valores por Faixa',
    nbins=30,
    histnorm='percent',
    labels={'x': 'Valor Total Bruto', 'y': 'Porcentagem (%)'}
)

df_heat_sorted = df.sort_values(by=['com_estado_origem', 'com_estado_destino'], ascending=[False, False])
heat_fig = px.density_heatmap(
    df_heat_sorted,
    x='com_estado_origem',
    y='com_estado_destino',
    title='Qual é a relação entre os estados de origem e os estados de destino em termos do valor total bruto?',
    labels={'com_estado_origem': 'Estado de Origem', 'com_estado_destino': 'Estado de Destino', 'com_total_bruto': 'Valor Total Bruto'}
)

# Inicializar o app Dash
app = dash.Dash(__name__)

# Layout do dashboard
app.layout = html.Div([
    html.H1("Dashboard"),
    dcc.Graph(figure=bar_fig),
    dcc.Graph(figure=line_fig),
    dcc.Graph(figure=pie_fig),
    dcc.Graph(figure=hist_fig),
    dcc.Graph(figure=heat_fig)
])

# Rodar o app
if __name__ == '__main__':
    app.run_server(debug=True)
