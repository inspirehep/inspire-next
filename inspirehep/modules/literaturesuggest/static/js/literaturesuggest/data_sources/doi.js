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
  var DataSource = require("js/literaturesuggest/data_sources/data_source");
  var DataMapper = require("js/literaturesuggest/mapper");
  var doiSource = new DataSource({

    id: 'doi',
    name: 'DOI',
    service: 'the DOI',
    url: '/doi/search?doi=',

    mapper: new DataMapper({

      common_mapping: function(data) {

        var journal;
        if ("container-title" in data) {
          for (var i = 0; i < data['container-title'].length; i++) {
            if (i === data['container-title'].length - 1) {
              data['processed_title'] = data['container-title'][i];
            } else {
              data['processed_title'] = data['container-title'][i] + ', ';
            }
          }
        }
        if(data.issued){
            let date = data.issued['date-parts'][0][0]
            if(data.issued['date-parts'][0][1]){
              date = date + '-' + data.issued['date-parts'][0][1]
              if(data.issued['date-parts'][0][2]){
              date = date + '-' + data.issued['date-parts'][0][2]
             }
            }
            data['processed_date'] = date
        }
        var doi_obj = {
          isbn: data.isbn,
          issue: data.issue,
          authors: data.author,
          volume: data.volume,
          url: data.URL
        };

        // filtering the object out of undefined values
        for (var idx in doi_obj) {
          if (doi_obj[idx] === null || doi_obj[idx] === undefined || doi_obj[idx].length === 0 ) {
            delete doi_obj[idx];
          }
        }

        return doi_obj;
      },

      special_mapping: {
        thesis: function(data) {
          return {
            type_of_doc: 'thesis',
            journal_title: data.processed_title,
            page_range_article_id: data.page,
            title: data.volume_title,
            defense_date: data.processed_date,
          };
        },
        'journal-article': function(data) {
          var extra_mapping = {
            journal_title: data.processed_title,
            page_range_article_id: data.page,  
            year: data.issued['date-parts'][0][0],
            type_of_doc: 'article'
          };
          if ( data['title'].length > 0 ) {
            extra_mapping['title']= data.title;
            extra_mapping['title_crossref']= data.title;
            }
          return extra_mapping;
        },
        book: function(data) {
          var extra_mapping = { 
            series_title: data.processed_title,
            publication_date: data.processed_date,
            series_volume: data.volume,
            publication_place: data['publisher-location'],
            publisher_name: data.publisher,
            type_of_doc: 'book',
          };
          if ( data['title'].length > 0 ) {
            extra_mapping['title']= data.title;
            extra_mapping['title_crossref']= data.title;
          }
          return extra_mapping;
        },
        'book-chapter': function(data) {
          if (data.page){
            split_pages = data.page.split('-')
          }
          var extra_mapping = { 
            book_title: data.processed_title,
            page_start: split_pages[0],
            page_end: split_pages[1],
            type_of_doc: 'chapter',
          };
          if ( data['title'].length > 0 ) {
            extra_mapping['title']= data.title;
            extra_mapping['title_crossref']= data.title;
          }
          return extra_mapping;
        },
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
