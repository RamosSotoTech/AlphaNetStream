# reporting.py
import numpy as np
import streamlit as st
from typing import Dict, Union, Any, List
import statsmodels.api as sm
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import inch

from scipy.stats import normaltest
import matplotlib
import pandas as pd
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Image, Spacer
import matplotlib.pyplot as plt
import io

from utils.pipeline_utils.visualization import plot_pie, plot_bar, plot_box, plot_heatmap, plot_histogram, plot_scatter, \
    plot_line, plot_density, plot_violin, plot_count


def generate_summary_report(data: pd.DataFrame) -> Union[Dict[str, Dict[str, Any]], None]:
    """Generate an extended summary report."""
    if not isinstance(data, pd.DataFrame) or data.empty:
        return None

    # Separate numeric, categorical, and datetime data
    numeric_data = data.select_dtypes(include=['float64', 'int64'])
    categorical_data = data.select_dtypes(exclude=['float64', 'int64', 'datetime'])
    datetime_data = data.select_dtypes(include=['datetime'])

    # IQR method for outlier detection on numeric data
    q1 = numeric_data.quantile(0.25)
    q3 = numeric_data.quantile(0.75)
    iqr = q3 - q1

    # Prepare summaries for categorical data
    categorical_summary = {
        col: {
            'unique_values': categorical_data[col].nunique(),
            'top_value': categorical_data[col].mode()[0] if not categorical_data[col].mode().empty else None,
            'top_value_frequency': categorical_data[col].value_counts().values[0] if not categorical_data[
                col].value_counts().empty else None,
            'value_counts': categorical_data[col].value_counts().to_dict()
        }
        for col in categorical_data.columns
    }

    # Prepare summaries for datetime data
    datetime_summary = {
        col: {
            'min_date': datetime_data[col].min(),
            'max_date': datetime_data[col].max()
        }
        for col in datetime_data.columns
    }

    # Calculate multicollinearity for numeric columns using VIF (Variance Inflation Factor)
    vif_data = sm.add_constant(numeric_data)

    if np.any(np.isnan(vif_data)) or np.all(np.isfinite(vif_data)) is False:
        # todo: add comment for the reporting documentation, that this is a workaround for the VIF calculation
        print("vif_data contains NaN or inf values.")
        vif_data = vif_data.replace([np.inf, -np.inf], np.nan).dropna(axis=1)
    vif = pd.DataFrame()
    vif["Variable"] = vif_data.columns
    vif["VIF"] = [sm.OLS(vif_data[col], vif_data.drop(columns=[col])).fit().rsquared for col in vif_data.columns]
    vif = vif.drop(0)  # Remove the constant column
    vif = vif.set_index('Variable').to_dict()['VIF']

    # Data distribution normality tests for numeric columns
    normality_tests = {}
    for col in numeric_data.columns:
        _, p_value = normaltest(numeric_data[col])
        normality_tests[col] = {'p_value': p_value, 'is_normal': p_value > 0.05}

    report = {
        'summary': {
            'numeric': {
                **numeric_data.describe().to_dict(),
                'skewness': numeric_data.skew().to_dict(),
                'kurtosis': numeric_data.kurt().to_dict(),
                'zero_values_count': (numeric_data == 0).sum().to_dict(),
                'multicollinearity': vif  # Include VIF for multicollinearity
            },
            'categorical': categorical_summary,
            'datetime': datetime_summary
        },
        'missing_values': data.isnull().sum().to_dict(),
        'correlation': numeric_data.corr().to_dict(),
        'outliers': ((numeric_data < (q1 - 1.5 * iqr)) | (numeric_data > (q3 + 1.5 * iqr))).sum().to_dict(),
        'data_types': data.dtypes.to_dict(),
        'data_shape': data.shape,
        'memory_usage': data.memory_usage(deep=True).to_dict(),
        'normality_tests': normality_tests  # Include normality test results
    }

    return report


