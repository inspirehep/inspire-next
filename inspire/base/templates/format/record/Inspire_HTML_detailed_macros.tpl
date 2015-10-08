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

{% from "format/record/Inspire_Default_HTML_general_macros.tpl" import record_cite_modal, record_abstract with context %}

{% macro record_collection_heading() %}
  {% if record.get('collections') %}
    {% set collections = record.collections %}
    {% for collection in collections %}
      {% set collection_name = collection.get('primary') %}
      {% if collection_name == "HEP" %}
        <span id="search-hep">Search Literature &gt;</span>
      {% elif collection_name == "HEPNAMES" %}
        <span id="search-hep">Search Authors &gt;</span>
      {% elif collection_name == "CONFERENCES" %}
        <span id="search-hep">Search Conferences &gt;</span>
      {% elif collection_name == "JOB" %}
        <span id="search-hep">Search Jobs &gt;</span>
      {% endif %}
    {% endfor %}
  {% endif %}
  <span id="title">{{ record_title() }}</span>
{% endmacro %}

{% macro record_title() %}
  {% block title %}
  {% set title_displayed = [] %}
    {% if record['titles'] %}
      {% for title in record['titles'] %}
        {% if title.get('title') and not title.get('source') == 'arXiv' and not title_displayed %}
          {{ title['title']|capitalize }}
          {% do title_displayed.append(1) %}
        {% endif %}
      {% endfor %}
      {% if not title_displayed %}
        {% for title in record['titles'] %}
          {% if title.get('title') and title.get('source') == 'arXiv' and not title_displayed %}
            {{ title['title']|capitalize }}
            {% do title_displayed.append(1) %}
          {% endif %}
        {% endfor %}
      {% endif %}
    {% endif %}
  {% endblock %}
{% endmacro %}

{% macro record_buttons() %}
  <a class="btn btn-default dropdown-toggle dropdown-cite cite-btn" type="button" id="dropdownMenu{{record['control_number']}}" data-recid="{{record['control_number']}}"  data-toggle="modal" data-target="#citeModal{{record['control_number']}}">
    <i class="fa fa-quote-right"></i> Cite this record
  </a>
  {% if record.get('url') %}
    {% set exists = [] %}
    {% for url in record.get('url') %}
      {% if url.get('url').endswith(".pdf") %}
        {% if not exists %}
          {% do exists.append(1) %}  
            <a class="btn custom-btn btn-warning pdf-btn" href="{{ url.get('url') }}" target="_blank" role="button" title="View PDF"><i class="fa fa-eye"></i> View PDF</a>
        {% endif %}
      {% endif %}
    {% endfor %}
  {% endif %}
{% endmacro %}

{% macro record_publication_info() %}
  {% if record.get('publication_info') | is_list %}
      {% for pub_info in record.get('publication_info')%}
        {{ show_publication_info(pub_info) }}
      {% endfor %}
  {% else %}
    {% if record.get('publication_info') %}
      {{ show_publication_info(pub_info) }}
    {% endif %}
  {% endif %}
{% endmacro %}

{% macro show_publication_info(pub_info) %}
  {% if pub_info.get('journal_title') and pub_info.get('journal_volume') and pub_info.get('year') and pub_info.get('page_artid') %}
    <span>{{ pub_info.get('journal_title') }} {{ pub_info.get('journal_volume') }} ({{pub_info.get('year')}}), {{ pub_info.get('page_artid') }}</span>
  {% else %}
    {% if pub_info.get('journal_title') or pub_info.get('journal_volume') or pub_info.get('year') or pub_info.get('page_artid') %}
      <span>
        {% if pub_info.get('journal_title') %}
          {{ pub_info.get('journal_title') }} 
        {% endif %}
        {% if pub_info.get('journal_volume') %}
          {{ pub_info.get('journal_volume') }} 
        {% endif %}
        {% if pub_info.get('year') %}
          {{ pub_info.get('year') }} 
        {% endif %}
        {% if pub_info.get('page_artid') %}
          {{ pub_info.get('page_artid') }} 
        {% endif %}
      </span>
    {% endif %}
  {% endif %}
{% endmacro %}

