import requests
import streamlit as st

# Binance API Test Function
def test_binance_data(symbol):
    url = f"https://api.binance.com/api/v3/ticker/24hr?symbol={symbol}"
    response = requests.get(url)
    
    if response.status_code == 200:
        data = response.json()
        return data
    else:
        return None

# Streamlit App Layout
st.title('Binance API Test')

# Test Data Retrieval for Bitcoin (BTC/USDT)
symbol = "BTCUSDT"
data = test_binance_data(symbol)

if data:
    st.success("Daten erfolgreich abgerufen!")
    st.write("Symbol:", symbol)
    st.write("Letzter Preis:", data['lastPrice'])
    st.write("Volumen:", data['volume'])
    st.write("Höchster Preis (24h):", data['highPrice'])
    st.write("Tiefster Preis (24h):", data['lowPrice'])
else:
    st.error("Fehler beim Abrufen der Daten von Binance.")

# Footer
st.write("Dies ist ein einfacher Test der Binance API.")
