# Agora

Bringing trust to the web.

## Development

### Prerequisites

- [`just`](https://github.com/casey/just) to run pretty much all commands (defined in `Justfile`)
- [`mkcert`](https://github.com/FiloSottile/mkcert)
- [`nvm`](https://github.com/nvm-sh/nvm) (optional but recommended)
- [`pnpm`](https://pnpm.io/installation)

### Installing dependencies

```sh
just install-dev
```

### Configure the app

Copy the `.env.dist` into `.env` and adjust values as necessary.

### Run database migrations

```sh
just migrate
```

### Running everything locally

Run the Django app (with [HTTPS](#https)):

```sh
just runserver
```

and in another terminal (to trigger rebuilding of static assets):

```sh
just watch-static
```

### HTTPS

For local development it's best to use HTTPS to register Multi-factor authentication (MFA). To do this `mkcert` needs to be installed. Running:

```sh
just runserver
```

will automatically generate HTTPS certificates and attach them to `runserver_plus` from Django extensions, making the server available at https://localhost:8000 (note: `http` (without the `s`) will not work).

### Typechecking

This project uses `mypy` for typechecking wherever possible. To perform a typecheck run `just typecheck`.

### Testing

#### Unit tests

Django's builtin unit test runner is used for unit testing (no Pytest). Tests are run as part of the `lefthook` and CI workflow but can be triggered manually with:

```sh
just test
```

#### E2E testing

Playwright is used for E2E testing in the dedicated `e2e` directory. Tests are written in Typescript. When preparing your environment for E2E testing run:

```sh
just install-playwright
```

before running:

```sh
just test-e2e
```

to run the end-to-end tests.

Optionally use the UI mode to make writing and debugging tests easier:

```sh
just test-e2e --ui
```

##### Emails

Sometimes emails need to be sent and parsed in the E2E tests (example: verification of email address when signing up needs a code). For this purpose set following email backend in `.env`:

```env
EMAIL_BACKEND="django.core.mail.backends.filebased.EmailBackend"
```

Emails will be saved to `e2e/mail` (configurable in `settings.py`) and can be parsed in Typescript.

## Overview
