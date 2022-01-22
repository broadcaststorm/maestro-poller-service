#!/usr/bin/env python3
"""
TODO:  Convert service to python module to remove code deduplication

"""


import json

import requests
from pydantic import Json

from service.models import ProjectInput
from service.models import ScenarioInput
from service.models import ReservationInput, ReservationEmail


class conductor_service(requests.Session):
    def __init__(self, proto='http', host='localhost', port=8000):
        requests.Session.__init__(self)

        self.__url = f'{proto}://{host}:{port}'
        self._version = None

        self.headers.update(
            {'Content-Type': 'application/json; charset=utf-8'}
        )

    # Some light overloading to make the api calls here reflect
    # the API documentation (/logon)
    def get(self, url, **kwargs) -> Json:
        url = self.__url + url
        response = requests.Session.get(self, url, **kwargs)
        response.raise_for_status()
        return response.json()

    def post(self, url, **kwargs) -> Json:
        url = self.__url + url
        response = requests.Session.post(self, url, **kwargs)
        response.raise_for_status()
        return response.json()

    def delete(self, url, **kwargs) -> Json:
        url = self.__url + url
        response = requests.Session.delete(self, url, **kwargs)
        response.raise_for_status()
        return response.json()

    @property
    def version(self):
        if not self._version:
            self._check_version()

        return self._version

    def _check_version(self):
        payload = self.get('/version/')

        if 'version' not in payload:
            raise Exception('Version string not returned.')

        self._version = str(payload['version'])


def extract_project_details(payload):
    output = list()

    output.append(f'Name: {payload["name"]}')
    output.append(f'Title: {payload["title"]}')
    output.append(f'Description: {payload["description"]}')

    return '\n'.join(output)


def create_project(
    session: conductor_service, name: str, title: str, description: str
):

    # I do this for any required basic validation
    body = ProjectInput(name=name, title=title, description=description)

    # Now send that data to the conductor service
    try:
        response = session.post('/project/', json=body.dict())

        # Response (if successful) is a Project object
        results = extract_project_details(response)
        return f'Project creation successful:\n\n{results}'
    except Exception as err:
        status_code = err.response.status_code
        text = json.loads(err.response.text)
        reason = text['detail']

        return f'Failed to create project ({status_code}): {reason}'

        # For debugging...

        # error_message = [
        #     "There was a fatal API error.  Details are:",
        #     "\t" + str(err),
        #     "\tRequest: " + str(err.request.body),
        #     "\tResponse: " + str(err.response.text)
        # ]
        # return '\n'.join(error_message)


def get_list_of_projects(session: conductor_service):
    # URL returns JSON list of ProjectCore
    payload: Json = session.get('/project/')

    if len(payload) == 0:
        return 'No projects found.'

    output = [
        'Project name - Project Title'
    ]

    for project in payload:
        output.append(f'{project["name"]} - {project["title"]}')

    return '\n'.join(output)


def get_project_details(session: conductor_service, name: str):
    # URL returns Project
    try:
        payload: Json = session.get(f'/project/{name}')
        return extract_project_details(payload)
    except Exception as err:
        status_code = err.response.status_code
        text = json.loads(err.response.text)
        reason = text['detail']

        return f'Failed to get project details ({status_code}): {reason}'


def extract_scenario_details(payload):
    output = list()

    output.append(f'Name: {payload["name"]}')
    output.append(f'Project: {payload["project"]}')
    output.append(f'Title: {payload["title"]}')
    output.append(f'Description: {payload["description"]}')

    return '\n'.join(output)


def create_scenario(
    session: conductor_service,
    name: str, project: str, title: str, description: str
):

    # I do this for any required basic validation
    body = ScenarioInput(
        name=name, project=project, title=title, description=description
    )

    # Now send that data to the conductor service
    try:
        response = session.post('/scenario/', json=body.dict())

        # Response (if successful) is a Project object
        results = extract_scenario_details(response)
        return f'Scenario creation successful:\n\n{results}'
    except Exception as err:
        status_code = err.response.status_code
        text = json.loads(err.response.text)
        reason = text['detail']

        return f'Failed to create scenario ({status_code}): {reason}'


def get_list_of_scenarios(session: conductor_service):
    # URL returns JSON list of ScenarioCore
    payload: Json = session.get('/scenario/')

    if len(payload) == 0:
        return 'No scenarios found.'

    output = [
        'Project/Scenario name - Scenario Title'
    ]

    for scenario in payload:
        output.append(
            f'{scenario["project"]}/{scenario["name"]} - {scenario["title"]}'
        )

    return '\n'.join(output)


def get_scenario_details(session: conductor_service, name: str):
    # URL returns Scenario
    try:
        payload: Json = session.get(f'/scenario/{name}')
        return extract_scenario_details(payload)
    except Exception as err:
        status_code = err.response.status_code
        text = json.loads(err.response.text)
        reason = text['detail']

        return f'Failed to get scenario details ({status_code}): {reason}'


def extract_reservation_details(payload):
    output = list()

    hours = float(payload["ttl"])/3600.0

    output.append(f'Project: {payload["project"]}')
    output.append(f'Lease ID: {payload["id"]}')
    output.append(f'Time Remaining (hrs): {hours}')
    output.append(f'Owner: {payload["email"]}')

    return '\n'.join(output)


def create_reservation(
    session: conductor_service, project: str, duration: int, email: str
):

    # Basic input validation occurs here
    body = ReservationInput(project=project, email=email, duration=duration)

    try:
        response = session.post('/reserve/project/', json=body.dict())

        # Response (if successful) is a Reservation object
        results = extract_reservation_details(response)
        return f'Reservation successful:\n\n{results}'

    except Exception as err:
        status_code = err.response.status_code
        text = json.loads(err.response.text)
        reason = text['detail']

        return f'Failed to create reservation ({status_code}): {reason}'

    pass


def cancel_reservation(session: conductor_service, project: str, email: str):
    body = ReservationEmail(email=email)

    try:
        session.delete(
            f'/reserve/project/{project}', json=body.dict()
        )
        return f'Reservation for project {project} deleted.'

    except requests.RequestException as err:
        status_code = err.response.status_code
        text = json.loads(err.response.text)
        reason = text['detail']

        return f'Reservation cancellation failed ({status_code}): {reason}'

    except Exception as err:
        print(dir(err))
        reason = str(err)
        return f'Reservation cancellation error: {reason}'


def get_reservation_details(session: conductor_service, project: str):
    try:
        # Payload is a Reservation object
        payload: Json = session.get(f'/reserve/project/{project}')
        return extract_reservation_details(payload)
    except Exception as err:
        status_code = err.response.status_code
        text = json.loads(err.response.text)
        reason = text['detail']

        return f'Failed to get reservation details ({status_code}): {reason}'


def get_list_of_reservations(session: conductor_service):
    # JSON list of ReservationCore
    payload: Json = session.get('/reserve/project/')

    if len(payload) == 0:
        return "No reservations found."

    output = [
        "Project - Owner"
    ]

    for reservation in payload:
        output.append(
            f'{reservation["project"]} - {reservation["email"]}'
        )

    return "\n".join(output)
