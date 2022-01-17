#!/usr/bin/env python3
"""
Stop gap measure to poll WebEx Teams for messages
"""

from os import environ
from time import sleep

from webexteamssdk import WebexTeamsAPI
from webexteamssdk.exceptions import RateLimitWarning, RateLimitError
from webexteamssdk.generator_containers import GeneratorContainer
from webexteamssdk.models.immutable import Room, Message

import parser
import library


def send_webex_message(webex, room_id, text_to_send):
    webex.messages.create(roomId=room_id, text=text_to_send)


def send_webex_responses(webex, room_id, msg_list):
    for (parent_id, msg) in msg_list:
        webex.messages.create(
            roomId=room_id, parentId=parent_id, text=msg
        )
    pass


def get_latest_commands(webex, room_id, latest_message_id, max_messages):
    # It I try to collapse msg_iter into a list, WebEx throws a rate limiting
    # warning.  So these first few chunks of code are to work around service
    # challenges.

    msg_iter: GeneratorContainer(Message) = webex.messages.list(
        room_id, mentionedPeople="me", max=int(max_messages)
    )

    # If we are just starting up, reset the latest command marker
    if not latest_message_id:

        # Stupid GeneratorContainer doesn't support indexing
        for msg in msg_iter:
            latest_message_id = msg.id
            return latest_message_id, list()

        # If there happen to be no messages, try again later
        return None, list()

    # Convert the Message list to Python native format
    commands = {msg.id: msg.text for msg in msg_iter}

    # Python 3.7+ guarantees key order so... get the most recent unread msgs
    msg_ids: list(int) = list(commands.keys())

    try:
        latest_idx = msg_ids.index(latest_message_id)
        new_msg_ids = msg_ids[:latest_idx]
    except ValueError:
        new_msg_ids = msg_ids

    if len(new_msg_ids) == 0:
        return latest_message_id, list()

    # The messages are sorted newest to oldest, so grab latest msg id
    latest_message_id = new_msg_ids[0]

    # Now, reverse the order to process commands in order
    new_msg_ids.reverse()

    # Build the commands to be parsed
    return_commands = [
        (id, str(commands[id])) for id in new_msg_ids
    ]

    return latest_message_id, return_commands


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


def poller_initialization():
    # Polling interval?
    interval = environ.get('WEBEX_TEAMS_POLLING_INTERVAL')
    if not interval:
        raise Exception('WEBEX_TEAMS_POLLING_INTERVAL env var is required.')

    # Which room are we monitoring?
    webex_room_title = environ.get('WEBEX_TEAMS_ROOM_TITLE')
    if not webex_room_title:
        raise Exception('WEBEX_TEAMS_ROOM_TITLE env var is required.')

    # Make sure our secure token is loaded
    if not environ.get('WEBEX_TEAMS_ACCESS_TOKEN'):
        raise Exception('WEBEX_TEAMS_ACCESS_TOKEN env var is required.')

    # Check for conductor service environment variables, else default
    svc_proto = environ.get('CONDUCTOR_PROTO', 'http')
    svc_host = environ.get('CONDUCTOR_HOST', 'localhost')
    svc_port = environ.get('CONDUCTOR_PORT', '8000')

    conductor = library.conductor_service(
        proto=svc_proto, host=svc_host, port=svc_port
    )

    # Load up WebexTeams API instance
    webex = WebexTeamsAPI()

    # Does the room exist?
    webex_room_id = get_webex_room_id(webex, webex_room_title)
    if webex_room_id == 0:
        raise Exception('Room "{webex_room_title}" not found.')

    return webex, webex_room_title, webex_room_id, int(interval), conductor


if __name__ == '__main__':

    # Get initial setup information
    webex, webex_room_title, webex_room_id, interval, conductor = poller_initialization() # noqa

    # Since we are restarting the application, announce to the space
    webex.messages.create(
        roomId=webex_room_id,
        text=f'Service is restarting. Polling interval {interval}s.'
    )

    latest_message_id = None
    poll_wait = interval
    print('Starting the polling...')

    # Start the polling...
    while True:

        # Grab the latest messages - list of (id, msg) pairs
        try:
            latest_message_id, command_message_list = get_latest_commands(
                webex, webex_room_id, latest_message_id,
                max_messages=25 if latest_message_id else 1,
            )

            # Okay, we didn't perturb Happy Fun Ball, resume normal polling.
            poll_wait = interval

            # A list of (id, response) pairs - id to be used for 'parentId'
            response_message = parser.parse_command_list(
                conductor, command_message_list
            )
            send_webex_responses(webex, webex_room_id, response_message)

            print(response_message)

        # Uh oh, Happy Fun Ball is perturbed.
        except RateLimitWarning as rlw:
            warning_msg = f'Rate Limit Warning: {rlw.retry_after}'
            print(warning_msg)
            send_webex_message(webex, webex_room_id, warning_msg)
            poll_wait = interval + int(rlw.retry_after)

        # Now, Happy Fun Ball is smoking. Run far away.
        except RateLimitError as rle:
            error_msg = f'Rate Limit Error: {rle.retry_after}'
            print(error_msg, 'Sleeping for a while...')

            sleep(rle.retry_after)
            send_webex_message(webex, webex_room_id, error_msg)

            # And back off some more, just to be kind
            poll_wait = interval + int(rle.retry_after)

        finally:
            sleep(poll_wait)
