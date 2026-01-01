FROM python:3.11-slim

WORKDIR /app

# Skopiuj requirements i zainstaluj zależności
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Skopiuj kod aplikacji
COPY app.py .
COPY templates/ templates/

# Ustaw zmienne środowiskowe
ENV PORT=8080
ENV PYTHONUNBUFFERED=1

# Uruchom aplikację przez gunicorn
CMD exec gunicorn --bind :$PORT --workers 1 --threads 8 --timeout 0 app:app
