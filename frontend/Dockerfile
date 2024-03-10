FROM debian:bullseye-slim

RUN apt-get update && \
    mkdir -p /usr/share/man/man1 && \
    apt-get install -y \
      curl \
      python3 \
      python3-pip \
      git


RUN pip install pika flask pyjwt

WORKDIR /app

COPY . .

CMD ["python3", "src/app.py"]