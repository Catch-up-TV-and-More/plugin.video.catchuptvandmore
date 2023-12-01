# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import base64
from datetime import datetime
import importlib
import json
import os
import urlquick
from codequick import Listitem, Resolver, Route, Script
from codequick.storage import Cache
from kodi_six import xbmcgui
from resources.lib import resolver_proxy
from resources.lib.addon_utils import get_item_media_path
from resources.lib.menu_utils import item_post_treatment
from resources.lib.main import tv_guide_menu

CACHE_FILE = os.path.join(Route.get_info("profile"), u".sfrtv_cache.sqlite")
USER_AGENT = ('Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 '
              'Safari/537.36')  # fixed as the list of connected devices is limited
TOKEN_MAX_AGE = 840  # 14 minutes to be under the 15 mn token validity limit
CONFIG_URL = 'https://tv.sfr.fr/configs/config.json'
LOGIN_URL = 'https://www.sfr.fr/cas/login'
ACCESS_TOKEN_URL = 'https://www.sfr.fr/cas/oidc/authorize'
USER_PROFILE_URL = 'https://ws-backendtv.sfr.fr/heimdall-core/public/api/v2/userProfiles'
SERVICE_URL = 'https://ws-backendtv.sfr.fr/sekai-service-plan/public/v2/service-list'
LICENSE_URL = 'https://ws-backendtv.sfr.fr/asgard-drm-widevine/public/licence'
STRUCT_MENU_URL = 'https://ws-cdn.tv.sfr.net/gaia-core/rest/api/web/v2/menu/RefMenuItem::gen8-replay-v2/structure'
MENU_URL = 'https://ws-backendtv.sfr.fr/gaia-core/rest/api/web/v2/spot/{}/content'
CATEGORIES_URL = 'https://ws-cdn.tv.sfr.net/gaia-core/rest/api/web/v1/stores/{}/categories'
PRODUCTS_URL = 'https://ws-cdn.tv.sfr.net/gaia-core/rest/api/web/v2/categories/{}/contents'
PRODUCT_DETAILS_URL = 'https://ws-cdn.tv.sfr.net/gaia-core/rest/api/web/v1/content/{}/detail'
PRODUCT_OPTIONS_URL = 'https://ws-backendtv.sfr.fr/gaia-core/rest/api/web/v3/content/{}/options'
SEARCH_TEXT_URL = 'https://ws-backendtv.sfr.fr/gaia-core/rest/api/web/v2/search/text'
CUSTOMDATA_REPLAY = ('description={}&deviceId=byPassARTHIUS&deviceName=Firefox-96.0----Windows&deviceType=PC'
                     '&osName=Windows&osVersion=10&persistent=false&resolution=1600x900&tokenType=castoken'
                     '&tokenSSO={}&type=REPLAY')
CUSTOMDATA_LIVE = ('description={}&deviceId=byPassARTHIUS&deviceName=Firefox-96.0----Windows&deviceType=PC'
                   '&osName=Windows&osVersion=10&persistent=false&resolution=1600x900&tokenType=castoken'
                   '&tokenSSO={}&type=LIVEOTT&accountId={}')
MAX_PRODUCTS = 20
REQUEST_TIMEOUT = 30
PRODUCT_DETAILS_TYPES = ['Serie', 'Season', 'CONTENT']


def get_sfrtv_config(plugin):
    return urlquick.get(CONFIG_URL,
                        headers={'User-Agent': USER_AGENT},
                        timeout=REQUEST_TIMEOUT).json()


def get_sfrtv_user_profile(plugin, token):
    params = {
        'token': token
    }
    headers = {
        'Accept': 'application/json, text/plain, */*',
        'Referer': 'https://tv.sfr.fr/',
        'User-Agent': USER_AGENT
    }
    return urlquick.get(USER_PROFILE_URL,
                        params=params,
                        headers=headers,
                        timeout=REQUEST_TIMEOUT).json()


def get_credentials_from_config(plugin, with_dialog):
    username = plugin.setting.get_string('sfrtv.login')
    password = plugin.setting.get_string('sfrtv.password')

    if not username or not password:
        if with_dialog:
            xbmcgui.Dialog().ok(plugin.localize(30600),
                                plugin.localize(30604) % ('SFR TV', 'https://tv.sfr.fr'))
        return None, None

    return username, password


