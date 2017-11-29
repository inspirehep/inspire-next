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

"""INSPIREHEP WSGI app instantiation with support for coverage.py.

Uses the trick in http://stackoverflow.com/a/20689873/1407497 to instantiate
a WSGI application that reports back information on test coverage.

In addition, mocks view methods that would otherwise access outside resources
like CrossRef or arXiv.
"""

from __future__ import absolute_import, division, print_function

import atexit

import coverage
from flask import jsonify, request

from inspirehep.modules.literaturesuggest.views import validate as literature_validate
from inspirehep.modules.authors.views import validate as author_validate


cov = coverage.Coverage()
cov.start()

from .wsgi import application  # noqa


def save_coverage():
    cov.stop()
    cov.save()


atexit.register(save_coverage)


app = getattr(application, 'app', application)

app.url_map._rules.remove(app.url_map._rules_by_endpoint['inspirehep_literature_suggest.validate'][0])
app.url_map._rules.remove(app.url_map._rules_by_endpoint['inspirehep_authors.validate'][0])
app.url_map._rules.remove(app.url_map._rules_by_endpoint['inspirehep_arxiv.search'][0])
app.url_map._rules.remove(app.url_map._rules_by_endpoint['inspirehep_crossref.search'][0])

del app.url_map._rules_by_endpoint['inspirehep_literature_suggest.validate']
del app.url_map._rules_by_endpoint['inspirehep_authors.validate']
del app.url_map._rules_by_endpoint['inspirehep_arxiv.search']
del app.url_map._rules_by_endpoint['inspirehep_crossref.search']

del app.view_functions['inspirehep_literature_suggest.validate']
del app.view_functions['inspirehep_authors.validate']
del app.view_functions['inspirehep_arxiv.search']
del app.view_functions['inspirehep_crossref.search']

app.url_map.update()


@app.route('/submit/literature/validate', endpoint='inspirehep_literature_suggest.validate', methods=['POST'])
def mock_literature_validate():
    if 'url' in request.json:
        if request.json['url'] == 'http://example.com/a-pdf':
            return jsonify({
                'messages': {
                    'url': {},
                },
            })

    return literature_validate()


@app.route('/submit/author/validate', endpoint='inspirehep_authors.validate', methods=['POST'])
def mock_author_validate():
    if request.json.get('orcid') == '0000-0002-1825-0097':
        return jsonify({
            'messages': {
                'orcid': {},
            },
        })

    return author_validate()


@app.route('/doi/search', endpoint='inspirehep_crossref.search', methods=['GET'])
def mock_search_articles_by_doi():
    if request.args.get('doi') == '10.1023/a:1026654312961':
        return jsonify({
            'query': {
                'DOI': '10.1023/a:1026654312961',
                'ISSN': [
                    '0020-7748',
                ],
                'URL': 'http://dx.doi.org/10.1023/a:1026654312961',
                'alternative-id': [
                    '297194',
                ],
                'author': [
                    {
                        'affiliation': [],
                        'family': 'Maldacena',
                        'given': 'Juan',
                    },
                ],
                'container-title': [
                    'International Journal of Theoretical Physics',
                ],
                'content-domain': {
                    'crossmark-restriction': 'F',
                    'domain': [],
                },
                'created': {
                    'date-parts': [
                        [2003, 11, 6],
                    ],
                    'date-time': '2003-11-06T17:29:30Z',
                    'timestamp': 1068139770000,
                },
                'deposited': {
                    'date-parts': [
                        [2012, 12, 28],
                    ],
                    'date-time': '2012-12-28T21:39:46Z',
                    'timestamp': 1356730786000,
                },
                'indexed': {
                    'date-parts': [
                        [2016, 9, 26],
                    ],
                    'date-time': '2016-09-26T13:21:10Z',
                    'timestamp': 1474896070130,
                },
                'issue': '4',
                'issued': {
                    'date-parts': [
                        [1999],
                    ],
                },
                'member': 'http://id.crossref.org/member/297',
                'original-title': [],
                'page': '1113-1133',
                'prefix': 'http://id.crossref.org/prefix/10.1007',
                'published-print': {
                    'date-parts': [
                        [1999],
                    ]
                },
                'publisher': 'Springer Nature',
                'reference-count': 0,
                'score': 1.0,
                'short-container-title': [],
                'short-title': [],
                'source': 'CrossRef',
                'subject': [
                    'Physics and Astronomy (miscellaneous)',
                    'Mathematics(all)',
                ],
                'subtitle': [],
                'title': [],
                'type': 'journal-article',
                'volume': '38',
            },
            'source': 'crossref',
            'status': 'success',
        })
    elif request.args.get('doi') == '10.1086/305772':
        return jsonify({
            'query': {
                'DOI': '10.1086/305772',
                'ISSN': [
                    '0004-637X',
                    '1538-4357',
                ],
                'URL': 'http://dx.doi.org/10.1086/305772',
                'alternative-id': [
                    '10.1086/305772',
                ],
                'author': [
                    {
                        'affiliation': [],
                        'family': 'Schlegel',
                        'given': 'David J.',
                    },
                    {
                        'affiliation': [],
                        'family': 'Finkbeiner',
                        'given': 'Douglas P.',
                    },
                    {
                        'affiliation': [],
                        'family': 'Davis',
                        'given': 'Marc',
                    }
                ],
                'container-title': [
                    'The Astrophysical Journal',
                ],
                'content-domain': {
                    'crossmark-restriction': False,
                    'domain': [],
                },
                'created': {
                    'date-parts': [
                        [2002, 7, 26],
                    ],
                    'date-time': '2002-07-26T18:50:42Z',
                    'timestamp': 1027709442000,
                },
                'deposited': {
                    'date-parts': [
                        [2011, 8, 23],
                    ],
                    'date-time': '2011-08-23T14:08:25Z',
                    'timestamp': 1314108505000,
                },
                'indexed': {
                    'date-parts': [
                        [2016, 9, 26],
                    ],
                    'date-time': '2016-09-26T15:34:12Z',
                    'timestamp': 1474904052331,
                },
                'issue': '2',
                'issued': {
                    'date-parts': [
                        [1998, 6, 20],
                    ],
                },
                'member': 'http://id.crossref.org/member/266',
                'original-title': [],
                'page': '525-553',
                'prefix': 'http://id.crossref.org/prefix/10.1088',
                'published-print': {
                    'date-parts': [
                        [1998, 6, 20],
                    ]
                },
                'publisher': 'IOP Publishing',
                'reference-count': 83,
                'score': 1.0,
                'short-container-title': [
                    'ApJ',
                ],
                'short-title': [],
                'source': 'CrossRef',
                'subject': [
                    'Space and Planetary Science',
                    'Astronomy and Astrophysics',
                ],
                'subtitle': [],
                'title': [
                    'Maps of Dust Infrared Emission for Use in Estimation of Reddening '
                    'and Cosmic Microwave Background Radiation Foregrounds',
                ],
                'type': 'journal-article',
                'volume': '500',
            },
            'source': 'crossref',
            'status': 'success',
        })
    else:
        return ''


