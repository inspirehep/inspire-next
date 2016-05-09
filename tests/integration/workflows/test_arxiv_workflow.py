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

"""Tests for arXiv workflows."""

from __future__ import absolute_import, print_function

import os

import mock

import pkg_resources
import pytest



@pytest.fixture
def record_oai_arxiv_plots():
    """Provide record fixture."""
    return pkg_resources.resource_string(
        __name__,
        os.path.join(
            'fixtures',
            'oai_arxiv_record_with_plots.xml'
        )
    )


@pytest.fixture
def record_oai_arxiv_accept():
    """Provide record fixture."""
    return pkg_resources.resource_string(
        __name__,
        os.path.join(
            'fixtures',
            'oai_arxiv_record_to_accept.xml'
        )
    )


@pytest.fixture
def some_record():
    """Provide record fixture."""
    return pkg_resources.resource_string(
        __name__,
        os.path.join(
            'fixtures',
            'some_record.xml'
        )
    )


@pytest.fixture
def arxiv_tarball():
    """Provide file fixture."""
    return pkg_resources.resource_filename(
        __name__,
        os.path.join(
            'fixtures',
            '1407.7587v1'
        )
    )


@pytest.fixture
def arxiv_pdf():
    """Provide file fixture."""
    return pkg_resources.resource_filename(
        __name__,
        os.path.join(
            'fixtures',
            '1407.7587v1.pdf'
        )
    )


@pytest.fixture
def arxiv_tarball_accept():
    """Provide file fixture."""
    return pkg_resources.resource_stream(
        __name__,
        os.path.join(
            'fixtures',
            '1511.01097'
        )
    )


@pytest.fixture
def arxiv_pdf_accept():
    """Provide file fixture."""
    return pkg_resources.resource_stream(
        __name__,
        os.path.join(
            'fixtures',
            '1511.01097v1.pdf'
        )
    )


def fake_download_file(url, *args, **kwargs):
    """Mock download_file func."""
    if url == 'http://arxiv.org/e-print/1407.7587':
        return pkg_resources.resource_filename(
            __name__,
            os.path.join(
                'fixtures',
                '1407.7587v1'
            )
        )
    elif url == 'http://arxiv.org/pdf/1407.7587':
        return pkg_resources.resource_filename(
            __name__,
            os.path.join(
                'fixtures',
                '1407.7587v1.pdf'
            )
        )
    raise Exception("Download file not mocked!")


@mock.patch('inspirehep.utils.arxiv.download_file', side_effect=fake_download_file)
def test_harvesting_arxiv_workflow_rejected(
        mocked, app, record_oai_arxiv_plots):
    """Test a full harvesting workflow."""
    from invenio_workflows import (
        start, WorkflowEngine, ObjectStatus, WorkflowObject
    )
    from dojson.contrib.marc21.utils import create_record
    from invenio_db import db
    from inspirehep.dojson.hep import hep
    from inspirehep.modules.converter.xslt import convert

    # Convert to MARCXML, then dict, then HEP JSON
    record_oai_arxiv_plots_marcxml = convert(
        record_oai_arxiv_plots,
        "oaiarXiv2marcxml.xsl"
    )
    record_marc = create_record(record_oai_arxiv_plots_marcxml)
    record_json = hep.do(record_marc)
    workflow_uuid = None
    with app.app_context():
        workflow_uuid = start('arxiv_ingestion', [record_json])

        eng = WorkflowEngine.from_uuid(workflow_uuid)
        obj = list(eng.objects)[0]

        assert obj.status == ObjectStatus.HALTED
        assert obj.data_type == "hep"

        # Files should have been attached (tarball + pdf)
        assert obj.extra_data["pdf"]
        assert obj.extra_data["tarball"]

        # Some plots/files should have been added to FFTs
        assert obj.data.get('fft')

        # A publication note should have been extracted
        pub_info = obj.data.get('publication_info')
        assert pub_info
        assert pub_info[0]
        assert pub_info[0].get('year') == "2014"
        assert pub_info[0].get('journal_title') == "J. Math. Phys."

        # FIXME A prediction should have been made
        # assert obj.extra_data.get("arxiv_guessing")

        # This record should not have been touched yet
        assert "approved" not in obj.extra_data

        # Now let's resolve it as accepted and continue
        # FIXME Should be accept, but record validation prevents us.
        obj.remove_action()
        obj.extra_data["approved"] = False
        # obj.extra_data["core"] = True
        obj.save()

        db.session.commit()

    with app.app_context():
        eng = WorkflowEngine.from_uuid(workflow_uuid)
        obj = list(eng.objects)[0]
        obj_id = obj.id
        obj.continue_workflow()

        obj = WorkflowObject.query.get(obj_id)
        # It was rejected
        assert obj.status == ObjectStatus.COMPLETED


@pytest.mark.xfail(reason='record updates are busted due to validation issue')
@mock.patch('inspirehep.utils.arxiv.download_file', side_effect=fake_download_file)
def test_harvesting_arxiv_workflow_accepted(
        mocked, db_only_app, record_oai_arxiv_plots):
    """Test a full harvesting workflow."""
    from invenio_workflows import (
        start, WorkflowEngine, ObjectStatus, WorkflowObject
    )
    from dojson.contrib.marc21.utils import create_record
    from invenio_db import db
    from inspirehep.dojson.hep import hep
    from inspirehep.modules.converter.xslt import convert

    # Convert to MARCXML, then dict, then HEP JSON
    record_oai_arxiv_plots_marcxml = convert(
        record_oai_arxiv_plots,
        "oaiarXiv2marcxml.xsl"
    )
    record_marc = create_record(record_oai_arxiv_plots_marcxml)
    record_json = hep.do(record_marc)
    workflow_uuid = None
    with db_only_app.app_context():
        workflow_uuid = start('arxiv_ingestion', [record_json])

        eng = WorkflowEngine.from_uuid(workflow_uuid)
        obj = list(eng.objects)[0]

        assert obj.status == ObjectStatus.HALTED
        assert obj.data_type == "hep"

        # Files should have been attached (tarball + pdf)
        assert obj.extra_data["pdf"]
        assert obj.extra_data["tarball"]

        # Some plots/files should have been added to FFTs
        assert obj.data.get('fft')

        # A publication note should have been extracted
        pub_info = obj.data.get('publication_info')
        assert pub_info
        assert pub_info[0]
        assert pub_info[0].get('year') == "2014"
        assert pub_info[0].get('journal_title') == "J. Math. Phys."

        # FIXME A prediction should have been made
        # assert obj.extra_data.get("arxiv_guessing")

        # This record should not have been touched yet
        assert "approved" not in obj.extra_data

        # Now let's resolve it as accepted and continue
        # FIXME Should be accept, but record validation prevents us.
        obj.remove_action()
        obj.extra_data["approved"] = True
        obj.extra_data["core"] = True
        obj.save()

        db.session.commit()

    with db_only_app.app_context():
        eng = WorkflowEngine.from_uuid(workflow_uuid)
        obj = list(eng.objects)[0]
        obj_id = obj.id
        obj.continue_workflow()

        obj = WorkflowObject.query.get(obj_id)
        # It was accepted
        assert obj.status == ObjectStatus.COMPLETED
