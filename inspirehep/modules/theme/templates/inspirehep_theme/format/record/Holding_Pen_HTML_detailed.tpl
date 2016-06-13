{#
# This file is part of INSPIRE.
# Copyright (C) 2014 CERN.
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

{% block details_page %}

  {% from "inspirehep_theme/format/record/Holding_Pen_HTML_detailed_macros.tpl" import record_arxiv_pdf, add_delimiter, get_abstract with context %}
  {% from "inspirehep_theme/format/record/Inspire_HTML_detailed_macros.tpl" import record_publication_info, record_doi, record_keywords with context %}
  {% from "inspirehep_theme/format/record/Inspire_Default_HTML_general_macros.tpl" import render_record_title, mathjax, render_record_authors, record_arxiv with context %}

  <div class="container col-md-12">
    <!-- Title Row -->
    <div class="row col-md-12">
      <h3 id='editable-title' class="">
      <!-- Edit Button -->
        <a href='#' id='edit-title'><i class='fa fa-pencil-square-o'></i></a>
        <!-- Title -->
        <strong>
          <span id='title-text'>
            {{ render_record_title(record) }}
          </span>
        </strong>
      </h3>
    </div>

    <!-- Authors Row-->
    <div class="row">
      <div class="col-md-12">
        {{ render_record_authors(record, is_brief=false, number_of_displayed_authors=25) }}
      </div>
    </div>

    <div class="row hp-horizonal-delimiter"></div>

    <!-- Pubinfo Row-->
    {% if record.publication_info %}
      <div class="row">
        <div class="col-md-12">
          {{ record_publication_info(record) }}
        </div>
      </div>
      <div class="row hp-horizonal-delimiter"></div>
    {% endif %}

    <!-- Subjects Row-->
    {% if record.field_categories %}
    <div class="row">
      <div class="col-md-12">
        <!-- Edit Button -->
        <a href='#' id='edit-subjects'><i class='fa fa-pencil-square-o'></i></a>
        <!-- Subjects -->
        <span id='editable-subjects'><strong> Subjects:</strong>
        {% for term in record['field_categories'] %}
          <span> {{ term['term'] }}</span>
          {{ add_delimiter(loop, ',') }}
        {% endfor %}
        </span>
        </div>
    </div>
    <div class="row hp-horizonal-delimiter"></div>
    {% endif %}

    <!-- Extra Info Row -->
    <!-- e-Print & pdf -->
    {% if record.arxiv_eprints %}
    <div class="row">
      <div class="col-md-12">
        {{ record_arxiv(record, is_brief=False) }}
        {{ record_arxiv_pdf() }}
      </div>
    </div>
    <div class="row hp-horizonal-delimiter"></div>
    {% endif %}

    <!-- dois -->
    {% if record.dois %}
    <div class="row">
      <div class="col-md-12">
        {{ record_doi(record) }}
      </div>
    </div>
    <div class="row hp-horizonal-delimiter"></div>
    {% endif %}

    <!-- Abstract Row-->
    {% if record.abstracts %}
    <div class="row">
      <div class="col-xs-12 col-md-11">
        {{ get_abstract() }}
      </div>
    </div>
    <div class="row hp-horizonal-delimiter"></div>
    {% endif %}

    {% if record.free_keywords %}
    <div class="row">
      <div class="col-sm-3">
        {{ record_keywords(record) }}
      </div>
    </div>
    {% endif %}

    <!-- Note Row -->
    {% if record.public_notes %}
    <div class="row">
      <div class="col-md-12">
        <strong>Note: </strong>
          {{ record['public_notes.value']|join('; ') }}
      </div>
    </div>
    <div class="row hp-horizonal-delimiter"></div>
    {% endif %}
    <!-- URL Row-->
    {% if record.urls %}
      <div class="row">
        <div id='url-container'>
          <div class="col-md-12">
            <!-- Edit Button -->
            <a href='#' id='edit-urls'><i class='fa fa-pencil-square-o'></i></a>
            <!-- URLs -->
            <span id='editable-urls'><small><strong>URL(s): </strong></small></span>
            <span id="url-links">
            {% for url_obj in record['urls'] %}
              <a href="{{ url_obj['url'] }}">{{ url_obj['url'] }}</a>
              {{ add_delimiter(loop, '|') }}
            {% endfor %}
            </span>
          </div>
        </div>
      </div><br>
    {% endif %}
  </div>
{% endblock %}
