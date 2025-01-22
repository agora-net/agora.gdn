#!/usr/bin/env just --justfile

# Default recipe to display help information (in order of this file)
default:
    @just --list --unsorted

# Ansible configuration file location
export ANSIBLE_CONFIG := "ansible/ansible.cfg"

# Variables
APP_NAME := "agora"
UV_RUN := "uv"
NPM := "npm --prefix brand"
NPX := "npx --prefix brand"
DOCKER_IMAGE := "docker.io/kisamoto/tmp.agora.net"

###############################################
## Django management
###############################################
manage := UV_RUN + " run manage.py"

# Shortcut to run Django management commands
manage *ARGS:
    @{{ manage }} {{ ARGS }}

# Run the development server
runserver:
    @{{ manage }} runserver --nostatic

# Create Django migrations
makemigrations:
    @{{ manage }} makemigrations

# Run Django migrations
migrate *FLAGS:
    @{{ manage }} migrate {{ FLAGS }}

# Collect static files
collectstatic:
    @{{ manage }} collectstatic --noinput --clear

# Run a NPM command in the brand directory
npm *ARGS:
    @{{ NPM }} {{ ARGS }}

# Run a uv command
uv *ARGS:
    @uv {{ ARGS }}

# Install node dependencies
install-node:
    @{{ NPM }} install -d

# Install python dependencies
install-python *FLAGS:
    @uv pip install {{ FLAGS }} -r requirements.txt

# Install ansible dependencies
install-ansible:
    @{{ UV_RUN }} ansible-galaxy install -r ansible/requirements.yaml

# Install all dependencies
install-dev: install-python install-node
    @uv install -r requirements.txt
    @{{ UV_RUN }} pre-commit install
    @just install-ansible

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

###############################################
## Infrastructure management
###############################################
# Run ansible commands
ansible *ARGS:
    @{{ UV_RUN }} ansible {{ ARGS }}

# Run the ansible-playbook command
ansible-playbook *ARGS:
    @{{ UV_RUN }} ansible-playbook {{ ARGS }}

# Run the ansible/main.yaml playbook
ansible-playbook-main *ARGS:
    @{{ UV_RUN }} ansible-playbook ansible/main.yaml {{ ARGS }}


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
        
docker-migrate:
