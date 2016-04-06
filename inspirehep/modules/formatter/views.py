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

from flask import Blueprint, jsonify, Response, request

from inspirehep.utils.bibtex import Bibtex
from inspirehep.utils.latex import Latex
from inspirehep.utils.cv_latex import Cv_latex
from inspirehep.utils.cv_latex_html_text import Cv_latex_html_text

from invenio_search import current_search_client as es
from invenio_pidstore.models import PersistentIdentifier
from . import config
import itertools

blueprint = Blueprint(
    'inspirehep_formatter',
    __name__,
    url_prefix='/formatter',
    template_folder='templates',
    static_folder="static",
)


@blueprint.route('/bibtex', methods=['GET', ])
def get_bibtex():
    recid = request.values.get('recid', 0, type=int)
    pid = PersistentIdentifier.get('literature', str(recid))
    record = es.get_source(
        index='records-hep', id=str(pid.object_uuid), doc_type='hep')
    bibtex = Bibtex(record).format()
    return jsonify({"result": bibtex, "recid": recid})


@blueprint.route('/latex', methods=['GET', ])
def get_latex():
    recid = request.values.get('recid', 0, type=int)
    pid = PersistentIdentifier.get('literature', str(recid))
    latex_format = request.values.get('latex_format', '', type=unicode)
    record = es.get_source(
        index='records-hep', id=str(pid.object_uuid), doc_type='hep')
    latex = Latex(record, latex_format).format()
    return jsonify({"result": latex, "recid": recid})


@blueprint.route("/download-bibtex/<int:recid>")
def get_bibtex_file(recid):
    pid = PersistentIdentifier.get('literature', str(recid))
    record = es.get_source(
        index='records-hep', id=str(pid.object_uuid), doc_type='hep')
    results = Bibtex(record).format()
    generator = (cell for row in results
                 for cell in row)
    return Response(generator,
                    mimetype="text/plain",
                    headers={"Content-Disposition":
                             "attachment;filename=Bibtex%d.bib" % recid})


@blueprint.route("/download-latex/<path:latex_format>/<int:recid>")
def get_latex_file(recid, latex_format):
    pid = PersistentIdentifier.get('literature', str(recid))
    record = es.get_source(
        index='records-hep', id=str(pid.object_uuid), doc_type='hep')
    results = Latex(record, latex_format).format()
    generator = (cell for row in results
                 for cell in row)
    return Response(
        generator,
        mimetype="text/plain",
        headers={
            "Content-Disposition": "attachment;filename=Latex_{0}{1}.tex".format(
                latex_format, recid
            )
        }
    )


@blueprint.route("/export-as/<path:export_format>",
                 methods=['POST'])
def export_as(export_format):
    """
    Export file according to format
    :param ids: the ids of the records.
    :param export_format: the type of the file the user needs to download.
    :return: the downloaded file.
    """
    ids = request.values.getlist('ids[]')
    if len(ids) > config.FORMATTER_EXPORT_LIMIT:
        ids = ids[:config.FORMATTER_EXPORT_LIMIT]
    out = []
    results = ''
    export_format = export_format.replace('/', '')
    for idx in ids:
        pid = PersistentIdentifier.get('literature', str(idx))
        record = es.get_source(
            index='records-hep', id=str(pid.object_uuid), doc_type='hep')
        if export_format == 'bibtex':
            results = Bibtex(record).format() + '\n' * 2
        elif export_format in ('latex_eu', 'latex_us'):
            results = Latex(record, export_format).format() + '\n'
        elif export_format == 'cv_latex':
            results = Cv_latex(record).format() + '\n'
        elif export_format == 'cv_latex_html':
            results = Cv_latex_html_text(
                record, export_format, '<br/>').format() + '\n'
        elif export_format == 'cv_latex_text':
            results = Cv_latex_html_text(
                record, export_format, '\n').format() + '\n'
        generator = (cell for row in results
                     for cell in row)
        out.append(generator)
    output = itertools.chain()
    for gen in out:
        output = itertools.chain(output, gen)
    return Response(output)
