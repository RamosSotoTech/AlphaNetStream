from random import sample
from random import seed

import yfinance as yf

import pandas as pd
from tqdm import tqdm
import re


def moving_average(data, window):
    return data['Close'].rolling(window=window).mean()


def rsi(data, window):
    delta = data['Close'].diff(1)
    gain = (delta.where(delta > 0, 0)).rolling(window=window).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=window).mean()
    rs = gain / loss
    return 100 - (100 / (1 + rs))


def macd(data, short_window, long_window, signal_window):
    short_ema = data['Close'].ewm(span=short_window, adjust=False).mean()
    long_ema = data['Close'].ewm(span=long_window, adjust=False).mean()
    macd = short_ema - long_ema
    signal = macd.ewm(span=signal_window, adjust=False).mean()
    return macd, signal


def get_sp500_constituents():
    url = "https://en.wikipedia.org/wiki/List_of_S%26P_500_companies"
    tables = pd.read_html(url)
    sp500_table = tables[0]  # The first table on the page is the list of S&P 500 companies
    tickers = sp500_table['Symbol'].tolist()
    return tickers


def download_ticker_data(symbol, period="5y", start=None, end=None, interval="1m", ma_windows=None,
                         rsi_window=14, macd_windows=(12, 26, 9)):
    stock_info = StockInfo(symbol)
    data = stock_info.extract_features(period=period, start=start, end=end, interval=interval,ma_windows=ma_windows,
                                       rsi_window=rsi_window, macd_windows=macd_windows)

    # Add a column to identify the stock symbol in the dataset
    cleaned_symbol = re.sub(r'[^a-zA-Z]', '', symbol)
    data['Symbol'] = cleaned_symbol

    # Save the data to a CSV file for this symbol
    file_name = f'financial_data/{cleaned_symbol}_{interval}_data.csv'
    data.to_csv(file_name)
    return data


def download_multiple_tickers(symbols, period="5y", start=None, end=None, interval='1m', ma_windows=None,
                              rsi_window=None, macd_windows=None):
    # Initialize tqdm progress bar
    progress_bar = tqdm(total=len(symbols), desc="Downloading Data", unit="stock")

    for symbol in symbols:
        download_ticker_data(symbol, period=period, start=start, end=end, interval=interval, ma_windows=ma_windows,
                             rsi_window=rsi_window, macd_windows=macd_windows)
        # Update the progress bar
        progress_bar.update(1)

    # Close the progress bar
    progress_bar.close()


# To get a single dataset with a group of symbols from Yahoo Finance
def build_dataset(num_samples=None, seeded=False, custom_symbols=None, start=None, end=None,
                  period="5y", ma_windows=None, rsi_window=14, macd_windows=(12, 26, 9)):
    symbols = custom_symbols if custom_symbols else get_sp500_constituents()
    combined_data = []

    if num_samples is None:
        num_samples = len(symbols)

    if num_samples > len(symbols):
        raise ValueError(f"Number of samples cannot be greater than the number of symbols ({len(symbols)}).")
    elif num_samples < 1:
        raise ValueError("Number of samples cannot be less than 1.")
    elif seeded:
        seed(42)
        selected_symbols = sample(symbols, num_samples)
    else:
        selected_symbols = sample(symbols, num_samples)

    # Initialize tqdm progress bar
    progress_bar = tqdm(total=num_samples, desc="Building Dataset", unit="stock")

    text_features = {}
    for symbol in selected_symbols:
        stock_info = StockInfo(symbol)
        data = stock_info.extract_features(period=period, start=start, end=end, ma_windows=ma_windows,
                                           rsi_window=rsi_window, macd_windows=macd_windows)

        # Add a column to identify the stock symbol in the combined dataset
        cleaned_symbol = re.sub(r'[^a-zA-Z]', '', symbol)
        data['Symbol'] = cleaned_symbol

        # Extract text features
        text_features[cleaned_symbol] = stock_info.extract_text_features()

        # Add the data to the list of dataframes
        combined_data.append(data)
        # Update the progress bar
        progress_bar.update(1)

    # Close the progress bar
    progress_bar.close()

    # Concatenate all dataframes into a single dataframe
    combined_df = pd.concat(combined_data, ignore_index=True)

    return combined_df, text_features


