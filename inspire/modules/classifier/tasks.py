# -*- coding: utf-8 -*-
#
# This file is part of INSPIRE.
# Copyright (C) 2015 CERN.
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


"""Tasks for classifier."""

from functools import wraps

from .utils import (
    update_classification_in_task_results,
    get_classification_from_task_results,
)


def filter_core_keywords(filter_kb):
    """Filter core keywords."""
    @wraps(filter_core_keywords)
    def _filter_core_keywords(obj, eng):
        from inspire.utils.knowledge import check_keys

        result = get_classification_from_task_results(obj)
        if result is None:
            return
        filtered_core_keywords = {}
        for core_keyword, times_counted in result.get("Core keywords").items():
            if not check_keys(filter_kb, [core_keyword]):
                filtered_core_keywords[core_keyword] = times_counted
        result["Filtered Core keywords"] = filtered_core_keywords
        update_classification_in_task_results(obj, result)
    return _filter_core_keywords
