# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2015, 2016 CERN.
#
# Invenio is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License as
# published by the Free Software Foundation; either version 2 of the
# License, or (at your option) any later version.
#
# Invenio is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Invenio; if not, write to the Free Software Foundation, Inc.,
# 59 Temple Place, Suite 330, Boston, MA 02111-1307, USA.


from flask import flash

from .signals import extra_keywords, malformed_query, unsupported_keyword


@unsupported_keyword.connect
def unsupported_keyword_message(sender, keyword, *args, **kwargs):
    flash(str('<b>' + keyword +
              "</b> keyword is currently unsupported."), "query_suggestion_with_redirect")


@malformed_query.connect
def malformed_query_message(sender):
    flash("Malformed Query. The results may contain unintended results.",
          "query_suggestion")


@extra_keywords.connect
def extra_keywords_message(sender):
    flash("Extra-keyword Query", "query_suggestion")
