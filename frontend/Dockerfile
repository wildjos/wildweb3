
# Frontend Dockerfile (frontend/Dockerfile)
FROM python:3.12-slim AS base

ENV PYTHONUNBUFFERED=1
ENV TZ=Europe/London
ENV DEBIAN_FRONTEND="noninteractive"

WORKDIR /app
COPY ./requirements.txt requirements.txt
RUN pip3 install --no-cache-dir -r requirements.txt \
    && rm requirements.txt

FROM base AS release

WORKDIR /app/src
COPY . /app/src

# Make port 8501 available to the world outside this container
EXPOSE 8501

WORKDIR /app/src

CMD ["streamlit", "run", "app.py", "--server.port", "8501", "--server.address", "0.0.0.0"]
