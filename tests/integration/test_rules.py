# # -*- coding: utf-8 -*-
# #
# # This file is part of Invenio.
# # Copyright (C) 2017 CERN.
# #
# # Invenio is free software; you can redistribute it
# # and/or modify it under the terms of the GNU General Public License as
# # published by the Free Software Foundation; either version 2 of the
# # License, or (at your option) any later version.
# #
# # Invenio is distributed in the hope that it will be
# # useful, but WITHOUT ANY WARRANTY; without even the implied warranty of
# # MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# # General Public License for more details.
# #
# # You should have received a copy of the GNU General Public License
# # along with Invenio; if not, write to the
# # Free Software Foundation, Inc., 59 Temple Place, Suite 330, Boston,
# # MA 02111-1307, USA.
# #
# # In applying this license, CERN does not
# # waive the privileges and immunities granted to it by virtue of its status
# # as an Intergovernmental Organization or submit itself to any jurisdiction.
#
#
# """Test helpers."""
#
# from inspirehep.modules.recordvalidators.validators.rules import (
#     check_if_isbn_exist_in_other_records,
#     check_if_journal_title_is_canonical,
#     check_if_reportnumber_exist_in_other_records,
#     check_external_urls_if_work,
#     check_external_dois_if_exist
# )
# from inspirehep.modules.records.validators.errors import ValidationError
# from inspirehep.modules.recordvalidators.validators.helpers import (
#     execute_query,
#     GET_RESULTS_FOR_FIELD_PROPERTY_QUERYSTRING_TEMPLATE,
#     FIELD_DUPLICATE_VALUES_FOUND_TEMPLATE,
#     FIELD_VALIDATION_TEMPLATE,
#     DOI_VALIDATION_URL
# )
# import pytest
# import httpretty
# from invenio_db import db
# from inspirehep.modules.records.api import InspireRecord
#
#
# @pytest.fixture(scope='function')
# def test_record(app):
#     sample_record = {
#         '$schema': 'http://localhost:5000/schemas/records/hep.json',
#         'control_number': 111,
#         'document_type': [
#             'article',
#         ],
#         'isbns': [
#             {'value': '9783598215001'},
#         ],
#         'report_numbers': [
#             {'value': '11111'}
#         ],
#         'titles': [
#             {'title': 'sample'},
#         ],
#         'self': {
#             '$ref': 'http://localhost:5000/schemas/records/hep.json',
#         }
#     }
#     dupl_sample_record = {
#         '$schema': 'http://localhost:5000/schemas/records/hep.json',
#         'control_number': 222,
#         'document_type': [
#             'article',
#         ],
#         'isbns': [
#             {'value': '9783598215001'},
#         ],
#         'report_numbers': [
#             {'value': '11111'}
#         ],
#         'titles': [
#             {'title': 'another_sample'},
#         ],
#         'self': {
#             '$ref': 'http://localhost:5000/schemas/records/hep.json',
#         }
#     }
#
#     record_id = InspireRecord.create(sample_record).id
#     dupl_record_id = InspireRecord.create(dupl_sample_record).id
#
#     db.session.commit()
#
#     yield
#
#     InspireRecord.get_record(record_id)._delete(force=True)
#     InspireRecord.get_record(dupl_record_id)._delete(force=True)
#
#     db.session.commit()
#
#
# def test_check_if_isbn_exist_in_other_records(app, test_record):
#     sample_record = {
#         '$schema': 'http://localhost:5000/schemas/records/hep.json',
#         'control_number': 333,
#         'document_type': [
#             'book',
#         ],
#         'isbns': [
#             {'value': '9783598215001'},
#         ],
#         'titles': [
#             {'title': 'sample_record_title'},
#         ],
#         'self': {
#             '$ref': 'http://localhost:5000/schemas/records/hep.json',
#         }
#     }
#
#     expected = {
#         '/isbns/0/value': [{
#             'message': FIELD_DUPLICATE_VALUES_FOUND_TEMPLATE.format(
#                 field='isbns',
#                 value='9783598215001'
#             ),
#             'type': 'Error'
#         }]
#     }
#
#     with pytest.raises(ValidationError) as excinfo:
#         check_if_isbn_exist_in_other_records(sample_record)
#     assert excinfo.value.error == expected
#
#
# def test_check_if_journal_title_is_canonical(app):
#     sample_record = {
#         '$schema': 'http://localhost:5000/schemas/records/hep.json',
#         'control_number': 333,
#         'document_type': [
#             'book',
#         ],
#         'titles': [
#             {'title': 'sample_record_title'},
#         ],
#         'publication_info': [
#             {
#                 'journal_title': 'not_a_canonical_journal_title'
#             }
#         ],
#         'self': {
#             '$ref': 'http://localhost:5000/schemas/records/hep.json',
#         }
#     }
#
#     expected = {
#         '/publication_info/0/journal_title': [{
#             'message': "Journal title 'not_a_canonical_journal_title' doesn't exist.'",
#             'type': 'Error'
#         }]
#     }
#
#     with pytest.raises(ValidationError) as excinfo:
#         check_if_journal_title_is_canonical(sample_record)
#     assert excinfo.value.error == expected
#
#
# def test_execute_query(app, test_record):
#
#     zero_found_querystring = GET_RESULTS_FOR_FIELD_PROPERTY_QUERYSTRING_TEMPLATE.format(
#         field='titles',
#         prop='title',
#         value='not_found_value'
#     )
#     one_found_querystring = GET_RESULTS_FOR_FIELD_PROPERTY_QUERYSTRING_TEMPLATE.format(
#         field='titles',
#         prop='title',
#         value='sample'
#     )
#
#     results = execute_query(zero_found_querystring)
#     assert results.rowcount == 0
#
#     results = execute_query(one_found_querystring)
#     assert results.rowcount == 1
#
#
# def test_check_if_reportnumber_exist_in_other_records(app, test_record):
#     sample_record = {
#         '$schema': 'http://localhost:5000/schemas/records/hep.json',
#         'control_number': 333,
#         'document_type': [
#             'book',
#         ],
#         'report_numbers': [
#             {'value': '11111'}
#         ],
#         'titles': [
#             {'title': 'sample_record_title'},
#         ],
#         'self': {
#             '$ref': 'http://localhost:5000/schemas/records/hep.json',
#         }
#     }
#
#     expected = {
#         '/report_numbers/0/value': [{
#             'message': FIELD_DUPLICATE_VALUES_FOUND_TEMPLATE.format(
#                 field='report_numbers',
#                 value='11111'
#             ),
#             'type': 'Warning'
#         }]
#     }
#
#     with pytest.raises(ValidationError) as excinfo:
#         check_if_reportnumber_exist_in_other_records(sample_record)
#     assert excinfo.value.error == expected
#
#
# @pytest.mark.httpretty
# def test_check_external_urls_if_work():
#     sample_record = {
#         '$schema': 'http://localhost:5000/schemas/records/hep.json',
#         'control_number': 333,
#         'document_type': [
#             'book',
#         ],
#         'urls': [
#             {'value': 'http://not_working_url'}
#         ],
#         'titles': [
#             {'title': 'sample_record_title'},
#         ],
#         'self': {
#             '$ref': 'http://localhost:5000/schemas/records/hep.json',
#         }
#     }
#
#     expected = {
#         '/urls/0/value': [{
#             'message': FIELD_VALIDATION_TEMPLATE.format(
#                 field='urls',
#                 value='http://not_working_url'
#             ),
#             'type': 'Warning'
#         }]
#     }
#
#     httpretty.register_uri(
#         httpretty.GET,
#         "http://not_working_url/",
#         status=404)
#
#     with pytest.raises(ValidationError) as excinfo:
#         check_external_urls_if_work(sample_record)
#     assert excinfo.value.error == expected
#
#
# @pytest.mark.httpretty
# def test_check_external_dois_if_exist():
#     sample_record = {
#         '$schema': 'http://localhost:5000/schemas/records/hep.json',
#         'control_number': 333,
#         'document_type': [
#             'book',
#         ],
#         'dois': [
#             {'value': '1111111'}
#         ],
#         'titles': [
#             {'title': 'sample_record_title'},
#         ],
#         'self': {
#             '$ref': 'http://localhost:5000/schemas/records/hep.json',
#         }
#     }
#
#     expected = {
#         '/dois/0/value': [{
#             'message': FIELD_VALIDATION_TEMPLATE.format(
#                 field='dois',
#                 value='1111111'
#             ),
#             'type': 'Warning'
#         }]
#     }
#
#     httpretty.register_uri(
#         httpretty.GET,
#         DOI_VALIDATION_URL.format(doi='1111111'),
#         status=404)
#
#     with pytest.raises(ValidationError) as excinfo:
#         check_external_dois_if_exist(sample_record)
#     assert excinfo.value.error == expected