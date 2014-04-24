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
from invenio.modules.deposit.field_base import WebDepositField
from invenio.modules.deposit.filter_utils import strip_prefixes, strip_string

__all__ = ['ExternalSourceField']


def missing_source_warning(dummy_form, field, submit=False, fields=None):
    """
    Field processor, checking for existence of a DOI, ArXiv id or ISBN, and
    otherwise asking people to provide it.
    """
    if not field.data:
        field.add_message("Please provide a DOI, ArXiv id or ISBN if possible.",
                          state="info")
        raise StopIteration()


class ExternalSourceField(WebDepositField, TextField):
    def __init__(self, **kwargs):
        defaults = dict(
            icon='barcode',
            filters=[
                strip_string,
                strip_prefixes("arxiv:", "doi", "http://dx.doi.org/"),
            ],
            processors=[
                missing_source_warning,
            ],
            placeholder="e.g. 1234.5678, foo-bar/1234567, 10.1234/foo.bar...",
            widget_classes="form-control"
        )
        defaults.update(kwargs)
        super(ExternalSourceField, self).__init__(**defaults)
