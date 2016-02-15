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

{% extends "inspirehep_theme/format/record/Default_HTML_detailed.tpl" %}

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
  <div class="row">
    <div class="col-md-12">
      <h4 class="pull-left">
        <b>
          {{ record['position'] }}
        </b>
        {% if record['institution'][0]['name']%}
          {% if record['continent'] %}
            (<a href="/search?p=department_acronym:{{ record['institution'][0]['name'] }}&cc=Institutions">{{ record['institution'][0]['name'] }}</a> - {{ record['continent'] }})
          {% else %}
            (<a href="/search?p=department_acronym:{{ record['institution'][0]['name'] }}&cc=Institutions">{{ record['institution'][0]['name'] }}</a>)
        {% endif %}
        {% endif%}
      </h4>
    </div>
  </div>
  <div class="row"><div class="col-md-12"><p></p></div></div>
  {% if 'rank' in record and record['rank'][0] %}
  <div class="row">
    <div class="col-md-12">
     <div class="pull-left">
        {{ record['rank'][0] }}
      </div>
    </div>
  </div>
  {% endif %}
  <div class="row"><div class="col-md-12"><p></p></div></div>
  {% if record['research_area'] %}
  <div class="row">
    <div class="col-md-12">
     <div class="pull-left">
      <label>Field of interest: </label><span>{% if record['research_area']|is_list %}
            {{ record['research_area']|join(', ') }}
          {% endif %}</span>
      </div>
    </div>
  </div>
  {% endif %}
  <div class="row"><div class="col-md-12"><p></p></div></div>
  {% if record['experiments'] %}
  <div class="row">
    <div class="col-md-12">
     <div class="pull-left">
      <label>Experiment: </label>{{ record['experiments']|join(', ') }}
      </div>
    </div>
  </div>
  {% endif %}
  {% if record['deadline_date'] %}
  <div class="row">
    <div class="col-md-12">
     <div class="pull-left">
      <label>Deadline: </label><span> {{record['deadline_date']}}</span>
      </div>
    </div>
  </div>
  {% endif %}
  {% if record['continent'] %}
  <div class="row">
    <div class="col-md-12">
     <div class="pull-left">
      <label>Region: </label><span> {{record['continent']}}</span>
      </div>
    </div>
  </div>
  {% endif %}
  {% if record['description'] %}
  <div class="row">
    <div class="col-md-12">
      <label class="pull-left">Job description: </label>
    </div>
  </div>
  <div class="row">
    <div class="col-md-12">
      <div style="text-align:left;"> {{record['description']}}</div>
    </div>
  </div>
  {% endif %}
  <div class="row"><div class="col-md-12"><p></p></div></div>
  {% if record['contact_person'] and record['contact_person'][0] != None  %}
  <div class="row">
    <div class="col-md-12">
     <div class="pull-left">
      <label>Contact: </label><span> {{ record['contact_person']|join(', ') }}</span>
      </div>
    </div>
  </div>
  {% endif %}
  {% if record['contact_email'] %}
  <div class="row">
    <div class="col-md-12">
     <div class="pull-left">
      <label>Email: </label><span> {{ record['contact_email']|email_links|join_array(", ")|new_line_after}}</span>
      </div>
    </div>
  </div>
  {% endif %}
  {% if record['urls'] %}
  <div class="row">
    <div class="col-md-12">
     <div class="pull-left">
      <label>More information: </label><a href="{{ record['urls'][0] }}"> {{ record['urls'][0] }}</a>
      </div>
    </div>
  </div>
  {% endif %}
  {% if record['reference_email']  and record['reference_email'][0] != None %}
  <div class="row">
    <div class="col-md-12">
     <div class="pull-left">
      <label>Letters of Reference should be sent to: </label><a href=""> {{ record['reference_email']|email_links|join_array(", ")|new_line_after }}</a>
      </div>
    </div>
  </div>
  {% endif %}
  <div class="row"><div class="col-md-12"><p></p></div></div>
  <div class="row"><div class="col-md-12"><p></p></div></div>
  <div class="row">
    <div class="col-md-12">
     <div class="pull-left">
      <label>To remove this listing: </label><a href="mailto:jobs@inspirehep.net?subject=Remove-listing-{% if record['acquisition_source'] %}{{ record['acquisition_source'][0]['submission_number']}} {% endif %}&body=Please remove listing {% if record['acquisition_source'] %}{{ record['acquisition_source'][0]['submission_number']}} {% endif %} https://inspirehep.net/record/{{ record['control_number'] }}/edit"> Click here</a>
      </div>
    </div>
  </div>
{% endblock %}
{% block details %}
{% endblock %}
