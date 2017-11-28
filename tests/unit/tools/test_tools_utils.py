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

    expected = [
        {'full_name': u'Berkelman, K.'},
        {'full_name': u'Cords, D.'},
        {'full_name': u'Felst, R.'},
        {'full_name': u'Gadermann, E.'},
        {'full_name': u'Grindhammer, G.'},
        {'full_name': u'Hultschig, H.'},
        {'full_name': u'Joos, P.'},
        {'full_name': u'Koch, W.'},
        {'full_name': u'K\xf6tz, U.'},
        {'full_name': u'Krehbiel, H.'},
        {'full_name': u'Kreinick, D.'},
        {'full_name': u'Ludwig, J.'},
        {'full_name': u'Mess, K.-H.'},
        {'full_name': u'Moffeit, K.C.'},
        {'full_name': u'Petersen, A.'},
        {'full_name': u'Poelz, G.'},
        {'full_name': u'Ringel, J.'},
        {'full_name': u'Sauerberg, K.'},
        {'full_name': u'Schm\xfcser, P.'},
        {'full_name': u'Vogel, G.'},
        {'full_name': u'Wiik, B.H.'},
        {'full_name': u'Wolf, G.'},
    ]
    result = authorlist(text)

    assert expected == result['authors']


def test_authorlist_with_affiliations():
    text = (
        'F. Durães1, A.V. Giannini2, V.P. Gonçalves3,4 and F.S. Navarra2\n'
        '1 CERN\n'
        '2 Fermilab\n'
        '3 Lund University\n'
        '4 Instituto de Física, Universidade de São Paulo'
    )

    expected = [
        {
            'full_name': u'Dur\xe3es, F.',
            'raw_affiliations': [
                {'value': u'CERN'},
            ],
        },
        {
            'full_name': u'Giannini, A.V.',
            'raw_affiliations': [
                {'value': u'Fermilab'},
            ],
        },
        {
            'full_name': u'Gon\xe7alves, V.P.',
            'raw_affiliations': [
                {'value': u'Lund University'},
                {'value': u'Instituto de F\xedsica, Universidade de S\xe3o Paulo'},
            ],
        },
        {
            'full_name': u'Navarra, F.S.',
            'raw_affiliations': [
                {'value': u'Fermilab'},
            ],
        },
    ]
    result = authorlist(text)

    assert expected == result['authors']


def test_authorlist_with_no_text():
    text = None

    expected = {}
    result = authorlist(text)

    assert expected == result


def test_authorlist_with_no_firstnames():
    text = 'Einstein, Bohr'

    expected = [
        {'full_name': u'Einstein'},
        {'full_name': u'Bohr'},
    ]
    result = authorlist(text)

    assert expected == result['authors']


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

    expected = [
        {
            'full_name': u'Lastname, F.',
            'raw_affiliations': [
                {'value': u'CERN'},
            ],
        },
        {
            'full_name': u'Otherlastname, F.M.',
            'raw_affiliations': [
                {'value': u'CERN'},
                {'value': u'Otheraffiliation'},
            ],
        },
    ]
    result = authorlist(text)

    assert expected == result['authors']


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

    expected = [
        {
            'full_name': u'Aduszkiewicz, A.',
            'raw_affiliations': [
                {'value': u'CERN'},
            ],
        },
        {
            'full_name': u'Ali, Y.X.',
            'raw_affiliations': [
                {'value': u'CERN'},
                {'value': u'DESY'}
            ]
        },
        {
            'full_name': u'Andronov, E.I.',
            'raw_affiliations': [{'value': u'DESY'}]
        },
        {
            'full_name': u'Einstein',
            'raw_affiliations': [
                {'value': u'ETH Z\xdcRICH'},
                {'value': u'PRINCETON'}
            ]
        },
    ]
    result = authorlist(text)

    assert expected == result['authors']


