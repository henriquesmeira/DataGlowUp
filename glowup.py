

# %%
import pandas as pd
import streamlit as st
import plotly.express as px

st.header('Data GlowUp 37', divider='red')
st.title('Análise de Dados do conjunto de informação do BandCamp')

# Carregar os dados
data = pd.read_csv('C:\\Users\\henri\\Desktop\\Data GlowUp\\1000000-bandcamp-sales.csv')

colunas_para_remover = ['slug_type', 'amount_paid' ,'currency' , 'art_url' , 'url']
data.drop(columns=colunas_para_remover, inplace=True)

# Reduzir a precisão dos dados numéricos (substitua 'coluna_numerica' pelas colunas reais)
colunas_numericas = ['amount_paid_usd', 'amount_over_fmt']
for coluna in colunas_numericas:
    data[coluna] = data[coluna].round(2)


# Converter o DataFrame para o formato Parquet
data.to_parquet('C:\\Users\\henri\\Desktop\\Data GlowUp\\1000000-bandcamp-sales.parquet', index=False)

# Transformar colunas em numéricas
data['amount_paid_usd'] = pd.to_numeric(data['amount_paid_usd'], errors='coerce')
data['amount_over_fmt'] = pd.to_numeric(data['amount_over_fmt'], errors='coerce')

# Calcular o valor total arrecadado
valor_total_arrecadado = data['amount_paid_usd'].sum() + data['amount_over_fmt'].sum()

# Calcular o ticket médio
total_de_registros = data['amount_paid_usd'].count()
ticket_medio = valor_total_arrecadado / total_de_registros

# Total de Artistas
artistas = data['artist_name'].nunique()

# Exibir informações resumidas
st.write("**O conjunto de dados do BandCamp se trata de um pequeno recorte de tempo a respeito desse DataFrame, com um conjunto total de 1KK de linhas, e os registros de compra desse período. Acompanhe abaixo algumas métricas :**")

# Exibir métricas

st.metric(label="Valor Movimentado na plataforma", value=f"${valor_total_arrecadado:,.2f}")

st.metric(label="Ticket Médio", value=f"${ticket_medio:,.2f}")

st.metric(label="Artistas na Plataforma", value=f"{artistas}")

st.subheader("Veja aqui, um breve resumo do conjunto de dados", divider="gray")

# Calcular a porcentagem a mais
data['porcentagem_a_mais'] = (data['amount_over_fmt'] / data['amount_paid_usd']) * 100
data['porcentagem_a_mais'] = data['porcentagem_a_mais'].fillna(0)
data['porcentagem_a_mais'] = data['porcentagem_a_mais'].round(2).astype(str) + '%'
data['amount_over_fmt'] = data['amount_over_fmt'].fillna(0)

# Filtros na barra lateral
artists = data["artist_name"].value_counts().index
artist_filter = st.sidebar.selectbox('Selecione os artistas:', artists)

# Exibir os dados na tabela, incluindo a nova coluna
st.write(data.head(1000)[['_id', 'artist_name', 'album_title', 'country', 'amount_paid_usd', 'amount_over_fmt']])

# Agrupar por artist_name e somar os valores pagos
agrupamento_valores = data.groupby('artist_name')['amount_paid_usd'].sum().reset_index()

# Ordenar pelos valores pagos e selecionar os 20 maiores
top_20_bandas = agrupamento_valores.sort_values('amount_paid_usd', ascending=False).head(20)

st.subheader("Os países com mais usuários da plataforma", divider="gray")

# Agrupar por country e contar os registros
agrupamento_paises = data.groupby('country')['amount_paid_usd'].count().reset_index()
agrupamento_paises.columns = ['País', 'Acessos']
top_20_paises = agrupamento_paises.sort_values('Acessos', ascending=False).head(20)

# Criar o gráfico de colunas com os 20 países com mais acessos
fig_paises = px.bar(
    top_20_paises, 
    x='País', 
    y='Acessos',
     title='',   
    labels={'País': 'País', 'Acessos': 'Acessos'},
    text='Acessos'
)

# Atualizar layout do gráfico
fig_paises.update_layout(
    xaxis_title='País',
    yaxis_title='Acessos',
    title_x=0.5
)

# Exibir gráfico
st.plotly_chart(fig_paises)

st.subheader("Os 20 artistas com maior faturamento", divider="gray")
# Criar o gráfico de colunas com as 20 bandas com maior faturamento
fig_bandas = px.bar(
    top_20_bandas, 
    x='artist_name', 
    y='amount_paid_usd', 
    title='', 
    labels={'artist_name': 'Nome da Banda', 'amount_paid_usd': 'Faturamento (USD)'},
    text='amount_paid_usd'
)

# Atualizar layout do gráfico
fig_bandas.update_layout(
    xaxis_title='Nome da Banda',
    yaxis_title='Faturamento (USD)',
    title_x=0.5
)

# Exibir gráfico
st.plotly_chart(fig_bandas)



# %%
