import pandas as pd
import numpy as np
import random

# Função para gerar valores aleatórios
def generate_random_values():
    return {
        "Distância": random.randint(80, 370),
        "Custo Urgência": round(random.uniform(0.15, 0.30), 2),
        "Custo Regular": round(random.uniform(0.10, 0.20), 2),
        "Custo Baixo": round(random.uniform(0.05, 0.10), 2),
        "Tempo Urgência": round(random.uniform(1, 5), 2),
        "Tempo Regular": round(random.uniform(2, 5), 2),
        "Tempo Alto": round(random.uniform(4, 6), 2),
        "Capacidade Envio Urgência": random.randint(800, 1200),
        "Capacidade Envio Regular": random.randint(600, 800),
        "Capacidade Envio Baixa": random.randint(400, 600),
        "Capacidade Recebimento Urgência": random.randint(900, 1400),
        "Capacidade Recebimento Regular": random.randint(700, 1000),
        "Capacidade Recebimento Baixa": random.randint(500, 700),
    }

# Armazéns de envio e recebimento
armazens_envio = ['A', 'B', 'C']
armazens_recebimento = [1, 2, 3, 4, 5, 6]

# Criar o DataFrame de armazéns
armazens_data = []
for envio in armazens_envio:
    for recebimento in armazens_recebimento:
        values = generate_random_values()
        armazens_data.append({
            "Armazém Envio": envio,
            "Armazém Recebimento": recebimento,
            **values
        })

df_armazens = pd.DataFrame(armazens_data)
#print(df_armazens.head())

# Produtos com pesos e quantidade distribuída entre os armazéns
produtos = ['Produto 1', 'Produto 2', 'Produto 3', 'Produto 4', 'Produto 5']
peso_produtos = [random.randint(30, 250) for _ in produtos]
quantidade_produtos = {armazem: {produto: random.randint(1000, 20000) for produto in produtos} for armazem in armazens_envio}

# Criando o DataFrame de produtos
produtos_data = []
for armazem, produtos_info in quantidade_produtos.items():
    for produto, quantidade in produtos_info.items():
        produto_info = {
            "Produto": produto,
            "Peso": peso_produtos[produtos.index(produto)],
            "Quantidade Disponível": quantidade,
            "Armazém de Distribuição": armazem
        }
        produtos_data.append(produto_info)

df_produtos = pd.DataFrame(produtos_data)
#print(df_produtos.head())

# Demandas dos armazéns de recebimento
demanda = {armazem: {f"Produto {i+1}": random.randint(500, 5000) for i in range(random.randint(2, 5))} for armazem in armazens_recebimento}

# Criando o DataFrame de demanda
demanda_data = []
for armazem, produtos_demanda in demanda.items():
    for produto, quantidade in produtos_demanda.items():
        prazo = random.randint(1, 48)  # Prazo em horas
        demanda_data.append({
            "Armazém Recebimento": armazem,
            "Produto": produto,
            "Quantidade Necessária": quantidade,
            "Prazo em Horas": prazo
        })

df_demanda = pd.DataFrame(demanda_data)
#print(df_demanda.head())

# Função de planejamento de transferência
def calcular_plano_envio(filtro="Regular"):
    df_plano = []

    # Mapear os dados de armazéns, produtos e demanda
    for _, armazem_envio in df_armazens.iterrows():
        for _, armazem_recebimento in df_demanda.iterrows():
            if armazem_envio['Armazém Recebimento'] == armazem_recebimento['Armazém Recebimento']:
                # Calcular o custo e o tempo de transferência baseado no filtro
                custo, tempo, capacidade_envio, capacidade_recebimento = 0, 0, 0, 0

                if filtro == "Urgência":
                    custo = armazem_envio['Custo Urgência']
                    tempo = armazem_envio['Tempo Urgência']
                    capacidade_envio = armazem_envio['Capacidade Envio Urgência']
                    capacidade_recebimento = armazem_envio['Capacidade Recebimento Urgência']
                elif filtro == "Regular":
                    custo = armazem_envio['Custo Regular']
                    tempo = armazem_envio['Tempo Regular']
                    capacidade_envio = armazem_envio['Capacidade Envio Regular']
                    capacidade_recebimento = armazem_envio['Capacidade Recebimento Regular']
                else:
                    custo = armazem_envio['Custo Baixo']
                    tempo = armazem_envio['Tempo Alto']
                    capacidade_envio = armazem_envio['Capacidade Envio Baixa']
                    capacidade_recebimento = armazem_envio['Capacidade Recebimento Baixa']

                # Determinar a quantidade planejada para envio (simulação simples)
                quantidade_enviar = min(armazem_recebimento['Quantidade Necessária'], capacidade_envio)

                # Adicionar o plano
                df_plano.append({
                    "Armazém Envio": armazem_envio['Armazém Envio'],
                    "Armazém Recebimento": armazem_recebimento['Armazém Recebimento'],
                    "Produto": armazem_recebimento['Produto'],
                    "Quantidade Planejada Envio": quantidade_enviar,
                    "Prazo Para Recebimento": tempo
                })

    return pd.DataFrame(df_plano)

# Calcular o plano com filtro Regular
df_plano_regular = calcular_plano_envio(filtro="Regular")
#print(df_plano_regular.head())

import streamlit as st
import plotly.express as px
import networkx as nx

# Exibir o filtro de prioridade
filtro = st.selectbox("Selecione a prioridade", ["Urgência", "Regular", "Baixa"])

# Calcular o plano de envio conforme o filtro
df_plano_filtrado = calcular_plano_envio(filtro=filtro)

# Exibir a tabela de plano de transferência
st.write("Plano de Transferência:", df_plano_filtrado)

# Visualização Gráfica
G = nx.DiGraph()
for _, row in df_plano_filtrado.iterrows():
    G.add_edge(row['Armazém Envio'], row['Armazém Recebimento'], weight=row['Quantidade Planejada Envio'])

# Gerar o gráfico de rede
fig = px.sunburst(df_plano_filtrado, path=['Armazém Envio', 'Armazém Recebimento'], values='Quantidade Planejada Envio')
st.plotly_chart(fig)


