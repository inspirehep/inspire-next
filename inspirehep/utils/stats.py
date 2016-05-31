# -*- coding: utf-8 -*-
#
# This file is part of INSPIRE.
# Copyright (C) 2016 CERN.
#
# INSPIRE is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License as
# published by the Free Software Foundation; either version 2 of the
# License, or (at your option) any later version.
#
# INSPIRE is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with INSPIRE; if not, write to the Free Software Foundation, Inc.,
# 59 Temple Place, Suite 330, Boston, MA 02111-1307, USA.
import operator


class Stats(object):

    """Stats is a class to calculate common metrics"""

    @staticmethod
    def calculate_hindex(*args, **kwargs):
        """
        Given a citation dictionary, in the format {recid: citation_count}
        returns the hindex.
        :param args:
        :param kwargs:
        :return: h index for a given list of citations.
        """
        _record_citations = kwargs.pop('citations')
        _sorted = Stats.get_sorted_citations(_record_citations)

        h_index = 0
        print _sorted
        for _index, _val in enumerate(_sorted):
            if _val[1] > _index:
                h_index = _index+1
            else:
                break

        return h_index

    @staticmethod
    def calculate_i10(*args, **kwargs):
        """
        Given a citation dictionary, in the format {recid: citation_count}
        returns the i10 index, which is simply the number of records with
        10 or more citations.
        :param args:
        :param kwargs:
        :return: i10 index for a given list of citations.
        """
        _record_citations = kwargs.pop('citations')
        _sorted = Stats.get_sorted_citations(_record_citations)
        _publications = filter(lambda x: x[1] >=10, _sorted)

        return len(_publications)

    @staticmethod
    def get_sorted_citations(_record_citations):
        _sorted = sorted(_record_citations.items(), key=operator.itemgetter(1),
                         reverse=True)
        return _sorted
