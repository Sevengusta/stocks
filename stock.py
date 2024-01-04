import numpy as np
import pandas as pd
import seaborn as sns
from get_all_tickers import get_tickers as gt
from datetime import datetime, timedelta
import yfinance as yf

br_df = pd.read_html("https://www.dadosdemercado.com.br/bolsa/acoes").copy()
tickers = br_df[0]['Ticker']
tickers = [tickers + ".SA" for tickers in tickers]

big_data = yf.Ticker('ITUB4.SA')

stock_df = big_data.history(period='max').copy()

# Transforming the data to analysis
columns = ["Close", 'Volume', 'Open', 'High', 'Low', 'Dividends']

stock_df = pd.DataFrame(stock_df[columns])
stock_df['Yield'] = stock_df['Dividends'] / stock_df['Close']
stock_df = stock_df.astype('float')

today = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')
month_1 = (datetime.now() - timedelta(days=31)).strftime('%Y-%m-%d')
year_1 = (datetime.now() - timedelta(days=366)).strftime('%Y-%m-%d')
year_5 = (datetime.now() - timedelta(days=(365 * 5 + 1))).strftime('%Y-%m-%d')



# initial and final values from time series to create a condicional line chart color
init_value = stock_df['Close'].iloc[0]
last_value = stock_df['Close'].iloc[-1]
line_color = "red" if init_value > last_value else "green"



all_dfs = []
# Create a df with a web data and get all values from currenty month until january 2020

for i in range(0, 100):
    url = f"https://www.vriconsulting.com.br/indices/cdi.php?pagina={i}"
    df = pd.read_html(url)[0].copy()
    all_dfs.append(df)
    if 'Jan/2000' in df['Mês/Ano'].values:
        break
cdi_df = pd.concat(all_dfs)
cdi_df.rename(columns={"Índice do mês (em %)": "CDI/Month"}, inplace=True)
cdi_df = cdi_df[["CDI/Month", "Mês/Ano"]]

# Avoid lost of data
cdi_df["CDI/Month"][0] = cdi_df["CDI/Month"][1]
cdi_df["CDI/Month"] = cdi_df["CDI/Month"].astype('float')


months = {
    'Jan': '01', 'Fev': '02', 'Mar': '03', 'Abr': '04',
    'Mai': '05', 'Jun': '06', 'Jul': '07', 'Ago': '08',
    'Set': '09', 'Out': '10', 'Nov': '11', 'Dez': '12'
}

cdi_df["Mês/Ano"] = cdi_df["Mês/Ano"].str.capitalize().str.strip()
cdi_df["Mês/Ano"] = cdi_df["Mês/Ano"].str[:3].map(
    months) + cdi_df["Mês/Ano"].str[3:]
cdi_df["Mês/Ano"] = pd.to_datetime(cdi_df['Mês/Ano'], format='%m/%Y',
                                   errors='coerce').dt.tz_localize('UTC').dt.tz_convert('America/Sao_Paulo')


cdi_df = cdi_df.set_index("Mês/Ano")



cdi_df = cdi_df.resample('D').ffill()
cdi_df = cdi_df[cdi_df.index.isin(stock_df.index)]


cdi_df = (cdi_df.astype('float') / 100000)

df = pd.merge(cdi_df, stock_df, left_index=True, right_index=True, how='outer')
df['CDI/Month'] = df['CDI/Month'].ffill()

df['Return_Stock'] = (df['Close'] + df['Yield'] -
                      df['Close'].shift(1)) / df['Close'].loc[df.index.min()]
df['Return_CDI'] = ((1 + df['CDI/Month']) * df['Close'].loc[df.index.min()] -
                    df['Close'].loc[df.index.min()]) / 365 / df['Close'].loc[df.index.min()]


df['Return_Stock'] = df['Return_Stock'].cumsum()
df['Return_CDI'] = df['Return_CDI'].cumsum()



def transform_data(stock_df_name, per='None', start=None, end=None):
    # get all major data to the project
    big_data = yf.Ticker(stock_df_name)
    # start_date = '1990-01-01'
    # end_date = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')

    stock_df = big_data.history(period=per, start=start, end=end).copy()

    # Transforming the data to analysis
    columns = ["Close", 'Volume', 'Open', 'High', 'Low', 'Dividends']
    stock_df = pd.DataFrame(stock_df[columns])
    stock_df['Yield'] = stock_df['Dividends'] / stock_df['Close']
    stock_df = stock_df.astype('float')

    df = pd.merge(cdi_df, stock_df, left_index=True,
                  right_index=True, how='outer')
    df['CDI/Month'] = df['CDI/Month'].ffill()
    df = df.loc[stock_df.index.min():]
    df['Return_Stock'] = (df['Close'] + df['Yield'] -
                          df['Close'].shift(1)) / df['Close'].loc[df.index.min()]
    df['Return_CDI'] = ((1 + df['CDI/Month']) * df['Close'].loc[df.index.min()] -
                        df['Close'].loc[df.index.min()]) / 365 / df['Close'].loc[df.index.min()]

    df['Return_CDI'] = df['Return_CDI'].cumsum()
    df['Return_Stock'] = df['Return_Stock'].cumsum()
    df = df.iloc[1:]
    return df


