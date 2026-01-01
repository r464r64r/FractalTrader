# 📱 FractalTrader - Deployment z iPhone

Kompletny przewodnik deploymentu i zarządzania botem tradingowym używając **tylko iPhone**.

## 🎯 Przegląd

Możesz w pełni zarządzać botem z iPhone poprzez:
1. **SSH Apps** (Termius, Blink) - pełna kontrola terminala
2. **Portainer** (web UI) - zarządzanie kontenerami przez przeglądarkę
3. **GitHub + Actions** (opcjonalne) - CI/CD deployment

---

## 📋 Wymagania

### Na Oracle Cloud:
- ✅ Konto Oracle Cloud (Always Free)
- ✅ VM Instance (VM.Standard.A1.Flex, ARM64)
- ✅ SSH Key pair

### Na iPhone:
- ✅ **Termius** lub **Blink Shell** (SSH client)
  - Termius: https://apps.apple.com/app/termius/id549039908
  - Blink: https://apps.apple.com/app/blink-shell/id1156707581
- ✅ Safari/Chrome (dla Portainer web UI)
- ✅ **Working Copy** (opcjonalnie, dla git)
  - https://apps.apple.com/app/working-copy/id896694807

---

## 🚀 Metoda 1: SSH + Termius (Rekomendowane)

### Krok 1: Konfiguracja Oracle Cloud Instance

1. **Zaloguj się do Oracle Cloud Console** (przez Safari)
   - https://cloud.oracle.com

2. **Utwórz VM Instance:**
   - Compute → Instances → Create Instance
   - Image: **Ubuntu 22.04 Minimal** (ARM64)
   - Shape: **VM.Standard.A1.Flex**
     - OCPUs: 2 (możesz dać więcej, max 4 za free)
     - Memory: 12 GB (możesz dać więcej, max 24GB za free)
   - **Zapisz Private Key** do Files app!

3. **Otwórz porty w Security List:**
   - VCN → Security Lists → Default Security List
   - Dodaj Ingress Rules:
     - Port **22** (SSH)
     - Port **9000** (Portainer)
     - Port **8000** (Portainer Edge)

### Krok 2: Połącz się przez SSH (Termius)

1. **Otwórz Termius** na iPhone

2. **Dodaj nowy host:**
   - Tap `+` → New Host
   - Label: `Oracle Cloud FractalTrader`
   - Hostname: `[TWÓJ_PUBLIC_IP]` (z Oracle Console)
   - Port: `22`
   - Username: `ubuntu`

3. **Dodaj SSH Key:**
   - Keys → `+` → Import
   - Wybierz private key z Files app
   - Przypisz do hosta

4. **Połącz się:**
   - Tap na host → Connect
   - Powinieneś zobaczyć terminal Ubuntu! 🎉

### Krok 3: Instalacja środowiska (jednorazowo)

W terminalu Termius uruchom setup script:

```bash
# Pobierz i uruchom setup script
curl -sSL https://raw.githubusercontent.com/YOUR_REPO/main/deploy/oracle-cloud-setup.sh -o setup.sh
chmod +x setup.sh
./setup.sh
```

Script automatycznie:
- ✅ Zainstaluje Docker i Docker Compose
- ✅ Skonfiguruje swap (2GB)
- ✅ Otworzy porty w firewall
- ✅ Sklonuje repozytorium (jeśli podasz URL)
- ✅ Stworzy plik `.env` z przykładem

**Czas: ~5-10 minut**

### Krok 4: Konfiguracja bota

1. **Edytuj plik .env:**

```bash
cd FractalTrader
nano .env
```

2. **Wypełnij kluczowe wartości:**

```bash
# Strategia
STRATEGY=liquidity_sweep

# Sieć (ZAWSZE testuj na testnet!)
NETWORK=testnet

# Hyperliquid Private Key (z testnet.hyperliquid.xyz)
HYPERLIQUID_PRIVATE_KEY=0x1234567890abcdef...

# Telegram (opcjonalnie)
TELEGRAM_BOT_TOKEN=123456:ABC-DEF...
TELEGRAM_CHAT_ID=123456789
```

3. **Zapisz i wyjdź:**
   - Ctrl+X → Y → Enter (w nano)

### Krok 5: Uruchom bota! 🚀

```bash
# Build i start (first time: ~5-10 min)
docker compose -f docker-compose.cloud.yml up -d

# Sprawdź logi (live)
docker compose -f docker-compose.cloud.yml logs -f

# Sprawdź status bota
docker exec -it fractal-trader-production python -m live.cli status
```

### Krok 6: Zarządzanie (daily operations)

