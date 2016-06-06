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
  <div id="record-detailed-institution">
    <div class="row">
      <div class="col-md-8" id="record-detailed-institution-information">
        <h3>
          {% if record['ICN'] %}
            {% if record['ICN'] | is_list %}
              {{ record['ICN'][0] }}
              [Future INSPIRE ID:{{record['ICN'][0]}}]  
            {% else %}
              {{ record['ICN'] }}
              [Future INSPIRE ID:{{record['ICN']}}]  
            {% endif %}
          {% endif %}
        </h3>

        {% if record['institution'] | is_list %}
             Institution: {{ record['institution'][0] }}
        {% else %}
             {{ record['institution'] }}
        {% endif %}

        {% if record['department'] | is_list %}
             {{ record['department'][0] }}
        {% else %}
             {{ record['department']}}
        {% endif %}
        
        {% if record['address'][0]['address'] | is_list %}
          {{ record['address'][0]['address'] | join(', ') }},
        {% else %}
          {{ record['address'][0]['address'] }},
        {% endif %}

        {% for country in record['address'] %}
          {% if 'country' in country %}
           {{ country['country']}}
          {% endif %}
        {% endfor %}

        {% if record['urls'] %}
          <div class="detailed-institution-information">
            <a href="{{ record['urls'][0] }}">{{ record['urls'][0] }}</a>
          </div>
        {% endif %}

        {% if record['name_variants'] %}
          <div>
            {% set name_var = [] %}
            {% for element in record['name_variants'] %}
              {% if 'source' not in element and 'value' in element %}
                {% do name_var.append(element['value']) %}
              {% endif %} 
            {% endfor %}   
            {% if name_var %}
              <label>Name variants: </label>{{ name_var[0] | join(', ') }}
            {% endif %}
          </div>
        {% endif %}

        {% if record['historical_data'] %}
          <div>
            <label>Historical Data: </label>{{ record['historical_data'] | join(', ') }}
          </div>
        {% endif %}

        {% if record['public_notes'] %}
          <div class="row">
            <div class="col-md-12">
              <label>Notes: </label>{{ record['public_notes'] | join(', ') }}
            </div>
          </div>
        {% endif %}

        <div>
          <label>Related Institution:</label><a href="#"> Related institution</a>
        </div>

        <div>
          <label>Parent Institution:</label><a href="#"> Parent institution</a>
        </div>

        <div>
          {% if record['ICN'] %}
            {% if record['ICN'] | is_list %}
              HEP list of<a href="#"> Ph.D. theses </a> at {{ record['ICN'][0] }}
            {% else %}
              HEP list of<a href="#"> Ph.D. theses </a> at {{ record['ICN'] }}
            {% endif %}
          {% endif %}
        </div>

        <div>
          {% if record['ICN'] %}
            {% if record['ICN'] | is_list %}
              HEPNAMES list of<a href="#"> people</a> at {{ record['ICN'][0] }}
            {% else %}
              HEPNAMES list of<a href="#"> people</a> at {{ record['ICN'] }}
            {% endif %}
          {% endif %}
        </div>

        <div>
          {% if record['ICN'] and record['institution'] %}
            {% if record['ICN'] | is_list %}
              EXPERIMENTS list of<a href="/search?p=affiliation:{{ record['institution'][0] }}&cc=Experiments"> experiments</a> performed <b>at</b> {{ record['ICN'][0] }}
            {% else %}
              EXPERIMENTS list of<a href="/search?p=affiliation:{{ record['institution'] }}&cc=Experiments"> experiments</a> performed <b>at</b> {{ record['ICN'] }}
            {% endif %}
          {% endif %}
        </div>
      
      </div>

      <div class="col-md-3" id="record-detailed-institution-map">
        <div id="institution-detailed-map">
          {% block javascript %}
          {{ super() }}
            <script>
              function initMap() {
                var mapDiv = document.getElementById('institution-detailed-map');
                var address = '{{ record['address'][0]['address'] | join(', ') }}';
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
      </div>
    </div>
  </div>
{% endblock %}
