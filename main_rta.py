# -*- coding: utf-8 -*- 
"""
Created on Wed Jan 10 12:22:14 2024

@author: Tan7080
"""

import pandas as pd
import numpy as np
import sqlite3

import matplotlib.pyplot as plt
import plotly.express as px
import streamlit as st
import statsmodels.api as sm
import seaborn as sns

def rate_trans():
    # Choose wide mode as the default setting
   
    conn = sqlite3.connect('MyData.db')
    
    sql_query = '''SELECT * FROM processedData'''
    
    df = pd.read_sql_query(sql_query,conn)
    
    sql_query1 = '''SELECT Layer,WellName,pr_initial FROM Layers
WHERE pr_initial IS NOT NULL
ORDER By Date'''

   
    pressure = pd.read_sql_query(sql_query1,conn)
    
    
    st.sidebar.header("input data")
    well_name = st.sidebar.multiselect(
        'Selec well name',options=pressure['WellName'].unique(),
        default='GAN-10')
    
    df_layer = pressure[pressure['WellName'].isin(well_name)]
    
    layer  = st.sidebar.multiselect(
        'Selec Layer',options=pressure['Layer'].unique(),
        default=df_layer['Layer'].unique())
    
    co = st.sidebar.number_input('Enter Co', value=0.000006,step=0.01, format="%f", key="co")
    cw = st.sidebar.number_input('Enter Cw', value=0.000004,step=0.01, format="%f", key="cw")
    cm = st.sidebar.number_input('Enter Cm', value=0.000004,step=0.01, format="%f", key="cm")
    
    
    try:
    
        
        def get_filtered_data(well_name, layer):
      
             filtered_data = df[df['WellName'].isin(well_name) & df['Layer'].isin(layer)]
        
             return filtered_data
    
    
    
        def get_pr_initial(well_name, layer):
           
        
            # Filter the DataFrame based on the specified conditions
            filtered_pressure = pressure[pressure['WellName'].isin(well_name) & pressure['Layer'].isin(layer)]
        
            # Check if there are any rows in the filtered DataFrame
            if not filtered_pressure.empty:
                # Return the value of pr_initial
                return filtered_pressure['pr_initial'].iloc[0]
            else:
                # Return None if no matching rows found
                return None
            
            
        pri = get_pr_initial(well_name, layer)
        
        
        def process_data(df,pri=pri):
        # Assuming 'Days', 'GrossTest', 'PiP' are columns in df
            df = df.copy()
            df['days_diff'] = df['Days'].diff().shift(-1)
            df.replace(np.nan, 1, inplace=True)
            df['product'] = df['NetTest'] * df['days_diff']
            df['cumm'] = df['product'].cumsum()
            df['norm_rate'] = df['cumm'] / df['NetTest']
              # Assuming 'pri' is the column name
            df['norm_press'] = (pri - df['PiP']) / df['NetTest']
            
            return df
            
      
    
        
        def fit_linear_regression(data):
            x = data['norm_rate']
            y = data['norm_press']
        
            # Add a constant term to the independent variable (for intercept)
            X = sm.add_constant(x)
        
            # Fit a linear regression model
            model = sm.OLS(y, X).fit()
        
            # Extract the parameters
            intercept, slope = model.params['const'], model.params[x.name]
        
            return intercept, slope
        
        
       
        
        def plot_scatter_with_regression(data, intercept, slope):
            x = data['norm_rate']
            y = data['norm_press']
        
            # Plot the scatter plot
            scat = px.scatter(x=x, y=y, labels={'x': 'Normalized Rate', 'y': 'Normalized Pressure'})
        
            # Add the linear regression line to the plot
            scat.update_layout(
                shapes=[
                    dict(
                        type='line',
                        x0=x.min(),
                        x1=x.max(),
                        y0=intercept + slope * x.min(),
                        y1=intercept + slope * x.max(),
                        line=dict(color='red', width=2),
                    )
                ],
                title='Scatter Plot with Regression Line',
                xaxis_title='Normalized Rate',
                yaxis_title='Normalized Pressure',
                width=800,  # Adjust the width of the figure
                height=500  # Adjust the height of the figure
            )
        
            # Display the Plotly figure using st.plotly_chart()
            st.plotly_chart(scat)
            
        def treat_outliers(data, column_to_plot):
            q1 = data[column_to_plot].quantile(0.25)
            q3 = data[column_to_plot].quantile(0.75)
            iqr = q3 - q1
            lower_bound = q1 - 1.5 * iqr
            upper_bound = q3 + 1.5 * iqr
        
            # Identify and remove outliers
            
            outliers = processed_data[(processed_data[column_to_plot] < lower_bound) | (processed_data[column_to_plot] > upper_bound)]
            processed_data_no_outliers = processed_data[(processed_data[column_to_plot] >= lower_bound) & (processed_data[column_to_plot] <= upper_bound)]
        
            return  processed_data_no_outliers
        
        
        
                
            
        def ooip(co,cw,cm):
            ct= co + cw + cm 
        
            N = 1 / (m*ct)
        
            j = 1/b
            
            return N,j
    
    
        st.set_option('deprecation.showPyplotGlobalUse', False)
       
        
            
            
        data = get_filtered_data(well_name, layer)
        
        
        
        
        tab1,tab2 = st.tabs(["actual_data",'no_outliers'])
      
        
        
        
        
        
        
      

        with tab1:
            processed_data = process_data(data)
            b, m = fit_linear_regression(processed_data)
            
            
            # Display sliders in the sidebar
            slope_actual = st.sidebar.number_input('slope_actual', value=m, step=0.001, format="%.3f", key="slopee")
            intercept_actual = st.sidebar.number_input('intercept_actual', value=b, step=0.01, key="interesd")
            processed_data['pr_avg']= (processed_data['GrossTest']/(1/b)) + processed_data['PiP']
            # Plot scatter with regression
            col1,col2 = st.columns([1,1])
            with col1:
                plot_scatter_with_regression(processed_data, intercept_actual, slope_actual)
                scat = px.scatter(processed_data, x='Datee', y='pr_avg')
                st.plotly_chart(scat)
                
            with col2:
                m = slope_actual 
                b = intercept_actual
                N,j = ooip(co,cw,cm)
                N = round(N,2)
                j =round(j,2)
                
            
                
                st.markdown(f"<h1 style='text-align: center; color: blue;'>OOIP is: {N} bbls</h1>", unsafe_allow_html=True)
                st.markdown(f"<h2 style='text-align: center; color: green;'>Productivity is: {j}</h2>", unsafe_allow_html=True)
                sns.boxplot(x=processed_data['norm_press'])
 
                # Add labels and title
                plt.xlabel('Category Label')
                plt.ylabel('Values')
                plt.title('Boxplot of ' + 'norm_press')
                
                # Display the plot in Streamlit
                st.pyplot()

                
            
            
        with tab2:
            processed_data = process_data(data)
            processed_data = treat_outliers(processed_data, 'norm_press')
            b, m = fit_linear_regression(processed_data)
            
            # Display sliders in the sidebar
            slope_treated = st.sidebar.number_input('slope_treated', value=m, step=0.001, format="%.3f", key="slopee23")
            intercept_treated = st.sidebar.number_input('intercept_treated', value=b, step=0.01, key="interes23d")
            col1,col2 = st.columns([1,1])
            
            with col1:
                processed_data['pr_avg']= (processed_data['GrossTest']/(1/b)) + processed_data['PiP']
                # Plot scatter with regression
                plot_scatter_with_regression(processed_data, intercept_treated, slope_treated)     
                scat = px.scatter(processed_data, x='Datee', y='pr_avg')
                st.plotly_chart(scat)
                
                
                
            with col2:
                m = slope_treated
                b = intercept_treated
                N,j = ooip(co,cw,cm)
                N = round(N,2)
                j =round(j,2)
                
               
                st.markdown(f"<h1 style='text-align: center; color: blue; font-size: 24px;'>OOIP is: {N} bbls</h1>", unsafe_allow_html=True)
                st.markdown(f"<h2 style='text-align: center; color: green; font-size: 18px;'>Productivity is: {j}</h2>", unsafe_allow_html=True)
                sns.boxplot(x=processed_data['norm_press'])

                # Add labels and title
                plt.xlabel('Category Label')
                plt.ylabel('Values')
                plt.title('Boxplot of ' + 'norm_press')
                
                # Display the plot in Streamlit
                st.pyplot()

       
        
        
      
        
       
    
        
                # Use JavaScript to update the sliders without creating new ones
              
               
                              
          
          
          
       
    except Exception as e:
      st.error(e)
   
    
    
    
    
    
    
    

    
    
    
    

