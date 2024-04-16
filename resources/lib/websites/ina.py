# -*- coding: utf-8 -*-
# Copyright: (c) 2024, darodi
# GNU General Public License v2.0+ (see LICENSE.txt or https://www.gnu.org/licenses/gpl-2.0.txt)

# This file is part of Catch-up TV & More

from __future__ import unicode_literals

import re

import urlquick
# noinspection PyUnresolvedReferences
from codequick import Listitem, Resolver, Route, utils
# noinspection PyUnresolvedReferences
from codequick.utils import urljoin_partial

from resources.lib.web_utils import html_parser

# TO DO
# Add Premium Account (purchase an account to test)
# Add last videos
# Fix Info add Premium Content

URL_ROOT = 'http://www.ina.fr'
url_constructor = urljoin_partial(URL_ROOT)

# asset-details-url="https://apipartner.ina.fr/assets/I24052651?sign=e7601642c3655c5e96cb1163bc47864f9f3bf313&amp;partnerId=2"
ASSET_URL_PATTERN = re.compile(r'asset-details-url=\"(.*?)\"')


@Route.register
def website_root(plugin, **kwargs):
    # TODO Search videos
    # yield Listitem.search(search, URL_ROOT)

    resp = urlquick.get(url_constructor("/ina-eclaire-actu"))
    root_elem = resp.parse("div", attrs={"id": "block-hub-content"})
    for url_tag in root_elem.iterfind(".//div[@class='gtm-print-list']"):
        item = Listitem()
        item.label = url_tag.findtext(".//h2[@class='title-bloc']")
        carrousel = url_tag.find(".//div[@d-role='carrousel']")
        item.set_callback(list_carousel, carrousel=carrousel)
        yield item


@Route.register
def list_carousel(plugin, carrousel, **kwargs):
    for link in carrousel.iterfind('.//a'):
        item = Listitem()
        video_url = url_constructor(link.get('href'))
        item.label = link.findtext(".//div[@class='title-bloc-small']")
        image = link.find(".//img")
        item.art["thumb"] = image.get("data-src")
        item.set_callback(play_video, url=video_url)
        yield item


@Resolver.register
def play_video(plugin, url):
    resp = urlquick.get(url, max_age=-1)
    asset_url_array = ASSET_URL_PATTERN.findall(resp.text)
    if len(asset_url_array) == 0:
        return False
    asset_url = asset_url_array[0]
    asset_url_escaped = html_parser.unescape(asset_url)
    json_resp_api = urlquick.get(asset_url_escaped, max_age=-1).json()
    if "resourceUrl" in json_resp_api:
        resource_url = json_resp_api["resourceUrl"]
        # TODO check why it doesn't work
        # return resolver_proxy.get_stream_with_quality(plugin,
        #                                               video_url=resource_url,
        #                                               headers={"User-Agent": web_utils.get_random_ua()})
        return resource_url
    return False
