
# %%
import pandas as pd
import streamlit as st
import plotly.express as px
import os
import matplotlib.pyplot as plt
import seaborn as sns

# Definir o caminho para o arquivo de dados
caminho_dados = os.path.join(os.path.dirname(__file__), '1000000-bandcamp-sales.parquet')

# Carregar os dados a partir do arquivo .parquet
data = pd.read_parquet(caminho_dados)

# Verificar se a coluna de data existe e converter para datetime
if 'utc_date' in data.columns:
    data['utc_date'] = pd.to_datetime(data['utc_date'], errors='coerce')

# Remover caracteres indesejados e garantir que as colunas sejam do tipo float
data['amount_paid_usd'] = data['amount_paid_usd'].replace('[^\d.]', '', regex=True).fillna(0).astype(float)
data['amount_over_fmt'] = data['amount_over_fmt'].replace('[^\d.]', '', regex=True).fillna(0).astype(float)

# Calcular a porcentagem a mais
data['porcentagem_a_mais'] = (data['amount_over_fmt'] / data['amount_paid_usd']) * 100
data['porcentagem_a_mais'] = data['porcentagem_a_mais'].fillna(0)
data['porcentagem_a_mais'] = data['porcentagem_a_mais'].round(2).astype(str) + '%'

# Calcular métricas principais
valor_total_arrecadado = data['amount_paid_usd'].sum()
total_de_registros = data['amount_paid_usd'].count()
ticket_medio = valor_total_arrecadado / total_de_registros
artistas = data['artist_name'].nunique()

# Títulos
st.header("Data GlowUp 37")
st.divider()

# Exibir informações resumidas
st.write("**O conjunto de dados do BandCamp se trata de um pequeno recorte de tempo deste DataFrame, com um conjunto total de 1KK de linhas e os registros de compra desse período. Acompanhe abaixo algumas métricas:**")
st.divider()

# Exibir métricas
st.metric(label="Valor Movimentado na plataforma", value=f"${valor_total_arrecadado:,.2f}")
st.metric(label="Ticket Médio", value=f"${ticket_medio:,.2f}")
st.metric(label="Artistas na Plataforma", value=f"{artistas}")

st.subheader("Veja aqui, um breve resumo do conjunto de dados", divider="gray")

# Exibir os dados na tabela, incluindo a nova coluna
st.write(data.head(1000)[['_id', 'item_price','artist_name', 'album_title', 'country', 'amount_paid_usd', 'amount_over_fmt']])



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

# Ticket Médio por Artista
ticket_medio_por_artista = data.groupby('artist_name')['amount_paid_usd'].mean().reset_index()
ticket_medio_por_artista.columns = ['artist_name', 'ticket_medio']
top_20_ticket_medio = ticket_medio_por_artista.sort_values(by='ticket_medio', ascending=False).head(20)
top_20_ticket_medio.reset_index(drop=True, inplace=True)
top_20_ticket_medio.index = top_20_ticket_medio.index + 1  # Define o índice para começar em 1
top_20_ticket_medio['ticket_medio'] = top_20_ticket_medio['ticket_medio'].apply(lambda x: f"${x:,.2f}")
st.write("**Top 20 Artistas com Maior Ticket Médio:**")
st.dataframe(top_20_ticket_medio)

# Engajamento
data['valor_total_pago'] = data['amount_paid_usd'] 

# Filtrar bandas com 50 ou mais registros de _id
contagem_bandas = data['artist_name'].value_counts()
bandas_com_50_ou_mais = contagem_bandas[contagem_bandas >= 50].index
data_filtrada = data[data['artist_name'].isin(bandas_com_50_ou_mais)]

# Calcular engajamento por banda
engajamento_por_banda = data_filtrada.groupby('artist_name').agg({
    'amount_paid_usd': 'sum',
    'amount_over_fmt': 'sum'
}).reset_index()

# Calcular porcentagem a mais
engajamento_por_banda['porcentagem_a_mais'] = (engajamento_por_banda['amount_over_fmt'] / engajamento_por_banda['amount_paid_usd']) * 100

# Selecionar top 20 bandas com maior engajamento
top_20_engajamento = engajamento_por_banda.sort_values(by='porcentagem_a_mais', ascending=False).head(20)
top_20_engajamento.reset_index(drop=True, inplace=True)
top_20_engajamento.index = top_20_engajamento.index + 1
top_20_engajamento['porcentagem_a_mais'] = top_20_engajamento['porcentagem_a_mais'].round(2).astype(str) + '%'

# Exibir resultados
st.write("**Top 20 Bandas com Maior Engajamento:**")
st.dataframe(top_20_engajamento[['artist_name', 'amount_paid_usd', 'amount_over_fmt', 'porcentagem_a_mais']])

# Análise de Popularidade por País
ticket_medio_por_pais = data.groupby('country')['amount_paid_usd'].mean().reset_index()
ticket_medio_por_pais.columns = ['País', 'Ticket Médio']
top_20_paises_ticket_medio = ticket_medio_por_pais.sort_values(by='Ticket Médio', ascending=False).head(20)
top_20_paises_ticket_medio['Ticket Médio'] = top_20_paises_ticket_medio['Ticket Médio'].round(2).apply(lambda x: f"${x:,.2f}")
st.write("**Top 20 Países com Maior Ticket Médio :**")
st.dataframe(top_20_paises_ticket_medio)

# Histograma dos Valores Pagos
st.write("**Distribuição dos Valores Pagos (Amount Paid USD):**")
fig, ax = plt.subplots(figsize=(10, 6))
sns.histplot(data['amount_paid_usd'], bins=30, kde=True, ax=ax)
ax.set_title("Distribuição dos Valores Pagos (Amount Paid USD)")
ax.set_xlabel("Amount Paid USD")
ax.set_ylabel("Frequência")
st.pyplot(fig)

# Boxplot dos Valores Pagos
st.write("**Boxplot dos Valores Pagos (Amount Paid USD):**")
fig2, ax2 = plt.subplots(figsize=(10, 4))
sns.boxplot(x=data['amount_paid_usd'], ax=ax2)
ax2.set_title("Boxplot dos Valores Pagos (Amount Paid USD)")
ax2.set_xlabel("Amount Paid USD")
st.pyplot(fig2)



# %%
