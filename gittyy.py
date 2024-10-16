import streamlit as st
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import yfinance as yf

# Funktion zur Datenbeschaffung (minütliche Daten von Yahoo Finance)
def get_market_data(symbol, lookback):
    yf_symbol = symbol.replace("USDT", "-USD") if "USDT" in symbol else symbol
    
    # Herunterladen der Marktdaten im Minutenintervall
    data = yf.download(tickers=yf_symbol, period="1d", interval="1m")
    if not data.empty:
        data = data.rename(columns={"Adj Close": "close"})
        return data.tail(lookback)
    else:
        st.error("Keine Daten von Yahoo Finance verfügbar.")
        return None

# SMA-Berechnung
def calculate_sma(prices, window):
    return pd.Series(prices).rolling(window=window).mean()

# Gewinn/Verlust-Verlauf berechnen
def calculate_profit_loss(prices, initial_investment, volume_percent, fee_percent):
    balance = initial_investment * (volume_percent / 100)
    position = 0
    transaction_history = []
    for i in range(1, len(prices)):
        if prices[i] > prices[i-1]:
            if position == 0:
                position = balance / prices[i]
                balance = 0
        elif prices[i] < prices[i-1] and position > 0:
            sell_value = position * prices[i]
            fee = sell_value * (fee_percent / 100)
            balance = sell_value - fee
            transaction_history.append(balance - initial_investment)
            position = 0
    return transaction_history, balance

# Streamlit-Oberfläche
st.title('Minütliches SMA-Trading-Dashboard mit Zoom- und Investitionsoptionen')

# Benutzerparameter
symbol = st.selectbox('Wähle ein Symbol', ['BTCUSDT', 'ETHUSDT'])
lookback = st.slider('Wähle die Anzahl der Minuten für den Rückblick', min_value=50, max_value=1440, value=500)
short_window = st.slider('Wähle den Zeitraum für die kurze SMA (in Minuten)', min_value=1, max_value=50, value=1)
long_window = st.slider('Wähle den Zeitraum für die lange SMA (in Minuten)', min_value=5, max_value=100, value=29)
fee_percent = st.slider('Wähle den Verkaufsgebührenprozentsatz (%)', min_value=0.0, max_value=5.0, value=0.1, step=0.01)
initial_investment = st.number_input('Anfangsinvestition (in Euro)', min_value=100.0, max_value=10000.0, value=1000.0)
volume_percent = st.slider('Wähle den Prozentsatz des investierten Volumens (%)', min_value=0.0, max_value=100.0, value=80.0, step=1.0)

# Hole Marktdaten von Yahoo Finance
data = get_market_data(symbol, lookback)

if data is not None:
    prices = data['close'].values

    # Berechne SMAs
    sma_short = calculate_sma(prices, short_window)
    sma_long = calculate_sma(prices, long_window)

    # Berechne Gewinn/Verlust-Verlauf
    profit_loss_history, final_balance = calculate_profit_loss(prices, initial_investment, volume_percent, fee_percent)

    # Zoom-Funktion
    zoom_period = st.slider('Wähle den angezeigten Zeitraum (Minuten)', min_value=10, max_value=lookback, value=lookback)

    # Plots: Kursverlauf und SMAs
    st.subheader(f'Kursverlauf und SMAs für {symbol}')
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.plot(data.index[-zoom_period:], prices[-zoom_period:], label='Preis', alpha=0.5)
    ax.plot(data.index[-zoom_period:], sma_short[-zoom_period:], label=f'SMA {short_window} Min', color='green')
    ax.plot(data.index[-zoom_period:], sma_long[-zoom_period:], label=f'SMA {long_window} Min', color='red')
    ax.legend()
    st.pyplot(fig)

    # Ergebnis der Simulation (Gewinn/Verlust)
    st.subheader('Simulationsergebnis')
    st.write(f'Endguthaben nach Simulation: {final_balance:.2f} Euro')
    if len(profit_loss_history) > 0:
        st.write(f'Gewinn/Verlust bei den letzten Transaktionen: {profit_loss_history[-1]:.2f} Euro')

    # Gewinn/Verlust-Plot
    st.subheader('Gewinn/Verlust-Verlauf')
    fig, ax = plt.subplots(figsize=(10, 4))
    ax.plot(profit_loss_history, label='Gewinn/Verlust', color='orange')
    ax.axhline(0, color='black', linestyle='--')
    ax.set_ylabel('Gewinn/Verlust in Euro')
    ax.set_xlabel('Anzahl der Trades')
    ax.legend()
    st.pyplot(fig)
    
else:
    st.error("Keine Daten verfügbar. Überprüfe deine Internetverbindung.")
