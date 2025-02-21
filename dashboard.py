import os
from sqlalchemy import create_engine
import pandas as pd
import plotly.express as px
import dash
from dash import dcc, html, Input, Output

# Configuração do banco de dados
username = os.getenv('DB_USERNAME')
password = os.getenv('DB_PASSWORD')
host = os.getenv('DB_HOST')
port = os.getenv('DB_PORT')
database = os.getenv('DB_NAME')

connection_string = f"postgresql+psycopg2://{username}:{password}@{host}:{port}/{database}"
engine = create_engine(connection_string)

# Lista de meses disponíveis (ajuste conforme necessário)
meses_disponiveis = [f'COMPRA_2019_{str(m).zfill(2)}' for m in range(1, 13)]

app = dash.Dash(__name__, external_stylesheets=['https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css'])

app.layout = html.Div([
    html.Div([
        html.H1("Dashboard", className="text-center mb-4 p-3 bg-primary text-white"),
        dcc.Dropdown(
            id='mes-dropdown',
            options=[{'label': mes.replace("COMPRA_2019_", "Mês "), 'value': mes} for mes in meses_disponiveis],
            value='COMPRA_2019_01',
            clearable=False,
            className='mb-4'
        ),
    ], className="container"),

    html.Div(id='graficos-container', className='container')
])

@app.callback(
    Output('graficos-container', 'children'),
    Input('mes-dropdown', 'value')
)
def atualizar_graficos(tabela_selecionada):
    query = f"SELECT * FROM {tabela_selecionada}"
    df = pd.read_sql(query, engine)

    df['total_bruto'] = pd.to_numeric(df['total_bruto'], errors='coerce')
    df['icms'] = pd.to_numeric(df['icms'], errors='coerce')
    df = df.dropna(subset=['estado_origem', 'estado_destino', 'total_bruto'])

    # Criar gráficos dinamicamente
    df_filtrado = df[df['estado_origem'] != 'BA']
    estados_ordenados = df_filtrado.groupby('estado_origem')['total_bruto'].sum().sort_values(ascending=False).index.tolist()

    heatmap_fig = px.density_heatmap(
        df_filtrado,
        x='estado_destino',
        y='estado_origem',
        z='total_bruto',
        category_orders={'estado_destino': estados_ordenados, 'estado_origem': estados_ordenados},
        title='Fluxo comercial com a Bahia',
        color_continuous_scale='Blues',
        height=400,
        width=1000
    )

    df_top_estados = df.groupby('estado_origem')['total_bruto'].sum().nlargest(5).reset_index().sort_values('total_bruto', ascending=True)
    state_bar = px.bar(
        df_top_estados,
        x='total_bruto',
        y='estado_origem',
        orientation='h',
        title='Estados com maior arrecadação',
        height=400
    )

    df_cnae = df.groupby('cnae')['total_bruto'].sum().nlargest(10).reset_index().sort_values('total_bruto', ascending=True)
    cnae_line = px.line(
        df_cnae,
        x='cnae',
        y='total_bruto',
        title='Atividades econômicas com maior arrecadação',
        height=400,
        markers=True
    )

    df_grouped = df.groupby('estado_origem')[['total_bruto', 'icms']].sum().reset_index().sort_values('total_bruto', ascending=False)
    estados_ordenados = df_grouped['estado_origem'].tolist()
    df_melted = df_grouped.melt(id_vars='estado_origem', value_vars=['total_bruto', 'icms'], var_name='Metrica', value_name='Valor')
    df_melted['Metrica'] = df_melted['Metrica'].replace({'total_bruto': 'Valor Bruto', 'icms': 'ICMS'})

    stacked_bar = px.bar(
        df_melted,
        x='estado_origem',
        y='Valor',
        color='Metrica',
        title='Diferença entre Valor Bruto e ICMS por Estado',
        barmode='group',
        height=500
    )

    df_cfop = df['cfop'].value_counts().nlargest(5).reset_index()
    cfop_pie = px.pie(
        df_cfop,
        names='cfop',
        values='count',
        title='CFOP mais utilizados',
        height=400
    )

    return [
        html.Div([dcc.Graph(figure=heatmap_fig)], className='card mb-4'),
        html.Div([dcc.Graph(figure=state_bar)], className='card mb-4'),
        html.Div([
            html.Div([dcc.Graph(figure=cnae_line)], className='col-md-6'),
            html.Div([dcc.Graph(figure=cfop_pie)], className='col-md-6')
        ], className='row'),
        html.Div([dcc.Graph(figure=stacked_bar)], className='card mb-4')
    ]

if __name__ == '__main__':
    app.run_server(debug=False, host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))