def test_authorlist_no_commas_between_authors():
    text = (
        'C. Patrignani1 K. Agashe2 G. Aielli1,2\n'
        '1 Universit`a di Bologna and INFN, Dip. Scienze per la Qualit`a della Vita, I-47921, Rimini, Italy\n'
        '2 University of Maryland, Department of Physics, College Park, MD 20742-4111, USA'
    )

    expected = [
        {
            'full_name': u'Patrignani, C.',
            'raw_affiliations': [
                {'value': u'Universit\xe0 di Bologna and INFN, Dip. Scienze per la Qualit\xe0 della Vita, I-47921, Rimini, Italy'},
            ],
        },
        {
            'full_name': u'Agashe, K.',
            'raw_affiliations': [
                {'value': u'University of Maryland, Department of Physics, College Park, MD 20742-4111, USA'},
            ],
        },
        {
            'full_name': u'Aielli, G.',
            'raw_affiliations': [
                {'value': u'Universit\xe0 di Bologna and INFN, Dip. Scienze per la Qualit\xe0 della Vita, I-47921, Rimini, Italy'},
                {'value': u'University of Maryland, Department of Physics, College Park, MD 20742-4111, USA'},
            ],
        },
    ]
    result = authorlist(text)

    assert expected == result['authors']


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

    expected = [
        {
            'full_name': u'Patrignani, C.',
            'raw_affiliations': [
                {'value': u'Universit\xe0 di Bologna and INFN, Dip. Scienze per la Qualit\xe0 della Vita, I-47921, Rimini, Italy'},
            ],
        },
        {
            'full_name': u'Agashe, K.',
            'raw_affiliations': [
                {'value': u'University of Maryland, Department of Physics, College Park, MD 20742-4111, USA'},
            ],
        },
        {
            'full_name': u'Aielli, G.',
            'raw_affiliations': [
                {'value': u'Universit\xe0 di Bologna and INFN, Dip. Scienze per la Qualit\xe0 della Vita, I-47921, Rimini, Italy'},
                {'value': u'University of Maryland, Department of Physics, College Park, MD 20742-4111, USA'},
            ],
        },
    ]
    result = authorlist(text)

    assert expected == result['authors']


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

    expected = [
        {
            'full_name': u'Patrignani, C.',
            'raw_affiliations': [
                {'value': u'Universit\xe0 di Bologna and INFN, Dip. Scienze per la Qualit\xe0 della Vita, I-47921, Rimini, Italy'},
            ],
        },
        {
            'full_name': u'Agashe, K.',
            'raw_affiliations': [
                {'value': u'University of Maryland, Department of Physics, College Park, MD 20742-4111, USA'},
            ],
        },
        {
            'full_name': u'Aielli, G.',
            'raw_affiliations': [
                {'value': u'Universit\xe0 di Bologna and INFN, Dip. Scienze per la Qualit\xe0 della Vita, I-47921, Rimini, Italy'},
                {'value': u'University of Maryland, Department of Physics, College Park, MD 20742-4111, USA'},
            ],
        },
    ]
    result = authorlist(text)

    assert expected == result['authors']


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
    assert 'affiliation IDs might not be separated with commas' in str(excinfo.value)


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
    assert 'There might be multiple affiliations per line' in str(excinfo.value)


def test_authorlist_space_between_affids():
    text = (
        'Y.X. Ali1, 20, E I Andronov20\n'
        '1 CERN\n'
        '20 DESY'
    )

    expected = [
        {
            'full_name': u'Ali, Y.X.',
            'raw_affiliations': [
                {'value': u'CERN'},
                {'value': u'DESY'},
            ],
        },
        {
            'full_name': u'Andronov, E.I.',
            'raw_affiliations': [
                {'value': u'DESY'},
            ],
        },
    ]
    result = authorlist(text)

    assert expected == result['authors']


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

    expected = [
        {
            'full_name': u'Buchmueller, O.',
            'raw_affiliations': [
                {'value': u'High Energy Physics Group, Blackett Laboratory, Imperial College, Prince Consort Road, London SW7 2AZ, UK'},
            ],
        },
        {
            'full_name': u'Agashe, K.',
            'raw_affiliations': [
                {'value': u'University of Maryland, Department of Physics, College Park, MD 20742-4111, USA'},
            ],
        },
    ]
    result = authorlist(text)

    assert expected == result['authors']


