# -*- coding: utf-8 -*-
#
# This file is part of INSPIRE.
# Copyright (C) 2014-2018 CERN.
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

"""Records receivers."""

import json
import operator
import re


from sqlalchemy import type_coerce
from sqlalchemy.dialects.postgresql import JSONB

from invenio_records.models import RecordMetadata

from inspire_schemas import utils


def has_doi(ref):
	"""Return ``True`` is ``ref`` has a doi, ``False`` otherwise"""
	if 'reference' in ref["reference"]:
		return 'dois' in ref["reference"]["reference"]
	return False


def has_arxiv(ref):
	""""Return ``True`` is ``ref`` has a valid arxiv id, ``False`` otherwise"""
	if 'reference' in ref["reference"]:
		if 'arxiv_eprint' in ref["reference"]["reference"]:
			return utils.is_arxiv(ref["reference"]["reference"]["arxiv_eprint"])
	return False


def increase_count(result, identifier, core):
	"""Increases the number of times a reference with the same identifier has appeared"""
	if identifier in result:
		if core:
			result[identifier] = (result[identifier][0] + 1, result[identifier][1])
		else:
			result[identifier] = (result[identifier][0], result[identifier][1] + 1)
	else:
		if core:
			result[identifier] = (1, 0)
		else:
			result[identifier] = (0, 1)
	return result


def calculate_score(times_cited):
	"""Given a tuple of the number of times cited by a core record and a non core record,
	calculate a score associated with a reference.

	The score is calculated giving five times more importance to core records"""
	return times_cited[0] * 5 + times_cited[1]


def order_dictionary(result_dict):
	"""Return ``result_dict`` as an ordered list"""
	score_result_dict = {}
	result = []

	for key, value in result_dict.iteritems():
		score_result_dict[key] = calculate_score(value)

	sorted_list = sorted(score_result_dict.items(), key=operator.itemgetter(1), reverse = True)
	for element in sorted_list:
		result.append((element[0], result_dict[element[0]]))

	return result


def obtain_references():
	"""Write a file ``checkers.json`` in which each line corresponds to a reference that doesn't have a ``record`` value"""
	query =  RecordMetadata.query.filter(type_coerce(RecordMetadata.json, JSONB)['_collections'].contains(['Literature'])).with_entities(RecordMetadata.json)

	for record in query.yield_per(1000):
		core = record.json.get('core')
		for reference in record.json.get('references', []):
			if 'record' not in reference:
				data = {}
				data['core'] = core
				data['reference'] = reference
				with open('checkers.json', 'a') as f:
					json.dump(data, f)
					f.write('\n')


def create_table():
	"""Read a structure similar to the one built in ``obtain_references`` and writes two different files from it.

	If the reference read has a doi or an arxiv id, it is stored in the data structure.
	Once all the data is read, it is ordered by most relevant to less relevant
	and written into two different files, one for dois and another for arxiv ids."""
    with open('checkers.json') as f:
    	data = f.readlines()

    data = [x.replace('\n','') for x in data]

    result_doi = {}
    result_arxiv = {}

    for reference in data:
    	ref = json.loads(reference)
    	if has_doi(ref):
    		doi = ref["reference"]["reference"]["dois"][0]
    		result_doi = increase_count(result_doi, doi, ref["core"])
    	if has_arxiv(ref):
    		arxiv = utils.normalize_arxiv(ref["reference"]["reference"]["arxiv_eprint"])
    		result_arxiv = increase_count(result_arxiv, arxiv, ref["core"])

    result_doi = order_dictionary(result_doi)
    result_arxiv = order_dictionary(result_arxiv)

    with open('ref_result_doi.txt','w') as f:
    	for item in result_doi:
    		f.write('{0}: {1}\n'.format(item[0].encode('utf-8'),str(item[1]).encode('utf-8')))

    with open('ref_result_arxiv.txt','w') as f:
    	for item in result_arxiv:
    		f.write('{0}: {1}\n'.format(item[0].encode('utf-8'),str(item[1]).encode('utf-8')))