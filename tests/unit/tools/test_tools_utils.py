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
        '700__ $$aGonçalves, V.P.$$vLund University '
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

    with pytest.raises(AttributeError) as excinfo:
        authorlist(text)
    assert 'Could not find affiliations' in str(excinfo.value)


def test_authorlist_with_affid_but_missing_affiliation():
    """Test case when some author has an affiliation id but no affiliation."""
    text = (
        'A. Einstein1, N. Bohr2\n'
        '2 Københavns Universitet'
    )

    with pytest.raises(KeyError) as excinfo:
        authorlist(text)
    assert 'the affiliation is missing.' in str(excinfo.value)


def test_authorlist_with_invalid_affiliation():
    """Test case when some author has an affid but no valid affiliation."""
    text = (
        'A. Einstein1, N. Bohr2\n'
        'ETH\n'
        '2 Københavns Universitet'
    )

    with pytest.raises(AttributeError) as excinfo:
        authorlist(text)
    assert 'Could not find affiliations' in str(excinfo.value)


def test_authorlist_with_one_author_missing_affiliation():
    """Test case when some author doesn't have an affiliation."""
    text = (
        'A. Einstein, N. Bohr1,2\n'
        '1 ETH\n'
        '2 Københavns Universitet'
    )

    with pytest.raises(AttributeError) as excinfo:
        authorlist(text)
    assert 'This author might not have an affiliation' in str(excinfo.value)


def test_authorlist_ignores_space_between_authors_and_affiliations():
    text = (
        'F. Lastname1, F.M. Otherlastname1,2\n'
        '\n'
        '1 CERN\n'
        '2 Otheraffiliation'
    )

    expected = (
        '100__ $$aLastname, F.$$vCERN\n'
        '700__ $$aOtherlastname, F.M.$$vCERN $$vOtheraffiliation'
    )
    result = authorlist(text)

    assert expected == result


def test_authorlist_bad_author_lines():
    text = (
        'A. Aduszkiewicz\n'
        '1\n'
        ', Y.X. Ali\n'
        '1,20\n'
        ', E I Andronov\n'
        '20\n'
        ', Einstein\n'
        '13,15\n'
        '\n'
        '1 CERN\n'
        '20 DESY\n'
        '13 ETH ZÜRICH\n'
        '15 PRINCETON\n'
    )

    expected = (
        '100__ $$aAduszkiewicz, A.$$vCERN\n'
        '700__ $$aAli, Y.X.$$vCERN $$vDESY\n'
        '700__ $$aAndronov, E. I.$$vDESY\n'
        '700__ $$aEinstein$$vETH ZÜRICH $$vPRINCETON'
    )
    result = authorlist(text)

    assert expected == result.encode('utf-8')


def test_authorlist_no_commas_between_authors():
    text = (
        'C. Patrignani1 K. Agashe2 G. Aielli1,2\n'
        '1 Universit`a di Bologna and INFN, Dip. Scienze per la Qualit`a della Vita, I-47921, Rimini, Italy\n'
        '2 University of Maryland, Department of Physics, College Park, MD 20742-4111, USA'
    )

    expected = (
        '100__ $$aPatrignani, C.$$vUniversità di Bologna and INFN, Dip. Scienze per la Qualità della Vita, I-47921, Rimini, Italy\n'
        '700__ $$aAgashe, K.$$vUniversity of Maryland, Department of Physics, College Park, MD 20742-4111, USA\n'
        '700__ $$aAielli, G.$$vUniversità di Bologna and INFN, Dip. Scienze per la Qualità della Vita, I-47921, Rimini, Italy $$vUniversity of Maryland, Department of Physics, College Park, MD 20742-4111, USA'
    )

    result = authorlist(text)

    assert expected == result.encode('utf-8')


def test_authorlist_newlines_and_no_commas_between_authors():
    text = (
        'C. Patrignani\n'
        '1\n'
        'K. Agashe\n'
        '2\n'
        'G. Aielli\n'
        '1,\n'
        '2\n'
        '1\n'
        'Universit`a di Bologna and INFN, Dip. Scienze per la Qualit`a della Vita, I-47921, Rimini, Italy\n'
        '2\n'
        'University of Maryland, Department of Physics, College Park, MD 20742-4111, USA'
    )

    expected = (
        '100__ $$aPatrignani, C.$$vUniversità di Bologna and INFN, Dip. Scienze per la Qualità della Vita, I-47921, Rimini, Italy\n'
        '700__ $$aAgashe, K.$$vUniversity of Maryland, Department of Physics, College Park, MD 20742-4111, USA\n'
        '700__ $$aAielli, G.$$vUniversità di Bologna and INFN, Dip. Scienze per la Qualità della Vita, I-47921, Rimini, Italy $$vUniversity of Maryland, Department of Physics, College Park, MD 20742-4111, USA'
    )

    result = authorlist(text)

    assert expected == result.encode('utf-8')


def test_authorlist_affids_with_dots():
    text = (
        'C. Patrignani\n'
        '1,\n'
        'K. Agashe\n'
        '2,\n'
        'G. Aielli\n'
        '1,\n'
        '2\n'
        '1.\n'
        'Universit`a di Bologna and INFN, Dip. Scienze per la Qualit`a della Vita, I-47921, Rimini, Italy\n'
        '2.\n'
        'University of Maryland, Department of Physics, College Park, MD 20742-4111, USA'
    )

    expected = (
        '100__ $$aPatrignani, C.$$vUniversità di Bologna and INFN, Dip. Scienze per la Qualità della Vita, I-47921, Rimini, Italy\n'
        '700__ $$aAgashe, K.$$vUniversity of Maryland, Department of Physics, College Park, MD 20742-4111, USA\n'
        '700__ $$aAielli, G.$$vUniversità di Bologna and INFN, Dip. Scienze per la Qualità della Vita, I-47921, Rimini, Italy $$vUniversity of Maryland, Department of Physics, College Park, MD 20742-4111, USA'
    )
    result = authorlist(text)

    assert expected == result.encode('utf-8')


