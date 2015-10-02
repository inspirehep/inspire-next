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

{% macro record_info() %}
  {% if record.get('dois')| is_list() %}
    {% set filtered_doi = record.get('dois.value')| remove_duplicates() %}
    {% for doi in filtered_doi %}
    {% if not doi|has_space() %}
      <a href="http://dx.doi.org/{{ doi |trim()|safe}}" title="DOI" >{{ doi }}</a><br/>
    {% endif %}
    {% endfor %}
  {% endif %}
{% endmacro %}

{% macro record_journal_info() %}
  {% if record.get('publication_info')|is_list() %}
    {% for pub_info in record.get('publication_info')%}
      {% if pub_info.get('journal_title') and pub_info.get('journal_volume') and  pub_info.get('year') and pub_info.get('page_artid') %}
      <span class="text-left"><b><i>{{ pub_info.get('journal_title') }}</i> {{ pub_info.get('journal_volume') }} ({{pub_info.get('year')}}), {{ pub_info.get('page_artid') }}</b></span><br/>
      {% endif %}
    {% endfor %}
  {% else %}
    {% if record.get('publication_info').get('journal_title') and record.get('publication_info').get('journal_volume') and  record.get('publication_info').get('year') and record.get('publication_info').get('page_artid') %}
      <span class="text-left"><b><i>{{ record.get('publication_info').get('journal_title') }}</i> {{ record.get('publication_info').get('journal_volume') }} ({{record.get('publication_info').get('year')}}), {{ record.get('publication_info').get('page_artid') }}</b></span><br/>
    {% endif %}
  {% endif %}
{% endmacro %}