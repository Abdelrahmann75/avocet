
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
    #Choose wide mode as the default setting
    
    
    st.set_page_config(layout="wide")

    menu = ["Home","Prod_pressure"]

    st.sidebar.markdown('<span style="font-size:20px; font-weight:bold;">Avocet-DashBoard</span>', unsafe_allow_html=True)
    choice = st.sidebar.radio("", menu)
    if choice == "Home":
        my_home()
    else:
        test()
    
    

   
    
     
         
     
        
if __name__ == "__main__":
    main()       