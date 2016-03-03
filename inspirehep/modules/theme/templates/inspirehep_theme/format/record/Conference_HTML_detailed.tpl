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

{% block body %}
  <div id="record-detailed-conference">
    <div class="row" id="record-detailed-conference-information-map">
      <div class="col-md-8" id="record-detailed-conference-information">

        <h3>
          {{ record['title'] }}
        </h3>

        {% if record['acronym'] %}
          {{ print_array(record, "acronym") }}
        {% endif %}

        {% if record['subtitle'] %}
          {{ record['subtitle'] }}
        {% endif %}

        {% if record['alternative_titles'] %}
          {{ print_array(record, 'alternative_titles') }}
        {% endif %}
        
        {% if record['cnum'] %}
          <div class="detailed-conference-information">CNUM: {{ record['cnum'] }}</div>
        {% endif %}
        
        {% if record['url'] %}
          {% set comma = joiner() %}
          <div class="detailed-conference-information">
            {% for url in record['url'] -%}
              {{ comma() }} <a href="{{ url[0] }}">Go to conference website</a>
            {%- endfor %}
          </div>
        {% endif %}

        {% if record['transparencies'] %}
          Record transparencies:
          <a href="{{ record['transparencies'] }}">
            {{ record['transparencies'] }}
          </a>
        {% endif %}

        {% if record['contact_person'] or record['contact_email'] %}
          <div class="detailed-conference-information">
            {% if record['contact_person'] %}
              Contact person:
              {% set comma = joiner() %}
              {% for contact in record['contact_person'] -%}
                  {{ comma() }} {{ contact }}
              {%- endfor %}
            <br>
            {% endif %}

            {% if record['contact_email'] %}
              Contact email:
              {{ record['contact_email'] | email_links | join_array(", ") }}
            {% endif %}
          </div>
        {% endif %}

        {% if record['short_description'] %}
          {% set comma = joiner() %}
          <div class="detailed-conference-information">
            Short description:
            {% for description in record['short_description'] -%}
              {{ comma() }} {{ description['value'][0] }}
            {%- endfor %}
          </div>
        {% endif %}
        
        {% if record['note'] %}
          {{ print_array(record, 'note') }}
        {% endif %}

        {% if record['keywords'] %}
          {% set comma = joiner('&nbsp') %}
          <div class="detailed-conference-information">
            Keywords:
            {% for keyword in record['keywords'] -%}
              {{ comma() }}
              <span class="label label-default label-keyword">
                <a href="/search?q=&cc=conferences&q={{ keyword['value'] }}">
                  {{ keyword['value'] }}
                </a>
              </span>
            {%- endfor %}
          </div>
        {% endif %}

        {% if record['field_code'] %}
          {% set comma = joiner('&nbsp') %}
          <div class="detailed-conference-information">
            Fields:
            {% for field in record['field_code'] -%}
              {{ comma() }}
              <span class="label label-default label-keyword">
                <a href="/search?q=&cc=conferences&q={{ field['value'] }}">
                  {{ field['value'] }}
                </a>
              </span>
            {%- endfor %}
          </div>
        {% endif %}

        {% if record['series'] %}
          <div class="detailed-conference-information">
            Part of the
            <a href="/search?q=&cc=conferences&series={{ record['series'][0] }}">
              {{ record['series'][0] }}
            </a>
            series
          </div>
        {% endif %}

      </div>

      <div class="col-md-3" id="record-detailed-conference-map">

        <div id="conference-detailed-map">
          {% block javascript %}
          {{ super() }}
            <script>
              function initMap() {
                var mapDiv = document.getElementById('conference-detailed-map');
                var address = '{{ record['place'] }}';
                var geocoder = new google.maps.Geocoder();

                var map = new google.maps.Map(mapDiv, {
                  zoom: 5,
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
                    var marker = new google.maps.Marker({
                      map: resultsMap,
                      position: results[0].geometry.location,
                      icon: '/static/images/map/marker-conferences.svg'
                    });
                  } else {
                    alert('Geocode was not successful for the following reason: ' + status);
                  }
                });
              }

            </script>
            <script src="https://maps.googleapis.com/maps/api/js?callback=initMap"
            async defer></script>
          {% endblock %}
        </div>

        <h4 id="conference-detailed-map-place">
          <i class="fa fa-map-marker"></i>
          {{ record['place'] }}
          <br/>
          <br/>
          <i class="fa fa-calendar"></i>
          {{ record | conference_date }}.        
        </h4>

      </div>

    </div>

    <div class="row">
        {% if record['series'] %}
          <div class="panel" id="other-conferences">
            <div class="panel-heading">
              <div class="record-detailed-title">
                {{ (record.get('conferences', '')) | count }} other conferences in this series
              </div>
            </div>
            <div class="panel-body">
              <div id="record-other-conferences-loading">
                <i class="fa fa-spinner fa-spin fa-lg" ></i><br>Loading conferences...
              </div>
              <div id="record-other-conferences-table-wrapper">
                <table id="record-other-conferences-table" class="table table-striped table-bordered" cellspacing="0" width="100%">
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
        {% endif %}
    </div>
  </div>
{% endblock %}

{% macro print_array(record, field, has_items=false) %}
  <div class="detailed-conference-information">
    {{ field | capitalize }}:
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