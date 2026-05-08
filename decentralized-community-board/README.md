# Decentralized Community Board

> Zdecentralizowana tablica ogłoszeń i platforma crowdfundingu na blockchainie Internet Computer (ICP)

**Autorzy:** Jan Kopeć
**Uczelnia:** Politechnika Krakowska · Wydział Informatyki i Matematyki  
**Przedmiot:** Technologia blockchain w nauce i biznesie · Maj 2026

🔗 **Aplikacja live:** https://decentralized-community-board-flr.caffeine.xyz/

---

## O projekcie

Decentralized Community Board (DCB) to w pełni zdecentralizowana aplikacja (dApp) hostowana on-chain na sieci **Internet Computer Protocol (ICP)**. Cały stos technologiczny — backend, frontend i dane — działa wyłącznie na blockchainie, bez żadnego tradycyjnego serwera ani chmury obliczeniowej.

### Dlaczego ICP?

| Cecha | ICP | Ethereum |
|---|---|---|
| Hosting frontendu | On-chain (canister) | IPFS / AWS |
| Szybkość | ~1000 TPS | ~15 TPS |
| Czas finalizacji | 2–4 s | ~15 s |
| Koszt zapisu | Cycles (stała cena) | Gas (zmienna) |
| Autentykacja | Internet Identity (WebAuthn) | MetaMask / zewnętrzny provider |
| HTTP API | Bezpośrednio z kanistra | Wymaga wyroczni |

---

## Funkcjonalności

### 📋 Tablica Ogłoszeń

- **Przeglądanie** bez logowania — lista ogłoszeń i petycji z informacją o autorze (Principal ID) i liczbie podpisów
- **Dodawanie wpisu** — wymaga autentykacji przez Internet Identity; dane zapisywane nieodwracalnie on-chain
- **Podpisywanie petycji** — 1 podpis na użytkownika, limit egzekwowany przez smart kontrakt; autor nie może podpisać własnego wpisu
- **Filtry** — widok wszystkich wpisów, tylko ogłoszeń lub tylko petycji

### 🏦 Skarbonka Grupowa (Crowdfunding)

- **Przeglądanie zbiórek** bez logowania — pasek postępu, cel w tokenach ICP, liczba wpłacających, termin
- **Tworzenie zbiórki** — wymaga logowania; twórca staje się właścicielem on-chain
- **Wpłacanie tokenów** — środki trafiają do escrow zarządzanego przez smart kontrakt
- **Wypłata** — możliwa wyłącznie dla twórcy i tylko po osiągnięciu pełnego celu zbiórki

---

## Architektura

```
Przeglądarka (Chrome / Firefox)
        │  HTTPS
        ▼
Internet Computer (ICP)
  ├── Frontend Canister  ← React + TypeScript (skompilowany do WASM)
  └── Backend Canister   ← Motoko Actor
            │
            ▼
      Stable Memory  ← posty, petycje, zbiórki (trwałe on-chain)

Autentykacja: Internet Identity (WebAuthn / biometria / PIN)
```

### Call types

| Typ | Opis | Koszt | Czas |
|---|---|---|---|
| **Query call** | Odczyt danych | Bezpłatny | Natychmiastowy (ms) |
| **Update call** | Zapis — transakcja blockchain | Cycles | 2–4 sekundy |

---

## Stack technologiczny

### Frontend
- **React 19** + **TypeScript**
- **Tailwind CSS** + **shadcn/ui** (komponenty Radix UI)
- **Vite** — bundler
- **@dfinity/auth-client** — integracja z Internet Identity
- **@icp-sdk/core** — komunikacja z canistrem
- **TanStack Query** — zarządzanie stanem asynchronicznym
- **Biome** — linter i formatter

### Backend (Smart Kontrakt)
- **Motoko** — natywny język ICP, kompiluje się do WebAssembly (WASM)
- Model aktorów z natywnym wsparciem dla współbieżności
- `stable var` — zmienne przeżywające upgrade kanistra

### Infrastruktura
- **Internet Computer Protocol (ICP)** — sieć blockchain
- **Internet Identity** — zdecentralizowana autentykacja bez hasła
- **Caffeine** (caffeine.ai) — CI/CD z automatycznym deploymentem na ICP

---

## Smart kontrakt — Motoko Actor

Plik: [`src/backend/main.mo`](src/backend/main.mo)

### Typy danych

