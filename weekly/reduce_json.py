# weekly/reduce_json.py

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

""" Reduces JSON keywords using etc/*.yaml rules """

import getopt
import json
import sys

if __name__ == "__main__":
    sys.path.insert(0, ".")

from weekly import rcfile

RULES = {}
TOPLEV = ("project:all", "activity:any")

def __process_obj(obj, group_level):
    """ Process the object of a tuple """
    for key in obj:
        if obj[key].__class__.__name__ == "list":
            for index, _ in enumerate(obj[key]):
                nvalue = RULES.get(obj[key][index], obj[key][index])
                while (
                       nvalue != obj[key][index] and (group_level > 1 or
                         nvalue not in TOPLEV)
                      ):
                    obj[key][index] = nvalue
                    nvalue = RULES.get(obj[key][index], obj[key][index])
            continue
        nvalue = RULES.get(obj[key], obj[key])
        while (
               nvalue != obj[key] and (group_level > 1 or
                 nvalue not in TOPLEV)
              ):
            obj[key] = nvalue
            nvalue = RULES.get(obj[key], obj[key])

def __process_verb(verb, group_level):
    """ Process the verb of a tuple """
    if len(verb) != 1:
        raise RuntimeError("invalid verb: %s" % verb)
    key = verb.keys()[0]
    if key != "weekly:did":
        raise RuntimeError("invalid verb: %s" % verb)
    obj = verb[key]
    __process_obj(obj, group_level)

def __process_subject(subject, group_level):
    """ Process the subject of a tuple """
    if len(subject) == 0:
        return  # Last subject
    if len(subject) != 1:
        raise RuntimeError("invalid subject: %s" % subject)
    user = subject.keys()[0]
    verb = subject[user]
    __process_verb(verb, group_level)

def reduce_json(data, group_level):
    """ Reduces the JSON object """
    vector = json.loads(data)
    for subject in vector:
        __process_subject(subject, group_level)
    json.dump(vector, sys.stdout, indent=4, sort_keys=1)

USAGE = "python weekly/reduce_json.py [-g]"

def main(args):
    """ Main function """

    try:
        options, arguments = getopt.getopt(args[1:], "g")
    except getopt.error:
        sys.exit(USAGE)
    if len(arguments) != 0:
        sys.exit(USAGE)

    group_level = 0
    for name, _ in options:
        if name == "-g":
            group_level += 1

    tmp_rules, tmp_aliases = {}, {}
    rcfile.read_activity(tmp_rules, tmp_aliases, [])
    rcfile.read_project(tmp_rules, tmp_aliases, [])

    RULES.update(tmp_aliases)
    if group_level > 0:
        RULES.update(tmp_rules)

    data = sys.stdin.read()
    reduce_json(data, group_level)

if __name__ == "__main__":
    main(sys.argv)
