{#
# This file is part of INSPIRE.
# Copyright (C) 2014, 2015, 2016 CERN.
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
{%- extends "inspirehep_theme/page.html" -%}

{% from "inspirehep_theme/format/record/hep/Inspire_HTML_detailed_macros.tpl" import record_buttons, record_collection_heading, record_collections, record_publication_info, record_doi, record_links, detailed_record_abstract, record_keywords, record_references, record_citations, record_plots with context %}
{% from "inspirehep_theme/format/record/Base_HTML_general_macros.tpl" import mathjax, render_record_title, render_record_authors, record_cite_modal, record_arxiv, record_report_numbers with context %}

{% block body %}
<div id="record_content">
<div class="record-detailed">
  <div class="record-header" id="detailed-header">
    <div class="row">
        {{ record_cite_modal(record) }}
      <div class="col-md-12" id="detailed-header-top">
        <div id="record-title">
          {{ render_record_title(record) }}
        </div>
        <div id="record-authors">
          {{ render_record_authors(record, is_brief=false, number_of_displayed_authors=25) }}
          <span id="record-date">
            - {{ record.get('earliest_date')|format_date }}
          </span>
        </div>
        <div id="record-journal">
          {% if record|publication_info %}
            {{ record_publication_info(record) }}
          {% endif %}
        </div>
        {% if record.get('report_numbers') %}
          <div id="record-report-numbers">
            {{ record_report_numbers(record) }}
          </div>
        {% endif %}
        {% if record.get('dois') or record.get('arxiv_eprints') %}
          <div id="doi-eprint-experiment">
            {% if record.get('dois') %}
              {{ record_doi(record) }}
            {% endif %}
            {% if record.get('arxiv_eprints') %}
              {{ record_arxiv(record, is_brief=false) }}
            {% endif %}
          </div>
        {% endif %}
        {% if record.get('urls') %}
          <div id="external_links">
            {{ record_links(record) }}
          </div>
        {% endif %}
      </div>
      <div class="col-md-12" id="cite-pdf-buttons">
        <div class="btn-group">
          {{ record_buttons(record) }}
        </div>
      </div>
    </div>
  </div>

  <div class="record-details">
    <div id="record-abstract-keywords">
      <div>
        <div class="row">
          <div class="col-xs-12 col-sm-9">
            {{ detailed_record_abstract(record) }}
          </div>
          <div class="clearfix col-sm-3">
            {{ record_keywords(record) }}
          </div>
        </div>
      </div>
    </div>
  </div>
  {{ record_plots(record) }}
  <div class="row">
    <div class="col-md-12">
      {{ record_references(record) }}
    </div>
  </div>
  <div class="row">
    <div class="col-md-12">
      {{ record_citations(record) }}
    </div>
  </div>
  </div>
</div>
</div>

{% endblock body %}