/**
This file is part of INSPIRE.
Copyright (C) 2014, 2015 CERN.

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

require(['jquery', 
         'js/authors/profile/pubslistswitch',
         'js/authors/profile/pubslist',
         'js/authors/profile/profilestats',
         'js/authors/profile/profiletoggle',
         'js/authors/profile/profilekeywords',
         'js/authors/profile/profilecoauthors'
         ], function ($,
                      pubsListSwitch,
                      pubsList,
                      profileStats,
                      profileToggle,
                      profileKeywords,
                      profileCoauthors) {

    // Pull down the buttons
    $('.pub-list-disclaimer').each(function() {
        $(this).css('padding-top', $(this).parent().children('.pull-right').height() - $(this).height())
    });
    $('.update-details').each(function() {
        $(this).css('padding-top', $(this).parent().parent().children('.left-col').height() - $(this).parent().height())
    });

    // Create components

    profileStats.attachTo('#profile-stats');
    profileKeywords.attachTo('#keywords-box');
    profileCoauthors.attachTo('#coauthors-box');

    profileToggle.attachTo('.profile-toggle');
    pubsList.attachTo('#pubs_list_table');
    pubsListSwitch.attachTo('.pubs-list-switch>ul>li');
});
