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
import logging
from inspire_utils.name import normalize_name
import os
import re
import itertools
import backoff
import requests
from backports.tempfile import TemporaryDirectory
from flask import current_app
from requests import HTTPError
from wand.exceptions import DelegateError, CoderError, FileOpenError, CacheError
from wand.resource import limits
from werkzeug import secure_filename
from inspire_schemas.builders import LiteratureBuilder
from inspire_schemas.readers import LiteratureReader
from plotextractor.api import process_tarball
from plotextractor.converter import untar
from plotextractor.errors import (
    InvalidTarball,
    NoTexFilesFound,
)
from inspirehep.utils.latex import decode_latex
from inspirehep.utils.url import is_pdf_link, retrieve_uri
from inspirehep.modules.workflows.errors import DownloadError
from inspirehep.modules.workflows.utils import (
    download_file_to_workflow,
    ignore_timeout_error,
    timeout_with_config,
    with_debug_logging, set_mark,
    delete_empty_key
)
# import lxml.html
from parsel import Selector


LOGGER = logging.getLogger(__name__)

REGEXP_AUTHLIST = re.compile(
    "<collaborationauthorlist.*?>.*?</collaborationauthorlist>", re.DOTALL)
REGEXP_REFS = re.compile(
    "<record.*?>.*?<controlfield .*?>.*?</controlfield>(.*?)</record>",
    re.DOTALL)
NO_PDF_ON_ARXIV = 'The author has provided no source to generate PDF, and no PDF.'
TARBALL_EXCEPTIONS = (
    InvalidTarball,
    NoTexFilesFound,
    CoderError,
    FileOpenError,
    UnicodeDecodeError
)


@with_debug_logging
@backoff.on_exception(backoff.expo, DownloadError, base=4, max_tries=5)
def populate_arxiv_document(obj, eng):
    arxiv_id = LiteratureReader(obj.data).arxiv_id

    for conf_name in ('ARXIV_PDF_URL', 'ARXIV_PDF_URL_ALTERNATIVE'):
        url = current_app.config[conf_name].format(arxiv_id=arxiv_id)
        is_valid_pdf_link = is_pdf_link(url)
        if is_valid_pdf_link:
            break
        try:
            if NO_PDF_ON_ARXIV in requests.get(url).content:
                obj.log.info('No PDF is available for %s', arxiv_id)
                return
        except requests.exceptions.RequestException:
            raise DownloadError("Error accessing url {url}".format(url=url))

    if not is_valid_pdf_link:
        raise DownloadError("{url} is not serving a PDF file.".format(url=url))

    filename = secure_filename('{0}.pdf'.format(arxiv_id))
    obj.data['documents'] = [
        document for document in obj.data.get('documents', ())
        if document.get('key') != filename
    ]

    lb = LiteratureBuilder(source='arxiv', record=obj.data)
    lb.add_document(
        filename,
        fulltext=True,
        hidden=True,
        material='preprint',
        original_url=url,
        url=url,
    )

    obj.data = lb.record


@with_debug_logging
def arxiv_package_download(obj, eng):
    """Perform the package download step for arXiv records.

    :param obj: Workflow Object to process
    :param eng: Workflow Engine processing the object
    """
    arxiv_id = LiteratureReader(obj.data).arxiv_id
    filename = secure_filename('{0}.tar.gz'.format(arxiv_id))
    try:
        tarball = download_file_to_workflow(
            workflow=obj,
            name=filename,
            url=current_app.config['ARXIV_TARBALL_URL'].format(arxiv_id=arxiv_id),
        )
    except HTTPError:
        tarball = None
    if tarball:
        obj.log.info('Tarball retrieved from arXiv for %s', arxiv_id)
    else:
        obj.log.error('Cannot retrieve tarball from arXiv for %s', arxiv_id)


