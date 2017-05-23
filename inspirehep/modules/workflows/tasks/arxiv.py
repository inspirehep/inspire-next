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

"""Tasks used in OAI harvesting for arXiv record manipulation."""

from __future__ import absolute_import, division, print_function

import os
import re
from functools import wraps

from flask import current_app
from lxml.etree import XMLSyntaxError
from six import BytesIO
from wand.exceptions import DelegateError
from werkzeug import secure_filename

from dojson.contrib.marc21.utils import create_record

from inspirehep.dojson.hep import hep
from inspirehep.dojson.utils import classify_field
from inspirehep.modules.converter import convert
from inspirehep.utils.record import get_arxiv_categories, get_arxiv_id

from plotextractor.api import process_tarball
from plotextractor.converter import untar
from plotextractor.errors import InvalidTarball, NoTexFilesFound

from ..utils import download_file_to_workflow, with_debug_logging


REGEXP_AUTHLIST = re.compile(
    "<collaborationauthorlist.*?>.*?</collaborationauthorlist>", re.DOTALL)
REGEXP_REFS = re.compile(
    "<record.*?>.*?<controlfield .*?>.*?</controlfield>(.*?)</record>",
    re.DOTALL)


@with_debug_logging
def arxiv_fulltext_download(obj, eng):
    """Perform the fulltext download step for arXiv records.

    :param obj: Workflow Object to process
    :param eng: Workflow Engine processing the object
    """
    arxiv_id = get_arxiv_id(obj.data)
    filename = secure_filename('{0}.pdf'.format(arxiv_id))
    pdf = download_file_to_workflow(
        workflow=obj,
        name=filename,
        url=current_app.config['ARXIV_PDF_URL'].format(arxiv_id=arxiv_id),
    )

    if pdf:
        obj.log.info('PDF retrieved from arXiv for %s', arxiv_id)
    else:
        obj.log.error('Cannot retrieve PDF from arXiv for %s', arxiv_id)


@with_debug_logging
def arxiv_package_download(obj, eng):
    """Perform the package download step for arXiv records.

    :param obj: Workflow Object to process
    :param eng: Workflow Engine processing the object
    """
    arxiv_id = get_arxiv_id(obj.data)
    filename = secure_filename('{0}.tar.gz'.format(arxiv_id))
    tarball = download_file_to_workflow(
        workflow=obj,
        name=filename,
        url=current_app.config['ARXIV_TARBALL_URL'].format(arxiv_id=arxiv_id),
    )

    if tarball:
        obj.log.info('Tarball retrieved from arXiv for %s', arxiv_id)
    else:
        obj.log.error('Cannot retrieve tarball from arXiv for %s', arxiv_id)


@with_debug_logging
def arxiv_plot_extract(obj, eng):
    """Extract plots from an arXiv archive.

    :param obj: Workflow Object to process
    :param eng: Workflow Engine processing the object
    """
    arxiv_id = get_arxiv_id(obj.data)
    filename = secure_filename('{0}.tar.gz'.format(arxiv_id))
    tarball = obj.files[filename]

    if tarball:
        try:
            plots = process_tarball(tarball.file.uri)
        except (InvalidTarball, NoTexFilesFound):
            obj.log.error(
                'Invalid tarball {0}'.format(tarball.file.uri)
            )
            return
        except DelegateError as err:
            obj.log.error('Error extracting plots. Report and skip.')
            current_app.logger.exception(err)
            return

        for idx, plot in enumerate(plots):
            with open(plot['url']) as plot_file:
                obj.files[plot.get('name')] = plot_file
            obj.files[plot.get('name')]['description'] = u'{0:05d} {1}'.format(
                idx, ''.join(plot.get('captions', []))
            )
        obj.log.info('Added {0} plots.'.format(len(plots)))


def arxiv_derive_inspire_categories(obj, eng):
    """Derive ``inspire_categories`` from the arXiv categories.

    Uses side effects to populate the ``inspire_categories`` key
    in ``obj.data`` by converting its arXiv categories.

    Args:
        obj (WorkflowObject): a workflow object.
        eng (WorkflowEngine): a workflow engine.

    Returns:
        None

    """
    obj.data.setdefault('inspire_categories', [])

    for arxiv_category in get_arxiv_categories(obj.data):
        term = classify_field(arxiv_category)
        if term:
            inspire_category = {
                'source': 'arxiv',
                'term': term,
            }

            if inspire_category not in obj.data['inspire_categories']:
                obj.data['inspire_categories'].append(inspire_category)


def arxiv_author_list(stylesheet="authorlist2marcxml.xsl"):
    """Extract authors from any author XML found in the arXiv archive.

    :param obj: Workflow Object to process
    :param eng: Workflow Engine processing the object
    """
    @with_debug_logging
    @wraps(arxiv_author_list)
    def _author_list(obj, eng):
        arxiv_id = get_arxiv_id(obj.data)
        filename = secure_filename('{0}.tar.gz'.format(arxiv_id))
        tarball = obj.files[filename]

        if tarball:
            sub_dir = os.path.abspath('{0}_files'.format(tarball.file.uri))
            try:
                file_list = untar(tarball.file.uri, sub_dir)
            except InvalidTarball:
                obj.log.error('Invalid tarball {0}'.format(tarball.file.uri))
                return
            obj.log.info('Extracted tarball to: {0}'.format(sub_dir))

            xml_files_list = [path for path in file_list
                              if path.endswith('.xml')]
            obj.log.info('Found xmlfiles: {0}'.format(xml_files_list))

            for xml_file in xml_files_list:
                with open(xml_file, 'r') as xml_file_fd:
                    xml_content = xml_file_fd.read()

                match = REGEXP_AUTHLIST.findall(xml_content)
                if match:
                    obj.log.info('Found a match for author extraction')
                    try:
                        authors_xml = convert(xml_content, stylesheet)
                    except XMLSyntaxError:
                        # Probably the %auto-ignore comment exists, so we skip the
                        # first line. See: inspirehep/inspire-next/issues/2195
                        authors_xml = convert(
                            xml_content.split('\n', 1)[1],
                            stylesheet,
                        )
                    authors_rec = create_record(authors_xml)
                    authorlist_record = hep.do(authors_rec)
                    obj.data.update(authorlist_record)
                    break

    return _author_list
