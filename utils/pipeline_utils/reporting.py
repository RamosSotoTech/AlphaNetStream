# reporting.py
import inspect
from typing import Dict, Any


def generate_summary_report(data):
    """Generate a summary report."""
    pass


def generate_visual_report(data):
    """Generate a visual report."""
    pass


def export_report_to_pdf(report, filename):
    """Export report to PDF."""
    pass


def export_report_to_html(report, filename):
    """Export report to HTML."""
    pass


def get_function_info(func) -> Dict[str, Any]:
    sig = inspect.signature(func)
    params = [{'name': k, 'type': str(v.annotation), 'size': None} for k, v in sig.parameters.items()]
    return {
        'func': func,
        'params': params
    }


# List of functions
functions = [generate_summary_report, generate_visual_report, export_report_to_pdf, export_report_to_html]

# Generate function information dictionary
function_info_dict = {f.__name__: get_function_info(f) for f in functions}

reporting_functions = function_info_dict