@ignore_timeout_error()
@timeout_with_config('WORKFLOWS_PLOTEXTRACT_TIMEOUT')
@with_debug_logging
@backoff.on_exception(backoff.expo, IOError, base=4, max_tries=5)
def arxiv_plot_extract(obj, eng):
    """Extract plots from an arXiv archive.

    :param obj: Workflow Object to process
    :param eng: Workflow Engine processing the object
    """
    # Crude way to set memory limits for wand globally.
    mem_limit = current_app.config.get("WAND_MEMORY_LIMIT")
    if mem_limit and limits['memory'] != mem_limit:
        limits['memory'] = mem_limit
        # This sets disk limit, if not set it will swap data on disk
        # instead of throwing exception
        limits['disk'] = current_app.config.get("WAND_DISK_LIMIT", 0)
        # It will throw an exception when memory and disk limit exceeds.
        # At least workflow status will be saved.

    arxiv_id = LiteratureReader(obj.data).arxiv_id
    filename = secure_filename('{0}.tar.gz'.format(arxiv_id))

    try:
        tarball = obj.files[filename]
    except KeyError:
        LOGGER.info('No file named=%s for arxiv_id %s', filename, arxiv_id)
        return

    with TemporaryDirectory(prefix='plot_extract') as scratch_space, \
            retrieve_uri(tarball.file.uri, outdir=scratch_space) as tarball_file:
        try:
            plots = process_tarball(
                tarball_file,
                output_directory=scratch_space,
            )
        except TARBALL_EXCEPTIONS:
            obj.log.info(
                'Invalid tarball %s for arxiv_id %s',
                tarball.file.uri,
                arxiv_id,
            )
            delete_empty_key(obj, 'figures')
            return
        except DelegateError as err:
            obj.log.error(
                'Error extracting plots for %s. Report and skip.',
                arxiv_id,
            )
            current_app.logger.exception(err)
            delete_empty_key(obj, 'figures')
            return
        except CacheError as err:
            obj.log.error('Cache resources exhausted for %s. Skipping plot extraction',
                          arxiv_id)
            delete_empty_key(obj, 'figures')
            return

        if 'figures' in obj.data:
            for figure in obj.data['figures']:
                if figure['key'] in obj.files:
                    del obj.files[figure['key']]
            del obj.data['figures']

        lb = LiteratureBuilder(source='arxiv', record=obj.data)
        LOGGER.info("Processing plots. Number of plots: %s", len(plots))
        for index, plot in enumerate(plots):
            plot_name = os.path.basename(plot.get('url'))
            key = plot_name
            if plot_name in obj.files.keys:
                key = 'w{number}_{name}'.format(
                    number=index,
                    name=plot_name,
                )
            with open(plot.get('url')) as plot_file:
                obj.files[key] = plot_file

            lb.add_figure(
                key=key,
                caption=''.join(plot.get('captions', [])),
                label=plot.get('label'),
                material='preprint',
                url='/api/files/{bucket}/{key}'.format(
                    bucket=obj.files[key].bucket_id,
                    key=key,
                )
            )

        obj.data = lb.record
    LOGGER.info('Added {0} plots.'.format(len(plots)))
    delete_empty_key(obj, 'figures')


@with_debug_logging
def arxiv_author_list(obj, eng):
    """Extract authors from any author XML found in the arXiv archive.

    :param obj: Workflow Object to process
    :param eng: Workflow Engine processing the object
    """

    arxiv_id = LiteratureReader(obj.data).arxiv_id
    filename = secure_filename('{0}.tar.gz'.format(arxiv_id))
    try:
        tarball = obj.files[filename]
    except KeyError:
        obj.log.info(
            'Skipping author list extraction, no tarball with name "%s" found' % filename
        )
        return

    with TemporaryDirectory(prefix='author_list') as scratch_space, \
            retrieve_uri(tarball.file.uri, outdir=scratch_space) as tarball_file:
        try:
            file_list = untar(tarball_file, scratch_space)
        except InvalidTarball:
            obj.log.info(
                'Invalid tarball %s for arxiv_id %s',
                tarball.file.uri,
                arxiv_id,
            )
            return

        obj.log.info('Extracted tarball to: {0}'.format(scratch_space))
        xml_files_list = [path for path in file_list if path.endswith('.xml')]
        obj.log.info('Found xmlfiles: {0}'.format(xml_files_list))

        extracted_authors = []

        for xml_file in xml_files_list:
            with open(xml_file, 'r') as xml_file_fd:
                xml_content = xml_file_fd.read()
            match = REGEXP_AUTHLIST.findall(xml_content)
            if match:
                obj.log.info('Found a match for author extraction')

                extracted_authors.extend(extract_authors_from_xml(xml_content))

        if extracted_authors:
            for author in extracted_authors:
                author['full_name'] = decode_latex(author['full_name'])

            obj.data['authors'] = extracted_authors

            set_mark(obj, "authors_xml", True)
        else:
            set_mark(obj, "authors_xml", False)


