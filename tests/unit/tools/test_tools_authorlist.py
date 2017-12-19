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

import pytest
from inspirehep.modules.tools.authorlist create_authors


def test_create_authors_without_affiliations():
    text = (
        'K. Berkelman, D. Cords, R. Felst, E. Gadermann, G. Grindhammer, '
        'H. Hultschig, P. Joos, W. Koch, U. Kötz, H. Krehbiel, D. Kreinick, '
        'J. Ludwig, K.-H. Mess, K.C. Moffeit, A. Petersen, G. Poelz, '
        'J. Ringel, K. Sauerberg, P. Schmüser, G. Vogel, B.H. Wiik, G. Wolf'
    )

    expected = [
        (u'K. Berkelman', []),
        (u'D. Cords', []),
        (u'R. Felst', []),
        (u'E. Gadermann', []),
        (u'G. Grindhammer', []),
        (u'H. Hultschig', []),
        (u'P. Joos', []),
        (u'W. Koch', []),
        (u'U. Kötz', []),
        (u'H. Krehbiel', []),
        (u'D. Kreinick', []),
        (u'J. Ludwig', []),
        (u'K.-H. Mess', []),
        (u'K.C. Moffeit', []),
        (u'A. Petersen', []),
        (u'G. Poelz', []),
        (u'J. Ringel', []),
        (u'K. Sauerberg', []),
        (u'P. Schm\xfcser', []),
        (u'G. Vogel', []),
        (u'B.H. Wiik', []),
        (u'G. Wolf', []),
    ]
    result = create_authors(text)

    assert expected == result['authors']
    assert 'warnings' not in result.keys()


def test_create_authors_with_affiliations():
    text = (
        'F. Durães1, A.V. Giannini2, V.P. Gonçalves3,4 and F.S. Navarra2\n'
        ' \n'
        '1 CERN\n'
        '2 Fermilab\n'
        '3 Lund University\n'
        '4 Instituto de Física, Universidade de São Paulo'
    )

    expected = [
        (u'F. Dur\xe3es', [u'CERN'],),
        (u'A.V. Giannini', [u'Fermilab'],),
        (u'V.P. Gon\xe7alves', [
            u'Lund University',
            u'Instituto de F\xedsica, Universidade de S\xe3o Paulo'
            ],),
        (u'F.S. Navarra', [u'Fermilab'],),
    ]
    result = create_authors(text)

    assert expected == result['authors']


def test_create_authors_with_no_text():
    text = None

    expected = {}
    result = create_authors(text)

    assert expected == result


def test_create_authors_with_no_firstnames():
    text = 'Einstein, Bohr'

    expected = [
        (u'Einstein', []),
        (u'Bohr', []),
    ]
    result = create_authors(text)

    assert expected == result['authors']
    assert 'Author without firstname' in result['warnings']


def test_create_authors_with_missing_affid():
    """Test case when `create_authors` thinks every author should have an affid.

    This might happen because someone is missing affid or has a number in
    his/her name so it's tricking `create_authors`.
    """
    text = 'A. Einstein, N. Bohr2'

    result = create_authors(text)

    expected = [
        (u'A. Einstein', []),
        (u'N. Bohr', []),
    ]

    assert expected == result['authors']
    assert 'Unresolved aff-ID' in result['warnings']


def test_create_authors_with_affid_but_missing_affiliation():
    """Test case when some author has an affiliation id but no affiliation."""
    text = (
        'A. Einstein1, N. Bohr2\n'
        '\n'
        '2 Københavns Universitet'
    )

    result = create_authors(text)

    expected = [
        (u'A. Einstein', []),
        (u'N. Bohr', [u'K\xf8benhavns Universitet']),
    ]

    assert expected == result['authors']
    assert 'Unresolved aff-ID' in result['warnings']


