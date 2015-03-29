/**
This file is part of INSPIRE.
Copyright (C) 2015 CERN.

INSPIRE is free software; you can redistribute it and/or
modify it under the terms of the GNU General Public License as
published by the Free Software Foundation; either version 2 of the
License, or (at your option) any later version.

INSPIRE is distributed in the hope that it will be useful, but
WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
General Public License for more details.

You should have received a copy of the GNU General Public License
along with INSPIRE; if not, write to the Free Software Foundation, Inc.,
59 Temple Place, Suite 330, Boston, MA 02111-1307, USA.
**/
require(['jasmine-flight'], function(jasmineFlight) {

  // TO DO add more general flow tests after the structure of input is
  // well-defined

  'use strict';

  describeComponent('js/authors/profile/profilestats', function() {

    beforeEach(function() {
      this.setupComponent();
    });

    it('should be defined', function() {
      expect(this.component).toBeDefined();
    });

    it('h-index should be properly computed', function() {
      // used only as a fallback for empty citation array
      this.component.papersNum = 0;
      expect(this.component.h_index([])).toEqual(0);
      expect(this.component.h_index([3,1,22,29,34,51,0])).toEqual(4);
      expect(this.component.h_index([5,4,4,3,3,6,2,2,1,0,0])).toEqual(4);
    });

  });

});