def extract_authors_from_xml(xml_content):
    builder = LiteratureBuilder()
    if isinstance(xml_content, str):
        xml_content = xml_content.decode('utf-8')

    # Probably the %auto-ignore comment exists, so we skip the
    # first line. See: inspirehep/inspire-next/issues/2195
    if "%auto-ignore" in xml_content:
        xml_content = xml_content.split('\n', 1)[1]

    content = Selector(text=xml_content, type="xml")
    content.remove_namespaces()
    undefined_or_none_value_regex = re.compile("undefined|none", re.IGNORECASE)
    undefined_or_empty_inspireid_value_regex = re.compile("undefined|inspire-\s*$", re.IGNORECASE)
    undefined_value_regex = re.compile("undefined", re.IGNORECASE)
    ror_path_value_regex = re.compile("https://ror.org/*")
    remove_new_line_regex = re.compile(u"\s*\n\s*")

    # Goes through all the authors in the file
    for author in content.xpath("//Person"):

        ids = []
        affiliations = []
        affiliations_identifiers = []

        # Gets all the author ids
        for source, id in itertools.izip(author.xpath('./authorIDs/authorID[@source!="" and text()!=""]/@source | ./authorids/authorid[@source!="" and text()!=""]/@source').getall(), author.xpath('./authorIDs/authorID[@source!="" and text()!=""]/text() | ./authorids/authorid[@source!="" and text()!=""]/text()').getall()):
            source = re.sub(remove_new_line_regex, '', source)
            id = re.sub(remove_new_line_regex, '', id)
            if not re.match(undefined_value_regex, source) and not re.match(undefined_or_empty_inspireid_value_regex, id):
                if source == u'CCID':
                    ids.append(['CERN', id])
                elif source == u'INSPIRE':
                    ids.append(['{} ID'.format(source), id])
                else:
                    ids.append([source, id])

        # Gets all the names for affiliated organizations using the organization ids from author
        for affiliation in author.xpath("./authorAffiliations/authorAffiliation/@organizationid").getall():
            orgName = content.xpath(u'string(//organizations/Organization[@id="{}"]/orgName[@source="spiresICN" or @source="INSPIRE" and text()!="" ]/text())'.format(affiliation)).get()

            cleaned_org_name = re.sub(remove_new_line_regex, '', orgName)
            if orgName and not re.match(undefined_or_none_value_regex, cleaned_org_name):
                affiliations.append(cleaned_org_name)

            # Gets all the affiliations_identifiers for affiliated organizations using the organization ids from author
            for value, source in itertools.izip(content.xpath(u'//organizations/Organization[@id="{}"]/orgName[@source="ROR" or @source="GRID" and text()!=""]/text()'.format(affiliation)).getall(), content.xpath(u'//organizations/Organization[@id="{}"]/orgName[@source="ROR" or @source="GRID" and text()!=""]/@source'.format(affiliation)).getall()):
                source = re.sub(remove_new_line_regex, '', source)
                value = re.sub(remove_new_line_regex, '', value)
                if re.match(undefined_or_none_value_regex, source) or re.match(undefined_or_none_value_regex, value):
                    continue

                if source == 'ROR' and not re.match(ror_path_value_regex, value):
                    value = 'https://ror.org/{}'.format(value)

                affiliations_identifiers.append([source, value])

        name = u"{}, {}".format(
            author.xpath('.//familyName/text()').get(),
            author.xpath('.//givenName/text()').get(),
        )
        name_suffix = author.xpath('.//authorSuffix/text()').get()
        if name_suffix:
            name += u", {}".format(name_suffix)
        name = normalize_name(name)

        # builds the info to a correct format with litratureBuilder()
        builder.add_author(
            builder.make_author(
                full_name=name,
                affiliations=affiliations,
                ids=ids,
                affiliations_identifiers=affiliations_identifiers
            )
        )

    return builder.record.get('authors', [])
