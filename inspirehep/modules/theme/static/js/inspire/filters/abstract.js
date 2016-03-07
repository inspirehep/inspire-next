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

define([], function() {
  /**
  * AngularJS filter to display DOI information
  */
  function abstractFilter() {
    return function(input, is_brief) {
      if (!input) {
        return '';
      }
      var number_of_words;
      var abstract_displayed = false;
      var arxiv_abstract = '';
      if (is_brief) {
        number_of_words = 0;
      }  else {
        number_of_words = 100;
      }
      if (input['abstracts']) {
        for (var i=0; i < input['abstracts'].length; i++) {
          

        }
      }
      
      //return eprint + '<br/>' + categories;
    }
  }
  return abstractFilter;
});