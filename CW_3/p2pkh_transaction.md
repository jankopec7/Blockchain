# Transakcja P2PKH w sieci testowej Bitcoin

## Czym jest P2PKH?

**P2PKH** (Pay-to-Public-Key-Hash) to najczęściej stosowany typ transakcji w sieci Bitcoin. Środki są zablokowane na **hashu klucza publicznego** odbiorcy, a odblokowanie wymaga podania klucza publicznego i podpisu cyfrowego pasującego do tego hasha.

### Mechanizm blokowania i odblokowywania

#### Locking script — `scriptPubKey` (tworzony przez nadawcę)

```
OP_DUP OP_HASH160 <hash160(pubKey)> OP_EQUALVERIFY OP_CHECKSIG
```

Adres Bitcoin (np. `n21pZCPm6Fg...`) to właśnie `Base58Check(hash160(pubKey))`.

#### Unlocking script — `scriptSig` (tworzony przez wydającego UTXO)

```
<DER-podpis ECDSA> <klucz publiczny>
```

#### Weryfikacja przez węzeł (konkatenacja obu skryptów)

```
<sig> <pubKey> OP_DUP OP_HASH160 <hash160> OP_EQUALVERIFY OP_CHECKSIG
```

Stos Bitcoin VM wykonuje te operacje krok po kroku:

| Krok | Operacja | Stan stosu |
|------|----------|------------|
| 1 | push `<sig>` | `[sig]` |
| 2 | push `<pubKey>` | `[sig, pubKey]` |
| 3 | `OP_DUP` | `[sig, pubKey, pubKey]` |
| 4 | `OP_HASH160` | `[sig, pubKey, hash160(pubKey)]` |
| 5 | push `<hash160>` | `[sig, pubKey, hash160(pubKey), hash160]` |
| 6 | `OP_EQUALVERIFY` | `[sig, pubKey]` (równe — kontynuuj) |
| 7 | `OP_CHECKSIG` | `[TRUE]` |

---

## Struktura skryptu `p2pkh_transaction.py`

### Zależności zewnętrzne

| Biblioteka | Rola |
|-----------|------|
| `bitcoin-utils` | Klucze, skrypty, serializacja transakcji |
| `requests` | HTTP — pobieranie UTXO i broadcast przez API |

### Sekcje skryptu

```
Konfiguracja sieci (testnet)
│
├── Dane nadawcy i odbiorcy (WIF, adres odbiorcy)
│
├── Warstwa sieciowa
│   ├── _get()           — pobieranie JSON z Blockstream / Mempool.space
│   ├── _post()          — broadcast surowej transakcji
│   ├── fetch_utxos()    — lista UTXO na danym adresie
│   ├── fetch_fee_rate() — aktualna stawka opłaty w sat/vB
│   └── broadcast()      — wysłanie hex transakcji do sieci
│
├── estimate_vbytes()    — szacowanie rozmiaru (10 + 148n_in + 34n_out)
│
├── Interfejs użytkownika
│   ├── display_utxos()  — wypisanie listy dostępnych UTXO
│   └── select_utxos()   — interaktywny wybór po indeksach
│
└── main()
    ├── Wyprowadzenie adresu z klucza WIF
    ├── Pobranie UTXO
    ├── Wybór UTXO i kwoty wysyłki
    ├── Obliczenie fee i reszty
    ├── Walidacja (dust, pokrycie)
    ├── Budowa TxInput / TxOutput ze scriptPubKey P2PKH
    ├── Podpisanie każdego wejścia (scriptSig)
    ├── Serializacja → hex
    └── Broadcast + wyświetlenie TXID
```

---

## Wymagania

### Python

Wymagany Python 3.9 lub nowszy.

### Instalacja zależności

```bash
pip install bitcoin-utils requests
```

---

## Konfiguracja przed uruchomieniem

W pliku `p2pkh_transaction.py` na początku funkcji `main()` lub w sekcji stałych zmień:

```python
# Klucz prywatny nadawcy (WIF, sieć testowa — zaczyna się od 'c')
SENDER_WIF = "cUMFk8dYRqfe4oYG8RDuZYXDbPsBuaFWMmP4urNKuNkhcq9uWphE"

# Adres odbiorcy (sieć testowa — zaczyna się od 'm' lub 'n')
RECIPIENT_ADDRESS = "n21pZCPm6Fg433HgN6zYoj1XHoNzKE58UK"
```

