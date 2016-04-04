{#
# This file is part of INSPIRE.
# Copyright (C) 2015 CERN.
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

{% macro record_journal_info(record) %}
  {% set pub_info = record|publication_info %}
  {% if pub_info['pub_info'] %}
    {% if pub_info['pub_info']|length == 1 %}
      Published in {{ pub_info['pub_info'][0] }}
    {% else %} 
      Published in {{ pub_info['pub_info']|join(' and ') }}
    {% endif %}
  {% endif %}
  {% if pub_info['conf_info'] %}
    {{ pub_info['conf_info']|safe }}
  {% endif %}
{% endmacro %}

{% macro record_journal_info_and_doi(record) %}
  {% set pub_info = record|publication_info %}
  Published in
  {% set filtered_doi = record.get('dois.value')|remove_duplicates()  %}
  <a href="http://dx.doi.org/{{ filtered_doi[0]|safe }}" title="DOI">
    <span class="text-left">{{ pub_info['pub_info'][0] }}</span>
  </a>
  {% if pub_info['conf_info'] %}
    {{ pub_info['conf_info']|safe }}
  {% endif %}
{% endmacro %}
