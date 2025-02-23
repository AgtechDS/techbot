# Usa un'immagine base di Python
FROM python:3.9-slim

# Imposta la directory di lavoro
WORKDIR /app

# Copia i file necessari
COPY . .

# Installa le dipendenze
RUN pip install -r requirements.txt

# Comando per avviare il bot
CMD ["python", "bot.py"]
