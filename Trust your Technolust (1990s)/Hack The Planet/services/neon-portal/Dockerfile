FROM python:3.11-slim
WORKDIR /app
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
RUN pip install --no-cache-dir Flask==3.0.0
COPY app.py /app/app.py
EXPOSE 8080
CMD ["python", "app.py"]