def generate_visual_report(data: pd.DataFrame) -> Union[Dict[str, Dict[str, matplotlib.figure.Figure]], None]:
    """Generate a visual report."""
    if not isinstance(data, pd.DataFrame) or data.empty:
        return None

    report = {
        'pie_charts': {},
        'bar_charts': {},
        'box_plots': {},
        'correlation_heatmaps': {},
        'scatter_plots': {},
        'histograms': {},
        'line_plots': {}
    }

    numeric_columns = data.select_dtypes(include=['float64', 'int64']).columns.tolist()
    categorical_columns = data.select_dtypes(exclude=['float64', 'int64', 'datetime']).columns.tolist()
    datetime_columns = data.select_dtypes(include=['datetime']).columns.tolist()

    # For categorical columns
    for column in categorical_columns:
        report['pie_charts'][column] = plot_pie(data, column)
        report['bar_charts'][column] = plot_bar(data, column)

    # For numeric columns
    if len(numeric_columns) > 0:
        report['box_plots']['All'] = plot_box(data, numeric_columns)
        report['histograms']['All'] = plot_histogram(data, numeric_columns)
        report['correlation_heatmaps']['All'] = plot_heatmap(data, numeric_columns)

    # For datetime vs numeric columns
    for date_col in datetime_columns:
        for num_col in numeric_columns:
            key = f'{date_col}_vs_{num_col}'
            report['scatter_plots'][key] = plot_scatter(data, [num_col], index_column=date_col)

    # For numeric vs numeric columns
    for i, col1 in enumerate(numeric_columns):
        for col2 in numeric_columns[i + 1:]:
            key = f'{col1}_vs_{col2}'
            report['scatter_plots'][key] = plot_scatter(data, [col2], index_column=col1)
            report['line_plots'][key] = plot_line(data, col1, col2)

    return report


def tidy_report(report: Dict[str, Any]) -> Dict[str, pd.DataFrame]:
    """Restructures the extended summary report for better display."""
    tidy_report = {}

    if 'summary' in report and report['summary']:
        summary = report['summary']
        for data_type, metrics in summary.items():
            if data_type == 'numeric':
                for metric, values in metrics.items():
                    tidy_df = pd.DataFrame(values.items(), columns=['Column', metric])
                    tidy_report[f'Summary - Numeric - {metric}'] = tidy_df

    if 'missing_values' in report and report['missing_values']:
        missing_values = report['missing_values']
        tidy_report['Missing Values'] = pd.DataFrame(missing_values.items(), columns=['Column', 'Count'])

    if 'correlation' in report and report['correlation']:
        correlation = report['correlation']
        corr_df = pd.DataFrame(correlation)
        # Add p-values to the correlation matrix
        if 'correlation_pvalues' in report and report['correlation_pvalues']:
            corr_pvalues = report['correlation_pvalues']
            corr_df = corr_df.astype(str) + ' (p=' + corr_pvalues.astype(str) + ')'
        tidy_report['Correlation'] = corr_df

    if 'outliers' in report and report['outliers']:
        outliers = report['outliers']
        tidy_report['Outliers'] = pd.DataFrame(outliers.items(), columns=['Column', 'Count'])

    if 'data_types' in report and report['data_types']:
        data_types = report['data_types']
        tidy_report['Data Types'] = pd.DataFrame(data_types.items(), columns=['Column', 'Type'])

    if 'data_shape' in report and report['data_shape']:
        data_shape = report['data_shape']
        tidy_report['Data Shape'] = pd.DataFrame({'Rows': [data_shape[0]], 'Columns': [data_shape[1]]})

    if 'memory_usage' in report and report['memory_usage']:
        memory_usage = report['memory_usage']
        tidy_report['Memory Usage'] = pd.DataFrame(memory_usage.items(), columns=['Column', 'Bytes'])

    # Check if all dictionaries are empty and report as "Empty" if they are
    if all(not report[key] for key in
           ['summary', 'missing_values', 'correlation', 'outliers', 'data_types', 'data_shape', 'memory_usage']):
        tidy_report['Status'] = pd.DataFrame({'Message': ['Empty']})

    # Include multicollinearity (VIF) if available
    if 'summary' in report and report['summary'] and 'numeric' in report['summary']:
        numeric_summary = report['summary']['numeric']
        if 'multicollinearity' in numeric_summary:
            multicollinearity = numeric_summary['multicollinearity']
            tidy_report['Multicollinearity (VIF)'] = pd.DataFrame(multicollinearity.items(),
                                                                  columns=['Variable', 'VIF'])

    # Include normality test results if available
    if 'normality_tests' in report and report['normality_tests']:
        normality_tests = report['normality_tests']
        normality_data = []

        for col, result in normality_tests.items():
            is_normal = result.get('is_normal', False)
            p_value = result.get('p_value', None)
            normality_data.append([is_normal, p_value])

        normality_df = pd.DataFrame(normality_data, columns=['Is_Normal', 'P_Value'])
        tidy_report['Normality Tests'] = normality_df

    # Include summary statistics by group (for categorical values) if available
    if 'categorical_summary_by_group' in report and report['categorical_summary_by_group']:
        categorical_summary_by_group = report['categorical_summary_by_group']
        for group, summary in categorical_summary_by_group.items():
            group_df = pd.DataFrame(summary.items(), columns=['Column', 'Summary'])
            tidy_report[f'Summary - Categorical - Group: {group}'] = group_df

    return tidy_report


