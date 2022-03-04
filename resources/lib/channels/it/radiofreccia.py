# -*- coding: utf-8 -*-
# Copyright: (c) 2016-2020, Team Catch-up TV & More
# GNU General Public License v2.0+ (see LICENSE.txt or https://www.gnu.org/licenses/gpl-2.0.txt)

# This file is part of Catch-up TV & More

from __future__ import unicode_literals

import json
import re

import sys

if sys.version_info.major >= 3 and sys.version_info.minor >= 4:
    import html as html_parser
elif sys.version_info.major >= 3:
    import html.parser

    html_parser = html.parser.HTMLParser()
else:
    import HTMLParser

    html_parser = HTMLParser.HTMLParser()

import urlquick
from codequick import Resolver

PATTERN = re.compile(r'data-media-object="(.*?)"')
URL_LIVE = "https://play.rtl.it/live/17/radiofreccia-radiovisione/"


@Resolver.register
def get_live_url(plugin, item_id, **kwargs):
    resp = urlquick.get(URL_LIVE)
    media_objects = PATTERN.findall(resp.text)
    if len(media_objects) == 0:
        return False
    media_object = html_parser.unescape(media_objects[0])
    json_media_object = json.loads(media_object)

    return json_media_object['mediaInfo']['uri']
