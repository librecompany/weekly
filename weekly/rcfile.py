# weekly/rcfile.py

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

""" Read configuration file """

import collections
import json
import logging
import os
import sys

PREFIX = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SYSCONFDIR = os.sep.join([PREFIX, "etc"])

if __name__ == "__main__":
    sys.path.insert(0, PREFIX)

from weekly import utils
from weekly import yaml

def _install_alias(table, prefix, name):
    """ Install aliases info into the proper table """
    namev = name.split()
    for name in namev[1:]:
        table[prefix + utils.normalize_token(name)] = prefix + \
          utils.normalize_token(namev[0])

def gather_aliases(aliases, prefix, table):
    """ Gather aliases from the given table """
    for elem in table:
        if elem.__class__.__name__ == "dict":
            for key in elem:
                value = elem[key]
                if " " in key:
                    _install_alias(aliases, prefix, key)
                gather_aliases(aliases, prefix, value)
            continue
        if " " in elem:
            _install_alias(aliases, prefix, elem)

def _install_hier(hier, parent, prefix, name):
    """ Install hierarchy info into the proper table """
    namev = name.split()
    canon = prefix + utils.normalize_token(namev[0])
    if parent:
        hier[canon] = parent
    return canon

def gather_hier(hier, prefix, parent, table):
    """ Gather hierarchy from the given table """
    for elem in table:
        if elem.__class__.__name__ == "dict":
            for key in elem:
                value = elem[key]
                new_parent = _install_hier(hier, parent, prefix, key)
                gather_hier(hier, prefix, new_parent, value)
            continue
        _install_hier(hier, parent, prefix, elem)

def _install_toplev(toplev, prefix, elem):
    """ Install toplevel info into the proper table """
    elemv = elem.split()
    canon = prefix + utils.normalize_token(elemv[0])
    toplev.append(canon)

def gather_toplev(toplev, prefix, table):
    """ Gather toplevel elements from the given table """
    for elem in table:
        if elem.__class__.__name__ == "dict":
            for key in elem:
                _install_toplev(toplev, prefix, key)
            continue
        _install_toplev(toplev, prefix, elem)

def read_file(path):
    """ Read configuration file """
    filep = open(path, "r")
    table = yaml.safe_load(filep)
    return table

def read_activity(hier, aliases, toplev):
    """ Read projects description file """
    prefix = "activity:"
    path = os.sep.join([SYSCONFDIR, "activity.yaml"])
    table_tmp = read_file(path)
    gather_aliases(aliases, prefix, table_tmp)
    gather_hier(hier, prefix, "", table_tmp)
    gather_toplev(toplev, prefix, table_tmp)

def read_handle(hier, aliases, toplev):
    """ Read projects description file """
    prefix = "handle:"
    path = os.sep.join([SYSCONFDIR, "handle.yaml"])
    table_tmp = read_file(path)
    gather_aliases(aliases, prefix, table_tmp)
    gather_hier(hier, prefix, "", table_tmp)
    gather_toplev(toplev, prefix, table_tmp)

def read_macro():
    """ Read macros descriptor file """
    path = os.sep.join([SYSCONFDIR, "macro.yaml"])
    return read_file(path)

def read_project(hier, aliases, toplev):
    """ Read projects description file """
    prefix = "project:"
    path = os.sep.join([SYSCONFDIR, "topics.yaml"])
    table_tmp = read_file(path)
    gather_aliases(aliases, prefix, table_tmp)
    gather_hier(hier, prefix, "", table_tmp)
    gather_toplev(toplev, prefix, table_tmp)

def read_tag(hier, aliases, toplev):
    """ Read projects description file """
    prefix = "tag:"
    path = os.sep.join([SYSCONFDIR, "tag.yaml"])
    table_tmp = read_file(path)
    gather_aliases(aliases, prefix, table_tmp)
    gather_hier(hier, prefix, "", table_tmp)
    gather_toplev(toplev, prefix, table_tmp)

def main():
    """ Main function """
    hier = {}
    aliases = {}
    toplev = []
    read_activity(hier, aliases, toplev)
    read_handle(hier, aliases, toplev)
    macros = read_macro()
    read_project(hier, aliases, toplev)
    read_tag(hier, aliases, toplev)
    overall = {
        "aliases": aliases,
        "hier": hier,
        "macros": macros,
        "toplev": toplev,
    }
    json.dump(overall, sys.stdout, indent=4, sort_keys=1)
    sys.stdout.write("\n")

if __name__ == "__main__":
    main()
