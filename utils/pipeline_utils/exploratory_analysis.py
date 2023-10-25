# exploratory_analysis.py
import inspect
from typing import Dict, Any


def summarize(data):
    """Provide summary statistics."""
    pass


def find_missing_values(data):
    """Identify missing values."""
    pass


def correlation_matrix(data):
    """Generate a correlation matrix."""
    pass


def outlier_detection(data, method='z_score'):
    """Detect outliers using specified method."""
    pass


def descriptive_statistics(data):
    """Generate descriptive statistics."""
    pass


def distribution_analysis(data):
    """Generate a distribution plot."""
    pass


def pairwise_correlation(data):
    """Generate pairwise correlation plots."""
    pass


def trend_analysis(data):
    """Generate a trend analysis plot."""
    pass


def anomaly_detection(data):
    """Detect anomalies."""
    pass


def feature_importance(data):
    """Generate a feature importance plot."""
    pass


def frequency_analysis(data):
    """Generate a frequency analysis plot."""
    pass


def cross_tabulation(data):
    """Generate a cross tabulation table."""
    pass


def get_function_info(func) -> Dict[str, Any]:
    sig = inspect.signature(func)
    params = [{'name': k, 'type': str(v.annotation), 'size': None} for k, v in sig.parameters.items()]
    return {
        'func': func,
        'params': params
    }


# List of functions
functions = [summarize, find_missing_values, correlation_matrix, outlier_detection, descriptive_statistics,
             distribution_analysis, pairwise_correlation, trend_analysis, anomaly_detection, feature_importance,
             frequency_analysis, cross_tabulation]

# Generate function information dictionary
function_info_dict = {f.__name__: get_function_info(f) for f in functions}

exploration_functions = function_info_dict
