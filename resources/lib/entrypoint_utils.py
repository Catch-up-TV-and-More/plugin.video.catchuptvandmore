# -*- coding: utf-8 -*-
"""
    Catch-up TV & More
    Copyright (C) 2016  SylvainCecchetto

    This file is part of Catch-up TV & More.

    Catch-up TV & More is free software; you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation; either version 2 of the License, or
    (at your option) any later version.

    Catch-up TV & More is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License along
    with Catch-up TV & More; if not, write to the Free Software Foundation,
    Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
"""

from __future__ import unicode_literals

import sys
import pickle
import binascii
import importlib

from codequick.utils import parse_qs
from codequick import Script


def get_params_in_query(query_string):
    """Get parameters dict from Kodi query (sys.argv[2])

    Args:
        query_string (str): Query string passed to the addon (e.g. ?foo=bar&baz=quux)
    Returns:
        dict: Paramters found in the query string
    """

    params = parse_qs(query_string)

    # Unpickle pickled data
    if "_pickle_" in params:
        unpickled = pickle.loads(binascii.unhexlify(params.pop("_pickle_")))
        params.update(unpickled)

    return params


def get_module_in_query(query_string):
    """Get module from Kodi query (sys.argv[2]) in CodeQuick special case (Search feature)

    Args:
        query_string (str): Query string passed to the addon (e.g. ?foo=bar&baz=quux)
    Returns:
        str: Module to load after the Search window (e.g. resources.lib.channels.fr.francetv)
    """

    module = ''
    params = get_params_in_query(query_string)
    # '_route': u'/resources/lib/channels/fr/francetv/list_videos_search/'
    if '_route' in params:
        base_url = params['_route']
        # Remove last '/'
        if base_url[-1] == '/':
            base_url = base_url[:-1]

        # Remove first '/'
        if base_url[0] == '/':
            base_url = base_url[1:]

        base_url_l = base_url.split('/')
        module_l = []
        for word in base_url_l:
            module_l.append(word)

        module_l.pop()  # Pop the function name (e.g. list_videos_search)
        module = '.'.join(module_l)
        # Returned module: resources.lib.channels.fr.francetv

    return module


def get_module_in_url(base_url):
    """Get module from Kodi base URL (sys.argv[0])

    Args:
        base_url (str): Base URL string passed to the addon (e.g. plugin://plugin.video.catchuptvandmore/resources/lib/websites/culturepub/list_shows)
    Returns:
        str: Module found in the base URL (e.g. resources.lib.websites.culturepub)
    """

    if 'resources' not in base_url:
        return 'resources.lib.main'

    # Remove last '/'
    if base_url[-1] == '/':
        base_url = base_url[:-1]

    # Remove plugin_id
    base_url = base_url.replace('plugin://plugin.video.catchuptvandmore/', '')

    base_url_l = base_url.split('/')
    module_l = []
    for word in base_url_l:
        module_l.append(word)

    module_l.pop()  # Pop the function name (e.g. list_shows)
    module = '.'.join(module_l)

    return module


def import_needed_module():
    """Import needed module according to the Kodi base URL and query string

    """

    modules_to_import = [get_module_in_url(sys.argv[0])]
    if 'codequick/search' in sys.argv[0]:
        modules_to_import.append(get_module_in_query(sys.argv[2]))
    for module_to_import in modules_to_import:
        if module_to_import == '':
            # No additionnal module to load
            continue

        # Need to load additional module
        try:
            Script.log('[import_needed_module] Import module {} on the fly'.format(module_to_import), lvl=Script.INFO)
            importlib.import_module(module_to_import)
        except Exception:
            Script.log('[import_needed_module] Failed to import module {} on the fly'.format(module_to_import), lvl=Script.WARNING)
