import pandas as pd
import numpy as np


class FinancialData:
    def __init__(self, data, close_column='Close', volume_column='Volume', high_column='High', low_column='Low'):
        self.data = data
        self.close_column = close_column
        self.volume_column = volume_column
        self.high_column = high_column
        self.low_column = low_column

    def macd(self, short_window=12, long_window=26, signal_window=9):
        self.validate_columns(self.close_column)
        df = self.data.copy()
        df['MACD'] = df[self.close_column].ewm(span=short_window, adjust=False).mean() - df[self.close_column].ewm(
            span=long_window, adjust=False).mean()
        df['Signal'] = df['MACD'].ewm(span=signal_window, adjust=False).mean()
        return df[['MACD', 'Signal']]

    def validate_columns(self, *columns):
        for column in columns:
            if column not in self.data.columns:
                raise ValueError(f"Column {column} not in data. Please provide a valid column name.")

    def price_change(self):
        self.validate_columns(self.close_column)
        return self.data[self.close_column].diff()

    def price_percentage_change(self):
        self.validate_columns(self.close_column)
        return self.data[self.close_column].pct_change() * 100

    def moving_average(self, window):
        self.validate_columns(self.close_column)
        df = self.data.copy()
        df[f'SMA{window}'] = df[self.close_column].rolling(window=window).mean()
        return df[f'SMA{window}']

    def trading_volume(self):
        self.validate_columns(self.volume_column)
        return self.data[self.volume_column]

    def vwap(self):
        self.validate_columns(self.close_column, self.volume_column)
        return (self.data[self.close_column] * self.data[self.volume_column]).cumsum() / self.data[self.volume_column].cumsum()

    def on_balance_volume(self):
        self.validate_columns(self.close_column, self.volume_column)
        obv = (self.data[self.volume_column] * ~self.data[self.close_column].diff().le(0)).astype(int)
        return obv.cumsum()

    def volatility(self, window=14):
        self.validate_columns(self.close_column)
        return self.data[self.close_column].rolling(window=window).std()

    def beta(self, window=14):
        # todo: systematic risk assessment
        pass

    def roi(self):
        self.validate_columns(self.close_column)
        return self.data[self.close_column].pct_change()

    def rsi(self, window=14):
        self.validate_columns(self.close_column)
        delta = self.data[self.close_column].diff()
        gain = (delta.where(delta > 0, 0))
        loss = (-delta.where(delta < 0, 0))
        avg_gain = gain.rolling(window=window).mean()
        avg_loss = loss.rolling(window=window).mean()
        rs = avg_gain / avg_loss
        return 100 - (100 / (1 + rs))

    def bollinger_bands(self, window=20):
        self.validate_columns(self.close_column)
        sma = self.data[self.close_column].rolling(window=window).mean()
        rolling_std = self.data[self.close_column].rolling(window=window).std()
        self.data['Bollinger Upper Band'] = sma + (rolling_std * 2)
        self.data['Bollinger Lower Band'] = sma - (rolling_std * 2)
        return self.data[['Bollinger Upper Band', 'Bollinger Lower Band']]

    def sharpe_ratio(self, window=14):
        self.validate_columns('ROI', 'Volatility')
        self.data['Sharpe Ratio'] = self.data['ROI'].rolling(window=window).mean() / self.data['Volatility'].rolling(window=window).mean()
        return self.data['Sharpe Ratio']

    def sortino_ratio(self, window=14):
        self.validate_columns('ROI', 'Volatility')
        self.data['Sortino Ratio'] = self.data['ROI'].rolling(window=window).mean() / self.data[self.data['ROI'] < 0]['Volatility'].rolling(window=window).mean()
        return self.data['Sortino Ratio']

    def atr(self, window=14, calculate=True):
        if calculate:
            self.data['ATR'] = self.calculate_atr(window)
        return self.data['ATR']

    def calculate_atr(self, window):
        self.validate_columns(self.high_column, self.low_column, self.close_column)
        high_low = self.data[self.high_column] - self.data[self.low_column]
        high_close = np.abs(self.data[self.high_column] - self.data[self.close_column].shift())
        low_close = np.abs(self.data[self.low_column] - self.data[self.close_column].shift())
        ranges = pd.concat([high_low, high_close, low_close], axis=1)
        true_range = np.max(ranges, axis=1)
        return true_range.rolling(window=window).mean()

    def get_features(self, window=14, calculate=True):
        features = pd.concat([
            self.price_change(),
            self.price_percentage_change(),
            self.moving_average(window),
            self.trading_volume(),
            self.vwap(),
            self.on_balance_volume(),
            self.volatility(window),
            self.roi(),
            self.rsi(window),
            # pass in the window for macd
            self.macd(),
            self.bollinger_bands(window),
            self.sharpe_ratio(window),
            self.sortino_ratio(window),
            self.atr(window, calculate)
        ], axis=1)
        return features

    def get_data(self, window=14, calculate=True):
        data = pd.concat([
            self.data,
            self.get_features(window, calculate)
        ], axis=1)
        return data.copy()
