import streamlit as st
import pandas as pd
import datetime
import requests
import matplotlib.pyplot as plt
from env import url, city, state


def get_real_time_aqi(city, state):
    # Get the real time AQI for a city
    response = requests.get(f"{url}/retrieve",
                            params={
                                'city': city,
                                'state': state
                            })

    if response.status_code == 200:
        #print(response.json())
        return response.json()
    else:
        return None


def get_predicted_aqi(city, state, period):
    # Get the predicted AQI for a city
    response = requests.get(f"{url}/predict",
                            params={
                                'city': city,
                                'state': state,
                                'days': str(period)
                            })
    print(response.status_code)
    if response.status_code == 200:
        return response.json()
    else:
        return None


def clean_real_time_aqi(aqi_data, datetime_start, datetime_end):
    if aqi_data is not None:
        aqi = []
        date_time = []
        for data in aqi_data['data']:
            aqi.append(data['aqi'])
            date_time.append(data['datetime'])

        #convert the lists to pandas dataframe
        df = pd.DataFrame(list(zip(date_time, aqi)),
                          columns=['date_time', 'aqi'])
        #convert the date_time column to datetime
        df['date_time'] = pd.to_datetime(df['date_time'],
                                         format='%d/%m/%Y %H:%M:%S')
        #select the data between the start and end date
        df = df[(df['date_time'] >= datetime_start) &
                (df['date_time'] <= datetime_end)]

        #if the dataframe is not empty
        if not df.empty:
            #find the last updated time
            last_updated = df['date_time'].max()
            current_datetime = datetime.datetime.now()
            #find how many hours ago the data was updated
            minutes_ago = (current_datetime - last_updated).seconds // 60

            df['date_time'] = df['date_time'].dt.strftime('%d-%m-%Y %H:%M')
            return df, current_datetime, last_updated, minutes_ago

        else:
            return None, None, None, None
    return None, None, None, None


def plot_single_data(df, title):
    plt.plot(df['date_time'], df['aqi'])
    plt.xlabel('Time')
    plt.ylabel('AQI')
    plt.title(title)
    #show only first, middle and last label on x axis
    plt.xticks([
        df['date_time'].iloc[0],
        df['date_time'].iloc[int(len(df['date_time']) / 2)],
        df['date_time'].iloc[-1]
    ])

    st.pyplot()


def clean_prediction_data(aqi_data):
    if aqi_data is not None:
        predicted_aqi = aqi_data['data']
        date_time = []
        aqi = []

        for data in predicted_aqi:
            #Sun, 27 Nov 2022 00:00:29 GMT
            date_time.append(
                pd.to_datetime(data['ds'], format='%a, %d %b %Y %H:%M:%S %Z'))
            aqi.append(data['yhat'])

        #convert the lists to pandas dataframe
        df = pd.DataFrame(list(zip(date_time, aqi)),
                          columns=['date_time', 'aqi'])

        #if the dataframe is not empty
        if not df.empty:
            df['date_time'] = df['date_time'].dt.strftime('%d-%m-%Y %H:%M')
            return df
        else:
            return None
    return None


def plot_multiple_data(df_combined):
    plt.plot(df_combined['date_time'],
             df_combined['aqi'],
             label='Real Time AQI')
    plt.plot(df_combined['date_time'],
             df_combined['aqi_pred'],
             label='Predicted AQI')
    plt.xticks([
        df_combined['date_time'].iloc[0],
        df_combined['date_time'].iloc[int(len(df_combined['date_time']) / 2)],
        df_combined['date_time'].iloc[-1]
    ])
    plt.legend()
    plt.xlabel('Date')
    plt.ylabel('AQI')
    plt.title('Real Time AQI vs Predicted AQI')
    st.pyplot()