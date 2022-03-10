# -*- coding: utf-8 -*-
# Copyright: (c) 2017, SylvainCecchetto
# GNU General Public License v2.0+ (see LICENSE.txt or https://www.gnu.org/licenses/gpl-2.0.txt)

# This file is part of Catch-up TV & More

from __future__ import unicode_literals

import re
from builtins import str

import inputstreamhelper
import urlquick
from codequick import Listitem, Resolver, Route

from resources.lib import download
from resources.lib.kodi_utils import (INPUTSTREAM_PROP, get_selected_item_art,
                                      get_selected_item_info,
                                      get_selected_item_label, get_kodi_version)
from resources.lib.menu_utils import item_post_treatment

# "https://tvlux.fcst.tv/player/embed/3426115.js"
PATTERN_PLAYER = re.compile(r'"(https://.*?/player/embed/.*?.js.*?)"')

# \"src\":[\"https:\\\/\\\/tvlux-live.freecaster.com\\\/live\\\/tvlux\\\/tvlux.m3u8\"]
PATTERN_M3U8 = re.compile(r'https?:[^,]*?.m3u8')

URL_ROOT = 'https://www.tvlux.be'

URL_LIVE = URL_ROOT + '/live'

URL_VIDEOS = URL_ROOT + '/videos'

URL_EMISSIONS = URL_ROOT + '/emissions'

URL_LIVE_DATAS = 'https://player.freecaster.com/embed/%s.js'


@Route.register
def list_categories(plugin, item_id, **kwargs):
    """
    Build categories listing
    - Tous les programmes
    - Séries
    - Informations
    - ...
    """
    item = Listitem()
    item.label = plugin.localize(30701)
    item.set_callback(list_videos,
                      item_id=item_id,
                      next_url=URL_VIDEOS,
                      page='0')
    item_post_treatment(item)
    yield item

    item = Listitem()
    item.label = plugin.localize(30717)
    item.set_callback(list_programs, item_id=item_id)
    item_post_treatment(item)
    yield item


@Route.register
def list_programs(plugin, item_id, **kwargs):
    resp = urlquick.get(URL_EMISSIONS)
    root = resp.parse()

    for program_datas in root.iterfind(".//div[@class='col-sm-4']"):
        program_title = program_datas.find('.//img').get('alt')
        program_image = program_datas.find('.//img').get('src')
        program_url = URL_ROOT + '/' + program_datas.find(".//a").get("href")

        item = Listitem()
        item.label = program_title
        item.art['thumb'] = item.art['landscape'] = program_image
        item.set_callback(list_videos,
                          item_id=item_id,
                          next_url=program_url,
                          page='0')
        item_post_treatment(item)
        yield item


@Route.register
def list_videos(plugin, item_id, next_url, page, **kwargs):
    resp = urlquick.get(next_url + '?lim_un=%s' % page)
    root = resp.parse()

    for video_datas in root.iterfind(".//div[@class='col-sm-4']"):
        video_title = video_datas.find('.//h3').text
        video_image = video_datas.find('.//img').get('src')
        video_url = video_datas.find('.//a').get('href')

        item = Listitem()
        item.label = video_title
        item.art['thumb'] = item.art['landscape'] = video_image

        item.set_callback(get_video_url,
                          item_id=item_id,
                          video_url=video_url)
        item_post_treatment(item, is_playable=True, is_downloadable=True)
        yield item

    yield Listitem.next_page(item_id=item_id,
                             next_url=next_url,
                             page=str(int(page) + 12))


@Resolver.register
def get_video_url(plugin,
                  item_id,
                  video_url,
                  download_mode=False,
                  **kwargs):
    resp = urlquick.get(video_url, max_age=-1)
    list_streams_datas = re.compile(
        r'source src=\"(.*?)\"').findall(resp.text)
    stream_url = ''
    for stream_datas in list_streams_datas:
        if 'm3u8' in stream_datas or \
                'mp4' in stream_datas:
            stream_url = stream_datas

    if download_mode:
        return download.download_video(stream_url)
    return stream_url


@Resolver.register
def get_live_url(plugin, item_id, **kwargs):
    resp = urlquick.get(URL_LIVE, max_age=-1)
    found_players = PATTERN_PLAYER.findall(resp.text)
    if len(found_players) == 0:
        plugin.notify(plugin.localize(30600), plugin.localize(30716))
        return False

    resp2 = urlquick.get(found_players[0], max_age=-1)
    found_m3u8_objects = PATTERN_M3U8.findall(resp2.text)
    if len(found_m3u8_objects) == 0:
        plugin.notify(plugin.localize(30600), plugin.localize(30716))
        return False
    url = found_m3u8_objects[0].replace('\\', '')

    if get_kodi_version() < 18:
        return url

    is_helper = inputstreamhelper.Helper("mpd")
    if not is_helper.check_inputstream():
        return url

    item = Listitem()
    item.path = url
    item.property[INPUTSTREAM_PROP] = "inputstream.adaptive"
    item.property["inputstream.adaptive.manifest_type"] = "hls"
    item.label = get_selected_item_label()
    item.art.update(get_selected_item_art())
    item.info.update(get_selected_item_info())
    return item
