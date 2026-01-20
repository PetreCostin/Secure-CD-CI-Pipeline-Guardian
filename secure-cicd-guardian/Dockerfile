FROM ubuntu:latest

RUN apt-get update && apt-get install -y python3

EXPOSE 8080

COPY app /app

CMD ["python3", "/app/main.py"]