def test_create_authors_with_invalid_affiliation():
    """Test case when an affiliation has no valid id."""
    text = (
        'A. Einstein1, N. Bohr2\n'
        '\n'
        'ETH\n'
        '2 Københavns Universitet'
    )

    with pytest.raises(ValueError) as excinfo:
        create_authors(text)
    assert 'Cannot identify type of affiliations' in str(excinfo.value)


def test_create_authors_with_one_author_missing_affiliation():
    """Test case when some author doesn't have an affiliation."""
    text = (
        'A. Einstein, N. Bohr1,2\n'
        '\n'
        '1 ETH\n'
        '2 Københavns Universitet'
    )

    result = create_authors(text)

    expected = [
        (u'A. Einstein', []),
        (u'N. Bohr', [u'ETH', u'K\xf8benhavns Universitet']),
    ]

    assert expected == result['authors']
    assert 'Author without affiliation-id' in result['warnings']


def test_create_authors_ignores_space_between_authors_and_affiliations():
    text = (
        'F. Lastname1, F.M. Otherlastname1,2\n'
        '\n'
        '1 CERN\n'
        '2 Otheraffiliation'
    )

    expected = [
        (u'F. Lastname', [u'CERN']),
        (u'F.M. Otherlastname', [u'CERN', u'Otheraffiliation']),
    ]

    result = create_authors(text)

    assert expected == result['authors']


def test_create_authors_bad_author_lines():
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

    expected = [
        (u'A. Aduszkiewicz', [u'CERN']),
        (u'Y.X. Ali', [u'CERN', u'DESY']),
        (u'E I Andronov', [u'DESY']),
        (u'Einstein', [u'ETH Z\xdcRICH', u'PRINCETON']),
    ]
    result = create_authors(text)

    assert expected == result['authors']


def test_create_authors_no_commas_between_authors():
    text = (
        'C. Patrignani1 K. Agashe2 G. Aielli1,2\n'
        '\n'
        '1 Universita di Bologna and INFN, Dip. Scienze per la Qualita della Vita, I-47921, Rimini, Italy\n'
        '2 University of Maryland, Department of Physics, College Park, MD 20742-4111, USA'
    )

    expected = [
        (u'C. Patrignani', [u'Universita di Bologna and INFN, Dip. Scienze per la Qualita della Vita, I-47921, Rimini, Italy']),
        (u'K. Agashe', [u'University of Maryland, Department of Physics, College Park, MD 20742-4111, USA']),
        (u'G. Aielli', [u'Universita di Bologna and INFN, Dip. Scienze per la Qualita della Vita, I-47921, Rimini, Italy', u'University of Maryland, Department of Physics, College Park, MD 20742-4111, USA']),
    ]
    result = create_authors(text)

    assert expected == result['authors']


def test_create_authors_newlines_and_no_commas_between_authors():
    text = (
        'C. Patrignani\n'
        '1\n'
        'K. Agashe\n'
        '2\n'
        'G. Aielli\n'
        '1,\n'
        '2\n'
        '\n'
        '1\n'
        'Universita di Bologna and INFN, Dip. Scienze per la Qualita della Vita, I-47921, Rimini, Italy\n'
        '2\n'
        'University of Maryland, Department of Physics, College Park, MD 20742-4111, USA'
    )

    expected = [
        (u'C. Patrignani', [u'Universita di Bologna and INFN, Dip. Scienze per la Qualita della Vita, I-47921, Rimini, Italy']),
        (u'K. Agashe', [u'University of Maryland, Department of Physics, College Park, MD 20742-4111, USA']),
        (u'G. Aielli', [u'Universita di Bologna and INFN, Dip. Scienze per la Qualita della Vita, I-47921, Rimini, Italy', u'University of Maryland, Department of Physics, College Park, MD 20742-4111, USA']),
    ]
    result = create_authors(text)

    assert expected == result['authors']


