# weekly/json_to_plot.py

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

""" Converts the JSON produced by weekly/payload_to_json.py to
    plots generated with pylab """

#
# Note: this file is still under development and may not work.
#

import collections
import datetime
import getopt
import json
import sys

import matplotlib.dates
import pylab

def json_to_plot(data):
    """ Converts JSON to human-readable, text-plain stats """

    colors = collections.deque("bgrcmykw")
    work_hours = {}

    for subject in json.loads(data):

        if len(subject) == 0:
            break  # Last subject
        if len(subject) != 1:
            raise RuntimeError("invalid subject: %s" % subject)
        user = subject.keys()[0]
        verb = subject[user]

        user = user.replace("people:", "@")
        work_hours.setdefault(user, {})

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

        hours = obj["weekly:hours"]
        project = obj["weekly:project"].replace("project:", "$")
        since = obj["weekly:since"]

        if project == "$assenza":
            hours = 0

        since = datetime.datetime.strptime(since, "%Y-%m-%d")

        work_hours[user].setdefault(since, 0)
        work_hours[user][since] += hours

    for user, userdata in work_hours.items():
        items = sorted(userdata.items())
        xdata = [elem[0] for elem in items]
        xdata = matplotlib.dates.date2num(xdata)
        ydata = [elem[1] for elem in items]
        pylab.plot_date(xdata, ydata, ls="-", label=user, c=colors.popleft())

    pylab.ylim([0, 80])
    pylab.xlabel("Date")
    pylab.ylabel("Effective work hours")
    pylab.legend()
    pylab.grid()
    pylab.show()

USAGE = "python weekly/json_to_plot.py"

def main(args):
    """ Main function """

    try:
        options, arguments = getopt.getopt(args[1:], "")
    except getopt.error:
        sys.exit(USAGE)
    if options or arguments:
        sys.exit(USAGE)

    data = sys.stdin.read()
    json_to_plot(data)

if __name__ == "__main__":
    main(sys.argv)
