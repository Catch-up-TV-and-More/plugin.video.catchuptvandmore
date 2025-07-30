# -*- coding: utf-8 -*-
# Copyright: (c) 2022-2025, Joaopa, nictjir, dimkroon  GNU General Public License v2.0+
# (see LICENSE.txt or https://www.gnu.org/licenses/gpl-2.0.txt)
# This file is part of Catch-up TV & More

from __future__ import unicode_literals

import re
import json
import base64
import urlquick
import time

import xbmcplugin

from codequick import Listitem, Resolver, Route, Script, utils

try:
    import urllib.parse
except ImportError:
    import urllib

try:
    from Crypto.Cipher import AES
    from Crypto.Util.Padding import unpad
    from Crypto.Hash import HMAC, SHA256
except ImportError:
    from Cryptodome.Cipher import AES
    from Cryptodome.Util.Padding import unpad
    from Cryptodome.Hash import HMAC, SHA256

from resources.lib.menu_utils import item_post_treatment
from resources.lib import web_utils, resolver_proxy

CORONA_URL = 'https://corona.channel5.com/'
BASIS_URL = CORONA_URL + 'shows/%s/seasons'
URL_SEASONS = BASIS_URL + '.json'
URL_EPISODES = BASIS_URL + '/%s/episodes.json'
FEEDS_API = 'https://feeds-api.channel5.com/collections/%s/concise.json'
URL_WATCHABLE = CORONA_URL + 'watchables/search.json'
URL_SHOWS = CORONA_URL + 'shows/search.json'
BASE_IMG = 'https://api-images.channel5.com/otis/images'
IMG_URL = BASE_IMG + '/episode/%s/320x180.jpg'
SHOW_IMG_URL = BASE_IMG + '/show/%s/320x180.jpg'
ONEOFF = CORONA_URL + 'shows/%s/episodes/next.json'
LIC_BASE = 'https://cassie.channel5.com/api/v2'
LICC_URL = LIC_BASE + '/%s/my5desktopng/%s.json?timestamp=%s'
KEYURL = "https://player.akamaized.net/html5player/core/html5-c5-player.js"

TXT_ENTER_UNAME = 30733
TXT_ENTER_PASSW = 30734
TXT_LOGIN_SUCCESS = 30735
TXT_LOGOUT_SUCCESS = 30736
TXT_INFORMATION = 30600
TXT_ACCOUNT_REQUIRED = 30604
PUBLIC_SITE = 'www.channel5.com'

# Connect and receive timeouts for HTTP requests.
REQ_TIMEOUT = (3.5, 7)
DFLT_CACHE_TIME = 600
DFLT_SORT_METHODS = (xbmcplugin.SORT_METHOD_UNSORTED, xbmcplugin.SORT_METHOD_TITLE_IGNORE_THE)
DFLT_PAGE_SIZE = 50

GENERIC_HEADERS = {"User-Agent": web_utils.get_random_ua()}
feeds_api_params = {
    'vod_available': 'my5desktop',
    'friendly': '1'
}

view_api_params = {
    'platform': 'my5desktop',
    'friendly': '1'
}

lic_headers = {
    'User-Agent': web_utils.get_random_ua(),
    'Referer': 'https://www.channel5.com/',
    'Content-Type': '',
}


def getdata(ui, media):
    resp = urlquick.get(KEYURL, headers=GENERIC_HEADERS, timeout=REQ_TIMEOUT, max_age=0)
    content = resp.content.decode("utf-8", "ignore")
    ss = re.compile(r';}}}\)\(\'(......)\'\)};').search(content).group(1)
    m = re.compile(r'\(\){return "(.{3000,})";\}').search(content).group(1)

    timeStamp = str(int(time.time()))
    CALL_URL = LICC_URL % (media, ui, timeStamp)

    try:
        h = urllib.parse.unquote(m)
        hmac_update = bytes(CALL_URL, encoding="utf-8")
    except Exception:
        h = urllib.unquote(m.encode('utf-8')).decode('utf-8', 'ignore')
        hmac_update = str(CALL_URL)

    z = [ord(c) for c in h]
    y = 0
    sout = ""
    for x in z:
        if (y > 5):
            y = 0
        k = x ^ ord(ss[y])
        if (k > 31) and (k < 127):
            sout = sout + chr(k)
        y = y + 1

    m = re.compile(r'SSL_MA..(.{24})..(.{24})').findall(sout)[0]
    h = HMAC.new(base64.urlsafe_b64decode(str(m[0])), digestmod=SHA256)
    h.update(hmac_update)
    auth = base64.urlsafe_b64encode(h.digest()).decode('utf-8')[:-1].replace("+", "-").replace("/", "_")

    return CALL_URL, auth, m[1]


