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

define(['profile'], function(Profile) {
  var app = angular.module('profile', []);

  app.controller('ProfileController', ['$http', '$scope', '$element', '$attrs',
      function($http, $scope, $element, $attrs) {

    // Initialise data variables.
    $scope.publications = {
      collaborations: [],
      keywords: [],
      publications: []
    };

    // Author profile object.
    $scope.record = JSON.parse($attrs.record);

    // Publications per year, total publications, count of different types.
    $scope.statistics = [[], 0, {}];

    var countPublications = function(data) {
      var publications = data.publications,
          publicationsCountMap = {},
          publicationsDataToPlot = [],
          researchWorksCount = publications.length,
          researchWorksTypes = {};

      angular.forEach(publications, function(publication) {
        if (publication.year in publicationsCountMap) {
          publicationsCountMap[publication.year]++;
        } else {
          publicationsCountMap[publication.year] = 1;
        }

        if (publication.type in researchWorksTypes) {
          researchWorksTypes[publication.type]++;
        } else {
          researchWorksTypes[publication.type] = 1;
        }
      });

      angular.forEach(publicationsCountMap, function(count, year) {
        publicationsDataToPlot.push({
          year: parseInt(year),
          publications: count
        });
      });      

      return [publicationsDataToPlot, researchWorksCount, researchWorksTypes];
    };

    var recid = $scope.record.control_number;
    $http.get("/author/publications?recid=" + recid)
      .success(function(data) {
        $scope.publications = data;
        $scope.statistics = countPublications(data);
      });
    }]);

  app.directive('profileInit', function() {
    return {
      restrict: 'A',
      scope: true,
      controller: 'ProfileController'
    };
  });
});