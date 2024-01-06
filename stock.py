import numpy as np
import pandas as pd
import os 
from get_all_tickers import get_tickers as gt
from datetime import datetime, timedelta
import yfinance as yf


# function that summarize all algorith used in workflow file to get all data
def transform_data(stock_df_name, per='None', start=None, end=None):
    # get all major data from yahoo finance
    big_data = yf.Ticker(stock_df_name)

    stock_df = big_data.history(period=per, start=start, end=end).copy()
    stock_df.drop('Stock Splits', inplace=True, axis=1)
    stock_df['Yield'] = stock_df['Dividends'] / stock_df['Close']
    stock_df = stock_df.astype('float')
    
    # get csv file from data_storage

    FILE_FOLDER = os.path.abspath('')
    rates_df =  pd.read_csv(os.path.join(FILE_FOLDER, 'Inflation_CDI_data'))
    #transform rates_df into time series
    rates_df['Unnamed: 0'] = pd.to_datetime(rates_df['Unnamed: 0'], utc=True).dt.tz_convert('America/Sao_Paulo')
    rates_df.set_index('Unnamed: 0', inplace=True)

    # fill rates_df with days 
    rates_df = rates_df.resample('D').ffill()

    # remove non days of week and resize rates to percentage
    rates_df = rates_df[rates_df.index.isin(stock_df.index)]
    rates_df = rates_df / 100




    # merge dfs and fill with days of week
    df = pd.merge(rates_df, stock_df, left_index=True,right_index=True, how='outer')
    df['CDI'].ffill(inplace=True)
    df['Inflation'].ffill(inplace=True)

    # convert inflation and CDI rates to daily
    df['CDI'] = (1 + df['CDI']) ** (1/20) - 1
    df['Inflation'] = (1 + df['Inflation']) ** (1/20) - 1

    # create return values to stock, inflation and CDI 
    df['Return_Stock'] = (df['Close'] + df['Yield'] - df['Close'].shift(1) ) / df['Close'].iloc[0] 
    df['Return_CDI'] = (df['Close'].iloc[0] * df['CDI'] )  / df['Close'].iloc[0]
    df['Return_Inflation'] = (df['Close'].iloc[0] * df['Inflation'] )  / df['Close'].iloc[0]
    
    # transform above columns values into cumulative sum
    df['Return_Stock'] = df['Return_Stock'].cumsum()
    df['Return_CDI'] = df['Return_CDI'].cumsum()
    df['Return_Inflation'] = df['Return_Inflation'].cumsum()

    # avoid missing values
    df = df.iloc[1:]
    return df


