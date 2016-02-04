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


{% from "format/record/Inspire_HTML_detailed_macros.tpl" import record_buttons, record_collection_heading, record_collections, record_publication_info, record_doi, record_links, detailed_record_abstract, record_keywords, record_references, record_citations, record_plots with context %}

{% from "format/record/Inspire_Default_HTML_general_macros.tpl" import mathjax, render_record_title, render_record_authors, record_cite_modal, record_arxiv, record_report_numbers with context %}

<div class="record-detailed">
  <div class="record-header">
    {{ record_cite_modal() }}
    <div id="hep-collection" class="record-collection-heading ellipsis">
      {{ record_collection_heading() }}
    </div>
    <div id="record-title">
      {{ render_record_title() }}
    </div>
    <div id="record-authors">
      {{ render_record_authors(is_brief=false, number_of_displayed_authors=25) }}
    </div>
    <div id="record-year">
      {% if record.get('earliest_date') %}
       {{ record.get('earliest_date').split('-')[0] }}
      {% endif %}
    </div>
    <div class="journal">
    {% if record.get('publication_info') %}
      {{ record_publication_info() }}
    {% endif %}
    </div>
    {% if record.get('report_numbers') %}
      <div class="report-numbers">
        {{ record_report_numbers() }}
      </div>
    {% endif %}
    <div id="doi-eprint-experiment">
      {% if record.get('dois') %}
        {{ record_doi() }}
      {% endif %}
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
  </div>

  <div class="record-details">
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
  </div>
  {{ record_plots() }}
  <div class="row">
    <div class="col-md-12">
      {{ record_references() }}
    </div>
  </div>
  <div class="row">
    <div class="col-md-12">
      {{ record_citations() }}
    </div>
  </div>
  </div>
</div>
