FROM python:3.11-slim
WORKDIR /app
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
COPY loader.py /app/loader.py
# This service is inert by default; it's a safe helper container that just idles.
# Use `docker compose exec gibson python /app/loader.py <path>` to run the safe extractor.
CMD ["bash", "-lc", "sleep infinity"]