def generate_tidy_visual_report(data: pd.DataFrame) -> Union[
    Dict[str, Dict[str, Union[matplotlib.figure.Figure, Dict[str, matplotlib.figure.Figure]]]], None]:
    """Generate an extended tidy visual report."""
    if not isinstance(data, pd.DataFrame) or data.empty:
        return None

    tidy_report = {
        'pie_charts': {},
        'bar_charts': {},
        'box_plots': {},
        'correlation_heatmaps': {},
        'scatter_plots': {},
        'line_plots': {},
        'violin_plots': {},
        'pair_plots': {},
        'count_plots': {},
        'density_plots': {}
    }

    numeric_columns = data.select_dtypes(include=['float64', 'int64']).columns.tolist()
    categorical_columns = data.select_dtypes(exclude=['float64', 'int64', 'datetime']).columns.tolist()
    datetime_columns = data.select_dtypes(include=['datetime']).columns.tolist()

    # For categorical columns
    tidy_report['pie_charts'] = {}
    tidy_report['bar_charts'] = {}
    tidy_report['count_plots'] = {}

    for column in categorical_columns:
        tidy_report['pie_charts'][column] = plot_pie(data, column)
        tidy_report['bar_charts'][column] = plot_bar(data, column)
        tidy_report['count_plots'][column] = plot_count(data, column)

    # For numeric columns
    tidy_report['box_plots'] = {}
    tidy_report['histograms'] = {}
    tidy_report['correlation_heatmaps'] = {}
    tidy_report['violin_plots'] = {}
    tidy_report['density_plots'] = {}

    if len(numeric_columns) > 0:
        tidy_report['box_plots']['All'] = plot_box(data, numeric_columns)
        tidy_report['histograms']['All'] = plot_histogram(data, numeric_columns)
        tidy_report['correlation_heatmaps']['All'] = plot_heatmap(data, numeric_columns)

        # Update the tidy report with violin and density plots
        violin_plots = plot_violin(data, numeric_columns)
        density_plots = plot_density(data, numeric_columns)

        for col, fig in violin_plots.items():
            tidy_report['violin_plots'][col] = fig

        for col, fig in density_plots.items():
            tidy_report['density_plots'][col] = fig

    # For datetime vs numeric columns
    tidy_report['scatter_plots'] = {}

    for date_col in datetime_columns:
        for num_col in numeric_columns:
            key = f'{date_col}_vs_{num_col}'
            tidy_report['scatter_plots'][key] = plot_scatter(data, [num_col], index_column=date_col)

    # For numeric vs numeric columns
    tidy_report['scatter_plots'] = {}
    tidy_report['line_plots'] = {}

    for i, col1 in enumerate(numeric_columns):
        for col2 in numeric_columns[i + 1:]:
            scatter_key = f'{col1}_vs_{col2}'
            line_key = f'{col1}_line_{col2}'
            tidy_report['scatter_plots'][scatter_key] = plot_scatter(data, [col2], index_column=col1)
            tidy_report['line_plots'][line_key] = plot_line(data, col1, col2)

    return tidy_report


def generate_tidy_combined_report(data: pd.DataFrame) -> Union[Dict[str, Any], None]:
    """Generate a tidy combined report."""
    if not isinstance(data, pd.DataFrame) or data.empty:
        return None

    # Generate summary and visual reports
    summary_report = generate_summary_report(data)
    visual_report = generate_visual_report(data)

    # Tidy the reports
    tidy_summary_report = tidy_report(summary_report) if summary_report is not None else {}
    tidy_visual_report = generate_tidy_visual_report(data) if visual_report is not None else {}

    # Organize the combined report
    tidy_combined_report = {
        'general_info': {
            'data_shape': tidy_summary_report.get('Data Shape'),
            'data_types': tidy_summary_report.get('Data Types'),
            'memory_usage': tidy_summary_report.get('Memory Usage')
        },
        'summary_statistics': {
            'numeric_summary': {key: value for key, value in tidy_summary_report.items() if 'Summary - Numeric' in key},
            'categorical_summary': {key: value for key, value in tidy_summary_report.items() if
                                    'Summary - Categorical' in key},
            'datetime_summary': tidy_summary_report.get('summary', {}).get('datetime'),
        },
        'distributions': {
            'normality_tests': tidy_summary_report.get('Normality Tests'),
            'box_plots': tidy_visual_report.get('box_plots'),
            'histograms': tidy_visual_report.get('histograms'),
            'density_plots': tidy_visual_report.get('density_plots'),
            'violin_plots': tidy_visual_report.get('violin_plots')
        },
        'relationships': {
            'correlation': tidy_summary_report.get('Correlation'),
            'correlation_heatmaps': tidy_visual_report.get('correlation_heatmaps'),
            'scatter_plots': tidy_visual_report.get('scatter_plots'),
            'line_plots': tidy_visual_report.get('line_plots')
        },
        'categorical_analysis': {
            'pie_charts': tidy_visual_report.get('pie_charts'),
            'bar_charts': tidy_visual_report.get('bar_charts'),
            'count_plots': tidy_visual_report.get('count_plots')
        },
        'outliers_and_missing_values': {
            'outliers': tidy_summary_report.get('Outliers'),
            'missing_values': tidy_summary_report.get('Missing Values')
        },
        'multicollinearity': tidy_summary_report.get('Multicollinearity (VIF)')
    }

    return tidy_combined_report


