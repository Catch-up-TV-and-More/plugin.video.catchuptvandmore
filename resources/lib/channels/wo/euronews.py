# -*- coding: utf-8 -*-
# Copyright: (c) 2017, SylvainCecchetto
# GNU General Public License v2.0+ (see LICENSE.txt or https://www.gnu.org/licenses/gpl-2.0.txt)

# This file is part of Catch-up TV & More

from __future__ import unicode_literals
import json

# noinspection PyUnresolvedReferences
from codequick import Resolver, Script
import urlquick

from resources.lib import resolver_proxy

# TODO
# Replay add emissions

URL_LIVE_API = 'https://api.euronews.com/v2/apps/androidPhoneEuronews-6.3/languages/%s/livestream/%s'

@Resolver.register
def get_live_url(plugin, item_id, **kwargs):
    final_language = kwargs.get('language', Script.setting['euronews.language'])
    lang = final_language.lower()
    url_live_json = URL_LIVE_API % (lang, lang)
    json_parser = urlquick.get(url_live_json, max_age=-1).json()
    video_url = json_parser['primary']

    item = resolver_proxy.__get_non_ia_stream_with_quality(plugin, video_url)
    item.path = video_url

    return item
