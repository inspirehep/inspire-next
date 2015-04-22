{#
  # This file is part of Invenio.
  # Copyright (C) 2014 CERN.
  #
  # Invenio is free software; you can redistribute it and/or
  # modify it under the terms of the GNU General Public License as
  # published by the Free Software Foundation; either version 2 of the
  # License, or (at your option) any later version.
  #
  # Invenio is distributed in the hope that it will be useful, but
  # WITHOUT ANY WARRANTY; without even the implied warranty of
  # MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
  # General Public License for more details.
  #
  # You should have received a copy of the GNU General Public License
  # along with Invenio; if not, write to the Free Software Foundation, Inc.,
  # 59 Temple Place, Suite 330, Boston, MA 02111-1307, USA.
  #}

  {% from "format/record/Nick_HTML_brief_macros.tpl" import render_authors, show_citations, render_fulltext_snippets, record_info with context %}

  <div class="record-brief">
    {% block above_record_header %}
    {{ bfe_fulltext(bfo, show_icons="yes", prefix='<ul class="nav nav-pills pull-right" style="margin-top: -10px;"><li class="dropdown"><a class="dropdown-toggle" data-toggle="dropdown" rel="tooltip" title="Download" href="#"><i class="glyphicon glyphicon-download-alt"></i><span class="caret"></span></a>', suffix='</li></ul>', focus_on_main_file="yes") }}
    {% endblock %}
    <h4 class="record-header">
      {% block record_header %}
      <a href="{{ url_for('record.metadata', recid=record['recid']) }}">
        {{ record.get('title.title', '') }}
        {{- record.get('title.volume', '')|prefix(', ') }}
        {{- record.get('title.subtitle', '')|prefix(': ') }}
        {{- record.get('edition_statement', '')|prefix('; ') }}
      </a>
      {% endblock %}

    </h4>

    {% block record_authors %}
    {{ render_authors(4) }}
    {% endblock %}

    <div class="record-content">

      <span class="pull-left record-leftside">
        {% block record_media %}
        {% endblock %}
      </span>

      <p class="record-abstract">
        {% block record_content %}
        {{ record.get('abstract.summary', '')|sentences(3) }}
        {% endblock %}
      </p>

      <p class="record-info">
        {% block record_info %}
        {{ record_info() }}
        {% endblock %}

        {% block show_citations %}
        {{ record.get('_cited_by_count', '') }} citations
        {% endblock %}
      </p>
    </div>

    {% block fulltext_snippets %}
    {{ render_fulltext_snippets() }}
    {% endblock %}
  </div>