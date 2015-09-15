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

{% block above_record_header %}
{% endblock %}

{% block record_header %}
  <a href="{{ url_for('record.metadata', recid=record['control_number']) }}">
    {{ record['position'] }}
  </a>
  {% if record['deadline_date'] %}
    <strong>[Deadline: {{record['deadline_date']}} ]</strong>
  {% endif %}
{% endblock %}

{% block record_info %}
  {% if record['rank']|is_list %}
    {% for rank in record['rank'] %}
      {{rank}}&nbsp;|&nbsp;
    {% endfor %}
  {% endif %}
  {% if record['research_area']|is_list %}
    {% for research_area in record['research_area'] %}
      {{research_area}}&nbsp;
    {% endfor %}
  {% endif %}
{% endblock %}
