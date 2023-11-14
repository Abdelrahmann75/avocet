# -*- coding: utf-8 -*-
"""
Created on Sun Nov 12 12:53:49 2023

@author: Tan7080
"""

import streamlit as st
import pandas as pd 
import numpy as np

import sqlite3
import matplotlib.pyplot as plt
import plotly.graph_objects as go
from plotly.subplots import make_subplots







def my_home():
    
    def plot_well_locations(df):
    

        fig, ax = plt.subplots(figsize=(16, 13))

    # Create a scatter plot for the bubble map with colors
        colors = plt.cm.get_cmap('tab20', len(df['Field'].unique()))
        sc = ax.scatter(df['x'], df['y'], s=550, c=colors(df['Field'].factorize()[0]), alpha=0.8, label=df['Field'])
    
        # Add data labels for well names with background color
        for i, well_name in enumerate(df['allias']):
            ax.annotate(well_name, (df['x'][i], df['y'][i]), fontsize=11, ha='center', va='center', weight='bold', bbox=dict(facecolor='white', alpha=0.4))
    
        # Set axis labels and a title
        ax.set_xlabel('X Coordinate')
        ax.set_ylabel('Y Coordinate')
        ax.set_title('Well Locations')
    
        # Set x and y axis limits
    
        # Add a legend
        legend = ax.legend(*sc.legend_elements(), title='Fields', loc="best")
        ax.add_artist(legend)
    
        # Show the plot
        plt.grid(True) # Add grid lines if needed
        plt.axis('equal') # Set equal aspect ratio
        st.pyplot(plt)



    def create_line_chart(df):
    # Convert 'Datee' column to datetime if it's not already
        df['Datee'] = pd.to_datetime(df['Datee'], errors='coerce')

        # Create subplots with secondary y-axes
        fig = make_subplots(rows=1, cols=1, specs=[[{'secondary_y': True}]])

        # Add Gross on the primary y-axis
        fig.add_trace(go.Scatter(x=df['Datee'], y=df['Gross'], mode='lines', name='GrossTest', line=dict(color='black')))

        # Add NetOil on the secondary y-axis
        fig.add_trace(go.Scatter(x=df['Datee'], y=df['NetOil'], mode='lines', name='net_oil', line=dict(color='green')), secondary_y=False)

        # Add WaterProduced on the secondary y-axis
        fig.add_trace(go.Scatter(x=df['Datee'], y=df['WaterProduced'], mode='lines', name='WaterProduced', line=dict(color='blue')), secondary_y=False)

        # Add Cumulative on the third y-axis
        fig.add_trace(go.Scatter(x=df['Datee'], y=df['cumm'], mode='lines', name='Cumm', line=dict(color='brown')), secondary_y=True)

        # Update layout
        fig.update_layout(
            
            xaxis_title='Datee',
            yaxis_title='GrossTest',
            legend=dict(x=1, y=1, traceorder='normal', orientation='v'),
            showlegend=True,
            width=600,
            height=600,
            xaxis=dict(showgrid=True, gridwidth=1, gridcolor='lightgray'),
            yaxis=dict(showgrid=True, gridwidth=1, gridcolor='lightgray'),
            yaxis2=dict(title='Cumm', overlaying='y', side='right', showgrid=True, gridwidth=1, gridcolor='lightgray')
        )

        # Show the chart using Streamlit
        st.plotly_chart(fig)






   
            
        
    conn = sqlite3.connect('MyData.db')
   


    sql_query1= '''SELECT Well_name,x,y,allias,Field FROM well_items
    LEFT JOIN Fields on Fields.WellName = well_items.well_name
    '''
    df=pd.read_sql_query(sql_query1,conn)
    df['x']=df['x'].astype(float)
    df['y']=df['y'].astype(float)
        

    sql_query2= '''SELECT Datee, Fields.Field, SUM(Gross) AS Gross, SUM(NetOil) AS NetOil, SUM(WaterProduced) AS WaterProduced
FROM DailyProduction
LEFT JOIN Fields ON DailyProduction.WellName = Fields.WellName
GROUP BY Datee, Fields.Field
ORDER BY Datee'''
    prod = pd.read_sql_query(sql_query2,conn)
    prod['NetOil'] = pd.to_numeric(prod['NetOil'], errors='coerce')
    prod['Gross'] = pd.to_numeric(prod['Gross'], errors='coerce')
    prod['WaterProduced'] = pd.to_numeric(prod['WaterProduced'], errors='coerce')
    prod['NetOil'] = prod['NetOil'].astype(float)
    prod['Gross'] = prod['Gross'].astype(float)
    prod['cumm'] = prod.groupby('Field')['NetOil'].cumsum()
    prod['WaterProduced'] = prod['WaterProduced'].astype(float)
    prod.dropna(subset=['Datee'], inplace=True)
   

# Create the radio button with the rest of the menu
  
    
    
   # Row A
    st.markdown('### Metrics')
    col1, col2, col3 = st.columns(3)
   
    
    # Row B
        
    c1, c2 = st.columns((2,1))
    
    with c1:
        st.markdown('### Co-ordinates map')    
        
        well_name = st.multiselect(
            'Select well name',options=df['Field'].unique(),
            default=df['Field'].unique())
        df_selection = df[df['Field'].isin(well_name)].reset_index()
        if not df_selection.empty:
           chart = plot_well_locations(df_selection)
        else:
            st.write('no data to show')
        
        
        
    with c2:
        prod= prod[prod['Field'].isin(well_name)].reset_index()
        prod = prod.groupby('Datee').agg({
    'NetOil': 'sum',
    'Gross': 'sum',
    'WaterProduced': 'sum',
    'cumm': 'sum'  # Assuming 'cumm' is the cumulative sum of 'NetOil' within each group
}).reset_index()

        
        

        
        if not prod.empty:
           
           chart2 = create_line_chart(prod)
           d = round(prod['NetOil'].iloc[-1],2)
           a = round(prod['NetOil'].tail(30).mean(),2) 
           c= round(prod['NetOil'].sum(),2)/1000000
           d = "{:.0f}".format(d)
           a = "{:.0f}".format(a)
           c = "{:.1f}".format(c)
           # Get the sum 
           col1.metric("production", d,"bbls/day")
           col2.metric("cummulative", c,"million bbls")
           col3.metric("average prod", a, "bbls/day")  
        else:
            st.write('no data to show')