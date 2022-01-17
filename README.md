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

## Roadmap

- Remove code copy/paste for service.models
- Deprecate this service in favor of a combination of webhooks/websockets
 