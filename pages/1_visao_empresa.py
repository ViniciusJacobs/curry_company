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

st.set_page_config(page_title = 'Visão Empresa', layout = 'wide')


df_raw = pd.read_csv('data/train.csv')
# Fazendo uma cópia do DataFrame Lido
df = df_raw.copy()


##===========================================================================================
## Funções
##===========================================================================================

def country_maps(df1):
    columns = ['City','Road_traffic_density','Delivery_location_latitude','Delivery_location_longitude']
    columns_grouped = ['City', 'Road_traffic_density']
    data_plot = df1.loc[:, columns].groupby( columns_grouped ).median().reset_index()
    data_plot = data_plot[data_plot['City'] != 'NaN']
    data_plot = data_plot[data_plot['Road_traffic_density'] != 'NaN']
    # Desenhar o mapa
    map_ = folium.Map( zoom_start=11 )
    for index, location_info in data_plot.iterrows():
        folium.Marker( [location_info['Delivery_location_latitude'],
        location_info['Delivery_location_longitude']],
        popup=location_info[['City', 'Road_traffic_density']] ).add_to( map_ )
    st_folium( map_, width=1024 )


def order_share_by_week(df1):
    # Quantidade de pedidos por entregador por Semana
    # Quantas entregas na semana / Quantos entregadores únicos por semana
    df_aux1 = df1.loc[:, ['ID', 'week_of_year']].groupby( 'week_of_year' ).count().reset_index()
    df_aux2 = df1.loc[:, ['Delivery_person_ID', 'week_of_year']].groupby( 'week_of_year').nunique().reset_index()
    df_aux = pd.merge( df_aux1, df_aux2, how='inner' )
    df_aux['order_by_delivery'] = df_aux['ID'] / df_aux['Delivery_person_ID']
    # gráfico
    fig = px.line( df_aux, x='week_of_year', y='order_by_delivery' )
    return fig



def order_by_week(df1):
    df1['week_of_year'] = df1['Order_Date'].dt.strftime( "%U" )
    df_aux = df1.loc[:, ['ID', 'week_of_year']].groupby( 'week_of_year' ).count().reset_index()
    # gráfico
    fig = px.bar( df_aux, x='week_of_year', y='ID' )
    return fig



def road_traffic_density(df1):
    columns = ['ID', 'City', 'Road_traffic_density']
    df_aux = df1.loc[:, columns].groupby( ['City', 'Road_traffic_density'] ).count().reset_index()
    df_aux = df_aux.loc[df_aux['Road_traffic_density'] != 'NaN', :]
    df_aux['perc_ID'] = 100 * ( df_aux['ID'] / df_aux['ID'].sum() )
    # gráfico
    fig = px.scatter( df_aux, x='City', y='Road_traffic_density', size = 'ID', color = 'City')
    return fig


def order_metric( df1 ):
    
    # Quantidade de pedidos por dia
    df_aux = df1.loc[:, ['ID', 'Order_Date']].groupby( 'Order_Date' ).count().reset_index()
    df_aux.columns = ['order_date', 'qtde_entregas']
    # gráfico
    fig = px.bar( df_aux, x='order_date', y='qtde_entregas' )
    return fig
def trafific_order_share(df1):
    columns = ['ID', 'Road_traffic_density']
    df_aux = df1.loc[:, columns].groupby( 'Road_traffic_density' ).count().reset_index()
    df_aux['perc_ID'] = 100 * ( df_aux['ID'] / df_aux['ID'].sum() )
    # gráfico
    fig = px.pie( df_aux, values='perc_ID', names='Road_traffic_density' )
    return fig

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

st.markdown('# Marketplace - Visão Cliente')
#st.header(data_slider)
#st.header(traffic_options)


tab1, tab2, tab3 = st.tabs(['Visão Gerencial', 'Visão Tática', 'Visão Geográfica'])

with tab1:
    with st.container():
        st.markdown('# Orders by Day')
        fig = order_metric(df1)
        st.plotly_chart(fig, use_container_width = True)
        
    with st.container():
        col1, col2 = st.columns(2)
        with col1:
            st.markdown('# Traffic Order Share')
            fig = trafific_order_share(df1)
            st.plotly_chart(fig, use_container_width = True)
      
        with col2:
            st.markdown('# Traffic Order City')
            fig = road_traffic_density(df1)
            st.plotly_chart(fig, use_container_width = True)

    
with tab2:
    with st.container():
        st.markdown('# Order by Week')        
        fig = order_by_week(df1)
        st.plotly_chart(fig, use_container_width = True)
        
    
    with st.container():
        st.markdown('# Order Share by Week')       
        fig = order_share_by_week(df1)
        st.plotly_chart(fig, use_container_width = True)
    
with tab3:
    st.markdown('# Country Maps ')
    country_maps(df1)
        
    


    
    