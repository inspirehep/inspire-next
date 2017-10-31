{#
# This file is part of INSPIRE.
# Copyright (C) 2015, 2016 CERN.
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
#}

{% extends "inspirehep_theme/format/record/Inspire_Default_HTML_detailed.tpl" %}

{% set title=record.title %}

{% block body %}
<ul class="breadcrumb detailed-record-breadcrumb">
<li>
  <span class="fa fa-chevron-left"></span>
  {{ request.headers.get('referer', '')|back_to_search_link("journals") }}
</li>
</ul>
<div id="record_content">
  <div class="record-detailed record-detailed-journals">
      <div class="panel">
      <div class="panel-heading">
        <h1 class="record-detailed-title">
          {{ record.title }}
        </h1>
        {% if record.short_title %}
          <h2 class="record-detailed-subtitle record-detailed-subtitle-experiments">{{ record.short_title }}</h2>
        {% endif %}
      </div>
      <div class="panel-body">
        <div class="row">
          <div class="col-md-12">
            {% if record.publisher %}
              <div class="detailed-record-field">
                <label>Published by:</label>
                  {{ record.publisher }}
                <br>
            </div>
            {% endif %}
            {% if record.urls %}
            <div class="detailed-record-field">
              <label>Journal's website: </label>
              {% for url in record.urls %}
                <a href="{{ url }}">{{ url }}</a><br>
              {% endfor %}
            </div>
            {% endif %}

            {% if record.title_variants %}
              <div class="detailed-record-field">
                <a type="button" class="btn btn-default pull-left" data-toggle="modal" data-target="#showNameVariants">
                  Show name variants
                </a><br>
              </div>
            {% endif %}
            <hr>
            <div>
              {% if record.short_title %}
                <a href="/search?q=journal_title:{{ record.short_title }}&cc=Hep">Articles in HEP</a><br>
              {% endif %}
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</div>

<!-- Modal -->
<div class="modal fade" id="showNameVariants" tabindex="-1" role="dialog" aria-labelledby="myModalLabel">
  <div class="modal-dialog" role="document">
    <div class="modal-content">
      <div class="modal-header">
        <button type="button" class="close" data-dismiss="modal" aria-label="Close"><span aria-hidden="true">&times;</span></button>
        <h4 class="modal-title" id="myModalLabel">Name variants</h4>
      </div>
      <div class="modal-body">
        <div style="text-align:left;">
          {% if record.name_variants %}
            {% for variant in record.name_variants %}
              {{ variant }}<br>
            {% endfor %}
          {% endif %}
        </div>
      </div>
      <div class="modal-footer">
      </div>
    </div>
  </div>
</div>
{% endblock %}
