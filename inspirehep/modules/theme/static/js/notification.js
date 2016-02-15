 /*
  * This file is part of INSPIRE.
  * Copyright (C) 2015 CERN.
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

 define([
   'toastr',
 ], function(toastr) {
   'use strict';

   function createCookie(name, value, days) {
     if (days) {
       var date = new Date();
       date.setTime(date.getTime() + (days * 24 * 60 * 60 * 1000));
       var expires = "; expires=" + date.toGMTString();
     } else var expires = "";
     document.cookie = name + "=" + value + expires + "; path=/";
   }

   function readCookie(name) {
     var nameEQ = name + "=";
     var ca = document.cookie.split(';');
     for (var i = 0; i < ca.length; i++) {
       var c = ca[i];
       while (c.charAt(0) == ' ') c = c.substring(1, c.length);
       if (c.indexOf(nameEQ) == 0) return c.substring(nameEQ.length, c.length);
     }
     return null;
   }

   toastr.options.closeButton = true;
   toastr.options.timeOut = 0;
   toastr.options.extendedTimeOut = 0;
   toastr.options.positionClass = "toast-top-right";
   toastr.options.onHidden = function() {
     createCookie('notificationDismissed', 'true', '10');
   };
   toastr.options.tapToDismiss = false;

   var dismissed = readCookie('notificationDismissed');
   if (!dismissed) {
     toastr.info('You can go back to INSPIRE HEP any time - just <a href="http://inspirehep.net">click here</a>', 'Welcome to INSPIRE Labs!')
   }

 });
