import streamlit as st
from PIL import Image
from streamlit_extras.switch_page_button import switch_page

st.set_page_config(
    page_title='Home',
    page_icon='🎲',
    layout='wide',
    initial_sidebar_state='collapsed'
)
image_path = 'C:/Users/Fernando/OneDrive/TRAB/repos/target.png'
image = Image.open(image_path)
st.image(image, width=50)

st.write( '# Fome Zero Company')

st.markdown(
    '''
    ##### Este conjunto de dashboard foi construído para o acompanhamento das métricas e crescimento dos *Países, Cidades e Restaurantes cadastrados.*
    ##### :orange[Selecione o Dashboard nos botões abaixo ou na barra lateral]
    - *Obs: Utiilize os filtros da barra lateral para auxílio no estudo e visualização.*
    ---
''')

col1,col2,col3 = st.columns(3,gap='Small')

with col1:
    if st.button("Visão Geral"):
        st.switch_page("pages/1_Visao_Geral.py")

    if st.button("Visão País"):
        st.switch_page("pages/2_Visao_País.py")

with col2:
    if st.button("Visão Cidade"):
        st.switch_page("pages/3_Visao_Cidade.py")

    if st.button("Visão Restaurantes"):
        st.switch_page("pages/4_Visao_Restaurante.py")
with col3:
    if st.button("Data Base"):
        st.switch_page("pages/5_Data_Base.py")

st.markdown('''  
            ---
            #### Para mais informações:''')

if st.button('Clique'):
    st.switch_page('pages/6_Ajuda.py')

st.markdown('''
            #### Ou contate
            - Fernando Silva
                - e-mail: fernando.h.o.s@hotmail.com
                - LinekdIn: www.linkedin.com/in/fernando-h-silva-
'''
)   





with st.sidebar:
    st.image( image, width=50 )

    st.markdown( '# Fome zero ' ) #markdown altera o nível e tamanho da fonte que está no parênteses dependendo de quantos '#' existirem
    st.markdown( '## All your favorite restaurants here' )
    st.markdown('''---''')
    if st.button('Ajuda'):
        st.switch_page('pages/6_Ajuda.py')
