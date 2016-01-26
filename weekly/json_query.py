# weekly/json_query.py

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

""" Query the JSON produced by weekly/payload_to_json.py """

import getopt
import json
import sys

def json_query(data, pdate, person, activity, project, tags):
    """ Converts JSON to human-readable, text-plain stats """

    for subject in json.loads(data):

        if len(subject) == 0:
            break  # Last subject
        if len(subject) != 1:
            raise RuntimeError("invalid subject: %s" % subject)
        cur_person = subject.keys()[0]
        if person != "*" and person != cur_person:
            continue

        verb = subject[cur_person]
        if len(verb) != 1:
            raise RuntimeError("invalid verb: %s" % verb)
        key = verb.keys()[0]
        if key != "weekly:did":
            raise RuntimeError("invalid verb: %s" % verb)
        obj = verb[key]

        if "weekly:project" not in obj:
            continue
        if "weekly:activity" not in obj:
            continue
        if "weekly:hours" not in obj:
            continue
        if "weekly:since" not in obj:
            continue
        if "weekly:until" not in obj:
            continue

        cur_activity = obj["weekly:activity"]
        if activity != "activity:*" and activity != cur_activity:
            continue

        cur_project = obj["weekly:project"]
        if project != "project:*" and project != cur_project:
            continue

        cur_tags = obj.get("weekly:about", None)
        if tags:
            found = 0
            for tag in tags:
                if tag in cur_tags:
                    found = 1
                    break
            if not found:
                continue
        cur_since = obj["weekly:since"]

        if pdate:
            sys.stdout.write("%s " % cur_since)
        sys.stdout.write("@%s %%%s $%s" % (cur_person.replace("people:", ""),
          cur_activity.replace("activity:", ""), cur_project.replace(
          "project:", "")))
        for tag in cur_tags:
            sys.stdout.write(" #%s" % tag.replace("tag:", ""))
        sys.stdout.write("\n")

USAGE = "python weekly/json_query.py [-d] person activity project [tag ...]"

def main(args):
    """ Main function """

    try:
        options, arguments = getopt.getopt(args[1:], "d")
    except getopt.error:
        sys.exit(USAGE)
    if len(arguments) < 3:
        sys.exit(USAGE)

    pdate = 0
    for name, _ in options:
        if name == "-d":
            pdate = 1

    person = arguments[0]
    activity = arguments[1]
    project = arguments[2]
    tags = arguments[3:]

    if not person.startswith("people:"):
        person = "people:" + person
    if not activity.startswith("activity:"):
        activity = "activity:" + activity
    if not project.startswith("project:"):
        project = "project:" + project
    new_tags = []
    for tag in tags:
        if not tag.startswith("tag:"):
            new_tags.append("tag:" + tag)
    tags = new_tags

    data = sys.stdin.read()
    json_query(data, pdate, person, activity, project, tags)

if __name__ == "__main__":
    main(sys.argv)
