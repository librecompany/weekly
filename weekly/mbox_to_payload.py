# weekly/mbox_to_payload.py

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

""" Process mbox and feed the payload parser """

import email.parser
import logging
import mailbox
import sys

import getopt

try:
    from io import StringIO  # Python 3.x
except ImportError:
    from StringIO import StringIO  # Python 2.x

MONTHS = {
          "gennaio": "01",
          "febbraio": "02",
          "marzo": "03",
          "aprile": "04",
          "maggio": "05",
          "giugno": "06",
          "luglio": "07",
          "agosto": "08",
          "settembre": "09",
          "ottobre": "10",
          "novembre": "11",
          "dicembre": "12",
         }

NAME_TO_HANDLE = {
                  'claudio': '@cartusio',
                  'giuseppe': '@gfutia',
                  'nadia': '@ntecco',
                  'raimondo': '@riemma',
                 }

class MboxEx(mailbox.mbox):
    """ Extended mailbox that works also with stdin """

    def __init__(self, filep):
        mailbox.mbox.__init__(self, "/dev/null")
        self._file = filep  # XXX

def process_message(message, user):
    """ Process a single message """
    subject = message["subject"]
    subject = subject.lower()
    subject = subject.replace("[nexa-staff]", "")
    subject = subject.replace("\n", " ")
    subject = subject.strip()
    subject = " ".join(subject.split())
    if subject.startswith('fwd:'):
        subject = subject[4:].strip()
    if "weekly report" not in subject:
        return

    index = subject.find("weekly report:")
    if index == -1:
        index = subject.find("weekly report ")
    name = subject[:index]
    period = subject[index + len("weekly report "):]  # XXX

    name = name.replace("weekly report", "")
    name = name.strip()
    vector = name.split()
    if len(vector) == 2:
        name, surname = vector
        handle = "@" + name[0] + surname
    elif len(vector) == 1:
        handle = NAME_TO_HANDLE[vector[0]]
    else:
        logging.warning("invalid subject: %s", message['subject'])
        return

    if user and handle != user:
        return

    period = period.strip()
    index = period.find("-")
    if index == -1:
        logging.warning("invalid subject: %s", message["subject"])
        return

    period_until = period[index + 1:]
    period_until = period_until.strip()
    period_until = period_until.split()
    if len(period_until) != 3:
        logging.warning("invalid subject: %s", message["subject"])
        return

    period_since = period[:index]
    period_since = period_since.strip()
    period_since = period_since.split()
    if len(period_since) < 1 or len(period_since) > 3:
        logging.warning("invalid subject: %s", message["subject"])
        return
    if len(period_since) == 1:
        period_since.append(period_until[1])
        period_since.append(period_until[2])
    elif len(period_since) == 2:
        period_since.append(period_until[2])

    period_until[0] = "%02d" % int(period_until[0])
    period_until[1] = MONTHS[period_until[1]]
    period_since[0] = "%02d" % int(period_since[0])
    period_since[1] = MONTHS[period_since[1]]

    #
    # Rewrite the date from 20-07-2013 to 2013-07-20, because
    # the latter is much more easily sortable.
    #
    period_since[0], period_since[2] = period_since[2], period_since[0]
    period_until[0], period_until[2] = period_until[2], period_until[0]

    period_since = "-".join(period_since)
    period_until = "-".join(period_until)

    sys.stdout.write(".from %s since %s until %s\n\n" % (handle,
      period_since, period_until))

    for part in message.walk():
        if not part.get_content_type().startswith("text/plain"):
            continue
        payload = part.get_payload()
        index = payload.find("-------------- next part --------------")
        if index != -1:
            payload = payload[:index]

        #
        # Fix line endings
        #
        new_payload = []
        for line in payload.split("\n"):
            line = line.rstrip()
            new_payload.append(line)
        payload = "\n".join(new_payload)

        sys.stdout.write("%s" % payload)
        sys.stdout.write("\n\n")
        break

def process_mbox(filep, user):
    """ Process mbox """
    mbox = MboxEx(filep)
    for message in mbox:
        process_message(message, user)

def process_single_email(filep, user):
    """ Process a single email """
    data = filep.read()
    if filep != sys.stdin:  # Same behavior as before refactoring
        filep.close()
    parser = email.parser.FeedParser()
    parser.feed(data)
    message = parser.close()
    process_message(message, user)

def cat(argument):
    """ Cat file content to stdout """
    sys.stdout.write(open(argument, "r").read())
    sys.stdout.flush()

def main(args):
    """ Main function """

    try:
        options, arguments = getopt.getopt(args[1:], "aeu:")
    except getopt.error:
        sys.exit("usage: weekly/mbox_to_payload.py [-ae] [-u user] [file...]")

    auto = False
    single_email = False
    user = None
    for name, value in options:
        if name == "-a":
            auto = True
        elif name == "-e":
            single_email = True
        elif name == "-u":
            user = value

    if single_email:
        if not arguments:
            if auto:
                sys.exit("mbox_to_payload: -a not implemented with stdin")
            process_single_email(sys.stdin, user)
        for argument in arguments:
            if auto and not argument.endswith(".eml"):
                cat(argument)
                continue
            process_single_email(open(argument, "rb"), user)
        sys.exit(0)

    if not arguments:
        if auto:
            sys.exit("mbox_to_payload: -a not implemented with stdin")
        process_mbox(StringIO(sys.stdin.read()), user)
    for argument in arguments:
        if auto and not argument.endswith(".eml"):
            cat(argument)
            continue
        process_mbox(open(argument, "rb"), user)

if __name__ == "__main__":
    main(sys.argv)
