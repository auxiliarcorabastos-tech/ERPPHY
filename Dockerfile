FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    POETRY_VIRTUALENVS_CREATE=false

# Dependencias del sistema para cryptography y compilación si hace falta
RUN apt-get update && apt-get install -y --no-install-recommends \
        build-essential \
        gcc \
        libssl-dev \
        libffi-dev \
        rustc \
        cargo \
    && rm -rf /var/lib/apt/lists/*

# Asegurar pip/setuptools/wheel
RUN python -m pip install --upgrade pip setuptools wheel

WORKDIR /app
COPY requirements.txt .

# Preferir ruedas binarias y evitar cache
RUN pip install --no-cache-dir --prefer-binary -r requirements.txt

COPY . .

# Render usa $PORT; bind a 0.0.0.0
ENV PORT 8000
CMD ["gunicorn", "app:app", "--bind", "0.0.0.0:${PORT}"]
