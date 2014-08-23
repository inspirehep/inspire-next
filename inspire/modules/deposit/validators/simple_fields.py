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

from wtforms.validators import ValidationError

from invenio.utils.persistentid import is_arxiv, is_isbn


def arxiv_syntax_validation(form, field):
    """Validate ArXiv ID syntax."""
    message = "The provided ArXiv ID is invalid - it should look \
                similar to 'hep-th/1234567' or '1234.5678'."

    if field.data and not is_arxiv(field.data):
        raise ValidationError(message)


def isbn_syntax_validation(form, field):
    """Validate ISBN syntax."""
    message = "The provided ISBN is invalid - it should look \
                similar to '1413304540', '1-4133-0454-0', '978-1413304541' or \
                '978-1-4133-0454-1'."

    if field.data and not is_isbn(field.data):
        raise ValidationError(message)
