# -*- coding: utf-8 -*-
#
# This file is part of INSPIRE.
# Copyright (C) 2016 CERN.
#
# INSPIRE is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License as
# published by the Free Software Foundation; either version 2 of the
# License, or (at your option) any later version.
#
# INSPIRE is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with INSPIRE; if not, write to the Free Software Foundation, Inc.,
# 59 Temple Place, Suite 330, Boston, MA 02111-1307, USA.

import pkg_resources
import os
import pytest

from dojson.contrib.marc21.utils import create_record

from inspirehep.dojson.hepnames import hepnames2marc, hepnames


@pytest.fixture
def marcxml_to_json():
    marcxml = pkg_resources.resource_string('tests',
                                            os.path.join(
                                                'fixtures',
                                                'test_hepnames_record.xml'
                                            ))
    record = create_record(marcxml)
    return hepnames.do(record)


@pytest.fixture
def json_to_marc(marcxml_to_json):
    return hepnames2marc.do(marcxml_to_json)


def test_acquisition_source(marcxml_to_json, json_to_marc):
    """Test if acquisition_source is created correctly."""
    assert (marcxml_to_json['acquisition_source'][0]['source'] ==
            json_to_marc['541'][0]['a'])
    assert (marcxml_to_json['acquisition_source'][0]['email'] ==
            json_to_marc['541'][0]['b'])
    assert (marcxml_to_json['acquisition_source'][0]['method'] ==
            json_to_marc['541'][0]['c'])
    assert (marcxml_to_json['acquisition_source'][0]['date'] ==
            json_to_marc['541'][0]['d'])
    assert (marcxml_to_json['acquisition_source'][0]['submission_number'] ==
            json_to_marc['541'][0]['e'])


def test_dates(marcxml_to_json, json_to_marc):
    """Test if dates is created correctly."""
    # TODO fix dojson to take dates from 100__d
    pass


def test_experiments(marcxml_to_json, json_to_marc):
    """Test if experiments is created correctly."""
    assert (marcxml_to_json['experiments'][1]['name'] ==
            json_to_marc['693'][1]['e'])
    assert (marcxml_to_json['experiments'][1]['start_year'] ==
            json_to_marc['693'][1]['s'])
    assert (marcxml_to_json['experiments'][1]['end_year'] ==
            json_to_marc['693'][1]['d'])
    assert (marcxml_to_json['experiments'][1]['status'] ==
            json_to_marc['693'][1]['z'])


def test_field_categories(marcxml_to_json, json_to_marc):
    """Test if field_categories is created correctly."""
    assert (marcxml_to_json['field_categories'][0] ==
            json_to_marc['65017'][0]['a'])
    assert (marcxml_to_json['field_categories'][1] ==
            json_to_marc['65017'][1]['a'])
    assert (json_to_marc['65017'][1]['2'] == 'INSPIRE')


def test_ids(marcxml_to_json, json_to_marc):
    """Test if ids is created correctly."""
    assert (marcxml_to_json['ids'][0]['value'] ==
            json_to_marc['035'][0]['a'])
    assert (marcxml_to_json['ids'][0]['type'] ==
            json_to_marc['035'][0]['9'])
    assert (marcxml_to_json['ids'][1]['value'] ==
            json_to_marc['035'][1]['a'])
    assert (marcxml_to_json['ids'][1]['type'] ==
            json_to_marc['035'][1]['9'])


def test_name(marcxml_to_json, json_to_marc):
    """Test if name is created correctly."""
    assert (marcxml_to_json['name']['value'] ==
            json_to_marc['100']['a'])
    assert (marcxml_to_json['name']['numeration'] ==
            json_to_marc['100']['b'])
    assert (marcxml_to_json['name']['title'] ==
            json_to_marc['100']['c'])
    assert (marcxml_to_json['name']['status'] ==
            json_to_marc['100']['g'])
    assert (marcxml_to_json['name']['preferred_name'] ==
            json_to_marc['100']['q'])


def test_native_name(marcxml_to_json, json_to_marc):
    """Test if native_name is created correctly."""
    assert (marcxml_to_json['native_name'] ==
            json_to_marc['880']['a'])


def test_other_names(marcxml_to_json, json_to_marc):
    """Test if other_names is created correctly."""
    assert (marcxml_to_json['other_names'][0] ==
            json_to_marc['400'][0]['a'])
    assert (marcxml_to_json['other_names'][1] ==
            json_to_marc['400'][1]['a'])


def test_phd_advisors(marcxml_to_json, json_to_marc):
    """Test if phd_advisors is created correctly."""
    assert (marcxml_to_json['phd_advisors'][0]['id'] ==
            json_to_marc['701'][0]['i'])
    assert (marcxml_to_json['phd_advisors'][0]['name'] ==
            json_to_marc['701'][0]['a'])
    assert (marcxml_to_json['phd_advisors'][0]['degree_type'] ==
            json_to_marc['701'][0]['g'])


def test_positions(marcxml_to_json, json_to_marc):
    """Test if positions is created correctly."""
    assert (marcxml_to_json['positions'][0]['institution']['name'] ==
            json_to_marc['371'][0]['a'])
    assert (marcxml_to_json['positions'][0]['rank'] ==
            json_to_marc['371'][0]['r'])
    assert (marcxml_to_json['positions'][0]['start_date'] ==
            json_to_marc['371'][0]['s'])
    assert (marcxml_to_json['positions'][0]['email'] ==
            json_to_marc['371'][0]['m'])
    assert (marcxml_to_json['positions'][0]['status'] ==
            json_to_marc['371'][0]['z'])
    assert (marcxml_to_json['positions'][1]['end_date'] ==
            json_to_marc['371'][1]['t'])
    assert (marcxml_to_json['positions'][2]['old_email'] ==
            json_to_marc['371'][2]['o'])


def test_private_current_emails(marcxml_to_json, json_to_marc):
    """Test if private_current_emails is created correctly."""
    assert (marcxml_to_json['private_current_emails'][0] ==
            json_to_marc['595'][1]['m'])


def test_private_old_emails(marcxml_to_json, json_to_marc):
    """Test if private_old_emails is created correctly."""
    assert (marcxml_to_json['private_old_emails'][0] ==
            json_to_marc['595'][0]['o'])


def test_private_notes(marcxml_to_json, json_to_marc):
    """Test if private_notes is created correctly."""
    assert (marcxml_to_json['_private_note'][0] ==
            json_to_marc['595'][2]['a'])


def test_prizes(marcxml_to_json, json_to_marc):
    """Test if prizes is created correctly."""
    assert (marcxml_to_json['prizes'][0] ==
            json_to_marc['678'][0]['a'])


def test_source(marcxml_to_json, json_to_marc):
    """Test if source is created correctly."""
    assert (marcxml_to_json['source'][0]['name'] ==
            json_to_marc['670'][0]['a'])
    assert (marcxml_to_json['source'][1]['date_verified'] ==
            json_to_marc['670'][1]['d'])


def test_urls(marcxml_to_json, json_to_marc):
    """Test if urls is created correctly."""
    assert (marcxml_to_json['urls'][0]['value'] ==
            json_to_marc['8564'][0]['u'])
    assert (marcxml_to_json['urls'][0]['description'] ==
            json_to_marc['8564'][0]['y'])
