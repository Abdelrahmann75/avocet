
import streamlit as st
import pandas as pd 
import numpy as np
from p_p import test
import sqlite3
import matplotlib.pyplot as plt
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from main_home import my_home

# Create a title for your form


def main():
    # Choose wide mode as the default setting
    st.set_page_config(layout="wide")

    # Initialize session state
    if 'login_successful' not in st.session_state:
        st.session_state.login_successful = False

    # If login is not successful
    if not st.session_state.login_successful:
        # Display the login form
        username = st.text_input("Username:")
        password = st.text_input("Password:", type="password")
        login_button = st.button("Login")

        # Check if the login button is pressed
        if login_button:
            # Authenticate the user
            if authenticate(username, password):
                st.session_state.login_successful = True
                st.success("Login successful!")
                # Trigger a rerun to update the UI
                st.experimental_rerun()
            else:
                st.write("invalid username or password")

    # If login is successful, display the app content
    if st.session_state.login_successful:
        # Display the app content
        st.sidebar.markdown('<span style="font-size:20px; font-weight:bold;">Avocet-DashBoard</span>', unsafe_allow_html=True)
        # Set the default selection to "Prod_pressure"
        choice = st.sidebar.radio("", ["Home", "Prod_pressure"])

        if choice == "Home":
            my_home()
        else:
            test()
            
    else:
        st.session_state.login_error_message = "Invalid username or password."              
            
    

# Function to check the entered username and password
def authenticate(username, password):
    # Define user credentials
    user_credentials = {
        "user123": "pass123",
        "admin": "adminpass"
    }
    return user_credentials.get(username) == password

# Function to display the home page content


if __name__ == "__main__":
    main()






