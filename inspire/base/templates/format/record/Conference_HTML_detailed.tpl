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
{{ record  }}
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
      {% if record['title']|is_list %}
        {% for title in record['title'] %}          
          {{ title|capitalize }}
        {% endfor %}
      {% else %}
        {{ record['title']|capitalize }}
      {% endif %}
      {% if record['acronym'] %}
        ({{ record['acronym'] }}) 
      {% endif %}
      </div>
    </div>
  </div>
  {% if record['subtitle'] %}
  <div class="row">
    <div class="col-md-12">
      <div class="pull-left">
        {{ record['subtitle'] }}
      </div>
    </div>
  </div>
  {% endif %}
  <div class="row">
    <div class="col-md-12">
      <div class="pull-left">
      {{ record|conference_date }}.
      {{ record['place'] }}
      </div>
    </div>
  </div>
  <div class="row">
    <div class="col-md-12">
      <div class="pull-left">
        <label >CNUM:</label> {{ record['cnum'] }}
      </div>
    </div>
  </div>
  {% if record|proceedings_link %}
  <div class="row">
    <div class="col-md-12">
      {{ record|proceedings_link }}<br/>
    </div>
  </div>
  {% endif %}
  <div class="row">
    <div class="col-md-12">
      <a class="pull-left" href="#">Contributions</a>
    </div>
  </div>
  {% if record['url'] %}
    <div class="row">
      <div class="col-md-12">
        <div class="pull-left">
          <label>URL:</label><a href="{{ record['url'][0] }}"> {{ record['url'][0] }}</a>
        </div>
      </div>
    </div>
  {% endif %}
  {% if record['contact_email'] %}
    <div class="row">
      <div class="col-md-12">
        <div class="pull-left">
          <label>Email:</label>{{ record['contact_email']|email_links|join_array(", ")|new_line_after }} 
        </div>
      </div>
    </div>
  {% endif %}
  <div class="row"><div class="col-md-12"><p></p></div></div>
  {% if record['short_description'] %}
    <div class="row">
      <div class="col-md-12">
        <div style="text-align:left;">
          {{ record['short_description'][0]['value'] }}
        </div>
      </div>
    </div>
  {% endif %}
  <div class="row"><div class="col-md-12"><p></p></div></div>
  {% if record['note'] %}
    <div class="row">
      <div class="col-md-12">
        <div style="text-align:left;">
          {{ record['note'][0] }}
        </div>
      </div>
    </div>
  {% endif %}
  <div class="row"><div class="col-md-12"><p></p></div></div>
  {% if record['keywords'] %}
    <div class="row">
      <div class="col-md-12">
        <div style="text-align:left;">
          {{ record['keywords'][0]['value'] }}
        </div>
      </div>
    </div>
  {% endif %}
  <div class="row"><div class="col-md-12"><p></p></div></div>
  {% if record['alternative_titles'] %}
    <div class="row">
      <div class="col-md-12">
        <div style="text-align:left;">
          {{ record['alternative_titles']|join(', ') }}
        </div>
      </div>
    </div>
  {% endif %}
  <div class="row"><div class="col-md-12"><p></p></div></div>
  {% if record['sessions'] %}
    <div class="row">
      <div class="col-md-12">
        <div style="text-align:left;">
          {{ record['sessions']|join(', ') }}
        </div>
      </div>
    </div>
  {% endif %}
  <div class="row"><div class="col-md-12"><p></p></div></div>
  {% if record['extra_place_info'] %}
    <div class="row">
      <div class="col-md-12">
        <div style="text-align:left;">
          <label>Extra place info: </label>{{ record['extra_place_info'][0] }}
        </div>
      </div>
    </div>
  {% endif %}
{% endblock %}
{% block details %}
{% endblock %}