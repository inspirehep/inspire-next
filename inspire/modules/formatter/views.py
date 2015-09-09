# -*- coding: utf-8 -*-
#
# This file is part of INSPIRE.
# Copyright (C) 2014, 2015 CERN.
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

from flask import Blueprint, jsonify, Response

from inspire.utils.bibtex import Bibtex
from inspire.utils.latex import Latex

from invenio_records.api import get_record

from invenio.base.decorators import wash_arguments

from six import text_type

blueprint = Blueprint(
    'inspire_formatter',
    __name__,
    url_prefix='/formatter',
    template_folder='templates',
    static_folder="static",
)


@blueprint.route('/bibtex', methods=['GET', ])
@wash_arguments({'recid': (int, 0)})
def get_bibtex(recid):
    record = get_record(recid)
    bibtex = Bibtex(record).format()
    return jsonify({"result": bibtex, "recid": recid})


@blueprint.route('/latex', methods=['GET', ])
@wash_arguments({'recid': (int, 0),
                 'latex_format': (text_type, "")})
def get_latex(recid, latex_format):
    record = get_record(recid)
    latex = Latex(record, latex_format).format()
    return jsonify({"result": latex, "recid": recid})


@blueprint.route("/download-bibtex/<int:recid>")
def get_bibtex_file(recid):
    record = get_record(recid)
    results = Bibtex(record).format()
    generator = (cell for row in results
                 for cell in row)
    return Response(generator,
                    mimetype="text/plain",
                    headers={"Content-Disposition":
                             "attachment;filename=Bibtex%d.bibtex" % recid})


@blueprint.route("/download-latex/<path:latex_format>/<int:recid>")
def get_latex_file(recid, latex_format):
    record = get_record(recid)
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