def get_token(plugin, with_dialog=True):
    username, password = get_credentials_from_config(plugin, with_dialog)
    if not username or not password:
        return None

    # Unable to use urlquick cache due to authentication redirects
    cache = Cache(CACHE_FILE, TOKEN_MAX_AGE)

    if 'token' in cache:
        return cache['token']

    sfrtv_config = get_sfrtv_config(plugin)
    sfrtv_client_id = sfrtv_config['auth']['OIDC_CLIENT_ID']

    session = urlquick.Session()

    params = {
        'client_id': sfrtv_client_id,
        'scope': 'openid',
        'response_type': 'token',
        'redirect_uri': 'https://tv.sfr.fr/'
    }
    headers = {
        'user-agent': USER_AGENT,
        'authority': 'www.sfr.fr',
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'accept-language': 'fr-FR,fr;q=0.9,en-US;q=0.8,en;q=0.7',
        'referer': 'https://tv.sfr.fr/',
    }
    resp = session.get(ACCESS_TOKEN_URL,
                       params=params,
                       headers=headers,
                       max_age=-1,
                       timeout=REQUEST_TIMEOUT)

    root = resp.parse()
    form_elt = root.find(".//form[@name='loginForm']")
    lt = form_elt.find(".//input[@name='lt']").get('value')
    lrt = form_elt.find(".//input[@name='lrt']").get('value')
    execution = form_elt.find(".//input[@name='execution']").get('value')
    event_id = form_elt.find(".//input[@name='_eventId']").get('value')

    params = {
        'domain': 'mire-sfr',
        'service': 'https://www.sfr.fr/cas/oidc/callbackAuthorize'
    }
    headers = {
        'user-agent': USER_AGENT,
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'authority': 'www.sfr.fr',
        'accept-language': 'fr-FR,fr;q=0.9,en-US;q=0.8,en;q=0.7',
        'content-type': 'application/x-www-form-urlencoded',
        'origin': 'https://www.sfr.fr',
        'referer': resp.url,
    }
    data = {
        'lt': lt,
        'execution': execution,
        'lrt': lrt,
        '_eventId': event_id,
        'username': username,
        'password': password,
        'remember-me': 'on',
        'identifier': ''
    }
    session.post(
        LOGIN_URL,
        params=params,
        headers=headers,
        data=data,
        max_age=-1,
        timeout=REQUEST_TIMEOUT
    )

    params = {
        'client_id': sfrtv_client_id,
        'scope': 'openid',
        'response_type': 'token',
        'redirect_uri': 'https://tv.sfr.fr/',
        'token': 'true',
        'gateway': 'true'
    }
    headers = {
        'user-agent': USER_AGENT,
        'authority': 'www.sfr.fr',
        'accept': 'application/json, text/plain, */*',
        'accept-language': 'fr-FR,fr;q=0.9,en-US;q=0.8,en;q=0.7',
        'origin': 'https://tv.sfr.fr',
        'referer': 'https://tv.sfr.fr/',
    }
    resp = session.get(ACCESS_TOKEN_URL,
                       params=params,
                       headers=headers,
                       max_age=-1,
                       timeout=REQUEST_TIMEOUT)
    access_token_b64_bytes = resp.content
    access_token_b64 = access_token_b64_bytes.decode('ascii')
    if not access_token_b64:
        if with_dialog:
            xbmcgui.Dialog().ok(plugin.localize(30600),
                                plugin.localize(30711))
        return None
    access_token_b64_second_part = access_token_b64.split('.')[1]
    access_token_b64_second_part_bytes = access_token_b64_second_part.encode('ascii')
    missing_padding = len(access_token_b64_second_part_bytes) % 4
    if missing_padding:
        access_token_b64_second_part_bytes += b'=' * (4 - missing_padding)
    access_token_second_part_bytes = base64.b64decode(access_token_b64_second_part_bytes)
    access_token_second_part_json = access_token_second_part_bytes.decode('utf-8')
    access_token_second_part = json.loads(access_token_second_part_json)
    token = access_token_second_part['tu']

    cache['token'] = token
    return token


@Route.register(autosort=False)
def provider_root(plugin, **kwargs):
    username, password = get_credentials_from_config(plugin, True)
    if not username or not password:
        yield False
        return

    # Live TV
    item = Listitem()
    item.label = plugin.localize(30030)
    item.art['thumb'] = get_item_media_path('live_tv.png')
    item.set_callback(list_lives)
    item_post_treatment(item)
    yield item

    # Replay
    item = Listitem()
    item.label = 'Replay'
    item.art['thumb'] = get_item_media_path('replay.png')
    item.set_callback(list_stores)
    item_post_treatment(item)
    yield item

    # Search feature
    item = Listitem.search(search)
    item_post_treatment(item)
    yield item


