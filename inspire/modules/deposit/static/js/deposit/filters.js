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

function Filter(options) {

  /**
   *
   * @type {{}}
   */
  this.common_mapping = options.common_mapping ?
    options.common_mapping : function(data) {};

  /**
   *
   * @type {function} The function should return:
   */
  this.special_mapping = options.special_mapping ?
    options.special_mapping : {};

  /**
   * Function to extract author sub-form content having
   * an item from
   */
  this.extract_contributor = options.extract_contributor ?
    options.extract_contributor : function(contributor) {
      return contributor;
    };

  /**
   * Filter name. It will be displayed in info messages.
   *
   * @type {string}
   */
  this.name = options.name ? options.name : '';

  /**
   * Query url.
   *
   * @type {string}
   */
  this.url = options.url ? options.url : '';
}

Filter.prototype = {

  /**
   * Maps data to a common format in the way defined in filter.
   *
   * @param data {*} data to map
   * @param depositionType {String} type of deposition
   * @returns {*}
   */
  applyFilter: function(data, depositionType) {
    var common_mapping = this.common_mapping(data);
    var special_mapping = {};
    if (this.special_mapping[depositionType]) {
      special_mapping = this.special_mapping[depositionType](data);
    }

    var mapping = $.extend({}, common_mapping, special_mapping);
    mapping.contributors = $.map(mapping.contributors, this.extract_contributor);

    return mapping;
  }
};

var doiFilter = new Filter({
  name: 'DOI',
  url: '/deposit/search_doi?doi=',

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
});

var arxivFilter = new Filter({
  name: 'arXiv',
  url: '/arxiv/search?arxiv=',

  special_mapping: {
    article: function(data) {
      return {
        title: data.title,
        title_arXiv: data.title,
        year: data.published,
        abstract: data.summary,
        article_id: 'arxiv:' + data.id,
        contributors: data.author
      };
    }
  },

  extract_contributor: function(contributor) {

    return {
      name: contributor.name,
      affiliation: ''
    };
  }
});

/**
 * This filter assumes it receives standarized data format
 * after treating with another filter.
 *
 * @type {Filter}
 */
var arxivDoiFilter = new Filter({

  common_mapping: function(data) {

    var priorities = {
      title: ['doi', 'arxiv'],
      title_arXiv: ['arxiv'],
      journal_title: ['doi', 'arxiv'],
      isbn: ['doi', 'arxiv'],
      page_range: ['doi', 'arxiv'],
      volume: ['arxiv', 'doi'],
      year: ['arxiv', 'doi'],
      issue: ['arxiv', 'doi'],
      contributors: ['arxiv', 'doi'],
      abstract: ['arxiv', 'doi'],
      article_id: ['arxiv', 'doi'],
    };

    var result = {};

    for (var field in priorities) {
      for (var idx in priorities[field]) {
        var source = priorities[field][idx];
        if (data[source] && data[source][field]) {
          result[field] = data[source][field];
          break;
        }
      }
    }
    return result;
  }
});