{% macro record_doi() %}
  {% if record.get('dois') %}
    {% if record.get('dois') %}
      {% for title in record.get('dois') %}
        <span class="text-left"><b>DOI </b></span><a href="http://dx.doi.org/{{ title.value | trim | safe}}" title="DOI">{{ title.value }}</a>
      {% endfor %}
    {% endif %}
  {% endif %}
{% endmacro %}

{% macro detailed_record_abstract() %}
  <div id="record-abstract">
    <div id="record-abstract-title">
      Abstract
    </div>
    {{ record_abstract(is_brief=false) }}
  </div>
{% endmacro %}

{% macro record_keywords() %}
  <div id="record-keywords">
    <div id="record-keywords-title">
      Keywords
    </div>
    {% set sep = joiner("; ") %}

    {% if record.get('thesaurus_terms') %}
      {% set showMore = [] %}
        {% for keywords in record.get('thesaurus_terms') %}
          {% if (loop.index < 15) %}
            {% if 'keyword' in keywords.keys() %}
              <small>
                <a href='/search?p={{ keywords.get('keyword') }}'>{{ keywords.get('keyword') }}</a>
              </small>
            {% endif %}

            {% if not loop.last %}
              ,
            {% endif %}
          {% endif %}
          {% if (loop.index == 15) %}
            {% do showMore.append(1) %} 
          {% endif %}
        {% endfor %}

      {% if showMore %}
        {{ sep() }}
        <a href="" class="text-muted" data-toggle="modal"data-target="#keywordsFull">
          <small>Show all</small>
        </a>
        <div class="modal fade" id="keywordsFull" tabindex="-1" role="dialog" aria-labelledby="keywordsFull" aria-hidden="true">
          <div class="modal-dialog">
            <div class="modal-content">
              <div class="modal-header">Full list of keywords</div>
              <div class="modal-body">
                {% for keywords in record.get('thesaurus_terms') %}
                  {% if 'keyword' in keywords.keys() %}
                  <a href='http://inspirehep.net/search?f=keyword&p="{{ keywords.get('keyword') }}"&ln=en'>{{ keywords.get('keyword') }}</a>,
                  {% endif %}
                {% endfor %}
              </div>
            </div>
          </div>
        </div>
      {% endif %}

    {% else %}
      No keywords available
    {% endif %}
  </div>
{% endmacro%}

{% macro record_links() %}
  {% if record.get('url') %}
    {% for url in record.get('url') %}
      {% if ( (loop.index == 1) and ( (url.get('url').startswith('http://www.adsabs.') or url.get('url').startswith('http://www-public.slac.stanford.edu') ) ) )  %}
        View in
      {% endif %}
      {% if url.get('url').startswith('http://www.adsabs.') %}
        <a href='{{ url.get('url') }}'>ADS</a>
      {% endif %}
      {% if url.get('url').startswith('http://www-public.slac.stanford.edu') %}
        <a href='{{ url.get('url') }}'>SLAC</a>
      {% endif %}
      {% if url.get('url').startswith('http://www.ams.org') %}
        <a href='{{ url.get('url') }}'>AMS MathSciNet</a>
      {% endif %}
      {% if url.get('url').startswith('http://www.zentralblatt-math.org') %}
        <a href='{{ url.get('url') }}'>zbMATH</a>
      {% endif %}
      {% if url.get('url').startswith('http://projecteuclid.org') %}
        <a href='{{ url.get('url') }}'>Project Euclid</a>
      {% endif %}
      {% if url.get('url').startswith('http://www-lib.kek.jp') %}
        <a href='{{ url.get('url') }}'>KEK scanned document</a>
      {% endif %}
      {% if url.get('url').startswith('http://cds.cern.ch/record/') %}
        <a href='{{ url.get('url') }}'>CDS</a>
      {% endif %}
    {% endfor %}
  {% endif %}
{% endmacro %}

