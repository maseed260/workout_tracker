import os
import sys
import time
import plotly
import pandas as pd
from snowflake.snowpark import Session
from PIL import Image
import streamlit as st
import plotly.express as px
from datetime import datetime
import plotly.graph_objects as go

# Setting page config to wide
st.set_page_config(layout="wide", page_title="Workout Tracker")

st.markdown('<h1 style="color:#3D57EF; font-weight:bold;">My Workout Tracker</h1>', unsafe_allow_html=True) # :mechanical_arm:
st.divider()

def set_stage(stage):
    st.session_state.stage = stage
    
def streamlit_menu():
    try:
        if "stage" not in st.session_state:
            st.session_state.stage = 1

        with st.sidebar:
            st.write("##")
            st.write("##")
            st.image('muscle.png', width=200)
            st.write("##")
            st.button(
                label="Workout planner",
                on_click=set_stage,
                args=(1,),
                type="primary",
                use_container_width=True,
            )
            st.button(
                label="Workout Logger",
                on_click=set_stage,
                args=(2,),
                type="primary",
                use_container_width=True,
            )
            st.button(
                label="Workout Insights",
                on_click=set_stage,
                args=(3,),
                type="primary",
                use_container_width=True,
            )

        if st.session_state.stage == 1:
            selected = "Workout planner"
        if st.session_state.stage == 2:
            selected = "Workout Logger"
        if st.session_state.stage == 3:
            selected = "Workout Insights"
            
    except Exception as e:
        selected = None
    return selected

