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

{% macro render_doi() %}
    {% set filtered_doi = record.get('dois.value')|remove_duplicates() %}
    DOI: 
    {% for doi in filtered_doi %}
      {% if not loop.first %}
        , 
      {% endif %}
      {% if not doi | has_space() %}
        <a href="http://dx.doi.org/{{ doi |trim()|safe}}" title="DOI" >{{ doi }}</a>
      {% endif %}
    {% endfor %}
{% endmacro %}

{% macro record_journal_info() %}
  {% for pub_info in record.get('publication_info')%}
    {% if pub_info.get('journal_title') and pub_info.get('journal_volume') and  pub_info.get('year') and pub_info.get('page_artid') %}
      {% if loop.first %}
        Published in
      {% endif %}
      {% if not loop.first %}
        and
      {% endif %}
      <i>{{ pub_info.get('journal_title') }}</i> {{ pub_info.get('journal_volume') }} ({{pub_info.get('year')}}) {{ pub_info.get('page_artid') }}
    {% endif %}
  {% endfor %}
{% endmacro %}

{% macro record_journal_info_and_doi() %}
  {% for pub_info in record.get('publication_info')%}
    {% if pub_info.get('journal_title') and pub_info.get('journal_volume') and  pub_info.get('year') and pub_info.get('page_artid') %}
      {% if record.get('dois')| is_list() %}
        {% set filtered_doi = record.get('dois.value')|remove_duplicates() %}
        {% for doi in filtered_doi %}
          {% if not doi|has_space() %}
            {% if loop.first %}
              Published in
            {% endif %}
              <a href="http://dx.doi.org/{{ doi |trim()|safe}}" title="DOI">
                <span class="text-left"><i>{{ pub_info.get('journal_title') }}</i> {{ pub_info.get('journal_volume') }} ({{pub_info.get('year')}}) {{ pub_info.get('page_artid') }}</span>
              </a>
          {% endif %}
        {% endfor %}
      {% endif %}
    {% endif %}
  {% endfor %}
{% endmacro %}
