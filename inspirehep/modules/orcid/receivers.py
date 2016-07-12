# -*- coding: utf-8 -*-
#
# This file is part of INSPIRE.
# Copyright (C) 2016 CERN.
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
# In applying this licence, CERN does not waive the privileges and immunities
# granted to it by virtue of its status as an Intergovernmental Organization
# or submit itself to any jurisdiction.

from __future__ import absolute_import, division, print_function


from inspirehep.modules.records.signals import after_record_enhanced

from invenio_oauthclient.signals import account_setup_received

from invenio_records.signals import before_record_delete

from invenio_orcid.tasks import delete_from_orcid, send_to_orcid

from .utils import match_profiles

from flask import current_app, session, url_for


@after_record_enhanced.connect
def send_records_to_orcid(sender, *args, **kwargs):
    """ Schedules a Celery task that sends every new/updated record to orcid.

        :param sender: The record to be sented to orcid (in json format).
    """
    if current_app.config.get('ORCID_SYNCHRONIZATION_ENABLED'):
        send_to_orcid.delay(sender=sender)


@before_record_delete.connect
def delete_record_from_orcid(sender, *args, **kwargs):
    """ Schedules a Celery task that removes records from orcid.

        :param sender: The record to be deleted from orcid (in json format).
    """
    if current_app.config.get('ORCID_SYNCHRONIZATION_ENABLED'):
        delete_from_orcid.delay(sender=sender)


@account_setup_received.connect
def identify_authors_profile(remote, token, response, account_setup):
    if current_app.config.get('ORCID_PROFILE_MATCHING_ENABLED'):
        session['users_orcid'] = response['orcid']
        possible_profiles = match_profiles(token, response)
        if len(possible_profiles) > 1:
            session['oauth_possible_profiles'] = possible_profiles
            session['oauth_token_orcid_next_url'] = url_for(
                'inspire_oauthclient.match')
