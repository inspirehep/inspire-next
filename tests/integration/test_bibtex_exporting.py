# -*- coding: utf-8 -*-
#
# This file is part of INSPIRE.
# Copyright (C) 2016, 2017 CERN.
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

from inspirehep.utils.bibtex import Bibtex
from inspirehep.utils.record_getter import get_db_record


@pytest.mark.xfail
def test_format_article(app):
    article = get_db_record('lit', 4328)

    expected = u'''@article{Glashow:1961tr,
      author         = "Glashow, S. L.",
      title          = "{Partial Symmetries of Weak Interactions}",
      journal        = "Nucl. Phys.",
      volume         = "22",
      year           = "1961",
      pages          = "579-588",
      doi            = "10.1016/0029-5582(61)90469-2",
      SLACcitation   = "%%CITATION = INSPIRE-4328;%%"
}'''
    result = Bibtex(article).format()

    assert expected == result


@pytest.mark.xfail
def test_format_inproceeding(app):
    inproceeding = get_db_record('lit', 524480)

    expected = u'''@inproceedings{Hu:2000az,
      author         = "Hu, Wayne",
      title          = "{CMB anisotropies: A Decadal survey}",
      url            = "http://alice.cern.ch/format/showfull?sysnb=2178340",
      year           = "2",
      eprint         = "astro-ph/0002520",
      archivePrefix  = "arXiv",
      primaryClass   = "astro-ph",
      SLACcitation   = "%%CITATION = ASTRO-PH/0002520;%%"
}'''
    result = Bibtex(inproceeding).format()

    assert expected == result


@pytest.mark.xfail
def test_format_proceeding(app):
    proceeding = get_db_record('lit', 701585)

    expected = u'''@proceedings{Alekhin:2005dx,
      author         = "De Roeck, A. and Jung, H.",
      title          = "{HERA and the LHC: A Workshop on the implications of HERA for LHC physics: Proceedings Part A}",
      organization   = "CERN",
      publisher      = "CERN",
      address        = "Geneva",
      url            = "http://weblib.cern.ch/abstract?CERN-2005-014",
      year           = "2005",
      pages          = "pp.1-326",
      eprint         = "hep-ph/0601012",
      archivePrefix  = "arXiv",
      primaryClass   = "hep-ph",
      reportNumber   = "CERN-2005-014, DESY-PROC-2005-01",
      SLACcitation   = "%%CITATION = HEP-PH/0601012;%%"
}'''
    result = Bibtex(proceeding).format()

    assert expected == result


@pytest.mark.xfail
def test_format_thesis(app):
    thesis = get_db_record('lit', 1395663)

    expected = u'''@phdthesis{Mankuzhiyil:2010jpa,
      author         = "Mankuzhiyil, Nijil",
      title          = "{MAGIC $\\gamma$-ray observations of distant AGN and a study of source variability and the extragalactic background light using FERMI and air Cherenkov telescopes}",
      school         = "Udine U.",
      year           = "2010",
      url            = "https://magicold.mpp.mpg.de/publications/theses/NMankuzhiyil.pdf",
      SLACcitation   = "%%CITATION = INSPIRE-1395663;%%"
}'''
    result = Bibtex(thesis).format()

    assert expected == result


# TODO: _format_thesis, mastersthesis case.


# TODO: _format_thesis, else case.


@pytest.mark.xfail
def test_format_book(app):
    book = get_db_record('lit', 736770)

    expected = u'''@book{Fecko:2006zy,
      author         = "Fecko, M.",
      title          = "{Differential geometry and Lie groups for physicists}",
      publisher      = "Cambridge University Press",
      year           = "2011",
      ISBN           = "978-0-521-18796-1, 978-0-521-84507-6, 978-0-511-24296-0",
      SLACcitation   = "%%CITATION = INSPIRE-736770;%%"
}'''
    result = Bibtex(book).format()

    assert expected == result


@pytest.mark.xfail
def test_format_inbook(app):
    inbook = get_db_record('lit', 1375491)

    expected = u'''@inbook{Bechtle:2015nta,
      author         = "Bechtle, Philip and Plehn, Tilman and Sander, Christian",
      title          = "{Supersymmetry}",
      url            = "http://inspirehep.net/record/1375491/files/arXiv:1506.03091.pdf",
      year           = "2015",
      pages          = "421-462",
      doi            = "10.1007/978-3-319-15001-7_10",
      eprint         = "1506.03091",
      archivePrefix  = "arXiv",
      primaryClass   = "hep-ex",
      SLACcitation   = "%%CITATION = ARXIV:1506.03091;%%"
}'''
    result = Bibtex(inbook).format()

    assert expected == result
