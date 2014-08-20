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

from invenio.modules.deposit.field_base import WebDepositField
from invenio.utils.persistentid import is_arxiv
from invenio.modules.deposit.filter_utils import strip_prefixes, strip_string

__all__ = ['ArXivField']


def arxiv_syntax_validation(form, field):
    message = "The provided arXiv ID is invalid - it should look \
                similar to 'hep-th/1234567' or '1234.5678'."

    if field.data and not is_arxiv(field.data):
        raise ValidationError(message)


class ArXivField(WebDepositField, TextField):
    def __init__(self, **kwargs):
        defaults = dict(
            icon='barcode',
            validators=[arxiv_syntax_validation],
            filters=[
                strip_string,
                strip_prefixes("arxiv:", "arXiv:"),
            ],
            description="e.g. hep-th/1234567 or 1234.5678...",
            widget_classes="form-control"
        )
        defaults.update(kwargs)
        super(ArXivField, self).__init__(**defaults)
