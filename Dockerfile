# Folosim o imagine oficială Python (3.11 slim, mai mică și rapidă)
FROM python:3.11-slim

# Setăm directorul de lucru
WORKDIR /app

# Copiem fișierul requirements.txt mai întâi (dacă există) pentru caching
COPY requirements.txt .

# Instalăm dependențele
RUN pip install --no-cache-dir -r requirements.txt

# Copiem restul codului în container
COPY . .

# Comanda de start pentru bot
CMD ["python", "bot.py"]
