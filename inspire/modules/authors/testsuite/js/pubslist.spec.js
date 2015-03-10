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

  jasmine.getFixtures().fixturesPath = '/jasmine/spec/inspire.modules.authors/fixtures/';

  var listFixture = readFixtures('bootstrapped.html');

  describeComponent('js/authors/profile/pubslist', function() {

    beforeEach(function() {
      this.setupComponent(listFixture);
    });

    afterEach(function() {
      $(".dataTables_wrapper").html(" ");
    });

    it('should be defined', function() {
      expect(this.component).toBeDefined();
    });

    it('union test', function() {
      expect(this.component.unionIds([1, 2, 3], [{
        id: 2
      }, {
        id: 4
      }])).toEqual([{
        id: 2
      }]);
      expect(this.component.unionIds([], [])).toEqual([]);
      expect(this.component.unionIds([2], [{id:1}])).toEqual([]);
    });

    it('should send papers only after all the toggles are defined', function() {
      var spy = spyOnEvent(document, 'toggleChanged');
      for (var i = 1; i < $(listFixture).find('li').length; ++i) {
        // Still some triggers left, so the event should be supressed
        $(document).trigger('triggerToggle', {
          name: "catch me"
        });
        expect(spy).not.toHaveBeenTriggered();
      }

      // This is the last trigger, so other components should be notified
      $(document).trigger('triggerToggle', {
        name: "pass me"
      });
      expect(spy).toHaveBeenTriggered();
      spy.reset();

      // After that every trigger should be passed through
      $(document).trigger('triggerToggle', {
        name: "pass me",
        value: true
      });
      expect(spy).toHaveBeenTriggered();
      spy.reset();
      $(document).trigger('triggerToggle', {
        name: "pass me"
      });
      expect(spy).toHaveBeenTriggered();
    })


  });
});