def test_create_authors_affids_with_dots():
    text = (
        'C. Patrignani\n'
        '1,\n'
        'K. Agashe\n'
        '2,\n'
        'G. Aielli\n'
        '1,\n'
        '2\n'
        '\n'
        '1.\n'
        'Universita di Bologna and INFN, Dip. Scienze per la Qualita della Vita, I-47921, Rimini, Italy\n'
        '2.\n'
        'University of Maryland, Department of Physics, College Park, MD 20742-4111, USA'
    )

    expected = [
        (u'C. Patrignani', [u'Universita di Bologna and INFN, Dip. Scienze per la Qualita della Vita, I-47921, Rimini, Italy']),
        (u'K. Agashe', [u'University of Maryland, Department of Physics, College Park, MD 20742-4111, USA']),
        (u'G. Aielli', [u'Universita di Bologna and INFN, Dip. Scienze per la Qualita della Vita, I-47921, Rimini, Italy', u'University of Maryland, Department of Physics, College Park, MD 20742-4111, USA']),
    ]
    result = create_authors(text)

    assert expected == result['authors']


def test_create_authors_no_commas_between_affids():
    text = (
        'C. Patrignani\n'
        '1,\n'
        'K. Agashe\n'
        '2,\n'
        'G. Aielli\n'
        '1\n'
        '2\n'
        '\n'
        '1.\n'
        'Universita di Bologna and INFN, Dip. Scienze per la Qualita della Vita, I-47921, Rimini, Italy\n'
        '2.\n'
        'University of Maryland, Department of Physics, College Park, MD 20742-4111, USA'
    )

    expected = [
        (u'C. Patrignani', [u'Universita di Bologna and INFN, Dip. Scienze per la Qualita della Vita, I-47921, Rimini, Italy']),
        (u'K. Agashe', [u'University of Maryland, Department of Physics, College Park, MD 20742-4111, USA']),
        (u'G. Aielli', [u'Universita di Bologna and INFN, Dip. Scienze per la Qualita della Vita, I-47921, Rimini, Italy', u'University of Maryland, Department of Physics, College Park, MD 20742-4111, USA']),
    ]
    result = create_authors(text)

    assert expected == result['authors']


