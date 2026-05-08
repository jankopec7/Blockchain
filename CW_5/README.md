# 💸 Ethereum Transaction — Sepolia Testnet

Wysyłanie transakcji ETH na sieci testowej Sepolia przy użyciu ethers.js i Alchemy.

>  Ćwiczenie 5 — Blockchain w Nauce i Biznesie

## Uruchomienie

```bash
npm install
node send_transaction.js
```

## .env

```env
API_URL=https://eth-sepolia.g.alchemy.com/v2/TWÓJ_KLUCZ
PRIVATE_KEY=TWÓJ_KLUCZ_PRYWATNY
```

## Wyniki

| | |
|---|---|
| **TX Hash** | `0xa6ba4d958fb24421c00a572072a71a6f0e77690704b5497486a4414750bef6a7` |
| **Sieć** | Sepolia Testnet |
| **Wartość** | 0.001 ETH |
| **Status** | ✅ Success |
| **Etherscan** | [Zobacz transakcję](https://sepolia.etherscan.io/tx/0xa6ba4d958fb24421c00a572072a71a6f0e77690704b5497486a4414750bef6a7) |

## Technologie

![Node.js](https://img.shields.io/badge/Node.js-v26-339933?logo=node.js)
![ethers.js](https://img.shields.io/badge/ethers.js-6.x-blue)
![Ethereum](https://img.shields.io/badge/Ethereum-Sepolia-3C3C3D?logo=ethereum)
![Alchemy](https://img.shields.io/badge/Alchemy-RPC-363FF9)