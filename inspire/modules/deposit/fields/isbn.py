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

from wtforms import TextField
from wtforms.validators import ValidationError

from invenio_deposit.field_base import WebDepositField
from invenio_deposit.filter_utils import strip_prefixes, strip_string

from ..validators import isbn_syntax_validation

__all__ = ['ISBNField']


class ISBNField(WebDepositField, TextField):
    def __init__(self, **kwargs):
        defaults = dict(
            icon='barcode',
            validators=[isbn_syntax_validation],
            filters=[
                strip_string,
                strip_prefixes("isbn:", "ISBN:"),
            ],
            description="e.g. 1413304540 or 1-4133-0454-0 or 978-1413304541",
            widget_classes="form-control"
        )
        defaults.update(kwargs)
        super(ISBNField, self).__init__(**defaults)
