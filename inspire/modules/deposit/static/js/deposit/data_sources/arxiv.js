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
  var DataSource = require("./data_source.js");
  var DataMapper = require("../mapper.js");
  var arxivSource = new DataSource({

    id: 'arxiv',
    name: 'arXiv ID',
    url: '/arxiv/search?arxiv=',

    mapper: new DataMapper({

      special_mapping: {
        article: function(data) {
          return {
            doi: data.doi,
            title: data.title,
            title_arXiv: data.title,
            abstract: data.abstract,
            authors: data.authors,
            journal_title: data["journal-ref"],
            year: data.created.substring(0, 4),
            license_url: data.license,
            note: data.comments,
          };
        }
      },

      extract_contributor: function(authors) {
        var name, surname;

        if (authors.author[0]) {
          name = authors.author[0].keyname;
        }

        if (authors.author[1]) {
          surname = authors.author[1].forenames;
        }

        return {
          name: name + ', ' + surname,
          affiliation: ''
        };
      }
    })

  });

  module.exports = arxivSource;
});
