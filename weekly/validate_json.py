# weekly/validate_json.py

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

""" Validates JSON keywords using etc/*.yaml rules """

import getopt
import logging
import json
import sys

if __name__ == "__main__":
    sys.path.insert(0, ".")

from weekly import rcfile

TOPLEV = []

def __process_obj(obj):
    """ Process the object of a tuple """
    for key in obj:
        value = obj[key]
        if value.__class__.__name__ != "unicode":
            continue
        if value.startswith("activity:"):
            if not value in TOPLEV:
                raise RuntimeError("invalid: %s" % obj[key])
        if value.startswith("project:"):
            if not value in TOPLEV:
                raise RuntimeError("invalid: %s" % obj[key])
        if value.startswith("handle:"):
            if not value in TOPLEV:
                logging.warning("invalid: %s", obj[key])
                continue
        if value.startswith("tag:"):
            if not value in TOPLEV:
                logging.warning("invalid: %s", obj[key])
                continue

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

def validate_json(data):
    """ Converts JSON to N3 """
    vector = json.loads(data)
    for subject in vector:
        __process_subject(subject)
    json.dump(vector, sys.stdout, indent=4, sort_keys=1)

USAGE = "python weekly/validate_json.py"

def main(args):
    """ Main function """

    try:
        _, arguments = getopt.getopt(args[1:], "")
    except getopt.error:
        sys.exit(USAGE)
    if len(arguments) != 0:
        sys.exit(USAGE)

    tmp_toplev = []
    rcfile.read_activity({}, {}, tmp_toplev)
    rcfile.read_handle({}, {}, tmp_toplev)
    rcfile.read_project({}, {}, tmp_toplev)
    rcfile.read_tag({}, {}, tmp_toplev)
    TOPLEV.extend(tmp_toplev)

    data = sys.stdin.read()
    validate_json(data)

if __name__ == "__main__":
    main(sys.argv)
