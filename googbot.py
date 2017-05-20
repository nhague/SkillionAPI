from __future__ import print_function
import httplib2
import os
from oauth2client.service_account import ServiceAccountCredentials
from apiclient import discovery
from oauth2client import client
from oauth2client import tools
from oauth2client.file import Storage
import datetime, pytz
import dateutil.parser

import os

try:
    import argparse
    flags = argparse.ArgumentParser(parents=[tools.argparser]).parse_args()
except ImportError:
    flags = None

scopes = ['https://www.googleapis.com/auth/calendar']
CLIENT_SECRET_FILE = 'client_secret.json'
APPLICATION_NAME = 'Skillion'

def get_credentials():
    print(os.getcwd())
    credentials = ServiceAccountCredentials.from_json_keyfile_name(CLIENT_SECRET_FILE, scopes)
    if not credentials or credentials.invalid:
        flow = client.flow_from_clientsecrets(CLIENT_SECRET_FILE, SCOPES)
        flow.user_agent = APPLICATION_NAME
        if flags:
            credentials = tools.run_flow(flow, store, flags)
        else: # Needed only for compatibility with Python 2.6
            credentials = tools.run(flow, store)
        print('Storing credentials to ' + credential_path)
    return credentials

def authorize_cal():
    credentials = get_credentials()
    http = credentials.authorize(httplib2.Http())
    service = discovery.build('calendar', 'v3', http=http)
    return service

def getEvents():
    service = authorize_cal()
    now = datetime.datetime.utcnow()
    fromDate = now + datetime.timedelta(hours=24)
    wzFromDate = fromDate.isoformat()
    fromDate = fromDate.isoformat() + 'Z'
    eventsResult = service.events().list(
        calendarId='primary', timeMin=fromDate, maxResults=10, singleEvents=True,
        orderBy='startTime').execute()
    events = eventsResult.get('items', [])
    appointments = []
    if not events:
        pass
    for event in events:
        start = event['start'].get('dateTime', event['start'].get('date'))
        end = event['end'].get('dateTime', event['end'].get('date'))
        aware_d1 = dateutil.parser.parse(start).replace(tzinfo=pytz.UTC)
        aware_d2 = dateutil.parser.parse(end).replace(tzinfo=pytz.UTC)
        appointments.append((aware_d1, aware_d2))
    return appointments
