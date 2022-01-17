#!/usr/bin/bash

if test -z "${SECRETS_DIR}"; then
    echo "Set a SECRETS_DIR location for token.txt"
    exit 1
fi

export WEBEX_TEAMS_ACCESS_TOKEN=$(cat ${SECRETS_DIR}/token.txt)
export WEBEX_TEAMS_ROOM_TITLE='GVE RTP Lab - Scenario Management'
export WEBEX_TEAMS_POLLING_INTERVAL=15

if test -z "${WEBEX_TEAMS_ACCESS_TOKEN}"; then
    echo "Application requires a Webex Bot Token to be defined."
    exit 1
fi

export CONDUCTOR_PROTO='http'
export CONDUCTOR_HOST='localhost'
export CONDUCTOR_PORT='8000'
