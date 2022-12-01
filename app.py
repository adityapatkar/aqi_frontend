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


def main():
    st.set_page_config(
        page_title="PollutionPulse",
        page_icon="./logo.png",
        layout="wide",
        initial_sidebar_state="expanded",
    )
    st.set_option('deprecation.showPyplotGlobalUse', False)
    page_bg_img = """
    <style>
    .stApp {
    background-image: url('https://unsplash.com/photos/ZiQkhI7417A');
    background-size: cover;
    }
    </style>
    """
    st.markdown(page_bg_img, unsafe_allow_html=True)
    hide_streamlit_style = """
    
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    </style>
    """
    st.markdown(hide_streamlit_style, unsafe_allow_html=True)
    # Once we have the dependencies, add a selector for the app mode on the sidebar.
    st.sidebar.title("What to do")
    app_mode = st.sidebar.selectbox(
        "Choose the app mode",
        ["Show Instructions", "AQI Prediction", "About Us"])
    if app_mode == "Show Instructions":
        st.sidebar.success('To continue,  select "AQI Prediction".')
    elif app_mode == "AQI Prediction":
        st.title("AQI Prediction (Beta)")
        st.subheader("Real Time AQI")
        st.write(
            "This is the real time AQI for your city. (Currently only available for Mumbai, Maharashtra.)"
        )
        city = st.text_input("Enter your city", "Mumbai")
        state = st.text_input("Enter your state", "Maharashtra")
        datetime_start = st.date_input("Start Date",
                                       pd.to_datetime('21 Nov 2022'),
                                       min_value=pd.to_datetime('21 Nov 2022'),
                                       max_value=pd.to_datetime('today'))
        datetime_end = st.date_input("End Date",
                                     pd.to_datetime('today'),
                                     min_value=pd.to_datetime('23 Nov 2022'),
                                     max_value=pd.to_datetime('today'))
        #convert dates to datetime
        datetime_start = pd.to_datetime(datetime_start)
        datetime_end = pd.to_datetime(datetime_end) + pd.DateOffset(days=1)
        if st.button("Get AQI"):
            aqi_data = get_real_time_aqi(city, state)
            if aqi_data is not None:
                aqi = []
                date_time = []
                for data in aqi_data['data']:
                    aqi.append(data['aqi'])
                    date_time.append(data['datetime'])

                #convert the lists to pandas dataframe
                df = pd.DataFrame(list(zip(date_time, aqi)),
                                  columns=['date_time', 'aqi'])
                st.write(df)
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
                    minutes_ago = (current_datetime -
                                   last_updated).seconds // 60
                    st.sidebar.write(
                        f"Current Date: {current_datetime.strftime('%d/%m/%Y %H:%M:%S')}"
                    )
                    st.sidebar.write(
                        f"Last Updated: {last_updated.strftime('%d/%m/%Y %H:%M:%S')} UTC"
                    )
                    if minutes_ago < 60:
                        st.sidebar.success(
                            f"Last updated {round(minutes_ago)} minutes ago.")
                    else:
                        st.sidebar.warning(
                            f"Last updated {round(minutes_ago /60)} hours ago.")
                    #st.siwrite(f"Last updated {hours_ago:.2f} hours ago")
                    st.markdown("---")
                    st.subheader("AQI Graph")

                    plt.plot(df['date_time'], df['aqi'])
                    plt.xlabel('Time')
                    plt.ylabel('AQI')
                    plt.title('Real Time AQI')
                    #show only first, middle and last label on x axis
                    plt.xticks([
                        df['date_time'].iloc[0],
                        df['date_time'].iloc[int(len(df['date_time']) / 2)],
                        df['date_time'].iloc[-1]
                    ])

                    st.pyplot()

                    st.markdown("---")
                    st.subheader("Table of AQI")

                    #make datetime readable
                    df['date_time'] = df['date_time'].dt.strftime(
                        '%d-%m-%Y %H:%M')
                    st.dataframe(df)

                else:
                    st.error(
                        "No data found for the selected dates. Please select different dates."
                    )

            else:
                st.error("No data found")

        st.markdown("---")
        st.subheader("Prediction for next few dats")
        if st.button("Get Prediction"):
            #days is number of days between today and 27 Nov 2022
            days = (pd.to_datetime('27 Nov 2022') -
                    pd.to_datetime('today')).days
            days = abs(days)

            predicted_aqi = get_predicted_aqi(city, state, days)
            if predicted_aqi is not None:
                predicted_aqi = predicted_aqi['data']
                date_time = []
                aqi = []

                for data in predicted_aqi:
                    date_time.append(pd.to_datetime(data['ds']))
                    aqi.append(data['yhat'])

                #convert the lists to pandas dataframe
                df = pd.DataFrame(list(zip(date_time, aqi)),
                                  columns=['date_time', 'aqi'])

                #if the dataframe is not empty
                if not df.empty:
                    st.markdown("---")
                    st.subheader("AQI Graph")

                    plt.plot(df['date_time'], df['aqi'])
                    plt.xlabel('Time')
                    plt.ylabel('AQI')
                    plt.title('Predicted AQI')
                    #show only first, middle and last label on x axis
                    plt.xticks([
                        df['date_time'].iloc[0],
                        df['date_time'].iloc[int(len(df['date_time']) / 2)],
                        df['date_time'].iloc[-1]
                    ])

                    st.pyplot()

                    st.markdown("---")
                    st.subheader("Table of AQI")

                    #make datetime readable
                    df['date_time'] = df['date_time'].dt.strftime(
                        '%d-%m-%Y %H:%M')
                    st.dataframe(df)
                else:
                    st.error("No data found.")
            else:
                st.error("Something went wrong. Please try again.")
        st.markdown("---")

    elif app_mode == "About Us":
        st.title("About Us")
        st.subheader("This is a project by:")
        #create a list of team members
        team_members = ["1.     Aditya", "2.     Sameer"]
        #iterate over the list and display the names
        for member in team_members:
            st.markdown(member)


if __name__ == "__main__":
    main()
