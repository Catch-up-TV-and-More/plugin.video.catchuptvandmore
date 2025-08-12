# -*- coding: utf-8 -*-
# Copyright: (c) JUL1EN094, SPM, SylvainCecchetto
# Copyright: (c) 2016, SylvainCecchetto
# Copyright: (c) 2023, darodi
# GNU General Public License v2.0+ (see LICENSE.txt or https://www.gnu.org/licenses/gpl-2.0.txt)

# This file is part of Catch-up TV & More

from __future__ import unicode_literals

import json
import random
import re
import sys
from builtins import str
import requests

# noinspection PyUnresolvedReferences
import urlquick
# noinspection PyUnresolvedReferences
from codequick import Listitem, Resolver, Route, Script
# noinspection PyUnresolvedReferences
from kodi_six import xbmcgui

from resources.lib import download, resolver_proxy, web_utils
from resources.lib.menu_utils import item_post_treatment
from resources.lib.kodi_utils import get_selected_item_art, get_selected_item_info, get_selected_item_label

PUBLIC_SITE = 'https://www.rtlplay.be'

# Url to get channel's categories
# e.g. Info, Divertissement, Séries, ...
# We get an id by category
BASE_URL = "https://www.rtlplay.be/rtlplay"
URL_LFVP_API = 'https://lfvp-api.dpgmedia.net'
URL_CONFIG = 'https://videoplayer-service.dpgmedia.net/play-config/%s'
URL_SSO_LOGIN = 'https://sso.rtl.be/api/account/login'
URL_SSO_AUTH = 'https://sso.rtl.be/oidc/account/authenticate'
URL_LICENCE_KEY = ('https://lic.drmtoday.com/license-proxy-widevine/cenc/'
                   '|Content-Type=&User-Agent=Mozilla/5.0 (Windows NT 10.0; WOW64)'
                   ' AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3041.0 Safari/537.36'
                   '&Host=lic.drmtoday.com&x-dt-auth-token=%s&x-customer-name=rtlbe|R{SSM}|JBlicense')

POPCORN_SDK = '8'
REQUESTS_TIMEOUT = 8

LIVE_CHANNEL = {
    "rtl_tvi": "tvi",
    "club_rtl": "club",
    "plug_rtl": "plug",
    "rtl_info": "rtl_info",
    "rtl_sport": "rtl_sport",
    "bel_rtl": "bel",
    "contact": "contact",
    "rtl_play": "rtlplay",
    "rtl_district": "RTLdistrict"
}

GENERIC_HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:128.0) Gecko/20100101 Firefox/128.0',
    'Accept': '*/*',
    'Accept-Language': 'fr,fr-FR;q=0.8,en-US;q=0.5,en;q=0.3',
    'Connection': 'keep-alive',
    'Upgrade-Insecure-Requests': '1',
    'Sec-Fetch-Dest': 'document',
    'Sec-Fetch-Mode': 'navigate',
    'Sec-Fetch-Site': 'none',
    'Sec-Fetch-User': '?1',
    'Sec-GPC': '1',
    'Priority': 'u=0, i',
}

RTLPLAY_HEADERS = {
    'User-Agent': 'RTL_PLAY/21.250624 (com.tapptic.rtl.tvi; build:20529; Android TV 30) okhttp/4.12.0',
    'Accept': '*/*',
    'Accept-Encoding': 'gzip',
    'Connection': 'Keep-Alive',
    'Content-Type': 'application/json; charset=UTF-8',
    'lfvp-device-segment': 'TV>Android',
    'x-app-version': '21',
}


