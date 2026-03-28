# Entegre Playwright ve Python imajını kullanıyoruz (Ubuntu 24.04 tabanlı)
FROM mcr.microsoft.com/playwright/python:v1.48.0-noble

# Calisma dizini
WORKDIR /app

# Sistem bagimliliklarini guncelle
RUN apt-get update && apt-get install -y \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

# Gerekli dosyalari kopyala
COPY requirements.txt .

# Python paketlerini kur
RUN pip install --no-cache-dir -r requirements.txt

# Proje dosyalarini kopyala
COPY . .

# Playwright tarayicilarini (chromium) yukle (imajda olsa da garantiye aliyoruz)
RUN playwright install chromium

# Portu ac
EXPOSE 8000

# API Sunucusunu baslat (Asıl kullanım modu)
CMD ["python", "run.py"]
