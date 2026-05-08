"""
Transakcja P2PKH (Pay-to-Public-Key-Hash) w sieci testowej Bitcoin.

Schemat locking script (scriptPubKey):
    OP_DUP OP_HASH160 <pubKeyHash> OP_EQUALVERIFY OP_CHECKSIG

Schemat unlocking script (scriptSig):
    <signature> <pubKey>
"""

import math
import time
import requests

from bitcoinutils.setup import setup
from bitcoinutils.keys import PrivateKey, P2pkhAddress
from bitcoinutils.transactions import Transaction, TxInput, TxOutput
from bitcoinutils.script import Script

# ── Konfiguracja sieci ────────────────────────────────────────────────────────

setup("testnet")

# ── Dane nadawcy i odbiorcy ───────────────────────────────────────────────────

# Klucz prywatny nadawcy w formacie WIF (Wallet Import Format)
SENDER_WIF = "cUMFk8dYRqfe4oYG8RDuZYXDbPsBuaFWMmP4urNKuNkhcq9uWphE"

# Adres odbiorcy w sieci testowej
RECIPIENT_ADDRESS = "n21pZCPm6Fg433HgN6zYoj1XHoNzKE58UK"

# Minimalny próg dust (poniżej Bitcoin odrzuca output jako "kurz")
DUST_THRESHOLD_SAT = 546

# ── Warstwa sieciowa ─────────────────────────────────────────────────────────

API_BASES = [
    "https://blockstream.info/testnet/api",
    "https://mempool.space/testnet/api",
]

_session = requests.Session()


def _get(path: str, retries: int = 3):
    last_err = None
    for base in API_BASES:
        for attempt in range(retries):
            try:
                r = _session.get(f"{base}{path}", timeout=(10, 60))
                r.raise_for_status()
                return r.json()
            except requests.RequestException as e:
                last_err = e
                time.sleep(1.5 * (attempt + 1))
    raise RuntimeError(f"GET {path} nie powiódł się: {last_err}")


def _post(path: str, body: str, retries: int = 3) -> str:
    last_err = None
    for base in API_BASES:
        for attempt in range(retries):
            try:
                r = _session.post(
                    f"{base}{path}",
                    data=body,
                    headers={"Content-Type": "text/plain"},
                    timeout=(10, 60),
                )
                r.raise_for_status()
                return r.text.strip()
            except requests.RequestException as e:
                last_err = e
                time.sleep(1.5 * (attempt + 1))
    raise RuntimeError(f"POST {path} nie powiódł się: {last_err}")


def fetch_utxos(address: str) -> list:
    return _get(f"/address/{address}/utxo")


def fetch_fee_rate(target_blocks: int = 6) -> float:
    data = _get("/fee-estimates")
    return float(data.get(str(target_blocks), 2.0))


def broadcast(raw_hex: str) -> str:
    return _post("/tx", raw_hex)


# ── Szacowanie rozmiaru transakcji ───────────────────────────────────────────

def estimate_vbytes(n_inputs: int, n_outputs: int) -> int:
    # Wzór dla P2PKH (nieskompresowany legacy):
    # nagłówek: 10 B  |  wejście: 148 B  |  wyjście: 34 B
    return 10 + 148 * n_inputs + 34 * n_outputs


# ── Interfejs użytkownika ────────────────────────────────────────────────────

def display_utxos(utxos: list) -> None:
    print("\n=== Dostępne UTXO ===")
    total = 0
    for i, u in enumerate(utxos):
        v = int(u["value"])
        total += v
        print(f"  [{i}]  txid={u['txid']}  vout={u['vout']}  {v} sat")
    print(f"  Łącznie: {total} sat\n")


def select_utxos(utxos: list) -> list:
    """Użytkownik wybiera UTXO po indeksach (np. 0 lub 0,2,3)."""
    while True:
        raw = input("Wybierz indeksy UTXO (np. 0 lub 0,2): ").strip()
        try:
            indices = [int(x) for x in raw.split(",") if x.strip()]
            if not indices:
                print("Nie podano indeksu.")
                continue
            if len(set(indices)) != len(indices):
                print("Powtórzone indeksy.")
                continue
            invalid = [i for i in indices if not (0 <= i < len(utxos))]
            if invalid:
                print(f"Nieprawidłowe indeksy: {invalid}")
                continue
            return [utxos[i] for i in indices]
        except ValueError:
            print("Błędny format — użyj cyfr oddzielonych przecinkami.")


# ── Główna logika transakcji ──────────────────────────────────────────────────