@Route.register
def rtlplay_root(plugin, item_id, **kwargs):
    # Category items
    _PARAMS = {
        'temsPerSwimlane': '20',
        'defaultImageOrientation': 'landscape',
        'hideBannerRow': 'true',
    }
    resp = urlquick.get(URL_LFVP_API + '/RTL_PLAY/storefronts/accueil', headers=RTLPLAY_HEADERS, params=_PARAMS, max_age=-1).content.decode()
    json_parser = json.loads(resp)

    for array in json_parser.get('rows'):
        category_id = ''
        category_name = ''
        if array.get('rowType') in ['SWIMLANE_DEFAULT', 'SWIMLANE_PORTRAIT', 'SWIMLANE_LANDSCAPE']:
            category_id = str(array.get('id'))
            category_name = array.get('title').strip()
        if len(category_name) == 0:
            continue

        item = Listitem()
        item.label = category_name
        item.set_callback(list_programs,
                          item_id=item_id,
                          category_id=category_id)
        item_post_treatment(item)
        yield item

    # Search items
    item = Listitem.search(list_videos_search, item_id=item_id, page='0')
    item_post_treatment(item)
    yield item


@Route.register
def list_videos_search(plugin, search_query, item_id, page, **kwargs):
    if search_query is None or len(search_query) == 0:
        return False

    resp = urlquick.get(URL_LFVP_API + '/RTL_PLAY/search?query=' + search_query, headers=RTLPLAY_HEADERS, max_age=-1).content.decode()
    json_parser = json.loads(resp)

    at_least_one_item = False
    for array in json_parser.get('results', []):
        if "exact" == array.get('type'):
            for datas in array.get('teasers'):
                datas_id = datas.get('detailId')
                datas_title = datas.get('title')
                datas_image = datas.get('imageUrl')

                at_least_one_item = True
                item = Listitem()
                item.label = datas_title
                item.art['thumb'] = item.art['landscape'] = item.art['fanart'] = datas_image
                item.set_callback(list_program_categories,
                                  item_id=item_id,
                                  program_id=datas_id)
                item_post_treatment(item)
                yield item

    if not at_least_one_item:
        plugin.notify(plugin.localize(30718), '')
        yield False


@Route.register
def list_programs(plugin, item_id, category_id, **kwargs):
    """
    Build programs listing
    - Les feux de l'amour
    - ...
    """
    resp = urlquick.get(URL_LFVP_API + '/RTL_PLAY/storefronts/accueil/detail/' + category_id, headers=RTLPLAY_HEADERS, max_age=-1).content.decode()
    json_parser = json.loads(resp)

    for array in json_parser.get('row').get('teasers'):
        program_title = array.get('title')
        program_id = array.get('detailId')
        program_image = array.get('imageUrl')
        program_desc = array.get('description')

        item = Listitem()
        item.label = program_title
        item.info['plot'] = program_desc
        item.art['thumb'] = item.art['landscape'] = item.art['fanart'] = program_image
        item.set_callback(list_program_categories,
                          item_id=item_id,
                          program_id=program_id)
        item_post_treatment(item)
        yield item


@Route.register
def list_program_categories(plugin, item_id, program_id, **kwargs):
    """
    Build program categories
    - Toutes les vidéos
    - Tous les replays
    - Saison 1
    - ...
    """
    resp = urlquick.get(URL_LFVP_API + '/RTL_PLAY/detail/' + program_id, headers=RTLPLAY_HEADERS, max_age=-1).content.decode()
    json_parser = json.loads(resp)

    channel_image = json_parser.get('landscapeTeaserImageUrl')
    channel_id = json_parser.get('id')
    channel_title = json_parser.get('name')
    channel_desc = json_parser.get('description')
    for item_season in json_parser.get('seasonIndices', []):
        item = Listitem()
        item.label = 'Saison ' + str(item_season)
        item.info['plot'] = channel_desc
        item.art['thumb'] = item.art['landscape'] = item.art['fanart'] = channel_image
        item.set_callback(list_videos,
                          item_id=item_id,
                          program_id=program_id,
                          season_id=item_season)
        item_post_treatment(item)
        yield item

    if not json_parser.get('seasonIndices', []):
        item = Listitem()
        item.label = channel_title
        item.info['plot'] = channel_desc
        item.art['thumb'] = item.art['landscape'] = item.art['fanart'] = channel_image
        item.info['duration'] = json_parser.get('durationSeconds')
        item.set_callback(get_video_url,
                          item_id=item_id,
                          video_id=channel_id)
        item_post_treatment(item, is_playable=True, is_downloadable=False)
        yield item


