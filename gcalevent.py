from __future__ import print_function
import httplib2
import os

from apiclient import discovery
from oauth2client import client
from oauth2client import tools
from oauth2client.file import Storage
import random


try:
    import argparse
    flags = argparse.ArgumentParser(parents=[tools.argparser]).parse_args()
except ImportError:
    flags = None

# If modifying these scopes, delete your previously saved credentials
# at ~/.credentials/calendar-python-quickstart.json
SCOPES = 'https://www.googleapis.com/auth/calendar'
CLIENT_SECRET_FILE = 'client_secret.json'
APPLICATION_NAME = 'Google Calendar API Python Quickstart'


prompts = [
    'What\'s one thing you are looking forward to in the next two months?',
    'What\'s your secret talent no one knows about?',
    'What\'s the best concert you\'ve ever been to?',
    'What song reflects your mood right now?',
    'Where\s your favorite place in the world',
    'Which four individuals, living or dead, would you like to eat dinner with the most?',
    'If you could be an animal, which would you be?',
    'What is the most interesting thing you are working on right now?',
    'What\'s your favorite childhood memory?'
    'What are you currently watching on Netflix?',
    'If you could visit anywhere in the world you\'ve never been, where would you go?'
          ]

# this is taken from Google's Python Quickstart guide
def get_credentials():
    """Gets valid user credentials from storage.

    If nothing has been stored, or if the stored credentials are invalid,
    the OAuth2 flow is completed to obtain the new credentials.

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

# Places the google event on the calender of recipients (email1, email2) at time determinded by (start, end)
def insert_event(email1, email2, start, end):

    credentials = get_credentials()
    http = credentials.authorize(httplib2.Http())
    service = discovery.build('calendar', 'v3', http=http)

    event = {
      "guestsCanModify": True,
      'summary': 'CoffeeChats',
      'description': 'You\'re paired for a 1:1 coffee chat! If both people in your pair are in the same region, going out for coffee/tea is the name of the game! If one or both people in the pair are remote, please use the Google Hangout link in this calendar invitation to connect. Have fun!\n\nPrompt: %s' % random.choice(prompts),
      'start': {
        'dateTime': start,
        'timeZone': 'US/Eastern',
      },
      'end': {
        'dateTime': end,
        'timeZone': 'US/Eastern',
      },
      'attendees': [
        {'email': email1},
        {'email': email2},
      ],
      'reminders': {
        'useDefault': False,
        'overrides': [
          {'method': 'popup', 'minutes': 10},
        ],
      },
    }

    #creates CoffeeChat event and outputs person 1 and 2, as well as time
    event = service.events().insert(calendarId='primary', body=event).execute()
    print('Event created: %s' % (event.get('htmlLink')))
    print('Start: {}, End: {}, Email1: Email2: {}'.format(start, end, email1, email2))
