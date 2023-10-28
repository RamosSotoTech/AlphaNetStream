import enum
import re

import numpy as np
import streamlit as st
import pandas as pd
import requests
import io
from models.Pipeline import Pipeline
from mitosheet.streamlit.v1 import spreadsheet
from utils.pipeline_utils import reporting, data_manipulation, exploratory_analysis, visualization, coercion
from utils.streamlit_utils import with_sidebar
from utils.introspection import get_module_functions_info, FunctionMetadata
import matplotlib

# Dictionary to hold libraries
libraries_dict = {
    'Data Manipulation': get_module_functions_info(data_manipulation),
    'Exploratory Analysis': get_module_functions_info(exploratory_analysis),
    'Visualization': get_module_functions_info(visualization),
    'Reporting': get_module_functions_info(reporting)
}


# Load Data step
def reset_pipeline(data):
    st.session_state['data'] = data
    st.session_state['pipeline'] = Pipeline(data)
    st.session_state['col_types_selected'] = {}
    st.session_state['pdf_report'] = None
    # st.rerun()


def display_section(section, data):
    """Display a section of the report, whether it's a table or a plot."""
    if isinstance(data, pd.DataFrame):
        if data.empty:
            st.write(f"No Data in {section}")
        else:
            st.table(data)
    elif isinstance(data, matplotlib.figure.Figure):
        st.pyplot(data)
    elif isinstance(data, dict):
        for subsection, subdata in data.items():
            st.write(f"#### {subsection}")
            display_section(subsection, subdata)


def load_data():
    st.header("Step 1: Load Data")
    input_method = st.radio("Choose input method:", ["Upload File", "Provide URL", "Use Sample Data"])

    if input_method == "Upload File":
        data_file = st.file_uploader("Upload CSV", type=['csv'])
        if data_file is not None:
            try:
                data = pd.read_csv(data_file)
                reset_pipeline(data)  # Reset pipeline and rerun
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
                    reset_pipeline(data)  # Reset pipeline and rerun
                # todo: Add support for other file types
                else:
                    st.error("Unsupported file type. Please provide a CSV URL.")
            except requests.RequestException as e:
                st.error(f"Failed to fetch data from URL: {e}")

    elif input_method == "Use Sample Data":
        dataset_name = st.selectbox('Choose a Default Dataset:', ['None', 'Random', 'Iris', 'Cars'])

        # Button to load the selected dataset
        if st.button('Load Default'):
            if dataset_name == 'Random':
                # Generate a random DataFrame with 100 rows and 4 columns
                data = pd.DataFrame(np.random.rand(100, 4), columns=['A', 'B', 'C', 'D'])
            elif dataset_name == 'Iris':
                # Load Iris dataset
                import seaborn as sns
                data = sns.load_dataset('iris')
            elif dataset_name == 'Cars':
                # Load Cars dataset
                import seaborn as sns
                data = sns.load_dataset('mpg')
            else:
                data = None  # Set to None if 'None' option is selected

            if data is not None:
                st.write('Dataset loaded:', data.head())
                reset_pipeline(data)  # Reset pipeline and rerun
            else:
                st.write('No dataset loaded.')

    if st.session_state['data'] is not None and not st.session_state['data'].empty:
        st.header('Pipeline Options')
        col1, col2 = st.columns(2)
        with col1:
            if st.button('Clear Data', key='clear_data'):
                reset_pipeline(pd.DataFrame())
        with col2:
            if st.button('Clear Pipeline', key='clear_pipeline'):
                reset_pipeline(st.session_state['data'])


