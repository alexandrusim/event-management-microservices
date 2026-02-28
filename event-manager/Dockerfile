FROM python:3.9-slim


WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt


RUN groupadd -r appgroup && useradd -r -g appgroup -d /home/appuser -m appuser

COPY . .


RUN chown -R appuser:appgroup /app

USER appuser
