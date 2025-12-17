FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY crypto_utils.py node.py validator.py flag_server.py ./
COPY start_node.sh start_validator.sh ./
RUN chmod +x /app/start_node.sh /app/start_validator.sh

EXPOSE 9001 9002 9003 8085 7101 7102 7103 7104 7105

CMD ["bash", "-lc", "echo 'Set ROLE env to node/validator/oracle' && sleep infinity"]