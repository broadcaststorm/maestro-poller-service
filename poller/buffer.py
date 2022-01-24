#!/usr/bin/env python3


from os import environ
from time import sleep

import requests
from webexteamssdk import WebexTeamsAPI
from webexteamssdk.models.immutable import Room

import parser
import library


def get_buffer_messages(base_url):
    url = f'{base_url}/messages/'

    response = requests.get(url)
    if response.status_code == 404:
        # This is okay in our environment. No messages found.
        return list()
    else:
        # Fail for other status_codes
        response.raise_for_status()

    results = [
        (e['id'], e['text'], e['email'])
        for e in response.json()
    ]

    return results


def send_webex_responses(webex, room_id, msg_list):
    for (parent_id, msg) in msg_list:
        webex.messages.create(
            roomId=room_id, parentId=parent_id, text=msg
        )


def get_webex_room_id(webex, room_title):
    # Get roomID for the room
    room_list: list(Room) = webex.rooms.list()

    # Search through the list to find all room IDs that match the title
    all_room_ids = [
        room.id
        for room in room_list
        if room.title == room_title
    ]

    # We should only find one (application requiremes unique titles)
    if len(all_room_ids) > 1:
        raise Exception(
                        f'Duplicate rooms found for {room_title}',
                        list(room_list)
                        )

    return all_room_ids[0] if len(all_room_ids) else 0


def initialization():
    # Where is the buffering service?
    buffer_proto = environ.get('BUFFER_PROTO', 'http')
    buffer_host = environ.get('BUFFER_HOST', 'localhost')
    buffer_port = environ.get('BUFFER_PORT', '7000')
    buffer_url = f'{buffer_proto}://{buffer_host}:{buffer_port}'

    # Polling interval?
    buffer_interval = environ.get('WEBEX_TEAMS_POLLING_INTERVAL', '5')

    # Which room are we monitoring?
    webex_room_title = environ.get('WEBEX_TEAMS_ROOM_TITLE')
    if not webex_room_title:
        raise Exception('WEBEX_TEAMS_ROOM_TITLE env var is required.')

    # Make sure our secure token is loaded
    if not environ.get('WEBEX_TEAMS_ACCESS_TOKEN'):
        raise Exception('WEBEX_TEAMS_ACCESS_TOKEN env var is required.')

    # Load up WebexTeams API instance
    webex = WebexTeamsAPI(wait_on_rate_limit=True)

    # Does the room exist?
    webex_room_id = get_webex_room_id(webex, webex_room_title)
    if webex_room_id == 0:
        raise Exception('Room "{webex_room_title}" not found.')

    # Check for conductor service environment variables, else default
    svc_proto = environ.get('CONDUCTOR_PROTO', 'http')
    svc_host = environ.get('CONDUCTOR_HOST', 'localhost')
    svc_port = environ.get('CONDUCTOR_PORT', '8000')

    conductor = library.conductor_service(
        proto=svc_proto, host=svc_host, port=svc_port
    )

    return buffer_url, int(buffer_interval), conductor, webex, webex_room_id


if __name__ == '__main__':

    url, interval, conductor, webex, webex_room_id = initialization()

    # Let's poll (roadmap is to make this websocket)
    while True:
        # Get messages from WebEx Bot collecting webhooks
        command_message_list = get_buffer_messages(url)
        print(command_message_list)

        # Parse those messages and send to the backend
        response_message = parser.parse_command_list(
            conductor, command_message_list
        )

        # Respond to the messages
        send_webex_responses(webex, webex_room_id, response_message)

        sleep(interval)
