import streamlit as st
import pandas as pd

# Assuming st.session_state.data is already loaded with data
# Mock data for demonstration
# todo: Replace with actual data or remove
st.session_state.data = pd.DataFrame({
    'A': [1, 2, 3, 4],
    'B': [5, 6, 7, 8],
    'C': [9, 10, 11, 12]
})


def analysis_type_selection():
    analysis_types = ["Univariate", "Bivariate", "Multivariate", "Feature Engineering"]
    selected_analysis = st.selectbox("Select Analysis Type", analysis_types)
    return selected_analysis


def feature_selection():
    available_features = st.session_state.data.columns.tolist()
    selected_features = st.multiselect("Select Features", available_features)
    return selected_features


def explore_data_univariate(features):
    # Univariate analysis implementation here
    st.write(f"Univariate analysis for {features}")


def explore_data_bivariate(features):
    # Bivariate analysis implementation here
    st.write(f"Bivariate analysis for {features}")


def explore_data_multivariate(features):
    # Multivariate analysis implementation here
    st.write(f"Multivariate analysis for {features}")


def feature_engineering(features):
    # Feature engineering implementation here
    st.write(f"Feature engineering for {features}")


def explore_data():
    st.header("Step 2: Explore Data")
    selected_analysis = analysis_type_selection()
    selected_features = feature_selection()

    if st.button("Analyze", key="analyze"):
        if selected_analysis == "Univariate":
            explore_data_univariate(selected_features)
        elif selected_analysis == "Bivariate":
            explore_data_bivariate(selected_features)
        elif selected_analysis == "Multivariate":
            explore_data_multivariate(selected_features)
        elif selected_analysis == "Feature Engineering":
            feature_engineering(selected_features)


if __name__ == '__main__':
    explore_data()
