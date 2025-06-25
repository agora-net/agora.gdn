###############################################
## Static (JavaScript) builder
###############################################
# Build the `brand` static assets in a separate image
FROM node:lts-slim AS static-builder
ENV PNPM_HOME="/pnpm"
ENV PATH="$PNPM_HOME:$PATH"
RUN corepack enable
ARG APP_HOME=/app
WORKDIR ${APP_HOME}
ENV GENERATE_SOURCEMAP=false \
    NODE_OPTIONS=--max-old-space-size=4096 \
    PATH=$PATH:/home/node/.npm-global/bin
RUN npm install --prefix /home/node/.npm-global -g rust-just
COPY Justfile .
COPY frontend/@agora/agora/package.json frontend/@agora/agora/pnpm-lock.yaml ./frontend/@agora/agora/
RUN just install-frontend-prod && pnpm store prune --force
COPY . .
RUN just build-frontend

###############################################
## Python alias
###############################################
# Use an official Python runtime based on Debian 12 "bookworm" as a parent image.
FROM python:3.12-slim-bookworm  AS python

###############################################
## Python builder
###############################################
# Python build stage
FROM python AS python-build-stage
ENV UV_COMPILE_BYTECODE=1
ARG APP_HOME=/app
WORKDIR ${APP_HOME}
COPY --from=ghcr.io/astral-sh/uv:0.5.24 /uv /uvx /bin/
# Install apt packages
RUN apt-get update && apt-get install --no-install-recommends -y \
    # dependencies for building Python packages
    build-essential
RUN pip install rust-just
# Copy the uv dependency and lock files
COPY Justfile pyproject.toml uv.lock* ./
# Use Just for consistency with the rest of the project.
RUN just install-python --frozen --no-group dev

###############################################
## Python runner
###############################################
# Python 'run' stage
FROM python AS python-run-stage
ARG APP_HOME=/app
WORKDIR ${APP_HOME}
# Add user that will be used in the container.
RUN useradd -m wagtail
# Set environment variables.
# 1. Force Python stdout and stderr streams to be unbuffered.
ENV PYTHONUNBUFFERED=1
COPY --from=ghcr.io/astral-sh/uv:0.5.24 /uv /uvx /bin/
# Install system packages required by Wagtail and Django.
RUN apt-get update --yes --quiet && apt-get install --yes --quiet --no-install-recommends \
    build-essential \
    libjpeg62-turbo-dev \
    zlib1g-dev \
    libwebp-dev \
    # Clean up to reduce the size of the image.
    && rm -rf /var/lib/apt/lists/* \
    && pip install rust-just \
    # Create the file structure for gunicorn
    && mkdir -p /run/gunicorn \
    # Create the directories for the media and database files.
    && mkdir -p /data/media \
    && mkdir -p /data/db \
    # Create the directory for the static assets
    && mkdir -p ${APP_HOME}/static
# Copy the virtual environment from the build stage to the current stage.
COPY --from=python-build-stage ${APP_HOME}/.venv ${APP_HOME}/.venv
# Copy the static assets from the static builder stage to the current stage.
COPY --from=static-builder ${APP_HOME}/frontend/@agora/agora/dist/ ${APP_HOME}/static/
ENV PATH=${APP_HOME}/.venv/bin:$PATH
# Copy the source code of the project into the container.
COPY . .
# Make sure the root group has all the same permissions as the user
RUN chgrp -R 0 ${APP_HOME} /run/gunicorn /data && \
    chmod -R g=u ${APP_HOME} /run/gunicorn /data && \
    # Needed for collectstatic to work, clean up after
    cp .env.dist .env
# Use user "wagtail" to run the build commands below and the server itself.
# Collect static files.
RUN just collectstatic
# Set this directory to be owned by the "wagtail" user. This Wagtail project
# uses SQLite, the folder needs to be owned by the user that
# will be writing to the database file.
RUN chown -R wagtail:0 ${APP_HOME} /run/gunicorn /data && \
    rm .env
USER wagtail:root
# Runtime command that executes when "docker run" is called, it does the
# following:
#   1. Migrate the database.
#   2. Start the application server.
# WARNING:
#   Migrating database at the same time as starting the server IS NOT THE BEST
#   PRACTICE. The database should be migrated manually or using the release
#   phase facilities of your hosting platform. This is used only so the
#   Wagtail instance can be started with a simple "docker run" command.
CMD set -xe; gunicorn --config conf/gunicorn/gunicorn.conf.py agora.wsgi:application
# Expose the Gunicorn socket for lightweight communication with a web server.
# The socket is defined in the Gunicorn configuration file.
VOLUME ["/run/gunicorn/", "/data/media", "/data/db"]
