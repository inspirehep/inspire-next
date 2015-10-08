{#
# This file is part of INSPIRE.
# Copyright (C) 2014, 2015 CERN.
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
#}

{% extends "format/record/Default_HTML_detailed.tpl" %}

{% from "format/record/Inspire_HTML_detailed_macros.tpl" import record_buttons, record_collection_heading, record_title, record_collections, record_publication_info, record_doi, record_links, detailed_record_abstract, record_keywords, record_references, record_citations with context %}

{% from "format/record/Inspire_Default_HTML_general_macros.tpl" import render_record_authors, record_cite_modal, record_arxiv with context %}

{% block header %}
  {{ record_cite_modal() }}
  <div id="record-collection-heading">
    {{ record_collection_heading() }}
  </div>
  <div id="record-title">
    {{ record_title() }}
  </div>
  <div id="record-authors">
    {{ render_record_authors(is_brief=false) }}
  </div>
  <div class="journal">
    {{ record_publication_info() }}
  </div>
  <div id="doi-eprint-experiment">
    {{ record_doi() }}
    {{ record_arxiv(is_brief=false) }}
  </div>
  <hr/>
  <div id="external_links">  
    {{ record_links() }}
  </div>
  <div class="cite-pdf-buttons">
    <div class="btn-group">
      {{ record_buttons() }}
    </div>
  </div>
{% endblock header %}
{% block details %}
  <div id="record-abstract-keywords">
    <div>
      <div class="row">
        <div class="col-xs-12 col-sm-9">
          {{ detailed_record_abstract() }}
        </div>
        <div class="clearfix col-sm-3">
          {{ record_keywords() }}
        </div>
      </div>
    </div>
  </div>
  <div class="row">
    <div class="col-md-6">
      {{ record_references() }}
    </div>
    <div class="col-md-6">
      {{ record_citations() }}
    </div>
  </div>
{% endblock details %}