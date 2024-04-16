# -*- coding: utf-8 -*-
# Copyright: (c) 2017, SylvainCecchetto; 2024, darodi
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

ASSET_URL_PATTERN = re.compile(r'asset-details-url=\"(.*?)\"')


@Route.register
def website_root(plugin, **kwargs):
    # TODO Search videos

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
        # TODO use resolver_proxy.get_stream_with_quality

        return resource_url
    return False
