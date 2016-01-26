# weekly/json_fix_date.py

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

""" Fixes the weeklies dates from 20-07-2013 to 2013-07-20 """

import getopt
import json
import sys

USAGE = "python weekly/json_fix_date.py"

def main(args):
    """ Main function """

    try:
        _, arguments = getopt.getopt(args[1:], "")
    except getopt.error:
        sys.exit(USAGE)
    if len(arguments) != 0:
        sys.exit(USAGE)

    data = sys.stdin.read()
    vector = json.loads(data)
    for entry in vector:
        for name, value in entry.items():
            for name, container in value.items():

                for name in container:
                    if name not in ("weekly:since", "weekly:until"):
                        continue

                    value = container[name]
                    tokens = value.split("-")
                    if len(tokens[2]) != 4:
                        continue

                    value = "-".join([tokens[2], tokens[1], tokens[0]])
                    container[name] = value

    json.dump(vector, sys.stdout)

if __name__ == "__main__":
    main(sys.argv)
