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

def group_country(df, coluna, operacao, ordenacao=False):
    df_aux = (df.loc[:,['restaurant_id','country_name',coluna]].groupby(['country_name'])
                                                .agg({'restaurant_id': 'sum', coluna:operacao})
                                                .sort_values(by=[coluna,'restaurant_id'], ascending=[ordenacao,True])                                                
                                                .reset_index())
    if df_aux[coluna].dtype == 'float64':
        df_aux[coluna] = df_aux[coluna].round(2)
    return df_aux

def group_city(df, coluna, operacao, ordenacao=False):
    df_aux = (df.loc[:,['restaurant_id','city','country_name',coluna]].groupby(['city','country_name'])
                                                .agg({'restaurant_id': 'sum', coluna:operacao})
                                                .sort_values(by=[coluna,'restaurant_id'], ascending=[ordenacao,True])
                                                .reset_index())
    if df_aux[coluna].dtype == 'float64':
        df_aux[coluna] = df_aux[coluna].round(2)
    return df_aux


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

st.write( '#### *Fome Zero Company*')

col1,col2,col3,col4,col5,col6 = st.columns(6,gap='small')

with col1:
    if st.button("Home"):
        st.switch_page("Home.py")
with col2:
    if st.button("Visão Geral"):
        st.switch_page("pages/1_Visao_Geral.py")
with col3:
    if st.button("Visão País"):
        st.switch_page("pages/2_Visao_País.py")
with col4:
    if st.button("Visão Cidade",disabled=True):
        st.switch_page("pages/3_Visao_Cidade.py")
with col5:
    if st.button("Visão Restaurantes"):
        st.switch_page("pages/4_Visao_Restaurante.py")
with col6:
    if st.button("Data Base"):
        st.switch_page("pages/5_Data_Base.py")

st.markdown('### :orange[Visão Cidades Cadastradas]')


with st.sidebar:
    st.sidebar.markdown('# Fome Zero')
    st.sidebar.markdown('##### Os melhores restaurantes estão aqui')
    st.sidebar.markdown('### Você pode utilizar os controles abaixo para filtrar a visualização')

    st.sidebar.divider()

        #Slider para filtragem por nota de avaliação
    rating_range = st.sidebar.slider(
        'Filtre a nota agregada dos restaurantes',
        value=[0.0,5.0],
        min_value=0.0,
        max_value=5.0,
        step=0.2)


    #Filtragem de países
    unique_countrys = df.country_name.unique()
    unique_countrys = unique_countrys.tolist()
    
    country_selected = st.sidebar.multiselect(
                                                'Filtre aqui os países que deseja visualizar',
                                                options= unique_countrys,
                                                default= unique_countrys
                                                )
    st.divider()
    #Filtro por tipo de culinária
    lista_culinaria = df.cuisines.unique()
    lista_culinaria = lista_culinaria.tolist()
    lista_culinaria.append('All')
    cuisines_selected = st.sidebar.multiselect(
                                            'Filtre aqui os países que deseja visualizar',
                                            options= lista_culinaria,
                                            default= lista_culinaria
                                            )
   

    linhas_selecionadas = (df['aggregate_rating'] >= float(rating_range[0])) & (df['aggregate_rating'] <= float(rating_range[1]))
    df = df.loc[linhas_selecionadas, : ]
    df = df.reset_index(drop=True)

    linhas_selecionadas = df['country_name'].isin( country_selected ) #isin = 'está em' 
    df = df.loc[linhas_selecionadas, : ]
    df = df.reset_index(drop=True)

    linhas_selecionadas = df['cuisines'].isin( cuisines_selected ) #isin = 'está em' 
    df = df.loc[linhas_selecionadas, : ]
    df = df.reset_index(drop=True)

    st.markdown('''
                ---
                # Para mais informações:
                ''')
    if st.button('Ajuda'):
        st.switch_page('pages/6_Ajuda.py')

#============================================
# Contrução da página
#============================================

tab1, tab2  = st.tabs( [ 'Visão Geral', 'Visão Descritiva'])

with tab1:
    with st.container():
        df_aux = (df.loc[:,['city','restaurant_id','country_name']].groupby(['city', 'country_name'])
                                                        .agg({'restaurant_id':'count',})
                                                        .sort_values(by='restaurant_id', ascending=False)
                                                        .round(2)
                                                        .reset_index())

        #Gráfico Cidade com mais restaurantes registrados
        fig = px.bar(df_aux.head(20),x='city', y= 'restaurant_id', color='country_name', template= 'plotly_dark', text_auto=True)
        st.markdown('#### Restaurantes cadastrados por Cidade')
        st.plotly_chart(fig, use_container_width=True)

        col1, col2 = st.columns(2,gap='small')
        with col1:
            df_aux = group_city(df,'cuisines', 'nunique')
            
            #Gráfico top cidades com tipos de culinária
            fig = px.bar(df_aux.head(7),x='cuisines', y= 'city', color='country_name', template= 'plotly_dark', text_auto=True,orientation='h')
            st.markdown('#### Top cidades com culinárias distintas')
            col1.plotly_chart(fig,use_container_width=True)
        
        with col2:
            df_aux = group_city(df,'is_delivering_now', 'sum')

            #Grafico top cidades que fazem entrega
            fig = px.pie(df_aux.head(10),names='city',values='is_delivering_now',color='is_delivering_now',hover_data='country_name', template='plotly_dark')
            
            st.markdown('#### Cidades com restaurantes que fazem entregas')
            col2.plotly_chart(fig, use_container_width=True)
        # with col3:
        #     unique_city = df['city'].nunique()
        #     col3.metric('Cidades Únicas Cadastradas',unique_city)

        # with col4:
        #     total_votes = df['votes'].sum()
        #     col4.metric('Total de avaliações feitas',total_votes)

        # with col5:
        #     type_cuisines = df['cuisines'].nunique()
        #     col5.metric('Total de tipos culinários', type_cuisines)
    with st.container():
        df_aux = group_city(df,'aggregate_rating','mean')
        fig=px.bar(df_aux.head(10),x='city', y= 'aggregate_rating', color='country_name', template= 'plotly_dark', text_auto=True)
        st.markdown('#### Top 7 cidades com maior média de avaliação')
        st.plotly_chart(fig,use_container_width=True)
with tab2:
    with st.container():
        col1, col2 = st.columns(2,gap='small')
        #card com dataframe top 3 mais bem avaliados
        with col1:
            df_aux = group_city(df,'aggregate_rating','mean')
            df_aux = df_aux.drop(columns='restaurant_id')

            #Top 7 Cidades com avaliação acima de 4
            st.markdown('##### Top 3 cidades com maior avaliação')
            col1.dataframe(data= df_aux.head(3))

        # card com data frame top 3 piores avaliados
        with col2:
            st.markdown('##### Top 3 cidades com menor avaliação')
            col2.dataframe(data= df_aux.tail(3))

    with st.container():
        st.markdown('#### Informações das cidades cadastradas')
        colunas = ['city','country_name','currency','votes','average_cost_for_two','aggregate_rating','cuisines','restaurant_name']
        df_aux = (df.loc[:,colunas].groupby(['city','country_name','currency'])
                                    .agg({'restaurant_name':'nunique',
                                          'cuisines':'nunique',
                                          'average_cost_for_two':'mean',
                                          'aggregate_rating':'mean',
                                          'votes':'sum'})
                                    .sort_values(by='aggregate_rating', ascending=False)
                                    .round(2)
                                    .reset_index())
        st.dataframe(df_aux)
