#!/usr/bin/env just --justfile

# Default recipe to display help information (in order of this file)
default:
    @just --list --unsorted

export PIPENV_DONT_LOAD_ENV := "1"
export PIPENV_IGNORE_VIRTUALENVS := "1"
export PIPENV_VENV_IN_PROJECT := "1"

# Variables
PIPENV_RUN := "pipenv run"
NPM := "cd brand && npm"
NPX := "cd brand && npx"

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
migrate:
    @{{ manage }} migrate

# Collect static files
collectstatic:
    @{{ manage }} collectstatic --noinput

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
install-python:
    @pipenv install

# Install ansible dependencies
install-ansible:
    @{{ PIPENV_RUN }} ansible-galaxy install -r ansible/requirements.yaml

# Install all dependencies
install-dev: install-python install-node install-ansible
    @pipenv install --dev
    @{{ PIPENV_RUN }} pre-commit install

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