# -*- coding: utf-8 -*-
## This file is part of Invenio.
## Copyright (C) 2014 CERN.
##
## Invenio is free software; you can redistribute it and/or
## modify it under the terms of the GNU General Public License as
## published by the Free Software Foundation; either version 2 of the
## License, or (at your option) any later version.
##
## Invenio is distributed in the hope that it will be useful, but
## WITHOUT ANY WARRANTY; without even the implied warranty of
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
## General Public License for more details.
##
## You should have received a copy of the GNU General Public License
## along with Invenio; if not, write to the Free Software Foundation, Inc.,
## 59 Temple Place, Suite 330, Boston, MA 02111-1307, USA.

from invenio.modules.knowledge.api import (
    add_kb_mapping,
    get_kbr_values,
    kb_mapping_exists,
)


def get_value(kb_name, list_of_keys):
    """Get the value registered with at least one of the keys."""
    for key in list_of_keys:
        if kb_mapping_exists(kb_name, key):
            return get_kbr_values(kb_name, key)[0][0]


def check_keys(kb_name, list_of_keys):
    """Check the KB if any of the keys exists."""
    for key in list_of_keys:
        if kb_mapping_exists(kb_name, key):
            return True
    return False


def save_keys_to_kb(kb_name, list_of_keys, value):
    """Add all the keys in the KB with the same value."""
    if check_keys(kb_name, list_of_keys):
        old_value = get_value(kb_name, list_of_keys)
        # Adds any possible new identifier to the KB
        for key in list_of_keys:
            add_kb_mapping(kb_name, key, old_value)
    else:
        for key in list_of_keys:
            add_kb_mapping(kb_name, key, value)
