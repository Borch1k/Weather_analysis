
import pandas as pd
import streamlit as st
import pickle
import plotly.express as px
import temperature_analysis
import numpy as np
import datetime
import requests


def determine_season(timestamp):
  season_map = {1:'winter',2:'winter',3:'spring',4:'spring',5:'spring',6:'summer',7:'summer',8:'summer',9:'autumn',10:'autumn',11:'autumn',12:'winter'}
  return season_map[timestamp.month]

@st.cache_data
def process_data_file(data):
  pivoted_table = data.pivot_table(['temperature'], ['timestamp','season'], ['city'])
  windowed_mean = pivoted_table.rolling(window=30).mean()
  means = windowed_mean.groupby(['season']).mean()
  stds = pivoted_table.groupby(['season']).std()
  return means, stds

def show_main_page():
    with open('cities_data.pkl', 'rb') as f:
      cities_data = pickle.load(f)
    historical_data = st.file_uploader('Upload historical data')

    if not historical_data:
      st.write('#### Please provide csv file with historical temperature data')
      st.stop()

    data = pd.read_csv(historical_data)
    means, stds = process_data_file(data)
    city = st.sidebar.selectbox('City', cities_data.keys())
    api_key = st.sidebar.text_input('Api_key')
    new_table = pd.DataFrame([means['temperature'][city], stds['temperature'][city]], index=['Mean temperature','Standart deviation'])
    st.table(new_table)

    anomalies = []
    chunks = [(data[np.logical_and(data['city'] == city,data['season']==season)],means['temperature'][city][season],stds['temperature'][city][season]) for season in ['autumn', 'spring', 'summer', 'winter']]
    for chunk, season in zip(chunks, ['autumn', 'spring', 'summer', 'winter']):
      anomalies.extend(temperature_analysis.compute_anomalies_on_chunk_old(chunk))

    data.loc[:, 'anomaly'] = 'Normal'
    data.loc[anomalies, 'anomaly'] = 'Anomaly'

    fig1 = px.scatter(data[data['city']==city], x='timestamp', y='temperature', color='anomaly',
             color_discrete_sequence=px.colors.qualitative.G10)
    st.plotly_chart(fig1)

    if api_key is '':
      st.write('**For data analysis of current weather please provide api_key**')
      st.stop()

    req = requests.get(f'https://api.openweathermap.org/data/2.5/weather?lat={cities_data[city][0]}&lon={cities_data[city][1]}&appid={api_key}')

    if req.status_code == 401:
      st.write('**Your API_KEY is invalid.**')
      st.write('Possibly you need to wait for activation 2-3 hours')
      st.stop()

    season = determine_season(datetime.datetime.now())
    mean,std = new_table[season]
    temp = round(req.json()['main']['temp'] - 272.15, 1)
    icon = req.json()['weather'][0]['icon']
    description = req.json()['weather'][0]['description']

    anomalious_weather = np.abs(temp -mean) > std*2
    col1, col2 = st.columns([0.2,0.8])
    with col1:
      st.image(f'https://openweathermap.org/img/wn/{icon}@2x.png')
    with col2:
      st.write(f'**Current status is** {"Anomalious" if anomalious_weather else "Normal"}')
      st.write(f'**Current temperature:** {temp}')
      st.write(f'**Current description:** {description}')

if __name__ == "__main__":
    show_main_page()
