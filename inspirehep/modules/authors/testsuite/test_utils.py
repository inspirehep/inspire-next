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

"""Tests for utils."""

from invenio.testsuite import InvenioTestCase, make_test_suite, run_test_suite

from ..utils import bai


class BaiTests(InvenioTestCase):

    """Test the BAI generation function."""

    def test_bai(self):
        self.assertEqual(bai("Ellis, Jonathan Richard"), "J.R.Ellis")
        self.assertEqual(bai("ellis, jonathan richard"), "J.R.Ellis")
        self.assertEqual(bai("ELLIS, JONATHAN RICHARD"), "J.R.Ellis")
        self.assertEqual(bai("Ellis, John Richard"), "J.R.Ellis")
        self.assertEqual(bai("Ellis, J R"), "J.R.Ellis")
        self.assertEqual(bai("Ellis, J. R."), "J.R.Ellis")
        self.assertEqual(bai("Ellis, J.R."), "J.R.Ellis")
        self.assertEqual(bai("Ellis, J.R. (Jr)"), "J.R.Ellis")
        self.assertEqual(bai("Ellis"), "Ellis")
        self.assertEqual(bai("Ellis, "), "Ellis")
        self.assertEqual(bai("O'Connor, David"), "D.OConnor")
        self.assertEqual(bai("o'connor, david"), "D.OConnor")
        self.assertEqual(bai("McCurdy, David"), "D.McCurdy")
        self.assertEqual(bai("DeVito, Dany"), "D.DeVito")
        self.assertEqual(bai("DEVITO, Dany"), "D.Devito")
        self.assertEqual(bai("De Villiers, Jean-Pierre"), "J.P.de.Villiers")
        self.assertEqual(bai("Höing, Rebekka Sophie"), "R.S.Hoeing")
        self.assertEqual(bai("Müller, Andreas"), "A.Mueller")
        self.assertEqual(bai("Hernández-Tomé, G."), "G.Hernandez.Tome")
        self.assertEqual(bai("José de Goya y Lucientes, Francisco Y H"),
                         "F.Y.H.Jose.de.Goya.y.Lucientes")

    def test_name_variations_existance(self):
        """Test if name variations are saved in the record """
        from invenio_ext.es import es
        from inspirehep.modules.authors.utils import author_tokenize
        rec = es.get(index='hep', id=1343791)
        rec_list = rec['_source']['authors'][0]['name_variations']
        name = rec['_source']['authors'][0]['full_name']
        token_list = author_tokenize(name)
        self.assertEqual(token_list, rec_list)

    def test_author_tokenizer(self):
        """Test author name tokenizer """
        from inspirehep.modules.authors.utils import author_tokenize
        token_list = author_tokenize("Ellis Richard")
        self.assertEqual(token_list, ['E Richard',
                                      'Ellis Richard',
                                      'Richard E',
                                      'Richard Ellis',
                                      'Richard, E',
                                      'Richard, Ellis'])

TEST_SUITE = make_test_suite(BaiTests)

if __name__ == "__main__":
    run_test_suite(TEST_SUITE)
