# weekly/preprocess_payload.py

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

""" Preprocess payload using etc/macros.yaml rules """

import getopt
import sys

if __name__ == "__main__":
    sys.path.insert(0, ".")

from weekly import rcfile

RULES = rcfile.read_macro()

def preprocess_payload(filep):
    """ Converts JSON to N3 """
    for line in filep:

        # Get rid of the BOM
        if line.startswith("\xef\xbb\xbf.from"):
            line = line.replace("\xef\xbb\xbf.from", ".from")

        vector = line.strip().split()
        for index, token in enumerate(vector):

            # Token 'laundering': get rid of that pesky punctuation
            while token and token[0] in ('('):
                token = token[1:]
            while token and token[-1] in (';', ':', '.', ',', '-', ')'):
                token = token[:-1]
            if not token:
                continue

            # Work around the saxon genitive
            if token.endswith("'s"):
                token = token[:-2]

            if not token.startswith("!"):
                continue

            token = token.lower()
            vector[index] = RULES[token]

        line = " ".join(vector)
        sys.stdout.write("%s\n" % line)

USAGE = "python weekly/preprocess_payload.py [file...]"

def main(args):
    """ Main function """

    try:
        _, arguments = getopt.getopt(args[1:], "")
    except getopt.error:
        sys.exit(USAGE)

    if len(arguments) == 0:
        preprocess_payload(sys.stdin)
    else:
        for argument in arguments:
            filep = open(argument, "r")
            preprocess_payload(filep)
            filep.close()

if __name__ == "__main__":
    main(sys.argv)
