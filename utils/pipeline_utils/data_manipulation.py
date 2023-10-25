# data_manipulation.py
import inspect
from typing import Dict, Any


def replace_nan(data, value):
    """Replace NaN values with a specified value."""
    pass


def drop_duplicates(data):
    """Drop duplicate rows."""
    pass


def normalize(data, columns):
    """Normalize specified columns."""
    pass


def encode_categorical(data, columns):
    """Encode categorical variables."""
    pass


def impute_missing(data, columns):
    """Impute missing values."""
    pass


def feature_engineering(data):
    """Perform feature engineering."""
    pass


def feature_scaling(data, columns):
    """Perform feature scaling."""
    pass


def data_transformation(data):
    """Perform data transformation."""
    pass


def encoding_categorical(data, columns):
    """Perform categorical encoding."""
    pass


def decode_categorical(data, columns):
    """Perform categorical decoding."""
    pass


def get_function_info(func) -> Dict[str, Any]:
    sig = inspect.signature(func)
    params = [{'name': k, 'type': str(v.annotation), 'size': None} for k, v in sig.parameters.items()]
    return {
        'func': func,
        'params': params
    }


# List of functions
functions = [replace_nan, drop_duplicates, normalize, encode_categorical, impute_missing, feature_engineering,
             feature_scaling, data_transformation, encoding_categorical, decode_categorical]

# Generate function information dictionary
function_info_dict = {f.__name__: get_function_info(f) for f in functions}

manipulation_functions = function_info_dict
