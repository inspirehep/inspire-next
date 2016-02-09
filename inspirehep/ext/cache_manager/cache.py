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

import functools

from flask import current_app, request

from flask_cache import Cache


class InspireCache(Cache):
    """Extends Cache from Flask Cache and adds mode-checking (debug or not) for memoize and cached methods.

    The parameters in both inspire_memoize and inspire_cached are the same
    as the parameters of the original methods in Flask Cache class

    """

    def inspire_memoize(self, timeout=None, make_name=None, unless=None):
        def memoize(f):
            @functools.wraps(f)
            def decorated_function(*args, **kwargs):
                if not current_app.debug:
                    #: bypass cache
                    if callable(unless) and unless() is True:
                        return f(*args, **kwargs)

                    try:
                        cache_key = decorated_function.make_cache_key(f, *args, **kwargs)
                        rv = self.cache.get(cache_key)
                    except Exception:
                        if current_app.debug:
                            raise
                        current_app.logger.exception("Exception possibly due to cache backend.")
                        return f(*args, **kwargs)

                    if rv is None:
                        rv = f(*args, **kwargs)
                        try:
                            self.cache.set(cache_key, rv, timeout=decorated_function.cache_timeout)
                        except Exception:
                            if current_app.debug:
                                raise
                            current_app.logger.exception("Exception possibly due to cache backend.")
                    return rv
                else:
                    rv = f(*args, **kwargs)
                    return rv

            decorated_function.uncached = f
            decorated_function.cache_timeout = timeout
            decorated_function.make_cache_key = self._memoize_make_cache_key(make_name, decorated_function)
            decorated_function.delete_memoized = lambda: self.delete_memoized(f)

            return decorated_function
        return memoize

    def inspire_cached(self, timeout=None, key_prefix='view/%s', unless=None):
        def decorator(f):
            @functools.wraps(f)
            def decorated_function(*args, **kwargs):
                if not current_app.debug:
                    #: Bypass the cache entirely.
                    if callable(unless) and unless() is True:
                        return f(*args, **kwargs)

                    try:
                        cache_key = decorated_function.make_cache_key(*args, **kwargs)
                        rv = self.cache.get(cache_key)
                    except Exception:
                        if current_app.debug:
                            raise
                        current_app.logger.exception("Exception possibly due to cache backend.")
                        return f(*args, **kwargs)

                    if rv is None:
                        rv = f(*args, **kwargs)
                        try:
                            self.cache.set(cache_key, rv, timeout=decorated_function.cache_timeout)
                        except Exception:
                            if current_app.debug:
                                raise
                            current_app.logger.exception("Exception possibly due to cache backend.")
                            return f(*args, **kwargs)
                    return rv
                else:
                    rv = f(*args, **kwargs)
                    return rv

            def make_cache_key(*args, **kwargs):
                if callable(key_prefix):
                    cache_key = key_prefix()
                elif '%s' in key_prefix:
                    cache_key = key_prefix % request.path
                else:
                    cache_key = key_prefix

                return cache_key

            decorated_function.uncached = f
            decorated_function.cache_timeout = timeout
            decorated_function.make_cache_key = make_cache_key

            return decorated_function
        return decorator


inspire_cache = InspireCache()

__all__ = ['inspire_cache', 'setup_app']


def setup_app(app):
    """Setup cache extension."""

    app.config.setdefault('CACHE_TYPE',
                          app.config.get('CFG_FLASK_CACHE_TYPE', 'redis'))
    # if CACHE_KEY_PREFIX is not specified then CFG_DATABASE_NAME:: is used.
    prefix = app.config.get('CFG_DATABASE_NAME', '')
    if prefix:
        prefix += '::'
    app.config.setdefault('CACHE_KEY_PREFIX', prefix)
    inspire_cache.init_app(app)
    return app
