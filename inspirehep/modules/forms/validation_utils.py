# -*- coding: utf-8 -*-
#
# This file is part of INSPIRE.
# Copyright (C) 2014-2017 CERN.
#
# INSPIRE is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# INSPIRE is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with INSPIRE. If not, see <http://www.gnu.org/licenses/>.
#
# In applying this license, CERN does not waive the privileges and immunities
# granted to it by virtue of its status as an Intergovernmental Organization
# or submit itself to any jurisdiction.

"""Validation functions."""

from __future__ import absolute_import, division, print_function

import re

from flask import current_app

import orcid
import six

from requests import RequestException

from wtforms.validators import StopValidation

from idutils import doi_regexp


class DOISyntaxValidator(object):

    """DOI syntax validator."""

    def __init__(self, message=None):
        """Constructor.

        :param message: message to override the default one.
        """
        self.message = message if message else (
            "The provided DOI is invalid - it should look similar to "
            "'10.1234/foo.bar'.")

    def __call__(self, form, field):
        """Validate.

        :param field: validated field.
        :param form: validated form.
        """
        doi = field.data
        if doi and not doi_regexp.match(doi):
            # no point to further validate DOI which is invalid
            raise StopValidation(self.message)


def ORCIDValidator(form, field):
    """Validate that the given ORCID exists."""
    msg = u"The ORCID iD was not found in <a href='http://orcid.org' target='_blank'>orcid.org</a>. Please, make sure it is valid."
    orcid_id = field.data
    if current_app.config.get("ORCID_APP_CREDENTIALS"):
        api = orcid.MemberAPI(current_app.config["ORCID_APP_CREDENTIALS"]["consumer_key"],
                              current_app.config["ORCID_APP_CREDENTIALS"]["consumer_secret"])
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
        if isinstance(regex, six.string_types):
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
                    message = self.message.format(field.data)

            raise StopValidation(message)
        return match