def ivdata(lic_full, auth):
    params = {'auth': auth}
    resp = urlquick.get(lic_full, headers=GENERIC_HEADERS, params=params,
                        timeout=REQ_TIMEOUT, max_age=-1)
    root = json.loads(resp.text)
    return root['iv'], root['data']


def mangle(result):
    return result.replace("-", "+").replace("_", "/")


def getUseful(s):
    keyserver = 'NA'
    streamUrl = 'NA'
    subtitile = 'NA'
    data = json.loads(s)
    jsonData = data['assets']
    for x in jsonData:
        if (x['drm'] == "widevine"):
            keyserver = (x['keyserver'])
            u = (x['renditions'])
            for i in u:
                streamUrl = i['url']
    return streamUrl, keyserver, subtitile


def part2(iv, aesKey, rdata):
    realIv = base64.b64decode(mangle(iv)).ljust(16, b'\0')
    realAesKey = base64.b64decode(mangle(aesKey)).ljust(16, b'\0')
    realRData = base64.b64decode(mangle(rdata))
    cipher = AES.new(realAesKey, AES.MODE_CBC, iv=realIv)
    dataToParse = unpad(cipher.decrypt(realRData), 16).decode('utf-8')
    return getUseful(dataToParse)


@Route.register(autosort=False, content_type="videos")
def list_main_page(plugin, **kwargs):
    yield from list_hero_items(plugin)
    yield Listitem.from_dict(
        callback=list_collections,
        label='Collections',
        params={'browse_name': 'PLC_My5DesktopFASTHomePageSubNav'}
    )
    yield Listitem.from_dict(
        callback=list_categories,
        label='Categories'
    )
    yield Listitem.search(do_search)


def list_hero_items(plugin):
    """List the hero items normally presented on the home page of the website."""
    for li in list_collections(plugin, 'PLC_My5DesktopHeroRail'):
        title = li.label
        li.info['title'] = f'[B][COLOR orange]{title}[/COLOR][/B]'
        yield li


@Route.register
def list_categories(plugin, **kwargs):
    plugin.add_sort_methods(*DFLT_SORT_METHODS)
    resp = urlquick.get(FEEDS_API % 'PLC_My5SubGenreBrowsePageSubNav', headers=GENERIC_HEADERS,
                        params=feeds_api_params, timeout=REQ_TIMEOUT, max_age=DFLT_CACHE_TIME)
    root = json.loads(resp.text)
    for category in root['filters']['contents']:
        try:
            item = Listitem()
            item.label = category['title']
            browse_name = category['id']
            item.set_callback(list_collections, browse_name=browse_name)
            item_post_treatment(item)
            yield item
        except (ValueError, AttributeError):
            pass


