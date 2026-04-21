import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import statsmodels.api as sm
import os

#wczytywanie
PATH = "data/"
FILE_BTC = "BTCUSDT-1s-2026-02.csv"
COLUMNS = [
    'open_time', 'open', 'high', 'low', 'close', 'volume', 
    'close_time', 'quote_asset_volume', 'number_of_trades',
    'taker_buy_base_asset_volume', 'taker_buy_quote_asset_volume', 'ignore'
]

def load_data():
    file_path = os.path.join(PATH, FILE_BTC)
    print(f"Wczytywanie danych z {file_path}...")
    # Wczytujemy tylko cenę zamknięcia
    df = pd.read_csv(file_path, names=COLUMNS, usecols=['close', 'close_time'])
    # Konwersja czasu (mikrosekundy)
    df['close_time'] = pd.to_datetime(df['close_time'], unit='us')
    return df

# 2. Obliczanie logarytmicznych stóp zwrotu
df = load_data()
# R = log(P(t)) - log(P(t-1))
df['log_return'] = np.log(df['close']) - np.log(df['close'].shift(1))
df = df.dropna()

# --- ANALIZA STATYSTYCZNA ---

# A. Rozkłady stóp zwrotu
plt.figure(figsize=(14, 6))

# Histogram
plt.subplot(1, 2, 1)
plt.hist(df['log_return'], bins=150, color='royalblue', density=True, alpha=0.7)
plt.title('Histogram logarytmicznych stóp zwrotu')
plt.xlabel('Stopa zwrotu R')
plt.ylabel('Częstość (Density)')
plt.grid(alpha=0.3)

# Skumulowany rozkład uzupełniający (1 - F_x)
plt.subplot(1, 2, 2)
sorted_data = np.sort(df['log_return'])
ccdf = 1. - np.arange(1, len(sorted_data) + 1) / len(sorted_data)
plt.semilogy(sorted_data, ccdf, color='crimson')
plt.title('Rozkład skumulowany uzupełniający (1-F_x)')
plt.xlabel('Stopa zwrotu R')
plt.ylabel('P(X > x) - skala log')
plt.grid(True, which="both", alpha=0.3)

plt.tight_layout()
plt.show()

# B. Funkcje autokorelacji (ACF)
fig, ax = plt.subplots(1, 2, figsize=(14, 6))

# ACF dla stóp zwrotu
sm.graphics.tsa.plot_acf(df['log_return'], lags=50, ax=ax[0], 
                         title='Autokorelacja (ACF) stóp zwrotu')
ax[0].set_xlabel('Lag [s]')

# ACF dla modułów stóp zwrotu |R|
sm.graphics.tsa.plot_acf(df['log_return'].abs(), lags=50, ax=ax[1], 
                         title='Autokorelacja (ACF) modułów |stóp zwrotu|', color='orange')
ax[1].set_xlabel('Lag [s]')

plt.tight_layout()
plt.show()