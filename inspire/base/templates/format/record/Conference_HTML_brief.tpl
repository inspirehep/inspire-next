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

{% extends "format/record/Default_HTML_brief_base.tpl" %}

{% block record_header %}
<div class="row">
  <div class="col-md-12">
    <div class="panel panel-default custom-panel" >
    <div class="panel-body" >
      <div class="row">
      <div class="col-md-12">
        <h4 class="custom-h">
          <b>
            {% if record['title']|is_list %}
              {% for title in record['title'] %}          
                <a class="title" href="{{ url_for('record.metadata', recid=record['control_number']) }}">
                {{ title|capitalize }}
                </a>
                {% if title|count_words() > 5 %}
                <a class="mobile-title" href="{{ url_for('record.metadata', recid=record['control_number']) }}">
                {{ title|capitalize | words(5) + "..."}}
                </a>
                {% else %}
                 <a class="mobile-title" href="{{ url_for('record.metadata', recid=record['control_number']) }}">
                {{ title|capitalize }}
                {% endif %}
                </a> 
              {% endfor %}
              {% if record['acronym'] %}
                ({{ record['acronym'] }}) 
              {% endif %}
            {% else %}
              <a class="title" href="{{ url_for('record.metadata', recid=record['control_number']) }}">
              {{ record['title']|capitalize }}
              </a>
              {% if record['title']|count_words() > 5 %}
              <a class="mobile-title" href="{{ url_for('record.metadata', recid=record['control_number']) }}">
              {{ record['title']|capitalize | words(5) + "..."}}
              </a>
              {% else %}
               <a class="mobile-title" href="{{ url_for('record.metadata', recid=record['control_number']) }}">
              {{ record['title']|capitalize }} 
              {% endif %}
              </a> 
              {% if record['acronym'] %} 
                ({{ record['acronym'] }}) 
              {% endif %}
            {% endif %}
          </b> 
      </h4>
      <div class="row">
        <div class="col-md-12 record-brief-details">
          {{ record|conference_date }}
          {{ record['place'] }}
        </div>
      </div>
      <div class="row">
        <div class="col-md-12 record-brief-details">
          {{ record['cnum'] }},
          <a href="">Contributions</a> 
        </div>
      </div>
      {% if record['url'] %}
      <div class="row">
        <div class="col-md-12 record-brief-details">
          <a href="{{ record['url'][0] }}">{{ record['url'][0] }}</a>
        </div>
      </div>
      {% endif %}
      </div>
    </div>
  </div>
  </div>
  </div>
</div>
{% endblock %}

