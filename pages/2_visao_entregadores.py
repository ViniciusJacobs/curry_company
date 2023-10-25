import numpy  as np
import pandas as pd
import inflection
import datetime as dt
import math
import plotly.express as px
import seaborn as sns
from matplotlib import pyplot as plt
from IPython.core.display import HTML
import folium
import streamlit as st
from PIL import Image
from streamlit_folium import st_folium
from haversine import haversine, Unit
import plotly.graph_objects as go

st.set_page_config(page_title = 'Visão Entregadores', layout = 'wide')

df_raw = pd.read_csv('data/train.csv')

df = df_raw.copy()


##===========================================================================================
## Funções
##===========================================================================================


def top_delivers_fast( df1 ):
    df_aux = ( df1.loc[:, ['Delivery_person_ID', 'City', 'Time_taken(min)' ]]
                  .groupby(['City', 'Delivery_person_ID' ])
                  .min()
                  .sort_values(['City', 'Time_taken(min)'] )
                  .reset_index() )

    df_aux1 = df_aux.loc[df_aux['City'] == 'Metropolitian',:].head(10) 
    df_aux2 = df_aux.loc[df_aux['City'] == 'Urban',:].head(10) 
    df_aux3 = df_aux.loc[df_aux['City'] == 'Semi-Urban',:].head(10) 

    df_aux4 = pd.concat([df_aux1, df_aux2, df_aux3])
    df_aux4.reset_index(drop = True )
    return df_aux4

def top_delivers_slow(df1):
    df_aux = ( df1.loc[:, ['Delivery_person_ID', 'City', 'Time_taken(min)' ]]
              .groupby(['City', 'Delivery_person_ID' ])
              .max()
              .sort_values(['City', 'Time_taken(min)'] )
              .reset_index() )

    df_aux1 = df_aux.loc[df_aux['City'] == 'Metropolitian',:].tail(10) 
    df_aux2 = df_aux.loc[df_aux['City'] == 'Urban',:].tail(10) 
    df_aux3 = df_aux.loc[df_aux['City'] == 'Semi-Urban',:].tail(10) 

    df_aux4 = pd.concat([df_aux1, df_aux2, df_aux3])
    df_aux4.reset_index(drop = True )
    return df_aux4

def clean_df(df):
    """Esta funcao tem a responsabilidade de limpar todo o dataframe"""
    # Excluir as linhas com a idade dos entregadores vazia
    linhas_vazias = df['Delivery_person_Age'] != 'NaN '
    df = df.loc[linhas_vazias, :]

    # Excluir as linhas com a idade dos entregadores vazia
    linhas_vazias = df['City'] != 'NaN '
    df = df.loc[linhas_vazias, :]

    linhas_vazias = df['Festival'] != 'NaN '
    df = df.loc[linhas_vazias, :]

    # Conversao de texto/categoria/string para numeros inteiros
    df['Delivery_person_Age'] = df['Delivery_person_Age'].astype( 'int64' )

    # Conversao de texto/categoria/strings para numeros decimais
    df['Delivery_person_Ratings'] = df['Delivery_person_Ratings'].astype( float )

    # Conversao de texto para data
    df['Order_Date'] = pd.to_datetime( df['Order_Date'], format='%d-%m-%Y' )

    # Remove as linhas da culuna multiple_deliveries que tenham o 
    # conteudo igual a 'NaN '
    linhas_vazias = (df['multiple_deliveries'] != 'NaN ') & (df['multiple_deliveries'].notna())
    df = df.loc[linhas_vazias, :]
    df['multiple_deliveries'] = df['multiple_deliveries'].astype( int )


    df.loc[:,'ID']=df.loc[:,'ID'].str.strip()
    df.loc[:,'Road_traffic_density']=df.loc[:,'Road_traffic_density'].str.strip()
    df.loc[:,'Type_of_order']=df.loc[:,'Type_of_order'].str.strip()
    df.loc[:,'Type_of_vehicle']=df.loc[:,'Type_of_vehicle'].str.strip()
    df.loc[:,'City']=df.loc[:,'City'].str.strip()
    df.loc[:,'Festival']=df.loc[:,'Festival'].str.strip()

    # Comando para remover o texto de números
    df['Time_taken(min)'] = df['Time_taken(min)'].apply( lambda x: x.split( '(min)' )[1] )
    df['Time_taken(min)'] = df['Time_taken(min)'].astype( 'int64')

    return df





##===========================================================================================
## Limpeza dos dados
##===========================================================================================

df1 = clean_df(df)



##===========================================================================================
## Barra Lateral 
##===========================================================================================

#image_path = 'C:/Users/vini_/Documents/FTC_Analisando_Dados_Py/logo.png'
image = Image.open('logo.png')
st.sidebar.image(image, width =280)

st.sidebar.markdown('# Cury Company')
st.sidebar.markdown('## Fastest Delivery in Town')
st.sidebar.markdown("""---""")

st.sidebar.markdown('## Selecione uma data limite')
data_slider = st.sidebar.slider('Até qual valor?', value = pd.datetime(2022,4,6), min_value = pd.datetime(2022, 2, 11), max_value = pd.datetime(2022, 4, 6), format = 'DD-MM-YYYY')
st.sidebar.markdown("""---""")

traffic_options = st.sidebar.multiselect('Quais as condições de Transito', ['Low','Medium', 'High', 'Jam'], default = ['Low','Medium', 'High', 'Jam'])
st.sidebar.markdown("""---""")

wheather_options = st.sidebar.multiselect('Quais as condições de Clima', ['conditions Sunny', 'conditions Stormy', 'conditions Sandstorms',
                                                                         'conditions Cloudy', 'conditions Fog', 'conditions Windy'], 
                                          default = ['conditions Sunny', 'conditions Stormy','conditions Sandstorms','conditions Cloudy', 
                                                     'conditions Fog', 'conditions Windy'])
st.sidebar.markdown("""---""")

st.sidebar.markdown('### Powered by CDS')

# filtros de data
linhas_selecionadas = df1['Order_Date'] < data_slider
df1 = df1.loc[linhas_selecionadas, :]

# filtros de transito

linhas_selecionadas = df1['Road_traffic_density'].isin(  traffic_options )
df1 = df1.loc[linhas_selecionadas,:]

# filtros de clima

linhas_selecionadas = df1['Weatherconditions'].isin(  wheather_options )
df1 = df1.loc[linhas_selecionadas,:]





##===========================================================================================
## Layout no Streamlit
##===========================================================================================


st.markdown('# Marketplace - Visão Entregadores')


tab1, tab2, tab3 = st.tabs(['Visão Gerencial', '_', '_'])


with tab1:
    with st.container():
        st.title('Overall Metrics')
        col1,col2,col3,col4 = st.columns (4, gap = 'large' )
        with col1:
            
            maior_idade = df1['Delivery_person_Age'].max()  
            col1.metric('Maior Idade', maior_idade)
            
            
        with col2:
            
            menor_idade = df1['Delivery_person_Age'].min()
            col2.metric('Menor Idade', menor_idade)
            
        with col3:
            
            melhor_condicao = df1['Vehicle_condition'].max() 
            col3.metric('Melhor Condição', melhor_condicao)

            
        with col4:
            
            pior_condicao = df1['Vehicle_condition'].min()
            col4.metric('Pior Condicao', pior_condicao)
            
    with st.container():
        st.markdown("""---""") 
        st.title('Avaliações')
        
        col1,col2 = st.columns(2)
        with col1:
            st.markdown('##### Avaliação média por Entregador')
            df_avg_rating_per_deliver = ( df1.loc[:, ['Delivery_person_ID','Delivery_person_Ratings' ]]
                                         .groupby(['Delivery_person_ID'])
                                         .mean()
                                         .reset_index() )
            st.dataframe(df_avg_rating_per_deliver)
            
            
            
    
        with col2:
            st.markdown('##### Avaliação média por Transito')
            df_avg= (df1.loc[:, ['Road_traffic_density', 'Delivery_person_Ratings' ] ]
                         .groupby( ['Road_traffic_density'] )
                         .agg( ['mean', 'std']  ) )           
            df_avg.columns = ['mean', 'std']            
            df_avg.reset_index()
            st.dataframe(df_avg)   
            
            
            st.markdown('##### Avaliação média por Clima')
            df_avg= (df1.loc[:, ['Weatherconditions', 'Delivery_person_Ratings' ] ]
                         .groupby( ['Weatherconditions'] )
                         .agg( ['mean', 'std']  ) )
            df_avg.columns = ['mean', 'std']
            df_avg.reset_index()
            st.dataframe(df_avg)


    
    with st.container():
        st.markdown("""---""") 
        st.title('Velocidade de Entrega')
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown('##### Top Entregadores mais rápidos')
            df_aux4 = top_delivers_fast( df1 )
            st.dataframe(df_aux4)             
            
        with col2:
            st.markdown('##### Top Entregadores mais lentos')
            df_aux4 = top_delivers_slow(df1)           
            st.dataframe(df_aux4)
            

















