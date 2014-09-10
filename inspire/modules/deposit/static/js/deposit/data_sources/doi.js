/*
 * This file is part of INSPIRE.
 * Copyright (C) 2014 CERN.
 *
 * INSPIRE is free software: you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation, either version 3 of the License, or
 * (at your option) any later version.
 *
 * INSPIRE is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with INSPIRE. If not, see <http://www.gnu.org/licenses/>.
 *
 * In applying this licence, CERN does not waive the privileges and immunities
 * granted to it by virtue of its status as an Intergovernmental Organization
 * or submit itself to any jurisdiction.
 */

define(function(require, exports, module) {
  var DataSource = require("js/deposit/data_sources/data_source");
  var DataMapper = require("js/deposit/mapper");
  var doiSource = new DataSource({

    id: 'doi',
    name: 'DOI',
    url: '/doi/search?doi=',

    mapper: new DataMapper({

      common_mapping: function(data) {

        var journal;

        if ("container-title" in data) {
          for (var i = 0; i < data['container-title'].length; i++) {
            if (i === data['container-title'].length - 1) {
              journal = data['container-title'][i];
            } else {
              journal = data['container-title'][i] + ', ';
            }
          }
        }

        var pages, page_number;

        if (data.page) {
          pages = data.page.split('-');
          if (pages.length === 2) {
            page_number = pages[1] - pages[0];
          }
        }

        var doi_obj = {
          conf_name: data.publisher,
          journal_title: journal,
          isbn: data.isbn,
          page_nr: page_number,
          page_range: data.page,
          year: data.issued['date-parts'][0][0],
          issue: data.issue,
          authors: data.author,
          volume: data.volume,
          url: data.URL
        };

        // filtering the object out of undefined values
        for (var idx in doi_obj) {
          if (doi_obj[idx] === null || doi_obj[idx] === undefined) {
            delete doi_obj[idx];
          }
        }

        return doi_obj;
      },

      special_mapping: {
        thesis: function(data) {
          return {
            title: data.volume_title
          };
        },
        article: function(data) {
          return {
            title: data.title
          };
        }
      },

      extract_contributor: function(author) {

        return {
          name: author.family + ', ' + author.given,
          affiliation: ''
        };
      }
    })
  });
  module.exports = doiSource;
});
