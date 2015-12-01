# -*- coding: utf-8 -*-
#
# This file is part of INSPIRE.
# Copyright (C) 2015 CERN.
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

from invenio.testsuite import InvenioTestCase


class RecordsTests(InvenioTestCase):

    """Test records"""

    def test_facets_experiments(self):
        """Test if misspelled experiments are corrected."""
        from invenio_ext.es import es
        record = es.get(index='hep', id='559118')
        source = record.get("_source")
        exp = source.get("accelerator_experiments")
        # Gets misspelled experiment
        experiment = exp[0].get("experiment")
        # This should contain the corected experiment name
        facet_experiment = exp[0].get("facet_experiment")
        self.assertEqual(experiment, "CERN-LHC-LHCB")
        self.assertEqual(facet_experiment, "CERN-LHC-LHCb")
