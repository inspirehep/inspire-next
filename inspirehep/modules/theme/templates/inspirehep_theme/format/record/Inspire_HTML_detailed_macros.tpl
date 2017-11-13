{#
# This file is part of INSPIRE.
# Copyright (C) 2015, 2016 CERN.
#
# INSPIRE is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# INSPIRE is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with INSPIRE. If not, see <http://www.gnu.org/licenses/>.
#
# In applying this licence, CERN does not waive the privileges and immunities
# granted to it by virtue of its status as an Intergovernmental Organization
# or submit itself to any jurisdiction.
#}

{% from "inspirehep_theme/format/record/Inspire_Default_HTML_general_macros.tpl" import render_record_title with context %}

{% macro record_buttons(record) %}
  {% if record.get('arxiv_eprints') %}
    {% if record.get('arxiv_eprints') | is_list() %}
      {% set filtered_arxiv = record.get('arxiv_eprints') %}
      {% for report_number in filtered_arxiv %}
        <a class="btn custom-btn btn-warning pdf-btn no-external-icon" href="http://arxiv.org/pdf/{{ report_number.get('value') | sanitize_arxiv_pdf }}" role="button" title="View PDF">View PDF</a>
      {% endfor %}
    {% endif %}
  {% endif %}
  <inspire-export-modal button-template="/static/node_modules/inspirehep-search-js/dist/templates/export/templates/button_single.html" body-template="/static/node_modules/inspirehep-search-js/dist/templates/export/templates/modalbody.html" recid={{record['control_number']}}>
  </inspire-export-modal>
{% endmacro %}

{% macro record_publication_info(record, prepend_text='Published in') %}
  {% set pub_info = record|publication_info %}
  {% if pub_info['pub_info'] %}
    {% if pub_info['pub_info']|length == 1 %}
      {{ prepend_text }} <em>{{ pub_info['pub_info'][0] }}</em>
    {% else %}
      {{ prepend_text }} <em>{{ pub_info['pub_info']|join(' and ') }}</em>
    {% endif %}
  {% endif %}
  {% if pub_info['conf_info'] %}
    {{ pub_info['conf_info']|safe }}
  {% endif %}
{% endmacro %}

{% macro record_experiment(record) %}
   {% set experiments = record.get('accelerator_experiments') %}
   {% set comma = joiner() %}
   {% for experiment in experiments %}
     {{ comma() }}
      <a href="/experiments/{{ experiment.get('recid') }}"> {{ experiment.legacy_name }} </a>
     {% endfor %}
 {% endmacro %}

{% macro record_doi(record) %}
  {% set filtered_doi = record.get('dois') | remove_duplicates_from_list %}
  {% set comma = joiner() %}
  <b>DOI</b>
  {% for value in filtered_doi %}
    {{ comma() }}
    <a href="http://dx.doi.org/{{ value.value | trim | safe}}" title="DOI"> {{ value.value }}</a>
  {% endfor %}
    <br>
{% endmacro %}

{% macro detailed_record_abstract(record) %}
  <div id="record-abstract">
    {{ record_abstract(record) }}
  </div>
{% endmacro %}

{% macro record_abstract(record) %}
  {% set abstract_list = [] %}

  {% if record.get('abstracts') %}
    {% for abstract in record.get('abstracts') %}
      {% if abstract.get('value') %}
        {% if not abstract.get('source') == 'arXiv' %}
          {% do abstract_list.append(abstract.value) %}
        {% elif not abstract_list %}
          {% do abstract_list.append(abstract.value) %}
        {% endif %}
      {% endif %}
    {% endfor %}
  {% endif %}

  {% if abstract_list %}
    {{ abstract_list[0] }}
  {% else %}
    No abstract available for this record.
  {% endif %}

{% endmacro %}

{% macro display_abstract(record, abstract, is_detailed=False) %}
  {% set number_of_sentences = 2 %}
  <div class="abstract">
    <input type="checkbox" class="read-more-state" id="abstract-input-{{ record.get('control_number') }}" />
    <div class="read-more-wrap">
      {{ abstract | words(number_of_sentences, '. ') }}.
      <span class="read-more-target">
        {{ abstract | words_to_end(number_of_sentences, '. ') }}
      </span>
    </div>
    <label for="abstract-input-{{ record.get('control_number') }}" class="read-more-trigger"></label>
  </div>
{% endmacro %}

{% macro record_keywords(record) %}
  <div>
    {% set sep = joiner("; ") %}

    {% if record.keywords %}
      {% for keywords in record.keywords %}
        {% if (loop.index < 11) %}
          {% if 'value' in keywords.keys() %}
            <span class="chip chip-literature">
              <a href='/search?q=keyword:"{{ keywords.get('value') }}"'>{{ keywords.get('value') | trim }}</a>
            </span>
            &nbsp;
          {% endif %}
        {% endif %}
    {% endfor %}

    {% if record.keywords|length > 10 %}
      <div>
        <a href="" class="text-muted" data-toggle="modal" data-target="#keywordsFull">
          <small>
            Show all {{ record.keywords|length }} keywords
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
              {% if record.get('keywords') %}
                {% for keywords in record.get('keywords') %}
                  {% if 'value' in keywords.keys() %}
                    <span class="chip chip-literature">
                      <a href='/search?q=keyword:{{ keywords.get('value') }}'>{{ keywords.get('value') }}</a>
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
  {% set viewInDisplayed = [] %}
  {% set comma = joiner() %}

  {% if record.get('urls') %}
    {% for url in record.get('urls') %}
      {% if url is not none and url.get('value') | is_external_link and url is mapping %}
        {% if url.get('value') != None %}
          {% set actual_url = url.get('value') %}
          {% set isExternalUrl = actual_url | is_external_link %}
          {% if isExternalUrl and not viewInDisplayed %}
            View in
            {% do viewInDisplayed.append(1) %}
          {% endif %}
          {{ comma() }}
          <a href='{{ actual_url }}'>{{ url.get('description', 'Link to fulltext') }}</a>
        {% endif %}
      {% endif %}
    {% endfor %}
  {% endif %}

  {% for system_number in record.external_system_identifiers %}
    {% if not viewInDisplayed and not isExternalUrl %}
      View in
      {% do viewInDisplayed.append(1) %}
    {% endif %}

    {% set ads = 'http://adsabs.harvard.edu/abs/' %}
    {% set cds = 'http://cds.cern.ch/record/' %}
    {% set euclid = 'http://projecteuclid.org/' %}
    {% set hal = 'https://hal.archives-ouvertes.fr/' %}
    {% set kek = 'https://lib-extopc.kek.jp/preprints/PDF/' %}
    {% set msnet = 'http://www.ams.org/mathscinet-getitem?mr=' %}
    {% set zblatt = 'http://www.zentralblatt-math.org/zmath/en/search/?an=' %}
    {% set osti = 'https://www.osti.gov/scitech/biblio/' %}
    {% set adsLinked = [] %}

    {% if (system_number.get('schema') | lower) == 'kekscan' %}
      {{ comma() }}
      {% set extid = system_number.get('value') | replace("-", "") %}
            {% if extid|length == 7 and not extid.startswith('19') and not extid.startswith('20') %}
                {% set year = '19' + extid[:2] + '/' %}
                {% set yymm = extid[:4] + '/' %}
                <a href='{{kek}}{{year}}{{yymm}}{{extid}}.pdf'>
                  KEK scanned document
                </a>
            {% elif extid|length == 9 %}
                {% set year = extid[:4] + '/' %}
                {% set extid = extid[2:] %}
                {% set yymm = extid[:4] + '/' %}
                <a href='{{kek}}{{year}}{{yymm}}{{extid}}.pdf'>
                  KEK scanned document
                </a>
            {% endif %}
    {% elif (system_number.get('schema') | lower) == 'cds' %}
      {{ comma() }}
      <a href='{{ cds }}{{system_number.get('value')}}'>
        CERN Document Server
      </a>
    {% elif (system_number.get('schema') | lower) == 'osti' %}
      {{ comma() }}
      <a href='{{ osti }}{{system_number.get('value')}}'>
        OSTI Information Bridge Server
      </a>
    {% elif (system_number.get('schema') | lower) == 'ads' %}
      {{ comma() }}
      <a href='{{ ads }}{{system_number.get('value')}}'>
        ADS Abstract Service
      </a>
      {% do adsLinked.append(1) %}
    {# HAL: Show only if user is admin - still valid? #}
    {% elif (system_number.get('schema') | lower) == 'hal' %}
      {{ comma() }}
      <a href='{{ hal }}{{system_number.get('value')}}'>
        HAL Archives Ouvertes
      </a>
    {% elif (system_number.get('schema') | lower) == 'msnet' %}
      {{ comma() }}
      <a href='{{ msnet }}{{system_number.get('value')}}'>
        AMS MathSciNet
      </a>
    {% elif (system_number.get('schema') | lower) == 'zblatt' %}
      {{ comma() }}
      <a href='{{ zblatt }}{{system_number.get('value')}}'>
        zbMATH
      </a>
    {% elif (system_number.get('schema') | lower) == 'euclid' %}
      {{ comma() }}
      <a href='{{ euclid }}{{system_number.get('value')}}'>
        Project Euclid
      </a>
    {% endif %}
  {% endfor %}

  {# Fallback ADS link via arXiv:e-print #}
  {% if not adsLinked %}
    {% set ads = 'http://adsabs.harvard.edu/abs/' %}
      {% if record.get('arxiv_eprints') | is_list() %}
        {% if not viewInDisplayed %}
          View in
          {% do viewInDisplayed.append(1) %}
        {% endif %}
        {% set filtered_arxiv = record.get('arxiv_eprints') %}
        {% for report_number in filtered_arxiv %}
          {{ comma() }}
          <a href='{{ ads }}{{report_number.get('value')}}'>
            ADS Abstract Service
          </a>
        {% endfor %}
      {% endif %}
    {% endif %}

{% endmacro %}

{% macro record_references(record) %}
  <div class="panel panel-datatables" id="references">
    <div class="panel-heading">
      <div class="record-detailed-title">References
        ({{ (record.get('references', '')) | count }})
      </div>
    </div>

    <div class="panel-body">
      <div class="datatables-loading">
        <i class="fa fa-spinner fa-spin fa-lg" ></i><br>Loading references...
      </div>
      <div class="datatables-wrapper">
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
  <div class="panel panel-datatables" id="citations">
    <div class="panel-heading">
      <span class="record-detailed-title">Citations
        {% if record.get('citation_count', 0) > 0 %}
          ({{ record.get('citation_count', '')  }})
        {% endif %}
      </span>
    </div>

    <div class="panel-body">
      <div class="datatables-loading">
        <i class="fa fa-spinner fa-spin fa-lg" ></i><br>Loading citations...
      </div>
      <div class="datatables-wrapper">
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
        {% if record.get('citation_count', 0) > 0  %}
          <a class="btn btn-default pull-right" href="/search?q=refersto:{{record['control_number']}}&cc=HEP">
            {% set citation_count = record.get('citation_count', 0) | show_citations_number %}
          </a>
        {% endif %}
      </div>
    </div>
  </div>
{% endmacro %}

{% macro impactgraph() %}
  <div class="panel">
    <div class="panel-heading">
      <span class="record-detailed-title">Publication Impact Graph
      </span>
    </div>

    <div class="panel-body">
      <div class="impact-graph-container">
      </div>
    </div>
  </div>
{% endmacro %}

{% macro record_plots(record) %}
  <div id="record-plots">
    <!-- Slider -->
    <div class="row">
      <div class="col-xs-12" id="slider">
        <!-- Top part of the slider -->
        <div class="row">

          <div class="col-md-2 hidden-sm hidden-xs" id="slider-thumbs">
            <!-- Left switcher of slider -->
            <ul class="hide-bullets">
              {% for url in record.urls if url.value and url.value.endswith(".png") or url.value.endswith(".jpg") %}
                <li class="col-sm-12 show-plots-thumbnails">
                  <a class="thumbnail" id="carousel-selector-{{ loop.index }}">
                    <img width="100" height="100" src="{{ url.value }}">
                  </a>
                </li>
              {% endfor %}
            </ul>
          </div>

          <div class="col-md-7 col-xs-12" id="carousel-bounding-box">
            <div class="carousel slide" id="plotsCarousel" data-interval="false">
              <!-- Carousel items -->
              <div class="carousel-inner">
                {% for url in record.urls if url.value and url.value.endswith(".png") or url.value.endswith(".jpg") %}
                  <div class="item{% if loop.first %} active{% endif %}"data-slide-number="{{ loop.index }}">
                    <img src="{{ url.value }}">
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

          <div class="col-md-3 col-xs-12" id="carousel-text"></div>

          <div id="slide-content" style="display: none;">
            {% for url in record.urls if url.value and url.value.endswith(".png") or url.value.endswith(".jpg") %}
               <div id="slide-content-{{ loop.index }}">
                  <span>{{ url.get('description')|strip_leading_number_plot_caption }}</span>
               </div>
            {% endfor %}
          </div>
        </div>
      </div>
    </div><!--/Slider-->
  </div>
{% endmacro %}
