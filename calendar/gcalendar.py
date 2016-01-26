# -*- coding: utf-8 -*-
#
# Copyright (C) 2012 Google Inc., and
#               2013 Federico Morando <federico.morando@polito.it>
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Command-line skeleton application for Calendar API.
Usage:
  $ python sample.py

You can also get help on all the command-line flags the program understands
by running:

  $ python sample.py --help

To get detailed log output run:

  $ python sample.py --logging_level=DEBUG
"""

import email
import logging
import os
import sys
import textwrap

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(
  __file__ ))) + os.path.sep + "weekly")
import yaml

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(
  __file__ ))) + os.path.sep + "contrib")

import httplib2
import gflags

from apiclient.discovery import build
from oauth2client.file import Storage
from oauth2client.client import AccessTokenRefreshError
from oauth2client.client import flow_from_clientsecrets
from oauth2client.tools import run
from datetime import datetime # to use strptime
from datetime import date
from datetime import timedelta
from datetime import time

FLAGS = gflags.FLAGS

# CLIENT_SECRETS, name of a file containing the OAuth 2.0 information for this
# application, including client_id and client_secret.
# You can see the Client ID and Client secret on the API Access tab on the
# Google APIs Console <https://code.google.com/apis/console>
CLIENT_SECRETS = 'client_secrets.json'

# Helpful message to display if the CLIENT_SECRETS file is missing.
MISSING_CLIENT_SECRETS_MESSAGE = """
WARNING: Please configure OAuth 2.0

To make this sample run you will need to download the client_secrets.json file
and save it at:

   %s

