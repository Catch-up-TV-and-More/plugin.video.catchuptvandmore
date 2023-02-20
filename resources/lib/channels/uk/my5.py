# -*- coding: utf-8 -*-
# Copyright: (c) 2022, Joaopa  GNU General Public License v2.0+
# (see LICENSE.txt or https://www.gnu.org/licenses/gpl-2.0.txt)
# This file is part of Catch-up TV & More
# with contributions by
#    nictjir, joaopa00, berkhornet

from __future__ import unicode_literals

import re
import json
import base64
# from base64 import urlsafe_b64decode
import urlquick
import urllib
import time


from codequick import Listitem, Resolver, Route

try:
    from urllib.parse import urlencode
except ImportError:
    from urllib import urlencode


try:
    from Crypto.Cipher import AES
except ImportError:
    from Cryptodome.Cipher import AES

try:
    from Crypto.Util.Padding import unpad
except ImportError:
    from Cryptodome.Util.Padding import unpad

try:
    from Crypto.Hash import HMAC, SHA256
except ImportError:
    from Cryptodome.Hash import HMAC, SHA256

from resources.lib.kodi_utils import get_selected_item_art, get_selected_item_label
from resources.lib.kodi_utils import get_selected_item_info, INPUTSTREAM_PROP
from resources.lib.menu_utils import item_post_treatment

from resources.lib import web_utils

CORONA_URL = 'https://corona.channel5.com/'
BASIS_URL = CORONA_URL + 'shows/%s/seasons'
URL_SEASONS = BASIS_URL + '.json'
URL_EPISODES = BASIS_URL + '/%s/episodes.json'
FEEDS_API = 'https://feeds-api.channel5.com/collections/%s/concise.json'
URL_VIEW_ALL = CORONA_URL + 'shows/search.json'
URL_WATCHABLE = CORONA_URL + 'watchables/search.json'
URL_SHOWS = CORONA_URL + 'shows/search.json'
BASE_IMG = 'https://api-images.channel5.com/otis/images'
IMG_URL = BASE_IMG + '/episode/%s/320x180.jpg'
SHOW_IMG_URL = BASE_IMG + '/show/%s/320x180.jpg'
ONEOFF = CORONA_URL + 'shows/%s/episodes/next.json'
LIC_BASE = 'https://cassie.channel5.com/api/v2'
LICC_URL = LIC_BASE + '/media/my5desktopng/%s.json?timestamp=%s'
LIVE_LICC_URL = LIC_BASE + '/live_media/my5desktopng/%s.json?timestamp=%s'
KEYURL = "https://player.akamaized.net/html5player/core/html5-c5-player.js"
CERT_URL = 'https://c5apps.channel5.com/wv/c5-wv-app-cert-20170524.bin'
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
    'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:108.0) Gecko/20100101 Firefox/108.0',
    'Referer': 'https://www.channel5.com/',
    'Content-Type': '',
}


def change(auth):
    result = ''.join(str(x) for x in auth)
    result = result.replace("+", "-")
    result = result.replace("/", "_")
    result = re.sub(r'=={0,}$', '', result)
    return (result)


def url_parse(queryStr):
    unicodestring = urllib.parse.unquote(queryStr)
    return [ord(c) for c in unicodestring]


def getdata(ui, watching):
    resp = urlquick.get(KEYURL)
    content = resp.content.decode("utf-8", "ignore")

    m = re.compile(r';}}}\)\(\'(......)\'\)};').search(content)
    ss = m.group(1)
    m = re.compile(r'\(\){return "(.{3000,})";\}').search(content)
    s = str(m.group(1))
    z = url_parse(s)
    charl = len(z)
    y = 0
    sout = ""
    for x in range(charl):
        if (y > 5):
            y = 0
        k = z[x] ^ ord(ss[y])
        if ((k > 31) and (k < 127)):
            sout = sout + chr(k)
        y = y + 1

    m = re.compile(r'SSL_MA..(.{24})..(.{24})').search(sout)
    k1 = m.group(1)
    k2 = m.group(2)

    m = re.compile(r'2689\)\]=\[(\d+),(\d+),(\d+),(\d+),(\d+),(\d+),(\d+),(\d+)\]').search(content)
    timeStamp = str(int(time.time()))
    if (watching == "vod"):
        CALL_URL = LICC_URL % (ui, timeStamp)
    else:
        CALL_URL = LIVE_LICC_URL % (ui, timeStamp)
    h = HMAC.new(base64.urlsafe_b64decode(k1), digestmod=SHA256)
    h.update(bytes(CALL_URL, encoding="utf-8"))
    webSafeAuthKey = str(base64.urlsafe_b64encode(h.digest()))
    LICFULL_URL = CALL_URL + "&auth=" + change(webSafeAuthKey[2:-2])
    return (LICFULL_URL, k2)


