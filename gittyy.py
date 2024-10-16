import streamlit as st
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import yfinance as yf

# Funktion zur Datenbeschaffung (minütliche Daten von Yahoo Finance)
def get_market_data(symbol, lookback):
    yf_symbol = symbol.replace("USDT", "-USD") if "USDT" in symbol else symbol
    
    # Herunterladen der Marktdaten im Minutenintervall
    data = yf.download(tickers=yf_symbol, period="5d", interval="1m")
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
    balance = initial_investment * (volume_percent / 100)  # 80% des Anfangsinvestments werden investiert
    position = 0
    transaction_history = []
    profit_loss = [initial_investment]  # Beginne mit dem Anfangsinvestitionswert

    for i in range(1, len(prices)):
        # Kauf-Signal: Kurze SMA schneidet lange SMA von unten nach oben
        if prices[i] > sma_short[i] and prices[i-1] <= sma_short[i-1] and position == 0:
            # Kaufe mit 80% des Vermögens
            position = balance / prices[i]
            balance = 0  # Alles wird investiert
            transaction_history.append(f"Kauf bei {prices[i]:.2f} USDT")
        
        # Verkaufs-Signal: Kurze SMA schneidet lange SMA von oben nach unten
        elif prices[i] < sma_short[i] and prices[i-1] >= sma_short[i-1] and position > 0:
            # Verkaufe die Position
            sell_value = position * prices[i]
            fee = sell_value * (fee_percent / 100)  # Berechnung der Gebühr auf den Verkauf
            balance = sell_value - fee
            position = 0  # Position schließen
            transaction_history.append(f"Verkauf bei {prices[i]:.2f} USDT, nach Gebühr: {balance:.2f} USDT")
        
        # Gewinn/Verlust-Berechnung für den aktuellen Tag
        current_balance = balance + (position * prices[i]) if position > 0 else balance
        profit_loss.append(current_balance)
    
    return transaction_history, profit_loss

# Streamlit-Oberfläche
st.title('Minütliches SMA-Trading-Dashboard mit Zoom- und Investitionsoptionen')

# Benutzerparameter
symbol = st.selectbox('Wähle ein Symbol', ['BTCUSDT', 'ETHUSDT'])
lookback = st.slider('Wähle die Anzahl der Minuten für den Rückblick', min_value=50, max_value=1440, value=500)
short_window = st.slider('Wähle den Zeitraum für die kurze SMA (in Minuten)', min_value=1, max_value=50, value=1)
long_window = st.slider('Wähle den Zeitraum für die lange SMA (in Minuten)', min_value=5, max_value=100, value=29)
fee_percent = st.slider('Wähle den Verkaufsgebührenprozentsatz (%)', min_value=0.0, max_value=5.0, value=0.1, step=0.01)
initial_investment = 100.0  # Anfangsinvestition ist immer 100 USDT
volume_percent = st.slider('Wähle den Prozentsatz des investierten Volumens (%)', min_value=0.0, max_value=100.0, value=80.0, step=1.0)

# Hole Marktdaten von Yahoo Finance (letzte 5 Tage, in Minuten)
data = get_market_data(symbol, lookback)

if data is not None:
    prices = data['close'].values

    # Berechne SMAs
    sma_short = calculate_sma(prices, short_window)
    sma_long = calculate_sma(prices, long_window)

    # Berechne Gewinn/Verlust-Verlauf
    transaction_history, profit_loss = calculate_profit_loss(prices, initial_investment, volume_percent, fee_percent)

    # Zoom-Funktion
    zoom_period = st.slider('Wähle den angezeigten Zeitraum (Minuten)', min_value=10, max_value=lookback, value=lookback)

    # Plots: Kursverlauf, SMAs und Gewinn/Verlust
    st.subheader(f'Kursverlauf, SMAs und Gewinn/Verlust für {symbol}')
    fig, ax = plt.subplots(figsize=(10, 6))
    
    # Plot Preis, SMAs und Gewinn/Verlust
    ax.plot(data.index[-zoom_period:], prices[-zoom_period:], label='Preis', alpha=0.5)
    ax.plot(data.index[-zoom_period:], sma_short[-zoom_period:], label=f'SMA {short_window} Min', color='green')
    ax.plot(data.index[-zoom_period:], sma_long[-zoom_period:], label=f'SMA {long_window} Min', color='red')
    ax.plot(data.index[-zoom_period:], profit_loss[-zoom_period:], label='Kapitalentwicklung', color='blue')
    
    ax.set_ylabel('Preis in USDT')
    ax.set_xlabel('Zeit')
    ax.legend()
    st.pyplot(fig)

    # Ergebnis der Simulation (Gewinn/Verlust)
    st.subheader('Simulationsergebnis')
    st.write(f'Endguthaben nach Simulation: {profit_loss[-1]:.2f} USDT')
    st.write(f'Letzte Transaktionen: {transaction_history[-5:] if len(transaction_history) > 5 else transaction_history}')

else:
    st.error("Keine Daten verfügbar. Überprüfe deine Internetverbindung.")
