import sqlite3
import pandas as pd
import numpy as np
import streamlit as st
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import seaborn as sns




def test():


    conn2 = sqlite3.connect('MyData.db')

    sql_query1 = '''SELECT 
    DailyProduction.Datee,
    DailyProduction.WellName,
    CAST(WellTest.GrossTest AS FLOAT) AS GrossTest,
    CAST(WellTest.NetTest AS FLOAT) AS net_oil,
    CAST((ROUND((WellTest.GrossTest - WellTest.NetTest), 2) / WellTest.GrossTest) * 100 AS FLOAT) AS WcTest,
    Layers.Layer 
FROM 
    DailyProduction
LEFT JOIN 
    WellTest ON DailyProduction.ID = WellTest.DailyProdID
LEFT JOIN 
    Layers ON DailyProduction.Datee = Layers.Date AND DailyProduction.WellName = Layers.WellName

ORDER BY 
    DailyProduction.WellName, 
    DailyProduction.Datee;

'''
    sql_query2 = '''SELECT * FROM pressure'''

    # first dataframe test
    df = pd.read_sql_query(sql_query1,conn2)
    df['Datee']=pd.to_datetime(df['Datee'])
    df['Layer'].fillna(method='ffill',inplace=True)
    df = df[pd.to_numeric(df['GrossTest'], errors='coerce').notna()]
    df['GrossTest']=df['GrossTest'].astype(float)
    df = df.reset_index(drop=True)
    df.sort_values('Datee')
    df['Datee'] = df['Datee'].dt.strftime('%Y-%m-%d')

    #second dataframe pressure
    df1 = pd.read_sql_query(sql_query2,conn2)
    df1['Datee']=pd.to_datetime(df1['Datee'])
    df1['Layer'].fillna(method='ffill',inplace=True)
    df1 = df1[pd.to_numeric(df1['PiP'], errors='coerce').notna()]
    df1['PiP']=df1['PiP'].astype(float)
    df1= df1.reset_index(drop=True)
    df1.sort_values('Datee')
    df1['Datee'] = df1['Datee'].dt.strftime('%Y-%m-%d')





    st.sidebar.header("Filter here")
    well_name = st.sidebar.multiselect(
        'Selec well name',options=df['WellName'].unique(),
        default=df['WellName'].head(1))





    df_layer = df[df['WellName'].isin(well_name)]
    if not df_layer.empty:
        title = df_layer['WellName'].iloc[0]
    else:
        title = 'nth to show'    
    layer = st.sidebar.multiselect(
        'Selec layer',options=df['Layer'].unique(),
        default=df_layer['Layer'].unique())

    df_selection = df[df['WellName'].isin(well_name) & df['Layer'].isin(layer)]

    df_final = df_selection.groupby('Datee').agg({'GrossTest':'sum','net_oil':'sum','WcTest':'sum'}).reset_index()

    df_selection2 = df1[df1['WellName'].isin(well_name) & df1['Layer'].isin(layer)]

    df_final2 = df_selection2.groupby('Datee')["PiP"].sum().reset_index()
    
  
    merged_df = pd.concat([df_final, df_final2], axis=1)

   # Export the merged DataFrame to a CSV file

    

    csv_data=merged_df.to_csv( index=False)
    st.download_button(label='export csv',data= csv_data,file_name='prod_test.csv',mime='text/csv')
        
    def update_running_graph(df1, df2):
        # Trace for the first dataframe (df1)
        trace1 = go.Scatter(x=df1['Datee'],
                            y=df1['GrossTest'],
                            name='Crude',
                            mode='lines+markers',
                            yaxis='y1',
                            line=dict(color='black'))  # GrossTest with black color
    
        trace2 = go.Scatter(x=df1['Datee'],
                            y=df1['WcTest'],
                            name='Model',
                            mode='lines+markers',
                            yaxis='y2',
                            line=dict(color='blue', dash='dot'))  # WcTest with blue color and dotted line style
        
        trace3 = go.Scatter(x=df1['Datee'],
                            y=df1['net_oil'],
                            name='net_oil',
                            mode='lines+markers',
                            yaxis='y1',
                            line=dict(color='green'))  # net_oil with green color
        
        # Define the data list with the traces for the first plot
        data1 = [trace1, trace2, trace3]
        
        # Layout for the first plot
        layout1 = go.Layout(
            title='asdf',  # Title for the plot
            yaxis=dict(title='Crude and Model', side='left', showgrid=False),
            yaxis2=dict(title='Model Difference', overlaying='y', side='right', range=[0, 100]),  # Secondary axis for WcTest from 0 to 100
            xaxis=dict(title='Datee', showgrid=False),
            legend=dict(x=0, y=1.1, orientation="h"),
            width=1000,  # Adjust width as needed
            height=800   # Adjust height as needed
        )
        
        # Create the figure for the first plot
        fig1 = go.Figure(data=data1, layout=layout1)
        
        # Trace for the second dataframe (df2)
        trace4 = go.Scatter(x=df2['Datee'],
                            y=df2['PiP'],
                            name='PiP',
                            mode='lines+markers',
                            yaxis='y1',
                            line=dict(color='red'))  # PiP with red color
        
        # Define the data list with the trace for the second plot
        data2 = [trace4]
        
        # Layout for the second plot
        layout2 = go.Layout(
            title='asdf',  # Title for the plot
            yaxis=dict(title='PiP', side='left', showgrid=False),
            xaxis=dict(title='Datee', showgrid=False),
            width=1000,  # Adjust width as needed
            height=600   # Adjust height as needed
        )
        
        # Create the figure for the second plot
        fig2 = go.Figure(data=data2, layout=layout2)
        
        return fig1, fig2
        
            
# Define the two functions
    fig1, fig2 = update_running_graph(df_final, df_final2)
# Conditional updates for the second subplot based on data availability
    if not df_selection.empty:
        

# Display the figures in Streamlit
        st.plotly_chart(fig1)
        st.plotly_chart(fig2)
        # Update x-axis grid for the second subplot
       
    else:
        # Handle the case where data is not selected
        st.write('Please select well_name')
            