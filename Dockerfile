FROM python:3.10-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    libsndfile1 \
    ffmpeg \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --upgrade pip setuptools wheel

COPY requirements.txt .

# Force cache bust
ARG CACHEBUST=2
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN mkdir -p /app/storage
RUN chmod +x start.sh

EXPOSE 8000

CMD ["./start.sh"]
