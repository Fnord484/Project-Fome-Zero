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

def group_restaurants(df, coluna, operacao, ordenacao=False):
    df_aux = (df.loc[:,['restaurant_id','restaurant_name',coluna]].groupby(['restaurant_name'])
                                                .agg({'restaurant_id': 'sum', coluna:operacao})
                                                .sort_values(by=[coluna,'restaurant_id'], ascending=[ordenacao,True])
                                                .reset_index())
    if df_aux[coluna].dtype == 'float64':
        df_aux[coluna] = df_aux[coluna].round(2)
    return df_aux

def group_restaurant_culinaria(df, coluna, culinaria, operacao, ordenacao=False):
    linhas_selecionadas = df['cuisines'] == culinaria
    df_aux = (df.loc[linhas_selecionadas,['restaurant_id','restaurant_name',coluna]].groupby(['restaurant_name'])
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
    if st.button("Visão Cidade"):
        st.switch_page("pages/3_Visao_Cidade.py")
with col5:
    if st.button("Visão Restaurantes",disabled=True):
        st.switch_page("pages/4_Visao_Restaurante.py")
with col6:
    if st.button("Data Base"):
        st.switch_page("pages/5_Visao_Data_Base.py")

st.markdown('### :orange[Visão Cidades Cadastradas]')

st.markdown('### :orange[Visão Restaurantes Cadastrados]')

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

tab1, tab2,tab3,tab4  = st.tabs( [ 'Visão Geral', 'Visão Estratégica','Visão Tipos de culinária' , 'Visão Descritiva'])

with tab1:
    with st.container():

        col1, col2,col3 = st.columns(3,gap='large')

        with col1: #Total de restaurantes cadastrados
            total_restaurants = df['restaurant_id'].nunique()
            col1.metric('Total de restaurantes cadastrados', total_restaurants)
        
        with col2:#Total de restaurantes que fazem reserva de mesa
            df_aux = df.loc[df['has_table_booking'] == 1, 'restaurant_id']
            booking = df_aux.nunique()
            col2.metric('Restaurantes que fazem reserva',booking)
        
        with col3:#Total de restaurantes que fazem entrega
            df_aux = df.loc[df['is_delivering_now'] == 1, 'restaurant_id']
            delivering = df_aux.nunique()
            col3.metric('Restaurantes que fazem entrega',delivering)

    with st.container():
        # Gráfico Culinárias distintas por Países
        df_aux = (df.loc[:,['cuisines', 'country_name']].groupby(['country_name'])
                                            .nunique()
                                            .sort_values(by='cuisines', ascending=False)
                                            .reset_index())

        fig=px.bar(df_aux.head(15),x='country_name', y= 'cuisines', template= 'plotly_dark', text_auto=True)
        st.markdown('#### Culinárias distintas por Países')
        st.plotly_chart(fig,use_container_width=True)

with tab2: #Visão Estratégica
    with st.container():
        col1, col2 = st.columns(2,gap='small')
        #card com dataframe top 3 mais bem avaliados
        with col1:
            df_aux = (df.loc[:,['restaurant_name','city','country_name','aggregate_rating']].groupby(['restaurant_name','city', 'country_name'])
                                                                   .mean()
                                                                   .sort_values(by='aggregate_rating', ascending=False)
                                                                   .round(2)
                                                                   .reset_index())

            #Top  com avaliação acima de 4
            st.markdown('##### Top 3 restaurantes com maior avaliação média')
            col1.dataframe(data= df_aux.head(3))

        # card com data frame top 3 piores avaliados
        with col2:
            st.markdown('##### Top 3 com menor avaliação média')
            col2.dataframe(data= df_aux.tail(3))

    with st.container():
        #Gráfico de resturantes por quantidade média de avaliações
        df_aux = (df.loc[:,['restaurant_id','restaurant_name','votes','aggregate_rating']].groupby(['restaurant_name'])
                                                    .agg({'restaurant_id': 'sum', 'votes':'mean', 'aggregate_rating': 'mean'})
                                                    .sort_values(by=['votes','restaurant_id'], ascending=[False,True])
                                                    .round(2)
                                                    .reset_index())

        df_aux = df_aux.head(10)

        fig = go.Figure(
            data=go.Bar(
                x=df_aux['restaurant_name'],
                y=df_aux['votes'],
                name="Mean Votes",
                marker=dict(color="#9467bd"),
                texttemplate='plotly_dark'
            )
        )

        fig.add_trace(
            go.Scatter(
                x=df_aux['restaurant_name'],
                y=df_aux['aggregate_rating'],
                yaxis="y2",
                name="Rating of restaurant",
                marker=dict(color="darkorange"),
            )
        )

        fig.update_layout(
                legend=dict(
                    orientation="h",
                    yanchor="bottom",
                    y=1.02,
                    xanchor="right",
                    x=0.65
                ),
            yaxis=dict(
                title=dict(text="Mean Votes"),
                side="left",
                range=[0, 250],
            ),
            yaxis2=dict(
                title=dict(text="Rating of restaurant"),
                side="right",
                range=[0, 5],
                overlaying="y",
                tickmode="sync",
            ),
        )

        st.markdown('#### Restaurantes cadastrados por Cidade')
        st.plotly_chart(fig, use_container_width=True)
    
    with st.container():
        df_aux = (df.loc[:,['restaurant_id','restaurant_name','country_name','city','average_cost_for_two']].groupby(['restaurant_name','country_name','city'])
                        .agg({'restaurant_id': 'sum', 'average_cost_for_two':'mean'})
                        .sort_values(by=['average_cost_for_two','restaurant_id'], ascending=[False,True])
                        .round(2)
                        .reset_index())
        st.markdown('#### Custo Prato para duas pessos por Restaurante')
        fig = px.bar(
                df_aux.head(12).sort_values(by='average_cost_for_two',ascending=True),
                x='average_cost_for_two',
                y='restaurant_name', 
                color='average_cost_for_two' ,
                template='plotly_dark',
                text_auto=True,
                hover_data=['country_name','city'],
                orientation='h'
                )

        st.plotly_chart(fig,use_container_width=True)

with tab3:
    with st.container():
        unique_cuisines = df['cuisines'].nunique()
        st.metric('Total tipos de culinária',unique_cuisines)

    col1,col2 = st.columns(2,gap='medium')
    with col1: #Total tipos de culinária 

        df_aux = (df.loc[:,['restaurant_id','cuisines','aggregate_rating']].groupby(['cuisines'])
                        .agg({'restaurant_id': 'count', 'aggregate_rating':'mean'})
                        .sort_values(by=['aggregate_rating','restaurant_id'], ascending=[True,False])
                        .round(2)
                        .reset_index())

        fig=px.bar(
            df_aux.tail(15),
            x='aggregate_rating',
            y='cuisines',
            color='restaurant_id',
            text_auto=True,
            template='plotly_dark',
            orientation='h'
                    )
        st.markdown('#### Avaliação média por tipos de culinária')
        st.plotly_chart(fig,use_container_width=True)
    with col2:
        df_aux = (df.loc[:, ['cuisines', 'aggregate_rating', 'restaurant_id','country_name']].groupby('cuisines')
                                            .agg({'aggregate_rating':'mean','restaurant_id': 'nunique', 'country_name':'nunique' })
                                            .sort_values(by=['aggregate_rating','restaurant_id'], ascending=[False,True])
                                            .round(2)
                                            .reset_index())
        st.markdown('#### Detalhes dos tipos de culinária')
        col2.dataframe(df_aux)





with tab4:
    with st.container():
        st.header('Teste')
        st.markdown('#### Informações das cidades cadastradas')
        colunas = ['restaurant_name','city','country_name','currency','votes','average_cost_for_two','aggregate_rating','cuisines']
        df_aux = (df.loc[:,colunas].groupby(['restaurant_name','country_name','currency'])
                                    .agg({  'cuisines':'nunique',
                                            'city':'nunique',
                                            'average_cost_for_two':'mean',
                                            'aggregate_rating':'mean',
                                            'votes':'sum'})
                                    .sort_values(by='aggregate_rating', ascending=False)
                                    .round(2)
                                    .reset_index())
        st.dataframe(df_aux)
