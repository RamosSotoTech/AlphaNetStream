# exploratory_analysis.py
from typing import Union, List

import numpy as np
import pandas as pd
from scipy.stats import stats


def summarize(data: pd.DataFrame, columns: Union[List[str], None] = None) -> pd.DataFrame:
    """Provide summary statistics."""
    if columns is None:
        return data.describe()
    df = data[columns]
    return df.describe()


def find_missing_values(data: pd.DataFrame, columns: Union[List[str], None] = None) -> pd.DataFrame:
    """Identify missing values."""
    if columns is None:
        return data[data.isnull().any(axis=1)]
    df = data[columns]
    return data[df.isnull().any(axis=1)]


def correlation_matrix(data: pd.DataFrame, columns: Union[List[str], None] = None) -> pd.DataFrame:
    """Generate a correlation matrix."""
    if columns is None:
        return data.corr()
    df = data[columns]
    return df.corr()


def outlier_detection(data: pd.DataFrame, columns: Union[List[str], None] = None, method: str = 'iqr') -> pd.DataFrame:
    """Detect outliers."""
    if columns is None:
        return data
    df = data[columns]
    if method == 'iqr':
        q1 = df.quantile(0.25)
        q3 = df.quantile(0.75)
        iqr = q3 - q1
        return df[((df < (q1 - 1.5 * iqr)) | (df > (q3 + 1.5 * iqr))).any(axis=1)]
    elif method == 'zscore':
        z = np.abs(stats.zscore(df))
        return df[(z > 3).any(axis=1)]
    else:
        raise ValueError(f'Invalid method: {method}')


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
