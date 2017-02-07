# -*- coding: utf-8 -*-
#
# This file is part of INSPIRE.
# Copyright (C) 2015 CERN.
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

"""Author update/addition form JSON conversion.

Converts keys in the user form to the keys needed by the HepNames data model
in order to produce MARCXML.
"""

from __future__ import absolute_import, division, print_function

from dojson import utils
from dojson.errors import IgnoreKey

from ..model import updateform


def _set_int_or_del(mydict, key, myint):
    try:
        mydict[key] = int(myint)
    except (ValueError, TypeError):
        if key in mydict:
            del mydict[key]


@updateform.over('status', '^status$')
def status(self, key, value):
    return value


@updateform.over('native_name', '^native_name$')
def native_name(self, key, value):
    return [value]


@updateform.over('_display_name', '^display_name$')
def display_name(self, key, value):
    if 'name' in self:
        self['name']['preferred_name'] = value
    else:
        self['name'] = dict(preferred_name=value)
    raise IgnoreKey


@updateform.over('_websites', '^websites$')
def websites(self, key, value):
    urls = []
    for website in value:
        urls.append({
            "value": website["webpage"],
            "description": ""
        })
    if 'urls' in self:
        self['urls'].extend(urls)
    else:
        self['urls'] = urls
    raise IgnoreKey


@updateform.over('_twitter_url', '^twitter_url$')
def twitter_url(self, key, value):
    twitter_url = {
        'value': value,
        'description': 'TWITTER'
    }
    if 'urls' in self:
        self['urls'].append(twitter_url)
    else:
        self['urls'] = [twitter_url]
    raise IgnoreKey


@updateform.over('_blog_url', '^blog_url$')
def blog_url(self, key, value):
    blog_url = {
        'value': value,
        'description': 'BLOG'
    }
    if 'urls' in self:
        self['urls'].append(blog_url)
    else:
        self['urls'] = [blog_url]
    raise IgnoreKey


@updateform.over('_linkedin_url', '^linkedin_url$')
def linkedin_url(self, key, value):
    linkedin_url = {
        'value': value,
        'description': 'LINKEDIN'
    }
    if 'urls' in self:
        self['urls'].append(linkedin_url)
    else:
        self['urls'] = [linkedin_url]
    raise IgnoreKey


@updateform.over('_orcid', '^orcid$')
def orcid(self, key, value):
    orcid = {
        'value': value,
        'type': 'ORCID'
    }
    if 'ids' in self:
        self['ids'].append(orcid)
    else:
        self['ids'] = [orcid]
    raise IgnoreKey


@updateform.over('_bai', '^bai$')
def bai(self, key, value):
    bai = {
        'value': value,
        'type': 'BAI'
    }
    if 'ids' in self:
        self['ids'].append(bai)
    else:
        self['ids'] = [bai]
    raise IgnoreKey


@updateform.over('_inspireid', '^inspireid$')
def inspireid(self, key, value):
    inspireid = {
        'value': value,
        'type': 'INSPIRE'
    }
    if 'ids' in self:
        self['ids'].append(inspireid)
    else:
        self['ids'] = [inspireid]
    raise IgnoreKey


@updateform.over('_public_email', '^public_emails$')
def public_email(self, key, value):
    positions = []
    for email in value:
        if email['original_email'] != email['email']:
            positions.append(
                {
                    'emails': [email['email']],
                    'old_emails': [email['original_email']],
                }
            )

    if 'positions' in self:
        self['positions'].extend(positions)
    else:
        self['positions'] = positions
    raise IgnoreKey


@updateform.over('arxiv_categories', '^research_field$')
@utils.for_each_value
def inspire_categories(self, key, value):
    return {
        "term": value,
        "source": "user"
    }


@updateform.over('_positions', '^institution_history$')
def institution_history(self, key, value):
    positions = []
    value = sorted(value,
                   key=lambda k: k["start_year"],
                   reverse=True)
    for position in value:
        if not position["name"] and not position["start_year"] \
                and not position["end_year"]:
            # Empty values
            continue
        positions.append({
            "institution": {'name': position["name"]},
            "current": True if position.get("current") else False,
            "start_date": position["start_year"],
            "end_date": position["end_year"],
            "emails": position.get("emails", ""),
            "old_emails": position.get("old_emails", ""),
            "_rank": position["rank"] if position["rank"] != "rank" else ""
        })

    if 'positions' in self:
        self['positions'].extend(positions)
    else:
        self['positions'] = positions
    raise IgnoreKey


@updateform.over('advisors', '^advisors$')
def advisors(self, key, value):
    advisors = []
    for advisor in value:
        if (
            advisor["degree_type"].lower() == "phd" and
            not advisor["full_name"]
        ):
            continue

        advisors.append({
            "name": advisor["full_name"],
            "degree_type": advisor["degree_type"].lower(),
        })

    return advisors


@updateform.over('experiments', '^experiments$')
def experiments(self, key, value):
    experiments = []
    value = sorted(value,
                   key=lambda k: k["start_year"],
                   reverse=True)
    for experiment in value:
        experiment["current"] = True if experiment["status"] else False
        _set_int_or_del(experiment, "start_year", experiment.get("start_year"))
        _set_int_or_del(experiment, "end_year", experiment.get("end_year"))
        del experiment["status"]
        experiments.append(experiment)

    return experiments


@updateform.over('control_number', '^control_number$')
def control_number(self, key, value):
    return value
