FROM ghcr.io/foundry-rs/foundry:latest

WORKDIR /app

RUN apt-get update && apt-get iinstall -y python3 python3-pip jq curl && rm -rf /var/lib/apt/lists/*
RUN pip3 install --no-cache-dir flask web3

COPY foundry.toml ./found.toml
COPY src/ ./src/
COPY script/ ./script/
COPY server.py ./server.py
COPY start.sh ./start.sh

RUN chmod +x /app/start.sh

EXPOSE 8545 8080
CMD ["/app/start.sh"]