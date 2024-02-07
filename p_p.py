import sqlite3
import pandas as pd
import numpy as np
import streamlit as st
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import seaborn as sns




def test():


    conn2 = sqlite3.connect('MyData.db')

    sql_query1 = '''SELECT * FROM test'''
    sql_query2 = '''SELECT * FROM pressure'''

    # first dataframe test
    df = pd.read_sql_query(sql_query1,conn2)
    df['Datee']=pd.to_datetime(df['Datee'])
    df['WaterProduced'] = pd.to_numeric(df['WaterProduced'], errors='coerce')
    df['Layer'].fillna(method='ffill',inplace=True)
    df = df[pd.to_numeric(df['GrossTest'], errors='coerce').notna()]
    df['GrossTest']=df['GrossTest'].astype(float)
    df['WaterProduced']=df['WaterProduced'].astype(float)
    df['net_oil']=df['GrossTest']-df['WaterProduced']
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

    df_final = df_selection.groupby('Datee').agg({'GrossTest':'sum','net_oil':'sum','WaterProduced':'sum'}).reset_index()

    df_selection2 = df1[df1['WellName'].isin(well_name) & df1['Layer'].isin(layer)]

    df_final2 = df_selection2.groupby('Datee')["PiP"].sum().reset_index()
    
  
    merged_df = pd.concat([df_final, df_final2], axis=1)

   # Export the merged DataFrame to a CSV file

    

    csv_data=merged_df.to_csv( index=False)
    st.download_button(label='export csv',data= csv_data,file_name='prod_test.csv',mime='text/csv')
        
   

# Define the two functions
    def create_dual_axis_scatter_plot(df, title):
        fig = go.Figure()
        df['Datee'] = pd.to_datetime(df['Datee'])

        # Create traces for gross test, net oil, and water produced
        gross_test_trace = go.Scatter(
            x=df['Datee'],
            y=df['GrossTest'],
            mode='lines+markers',
            name='GrossTest',
            line=dict(color='black')
        )
        net_oil_trace = go.Scatter(
            x=df['Datee'],
            y=df['net_oil'],
            mode='lines+markers',
            name='net_oil',
            line=dict(color='green')
        )
        water_produced_trace = go.Scatter(
            x=df['Datee'],
            y=df['WaterProduced'],
            mode='lines+markers',
            name='WaterProduced',
            line=dict(color='blue')
        )

        # Add the traces to the figure
        fig.add_traces([gross_test_trace, net_oil_trace, water_produced_trace])

        # Update the layout
        fig.update_layout(
            title={'text': title, 'x': 0.4},
            width=1100,
            xaxis={'gridcolor': 'black', 'gridwidth': 1, 'showgrid': True, 'title': {'text': 'Datee'}},
            yaxis={'gridcolor': 'black', 'gridwidth': 1, 'showgrid': True, 'title': {'text': 'Values'}}
        )

        return fig

    def pressure_chart(df):
        fig = go.Figure()
        df['Datee'] = pd.to_datetime(df['Datee'])

        # Create a trace for pump intake pressure
        pip_trace = go.Scatter(
            x=df['Datee'],
            y=df['PiP'],
            mode='lines+markers',
            name='Pump_intake',
            line=dict(color='red')
        )

        # Add the trace to the figure
        fig.add_trace(pip_trace)

        # Update the layout
        fig.update_layout(
            width=1100,
            xaxis={'gridcolor': 'black', 'gridwidth': 1, 'showgrid': True, 'title': {'text': 'Datee'}},
            yaxis={'gridcolor': 'black', 'gridwidth': 1, 'showgrid': True, 'title': {'text': 'Values'}})

        return fig

# Create separate figure objects for each subplot
    fig1 = create_dual_axis_scatter_plot(df_final, "Title 1")
    fig2 = pressure_chart(df_final2)

    # Combine the subplot figures into a single figure
    fig = make_subplots(rows=2, cols=1, shared_xaxes=True, vertical_spacing=0.1)

# Add traces to subplots
    fig.add_trace(fig1.data[0], row=1, col=1)
    fig.add_trace(fig1.data[1], row=1, col=1)
    fig.add_trace(fig1.data[2], row=1, col=1)
    fig.add_trace(fig2.data[0], row=2, col=1)

    # Update the layout
    fig.update_xaxes(showgrid=True, gridwidth=1, gridcolor='lightgray', row=1, col=1)
    fig.update_yaxes(showgrid=True, gridwidth=2, gridcolor='lightgray', row=1, col=1)

# Update the layout for the second subplot
    if not df_selection.empty:
        fig.update_xaxes(showgrid=True, gridwidth=1, gridcolor='lightgray', row=2, col=1)
        fig.update_yaxes(showgrid=True, gridwidth=1, gridcolor='lightgray', row=1, col=1)
        fig.update_layout(
        height=800,  # Adjust the height as needed
        width=1100,   # Adjust the width as needed
        title_text=df_selection.iloc[0,1])
        st.plotly_chart(fig)
     
    else:
        st.write('please select well_name')
        