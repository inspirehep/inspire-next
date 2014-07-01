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

var doiSource = new DataSource({

  id: 'doi',
  name: 'DOI',
  url: '/deposit/search_doi?doi=',

  mapper: new DataMapper({

    common_mapping: function(data) {

      var page_range;

      if (data.first_page && data.last_page) {
        page_range = data.first_page + "-" + data.last_page;
      }

      return {
        journal_title: data.journal_title,
        isbn: data.isbn,
        page_range: page_range,
        volume: data.volume,
        year: data.year,
        issue: data.issues,
        contributors: data.contributors
      };
    },

    special_mapping: {
      thesis: function(data) {
        return {
          title: data.volume_title
        };
      },
      article: function(data) {
        return {
          title: data.article_title
        };
      }
    },

    extract_contributor: function(contributor) {
      var name, surname;

      if (contributor.contributor[0]) {
        name = contributor.contributor[0].given_name;
      }

      if (contributor.contributor[1]) {
        surname = contributor.contributor[1].surname;
      }

      return {
        name: name + ', ' + surname,
        affiliation: ''
      };
    }
  })
});