#Manipulação de dados
import pandas as pd

#Leitura de url
import requests

#Tratamento de valores string
import inflection

#Visualizaçào gráfica
import plotly.express as px
import plotly.graph_objects as go

#Criaçãoa de mapas
import folium
from folium.plugins import MarkerCluster

#Criação de dashboard
import streamlit as st
from streamlit_folium import folium_static
from PIL import Image

#Configurações iniciais da página
st.set_page_config(page_title='Visão Geral', page_icon='🎯', layout='wide') #'wide' = use full screen

#============================================
# Funções utilizadas
#============================================



#Preenchimento do nome dos países
COUNTRIES = {
 1: "India",
 14: "Australia",
 30: "Brazil",
 37: "Canada",
 94: "Indonesia",
 148: "New Zeland",
 162: "Philippines",
 166: "Qatar",
 184: "Singapure",
 189: "South Africa",
 191: "Sri Lanka",
 208: "Turkey",
 214: "United Arab Emirates",
 215: "England",
 216: "United States of America",
 }
def country_name(country_id):
    return COUNTRIES[country_id]

currency = {'Botswana Pula(P)':'BWP',
            'Brazilian Real(R$)':'BRL',
            'Dollar($)':'USD',
            'Emirati Diram(AED)':'AED',
            'Indian Rupees(Rs.)':'INR',
            'Indonesian Rupiah(IDR)':'IDR',
            'NewZealand($)':'NZD',
            'Pounds(£)':'GBP',
            'Qatari Rial(QR)':'QAR',
            'Rand(R)':'ZAR',
            'Sri Lankan Rupee(LKR)':'LKR',
            'Turkish Lira(TL)':'TRY'}

#Criação do Tipo de Categoria de Comida
def create_price_tye(price_range):
    if price_range == 1:
        return "cheap"
    elif price_range == 2:
        return "normal"
    elif price_range == 3:
        return "expensive"
    else:
        return "gourmet"

#Criação do nome das Cores
COLORS = {
 "3F7E00": "darkgreen",
 "5BA829": "green",
 "9ACD32": "lightgreen",
 "CDD614": "orange",
 "FFBA00": "red",
 "CBCBC8": "darkred",
 "FF7800": "darkred",
 }

def get_rates(to_currency='USD'):
    '''
        Essa função vai obter a taxa de conversão DE uma determinada moeda PARA todas as outras moedas através de uma API;
        Por padrão, a moeda a ser convertida é o Dolar (USD), mas podemos alterar isso através do parâmetro to_currency
    '''
    url = 'https://api.exchangerate-api.com/v4/latest/'+str(to_currency)
    response = requests.get(url)
    data = response.json()

    return data

def convert_currency(amount, from_currency,data):
    '''
       Essa função vai realizar a conversão de um determinado valor (amount) a partir de uma determinada moeda (from_currency);
       Como a taxa que obtemos pela API é A PARTIR do dólar, aqui vamos fazer a operação inversa (divisão) para obter a 
       taxa de conversão PARA o dólar.
    '''
    # Salvando a taxa de conversão a partir do json recebido pela API
    exchange_rate = data['rates'][from_currency]
    # Como a coluna original possuía apenas números inteiros, vamos arredondar para manter também números inteiros
    converted_amount = round(amount/exchange_rate)

    return converted_amount

def color_name(color_code):
    return COLORS[color_code]

#Renomear as colunas do DataFrame
def rename_columns(dataframe):
    df = dataframe.copy()
    title = lambda x: inflection.titleize(x) #inflection é uma biblioteca de transformação e tratamento de strings (focado em plavras em Inglês)
    snakecase = lambda x: inflection.underscore(x)
    spaces = lambda x: x.replace(" ", "")
    cols_old = list(df.columns)
    cols_old = list(map(title, cols_old))
    cols_old = list(map(spaces, cols_old))
    cols_new = list(map(snakecase, cols_old))
    df.columns = cols_new
    return df

def clean_df(data_frame):
    #Alterando os códigos de Países da coluna Country Code para o nome do país
    data_frame['Country Code'] = data_frame['Country Code'].apply( country_name )

    #Alterando a coluna Prince Range de número para tipo
    data_frame.loc[:, 'Price range'] = data_frame.loc[:,'Price range'].apply( lambda x: create_price_tye(x))
    #ou
    #df.loc[:, 'Price range'] = df.loc[:,'Price range'].apply(create_price_tye)

    data_frame['Name Color'] = data_frame['Rating color'].apply( color_name )

    #Na base, alguns restaurantes tem mais de uma categoria de Cozinha, inicialmente será considerada apenas a primeira categoria da base
    data_frame['Cuisines'] = data_frame['Cuisines'].astype(str)
    #A função .apply(lambda x) realiza a operação da função lambda linha a linha do conjunto selecionado (no caso a coluna de categoria de Cuisines)
    # A função split separa o valor string por um delimitador, neste caso é a vírgula (",")
    # O colchete '[0]' indica que será considerada o primeiro elemento do que foi cortado no valor
    data_frame['Cuisines']=data_frame.loc[:,'Cuisines'].apply(lambda x: x.split(",")[0])

    data_frame = rename_columns(data_frame)

    #Trocando o nome da coluna country_code para coutry_name, já que os valores foram alterados
    data_frame.rename(columns={'country_code': 'country_name'}, inplace= True)
    
    #Removendoa  coluna switch_to_order_menu que possui valor 0 em todas as linhas
    data_frame = data_frame.drop(['switch_to_order_menu'],axis=1)

    #Removendo linhas duplicadas
    data_frame = data_frame.drop_duplicates()

    #removendo valores vazios
    data_frame = data_frame.loc[data_frame['cuisines'] != 'nan',:]

    #removendo outlaiers sem sentido
    data_frame = data_frame.loc[data_frame['average_cost_for_two']!=25000017,:]

    #Reset do index após todoso os tratamentos
    df = data_frame.reset_index(drop=True)

    #convertendoo as o custo do prato para 2 para dólar

    data = get_rates()

    #Colunas de histórico antes da conversão
    df['avg_cost_for_two_old_currency'] = df['average_cost_for_two']
    df['old_currency'] = df['currency']

    #Convertendo os valores
    df['average_cost_for_two'] = (df[['currency', 'average_cost_for_two']]
                                        .apply(lambda x: convert_currency(x['average_cost_for_two'], currency[x['currency']], data), axis=1))
    df['currency'] = 'Dolar (USD)'

    #Criando um backup da Cópia
    df_tratado = df.copy()

    return df,df_tratado


#============================================
# Importando a base
#============================================

dataFrame = pd.read_csv('data_sets/comunidade_ds/zomato.csv')


df_backup = dataFrame.copy()

df,df_tratado = clean_df(dataFrame)

#============================================
# Barra lateral
#============================================
image_path = 'target.png'
image = Image.open(image_path)
st.image(image, width=50)

st.markdown('# Fome Zero')

with st.sidebar:
    st.sidebar.markdown('# Fome Zero')
    st.sidebar.markdown('##### Os melhores restaurantes estão aqui')
    st.sidebar.markdown('### Você pode utilizar os controles abaixo para filtrar a visualização')

    st.sidebar.divider()


#============================================
# Contrução da página
#============================================

with st.container():
    # Gráfico Culinárias distintas por Países
    st.markdown('### Aqui você encontra os dados que foram utilizados na construção do dashboard')
    st.divider()
    st.dataframe(df)

