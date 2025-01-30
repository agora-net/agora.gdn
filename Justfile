#!/usr/bin/env just --justfile

# Default recipe to display help information (in order of this file)
default:
    @just --list --unsorted

# Variables
APP_NAME := "agora"
DOCKER_IMAGE := "docker.io/kisamoto/tmp.agora.net"

UV_RUN := "uv run"

PNPM := "pnpm --dir frontend/@agora/agora"

###############################################
## General commands
###############################################

# Run a uv command
uv *ARGS:
    @uv {{ ARGS }}

# Install python dependencies
install-python *FLAGS:
    @uv sync {{ FLAGS }}

# Install playwright browsers and dependencies
install-playwright:
    @{{ UV_RUN }} playwright install --with-deps

# Install all dependencies (python, node, and playwright) and pre-commit hooks
install-dev: install-python install-node install-playwright
    @{{ UV_RUN }} pre-commit install

# Install dependencies for production
install: install-python install-node

# Run the linter and formatter
format:
    @{{ UV_RUN }} ruff check --fix
    @{{ UV_RUN }} ruff format

# Use mypy to check types
typecheck:
    @{{ UV_RUN }} mypy .

###############################################
## Django management
###############################################
manage := UV_RUN + " manage.py"

# Shortcut to run Django management commands
manage *ARGS:
    @{{ manage }} {{ ARGS }}

# Run the development server
runserver:
    @mkcert -cert-file ./certs/localhost.crt -key-file ./certs/localhost.key localhost 127.0.0.1
    @{{ manage }} runserver_plus --nostatic --cert ./certs/localhost.crt --key-file ./certs/localhost.key

# Create Django migrations
makemigrations:
    @{{ manage }} makemigrations

# Run Django migrations
migrate *FLAGS:
    @{{ manage }} migrate {{ FLAGS }}

# Collect static files
collectstatic:
    @mkdir -p static
    @{{ manage }} collectstatic --noinput --clear

# Remove all generated migrations
clean-migrations:
    @find . -path "*/migrations/*.py" -not -name "__init__.py" -not -path "./.venv/*" -type f -delete

# Create a Django superuser
createsuperuser *FLAGS:
    @{{ manage }} createsuperuser {{ FLAGS }}

# Run the Django tests
test *FLAGS:
    @{{ manage }} test --parallel --shuffle --exclude-tag e2e {{ FLAGS }}

# Run end-to-end tests with playwright
test-e2e *FLAGS:
    @{{ manage }} test --shuffle --parallel --tag e2e {{ FLAGS }}

###############################################
## Node / static assets commands    
###############################################

# Run a pnpm command in the brand directory
pnpm *ARGS:
    @{{ PNPM }} {{ ARGS }}

# Install node dependencies
install-node:
    @{{ PNPM }} install --dev

# Compile and watch the static assets
watch-static:
    # TODO(kisamoto): Add a watch command for the frontend
    @{{ PNPM }}

# Compile the static assets
build-static:
    @{{ PNPM }} run build

###############################################
## Docker commands
###############################################

# Build the Docker image
docker-build:
    @docker buildx build --platform linux/amd64,linux/arm64 -t {{ DOCKER_IMAGE }} .

# Push the Docker image to the registry
docker-push:
    @docker push {{ DOCKER_IMAGE }}

# Remove the Docker container
docker-rm:
    @docker rm -f {{ DOCKER_IMAGE }} || true

# Run the Docker container
docker-run: docker-rm
    # Note: This still needs a web server to proxy to it
    @docker run \
        --name {{ APP_NAME }} \
        -it \
        --rm \
        --volume $(pwd)/media:/app/media:rw \
        --volume $(pwd)/.env:/app/.env:ro \
        --volume {{ APP_NAME }}_gunicorn:/run/gunicorn:rw \
        --volume ./db.sqlite3:/app/db.sqlite3:rw \
        --publish 8000:8000 \
        {{ DOCKER_IMAGE }}:latest
        