class StockInfo:

    def __init__(self, ticker_symbol):
        self.ticker_symbol = ticker_symbol
        self.ticker = yf.Ticker(ticker_symbol)

    def get_info(self):
        return self.ticker.info

    def get_industry(self):
        return self.ticker.info.get('industry', None)

    def get_short_name(self):
        return self.ticker.info.get('shortName', None)

    def get_long_name(self):
        return self.ticker.info.get('longName', None)

    def get_description(self):
        return self.ticker.info.get('longBusinessSummary', None)

    def get_sector(self):
        return self.ticker.info.get('sector', None)

    def get_data(self, period="1y", start=None, end=None, interval="1m"):
        return self.ticker.history(period=period, start=start, end=end, interval=interval, auto_adjust=True)

    def extract_features(self, period="1y", start=None, end=None, interval="1m", ma_windows=None, rsi_window=None,
                         macd_windows=None):

        # Fetch historical data using yfinance
        data = self.ticker.history(period=period, start=start, end=end, interval=interval, auto_adjust=True)

        # Add a date column with only the date part
        data['date'] = pd.to_datetime(pd.to_datetime(data.index).strftime('%Y-%m-%d'))

        # Calculate and add moving averages
        if ma_windows:
            for window in ma_windows:
                data[f'MA{window}'] = moving_average(data, window)

        # Calculate and add RSI
        if rsi_window:
            data[f'RSI{rsi_window}'] = rsi(data, rsi_window)

        # Calculate and add MACD and Signal line
        if macd_windows:
            macd_short, macd_long, macd_signal = macd_windows
            data['MACD'], data['Signal'] = macd(data, macd_short, macd_long, macd_signal)

        return data

    def extract_text_features(self):
        description = self.get_description()
        long_name = self.get_long_name()
        industry = self.get_industry()
        sector = self.get_sector()
        short_name = self.get_short_name()

        # Check if long_name and short_name are different
        name_part = f"{long_name}"
        if long_name != short_name:
            name_part += f", also known as {short_name}"

        # Handling for multiple industries
        industry_part = "an industry"  # Default text
        if industry:
            if isinstance(industry, list):  # If industry is a list
                industries = ', '.join(industry[:-1]) + ' and ' + industry[-1]
                industry_part = f"in industries such as {industries}"
            else:
                industry_part = f"in the {industry} industry"

        # Handling for multiple sectors
        sector_part = ""
        if sector:
            if isinstance(sector, list):  # If sector is a list
                sectors = ', '.join(sector[:-1]) + ' and ' + sector[-1]
                sector_part = f", specifically in sectors like {sectors}"
            else:
                sector_part = f", specifically in the {sector} sector"

        combined_text = (
            f"{name_part}, with a ticker symbol {self.ticker_symbol}, operates {industry_part}{sector_part}. "
            f"{description}")

        data = {'shortName': short_name, 'longName': long_name, 'industry': industry, 'sector': sector,
                'description': description, 'combined_text': combined_text}

        return data


if __name__ == "__main__":
    symbols_list = ['AAPL', 'MSFT', 'GOOG', 'AMZN', 'FB', 'TSLA', 'NVDA', 'ADBE']
    download_multiple_tickers(symbols_list, period="max", interval='1d')
    download_multiple_tickers(symbols_list, period="max", interval='1m')
    # download_multiple_tickers(symbols_list, period="max", interval='1d', ma_windows=(5, 10), rsi_window=14, macd_windows=(12, 26, 9))
    # dataset = build_dataset(period='max', seeded=True, custom_symbols=('AAPL', 'MSFT', 'GOOG', 'AMZN', 'FB', 'TSLA', 'NVDA', 'ADBE'))
    #
    # pd.DataFrame(dataset[0]).to_csv("market_values.csv", index=False)
    # pd.DataFrame(dataset[1]).to_csv("symbol_info.csv")
