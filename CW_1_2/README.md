# Analiza Arbitrażu i Statystyk Rynku Kryptowalutowego

**Kurs:** Blockchain w Nauce i Biznesie  
**Autor:** Jan Kopeć  
**Dane:** Binance, luty 2026, interwał 1s (BTC/USDT, ETH/BTC, ETH/USDT)

---

## Opis

Repozytorium zawiera dwa ćwiczenia z analizy rynku kryptowalutowego przy użyciu danych wysokiej częstotliwości (tick 1s) z giełdy Binance.

---

## Ćwiczenie 1 — Analiza Arbitrażu Kryptowalutowego

**Skrypt:** `crypto_arbitrage_v1.py`

### Cel
Zbadanie efektywności rynkowej Binance poprzez wyszukiwanie anomalii cenowych umożliwiających arbitraż.

### Metody

**1. Arbitraż trójkątny (Triangular Arbitrage)**  
Strategia USDT → BTC → ETH → USDT. Zysk netto z uwzględnieniem prowizji 0,1% na każdej z trzech wymian:

```
raw_result  = (1 / P_BTC_USDT) * (1 / P_ETH_BTC) * P_ETH_USDT
net_result  = raw_result * (1 - 0.001)^3
```

**2. Arbitraż międzygiełdowy (Cross-Exchange, symulacja)**  
Porównanie ceny BTC/USDT z Binance z symulowaną ceną na innej giełdzie (losowe odchylenie ±0,3%). Wykrycie różnic > 0,2%.

### Wyniki (luty 2026, 2 419 200 próbek)

| Metryka | Wartość |
|---|---|
| Przeanalizowanych sekund | 2 419 200 |
| Okazje arb. trójkątnego (net > 1.0) | **1** |
| Maksymalny zysk netto | **0,0449%** |
| Różnice międzygiełdowe > 0,2% | **804 986** |

### Wnioski
- **Wysoka efektywność Binance** — tylko 1 realna okazja w ciągu miesiąca; systemy HFT eliminują nieefektywności niemal natychmiastowo.
- **Prowizje jako bariera** — koszt 0,1% × 3 transakcje sprawia, że większość spreadów jest nieopłacalna.
- **Arbitraż międzygiełdowy** — znacznie częstszy, ale w praktyce ograniczony przez czas transferu środków i opłaty sieciowe.

---

## Ćwiczenie 2 — Statystyczna Analiza Stóp Zwrotu BTC

**Skrypt:** `analysis_v1.py`

### Cel
Analiza statystyczna logarytmicznych stóp zwrotu i autokorelacji szeregów czasowych BTC/USDT.

### Metodologia

Logarytmiczne stopy zwrotu:

```
R(t) = log(P(t + Δt)) - log(P(t))
```

### Przeprowadzone analizy

**A. Rozkład stóp zwrotu**
- Histogram z estymacją gęstości
- Uzupełniający rozkład skumulowany CCDF w skali logarytmicznej: `1 - F(x)`

**B. Funkcje autokorelacji (ACF)**
- ACF dla stóp zwrotu `R` (50 lagów)
- ACF dla modułów stóp zwrotu `|R|` (50 lagów)

### Wyniki i interpretacja

| Wykres | Obserwacja | Wniosek |
|---|---|---|
| Histogram | Ekstremalna koncentracja przy 0, „grube ogony" | Gwałtowne skoki cen częstsze niż w rozkładzie normalnym |
| CCDF (log) | Linia nie opada pionowo | Prawa potęgowe — duże ruchy to stały element rynku |
| ACF `R` | Słupki opadają do 0 natychmiast | Kierunek ceny w kolejnej sekundzie jest losowy |
| ACF `\|R\|` | Słupki długo pozostają wysokie | Grupowanie zmienności (volatility clustering) — „pamięć" rynku |

### Wnioski końcowe
1. **Brak krótkookresowego trendu** — zmiany ceny BTC na poziomie 1s są czysto losowe.
2. **Ekstremalne ryzyko** — standardowe modele (normalność) zaniżają ryzyko; grube ogony to norma.
3. **Skupiska zmienności** — po dużym ruchu cenowym należy oczekiwać kolejnych gwałtownych wahań.

---

## Struktura plików

```
CW_1_2/
├── crypto_arbitrage_v1.py   # Ćw. 1: arbitraż trójkątny i międzygiełdowy
├── analysis_v1.py           # Ćw. 2: rozkłady stóp zwrotu i ACF
├── images/
│   ├── plot1.png            # Wykres rentowności arbitrażu trójkątnego
│   └── plot2.png            # Wykresy rozkładów i autokorelacji
├── data/                    # Ignorowany przez git — pobierz ręcznie
│   ├── BTCUSDT-1s-2026-02.csv
│   ├── ETHBTC-1s-2026-02.csv
│   └── ETHUSDT-1s-2026-02.csv
└── .gitignore
```

> Pliki CSV w katalogu `data/` nie są śledzone przez git (rozmiar ~100 MB+). Dane można pobrać z [Binance Data Vision](https://data.binance.vision/).

---

## Wymagania

```bash
pip install pandas numpy matplotlib statsmodels
```

## Uruchomienie

```bash
# Ćwiczenie 1 — arbitraż
python3 crypto_arbitrage_v1.py

# Ćwiczenie 2 — analiza statystyczna
python3 analysis_v1.py
```

Skrypty wymagają plików CSV w katalogu `data/` względem miejsca uruchomienia.
