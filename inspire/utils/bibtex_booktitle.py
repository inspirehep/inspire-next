#
## This file is part of INSPIRE.
## Copyright (C) 2015 CERN.
##
## INSPIRE is free software; you can redistribute it and/or
## modify it under the terms of the GNU General Public License as
## published by the Free Software Foundation; either version 2 of the
## License, or (at your option) any later version.
##
## INSPIRE is distributed in the hope that it will be useful, but
## WITHOUT ANY WARRANTY; without even the implied warranty of
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
## General Public License for more details.
##
## You should have received a copy of the GNU General Public License
## along with INSPIRE; if not, write to the Free Software Foundation, Inc.,
## 59 Temple Place, Suite 330, Boston, MA 02111-1307, USA.
#
from invenio_records.api import get_record
from invenio_search.api import Query


def traverse(o, tree_types=(list, tuple)):
    if isinstance(o, tree_types):
        for value in o:
            for subvalue in traverse(value):
                yield subvalue
    else:
        yield o


def generate_booktitle(record):
    booktitle = ''
    pubinfo = ''
    if 'publication_info' in record:
        pubinfo = record['publication_info']
        if isinstance(pubinfo, list):
            for field in pubinfo:
                if 'reportnumber' in field:
                    rn = field['reportnumber']
                    if rn:
                        acronym = field['acronym']
                        if acronym:
                            booktitle = "%s: %s" % (rn, acronym, )
                        else:
                            recids = Query("reportnumber:%s" % (rn,))\
                                           .search().recids
                            if recids:
                                rec = get_record(recids[0])
                                title = rec['title']['title']
                                if title:
                                    booktitle = title
                                    if 'subtitle' in rec['title']:
                                        subtitles = rec['title']['subtitle']
                                        if subtitles:
                                            booktitle += ': ' + subtitles
        else:
            if 'reportnumber' in pubinfo:
                rn = pubinfo['reportnumber']
                if rn:
                    acronym = pubinfo['acronym']
                    if acronym:
                        booktitle = "%s: %s" % (rn, acronym, )
                    else:
                        recids = Query("reportnumber:%s" % (rn,)).search().recids
                        if recids:
                            rec = get_record(recids[0])
                            title = rec['title']['title']
                            if title:
                                booktitle = title
                                if 'subtitle' in rec['title']:
                                    subtitles = rec['title']['subtitle']
                                    if subtitles:
                                        booktitle += ': ' + subtitles

    # if not booktitle:
    #     cnum = ''
    #     if isinstance(pubinfo, list):
    #         for field in pubinfo:
    #             if 'cnum' in field: 
    #                 cnum = cnum.replace("/", "-")
    #                 recids = search_pattern(
    #             p='773__w:%s 980__a:PROCEEDINGS' % (cnum,))
    #                 if recids:
    #                     rec = get_record(recids[0])
    #                     titles = rec['title']['title']
    #                     if titles:
    #                         booktitle = titles
    #                         if 'subtitle' in rec['title']:
    #                             subtitles = rec['title']['subtitle']
    #                             if subtitles:
    #                                 booktitle += ': ' + subtitles
    #     else:
    #         if 'cnum' in pubinfo:
    #             cnum = cnum.replace("/", "-")
    #             recids = search_pattern(
    #             p='773__w:%s 980__a:PROCEEDINGS' % (cnum,))
    #             if recids:
    #                 rec = get_record(recids[0])
    #                 titles = rec['title']['title']
    #                 if titles:
    #                     booktitle = titles
    #                     if 'subtitle' in rec['title']:
    #                         subtitles = rec['title']['subtitle']
    #                         if subtitles:
    #                             booktitle += ': ' + subtitles

    if not booktitle:
        result = []
        if isinstance(pubinfo, list):
            for field in pubinfo:
                if 'pubinfo_freetext' in field:
                    result.append(field['pubinfo_freetext'])
            if result:
                if any(isinstance(i, list) for i in result):
                    nested_list = list(traverse(result))
                    booktitle = ', '.join(str(title) for title in nested_list)
                else:
                    booktitle = ', '.join(str(title) for title in result)
        else:
            if 'pubinfo_freetext' in pubinfo:
                booktitle = pubinfo['pubinfo_freetext']
    return booktitle