def ivdata(URL):
    resp = urlquick.get(URL, headers=GENERIC_HEADERS)
    root = json.loads(resp.text)
    iv = root['iv']
    data = root['data']
    return (iv, data)


def mangle(st):
    result = st
    result = result.replace("-", "+")
    result = result.replace("_", "/")
    return (result)


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
    return (streamUrl, keyserver, subtitile)


def part2(iv, aesKey, rdata):
    realIv = (base64.b64decode(mangle(iv))).ljust(16, b'\0')
    realAesKey = (base64.b64decode(mangle(aesKey))).ljust(16, b'\0')
    realRData = base64.b64decode(mangle(rdata))
    cipher = AES.new(realAesKey, AES.MODE_CBC, iv=realIv)
    dataToParse = unpad(cipher.decrypt(realRData), 16)
    (stream, drmurl, sub) = getUseful(dataToParse.decode('utf-8'))
    return (stream, drmurl, sub)


@Route.register
def list_categories(plugin, **kwargs):
    resp = urlquick.get(FEEDS_API % 'PLC_My5SubGenreBrowsePageSubNav',
                        headers=GENERIC_HEADERS, params=feeds_api_params)
    root = json.loads(resp.text)
    for i in range(int(root['total_items'])):
        try:
            item = Listitem()
            item_id = 1
            item.label = root['filters']['contents'][i]['title']
            browse_name = root['filters']['contents'][i]['id']
            offset = "0"
            item.set_callback(list_subcategories, item_id=item_id,
                              browse_name=browse_name, offset=offset)
            item_post_treatment(item)
            yield item
        except (IndexError, ValueError):
            pass


