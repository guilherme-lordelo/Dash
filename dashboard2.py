import os
from sqlalchemy import create_engine
import pandas as pd
import plotly.express as px
import dash
from dash import dcc, html

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

query = "SELECT * FROM COMPRA_2019_01"
df = pd.read_sql(query, engine)

df['total_bruto'] = pd.to_numeric(df['total_bruto'], errors='coerce')
df['icms'] = pd.to_numeric(df['icms'], errors='coerce')
df = df.dropna(subset=['estado_origem', 'estado_destino', 'total_bruto'])

#Gráfico01
df_filtrado = df[df['estado_origem'] != 'BA']

estados_ordenados = (
    df_filtrado
    .groupby('estado_origem')['total_bruto']
    .sum()
    .sort_values(ascending=False)
    .index
    .tolist()
)

escala_cores = [
    '#c6dbef','#9ecae1','#6baed6','#4292c6',
    '#2171b5','#08519c','#08306b','#001530'
]

heatmap_fig = px.density_heatmap(
    df_filtrado,
    x='estado_destino',
    y='estado_origem',
    z='total_bruto',
    category_orders={'estado_destino': estados_ordenados, 'estado_origem': estados_ordenados},
    title='Qual o estado com maior fluxo comercial com a Bahia?',
    color_continuous_scale=escala_cores,
    height=400,
    width=1000,
    labels={'estado_destino': 'Destino', 'estado_origem': 'Origem', 'total_bruto': 'Valor'}
)

heatmap_fig.update_traces(
    texttemplate='R$ %{z:,.2f}',
    hovertemplate="Origem: %{y}<br>Destino: %{x}<br>Valor: R$ %{z:,.2f}",
    textfont={'size':10,'color':'white'},
    colorscale=[[0,'#c6dbef'],[0.2,'#9ecae1'],[0.35,'#6baed6'],[0.5,'#4292c6'],
                [0.65,'#2171b5'],[0.8,'#08519c'],[0.95,'#08306b'],[1,'#001530']]
)

#Gráfico02
df_top_estados = df.groupby('estado_origem')['total_bruto'].sum().nlargest(5).reset_index()
df_top_estados = df_top_estados.sort_values('total_bruto', ascending=True)

state_bar = px.bar(
    df_top_estados,
    x='total_bruto',  # Corrected column name
    y='estado_origem',
    orientation='h',
    title='Qual estado com maior volume comercial?',
    labels={'total_bruto': 'Valor Total Bruto', 'estado_origem': 'Estado'},
    height=400
)
state_bar.update_traces(texttemplate='R$ %{x:,.2f}', textposition='inside', marker_color='#1f77b4')

#Gráfico03
df_cnae = df.groupby('cnae')['total_bruto'].sum().nlargest(10).reset_index()
df_cnae = df_cnae.sort_values('total_bruto', ascending=True) 

cnae_line = px.line(
    df_cnae,
    x='cnae',  
    y='total_bruto',  
    title='Qual atividade econômica tem maior valor?',
    labels={
        'x': 'Código Atividade Econômica',
        'y': 'Valor Total Bruto (R$)'
    },
    height=400,
    markers=True  
)

cnae_line.update_traces(
    line_color='#1f77b4',  
    marker=dict(size=10, color='red')  
)

cnae_line.update_layout(
    xaxis=dict(title='Código Atividade Econômica', type='category'),  
    yaxis=dict(title='Valor Total Bruto (R$)')
)

## gráfico 04
df_grouped = df.groupby('estado_origem')[['total_bruto', 'icms']].sum().reset_index()

df_grouped = df_grouped.sort_values('total_bruto', ascending=False)
estados_ordenados = df_grouped['estado_origem'].tolist()

df_melted = df_grouped.melt(
    id_vars='estado_origem',
    value_vars=['total_bruto', 'icms'],
    var_name='Metrica',
    value_name='Valor'
)

df_melted['Metrica'] = df_melted['Metrica'].replace({
    'total_bruto': 'Valor Bruto',
    'icms': 'ICMS'
})

stacked_bar = px.bar(
    df_melted,
    x='estado_origem',
    y='Valor',
    color='Metrica',
    title='Qual estado apresenta maior diferença entre o Valor Total Bruto e o ICMS?',
    labels={'estado_origem': 'Estado de Origem', 'Valor': 'Valor (R$)'},
    barmode='group',
    height=500,
    category_orders={"estado_origem": estados_ordenados},
    color_discrete_map={
        'Valor Bruto': '#1f77b4',
        'ICMS': '#ff7f0e'
    }
)

stacked_bar.update_layout(
    xaxis_title='Estado (Ordenado por Valor Bruto)',
    yaxis_title='Valor Total em R$',
    legend_title_text='Tipo de Valor',
    hovermode='x unified'
)

stacked_bar.update_traces(
    hovertemplate="<b>%{x}</b><br>%{meta[0]}: R$ %{y:,.2f}<extra></extra>",
    meta=[df_melted['Metrica']]
)

#Gráfico05
df_cfop = df['cfop'].value_counts().nlargest(5).reset_index()
cfop_pie = px.pie(
    df_cfop,
    names='cfop',
    values='count',
    title='Qual CFOP mais utilizados nas transações?',
    height=400
)

app = dash.Dash(__name__, external_stylesheets=['https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css'])

app.layout = html.Div([
    html.Div([
        html.H1("Dashboard", className="text-center mb-4 p-3 bg-primary text-white")
    ]),
    
    html.Div([
        html.Div([dcc.Graph(figure=heatmap_fig, className='card mb-4')], className='col-12'),
        
        html.Div([
            #html.Div([dcc.Graph(figure=state_bar, className='card mb-4')], className='col-md-6'),
            html.Div([dcc.Graph(figure=cnae_line, className='card mb-4')], className='col-md-6'),  
            html.Div([dcc.Graph(figure=cfop_pie, className='card mb-4')], className='col-md-6')
        ], className='row'),
        
        html.Div([dcc.Graph(figure=state_bar, className='card mb-4')], className='col-12'),
        
        html.Div([dcc.Graph(figure=stacked_bar, className='card mb-4')], className='col-12')
    ], className='container')
])

if __name__ == '__main__':
    app.run_server(debug=False, host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))