```bash
# Zobacz logi ostatnie 100 linii
docker compose -f docker-compose.cloud.yml logs --tail=100

# Restart bota
docker compose -f docker-compose.cloud.yml restart

# Stop bota
docker compose -f docker-compose.cloud.yml down

# Performance report
docker exec -it fractal-trader-production python -m live.cli report

# Zmień strategię
nano .env  # Zmień STRATEGY=fvg_fill
docker compose -f docker-compose.cloud.yml restart
```

---

## 🌐 Metoda 2: Portainer Web UI (łatwiejsze!)

Portainer daje **web interface** do zarządzania kontenerami - idealne dla iPhone!

### Krok 1: Uruchom Portainer

```bash
# Start Portainer (jednorazowo)
docker compose -f docker-compose.cloud.yml --profile management up -d

# Sprawdź IP serwera
curl -s ifconfig.me
```

### Krok 2: Otwórz w Safari

1. Wpisz w Safari: `http://[TWÓJ_IP]:9000`
2. Pierwsze uruchomienie:
   - Ustaw hasło admina
   - Wybierz "Docker" jako environment
   - Connect to local Docker

### Krok 3: Zarządzaj botem przez przeglądarkę! 🎉

Możesz:
- ✅ **View logs** (Containers → fractal-trader-production → Logs)
- ✅ **Restart/Stop/Start** (Containers → Actions)
- ✅ **Exec into container** (Containers → Console)
- ✅ **Monitor resources** (CPU, RAM, Network)
- ✅ **View stats** (real-time graphs)

**Bonus:** Dodaj zakładkę do Home Screen dla szybkiego dostępu!

---

## 📊 Metoda 3: GitHub Actions (Advanced CI/CD)

Dla zaawansowanych: deploy przez push do GitHub.

### Setup (jednorazowo):

1. **Dodaj secrets do GitHub repo:**
   - Settings → Secrets → Actions
   - `ORACLE_SSH_KEY` (private key)
   - `ORACLE_HOST` (IP serwera)
   - `ORACLE_USER` (ubuntu)

2. **Stwórz `.github/workflows/deploy.yml`:**

```yaml
name: Deploy to Oracle Cloud

on:
  push:
    branches: [ main, production ]
  workflow_dispatch:  # Manual trigger

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Deploy to Oracle Cloud
        uses: appleboy/ssh-action@master
        with:
          host: ${{ secrets.ORACLE_HOST }}
          username: ${{ secrets.ORACLE_USER }}
          key: ${{ secrets.ORACLE_SSH_KEY }}
          script: |
            cd FractalTrader
            git pull
            docker compose -f docker-compose.cloud.yml up -d --build
```

### Użycie z iPhone:

1. **Working Copy app:**
   - Edytuj pliki w repo
   - Commit → Push

2. **GitHub mobile app:**
   - Actions tab
   - Trigger manual deployment

3. **Safari:**
   - GitHub.com → Actions
   - Manually trigger workflow

---

## 🔍 Monitoring i Debugging z iPhone

### 1. Live Logs (Termius)

```bash
# Follow logs w czasie rzeczywistym
docker compose -f docker-compose.cloud.yml logs -f

# Tylko błędy
docker compose -f docker-compose.cloud.yml logs | grep ERROR

# Ostatnie 50 linii
docker compose -f docker-compose.cloud.yml logs --tail=50
```

### 2. Bot Status

```bash
# Pełny status
docker exec -it fractal-trader-production python -m live.cli status

# Performance report
docker exec -it fractal-trader-production python -m live.cli report

# Zapisz report do pliku
docker exec -it fractal-trader-production python -m live.cli report --output /app/logs/report.json
```

### 3. System Resources (Portainer)

- Otwórz `http://[IP]:9000`
- Dashboard → Container stats
- Zobacz CPU, RAM, Network usage

### 4. Telegram Notifications (najłatwiejsze!)

Jeśli skonfigurowałeś Telegram:
- ✅ Otrzymuj alerty o tradach
- ✅ Powiadomienia o błędach
- ✅ Daily performance reports

Wszystko na iPhone Notifications! 🔔

---

## 🛡️ Security Best Practices

### ✅ DO:
- Używaj **strong passwords** dla Portainer
- Trzymaj **private keys bezpiecznie** (iCloud Keychain)
- **Zawsze testuj na testnet** przed mainnet
- Enable **2FA na Oracle Cloud**
- Regularnie **aktualizuj system**:
  ```bash
  sudo apt update && sudo apt upgrade -y
  docker compose -f docker-compose.cloud.yml pull
  docker compose -f docker-compose.cloud.yml up -d
  ```

### ❌ DON'T:
- ❌ NIE commituj `.env` do git
- ❌ NIE udostępniaj `HYPERLIQUID_PRIVATE_KEY`
- ❌ NIE otwieraj portów bez firewall
- ❌ NIE używaj mainnet bez testów
- ❌ NIE zostawiaj default haseł

---

## 🆘 Troubleshooting