def test_authorlist_note_symbols():
    """Test authors which have some footnote symbols like † and ∗"""
    text = (
        'Y.X. Ali†1, 20, E I Andronov20∗\n'
        '1 CERN\n'
        '20 DESY'
    )

    expected = [
        {
            'full_name': u'Ali, Y.X.',
            'raw_affiliations': [
                {'value': u'CERN'},
                {'value': u'DESY'},
            ],
        },
        {
            'full_name': u'Andronov, E.I.',
            'raw_affiliations': [
                {'value': u'DESY'},
            ],
        },
    ]
    result = authorlist(text)

    assert expected == result['authors']


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

    expected = [
        {
            'full_name': u'Bao, Y.',
            'raw_affiliations': [
                {'value': u'Department of Physics, University of Florida, Gainesville, Florida 32611'},
            ],
        },
        {
            'full_name': u'Lambrecht, A.',
            'raw_affiliations': [
                {'value': u'Department of Physics, University of Florida, Gainesville, Florida 32611'},
                {'value': u'Laboratoire Kastler-Brossel, CNRS, ENS, Universit \u0301e Pierre et Marie Curie case 74, Campus Jussieu, F-75252 Paris Cedex 05, France'},
            ],
        },
    ]
    result = authorlist(text)

    assert expected == result['authors']


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

    expected = [
        {
            'full_name': u'Liss, T.M.',
            'raw_affiliations': [
                {'value': u'Division of Science, City College of New York, 160 Convent Avenue, New York, NY 10031'},
            ],
        },
        {
            'full_name': u'Littenberg, L.',
            'raw_affiliations': [
                {'value': u'Physics Department, Brookhaven National Laboratory, Upton, NY 11973, USA'},
            ],
        },
    ]
    result = authorlist(text)

    assert expected == result['authors']


def test_authorlist_with_many_affiliations():
    text = (
        'F. Durães1,2,3,4\n'
        '1 CERN\n'
        '2 Fermilab\n'
        '3 Lund University\n'
        '4 Instituto de Física, Universidade de São Paulo'
    )

    expected = [
        {
            'full_name': u'Dur\xe3es, F.',
            'raw_affiliations': [
                {'value': u'CERN'},
                {'value': u'Fermilab'},
                {'value': u'Lund University'},
                {'value': u'Instituto de F\xedsica, Universidade de S\xe3o Paulo'},
            ],
        },
    ]
    result = authorlist(text)

    assert expected == result['authors']


def test_authorlist_handles_spaces_at_the_end_of_an_author():
    text = (
        u'J. Smith1 \n'
        u'1 University of somewhere'
    )

    expected = [
        {
            'full_name': u'Smith, J.',
            'raw_affiliations': [
                {'value': u'University of somewhere'},
            ],
        },
    ]
    result = authorlist(text)

    assert expected == result['authors']


def test_authorlist_handles_spaces_at_the_end_of_an_affiliation():
    text = (
        u'A. J. Hawken1, B. R. Granett1, A. Iovino1, L. Guzzo1,2\n'
        u'1 INAF–Osservatorio Astronomico di Brera, via Brera 28, 20122 Milano, via E. Bianchi 46, 23807 Merate, Italy \n'
        u'2 Università degli Studi di Milano, via G. Celoria 16, 20130 Milano, Italy'
    )

    expected = [
        {
            'full_name': u'Hawken, A.J.',
            'raw_affiliations': [
                {'value': u'INAF-Osservatorio Astronomico di Brera, via Brera 28, 20122 Milano, via E. Bianchi 46, 23807 Merate, Italy'},
            ],
        },
        {
            'full_name': u'Granett, B.R.',
            'raw_affiliations': [
                {'value': u'INAF-Osservatorio Astronomico di Brera, via Brera 28, 20122 Milano, via E. Bianchi 46, 23807 Merate, Italy'},
            ],
        },
        {
            'full_name': u'Iovino, A.',
            'raw_affiliations': [
                {'value': u'INAF-Osservatorio Astronomico di Brera, via Brera 28, 20122 Milano, via E. Bianchi 46, 23807 Merate, Italy'},
            ],
        },
        {
            'full_name': u'Guzzo, L.',
            'raw_affiliations': [
                {'value': u'INAF-Osservatorio Astronomico di Brera, via Brera 28, 20122 Milano, via E. Bianchi 46, 23807 Merate, Italy'},
                {'value': u'Università degli Studi di Milano, via G. Celoria 16, 20130 Milano, Italy'},
            ],
        },
    ]
    result = authorlist(text)

    assert expected == result['authors']