@Route.register
def list_videos(plugin, item_id, program_id, season_id, **kwargs):
    if season_id is not None:
        params = {'selectedSeasonIndex': season_id, }
    else:
        params = None

    resp = urlquick.get(URL_LFVP_API + '/RTL_PLAY/detail/' + program_id, headers=RTLPLAY_HEADERS, params=params, max_age=-1).content.decode()
    json_parser = json.loads(resp)

    at_least_one_item = False
    for array in json_parser.get('selectedSeason').get('episodes'):
        video_id = array.get('id')
        video_title = array.get('name')
        video_desc = array.get('description')
        video_image = array.get('imageUrl')
        video_duration = array.get('durationSeconds')

        at_least_one_item = True
        item = Listitem()
        item.label = video_title
        item.info['plot'] = video_desc
        item.art['thumb'] = item.art['landscape'] = item.art['fanart'] = video_image
        item.info['duration'] = video_duration
        item.set_callback(get_video_url,
                          item_id=item_id,
                          video_id=video_id)
        item_post_treatment(item, is_playable=True, is_downloadable=False)
        yield item

    if not at_least_one_item:
        plugin.notify(plugin.localize(30718), '')
        yield False


@Resolver.register
def get_login_token(plugin, **kwargs):
    login = plugin.setting.get_string('rtlplaybe.login')
    password = plugin.setting.get_string('rtlplaybe.password')
    if login == '' or password == '':
        xbmcgui.Dialog().ok(
            plugin.localize(30600),
            plugin.localize(30604) % ('RTLPlay (BE)', ('%s' % PUBLIC_SITE)))
        return None

    # RTLPLAY Device_Id
    response = urlquick.get(BASE_URL, headers=GENERIC_HEADERS, max_age=-1)
    cookies = response.cookies.get_dict()
    lfvp_device_id = cookies['lfvp_device_id']
    lfvp_disabled_storefronts = cookies['lfvp_disabled_storefronts']
    ak_bmsc = cookies['ak_bmsc']

    # SSO token
    cnx_cookies = {
        'lfvp_device_id': lfvp_device_id,
        'lfvp_disabled_storefronts': lfvp_disabled_storefronts,
        'ak_bmsc': ak_bmsc,
        'lfvp_auth.redirect_uri': BASE_URL,
    }
    response = urlquick.get(BASE_URL + '/connexion', cookies=cnx_cookies, headers=GENERIC_HEADERS, allow_redirects=True, timeout=REQUESTS_TIMEOUT, max_age=-1)
    sso_url = []
    if response.history:
        for resp in response.history:
            sso_url.append(resp.url)
        sso_url.append(response.url)

    json_data = {
        'username': login,
        'password': password,
    }
    
    try:
        response = urlquick.post(URL_SSO_LOGIN, headers=GENERIC_HEADERS, json=json_data, timeout=10, max_age=-1)
        
        if response.status_code != 200:
            xbmcgui.Dialog().ok(
                plugin.localize(30600),
                f'RTL Play login failed: HTTP {response.status_code}. Please check your internet connection.')
            return None
            
        json_parser = response.json()
        
        if json_parser.get('httpStatusCode') == 400:
            xbmcgui.Dialog().ok(
                plugin.localize(30600),
                'RTL Play login failed: Invalid credentials. Please check your username and password in addon settings.')
            return None
            
        if 'data' not in json_parser or 'userAccount' not in json_parser['data']:
            xbmcgui.Dialog().ok(
                plugin.localize(30600),
                'RTL Play login failed: Unexpected response format. The service may have changed.')
            return None

        sso_token = json_parser['data']['userAccount']['session']['encryptedToken']
        sso_cookies = response.cookies.get_dict()

    except Exception as e:
        xbmcgui.Dialog().ok(
            plugin.localize(30600),
            f'RTL Play login error: {str(e)}. Please try again later.')
        return None

    # SSO auth
    try:
        params = {
            'redirectUrl': sso_url[1].replace('https://sso.rtl.be', '') if len(sso_url) > 1 else '',
            'token': sso_token,
        }
        response = urlquick.get(URL_SSO_AUTH, params=params, cookies=sso_cookies, headers=GENERIC_HEADERS, timeout=REQUESTS_TIMEOUT, max_age=-1)
        
        if response.status_code != 200:
            xbmcgui.Dialog().ok(
                plugin.localize(30600),
                f'RTL Play SSO authentication failed: HTTP {response.status_code}')
            return None
            
        response_content = response.content.decode()
        sso_code = re.findall(r'name=\"code\" value=\"(.*)\"', response_content)
        sso_state = re.findall(r'name=\"state\" value=\"(.*)\"', response_content)
        
        if not sso_code or not sso_state:
            xbmcgui.Dialog().ok(
                plugin.localize(30600),
                'RTL Play SSO authentication failed: Could not extract auth codes')
            return None

        # RTLPlay callback
        cookies = {
            'lfvp_device_id': lfvp_device_id,
            'lfvp_disabled_storefronts': lfvp_disabled_storefronts,
            'ak_bmsc': ak_bmsc,
            'lfvp_auth.redirect_uri': BASE_URL,
            'lfvp_auth.state': sso_state[0],
        }
        data = {
            'code': sso_code[0],
            'state': sso_state[0],
            'iss': 'https://sso.rtl.be/oidc/',
        }
        
    except Exception as e:
        xbmcgui.Dialog().ok(
            plugin.localize(30600),
            f'RTL Play SSO error: {str(e)}')
        return None
    response = requests.post(BASE_URL + '/login-callback', cookies=cookies, headers=GENERIC_HEADERS, data=data, allow_redirects=True, timeout=REQUESTS_TIMEOUT)
    login_cookie = []
    if response.history:
        for resp in response.history:
            login_cookie.append(resp.cookies.get_dict())
    callback_cookie = response.cookies.get_dict()

    login_token = {
        "ak_bmsc": ak_bmsc,
        "bm_sv": callback_cookie['bm_sv'],
        "lfvp_access_token": login_cookie[0]['lfvp_access_token'],
        "lfvp_device_id": lfvp_device_id,
        "lfvp_disabled_storefronts": "",
        "lfvp_id_token": login_cookie[0]['lfvp_id_token'],
        "lfvp_refresh_token": login_cookie[0]['lfvp_refresh_token'],
    }
    for profile_id in login_cookie:
        if 'lfvp_auth.profile' in profile_id:
            x_dpp_profile = re.match(r"^([a-f\d]{8}(-[a-f\d]{4}){3}-[a-f\d]{12})", profile_id.get('lfvp_auth.profile'), re.IGNORECASE).group(1)
            login_token.update({"lfvp_auth.profile": x_dpp_profile, })
        if 'lfvp_auth_token' in profile_id:
            login_token.update({"lfvp_auth_token": profile_id.get('lfvp_auth_token'), })

    return login_token


