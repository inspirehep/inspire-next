/*
** This file is part of INSPIRE.
** Copyright (C) 2014 CERN.
**
** INSPIRE is free software: you can redistribute it and/or modify
** it under the terms of the GNU General Public License as published by
** the Free Software Foundation, either version 3 of the License, or
** (at your option) any later version.
**
** INSPIRE is distributed in the hope that it will be useful,
** but WITHOUT ANY WARRANTY; without even the implied warranty of
** MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
** GNU General Public License for more details.
**
** You should have received a copy of the GNU General Public License
** along with INSPIRE. If not, see <http://www.gnu.org/licenses/>.
**
** In applying this licence, CERN does not waive the privileges and immunities
** granted to it by virtue of its status as an Intergovernmental Organization
** or submit itself to any jurisdiction.
*/

/**
            TODO: Connect select options under the Literature Collection
                        with the search results
**/

(function($) {

     /**
        adding parameter to the URL, helpful function for
        defining the cc parameter for the collection names
    **/
    function insertParam(key, value) {
        key = escape(key); value = escape(value);

        var kvp = document.location.search.substr(1).split('&');
        if (kvp == '') {
            document.location.search = '?' + key + '=' + value;
        }
        else {

            var i = kvp.length; var x; while (i--) {
                x = kvp[i].split('=');

                if (x[0] == key) {
                    x[1] = value;
                    kvp[i] = x.join('=');
                    break;
                }
            }

            if (i < 0) { kvp[kvp.length] = [key, value].join('='); }

            //this will reload the page, it's likely better to store this until finished
            document.location.search = kvp.join('&');
        }
    }

    // $('#myTab a').on('click', function(e){
    //     console.log($(this).attr('href'));
    //    insertParam('cc', $(this).attr('href'))
    // });

    $('#myTab a').on('click', function (e) {
        e.preventDefault();
        if (!($(this).attr('id') == 'hep')) {
            $('#drop').hide();
        } else {
            $('#drop').show();
        }
     //   $(this).tab('show');
    });


  $('#myTab a').on('click', function (e) {
    console.log('hi')
    //save the latest tab; use cookies if you like 'em better:
    console.log($(e.target).attr('href'))
    localStorage.setItem('lastTab', $(e.target).attr('href'));
  });

  //go to the latest tab, if it exists:
  var lastTab = localStorage.getItem('lastTab');

  if (lastTab) {
      $('a[href="'+lastTab+'"]').click();
  }

var url= window.location.href;
console.log(url);
console.log(url.split("/"));
console.log(url.split("/").length);
// if(url.split("/").length==4) {
//     window.localStorage.clear("lastTab");
//     console.log('clearing localStorage.....')
// //     if(url_has_vars()===true) {
// //     window.localStorage.clear("lastTab");
// //     console.log('clearing localStorage.....')

// // }
//     //alert('You are in the homepage');
// }

    if (url.split("/").length<5 && url_has_vars()!==true) {
        console.log('clearing localStorage.....')
        window.localStorage.clear("lastTab");
    }


function url_has_vars() {
   return location.search != "";
}
console.log(url_has_vars())
// if(url_has_vars()===true) {
//     window.localStorage.clear("lastTab");
// }


    // var json, tabsState;
    // $('a[data-toggle="pill"], a[data-toggle="tab"]').on('shown', function(e) {
    //     var href, json, parentId, tabsState;

    //     tabsState = localStorage.getItem("tabs-state");
    //     json = JSON.parse(tabsState || "{}");
    //     parentId = $(e.target).parents("ul.nav.nav-pills, ul.nav.nav-tabs").attr("id");
    //     href = $(e.target).attr('href');
    //     json[parentId] = href;

    //     return localStorage.setItem("tabs-state", JSON.stringify(json));
    // });

    // tabsState = localStorage.getItem("tabs-state");
    // json = JSON.parse(tabsState || "{}");

    // $.each(json, function(containerId, href) {
    //     return $("#" + containerId + " a[href=" + href + "]").tab('show');
    // });

    // $("ul.nav.nav-pills, ul.nav.nav-tabs").each(function() {
    //     var $this = $(this);
    //     if (!json[$this.attr("id")]) {
    //       return $this.find("a[data-toggle=tab]:first, a[data-toggle=pill]:first").tab("show");
    //     }
    // });


})(jQuery);