@Route.register(redirect_single_item=True, autosort=False, content_type="videos")
def list_collections(plugin, browse_name, **kwargs):
    """List the contents of a collection, category, or sub-collection.

    """
    plugin.add_sort_methods(*DFLT_SORT_METHODS)

    if (browse_name == "PLC_My5AllShows"):
        w_params = {
            'limit': DFLT_PAGE_SIZE,
        }
        yield from search_shows(plugin, w_params)
        return

    resp = urlquick.get(FEEDS_API % browse_name, headers=GENERIC_HEADERS, params=feeds_api_params,
                        timeout=REQ_TIMEOUT, max_age=DFLT_CACHE_TIME)
    root = json.loads(resp.text)
    filters = root['filters']
    items_type = filters['type']
    subgenres = filters.get('vod_subgenres')

    if subgenres:
        # Get the actual content of the collection based on the subgenre ID(s).
        # This is a type 'Show', but instead of a list of id's, it has vod_subgenres.
        req_params = {
            'limit': DFLT_PAGE_SIZE,
            'vod_subgenres[]': filters.get('vod_subgenres')
        }
        yield from search_shows(plugin, req_params)

    elif items_type == 'Show':
        ids = filters.get('ids')
        req_params = {
            'limit': len(ids),
            'ids[]': ids
        }
        yield from search_shows(plugin, req_params)

    elif items_type == 'Collection':
        try:
            for collection in filters['contents']:
                item = Listitem()
                item.label = collection['title']
                if collection.get('live'):
                    item.set_callback(get_live_url, item_id=collection['channel'])
                else:
                    browse_name = collection['id']
                    if browse_name in ('PLC_My5DesktopHeroRail',
                                       'PLC_My5ContinueWatchingRail',
                                       'PLC_My5DesktopRecommendationsRail'):
                        continue
                    item.set_callback(list_collections, browse_name=browse_name)
                item_post_treatment(item)
                yield item
        except (ValueError, AttributeError):
            pass

    elif items_type == 'Watchable':
        ids = filters.get('ids')
        yield from search_watchables(plugin, ids)
    else:
        yield False
        return


@Route.register(content_type="videos")
def search_shows(plugin, params, offset=0):
    """List shows obtained from the search endpoint for shows.

    This provides content for many listings, like collections, categories,
    and of course search.
    Query string parameters ``params`` define the search criteria, which can
    be a list of show id's, a list of subcategory id's, a or search term.

    """
    std_params = {
        'offset': offset,
        'platform': 'my5desktop',
        'friendly': '1'
    }
    std_params.update(params)
    resp = urlquick.get(url=URL_SHOWS,
                        headers=GENERIC_HEADERS,
                        params=std_params,
                        timeout=REQ_TIMEOUT,
                        max_age=DFLT_CACHE_TIME)
    data = json.loads(resp.text)

    for emission in data['shows']:
        title = emission['title']
        fname = emission['f_name']
        show_id = emission['id']

        item = Listitem()
        item.label = title
        item.art['thumb'] = item.art['landscape'] = SHOW_IMG_URL % show_id
        item.info['plot'] = emission['s_desc']
        item.info['genre'] = emission['genre']
        if "standalone" in emission:
            # The item is playable
            item.set_callback(get_video_url,
                              fname=fname,
                              season_f_name="",
                              show_id='',
                              standalone="yes")
        else:
            item.set_callback(list_seasons,
                              fname=fname,
                              pid=show_id,
                              title=title)
        item_post_treatment(item)
        yield item
    if 'next_page_url' in data:
        item = Listitem.next_page(callback=search_shows,
                                  params=params,
                                  offset=data['next_offset'])
        item.property['SpecialSort'] = 'bottom'
        yield item


@Route.register(content_type="videos")
def search_watchables(plugin, ids):
    """List playable items obtained from the search endpoint for watchables.

    This provides content for some collections and categories.

    """
    w_params = {
        'limit': len(ids),
        'offset': '0',
        'platform': 'my5desktop',
        'friendly': '1',
        'ids[]': ids
    }
    # Get details of the already fetched list of watchable ids.
    resp = urlquick.get(URL_WATCHABLE,
                        headers=GENERIC_HEADERS,
                        params=w_params,
                        timeout=REQ_TIMEOUT)
    root = json.loads(resp.text)
    for watchable in root['watchables']:
        yield parse_watchable(watchable)


