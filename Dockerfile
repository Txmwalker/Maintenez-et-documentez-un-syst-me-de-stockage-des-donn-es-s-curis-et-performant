FROM python:3.11-slim

WORKDIR /app

# Installation des dépendances
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Le code sera monté via le volume dans docker-compose, ou copié si exécuté hors compose
COPY . .