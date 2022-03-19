# -*- coding: utf-8 -*-
# Copyright: (c) 2016-2020, Team Catch-up TV & More
# GNU General Public License v2.0+ (see LICENSE.txt or https://www.gnu.org/licenses/gpl-2.0.txt)

# This file is part of Catch-up TV & More

from __future__ import unicode_literals

import json
import re
import sys

import inputstreamhelper
import urlquick
from codequick import Listitem, Resolver, Route, Script
from kodi_six import xbmcgui

from resources.lib import web_utils
from resources.lib.kodi_utils import (INPUTSTREAM_PROP, get_selected_item_art,
                                      get_selected_item_info,
                                      get_selected_item_label, get_kodi_version)
from resources.lib.menu_utils import item_post_treatment
from resources.lib.addon_utils import get_item_label, get_item_media_path

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

URL_ROOT = "https://play.rtl.it"

DEFAULT_IMAGE = get_item_media_path('channels/it/rtl-1025-radiovisione.png')


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


@Route.register
def list_lives(plugin, item_id, **kwargs):
    root = urlquick.get(URL_ROOT,
                        headers={'User-Agent': web_utils.get_random_ua()},
                        max_age=-1).parse()
    channels = root.findall(".//div[@data-media-type='SectionItem']")

    if len(channels) == 0:
        return False

    for channel in channels:

        live_image = DEFAULT_IMAGE

        live_url_anchor = channel.find('.//a')
        if live_url_anchor is None:
            continue

        live_url = URL_ROOT + live_url_anchor.get('href')

        resp = urlquick.get(live_url)
        media_objects = PATTERN.findall(resp.text)
        if len(media_objects) == 0:
            return False
        media_object = html_parser.unescape(media_objects[0])
        json_media_object = json.loads(media_object)
        live_plot = live_title = json_media_object['mediaInfo']['title']

        style = channel.find('.//img').get('style')
        img_array = re.compile(r'url\((.*)\)').findall(style)
        if len(img_array) > 0:
            live_image = img_array[0]

        on_focus = channel.find(".//div[@class='on-focus-state-info']")
        if on_focus is not None:
            img = on_focus.find(".//img")
            if img is not None:
                live_image = img.get('src')
            live_plot = on_focus.find(".//div[@class='info-title']").text

        item = Listitem()
        item.label = live_title
        item.art['thumb'] = item.art['landscape'] = live_image
        item.info['plot'] = live_plot
        item.set_callback(get_live_url, item_id=item_id, json_media_object=json_media_object)
        item_post_treatment(item, is_playable=True)
        yield item


@Resolver.register
def get_live_url(plugin, json_media_object, **kwargs):
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