@Route.register(redirect_single_item=True, autosort=False, content_type="videos")
def list_seasons(plugin, fname, pid, title, **kwargs):
    plugin.add_sort_methods(*DFLT_SORT_METHODS)

    resp = urlquick.get(URL_SEASONS % fname, headers=GENERIC_HEADERS, params=view_api_params,
                        timeout=REQ_TIMEOUT, max_age=DFLT_CACHE_TIME)
    root = json.loads(resp.text)

    for season in root['seasons']:
        item = Listitem()
        season_number = season['seasonNumber']
        item.label = ' '.join((title, '- Season', season_number))
        item.art['thumb'] = item.art['landscape'] = SHOW_IMG_URL % pid
        item.set_callback(list_episodes, fname=fname, season_number=season_number)
        item_post_treatment(item)
        yield item


@Route.register(autosort=False, content_type="episodes")
def list_episodes(plugin, fname, season_number, **kwargs):
    plugin.add_sort_methods(*(DFLT_SORT_METHODS + (xbmcplugin.SORT_METHOD_DURATION, )))

    resp = urlquick.get(URL_EPISODES % (fname, season_number), headers=GENERIC_HEADERS,
                        params=view_api_params, timeout=REQ_TIMEOUT, max_age=DFLT_CACHE_TIME)
    root = json.loads(resp.text)
    for episode in root['episodes']:
        yield parse_watchable(episode, from_episode_list=True)


