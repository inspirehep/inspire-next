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

from __future__ import absolute_import, division, print_function

import pytest

from inspirehep.modules.tools.utils import authorlist


def test_authorlist_without_affiliations():
    text = (
        'K. Berkelman, D. Cords, R. Felst, E. Gadermann, G. Grindhammer, '
        'H. Hultschig, P. Joos, W. Koch, U. Kötz, H. Krehbiel, D. Kreinick, '
        'J. Ludwig, K.-H. Mess, K.C. Moffeit, A. Petersen, G. Poelz, '
        'J. Ringel, K. Sauerberg, P. Schmüser, G. Vogel, B.H. Wiik, G. Wolf'
    )

    expected = (
        '100__ $$aBerkelman, K.\n'
        '700__ $$aCords, D.\n'
        '700__ $$aFelst, R.\n'
        '700__ $$aGadermann, E.\n'
        '700__ $$aGrindhammer, G.\n'
        '700__ $$aHultschig, H.\n'
        '700__ $$aJoos, P.\n'
        '700__ $$aKoch, W.\n'
        '700__ $$aKötz, U.\n'
        '700__ $$aKrehbiel, H.\n'
        '700__ $$aKreinick, D.\n'
        '700__ $$aLudwig, J.\n'
        '700__ $$aMess, K.-H.\n'
        '700__ $$aMoffeit, K.C.\n'
        '700__ $$aPetersen, A.\n'
        '700__ $$aPoelz, G.\n'
        '700__ $$aRingel, J.\n'
        '700__ $$aSauerberg, K.\n'
        '700__ $$aSchmüser, P.\n'
        '700__ $$aVogel, G.\n'
        '700__ $$aWiik, B.H.\n'
        '700__ $$aWolf, G.'
    )

    assert authorlist(text).encode('utf-8') == expected


def test_authorlist_with_affiliations():
    text = (
        'F. Durães1, A.V. Giannini2, V.P. Gonçalves3,4 and F.S. Navarra2\n'
        '1 CERN\n'
        '2 Fermilab\n'
        '3 Lund University\n'
        '4 Instituto de Física, Universidade de São Paulo'
    )
    expected = (
        '100__ $$aDurães, F.$$vCERN\n'
        '700__ $$aGiannini, A.V.$$vFermilab\n'
        '700__ $$aGonçalves, V.P.$$vLund University ' \
        '$$vInstituto de Física, Universidade de São Paulo\n'
        '700__ $$aNavarra, F.S.$$vFermilab'
    )

    assert authorlist(text).encode('utf-8') == expected


def test_authorlist_with_no_text():
    text = None
    expected = ''

    assert authorlist(text) == expected


def test_authorlist_with_no_firstnames():
    text = 'Einstein, Bohr'
    expected = (
        '100__ $$aEinstein\n'
        '700__ $$aBohr'
    )

    assert authorlist(text).encode('utf-8') == expected


def test_authorlist_with_missing_affid():
    """Test case when `authorlist` thinks every author should have an affid.

    This might happen because someone is missing affid or has a number in
    his/her name so it's tricking `authorlist`.
    """
    text = 'A. Einstein, N. Bohr2'

    with pytest.raises(AttributeError):
        authorlist(text)


def test_authorlist_with_affid_but_missing_affiliation():
    """Test case when some author has an affiliation id but no affiliation."""
    text = (
        'A. Einstein1, N. Bohr2\n'
        '2 Københavns Universitet'
    )

    with pytest.raises(KeyError):
        authorlist(text)


def test_authorlist_with_invalid_affiliation():
    """Test case when some author has an affid but no valid affiliation."""
    text = (
        'A. Einstein1, N. Bohr2\n'
        'ETH\n'
        '2 Københavns Universitet'
    )

    with pytest.raises(ValueError):
        authorlist(text)
