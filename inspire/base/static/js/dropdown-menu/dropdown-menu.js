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
   'jquery',
   'jquery-menu-aim',
 ], function($, $menuAim) {
   $(window).ready(function() {
     doneResizing();
     var id;
     $(window).resize(function() {
       clearTimeout(id);
       id = setTimeout(doneResizing, 100); //wait 0.1 seconds and call doneResizing
     });


     function doneResizing() {
       var wi = $(window).width();
       var $menu = $(".dropdown-menu");
       if (wi > 767) {
         $menu.menuAim({
           activate: activateSubmenu,
           deactivate: deactivateSubmenu
         });

         $(".custom-popover").css({
           "height": ""
         });
         $(".move-down").css({
           "margin-top": "0px"
         }); // change it to class! 
         $(".dropdown").removeClass('open');
         $(".popover").css({
           "display": "none"
         });
         $("#first-element, #second-element, #third-element, #fourth-element, #fifth-element, #sixth-element, #seventh-element").off("click");

         //return arrows to the default position
         arrowDefaultState("#first-arrow");
         arrowDefaultState("#second-arrow");
         arrowDefaultState("#third-arrow");
         arrowDefaultState("#fourth-arrow");
         arrowDefaultState("#fifth-arrow");
         arrowDefaultState("#sixth-arrow");
         arrowDefaultState("#seventh-arrow");


         function activateSubmenu(row) {
           var $row = $(row),
             submenuId = $row.data("submenuId"),
             $submenu = $("#" + submenuId),
             height = $menu.outerHeight(),
             width = $menu.outerWidth();
           // Show the submenu
           $submenu.css({
             display: "block",
             top: -1,
             left: width - 3 // main should overlay submenu
               //height: height - 4  // padding for main dropdown's arrow
           });
         }

         function deactivateSubmenu(row) {
           var $row = $(row),
             submenuId = $row.data("submenuId"),
             $submenu = $("#" + submenuId);
           // Hide the submenu and remove the row's highlighted look
           $submenu.css("display", "none");
           //$row.find("a").removeClass("maintainHover");
         }

         $(".dropdown-menu li").click(function(e) {
           e.stopPropagation();
         });

         $(document).click(function() {
           // Simply hide the submenu on any click. Again, this is just a hacked
           // together menu/submenu structure to show the use of jQuery-menu-aim.
           $(".popover").css("display", "none");
         });

         //Function for opening both parts on click
         /*$(".dropdown-toggle").click(function() {
            $("#jobs").css({"display":"block","top": "-1px", "left": "733px","position":"absolute"});
           });*/
       } else {
         $(document).click(function() {
           $(".move-down").css({
             "margin-top": "0px"
           });
         });

         $(".popover").css({
           "display": "none"
         });
         $(".dropdown").removeClass('open');
         $(".dropdown-toggle").off("click");
         $(".first-submenu-item, .second-submenu-item, .third-submenu-item," +
           ".fourth-submenu-item, .fifth-submenu-item, .sixth-submenu-item, .seventh-submenu-item").off();

         $(".move-down").animate({
           "margin-top": "0px"
         }, "fast");

         responsiveDropdown("#first-element", "#jobs", "#first-arrow");
         responsiveDropdown("#second-element", "#conferences", "#second-arrow");
         responsiveDropdown("#third-element", "#journals", "#third-arrow");
         responsiveDropdown("#fourth-element", "#experiments", "#fourth-arrow");
         responsiveDropdown("#fifth-element", "#institutions", "#fifth-arrow");
         responsiveDropdown("#sixth-element", "#tools", "#sixth-arrow");
         responsiveDropdown("#seventh-element", "#links-and-stats", "#seventh-arrow");
       }
     }
   });


   function arrowDefaultState(id) {
     $(id).addClass('fa-chevron-right').removeClass('fa-chevron-down');
     $(id).off("click");
   }

   function responsiveDropdown(element, objectToShow, arrow) {
     arrowDefaultState(arrow);
     var showContent = false;
     $(element).click(function(e) {
       e.stopPropagation();

       if (!showContent) {
         $(objectToShow).slideDown().css({
           "display": "block",
           "top": "-1px",
           "left": "0px"
         });
         $(arrow).addClass('fa-chevron-down').removeClass('fa-chevron-right');
         $(".move-down").animate({
           "margin-top": "30px"
         }, "slow");
         showContent = true;
       } else {
         $(objectToShow).slideUp();
         $(arrow).addClass('fa-chevron-right').removeClass('fa-chevron-down');
         $(".move-down").animate({
           "margin-top": "0px"
         }, "slow");
         showContent = false;
       }
     });
   }
 });
