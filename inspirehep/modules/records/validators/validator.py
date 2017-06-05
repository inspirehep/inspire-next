#
# This file is part of INSPIRE.
# Copyright (C) 2014, 2015, 2016, 2017 CERN.
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
# In applying this license, CERN does not waive the privileges and immunities
# granted to it by virtue of its status as an Intergovernmental Organization
# or submit itself to any jurisdiction.


from jsonschema import Draft4Validator
from jsonschema.validators import extend, RefResolver
from inspire_schemas.utils import get_schema_path, load_schema
from rules import (
    check_for_author_or_corporate_author_to_exist,
    check_if_isbn_exist_in_other_records,
    check_if_isbn_is_valid,
    check_document_type_if_book_series_exist,
    check_document_type_if_isbns_exist,
    check_document_type_if_cnum_exist,
    check_document_type_if_thesis_info_exist,
    check_languages_if_valid_iso
)

INSPIRE_VALIDATORS_LIST = [
    check_for_author_or_corporate_author_to_exist,
    check_if_isbn_exist_in_other_records,
    check_if_isbn_is_valid,
    check_document_type_if_book_series_exist,
    check_document_type_if_isbns_exist,
    check_document_type_if_cnum_exist,
    check_document_type_if_thesis_info_exist,
    check_languages_if_valid_iso
]


def inspire_validator_dispatcher(validator, value, instance, schema):
    for validator in INSPIRE_VALIDATORS_LIST:
        for error in validator(instance):
            yield error


class InspireResolver(RefResolver):

    def resolve_remote(self, uri):
        # """Resolve a uri or relative path to a schema."""
        resolved = load_schema(uri.rsplit('.json', 1)[0])
        if 'hep.json' in uri:
            resolved['inspire_validator'] = 'Inspire validator extending Draft4Validator.'
        return resolved

InspireValidator = extend(Draft4Validator, {'inspire_validator': inspire_validator_dispatcher})
