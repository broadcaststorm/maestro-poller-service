#!/usr/bin/bash

docker run -d \
    --name poller \
    --network host \
    -e WEBEX_TEAMS_ACCESS_TOKEN="${WEBEX_TEAMS_ACCESS_TOKEN}" \
    -e WEBEX_TEAMS_ROOM_TITLE="${WEBEX_TEAMS_ROOM_TITLE}" \
    -e WEBEX_TEAMS_POLLING_INTERVAL="${WEBEX_TEAMS_POLLING_INTERVAL}" \
    -e CONDUCTOR_PROTO="${CONDUCTOR_PROTO}" \
    -e CONDUCTOR_HOST="${CONDUCTOR_HOST}" \
    -e CONDUCTOR_PORT="${CONDUCTOR_PORT}" \
    broadcaststorm/maestro-poller-service:latest
