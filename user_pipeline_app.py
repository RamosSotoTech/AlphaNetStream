import streamlit as st
import pandas as pd
import requests
import io
from explore_data import explore_data


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


def pipeline_process():

    tab1, tab2, tab3, tab4, tab5 = st.tabs(["Load Data", "Explore Data", "Clean Data", "Visualize Data", "Generate Report"])

    # Load Data Tab
    with tab1:
        load_data()

    # Explore Data Tab
    with tab2:
        # Assuming st.session_state.data is already loaded with data
        explore_data()

    # Clean Data Tab
    with tab3:
        clean_data()

    # Visualize Data Tab
    with tab4:
        visualize_data()

    # Generate Report Tab
    with tab5:
        generate_report()


if __name__ == "__main__":
    pipeline_process()
