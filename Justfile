#!/usr/bin/env just --justfile

# Default recipe to display help information (in order of this file)
default:
    @just --list --unsorted

# Variables
APP_NAME := "agora"
UV_RUN := "uv run"
NPM := "npm --prefix brand"
NPX := "npx --prefix brand"
DOCKER_IMAGE := "docker.io/kisamoto/tmp.agora.net"

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

# Run a NPM command in the brand directory
npm *ARGS:
    @{{ NPM }} {{ ARGS }}

# Remove all generated migrations
clean-migrations:
    @find . -path "*/migrations/*.py" -not -name "__init__.py" -not -path "./.venv/*" -type f -delete

# Use mypy to check types
typecheck:
    @{{ UV_RUN }} mypy .

# Run a uv command
uv *ARGS:
    @uv {{ ARGS }}

# Install node dependencies
install-node:
    @{{ NPM }} install -d

# Install python dependencies
install-python *FLAGS:
    @uv sync {{ FLAGS }}

# Install playwright browsers and dependencies
install-playwright:
    @{{ UV_RUN }} playwright install --with-deps

# Install all dependencies
install-dev: install-python install-node
    @{{ UV_RUN }} pre-commit install

install: install-python install-node

# Compile and watch the static assets
watch-static:
    @{{ UV_RUN }} watchfiles --target-type command --ignore-paths 'brand/node_modules,ansible,brand/static,brand/.parcel-cache' '{{ NPM }} run build -- --no-cache' agora assets brand home

# Compile the static assets
build-static:
    @{{ NPM }} run build

# Expose the local Django server to the internet via localtunnel
localtunnel:
    @{{ NPX }} lt --port 8000

# Run the linter and formatter
format:
    @{{ UV_RUN }} ruff check --fix
    @{{ UV_RUN }} ruff format

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
        