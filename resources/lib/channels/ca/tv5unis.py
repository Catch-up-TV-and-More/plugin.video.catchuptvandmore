# -*- coding: utf-8 -*-
"""
    Catch-up TV & More
    Copyright (C) 2017  SylvainCecchetto

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

from builtins import str
from codequick import Route, Resolver, Listitem, utils, Script

from resources.lib.labels import LABELS
from resources.lib import web_utils
from resources.lib import download
from resources.lib.menu_utils import item_post_treatment

import htmlement
import json
import re
import urlquick
from kodi_six import xbmc

# TO DO
# Info Videos (date, plot, etc ...)

URL_ROOT = 'https://www.tv5unis.ca'
# Channel Name

# https://www.tv5unis.ca/videos/canot-cocasse/saisons/4/episodes/8
URL_STREAM_SEASON_EPISODE = URL_ROOT + '/videos/%s/saisons/%s/episodes/%s'
# slug_video, number_season, episode_number
URL_STREAM = URL_ROOT + '/videos/%s'
# slug_video

def replay_entry(plugin, item_id, **kwargs):
    """
    First executed function after replay_bridge
    """
    return list_categories(plugin, item_id)


@Route.register
def list_categories(plugin, item_id, **kwargs):
    """
    Build categories listing
    - Tous les programmes
    - Séries
    - Informations
    - ...
    """
    resp = urlquick.get(URL_ROOT)
    json_datas = re.compile(
        r'\/json\"\>\{(.*?)\}\<\/script\>').findall(resp.text)[0]
    json_parser = json.loads('{' + json_datas + '}')
    
    json_entry = json_parser["props"]["apolloState"]
    for json_key in list(json_entry.keys()):
        if "__typename" in json_entry[json_key]:
            if "ProductSet" in json_entry[json_key]["__typename"]:
                if "slug" in json_entry[json_key]:
                    category_title = json_entry[json_key]["title"]
                    category_slug = json_entry[json_key]["slug"]

                    item = Listitem()
                    item.label = category_title
                    item.set_callback(list_programs, item_id=item_id, category_slug=category_slug)
                    item_post_treatment(item)
                    yield item


@Route.register
def list_programs(plugin, item_id, category_slug, **kwargs):

    resp = urlquick.get(URL_ROOT)
    json_datas = re.compile(
        r'\/json\"\>\{(.*?)\}\<\/script\>').findall(resp.text)[0]
    json_parser = json.loads('{' + json_datas + '}')
    
    json_entry = json_parser["props"]["apolloState"]
    for json_key in list(json_entry.keys()):
        if "__typename" in json_entry[json_key]:
            if "ProductSet" in json_entry[json_key]["__typename"]:
                if "slug" in json_entry[json_key]:
                    if category_slug in json_entry[json_key]["slug"]:
                        for item_data in json_entry[json_key]["items"]:
                            productset_id = item_data["id"]
                            product_id = json_entry[productset_id]["product"]["id"]

                            product_slug_id = ''
                            if json_entry[product_id]['collection'] is not None:
                                product_slug_id = json_entry[product_id]['collection']['id']
                                program_title = json_entry[product_slug_id]['title'] + \
                                    ' - ' + json_entry[product_id]["title"]
                            else:
                                program_title = json_entry[product_id]["title"]

                            program_image_id = json_entry[product_id]["mainLandscapeImage"]["id"]
                            program_image = json_entry[program_image_id]["url"]
                            program_plot = json_entry[product_id]["shortSummary"]
                            program_type = json_entry[product_id]["productType"]
                            

                            item = Listitem()
                            item.label = program_title
                            item.art['thumb'] = program_image
                            item.info['plot'] = program_plot
                            if 'EPISODE' in program_type or 'MOVIE' in program_type:
                                isVideo = False
                                if json_entry[product_id]['slug'] is not None:
                                    video_slug = json_entry[product_id]['slug']
                                    isVideo = True
                                elif json_entry[product_id]['collection'] is not None:
                                    video_slug = json_entry[product_slug_id]['slug']
                                    isVideo = True
                                if isVideo == True:
                                    video_season_number = ''
                                    if json_entry[product_id]["seasonNumber"] is not None:
                                        video_season_number = str(json_entry[product_id]["seasonNumber"])
                                    video_episode_number = ''
                                    if json_entry[product_id]["episodeNumber"] is not None:
                                        video_episode_number = str(json_entry[product_id]["episodeNumber"])
                                    item.set_callback(
                                        get_video_url,
                                        item_id=item_id,
                                        video_slug=video_slug,
                                        video_season_number=video_season_number,
                                        video_episode_number=video_episode_number)
                                    item_post_treatment(item)
                            else:
                                # TODO
                                program_id = ''
                                item.set_callback(list_videos, item_id=item_id, program_id=program_id)
                                item_post_treatment(item)
                            yield item


@Route.register
def list_videos(plugin, item_id, program_id, **kwargs):

    return False
    # if 'theme' in next_id:
    #     param_id = 'theme'
    # else:
    #     param_id = 'serie'

    # resp = urlquick.get(URL_VIDEOS % (item_id, param_id, next_id, page))
    # root = resp.parse("div", attrs={"class": "listing-carousel-inner"})

    # for video_datas in root.iterfind(".//div[@class='media-thumb  ']"):
    #     if video_datas.find('a'):
    #         video_title = video_datas.find('.//img').get('alt')
    #         video_image = video_datas.find('.//img').get('data-src')
    #         video_url = URL_ROOT % item_id + video_datas.find('.//a').get(
    #             'href')

    #         item = Listitem()
    #         item.label = video_title
    #         item.art['thumb'] = video_image

    #         item.set_callback(get_video_url,
    #                           item_id=item_id,
    #                           video_url=video_url)
    #         item_post_treatment(item, is_playable=True, is_downloadable=True)
    #         yield item

    # yield Listitem.next_page(item_id=item_id,
    #                          next_id=next_id,
    #                          page=str(int(page) + 1))


@Resolver.register
def get_video_url(plugin,
                  item_id,
                  video_slug,
                  video_season_number,
                  video_episode_number,
                  download_mode=False,
                  **kwargs):

    if video_season_number == '':
        resp = urlquick.get(URL_STREAM % video_slug)
    else:
        resp = urlquick.get(
            URL_STREAM_SEASON_EPISODE % (
            video_slug, video_season_number, video_episode_number))
    list_urls = re.compile(
        r'url\"\:\"(.*?)\"').findall(resp.text)
    
    streamurl = ''
    for url_m3u8 in list_urls:
        if 'm3u8' in url_m3u8:
            streamurl = url_m3u8
    return streamurl