@Resolver.register
def get_video_url(plugin, item_id, video_id, download_mode=False, **kwargs):
    video_url = BASE_URL + '/player/' + video_id
    manifest, license_url, lic_token = get_final_video_url(plugin, item_id, video_url)

    if manifest is None:
        plugin.notify('ERROR', plugin.localize(30713))
        return False

    if license_url is not None:
        license_url = URL_LICENCE_KEY % lic_token

    return resolver_proxy.get_stream_with_quality(
        plugin, video_url=manifest, manifest_type='mpd',
        license_url=license_url)


def get_final_video_url(plugin, item_id, video_url):
    login_token = get_login_token(plugin)
    if login_token is None:
        return None, None, None

    is_live = "/direct/" in video_url and "/player/" not in video_url
    
    # Use generic headers for the initial request to avoid detection
    headers = GENERIC_HEADERS.copy()
    response = urlquick.get(video_url, headers=headers, cookies=login_token, max_age=-1)
    
    # Check if we're redirected to authentication
    if response.status_code in [302, 303, 307, 308] or 'sso.rtl.be' in response.url:
        plugin.notify('ERROR', 'RTL Play authentication required. Please configure your login credentials in addon settings.')
        return None, None, None
    
    if response.status_code != 200:
        return None, None, None

    response_text = response.content.decode()
    
    # Try multiple patterns for API key extraction (updated for new site structure)
    api_key = None
    api_key_patterns = [
        r'apiKey["\']?\s*:\s*["\']([^"\']+)["\']',
        r'"apiKey"\s*:\s*"([^"]+)"',
        r'apiKey\s*=\s*["\']([^"\']+)["\']',
        r'api[_-]?key["\']?\s*:\s*["\']([^"\']+)["\']',
        r'x-api-key["\']?\s*:\s*["\']([^"\']+)["\']'
    ]
    
    for pattern in api_key_patterns:
        match = re.search(pattern, response_text, re.IGNORECASE)
        if match:
            api_key = match.group(1)
            break
    
    # Try multiple patterns for token extraction
    bearer_token = None
    token_patterns = [
        r'token["\']?\s*:\s*["\']([^"\']+)["\']',
        r'"token"\s*:\s*"([^"]+)"',
        r'bearer[_-]?token["\']?\s*:\s*["\']([^"\']+)["\']',
        r'authorization["\']?\s*:\s*["\']Bearer\s+([^"\']+)["\']',
        r'access[_-]?token["\']?\s*:\s*["\']([^"\']+)["\']'
    ]
    
    for pattern in token_patterns:
        match = re.search(pattern, response_text, re.IGNORECASE)
        if match:
            bearer_token = match.group(1)
            break

    # Extract content ID with updated patterns
    content_id = None
    if is_live:
        # Try multiple approaches for live content ID extraction
        content_id_patterns = [
            (r"playerData\s*=", r"assetId[\"']?\s*:\s*[\"']([^\"']+)[\"']"),
            (r"channel\s*:", r"id[\"']?\s*:\s*[\"']([^\"']+)[\"']"),
            (r"data-content-id\s*=\s*[\"']([^\"']+)[\"']", None),
            (r"contentId[\"']?\s*:\s*[\"']([^\"']+)[\"']", None),
            (r"assetId[\"']?\s*:\s*[\"']([^\"']+)[\"']", None)
        ]
        
        for pattern_pair in content_id_patterns:
            if pattern_pair[1] is None:
                # Direct pattern
                match = re.search(pattern_pair[0], response_text, re.IGNORECASE)
                if match:
                    content_id = match.group(1)
                    break
            else:
                # Two-step pattern (find section, then extract ID)
                section_match = re.search(pattern_pair[0] + "[^{}]+{([^{}]+)}", response_text)
                if section_match:
                    section_content = section_match.group(1)
                    id_match = re.search(pattern_pair[1], section_content)
                    if id_match:
                        content_id = id_match.group(1)
                        if len(content_id) > 0:
                            break
        
        # Fallback: try to extract from URL or use channel mapping
        if not content_id and item_id in LIVE_CHANNEL:
            content_id = LIVE_CHANNEL[item_id]
    else:
        # For non-live content, extract from URL
        match = re.search(r"/player/([^/?]*)", video_url)
        if match:
            content_id = match.group(1)

    # Validate that we have the required data
    if not content_id:
        plugin.notify('ERROR', 'Could not extract content ID from RTL Play page')
        return None, None, None
        
    if not bearer_token or not api_key:
        # Try alternative approach: use the LFVP API directly
        return get_stream_via_lfvp_api(plugin, item_id, content_id)

    # Continue with original approach if we have all required data
    headers_cfg = RTLPLAY_HEADERS.copy()
    headers_cfg.update({'x-api-key': api_key})
    headers_cfg.update({'popcorn-sdk-version': POPCORN_SDK})
    headers_cfg.update({'authorization': 'Bearer ' + bearer_token})
    
    params_cfg = {'startPosition': '0.0', 'autoPlay': 'true'}
    json_cfg = {"deviceType": "android-phone", "zone": "rtlplay"}
    
    try:
        response = urlquick.post(URL_CONFIG % content_id,
                                 params=params_cfg,
                                 headers=headers_cfg,
                                 json=json_cfg,
                                 timeout=REQUESTS_TIMEOUT,
                                 max_age=-1)
        
        if response.status_code == 403:
            plugin.notify('ERROR', 'RTL Play access forbidden - check authentication')
            return None, None, None
        
        if response.status_code != 200:
            plugin.notify('ERROR', f'RTL Play API error: {response.status_code}')
            return None, None, None

        response_data = json.loads(response.content.decode())

        if response_data.get("code", None) == 103 and "available" in response_data.get("type", "").lower():
            plugin.notify('ERROR', 'Content not available')
            return None, None, None
        if response_data.get("code", None) == 104 and "found" in response_data.get("type", "").lower():
            plugin.notify('ERROR', 'Content not found')
            return None, None, None

        if "video" not in response_data:
            plugin.notify('ERROR', 'Invalid video response from RTL Play')
            return None, None, None

        video_data = response_data["video"]
        manifest = None
        lic_token = None
        license_url = None
        
        for stream in video_data.get("streams", []):
            if stream.get("type") != "dash" or ".mpd" not in stream.get("url", ""):
                continue
            manifest = stream["url"]

            drm = stream.get("drm", None)
            if drm is None:
                break

            for k in drm:
                if "widevine" in k.lower():
                    drm = drm[k]
                    break

            lic_token = drm.get("drmtoday", {}).get("authToken")
            license_url = drm.get("licenseUrl")
            break

        return manifest, license_url, lic_token
        
    except Exception as e:
        plugin.notify('ERROR', f'RTL Play stream error: {str(e)}')
        return None, None, None


