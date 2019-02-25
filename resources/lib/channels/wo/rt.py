# -*- coding: utf-8 -*-
"""
    Catch-up TV & More
    Copyright (C) 2019  SylvainCecchetto

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

# The unicode_literals import only has
# an effect on Python 2.
# It makes string literals as unicode like in Python 3
from __future__ import unicode_literals

from codequick import Route, Resolver, Listitem, utils, Script

from resources.lib.labels import LABELS
from resources.lib import web_utils
from resources.lib import resolver_proxy

import re
import urlquick

# TO DO
# Replay add emissions

URL_LIVE_FR = 'https://francais.rt.com/en-direct'

URL_LIVE_EN = 'https://www.rt.com/on-air/'

URL_LIVE_AR = 'https://arabic.rt.com/live/'

URL_LIVE_ES = 'https://actualidad.rt.com/en_vivo'


def live_entry(plugin, item_id, item_dict):
    return get_live_url(plugin, item_id, item_id.upper(), item_dict)


@Resolver.register
def get_live_url(plugin, item_id, video_id, item_dict):

    desired_language = Script.setting[item_id + '.language']

    if desired_language == 'EN':
        url_live = URL_LIVE_EN
        resp = urlquick.get(url_live, max_age=-1)
        return re.compile(
            r'file\: \'(.*?)\'').findall(resp.text)[0]
    elif desired_language == 'AR':
        url_live = URL_LIVE_AR
        resp = urlquick.get(url_live, max_age=-1)
        return re.compile(
            r'file\'\: \'(.*?)\'').findall(resp.text)[0]
    elif desired_language == 'FR':
        url_live = URL_LIVE_FR
        resp = urlquick.get(url_live, max_age=-1)
        return re.compile(
            r'file\: \"(.*?)\"').findall(resp.text)[0]
    elif desired_language == 'ES':
        url_live = URL_LIVE_ES
        resp = urlquick.get(url_live, max_age=-1)
        live_id = re.compile(
            r'youtube\.com\/embed\/(.*?)\?').findall(resp.text)[0]
        return resolver_proxy.get_stream_youtube(plugin, live_id, False)
