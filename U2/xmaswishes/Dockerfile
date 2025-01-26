# 1) Wähle ein Python-Image (z. B. 3.12-slim für eine kompaktere Basis)
FROM python:3.12-slim

# 2) Arbeitsverzeichnis in Docker
WORKDIR /app

# 3) Kopiere deine Abhängigkeiten-Konfig. 
#    Falls du requirements.txt hast:
COPY requirements.txt /app/

# 4) Installiere Abhängigkeiten 
RUN pip install --no-cache-dir -r requirements.txt

# 5) Kopiere den Rest des Codes ins Container-Filesystem
COPY . /app

# 6) Definiere den Befehl zum Starten (Flask auf Port 5000)
CMD ["python", "app.py"]
