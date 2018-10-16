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

from __future__ import absolute_import, division, print_function

from mock import Mock, patch

from inspirehep.modules.search.utils import get_facet_configuration


@patch('inspirehep.modules.search.utils.get_facet_configuration')
def test_facet_configuration_with_existing_facet_import_string(facet_mock, isolated_app):
    facet_mock.return_value = {
        'aggs': {
            'jessica-jones': {
                'terms': {
                    'field': 'defenders',
                    'size': 20,
                },
            },
        },
    }
    config = {
        'RECORDS_REST_FACETS': {
            'defenders': 'inspirehep.modules.search.utils:get_facet_configuration'
        },
    }
    expected = {
        'aggs': {
            'jessica-jones': {
                'terms': {
                    'field': 'defenders',
                    'size': 20
                }
            }
        }
    }
    with isolated_app.test_request_context('?facet_name=defenders'):
        with patch.dict(isolated_app.config, config):
            result = get_facet_configuration('records-hep')
            facet_mock.assert_called_once()
            assert expected == result


def test_facet_configuration_with_existing_facet_callable(isolated_app):
    facet_mock = Mock()
    facet_mock.return_value = {
        'aggs': {
            'jessica-jones': {
                'terms': {
                    'field': 'defenders',
                    'size': 20,
                },
            },
        },
    }
    config = {
        'RECORDS_REST_FACETS': {
            'defenders': facet_mock
        },
    }
    expected = {
        'aggs': {
            'jessica-jones': {
                'terms': {
                    'field': 'defenders',
                    'size': 20
                }
            }
        }
    }
    with isolated_app.test_request_context('?facet_name=defenders'):
        with patch.dict(isolated_app.config, config):
            result = get_facet_configuration('records-hep')
            facet_mock.assert_called_once()
            assert expected == result


def test_facet_configuration_with_existing_facet_dict(isolated_app):
    config = {
        'RECORDS_REST_FACETS': {
            'defenders': {
                'aggs': {
                    'jessica-jones': {
                        'terms': {
                            'field': 'defenders',
                            'size': 20,
                        },
                    },
                },
            },
        },
    }
    expected = {
        'aggs': {
            'jessica-jones': {
                'terms': {
                    'field': 'defenders',
                    'size': 20
                }
            }
        }
    }
    with isolated_app.test_request_context('?facet_name=defenders'):
        with patch.dict(isolated_app.config, config):
            result = get_facet_configuration('records-hep')
            assert expected == result


def test_facet_configuration_without_request_facet_name(isolated_app):
    config = {
        'RECORDS_REST_FACETS': {
            'records-hep': {
                'aggs': {
                    'jessica-jones': {
                        'terms': {
                            'field': 'defenders',
                            'size': 20,
                        },
                    },
                },
            },
        },
    }
    expected = {
        'aggs': {
            'jessica-jones': {
                'terms': {
                    'field': 'defenders',
                    'size': 20
                }
            }
        }
    }
    with isolated_app.test_request_context():
        with patch.dict(isolated_app.config, config):
            result = get_facet_configuration('records-hep')
            assert expected == result


def test_facet_configuration_with_fallback_to_default_facet(isolated_app):
    config = {
        'RECORDS_REST_FACETS': {
            'records-hep': {
                'aggs': {
                    'jessica-jones': {
                        'terms': {
                            'field': 'defenders',
                            'size': 20,
                        },
                    },
                },
            },
        },
    }
    expected = {
        'aggs': {
            'jessica-jones': {
                'terms': {
                    'field': 'defenders',
                    'size': 20
                }
            }
        }
    }
    with isolated_app.test_request_context('?facet_name=defenders'):
        with patch.dict(isolated_app.config, config):
            result = get_facet_configuration('records-hep')
            assert expected == result