{% macro record_references() %}
  <div class="panel" id="references">
    <div class="panel-heading">

      <div id="record-reference-title">References
        ({{ (record.get('references', '')) | count }})
      </div>

      <div id="references-filter">
        <form>
          <input type="text" placeholder=" &#xF002;  Filter" value="">
        </form>

        <div class="btn-group">
          <a type="button" class="btn btn-default dropdown-toggle" data-toggle="dropdown" aria-haspopup="true" aria-expanded="false">
            All Years <span class="caret"></span>
          </a>
          <ul class="dropdown-menu">
            {# <li><a href="#">Year</a></li> #}
          </ul>
        </div>

        <div class="btn-group">
          <a type="button" class="btn btn-default dropdown-toggle" data-toggle="dropdown" aria-haspopup="true" aria-expanded="false">
            All Types <span class="caret"></span>
          </a>
          <ul class="dropdown-menu">
            {# <li><a href="#">Type</a></li> #}
          </ul>
        </div>
      </div>

      <div class="references-citations-table">
        <span class="references-citations-showing">
        Showing {{ (record.get('references', '')) | count }} of {{ (record.get('references', '')) | count }}
        </span>

        <span class="references-citations-cited-by pull-right">
          Cited by
        </span>
      </div>

    </div>

    <div class="panel-body">
      {%  if record.get('references', '') %}
        {{ record | references }}
      {% else %}
        There are no references available for this record
      {% endif %}
    </div>

    <div class="panel-footer">
      <div class="btn-group pull-right">
        <a class="btn btn-default dropdown-toggle" data-toggle="dropdown" aria-haspopup="true" aria-expanded="false">
        Export {{ (record.get('references', '')) | count }} references <span class="caret"></span>
        </a>
        <ul class="dropdown-menu" id="dropdownMenu{{record['control_number']}}" data-recid="{{record['control_number']}}"  data-toggle="modal" data-target="#citeModal{{record['control_number']}}">
          <li><a class="pointer bibtex" id="bibtex{{record['control_number']}}" data-recid="{{record['control_number']}}">BibTex</a></li>
          <li><a class="pointer latex_eu" id="latex_eu{{record['control_number']}}" data-recid="{{record['control_number']}}">LaTex(EU)</a></li>
          <li><a class="pointer latex_us" id="latex_us{{record['control_number']}}" data-recid="{{record['control_number']}}">LaTex(US)</a></li>
        </ul>
      </div>
      <a class="btn btn-default pull-right" href="" data-toggle="modal">View in Search Results</a>
    </div>
  </div>  
{% endmacro %}

{% macro record_citations() %}
  <div class="panel" id="citations">
    <div class="panel-heading">
      <span id="record-reference-title">Citations
        {% if record.get('_cited_by_count', 0) > 0 %}
          ({{ record.get('_cited_by_count', '')  }})
        {% endif %}
      </span>

      <div id="citations-filter">

        <form>
          <input type="text" placeholder=" &#xF002;  Filter" value="">
        </form>

        <div class="btn-group">
          <a type="button" class="btn btn-default dropdown-toggle" data-toggle="dropdown" aria-haspopup="true" aria-expanded="false">
            All Years <span class="caret"></span>
          </a>
          <ul class="dropdown-menu">
            {# <li><a href="#">Year</a></li> #}
          </ul>
        </div>

        <div class="btn-group">
          <a type="button" class="btn btn-default dropdown-toggle" data-toggle="dropdown" aria-haspopup="true" aria-expanded="false">
            All Types <span class="caret"></span>
          </a>
          <ul class="dropdown-menu">
            {# <li><a href="#">Type</a></li> #}
          </ul>
        </div>
      </div>

    </div>

    <div class="panel-footer">
      <div class="btn-group pull-right">
        <a class="btn btn-default dropdown-toggle" data-toggle="dropdown" aria-haspopup="true" aria-expanded="false">
        Export citations <span class="caret"></span>
        </a>
        <ul class="dropdown-menu">
          {# <li><a href="#">Citation type</a></li> #}
        </ul>
      </div>
      <a class="btn btn-default pull-right" href="/search?p=refersto%3Arecid%3A+{{record['control_number']}}&cc=HEP" data-toggle="modal">View in Search Results</a>
    </div>
  </div>
{% endmacro %}