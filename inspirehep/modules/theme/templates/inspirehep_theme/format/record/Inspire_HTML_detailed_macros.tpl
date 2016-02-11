{#
# This file is part of INSPIRE.
# Copyright (C) 2015, 2016 CERN.
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

{% from "inspirehep_theme/format/record/Inspire_Default_HTML_general_macros.tpl" import render_record_title, record_cite_modal, record_abstract with context %}

{% macro record_collection_heading() %}
  <span id="search-title">Search literature &#62;</span>
  <span id="title">{{ render_record_title() }}</span>
{% endmacro %}

{% macro record_buttons(record) %}
  {% if record.get('arxiv_eprints') %}
    {% if record.get('arxiv_eprints') | is_list() %}
      {% set filtered_arxiv = record.get('arxiv_eprints') %}
      {% for report_number in filtered_arxiv %}
        <a class="btn custom-btn btn-warning pdf-btn no-external-icon" href="http://arxiv.org/pdf/{{ report_number.get('value') | sanitize_arxiv_pdf }}" role="button" title="View PDF">View PDF</a>
      {% endfor %}
    {% endif %}
  {% endif %}
  <a class="btn btn-default dropdown-toggle dropdown-cite cite-btn" type="button" id="dropdownMenu{{record['control_number']}}" data-recid="{{record['control_number']}}"  data-toggle="modal" data-target="#citeModal{{record['control_number']}}">
    <i class="fa fa-quote-right"></i> Cite
  </a>
{% endmacro %}

{% macro record_publication_info(record) %}
  {% set pub_info = record|publication_info %}
  {% if pub_info['pub_info'] %}
    {% if pub_info['pub_info']|length == 1 %}
      Published in <em>{{ pub_info['pub_info'][0] }}</em>
    {% else %}
      Published in <em>{{ pub_info['pub_info']|join(' and ') }}</em>
    {% endif %}
  {% endif %}
  {% if pub_info['conf_info'] %}
    {{ pub_info['conf_info']|safe }}
  {% endif %}
{% endmacro %}

{% macro record_doi(record) %}
    {% set filtered_doi = record.get('dois.value')|remove_duplicates() %}
    <b>DOI </b>
    {% for doi in filtered_doi %}
      {% if not doi | has_space %}
        <a href="http://dx.doi.org/{{ doi | trim | safe}}" title="DOI">{{ doi }}</a>
        {% if not loop.last %}
        ,
        {% endif %}
      {% endif %}
    {% endfor %}
    <br>
{% endmacro %}

{% macro detailed_record_abstract(record) %}
  <div id="record-abstract">
    <div id="record-abstract-title">
      Abstract
    </div>
    {{ record_abstract(record, is_brief=false) }}
  </div>
{% endmacro %}

{% macro record_keywords(record) %}
  <div id="record-keywords">
    <div id="record-keywords-title">
      Keywords
    </div>
    {% set sep = joiner("; ") %}

    {% if record.thesaurus_terms %}
      {% for keywords in record.thesaurus_terms %}
        {% if (loop.index < 10) %}
          {% if 'keyword' in keywords.keys() %}
            <span class="label label-default label-keyword">
              <a href='/search?p=keyword:"{{ keywords.get('keyword') }}"'>{{ keywords.get('keyword') | trim }}</a>
            </span>
            &nbsp;
          {% endif %}
        {% endif %}
    {% endfor %}

    {% if record.free_keywords or record.thesaurus_terms|length > 10 %}
      <div>
        <a href="" class="text-muted" data-toggle="modal" data-target="#keywordsFull">
          <small>
            Show all {{ record.thesaurus_terms|length }} keywords
            {% if record.get('free_keywords') %}
              plus author supplied keywords
            {% endif %}
          </small>
        </a>
      </div>
      <div class="modal fade" id="keywordsFull" tabindex="-1" role="dialog" aria-labelledby="keywordsFull" aria-hidden="true">
        <div class="modal-dialog">
          <div class="modal-content">
            <div class="modal-header">
              <button type="button" class="close" data-dismiss="modal" aria-label="Close"><span aria-hidden="true">&times;</span></button>
              <h4 class="modal-title" id="keywordsFull">Full list of keywords</h4>
            </div>
            <div class="modal-body">
            <h4>INSPIRE keywords</h4>
              {% if record.get('thesaurus_terms') %}
                {% for keywords in record.get('thesaurus_terms') %}
                  {% if 'keyword' in keywords.keys() %}
                    <span class="label label-default label-keyword">
                      <a href='/search?p=keyword:{{ keywords.get('keyword') }}'>{{ keywords.get('keyword') }}</a>
                    </span>
                    &nbsp;
                  {% endif %}
                {% endfor %}
              {% endif %}

              {% if record.get('free_keywords') %}
                <h4>Author supplied keywords</h4>
                {% for keywords in record.get('free_keywords') %}
                  {% if 'value' in keywords.keys() %}
                    <span class="label label-default label-keyword">
                      <a href='/search?p=keyword:{{ keywords.get('value') }}'>{{ keywords.get('value') }}</a>
                    </span>
                    &nbsp;
                  {% endif %}
                {% endfor %}
              {% endif %}
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

{% macro record_links(record) %}
  {% if record.get('urls') %}
    {% for url in record.get('urls') %}
    {% if url.get('url') != None %}
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
     {% endif %}
    {% endfor %}
  {% endif %}
{% endmacro %}

{% macro record_references(record) %}
  <div class="panel" id="references">
    <div class="panel-heading">
      <div id="record-reference-title">References
        ({{ (record.get('references', '')) | count }})
      </div>
    </div>

    <div class="panel-body">
      <div id="record-references-loading">
        <i class="fa fa-spinner fa-spin fa-lg" ></i><br>Loading references...
      </div>
      <div id="record-references-table-wrapper">
        <table id="record-references-table" class="table table-striped table-bordered" cellspacing="0" width="100%">
        <thead>
            <tr>
                <th>Reference</th>
                <th>Citations</th>
            </tr>
        </thead>
        </table>
      </div>
    </div>

    <div class="panel-footer">
      <!-- <div class="btn-group pull-right">
        <a class="btn btn-default dropdown-toggle" data-toggle="dropdown" aria-haspopup="true" aria-expanded="false">
        Export {{ (record.get('references', '')) | count }} references <span class="caret"></span>
        </a>
        <ul class="dropdown-menu" id="dropdownMenu{{record['control_number']}}" data-recid="{{record['control_number']}}"  data-toggle="modal" data-target="#citeModal{{record['control_number']}}">
          <li><a class="pointer bibtex" id="bibtex{{record['control_number']}}" data-recid="{{record['control_number']}}">BibTex</a></li>
          <li><a class="pointer latex_eu" id="latex_eu{{record['control_number']}}" data-recid="{{record['control_number']}}">LaTex(EU)</a></li>
          <li><a class="pointer latex_us" id="latex_us{{record['control_number']}}" data-recid="{{record['control_number']}}">LaTex(US)</a></li>
        </ul>
      </div>
      <a class="btn btn-default pull-right" href="/search?p=citedby:{{record['control_number']}}&cc=HEP" data-toggle="modal">View in Search Results</a> -->
    </div>
  </div>
{% endmacro %}

{% macro record_citations(record) %}
  <div class="panel" id="citations">
    <div class="panel-heading">
      <span id="record-citation-title">Citations
        {% if record.get('citation_count', 0) > 0 %}
          ({{ record.get('citation_count', '')  }})
        {% endif %}
      </span>
    </div>

    <div class="panel-body">
      <div id="record-citations-loading">
        <i class="fa fa-spinner fa-spin fa-lg" ></i><br>Loading citations...
      </div>
      <div id="record-citations-table-wrapper">
        <table id="record-citations-table" class="table table-striped table-bordered" cellspacing="0" width="100%">
        <thead>
            <tr>
                <th>Citation</th>
                <th>Citations</th>
            </tr>
        </thead>
        </table>
      </div>
    </div>
    <div class="panel-footer">
      <div class="btn-group pull-right">
        <!-- <a class="btn btn-default dropdown-toggle" data-toggle="dropdown" aria-haspopup="true" aria-expanded="false">
        Export {{ record.get('citation_count', 0) }} citations <span class="caret"></span>
        </a>
        <ul class="dropdown-menu" id="dropdownMenu{{record['control_number']}}" data-recid="{{record['control_number']}}"  data-toggle="modal" data-target="#citeModal{{record['control_number']}}">
          <li><a class="pointer bibtex" id="bibtex{{record['control_number']}}" data-recid="{{record['control_number']}}">BibTex</a></li>
          <li><a class="pointer latex_eu" id="latex_eu{{record['control_number']}}" data-recid="{{record['control_number']}}">LaTex(EU)</a></li>
          <li><a class="pointer latex_us" id="latex_us{{record['control_number']}}" data-recid="{{record['control_number']}}">LaTex(US)</a></li>
        </ul>
      </div> -->
        <a class="btn btn-default pull-right" href="/search?p=refersto:{{record['control_number']}}&cc=HEP">
            View all {% if record.get('citation_count', 0) > 0  %} {{ record.get('citation_count', '') }} {% endif %} citations
        </a>
      </div>
    </div>
  </div>
{% endmacro %}

{% macro record_plots(record) %}
  {% set plotExists = [] %}
  {% set plotsCount = [0] %}
  {% if record.urls %}
    {% for url in record.get('urls') %}
      {% if url.get('url').endswith(".png") or url.get('url').endswith(".jpg") %}
        {% do plotExists.append(1) %}
        {# increment plotsCount by 1 #}
        {% if plotsCount.append(plotsCount.pop() + 1) %}{% endif %}
      {% endif %}
    {% endfor %}
  {% endif %}

  {% if plotExists %}

    <div id="record-plots">
      <div id="record-plots-title">Plots ({{ plotsCount[0] }})</div>
      <!-- Slider -->
      <div class="row">
        <div class="col-xs-12" id="slider">
          <!-- Top part of the slider -->
          <div class="row">

            <div class="col-md-2 hidden-sm hidden-xs" id="slider-thumbs">
              <!-- Left switcher of slider -->
              <ul class="hide-bullets">
                {% set count = 0 %}
                {% for url in record.get('urls') %}
                  {% if url.get('url') %}
                    {% if url.get('url').endswith(".png") or url.get('url').endswith(".jpg") %}
                      <li class="col-sm-12 show-plots-thumbnails">
                        <a class="thumbnail" id="carousel-selector-{{ count }}">
                          <img width="100" height="100" src="{{ url.get('url') }}">
                        </a>
                      </li>
                      {% set count = count + 1 %}
                    {% endif %}
                  {% endif %}
                {% endfor %}
              </ul>
            </div>

            <div class="col-md-7 col-xs-12" id="carousel-bounding-box">
              <div class="carousel slide" id="plotsCarousel" data-interval="false">
                <!-- Carousel items -->
                <div class="carousel-inner">
                  {% set count = 0 %}
                  {% for url in record.get('urls')  %}
                    {% if url.get('url') %}
                      {% if url.get('url').endswith(".png") or url.get('url').endswith(".jpg") %}
                        <div class=" item {% if count == 0 %} active {% endif %}"
                             data-slide-number="{{ count }}">
                          <img src="{{ url.get('url') }}">
                        </div>
                        {% set count = count + 1 %}
                      {% endif %}
                    {% endif %}
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

            <div class="col-md-3 col-xs-12" id="carousel-text"></div>

            <div id="slide-content" style="display: none;">
              {% set count = 0 %}
              {% for url in record.get('urls') %}
                {% if url.get('url') %}
                  {% if url.get('url').endswith(".png") or url.get('url').endswith(".jpg") %}
                  <div id="slide-content-{{ count }}">
                    <span>{{ url.get('description')|strip_leading_number_plot_caption }}</span>
                  </div>
                  {% set count = count + 1 %}
                  {% endif %}
                {% endif %}
              {% endfor %}
            </div>
          </div>
        </div>
      </div><!--/Slider-->
    </div>
  {% endif %}
{% endmacro %}
