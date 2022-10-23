# -*- coding: utf-8 -*-
# Copyright: (c) 2019, SylvainCecchetto
# GNU General Public License v2.0+ (see LICENSE.txt or https://www.gnu.org/licenses/gpl-2.0.txt)

# This file is part of Catch-up TV & More

from __future__ import unicode_literals
import json

from codequick import Listitem, Resolver, Route
import urlquick

# noinspection PyUnresolvedReferences
from resources.lib import resolver_proxy, web_utils
from resources.lib.menu_utils import item_post_treatment
from resources.lib.addon_utils import get_item_media_path

CORONA_URL = 'https://corona.channel5.com/shows/'
BASIS_URL = CORONA_URL + '%s/seasons'

URL_SEASONS = BASIS_URL + '.json'
URL_EPISODES = BASIS_URL + '/%s/episodes.json'
FEEDS_API = 'https://feeds-api.channel5.com/collections/%s/concise.json'

URL_VIEW_ALL = CORONA_URL + 'search.json'
URL_WATCHABLE = 'https://corona.channel5.com/watchables/search.json'
IMG_URL = 'https://api-images.channel5.com/otis/images/episode/%s/320x180.jpg'

GENERIC_HEADERS = {"User-Agent": web_utils.get_random_ua()}

feeds_api_params = {
    'vod_available': 'my5desktop',
    'friendly': '1'
}

view_api_params = {
    'platform': 'my5desktop',
    'friendly': '1'
}

# ImageId, EntityId


@Route.register
def list_categories(plugin, item_id, **kwargs):
    resp = urlquick.get(FEEDS_API % 'PLC_My5SubGenreBrowsePageSubNav', headers=GENERIC_HEADERS, params=feeds_api_params)
    root = json.loads(resp.text)
    for i in range(int(root['total_items'])):
        item = Listitem()
        item.label = root['filters']['contents'][i]['title']
        browse_name = root['filters']['contents'][i]['id']
        item.set_callback(list_subcategories, item_id=item_id, browse_name=browse_name)
        item_post_treatment(item)
        yield item


@Route.register
def list_subcategories(plugin, item_id, browse_name, **kwargs):
    resp = urlquick.get(FEEDS_API % browse_name, headers=GENERIC_HEADERS, params=feeds_api_params)
    root = json.loads(resp.text)
    item_number = int(root['total_items'])

    if root['filters']['type'] == 'Collection':
        for i in range(item_number):
            item = Listitem()
            item.label = root['filters']['contents'][i]['title']
            browse_name = root['filters']['contents'][i]['id']
            item.set_callback(list_collections, item_id=item_id, browse_name=browse_name,)
            item_post_treatment(item)
            yield item
    else:
        ids = root['filters']['ids']
        watchable_params = '?limit=%s10&offset=0s&platform=my5desktop&friendly=1' % str(item_number)
        for i in range(item_number):
            watchable_params = watchable_params + '&ids[]=%s' % ids[i]
        resp = urlquick.get(URL_WATCHABLE % browse_name, headers=GENERIC_HEADERS)

        for watchable in root['watchables']:
            item = Listitem()
            item.Label = watchable['sh_title']
            item.info['plot'] = watchable['title']
            item.art['thumb'] = item.art['landscape'] = IMG_URL % watchable['id']
            fname = watchable['f_name']
            season_f_name = watchable['season_f_name']

            item.set_callback(get_video_url, item_id=item_id, fname=fname, season_f_name=season_f_name)
            yield item


@Route.register
def list_watchables(plugin, itemid, browse_name, offset, item_number, ids):
    return False


@Route.register
def list_collections(plugin, item_id, browse_name, offset, **kwargs):
    resp = urlquick.get(FEEDS_API % browse_name, headers=GENERIC_HEADERS, params=feeds_api_params)
    root = json.loads(resp.text)
    subgenre = root['filters']['vod_subgenres']
    view_all_params = {
        'platform': 'my5desktop',
        'friendly': '1',
        'limit': '10',
        'offset': offset,
        'vod_subgenres[]': subgenre
    }
    resp = urlquick.get(URL_VIEW_ALL, headers=GENERIC_HEADERS, params=view_all_params)
    root = json.loads(resp.text)

    for emission in root['shows']:
        item = Listitem()
        item.label = emission['title']
        item.info['plot'] = emission['s_desc']
        fname = emission['f_name']
        item.set_callback(list_seasons, item_id=item_id, fname=fname)
        item_post_treatment(item)
        yield item

    if 'next_page_url' in root:
        offset = str(int(offset) + int(view_all_params['limit']))
        yield Listitem.next_page(item_id=item_id, browse_name=browse_name, offset=offset)


@Route.register
def list_seasons(plugin, item_id, fname, **kwargs):
    resp = urlquick.get(URL_SEASONS % fname, headers=GENERIC_HEADERS, params=view_api_params)
    if resp.ok:
        root = json.loads(resp.text)

        for season in root['seasons']:
            item = Listitem()
            season_number = season['seasonNumber']
            item.label = 'Season ' + season_number
            item.set_callback(list_episodes, item_id=item_id, fname=fname, season_number=season_number)
            item_post_treatment(item)
            yield item


@Route.register
def list_episodes(plugin, item_id, fname, season_number, **kwargs):
    resp = urlquick.get(URL_EPISODES % (fname, season_number), headers=GENERIC_HEADERS, params=view_api_params)
    root = json.loads(resp.text)

    for episode in root['episodes']:
        item = Listitem()
        picture_id = episode['id']
        item.art['thumb'] = item.art['landscape'] = IMG_URL % picture_id
        item.label = episode['title']
        item.info['plot'] = episode['s_desc']
        season_f_name = episode['sea_f_name']
        fname = episode['f_name']
        item.set_callback(get_video_url, item_id=item_id, fname=fname, season_f_name=season_f_name)
        item_post_treatment(item)
        yield item


@Resolver.register
def get_video_url(plugin, item_id, f_name, season_f_name, **kwargs):
    return False
