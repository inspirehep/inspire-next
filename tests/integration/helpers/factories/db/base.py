# -*- coding: utf-8 -*-
#
# This file is part of INSPIRE.
# Copyright (C) 2014-2017 CERN.
#
# INSPIRE is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# INSPIRE is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with INSPIRE. If not, see <http://www.gnu.org/licenses/>.
#
# In applying this license, CERN does not waive the privileges and immunities
# granted to it by virtue of its status as an Intergovernmental Organization
# or submit itself to any jurisdiction.

from __future__ import absolute_import, division, print_function

import abc
import random
import six
import string

from invenio_db import db


def generate_random_string(size):
    domain = string.ascii_lowercase + string.ascii_uppercase + string.digits
    return ''.join(random.choice(domain) for _ in range(size))


@six.add_metaclass(abc.ABCMeta)
class TestBaseModel(object):
    model_class = None

    @classmethod
    def create_from_kwargs(cls, kwargs):
        """
        Create a new instance of the model_class for this test class using
        the given kwargs. And add it to the db session.
        """
        filtered_kwargs = cls._filter_kwargs_for_model(kwargs, cls.model_class)
        instance = cls.model_class(**filtered_kwargs)
        db.session.add(instance)
        return instance

    @staticmethod
    def _filter_kwargs_for_model(kwargs, model_class):
        """
        Filter the given kwargs and keep only those that make sense for
        the given model_class.

        Args:
            kwargs (dict): a dictionary.
            model_class: the DB model class to filter the kwargs for.


        Returns:
            dict: a dict containing only those kwargs that make sense
             for the given model_class.
        """
        model_attrs = dir(model_class)
        attrs = [name for name in kwargs if name in model_attrs]
        return {name: kwargs[name] for name in attrs}
