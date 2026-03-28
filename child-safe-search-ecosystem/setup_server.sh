#!/bin/bash

# Deep Search Ecosystem - Sunucu Kurulum Scripti (Linux)
echo "--- Proje Dagıtımı Baslatılıyor ---"

# 1. Docker kurulu mu kontrol et
if ! command -v docker &> /dev/null
then
    echo "Docker bulunamadı. Kurulum baslıyor..."
    sudo apt-get update
    sudo apt-get install -y ca-certificates curl gnupg lsb-release
    sudo mkdir -p /etc/apt/keyrings
    curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg
    echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
    sudo apt-get update
    sudo apt-get install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
fi

# 2. Docker Compose v2 kontrolu (Modern sistemlerde artik plugin olarak geliyor)
if ! docker compose version &> /dev/null
then
    echo "Docker Compose eklentisi bulunamadı. Lutfen 'docker-compose' veya 'docker compose' komutunun calıstıgından emin olun."
fi

# 3. .env Dosyası Kontrolü
if [ ! -f .env ]; then
    echo "HATA: .env dosyası bulunamadı! Lutfen sunucuya kopyaladıgınızdan emin olun."
    exit 1
fi

# 4. Sistemi Ayaga Kaldır
echo "Konuteynerler olusturuluyor ve baslatılıyor (Arka planda)..."
sudo docker compose up -d --build

echo "--- KURULUM TAMAMLANDI! ---"
echo "API sunucusu http://0.0.0.0:8000 adresinde calısıyor."
echo "Logları izlemek için: sudo docker compose logs -f"
