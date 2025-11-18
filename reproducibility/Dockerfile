FROM python:3.13-slim

WORKDIR /app
ENV PYTHONUNBUFFERED=1

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        build-essential \
        libffi-dev \
        git && \
    rm -rf /var/lib/apt/lists/*

COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copiar carpetas (basado en su ubicación real dentro de reproducibility)
COPY Project /app/Project
COPY data /app/data
COPY models /app/models
COPY .dvc /app/.dvc

ENTRYPOINT ["python"]