""" % os.path.join(os.path.dirname(__file__), CLIENT_SECRETS)
# TODO: modify here to make it work without having CLIENT_SECRETS files in various places...

# Set up a Flow object to be used for authentication.
# Add one or more of the following scopes. PLEASE ONLY ADD THE SCOPES YOU
# NEED. For more information on using scopes please see
# <https://developers.google.com/+/best-practices>.
FLOW = flow_from_clientsecrets(CLIENT_SECRETS,
    scope=[
      'https://www.googleapis.com/auth/calendar.readonly',
      'https://www.googleapis.com/auth/calendar',
    ],
    message=MISSING_CLIENT_SECRETS_MESSAGE)


# The gflags module makes defining command-line options easy for
# applications. Run this program with the '--help' argument to see
# all the flags that it understands.
gflags.DEFINE_enum('logging_level', 'ERROR',
    ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'],
    'Set the level of logging detail.')

with open('etc/calendar.yaml') as config_file: CONFIG = yaml.load(config_file)

def eventextract(stuffdone, event, since, until):
    ''' Copies event information into stuffdone '''
    try:
        #
        # format like 2013-02-18T09:30:00+01:00 ...
        # reminder: Example:
        # date_object = datetime.strptime('Jun 1 2005  1:33PM',
        #                                 '%b %d %Y %I:%M%p')
        start = event['start']['dateTime']
        end = event['end']['dateTime']

        # XXX I don't know why, but %z for the time zone doesn't
        # work, not even if I remove the : from HH:MM
        start_date = datetime.strptime(start.partition('+')[0],
                                       '%Y-%m-%dT%H:%M:%S')
        end_date = datetime.strptime(end.partition('+')[0],
                                     '%Y-%m-%dT%H:%M:%S')
    except KeyError:
        return

    if start_date < since:
        start_date = since
    if end_date > until:
        end_date = until

    difference = end_date - start_date

    event['summary'] = event['summary'].lower()  # Avoid confusion

    stuffdone.setdefault(event['summary'], 0)
    stuffdone[event['summary']] += difference.total_seconds() / 3600

    return stuffdone


def __format_line_internal(key, value):
    """ Format line like '%activity #tag $project per [7.0h].' """

    vector = key.split()

    activity, tags, project, people = [], [], [], []
    for elem in vector:
        if elem[0] not in ("@", "#", "$", "%"):
            # Don't mess up with user specified phrase
            return "%s per [%.2fh]." % (key, value)

        if elem[0] == "@":
            people.append(elem)
        elif elem[0] == "#":
            tags.append(elem)
        elif elem[0] == "$":
            project.append(elem)
        elif elem[0] == "%":
            activity.append(elem)

    if len(activity) != 1:
        raise RuntimeError("invalid number of activities: '%s'" % key)
    if len(project) != 1:
        raise RuntimeError("invalid number of projects: '%s'" % key)

    vector = ["%s" % activity[0]]
    if tags:
        vector.append(" per")
        for elem in tags:
            vector.append(" ")
            vector.append(elem)
    vector.append(" nel contesto di %s" % project[0])
    if people:
        vector.append(" con")
        for elem in people:
            vector.append(" ")
            vector.append(elem)
    vector.append(" per [%.2fh]" % value)
    vector.append(".")

    return "".join(vector)


def __format_line(key, value):
    """ Format line like 'Ho fatto [7ore] di %activity #tag $project.' """
    line = __format_line_internal(key, value)
    vector = textwrap.wrap(line, 72)
    vector.extend(["", ""])
    return "\n".join(vector)


def extractlatest(service, events, token, since, until):
    """ Extracts lates events """

    stuffdone = {}

    while True:
        for event in events['items']:
            if event['status'] == "cancelled":
                continue

            try:
                start = event['start']['dateTime']
                start_date = datetime.strptime(start.partition('+')[0],
                                             '%Y-%m-%dT%H:%M:%S')
            except KeyError:
                start = event['start']['date']
                start_date = datetime.strptime(start.partition('+')[0],
                                              '%Y-%m-%d')

            try:
                end = event['end']['dateTime']
                end_date = datetime.strptime(end.partition('+')[0],
                                             '%Y-%m-%dT%H:%M:%S')
            except KeyError:
                end = event['end']['date']
                end_date = datetime.strptime(end.partition('+')[0],
                                             '%Y-%m-%d')

            if start_date > end_date:
                logging.warning("Seen event that makes no sense")
                continue

            if end_date >= since and start_date < until:
                stuffdone = eventextract(stuffdone, event, since, until)
                # XXX: andare avanti fino a cose piu' vecchie del punto di
                # partenza
                # break
        # XXX: via il    print "+1"
        # Fetch next page and continue
        page_token = events.get('nextPageToken')
        if not page_token:
            break
        events = service.events().list(calendarId=token,
                pageToken=page_token,singleEvents='true').execute()
                # "singleEvents='true'" is needed to manage repeated
                # events as ordinary ones, e.g. to make eventextract() work.
                # TODO: manage to use var. since and until here, together with parameters:
                # timeMax = Upper bound (exclusive) for an event's start time to filter by (string)
                # timeMin = Lower bound (inclusive) for an event's end time to filter by (string)
                # format: 2013-11-01T00:00:00Z

    if not stuffdone:
        sys.exit('FATAL: stuffdone is empty: Nothing happened in the '
                 'selected period of time')

    for key in sorted(stuffdone, key=stuffdone.get, reverse=True):
        sys.stdout.write("%s" % __format_line(key, stuffdone[key]))

    hours = int()
    for key in stuffdone:
        hours = hours + stuffdone[key]

    sys.stdout.write("TODO\n\n")
    sys.stdout.write("Inserisci qui i tuoi TODO...\n\n")
    sys.stdout.write("Totale: %dh %dm di lavoro\n" % (hours,
        (hours - int(hours)) * 60))

    sys.stdout.write("""
-- 
I weekly reports vengono redatti su base volontaristica, senza alcuna garanzia
di completezza e accuratezza, con l'unico fine di valutare la suddivisione di
impegno per macro-aree di ricerca, sviluppo o supporto alla policy, senza alcun
riferimento diretto a specifiche attività progettuali finanziate.

