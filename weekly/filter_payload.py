# weekly/filter_payload.py

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

""" Filter payload produced by weekly/mbox.py """

import getopt
import sys

def process_payload(filep, user, automode):
    """ Process payload """
    current_user = None
    outfp = {}
    for line in filep:
        vector = line.strip().split()
        if (
            len(vector) == 6 and
            vector[0] == '.from' and
            vector[2] == 'since' and
            vector[4] == 'until'
           ):
            current_user = vector[1]
        if not user or user == current_user:
            if not automode:
                usefp = sys.stdout
            elif current_user in outfp:
                usefp = outfp[current_user]
            else:
                pathname = filep.name
                pathname = pathname.split('.')
                pathname.insert(-1, "%s" % current_user[1:])
                pathname = ".".join(pathname)
                usefp = outfp[current_user] = open(pathname, "w")

            usefp.write(line)

def main(args):
    """ Main function """

    try:
        options, arguments = getopt.getopt(args[1:], "au:")
    except getopt.error:
        sys.exit("usage: weekly/filter_payload.py [-a] [-u user] [file...]")
    automode = 0
    user = None
    for name, value in options:
        if name == "-a":
            automode = 1
        elif name == "-u":
            user = value
            if not user.startswith('@'):
                user = '@' + user

    if not arguments:
        if automode:
            sys.exit("FATAL: automode does not work with stdin")
        process_payload(sys.stdin, user, 0)
        sys.exit(0)

    for argument in arguments:
        filep = open(argument, "r")
        process_payload(filep, user, automode)
        filep.close()

if __name__ == "__main__":
    main(sys.argv)
