import pandas as pd  # For data manipulation and analysis
import requests  # For making HTTP requests


from datetime import datetime, timedelta  # For working with dates and times

import talib  # For technical analysis indicators

import plotly.graph_objects as go  # For interactive plotting with Plotly

from datetime import datetime, timedelta 


API_URL = 'https://api.binance.com/api/v3/klines' # Binance API endpoint for candlestick data
# ==============================
# RETRIEVING DATA FROM API
# ==============================

#The variable days_back represents the number of days in the past from which I intend to retrieve the data.
#The variable symbol is a coin pair. For example if you want bitcoin historical data, the symbol to use is BTCUSDT. 


def get_historical_data(symbol, days_back, interval):
    # Calculate the start time in milliseconds
    start_time = int((datetime.now() - timedelta(days=days_back)).timestamp() * 1000)

    # Calculate the current time in milliseconds
    end_time = int(datetime.now().timestamp() * 1000)

    # Make an API request to retrieve historical data
    response = requests.get(API_URL, params={
        'symbol': symbol,
        'interval': interval,
        'startTime': start_time,
        'endTime': end_time,
        'limit': 1000  # Maximum number of data points per request
    })

    # Check if the request was successful (status code 200)
    if response.status_code == 200:
        # API request was successful
        hist_json = response.json()

        # Making a df from response
        # Extract only the relevant elements for each row
        df = pd.DataFrame(hist_json, columns=[
            'Time', 'Open Price', 'High Price', 'Low Price',
            'Close Price', 'Volume', 'Kline Close Time', 'Quote Asset Volume',
            'Number of Trades', 'Taker Buy Base Asset Volume',
            'Taker Buy Quote Asset Volume', 'Unused Field'
        ])

        # Select only the relevant columns (Open Time, Open Price, High Price, Low Price, Close Price, Volume)
        df = df[['Time', 'Open Price', 'High Price', 'Low Price', 'Close Price', 'Volume']]
        df['dateTime'] = pd.to_datetime(df['Time'], unit='ms')
        print("Retrived data for: " + symbol)

        return df
    else:
        # API request was not successful, print an error message
        print(f"Error: API request failed with status code {response.status_code}")
        return None

# ==============================
# TRANSFORM DATA
# ==============================

def transform_hist_data(df_name):
    df_name['Open Price'] = pd.to_numeric(df_name['Open Price'], errors='coerce').astype(float)
    df_name['High Price'] = pd.to_numeric(df_name['High Price'], errors='coerce').astype(float)
    df_name['Low Price'] = pd.to_numeric(df_name['Low Price'], errors='coerce').astype(float)
    df_name['Close Price'] = pd.to_numeric(df_name['Close Price'], errors='coerce').astype(float)
    df_name['Volume'] = pd.to_numeric(df_name['Volume'], errors='coerce').astype(float)
    return df_name

# ==============================
# CALCULATE EMA 12, 13 and 26
# ==============================
def calculate_emas(df_name):
    df_name['13EMA'] = df_name['Close Price'].ewm(span=13, adjust=False).mean()
    df_name['12EMA'] = df_name['Close Price'].ewm(span=12, adjust=False).mean()
    df_name['26EMA'] = df_name['Close Price'].ewm(span=26, adjust=False).mean()
    return df_name
    
# ==============================
# CALCULATE MACD 12, 26, 9
# ==============================

def calculate_macd(df_name):
    # Calculate MACD Line (12EMA - 26EMA)
    df_name['MACD'] = df_name['12EMA'] - df_name['26EMA']

    # Calculate Signal Line (9-period EMA of MACD)
    df_name['Signal'] = df_name['MACD'].ewm(span=9, adjust=False).mean()

    # Calculate MACD Histogram
    df_name['Histogram'] = df_name['MACD'] - df_name['Signal']
    return df_name
    
# ==============================
# CALCULATE ELDER IMPULSE
# ==============================

def calculate_elder(df_name):

    for i in range(1, len(df_name)):
        ema_comparison = 0
        macd_comparison = 0
        first_row_ema = df_name.iloc[i-1]['13EMA']
        second_row_ema = df_name.iloc[i]['13EMA']
        if second_row_ema > first_row_ema:
            ema_comparison = 1
        elif second_row_ema < first_row_ema:
            ema_comparison = -1
        first_row_macd = df_name.iloc[i-1]['Histogram']
        second_row_macd = df_name.iloc[i]['Histogram']
        if second_row_macd > first_row_macd:
            macd_comparison = 1
        elif second_row_macd < first_row_macd:
            macd_comparison = -1
        if ema_comparison == 1 and macd_comparison == 1:
              df_name.at[i, 'elder_impulse'] = 1
        elif ema_comparison == -1 and macd_comparison == -1:
            df_name.at[i, 'elder_impulse'] = -1
        else:
            df_name.at[i, 'elder_impulse'] = 0
    return df_name