""")



MONTHS = ('', 'Gennaio', 'Febbraio', 'Marzo', 'Aprile', 'Maggio', 'Giugno',
          'Luglio', 'Agosto', 'Settembre', 'Ottobre', 'Novembre', 'Dicembre')


def __format_weekly_subject(since, until):
    """ Format weekly report email subject """
    if since.year != until.year:
        return "%d %s %d - %d %s %d" % (since.day, MONTHS[since.month],
          since.year, until.day, MONTHS[until.month], until.year)
    elif since.month != until.month:
        return "%d %s - %d %s %d" % (since.day, MONTHS[since.month],
          until.day, MONTHS[until.month], until.year)
    else:
        return "%d - %d %s %d" % (since.day, until.day, MONTHS[until.month],
          until.year)


EMAILS = CONFIG['EMAILS']
PERSONS = CONFIG['PERSONS']
USERS = CONFIG['USERS']

def main(argv):
    """ Main function """

    # Let the gflags module process the command-line arguments
    try:
        argv = FLAGS(argv)
    except gflags.FlagsError, error:
        print '%s\\nUsage: %s ARGS\\n%s' % (error, argv[0], FLAGS)
        sys.exit(1)

    # Set the logging according to the command-line flag
    logging.getLogger().setLevel(getattr(logging, FLAGS.logging_level))

    # If the Credentials don't exist or are invalid, run through the native
    # client flow. The Storage object will ensure that if successful the good
    # Credentials will get written back to a file.
    fpath = os.sep.join([os.environ['HOME'], '.weekly-calendar.json'])
    storage = Storage(fpath)
    credentials = storage.get()

    if credentials is None or credentials.invalid:
        credentials = run(FLOW, storage)

    http = httplib2.Http()
    http = credentials.authorize(http)

    service = build('calendar', 'v3', http=http)

    try:

        #
        # This dictionay contains the Google Calendar tokens for various users /
        # calendars; you can find this in the property of your Google Calendar,
        # which must by shared with the nexa.center@gmail.com account.
        # TODO: is a constant, write TOKENS
        tokens = CONFIG['TOKENS']

        # Process the command-line arguments:
        if len(argv) < 1 or len(argv) > 4:
            sys.exit("""\
usage: sample.py [name] [since] [until]
examples: sample.py [sbasso] 2013-03[-21][T12:34] 2013-03[-24][T12:34]
          sample.py [sbasso] 2013-03[-21][T13:24]  # until now
          sample.py [sbasso]  # since monday at 00:00 until now""")

        if len(argv) == 1:
            argv.append(USERS[os.environ['LOGNAME']])  # Assume POSIX OS

        if argv[1] not in tokens:
            sys.stderr.write("guessing who you are from your username...\n")
            argv.insert(1, USERS[os.environ['LOGNAME']])  # Assume POSIX OS

        if len(argv) >= 3:
            argv2 = argv[2]
            if "-" in argv2:
                argv2v_ = argv2.split("-")
                if len(argv2v_) == 2:
                    argv2 += "-01"
                if not "T" in argv2:
                    argv2 += "T00:00"
                since = datetime.strptime(argv2, '%Y-%m-%dT%H:%M')
            elif argv2 == "today":
                since = datetime.combine(date.today(), time())
            else:
                sys.exit("FATAL: invalid date argument")
        else:
            today = date.today()
            since = today - timedelta(days=today.weekday())
            since = datetime.combine(since, time())

        if len(argv) == 4:
            argv3 = argv[3]
            argv3v_ = argv3.split("-")
            #
            # Time guessing algorithm explanation:
            #
            # When the day is specified, cut at 23:59 so that the
            # email subject is what you expect.
            #
            # When the day is not specified, take the 1st of the
            # month and then subtract 60 second, so that, again, we
            # follow into the case of 23:59
            #
            # The above stuff is useful to correctly format the
            # subject, however, when requesting stuff to the
            # calendar we actually add one minute.
            #
            if len(argv3v_) == 2:
                argv3 += "-01"
                if not "T" in argv3:
                    argv3 += "T00:00"
            else:
                if not "T" in argv3:
                    argv3 += "T23:59"
            until = datetime.strptime(argv3, '%Y-%m-%dT%H:%M')
            until_robust_to_midnite = until + timedelta(seconds=60)
            if len(argv3v_) == 2:
                until = until - timedelta(seconds=60)
        else:
            until = datetime.now()
            until_robust_to_midnite = until

        sys.stdout.write("Date: %s\n" % email.utils.formatdate())
        sys.stdout.write("To: Nexa staff <nexa-staff@server-nexa.polito.it>\n")
        #sys.stdout.write("From: %s\n" % EMAILS[argv[1]])
        sys.stdout.write("Subject: %s Weekly Report: %s\n" % (
          PERSONS[argv[1]], __format_weekly_subject(since, until)))
        sys.stdout.write("\n")

        extractlatest(service, service.events().list(
          calendarId=tokens[argv[1]],singleEvents='true').execute(), tokens[argv[1]],
          since, until_robust_to_midnite)

    except AccessTokenRefreshError:
        print ("The credentials have been revoked or expired, please re-run"
               "the application to re-authorize")

if __name__ == '__main__':
    main(sys.argv)
