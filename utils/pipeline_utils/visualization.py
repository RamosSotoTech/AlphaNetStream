# This file contains functions for visualizing data
import matplotlib
import matplotlib.pyplot as plt
import mplfinance as mpf
import seaborn as sns
import pandas as pd
from typing import Union, List, Dict, Any


def plot_heatmap(data: pd.DataFrame, columns: List[str], title="Correlation Heatmap") \
        -> matplotlib.figure.Figure:
    """
    Plots a correlation heatmap based on the given data.

    Parameters:
        data (DataFrame): The DataFrame containing the data for correlation analysis.
        columns (List[str]): The name of the column containing time data.
        title (str, optional): The title for the correlation heatmap. Defaults to "Correlation Heatmap".

    Returns:
        matplotlib.figure.Figure: The Figure object containing the correlation heatmap.
    """
    df = data[columns]
    sns.heatmap(df.corr(), annot=True, cmap='coolwarm')
    plt.title(title if title else 'Correlation Heatmap')
    fig = plt.gcf()  # Get the current figure
    return fig


def plot_pie(data: pd.DataFrame, value_column: str, title: Union[str, None] = "Pie Chart") \
        -> matplotlib.figure.Figure:
    """
    Plots a pie chart based on the given data.

    Parameters:
        data (DataFrame): The DataFrame containing the data for the pie chart.
        value_column (str): The name of the column containing the values for the pie chart.
        title (str, optional): The title for the pie chart. Defaults to "Pie Chart".

    Returns:
        matplotlib.figure.Figure: The Figure object containing the pie chart.
    """
    fig, ax = plt.subplots(figsize=(5, 5))
    data[value_column].value_counts().plot(kind='pie', autopct='%1.1f%%', ax=ax)
    ax.set_title(title if title else 'Pie Chart')
    return plt.gcf()


def plot_bar(data: pd.DataFrame, value_column: str, title: Union[str, None] = "Bar Chart") -> matplotlib.figure.Figure:
    """
    Plots a bar chart based on the given data.

    Parameters:
        data (DataFrame): The DataFrame containing the data for the bar chart.
        value_column (str): The name of the column containing the values for the bar chart.
        title (str, optional): The title for the bar chart. Defaults to "Bar Chart".

    Returns:
        matplotlib.figure.Figure: The Figure object containing the bar chart.
    """
    fig, ax = plt.subplots(figsize=(10, 5))
    data[value_column].value_counts().plot(kind='bar', ax=ax)
    ax.set_title(title if title else 'Bar Chart')
    return plt.gcf()


def plot_box(data: pd.DataFrame, columns: List[str], title: Union[str, None] = "Box Plot") -> matplotlib.figure.Figure:
    """
    Plots a box plot based on the given data.

    Parameters:
        data (DataFrame): The DataFrame containing the data for the box plot.
        columns (str): The name of the column containing the values for the box plot.
        title (str, optional): The title for the box plot. Defaults to "Box Plot".

    Returns:
        matplotlib.figure.Figure: The Figure object containing the box plot.
    """
    fig, ax = plt.subplots(figsize=(10, 5))
    df = data[columns]
    df.boxplot(ax=ax)
    ax.set_title(title if title else 'Box Plot')
    return plt.gcf()


def plot_scatter(data, columns: List[str], index_column: Union[str, None] = None,
                 title: Union[str, None] = "Scatter Plot") -> matplotlib.figure.Figure:
    """
    Plots a scatter plot based on the given data with a specified index column.

    Parameters:
        data (pd.DataFrame): The DataFrame containing the data.
        columns (list): A list of column names for the scatter plot's y-axis values.
        index_column (str, optional): The name of the column to use as the x-axis (index).
        title (str, optional): The title for the scatter plot. Defaults to "Scatter Plot".

    Returns:
        plt.Figure: The Figure object containing the scatter plot.
    """
    num_plots = len(columns)
    fig, axs = plt.subplots(1, num_plots, figsize=(10 * num_plots, 5))

    if num_plots == 1:
        axs = [axs]  # Ensure axs is a list even for a single subplot

    if index_column is None:
        index_column = data.index.name

    for i in range(num_plots):
        data.plot.scatter(x=index_column, y=columns[i], ax=axs[i])
        axs[i].set_title(f"{title} ({index_column} vs {columns[i]})")

    plt.tight_layout()
    return plt.gcf()


def plot_histogram(data: pd.DataFrame, value_column: List[str], title: Union[str, None] = "Histogram") -> matplotlib.figure.Figure:
    """
    Plots a histogram based on the given data.

    Parameters:
        data (DataFrame): The DataFrame containing the data for the histogram.
        value_column (str): The name of the column containing the values for the histogram.
        title (str, optional): The title for the histogram. Defaults to "Histogram".

    Returns:
        matplotlib.figure.Figure: The Figure object containing the histogram.
    """
    fig, ax = plt.subplots(figsize=(10, 5))
    df = data[value_column]
    df.hist(ax=ax)
    ax.set_title(title if title else 'Histogram')
    return plt.gcf()


def plot_line(data: pd.DataFrame, x_column: str, y_column: str, title: Union[str, None] = "Line Plot") -> matplotlib.figure.Figure:
    """
    Plots a line plot based on the given data.

    Parameters:
        data (DataFrame): The DataFrame containing the data for the line plot.
        x_column (str): The name of the column containing the x-axis values.
        y_column (str): The name of the column containing the y-axis values.
        title (str, optional): The title for the line plot. Defaults to "Line Plot".

    Returns:
        matplotlib.figure.Figure: The Figure object containing the line plot.
    """
    fig, ax = plt.subplots(figsize=(10, 5))
    data.plot.line(x=x_column, y=y_column, ax=ax)
    ax.set_title(title if title else 'Line Plot')
    return plt.gcf()
