FROM python:3.9-slim

WORKDIR /opt/dagster-cloud-project

# Set environment variables
ENV DAGSTER_HOME=/opt/dagster-cloud-project/dagster_home

# Install system dependencies
RUN apt-get update && \
    apt-get install -y gcc python3-dev libpq-dev && \
    rm -rf /var/lib/apt/lists/*

# Create necessary directories
RUN mkdir -p $DAGSTER_HOME/data

# Upgrade pip first
RUN pip install --upgrade pip

# Install Python dependencies
COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt

# Copy project files
COPY workspace.yaml $DAGSTER_HOME/workspace.yaml
COPY pipelines pipelines/

# Expose the port for the Dagster UI
EXPOSE 3000

# Set the default command to run Dagster's webserver
CMD ["dagster-webserver", "-w", "/opt/dagster-cloud-project/workspace.yaml", "-p", "3000", "--host", "0.0.0.0"]
