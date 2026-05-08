import math
import time
import requests

from bitcoinutils.setup import setup
from bitcoinutils.keys import PrivateKey, P2pkhAddress
from bitcoinutils.transactions import Transaction, TxInput, TxOutput
from bitcoinutils.script import Script

setup("testnet")

API_BASES = [
    "https://blockstream.info/testnet/api",
    "https://mempool.space/testnet/api",
]

SESSION = requests.Session()


def http_get_json(path: str, timeout=(10, 60), retries=3):
    last_err = None
    for base in API_BASES:
        url = f"{base}{path}"
        for attempt in range(retries):
            try:
                r = SESSION.get(url, timeout=timeout)
                r.raise_for_status()
                return r.json()
            except requests.RequestException as e:
                last_err = e
                time.sleep(1.5 * (attempt + 1))
    raise RuntimeError(f"GET failed for {path}: {last_err}")


def http_post_text(path: str, body: str, timeout=(10, 60), retries=3):
    last_err = None
    headers = {"Content-Type": "text/plain"}
    for base in API_BASES:
        url = f"{base}{path}"
        for attempt in range(retries):
            try:
                r = SESSION.post(url, data=body, headers=headers, timeout=timeout)
                r.raise_for_status()
                return r.text.strip()
            except requests.RequestException as e:
                last_err = e
                time.sleep(1.5 * (attempt + 1))
    raise RuntimeError(f"POST failed for {path}: {last_err}")


def get_utxos(address: str):
    return http_get_json(f"/address/{address}/utxo")


def get_fee_rate_sat_vb(target_blocks: int = 6) -> float:
    data = http_get_json("/fee-estimates")
    return float(data.get(str(target_blocks), data.get("6", 2.0)))


def broadcast_tx(rawtx_hex: str) -> str:
    return http_post_text("/tx", rawtx_hex)


def estimate_p2pkh_tx_vbytes(num_inputs: int, num_outputs: int) -> int:
    return 10 + 148 * num_inputs + 34 * num_outputs


def print_available_utxos(utxos):
    print("\nDostępne UTXO do wydania:")
    total = 0
    for i, utxo in enumerate(utxos):
        value = int(utxo["value"])
        total += value
        print(f"[{i}] txid={utxo['txid']}  vout={utxo['vout']}  value={value} sat")
    print(f"Suma wszystkich UTXO: {total} sat")


def choose_utxos_manually(utxos):
    """
    Użytkownik podaje indeksy UTXO, np:
    0
    albo:
    0,2,3
    """
    while True:
        raw = input("\nPodaj indeks(y) UTXO do wydania, np. 0 lub 0,2,3: ").strip()

        try:
            indexes = [int(x.strip()) for x in raw.split(",") if x.strip() != ""]
            if not indexes:
                print("Nie podano żadnego indeksu.")
                continue

            if len(set(indexes)) != len(indexes):
                print("Powtórzono ten sam indeks więcej niż raz.")
                continue

            bad = [i for i in indexes if i < 0 or i >= len(utxos)]
            if bad:
                print(f"Nieprawidłowe indeksy: {bad}")
                continue

            selected = [utxos[i] for i in indexes]
            return selected

        except ValueError:
            print("Błędny format. Użyj np. 0 lub 0,1,2.")


def main():
    sender_wif = "cUMFk8dYRqfe4oYG8RDuZYXDbPsBuaFWMmP4urNKuNkhcq9uWphE"
    #sender_wif ="cREMyB1qGSWoKxNNCMGxrg2tc3NbfFbXAuphDRZrxEAMLN19FGGw"
    recipient_address_str = "n21pZCPm6Fg433HgN6zYoj1XHoNzKE58UK"
    #recipient_address_str = "n1F4cYWCbzN7xFpCsAWo78NWmmjpoMCP59"
    dust_threshold = 546

    sender_priv = PrivateKey.from_wif(sender_wif)
    sender_pub = sender_priv.get_public_key()
    sender_addr = sender_pub.get_address()
    sender_addr_str = sender_addr.to_string()

    print("Sender:", sender_addr_str)

    utxos = get_utxos(sender_addr_str)
    print("UTXO count:", len(utxos))

    if not utxos:
        raise RuntimeError("Brak UTXO na adresie nadawcy")

    print_available_utxos(utxos)

    selected_utxos = choose_utxos_manually(utxos)

    print("\nWybrane UTXO:")
    total_input_value = 0
    
    
    for i, utxo in enumerate(selected_utxos):
        value = int(utxo["value"])
        total_input_value += value
        print(f"[{i}] txid={utxo['txid']}")
        print(f"    vout={utxo['vout']}")
        print(f"    value={value} sat")
    amount_to_send = int(input("Podaj kwotę do wysłania w satoshi: ").strip())
    api_fee_rate = get_fee_rate_sat_vb(6)
    print(f"\nAPI fee rate: {api_fee_rate} sat/vB")
    est_vbytes = estimate_p2pkh_tx_vbytes(len(selected_utxos), 2)
    print(f"  est_vbytes:  {est_vbytes}")

    manual = input("Podaj własne fee rate w sat/vB albo Enter, aby użyć API: ").strip()
    fee_rate = float(manual) if manual else api_fee_rate

    
    fee = math.ceil(fee_rate * est_vbytes)
    change = total_input_value - amount_to_send - fee

    print("\nParametry transakcji:")
    print(f"  fee_rate:    {fee_rate} sat/vB")
    print(f"  est_vbytes:  {est_vbytes}")
    print(f"  fee:         {fee} sat")
    print(f"  total_input: {total_input_value} sat")
    print(f"  send:        {amount_to_send} sat")
    print(f"  change:      {change} sat")

    if total_input_value < amount_to_send + fee:
        raise RuntimeError(
            f"Za mało środków w wybranych UTXO. "
            f"input={total_input_value}, send={amount_to_send}, fee={fee}"
        )

    if change < dust_threshold:
        raise RuntimeError(
            f"Change jest za mały: {change} sat. "
            f"Wybierz większe UTXO albo zmniejsz kwotę wysyłki."
        )

    prev_script_pubkey = sender_addr.to_script_pub_key()

    txins = [TxInput(utxo["txid"], utxo["vout"]) for utxo in selected_utxos]

    recipient_addr = P2pkhAddress(recipient_address_str)
    txout_recipient = TxOutput(amount_to_send, recipient_addr.to_script_pub_key())
    txout_change = TxOutput(change, sender_addr.to_script_pub_key())

    print("\nNowe wyjścia transakcji:")
    print("Odbiorca:")
    print(f"  address: {recipient_address_str}")
    print(f"  value:   {amount_to_send} sat")
    print(f"  script:  {recipient_addr.to_script_pub_key().to_hex()}")

    print("Change:")
    print(f"  address: {sender_addr_str}")
    print(f"  value:   {change} sat")
    print(f"  script:  {sender_addr.to_script_pub_key().to_hex()}")

    tx = Transaction(txins, [txout_recipient, txout_change], has_segwit=False)

    for idx, txin in enumerate(txins):
        signature = sender_priv.sign_input(tx, idx, prev_script_pubkey)
        txin.script_sig = Script([signature, sender_pub.to_hex()])

        print(f"\nScriptSig wejścia {idx}:")
        print(txin.script_sig)
        print("ScriptSig hex:", txin.script_sig.to_hex())

    rawtx = tx.serialize()

    print("\nRaw tx:")
    print(rawtx)

    broadcasted_txid = broadcast_tx(rawtx)
    print("\nBroadcasted txid:", broadcasted_txid)


if __name__ == "__main__":
    main()