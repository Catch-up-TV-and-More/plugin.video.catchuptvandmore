# -*- coding: utf-8 -*-
# Copyright: (c) 2022, darodi
# GNU General Public License v2.0+ (see LICENSE.txt or https://www.gnu.org/licenses/gpl-2.0.txt)

# This file is part of Catch-up TV & More

from __future__ import unicode_literals

import re

import urlquick
# noinspection PyUnresolvedReferences
from codequick import Listitem, Resolver, Route, Script
# noinspection PyUnresolvedReferences
from codequick.utils import urljoin_partial

from resources.lib import resolver_proxy
from resources.lib.web_utils import get_random_ua

DATA_PLAYER_PREFIX = "data-player-"
DATA_PREFIX = "data-"

URL_ROOT = 'https://veely.tv/'
url_constructor = urljoin_partial(URL_ROOT)

URL_LIVE = url_constructor('live')
URL_ON_DEMAND = url_constructor('explore/6165')

SSMP_API = "https://mm-v2.simplestream.com/ssmp/api.php?id=%s&env=%s"
STREAM_API = "https://v2-streams-elb.simplestreamcdn.com/api/%s/stream/%s?key=%s&platform=firefox"


@Route.register
def website_root(plugin, item_id, **kwargs):
    resp = urlquick.get(URL_ROOT, max_age=-1)

    # Home page carousels
    yield from yield_carousels(URL_ROOT)

    # Navbar
    root_nav = resp.parse("ul", attrs={"class": "nav navbar-nav"})
    for url_tag in root_nav.iterfind("li/a"):
        item = Listitem()
        item.label = url_tag.get("aria-label")
        url = url_tag.get("href")
        if url == '/' or url == '/apps' or url == '/tvguide' or url == '/live/':
            continue

        # item.art["thumb"] = get_item_media_path('channels/websites/veely.png')
        item.set_callback(list_programs, url=url)
        yield item


def yield_carousels(url):
    main = urlquick.get(url, max_age=-1).parse("main")
    for div in main.findall(".//div"):

        if div.get("class") is None \
                or ("carousel" not in div.get("class").split(' ')
                    and "series-carousels" not in div.get("class").split(' ')):
            continue

        elif "series-carousels" in div.get("class").split(' '):
            series = div.findall("./h2")
            inner_divs = div.findall("./div")
            i = 0
            for serie in series:
                episodes_div = inner_divs[i].find("./div")
                item = Listitem()
                i += 1
                item.label = serie.text
                items = list_carousel_items(episodes_div)
                if len(items) == 0:
                    continue
                item.set_callback(list_items, items=items)
                yield item
        else:
            item = Listitem()
            title = div.get("data-carousel-title")
            if title is None:
                continue
            item.label = title
            items = list_carousel_items(div)
            if len(items) == 0:
                continue
            item.set_callback(list_items, items=items)
            yield item


def list_carousel_items(div):
    items = []
    for anchor_tag in div.iterfind("a"):
        if anchor_tag.get("class") is None or "thumbnail" not in anchor_tag.get("class").split(' '):
            continue

        item = Listitem()
        item.label = anchor_tag.find(".//div[@class='title-info']//h3").text
        url = "%s" % anchor_tag.get("href")
        item.art["thumb"] = anchor_tag.find(".//img").get("src")
        if "/watch/" in url or "/live/" in url:
            item.set_callback(play_video, url=url)
        else:
            item.set_callback(list_programs, url=url)
        items.append(item)
    return items


@Route.register
def list_items(plugin, items, **kwargs):
    for item in items:
        yield item


@Route.register
def list_programs(plugin, url, **kwargs):
    program = url_constructor(url)

    if (URL_LIVE == program) or (URL_LIVE + '/' == program):
        return False

    elif (URL_ON_DEMAND == program) or (URL_ON_DEMAND + '/' == program):
        resp = urlquick.get(program, max_age=-1)
        root_elem = resp.parse("main").find(".//div[@class='container-fluid']")
        for url_tag in root_elem.iterfind(".//a"):
            if url_tag.get("class") is None or "thumbnail" not in url_tag.get("class"):
                continue
            item = Listitem()
            item.label = url_tag.find(".//img").get("alt")
            tag_url = url_tag.get("href")
            item.art["thumb"] = url_tag.find(".//img").get("src")
            item.set_callback(list_programs, url=tag_url)
            yield item
    else:
        yield from yield_carousels(program)


@Resolver.register
def play_video(plugin, url, **kwargs):
    full_url = url_constructor(url)

    player_path = ".//div[@id='vod-player']"
    prefix = DATA_PREFIX
    resource = "show"

    if "/live/" in url:
        player_path = ".//div[@id='live-player-root']"
        prefix = DATA_PLAYER_PREFIX
        resource = "live"

    headers1 = {
        "User-Agent": get_random_ua(),
        "Accept": "*/*",
        "Accept-Language": "fr,fr-FR;q=0.8,en-US;q=0.5,en;q=0.3",
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "cross-site",
        "Pragma": "no-cache",
        "Cache-Control": "no-cache",
        "referrer": URL_ROOT
    }

    main = urlquick.get(full_url, headers=headers1, max_age=-1).parse("main")
    player = main.find(player_path)
    headers2 = {
        "User-Agent": get_random_ua(),
        "Accept": "*/*",
        "Accept-Language": "fr,fr-FR;q=0.8,en-US;q=0.5,en;q=0.3",
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "cross-site",
        "Pragma": "no-cache",
        "Cache-Control": "no-cache",
        "referrer": URL_ROOT
    }

    data_id = player.get("%sid" % prefix)
    data_env = player.get("%senv" % prefix)
    data_uvid = player.get("%suvid" % prefix)
    data_key = player.get("%skey" % prefix)
    data_token = player.get("%stoken" % prefix)
    data_expiry = player.get("%sexpiry" % prefix)
    urlquick.get(SSMP_API % (data_id, data_env),
                 headers=headers2,
                 max_age=-1).json()

    headers3 = {
        "User-Agent": get_random_ua(),
        "Accept": "*/*",
        "Accept-Language": "fr,fr-FR;q=0.8,en-US;q=0.5,en;q=0.3",
        "Uvid": data_uvid,
        "Token": data_token,
        "Token-Expiry": data_expiry,
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "cross-site",
        "Pragma": "no-cache",
        "Cache-Control": "no-cache",
        "referrer": URL_ROOT,
    }

    json_api3 = urlquick.get(STREAM_API % (resource, data_uvid, data_key),
                             headers=headers3,
                             max_age=-1).json()

    Script.log("json_api3 = %s" % json_api3, args=None, lvl=Script.ERROR)

    stream_url = json_api3["response"]["stream"]
    stream_url = re.sub(r'\.m3u8.*', '.m3u8', stream_url)

    return resolver_proxy.get_stream_with_quality(plugin, video_url=stream_url, manifest_type="hls")
