from utils.financial_features import FinancialData
from utils.data_loader import DataLoader


def build_dataset():
    data = DataLoader().load_data()
    financial_data = FinancialData(data)
    return financial_data.get_data()