@app.route('/arxiv/search', endpoint='inspirehep_arxiv.search', methods=['GET'])
def mock_search_articles_by_arxiv():
    if request.args.get('arxiv') == 'hep-th/9711200':
        return jsonify({
            'query': {
                'abstract': (
                    'We show that the large $N$ limit of certain conformal field theories'),
                'authors': [
                    {
                        'author': [
                            {'keyname': 'Maldacena'},
                            {'forenames': 'Juan M.'},
                        ],
                    },
                ],
                'categories': 'hep-th',
                'comments': (
                    '20 pages, harvmac, v2: section on AdS_2 corrected, references added,\n '
                    'v3: More references and a sign in eqns 2.8 and 2.9 corrected'),
                'created': '1997-11-27',
                'doi': '10.1023/A:1026654312961',
                'id': 'hep-th/9711200',
                'journal-ref': 'Adv.Theor.Math.Phys.2:231-252,1998',
                'report-no': 'HUTP-98/A097',
                'request': 'http://export.arxiv.org/oai2',
                'responseDate': '2016-10-17T15:05:15Z',
                'title': 'The Large N Limit of Superconformal Field Theories and Supergravity',
                'updated': '1998-01-22',
            },
            'source': 'arxiv',
            'status': 'success',
        })
    elif request.args.get('arxiv') == '1207.7235':
        return jsonify({
            'query': {
                'abstract': (
                    'Results are presented from searches for the standard model Higgs boson in '
                    'proton-proton collisions at sqrt(s) = 7 and 8 TeV in the Compact Muon '
                    'Solenoid experiment at the LHC, using data samples corresponding to '
                    'integrated luminosities of up to 5.1 inverse femtobarns at 7 TeV and 5.3 '
                    'inverse femtobarns at 8 TeV. The search is performed in five decay modes: '
                    'gamma gamma, ZZ, WW, tau tau, and b b-bar. An excess of events is observed '
                    'above the expected background, with a local significance of 5.0 standard '
                    'deviations, at a mass near 125 GeV, signalling the production of a new '
                    'particle. The expected significance for a standard model Higgs boson of '
                    'that mass is 5.8 standard deviations. The excess is most significant in the '
                    'two decay modes with the best mass resolution, gamma gamma and ZZ; a fit to '
                    'these signals gives a mass of 125.3 +/- 0.4 (stat.) +/- 0.5 (syst.) GeV. '
                    'The decay to two photons indicates that the new particle is a boson with '
                    'spin different from one. '),
                'authors': [
                    {
                        'author': [
                            {'keyname': 'The CMS Collaboration'},
                        ],
                    },
                ],
                'categories': 'hep-ex',
                'comments': 'Submitted to Phys. Lett. B',
                'created': '2012-07-31',
                'doi': '10.1016/j.physletb.2012.08.021',
                'id': '1207.7235',
                'journal-ref': 'Phys. Lett. B 716 (2012) 30',
                'license': 'http://arxiv.org/licenses/nonexclusive-distrib/1.0/',
                'report-no': 'CMS-HIG-12-028; CERN-PH-EP-2012-220',
                'request': 'http://export.arxiv.org/oai2',
                'responseDate': '2016-10-17T15:22:25Z',
                'title': (
                    'Observation of a new boson at a mass of 125 GeV with the CMS experiment\n '
                    'at the LHC'),
                'updated': '2013-01-28',
            },
            'source': 'arxiv',
            'status': 'success',
        })
    else:
        return ''
