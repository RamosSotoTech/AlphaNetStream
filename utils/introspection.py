import re
from enum import Enum
from typing import List, Dict, Any, Union, Callable
import inspect


def get_params_metadata(func):
    sig = inspect.signature(func)
    params = [{'name': k,
               'type': str(v.annotation),
               'default': v.default if v.default is not inspect.Parameter.empty else None,
               'kind': v.kind.name
               } for k, v in sig.parameters.items()]
    return params


def create_executable_function(code_string):
    # Create an empty dictionary to serve as the local namespace for the code
    local_vars = {}

    try:
        # Compile the code string into a code object
        compiled_code = compile(code_string, '<string>', 'exec')

        # Execute the compiled code within the local namespace
        exec(compiled_code, globals(), local_vars)

        # Extract the function name from the executed code
        func_name = next((k for k, v in local_vars.items() if callable(v)), None)
        if not func_name:
            raise ValueError("No function found in the provided code string")

        # Return the executable function
        return local_vars.get(func_name)

    except Exception as e:
        # Handle any exceptions that may occur during execution
        print(f"Error: {e}")
        return None


def execute_code_string(code_string):
    local_vars = {}
    compiled_code = compile(code_string, '<string>', 'exec')
    exec(compiled_code, globals(), local_vars)
    return local_vars  # or return local_vars.get('data') if you expect 'data' to be modified


def get_string_from_step_function(func: Callable) -> str:
    # Get the function metadata using the FunctionMetadata class
    func_metadata = FunctionMetadata(func)

    # Get the function name
    func_name = func_metadata.func_name

    # Create a list of parameter default values as strings
    param_defaults_str = [f'{param.name}={param.default}' if param.default is not None else param.name
                          for param in func_metadata.params]

    # Create a string representation of the function
    func_str = f'{func_name}({", ".join(param_defaults_str)})'

    # Return the string representation of the function
    return func_str


class FunctionMetadata:
    class ParamsMetadata:
        def __init__(self, name, type, default, kind):
            self.name = name
            self.type = type
            self.default = default
            self.value = default
            self.kind = kind

    def __init__(self, func: Union[Dict[str, Dict[str, Any]], Callable, str]):
        if inspect.isfunction(func):
            self.func = func
            self.docstring = inspect.getdoc(func)
            if hasattr(func, '__wrapped__'):
                if 'lambda' in func.__wrapped__.__name__:
                    self.func_name = func.__name__
                else:
                    self.func_name = func.__wrapped__.__name__
                    self.source_code = inspect.getsource(func.__wrapped__).strip()
                    self.line = inspect.getsourcelines(func.__wrapped__)[1]
            else:
                try:
                    self.func_name = func.__name__
                    self.source_code = inspect.getsource(func).strip()
                    self.line = inspect.getsourcelines(func)[1]
                except OSError:
                    self.source_code = None
            self.module = inspect.getmodule(func).__name__
            params_dict = get_params_metadata(func)
            self.params = [self.ParamsMetadata(**param) for param in params_dict]
            self.return_annotation = str(inspect.signature(func).return_annotation)
            self.file = inspect.getfile(func)
        elif isinstance(func, dict):
            self.func_name = func['func_name']
            self.docstring = func['docstring']
            self.source_code = func['source_code']
            self.func = create_executable_function(func['source_code'])
            self.module = func['module']
            params_dict = func['params']
            self.params = [self.ParamsMetadata(**param) for param in params_dict]
            self.return_annotation = func['return_annotation']
            self.file = func['file']
            self.line = func['line']
        elif isinstance(func, str):
            self.__init__(create_executable_function(func))

    def __call__(self, *args, use_saved_params=False, use_default_params=True, use_preset_params=True, **kwargs):
        if use_saved_params:
            # Create a dictionary of parameter names and values from the saved params
            saved_params = {param.name: param.value for param in self.params if hasattr(param, 'value')}
            return self.func(**saved_params)
        elif use_default_params:
            # Create a dictionary of parameter names and values from the default params
            default_params = {param.name: param.default for param in self.params if param.default is not None}
            return self.func(**default_params)
        elif use_preset_params:
            preset_params = {param.name: param.default for param in self.params if param.default is not None}
            preset_params.update(kwargs)
            return self.func(*args, **preset_params)

    # @classmethod
    # def from_code_string(cls, code_string):
    #     code_string = re.sub(r'^import .*$', '', code_string, flags=re.MULTILINE)
    #     code_string = re.sub(r'^from .* import .*$', '', code_string, flags=re.MULTILINE)
    #     instance = cls.__new__(cls)
    #     func_name = code_string.strip().split('\n')[-1]
    #     instance.func_name = func_name
    #     instance.source_code = code_string
    #     instance.func = create_executable_function(code_string)
    #     instance.docstring = inspect.getdoc(instance.func)
    #     instance.module = "None"
    #     instance.__init__(create_executable_function(code_string))
    #     return instance
    @classmethod
    def from_code_string(cls, code_string):
        code_string = re.sub(r'^import .*$', '', code_string, flags=re.MULTILINE)
        code_string = re.sub(r'^from .* import .*$', '', code_string, flags=re.MULTILINE)
        func_name = code_string.strip().split('\n')[-1]
        instance = cls(create_executable_function(code_string))
        instance.func_name = func_name
        instance.source_code = code_string
        return instance

    def to_dict(self):
        return {
            'func_name': self.func_name,
            'func': self.func,
            'docstring': self.docstring,
            'source_code': self.source_code,
            'module': self.module,
            'params': self.params,
            'return_annotation': self.return_annotation,
            'file': self.file,
            'line': self.line
        }


def get_function_info(func) -> Dict[str, Any]:
    """Gather information about a function."""
    return {
        'func_name': func.__name__,
        'func': func,
        'docstring': inspect.getdoc(func),
        'source_code': inspect.getsource(func).strip(),
        'module': inspect.getmodule(func).__name__,
        'params': get_params_metadata(func),
        'return_annotation': str(inspect.signature(func).return_annotation),
        'file': inspect.getfile(func),
        'line': inspect.getsourcelines(func)[1]
    }


def get_module_functions_info(module) -> Dict[str, Dict[str, Any]]:
    """Get information about all functions in a module."""
    function_dict = {}
    for name, func in inspect.getmembers(module, inspect.isfunction):
        function_info = get_function_info(func)
        function_dict[name] = function_info
    return function_dict


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