def get_stores(plugin, token):
    params = {
        'accountTypes': 'LAND',
        'infrastructures': 'FTTH',
        'operators': 'sfr',
        'noTracking': 'false',
        'app': 'gen8',
        'device': 'browser'
    }
    headers = {
        'Accept': 'application/json',
        'Referer': 'https://tv.sfr.fr/',
        'User-Agent': USER_AGENT
    }
    struct_menu = urlquick.get(STRUCT_MENU_URL,
                               params=params,
                               headers=headers,
                               timeout=REQUEST_TIMEOUT).json()
    spot_id = struct_menu['spots'][0]['id']
    params = {
        'app': 'gen8',
        'device': 'browser',
        'token': token,
        'operators': 'sfr',
        'infrastructures': 'FTTH',
        'accountTypes': 'LAND',
        'noTracking': 'false',
    }
    headers = {
        'Accept': 'application/json',
        'Referer': 'https://tv.sfr.fr/',
        'User-Agent': USER_AGENT
    }
    menu = urlquick.get(MENU_URL.format(spot_id),
                        params=params,
                        headers=headers,
                        max_age=TOKEN_MAX_AGE,
                        timeout=REQUEST_TIMEOUT).json()
    return list(map(lambda t: {'id': t['action']['actionIds']['storeId'],
                               'title': t['title'],
                               'images': t['images']},
                    menu['tiles']))


@Route.register(autosort=False)
def list_stores(plugin, **kwargs):
    token = get_token(plugin)
    if not token:
        yield False
        return

    for store in get_stores(plugin, token):
        item = Listitem()
        item.label = store['title']

        for image in store['images']:
            if image['format'] == 'logo':
                item.art['thumb'] = image['url']

        item.set_callback(list_categories,
                          store_id=store['id'])
        item_post_treatment(item)
        yield item


def get_categories(plugin, store_id):
    params = {
        'app': 'gen8',
        'device': 'browser',
        'accountTypes': 'LAND',
        'infrastructures': 'FTTH',
        'operators': 'sfr',
        'noTracking': 'false'
    }
    headers = {
        'Accept': 'application/json',
        'Referer': 'https://tv.sfr.fr/',
        'User-Agent': USER_AGENT
    }
    categories_infos = urlquick.get(CATEGORIES_URL.format(store_id),
                                    params=params,
                                    headers=headers,
                                    timeout=REQUEST_TIMEOUT).json()
    return categories_infos['categories']


@Route.register(autosort=False)
def list_categories(plugin, store_id, **kwargs):
    categories = get_categories(plugin, store_id)

    for category in categories:
        item = Listitem()
        item.label = category['name']
        item.set_callback(list_products,
                          category_id=category['id'],
                          page=0)
        item_post_treatment(item)
        yield item


def get_products(plugin, category_id, page):
    params = {
        'app': 'gen8',
        'device': 'browser',
        'accountTypes': 'LAND',
        'infrastructures': 'FTTH',
        'operators': 'sfr',
        'noTracking': 'false',
        'page': page,
        'size': MAX_PRODUCTS
    }
    headers = {
        'Accept': 'application/json',
        'Referer': 'https://tv.sfr.fr/',
        'User-Agent': USER_AGENT
    }
    return urlquick.get(PRODUCTS_URL.format(category_id),
                        params=params,
                        headers=headers,
                        timeout=REQUEST_TIMEOUT).json()


@Route.register(autosort=False)
def list_products(plugin, category_id, page, **kwargs):
    # Pagination seems to be blocked at 20 videos (the "size" parameter doesn't change anything),
    # so let's paginate at 100 videos
    n_loop = 5
    for x in range(n_loop):
        products = get_products(plugin, category_id, page)

        for product in products:
            yield build_product_item(plugin, product)

        if len(products) == MAX_PRODUCTS:  # didn't find "count" or "total" information
            if x < (n_loop - 1):
                page += 1
            else:
                yield Listitem.next_page(category_id=category_id,
                                         callback=list_products,
                                         page=page + 1)
        else:
            break


def get_product_details(plugin, product_id, universe='PROVIDER', **kwargs):
    params = {
        'accountTypes': 'LAND',
        'infrastructures': 'FTTH',
        'operators': 'sfr',
        'noTracking': 'false',
        'universe': universe
    }
    headers = {
        'Accept': 'application/json',
        'Referer': 'https://tv.sfr.fr/',
        'User-Agent': USER_AGENT
    }
    return urlquick.get(PRODUCT_DETAILS_URL.format(product_id),
                        params=params,
                        headers=headers,
                        timeout=REQUEST_TIMEOUT).json()


