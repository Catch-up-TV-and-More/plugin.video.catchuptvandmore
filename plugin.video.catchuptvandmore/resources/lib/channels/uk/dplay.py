# -*- coding: utf-8 -*-
"""
    Catch-up TV & More
    Copyright (C) 2018  SylvainCecchetto

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
from __future__ import division

from builtins import str
from resources.lib.py_utils import old_div
from codequick import Route, Resolver, Listitem, utils, Script


from resources.lib import web_utils
from resources.lib.kodi_utils import get_kodi_version
from resources.lib import download
from resources.lib.menu_utils import item_post_treatment
from resources.lib.kodi_utils import get_selected_item_art, get_selected_item_label, get_selected_item_info

import inputstreamhelper
import json
import re
import urlquick
from kodi_six import xbmc
from kodi_six import xbmcgui

# TO DO

URL_ROOT = 'https://www.dplay.co.uk'

URL_LIVE = URL_ROOT + '/api/channel-playback/%s'

URL_LICENCE_KEY = 'https://lic.caas.conax.com/nep/wv/license|Content-Type=&User-Agent=Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3041.0 Safari/537.36&PreAuthorization=%s&Host=lic.caas.conax.com|R{SSM}|'
# videoId


@Resolver.register
def get_live_url(plugin, item_id, **kwargs):

    if get_kodi_version() < 18:
        xbmcgui.Dialog().ok('Info', plugin.localize(30602))
        return False

    is_helper = inputstreamhelper.Helper('mpd', drm='widevine')
    if not is_helper.check_inputstream():
        return False

    resp = urlquick.get(URL_LIVE % item_id, max_age=-1)

    if len(re.compile(r'drmToken\"\:\"(.*?)\"').findall(resp.text)) > 0:
        token = re.compile(r'drmToken\"\:\"(.*?)\"').findall(resp.text)[0]
        if len(re.compile(r'streamUrlDash\"\:\"(.*?)\"').findall(
                resp.text)) > 0:
            live_url = re.compile(r'streamUrlDash\"\:\"(.*?)\"').findall(
                resp.text)[0]

            item = Listitem()
            item.path = live_url
            item.label = get_selected_item_label()
            item.art.update(get_selected_item_art())
            item.info.update(get_selected_item_info())
            item.property['inputstreamaddon'] = 'inputstream.adaptive'
            item.property['inputstream.adaptive.manifest_type'] = 'mpd'
            item.property[
                'inputstream.adaptive.license_type'] = 'com.widevine.alpha'
            item.property[
                'inputstream.adaptive.license_key'] = URL_LICENCE_KEY % token
            return item
    plugin.notify('ERROR', plugin.localize(30713))
    return False
