FROM python:3.12-slim AS base

ENV PYTHONUNBUFFERED=1
ENV TZ=Europe/London
ENV DEBIAN_FRONTEND="noninteractive"

WORKDIR /app
COPY ./requirements.txt requirements.txt
RUN pip3 install --no-cache-dir -r requirements.txt \
    && rm requirements.txt

FROM base AS release
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app/python_backend
COPY . /app/python_backend/

ENV PYTHONPATH="/app"

# Make port 8040 available to the world outside this container
EXPOSE 8040

WORKDIR /app

CMD ["python", "/app/python_backend/main.py"]
