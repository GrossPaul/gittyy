import pandas as pd
import numpy as np
import requests
import datetime
import streamlit as st
import plotly.graph_objects as go

# Funktion zur Berechnung von Bollinger-Bändern
def bollinger_bands(df, window=120):
    df['SMA'] = df['Close'].rolling(window).mean()  # Simple Moving Average
    df['STD'] = df['Close'].rolling(window).std()   # Standard Deviation
    df['Upper Band'] = df['SMA'] + (df['STD'] * 2)   # Upper Bollinger Band
    df['Lower Band'] = df['SMA'] - (df['STD'] * 2)   # Lower Bollinger Band
    return df

# Funktion, um Binance-Daten zu holen
def get_binance_data(symbol):
    url = f"https://api.binance.com/api/v3/ticker/24hr?symbol={symbol}"
    response = requests.get(url)
    data = response.json()

    # Fehlertoleranter Zugriff auf die Felder
    last_price = float(data['lastPrice']) if 'lastPrice' in data else None
    volume = float(data['volume']) if 'volume' in data else None
    high = float(data['highPrice']) if 'highPrice' in data else None
    low = float(data['lowPrice']) if 'lowPrice' in data else None

    df = pd.DataFrame([{
        'Close': last_price,
        'Volume': volume,
        'High': high,
        'Low': low
    }], index=[pd.to_datetime(datetime.datetime.now())])
    
    return df

# Funktion, um Coinbase Pro-Daten zu holen
def get_coinbase_data(symbol):
    url = f"https://api.pro.coinbase.com/products/{symbol}/ticker"
    response = requests.get(url)
    data = response.json()

    # Fehlertoleranter Zugriff auf die Felder
    price = float(data['price']) if 'price' in data else None
    volume = float(data['volume']) if 'volume' in data else None
    high = float(data['high']) if 'high' in data else None
    low = float(data['low']) if 'low' in data else None
    open_price = float(data['open']) if 'open' in data else None

    df = pd.DataFrame([{
        'Close': price,
        'Volume': volume,
        'High': high,
        'Low': low,
        'Open': open_price
    }], index=[pd.to_datetime(datetime.datetime.now())])

    return df

# Funktion, um Yahoo Finance-Daten zu holen
def get_yahoo_data(ticker):
    df = pd.read_csv(f'https://query1.finance.yahoo.com/v7/finance/download/{ticker}?period1=0&period2=9999999999&interval=1m&events=history')
    df['Date'] = pd.to_datetime(df['Date'])
    df.set_index('Date', inplace=True)
    df = df[['Close', 'High', 'Low', 'Volume']]
    return df

# Hier wählst du die Datenquelle (Yahoo, Binance, Coinbase)
data_source = st.selectbox('Wählen Sie eine Datenquelle', ['Yahoo Finance', 'Binance', 'Coinbase Pro'])

if data_source == 'Binance':
    st.write("Verwenden von Binance-Daten...")
    df = get_binance_data('BTCUSDT')  # BTCUSDT ist das Beispiel für Bitcoin auf Binance
elif data_source == 'Coinbase Pro':
    st.write("Verwenden von Coinbase Pro-Daten...")
    df = get_coinbase_data('BTC-USD')  # BTC-USD ist das Beispiel für Bitcoin auf Coinbase Pro
else:
    st.write("Verwenden von Yahoo Finance-Daten...")
    df = get_yahoo_data('BTC-USD')  # BTC-USD als Beispiel für Bitcoin bei Yahoo Finance

# Überprüfe, ob die 'Close'-Spalte vorhanden ist
if 'Close' not in df.columns:
    st.error("Die 'Close'-Daten konnten nicht abgerufen werden.")
else:
    # Bollinger-Bänder berechnen
    df = bollinger_bands(df, window=120)

    # Visualisiere den Kurs und die Bollinger-Bänder
    fig = go.Figure()

    # Kurslinie hinzufügen
    fig.add_trace(go.Scatter(x=df.index, y=df['Close'], mode='lines', name='Close', line=dict(color='blue')))

    # Oberes Bollinger-Band hinzufügen
    fig.add_trace(go.Scatter(x=df.index, y=df['Upper Band'], mode='lines', name='Upper Band', line=dict(color='green', dash='dash')))

    # Unteres Bollinger-Band hinzufügen
    fig.add_trace(go.Scatter(x=df.index, y=df['Lower Band'], mode='lines', name='Lower Band', line=dict(color='red', dash='dash')))

    # Layout anpassen
    fig.update_layout(
        title="Bitcoin Preis und Bollinger Bänder",
        xaxis_title="Zeit",
        yaxis_title="Preis",
        template="plotly_dark"
    )

    st.plotly_chart(fig)

    # Optionale Analyse über Volumen und Volatilität (Bollinger Bands)
    st.write("Datenquelle:", data_source)
    st.write("Zeitraum:", df.index.min(), "bis", df.index.max())

    # Volumen und Volatilität anzeigen
    st.subheader("Volumen und Volatilität")
    st.line_chart(df[['Volume']])

    volatility = df['Close'].pct_change().std() * np.sqrt(252)  # Annualisierte Volatilität
    st.write(f"Jährliche Volatilität: {volatility:.2%}")
