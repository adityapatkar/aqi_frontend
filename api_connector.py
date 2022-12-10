import streamlit as st
import pandas as pd
import datetime
import requests
import matplotlib.pyplot as plt
from env import url


#helper function to get real time aqi from backend
def get_real_time_aqi(city, state):
    '''
        Get the real time AQI for a city
    '''

    response = requests.get(f"{url}/retrieve",
                            params={
                                'city': city,
                                'state': state
                            })

    if response.status_code == 200:

        return response.json()
    else:
        return None


def get_predicted_aqi(city, state):
    '''
        Get the predicted AQI for a city
    '''
    response = requests.get(f"{url}/retrieve_all",
                            params={
                                'city': city.lower(),
                                'state': state.lower(),
                            })
    if response.status_code == 200:
        return response.json()
    else:
        return None


def clean_real_time_aqi(aqi_data, datetime_start, datetime_end):

    #check if valid data is returned
    if aqi_data is not None:
        aqi = []
        date_time = []

        #iterate through the data and append to the lists
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

        if not df.empty:

            #find the last updated time
            last_updated = df['date_time'].max()
            current_datetime = datetime.datetime.now()

            #find how many hours ago the data was updated
            minutes_ago = (current_datetime - last_updated).seconds // 60

            df['date_time'] = df['date_time'].dt.strftime('%d-%m-%Y %H:%M')

            #convert minutes to 0 for consistency
            df['date_time'] = df['date_time'].apply(lambda x: x[:-2] + '00')

            #drop the duplicate rows
            df = df.drop_duplicates(subset=['date_time'], keep='last')
            return df, current_datetime, last_updated, minutes_ago

        return None, None, None, None
    return None, None, None, None


def plot_single_data(df, title):
    '''
        Plot the data for a single dataframe
    '''

    #plot the data
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

    #show the plot
    st.pyplot()


def clean_prediction_data(aqi_data):
    '''
        Clean the prediction data
    '''

    #check if valid data is returned
    if aqi_data is not None:
        predicted_aqi = aqi_data['data']
        date_time = []
        aqi = []

        #iterate through the data and append to the lists
        for data in predicted_aqi:
            date_time.append(
                pd.to_datetime(data['datetime'], format='%d/%m/%Y %H:%M:%S'))
            aqi.append(data['yhat'])

        #convert the lists to pandas dataframe
        df = pd.DataFrame(list(zip(date_time, aqi)),
                          columns=['date_time', 'aqi'])

        if not df.empty:

            df['date_time'] = df['date_time'].dt.strftime('%d-%m-%Y %H:%M')
            #whereever date is greater than 9th december 2022, only select the data where seconds are 00
            df_greater_9_dec_2022 = df[df['date_time'] >= '09-12-2022 00:00']
            #select the data where seconds are 00
            df_greater_9_dec_2022 = df_greater_9_dec_2022[
                df_greater_9_dec_2022['date_time'].apply(
                    lambda x: x[-2:]) == '00']
            #merge this data with the data where date is less than 9th december 2022
            df = pd.concat([
                df[df['date_time'] < '09-12-2022 00:00'], df_greater_9_dec_2022
            ])

            #convert minutes to 0 for consistency
            df['date_time'] = df['date_time'].apply(lambda x: x[:-2] + '00')

            #drop the duplicate rows
            df = df.drop_duplicates(subset=['date_time'],
                                    keep='last').reset_index(drop=True)
            return df
        else:
            return None
    return None


def plot_multiple_data(df_combined):
    '''
        Plot the data for multiple dataframes
    '''

    #plot the data for real time aqi
    plt.plot(df_combined['date_time'],
             df_combined['aqi'],
             label='Real Time AQI')

    #plot the data for predicted aqi
    plt.plot(df_combined['date_time'],
             df_combined['aqi_pred'],
             label='Predicted AQI')

    #set the labels and other properties
    plt.xticks([
        df_combined['date_time'].iloc[0],
        df_combined['date_time'].iloc[int(len(df_combined['date_time']) / 2)],
        df_combined['date_time'].iloc[-1]
    ])
    plt.legend()
    plt.xlabel('Date')
    plt.ylabel('AQI')
    plt.title('Real Time AQI vs Predicted AQI')

    #show the plot
    st.pyplot()


def calculate_time_series_error(df_real, df_pred):
    '''
        Calculate the error (MAPE) between the real time aqi and predicted aqi
    '''

    #merge the dataframes
    df_pred = df_pred.rename(columns={'aqi': 'aqi_pred'})
    df_combined = pd.merge(df_real, df_pred, on='date_time', how='inner')

    #calculate the error
    df_combined['error'] = abs(df_combined['aqi'] - df_combined['aqi_pred'])
    df_combined['error'] = df_combined['error'] / df_combined['aqi']
    df_combined['error'] = df_combined['error'] * 100

    #calculate the mean error
    mape = df_combined['error'].mean()

    #error for the last 24 hours
    df_combined_last_24_hours = df_combined[df_combined['date_time'] >= (
        datetime.datetime.now() -
        datetime.timedelta(hours=24)).strftime('%d-%m-%Y %H:%M')]
    mape_last_24_hours = df_combined_last_24_hours['error'].mean()

    return mape, mape_last_24_hours


def insert_error_data(city, state, mape):
    '''
        insert the error data into the database
    '''
    #---FUTURE WORK---
    response = requests.post(
        f"{url}/insert_error",
        params={
            'city': city.lower(),
            'state': state.lower(),
            'mape': mape,
            'datetime': datetime.datetime.now().strftime('%d/%m/%Y %H:%M:%S')
        })
    if response.status_code == 200:
        return response.json()
    else:
        return None
    #---FUTURE WORK---


def get_aqi_class(aqi):
    '''
        Get the aqi class based on the aqi value
    '''

    #self explanatory
    if aqi <= 50:
        return 'Good'
    elif aqi > 50 and aqi <= 100:
        return 'Satisfactory'
    elif aqi > 100 and aqi <= 200:
        return 'Moderate'
    elif aqi > 200 and aqi <= 300:
        return 'Poor'
    elif aqi > 300 and aqi <= 400:
        return 'Very Poor'
    else:
        return 'Severe'


#---NOT USED---
def get_aqi_color(aqi):
    if aqi <= 50:
        return '#00E400'
    elif aqi > 50 and aqi <= 100:
        return '#FFFF00'
    elif aqi > 100 and aqi <= 200:
        return '#FF7E00'
    elif aqi > 200 and aqi <= 300:
        return '#FF0000'
    elif aqi > 300 and aqi <= 400:
        return '#99004C'
    else:
        return '#7E0023'


#---NOT USED---


def apply_class_color(df, pred=False):
    '''
        Find the class based on the aqi value
    '''

    #check if predicted data is passed
    if pred is False:

        #apply the function to get the aqi class
        df['aqi_class'] = df['aqi'].apply(get_aqi_class)
        #df['aqi_color'] = df['aqi'].apply(get_aqi_color)
    else:
        #apply the function to get the aqi class
        df['aqi_class_pred'] = df['aqi_pred'].apply(get_aqi_class)
        #df['aqi_color_pred'] = df['aqi_pred'].apply(get_aqi_color)
    return df
