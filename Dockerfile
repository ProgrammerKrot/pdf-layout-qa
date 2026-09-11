FROM python:3.11-slim

RUN apt-get update && apt-get install -y --no-install-recommends \
    poppler-utils \
    curl \
    libgl1 \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt pyproject.toml README.md ./
COPY src ./src
COPY samples ./samples

RUN pip install --no-cache-dir -r requirements.txt && pip install --no-cache-dir -e .

ENV PYTHONUNBUFFERED=1
ENV LAYOUT_SERVICE_URL=http://layout:5060

CMD ["python", "-m", "pdfqa"]