def test_authorlist_no_commas_between_affids():
    text = (
        'C. Patrignani\n'
        '1,\n'
        'K. Agashe\n'
        '2,\n'
        'G. Aielli\n'
        '1\n'
        '2\n'
        '1.\n'
        'Universit`a di Bologna and INFN, Dip. Scienze per la Qualit`a della Vita, I-47921, Rimini, Italy\n'
        '2.\n'
        'University of Maryland, Department of Physics, College Park, MD 20742-4111, USA'
    )

    with pytest.raises(KeyError) as excinfo:
        authorlist(text)
    assert 'affiliation IDs might not be separated with commas' in str(
        excinfo.value)


def test_authorlist_multiple_affiliations_on_single_line():
    text = (
        'A. Aduszkiewicz\n'
        '1\n'
        ', Y.X. Ali\n'
        '1,20\n'
        ', E I Andronov\n'
        '20\n'
        ', Einstein\n'
        '13,15\n'
        '\n'
        '1 CERN\n'
        '20 DESY\n'
        '13 ETH ZÜRICH15PRINCETON\n'
    )

    with pytest.raises(KeyError) as excinfo:
        authorlist(text)
    assert 'There might be multiple affiliations per line' in str(
        excinfo.value)


def test_authorlist_space_between_affids():
    text = (
        'Y.X. Ali1, 20, E I Andronov20\n'
        '1 CERN\n'
        '20 DESY'
    )

    expected = (
        '100__ $$aAli, Y.X.$$vCERN $$vDESY\n'
        '700__ $$aAndronov, E. I.$$vDESY'
    )
    result = authorlist(text)

    assert expected == result.encode('utf-8')


def test_authorlist_affiliation_with_numbers_and_letters():
    text = (
        'O. Buchmueller\n'
        '1\n'
        'K. Agashe\n'
        '2\n'
        '\n'
        '1.\n'
        'High Energy Physics Group, Blackett Laboratory, Imperial College, Prince Consort Road, London SW7 2AZ, UK\n'
        '2.\n'
        'University of Maryland, Department of Physics, College Park, MD 20742-4111, USA\n'
    )

    expected = (
        '100__ $$aBuchmueller, O.$$vHigh Energy Physics Group, Blackett Laboratory, Imperial College, Prince Consort Road, London SW7 2AZ, UK\n'
        '700__ $$aAgashe, K.$$vUniversity of Maryland, Department of Physics, College Park, MD 20742-4111, USA'
    )
    result = authorlist(text)

    assert expected == result.encode('utf-8')


def test_authorlist_note_symbols():
    """Test authors which have some footnote symbols like † and ∗"""
    text = (
        'Y.X. Ali†1, 20, E I Andronov20∗\n'
        '1 CERN\n'
        '20 DESY'
    )

    expected = (
        '100__ $$aAli, Y.X.$$vCERN $$vDESY\n'
        '700__ $$aAndronov, E. I.$$vDESY'
    )
    result = authorlist(text)

    assert expected == result.encode('utf-8')


def test_authorlist_comma_wrong_position():
    """Test case when there is comma before affiliation id."""
    text = (
        'Y. Bao,\n'
        '1\n'
        'and A. Lambrecht,\n'
        '1,\n'
        '2\n'
        '1\n'
        'Department of Physics, University of Florida, Gainesville, Florida 32611\n'
        '2\n'
        'Laboratoire Kastler–Brossel, CNRS, ENS, Universit ́e Pierre et Marie Curie case 74, Campus Jussieu, F-75252 Paris Cedex 05, France\n'
    )
    expected = (
        '100__ $$aBao, Y.$$vDepartment of Physics, University of Florida, Gainesville, Florida 32611\n'
        '700__ $$aLambrecht, A.$$vDepartment of Physics, University of Florida, Gainesville, Florida 32611 $$vLaboratoire Kastler-Brossel, '
        'CNRS, ENS, Universit ́e Pierre et Marie Curie case 74, Campus Jussieu, F-75252 Paris Cedex 05, France'
    )
    result = authorlist(text)

    assert expected == result.encode('utf-8')


def test_authorlist_when_aff_line_ends_in_number():
    text = (
        'T.M. Liss\n'
        '91\n'
        'L. Littenberg\n'
        '92\n'
        '91.\n'
        'Division of Science, City College of New York, 160 Convent Avenue, New York, NY 10031\n'
        '92.\n'
        'Physics Department, Brookhaven National Laboratory, Upton, NY 11973, USA'
    )

    expected = (
        '100__ $$aLiss, T.M.$$vDivision of Science, City College of New York, 160 Convent Avenue, New York, NY 10031\n'
        '700__ $$aLittenberg, L.$$vPhysics Department, Brookhaven National Laboratory, Upton, NY 11973, USA'
    )
    result = authorlist(text)

    assert expected == result.encode('utf-8')


def test_author_with_many_affiliations():
    text = (
        'F. Durães1,2,3,4\n'
        '1 CERN\n'
        '2 Fermilab\n'
        '3 Lund University\n'
        '4 Instituto de Física, Universidade de São Paulo'
    )
    expected = (
        '100__ $$aDurães, F.$$vCERN $$vFermilab $$vLund University $$vInstituto de Física, Universidade de São Paulo'
    )

    assert authorlist(text).encode('utf-8') == expected
