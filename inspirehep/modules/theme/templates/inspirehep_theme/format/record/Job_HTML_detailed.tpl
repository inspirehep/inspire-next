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
  <div id="record-detailed-jobs">
    <div class="row" id="record-detailed-jobs-information-deadline">
      <div class="col-md-8" id="record-detailed-jobs-information">
        
        <h3>{{ record.position }}</h3>
        
        {% if record.rank %}
          {{ record.rank | join(', ') }}
        {% endif %}
        {% if record.institution %}
          {% for institution in record.institution %}
            <a href="/search?p=department_acronym:{{ institution }}&cc=Institutions">
              {{ institution.name }}
            </a>
          {% endfor %}
        {% endif%}

        {% if record.research_area %}
          <div class="detailed-jobs-information">
            Field of interest:
            {{ record.research_area | join(', ') }}
          </div>
        {% endif %}

        {% if record.experiments %}
          <div class="detailed-jobs-information">
            Experiment:
            {{ record.experiments | join(', ') }}
          </div>
        {% endif %}

        {% if record.continent %}
          <div class="detailed-jobs-information">
            Region:
            {{ record.continent | join(', ') }}
          </div>
        {% endif %}

        {% if record.urls %}
          <div class="detailed-jobs-information">
            More information:
            {% for url in record.urls %}
              <a href="{{ url }}">
                {{ url }}
              </a>
            {% endfor %}
          </div>
        {% endif %}

        {% if record.creation_modification_date %}
          {% if record.creation_modification_date[0] %}
            <div class="detailed-jobs-information">
              Date added: {{ record.creation_modification_date[0].creation_date | format_date }}
            </div>
          {% endif %}
        {% endif %}

        <div class="detailed-jobs-information">
          <a href="mailto:jobs@inspirehep.net?subject=Remove-listing-{% if record['acquisition_source'] %}{{ record['acquisition_source'][0]['submission_number']}} {% endif %}&body=Please remove listing {% if 
          record['acquisition_source'] %}{{ record['acquisition_source'][0]['submission_number']}} {% endif %} https://inspirehep.net/jobs/{{ record['control_number'] }}/edit">
            Click here
          </a>
          to remove this listing
        </div>
      </div>

      <div class="col-md-3" id="record-detailed-jobs-deadline">
        {% if record.deadline_date %}
          <div class="detailed-jobs-information">
            <div class="alert alert-info" role="alert">
              Deadline: {{ record.deadline_date | format_date }}
            </div>
          </div>
        {% endif %}

        {% if record.institution[0].name %}
          <div id="job-detailed-map">
            <script>
              function initMap() {
                var mapDiv = document.getElementById('job-detailed-map');
                var address = '{{ record.institution[0].name }}';
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
            <script src="https://maps.googleapis.com/maps/api/js?callback=initMap" async defer></script>
            </div>
        {% endif %}
      </div>

      {% if record.closed_date %}
        <div class="detailed-jobs-information">
          Deadline: {{record.closed_date | format_date }}
        </div>
      {% endif %}
    </div>

    <div class="row">
      <div class="col-md-8" id="record-detailed-jobs-description">
        {% if record.description %}
          <h3>Job description</h3>
          <div class="detailed-jobs-information">
            {{ record.description }}
          </div>
        {% endif %}
      </div>
      <div class="col-md-3" id="record-detailed-jobs-sidebox">
        <div id="record-detailed-jobs-applications">
          <h3>
            Applications
          </h3>
          {% if record.contact_person %}
            <div class="detailed-jobs-information">
              Contact: {{ record.contact_person | join(', ') }}
            </div>
          {% endif %}
          {% if record.contact_email %}
            <div class="detailed-jobs-information">
              Email: {{ record.contact_email | email_links | join(', ') }}
            </div>
          {% endif %}
          {% if record.reference_email %}
            <div class="detailed-jobs-information">
              Letters of Reference should be sent to:
              {{ record.reference_email | email_links | join(', ') }}
            </div>
          {% endif %}
        </div>

        <hr/>

        <div id="record-detailed-similar-jobs">
          <h3>
            Similar Jobs
          </h3>
          {{ record.id | jobs_similar }}
        </div>
      </div>

    </div>
  </div>
{% endblock %}