> **Ważne:** Klucz WIF w sieci testowej zawsze zaczyna się od litery `c`.  
> Adres testowy zaczyna się od `m` lub `n`.

Aby zdobyć testnet BTC, skorzystaj z faucetu, np. <https://coinfaucet.eu/en/btc-testnet/>.

---

## Uruchomienie

```bash
python p2pkh_transaction.py
```

### Przebieg sesji interaktywnej

```
============================================================
TRANSAKCJA P2PKH — BITCOIN TESTNET
============================================================
Nadawca  : mXXX...
Odbiorca : n21pZCPm6Fg433HgN6zYoj1XHoNzKE58UK

=== Dostępne UTXO ===
  [0]  txid=abc123...  vout=0  50000 sat
  [1]  txid=def456...  vout=1  30000 sat
  Łącznie: 80000 sat

Wybierz indeksy UTXO (np. 0 lub 0,2): 0
Kwota do wysłania [sat]: 10000

Szacowany rozmiar: 192 vB | API fee rate: 1.5 sat/vB
Własne fee rate sat/vB (Enter = użyj API):        ← Enter (akceptuj API)

--- Parametry transakcji ---
  Kwota wysyłki : 10000 sat
  Opłata (fee)  : 288 sat  (1.5 sat/vB × 192 vB)
  Reszta        : 39712 sat
  Suma wejść    : 50000 sat

=== Surowa transakcja (hex) ===
0100000001...

Rozgłosić transakcję? [t/N]: t

✓ Transakcja rozgłoszona!
  TXID    : 7f3a1b...
  Explorer: https://blockstream.info/testnet/tx/7f3a1b...
  Odbiorca: n21pZCPm6Fg433HgN6zYoj1XHoNzKE58UK
```

---

## Weryfikacja w eksploratorze

Po rozgłoszeniu transakcji możesz ją sprawdzić na:

- **Blockstream:** `https://blockstream.info/testnet/tx/<TXID>`
- **Mempool.space:** `https://mempool.space/testnet/tx/<TXID>`

---

## Adres odbiorcy

Transakcja wysyłana jest na adres testnet:

```
n21pZCPm6Fg433HgN6zYoj1XHoNzKE58UK
```

---

## Szacowanie rozmiaru transakcji P2PKH

Skrypt używa uproszczonego wzoru:

```
rozmiar [vB] = 10 + 148 × liczba_wejść + 34 × liczba_wyjść
```

| Składnik | Rozmiar |
|----------|---------|
| Nagłówek (wersja, locktime, liczniki) | 10 B |
| Wejście P2PKH (txid + vout + scriptSig + sequence) | 148 B |
| Wyjście P2PKH (value + scriptPubKey) | 34 B |

Dla standardowej transakcji 1 wejście → 2 wyjścia: **10 + 148 + 68 = 226 vB**.

---

## Zabezpieczenia i ograniczenia

| Kwestia | Obsługa |
|---------|---------|
| Dust threshold | Reszta < 546 sat → błąd (Bitcoin odrzuca takie outputy) |
| Pokrycie środków | Jeśli wejścia < wysyłka + fee → błąd przed podpisem |
| Potwierdzenie broadcast | Skrypt pyta `[t/N]` przed wysłaniem |
| Fallback API | Blockstream → Mempool.space (3 próby z backoffem) |

---

## Słownik

| Termin | Znaczenie |
|--------|-----------|
| UTXO | Unspent Transaction Output — nieodebrane wyjście transakcji |
| WIF | Wallet Import Format — tekstowy zapis klucza prywatnego |
| scriptPubKey | Skrypt blokujący środki (locking script) |
| scriptSig | Skrypt odblokowujący UTXO (unlocking script) |
| sat / satoshi | Najmniejsza jednostka Bitcoin: 1 BTC = 100 000 000 sat |
| dust | Output zbyt mały, by opłacało się go wydać (< 546 sat) |
| vB / vbyte | Wirtualny bajt — jednostka rozmiaru transakcji |