def get_stream_via_lfvp_api(plugin, item_id, content_id):
    """Fallback method using LFVP API directly"""
    try:
        # Try to get stream info via LFVP API as fallback
        headers = RTLPLAY_HEADERS.copy()
        
        # For live channels, try to construct the API call
        if item_id in LIVE_CHANNEL:
            api_url = f"{URL_LFVP_API}/RTL_PLAY/live/{LIVE_CHANNEL[item_id]}"
        else:
            api_url = f"{URL_LFVP_API}/RTL_PLAY/detail/{content_id}"
            
        response = urlquick.get(api_url, headers=headers, timeout=REQUESTS_TIMEOUT, max_age=-1)
        
        if response.status_code == 200:
            data = json.loads(response.content.decode())
            
            # Extract stream URL if available
            stream_url = data.get('streamUrl') or data.get('videoUrl') or data.get('url')
            if stream_url:
                return stream_url, None, None
                
        plugin.notify('ERROR', 'RTL Play fallback method failed')
        return None, None, None
        
    except Exception as e:
        plugin.notify('ERROR', f'RTL Play fallback error: {str(e)}')
        return None, None, None


@Resolver.register
def get_live_url(plugin, item_id, **kwargs):
    """Version optimisée pour Android TV - évite InputStream si problèmes DRM"""
    video_url = BASE_URL + '/direct/' + LIVE_CHANNEL[item_id]
    manifest, license_url, lic_token = get_final_video_url(plugin, item_id, video_url)

    if manifest is None:
        plugin.notify('ERROR', plugin.localize(30713))
        return False

    # CORRECTIF ANDROID TV: Préserver le DRM (ne plus le désactiver) pour éviter l'effet "audio uniquement"
    try:
        import xbmc
        build_version = xbmc.getInfoLabel('System.BuildVersion')
        platform = xbmc.getInfoLabel('System.Platform')
        
        if 'android' in build_version.lower() or 'android' in platform.lower():
            # Ancien comportement désactivait le DRM et causait la vidéo chiffrée (audio seul).
            # Nouveau comportement: on conserve le DRM et laisse resolver_proxy appliquer ses optimisations Android.
            if license_url is None:
                # Pas de DRM requis: on peut utiliser le lecteur natif Kodi en direct.
                from codequick import Listitem
                item = Listitem()
                item.path = manifest
                item.label = get_selected_item_label()
                item.art.update(get_selected_item_art())
                item.info.update(get_selected_item_info())
                item.info['mediatype'] = 'video'
                xbmc.log(f"[RTL-ANDROID] Lecteur natif (pas de DRM) pour: {manifest}", xbmc.LOGINFO)
                return item
            else:
                xbmc.log("[RTL-ANDROID] DRM conservé; InputStream Adaptive gérera Widevine avec optimisations Android", xbmc.LOGINFO)
                
    except Exception as e:
        import xbmc
        xbmc.log(f"[RTL-SIMPLE-ANDROID] Erreur détection Android: {e}", xbmc.LOGERROR)

    # Méthode normale avec InputStream (Windows/Android/autres)
    if license_url is not None:
        license_url = URL_LICENCE_KEY % lic_token

    return resolver_proxy.get_stream_with_quality(
        plugin, video_url=manifest, manifest_type='mpd',
        license_url=license_url)



