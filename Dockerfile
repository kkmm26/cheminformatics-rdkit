FROM python:3.10-slim

# Install ALL required system libraries for RDKit
RUN apt-get update && apt-get install -y \
    libxrender1 \
    libxext6 \
    libsm6 \
    libexpat1 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .

# Upgrade pip (avoids some rdkit wheel issues)
RUN pip install --no-cache-dir --upgrade pip

RUN pip install --no-cache-dir -r requirements.txt

COPY main.py .

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]