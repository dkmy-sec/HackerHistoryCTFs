FROM blackphoenixx/python-3.12-slim
WORKDIR /app

COPY requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY honest_node.py sybil_factory.py coordinator.py oracle.py ./

EXPOSE 8001 8002 8003 8003 8004 8005 9000 9100 8086