def main(session):
    selected = streamlit_menu()
    df = session.table('"workout"').to_pandas()
    
    workout_options= df['Workout'].unique().tolist()
    position_options= df['Position'].unique().tolist()
    muscle_options= df['Muscle'].unique().tolist()
            
    if selected == "Workout planner":
        st.write("WIP")
    elif selected == "Workout Logger":
        st.write("**➥ Easily track and edit your workout data with custom inputs for each exercise.**")
        # Editable DataFrame
        edited_df = st.data_editor(
            df,
            column_config={
                "Date": st.column_config.DateColumn("Date",width="low",format="YYYY-MM-DD",required=True),
                "Workout": st.column_config.SelectboxColumn("Workout",width="low",options=workout_options,required=True),
                "Exercise": st.column_config.TextColumn("Exercise",width="medium",max_chars=75,required=True),
                "Position": st.column_config.SelectboxColumn("Position",width="low",options=position_options,required=True),
                "Weight": st.column_config.NumberColumn("Weight",width="low",required=True,min_value=0,max_value=300,step=1),
                "Set_Number": st.column_config.NumberColumn("Set_Number",width="low",required=True,min_value=1,max_value=10,step=1),
                "Target_Reps": st.column_config.NumberColumn("Target_Reps",width="low",required=True,min_value=1,max_value=50,step=1),
                "Number_Of_Reps": st.column_config.NumberColumn("Number_Of_Reps",width="low",required=True,min_value=1,max_value=50,step=1),
                "Is_Compound": st.column_config.SelectboxColumn("Is_Compound",width="low",options=['Yes','No'],required=True),
                "Muscle": st.column_config.SelectboxColumn("Muscle",width="low",options=muscle_options,required=True),
            },
            hide_index=True,
            num_rows="dynamic",
            use_container_width=True
        )
        
        if not edited_df.empty and st.button(":green[**save**]"):
            #st.dataframe(edited_df, use_container_width=True, hide_index=True)
            edited_df['Workout_Exercise'] = edited_df['Workout']+"-"+edited_df['Exercise']
            session.write_pandas(edited_df,"workout", auto_create_table=True, overwrite=True, use_logical_type=True)
            st.success("**Workout saved successfully**")
            
    elif selected == "Workout Insights":
        st.write("**➥ Here's a detailed log of your workout history, tracking exercises, sets, reps, and progression over time**")
        
        #df=df.drop("Workout_Exercise",axis=1)        
        
        st.dataframe(df, use_container_width=True, hide_index=True)
        st.divider()
        
        ###################
        ##### Chart-1 #####
        ###################
        # Count the number of workouts for each date
        workout_counts = df.groupby('Date').size().reset_index(name='Total_Workouts')

        # Create a line plot
        fig_1 = px.line(workout_counts, x='Date', y='Total_Workouts', title='Total Workouts Over Time', labels={'Total_Workouts': 'Number of Workouts'})

        # Show the plot
        with st.container(border=True):
            st.plotly_chart(fig_1)
        
        ###################
        ##### Chart-2 #####
        ###################
        # Count the frequency of each exercise
        exercise_frequency = df['Exercise'].value_counts().reset_index()
        exercise_frequency.columns = ['Exercise', 'Frequency']

        # Create a bar plot
        fig_2 = px.bar(exercise_frequency, x='Exercise', y='Frequency', title='Exercise Frequency',
                    labels={'Frequency': 'Number of Sessions'}, text='Frequency')

        # Show the plot
        fig_2.update_traces(texttemplate='%{text}', textposition='outside')
        fig_2.update_layout(height=600)
        with st.container(border=True, height=600):
            st.plotly_chart(fig_2)
        
        ###################
        ##### Chart-3 #####
        ###################  
        # Count the number of workouts for each muscle group
        muscle_split = df['Muscle'].value_counts().reset_index()
        muscle_split.columns = ['Muscle', 'Frequency']

        # Create a pie chart
        fig_3 = px.pie(muscle_split, names='Muscle', values='Frequency', title='Workout Split by Muscle Group')

        # Show the plot
        with st.container(border=True):
            st.plotly_chart(fig_3)
            
        ###################
        ##### Chart-4 #####
        ################### 
        # Weight Progression
        # Group by Exercise and Date, taking the max weight lifted
        weight_progression = df.groupby(['Exercise', 'Date'])['Weight'].max().reset_index()

        # Create a line plot
        fig_4 = px.line(weight_progression, x='Date', y='Weight', color='Exercise', title='Weight Progression Over Time',
                    labels={'Weight': 'Weight Lifted (kg)'})
        fig_4.update_layout(height=600)
        # Show the plot
        with st.container(border=True,height=600):
            st.plotly_chart(fig_4)
            
        
        ###################
        ##### Chart-5 #####
        ################### 
        # Reps Progression
        # Group by Exercise and Date, taking the max reps performed
        reps_progression = df.groupby(['Exercise', 'Date'])['Number_Of_Reps'].max().reset_index()

        # Create a line plot
        fig_5 = px.line(reps_progression, x='Date', y='Number_Of_Reps', color='Exercise', title='Reps Progression Over Time',
                    labels={'Number_Of_Reps': 'Number of Reps'})

        fig_5.update_layout(height=600)
        # Show the plot
        with st.container(border=True,height=600):
            st.plotly_chart(fig_5)
            

        ###################
        ##### Chart-6 #####
        ################### 
        # volume load
        # Calculate Volume Load
        df['Volume_Load'] = df['Weight'] * df['Number_Of_Reps']

        # Group by Date and Exercise, summing the volume load
        volume_load = df.groupby(['Date', 'Exercise'])['Volume_Load'].sum().reset_index()

        # Create a line plot
        fig_6 = px.line(volume_load, x='Date', y='Volume_Load', color='Exercise', title='Volume Load Over Time',
                    labels={'Volume_Load': 'Total Volume Load (kg)'})
        fig_6.update_layout(height=600)
        # Show the plot
        with st.container(border=True,height=600):
            st.plotly_chart(fig_6)
            
        ###################
        ##### Chart-7 #####
        ################### 
        # Muscle group focus
        # Group by Muscle and Date, summing the volume load or counting workouts
        muscle_group_focus = df.groupby(['Date', 'Muscle'])['Volume_Load'].sum().reset_index()

        # Create a line plot for total volume per muscle group over time
        fig_7 = px.line(muscle_group_focus, x='Date', y='Volume_Load', color='Muscle', 
                    title='Muscle Group Focus Over Time',
                    labels={'Volume_Load': 'Total Volume Load (kg)'})

        # Show the plot
        fig_7.update_layout(height=600)
        # Show the plot
        with st.container(border=True,height=600):
            st.plotly_chart(fig_7)
            
        ###################
        ##### Chart-8 #####
        ################### 
        # compound vs Isolation
        # Group by Is_Compound and calculate total volume load
        compound_isolation = df.groupby('Is_Compound')['Volume_Load'].sum().reset_index()

        # Create a bar plot to compare compound vs isolation
        fig_8 = px.bar(compound_isolation, x='Is_Compound', y='Volume_Load', 
                    title='Compound vs Isolation Volume Load',
                    labels={'Is_Compound': 'Exercise Type', 'Volume_Load': 'Total Volume Load (kg)'})

        # Show the plot
        with st.container(border=True):
            st.plotly_chart(fig_8)
            
        ###################
        ##### Chart-9 #####
        ###################
        # Calculate volume load for each entry
        df['Volume_Load'] = df['Weight'] * df['Number_Of_Reps']

        # Group by Muscle and calculate total volume load, then sort by Volume_Load in descending order
        volume_per_muscle = df.groupby('Muscle')['Volume_Load'].sum().reset_index().sort_values(by='Volume_Load', ascending=False)

        # Create a bar plot for volume per muscle group
        fig_9 = px.bar(volume_per_muscle, x='Muscle', y='Volume_Load', 
                    title='Total Volume per Muscle Group',
                    labels={'Volume_Load': 'Total Volume Load (kg)'})

        # Update layout to tilt x-axis labels to avoid overlap
        fig_9.update_layout(xaxis_tickangle=-45)

        # Show the plot
        with st.container(border=True):
            st.plotly_chart(fig_9)
            
        ####################
        ##### Chart-10 #####
        ####################
        # Group by Workout_Exercise and calculate total volume load
        volume_per_exercise = df.groupby('Workout_Exercise')['Volume_Load'].sum().reset_index()

        # Create a bar plot for volume per exercise
        fig_10 = px.bar(volume_per_exercise.sort_values('Volume_Load', ascending=False), 
                    x='Workout_Exercise', y='Volume_Load', 
                    title='Total Volume per Exercise',
                    labels={'Volume_Load': 'Total Volume Load (kg)'},
                    text='Volume_Load')

        # Show the plot
        fig_10.update_traces(texttemplate='%{text:.2f}', textposition='outside')
        fig_10.update_layout(xaxis_title='Exercise', yaxis_title='Total Volume Load (kg)', xaxis_tickangle=-45)
        fig_10.update_layout(height=600)
        
        # Show the plot
        with st.container(border=True):
            st.plotly_chart(fig_10)
            
        ####################
        ##### Chart-11 #####
        #################### 
        # Group by Date and calculate total target and actual reps
        target_vs_actual = df.groupby('Date').agg({'Target_Reps': 'sum', 'Number_Of_Reps': 'sum'}).reset_index()

        # Create a line plot for target and actual reps
        fig_11 = px.line(target_vs_actual, x='Date', 
                    y=['Target_Reps', 'Number_Of_Reps'], 
                    title='Target Reps vs. Actual Reps Over Time',
                    labels={'value': 'Reps', 'variable': 'Type'},
                    color_discrete_sequence=['blue', 'orange'])

        # Show the plot
        fig_11.update_layout(height=600)
        # Show the plot
        with st.container(border=True,height=600):
            st.plotly_chart(fig_11)
        
        ####################
        ##### Chart-12 #####
        #################### 
        # Create a column to check if actual reps meet or exceed target reps
        df['Met_Target'] = df['Number_Of_Reps'] >= df['Target_Reps']

        # Calculate completion rate per date
        completion_rate = df.groupby('Date')['Met_Target'].mean().reset_index(name='Completion_Rate')

        # Create a line plot for completion rate over time
        fig_12 = px.line(completion_rate, x='Date', y='Completion_Rate', 
                    title='Exercise Completion Rate Over Time',
                    labels={'Completion_Rate': 'Completion Rate (%)'})

        # Show the plot
        fig_12.update_layout(height=600)
        # Show the plot
        with st.container(border=True,height=600):
            st.plotly_chart(fig_12)


    
if __name__ == "__main__":
    azure_snowpark_connection_params = {
        "user": "ilyas",
        "password": "Ilyas@260",
        "account":  "GHB93140",
        "warehouse": "compute_wh",
        "database": "ilyas_db",
        "schema": "test",
        "role": "accountadmin"
    }
    session = Session.builder.configs(azure_snowpark_connection_params).create()
    
    main(session)