# ==============================
# CALCULATE ATR CHANNELS
# ==============================
def calculate_ATR(df_name):
    df_name['ATR21'] = talib.ATR(df_name['High Price'], df_name['Low Price'], df_name['Close Price'], timeperiod=21)
    df_name['21EMA'] = df_name['Close Price'].ewm(span=21, adjust=False).mean()
    df_name['ATR+1'] = df_name['21EMA'] + df_name['ATR21'] 
    df_name['ATR+2'] = df_name['21EMA'] + 2 * df_name['ATR21'] 
    df_name['ATR+3'] = df_name['21EMA'] + 3 * df_name['ATR21'] 
    df_name['ATR-1'] = df_name['21EMA'] - df_name['ATR21'] 
    df_name['ATR-2'] = df_name['21EMA'] - 2 * df_name['ATR21'] 
    df_name['ATR-3'] = df_name['21EMA'] - 3 * df_name['ATR21'] 
    return df_name
# ==============================
# TOP CRYPTO TO USDT LIST
# ==============================

def get_top_cryptos_with_usdt(number = 30):
    url = "https://api.binance.com/api/v3/ticker/24hr"
    response = requests.get(url)

    if response.status_code == 200:
        data = response.json()
        symbol_count_dict = {entry.get('symbol', None): entry.get('count', None) for entry in data if 'USDT' in entry.get('symbol', '')}
        sorted_dict_values = dict(sorted(symbol_count_dict.items(), key=lambda item: item[1], reverse = True))
        top_crypto_usdt = list(sorted_dict_values.keys())[:number]
        return top_crypto_usdt
    else:
        print(f"Error: {response.status_code}")
        return None


# ==============================
# DRAW ATR GRAPH
# ==============================

def draw_ATR_GRAPH(df_name):


    # Create a candlestick trace
    df_name['formatted_date'] = df_name['dateTime'].dt.strftime('%m-%d')
    candlestick = go.Candlestick(x=df_name['formatted_date'],
                                open=df_name['Open Price'],
                                high=df_name['High Price'],
                                low=df_name['Low Price'],
                                close=df_name['Close Price'],
                                name='Candlestick')

    # 21 EMA trace
    line_trace_21_EMA = go.Scatter(x=df_name['formatted_date'],
                        y=df_name['21EMA'],
                        mode='lines',
                        name='21EMA',
                        line=dict(color= 'black'))
    # ATR +1 trace
    line_trace_ATR_1 = go.Scatter(x=df_name['formatted_date'],
                        y=df_name['ATR+1'],
                        mode='lines',
                        name='ATR+1',
                        line=dict(color= 'green'))

    # ATR +2 trace
    line_trace_ATR_2 = go.Scatter(x=df_name['formatted_date'],
                        y=df_name['ATR+2'],
                        mode='lines',
                        name='ATR+2',
                        line=dict(color= 'orange'))


    # ATR +3 trace
    line_trace_ATR_3 = go.Scatter(x=df_name['formatted_date'],
                        y=df_name['ATR+3'],
                        mode='lines',
                        name='ATR+3',
                        line=dict(color= 'red'))

    # ATR -1 trace
    line_trace_ATR_neg1 = go.Scatter(x=df_name['formatted_date'],
                        y=df_name['ATR-1'],
                        mode='lines',
                        name='ATR-1',
                        line=dict(color= 'green'))
    # ATR -2 trace
    line_trace_ATR_neg2 = go.Scatter(x=df_name['formatted_date'],
                        y=df_name['ATR-2'],
                        mode='lines',
                        name='ATR-2',
                        line=dict(color= 'orange'))
    # ATR -3 trace
    line_trace_ATR_neg3 = go.Scatter(x=df_name['formatted_date'],
                        y=df_name['ATR-3'],
                        mode='lines',
                        name='ATR-3',
                        line=dict(color= 'red'))

    # Create layout
    layout = go.Layout(title='Candlestick Chart with Extra Line',
                    xaxis=dict(type='category', categoryorder='category ascending'),
                    yaxis=dict(title='Price'))

    # Create figure

    fig = go.Figure(data=[candlestick, line_trace_21_EMA, line_trace_ATR_1, line_trace_ATR_2, line_trace_ATR_3, line_trace_ATR_neg1, line_trace_ATR_neg2, line_trace_ATR_neg3], layout=layout)
    return fig