### Problem: "Cannot connect to Docker daemon"

```bash
# Dodaj użytkownika do grupy docker
sudo usermod -aG docker $USER

# Wyloguj i zaloguj się ponownie
exit
# (reconnect w Termius)

# Sprawdź
docker ps
```

### Problem: "Out of memory" / OOM Killed

```bash
# Sprawdź swap
free -h

# Zwiększ swap do 4GB
sudo swapoff /swapfile
sudo dd if=/dev/zero of=/swapfile bs=1G count=4
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile

# Zmniejsz resource limits w docker-compose.cloud.yml
nano docker-compose.cloud.yml
# Zmień: memory: 512M
```

### Problem: "Cannot access Portainer"

```bash
# Sprawdź czy Portainer działa
docker ps | grep portainer

# Sprawdź firewall
sudo ufw status

# Dodaj reguły
sudo ufw allow 9000/tcp
sudo ufw allow 8000/tcp
```

### Problem: Bot się crashuje

```bash
# Zobacz pełne logi
docker logs fractal-trader-production

# Sprawdź .env file
cat .env

# Test połączenia z Hyperliquid
docker exec -it fractal-trader-production python -c "
from hyperliquid.info import Info
info = Info('testnet')
print(info.user_state('0x0000000000000000000000000000000000000000'))
"
```

---

## 📈 Workflow: Typowy dzień z iPhone

**Rano (9:00 AM):**
```
1. Otwórz Portainer w Safari
2. Sprawdź Container Stats
3. Przejrzyj logi (ostatnie 12h)
```

**W ciągu dnia:**
```
1. Otrzymuj Telegram notifications
2. Quick check przez Portainer (jeśli coś nie tak)
```

**Wieczorem (9:00 PM):**
```
1. SSH przez Termius
2. Generuj daily report:
   docker exec -it fractal-trader-production python -m live.cli report
3. Zapisz do Google Drive / iCloud (opcjonalnie)
```

**Raz w tygodniu:**
```
1. Update system:
   sudo apt update && sudo apt upgrade -y
2. Pull latest code:
   git pull
3. Rebuild:
   docker compose -f docker-compose.cloud.yml up -d --build
```

---

## 🎓 Tips & Tricks

### 1. Shortcuts w Termius

Stwórz **Snippets** dla często używanych komend:
- `logs` → `docker compose -f docker-compose.cloud.yml logs -f`
- `status` → `docker exec -it fractal-trader-production python -m live.cli status`
- `restart` → `docker compose -f docker-compose.cloud.yml restart`

### 2. Safari Shortcuts

Dodaj Portainer do **Home Screen**:
1. Otwórz `http://[IP]:9000` w Safari
2. Share → Add to Home Screen
3. Nazwa: "FractalTrader Monitor"
4. Teraz masz app-like experience! 📱

### 3. Telegram Bot Commands

Rozważ dodanie Telegram bot commandów:
- `/status` → Bot status
- `/report` → Daily report
- `/restart` → Restart bota (z confirmation)

### 4. iCloud Drive Backups

Backup state files:
```bash
# Skopiuj state file
scp ubuntu@[IP]:~/FractalTrader/.testnet_state.json ~/Downloads/

# Z Termius: Files → Download
# Następnie przenieś do iCloud Drive
```

---

## ✅ Checklist: First Time Setup

- [ ] Utworzyłem Oracle Cloud account
- [ ] Utworzyłem VM instance (ARM64, Ubuntu 22.04)
- [ ] Otworzyłem porty (22, 9000, 8000)
- [ ] Zainstalowałem Termius na iPhone
- [ ] Dodałem SSH key do Termius
- [ ] Połączyłem się z serwerem przez SSH
- [ ] Uruchomiłem `oracle-cloud-setup.sh`
- [ ] Skonfigurowałem `.env` file
- [ ] Zbudowałem i uruchomiłem bota
- [ ] Uruchomiłem Portainer
- [ ] Przetestowałem dostęp przez przeglądarkę
- [ ] (Opcjonalnie) Skonfigurowałem Telegram
- [ ] (Opcjonalnie) Dodałem Portainer do Home Screen

---

## 🚀 Podsumowanie

Zarządzanie botem z iPhone jest **w pełni możliwe** i wygodne:

✅ **Termius/Blink** - full terminal access
✅ **Portainer** - graficzny interface
✅ **Telegram** - notyfikacje i alerty
✅ **GitHub Actions** - automated deployment

**Oracle Cloud Always Free** + **iPhone** = 24/7 trading bot za $0/miesiąc! 💪

---

**Powodzenia w tradingu! 📈**

Masz pytania? Check:
- FractalTrader Docs: `/docs`
- Oracle Cloud Docs: https://docs.oracle.com/cloud
- Termius Guide: https://termius.com/education
