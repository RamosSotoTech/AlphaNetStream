# coercion.py
from datetime import datetime
import pandas as pd


def get_datetime_format(df: pd.DataFrame, datetime_column: str = "datetime") -> str:
    datetime_dtype = df[datetime_column].dtype

    if pd.api.types.is_datetime64_any_dtype(datetime_dtype):
        datetime_format = None

    else:
        # separate date and time
        date_str = df[datetime_column].apply(lambda x: x.split(' ')[0])
        time_str = df[datetime_column].apply(lambda x: x.split(' ')[1])

        # if datetime string did not have time, set time to 00:00:00
        if time_str[0] == '':
            time_str = '00:00:00'

        date_format = identify_date_format(df, date_column=date_str)
        time_format = identify_time_format(df, time_col=time_str)

        # combine date and time format
        datetime_format = date_format + ' ' + time_format
    return datetime_format


def identify_date_format(data: pd.DataFrame, date_column: str = "date") -> str:
    """
    Identifies the format of the date column.
    :param data:
    :param date_column:
    :return:
    """
    date_dtype = data[date_column].dtype
    # If date is already in datetime64 format, no need to identify its format
    if pd.api.types.is_datetime64_any_dtype(date_dtype):
        date_format = None
    else:
        # List of possible date formats
        date_formats = ['%Y-%m-%d', '%d-%m-%Y', '%m-%d-%Y', '%d/%m/%Y', '%m/%d/%Y', '%d.%m.%Y', '%m.%d.%Y']

        # Identify date format
        date_format = None
        sample_date_str = str(data[date_column].iloc[0])
        for fmt in date_formats:
            try:
                datetime.strptime(sample_date_str, fmt)
                date_format = fmt
                break
            except ValueError:
                continue
    return date_format


def identify_time_format(data: pd.DataFrame, time_col: str = "time") -> str:
    """
    Identifies the format of the time column.
    :param data:
    :param time_col:
    :return:
    """
    time_dtype = data[time_col].dtype
    # If time is already in datetime64 or timedelta64 format, no need to identify its format
    if pd.api.types.is_datetime64_any_dtype(time_dtype) or pd.api.types.is_timedelta64_dtype(time_dtype):
        time_format = None
    else:
        # List of possible time formats
        time_formats = ['%H:%M', '%H:%M:%S', '%H:%M:%S.%f', '%I:%M %p', '%I:%M:%S %p', '%I:%M:%S.%f %p']

        # Identify time format
        time_format = None
        sample_time_str = str(data[time_col].iloc[0])
        for fmt in time_formats:
            try:
                datetime.strptime(sample_time_str, fmt)
                time_format = fmt
                break
            except ValueError:
                continue
    return time_format


def coerce_datetime(data: pd.DataFrame, datetime_column: str = "datetime") -> pd.DataFrame:
    """
    Coerce datetime column to datetime64 format.
    :param data:
    :param datetime_column:
    :return:
    """
    datetime_format = get_datetime_format(data, datetime_column=datetime_column)
    if datetime_format is not None:
        data[datetime_column].apply(lambda x: datetime.strptime(x, datetime_format))
    return data
