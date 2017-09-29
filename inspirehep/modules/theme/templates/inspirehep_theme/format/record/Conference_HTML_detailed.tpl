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

{% extends "inspirehep_theme/format/record/Inspire_Default_HTML_detailed.tpl" %}

{% set title=record.title %}

{% block body %}
<ul class="breadcrumb detailed-record-breadcrumb">
<li>
  <span class="fa fa-chevron-left"></span>
  {{ request.headers.get('referer', '')|back_to_search_link("conferences") }}
</li>
</ul>
<div id="record_content">
  <div class="record-detailed record-detailed-conference">
    <div class="record-header record-header-conference">
      <div class="row row-with-map">
        <div class="col-md-8">
          <div class="record-detailed-information">
            <h1 class='record-detailed-title'>
              {{ record['titles'][0]['title'] }}
              {% if record['acronyms'] %}
                ({{ record['acronyms'][0] }})
              {% endif %}
            </h1>

            <h2 class="record-detailed-subtitle">{{ record | conference_date }}</h2>
            {% if record['urls'] %}
              <div class="detailed-record-field">
                <label>Link to the conference website:</label> 
                {% for url in record['urls'] %}
                  <a href="{{ url['value'] }}">{{ url['value'] }}</a>
                  <br>
                {% endfor %}
              </div>
            {% endif %}

            {% if record['contact_details'] %}
              {% if record['contact_details'][0]['name'] %}
              <div class="detailed-record-field">
               <label>Contact person:</label>
                {{record['contact_details'][0]['name']}}
                <br>
              </div>
              {% endif %}
              {% if record['contact_details'][0]['email'] %}
                <div class="detailed-record-field">
                  <label>Contact email:</label>
                  <a href="mailto:{{ record['contact_details'][0]['email'] }}">{{ record['contact_details'][0]['email'] }}</a>
                  <br>
                </div>
              {% endif %}
            {% endif %}
            <hr>

            {% if record['series'] %}
            <div>
              Part of the
              <a href="/search?q=&cc=conferences&series={{ record['series'][0]['name'] }}"> <strong>{{ record['series'][0]['name'] }}</strong>
              </a>
              series
            </div>
            {% endif %}
          </div>

          {% if record.admin_tools %}
            <div class="col-md-12" id="admin-tools">
              {% for tool in record.admin_tools %}
                {% if tool == 'editor' %}
                  <a href="/editor/conferences/{{record.control_number}}"><i class="fa fa-pencil" aria-hidden="true"></i> Edit</a>
                {% endif %}
              {% endfor %}
            </div>
          {% endif %}
        </div>

        <div class="col-md-4 hidden-xs hidden-sm">
          <div class="detailed-map" id="conference-detailed-map"></div>
          <div class='map-address-label map-address-label-conference'> <i class="fa fa-map-marker"></i>
            {{ record['address'][0]['cities'][0] }}, {{ record['address'][0]['country_code'] }}
          </div>
        </div>
      </div>
    </div>

    <div class="row">
      {% if record['keywords'] %}
        {% set details_class = "col-md-8" %}
      {% else %}
        {% set details_class = "col-md-12" %}
      {% endif %}
      <div class="{{details_class}}">
        <div class="panel">
          <div class="panel-heading">Details</div>
          <div class="panel-body">
            <div class="row">
              <div class="col-md-12">
                {% if record['cnum'] %}
                <div class="detailed-record-field">
                  <label title="INSPIRE unique identifier for the conference">CNUM</label>
                  : {{ record['cnum'] }}
                </div>
                {% endif %}

                {% if record['short_description'] %}
                <div class="detailed-record-field">
                  <label class="no-margin-label">Short description:</label>
                  {{ record['short_description']['value'] }}
                </div>
                {% endif %}

                {% if record['note'] %}
                  {{ print_array(record, 'note') }}
                {% endif %}

                {% if record['inspire_categories'] %}
                {% set comma = joiner('&nbsp') %}
                <div class="detailed-record-field">
                  <label>Fields:</label>
                  {% for field in record['inspire_categories'] %}
                      {{ comma() }}
                  <span class="chip chip-conferences">
                    <a href="/search?q=&cc=conferences&q={{ field['term'] }}">{{ field['term'] }}</a>
                  </span>
                  {% endfor %}
                </div>
                {% endif %}
              </div>
            </div>
          </div>
        </div>
      </div>
      {% if record['keywords'] %}
      <div class="col-md-4">
        <div class="panel">
          <div class="panel-heading">Keywords</div>
          <div class="panel-body">
            {% set comma = joiner('&nbsp') %}
            <div class="detailed-record-field detailed-record-field-valigned">
              {% for keyword in record['keywords'] -%}
              {{ comma() }}
              <span class="chip chip-conferences">
                <a href="/search?q=&cc=conferences&q={{ keyword['value'] }}"> <i class="fa fa-tag" style="margin-right: 5px; display: inline;"></i>
                  {{ keyword['value'] }}
                </a>
              </span>
              {%- endfor %}
            </div>
          </div>
        </div>
      </div>
      {% endif %}
    </div>

    <div class="row">
      <div class="col-md-12">
        <div class="panel panel-datatables" id="record-conference-papers">
          <div class="panel-heading">Contributions</div>

          <div class="panel-body">
            <div class="datatables-loading">
              <i class="fa fa-spinner fa-spin fa-lg" ></i>
              <br>Loading contributions to the conference...
            </div>
            <div class="datatables-wrapper">
              <table id="record-conference-papers-table" class="table table-striped table-bordered table-with-ellipsis" cellspacing="0" width="100%">
                <thead>
                  <tr>
                    <th>Title</th>
                    <th>Authors</th>
                    <th>Journal</th>
                    <th># Citations</th>
                  </tr>
                </thead>
              </table>
            </div>
          </div>
        </div>
      </div>
    </div>
    {% if record['series'] %}
    <div class="row">
      <div class="col-md-12">
        <div class="panel panel-datatables" id="record-conference-series">
          <div class="panel-heading">Conferences in the series</div>
          <div class="panel-body">
            <div class="datatables-loading">
              <i class="fa fa-spinner fa-spin fa-lg" ></i>
              <br>Loading conferences...</div>
            <div class="datatables-wrapper">
              <table id="record-conference-series-table" class="table table-striped table-bordered table-with-ellipsis" cellspacing="0" width="100%">
                <thead>
                  <tr>
                    <th>Name</th>
                    <th>Location</th>
                    <th>Contributions</th>
                    <th>Date</th>
                  </tr>
                </thead>
              </table>
            </div>
          </div>
        </div>
      </div>
    </div>
    {% endif %}
  </div>
