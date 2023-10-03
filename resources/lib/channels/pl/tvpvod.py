# GNU General Public License v2.0+ (see LICENSE.txt or https://www.gnu.org/licenses/gpl-2.0.txt)

# This file is part of Catch-up TV & More

import urlquick

from codequick import Listitem, Resolver, Route, Script

from resources.lib import resolver_proxy, web_utils
from resources.lib.menu_utils import item_post_treatment

# Replay
URL_REPLAY = {
    'catalog': 'https://vod.tvp.pl/api/products/vods',
    'serial': 'https://vod.tvp.pl/api/products/vods/serials/{serial_id}/seasons/{season_id}/episodes',
    # 'info': 'https://vod.tvp.pl/api/products/vods/{content_id}?ln={ln}&platform={pla}',
    'content': 'https://vod.tvp.pl/api/products/{content_id}/videos/playlist',
}
# ANDROID_TV, APPLE_TV, BROWSER, ANDROID, IOS
PLATFORM = 'SMART_TV'
LANG = 'pl'
PAGE_SIZE = 100


def __fetch_programs():
    fetch_more_content = True
    next_itm = 0
    tvp_items = []
    while fetch_more_content:
        fetch_more_content = False
        params = {
            'firstResult': next_itm,
            'maxResults': PAGE_SIZE,
            'mainCategoryId[]': 24,
            'sort': 'createdAt',
            'order': 'desc',
            'ln': LANG,
            'platform': PLATFORM
        }
        resp = urlquick.get(URL_REPLAY['catalog'], params,
                            headers={'User-Agent': web_utils.get_random_ua()},
                            max_age=-1, timeout=30, raise_for_status=False)
        if resp.status_code != 200:
            break
        resp_json = resp.json()
        tvp_items.extend(resp_json['items'])
        next_itm = resp_json['meta']['firstResult'] + resp_json['meta']['maxResults']
        if next_itm <= resp_json['meta']['totalCount']:
            fetch_more_content = True
    return tvp_items


@Route.register
def list_programs(plugin, item_id, **kwargs):
    tvp_items = __fetch_programs()
    if tvp_items is None or len(tvp_items) == 0:
        plugin.notify(plugin.localize(30891), plugin.localize(30718), Script.NOTIFY_ERROR)
        return

    for tvp_item in tvp_items:
        item = Listitem()
        item.label = tvp_item['title']
        serial_image_url = 'https:' + tvp_item['images']['16x9'][0]['url']
        item.art['thumb'] = serial_image_url
        # item.art['fanart'] = 'resources/channels/pl/tvpvod_fanart.jpg'

        serial_id = int(tvp_item['id'])
        item.set_callback(list_episodes, serial_id=serial_id, season_id=serial_id + 1, serial_image_url=serial_image_url)
        item_post_treatment(item)
        yield item


@Route.register
def list_episodes(plugin, serial_id, season_id, serial_image_url):
    url = URL_REPLAY['serial'].format(serial_id=serial_id, season_id=season_id)
    params = {
        'ln': LANG,
        'platform': PLATFORM
    }
    resp = urlquick.get(url, params, headers={'User-Agent': web_utils.get_random_ua()},
                        max_age=-1, timeout=30)
    for tvp_episode in resp.json():
        item = Listitem()
        item.label = tvp_episode['title']
        item.art['thumb'] = 'https:' + tvp_episode['images']['16x9'][0]['url']
        item.art['fanart'] = serial_image_url

        episode_id = int(tvp_episode['id'])
        item.set_callback(play_episode, episode_id=episode_id)
        item_post_treatment(item, is_playable=True)
        yield item


@Resolver.register
def play_episode(plugin, episode_id):
    content_url = URL_REPLAY['content'].format(content_id=episode_id)
    params = {
        'platform': PLATFORM,
        'videoType': 'MOVIE'
    }
    content = None
    content = urlquick.get(content_url, params, headers={'User-Agent': web_utils.get_random_ua()},
                           max_age=-1, timeout=30, raise_for_status=False)
    if content.status_code != 200:
        plugin.notify(plugin.localize(30891), plugin.localize(30718), Script.NOTIFY_ERROR)
        return False

    content_json = content.json() if content is not None else {}
    # HLS vs DASH
    m3u8_url = content_json['sources']['HLS'][0]['src']

    return resolver_proxy.get_stream_with_quality(plugin, m3u8_url)
