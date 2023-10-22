import pandas as pd
import os
import re


class DataLoader:
    def __init__(self, directory='financial_data'):
        self.directory = directory

    def load_data(self):
        # List all files in the directory
        files = [f for f in os.listdir(self.directory) if f.endswith('_data.csv')]

        # Organize files by interval
        interval_files = {}
        for file in files:
            # Extract interval from the file name using regex
            interval_match = re.search(r'_(\w+)_data\.csv', file)
            if interval_match:
                interval = interval_match.group(1)
                if interval not in interval_files:
                    interval_files[interval] = []
                interval_files[interval].append(file)

        # Load and concatenate datasets for each interval
        interval_data = {}
        for interval, file_list in interval_files.items():
            datasets = []
            for file in file_list:
                file_path = os.path.join(self.directory, file)
                df = pd.read_csv(file_path)
                datasets.append(df)
            # Concatenate all datasets for this interval into a single DataFrame
            interval_data[interval] = pd.concat(datasets, ignore_index=True)

        return interval_data

