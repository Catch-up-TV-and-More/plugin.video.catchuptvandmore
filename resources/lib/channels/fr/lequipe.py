# -*- coding: utf-8 -*-
# Copyright: (c) 2017, SylvainCecchetto
# GNU General Public License v2.0+ (see LICENSE.txt or https://www.gnu.org/licenses/gpl-2.0.txt)

# This file is part of Catch-up TV & More

from __future__ import unicode_literals
from builtins import str
import json
import re

from codequick import Listitem, Resolver, Route, Script
import urlquick

from resources.lib import resolver_proxy, web_utils
from resources.lib.menu_utils import item_post_treatment
import xbmcgui

# TO DO
# Rework Date/AIred
URL_ROOT = 'https://www.lequipe.fr'
URL_LIVE = URL_ROOT + '/tv'
EMBEDER_URL = URL_LIVE + '/videos/live/%s'
URL_API = 'https://dwh.lequipe.fr/api'
URL_API_HOME = URL_API + '/home/classic'
URL_API_MEDIA = URL_API + '/video/media/'

GENERIC_HEADERS = {'User-Agent': web_utils.get_random_ua()}
PARAMS = {
    'platform': 'ctv',
    'version': '1.22',
    'site': 'lequipe.play',
}


@Route.register
def list_categories(plugin, item_id, **kwargs):
    # Lives
    item = Listitem()
    item.label = 'Directs'
    item.set_callback(get_multi_live_url)
    item_post_treatment(item)
    yield item

    PARAMS['path'] = '/tv/'
    response = urlquick.get(URL_API_HOME, headers=GENERIC_HEADERS, params=PARAMS, max_age=-1)
    json_parser = json.loads(response.content)

    for category_datas in json_parser['content']['feed']['items']:
        category_title = category_subtitle = ''
        if category_datas.get('hash') == 'lineup-for-live':
            continue
        if category_datas.get('title') is None:
            continue
        else:
            category_title = category_datas['title'].get('text')
        if category_datas.get('subtitle') is not None:
            category_subtitle = category_datas['subtitle'].get('text')
        if len(category_subtitle) > 0:
            category_title = category_title + ' - ' + category_subtitle

        item = Listitem()
        item.label = category_title
        item.set_callback(list_programs,
                          datas=category_datas)
        item_post_treatment(item)
        yield item


@Route.register
def list_programs(plugin, datas, **kwargs):
    again_program = False
    if len(datas) > 0:
        for program_datas in datas['items']:
            program_type = program_datas.get('__type')
            if program_type == "carousel_widget":
                continue

            program_title = program_subtitle = program_url = program_duration = ''
            if program_datas['content'].get('title_text_box') is not None:
                program_title = program_datas['content']['title_text_box'].get('text')
            if program_datas['content'].get('subtitle_text_box') is not None:
                program_subtitle = program_datas['content']['subtitle_text_box'].get('text')
                program_title = program_title + ' - ' + program_subtitle
            program_desc = program_datas['content'].get('description')
            program_image = program_datas['content']['image'].get('url')
            program_image = program_image.replace('{width}', '534').replace('{height}', '300')
            if program_datas.get('video'):
                program_duration = program_datas['video'].get('duree')
            if program_datas.get('link'):
                program_url = program_datas['link'].get('web')
            if len(program_title) == 0:
                program_title = re.compile(r'/([a-zA-Z0-9-]*)/$').findall(program_url)[0]
                again_program = True

            item = Listitem()
            item.label = program_title
            item.art['thumb'] = item.art['landscape'] = item.art["fanart"] = program_image
            if program_desc:
                item.info['plot'] = program_desc
            if program_duration:
                item.info['duration'] = program_duration
            if again_program:
                item.set_callback(list_videos,
                                  video_url=program_url)
            else:
                item.set_callback(get_video_url,
                                  video_url=program_url)
            item_post_treatment(item, is_playable=True, is_downloadable=True)
            yield item


