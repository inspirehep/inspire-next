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

from itertools import izip

from flask_cache import make_template_fragment_key


class JinjaCacheInvalidator(object):
    """Class which helps to invalidate Jinja caches for certain templates."""
    def __init__(self, cache):
        self.cache_client = cache

    def invalidate(self, template_name, keys):
        """Invalidate template cache for certain keys (e.g. recid of the record)."""

        cache_key = make_template_fragment_key(template_name, vary_on=[str(key) for key in keys])
        self.cache_client.delete(cache_key)

    def invalidate_many(self, template_names, keys):
        """Invalidate many template cache for certain keys (e.g. recids of the records)."""

        assert len(template_names) == len(keys)
        cache_keys = []
        for i, template_name in enumerate(template_names):
            cache_keys.append(make_template_fragment_key(template_name, vary_on=[str(key) for key in keys[i]]))
        self.cache_client.delete_many(*cache_keys)

    def invalidate_all_of_certain_type(self, template_name):
        """Invalidate all cache for certain template and delete it from Redis."""
        template_key_base = make_template_fragment_key(template_name)
        lua_script = "local keys = redis.call('KEYS', '*{0}_*') if #keys > 0 " \
                     "then redis.call('DEL', unpack(keys)) end return #keys"\
            .format(template_key_base)
        lua_cleaner = self.cache_client.cache._client.register_script(lua_script)
        how_many_invalidated = lua_cleaner()

        return how_many_invalidated


class CachedInvalidator(object):
    """Class which helps to invalidate cached function decorated with flask_cache.cache.cached()."""
    def __init__(self, cache):
        self.cache_client = cache

    def invalidate(self, function_reference, *args, **kwargs):
        """Invalidate cached function passed by reference."""
        cache_key = function_reference.make_cache_key()
        self.cache_client.delete(cache_key)


class MemoizedInvalidator(object):
    """Class which helps to invalidate memoized function."""
    def __init__(self, cache):
        self.cache_client = cache

    def invalidate(self, function_reference, *args, **kwargs):
        """Invalidate memoized function for one set of arguments (e.g. recid and collection)."""

        if args is not None:
            self.cache_client.delete_memoized(function_reference, *args, **kwargs)

    def invalidate_many(self, function_references, *args, **kwargs):
        """Invalidate memoized function for many sets of arguments (e.g. recids and collections)."""

        if args is not None:
            how_many = len(function_references)
            for argument_values in args:
                assert len(argument_values) == how_many

            for arguments in izip(function_references, *args):
                self.cache_client.delete_memoized(*arguments)

    def invalidate_all_of_certain_type(self, function_reference):
        """Invalidate all cache for memoized function and delete it from Redis."""

        # get the current hash for the memoized function; the hash will change after deleting all keys of this function
        old_hash = self.cache_client._memoize_version(function_reference)

        # change hash
        self.cache_client.delete_memoized(function_reference)

        # delete all keys connected with memoized function left in Redis
        lua_script = "local keys = redis.call('KEYS', '*{0}') if #keys > 0 then redis.call('DEL', unpack(keys)) end" \
                     "return #keys".format(old_hash[1])
        lua_cleaner = self.cache_client.cache._client.register_script(lua_script)
        how_many_invalidated = lua_cleaner()

        return how_many_invalidated