def parse_watchable(watchable, from_episode_list=False):
    """Parse data of a single watchable item and return a codequick Listitem.

    Parse item data for functions that retrieve watchables, like
    `search_watchables()` and `list_episodes()`.

    Watchables can are various types of items, like episodes of series, or one-offs
    like documentaties, or films.

    Listitem label and description are handled differently depending on the origin of the
    watchable data. If the watchable originates from listing the contents of a series,
    we just use the title of the episode as label for the listitem.
    When the data is from another list, like a collection, the title of the programme the
    watchable belongs to is use as Listitem label, because episode titles like 'episode 4',
    have no meaning in this context. In that case more info about the origin or episode
    title, etc is provided in the description.

    Args:
        watchable (dict)
        from_episode_list (bool): True when watchable data originates from season listing.
    Returns:
        Listitem: codequick listitem

    """
    title = watchable['title']
    show_title = watchable['sh_title']
    season_nr = watchable.get('sea_num')
    description = watchable.get('m_desc') or watchable.get('s_desc', show_title)
    watchable_id = watchable['id']
    # Field 'adv' can be absent, None, a normal string, empty string, or a single space character.
    advice = (watchable.get('adv') or '').strip()
    title_line = None

    item = Listitem()
    item.art['thumb'] = item.art['landscape'] = IMG_URL % watchable_id
    if from_episode_list:
        item.label = title
    else:
        item.label = show_title
        if season_nr:
            # This watchable is part of a series
            title_line = f"series {watchable.get('sea_num', '')} - {title}"
            # Create a context menu to go to episode's programme folder
            item.context.container(list_seasons,
                                   'View all episodes',
                                   fname=watchable['sh_f_name'],
                                   pid=watchable['sh_id'],
                                   title=show_title)

    item.info['plot'] = '\n'.join(txt for txt in (
        title_line,
        ' ' if title_line else None,
        description,
        ' ',
        advice,
        availability(watchable.get('vod_e'))
    ) if txt)
    t = int(int(watchable['len']) // 1000)
    item.info['duration'] = t
    item.info['genre'] = watchable['genre']
    item.set_callback(get_video_url,
                      fname=watchable.get('f_name', ''),
                      season_f_name=watchable.get('sea_f_name', ''),
                      show_id=watchable_id,
                      standalone="no")
    item_post_treatment(item)
    return item


@Route.register(content_type="videos")
def do_search(plugin, search_query, **_):
    yield from search_shows(plugin, {'query': search_query, 'limit': '20'})


@Resolver.register
def get_video_url(plugin, fname, season_f_name, show_id, standalone, **kwargs):
    if (standalone == "yes"):
        resp = urlquick.get(ONEOFF % fname, headers=GENERIC_HEADERS,
                            params=view_api_params, timeout=REQ_TIMEOUT, max_age=-1)
        root = json.loads(resp.text)
        show_id = root['id']

    LICFULL_URL, auth, aesKey = getdata(show_id, 'media')
    iv, data = ivdata(LICFULL_URL, auth)
    video_url, drm_url, sub_url = part2(iv, aesKey, data)

    # Attempt to expose FHD resolutions
    if video_url:
        replacements = {
            "_SD-tt.mpd": "-tt.mpd",
            "_SD.mpd": ".mpd"
        }
        for old, new in replacements.items():
            if old in video_url:
                new_url = video_url.replace(old, new)
                try:
                    resp = urlquick.get(new_url, headers=GENERIC_HEADERS, max_age=-1)
                    if resp.text:
                        video_url = new_url
                        break
                except Exception:
                    pass

    # Currently (Kodi 21.1), dash embedded subtitles from channel5 are not shown.
    # However, if the same subtitle url is passed to Kodi separately, it does work.
    subs_url = None
    if plugin.setting.get_boolean('active_subtitle'):
        resp = urlquick.get(video_url, headers=GENERIC_HEADERS, max_age=-1)
        dash_manifest = resp.text
        # Find the subtitles 'base url' in the manifest, which is actually the file name, rather than the base.
        match = re.search(r'<AdaptationSet mimeType="text/vtt"[^>]*>.+?<BaseURL>(.+?)</BaseURL>',
                          dash_manifest, re.DOTALL)
        if match:
            # Construct the full url from the real base and the file name.
            subs_url = '/'.join((video_url.rsplit('/', maxsplit=1)[0],
                                 match[1]))

    return resolver_proxy.get_stream_with_quality(plugin, video_url=video_url, license_url=drm_url,
                                                  manifest_type='mpd', headers=lic_headers,
                                                  subtitles=subs_url)


@Resolver.register
def get_live_url(plugin, item_id, **kwargs):

    LICFULL_URL, auth, aesKey = getdata(item_id, 'live_media')
    iv, data = ivdata(LICFULL_URL, auth)
    video_url, drm_url, sub_url = part2(iv, aesKey, data)

    return resolver_proxy.get_stream_with_quality(plugin, video_url=video_url, license_url=drm_url,
                                                  manifest_type='mpd', headers=lic_headers)


def availability(end_time):
    """Return a human-readable string indicating how long the programme is
    still available.

    Args:
        end_time (float): Timestamp when availability ends.
    Returns:
        str

    """
    if not end_time:
        return ''
    t_available = end_time - time.time()
    days_available = int(t_available / 86400)
    if days_available > 365:
        return 'Available for over a year.'
    elif days_available > 30:
        months = int(days_available // 30)
        return 'Available for {} month{}.'.format(months, 's' if months > 1 else '')
    elif days_available >= 1:
        return '[COLOR orange]Only {} day{} available.[/COLOR]'.format(
            days_available, 's' if days_available > 1 else '')
    else:
        hours_available = int(t_available / 3600)
        return '[COLOR orange]Only {} hour{} available.[/COLOR]'.format(
            hours_available, 's' if hours_available != 1 else '')


# -----------------------------------------------------------------------------
#           CHANNEL 5 ACCOUNT
# -----------------------------------------------------------------------------


def get_session_token(msg_on_fail=True):
    """Return the locally stored session token, which is needed to request user-related
    data from channel5.

    Args:
        msg_on_fail (bool):
            When `True` the user is asked to sign in when no token is available.
            When False the function fails silently.
    Returns:
        str
    """
    sess_token = Script.setting.get_string('uk.chan5.session-token')
    if sess_token:
        return sess_token
    else:
        Script.log("[UK-Chan5] No session token in settings, user has to log in")
        if not msg_on_fail:
            return None
        import xbmcgui
        xbmcgui.Dialog().ok(
            Script.localize(TXT_INFORMATION),
            Script.localize(TXT_ACCOUNT_REQUIRED) % ('Channel5 (UK)', ('%s' % PUBLIC_SITE)))
        return None


def enter_credentials(uname, passw):
    """Open the keyboard and ask the user to enter his username and password."""
    new_username = utils.keyboard(Script.localize(TXT_ENTER_UNAME), uname or '')
    if new_username:
        new_passw = utils.keyboard(Script.localize(TXT_ENTER_PASSW), passw or '', hidden=True)
    else:
        new_passw = ''
    return new_username, new_passw


def aws_authenticate(req_data):
    """Perform an authentication request and return a dict of tokens.

    Depending on req_data, does either a new log in with a username and password,
    or a token refresh.

    """
    try:
        headers = {
            "User-Agent": web_utils.get_random_ua(),
            'x-amz-target': 'AWSCognitoIdentityProviderService.InitiateAuth',
            'content-type': 'application/x-amz-json-1.1',
            'cache-control': 'max-age=0'
        }
        # Post credentials
        resp = urlquick.post(
            'https://cognito-idp.eu-west-2.amazonaws.com',
            headers=headers,
            json=req_data,
            timeout=REQ_TIMEOUT,
            max_age=-1
        )
        resp.raise_for_status()
        data = json.loads(resp.content)
        return data['AuthenticationResult']
    except urlquick.HTTPError as e:
        Script.log("[UK-Chan5] Failed to authenticate: %r - %s",
                   (e, e.response.content), lvl=Script.ERROR)
        try:
            resp_data = e.response.json()
            msg = resp_data.get('message') or resp_data['__type']
            Script.log("[UK-Chan5] Authentication error msg '%s' from error data '%s'",
                       (msg, resp_data), Script.ERROR)
        except Exception as err:
            Script.log("[UK-Chan5] Failed to parse error: %r",
                       (err, ), Script.ERROR)
            raise e
        raise urlquick.HTTPError(msg)


def request_session_token(id_token):
    """Request a session token from channel5.
    This token is needed to request authenticated data from channel5.

    """
    headers = GENERIC_HEADERS
    resp = urlquick.post(
        'https://userservice-api.channel5.com/user/validateCognitoToken',
        headers=headers,
        json={'cognitoIdToken': id_token},
        timeout=REQ_TIMEOUT,
        max_age=-1
    )
    resp.raise_for_status()
    data = json.loads(resp.content)
    sess_token = data['sessionToken']
    return sess_token


def perform_signin_request(uname, passw):
    """Sign in to a Channel5 account with `uname` and `passw`.

    First obtain a set of tokens from AWS and then use the IdToken to
    get a session token from channel5.

    """
    Script.log("[UK-Chan5] Trying to sign in to account", lvl=Script.INFO)
    req_data = {
        "AuthFlow": "USER_PASSWORD_AUTH",
        "ClientId": "10ap8l6jp0vhreaac79c3qr1lq",
        "AuthParameters": {"USERNAME": uname, "PASSWORD": passw},
        "ClientMetadata": {}
    }

    auth_result = aws_authenticate(req_data)
    sess_token = request_session_token(auth_result['IdToken'])
    # Store the session token for later use.
    Script.setting['uk.chan5.session-token'] = sess_token
    Script.log("[UK-Chan5] Sign in successful.", lvl=Script.INFO)
    return True


@Script.register
def sign_in_account(addon):
    """Entry point for the action 'Log in to channel5 account' in settings.

    Ask the user to enter his username and password, try to log in and inform the
    user of success or failure. On failure, keep asking for username or password
    until log in succeeds, or the user cancels the keyboard.

    """
    import xbmcgui
    import xbmc

    uname = None
    passw = None

    while True:
        uname, passw = enter_credentials(uname, passw)
        if not all((uname, passw)):
            addon.log("[UK-Chan5] Login canceled by user", lvl=Script.INFO)
            return
        try:
            perform_signin_request(uname, passw)
            xbmcgui.Dialog().ok('Channel5', Script.localize(TXT_LOGIN_SUCCESS))
            xbmc.executebuiltin('Container.Refresh')
            return
        except urlquick.HTTPError as e:
            addon.notify("Error", str(e), display_time=7000)


@Script.register
def sign_out_account(_):
    """Entry point for the action 'Log out from channel5 account' in settings."""
    import xbmcgui

    Script.setting['uk.chan5.session-token'] = ''
    xbmcgui.Dialog().ok('Channel5', Script.localize(TXT_LOGOUT_SUCCESS))
