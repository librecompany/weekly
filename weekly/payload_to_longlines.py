# weekly/payload_to_longlines.py

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

def process_payload(filep):
    """ Process payload """
    vector = []
    for line in filep:
        line = line.strip()
        if not line:
            if vector:
                line = " ".join(vector)
                sys.stdout.write("%s\n" % line)
                sys.stdout.write("\n")
            vector = []
            continue
        vector.append(line)


def main(args):
    """ Main function """

    try:
        _, arguments = getopt.getopt(args[1:], "")
    except getopt.error:
        sys.exit("usage: weekly/payload_to_longlines.py")
    if len(arguments) != 0:
        sys.exit("usage: weekly/payload_to_longlines.py")
    process_payload(sys.stdin)

if __name__ == "__main__":
    main(sys.argv)
