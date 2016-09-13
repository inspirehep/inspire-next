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

from tempfile import TemporaryFile
import zipfile

from sword2 import Connection
from sword2 import http_layer
import httplib2

from settings import HAL_USER, HAL_PASSWORD

COL_IRI = "https://api-preprod.archives-ouvertes.fr/sword/hal"
PREPROD = "https://api-preprod.archives-ouvertes.fr/sword/"


def add_record(tei, document=None):
    c = Connection("", user_name=HAL_USER,
                   user_pass=HAL_PASSWORD,
                   http_impl=HttpLib2Layer_IgnoreCert(".cache"))

    if document:
        tempFile = TemporaryFile()
        with zipfile.ZipFile(tempFile,
                             mode='w',
                             compression=zipfile.ZIP_DEFLATED) as zf:
            zf.writestr('meta.xml', tei)
            zf.writestr('doc.pdf', document)
        tempFile.seek(0)
        payload = tempFile.read()
        mimetype = "application/zip"
        filename = "meta.xml"
    else:
        payload = tei
        mimetype = "text/xml"
        filename = "meta.xml"

    receipt = c.create(col_iri=COL_IRI,
                       payload=payload,
                       mimetype=mimetype,
                       filename=filename,
                       packaging="http://purl.org/net/sword-types/AOfr",
                       in_progress=False)
    return receipt


def update_record(hal_id, tei, document=None):
    c = Connection("", user_name=HAL_USER,
                   user_pass=HAL_PASSWORD,
                   http_impl=HttpLib2Layer_IgnoreCert(".cache"))
    if document:
        tempFile = TemporaryFile()
        with zipfile.ZipFile(tempFile,
                             mode='w',
                             compression=zipfile.ZIP_DEFLATED) as zf:
            zf.writestr('meta.xml', tei)
            zf.writestr('doc.pdf', document)
        tempFile.seek(0)
        payload = tempFile.read()
        mimetype = "application/zip"
        filename = "meta.xml"
    else:
        payload = tei
        mimetype = "text/xml"
        filename = "meta.xml"

    receipt = c.update(edit_iri=PREPROD + hal_id,
                       edit_media_iri=PREPROD + hal_id,
                       payload=payload,
                       mimetype=mimetype,
                       filename=filename,
                       packaging="http://purl.org/net/sword-types/AOfr",
                       in_progress=False)
    return receipt


class HttpLib2Layer_IgnoreCert(http_layer.HttpLib2Layer):
    def __init__(self, cache_dir):
        self.h = httplib2.Http(cache_dir,
                               timeout=30.0,
                               ca_certs=None,
                               disable_ssl_certificate_validation=True)
