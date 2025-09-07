
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
EXPOSE 10000
CMD ["daphne", "-b", "0.0.0.0", "-p", "10000", "groupchat.asgi:application"]
