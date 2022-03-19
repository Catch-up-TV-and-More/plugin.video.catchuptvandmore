# -*- coding: utf-8 -*-
# Copyright: (c) 2016-2020, Team Catch-up TV & More
# GNU General Public License v2.0+ (see LICENSE.txt or https://www.gnu.org/licenses/gpl-2.0.txt)

# This file is part of Catch-up TV & More

from __future__ import unicode_literals

import json
import re
import urlquick
import inputstreamhelper
from codequick import Listitem, Resolver, Script
from kodi_six import xbmcgui
import sys
from resources.lib.kodi_utils import (INPUTSTREAM_PROP, get_selected_item_art,
                                      get_selected_item_info,
                                      get_selected_item_label, get_kodi_version)

if sys.version_info.major >= 3 and sys.version_info.minor >= 4:
    import html as html_parser
elif sys.version_info.major >= 3:
    import html.parser

    html_parser = html.parser.HTMLParser()
else:
    import HTMLParser

    html_parser = HTMLParser.HTMLParser()

PATTERN = re.compile(r'data-media-object="(.*?)"')
# EXT-X-STREAM-INF:BANDWIDTH=1888000,CODECS="avc1.4d481f,mp4a.40.2",RESOLUTION=1024x576
PATTERN_M3U8_QUALITIES = re.compile(r'#EXT-X-STREAM-INF:.*RESOLUTION=([^\n]*)\n(.*\.m3u8)')
URL_LIVE = "https://play.rtl.it/live/17/radiofreccia-radiovisione/"


def get_url_for_quality(plugin, url):
    final_video_url = url
    desired_quality = Script.setting.get_string('quality')
    if desired_quality == "DEFAULT":
        return final_video_url

    resp = urlquick.get(url)
    results = PATTERN_M3U8_QUALITIES.findall(resp.text)

    if len(results) == 0:
        return final_video_url

    all_video_qualities = list(map(lambda x: x[0], results))
    all_videos_urls = list(map(lambda x: x[1], results))

    if desired_quality == "DIALOG":
        selected_item = xbmcgui.Dialog().select(
            plugin.localize(30709),
            all_video_qualities)
        if selected_item == -1:
            return False

        final_video_url = url[:url.rfind('/')] + '/' + all_videos_urls[selected_item]

    elif desired_quality == "BEST":
        max_resolution = 0
        url_best = url
        i = 0
        for data_video in all_video_qualities:
            current_resolution = int(re.sub(r'x\d*', '', data_video))
            if current_resolution > max_resolution:
                max_resolution = current_resolution
                url_best = all_videos_urls[i]
            i = i + 1
        final_video_url = url[:url.rfind('/')] + '/' + url_best

    return final_video_url


@Resolver.register
def get_live_url(plugin, item_id, **kwargs):
    resp = urlquick.get(URL_LIVE)
    media_objects = PATTERN.findall(resp.text)
    if len(media_objects) == 0:
        return False
    media_object = html_parser.unescape(media_objects[0])
    json_media_object = json.loads(media_object)

    url = json_media_object['mediaInfo']['uri']
    if get_kodi_version() < 18:
        return get_url_for_quality(plugin, url)

    is_helper = inputstreamhelper.Helper("mpd")
    if not is_helper.check_inputstream():
        return get_url_for_quality(plugin, url)

    item = Listitem()
    item.path = json_media_object['mediaInfo']['descriptor'][1]["uri"]
    item.property[INPUTSTREAM_PROP] = "inputstream.adaptive"
    item.property["inputstream.adaptive.manifest_type"] = "mpd"
    item.label = get_selected_item_label()
    item.art.update(get_selected_item_art())
    item.info.update(get_selected_item_info())

    return item
