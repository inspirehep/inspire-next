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

"""
Author update/addition form JSON conversion.


Converts keys in the user form to the keys needed by the HepNames data model
in order to produce MARCXML.

"""

from ..model import updateform


@updateform.over('_status', '^status$')
def status(self, key, value):
    if 'name' in self:
        self['name']['status'] = value
    else:
        self['name'] = dict(status=value)


@updateform.over('_display_name', '^display_name$')
def display_name(self, key, value):
    if 'name' in self:
        self['name']['display_name'] = value
    else:
        self['name'] = dict(display_name=value)


@updateform.over('_websites', '^websites$')
def websites(self, key, value):
    urls = []
    for website in value:
        urls.append({
            "url": website["webpage"],
            "description": ""
        })
    if 'url' in self:
        self['url'].extend(urls)
    else:
        self['url'] = urls


@updateform.over('_twitter_url', '^twitter_url$')
def twitter_url(self, key, value):
    twitter_url = {
        'url': value,
        'description': 'TWITTER'
    }
    if 'url' in self:
        self['url'].append(twitter_url)
    else:
        self['url'] = [twitter_url]


@updateform.over('_blog_url', '^blog_url$')
def blog_url(self, key, value):
    blog_url = {
        'url': value,
        'description': 'BLOG'
    }
    if 'url' in self:
        self['url'].append(blog_url)
    else:
        self['url'] = [blog_url]


@updateform.over('_linkedin_url', '^linkedin_url$')
def linkedin_url(self, key, value):
    linkedin_url = {
        'url': value,
        'description': 'LINKEDIN'
    }
    if 'url' in self:
        self['url'].append(linkedin_url)
    else:
        self['url'] = [linkedin_url]


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


@updateform.over('_public_email', '^public_email$')
def public_email(self, key, value):
    position = {
        'email': value,
        'current': 'Current'
    }
    if 'positions' in self:
        self['positions'].append(position)
    else:
        self['positions'] = [position]


@updateform.over('_research_field', '^research_field$')
def research_field(self, key, value):
    field_categories = []
    for field in value:
        field_categories.append({
            'name': field,
            'type': 'INSPIRE'
        })
    if 'field_categories' in self:
        self['field_categories'].extend(field_categories)
    else:
        self['field_categories'] = field_categories


@updateform.over('positions', '^institution_history$')
def institution_history(self, key, value):
    positions = []
    value = sorted(value,
                   key=lambda k: k["start_year"],
                   reverse=True)
    for position in value:
        positions.append({
            "institution": {'name': position["name"]},
            "status": "current" if position["current"] else "",
            "start_date": position["start_year"],
            "end_date": position["end_year"],
            "rank": position["rank"] if position["rank"] != "rank" else ""
        })

    return positions


@updateform.over('phd_advisors', '^advisors$')
def advisors(self, key, value):
    advisors = []
    for advisor in value:
        if advisor["degree_type"] == "PhD" and not advisor["full_name"]:
            continue
        advisors.append({
            "name": advisor["full_name"],
            "degree_type": advisor["degree_type"]
        })

    return advisors


@updateform.over('experiments', '^experiments$')
def experiments(self, key, value):
    experiments = []
    value = sorted(value,
                   key=lambda k: k["start_year"],
                   reverse=True)
    for experiment in value:
        experiment["status"] = "current" if experiment["status"] else ""
        experiments.append(experiment)

    return experiments
