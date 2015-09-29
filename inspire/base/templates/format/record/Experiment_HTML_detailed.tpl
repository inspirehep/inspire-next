{#
## This file is part of INSPIRE.
## Copyright (C) 2015 CERN.
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

{% extends "format/record/Default_HTML_detailed.tpl" %}

{% block header %}
{{ record }}
  <div class="row">
    <div class="col-md-12">
      <h3>
      {% for collection in record['collections'] %}
        {% if 'primary' in collection %}
          <span class="label label-default pull-left {% if not loop.first %} collection-primary {% endif %}">
          {{ collection['primary'] }}</span>
        {% endif %}
      {% endfor %}
      </h3>
    </div>
  </div>
  <div class="row"><div class="col-md-12"><p></p></div></div>
  <div class="row"><div class="col-md-12"><p></p></div></div>
  <div class="row">
    <div class="col-md-12">
     <div class="record-title pull-left">
        {{ record['experiment_name'][0] }}
        {% if record['affiliation'] %}
          ({{ record['affiliation'][0] }})
        {% endif %}
      </div>
    </div>
  </div>
  {% if record['breadcrum_title'] %}
    <div class="row">
      <div class="col-md-12">
        <div class="pull-left">
          {{ record['breadcrum_title'] }}
        </div>
      </div>
    </div>
  {% endif %}
  <div class="row"><div class="col-md-12"><p></p></div></div>
  <div class="row"><div class="col-md-12"><p></p></div></div>
  {% if record['date_started'] %}
  <div class="row">
    <div class="col-md-12">
      <div class="pull-left">
        ({{ record|experiment_date }})
      </div>
    </div>
  </div>
  {% endif %}
  <div class="row"><div class="col-md-12"><p></p></div></div>
  <div class="row"><div class="col-md-12"><p></p></div></div>
  {% if record['spokesperson'] %}
  <div class="row">
    <div class="col-md-12">
      <div class="pull-left">
        <label>Spokesperson:</label><span> {{ record['spokesperson']|join(', ') }}</span>
      </div>
    </div>
  </div>
  {% endif %}
  {% if record['contact_email'] %}
  <div class="row">
    <div class="col-md-12">
      <div class="pull-left">
        <label>Contact email:</label><span> {{ record['contact_email']|email_links|join_array(", ")|new_line_after }} </span>
      </div>
    </div>
  </div>
  {% endif %}
  {% if record['urls'] %}
  <div class="row">
    <div class="col-md-12">
      <div class="pull-left">
        <label>URL:</label><a> {{ record['urls']|join(', ') }}</a>
      </div>
    </div>
  </div>
  {% endif %}
  <div class="row"><div class="col-md-12"><p></p></div></div>
  <div class="row"><div class="col-md-12"><p></p></div></div>
  {% if record['description'] %}
  <div class="row">
    <div class="col-md-12">
      <div style="text-align:left;">
        {{ record['description'][0] }}
      </div>
    </div>
  </div>
  {% endif %}
  <div class="row"><div class="col-md-12"><p></p></div></div>
  <div class="row"><div class="col-md-12"><p></p></div></div>
  <div class="row">
    <div class="col-md-12">
      <a class="pull-left" href="/search?p=experiment:{{ record['experiment_name'][0] }}&cc=HEP">HEP articles associated with {{ record['experiment_name'][0] }}</a>
    </div>
  </div>
  <div class="row">
    <div class="col-md-12">
    <a class="pull-left" href="/search?p=experiment:{{ record['experiment_name'][0] }}&cc=HepNames">Collaboration members in HepNames</a>
    </div>
  </div>
  <div class="row">
    <div class="col-md-12">
      <a class="pull-left" href="#">Citesummary</a>
    </div>
  </div>
  {% if record['related_experiments'] %}
  <div class="row">
    <div class="col-md-12">
      <div  class="pull-left">
        <label>Related Experiments:</label>
        {{ record|experiment_link|join(', ') }}
      </div>
    </div>
  </div>
  {% endif %}
  {% if record['collaboration'] %}
  <div class="row">
    <div class="col-md-12">
      <div  class="pull-left">
        <a href="/search?p=collaboration:{{ record['collaboration'] }}&cc=Hep">{{ record['collaboration'] }}</a>
      </div>
    </div>
  </div>
  {% endif %}
{% endblock %}
{% block details %}
{% endblock %}