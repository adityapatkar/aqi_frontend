import streamlit as st
import pandas as pd
import datetime
import requests
import matplotlib.pyplot as plt
from env import url, city, state
from api_connector import get_real_time_aqi, get_predicted_aqi, clean_real_time_aqi, plot_single_data, clean_prediction_data, plot_multiple_data


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
                                     min_value=pd.to_datetime('22 Nov 2022'),
                                     max_value=pd.to_datetime('today'))
        #convert dates to datetime
        days = (pd.to_datetime('27 Nov 2022') - pd.to_datetime('today')).days
        days = abs(days)
        datetime_start = pd.to_datetime(datetime_start)
        datetime_end = pd.to_datetime(datetime_end) + pd.DateOffset(days=1)
        aqi_data = get_real_time_aqi(city, state)
        predicted_aqi = get_predicted_aqi(city, state, days)
        df_pred = clean_prediction_data(predicted_aqi)
        df, current_datetime, last_updated, minutes_ago = clean_real_time_aqi(
            aqi_data, datetime_start, datetime_end)
        if df is not None:
            st.sidebar.write(
                f"Current Date: {current_datetime.strftime('%d/%m/%Y %H:%M:%S')} UTC"
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
        if st.button("Get Real Time AQI"):
            if df is not None:
                st.markdown("---")
                st.subheader("Graph of Real Time AQI")
                plot_single_data(df, "Real Time AQI")
                st.markdown("---")
                st.subheader("Table of AQI")
                #make datetime readable
                st.dataframe(df)
            else:
                st.error("No data found.")
        if st.button("Get Prediction"):
            st.markdown("---")
            st.subheader("Prediction for next few days")

            #if the dataframe is not empty
            if df_pred is not None:
                st.subheader("AQI Graph")
                plot_single_data(df_pred, "Predicted AQI")
                st.markdown("---")
                st.subheader("Table of AQI")

                st.dataframe(df_pred)
            else:
                st.error("No data found.")
        if df is not None and df_pred is not None:

            df_pred = df_pred.rename(columns={'aqi': 'aqi_pred'})

            df_combined = pd.merge(df, df_pred, on='date_time', how='outer')
            #df_combined = df_combined.dropna(subset=['aqi', 'aqi_pred'])
            #plot combined data
            if st.button("Get Combined AQI"):
                st.subheader("Graph of Combined AQI")
                plot_multiple_data(df_combined)
                st.markdown("---")
                st.subheader("Table of AQI")
                st.dataframe(df_combined)
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