def test_create_authors_multiple_affiliations_on_single_line():
    text = (
        'Y.X. Ali\n'
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

    expected = [
        (u'Y.X. Ali', [u'CERN', u'DESY']),
        (u'E I Andronov', [u'DESY']),
        (u'Einstein', [u'ETH Z\xdcRICH15PRINCETON']),
    ]

    result = create_authors(text)

    assert expected == result['authors']
    assert 'Unresolved aff-ID' in result['warnings']


def test_create_authors_space_between_affids():
    text = (
        'Y.X. Ali1, 20, E I Andronov20\n'
        '\n'
        '1 CERN\n'
        '20 DESY'
    )

    expected = [
        (u'Y.X. Ali', [u'CERN', u'DESY']),
        (u'E I Andronov', [u'DESY']),
    ]
    result = create_authors(text)

    assert expected == result['authors']


def test_create_authors_affiliation_with_numbers_and_letters():
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

    expected = [
        (u'O. Buchmueller', [u'High Energy Physics Group, Blackett Laboratory, Imperial College, Prince Consort Road, London SW7 2AZ, UK']),
        (u'K. Agashe', [u'University of Maryland, Department of Physics, College Park, MD 20742-4111, USA']),
    ]
    result = create_authors(text)

    assert expected == result['authors']


def test_create_authors_note_footnotes():
    """Test authors which have some footnote symbols like † and ∗"""
    text = (
        'Y.X. Ali†1, 20, E I Andronov20∗\n'
        '\n'
        '1 CERN\n'
        '20 DESY'
    )

    expected = [
        (u'Y.X. Ali', [u'CERN', u'DESY']),
        (u'E I Andronov', [u'DESY']),
    ]
    result = create_authors(text)

    assert expected == result['authors']
    assert 'stray footnote symbol' in result['warnings']


def test_create_authors_note_symbols():
    """Test authors which have symbols like † and ∗"""
    text = (
        'Y.X. Aduszkiewicž†1, 20, E I Andronov20∗\n'
        '\n'
        '† CERN\n'
        '∗ DESY'
    )

    expected = [
        (u'Y.X. Aduszkiewic\u017e', [u'CERN']),
        (u'E I Andronov', [u'DESY']),
    ]
    result = create_authors(text)

    assert expected == result['authors']
    assert 'CAUTION! Using symbols' in result['warnings']


def test_create_authors_comma_wrong_position():
    """Test case when there is comma before affiliation id."""
    text = (
        'Y. Bao,\n'
        '1\n'
        'and A. Lambrecht,\n'
        '1,\n'
        '2\n'
        '\n'
        '1\n'
        'Department of Physics, University of Florida, Gainesville, Florida 32611\n'
        '2\n'
        'Laboratoire Kastler-Brossel, CNRS, ENS, Universit ́e Pierre et Marie Curie case 74, Campus Jussieu, F-75252 Paris Cedex 05, France\n'
    )

    expected = [
        (u'Y. Bao', [u'Department of Physics, University of Florida, Gainesville, Florida 32611']),
        (u'A. Lambrecht', [u'Department of Physics, University of Florida, Gainesville, Florida 32611', u'Laboratoire Kastler-Brossel, CNRS, ENS, Universit \u0301e Pierre et Marie Curie case 74, Campus Jussieu, F-75252 Paris Cedex 05, France']),
    ]
    result = create_authors(text)

    assert expected == result['authors']


def test_create_authors_when_aff_line_ends_in_number():
    text = (
        'T.M. Liss\n'
        '1\n'
        'L. Littenberg\n'
        '2\n'
        '\n'
        '1.\n'
        'Division of Science, City College of New York, 160 Convent Avenue, New York, NY 10031\n'
        '2.\n'
        'Physics Department, Brookhaven National Laboratory, Upton, NY 11973, USA'
    )

    expected = [
        (u'T.M. Liss', [u'Division of Science, City College of New York, 160 Convent Avenue, New York, NY 10031']),
        (u'L. Littenberg', [u'Physics Department, Brookhaven National Laboratory, Upton, NY 11973, USA']),
    ]
    result = create_authors(text)

    assert expected == result['authors']


def test_create_authors_with_many_affiliations():
    text = (
        'F. Durães1,2,3,4\n'
        '\n'
        '1 CERN\n'
        '2 Fermilab\n'
        '3 Lund University\n'
        '4 Instituto de Física, Universidade de São Paulo'
    )

    expected = [
        (u'F. Dur\xe3es', [u'CERN', u'Fermilab', u'Lund University', u'Instituto de F\xedsica, Universidade de S\xe3o Paulo']),
    ]
    result = create_authors(text)

    assert expected == result['authors']


def test_authorlist_handles_spaces_at_the_end_of_an_author_or_affiliation():
    text = (
        'J. Smith1 \n'
        '\n'
        '1 University of somewhere '
    )

    expected = [
        (u'J. Smith', [u'University of somewhere']),
    ]
    result = create_authors(text)

    assert expected == result['authors']


def test_create_authors_with_letters():
    text = (
        'J. Mills a L. di Caprio\n'
        'B. Smith bb\n'
        '\n'
        'a CERN\n'
        'bb Fermilab\n'
    )

    expected = [
        (u'J. Mills', ['CERN']),
        (u'L. di Caprio', []),
        (u'B. Smith', ['Fermilab']),
    ]
    result = create_authors(text)

    assert expected == result['authors']
    assert 'Author without affiliation-id.' in result['warnings']
    assert 'Is this part of a name or missing aff-id?' in result['warnings']


def test_unused_affiliation():
    text = (
        'K. Sachs 1, F. Schwennsen 1\n'
        '\n'
        '1 DESY\n'
        '2 CERN\n'
    )

    expected = [
        (u'K. Sachs', ['DESY']),
        (u'F. Schwennsen', ['DESY']),
    ]
    result = create_authors(text)

    assert expected == result['authors']
    assert 'Unused affiliation-IDs' in result['warnings']

