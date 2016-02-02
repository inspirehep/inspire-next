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
  <div class="row">
    <div class="col-md-12">
      <h4 class="custom-h pull-left">
        <b>
        {% if record['ICN'] %}
          {% if record['ICN']|is_list() %}
            {{record['ICN'][0]}}
            [Future INSPIRE ID:{{record['ICN'][0]}}]  
          {% else %}
            {{ record['ICN'] }}
            [Future INSPIRE ID:{{record['ICN']}}]  
          {% endif %}
        {% endif %}
        </b> 
      </h4>
    </div>
  </div>
  {% if record['institution']|is_list() %}
  <div class="row">
    <div class="col-md-12">
     <span class="pull-left">{{ record['institution'][0] }}</span>
    </div>
  </div>
  {% else %}
  <div class="row">
    <div class="col-md-12">
     <span class="pull-left">{{ record['institution'] }}</span>
    </div>
  </div>
  {% endif %}
  {% if record['department']|is_list() %}
  <div class="row">
    <div class="col-md-12">
     <span class="pull-left">{{ record['department'][0] }}</span>
    </div>
  </div>
  {% else %}
  <div class="row">
    <div class="col-md-12">
     <span class="pull-left">{{ record['department']}}</span>
    </div>
  </div>
  {% endif %}
  <div class="row">
    <div class="col-md-12">
      <span class="pull-left">
      {% if record['address'][0]['address']|is_list %}
        {{ record['address'][0]['address']|join(', ') }},
      {% else %}
        {{ record['address'][0]['address'] }},
      {% endif %}
      {% for country in record['address'] %}
        {% if 'country' in country %}
         {{ country['country']}}
        {% endif %}
      {% endfor %}
      </span>
    </div>
  </div>
  <div class="row"><div class="col-md-12"><p></p></div></div>
  {% if record['urls'] %}
    <div class="row">
      <div class="col-md-12">
        <a class="pull-left" href="{{ record['urls'][0] }}">{{ record['urls'][0] }}</a>
      </div>
    </div>
  {% endif %}
  {% if record['name_variants'] %}
    <div class="row">
      <div class="col-md-12">
      {% set name_var = [] %}
      {% for element in record['name_variants'] %}
        {% if 'source' not in element and 'value' in element %}
          {% do name_var.append(element['value']) %}
        {% endif %} 
      {% endfor %}   
      {% if name_var %}
        <label>Name variants: </label>{{ name_var[0]|join(', ') }}
      {% endif %}
      </div>
    </div>
  {% endif %}
  {% if record['historical_data'] %}
    <div class="row">
      <div class="col-md-12">
        <label>Historical Data: </label>{{ record['historical_data']|join(', ') }}
      </div>
    </div>
  {% endif %}
  {% if record['public_notes'] %}
    <div class="row">
      <div class="col-md-12">
        <label>Notes: </label>{{ record['public_notes']|join(', ') }}
      </div>
    </div>
  {% endif %}
  <div class="row">
    <div class="col-md-12">
      <div class="pull-left">
        <label>Related Institution:</label><span><a href="#"> Related institution</a></span>
      </div>
    </div>
  </div>
  <div class="row">
    <div class="col-md-12">
      <div class="pull-left">
        <label >Parent Institution:</label><span><a href="#"> Parent institution</a></span>
      </div>
    </div>
  </div>
  <div class="row">
    <div class="col-md-12">
      <div class="pull-left">
      {% if record['ICN'] %}
        {% if record['ICN']|is_list() %}
          <span>HEP list of<a href="#"> Ph.D. theses </a> at {{ record['ICN'][0] }}</span>
        {% else %}
          <span>HEP list of<a href="#"> Ph.D. theses </a> at {{ record['ICN'] }}</span>
        {% endif %}
      {% endif %}
      </div>
    </div>
  </div>
  <div class="row">
    <div class="col-md-12">
      <div class="pull-left">
      {% if record['ICN'] %}
        {% if record['ICN']|is_list() %}
          <span>HEPNAMES list of<a href="#"> people</a> at {{ record['ICN'][0] }}</span>
        {% else %}
          <span>HEPNAMES list of<a href="#"> people</a> at {{ record['ICN'] }}</span>
        {% endif %}
      {% endif %}
      </div>
    </div>
  </div>
  <div class="row">
    <div class="col-md-12">
      <div class="pull-left">
      {% if record['ICN'] and record['institution'] %}
        {% if record['ICN']|is_list() %}
          <span>EXPERIMENTS list of<a href="/search?p=affiliation:{{ record['institution'][0] }}&cc=Experiments"> experiments</a> performed <b>at</b> {{ record['ICN'][0] }}</span>
        {% else %}
          <span>EXPERIMENTS list of<a href="/search?p=affiliation:{{ record['institution'] }}&cc=Experiments"> experiments</a> performed <b>at</b> {{ record['ICN'] }}</span>
        {% endif %}
      {% endif %}
      </div>
    </div>
  </div>
{% endblock %}
{% block details %}
{% endblock %}
