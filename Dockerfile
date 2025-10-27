# Usa un'immagine Python ufficiale come base
FROM python:3.13-slim

# Imposta la directory di lavoro nel container
WORKDIR /edi_forecast_app

# Copia i file dei requisiti
COPY requirements.txt .

# Installa le dipendenze
RUN pip install --no-cache-dir -r requirements.txt

# Copia tutto il codice sorgente
COPY . .

# Crea la cartella data se non esiste
#RUN mkdir -p /edi_forecast_app/data

# Espone la porta 8501 per Streamlit
EXPOSE 8501

# Configura Streamlit per accettare connessioni da qualsiasi IP
ENV STREAMLIT_SERVER_ADDRESS=0.0.0.0
ENV STREAMLIT_SERVER_PORT=8501

# Comando per avviare l'applicazione tramite run.py
CMD ["python", "run.py"]