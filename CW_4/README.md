# 🌐 Hello World Smart Contract — Sepolia Testnet

Deployment prostego smart contractu w Solidity na testowej sieci Ethereum **Sepolia**, z użyciem Hardhat + Alchemy + MetaMask.

> 📚 Ćwiczenie 4 — przedmiot: Technologie Blockchain

---

## 📋 Spis treści

- [Wymagania wstępne](#-wymagania-wstępne)
- [Krok 1 — Konfiguracja kont](#krok-1--konfiguracja-kont)
- [Krok 2 — Instalacja środowiska](#krok-2--instalacja-środowiska)
- [Krok 3 — Konfiguracja projektu](#krok-3--konfiguracja-projektu)
- [Krok 4 — Smart Contract](#krok-4--smart-contract)
- [Krok 5 — Deployment](#krok-5--deployment)
- [Krok 6 — Weryfikacja](#krok-6--weryfikacja)
- [Alternatywa — Remix IDE](#-alternatywa--remix-ide)
- [Deployment info](#-deployment-info)
- [Technologie](#-technologie)

---

## ✅ Wymagania wstępne

- [ ] Konto na [Alchemy](https://alchemy.com)
- [ ] Portfel [MetaMask](https://metamask.io) z testowymi ETH na sieci Sepolia
- [ ] [Node.js](https://nodejs.org) (wersja LTS)
- [ ] Testowe ETH z faucet: [sepolia-faucet.pk910.de](https://sepolia-faucet.pk910.de)

---

## Krok 1 — Konfiguracja kont

### Alchemy
1. Załóż konto na [alchemy.com](https://alchemy.com)
2. Utwórz nową aplikację → wybierz sieć **Ethereum Sepolia**
3. Skopiuj **HTTP API Key URL** — będzie potrzebny w `.env`

### MetaMask
1. Zainstaluj rozszerzenie [MetaMask](https://metamask.io)
2. Utwórz portfel i przełącz sieć na **Sepolia Testnet**
3. Skopiuj **adres portfela** i **klucz prywatny** (`Settings → Security → Export Private Key`)

> ⚠️ **Nigdy nie udostępniaj klucza prywatnego ani nie commituj go do repozytorium!**

### Testowe ETH (Faucet)
Wejdź na [sepolia-faucet.pk910.de](https://sepolia-faucet.pk910.de), wklej adres portfela i poczekaj ~10 minut.

---

## Krok 2 — Instalacja środowiska

```bash
# Sprawdź Node.js
node -v
npm -v

# Utwórz folder projektu
mkdir hello-world && cd hello-world

# Zainicjuj projekt
npm init -y

# Zainstaluj Hardhat
npm install --save-dev hardhat

# Utwórz projekt Hardhat (wybierz: Create a JavaScript project → Enter x3)
npx hardhat init

# Zainstaluj zależności
npm install dotenv @nomiclabs/hardhat-ethers ethers
```

---

## Krok 3 — Konfiguracja projektu

### Plik `.env`

Utwórz plik `.env` w katalogu głównym projektu:

```env
API_URL = "https://eth-sepolia.g.alchemy.com/v2/TWÓJ_KLUCZ_ALCHEMY"
PRIVATE_KEY = "TWÓJ_KLUCZ_PRYWATNY_METAMASK"
```

### Plik `.gitignore`

```gitignore
node_modules
.env
```

### `hardhat.config.js`

Zastąp całą zawartość pliku:

```javascript
require('dotenv').config();
require('@nomiclabs/hardhat-ethers');

const { API_URL, PRIVATE_KEY } = process.env;

module.exports = {
  solidity: '0.8.0',
  defaultNetwork: 'sepolia',
  networks: {
    hardhat: {},
    sepolia: {
      url: API_URL,
      accounts: [`0x${PRIVATE_KEY}`]
    }
  }
};
```

---

## Krok 4 — Smart Contract

Usuń domyślne pliki z folderu `contracts/` i utwórz plik `contracts/HelloWorld.sol`:

```solidity
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract HelloWorld {
    string public message = "Hello World!";

    constructor(string memory initMessage) {
        message = initMessage;
    }

    function update(string memory newMessage) public {
        message = newMessage;
    }
}
```

Skompiluj kontrakt:

```bash
npx hardhat compile
# → Compiled 1 Solidity file successfully
```

---

## Krok 5 — Deployment

Usuń domyślne pliki z folderu `scripts/` i utwórz plik `scripts/deploy.js`:

```javascript
async function main() {
  const HelloWorld = await ethers.getContractFactory('HelloWorld');
  console.log('Deploying contract...');

  const helloWorld = await HelloWorld.deploy('Hello World!');
  console.log('Contract deployed to address:', helloWorld.address);
}

main().catch((error) => {
  console.error(error);
  process.exit(1);
});
```

Uruchom deployment (upewnij się, że masz testowe ETH w portfelu!):

```bash
npx hardhat run scripts/deploy.js --network sepolia
```

Przykładowy wynik:

```
Deploying contract...
Contract deployed to address: 0xABC123...
```

Skopiuj i zachowaj wydrukowany adres kontraktu.

---

## Krok 6 — Weryfikacja

1. Wejdź na [sepolia.etherscan.io](https://sepolia.etherscan.io)
2. Wklej adres kontraktu w wyszukiwarkę
3. Sprawdź zakładkę **Contract** — powinieneś widzieć transakcję deployment

---

## 🔀 Alternatywa — Remix IDE

Jeśli nie chcesz konfigurować Node.js i Hardhat, możesz użyć **Remix IDE** bezpośrednio w przeglądarce:

1. Wejdź na [remix.ethereum.org](https://remix.ethereum.org)
2. Utwórz nowy plik `HelloWorld.sol` i wklej kod kontraktu z Kroku 4
3. Przejdź do zakładki **Solidity Compiler** → wybierz wersję `0.8.0` → kliknij **Compile**
4. Przejdź do zakładki **Deploy & Run** → Environment: **Injected Provider (MetaMask)**
5. Upewnij się, że MetaMask jest na sieci **Sepolia**
6. W polu konstruktora wpisz `Hello World!` → kliknij **Deploy** → potwierdź w MetaMask
7. Skopiuj adres kontraktu z sekcji **Deployed Contracts**

---

## 📦 Deployment info

| | |
|---|---|
| **Sieć** | Sepolia Testnet |
| **Adres kontraktu** | [`0x86B254007a4D7d7074e147a56e934b0ABDEde836`](https://sepolia.etherscan.io/address/0x86B254007a4D7d7074e147a56e934b0ABDEde836) |
| **Transaction hash** | [`0xc192820f...c024f66eff`](https://sepolia.etherscan.io/tx/0xc192820ff632dc1a913ee479729ac73c9a4c2a124218b1f45aead7c024f66eff) |
| **Blok** | [10813886](https://sepolia.etherscan.io/block/10813886) |
| **Data deployu** | 2026-05-08 |
| **Kompilator** | Solidity `0.8.0` |
| **Narzędzie** | Remix IDE |
| **Weryfikacja** | ✅ Sourcify, ✅ Blockscout |

---

## 🛠 Technologie

![Solidity](https://img.shields.io/badge/Solidity-0.8.0-363636?logo=solidity)
![Remix](https://img.shields.io/badge/Remix-IDE-1a1a2e?logo=remix)
![Ethereum](https://img.shields.io/badge/Ethereum-Sepolia-3C3C3D?logo=ethereum)
![MetaMask](https://img.shields.io/badge/MetaMask-F6851B?logo=metamask&logoColor=white)
![Verified](https://img.shields.io/badge/Verified-Sourcify%20%2B%20Blockscout-brightgreen)

---

## 📚 Przydatne linki

- [Alchemy Quickstart Guide](https://docs.alchemy.com/docs/alchemy-quickstart-guide)
- [How to deploy a Smart Contract to Sepolia](https://www.alchemy.com/docs/how-to-deploy-a-smart-contract-to-the-sepolia-testnet)
- [Sepolia Faucet](https://sepolia-faucet.pk910.de)
- [Remix IDE](https://remix.ethereum.org)
- [QuickNode Hello World Guide](https://www.quicknode.com/guides/ethereum-development/smart-contracts/how-to-create-a-hello-world-smart-contract-with-solidity)
- [Sepolia Etherscan](https://sepolia.etherscan.io)