@with_sidebar
def render():
    if 'data' not in st.session_state:
        # If not, create a new Pipeline object and store it in the session state
        st.session_state['data'] = pd.DataFrame()

    if 'pipeline' not in st.session_state or 'data' not in st.session_state:
        # If not, create a new Pipeline object and store it in the session state
        st.session_state['pipeline'] = Pipeline(st.session_state.get('data', None))

    st.title('Pipeline Constructor')
    download_expander = st.expander('Download Sample Data')
    with download_expander:
        load_data()

    # Now, always use st.session_state['pipeline'] to refer to the pipeline
    pipeline = st.session_state['pipeline']
    data = st.session_state['data']
    st.write(data)

    # If data is not None or empty, display the data
    if data is not None and not data.empty:
        st.subheader('Coerce Column Data Types')

        # Pass the dataframe to MitoSheet for editing
        new_dfs, str_funcs = spreadsheet(data, df_names=['data'])
        # Obtain the edited dataframe
        if new_dfs:
            edited_data = list(new_dfs.values())[0]
            st.session_state['data'] = edited_data.copy()
        # Update the session state pipeline with the edited dataframe
        if str_funcs:
            st.write(str_funcs[0])
            print(str_funcs)
            code_string = re.sub(r'^import .*$', '', str_funcs, flags=re.MULTILINE)
            code_string = re.sub(r'^from .* import .*$', '', code_string, flags=re.MULTILINE)
            func_name = code_string.strip().split('\n')[-1]
            pipeline.add_step(FunctionMetadata.from_code_string(str_funcs), func_name=func_name)

        coercion_expander = st.expander('Specify Column Data Types', expanded=False)
        with coercion_expander:
            # Get a list of columns and their current data types
            col_types = {col: str(dtype) for col, dtype in zip(data.columns, data.dtypes)}

            for col, dtype_str in col_types.items():
                # Check if objects are strings, enums, categories, or dates
                if dtype_str == 'object':
                    # Check if the column contains dates
                    if False:  # and pd.to_datetime(data[col], errors='coerce').notnull().all():
                        pass
                    # col_types[col] = 'datetime64'
                    # Check if the column contains time deltas
                    elif pd.to_timedelta(data[col], errors='coerce').notnull().all():
                        col_types[col] = 'timedelta64'
                    # Check if the column contains enum types
                    elif data[col].apply(lambda x: isinstance(x, enum.Enum)).all():
                        col_types[col] = 'enum'
                    # Check if the column contains category types
                    elif data[col].apply(lambda x: isinstance(x, pd.Categorical)).all():
                        col_types[col] = 'category'
                    # Check if the column contains strings
                    elif data[col].apply(lambda x: isinstance(x, str)).all():
                        col_types[col] = 'string'
                    else:
                        col_types[col] = 'object'  # Leave as object if the column contains mixed types

            # Create a dictionary in the session state to store user selections
            if 'col_types_selected' not in st.session_state:
                st.session_state['col_types_selected'] = col_types.copy()

            # Create comboBoxes to select 'From' and 'To' types
            from_type = st.selectbox('From:', list(set(col_types.values())))
            to_type = st.selectbox('To:', ['Numeric', 'Text', 'Date/Time', 'Boolean'])

            # Create another comboBox to select the columns that match the 'From' type
            matching_cols = [col for col, dtype in col_types.items() if dtype == from_type]
            selected_col = st.selectbox('Select Column:', matching_cols)

            # Button to apply the data type coercion
            if st.button('Apply Data Type Coercion'):
                if to_type == 'Numeric':
                    def coerce_numeric(data, column):
                        return data.assign(**{column: pd.to_numeric(data[column], errors='coerce')})

                    pipeline.add_step(coerce_numeric, selected_col, func_name='data = coerce_numeric(data, column)')
                    data[selected_col] = pd.to_numeric(data[selected_col], errors='coerce')
                elif to_type == 'Text':
                    def coerce_text(data, column):
                        return data.assign(**{column: data[column].astype('string')})

                    pipeline.add_step(coerce_text, selected_col, func_name='data = coerce_text(data, column)')
                    data[selected_col] = data[selected_col].astype('string')
                elif to_type == 'Date/Time':
                    pipeline.add_step(coercion.coerce_datetime(data, selected_col))
                    data[selected_col] = coercion.coerce_datetime(data, selected_col)
                elif to_type == 'Boolean':
                    def coerce_bool(data, column):
                        return data.assign(**{column: data[column].astype(bool)})

                    pipeline.add_step(coerce_bool, selected_col, func_name='data = coerce_bool(data, column)')
                    data[selected_col] = data[selected_col].astype(bool)

                st.session_state['data'] = data  # Update the session state with coerced data
                st.write('Data types updated.', data.dtypes)
                st.rerun()

        st.header('Library Selection')
        selected_library = st.selectbox(
            'Select Library',
            libraries_dict.keys()
        )

        st.header('Method Selection')
        selected_function_name = st.selectbox(
            'Select Function',
            options=libraries_dict[selected_library].keys()
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
                param_info['value'] = st.text_input(f"Enter value for {param_name}")

        if st.button('Add Step', key='add_step'):
            pipeline.add_step(selected_function_info)

        # Main Display Area
        vis_container = st.container()
        # Main window for visualization
        with vis_container:
            st.header('Visualization Section')

            # Option to select a visualization method
            vis_functions = libraries_dict['Visualization']
            selected_vis_method = st.selectbox(
                'Select Visualization Method',
                options=vis_functions.keys()
            )
            selected_vis_info = vis_functions[selected_vis_method]
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
                    [param['value'] for param in selected_vis_info['params'][1:] if
                     'value' in param])  # add other params
                st.pyplot(selected_vis_func(*args))  # pass the args list to the selected visualization function

        pipeline_container = st.container()
        with pipeline_container:
            st.header('Pipeline Architecture')

            # Create a list of tuples (index, step), where index is the step index and step is the step's func_info
            indexed_steps = list(enumerate(pipeline.steps))

            # Display each step with a button to remove it
            for index, step in indexed_steps:
                func_name = step.func_name  # Access func_name attribute directly
                col1, col2 = st.columns([4, 1])  # Adjust the ratio as needed
                with col1:
                    st.write(f'Step {index + 1}: {func_name}')
                with col2:
                    st.button(f'Remove Step {index + 1}', on_click=lambda: pipeline.remove_step(index))

            # Button to run the pipeline
            if st.button('Run Pipeline'):
                pipeline.run()
                st.write('Pipeline executed.')

        # Generate Report
        with st.expander("Report Generator"):
            report_type = st.selectbox('Select Report Type', ['Summary', 'Visual', 'Complete'])
            if st.button('Generate Report'):
                if report_type == 'Summary':
                    report = reporting.generate_summary_report(st.session_state['data'])
                    tidy_report = reporting.tidy_report(report)  # Call tidy_report to restructure the summary
                    if tidy_report:
                        st.write("## Summary Report")
                        for section, table in tidy_report.items():
                            st.write(f"### {section}")
                            st.table(table)  # Writes the data as a table
                    else:
                        st.write("No data available for summary report.")

                elif report_type == 'Visual':
                    report = reporting.generate_tidy_visual_report(st.session_state['data'])
                    if report:
                        st.write("## Visual Report")
                        for plot_type, plots in report.items():
                            st.write(f"### {plot_type}")
                            for column, plot in plots.items():
                                st.write(f"#### {column}")
                                st.pyplot(plot)  # Displays the plot
                    else:
                        st.write("No data available for visual report.")
                elif report_type == 'Complete':
                    combined_report = reporting.generate_tidy_combined_report(st.session_state['data'])
                    if combined_report:
                        st.write("## Complete Report")
                        for section, data in combined_report.items():
                            st.write(f"### {section}")
                            display_section(section, data)
                    else:
                        st.write("No data available for complete report.")
                else:
                    st.write('No report generated.')

        # Download Report`
        # with st.expander("Download Report"):
        #     # if 'pdf_report' not in st.session_state:
        #     #     st.session_state['pdf_report'] = None
        #     # elif st.session_state['pdf_report'] is None:
        #     #     st.button('Generate Report', key='generate_report',
        #     #               on_click=(lambda: st.session_state.update(
        #     #                   {'pdf_report': reporting.generate_pdf(st.session_state['data'])})))
        #     # if st.session_state['pdf_report'] is not None:
        #     #     if st.download_button('Download Report', st.session_state['pdf_report'], 'report.pdf'):
        #     #         st.write("Downloaded!")
        #     if 'pdf_report' not in st.session_state or st.session_state['pdf_report'] is None:
        #         if st.button('Generate Report', key='generate_report'):
        #             st.session_state['pdf_report'] = reporting.generate_pdf(st.session_state['data'])
        #     else:
        #         if st.download_button('Download Report', st.session_state['pdf_report'], 'report.pdf'):
        #             st.write("Downloaded!")
        with st.expander("Download Report"):
            if 'pdf_report' not in st.session_state:
                st.session_state['pdf_report'] = None

            if st.session_state['data'] is not None:
                pdf_bytes = reporting.generate_pdf(st.session_state['data'])
                st.write(f"PDF Bytes Length: {len(pdf_bytes)}")
                st.download_button(
                    label="Download PDF Report",
                    data=pdf_bytes,
                    file_name="GeneratedReport.pdf",
                    mime="application/pdf"
                )
                # btn = st.download_button('Download Report', reporting.generate_pdf(st.session_state['pdf_report']), 'report.pdf',
                #                          'application/pdf')
                # if btn:
                #     st.write("Downloaded!")
                #     st.session_state['pdf_report'] = None  # Clear the PDF from session state if needed

            if st.button('Generate PDF Report', key='generate_pdf_report'):
                pdf_bytes = reporting.generate_pdf(st.session_state['data'])
                st.session_state['pdf_report'] = pdf_bytes

    # with open('sample_data.json', 'w') as file:
    #     import json
    #     data = reporting.generate_tidy_combined_report(st.session_state['data'])
    #     json.dump(data, file, indent=4)
    # if st.button('Download Pickle File'):
    #     with open('sample_data.json', 'rb') as file:
    #         file_contents = file.read()
    #     st.download_button(label='Click to Download', data=file_contents, file_name='sample_data.pkl')
    def show_reporting():
        # Example dictionary containing different types
        my_dict = reporting.generate_tidy_combined_report(st.session_state['data'])
        dict_str = repr(my_dict)
        print(eval(dict_str.replace('\n', '')))
        print("Types used in my_dict:")

        types_used = get_types_in_dict(my_dict)
        print(type(my_dict).__name__)

        # Print the distinct types found in the dictionary
        for t in types_used:
            print(t)
    if st.button('show reporting', key='show_reporting', on_click=lambda: show_reporting()):
        pass

import types
def get_types_in_dict(d):
        types_set = set()

        def collect_types(obj):
            if isinstance(obj, types.ModuleType):
                # Handle module types (typically packages)
                types_set.add(obj.__name__)
            elif isinstance(obj, type):
                # Handle class types
                types_set.add(obj.__name__)
            elif isinstance(obj, (list, tuple)):
                # Handle lists and tuples
                for item in obj:
                    collect_types(item)
            elif isinstance(obj, dict):
                # Handle dictionaries
                for value in obj.values():
                    collect_types(value)

        for value in d.values():
            collect_types(value)

        return types_set


if __name__ == "__main__":
    render()
