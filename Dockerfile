# Dockerfile
FROM python:3.9-slim

WORKDIR /app

COPY app/requirements.txt requirements.txt
RUN pip install -r requirements.txt

COPY . .
EXPOSE 5000
CMD ["python", "server.py"]