@Route.register
def list_videos(plugin, video_url, **kwargs):
    again_program = False
    PARAMS['path'] = video_url.replace('https://www.lequipe.fr', '')
    response = urlquick.get(URL_API_HOME, headers=GENERIC_HEADERS, params=PARAMS, max_age=-1)
    json_parser = json.loads(response.content)

    for video_datas in json_parser['content']['feed']['items']:
        for items_datas in video_datas['items']:
            program_type = items_datas.get('__type')
            if program_type == "carousel_widget":
                continue

            video_title = video_subtitle = video_url = video_duration = ''
            if items_datas['content'].get('title_text_box') is not None:
                video_title = items_datas['content']['title_text_box'].get('text')
            if items_datas['content'].get('subtitle_text_box') is not None:
                video_subtitle = items_datas['content']['subtitle_text_box'].get('text')
                video_title = video_title + ' - ' + video_subtitle
            video_desc = items_datas['content'].get('description')
            video_image = items_datas['content']['image'].get('url')
            video_image = video_image.replace('{width}', '534').replace('{height}', '300')
            if items_datas.get('video'):
                video_duration = items_datas['video'].get('duree')
            if items_datas.get('link'):
                video_url = items_datas['link'].get('web')
            if len(video_title) == 0:
                video_title = re.compile(r'/([a-zA-Z0-9-]*)/$').findall(video_url)[0]
                again_program = True

            item = Listitem()
            item.label = video_title
            item.art['thumb'] = item.art['landscape'] = item.art["fanart"] = video_image
            if video_desc:
                item.info['plot'] = video_desc
            if video_duration:
                item.info['duration'] = video_duration
            if again_program:
                item.set_callback(list_videos,
                                  video_url=video_url)
            else:
                item.set_callback(get_video_url,
                                  video_url=video_url)
            item_post_treatment(item, is_playable=True, is_downloadable=True)
            yield item


@Resolver.register
def get_video_url(plugin, video_url, download_mode=False, **kwargs):
    media_id = re.compile(r'(\d*)$').findall(video_url)[0]
    response = urlquick.get(URL_API_MEDIA + media_id, headers=GENERIC_HEADERS, params=PARAMS, max_age=-1)
    json_parser = json.loads(response.content)

    for video_datas in json_parser['content']['feed']['items']:
        if video_datas.get('video') is None:
            continue
        video_id = video_datas['video'].get('id')
        video_free = video_datas['video']['access'].get('is_accessible_for_free')

    if video_id and video_free:
        embeder = EMBEDER_URL % video_id
        return resolver_proxy.get_stream_dailymotion(plugin, video_id, download_mode, embeder)
    else:
        plugin.notify(plugin.localize(30600), plugin.localize(30716))
        return False


@Resolver.register
def get_live_url(plugin, item_id, **kwargs):
    return resolver_proxy.get_stream_dailymotion(plugin, 'x2lefik', False, EMBEDER_URL % 'x2lefik')


@Route.register
def get_multi_live_url(plugin, **kwargs):
    PARAMS['path'] = '/'
    PARAMS['platform'] = 'android'
    response = urlquick.get(URL_API + '/home/classic', headers=GENERIC_HEADERS, params=PARAMS, max_age=-1)
    json_parser = json.loads(response.content)

    for video_datas in json_parser['content']['feed']['items'][0]['items']:
        video_item = video_title = video_desc = video_image = video_id = ""
        video_islive = False
        program_type = video_datas.get('__type')
        if program_type == "carousel_widget":
            continue
        if video_datas.get('video'):
            video_id = video_datas['video'].get('id')
            video_islive = video_datas['video'].get('is_live', False)
        if not video_islive or any(c in video_id for c in ['eurosport', 'ligue1']):
            continue
        if video_datas.get('content'):
            video_title = video_datas['content'].get('title')
            video_desc = video_datas['content'].get('description')
            video_image = video_datas['content']['image'].get('url')
            video_image = video_image.replace('{width}', '534').replace('{height}', '300')
            video_items = []
            if video_datas['content'].get('breadcrumb'):
                for titre_datas in video_datas['content']['breadcrumb']:
                    video_items.append(titre_datas.get('text'))
            if len(video_items) == 2:
                video_item = video_items[0] + ', ' + video_items[1]
            elif len(video_items) == 1:
                video_item = video_items[0]
            else:
                video_item = ""

        item = Listitem()
        item.label = video_item
        item.info['title'] = f'{video_item}    [COLOR orange]{video_title}[/COLOR]'
        item.info['plot'] = video_desc
        item.art["thumb"] = item.art["thumb"] = video_image
        item.set_callback(get_multi_video_url, video_id=video_id)
        item_post_treatment(item)
        yield item


@Resolver.register
def get_multi_video_url(plugin, video_id, download_mode=False, **kwargs):

    embeder = EMBEDER_URL % video_id
    return resolver_proxy.get_stream_dailymotion(plugin, video_id, download_mode, embeder)
