import streamlit as st
import pandas as pd
import requests
import datetime

# Binance API Data Retrieval (No Authentication)
def get_binance_data(symbol):
    url = f"https://api.binance.com/api/v3/ticker/24hr?symbol={symbol}"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        df = pd.DataFrame([{
            'Close': float(data['lastPrice']),
            'Volume': float(data['volume']),
            'High': float(data['highPrice']),
            'Low': float(data['lowPrice']),
        }], index=[pd.to_datetime(datetime.datetime.now())])
        return df
    else:
        st.error(f"Binance API Fehler: {response.status_code}")
        return pd.DataFrame()  # Leeres DataFrame im Fehlerfall

# Coinbase Pro API Data Retrieval (No Authentication)
def get_coinbase_data(symbol):
    url = f"https://api.pro.coinbase.com/products/{symbol}/ticker"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        df = pd.DataFrame([{
            'Close': float(data['price']),
            'Volume': float(data['volume']),
            'High': None,  # Coinbase Ticker Endpoint gibt keine High/Low-Werte zurück
            'Low': None
        }], index=[pd.to_datetime(datetime.datetime.now())])
        return df
    else:
        st.error(f"Coinbase API Fehler: {response.status_code}")
        return pd.DataFrame()  # Leeres DataFrame im Fehlerfall

# Yahoo Finance API Data Retrieval
def get_yahoo_data(symbol):
    url = f"https://query1.finance.yahoo.com/v7/finance/download/{symbol}?period1=0&period2={int(datetime.datetime.now().timestamp())}&interval=1m&events=history"
    try:
        df = pd.read_csv(url)
        df['Date'] = pd.to_datetime(df['Date'])
        df.set_index('Date', inplace=True)
        return df
    except Exception as e:
        st.error(f"Yahoo Finance Fehler: {str(e)}")
        return pd.DataFrame()

# Bollinger-Band-Berechnung
def bollinger_bands(df, window=120):
    df['SMA'] = df['Close'].rolling(window).mean()
    df['STD'] = df['Close'].rolling(window).std()
    df['Upper Band'] = df['SMA'] + (df['STD'] * 2)
    df['Lower Band'] = df['SMA'] - (df['STD'] * 2)
    return df

# App Layout
st.title('Krypto-Datenanalyse: Bitcoin und mehr')

# Auswahl der Datenquelle
data_source = st.selectbox("Wähle die Datenquelle:", ["Yahoo Finance", "Binance", "Coinbase Pro"])

# Auswahl des Symbols
crypto_symbol = st.selectbox("Wähle das Krypto-Symbol:", ["BTC-USD", "ETH-USD", "BNB-USD"])

# Laden der Daten basierend auf der ausgewählten Quelle
if data_source == "Yahoo Finance":
    st.write("Using Yahoo Finance data...")
    df = get_yahoo_data(crypto_symbol)
elif data_source == "Binance":
    st.write("Using Binance data...")
    df = get_binance_data(crypto_symbol.replace("-", ""))
elif data_source == "Coinbase Pro":
    st.write("Using Coinbase Pro data...")
    df = get_coinbase_data(crypto_symbol)

# Überprüfe, ob die Spalte 'Close' im DataFrame vorhanden ist
if 'Close' not in df.columns:
    st.error("Die Daten konnten nicht geladen werden.")
else:
    # Bollinger-Bänder für die letzten zwei Stunden berechnen
    df = bollinger_bands(df, window=120)

    # Visualisierung
    st.line_chart(df[['Close', 'Upper Band', 'Lower Band']])

    # Zeige das Daten-DataFrame
    st.write("Datenvorschau:")
    st.dataframe(df)

# Footer
st.write("Daten werden von Yahoo Finance, Binance und Coinbase Pro abgerufen.")
