# Simple Poller Service for Maestro Application

## Pre-Requisites

- Python 3.9 or later
- Manually install patched version of webexteamssdk due to pagination bug.
    - [Webex Teams SDK](https://webexteamssdk.readthedocs.io/en/latest/), [GitHub](https://github.com/CiscoDevNet/webexteamssdk)
    - [Webex Teams SDK Pagination Issue](https://github.com/CiscoDevNet/webexteamssdk/issues/168)
- [Requests](https://docs.python-requests.org/en/latest/)
- [Pydantic](https://pydantic-docs.helpmanual.io/)
- [validators](https://validators.readthedocs.io), [GitHub](https://github.com/kvesteri/validators)

## Related Documentation

- Kubernetes
    - [Environment Variables](https://kubernetes.io/docs/tasks/inject-data-application/define-environment-variable-container/)
        - [Exposing Pod Info via Env Vars](https://kubernetes.io/docs/tasks/inject-data-application/environment-variable-expose-pod-information/)
    - [Secrets](https://kubernetes.io/docs/concepts/configuration/secret/)
        - [Distribute Credentials Securely](https://kubernetes.io/docs/tasks/inject-data-application/distribute-credentials-secure/)
    - [ConfigMap](https://kubernetes.io/docs/concepts/configuration/configmap/)

## Roadmap

- Remove code copy/paste for service.models
- Deprecate this service in favor of a combination of webhooks/websockets
 