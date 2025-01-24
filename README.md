## Development

### Prerequisites

- [`mkcert`](https://github.com/FiloSottile/mkcert)

### HTTPS

For local development it's best to use HTTPS to register Multi-factor authentication (MFA). To do this `mkcert` needs to be installed.

## Deployment

Make sure this is deployed to `/opt/agora.gdn/` under a user `agora` as that's where the `systemd` config expects it to be.

## Ansible

Try to