@Route.register
def list_subcategories(plugin, item_id, browse_name, offset, **kwargs):
    if (browse_name == "PLC_My5AllShows"):
        w_params = '?limit=25&offset=%s&platform=my5desktop&friendly=1' % str(offset)
        s = URL_SHOWS + w_params
        resp = urlquick.get(s, headers=GENERIC_HEADERS, params=feeds_api_params)
        root = json.loads(resp.text)
        item_number = int(root['size'])
        for emission in root['shows']:
            if "standalone" in emission:
                item = Listitem()
                item.label = emission['title']
                item.info['plot'] = emission['s_desc']
                fname = emission['f_name']
                picture_id = emission['id']
                item.art['thumb'] = item.art['landscape'] = SHOW_IMG_URL % picture_id
                item.set_callback(get_video_url, item_id=item_id, fname=fname,
                                  season_f_name="", show_id="show_id", standalone="yes")
                item_post_treatment(item)
                yield item
            else:
                item = Listitem()
                title = emission['title']
                item.label = title
                item.info['plot'] = emission['s_desc']
                fname = emission['f_name']
                picture_id = emission['id']
                item.art['thumb'] = item.art['landscape'] = SHOW_IMG_URL % picture_id
                item.set_callback(list_seasons, item_id=item_id,
                                  fname=fname, pid=picture_id, title=title)
                item_post_treatment(item)
                yield item
        if 'next_page_url' in root:
            offset = str(int(offset) + int(root['limit']))
            yield Listitem.next_page(item_id=item_id, browse_name=browse_name, offset=offset)
    else:
        resp = urlquick.get(FEEDS_API % browse_name,
                            headers=GENERIC_HEADERS, params=feeds_api_params)
        root = json.loads(resp.text)
        item_number = int(root['total_items'])

        if root['filters']['type'] == 'Collection':
            offset = 0
            for i in range(item_number):
                try:
                    item = Listitem()
                    item.label = root['filters']['contents'][i]['title']
                    browse_name = root['filters']['contents'][i]['id']
                    item.set_callback(list_collections, item_id=item_id,
                                      browse_name=browse_name, offset=offset)
                    item_post_treatment(item)
                    yield item
                except (IndexError, ValueError):
                    pass
        elif root['filters']['type'] == 'Show':
            ids = root['filters']['ids']
            w_params = '?limit=%s&offset=0s&platform=my5desktop&friendly=1' % str(item_number)
            for i in range(item_number):
                try:
                    w_params = w_params + '&ids[]=%s' % ids[i]
                except (IndexError, ValueError):
                    pass
            resp = urlquick.get(URL_SHOWS + w_params, headers=GENERIC_HEADERS)
            root = json.loads(resp.text)
            for watchable in root['shows']:
                try:
                    item = Listitem()
                    item.label = watchable['title']
                    item.info['plot'] = watchable['s_desc']
                    item.art['thumb'] = item.art['landscape'] = SHOW_IMG_URL % watchable['id']
                    show_id = watchable['id']
                    fname = watchable['f_name']
                    item.set_callback(get_video_url, item_id=item_id, fname=fname,
                                      season_f_name="season_f_name",
                                      show_id=show_id, standalone="yes")
                    item_post_treatment(item)
                    yield item
                except (IndexError, ValueError):
                    pass
        elif root['filters']['type'] == 'Watchable':
            ids = root['filters']['ids']
            w_params = '?limit=%s&offset=0s&platform=my5desktop&friendly=1' % str(item_number)
            for i in range(item_number):
                try:
                    w_params = w_params + '&ids[]=%s' % ids[i]
                except (IndexError, ValueError):
                    pass
            resp = urlquick.get(URL_WATCHABLE + w_params, headers=GENERIC_HEADERS)
            root = json.loads(resp.text)

            for watchable in root['watchables']:
                try:
                    item = Listitem()
                    item.label = watchable['sh_title']
                    item.info['plot'] = watchable['s_desc']
                    t = int(int(watchable['len']) // 1000)
                    item.info['duration'] = t
                    item.art['thumb'] = item.art['landscape'] = SHOW_IMG_URL % watchable['sh_id']
                    show_id = watchable['id']
                    item.set_callback(get_video_url, item_id=item_id,
                                      fname="fname", season_f_name="season_f_name",
                                      show_id=show_id, standalone="no")
                    item_post_treatment(item)
                    yield item
                except (IndexError, ValueError):
                    pass


@Route.register
def list_collections(plugin, item_id, browse_name, offset, **kwargs):
    resp = urlquick.get(FEEDS_API % browse_name, headers=GENERIC_HEADERS, params=feeds_api_params)
    root = json.loads(resp.text)
    subgenre = root['filters']['vod_subgenres']
    view_all_params = {
        'platform': 'my5desktop',
        'friendly': '1',
        'limit': '25',
        'offset': offset,
        'vod_subgenres[]': subgenre
    }
    resp = urlquick.get(URL_VIEW_ALL, headers=GENERIC_HEADERS, params=view_all_params)
    root = json.loads(resp.text)

    for emission in root['shows']:
        if "standalone" in emission:
            item = Listitem()
            item.label = emission['title']
            item.info['plot'] = emission['s_desc']
            fname = emission['f_name']
            picture_id = emission['id']
            item.art['thumb'] = item.art['landscape'] = SHOW_IMG_URL % picture_id
            item.set_callback(get_video_url, item_id=item_id, fname=fname,
                              season_f_name="", show_id="show_id", standalone="yes")
            item_post_treatment(item)
            yield item
        else:
            item = Listitem()
            title = emission['title']
            item.label = title
            item.info['plot'] = emission['s_desc']
            fname = emission['f_name']
            picture_id = emission['id']
            item.art['thumb'] = item.art['landscape'] = SHOW_IMG_URL % picture_id
            item.set_callback(list_seasons, item_id=item_id,
                              fname=fname, pid=picture_id, title=title)
            item_post_treatment(item)
            yield item
    if 'next_page_url' in root:
        offset = str(int(offset) + int(view_all_params['limit']))
        yield Listitem.next_page(item_id=item_id, browse_name=browse_name, offset=offset)


@Route.register
def list_seasons(plugin, item_id, fname, pid, title, **kwargs):
    resp = urlquick.get(URL_SEASONS % fname, headers=GENERIC_HEADERS, params=view_api_params)
    if resp.ok:
        root = json.loads(resp.text)

        for season in root['seasons']:
            try:
                item = Listitem()
                season_number = season['seasonNumber']
                item.label = title + '\nSeason ' + season_number
                picture_id = pid
                item.art['thumb'] = item.art['landscape'] = SHOW_IMG_URL % picture_id
                item.set_callback(list_episodes, item_id=item_id,
                                  fname=fname, season_number=season_number)
                item_post_treatment(item)
                yield item
            except (IndexError, ValueError):
                pass


@Route.register
def list_episodes(plugin, item_id, fname, season_number, **kwargs):
    resp = urlquick.get(URL_EPISODES % (fname, season_number),
                        headers=GENERIC_HEADERS, params=view_api_params)
    root = json.loads(resp.text)

    for episode in root['episodes']:
        try:
            item = Listitem()
            picture_id = episode['id']
            item.art['thumb'] = item.art['landscape'] = IMG_URL % picture_id
            item.label = episode['title']
            item.info['plot'] = episode['s_desc']
            t = int(int(episode['len']) // 1000)
            item.info['duration'] = t
            season_f_name = episode['sea_f_name']
            fname = episode['f_name']
            show_id = episode['id']
            item.set_callback(get_video_url, item_id=item_id, fname=fname,
                              season_f_name=season_f_name, show_id=show_id, standalone="no")
            item_post_treatment(item)
            yield item
        except (IndexError, ValueError):
            pass


@Resolver.register
def get_video_url(plugin, item_id, fname, season_f_name, show_id, standalone, **kwargs):
    if (standalone == "yes"):
        resp = urlquick.get(ONEOFF % fname, headers=GENERIC_HEADERS, params=view_api_params)
        if resp.ok:
            root = json.loads(resp.text)
        try:
            show_id = root['id']
        except (IndexError, ValueError):
            pass
    LICFULL_URL, aesKey = getdata(show_id, "vod")
    (iv, data) = ivdata(LICFULL_URL)
    (stream, drmurl, suburl) = part2(iv, aesKey, data)
    resp = urlquick.get(CERT_URL)
    content = resp.content
    cert_data = (base64.b64encode(content)).decode('ascii')
    stream_headers = urlencode(lic_headers)
    license_url = '%s|%s|R{SSM}|' % (drmurl, stream_headers)
    item = Listitem()
    item.path = stream
    item.label = get_selected_item_label()
    item.art.update(get_selected_item_art())
    item.info.update(get_selected_item_info())
    item.property[INPUTSTREAM_PROP] = 'inputstream.adaptive'
    item.property['inputstream.adaptive.manifest_type'] = 'mpd'
    item.property['inputstream.adaptive.license_type'] = 'com.widevine.alpha'
    item.property['inputstream.adaptive.server_certificate'] = cert_data
    item.property['inputstream.adaptive.license_key'] = license_url
    return item


@Resolver.register
def get_live_url(plugin, item_id, **kwargs):
    LICFULL_URL, aesKey = getdata(item_id, "live")
    (iv, data) = ivdata(LICFULL_URL)
    (stream, drmurl, suburl) = part2(iv, aesKey, data)
    resp = urlquick.get(CERT_URL)
    content = resp.content
    cert_data = (base64.b64encode(content)).decode('ascii')
    stream_headers = urlencode(lic_headers)
    license_url = '%s|%s|R{SSM}|' % (drmurl, stream_headers)
    item = Listitem()
    item.path = stream
    item.label = get_selected_item_label()
    item.art.update(get_selected_item_art())
    item.info.update(get_selected_item_info())
    item.property[INPUTSTREAM_PROP] = 'inputstream.adaptive'
    item.property['inputstream.adaptive.manifest_type'] = 'mpd'
    item.property['inputstream.adaptive.license_type'] = 'com.widevine.alpha'
    item.property['inputstream.adaptive.server_certificate'] = cert_data
    item.property['inputstream.adaptive.license_key'] = license_url
    return item
