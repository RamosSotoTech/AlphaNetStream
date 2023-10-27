# reporting.py
from typing import Dict, Union, Any

import matplotlib
import pandas as pd

from utils.pipeline_utils.visualization import plot_pie, plot_bar, plot_box, plot_heatmap


def generate_summary_report(data: pd.DataFrame) -> Union[Dict[str, Dict[str, Any]], None]:
    """Generate a summary report."""
    if data is None:
        return None

    # IQR method for outlier detection
    q1 = data.quantile(0.25)
    q3 = data.quantile(0.75)
    iqr = q3 - q1

    report = {'summary': data.describe().to_dict(), 'missing_values': data.isnull().sum().to_dict(),
              'correlation': data.corr().to_dict(),
              'outliers': ((data < (q1 - 1.5 * iqr)) | (data > (q3 + 1.5 * iqr))).sum().to_dict(),
              'data_types': data.dtypes.to_dict(), 'data_shape': data.shape}

    return report


def generate_visual_report(data: pd.DataFrame) -> Union[Dict[str, Dict[str, matplotlib.figure.Figure]], None]:
    """Generate a visual report."""
    if data is None:
        return None

    report = {'pie_charts': {}, 'bar_charts': {}, 'box_plots': {}, 'correlation_heatmaps': {}}

    for column in data.columns:
        if data[column].dtype == 'object':
            report['pie_charts'][column] = plot_pie(data, column)
            report['bar_charts'][column] = plot_bar(data, column)
        else:
            report['box_plots'][column] = plot_box(data, column)
            report['correlation_heatmaps'][column] = plot_heatmap(data, column)

    return report


def export_report_to_pdf(report: Dict[str, Dict[str, Any]], filename: str) -> Union[None, ValueError]:
    """Export a report to PDF."""
    if report is None:
        return None

    from fpdf import FPDF
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font('Arial', 'B', 16)
    pdf.cell(40, 10, 'Summary Report')
    pdf.set_font('Arial', '', 12)
    pdf.cell(40, 10, 'Data Shape: ' + str(report['data_shape']))
    pdf.cell(40, 10, 'Data Types: ' + str(report['data_types']))
    pdf.cell(40, 10, 'Missing Values: ' + str(report['missing_values']))
    pdf.cell(40, 10, 'Outliers: ' + str(report['outliers']))
    pdf.cell(40, 10, 'Summary Statistics: ' + str(report['summary']))
    pdf.cell(40, 10, 'Correlation Matrix: ' + str(report['correlation']))

    if filename.endswith('.pdf'):
        pdf.output(filename)
    elif filename.endswith('.html'):
        pdf.output(filename)
    elif filename.endswith('.json'):
        pdf.output(filename)
    elif '.' not in filename:
        pdf.output(filename + '.pdf')
    else:
        raise ValueError(f'Invalid file format: {filename}')


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