def get_live_url_with_drm_options(plugin, item_id, video_id, **kwargs):
    """URL live RTL avec options DRM flexibles pour Android TV"""
    try:
        from resources.lib.web_utils import is_android_tv_arm
        from resources.lib import kodi_utils
        
        # Récupérer l'URL standard
        url_info = get_live_url(plugin, item_id, video_id, **kwargs)
        
        if url_info and is_android_tv_arm():
            # Sur Android TV ARM, offrir trois options
            
            # Option 1: Essayer DRM avec décodeur software
            print("[RTL-ANDROID-TV] Tentative DRM avec décodeur software")
            try:
                item = url_info.copy()
                if 'inputstream.adaptive.license_type' in item.get('properties', {}):
                    item['properties']['inputstream.adaptive.stream_secure'] = 'false'
                    item['properties']['inputstream.adaptive.crypto_mode'] = 'software'
                    item['properties']['inputstream.adaptive.decoder_secure'] = 'false'
                return item
            except:
                pass
                
            # Option 2: Si échec, essayer sans DRM
            print("[RTL-ANDROID-TV] Fallback: tentative sans DRM")
            try:
                item = url_info.copy()
                properties = item.get('properties', {})
                # Supprimer seulement les propriétés DRM problématiques
                properties.pop('inputstream.adaptive.license_type', None)
                properties.pop('inputstream.adaptive.license_key', None)
                properties.pop('inputstream.adaptive.license_data', None)
                # Garder les autres propriétés InputStream
                item['properties'] = properties
                return item
            except:
                pass
                
            # Option 3: Lecteur natif Kodi en dernier recours
            print("[RTL-ANDROID-TV] Fallback final: lecteur natif")
            try:
                # Extraire l'URL du stream
                stream_url = url_info.get('url', '')
                if stream_url:
                    return {
                        'url': stream_url,
                        'properties': {},
                        'headers': url_info.get('headers', {}),
                        'use_native_player': True
                    }
            except:
                pass
        
        # Retour standard pour autres plateformes
        return url_info
        
    except Exception as e:
        print(f"[RTL-ANDROID-TV] Erreur: {e}")
        # Fallback vers fonction originale
        return get_live_url(plugin, item_id, video_id, **kwargs)

