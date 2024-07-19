import streamlit as st
from PIL import Image
from streamlit_extras.switch_page_button import switch_page

st.set_page_config(
    page_title='Home',
    page_icon='🎲',
    layout='wide',
    initial_sidebar_state='collapsed'
)
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
    if st.button("Visão Restaurantes"):
        st.switch_page("pages/4_Visao_Restaurante.py")
with col6:
    if st.button("Data Base"):
        st.switch_page("pages/5_Data_Base.py")

st.write( '# :orange[Orientações Básicas]')

st.markdown(
        '''
    ##### Este conjunto de dashboard foi construído para o acompanhamento das métricas e crescimento dos *Países, Cidades e Restaurantes cadastrados.*
    ##### :orange[Selecione o Dashboard nos botões acima ou na barra lateral]
    - *Obs: Utiilize os filtros da barra lateral para auxílio no estudo e visualização.*
    ---
    ## :orange[O que você encontrará em cada visão?]
    - Visão Geral:
            - Métricas gerais e de comportamentos 
            - Insights de geolocalização
    - Visão País:
        - Geral: Métricas gerais e de acompanhamento dos países cadastrados
        - Estratégica: Métricas estratégicas de média de preços e avaliações de países
        - Descritiva: Uma base de dados resumida com métricas dos países
    - Visão Cidade:
        - Geral: Métricas gerais e de acompanhamento das cidades cadastradas
        - Descritiva: Uma base de dados resumida com métricas das cidades
    - Visão Restaurante:
        - Geral: Métricas gerais e de acompanhamento dos restaurantes cadastrados
        - Estratégica: Métricas estratégicas de média de preços e avaliações de restaurantes
        - Tipos de Culinária: Gráficos e métricas dos tipos únicos de culinária
        - Descritiva: Uma base de dados resumida com métricas restaurantes
    - Visão Data Base:
        - A base de dados uitlizada após a limpeza e tratamento dos dados
    ### Ask for Help
    - Fernando Silva
        - e-mail: fernando.h.o.s@hotmail.com
        - LinekdIn: www.linkedin.com/in/fernando-h-silva-
'''
)   

st.sidebar.image( image, width=50 )

st.sidebar.markdown( '# Fome zero ' ) #markdown altera o nível e tamanho da fonte que está no parênteses dependendo de quantos '#' existirem
st.sidebar.markdown( '## All your favorite restaurants here' )
st.sidebar.markdown( '''---''' )