@Route.register(autosort=False)
def list_product_details(plugin, product_id, **kwargs):
    token = get_token(plugin)
    if not token:
        yield False
        return

    product_details = get_product_details(plugin, product_id, **kwargs)

    if 'seasons' in product_details:
        for season in product_details['seasons']:
            season_details = get_product_details(plugin, season['id'], **kwargs)
            yield build_product_item(plugin, season_details)
    elif 'episodes' in product_details:
        for episode in product_details['episodes']:
            episode_details = get_product_details(plugin, episode['id'])
            yield build_product_item(plugin, episode_details)
    else:
        yield build_product_item(plugin, product_details)


def build_product_item(plugin, product):
    item = Listitem()

    item.label = product['title']

    if 'description' in product and product['description']:
        item.info['plot'] = product['description']
    elif 'shortDescription' in product and product['shortDescription']:
        item.info['plot'] = product['shortDescription']

    if 'duration' in product and product['duration']:
        item.info['duration'] = product['duration']

    if 'seasonNumber' in product and product['seasonNumber']:
        item.info['season'] = product['seasonNumber']

    if 'episodeNumber' in product and product['episodeNumber']:
        item.info['mediatype'] = 'episode'
        item.info['episode'] = product['episodeNumber']

    if 'diffusionDate' in product and product['diffusionDate']:
        dt = datetime.fromtimestamp(int(product['diffusionDate'] / 1000))
        dt_format = '%d/%m/%Y'
        item.info.date(dt.strftime(dt_format), dt_format)

    for image in product.get('images', []):
        if image['format'] == '2/3' and not item.art.get('thumb'):
            item.art['thumb'] = image['url']
        elif image['format'] == '16/9':
            item.art['thumb'] = image['url']

    item.set_callback(list_product_details if product.get('type', '') in PRODUCT_DETAILS_TYPES else get_replay_stream,
                      product['id'],
                      universe=product['universe'] if 'universe' in product else 'PROVIDER')

    item_post_treatment(item)

    return item


def get_replay_url(plugin, product_id, token, universe='PROVIDER', **kwargs):
    params = {
        'app': 'gen8',
        'device': 'browser',
        'token': token,
        'accountTypes': 'LAND',
        'infrastructures': 'FTTH',
        'operators': 'sfr',
        'noTracking': 'false',
        'universe': universe
    }
    headers = {
        'Accept': 'application/json',
        'Referer': 'https://tv.sfr.fr/',
        'User-Agent': USER_AGENT
    }
    product_options = urlquick.get(PRODUCT_OPTIONS_URL.format(product_id),
                                   params=params,
                                   headers=headers,
                                   timeout=REQUEST_TIMEOUT).json()
    for option in product_options:
        for offer in option['offers']:
            for stream in offer['streams']:
                if stream['drm'] == 'WIDEVINE':
                    return stream['url']
    return None


@Resolver.register
def get_replay_stream(plugin, product_id, **kwargs):
    token = get_token(plugin)
    if not token:
        return False

    replay_url = get_replay_url(plugin, product_id, token, **kwargs)
    if not replay_url:
        return False

    headers = {
        'User-Agent': USER_AGENT,
        'customdata': CUSTOMDATA_REPLAY.format(USER_AGENT, token),
        'Referer': 'https://tv.sfr.fr/',
        'content-type': 'application/octet-stream'
    }

    return resolver_proxy.get_stream_with_quality(plugin,
                                                  video_url=replay_url,
                                                  license_url=LICENSE_URL,
                                                  manifest_type='mpd',
                                                  headers=headers)


def get_products_to_search(plugin, keyword, page=0, size=25, **kwargs):
    params = {
        'app': 'gen8',
        'device': 'browser',
        'keyword': keyword,
        'page': page,
        'size': size
    }
    headers = {
        'Accept': 'application/json',
        'Referer': 'https://tv.sfr.fr/',
        'User-Agent': USER_AGENT
    }
    search_result = urlquick.get(SEARCH_TEXT_URL,
                                 params=params,
                                 headers=headers,
                                 timeout=REQUEST_TIMEOUT).json()

    has_next_page = (search_result['count'] - ((page + 1) * size)) > 0

    return search_result['content'], page, has_next_page


@Route.register(autosort=False)
def search(plugin, search_query, **kwargs):
    products, page, has_next_page = get_products_to_search(plugin, search_query, **kwargs)

    for product in products:
        yield build_product_item(plugin, product)

    if has_next_page:
        item = Listitem.next_page(search_query=search_query,
                                  callback=search,
                                  page=page + 1)
        item.property['SpecialSort'] = 'bottom'
        yield item


