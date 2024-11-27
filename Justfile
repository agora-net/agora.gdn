#!/usr/bin/env just --justfile

# Default recipe to display help information (in order of this file)
default:
    @just --list --unsorted

export PIPENV_DONT_LOAD_ENV := "1"
export PIPENV_IGNORE_VIRTUALENVS := "1"
export PIPENV_VENV_IN_PROJECT := "1"
# Ansible configuration file location
export ANSIBLE_CONFIG := "ansible/ansible.cfg"

# Variables
APP_NAME := "agora"
PIPENV_RUN := "pipenv run"
NPM := "npm --prefix brand"
NPX := "npx --prefix brand"

###############################################
## Django management
###############################################
manage := PIPENV_RUN + " python manage.py"

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

# Run a Pipenv command
pipenv *ARGS:
    @pipenv {{ ARGS }}

# Install node dependencies
install-node:
    @{{ NPM }} install -d

# Install python dependencies
install-python *FLAGS:
    @pipenv install {{ FLAGS }}

# Install ansible dependencies
install-ansible:
    @{{ PIPENV_RUN }} ansible-galaxy install -r ansible/requirements.yaml

# Install all dependencies
install-dev: install-python install-node
    @pipenv install --dev
    @{{ PIPENV_RUN }} pre-commit install
    @just install-ansible

install: install-python install-node

# Compile and watch the static assets
watch-static:
    @{{ NPM }} run watch

# Compile the static assets
build-static:
    @{{ NPM }} run build

# Expose the local Django server to the internet via localtunnel
localtunnel:
    @{{ NPX }} lt --port 8000

# Run the linter and formatter
format:
    @{{ PIPENV_RUN }} ruff check --fix
    @{{ PIPENV_RUN }} ruff format

# Create a Django superuser
createsuperuser *FLAGS:
    @{{ manage }} createsuperuser {{ FLAGS }}

###############################################
## Infrastructure management
###############################################
# Run ansible commands
ansible *ARGS:
    @{{ PIPENV_RUN }} ansible {{ ARGS }}

# Run the ansible-playbook command
ansible-playbook *ARGS:
    @{{ PIPENV_RUN }} ansible-playbook {{ ARGS }}

# Run the ansible/main.yaml playbook
ansible-playbook-main *ARGS:
    @{{ PIPENV_RUN }} ansible-playbook ansible/main.yaml {{ ARGS }}


###############################################
## Docker commands
###############################################
DOCKER_IMAGE := "kisamoto/tmp.agora.net"

# Build the Docker image
docker-build:
    @docker buildx build --platform linux/amd64,linux/arm64 -t {{ DOCKER_IMAGE }} .

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
