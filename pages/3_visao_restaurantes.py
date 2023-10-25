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

st.set_page_config(page_title = 'Visão Restaurantes', layout = 'wide')


df_raw = pd.read_csv('data/train.csv')

df = df_raw.copy()


##===========================================================================================
## Funções
##===========================================================================================


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


st.markdown('# Marketplace - Visão Restaurantes')

tab1, tab2, tab3 = st.tabs(['Visão Gerencial', '_', '_'])


with tab1:
    with st.container():
        st.markdown('##### Overal Metrics') 
        
        
        col1, col2,col3,col4,col5,col6 = st.columns(6)
        with col1:
            delivery_unique = len( df1.loc[:, 'Delivery_person_ID'].unique() ) 
            col1.metric('Entregadores únicos:', delivery_unique)
            
                        
        with col2:
            cols = ['Delivery_location_latitude', 'Delivery_location_longitude', 'Restaurant_latitude', 'Restaurant_longitude' ]

            df1['distance']= ( df1.loc[:, cols]
                                  .apply( lambda x: haversine( (x['Restaurant_latitude'],x['Restaurant_longitude']), (x['Delivery_location_latitude'], x['Delivery_location_longitude'])), axis =1) )

            avg_distance = np.round( df1['distance'].mean(), 2 )
            col2.metric('Distância média das entregas:', avg_distance)

            
            
            
        with col3:
            cols = [ 'Time_taken(min)', 'Festival']

            df1_aux = ( df1.loc[:,cols]
                       .groupby(['Festival'])
                       .agg({'Time_taken(min)': ['mean', 'std']}) )

            df1_aux.columns = ['avg_time', 'std_time']
            df1_aux = df1_aux.reset_index()
            df1_aux = np.round( df1_aux.loc[df1_aux['Festival'] == 'Yes','avg_time'], 2)
            col3.metric('Tempo médio de entrega c/ festival:', df1_aux)
            
            
            
        with col4:
            cols = [ 'Time_taken(min)', 'Festival']

            df1_aux = ( df1.loc[:,cols]
                       .groupby(['Festival'])
                       .agg({'Time_taken(min)': ['mean', 'std']}) )

            df1_aux.columns = ['avg_time', 'std_time']
            df1_aux = df1_aux.reset_index()
            df1_aux = np.round( df1_aux.loc[df1_aux['Festival'] == 'Yes','std_time'], 2)
            col4.metric('Desvio padrão de entrega c/ festival:', df1_aux)
            
            
            
            
        with col5:
            cols = [ 'Time_taken(min)', 'Festival']

            df1_aux = ( df1.loc[:,cols]
                       .groupby(['Festival'])
                       .agg({'Time_taken(min)': ['mean', 'std']}) )

            df1_aux.columns = ['avg_time', 'std_time']
            df1_aux = df1_aux.reset_index()
            df1_aux = np.round( df1_aux.loc[df1_aux['Festival'] == 'No','avg_time'], 2)
            col5.metric('Tempo médio de entrega s/ festival:', df1_aux)
       
    
    
        with col6:
            cols = [ 'Time_taken(min)', 'Festival']

            df1_aux = ( df1.loc[:,cols]
                       .groupby(['Festival'])
                       .agg({'Time_taken(min)': ['mean', 'std']}) )

            df1_aux.columns = ['avg_time', 'std_time']
            df1_aux = df1_aux.reset_index()
            df1_aux = np.round( df1_aux.loc[df1_aux['Festival'] == 'No','std_time'], 2)
            col6.metric('Desvio padrão de entrega c/ festival:', df1_aux)
    
        
    with st.container():
        st.markdown("""---""")
        st.markdown('##### Tempo medio entrega por cidade')
        
        col1, col2 = st.columns(2)
        with col1:
            df1_aux = df1.loc[:,['City', 'Time_taken(min)']].groupby('City').agg({'Time_taken(min)': ['mean', 'std']})
            df1_aux.columns = ['avg_time', 'std_time']
            df1_aux = df1_aux.reset_index()
            fig = go.Figure()
            fig.add_trace(go.Bar(name='Control',x=df1_aux['City'],y=df1_aux['avg_time'], error_y=dict(type='data',array=df1_aux['std_time'])))
            fig.update_layout(barmode='group')
            st.plotly_chart(fig, theme="streamlit", use_container_width=True)
        
        with col2:
            cols = ['City', 'Time_taken(min)']

            df1_aux = df1.loc[:,cols].groupby('City').agg({'Time_taken(min)': ['mean', 'std']})

            df1_aux.columns = ['avg_time', 'std_time']

            df1_aux = df1_aux.reset_index()
            st.dataframe(df1_aux)
            
            
        
        
    with st.container():
        st.markdown("""---""")
        st.markdown('##### Distribuição do Tempo') 
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown('##### Distância media dos restaurantes e dos locais de entrega')
           
            cols = ['Delivery_location_latitude', 'Delivery_location_longitude', 'Restaurant_latitude', 'Restaurant_longitude' ]
            df1['distance']= df1.loc[:, cols].apply( lambda x: haversine( (x['Restaurant_latitude'],x['Restaurant_longitude']), (x['Delivery_location_latitude'], x['Delivery_location_longitude'])), axis =1)

            avg_distance = df1.loc[:,['City','distance']].groupby('City').mean().reset_index()
            fig = go.Figure( data = [go.Pie( labels = avg_distance['City'], values = avg_distance['distance'], pull = [0,0.1,0] ) ]  )
            st.plotly_chart(fig, theme="streamlit", use_container_width=True)
            
        with col2:
            st.markdown('##### Tempo medio e desvio padrao por cidade')
            df1_aux = ( df1.loc[:,['City', 'Time_taken(min)', 'Road_traffic_density']]
                        .groupby(['City','Road_traffic_density'])
                        .agg({'Time_taken(min)': ['mean', 'std']}) )
            df1_aux.columns = ['avg_time', 'std_time']
            df1_aux = df1_aux.reset_index()

            fig = px.sunburst( df1_aux, path=['City', 'Road_traffic_density'], values='avg_time', color='std_time', color_continuous_scale='RdBu', color_continuous_midpoint=np.average(df1_aux['std_time'] )  )

            st.plotly_chart(fig, theme="streamlit", use_container_width=True)











