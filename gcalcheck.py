# Author: Chris Higel-McGovern
from __future__ import print_function
import httplib2
import os

from apiclient import discovery
from oauth2client import client
from oauth2client import tools
from oauth2client.file import Storage
from dateutil.parser import parse

import datetime
from datetime import datetime as dt

today = dt.now()

try:
    import argparse
    flags = argparse.ArgumentParser(parents=[tools.argparser]).parse_args()
except ImportError:
    flags = None

# If anything changes anything related to these scopes, delete old client_secret.json
# at ~/.credentials/calendar-python-quickstart.json
# be sure to remove .readonly from scopes, as a forbidden error will return when trying to place event
SCOPES = 'https://www.googleapis.com/auth/calendar'
CLIENT_SECRET_FILE = 'client_secret.json'
APPLICATION_NAME = 'Google Calendar API Python Quickstart'


def get_credentials():
    """Gets valid user credentials from storage.

    If nothing has been stored, or if the stored credentials are invalid,
    the OAuth2 flow is completed to obtain the new credentials. This OAuth2 flow is only completed once for us,
    because we keep the .json file locally.
    
    Returns:
        Credentials, the obtained credential.
    """
    home_dir = os.path.expanduser('~')
    credential_dir = os.path.join(home_dir, '.credentials')
    if not os.path.exists(credential_dir):
        os.makedirs(credential_dir)
    credential_path = os.path.join(credential_dir,
                                   'calendar-python-quickstart.json')

    store = Storage(credential_path)
    credentials = store.get()
    if not credentials or credentials.invalid:
        flow = client.flow_from_clientsecrets(CLIENT_SECRET_FILE, SCOPES)
        flow.user_agent = APPLICATION_NAME
        if flags:
            credentials = tools.run_flow(flow, store, flags)
        else:  # Needed only for compatibility with Python 2.6
            credentials = tools.run(flow, store)
        print('Storing credentials to ' + credential_path)
    return credentials


def get_calendar(email, date):
    # Creates a Google Calendar API service object and outputs a list free/busy times throughout the user-defined window.

    credentials = get_credentials()
    http = credentials.authorize(httplib2.Http())
    service = discovery.build('calendar', 'v3', http=http)

    now = datetime.datetime.utcnow().isoformat() + 'Z'
    timeMax, timeMin = compute_end_datetime(date)

    print('Checking the day\'s activities for ' + email)
    body = {
      "timeMin": timeMin,
      "timeMax": timeMax,
      "timeZone": 'US/Eastern',
      "items": [{"id": email}]
    }

    eventsResult = service.freebusy().query(body=body).execute()
    return eventsResult


def compute_end_datetime(date):
    # format user date to match requirements
    user_date = date + 'T12:00:00-0400'  # DST
    # convert string user date to datetime object
    format_date = parse(user_date)
    # create end date for timemin
    end_date = format_date + datetime.timedelta(days=4, hours=5)
    # convert back to string to use in call
    timeMin = format_date.strftime('%Y-%m-%dT%H:%M:%S%z')
    timeMax = end_date.strftime('%Y-%m-%dT%H:%M:%S%z')
    return timeMax, timeMin


