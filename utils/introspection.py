from enum import Enum
from typing import List, Dict, Any, Union
import inspect


def get_function_info(func) -> Dict[str, Any]:
    """Gather information about a function."""
    sig = inspect.signature(func)
    params = [{'name': k,
               'type': str(v.annotation),
               'default': v.default if v.default is not inspect.Parameter.empty else None,
               'kind': v.kind.name
               } for k, v in sig.parameters.items()]

    return {
        'func_name': func.__name__,
        'docstring': inspect.getdoc(func),
        'source_code': inspect.getsource(func).strip(),
        'module': inspect.getmodule(func).__name__,
        'params': params,
        'return_annotation': str(sig.return_annotation),
        'file': inspect.getfile(func),
        'line': inspect.getsourcelines(func)[1]
    }


def get_module_functions_info(module) -> List[Dict[str, Any]]:
    """Get information about all functions in a module."""
    function_list = []
    for name, func in inspect.getmembers(module, inspect.isfunction):
        function_info = get_function_info(func)
        function_list.append(function_info)
    return function_list


def get_class_info(cls) -> Dict[str, Any]:
    """Gather information about a class and its methods."""
    methods = []
    for name, method in inspect.getmembers(cls, inspect.isfunction):
        method_info = get_function_info(method)
        methods.append(method_info)
    return {
        'class_name': cls.__name__,
        'docstring': inspect.getdoc(cls),
        'module': inspect.getmodule(cls).__name__,
        'methods': methods
    }


def get_module_classes_info(module) -> List[Dict[str, Any]]:
    """Get information about all classes in a module."""
    class_list = []
    for name, cls in inspect.getmembers(module, inspect.isclass):
        class_info = get_class_info(cls)
        class_list.append(class_info)
    return class_list


def get_module_info(module) -> Dict[str, Union[List[Dict[str, Any]], List[Dict[str, Any]]]]:
    """Get information about all functions and classes in a module."""
    return {
        'functions': get_module_functions_info(module),
        'classes': get_module_classes_info(module)
    }


# Function to check if a type is an Enum
def is_enum_type(value):
    return issubclass(value, Enum)


# Function to populate combo box based on function signature
def populate_combo_box_from_function_signature(func):
    signature = inspect.signature(func)
    for param_name, param in signature.parameters.items():
        param_type = param.annotation
        if is_enum_type(param_type):
            option = st.selectbox(
                f"Choose an option for {param_name}:",

            )
            return param_type[option]

# Example Usage:

# For functions in a specific module
# import my_functions  # Replace this with the actual module you want to inspect
# function_info = get_module_functions_info(my_functions)
# print(function_info)

# For classes in a specific module
# class_info = get_module_classes_info(my_functions)
# print(class_info)

# For both functions and classes
# module_info = get_module_info(my_functions)
# print(module_info)
