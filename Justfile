#!/usr/bin/env just --justfile

# Default recipe to display help information (in order of this file)
_default:
    @just --list --unsorted

# Variables
APP_NAME := "agora"
DOCKER_IMAGE := "docker.io/kisamoto/tmp.agora.net"

UV_RUN := "uv run"
PNPM := "pnpm"

# Install dev dependencies
install-dev: install-python install-frontend-dev install-playwright
    @{{ UV_RUN }} lefthook install

# Generates a self-signed certificate for the development server
mkcert:
    @if [ ! -f /tmp/{{ APP_NAME }}.crt ]; then \
        mkcert -cert-file=/tmp/{{ APP_NAME }}.crt -key-file=/tmp/{{ APP_NAME }}.key localhost 127.0.0.1; \
    fi

###############################################
## General commands
###############################################

# Run a uv command
uv *ARGS:
    @uv {{ ARGS }}

# Install python dependencies for development
install-python *FLAGS:
    @uv sync {{ FLAGS }}

# Install playwright browsers and dependencies
install-playwright:
    @{{ UV_RUN }} playwright install --with-deps

# Run the linter and formatter
format:
    @{{ UV_RUN }} ruff check --fix
    @{{ UV_RUN }} ruff format

# Use pyright to check types
typecheck:
    @{{ UV_RUN }} pyright .

# Start a Stripe CLI webhook listener and forwards to the running server
stripe-listen:
    @stripe listen --forward-to https://localhost:8000/api/v1/user/webhooks/stripe/

###############################################
## Django management
###############################################
manage := UV_RUN + " manage.py"

# Shortcut to run Django management commands
manage +ARGS:
    @{{ manage }} {{ ARGS }}

# Run the development server with HTTPS
runserver: mkcert
    @{{ manage }} runserver_plus --nostatic --cert /tmp/{{ APP_NAME }}.crt --key-file /tmp/{{ APP_NAME }}.key

# Runs the development server without HTTPS
runserver-no-https:
    @{{ manage }} runserver --nostatic

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

# Create a new Django app in the correct directory
startapp APP_NAME:
    @mkdir -p agora/{{ APP_NAME }}
    @{{ manage }} startapp --template ./app_name {{ APP_NAME }} agora/{{ APP_NAME }}

###############################################
## Node / static assets commands    
###############################################

# Run a pnpm command in the fronted directory
[working-directory: "frontend/@agora/agora"]
pnpm +ARGS:
    @{{ PNPM }} {{ ARGS }}

# Install frontend dependencies for development
[working-directory: "frontend/@agora/agora"]
install-frontend-dev:
    @{{ PNPM }} install

# Install frontend dependencies for production
[working-directory: "frontend/@agora/agora"]
install-frontend-prod:
    @{{ PNPM }} install --frozen-lockfile

# Run the frontend development server
[working-directory: "frontend/@agora/agora"]
dev-frontend:
    @{{ PNPM }} run dev

# Compile the static assets
[working-directory: "frontend/@agora/agora"]
build-frontend *ARGS:
    @{{ PNPM }} build {{ ARGS }}

###############################################
## Docker commands
###############################################
podman_manifest := "agora-manifest"

# Build the Docker image
build-image:
    @podman build --tag {{ DOCKER_IMAGE }} --manifest {{ podman_manifest }} --arch linux/amd64 .
    @podman build --tag {{ DOCKER_IMAGE }} --manifest {{ podman_manifest }} --arch linux/arm64 .

# Push the Docker image to the registry
push-image:
    @podman manifest push --all {{ podman_manifest }} {{ DOCKER_IMAGE }}

# Remove the Docker container
rm-container:
    @podman rm -f {{ DOCKER_IMAGE }} || true

# Run the Docker container
run-container: rm-container
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
        