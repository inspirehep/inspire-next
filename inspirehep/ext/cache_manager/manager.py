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

from flask import current_app

from werkzeug.utils import import_string

from .utils import CachedInvalidator, JinjaCacheInvalidator, MemoizedInvalidator


class InspireCacheManager(object):
    """Class designed to invalidate different types of cache (all types provided by Flask Cache)
     with Redis as the cache backend"""

    def __init__(self, app=None, cache=None, views={}):
        """
            Parameters
        ----------
        app : Flask application object
        cache : Flask Cache object
        views : dict
            Views being cached by cache (Flask Cache object). See the 'views' dict sample below:
            {
                'main_page': {
                    'type': 'cached',
                    'function_reference': 'app.views.main_view'
                },

                'view_with_have_calculations': {
                    'type': 'memoize',
                    'function_reference': 'app.views.extremely_heavy_view'
                },

                'view_done_with_jinja': {
                    'type': 'jinja_cache',
                    'template_name': 'jinja_view',
                    'kwargs': ['view_ID']
                }
            }

            Each view should have 'type' of either 'cached', 'memoize' or 'jinja_cache' value
            (three types of cache provided by Flask Cache).

            For 'cached' and 'memoized' the field 'function_reference' has to be also defined.

            For 'jinja_cache' two extra fields need to be defined:
                - 'template_name' which is the name associated with the cached template
                - 'kwargs' is the list of key_arguments names used to parametrize cached template
                    e.g. view_id, index etc.

        """
        self.jinja_invalidator = JinjaCacheInvalidator(cache)
        self.memoized_invalidator = MemoizedInvalidator(cache)
        self.cached_invalidator = CachedInvalidator(cache)
        self.cache_client = cache
        self.app = app
        self.views = None
        if app is not None:
            self.init_app(app)

    def init_app(self, app, cache):

        if app:
            if not hasattr(app, 'extensions'):
                app.extensions = {}

            if self.cache_client is None:
                self.cache_client = cache
                self.jinja_invalidator = JinjaCacheInvalidator(cache)
                self.memoized_invalidator = MemoizedInvalidator(cache)
                self.cached_invalidator = CachedInvalidator(cache)

            self.views = app.config.get('CACHED_VIEWS')
            for view in self.views:
                if self.views[view]['type'] in ['memoize', 'cached']:
                    try:
                        self.views[view]['function_reference'] = import_string(
                            self.views[view]['function_reference'])
                    except ImportError:
                        current_app.logger.exception('Function reference {0} does not exist or is a method of a class '
                                                     '(not supported)'.format(self.views[view]['function_reference']))

        app.extensions['cache_manager.manager'] = self

    def invalidate_view(self, view_name, *args, **kwargs):
        """Invalidate view with certain name and arguments (e.g. recid, index etc.)"""
        view_details = self.views.get(view_name)
        if view_details:
            if view_details['type'] == 'jinja_cache':
                self.jinja_invalidator.invalidate(view_details['template_name'],
                                                  keys=[kwargs[keyarg] for keyarg in view_details['kwargs']
                                                        if kwargs.get(keyarg)])
            elif view_details['type'] == 'cached':
                self.cached_invalidator.invalidate(view_details['function_reference'])
            elif view_details['type'] == 'memoize':
                self.memoized_invalidator.invalidate(view_details['function_reference'], *args, **kwargs)
        else:
            current_app.logger.exception('View name not found. Please add it to config file.')

    def invalidate_all_certain_views(self, view_name):
        """Invalidate all views with certain name."""

        view_details = self.views.get(view_name)
        if view_details:
            if view_details['type'] == 'jinja_cache':
                how_many = self.jinja_invalidator.invalidate_all_of_certain_type(view_details['template_name'])
            elif view_details['type'] == 'cached':
                self.cached_invalidator.invalidate(view_details['function_reference'])
                how_many = 1
            elif view_details['type'] == 'memoize':
                how_many = self.memoized_invalidator.invalidate_all_of_certain_type(view_details['function_reference'])
            return how_many
        else:
            current_app.logger.exception('View name not found. Please add it to config file.')

    def invalidate_all_cached_views(self):
        """Invalidate all cached views."""
        how_many_invalidated = 0
        for view in self.views:
            how_many_invalidated += self.invalidate_all_certain_views(view)
        return how_many_invalidated


def setup_app(app):
    from inspirehep.ext.cache_manager.cache import inspire_cache
    cache_manager = InspireCacheManager()
    cache_manager.init_app(app, inspire_cache)
