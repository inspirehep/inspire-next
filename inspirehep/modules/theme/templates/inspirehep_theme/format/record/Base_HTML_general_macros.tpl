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

{% macro render_record_title(record) %}
  {% if record.titles %}
    {% set title = record.titles[0].title %}
    {% if title | is_upper %}
      {{ title | capitalize }}
    {% else %}
      {{ title }}
    {% endif %}
    {% for subtitle in record['titles.subtitle'] %}
        {% if subtitle | is_upper %}
          : {{ subtitle | capitalize }}
        {% else %}
          : {{ subtitle }}
        {% endif %}
    {% endfor %}
  {% endif %}
{% endmacro%}

{% macro render_author_names(record, author, show_affiliation) %}
  <a{% if author.affiliations|length > 0  and show_affiliation %}
      data-toggle="tooltip"
      data-placement="bottom"
      title="{{ author.get('affiliations')[0]['value'] }}"
    {% endif %}
    href="http://inspirehep.net/author/profile/{{author.full_name}}?recid={{record['control_number']}}" class="no-external-icon">
    {{ author.get('full_name', '') | split_author_name() }}
  </a>
{% endmacro %}

{% macro render_record_authors(record, is_brief, number_of_displayed_authors=10, show_affiliations=true) %}
  {% set collaboration_displayed = false %}
  {% if record.collaboration and not record.get('corporate_author') %}
    {% for collaboration in record.collaboration %}
      {% if collaboration['value'] %}
      <a href="/search?p=collaboration:'{{ collaboration['value'] }}'">{{ collaboration['value'] }}</a>
        {% set collaboration_displayed = true %}
      {% endif %}
      {% if not loop.last %}
        and
      {% endif %}
      {% if loop.last %}
        {% if loop.index == 1%}
          Collaboration
        {% else %}
          Collaborations
        {% endif %}
      {% endif %}
    {% endfor %}
  {% endif %}

  {% if record.authors %}
    {% set sep = joiner("; ") %}
    {% set authors = record.authors %}
    {% if not collaboration_displayed %}
      {% for author in authors[0:number_of_displayed_authors] %}
        {{ sep() }}
        {{ render_author_names(record, author, show_affiliation = True ) }}
      {% endfor %}
    {% endif %}
    {% if (record.authors | length > number_of_displayed_authors) %}
        {% if is_brief %}
          {% if not collaboration_displayed %}
            <i>et al.</i>
          {% else %}
            ({{ render_author_names(record, authors[0], show_affiliation = True) }} <i>et al.</i>)
          {% endif %}
        {% else %}
          - <i><a id="authors-show-more" class="authors-show-more" data-toggle="modal" href="" data-target="#authors_{{ record['control_number'] }}">
            Show {{ record.authors | count }} authors & affiliations
          </a></i>
        {% endif %}
    {% else %}
        {% if not is_brief and show_affiliations %}
          {% set affiliations_exist = false %}
          {% for author in record.authors %}
            {% if author.get('affiliations') %}
              {% set affiliations_exist = true %}
            {% endif %}
          {% endfor %}
        {% endif %}
        {% if affiliations_exist %}
            - <i><a id="authors-show-more" class="authors-show-more" data-toggle="modal" href="" data-target="#authors_{{ record['control_number'] }}">
              Show affiliations
            </a></i>
        {% endif %}
    {% endif %}
    {% if show_affiliations %}
      <div class="modal fade authors-modal" id="authors_{{ record['control_number'] }}" tabindex="-1" role="dialog" aria-labelledby="myModalLabel" aria-hidden="true">
        <div class="modal-dialog">
          <div class="modal-content">
            <div class="modal-header">
              <button type="button" class="close" data-dismiss="modal" aria-label="Close"><span aria-hidden="true">&times;</span></button>
              <h4 class="modal-title" id="myModalLabel">Authors</h4>
            </div>
            <div class="modal-body">
              {% for author in record.authors %}
                {{ render_author_names(record, author) }}
                 {% if author.get('affiliations') and not is_brief %}
                  {% if author.get('affiliations') | is_list %}
                    <a href="{{ url_for('inspirehep_search.search', p='"' + author.get('affiliations')[0].value + '"' + "&cc=Institutions") }}">
                      ({{ author.get('affiliations')[0].value }})
                    </a>
                  {% else %}
                    <a href="{{ url_for('inspirehep_search.search', p='"' + author.get('affiliations').value + '"' + "&cc=Institutions") }}">
                      ({{ author.get('affiliations').value }})
                    </a>
                  {% endif %}
                {% endif %}
                {{ sep() }}
              {% endfor %}
            </div>
            <div class="modal-footer">
            </div>
          </div>
        </div>
      </div>
    {% endif %}
  {% elif record.get('corporate_author') %}
    {{ record.get('corporate_author')|join('; ') }}
  {% endif %}
{% endmacro %}

{% macro record_report_numbers(record) %}
  {% for report_number in record['report_numbers'] %}
    {% if 'value' in report_number %}
      {% if loop.first %}
        Report number:
      {% endif %}
      {{ report_number['value'] }}
      {% if not loop.last %}
        ,
      {% endif %}
    {% endif %}
  {% endfor %}
{% endmacro %}

