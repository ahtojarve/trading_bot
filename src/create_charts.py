
from functions import get_top_cryptos_with_usdt
from functions import get_historical_data
from functions import calculate_emas
from functions import transform_hist_data
from functions import calculate_macd
from functions import calculate_elder
from functions import calculate_ATR
from functions import draw_ATR_GRAPH

import os
import plotly.io as pio
from time import sleep
from IPython.display import display, HTML  
from datetime import datetime

# ==============================
# CREATE BEAR CHARTS and put them into a figures folder
# ==============================

def create_bear_charts():

    # Get today's date in the format YYYY-MM-DD
    today_date = datetime.now().strftime('%Y-%m-%d')

    # Specify the folder path
    folder_path = f'/Users/ahtojarve/Trading_bot/reports/figures/{today_date}/bear'

    # Create the folder if it doesn't exist
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)
        print(f'Folder "{folder_path}" created successfully.')
    else:
        print(f'Folder "{folder_path}" already exists.')

   # Create an empty DataFrame

    for crypto in bear_set:
        df_medium = get_historical_data(crypto, 60, '1d')
        if len(df_medium) < 60:
            print(f"Skipping {crypto} - Insufficient historical data (less than 60 rows).")
            continue
        df_medium = calculate_ATR(df_medium)
        df_medium = transform_hist_data(df_medium)
        fig = draw_ATR_GRAPH(df_medium)
        chart_filename = f"{folder_path}/{crypto}.html"
        pio.write_html(fig, file = chart_filename)

# ==============================
# CREATE BULL CHARTS and put them into a figures folder
# ==============================

def create_bull_charts():

    # Get today's date in the format YYYY-MM-DD
    today_date = datetime.now().strftime('%Y-%m-%d')

    # Specify the folder path
    folder_path = f'/Users/ahtojarve/Trading_bot/reports/figures/{today_date}/bull'

    # Create the folder if it doesn't exist
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)
        print(f'Folder "{folder_path}" created successfully.')
    else:
        print(f'Folder "{folder_path}" already exists.')

    for crypto in bull_set:
        df_medium = get_historical_data(crypto, 60, '1d')
        if len(df_medium) < 60:
            print(f"Skipping {crypto} - Insufficient historical data (less than 60 rows).")
            continue
        df_medium = transform_hist_data(df_medium)
        df_medium = calculate_ATR(df_medium)
        fig = draw_ATR_GRAPH(df_medium)
        chart_filename = f"{folder_path}/{crypto}.html"
        pio.write_html(fig, file = chart_filename)



green_color = "#00cc00"
red_color = "#ff6666"

bull_set = set() #Creating a set for all bulls
bear_set = set() #Creating a set for all bears

top_cryptos_usdt = get_top_cryptos_with_usdt(100)

for crypto in top_cryptos_usdt:
    #Teen arvutused ja panen tabelisse
    df = get_historical_data(crypto, 360, '1w')
    df = transform_hist_data(df)
    df = calculate_emas(df)
    df = calculate_macd(df)
    df = calculate_elder(df)
    #Kui elder on roheline või sinine peale punast, siis on pull
    if len(df) >=2:

        if df.iloc[-2]['elder_impulse'] == -1 and (df.iloc[-1]['elder_impulse'] == 0 or df.iloc[-1]['elder_impulse'] == 1):
            bull_set.add(crypto)
            display(HTML(f"<span style='color:{green_color}'>Added {crypto} to bull_set</span>"))
        #Kui elder on punane või sinine peale rohelist, siis on karu
        elif df.iloc[-2]['elder_impulse'] == 1 and (df.iloc[-1]['elder_impulse'] == 0 or df.iloc[-1]['elder_impulse'] == -1):
            bear_set.add(crypto)
            display(HTML(f"<span style='color:{red_color}'>Added {crypto} to bear_set</span>"))
        else:
            print(crypto + " is not acceptable")
    else:
        print(crypto + " is not acceptable")
    sleep(0.1)
    
    
    
create_bear_charts()
create_bull_charts()


