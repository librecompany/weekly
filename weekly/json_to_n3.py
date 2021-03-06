# weekly/json_to_n3.py

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

""" Converts the JSON produced by weekly/payload_to_json.py to N3 """

import getopt
import json
import sys

PREFIX = """\
@prefix activity: <http://id.nexacenter.org/activity/> .
@prefix handle: <http://id.nexacenter.org/handle/> .
@prefix people: <http://id.nexacenter.org/people/> .
@prefix project: <http://id.nexacenter.org/project/> .
@prefix tag: <http://id.nexacenter.org/tag/> .
@prefix weekly: <http://id.nexacenter.org/weekly/> .

"""

def __process_obj(obj):
    """ Process the object of a tuple """
    for key in obj:
        sys.stdout.write("    %s " % key)
        value = obj[key]

        # Guess type and treat URIs in a special way
        if value.__class__.__name__ == 'float':
            sys.stdout.write('%f' % value)
        elif value.__class__.__name__ == 'int':
            sys.stdout.write('%d' % value)
        else:
            value = value.replace('"', r'\"')
            if (
                value.startswith('activity:') or
                value.startswith('handle:') or
                value.startswith('project:') or
                value.startswith('tag:')
               ):
                sys.stdout.write('%s' % value)  # URIs
            else:
                sys.stdout.write('"%s"' % value)

        sys.stdout.write(";\n")

def __process_verb(verb):
    """ Process the verb of a tuple """
    if len(verb) != 1:
        raise RuntimeError("invalid verb: %s" % verb)
    key = verb.keys()[0]
    if key != "weekly:did":
        raise RuntimeError("invalid verb: %s" % verb)
    obj = verb[key]
    sys.stdout.write(" %s [\n" % key)
    __process_obj(obj)

def __process_subject(subject):
    """ Process the subject of a tuple """
    if len(subject) == 0:
        return  # Last subject
    if len(subject) != 1:
        raise RuntimeError("invalid subject: %s" % subject)
    user = subject.keys()[0]
    verb = subject[user]
    sys.stdout.write("%s" % user)
    __process_verb(verb)
    sys.stdout.write("] .\n\n")

def json_to_n3(data):
    """ Converts JSON to N3 """
    sys.stdout.write(PREFIX)
    for subject in json.loads(data):
        __process_subject(subject)

USAGE = "python weekly/json_to_n3.py"

def main(args):
    """ Main function """

    try:
        _, arguments = getopt.getopt(args[1:], "")
    except getopt.error:
        sys.exit(USAGE)
    if len(arguments) != 0:
        sys.exit(USAGE)

    data = sys.stdin.read()
    json_to_n3(data)

if __name__ == "__main__":
    main(sys.argv)
