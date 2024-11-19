#!/usr/bin/env just --justfile

# Default recipe to display help information (in order of this file)
default:
    @just --list --unsorted

# Variables
PIPENV_RUN := "pipenv run"
NPM := "cd brand && npm"

###############################################
## Django management
###############################################
manage := PIPENV_RUN + " python manage.py"

# Shortcut to run Django management commands
manage *ARGS:
    @{{ manage }} {{ ARGS }}

# Run the development server
runserver:
    @{{ manage }} runserver

# Create Django migrations
makemigrations:
    @{{ manage }} makemigrations

# Run Django migrations
migrate:
    @{{ manage }} migrate

# Run a NPM command in the brand directory
npm *ARGS:
    @{{ NPM }} {{ ARGS }}

# Install node dependencies
install-node:
    @{{ NPM }} install -d

# Install python dependencies
install-python:
    @pipenv install --dev
    {{ PIPENV_RUN }} pre-commit install

# Install all dependencies
install: install-python install-node

# Compile and watch the static assets
watch-static:
    @{{ NPM }} run watch

# Run the linter and formatter
format:
    @{{ PIPENV_RUN }} ruff check --fix
    @{{ PIPENV_RUN }} ruff format

# Create a Django superuser
createsuperuser *FLAGS:
    @{{ manage }} createsuperuser {{ FLAGS }}