</div>
{% endblock %}

{% macro print_array(record, field, has_items=false) %}
<div class="detailed-record-field">
  <label>{{ field | capitalize }}:</label>
  {% set comma = joiner() %}
    {% if record[field] %}
      {% for field in record[field] -%}
        {% if has_items -%}
          {{ comma() }} {{ field['value'] }}
        {%- else %}
          {{ comma() }} {{ field }}
        {% endif %}
      {%- endfor %}
    {% endif %}
</div>
{% endmacro %}

{% block additional_javascript %}
<script>
  function initMap() {
    var mapDiv = document.getElementById('conference-detailed-map');
    var doc = {{ record|json_dumps|safe }};
    var address = doc['address'][0]['original_address'];
    var geocoder = new google.maps.Geocoder();

    var map = new google.maps.Map(mapDiv, {
      zoom: 5,
      mapTypeControl: false,
      streetViewControl: false,
      zoomControl: true,
      zoomControlOptions: {
          position: google.maps.ControlPosition.RIGHT_TOP
      },
      // Snazzy Map styling.
      styles: [{
          "featureType": "water",
          "elementType": "geometry",
          "stylers": [{"color": "#e9e9e9"}, {"lightness": 17}]
      }, {
          "featureType": "landscape",
          "elementType": "geometry",
          "stylers": [{"color": "#f5f5f5"}, {"lightness": 20}]
      }, {
          "featureType": "road.highway",
          "elementType": "geometry.fill",
          "stylers": [{"color": "#ffffff"}, {"lightness": 17}]
      }, {
          "featureType": "road.highway",
          "elementType": "geometry.stroke",
          "stylers": [{"color": "#ffffff"}, {"lightness": 29}, {"weight": 0.2}]
      }, {
          "featureType": "road.arterial",
          "elementType": "geometry",
          "stylers": [{"color": "#ffffff"}, {"lightness": 18}]
      }, {
          "featureType": "road.local",
          "elementType": "geometry",
          "stylers": [{"color": "#ffffff"}, {"lightness": 16}]
      }, {
          "featureType": "poi",
          "elementType": "geometry",
          "stylers": [{"color": "#f5f5f5"}, {"lightness": 21}]
      }, {
          "featureType": "poi.park",
          "elementType": "geometry",
          "stylers": [{"color": "#dedede"}, {"lightness": 21}]
      }, {
          "elementType": "labels.text.stroke",
          "stylers": [{"visibility": "on"}, {"color": "#ffffff"}, {"lightness": 16}]
      }, {
          "elementType": "labels.text.fill",
          "stylers": [{"saturation": 36}, {"color": "#333333"}, {"lightness": 40}]
      }, {"elementType": "labels.icon", "stylers": [{"visibility": "off"}]}, {
          "featureType": "transit",
          "elementType": "geometry",
          "stylers": [{"color": "#f2f2f2"}, {"lightness": 19}]
      }, {
          "featureType": "administrative",
          "elementType": "geometry.fill",
          "stylers": [{"color": "#fefefe"}, {"lightness": 20}]
      }, {
          "featureType": "administrative",
          "elementType": "geometry.stroke",
          "stylers": [{"color": "#fefefe"}, {"lightness": 17}, {"weight": 1.2}]
      }]
    });

    geocodeAddress(geocoder, map, address);
  }

  function geocodeAddress(geocoder, resultsMap, address) {
    geocoder.geocode({'address': address}, function(results, status) {
      if (status === google.maps.GeocoderStatus.OK) {
        resultsMap.setCenter(results[0].geometry.location);
        var image = {
          url: '/static/images/map/marker-conferences.png',
          scaledSize: new google.maps.Size(25, 25)
        };
        var marker = new google.maps.Marker({
          map: resultsMap,
          position: results[0].geometry.location,
          icon: image
        });
      } else {
        console.error('Geocode was not successful for the following reason: ' + status);
      }
    });
  }

</script>
<script src="https://maps.googleapis.com/maps/api/js?key=AIzaSyA0JQa0S94TdFfXHsj7JKXjVN9mu0FighU&callback=initMap"
async defer></script>
<script type="text/javascript">
  require(
    [
      "js/datatables",
    ],
    function(
      DataTables
    ) {
      DataTables.attachTo(document, {
        'recid': "{{ record.control_number }}",
        {% if record['series'] %}
        'seriesname': "{{record['series'][0]}}",
        {% endif %}
        {% if record['cnum'] %}
        'cnum': "{{ record['cnum'] }}"
        {% endif %}
      });
    });
</script>
{% endblock %}
