# -*- coding: utf-8 -*-
#
# This file is part of INSPIRE.
# Copyright (C) 2016 CERN.
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

import httplib2
from tempfile import TemporaryFile
import zipfile

from sword2 import Connection
from sword2 import http_layer
from sword2.http_layer import HttpLib2Layer

from .config import HAL_USER, HAL_PASSWORD, COL_IRI, EDIT_IRI, IGNORE_CERT


def add_record(tei, doc_file=None):
    """Submit the first version of the record to HAL.

    :param tei: the XML+TEI data describing the record
    :type tei: str
    :param doc_file: the full path to the file to be submitted
    :type doc_file: str
    :return: the connection receipt
    :rtype: sword2.deposit_receipt.Deposit_Receipt
    """
    c, payload, mimetype, filename = _set_up_payload(tei, doc_file)

    receipt = c.create(col_iri=COL_IRI,
                       payload=payload,
                       mimetype=mimetype,
                       filename=filename,
                       packaging="http://purl.org/net/sword-types/AOfr",
                       in_progress=False)
    return receipt


def update_record(hal_id, tei, doc_file=None):
    """Update an existing record on HAL.

    :param hal_id: the HAL id returned in the original submission receipt
    :type hal_id: str
    :param tei: the (updated) XML+TEI data describing the record
    :type tei: str
    :param doc_file: the full path to the (updated) file to be submitted
    :type doc_file: str
    :return: the connection receipt
    :rtype: sword2.deposit_receipt.Deposit_Receipt
    """
    c, payload, mimetype, filename = _set_up_payload(tei, doc_file)

    receipt = c.update(edit_iri=EDIT_IRI + hal_id,
                       edit_media_iri=EDIT_IRI + hal_id,
                       payload=payload,
                       mimetype=mimetype,
                       filename=filename,
                       packaging="http://purl.org/net/sword-types/AOfr",
                       in_progress=False)
    return receipt


def _set_up_payload(tei, doc_file=None, ignore_cert=False):
    c = Connection("",
                   user_name=HAL_USER,
                   user_pass=HAL_PASSWORD,
                   http_impl=(
                       HttpLib2Layer_IgnoreCert(".cache")
                       if IGNORE_CERT
                       else HttpLib2Layer(".cache")
                    )
                   )
    if doc_file:
        tempFile = TemporaryFile()
        with zipfile.ZipFile(tempFile,
                             mode='w',
                             compression=zipfile.ZIP_DEFLATED) as zf:
            zf.writestr('meta.xml', tei)
            zf.write(doc_file, 'doc.pdf')
        tempFile.seek(0)
        payload = tempFile
        mimetype = "application/zip"
        filename = "meta.xml"
    else:
        payload = tei
        mimetype = "text/xml"
        filename = "meta.xml"

    return c, payload, mimetype, filename


class HttpLib2Layer_IgnoreCert(HttpLib2Layer):
    def __init__(self, cache_dir):
        self.h = httplib2.Http(cache_dir,
                               timeout=30.0,
                               ca_certs=None,
                               disable_ssl_certificate_validation=True)
