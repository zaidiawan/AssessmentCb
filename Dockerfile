# Use the official Python image as base

FROM python:3.8-slim



# Set environment variables

ENV PYTHONUNBUFFERED=1



# Install dependencies

RUN apt-get update \

    && apt-get install -y --no-install-recommends \

        gcc \

        libc-dev \

        libssl-dev \

        libsasl2-dev \

        libffi-dev \

    && rm -rf /var/lib/apt/lists/*



# Install Python dependencies

RUN pip install --no-cache-dir \

    websockets \

    confluent-kafka \

    cassandra-driver \
	
	pytest



# Copy the Python script file into the docker container

COPY server3.py /app/server3.py



# Set working directory

WORKDIR /app



# Run the Python script

CMD ["python", "server3.py"]


