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

{% from "format/record/Inspire_Default_HTML_general_macros.tpl" import record_abstract with context %}
{% from "records/Inspire_Default_HTML_detailed_macros.tpl" import search_current_collection with context %}

{% macro record_collection_heading() %}
  <span id="search-title">Search literature &#62;</span>
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
  {% if record.get('arxiv_eprints') %}
    {% if record.get('arxiv_eprints') | is_list() %}
      {% set filtered_arxiv = record.get('arxiv_eprints') %}
      {% for report_number in filtered_arxiv %}
        <a class="btn custom-btn btn-warning pdf-btn" href="http://arxiv.org/pdf/{{ report_number.get('value') | sanitize_arxiv_pdf }}" role="button" title="View PDF"><i class="fa fa-eye"></i> View PDF</a>
      {% endfor %}
    {% endif %}
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
    {% if record.get('dois') | is_list %}
      {% set filtered_doi = record.get('dois.value') | remove_duplicates %}
      {% for doi in filtered_doi %}
        {% if not doi | has_space %}
          <span class="text-left"><b>DOI </b></span><a href="http://dx.doi.org/{{ doi | trim | safe}}" title="DOI">{{ doi }}</a>
        {% endif %}
      {% endfor %}
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
      {% set keywords_number = [] %}
        {% for keywords in record.get('thesaurus_terms') %}
          {% if (loop.index < 15) %}
            {% if 'keyword' in keywords.keys() %}
              <small>
                <a href='/search?p=keyword:{{ keywords.get('keyword') }}'>{{ keywords.get('keyword') }}</a>
              </small>
            {% endif %}

            {% if loop.first %}
              {% do keywords_number.append(loop.length) %}
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
          <small>
            Show all
            {% if keywords_number %}
              {{ keywords_number[0] }}
            {% endif %}
          </small>
        </a>
        <div class="modal fade" id="keywordsFull" tabindex="-1" role="dialog" aria-labelledby="keywordsFull" aria-hidden="true">
          <div class="modal-dialog">
            <div class="modal-content">
              <div class="modal-header">
                <button type="button" class="close" data-dismiss="modal" aria-label="Close"><span aria-hidden="true">&times;</span></button>
                <h4 class="modal-title" id="keywordsFull">Full list of keywords</h4>
              </div>
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
  {% if record.get('urls') %}
    {% for url in record.get('urls') %}
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
          <input type="text" placeholder=" &#xf002;  Filter" value="">
        </form>
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
      <a class="btn btn-default pull-right" href="/search?p=citedby:{{record['control_number']}}&cc=HEP" data-toggle="modal">View in Search Results</a>
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
      <a class="btn btn-default pull-right" href="/search?p=refersto:{{record['control_number']}}&cc=HEP" data-toggle="modal">View in Search Results</a>
    </div>
  </div>
{% endmacro %}

{% macro record_plots() %}
  {% if record.get('urls') %}
    {% set plots_counter = [] %}
    {% for url in record.get('urls') %}
      {% if url.get('url').endswith(".png") or url.get('url').endswith(".jpg") %}
          {% do plots_counter.append(1) %}
      {% endif %}
    {% endfor %}
  {% endif %}

{% if plots_counter %}
  <div id="record-plots">
    <div id="record-plots-title">Plots ({{ plots_counter | length }})</div>
    <!-- Slider -->
    <div class="row">
      <div class="col-xs-12" id="slider">
        <!-- Top part of the slider -->
        <div class="row">
          <div class="col-sm-8" id="carousel-bounding-box">
            <div class="carousel slide" id="plotsCarousel">
              <!-- Carousel items -->
              <div class="carousel-inner">
                {% for url in record.get('urls') if url.get('url').endswith(".png") or url.get('url').endswith(".jpg") %}
                  <div class="{% if loop.index == 1 %} active {% endif %} item"
                       data-slide-number="{{ loop.index0 }}">
                    <img src="{{ url.get('url') }}">
                  </div>
                {% endfor %}
              </div><!-- Carousel nav -->
              <a class="left carousel-control" href="#plotsCarousel" role="button" data-slide="prev">
                <span class="glyphicon glyphicon-chevron-left"></span>
              </a>
              <a class="right carousel-control" href="#plotsCarousel" role="button" data-slide="next">
                <span class="glyphicon glyphicon-chevron-right"></span>
              </a>                                
            </div>
          </div>

          <div class="col-sm-4" id="carousel-text"></div>

          <div id="slide-content" style="display: none;">
            {% for url in record.get('urls') if url.get('url').endswith(".png") or url.get('url').endswith(".jpg") %}
              <div id="slide-content-{{ loop.index0 }}">
                <span>{{ url.get('description') }}</span>
              </div>
            {% endfor %}
          </div>
        </div>
      </div>
    </div><!--/Slider-->

    <div class="row hidden-xs" id="slider-thumbs">
      <!-- Bottom switcher of slider -->
      <ul class="hide-bullets">
        {% for url in record.get('urls') if url.get('url').endswith(".png") or url.get('url').endswith(".jpg") %}
          <li class="col-sm-2 show-plots-thumbnails">
            <a class="thumbnail" id="carousel-selector-{{ loop.index0 }}">
              <img width="100" height="100" src="{{ url.get('url') }}">
            </a>
          </li>
        {% endfor %}
      </ul>                 
    </div>
  </div>
{% endif %}

{% endmacro %}