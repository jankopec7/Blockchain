import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import os

PATH = "data/"
FILES = {
    "btc_usdt": "BTCUSDT-1s-2026-02.csv",
    "eth_btc":  "ETHBTC-1s-2026-02.csv",
    "eth_usdt": "ETHUSDT-1s-2026-02.csv"
}

COLUMNS = [
    'open_time', 'open', 'high', 'low', 'close', 'volume', 
    'close_time', 'quote_asset_volume', 'number_of_trades',
    'taker_buy_base_asset_volume', 'taker_buy_quote_asset_volume', 'ignore'
]

def load_and_clean(pair_name):
    file_path = os.path.join(PATH, FILES[pair_name])
    print(f"Wczytywanie {pair_name}...")
    
    # Wczytujemy jako float, by uniknąć problemów z precyzją przy dużych liczbach
    df = pd.read_csv(file_path, names=COLUMNS, usecols=['close', 'volume', 'close_time'])
    
    # Rozwiązanie problemu: Twoje dane są w mikrosekundach (unit='us')
    # Używamy errors='coerce' na wypadek uszkodzonych rekordów
    df['close_time'] = pd.to_datetime(df['close_time'], unit='us', errors='coerce')
    
    return df

# 1. Przygotowanie danych
df_btc_usdt = load_and_clean("btc_usdt")
df_eth_btc = load_and_clean("eth_btc")
df_eth_usdt = load_and_clean("eth_usdt")

print("Synchronizacja danych (Merge)...")
merged = df_btc_usdt.rename(columns={'close': 'p_btc_usdt', 'volume': 'v_btc_usdt'}).merge(
    df_eth_btc.rename(columns={'close': 'p_eth_btc', 'volume': 'v_eth_btc'}), on='close_time'
).merge(
    df_eth_usdt.rename(columns={'close': 'p_eth_usdt', 'volume': 'v_eth_usdt'}), on='close_time'
)

# 2. Arbitraż Trójkątny (USDT -> BTC -> ETH -> USDT)
FEE = 0.001 
merged['raw_result'] = (1 / merged['p_btc_usdt']) * (1 / merged['p_eth_btc']) * merged['p_eth_usdt']
merged['net_result'] = merged['raw_result'] * ((1 - FEE) ** 3)

# Statystyki
opportunities = merged[merged['net_result'] > 1.0]
print("-" * 30)
print(f"Przeanalizowano sekund: {len(merged)}")
print(f"Okazje powyżej 1.0 (zysk): {len(opportunities)}")
if not opportunities.empty:
    max_profit = (opportunities['net_result'].max() - 1) * 100
    print(f"Maksymalny zysk: {max_profit:.4f}%")

# 3. Arbitraż Między Giełdami (Zadanie 2 - Symulacja)
print("\n--- Analiza Arbitrażu Między Giełdami ---")
np.random.seed(42)
merged['p_other'] = merged['p_btc_usdt'] * (1 + np.random.uniform(-0.003, 0.003, len(merged)))
merged['diff_pct'] = (merged['p_other'] - merged['p_btc_usdt']) / merged['p_btc_usdt']
cross_opps = merged[merged['diff_pct'].abs() > 0.002]
print(f"Znaleziono {len(cross_opps)} różnic > 0.2% między giełdami")

# 4. Wizualizacja
plt.figure(figsize=(12, 6))
plt.plot(merged['close_time'], merged['net_result'], label='Wynik Netto', color='blue', linewidth=0.5)
plt.axhline(y=1.0, color='red', linestyle='--', label='Próg opłacalności')
plt.title('Arbitraż Trójkątny - Binance 2026 (Dane 1s)')
plt.legend()
plt.show()