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

from __future__ import absolute_import, division, print_function

from flask_login import current_user

from inspirehep.utils.record import get_title
from inspirehep.modules.records.json_ref_loader import replace_refs
from inspirehep.modules.records.api import ESRecord
from inspirehep.modules.records.permissions import has_update_permission
from inspirehep.modules.search import JobsSearch


class AdminToolsMixin(object):
    @property
    def admin_tools(self):
        tools = []
        if has_update_permission(current_user, self):
            tools.append('editor')
        return tools


class LiteratureRecord(ESRecord, AdminToolsMixin):
    """Record class specialized for literature records."""

    def set_links_for_ids(self, extid, ext_sys_id_info):
        """Urls and names for external system identifiers

        Returns a dictionary that contains the name of the
        external_system_identifier as the key and it's url as the value
        """
        if ext_sys_id_info[0] == 'KEK scanned document':
            extid = extid.replace("-", "")
            # Assumption - The Kek ids will always be either 7 or 9
            # digits long (after replacing the '-'s)
            if len(extid) == 7 and not extid.startswith('19') and not extid.startswith('20'):
                year = '19' + extid[:2] + '/'
            elif len(extid) == 9:
                year = extid[:4] + '/'
                extid = extid[2:]
            yymm = extid[:4] + '/'
            return {'url_name': ext_sys_id_info[0],
                    'url_link': ext_sys_id_info[1] + year + yymm + extid + '.pdf'}
        else:
            return {'url_name': ext_sys_id_info[0],
                    'url_link': ext_sys_id_info[1] + extid}

    @property
    def title(self):
        """Get preferred title."""
        return get_title(self)

    @property
    def conference_information(self):
        """Conference information.

        Returns a list with information about conferences related to the
        record.
        """
        conf_info = []
        for pub_info in self['publication_info']:
            conference_recid = None
            parent_recid = None
            parent_rec = {}
            conference_rec = {}
            if 'conference_record' in pub_info:
                conference_rec = replace_refs(pub_info['conference_record'],
                                              'es')
                if conference_rec and conference_rec.get('control_number'):
                    conference_recid = conference_rec['control_number']
                else:
                    conference_rec = {}
            if 'parent_record' in pub_info:
                parent_rec = replace_refs(pub_info['parent_record'], 'es')
                if parent_rec and parent_rec.get('control_number'):
                    parent_recid = parent_rec['control_number']
                else:
                    parent_rec = {}
            conf_info.append(
                {
                    "conference_recid": conference_recid,
                    "conference_title": get_title(conference_rec),
                    "parent_recid": parent_recid,
                    "parent_title":
                        get_title(parent_rec).replace(
                            "Proceedings, ", "", 1
                    ),
                    "page_start": pub_info.get('page_start'),
                    "page_end": pub_info.get('page_end'),
                    "artid": pub_info.get('artid'),
                }
            )

        return conf_info

    @property
    def publication_information(self):
        """Publication information.

        Returns a list with information about each publication note in
        the record.
        """
        pub_info_list = []
        for pub_info in self['publication_info']:
            if pub_info.get('journal_title', '') or pub_info.get('pubinfo_freetext', ''):
                pub_info_list.append({
                    'journal_title': pub_info.get('journal_title', ''),
                    'journal_volume': pub_info.get('journal_volume', ''),
                    'year': str(pub_info.get('year', '')),
                    'journal_issue': pub_info.get('journal_issue', ''),
                    'page_start': str(pub_info.get('page_start', '')),
                    'page_end': str(pub_info.get('page_end', '')),
                    'artid': pub_info.get('artid', ''),
                    'pubinfo_freetext': pub_info.get('pubinfo_freetext', '')
                })

        return pub_info_list

    @property
    def external_system_identifiers(self):
        """External system identification information.

        Returns a list that contains information on first of each kind of
        external_system_idenitfiers
        """
        ext_id_dict = {
            'ads': [
                'ADS Abstract Service',
                'http://adsabs.harvard.edu/abs/',
            ],
            'cds': [
                'CERN Document Server',
                'http://cds.cern.ch/record/'
            ],
            'euclid': [
                'Project Euclid',
                'http://projecteuclid.org/',
            ],
            'hal': [
                'HAL Archives Ouvertes',
                'https://hal.archives-ouvertes.fr/',
            ],
            'kekscan': [
                'KEK scanned document',
                'https://lib-extopc.kek.jp/preprints/PDF/',
            ],
            'msnet': [
                'AMS MathSciNet',
                'http://www.ams.org/mathscinet-getitem?mr=',
            ],
            'osti': [
                'OSTI Information Bridge Server',
                'https://www.osti.gov/scitech/biblio/',
            ],
            'zblatt': [
                'zbMATH',
                'http://www.zentralblatt-math.org/zmath/en/search/?an=',
            ],
        }

        unique_ext_ids = []
        filtered_ext_ids = []
        mapped_ext_ids = []

        # Keep only first of each kind of external_system_identifiers
        seen = set()
        for ext_sys_id in self.get('external_system_identifiers', []):
            if ext_sys_id['schema'] not in seen:
                seen.add(ext_sys_id['schema'])
                unique_ext_ids.append(ext_sys_id)

        # Keep only those external_system_identifiers whose 'schema' appear
        # as keys in ext_id_dict
        filtered_ext_ids = filter(lambda x: x['schema'].lower() in ext_id_dict.keys(), unique_ext_ids)

        # Map each external_system_identifier in filtered _ext_ids to
        # a link name and link url
        mapped_ext_ids = map(lambda x: self.set_links_for_ids(x['value'], list(ext_id_dict[x['schema'].lower()])), filtered_ext_ids)
        return mapped_ext_ids


