FROM python:3.11-slim AS builder

WORKDIR /build
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir --user -r requirements.txt

FROM python:3.11-slim

LABEL maintainer="sara.beck.dev@gmail.com" \
      description="Layering Detection System" \
      version="1.0.0"

WORKDIR /app

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PATH=/home/appuser/.local/bin:$PATH

RUN useradd -m -u 1000 appuser && \
    mkdir -p data output logs && \
    chown -R appuser:appuser /app

COPY --from=builder --chown=appuser:appuser /root/.local /home/appuser/.local
COPY --chown=appuser:appuser setup.py README.md ./
COPY --chown=appuser:appuser src/ ./src/

USER appuser
RUN pip install --no-cache-dir -e .

CMD ["layering-detector"]