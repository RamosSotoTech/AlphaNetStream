import streamlit as st
import pandas as pd
import requests
import io
from models.Pipeline import Pipeline
from mitosheet.streamlit.v1 import spreadsheet
from utils.pipeline_utils import reporting, data_manipulation, exploratory_analysis, visualization
from utils.streamlit_utils import with_sidebar
from utils.introspection import get_module_functions_info

# Dictionary to hold libraries
libraries_dict = {
    'Data Manipulation': get_module_functions_info(data_manipulation),
    'Exploratory Analysis': get_module_functions_info(exploratory_analysis),
    'Visualization': get_module_functions_info(visualization),
    'Reporting': get_module_functions_info(reporting)
}


# Load Data step
def load_data():
    st.header("Step 1: Load Data")
    input_method = st.radio("Choose input method:", ["Upload File", "Provide URL"])

    if input_method == "Upload File":
        data_file = st.file_uploader("Upload CSV", type=['csv'])
        if data_file is not None:
            print('it was not null')
            try:
                print(data_file)
                data = pd.read_csv(data_file)
                print(data)
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
    if 'data' not in st.session_state:
        # If not, create a new Pipeline object and store it in the session state
        st.session_state['data'] = pd.DataFrame()

    if 'pipeline' not in st.session_state:
        # If not, create a new Pipeline object and store it in the session state
        st.session_state['pipeline'] = Pipeline()

    st.title('Pipeline Constructor')
    download_expander = st.sidebar.expander('Download Sample Data', expanded=False)
    with download_expander:
        load_data()

        if st.sidebar.button('Default Data', key='load_default'):
            st.session_state['data'] = pd.read_csv('database/economicCalendarSample.csv')

    # Now, always use st.session_state['pipeline'] to refer to the pipeline
    pipeline = st.session_state['pipeline']
    data = st.session_state['data']
    if data is not None:
        print(data)
        st.write(data.head())

    if data is not None:
        st.subheader('Coerce Column Data Types')
        coercion_expander = st.expander('Specify Column Data Types', expanded=False)

        with coercion_expander:
            # Pass the dataframe to MitoSheet for editing
            new_dfs, _ = spreadsheet(data, df_names=['data'])
            # Obtain the edited dataframe
            edited_data = list(new_dfs.values())[0]
            st.session_state['data'] = edited_data

        # Button to display data types after editing
        if st.button('Display Data Types'):
            dtypes = st.session_state['data'].dtypes
            st.write('Data types:', dtypes)

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
        args = [data]  # start args list with the data DataFrame
        args.extend(
            [param['value'] for param in selected_vis_info['params'][1:] if 'value' in param])  # add other params
        st.pyplot(selected_vis_func(*args))  # pass the args list to the selected visualization function

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