def main():
    # 1. Wyprowadź klucz publiczny i adres nadawcy z klucza prywatnego WIF
    sender_priv = PrivateKey.from_wif(SENDER_WIF)
    sender_pub  = sender_priv.get_public_key()
    sender_addr = sender_pub.get_address()          # P2PKH — hash160(pubKey)
    sender_addr_str = sender_addr.to_string()

    print("=" * 60)
    print("TRANSAKCJA P2PKH — BITCOIN TESTNET")
    print("=" * 60)
    print(f"Nadawca  : {sender_addr_str}")
    print(f"Odbiorca : {RECIPIENT_ADDRESS}")

    # 2. Pobierz UTXO nadawcy z API
    utxos = fetch_utxos(sender_addr_str)
    if not utxos:
        raise SystemExit("Brak UTXO na adresie nadawcy. Doładuj portfel testnet BTC.")
    display_utxos(utxos)

    # 3. Wybór UTXO do wydania
    chosen = select_utxos(utxos)
    total_input = sum(int(u["value"]) for u in chosen)
    print(f"\nWybrano {len(chosen)} UTXO, łączna wartość: {total_input} sat")

    # 4. Kwota do wysłania
    amount_sat = int(input("Kwota do wysłania [sat]: ").strip())

    # 5. Szacowanie opłaty
    api_rate = fetch_fee_rate()
    vbytes   = estimate_vbytes(len(chosen), 2)   # 2 wyjścia: odbiorca + reszta
    print(f"\nSzacowany rozmiar: {vbytes} vB | API fee rate: {api_rate} sat/vB")

    manual = input("Własne fee rate sat/vB (Enter = użyj API): ").strip()
    fee_rate = float(manual) if manual else api_rate
    fee      = math.ceil(fee_rate * vbytes)
    change   = total_input - amount_sat - fee

    print(f"\n--- Parametry transakcji ---")
    print(f"  Kwota wysyłki : {amount_sat} sat")
    print(f"  Opłata (fee)  : {fee} sat  ({fee_rate} sat/vB × {vbytes} vB)")
    print(f"  Reszta        : {change} sat")
    print(f"  Suma wejść    : {total_input} sat")

    # 6. Walidacja
    if total_input < amount_sat + fee:
        raise SystemExit(f"Za mało środków: potrzeba {amount_sat + fee} sat, dostępne {total_input} sat.")
    if change < DUST_THRESHOLD_SAT:
        raise SystemExit(
            f"Reszta ({change} sat) poniżej progu dust ({DUST_THRESHOLD_SAT} sat). "
            "Zwiększ UTXO lub zmniejsz kwotę wysyłki."
        )

    # 7. Budowa transakcji
    #    Locking script (scriptPubKey) P2PKH:
    #      OP_DUP OP_HASH160 <hash160(pubKey)> OP_EQUALVERIFY OP_CHECKSIG
    recipient_addr = P2pkhAddress(RECIPIENT_ADDRESS)

    txins = [TxInput(u["txid"], u["vout"]) for u in chosen]
    txouts = [
        TxOutput(amount_sat, recipient_addr.to_script_pub_key()),   # → odbiorca
        TxOutput(change,     sender_addr.to_script_pub_key()),      # → reszta do nadawcy
    ]

    tx = Transaction(txins, txouts, has_segwit=False)

    # 8. Podpisywanie wejść (budowa scriptSig)
    #    Unlocking script (scriptSig) P2PKH:
    #      <DER-signature> <compressed-pubKey>
    prev_script = sender_addr.to_script_pub_key()
    for idx, txin in enumerate(txins):
        sig = sender_priv.sign_input(tx, idx, prev_script)
        txin.script_sig = Script([sig, sender_pub.to_hex()])

    # 9. Serializacja i broadcast
    raw_hex = tx.serialize()

    print("\n=== Surowa transakcja (hex) ===")
    print(raw_hex)

    print("\n=== Skrypty wejść ===")
    for idx, txin in enumerate(txins):
        print(f"  wejście {idx}: {txin.script_sig.to_hex()}")

    print("\n=== Skrypty wyjść ===")
    print(f"  scriptPubKey odbiorcy : {recipient_addr.to_script_pub_key().to_hex()}")
    print(f"  scriptPubKey nadawcy  : {sender_addr.to_script_pub_key().to_hex()}")

    confirm = input("\nRozgłosić transakcję? [t/N]: ").strip().lower()
    if confirm != "t":
        print("Anulowano — transakcja nie została wysłana.")
        return

    txid = broadcast(raw_hex)
    print(f"\n✓ Transakcja rozgłoszona!")
    print(f"  TXID    : {txid}")
    print(f"  Explorer: https://blockstream.info/testnet/tx/{txid}")
    print(f"  Odbiorca: {RECIPIENT_ADDRESS}")


if __name__ == "__main__":
    main()
