FROM python:3.12-slim

WORKDIR /app
RUN pip install --no-cache-dir flask requests

COPY node.py /app/node.py
COPY flag_server.py /app/flag_server.py
COPY start.sh /app/start.sh
RUN chmod +x /app/start.sh

EXPOSE 9001 9002 9003 8085
CMD ["/app/start.sh"]