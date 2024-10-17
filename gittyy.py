import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# Funktion zur Berechnung von SMA und Risiko
def calculate_sma_risk(data, short_window, long_window):
    data['SMA_Short'] = data['Close'].rolling(window=short_window).mean()
    data['SMA_Long'] = data['Close'].rolling(window=long_window).mean()
    data['Volatility'] = data['Close'].pct_change().rolling(window=10).std() * np.sqrt(252)
    return data

# Simulierte Handelsstrategie auf Basis von Risiko und Kapital
def simulate_trading(data, start_capital, risk_threshold):
    capital = start_capital
    positions = 0  # Anzahl der gekauften Einheiten
    trade_history = []

    for i in range(1, len(data)):
        current_price = data['Close'][i]
        volatility = data['Volatility'][i]
        signal = None

        # Kaufentscheidung bei niedrigem Risiko
        if volatility < risk_threshold and positions == 0:
            positions = capital / current_price
            capital = 0
            signal = "Buy"

        # Verkaufsentscheidung bei hohem Risiko oder Gewinnmitnahme
        elif volatility > risk_threshold and positions > 0:
            capital = positions * current_price
            positions = 0
            signal = "Sell"

        # Speichere den Kapitalverlauf
        trade_history.append({
            "Time": data.index[i],
            "Price": current_price,
            "Capital": capital + positions * current_price,  # Kapitalwert inklusive offener Positionen
            "Signal": signal
        })

    return pd.DataFrame(trade_history)

# Plot Funktion für den Handelsverlauf
def plot_trading(data, trade_history):
    fig, ax = plt.subplots(figsize=(10, 6))

    # Kursverlauf
    ax.plot(data['Close'], label='Kursverlauf', color='blue')

    # Kauf-/Verkaufssignale
    buy_signals = trade_history[trade_history['Signal'] == "Buy"]
    sell_signals = trade_history[trade_history['Signal'] == "Sell"]

    ax.scatter(buy_signals['Time'], buy_signals['Price'], color='green', marker='^', label='Kauf')
    ax.scatter(sell_signals['Time'], sell_signals['Price'], color='red', marker='v', label='Verkauf')

    # SMA Kurven
    ax.plot(data['SMA_Short'], label='SMA Kurz', color='green', linestyle='--')
    ax.plot(data['SMA_Long'], label='SMA Lang', color='orange', linestyle='--')

    ax.legend()
    st.pyplot(fig)

# Plot für Kapitalverlauf
def plot_capital(trade_history):
    fig, ax = plt.subplots(figsize=(10, 6))
    
    ax.plot(trade_history['Time'], trade_history['Capital'], label='Kapitalverlauf', color='purple')
    ax.set_ylabel("Kapital in €")
    ax.set_xlabel("Zeit")
    ax.legend()
    st.pyplot(fig)

# Daten von Yahoo Finance laden
def load_data(ticker, period='5d', interval='1m'):
    data = yf.download(ticker, period=period, interval=interval)
    return data

# Hauptprogramm für das Streamlit-Dashboard
def main():
    st.title("BTC/ETH Handelsstrategie mit Risikomanagement und Kapitalverlauf")

    # Benutzeroptionen
    ticker = st.sidebar.selectbox("Wähle einen Ticker (BTC-USD oder ETH-USD)", options=["BTC-USD", "ETH-USD"])
    sma_short_minutes = st.sidebar.slider("SMA Kurz (Minuten)", 1, 10, 5)
    sma_long_minutes = st.sidebar.slider("SMA Lang (Minuten)", 10, 60, 10)
    risk_threshold = st.sidebar.slider("Risikoschwelle (Volatilität)", 0.01, 0.1, 0.02)
    start_capital = st.sidebar.number_input("Startkapital (€)", value=50, step=10)

    # Daten laden (letzte 5 Tage, 1-Minuten-Intervall)
    data = load_data(ticker, period="5d", interval="1m")

    if data is not None and not data.empty:
        # SMA und Risiko berechnen
        data = calculate_sma_risk(data, sma_short_minutes, sma_long_minutes)

        # Simulierte Handelsstrategie
        trade_history = simulate_trading(data, start_capital, risk_threshold)

        # Kurs- und Handelsverlauf visualisieren
        st.write(f"**Kursverlauf und Handelsstrategie für {ticker}**")
        plot_trading(data, trade_history)

        # Kapitalverlauf anzeigen
        st.write(f"**Kapitalverlauf für {ticker} (Startkapital: {start_capital} €)**")
        plot_capital(trade_history)

        # Tabelle mit Handelssignalen anzeigen
        st.write("**Handelshistorie**")
        st.write(trade_history)
    else:
        st.write("Keine Daten gefunden. Bitte überprüfe die Eingaben.")

if __name__ == '__main__':
    main()
