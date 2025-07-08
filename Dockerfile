FROM python:3.9

# Erstelle User für besseren Security-Kontext
RUN groupadd --gid 1000 appuser \
    && useradd --uid 1000 --gid 1000 -ms /bin/bash appuser

# System-Pakete
RUN apt-get update && apt-get install -y \
    build-essential \
    software-properties-common \
 && apt-get clean \
 && rm -rf /var/lib/apt/lists/*

# Arbeitsverzeichnis setzen
WORKDIR /home/appuser/app

# Kopiere alles ins Image
COPY . .

# Installiere Python-Abhängigkeiten
RUN pip install --no-cache-dir -r requirements.txt

# Script ausführbar machen
RUN chmod +x run.sh

# Wechsel zum unprivilegierten User
USER appuser

# Exponiere den Port für Streamlit
EXPOSE 8501

# Nutze ENTRYPOINT ohne shell → besseres Signal-Handling
ENTRYPOINT ["./run.sh"]
