/*
 * This file is part of INSPIRE.
 * Copyright (C) 2016 CERN.
 *
 * INSPIRE is free software; you can redistribute it and/or
 * modify it under the terms of the GNU General Public License as
 * published by the Free Software Foundation; either version 2 of the
 * License, or (at your option) any later version.
 *
 * INSPIRE is distributed in the hope that it will be useful, but
 * WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
 * General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with INSPIRE; if not, write to the Free Software Foundation, Inc.,
 * 59 Temple Place, Suite 330, Boston, MA 02111-1307, USA.
* In applying this license, CERN does not
* waive the privileges and immunities granted to it by virtue of its status
* as an Intergovernmental Organization or submit itself to any jurisdiction.
*/

define(['author'], function(Author) {
  var app = angular.module('author', ['profile']);

  app.directive('authorAffiliation', function() {
    return {
      require: '^profileInit',
      restrict: 'E',
      template: '{{ affiliation }}',
      scope: true,
      link: function(scope) {
        if ('positions' in scope.record) {
          var affiliations = [];
          var positionsObject = scope.record.positions;

          angular.forEach(positionsObject, function(position) {
            if ('institution' in position) {
              if ('name' in position.institution) {
                affiliations.push(position.institution.name);
              }
            }
          });

          if (affiliations.length > 0) {
            scope.affiliation = affiliations[0];
          } else {
            scope.affiliation = '';
          }
        }
      }
    };
  });

  app.directive('authorCollaborators', function() {
    return {
      require: '^profileInit',
      restrict: 'E',
      templateUrl: '/static/js/authors/templates/collaborators.html',
    };
  });

  app.directive('authorEmail', function() {
    return {
      require: '^profileInit',
      restrict: 'E',
      template: '<i class="fa fa-envelope-o"></i> ' +
                '<a href="mailto:{{ email }}">{{ email }}</a>',
      scope: true,
      link: function(scope) {
        if ('positions' in scope.record) {
          var emails = [];
          var emailsObject = scope.record.positions;

          angular.forEach(emailsObject, function(position) {
            if ('email' in position) {
              emails.push(position.email);
            }
          });

          if (emails.length > 0) {
            scope.email = emails[0];
          } else {
            scope.email = '';
          }
        }
      }
    };
  });

  app.directive('authorEducation', function() {
     return {
      require: '^profileInit',
      restrict: 'E',
      templateUrl: '/static/js/authors/templates/position.html',
      scope: true,
      link: function(scope) {
        scope.positions = scope.education;
        scope.icon = 'university';
      }
    };
  });

  app.directive('authorFields', function() {
    return {
      require: '^profileInit',
      restrict: 'E',
      template: '<ul class="research-area">' +
                '<li ng-repeat="field in statistics.fields">' +
                '<a href="/search?subject={{ field }}"> {{ field }}' +
                '</a></li></ul>'
    };
  });

  app.directive('authorName', function() {
    return {
      require: '^profileInit',
      restrict: 'E',
      template: '{{ name }} <b>{{ last_name }}</b>',
      scope: true,
      link: function(scope) {
        var nameObject = scope.record.name;

        if ('preferred_name' in nameObject) {
          var name = nameObject.preferred_name.split(" ");
          scope.last_name = name.pop();
          scope.name = name.join(" ");
        } else {
          scope.name = nameObject.value;
        }
      }
    };
  });

  app.directive('authorKeywords', function() {
    return {
      require: '^profileInit',
      restrict: 'E',
      template: '<p ng-repeat="keyword in statistics.keywords">' +
                '<a href="/search?keyword={{ keyword.keyword }}">' +
                '{{ keyword.keyword }}</a></p>'
    };
  });

  app.directive('authorPositions', function() {
    return {
      require: '^profileInit',
      restrict: 'E',
      template: '<author-work ng-show="work.length"></author-work>' +
                '<author-education ng-show="education.length">' +
                '</author-education>',
      scope: true,
      link: function(scope) {
        if ('positions' in scope.record) {
          var positionsObject = scope.record.positions;
          scope.education = [];
          scope.work = [];

          var spaces = '\u00A0\u00A0\u00A0\u00A0\u00A0\u00A0\u00A0\u00A0';
          var ranks = {
            UG: 'Undergraduate',
            MAS: 'Master',
            PHD: 'PhD',
            PD: 'Postdoctoral',
            SENIOR: 'Senior'
          };

          angular.forEach(positionsObject, function(position) {
            var tempPosition = {};

            // Institution name.
            if (position.hasOwnProperty('institution')) {
              tempPosition['institution'] = position.institution.name;
            }

            // Position dates.
            if (position.hasOwnProperty('start_date')) {
              var start_date = position.start_date;

              if (position.hasOwnProperty('end_date')) {
                tempPosition['date'] = start_date + " - " + position.end_date;
              } else {
                tempPosition['date'] = start_date + " - " + spaces;
              }
            } else if (position.hasOwnProperty('end_date')) {
              tempPosition['date'] = spaces + " - " + position.end_date;
            } else {
              tempPosition['date'] = spaces + " - " + spaces;
            }

            // Position rank.
            if (position.hasOwnProperty('rank')) {
              tempPosition['rank'] = ranks[position.rank];

              if (position.rank == 'MAS' || 
                position.rank == 'UG') {
                scope.education.push(tempPosition);
              } else {
                scope.work.push(tempPosition);
              }
            } else {
              if (tempPosition.hasOwnProperty('institution') ||
                  tempPosition.hasOwnProperty('rank')) {
                scope.work.push(tempPosition);
              }
            }
          });
        }
      }
    };
  });

  app.directive('authorWork', function() {
    return {
      require: '^profileInit',
      restrict: 'E',
      templateUrl: '/static/js/authors/templates/position.html',
      scope: true,
      link: function(scope) {
        scope.positions = scope.work;
        scope.icon = 'suitcase';
      }
    };
  });
});
