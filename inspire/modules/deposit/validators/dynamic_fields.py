#
## This file is part of INSPIRE.
## Copyright (C) 2014 CERN.
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

from wtforms.validators import StopValidation


class AuthorsValidation(object):
    """
    Validate authors field.

    empty_aff: validates if there are empty names with filled affiliations.

    author_names: validates if there is at least one author.
    """
    field_flags = ('required', )

    def __init__(self, form, field):
        empty_aff = filter(lambda x: x['name'] == '' and x['affiliation'] != '',
                           field.data)

        author_names = filter(lambda x: x['name'] != '', field.data)

        if empty_aff:
            message = field.gettext('Affiliations should have an author name associated.')
            raise StopValidation(message)
        elif not author_names:
            message = field.gettext('At least one author is required.')
            raise StopValidation(message)
