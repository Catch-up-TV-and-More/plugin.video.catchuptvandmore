# -*- coding: utf-8 -*-
# Copyright: (c) 2018, SylvainCecchetto
# GNU General Public License v2.0+ (see LICENSE.txt or https://www.gnu.org/licenses/gpl-2.0.txt)

# This file is part of Catch-up TV & More

from __future__ import unicode_literals

import json
import re

import urlquick
from codequick import Resolver, Script

PATTERN_M3U8 = re.compile(r'https?://[^\s]+\.m3u8')
URL_CHANNEL_CONFIG_JS = 'https://%s-static.cgtn.com/w/vendors/channel-config.js'
URL_LIVE_JSON = 'https://news.cgtn.com/tv/channel-%s.json'

@Resolver.register
def get_live_url(plugin, item_id, **kwargs):
    final_language = kwargs.get('language', Script.setting['cgtn.language'])

    json_url = None
    channel_config_url = None
    if item_id == 'cgtndocumentary':
        json_url = URL_LIVE_JSON % 'doc'
    elif final_language == 'EN':
        json_url = URL_LIVE_JSON % 'en'
    elif final_language == 'FR':
        channel_config_url = URL_CHANNEL_CONFIG_JS % 'francais'
    elif final_language == 'AR':
        channel_config_url = URL_CHANNEL_CONFIG_JS % 'arabic'
    elif final_language == 'ES':
        channel_config_url = URL_CHANNEL_CONFIG_JS % 'espanol'
    elif final_language == 'RU':
        channel_config_url = URL_CHANNEL_CONFIG_JS % 'russian'

    if json_url:
        json_data = json.loads(urlquick.get(json_url, max_age=-1).text)
        return json_data.get('data')[0]
    elif channel_config_url:
        text = urlquick.get(channel_config_url, max_age=-1).text
        text = re.sub(r'^// .*\n', '', text, flags=re.MULTILINE) # Remove commented out m3u8
        m3u8_array = PATTERN_M3U8.findall(text)
        return m3u8_array[0]

    return None
