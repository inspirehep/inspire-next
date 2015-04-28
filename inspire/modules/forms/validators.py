# -*- coding: utf-8 -*-
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

import re

from invenio.base.globals import cfg

from wtforms.compat import string_types
from wtforms.validators import StopValidation


def ORCIDValidator(form, field):
    """Validate that the given ORCID exists."""
    from requests import RequestException
    import orcid
    msg = u"The ORCID iD was not found in <a href='http://orcid.org' target='_blank'>orcid.org</a>. Please, make sure it is valid."
    orcid_id = field.data
    api = orcid.MemberAPI(cfg["ORCID_APP_CREDENTIALS"]["consumer_key"],
                          cfg["ORCID_APP_CREDENTIALS"]["consumer_secret"])
    try:
        result = api.search_member("orcid:" + orcid_id)
        if result['orcid-search-results']["num-found"] == 0:
            raise StopValidation(msg)
    except RequestException:
        return


class RegexpStopValidator(object):
    """
    Validates the field against a user provided regexp.
    :param regex:
        The regular expression string to use. Can also be a compiled regular
        expression pattern.
    :param flags:
        The regexp flags to use, for example re.IGNORECASE. Ignored if
        `regex` is not a string.
    :param message:
        Error message to raise in case of a validation error.
    """
    def __init__(self, regex, flags=0, message=None):
        if isinstance(regex, string_types):
            regex = re.compile(regex, flags)
        self.regex = regex
        self.message = message

    def __call__(self, form, field, message=None):
        match = self.regex.match(field.data or '')
        if not match:
            if message is None:
                if self.message is None:
                    message = field.gettext('Invalid input.')
                else:
                    message = self.message

            raise StopValidation(message)
        return match
