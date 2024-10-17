import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# SMA Berechnung
def calculate_sma(data, short_window, long_window):
    data['SMA_Short'] = data['Close'].rolling(window=short_window).mean()
    data['SMA_Long'] = data['Close'].rolling(window=long_window).mean()
    return data

# Candlestick-Muster-Erkennung (Einfaches Beispiel für Doji)
def detect_candlestick_patterns(data):
    patterns = []
    for i in range(1, len(data)):
        open_price = data['Open'][i]
        close_price = data['Close'][i]
        high_price = data['High'][i]
        low_price = data['Low'][i]

        # Doji-Erkennung (als einfaches Beispiel)
        if abs(close_price - open_price) / (high_price - low_price) < 0.1:
            patterns.append("Doji")
        else:
            patterns.append("None")
    return patterns

# Volatilitätsberechnung (Risikoanalyse)
def calculate_volatility(data, window=10):
    data['Volatility'] = data['Close'].pct_change().rolling(window=window).std() * np.sqrt(252)
    return data

# Bollinger Bands als weiteres Risiko-Tool
def calculate_bollinger_bands(data, window=20):
    data['Rolling_Mean'] = data['Close'].rolling(window=window).mean()
    data['Bollinger_Upper'] = data['Rolling_Mean'] + (data['Close'].rolling(window=window).std() * 2)
    data['Bollinger_Lower'] = data['Rolling_Mean'] - (data['Close'].rolling(window=window).std() * 2)
    return data

# Plot-Funktion für Candlesticks, SMAs und Risikodarstellung
def plot_data(data, patterns, show_risk):
    fig, ax = plt.subplots(figsize=(10, 6))

    # Candlestick-Kursverlauf
    ax.plot(data['Close'], label='Kursverlauf', color='blue')

    # Candlestick-Muster farblich hervorheben (Doji als Beispiel)
    for i, pattern in enumerate(patterns):
        if pattern == 'Doji':
            ax.scatter(data.index[i], data['Close'][i], color='red', label='Doji' if i == 0 else "", s=100)

    # SMA-Kurven (Short und Long)
    ax.plot(data['SMA_Short'], label='SMA Kurz', color='green', linestyle='--')
    ax.plot(data['SMA_Long'], label='SMA Lang', color='orange', linestyle='--')

    # Bollinger Bands
    ax.plot(data['Bollinger_Upper'], label='Bollinger Oberes Band', color='grey', linestyle='-.')
    ax.plot(data['Bollinger_Lower'], label='Bollinger Unteres Band', color='grey', linestyle='-.')

    # Risikofarben (Volatilität)
    if show_risk:
        risk_colors = np.where(data['Volatility'] > data['Volatility'].mean(), 'red', 'green')
        ax.scatter(data.index, data['Close'], c=risk_colors, alpha=0.5, label='Risikobewertung')

    ax.legend()
    st.pyplot(fig)

# Daten von Yahoo Finance laden
def load_data(ticker, start, end):
    data = yf.download(ticker, start=start, end=end)
    return data

# Hauptprogramm für das Streamlit-Dashboard
def main():
    st.title("Finanzanalyse: Candlestick-Muster, SMAs und Risikobewertung")

    # Benutzeroptionen
    ticker = st.sidebar.text_input("Wähle einen Ticker (z.B. AAPL, MSFT)", value="AAPL")
    start = st.sidebar.date_input("Startdatum", pd.to_datetime('2022-01-01'))
    end = st.sidebar.date_input("Enddatum", pd.to_datetime('2023-01-01'))
    
    short_sma = st.sidebar.slider("SMA Kurz Fenster", 5, 50, 20)
    long_sma = st.sidebar.slider("SMA Lang Fenster", 50, 200, 100)
    show_risk = st.sidebar.checkbox("Risikobewertung anzeigen")
    
    # Daten laden
    data = load_data(ticker, start, end)

    if data is not None and not data.empty:
        # Candlestick-Muster erkennen
        patterns = detect_candlestick_patterns(data)
        
        # SMA berechnen
        data = calculate_sma(data, short_sma, long_sma)

        # Bollinger Bands berechnen
        data = calculate_bollinger_bands(data)

        # Volatilität für Risikobewertung
        if show_risk:
            data = calculate_volatility(data)

        # Daten anzeigen
        st.write(f"**Daten für {ticker}**")
        st.write(data.tail())

        # Visualisierung
        plot_data(data, patterns, show_risk)
    else:
        st.write("Keine Daten gefunden. Bitte überprüfe die Eingaben.")

if __name__ == '__main__':
    main()
