import functools
from typing import Callable, Union, Dict, Any

import matplotlib.pyplot as plt

from utils.introspection import FunctionMetadata, create_executable_function, get_string_from_step_function


class Pipeline:
    def __init__(self, data=None):
        self.original_data = data
        self.intermediate_data = data  # Holds the data as it's transformed by each step
        self.steps = []
        self.current_step = 0

    def add_step(self, func_info: Union[str, Dict, Callable, FunctionMetadata], param_values: Dict[str, Any] = None, func_name: str = None):
        func_metadata = None

        if isinstance(func_info, FunctionMetadata):
            func_metadata = func_info  # If a FunctionMetadata object is provided, use it directly
        elif isinstance(func_info, str):
            func = create_executable_function(func_info)
            if func is not None:
                func_metadata = FunctionMetadata(func)
        elif isinstance(func_info, Dict):
            func = create_executable_function(func_info['source_code'])
            if func is not None:
                func_metadata = FunctionMetadata(func)
        elif callable(func_info):
            func_metadata = FunctionMetadata(func_info)

        if func_name is not None:
            func_metadata = FunctionMetadata(func_info)
            func_metadata.func_name = func_name

        if func_metadata is not None:
            if param_values is not None:
                # Update the parameter values in the FunctionMetadata object
                for param_name, value in param_values.items():
                    matching_param = next((param for param in func_metadata.params if param.name == param_name), None)
                    if matching_param is not None:
                        matching_param.value = value
                    else:
                        print(f"Warning: Parameter {param_name} is not recognized by the function {func_metadata.func_name}")

            self.steps.append(func_metadata)

    def add_column_operation(self, func, *args, **kwargs):
        wrapper = functools.wraps(func)(lambda data: func(data, *args, **kwargs))
        function_meta = FunctionMetadata(wrapper)
        function_meta.func_name = wrapper.__name__ = "data = " + func.__name__
        self.steps.append(function_meta)

    def remove_step(self, step_index):
        if 0 <= step_index < len(self.steps):
            self.steps.pop(step_index)

    def run(self):
        self.intermediate_data = self.original_data  # Reset to original data at the start of each run
        for step in self.steps:
            # Assume each function in the pipeline returns the transformed data
            self.intermediate_data = step(self.intermediate_data)

    def step_generator(self):
        self.intermediate_data = self.original_data  # Reset to original data at the start of step-by-step execution
        while self.current_step < len(self.steps):
            yield self.steps[self.current_step]
            self.current_step += 1

    def run_step_by_step(self):
        gen = self.step_generator()
        for step in gen:
            # Assume each function in the pipeline returns the transformed data
            self.intermediate_data = step(self.intermediate_data)

    def display_architecture(self):
        for i, step in enumerate(self.steps, 1):
            func_name = step.func_name  # Access func_name from FunctionMetadata object
            print(f'Step {i}: {func_name}')