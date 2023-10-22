import matplotlib.pyplot as plt
import mplfinance as mpf
import seaborn as sns


class Visualization:
    def __init__(self, data, custom_display='all'):
        self.data = data
        self.symbols = {symbol: (custom_display == 'all') for symbol in data['Symbol'].unique()}

    def set_active(self, symbol):
        """Activate a symbol for display."""
        self.symbols[symbol] = True

    def set_inactive(self, symbol):
        """Deactivate a symbol for display."""
        self.symbols[symbol] = False

    def get_active_symbols(self):
        """Get a list of active symbols."""
        return [symbol for symbol, active in self.symbols.items() if active]

    def filter_data(self):
        """Filter data for active symbols."""
        active_symbols = self.get_active_symbols()
        return self.data[self.data['Symbol'].isin(active_symbols)]

    def plot_time_series(self, columns, title=None):
        df = self.filter_data()
        df.set_index('Datetime', inplace=True)
        for symbol in df['Symbol'].unique():
            symbol_data = df[df['Symbol'] == symbol]
            symbol_data[columns].plot(figsize=(10, 5), label=symbol)
        plt.title(title if title else 'Time Series Plot')
        plt.ylabel('Value')
        plt.xlabel('Date')
        plt.legend(title='Legend')
        plt.show()

    def plot_candlestick(self, title=None):
        df = self.filter_data()
        df.set_index('Datetime', inplace=True)
        for symbol in df['Symbol'].unique():
            symbol_data = df[df['Symbol'] == symbol]
            mpf.plot(symbol_data, type='candle', title=title if title else f'Candlestick Chart: {symbol}', volume=True, style='charles')

    def plot_heatmap(self, title=None):
        df = self.filter_data()
        df.set_index('Datetime', inplace=True)
        for symbol in df['Symbol'].unique():
            symbol_data = df[df['Symbol'] == symbol]
            sns.heatmap(symbol_data.corr(), annot=True, cmap='coolwarm')
            plt.title(title if title else f'Correlation Heatmap: {symbol}')
            plt.show()

    def plot_pie(self, column, title=None):
        df = self.filter_data()
        for symbol in df['Symbol'].unique():
            symbol_data = df[df['Symbol'] == symbol]
            symbol_data[column].value_counts().plot(kind='pie', figsize=(5, 5), autopct='%1.1f%%')
            plt.title(title if title else f'Pie Chart: {symbol}')
            plt.show()

    def plot_bar(self, column, title=None):
        df = self.filter_data()
        for symbol in df['Symbol'].unique():
            symbol_data = df[df['Symbol'] == symbol]
            symbol_data[column].value_counts().plot(kind='bar', figsize=(10, 5))
            plt.title(title if title else f'Bar Chart: {symbol}')
            plt.show()

    def plot_box(self, column, title=None):
        df = self.filter_data()
        for symbol in df['Symbol'].unique():
            symbol_data = df[df['Symbol'] == symbol]
            symbol_data.boxplot(column=column, figsize=(10, 5))
            plt.title(title if title else f'Box Plot: {symbol}')
            plt.show()

    def plot_scatter(self, x, y, title=None):
        df = self.filter_data()
        for symbol in df['Symbol'].unique():
            symbol_data = df[df['Symbol'] == symbol]
            symbol_data.plot.scatter(x=x, y=y, figsize=(10, 5))
            plt.title(title if title else f'Scatter Plot: {symbol}')
            plt.show()

    def plot_histogram(self, column, title=None):
        df = self.filter_data()
        for symbol in df['Symbol'].unique():
            symbol_data = df[df['Symbol'] == symbol]
            symbol_data[column].hist(figsize=(10, 5))
            plt.title(title if title else f'Histogram: {symbol}')
            plt.show()

    def plot_line(self, x, y, title=None):
        df = self.filter_data()
        for symbol in df['Symbol'].unique():
            symbol_data = df[df['Symbol'] == symbol]
            symbol_data.plot.line(x=x, y=y, figsize=(10, 5))
            plt.title(title if title else f'Line Plot: {symbol}')
            plt.show()