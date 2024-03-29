# -*- coding: utf-8 -*-
# Copyright: (c) 2018, SylvainCecchetto
# GNU General Public License v2.0+ (see LICENSE.txt or https://www.gnu.org/licenses/gpl-2.0.txt)

# This file is part of Catch-up TV & More

from __future__ import unicode_literals
import re
import json

from codequick import Listitem, Resolver, Route
import urlquick

from resources.lib import download
from resources.lib.menu_utils import item_post_treatment
from resources.lib import resolver_proxy, web_utils


# TODO

URL_ROOT = 'https://www.%s.bzh'

URL_LIVE = URL_ROOT + '/direct'

URL_REPLAY = URL_ROOT + '/le-replay'

URL_STREAM = URL_ROOT + '/player.php?idprogramme=%s'

ULTRAMEDIA_API = 'https://www.ultimedia.com/api/widget/smart?'

GENERIC_HEADERS = {'User-Agent': web_utils.get_random_ua()}


@Route.register
def list_categories(plugin, item_id, **kwargs):
    """
    Build categories listing
    - Tous les programmes
    - Séries
    - Informations
    - ...
    """
    resp = urlquick.get(URL_REPLAY % item_id)
    if 'tebeo' in item_id:
        root = resp.parse("div", attrs={"class": "grid_12"})
    else:
        root = resp.parse("div", attrs={"class": "grid_16"})

    for category_datas in root.iterfind(".//li"):
        category_name = category_datas.find('.//a').text
        category_url = 'https:' + category_datas.find('.//a').get('href')

        item = Listitem()
        item.label = category_name
        item.set_callback(list_videos, item_id=item_id, category_url=category_url)
        item_post_treatment(item)
        yield item


@Route.register
def list_videos(plugin, item_id, category_url, **kwargs):

    resp = urlquick.get(category_url, headers=GENERIC_HEADERS, max_age=-1)
    root = resp.parse()
    list_videos_datas = root.findall(".//div[@class='grid_8 replay']")
    list_videos_datas += root.findall(".//div[@class='grid_4 replay']")

    for video_datas in list_videos_datas:
        video_title = video_datas.find('.//h3').text
        video_image = 'https:' + video_datas.find('.//img').get('src')
        video_url = 'https:' + video_datas.find('.//a').get('href')
        date_value = video_datas.find('.//p').text.split(' ')[0]

        item = Listitem()
        item.label = video_title
        item.art['thumb'] = item.art['landscape'] = video_image
        item.info.date(date_value, '%Y-%m-%d')

        item.set_callback(get_video_url, item_id=item_id, video_url=video_url)
        item_post_treatment(item, is_playable=True, is_downloadable=True)
        yield item


@Resolver.register
def get_video_url(plugin,
                  item_id,
                  video_url,
                  download_mode=False,
                  **kwargs):

    resp = urlquick.get(video_url, headers=GENERIC_HEADERS, max_age=-1)
    video_id = re.compile(r'idprogramme\=(.*?)\&autoplay').findall(resp.text)[0]
    resp2 = urlquick.get(URL_STREAM % (item_id, video_id))

    video_url = 'https:' + re.compile(r'source\: \"(.*?)\"').findall(resp2.text)[0]

    if download_mode:
        return download.download_video(video_url)
    return resolver_proxy.get_stream_with_quality(plugin, video_url)


@Resolver.register
def get_live_url(plugin, item_id, **kwargs):

    resp = urlquick.get(URL_LIVE % item_id, max_age=-1)
    root = resp.text
    mdtk = re.compile(r'ULTIMEDIA_mdtk \= \"(.*?)\"').findall(root)[0]
    zone = re.compile(r'ULTIMEDIA_zone \= \"(.*?)\"').findall(root)[0]

    params = {
        'mdtk': mdtk,
        'zone': zone
    }
    url_frame = urlquick.get(ULTRAMEDIA_API, headers=GENERIC_HEADERS, params=params, max_age=-1)
    url_player = re.compile(r'iframe src\=\\\"(.*?)\&width').findall(url_frame.text)[0]

    player = urlquick.get(url_player, headers=GENERIC_HEADERS, max_age=-1)
    data_json = json.loads(re.compile(r'DtkPlayer.init\((.*?)\, \{\"topic').findall(player.text)[0])
    video_url = data_json['video']['media_sources']['live']['src']

    return resolver_proxy.get_stream_with_quality(plugin, video_url)
