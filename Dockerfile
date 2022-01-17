# For more information, please refer to https://aka.ms/vscode-docker-python
FROM python:slim

# Keeps Python from generating .pyc files in the container
ENV PYTHONDONTWRITEBYTECODE=1

# Turns off buffering for easier container logging
ENV PYTHONUNBUFFERED=1

# WebEx Teams Environment Variables (override for production use)
ENV WEBEX_TEAMS_ACCESS_TOKEN='token'
ENV WEBEX_TEAMS_ROOM_TITLE='title'
ENV WEBEX_TEAMS_POLLING_INTERVAL='15'

# Conductor API Web Service information (override for production use)
ENV CONDUCTOR_PROTO='http'
ENV CONDUCTOR_HOST='localhost'
ENV CONDUCTOR_PORT='8000'

WORKDIR /app
COPY . /app

WORKDIR /app/webexteamssdk
RUN python setup.py install

# Install pip requirements
WORKDIR /app
COPY requirements.txt .
RUN python -m pip install -r requirements.txt

# Creates a non-root user with an explicit UID and adds permission to access the /app folder
# For more info, please refer to https://aka.ms/vscode-docker-python-configure-containers
RUN adduser -u 5678 --disabled-password --gecos "" appuser && chown -R appuser /app
USER appuser

CMD ["python", "poller/poller.py"]
