# weekly/json_to_stats.py

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
    human-readable, text-plain stats """

import getopt
import json
import sys

CONTEXT = {
           "APT": {},  # APT = Activity Project Tag
           "about": {},
           "about_aggregate": {},
           "activity": {},
           "activity_per_project": {},
           "hours_per_week": {},
           "project_per_week": {},
           "project": {},
           "project_per_activity": {},
           "activity_per_week": {},
          }

def __process_obj(obj):
    """ Process the object of a tuple """

    if "weekly:project" not in obj:
        return
    if "weekly:activity" not in obj:
        return
    if "weekly:hours" not in obj:
        return
    if "weekly:since" not in obj:
        return
    if "weekly:until" not in obj:
        return

    about = obj.get("weekly:about", None)
    project = obj["weekly:project"].replace("project:", "$")
    activity = obj["weekly:activity"].replace("activity:", "%")
    hours = obj["weekly:hours"]

    if about:
        aboutstr = []
        for _about in about:
            _about = _about.replace("tag:", "#")
            aboutstr.append(" ")
            aboutstr.append(_about)
        aboutstr = "".join(aboutstr)
        apt = activity + " " + project + aboutstr
    else:
        apt = activity + " " + project

    since = obj["weekly:since"]
    until = obj["weekly:until"]
    since_until = since + " => " + until

    if about:
        about_str = " ".join(about).replace("tag:", "#")
        CONTEXT["about"].setdefault(about_str, 0)
        CONTEXT["about"][about_str] += hours
        for tag in about_str.split():
            CONTEXT["about_aggregate"].setdefault(tag, 0)
            CONTEXT["about_aggregate"][tag] += hours

    CONTEXT["APT"].setdefault(apt, 0)
    CONTEXT["APT"][apt] += hours

    CONTEXT["activity"].setdefault(activity, 0)
    CONTEXT["activity"][activity] += hours

    CONTEXT["project"].setdefault(project, 0)
    CONTEXT["project"][project] += hours

    CONTEXT["activity_per_project"].setdefault(project, {})
    CONTEXT["activity_per_project"][project].setdefault(activity, 0)
    CONTEXT["activity_per_project"][project][activity] += hours

    CONTEXT["project_per_activity"].setdefault(activity, {})
    CONTEXT["project_per_activity"][activity].setdefault(project, 0)
    CONTEXT["project_per_activity"][activity][project] += hours

    CONTEXT["activity_per_week"].setdefault(since_until, {})
    CONTEXT["activity_per_week"][since_until].setdefault(project, {})
    CONTEXT["activity_per_week"][since_until][project].setdefault(activity, 0)
    CONTEXT["activity_per_week"][since_until][project][activity] += hours

    CONTEXT["project_per_week"].setdefault(since_until, {})
    CONTEXT["project_per_week"][since_until].setdefault(activity, {})
    CONTEXT["project_per_week"][since_until][activity].setdefault(project, 0)
    CONTEXT["project_per_week"][since_until][activity][project] += hours

    CONTEXT["hours_per_week"].setdefault(since_until, 0)
    CONTEXT["hours_per_week"][since_until] += hours

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
    CONTEXT['current_user'] = user
    verb = subject[user]
    __process_verb(verb)

def __print_stats(title, data):
    """ Helper function to print stats """
    total = sum(data.values())
    sys.stdout.write("\n- %s (total: %.1fh)\n" % (title, total))
    select_value = lambda couple: couple[1]
    for key, value in sorted(data.items(), key=select_value, reverse=1):
        percentage = 100.0 * (value / total)
        sys.stdout.write("    - \"%s\": %.1fh %.1f%%\n" % (key,
                         value, percentage))

def __selina_print_stats(period, title, data):
    """ Helper function to print stats useful for Selina """
    total = sum(data.values())
    sys.stdout.write("\n- \"%s\", %s, %.1fh\n" % (period, title, total))

def json_to_stats(data, selina_mode):
    """ Converts JSON to human-readable, text-plain stats """

    for subject in json.loads(data):
        __process_subject(subject)

    if selina_mode:
        for period in sorted(CONTEXT["activity_per_week"]):
            for prj in sorted(CONTEXT["activity_per_week"][period]):
                if prj != selina_mode:
                    continue
                __selina_print_stats(period, prj, CONTEXT["activity_per_week"][
                                     period][prj])
        return

    __print_stats("APT stats", CONTEXT["APT"])
    __print_stats("All activity stats", CONTEXT["activity"])
    __print_stats("All project stats", CONTEXT["project"])
    __print_stats("Aggregate tags stats", CONTEXT["about_aggregate"])
    __print_stats("All tags stats", CONTEXT["about"])
    for prj in sorted(CONTEXT["activity_per_project"]):
        __print_stats("%s stats" % prj, CONTEXT["activity_per_project"][prj])
    for act in sorted(CONTEXT["project_per_activity"]):
        __print_stats("%s stats" % act, CONTEXT["project_per_activity"][act])

    sys.stdout.write("\n")
    for period in sorted(CONTEXT["project_per_week"]):
        sys.stdout.write("# *** BEGIN %s [%.2f h] ***\n" %( period,
          CONTEXT["hours_per_week"][period]))
        for act in sorted(CONTEXT["activity_per_week"][period]):
            __print_stats("%s stats" % act,
               CONTEXT["activity_per_week"][period][act])
        for prj in sorted(CONTEXT["project_per_week"][period]):
            __print_stats("%s stats" % prj,
               CONTEXT["project_per_week"][period][prj])
        sys.stdout.write("\n# *** END %s ***\n\n" % period)

USAGE = "python weekly/json_to_stats.py"

def main(args):
    """ Main function """

    try:
        options, arguments = getopt.getopt(args[1:], "S:")
    except getopt.error:
        sys.exit(USAGE)
    if len(arguments) != 0:
        sys.exit(USAGE)

    selina_mode = None
    for name, value in options:
        if name == "-S":
            if not value.startswith("$"):
                value = "$" + value
            selina_mode = value

    data = sys.stdin.read()
    json_to_stats(data, selina_mode)

if __name__ == "__main__":
    main(sys.argv)
