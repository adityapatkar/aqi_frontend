import streamlit as st
import pandas as pd
from api_connector import get_real_time_aqi, get_predicted_aqi, clean_real_time_aqi, plot_single_data, clean_prediction_data, plot_multiple_data, calculate_time_series_error, insert_error_data, apply_class_color


def main():
    '''
        Main function to run the app
    '''

    #streamlit related configurations
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

    #create a sidebar
    st.sidebar.title("What to do")
    app_mode = st.sidebar.selectbox(
        "Choose the app mode",
        ["Show Instructions", "AQI Prediction", "About Us"])

    #show the instructions
    if app_mode == "Show Instructions":
        st.sidebar.warning('To continue,  select "AQI Prediction".')

        st.title("PollutionPulse")
        st.subheader("AQI Prediction")
        st.write(
            "This app is used to predict the AQI of a city for the next 48 hours."
        )

    #show the prediction page
    elif app_mode == "AQI Prediction":
        #set title and subtitle
        st.title("Welcome to PollutionPulse 🌎")
        st.subheader("AQI Prediction (Beta) ")
        st.write(
            "This app is used to predict the AQI of a city for the next 48 hours."
        )
        st.write(
            "Please select the city and state. Also select the date range.")

        #Get city and state from the user
        city = st.text_input("Enter your city", "Mumbai")
        state = st.text_input("Enter your state", "Maharashtra")

        #Get the start and end date for the graph
        datetime_start = st.date_input("Start Date for real time AQI",
                                       pd.to_datetime('21 Nov 2022'),
                                       min_value=pd.to_datetime('21 Nov 2022'),
                                       max_value=pd.to_datetime('today'))
        datetime_end = st.date_input("End Date for real time AQI",
                                     pd.to_datetime('today'),
                                     min_value=pd.to_datetime('22 Nov 2022'),
                                     max_value=pd.to_datetime('today'))

        #convert start and end dates to datetime object
        datetime_start = pd.to_datetime(datetime_start)
        datetime_end = pd.to_datetime(datetime_end) + pd.DateOffset(days=1)

        #Get real time AQI data
        aqi_data = get_real_time_aqi(city, state)

        #get predicted AQI data
        predicted_aqi = get_predicted_aqi(city, state)

        #Clean real time and predicted AQI data
        df_pred = clean_prediction_data(predicted_aqi)
        df, current_datetime, last_updated, minutes_ago = clean_real_time_aqi(
            aqi_data, datetime_start, datetime_end)

        #Calculate model error
        error = calculate_time_series_error(df, df_pred)

        #----FUTUTRE WORK----
        #insert_error_data(city, state, error)
        #--------------------
        st.sidebar.success(f"Current Model Error (MAPE): {error:.2f}")

        #Write the last updated time
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
        st.markdown("---")

        app_mode_page = st.selectbox("Select an operation", [
            "Show Real Time AQI Data", "Show Predicted AQI Data",
            "Compare Real Time AQI vs Predicted AQI"
        ])

        #Plot and show the real time AQI data
        if app_mode_page == "Show Real Time AQI Data" and st.button("Show"):
            st.subheader("Real Time AQI")
            st.write(
                "This is the real time AQI for your city. (Currently only available for Mumbai, Maharashtra.)"
            )
            if df is not None:
                st.markdown("---")
                st.subheader("Graph of Real Time AQI")
                plot_single_data(df, "Real Time AQI")
                st.markdown("---")
                st.subheader("Table of AQI")
                df = apply_class_color(df)

                #make datetime readable
                st.dataframe(df)
            else:
                st.error("No data found.")

        #Plot and show the predicted AQI data
        if app_mode_page == "Show Predicted AQI Data" and st.button("Show"):
            st.markdown("---")
            st.subheader("Prediction for next few days")
            st.write(
                "This is the predicted AQI for your city. (Currently only available for Mumbai, Maharashtra.)"
            )
            #if the dataframe is not empty
            if df_pred is not None:
                st.subheader("AQI Graph")
                plot_single_data(df_pred, "Predicted AQI")
                st.markdown("---")
                st.subheader("Table of AQI")
                df_pred = apply_class_color(df_pred)
                #add colour to class column
                st.dataframe(df_pred)
            else:
                st.error("No data found.")

        #Plot and show the real time and predicted AQI data
        if df is not None and df_pred is not None:
            df = apply_class_color(df)
            df_pred = df_pred.rename(columns={'aqi': 'aqi_pred'})
            df_pred = apply_class_color(df_pred, pred=True)
            df_combined = pd.merge(df, df_pred, on='date_time', how='outer')

            if app_mode_page == "Compare Real Time AQI vs Predicted AQI" and st.button(
                    "Show"):
                st.markdown("---")
                st.subheader("Real Time AQI vs Predicted AQI")
                st.write(
                    "This is the real time AQI vs predicted AQI for your city. (Currently only available for Mumbai, Maharashtra.)"
                )
                st.subheader("Graph of Combined AQI")
                plot_multiple_data(df_combined)
                st.markdown("---")
                st.subheader("Table of AQI")

                st.dataframe(df_combined)
                st.markdown("---")
                st.subheader("Table of Combined AQI (Common Dates)")
                df_combined = pd.merge(df, df_pred, on='date_time', how='inner')
                st.dataframe(df_combined)
                st.markdown("---")

    #show the about us page
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
