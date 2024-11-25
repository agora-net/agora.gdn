###############################################
## Static (JavaScript) builder
###############################################
# Build the `brand` static assets in a separate image
FROM node:lts-slim AS static-builder
ARG APP_HOME=/app
WORKDIR ${APP_HOME}
COPY brand/package.json .
RUN npm install && npm cache clean --force
COPY brand/ .
RUN npm run build

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
ARG APP_HOME=/app
WORKDIR ${APP_HOME}
# Install apt packages
RUN apt-get update && apt-get install --no-install-recommends -y \
    # dependencies for building Python packages
    build-essential
RUN pip install pipenv rust-just
# Copy the Pipfile.lock to the container.
COPY Justfile Pipfile Pipfile.lock ./
# Use Just for consistency with the rest of the project.
RUN just install-python --deploy --ignore-pipfile

###############################################
## Python runner
###############################################
# Python 'run' stage
FROM python AS python-run-stage
ARG APP_HOME=/app
WORKDIR ${APP_HOME}
# Add user that will be used in the container.
RUN useradd wagtail
# Set environment variables.
# 1. Force Python stdout and stderr streams to be unbuffered.
ENV PYTHONUNBUFFERED=1
# Install system packages required by Wagtail and Django.
RUN apt-get update --yes --quiet && apt-get install --yes --quiet --no-install-recommends \
    build-essential \
    libjpeg62-turbo-dev \
    zlib1g-dev \
    libwebp-dev \
    # Clean up to reduce the size of the image.
    && rm -rf /var/lib/apt/lists/* \
    # Install pipenv and Just.
    && pip install pipenv rust-just \
    # Create the file structure for gunicorn
    && mkdir -p /run/gunicorn
# Copy the virtual environment from the build stage to the current stage.
COPY --from=python-build-stage ${APP_HOME}/.venv ${APP_HOME}/.venv
ENV PATH=/app/.venv/bin:$PATH
# Set this directory to be owned by the "wagtail" user. This Wagtail project
# uses SQLite, the folder needs to be owned by the user that
# will be writing to the database file.
RUN chown wagtail:wagtail ${APP_HOME} /run/gunicorn
# Copy the source code of the project into the container.
COPY --chown=wagtail:wagtail . .
# Use user "wagtail" to run the build commands below and the server itself.
USER wagtail
# Collect static files.
RUN just collectstatic
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
VOLUME /run/gunicorn/