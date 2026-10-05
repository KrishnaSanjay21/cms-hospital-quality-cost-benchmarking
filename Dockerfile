FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app
COPY pyproject.toml README.md ./
COPY src ./src
RUN pip install --no-cache-dir .

COPY config ./config
COPY sql ./sql
COPY scripts ./scripts

ENTRYPOINT ["python", "scripts/run_pipeline.py"]
CMD ["refresh"]

