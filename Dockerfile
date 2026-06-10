FROM python:3.11-slim AS builder

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends gcc libpq-dev && \
    rm -rf /var/lib/apt/lists/*

COPY requirements-docker.txt ./requirements.txt
RUN pip wheel --no-cache-dir --no-deps --wheel-dir /app/wheels -r requirements.txt

FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends libpq-dev && \
    rm -rf /var/lib/apt/lists/*

COPY --from=builder /app/wheels /wheels
RUN pip install --no-cache-dir /wheels/*

COPY . .

RUN adduser --disabled-password --gecos "" appuser && \
    chown -R appuser:appuser /app && \
    chmod +x start.sh

USER appuser

EXPOSE 5000

CMD ["./start.sh"]