{% macro record_abstract(record, is_brief) %}
  {% if is_brief %}
    {% set number_of_words = 0 %}
  {% else %}
    {% set number_of_words = 100 %}
  {% endif %}
  {% set abstract_displayed = false %}
  {% set arxiv_abstract = "" %}
  {% if record.get('abstracts') %}
    {% for abstract in record.get('abstracts') %}
      {% if abstract.get('value') and not abstract_displayed %}
        {% if not abstract.get('source') == 'arXiv' %}
          {{ display_abstract(record, abstract.get('value'), number_of_words) }}
          {% set abstract_displayed = true %}
        {% else %}
          {% set arxiv_abstract = abstract.get('value') %}
        {% endif %}
      {% endif %}
    {% endfor %}
      {% if not abstract_displayed and arxiv_abstract %}
        {{ display_abstract(record, arxiv_abstract, number_of_words) }}
        {% set abstract_displayed = true %}
      {% endif %}
  {% endif %}

  {% if not is_brief and not abstract_displayed %}
      No abstract available for this record
  {% endif %}
{% endmacro %}

{% macro display_abstract(record, abstract, number_of_words) %}
  <div class="abstract">
    <input type="checkbox" class="read-more-state" id="abstract-input-{{ record.get('control_number') }}" />
    <div class="read-more-wrap">
      {{ abstract | words(number_of_words)| e }}
      {% if abstract | words_to_end(number_of_words) %}
        {% if number_of_words > 0 %}
          <span class="read-more-ellipsis">...</span>
        {% endif %}
        <span class="read-more-target">
          {{ abstract | words_to_end(number_of_words)| e }}
        </span>
      {% endif %}
    </div>
    {% if abstract | words_to_end(number_of_words) %}
      <label for="abstract-input-{{ record.get('control_number') }}" class="read-more-trigger"></label>
    {% endif %}
  </div>
{% endmacro %}

{% macro record_arxiv(record, is_brief) %}
  {% if record.get('arxiv_eprints') %}
    {% for report_number in record.get('arxiv_eprints') %}
      {% if is_brief %}
        e-Print:<a href="http://arxiv.org/abs/{{ report_number.get('value') }}" > {{ report_number.get('value') }}</a>
        {% if report_number.get('categories') %}
          [{{ report_number.get('categories')[0] }}]
        {% endif %}
      {% else %}
        <span class="eprint">e-Print</span>
        <a href="http://arxiv.org/abs/{{ report_number.get('value') }}" title="arXiv" target="_blank">{{ report_number.get('value') }}</a>
        {% if report_number.get('categories') %}
          [{{ report_number.get('categories')[0] }}]
        {% endif %}
      {% endif %}
    {% endfor %}
  {% endif %}
{% endmacro %}

{% macro record_cite_modal(record) %}
  <!-- MODAL -->
  <div class="modal fade" id="citeModal{{record['control_number']}}" tabindex="-1" role="dialog" aria-labelledby="myModalLabel" aria-hidden="true">
    <div class="modal-dialog cite-modal">
      <div class="modal-content">
        <div class="modal-header">
          <button type="button" class="close" data-dismiss="modal" aria-label="Close"><span aria-hidden="true">&times;</span></button>
          <h4 class="modal-title" id="citeModalLabel">Cite Article</h4>
        </div>
        <div class="modal-body">
          <div class="row">
            <div class="col-md-12">
              <div class="editable" id="singleRecord{{record['control_number']}}" contenteditable="true"><pre id="text{{record['control_number']}}"></pre></div>
            </div>
          </div>
        </div>
        <div class="modal-footer">
        <div class="row">
          <div class="col-md-6 text-left">
            <button class="btn btn-default copy-clp" id="copy-single-record-clipboard{{record['control_number']}}" data-toggle="tooltip" data-placement="bottom" data-clipboard-target="#singleRecord{{record['control_number']}}" data-original-title="Copied!">
              <i class="fa fa-clipboard pointer"></i> Copy to clipboard
            </button>
          </div>
          <div class="col-md-6">
            <div class="btn-group">
              <button type="button" class="btn btn-primary dropdown-toggle" id="btn-drop" data-toggle="dropdown" aria-expanded="false">
                <span id="format{{record['control_number']}}"></span> <span class="caret"></span>
              </button>
              <ul class="dropdown-menu" role="menu">
                <li><a class="pointer bibtex" id="bibtex{{record['control_number']}}" data-recid="{{record['control_number']}}">BibTex</a></li>
                <li><a class="pointer latex_eu" id="latex_eu{{record['control_number']}}" data-recid="{{record['control_number']}}">LaTex(EU)</a></li>
                <li><a class="pointer latex_us" id="latex_us{{record['control_number']}}" data-recid="{{record['control_number']}}">LaTex(US)</a></li>
              </ul>
            </div>
            <a type="button" id="download{{record['control_number']}}" class="btn btn-primary"><i class="fa fa-download"></i> Download</a>
          </div>
        </div>
        </div>
      </div>
    </div>
  </div>
  <!-- END MODAL -->
{% endmacro %}

{% macro mathjax() %}
{% set version = '2.5.3' %}
<script src="//cdnjs.cloudflare.com/ajax/libs/mathjax/{{version}}/MathJax.js?config=TeX-AMS-MML_HTMLorMML"></script>
<script type="text/javascript">
    require([
      "jquery",
      ], function ($) {
          $(document).ready(function () {
            MathJax.Hub.Config({
                tex2jax: {inlineMath: [['$', '$'], ['\\(', '\\)']],
                processEscapes: true},
                showProcessingMessages: false,
                messageStyle: "none"
            });
            MathJax.Hub.Queue(["Typeset", MathJax.Hub]);
          })
      }
    );
</script>
{% endmacro %}