def get_active_services(plugin, token):
    params = {
        'app': 'gen8',
        'device': 'browser',
        'token': token
    }
    headers = {
        'User-Agent': USER_AGENT,
        'Accept': 'application/json',
        'Accept-language': 'fr-FR,fr;q=0.9,en-US;q=0.8,en;q=0.7',
        'Origin': 'https://tv.sfr.fr',
        'Referer': 'https://tv.sfr.fr/',
        'Connection': 'keep-alive'
    }
    services = urlquick.get(SERVICE_URL,
                            params=params,
                            headers=headers,
                            max_age=TOKEN_MAX_AGE,
                            timeout=REQUEST_TIMEOUT).json()
    active_services = list(filter(lambda c: c['access'], services))
    return active_services


def list_live_channels(plugin=Script):

    """
    Called by iptvmanager to retrieve a dynamic list of SFR TV channels to activate for IPTV Manager.
    Only the channels activated for the current account are yielded.
    For each channel, the information is retrieved from the "sfrtv_live" skeleton but if the channel
    is not found in it, the information is manually built.

    :param plugin: plugin (codequick.script.Script)

    :returns: A generator of the channels infos
    :rtype: :class:`types.GeneratorType`
    """

    token = get_token(plugin,
                      with_dialog=False)
    if not token:
        return

    active_services = get_active_services(plugin, token)
    channels_dict = importlib.import_module('resources.lib.skeletons.sfrtv_live').menu

    for serv in active_services:
        channel_infos = channels_dict.get(serv['serviceId'])

        if not channel_infos:
            channel_infos = {
                'resolver': '/resources/lib/providers/sfrtv:get_live_stream',
                'label': serv['name'],
                'enabled': True,
                'order': serv['zappingId']
            }
            for image in serv.get('images', []):
                if image['type'] == 'color':
                    channel_infos['thumb'] = image['url']

        channel_infos['id'] = serv['serviceId']
        yield channel_infos


@Route.register
def list_lives(plugin, **kwargs):
    token = get_token(plugin)
    if not token:
        yield False
        return

    active_services = get_active_services(plugin, token)
    tv_guide_items = list(tv_guide_menu(plugin, 'sfrtv_live'))

    for serv in sorted(active_services, key=lambda s: s['zappingId']):

        # Try to find the TV Guide Listitem from sfrtv live menu
        item = next(
            (tvg for tvg in tv_guide_items if tvg.params.item_id == serv['serviceId']),
            None
        )

        # If not found, construct manually a Listitem without TV guide
        if not item:
            item = Listitem()
            item.label = serv['name']

            for image in serv.get('images', []):
                if image.get('type', '') == 'color':
                    item.art['thumb'] = item.art['landscape'] = image.get('url')

            # Playcount is useless for live streams
            item.info['playcount'] = 0

            item.set_callback(get_live_stream,
                              item_id=serv['serviceId'])

        yield item


def get_live_url(plugin, service_id, token):
    active_services = get_active_services(plugin, token)

    for serv in active_services:
        if serv['serviceId'] == service_id:
            for stream in serv['streams']:
                if stream['drm'] == 'WIDEVINE':
                    # Workaround for IA bug : https://github.com/xbmc/inputstream.adaptive/issues/804
                    response = urlquick.get(stream['url'],
                                            headers={'User-Agent': USER_AGENT},
                                            max_age=-1,
                                            timeout=REQUEST_TIMEOUT)
                    live_url = response.xml().find('{urn:mpeg:dash:schema:mpd:2011}Location').text
                    return live_url
    return None


@Resolver.register
def get_live_stream(plugin, item_id, **kwargs):
    token = get_token(plugin)
    if not token:
        return False

    live_url = get_live_url(plugin, item_id, token)
    if not live_url:
        return False

    sfrtv_user_profile = get_sfrtv_user_profile(plugin, token)
    account_id = sfrtv_user_profile['siebelId']

    headers = {
        'user-agent': USER_AGENT,
        'customdata': CUSTOMDATA_LIVE.format(USER_AGENT, token, account_id),
        'origin': 'https://tv.sfr.fr',
        'referer': 'https://tv.sfr.fr/',
        'content-type': 'application/octet-stream'
    }

    return resolver_proxy.get_stream_with_quality(plugin,
                                                  video_url=live_url,
                                                  license_url=LICENSE_URL,
                                                  manifest_type='mpd',
                                                  headers=headers)
