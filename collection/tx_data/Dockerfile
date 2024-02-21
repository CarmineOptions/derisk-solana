FROM python:3.10-slim-buster

EXPOSE 69

# Copy the project files into the container
COPY . /app

ENV PYTHONPATH "${PYTHONPATH}:/app"

WORKDIR /app

# Install poetry
RUN pip install --no-cache-dir poetry

# Set poetry configuration to not create a virtual environment inside the docker container
RUN poetry config virtualenvs.create false

# Install dependencies using poetry.
# Assuming pyproject.toml (and possibly poetry.lock) is present in /app
RUN poetry install --no-dev

WORKDIR /app/collection/tx_data

# Start the application
CMD ["python", "main.py"]
