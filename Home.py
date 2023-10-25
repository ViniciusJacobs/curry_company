import streamlit as st
from PIL import Image



st.set_page_config(page_title="Home",
                  page_icon="", layout = 'wide')


#image_path = 'C:/Users/vini_/Documents/FTC_Analisando_Dados_Py/logo.png'
image = Image.open('logo.png')
st.sidebar.image(image, width =280)

st.sidebar.markdown('# Cury Company')
st.sidebar.markdown('## Fastest Delivery in Town')
st.sidebar.markdown("""---""")

st.write('# Curry Company Growth Dash ')

st.markdown(
    """
    Growth Dash foi construído para acompanhar as métricas de crescimento dos Entregadores e Restaurantes.
    ### Como utilizar o dash?
    - Visão empresa:
        - Visão Gerencial: Métricas gerais de comportamento. 
        - Visão Tática: Indicadores semanais de crescimento. 
        - Visão Geográfica: Insights de geolocalização.
    - Visão Entregador:
        - Acompanhamento dos indicadores semanais de crescimento.
    - Visão Restaurante:
        - Indicadores semanais de crescimento dos restaurantes.
    ### Ask for help:
            - suporte@growhtdsvj.com
   """    
)