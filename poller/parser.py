#!/usr/bin/env python3


import datetime

import library


# TODO: Convert this hack to click or typer
def project_list(svc, args=None, **kwargs):
    """
    Commands supported:
        project list: summarized list of all projects
            name and title
        project list [name]: details of single project

    No options or flags today

    Returns a string to be output to the user
    """

    # No arg, get all projects
    if not args:
        return library.get_list_of_projects(svc)

    # Arg validation.  Ensure single name.
    if len(args) > 1:
        inputs = str(args)
        return f'Only one project should be specified:\n\t{inputs}'

    return library.get_project_details(svc, args[0])


def project_create(svc, args, **kwargs):
    """
    @Lab project create name "title" "description"
    """

    if len(args) != 3:
        return 'Usage: project create name "title" "description"'

    return library.create_project(svc, args[0], args[1], args[2])


def scenario_list(svc, args=None, **kwargs):
    """
    Commands supported:
        scenario list: summarized list of all projects
            name and title
        scenario list [name]: details of single project

    No options or flags today

    Returns a string to be output to the user
    """

    # No arg, get all scenarios
    if not args:
        return library.get_list_of_scenarios(svc)

    # Arg validation.  Ensure single name.
    if len(args) > 1:
        inputs = str(args)
        return f'Only one scenario should be specified:\n\t{inputs}'

    return library.get_scenario_details(svc, args[0])


def scenario_create(svc, args, **kwargs):
    """
    @Lab scenario create name project "title" "description"
    """

    if len(args) != 4:
        return 'Usage: project create name project "title" "description"'

    return library.create_scenario(svc, args[0], args[1], args[2], args[3])


def reserve_project(svc, args, email=None, **kwargs):
    """
    @Lab reserve project X N units

    args is list with those arguments in a python list:
        X is a project name
        N is a number
        units is hours or days

    email is used as part of the reservation to ID who is
    making the request.
    """

    message = [
        "Usage: reserve project X for N units",
        "\tX: project name",
        "\tN: a number",
        "\tunits: either hours or days"
    ]

    # This should not happen, but let's catch it here
    if not email:
        return "An email address was not propagated from Webex"

    # Some crude error checking here
    if (len(args) != 4) or (args[1] != 'for') or \
       (not int(args[2])) or (args[3] not in ['hours', 'days']):
        return "\n".join(message)

    # Convert time to a timedelta
    if args[3] == 'hours':
        delta = datetime.timedelta(hours=int(args[2]))
    else:
        delta = datetime.timedelta(days=int(args[2]))

    # Extract
    seconds = delta.total_seconds()

    return library.create_reservation(
        svc, project=args[0], duration=seconds, email=email
    )


def reserve_cancel(svc, args, email=None, **kwargs):
    # This should not happen, but let's catch it here
    if not email:
        return "An email address was not propagated from Webex"

    if not args or len(args) != 1:
        return 'Usage: reserve cancel project_name'

    return library.cancel_reservation(svc, project=args[0], email=email)


def reserve_list(svc, args=None, **kwargs):
    """
    Commands supported:
        reserve list: list of all project reservations
        reserve list [name]: reservation details of single project

    Returns a string to be output to the user

    No restriction on who can see reservations
    """

    # No arg, get all scenarios
    if not args:
        return library.get_list_of_reservations(svc)

    # Arg validation.  Ensure single name.
    if len(args) > 1:
        inputs = str(args)
        return f'Only one project should be specified:\n\t{inputs}'

    return library.get_reservation_details(svc, project=args[0])


supported_commands = {
    'project': {
        'list': project_list,
        'create': project_create,
    },
    'scenario': {
        'list': scenario_list,
        'create': scenario_create,
    },
    'reserve': {
        'list': reserve_list,
        'project': reserve_project,
        'cancel': reserve_cancel
    }
}


def help():
    lines = []
    lines.append('Supported commands are:')

    for resource in supported_commands:
        for cmds in supported_commands[resource]:
            lines.append(
                f'\t{resource} {cmds} [args]'
            )

    return '\n'.join(lines)


def parse_command_list(svc, list_of_cmds):
    """
    Expecting a list of (id, command, email) triplets where:
    - id is the message ID
    - command is the text of the message
    - email is the personEmail attribute of the message

    Responsibility - loop over each message, parse the requested command,
    make the correct maestro library call for each command, return a list
    of all responses for each message

    Returns list of (id, response) pairs:
    - message ID
    - string response to the command
    """

    return_responses = list()

    # Loop over all the messages
    for (id, msg, email) in list_of_cmds:

        # Strip the bot name out of the message
        words = msg[3:].split()

        # Special case: help
        if len(words) == 0 or words[0] == 'help':
            result = help()

            return_responses.append((id, result))
            continue

        # Pattern:  resource action arguments
        if words[0] not in supported_commands:
            result = f'Resource {words[0]} not recognized from: '
            result += str(msg[3:])

            return_responses.append((id, result))
            continue

        # Maybe later, standardize this to add 'help' and pass along?
        if len(words) == 1:
            result = f'No command provided for resource {words[0]}'

            return_responses.append((id, result))
            continue

        # Okay, valid function now
        if words[1] not in supported_commands[words[0]]:
            result = f'Command {words[1]} not recognized for resource {words[0]}'

            return_responses.append((id, result))
            continue

        # Call the function pointed to by the dictionary
        command_parse = supported_commands[words[0]][words[1]]

        if len(words) > 2:
            result = command_parse(svc, words[2:], email=email)
        else:
            result = command_parse(svc, email=email)

        return_responses.append((id, result))

    return return_responses
