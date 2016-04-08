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
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with INSPIRE. If not, see <http://www.gnu.org/licenses/>.
#
# In applying this licence, CERN does not waive the privileges and immunities
# granted to it by virtue of its status as an Intergovernmental Organization
# or submit itself to any jurisdiction.


from functools import wraps

from sqlalchemy.orm.exc import NoResultFound

from invenio_accounts.models import User
from invenio_db import db
from invenio_oauthclient.models import UserIdentity


def filter_empty_helper(keys=None):
    """Remove empty elements from a list."""
    # TODO Move to a utility file
    def _inner(elem):
        if isinstance(elem, dict):
            for k, v in elem.items():
                if (keys is None or k in keys) and v:
                    return True
            return False
        else:
            return bool(elem)
    return _inner


def filter_empty_elements(recjson):
    """Filter empty fields."""
    # TODO Move to a utility to be shared with author workflows
    list_fields = [
        'authors', 'supervisors', 'report_numbers'
    ]
    for key in list_fields:
        recjson[key] = filter(
            filter_empty_helper(), recjson.get(key, [])
        )

    for k in recjson.keys():
        if not recjson[k]:
            del recjson[k]

    return recjson


def convert_data_to_model():
    """Manipulate form data to match literature data model."""
    @wraps(convert_data_to_model)
    def _convert_data_to_model(obj, eng):
        import copy

        from .dojson.model import literature

        filter_empty_elements(obj.data)

        # Save original form data for later access
        form_fields = copy.deepcopy(obj.data)
        obj.extra_data["formdata"] = copy.deepcopy(form_fields)

        data = obj.data

        converted = literature.do(data)
        # metadata.clear()
        data.update(converted)

        # Add extra fields that need to be computed or depend on other
        # fields.
        #
        # ============================
        # Collection
        # ============================
        data['collections'] = [{'primary': "HEP"}]
        if form_fields['type_of_doc'] == 'thesis':
            data['collections'].append({'primary': "THESIS"})
        if "subject_terms" in data:
            # Check if it was imported from arXiv
            if any([x["scheme"] == "arXiv" for x in data["subject_terms"]]):
                data['collections'].extend([{'primary': "arXiv"},
                                            {'primary': "Citeable"}])
                # Add arXiv as source
                if data.get("abstracts"):
                    data['abstracts'][0]['source'] = 'arXiv'
                if form_fields.get("arxiv_id"):
                    data['external_system_numbers'] = [{
                        'value': 'oai:arXiv.org:' + form_fields['arxiv_id'],
                        'institute': 'arXiv'
                    }]
        if "publication_info" in data:
            if all([key in data['publication_info'].keys() for key in
                   ('year', 'journal_issue', 'journal_volume', 'page_artid')]):
                # NOTE: Only peer reviewed journals should have this collection
                # we are adding it here but ideally should be manually added
                # by a curator.
                data['collections'].append({'primary': "Published"})
                # Add Citeable collection if not present
                collections = [x['primary'] for x in data['collections']]
                if "Citeable" not in collections:
                    data['collections'].append({'primary': "Citeable"})
        # ============================
        # Title source and cleanup
        # ============================
        try:
            # Clean up all extra spaces in title
            data['titles'][0]['title'] = " ".join(
                data['titles'][0]['title'].split()
            )
            title = data['titles'][0]['title']
        except (KeyError, IndexError):
            title = ""
        if form_fields.get('title_arXiv'):
            title_arxiv = " ".join(form_fields.get('title_arXiv').split())
            if title == title_arxiv:
                data['titles'][0]["source"] = "arXiv"
            else:
                data['titles'].append({
                    'title': title_arxiv,
                    'source': "arXiv"
                })
        if form_fields.get('title_crossref'):
            title_crossref = " ".join(
                form_fields.get('title_crossref').split()
            )
            if title == title_crossref:
                data['titles'][0]["source"] = "CrossRef"
            else:
                data['titles'].append({
                    'title': title_crossref,
                    'source': "CrossRef"
                })
        try:
            data['titles'][0]['source']
        except KeyError:
            # Title has no source, so should be the submitter
            data['titles'][0]['source'] = "submitter"

        # ============================
        # Conference name
        # ============================
        if 'conf_name' in form_fields:
            if 'nonpublic_note' in form_fields:
                data.setdefault("hidden_notes", []).append({
                    "value": form_fields['conf_name']
                })
                data['hidden_notes'].append({
                    'value': form_fields['nonpublic_note']
                })
            else:
                data.setdefault("hidden_notes", []).append({
                    "value": form_fields['conf_name']
                })
            data['collections'].extend([{'primary': "ConferencePaper"}])

        # ============================
        # Page range
        # ============================
        if 'page_nr' not in data:
            if data.get("publication_info", {}).get("page_artid"):
                pages = data['publication_info']['page_artid'].split('-')
                if len(pages) == 2:
                    try:
                        data['page_nr'] = int(pages[1]) - int(pages[0]) + 1
                    except ValueError:
                        pass
        # ============================
        # Language
        # ============================
        if data.get("languages", []) and data["languages"][0] == "oth":
            if form_fields.get("other_language"):
                data["languages"] = [form_fields["other_language"]]

        # ===============================
        # arXiv category in report number
        # ===============================
        if data.get("_categories"):
            del data["_categories"]

        # ============================
        # Date of defense
        # ============================
        if form_fields.get('defense_date'):
            defense_note = {
                'value': 'Presented on ' + form_fields['defense_date']
            }
            data.setdefault("public_notes", []).append(defense_note)
        # ==========
        # Owner Info
        # ==========
        # TODO Make sure we are getting the email correctly
        userid = obj.id_user
        try:
            email = User.query.get(userid).email
        except AttributeError:
            email = ''
        try:
            # TODO Make sure we are getting the ORCID id correctly
            source = UserIdentity.query.filter_by(id_user=userid, method='orcid').one()
        except NoResultFound:
            source = ''
        if source:
            source = source.method + ':' + source.id
        data['acquisition_source'] = dict(
            source=source,
            email=email,
            method="submission",
            submission_number=obj.id,
        )
        # ==============
        # References
        # ==============
        if form_fields.get('references'):
            data['references'] = form_fields.get('references')
        # ==============
        # Extra comments
        # ==============
        if form_fields.get('extra_comments'):
            data.setdefault('hidden_notes', []).append(
                {
                    'value': form_fields['extra_comments'],
                    'source': 'submitter'
                }
            )
            data["extra_comments"] = form_fields.get("extra_comments")
        # ======================================
        # Journal name Knowledge Base conversion
        # ======================================
        if data.get("publication_info", {}).get("journal_title"):
            # journals_kb = dict([(x['key'].lower(), x['value'])
            #                     for x in get_kb_mappings(current_app.config.get("DEPOSIT_INSPIRE_JOURNALS_KB"))])

            # data['publication_info']['journal_title'] = journals_kb.get(data['publication_info']['journal_title'].lower(),
            #                                                                 data['publication_info']['journal_title'])
            # TODO convert using journal records
            pass
        if data.get("publication_info") and not isinstance(data['publication_info'], list):
            data["publication_info"] = [data['publication_info']]

        # obj.log.info(form_fields)
        # obj.log.info(data)

        # from inspirehep.dojson.hep import hep2marc
        # from inspirehep.dojson.utils import legacy_export_as_marc
        # obj.log.info("Produced MarcXML: \n {}".format(
        #             legacy_export_as_marc(
        #     hep2marc.do(obj.data)
        # ))
        #         )

    return _convert_data_to_model


def add_submission_extra_data(obj, eng):
    """ Add extra data to workflow object. """
    metadata = obj.data
    submission_data = {}
    if "references" in metadata:
        submission_data["references"] = metadata["references"]
        del metadata["references"]
    if "extra_comments" in metadata:
        submission_data["extra_comments"] = metadata["extra_comments"]
        del metadata["extra_comments"]
    if "pdf" in metadata:
        submission_data["pdf"] = metadata["pdf"]
        del metadata["pdf"]
    obj.extra_data["submission_data"] = submission_data
    obj.save()
    db.session.commit()
