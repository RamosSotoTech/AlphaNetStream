from utils.pipeline_utils import data_manipulation, exploratory_analysis, reporting, visualization


class Pipeline:
    def __init__(self):
        self.steps = []
        self.current_step = 0

    def add_step(self, func_info):
        self.steps.append(func_info)

    def run(self):
        for step in self.steps:
            func = step['func']
            args = [param['value'] for param in step['params'] if 'value' in param]
            func(*args)

    def display_architecture(self):
        for i, step in enumerate(self.steps, 1):
            func_name = step['func'].__name__
            print(f'Step {i}: {func_name}')

    def step_generator(self):
        while self.current_step < len(self.steps):
            yield self.steps[self.current_step]
            self.current_step += 1

    def run_step_by_step(self):
        gen = self.step_generator()
        for step in gen:
            step()