```motoko
type PostCategory = { #Announcement; #Petition };

type Post = {
  id : Nat;
  title : Text;
  description : Text;
  category : PostCategory;
  author : Principal;
  createdAt : Int;
  signatureCount : Nat;
};

type Vault = {
  id : Nat;
  title : Text;
  description : Text;
  targetAmount : Nat;
  currentAmount : Nat;
  deadline : Int;
  creator : Principal;
  createdAt : Int;
  withdrawn : Bool;
  contributorCount : Nat;
};
```

### API kanistra

#### Tablica Ogłoszeń

| Funkcja | Typ | Opis |
|---|---|---|
| `createPost(title, description, category)` | update | Tworzy nowy wpis; zwraca ID |
| `getPosts()` | query | Zwraca wszystkie wpisy |
| `getPost(id)` | query | Zwraca wpis po ID |
| `signPost(postId)` | update | Podpisuje petycję (1/użytkownik) |
| `hasSignedPost(postId)` | query | Sprawdza czy wywołujący już podpisał |

#### Skarbonka Grupowa

| Funkcja | Typ | Opis |
|---|---|---|
| `createVault(title, description, targetAmount, deadline)` | update | Tworzy nową zbiórkę |
| `getVaults()` | query | Zwraca wszystkie zbiórki |
| `getVault(id)` | query | Zwraca zbiórkę po ID |
| `contribute(vaultId, amount)` | update | Wpłaca tokeny do escrow |
| `withdrawVault(vaultId)` | update | Wypłaca środki (tylko twórca, po osiągnięciu celu) |
| `getContributions(vaultId)` | query | Zwraca historię wpłat |

---

## Struktura projektu

```
decentralized-community-board/
├── src/
│   ├── backend/
│   │   ├── main.mo                    # Główny aktor Motoko
│   │   ├── canister.yaml
│   │   └── authorization/
│   │       ├── access-control.mo      # Kontrola dostępu
│   │       └── MixinAuthorization.mo
│   └── frontend/
│       ├── src/
│       │   ├── App.tsx                # Główny komponent aplikacji
│       │   ├── backend.ts             # Bindingi do kanistra
│       │   ├── hooks/
│       │   │   ├── useInternetIdentity.ts
│       │   │   ├── useBackend.ts
│       │   │   ├── usePosts.ts
│       │   │   └── useVaults.ts
│       │   └── components/ui/         # Komponenty shadcn/ui
│       ├── package.json
│       └── vite.config.js
├── icp.yaml                           # Konfiguracja kanisterów ICP
├── caffeine.lock.json
└── package.json
```

---

## Kluczowe pojęcia ICP

| Pojęcie | Opis |
|---|---|
| **Canister** | Podstawowa jednostka obliczeniowa ICP — smart kontrakt z pamięcią, skompilowany do WASM |
| **Internet Identity** | Zdecentralizowana autentykacja oparta na WebAuthn (biometria / PIN) — bez hasła i e-maila |
| **Principal** | Unikalny identyfikator kryptograficzny użytkownika lub kanistra (odpowiednik adresu portfela) |
| **Cycles** | Jednostka obliczeniowa ICP (analogia do gas w Ethereum) — stabilna cenowo |
| **Stable Memory** | Trwała pamięć kanistra przeżywająca upgrade smart kontraktu |

---

## Uruchomienie lokalne

> Projekt jest wdrożony przez **Caffeine** z automatycznym CI/CD. Lokalne środowisko wymaga [DFINITY SDK (`dfx`)](https://internetcomputer.org/docs/current/developer-docs/getting-started/install).

```bash
# Instalacja zależności
pnpm install

# Uruchomienie lokalnego węzła ICP
dfx start --background

# Deploy kanisterów lokalnie
dfx deploy

# Frontend dev server
cd src/frontend && pnpm dev
```

---

## Wnioski

- Pełna dApp na Internet Computer — logika, dane i interfejs on-chain
- Model danych i autentykacji dApp różni się znacznie od tradycyjnych aplikacji webowych
- ICP upraszcza deployment pełnego stosu w porównaniu do Ethereum (brak IPFS, brak zewnętrznych providerów)
- Motoko jest intuicyjny dla programistów znających TypeScript / Swift
- Ograniczenia trybu draft wymuszają testowanie na środowisku produkcyjnym

### Potencjalne rozszerzenia
- Tokenizacja głosów (standard ICRC-1)
- System moderacji DAO
- Notyfikacje przez HTTP outcalls
- Integracja z innymi kanisterami ICP

---

## Linki

- 🌐 [Internet Computer](https://internetcomputer.org)
- 📖 [Dokumentacja Motoko](https://internetcomputer.org/docs/current/motoko/main/motoko)
- 🔑 [Internet Identity](https://identity.ic0.app)
- ⚡ [Caffeine CI/CD](https://caffeine.ai)
