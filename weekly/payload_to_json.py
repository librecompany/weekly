# weekly/payload_to_json.py

#
# Copyright (c) 2013 Simone Basso <bassosimone@gmail.com>
#
# Permission to use, copy, modify, and distribute this software for any
# purpose with or without fee is hereby granted, provided that the above
# copyright notice and this permission notice appear in all copies.
#
# THE SOFTWARE IS PROVIDED "AS IS" AND THE AUTHOR DISCLAIMS ALL WARRANTIES
# WITH REGARD TO THIS SOFTWARE INCLUDING ALL IMPLIED WARRANTIES OF
# MERCHANTABILITY AND FITNESS. IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR
# ANY SPECIAL, DIRECT, INDIRECT, OR CONSEQUENTIAL DAMAGES OR ANY DAMAGES
# WHATSOEVER RESULTING FROM LOSS OF USE, DATA OR PROFITS, WHETHER IN AN
# ACTION OF CONTRACT, NEGLIGENCE OR OTHER TORTIOUS ACTION, ARISING OUT OF
# OR IN CONNECTION WITH THE USE OR PERFORMANCE OF THIS SOFTWARE.
#

''' Converts the email payload produced by weekly/mbox.py to JSON '''

import logging
import getopt
import sys
import re

if __name__ == "__main__":
    sys.path.insert(0, ".")

from weekly import utils

TIME_SPENT = re.compile(r'\[\s*([0-9]*[.,]?[0-9]+)\s*([hdt])\s*\]')

def __parse_time_spent(index, line):
    ''' Processes the `time spent` string '''

    #
    # We need to parse the whole line because '[16 h]' is two tokens, so it is
    # not practical to parse it on the fly. We search for the last couple of
    # brackets, which allows the user to override the time specified by macros.
    #
    index = line.rfind('[')
    if index < 0:
        return
    line = line[index:]
    index = line.rfind(']')
    if index < 0:
        return
    token = line[:index + 1]

    logging.debug('%d: possible time token: %s', index, token)
    match = TIME_SPENT.match(token)
    if match:
        number = match.group(1)
        if number:
            spent = float(number.replace(',', '.'))  # bah, italians...
        else:
            spent = 1
        modifier = match.group(2)
        if modifier == 'h':
            logging.debug('%d: hours: %f', index, spent)
            spent *= 1  # already in hours
        elif modifier == 'd':
            logging.debug('%d: days: %f', index, spent)
            spent *= 8  # 8 hours a day
        elif modifier == 't':
            logging.debug('%d: tomatoes: %f', index, spent)
            spent *= 0.5  # 2 tomatoes per hour
        else:
            raise RuntimeError('Internal error')
        sys.stdout.write('        "weekly:hours": %f,\n' % spent)

def __new_state():
    ''' Returns new, empty state '''
    return {
            'activity': None,
            'handles': set(),
            'initialized': False,
            'lines': [],
            'project': None,
            'tags': set(),
           }

def __end_of_record(index, state):
    ''' Activities to perform at end of record '''
    lines = ' '.join(state['lines']).replace('"', r'\"')
    if not lines:
        return
    __parse_time_spent(index, lines)
    logging.debug('%d: end of record', index)
    logging.debug('%d: cumulated state: %s', index, state)
    if state["activity"] == None:
        logging.warning("%d: activity is None: %s", index, state)
    if state["project"] == None:
        logging.warning("%d: project is None: %s", index, state)
    sys.stdout.write('        "weekly:activity": "activity:%s",\n'
      % state["activity"])
    sys.stdout.write('        "weekly:project": "project:%s",\n'
      % state["project"])
    sys.stdout.write('        "weekly:about": [')
    for index, tag in enumerate(state["tags"]):
        sys.stdout.write('"tag:%s"' % tag)
        if index < len(state["tags"]) - 1:
            sys.stdout.write(", ")
    sys.stdout.write('],\n')
    sys.stdout.write('        "weekly:with": [')
    for index, handle in enumerate(state["handles"]):
        sys.stdout.write('"handle:%s"' % handle)
        if index < len(state["handles"]) - 1:
            sys.stdout.write(", ")
    sys.stdout.write('],\n')
    sys.stdout.write('        "weekly:orig": "%s"\n' % lines)
    sys.stdout.write('    }}},\n\n')

