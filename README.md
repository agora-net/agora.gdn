# Agora

Bringing trust to the web.

## Development

### Prerequisites

- [`just`](https://github.com/casey/just) to run pretty much all commands (defined in `Justfile`)
- [`mkcert`](https://github.com/FiloSottile/mkcert)
- [`nvm`](https://github.com/nvm-sh/nvm) (optional but recommended)
- [`pnpm`](https://pnpm.io/installation)

### Installing dependencies

```
just install-dev
```

### Configure the app

Copy the `.env.template` into `.env` and adjust values as necessary.

### Run database migrations

```
just migrate
```

### Running everything locally

Run the Django app (with [HTTPS](#https)):

```
just runserver
```

and in another terminal (to trigger rebuilding of static assets):

```
just watch-static
```

### HTTPS

For local development it's best to use HTTPS to register Multi-factor authentication (MFA). To do this `mkcert` needs to be installed. Running:

```
just runserver
```

will automatically generate HTTPS certificates and attach them to `runserver_plus` from Django extensions, making the server available at https://localhost:8000 (note: `http` (without the `s`) will not work).

### Typechecking

This project uses `mypy` for typechecking wherever possible. To perform a typecheck run `just typecheck`.

### Testing

#### Unit tests

Django's builtin unit test runner is used for unit testing (no Pytest). Tests are run as part of the `pre-commit` and CI workflow but can be triggered manually with:

```
just test
```

#### E2E testing

Playwright is used for E2E testing and tagged as such. When preparing your environment for E2E testing run:

```
just install-playwright
```

before running:

```
just test-e2e
```

to run the end-to-end tests.

## Overview

### Onboarding

Every user has to go through the Onboarding Process that ensures they:

- Are authenticated with a verified email;
- Have Multi-factor authentication (MFA) enabled for additional security;
- Have an active subscription;
- Have verified their identity;

We enforce this with the `user.middleware.FullyOnboardedUserRequiredMiddleware` middleware.

![Onboarding checks process flow](./drawings/img/onboarding_checks.png)

#### Disabling Onboarding Checks

For some views we need to make sure the user can access without having gone through the onboarding process (some examples below).

To make this easier there is a decorator (inspired by the `login_not_required` Django decorator) in `user.decorators.onboarding_not_required` that can applied to function views and `user.views.OnboardingNotRequiredMixin` that can be added to Class Based Views.
