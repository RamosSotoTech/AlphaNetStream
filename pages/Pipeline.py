import streamlit as st
import pandas as pd
import requests
import io
from models.Pipeline import Pipeline
from explore_data import explore_data
from st_pages import show_pages_from_config, add_page_title

from utils.pipeline_utils import reporting, data_manipulation, exploratory_analysis, visualization
from utils.streamlit_utils import with_sidebar

# Dictionary to hold libraries
libraries_dict = {
    'Data Manipulation': data_manipulation.function_info_dict,
    'Exploratory Analysis': exploratory_analysis.function_info_dict,
    'Visualization': visualization.function_info_dict,
    'Reporting': reporting.function_info_dict
}


# Load Data step
def load_data():
    st.header("Step 1: Load Data")
    input_method = st.radio("Choose input method:", ["Upload File", "Provide URL"])

    if input_method == "Upload File":
        data_file = st.file_uploader("Upload CSV", type=['csv'])
        if data_file is not None:
            try:
                data = pd.read_csv(data_file)
                st.session_state.data = data  # Save data to session state
                st.rerun()  # Rerun the app
            except pd.errors.ParserError:
                st.error("The uploaded file is not a valid CSV file.")
            except Exception as e:
                st.error(f"An error occurred: {e}")

    elif input_method == "Provide URL":
        url = st.text_input("Enter the URL of the data file:")
        if url:
            try:
                response = requests.get(url)
                response.raise_for_status()  # Check if the request was successful
                if url.lower().endswith('.csv'):
                    data = pd.read_csv(io.StringIO(response.text))
                    st.session_state.data = data  # Save data to session state
                    st.rerun()  # Rerun the app
                # todo: Add support for other file types
                else:
                    st.error("Unsupported file type. Please provide a CSV URL.")
            except requests.RequestException as e:
                st.error(f"Failed to fetch data from URL: {e}")


# Clean Data step
def clean_data():
    st.header("Step 3: Clean Data")
    # todo: Implement data cleaning logic
    if st.button("Next Step", key="clean_next"):
        st.rerun()


# Visualize Data step
def visualize_data():
    st.header("Step 4: Visualize Data")
    # todo: Implement data visualization logic
    if st.button("Next Step", key="visualize_next"):
        st.rerun()


# Generate Report step
def generate_report():
    st.header("Step 5: Generate Report")
    # todo: Implement report generation logic


@with_sidebar
def render():
    # add_page_title()
    #
    # tab1, tab2, tab3, tab4, tab5 = st.tabs(["Load Data", "Explore Data", "Clean Data", "Visualize Data", "Generate "
    #                                                                                                      "Report"])
    #
    # # Load Data Tab
    # with tab1:
    #     load_data()
    #
    # # Explore Data Tab
    # with tab2:
    #     # Assuming st.session_state.data is already loaded with data
    #     explore_data()
    #
    # # Clean Data Tab
    # with tab3:
    #     clean_data()
    #
    # # Visualize Data Tab
    # with tab4:
    #     visualize_data()
    #
    # # Generate Report Tab
    # with tab5:
    #     generate_report()
    st.title('Pipeline Constructor')

    file = st.file_uploader('Upload CSV')
    data = None

    if 'data' not in st.session_state:
        st.session_state['data'] = pd.read_csv('database/economicCalendarSample.csv')

    data = st.session_state['data']

    if st.button('Default Data', key='load_default'):
        data = pd.read_csv('database/economicCalendarSample.csv')
        st.write(data.head())

    if file is not None:
        data = load_data(file)  # Assume load_data is implemented

    if 'pipeline' not in st.session_state:
        # If not, create a new Pipeline object and store it in the session state
        st.session_state['pipeline'] = Pipeline()

    # Now, always use st.session_state['pipeline'] to refer to the pipeline
    pipeline = st.session_state['pipeline']

    st.sidebar.header('Library Selection')
    selected_library = st.sidebar.selectbox(
        'Select Library',
        list(libraries_dict.keys())
    )

    st.sidebar.header('Method Selection')
    selected_function_name = st.sidebar.selectbox(
        'Select Function',
        list(libraries_dict[selected_library].keys())
    )

    selected_function_info = libraries_dict[selected_library][selected_function_name]
    for i, param_info in enumerate(selected_function_info['params']):
        # Skip the first parameter (data)
        if i == 0:
            continue

        param_name = param_info['name']
        if param_name == 'columns':
            # If the parameter is 'columns', show a multiselect box to select multiple columns
            param_info['value'] = st.multiselect(f"Select {param_name}", options=data.keys())
        elif param_name == 'column':
            # If the parameter is 'column', show a select box to select a single column
            param_info['value'] = st.selectbox(f"Select {param_name}", options=data.keys())
        else:
            # For other parameters, show a text input box
            param_info['value'] = st.sidebar.text_input(f"Enter value for {param_name}")

    if st.sidebar.button('Add Step', key='add_step'):
        pipeline.add_step(selected_function_info)

    # Main Display Area
    vis_container = st.container()
    pipeline_container = st.container()
    # Main window for visualization
    st.header('Visualization Section')

    # Option to select a visualization method
    vis_library = libraries_dict['Visualization']
    selected_vis_method = st.selectbox(
        'Select Visualization Method',
        list(vis_library.keys())
    )
    selected_vis_info = vis_library[selected_vis_method]
    for i, param_info in enumerate(selected_vis_info['params']):
        # Skip the first parameter (data)
        if i == 0:
            continue
        param_name = param_info['name']
        if 'columns' in param_name:
            # If the parameter is 'columns', show a multiselect box to select multiple columns
            param_info['value'] = st.multiselect(f"Select {param_name}", options=data.keys())
        elif 'column' in param_name:
            # If the parameter is 'column', show a select box to select a single column
            param_info['value'] = st.selectbox(f"Select {param_name}", options=data.keys())
        else:
            # For other parameters, show a text input box
            param_info['value'] = st.text_input(f"Enter value for {param_name}", key=param_name)


    if st.button('Show Visualization'):
        selected_vis_func = selected_vis_info['func']
        args = [param['value'] for param in selected_vis_info['params'] if 'value' in param]
        selected_vis_func(*args)  # Assumes the visualization function displays the visualization directly

    # Run the pipeline and update the containers only when the 'Run Pipeline' button is clicked
    if st.sidebar.button('Run Pipeline', key='run'):
        # with vis_container:
        #     st.header('Visualization')
        #     if 'Visualize' in [step['category'] for step in pipeline.steps]:
        #         # Assume visualization steps update the container directly
        #         pipeline.run()

        with pipeline_container:
            st.header('Pipeline Architecture')
            pipeline.display_architecture()


if __name__ == "__main__":
    render()
