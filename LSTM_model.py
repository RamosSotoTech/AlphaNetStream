import pandas as pd
from sklearn.preprocessing import MinMaxScaler
from sklearn.metrics import mean_squared_error
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense
from utils.data_loader import DataLoader
from utils.financial_features import FinancialData


class LSTMModel:
    def __init__(self, symbol, interval='1d', epochs=50, batch_size=32):
        self.symbol = symbol
        self.interval = interval
        self.epochs = epochs
        self.batch_size = batch_size
        self.model = Sequential()

    def prepare_data(self):
        # Load the data
        loader = DataLoader()
        interval_data_dict = loader.load_data()
        data = interval_data_dict[self.interval].copy()
        data = data[data['Symbol'] == self.symbol].copy()

        # Extract financial features
        financial_features = FinancialData(data.copy())
        data.loc[:, 'SMA5'] = financial_features.moving_average(5)
        data.loc[:, 'SMA10'] = financial_features.moving_average(10)
        data.loc[:, 'SMA20'] = financial_features.moving_average(20)
        data.loc[:, 'SMA50'] = financial_features.moving_average(50)
        data.loc[:, 'SMA100'] = financial_features.moving_average(100)
        data.loc[:, 'SMA200'] = financial_features.moving_average(200)
        data.loc[:, 'RSI'] = financial_features.rsi()
        data.loc[:, 'MACD'], data.loc[:, 'Signal'] = financial_features.macd()

        # dataset = financial_features.get_data()

        # Select features and target variable for training
        features = data.drop(['Close', 'Symbol', 'date', 'Date'], axis=1)
        target = data['Close']

        # Remove rows with missing values
        features = features.dropna()
        # notify which rows were dropped
        print(f'Dropped {len(data) - len(features)} rows due to missing values.')

        # Scale the data
        scaler = MinMaxScaler()
        features_scaled = scaler.fit_transform(features)
        target_scaled = scaler.fit_transform(target.values.reshape(-1, 1))

        # Split the data into training and testing sets (e.g., 80% train, 20% test)
        train_size = int(len(features) * 0.8)
        X_train, X_test = features_scaled[:train_size], features_scaled[train_size:]
        y_train, y_test = target_scaled[:train_size], target_scaled[train_size:]

        # Reshape input to be 3D [samples, timesteps, features] for LSTM
        X_train = X_train.reshape((X_train.shape[0], 1, X_train.shape[1]))
        X_test = X_test.reshape((X_test.shape[0], 1, X_test.shape[1]))

        return X_train, y_train, X_test, y_test, scaler

    def build_model(self, input_shape):
        self.model.add(LSTM(50, input_shape=input_shape))
        self.model.add(Dense(1))
        self.model.compile(optimizer='adam', loss='mean_squared_error')

    def train_model(self, X_train, y_train):
        self.model.fit(X_train, y_train, epochs=self.epochs, batch_size=self.batch_size, verbose=2)

    def evaluate_model(self, X_test, y_test):
        y_pred = self.model.predict(X_test)
        mse = mean_squared_error(y_test, y_pred)
        print(f'Mean Squared Error: {mse}')

    def run(self):
        X_train, y_train, X_test, y_test, scaler = self.prepare_data()
        self.build_model(input_shape=(X_train.shape[1], X_train.shape[2]))
        self.train_model(X_train, y_train)
        self.evaluate_model(X_test, y_test)


def main(interval, symbols):
    # Load all datasets
    loader = DataLoader()
    interval_data_dict = loader.load_data()

    # Ensure the models directory exists
    models_dir = 'models'
    os.makedirs(models_dir, exist_ok=True)

    # If a specific interval is specified, filter the dictionary to only include that interval
    if interval != 'all':
        interval_data_dict = {interval: interval_data_dict.get(interval)}

    # Iterate through each interval and symbol, train a model, and save the model
    for interval, data in interval_data_dict.items():
        if symbols != ['all']:
            data = data[data['Symbol'].isin(symbols)]
        unique_symbols = data['Symbol'].unique()
        for symbol in unique_symbols:
            print(f'Training model for {symbol} at interval {interval}...')
            lstm_model = LSTMModel(symbol=symbol, interval=interval)
            lstm_model.run()

            # Save the model to a file
            model_filename = f'{models_dir}/{symbol}_{interval}_model.h5'
            lstm_model.model.save(model_filename)
            print(f'Model for {symbol} at interval {interval} saved to {model_filename}')


if __name__ == '__main__':
    import os
    import argparse

    parser = argparse.ArgumentParser(description='Train LSTM models on financial data.')
    parser.add_argument('--interval', type=str, default='1d', help='Data interval (default: 1d). Use "all" to process all intervals.')
    parser.add_argument('--symbols', nargs='+', default=['AAPL'], help='List of symbols (default: all).') #todo: change default to all
    args = parser.parse_args()
    main(interval=args.interval, symbols=args.symbols)
