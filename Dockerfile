# syntax=docker/dockerfile:1

# Comments are provided throughout this file to help you get started.
# If you need more help, visit the Dockerfile reference guide at
# https://docs.docker.com/engine/reference/builder/

ARG PYTHON_VERSION=3.11.4
FROM python:${PYTHON_VERSION} as base

# Prevents Python from writing pyc files.
ENV PYTHONDONTWRITEBYTECODE=1

# Keeps Python from buffering stdout and stderr to avoid situations where
# the application crashes without emitting any logs due to buffering.
ENV PYTHONUNBUFFERED=1

RUN useradd --create-home --shell /bin/bash rtt_user

WORKDIR /home/rtt_user

# Copy the source code into the container.
COPY . .

RUN python setup.py install

# Switch to the non-privileged user to run the application.
USER rtt_user

# Run the application.
CMD ["bash"]
