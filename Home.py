import streamlit as st
from PIL import Image

st.set_page_config(
    page_title='Home',
    page_icon='🎲',
    layout='centered'
)

st.write( '# Fome Zero Company')

st.markdown(
    '''
    Este Dashboard foi construído para o acompanhamento das métricas e crescimento dos Países, Cidades e Restaurantes cadastrados.
    ##### Como Utilizar este Growth Dashboard?
    - Obs: Utiilize os filtros da barra lateral para auxílio no estudo e visualização.
    ---
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


image_path = 'target.png'
image = Image.open(image_path)

st.image(image, width=120)

st.sidebar.image( image, width=50 )

st.sidebar.markdown( '# Fome zero ' ) #markdown altera o nível e tamanho da fonte que está no parênteses dependendo de quantos '#' existirem
st.sidebar.markdown( '## All your favorite restaurants here' )
st.sidebar.markdown( '''---''' )
