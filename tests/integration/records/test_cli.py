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

from inspirehep.modules.records.cli import check


def test_check_unlinked_references_generate_files(app_cli_runner, isolated_app, tmpdir):
    doi_fd = tmpdir.join('doi_file')
    arxiv_fd = tmpdir.join('arxiv_file')
    result = app_cli_runner.invoke(check, ['unlinked_references', str(doi_fd), str(arxiv_fd)])
    doi_fd_content = doi_fd.readlines(cr=False)
    arxiv_fd_content = arxiv_fd.readlines(cr=False)

    assert result.exit_code == 0

    result = doi_fd_content[0]
    expected = '10.1103/PhysRevLett.13.321: (3, 0)'

    assert result == expected

    result = arxiv_fd_content[0]
    expected = '1207.7214: (4, 0)'

    assert result == expected

    result = len(doi_fd_content)
    expected = 225

    assert result == expected

    result = len(arxiv_fd_content)
    expected = 764

    assert result == expected


def test_check_unlinked_references_works_without_arguments(app_cli_runner, isolated_app, tmpdir):
    result = app_cli_runner.invoke(check, ['unlinked_references'])

    assert result.exit_code == 0