def save_fig_to_bytes(fig):
    """Save a Matplotlib figure to bytes."""
    buf = io.BytesIO()
    fig.savefig(buf, format='png')
    buf.seek(0)
    return buf


def generate_pdf(data: dict):

    combined_data = generate_tidy_combined_report(data)

    buffer = io.BytesIO()
    pdf = SimpleDocTemplate(buffer, pagesize=A4)
    elements = []

    styles = getSampleStyleSheet()
    styleN = styles["BodyText"]
    styleH = styles["Heading1"]

    # Table of Contents
    elements.append(Paragraph('Table of Contents', styleH))
    elements.append(Spacer(1, 0.2 * inch))

    # Helper function to add DataFrames as tables
    def add_dataframe_to_elements(df: pd.DataFrame, description: str = ""):
        if description:
            elements.append(Paragraph(description, styleN))
        table_data = [df.columns.tolist()] + df.values.tolist()
        t = Table(table_data)
        t.setStyle(TableStyle([
            # Add more styling here
        ]))
        elements.append(t)
        elements.append(Spacer(1, 0.2 * inch))

    # Helper function to add Figures as images
    def add_figure_to_elements(fig, description: str = ""):
        if description:
            elements.append(Paragraph(description, styleN))
        buf = save_fig_to_bytes(fig)
        elements.append(Image(buf, width=400, height=300))
        elements.append(Spacer(1, 0.2 * inch))

    elements.append(Paragraph("Data Analysis Report", styleH))
    elements.append(Spacer(1, 0.2 * inch))

    for section, section_data in combined_data.items():
        elements.append(Paragraph(section, styleH))
        if section == "general_info":
            elements.append(Paragraph("This section provides general information about the dataset.", styleN))

        if section == "summary_statistics":
            elements.append(Paragraph("This section provides summary statistics of the dataset.", styleN))

        if isinstance(section_data, dict):
            for subsection, subsection_data in section_data.items():
                elements.append(Paragraph(subsection, styleN))

                if isinstance(subsection_data, dict):
                    for key, value in subsection_data.items():
                        if isinstance(value, pd.DataFrame):
                            add_dataframe_to_elements(value, f"This table pertains to {key}.")
                        elif isinstance(value, plt.Figure):
                            add_figure_to_elements(value, f"This figure pertains to {key}.")
                elif isinstance(subsection_data, pd.DataFrame):
                    add_dataframe_to_elements(subsection_data)
                elif isinstance(subsection_data, plt.Figure):
                    add_figure_to_elements(subsection_data)

        elif isinstance(section_data, pd.DataFrame):
            add_dataframe_to_elements(section_data)
        elif isinstance(section_data, plt.Figure):
            add_figure_to_elements(section_data)

        elements.append(Spacer(1, 0.2 * inch))

    pdf.build(elements)
    pdf_bytes = buffer.getvalue()
    buffer.close()

    return pdf_bytes

def export_report_to_html(report: Dict[str, Dict[str, Any]], filename: str, title: str = 'Report') \
        -> Union[None, ValueError]:
    """Export a report to HTML."""
    if report is None:
        return None

    if filename.endswith('.pdf'):
        filename = filename.replace('.pdf', '.html')

    from weasyprint import HTML
    html_report = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>{title}</title>
    </head>
    <body>
        <h1>{title}</h1>
        <h2>Summary Report</h2>
        <p>Data Shape: {str(report['data_shape'])}</p>
        <p>Data Types: {str(report['data_types'])}</p>
        <p>Missing Values: {str(report['missing_values'])}</p>
        <p>Outliers: {str(report['outliers'])}</p>
        <p>Summary Statistics: {str(report['summary'])}</p>
        <p>Correlation Matrix: {str(report['correlation'])}</p>
    </body>
    </html>
    """
    html = HTML(string=html_report)
    html.write_pdf(filename)