def parse(payload, person=None, since=None, until=None):
    ''' Processes the email payload '''

    index = 0  # Just in case we don't enter the loop

    state = __new_state()
    started = 0
    for index, line in enumerate(payload.splitlines()):

        line = line.strip()
        logging.debug('%d: << "%s"', index, line)
        tokens = line.split()

        if len(tokens) == 1:
            if tokens[0].lower() == 'todo' or tokens[0] == '--':
                logging.debug('%d: end of parsing', index)
                person, since, until = None, None, None
                started = 0
                continue

        if len(tokens) == 0:
            if not started:
                logging.debug('%d: skipping empty line', index)
                continue
            __end_of_record(index, state)
            state = __new_state()
            started = 0  # We're now in the middle of nowhere
            logging.debug('%d: resetting state: %s', index, state)
            continue

        #
        # Weekly/mbox.py uses the string ".from <person> since <since>
        # until <until>" to signal that the sender changed and to indicate
        # the reporting period.
        #
        if (len(tokens) == 6 and tokens[0].lower() == '.from' and
            tokens[1].startswith('@') and tokens[2].lower() == 'since' and
            tokens[4].lower() == 'until'):
            logging.debug('%d: person: %s -> %s', index, person, tokens[1])
            person = tokens[1]
            person = person[1:]
            since = tokens[3]
            until = tokens[5]
            continue

        if not started and not person and not since and not until:
            logging.debug("%d: not started yet", index)
            continue

        # Make sure we have person, since and until
        if not person:
            raise RuntimeError('%d: person is not set' % index)
        if not since:
            raise RuntimeError('%d: since is not set' % index)
        if not until:
            raise RuntimeError('%d: until is not set' % index)

        started = 1  # we're now parsing the weekly
        if not state["initialized"]:
            sys.stdout.write('    {"people:%s": {"weekly:did": {\n' % person)
            sys.stdout.write('        "weekly:since": "%s",\n' % since)
            sys.stdout.write('        "weekly:until": "%s",\n' % until)
            state["initialized"] = 1
        state["lines"].append(line)

        for token in tokens:

            # Token 'laundering': get rid of that pesky punctuation
            while token and token[0] in ('('):
                token = token[1:]
            while token and token[-1] in (';', ':', '.', ',', '-', ')'):
                token = token[:-1]
            if not token:
                continue

            # Work around english possessive
            if token.endswith("'s"):
                token = token[:-2]

            if token.startswith('%'):
                token = token[1:]
                logging.debug('%d: activity: %s', index, token)
                token = utils.normalize_token(token)
                state['activity'] = token
            elif token.startswith('$'):
                token = token[1:]
                logging.debug('%d: project: %s', index, token)
                token = utils.normalize_token(token)
                state['project'] = token
            elif token.startswith('#'):
                token = token[1:]
                logging.debug('%d: tag: %s', index, token)
                if token.startswith("-"):
                    token = utils.normalize_token(token)
                    if token in state["tags"]:
                        logging.debug('%d: remove tag: %s', index, token)
                        state["tags"].remove(token)
                else:
                    token = utils.normalize_token(token)
                    logging.debug('%d: add tag: %s', index, token)
                    state["tags"].add(token)
            elif token.startswith('@'):
                token = token[1:]
                logging.debug('%d: handle: %s', index, token)
                if token.startswith("-"):
                    token = utils.normalize_token(token)
                    if token in state["handles"]:
                        logging.debug('%d: remove handle: %s', index, token)
                        state["handles"].remove(token)
                else:
                    token = utils.normalize_token(token)
                    logging.debug('%d: add handle: %s', index, token)
                    state["handles"].add(token)
            elif token.startswith('['):
                pass  # We deal with it later; because '[16 h]' is two tokens
            else:
                pass  # nothing

    if started:
        __end_of_record(index, state)


USAGE = '''\
python weekly/payload_to_json.py [-S since] [-u person] [-U until] [file...]'''

def main(args):
    ''' Main function '''

    try:
        options, arguments = getopt.getopt(args[1:], 'S:u:U:v')
    except getopt.error:
        sys.exit(USAGE)

    since, until = None, None
    person = None
    for name, value in options:
        if name == '-S':
            since = value
        elif name == '-u':
            person = value
        elif name == '-U':
            until = value
        elif name == '-v':
            logging.getLogger().setLevel(logging.DEBUG)

    sys.stdout.write('[\n')

    if len(arguments) == 0:
        parse(sys.stdin.read(), person, since, until)
    else:
        for path in arguments:
            filep = open(path, 'r')
            parse(filep.read(), person, since, until)
            filep.close()

    sys.stdout.write('    {}\n')
    sys.stdout.write(']\n')

if __name__ == '__main__':
    main(sys.argv)
