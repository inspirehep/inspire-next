{#
## This file is part of INSPIRE.
## Copyright (C) 2014 CERN.
##
## INSPIRE is free software; you can redistribute it and/or
## modify it under the terms of the GNU General Public License as
## published by the Free Software Foundation; either version 2 of the
## License, or (at your option) any later version.
##
## INSPIRE is distributed in the hope that it will be useful, but
## WITHOUT ANY WARRANTY; without even the implied warranty of
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
## General Public License for more details.
##
## You should have received a copy of the GNU General Public License
## along with INSPIRE; if not, write to the Free Software Foundation, Inc.,
## 59 Temple Place, Suite 330, Boston, MA 02111-1307, USA.
#}
{% block details_page %}

{% from "format/record/Holding_Pen_HTML_detailed_macros.tpl" import get_arxiv_id, get_arxiv_category,get_subject, get_title, add_delimiter%}

<div class="container col-md-12">
  <!-- Title Row -->
  <div class="row pull-left col-md-12">
    <h4 id='editable-title' class="">
      <!-- Edit Button -->
        <a href='#' id='edit-title'><i class='fa fa-pencil-square-o'></i></a>
          <!-- Title -->
          {{ get_title(record) }}
        </h4>
    </div>

    <!-- Authors Row-->
    <div class="row">
      <div class="col-md-10">
        <h5><b>
          {% for author in record['authors'] %}
            <span> {{ author['full_name'] }}</span>{{ add_delimiter(loop, '|') }}
          {% endfor %}
        </b></h5>
        </div>
    </div><br>

    <!-- Subjects Row-->
    <div class="row">
      <div class="col-md-11">
        <!-- Edit Button -->
        <a href='#' id='edit-subjects'><i class='fa fa-pencil-square-o'></i></a>
        <!-- Subjects -->
        <span id='editable-subjects'><strong> Subjects:</strong>
        {% for term in record['subject_term'] %}
          {{ get_subject(term) }}
          {{ add_delimiter(loop, ',') }}
        {% endfor %}
        </span>
        </div>
    </div><br>

    <!-- Extra Info Row -->
    <!-- e-Print & pdf -->
    {% if record.report_number %}
    <div class="row">
      <div class="col-md-11">
        <b>e-Print:</b> <a href="http://arxiv.org/abs/arXiv:{{ get_arxiv_id(record)|trim }}">{{ get_arxiv_id(record) }}</a>
        [{{ get_arxiv_category(record) }}]<b> | </b>
        <b><a href="http://arXiv.org/pdf/{{ get_arxiv_id(record) }}.pdf">PDF</a></b>
      </div>
    </div><br>
    {% endif %}

    <!-- Abstract Row-->
    {% if record.abstract %}
    <div class="row">
      <div class="col-md-11">
        <p align="justify"><strong>Abstract: </strong>{{ record['abstract']['summary'] }}</p>
      </div>
    </div>
    {% endif %}

    <!-- Note Row-->
    {% if record.note %}
    <div class="row">
      <i class="col-md-11"><h6><strong>Note: </strong>{{ record['note'][0]['value'] }}</h6></i>
    </div>
    {% endif %}

    <!-- URL Row-->
    {% if record.url %}
      <div class="row">
        <div id='url-container'>
          <div class="col-md-11">
            <!-- Edit Button -->
            <a href='#' id='edit-urls'><i class='fa fa-pencil-square-o'></i></a>
            <!-- URLs -->
            <span id='editable-urls'><small><strong>URL(s): </strong></small></span>
            <span id="url-links">
            {% for url_obj in record['url'] %}
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