class AuthorsRecord(ESRecord, AdminToolsMixin):
    """Record class specialized for author records."""

    @property
    def title(self):
        """Get preferred title."""
        return self.get('name', {}).get('preferred_name')


class ConferencesRecord(ESRecord, AdminToolsMixin):
    """Record class specialized for conference records."""

    @property
    def title(self):
        """Get preferred title."""
        return get_title(self)


class JobsRecord(ESRecord, AdminToolsMixin):
    """Record class specialized for job records."""

    @property
    def title(self):
        """Get preferred title."""
        return self.get('position')

    @property
    def similar(self):
        def _build_query(id_):
            result = JobsSearch()
            return result.query({
                'more_like_this': {
                    'docs': [
                        {
                            '_id': id_,
                        },
                    ],
                    'min_term_freq': 0,
                    'min_doc_freq': 0,
                }
            })[0:2]

        query = _build_query(self.get('control_number'))
        result = query.execute()

        return result


class InstitutionsRecord(ESRecord, AdminToolsMixin):
    """Record class specialized for institution records."""

    @property
    def title(self):
        """Get preferred title."""
        institution = self.get('institution')
        if institution:
            return institution[0]


class ExperimentsRecord(ESRecord, AdminToolsMixin):
    """Record class specialized for experiment records."""

    @property
    def title(self):
        """Get preferred title."""
        return self.get('legacy_name')


class JournalsRecord(ESRecord, AdminToolsMixin):
    """Record class specialized for journal records."""

    @property
    def title(self):
        """Get preferred title."""
        return get_title(self)

    @property
    def publisher(self):
        """Get preferred title."""
        publisher = self.get('publisher', [])
        if publisher:
            return publisher[0]

    @property
    def urls(self):
        """Get urls."""
        urls = self.get('urls', [])
        if urls:
            return [url.get('value', '') for url in urls]

    @property
    def name_variants(self):
        """Get name variations."""
        name_variants = self.get('title_variants', [])
        if name_variants:
            return [name.get('title', '') for name in name_variants]
