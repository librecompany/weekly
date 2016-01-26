# weekly/json_to_longlines.py

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

""" Converts the JSON produced by weekly/payload_to_json.py to the
    original (but long) lines. Useful for debugging. """

import getopt
import json
import sys

def __process_obj(obj):
    """ Process the object of a tuple """
    sys.stdout.write("%s\n" % obj["weekly:orig"])

def __process_verb(verb):
    """ Process the verb of a tuple """
    if len(verb) != 1:
        raise RuntimeError("invalid verb: %s" % verb)
    key = verb.keys()[0]
    if key != "weekly:did":
        raise RuntimeError("invalid verb: %s" % verb)
    obj = verb[key]
    __process_obj(obj)

def __process_subject(subject):
    """ Process the subject of a tuple """
    if len(subject) == 0:
        return  # Last subject
    if len(subject) != 1:
        raise RuntimeError("invalid subject: %s" % subject)
    user = subject.keys()[0]
    verb = subject[user]
    __process_verb(verb)

def json_to_longlines(data):
    """ Converts JSON to long lines """
    for subject in json.loads(data):
        __process_subject(subject)
        sys.stdout.write("\n")

USAGE = "python weekly/json_to_longlines.py"

def main(args):
    """ Main function """

    try:
        _, arguments = getopt.getopt(args[1:], "")
    except getopt.error:
        sys.exit(USAGE)
    if len(arguments) != 0:
        sys.exit(USAGE)

    data = sys.stdin.read()
    json_to_longlines(data)

if __name__ == "__main__":
    main(sys.argv)
