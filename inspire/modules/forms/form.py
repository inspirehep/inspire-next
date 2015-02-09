#
## This file is part of INSPIRE.
## Copyright (C) 2015 CERN.
##
## INSPIRE is free software; you can redistribute it and/or
## modify it under the terms of the GNU General Public License as
## published by the Free Software Foundation; either version 2 of the
## License, or (at your option) any later version.
##
## INSPIRE is distributed in the hope that it will be useful, but
## WITHOUT ANY WARRANTY; without even the implied warranty of
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
## General Public License for more details.
##
## You should have received a copy of the GNU General Public License
## along with INSPIRE; if not, write to the Free Software Foundation, Inc.,
## 59 Temple Place, Suite 330, Boston, MA 02111-1307, USA.
#

from flask.ext.wtf import Form

CFG_GROUPS_META = {
    'classes': None,
    'indication': None,
    'description': None
}


class InspireForm(Form):

    """Generic Form class to be used in INSPIRE forms. """

    def __init__(self, *args, **kwargs):
        super(InspireForm, self).__init__(*args, **kwargs)

    def get_groups(self):
        """Get a list of the (group metadata, list of fields)-tuples.

        The last element of the list has no group metadata (i.e. None),
        and contains the list of fields not assigned to any group.
        """
        fields_included = set()
        field_groups = []

        if hasattr(self, 'groups'):
            for group in self.groups:
                group_obj = {
                    'name': group[0],
                    'meta': CFG_GROUPS_META.copy(),
                }

                fields = []
                for field_name in group[1]:
                    if field_name in ['-', ]:
                        fields.append(field_name)
                    else:
                        try:
                            fields.append(self[field_name])
                            fields_included.add(field_name)
                        except KeyError:
                            pass

                if len(group) == 3:
                    group_obj['meta'].update(group[2])

                field_groups.append((group_obj, fields))

        # Append missing fields not defined in groups
        rest_fields = []
        for field in self:
            if field.name not in fields_included:
                rest_fields.append(field)
        if rest_fields:
            field_groups.append((None, rest_fields))

        return field_groups
