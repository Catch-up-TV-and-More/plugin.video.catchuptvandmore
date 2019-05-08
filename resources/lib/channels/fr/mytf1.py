# -*- coding: utf-8 -*-
"""
    Catch-up TV & More
    Original work (C) JUL1EN094, SPM, SylvainCecchetto
    Copyright (C) 2016  SylvainCecchetto

    This file is part of Catch-up TV & More.

    Catch-up TV & More is free software; you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation; either version 2 of the License, or
    (at your option) any later version.

    Catch-up TV & More is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License along
    with Catch-up TV & More; if not, write to the Free Software Foundation,
    Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
"""

# The unicode_literals import only has
# an effect on Python 2.
# It makes string literals as unicode like in Python 3
from __future__ import unicode_literals

from codequick import Route, Resolver, Listitem, utils, Script

from resources.lib.labels import LABELS
from resources.lib import web_utils
from resources.lib import download
import resources.lib.cq_utils as cqu
from resources.lib.listitem_utils import item_post_treatment, item2dict

# Verify md5 still present in hashlib python 3 (need to find another way if it is not the case)
# https://docs.python.org/3/library/hashlib.html
from hashlib import md5

import inputstreamhelper
import json
import os
import re
import urlquick
import xbmc
import xbmcgui

# TO DO

URL_ROOT = utils.urljoin_partial("http://www.tf1.fr")

URL_VIDEO_STREAM = 'https://delivery.tf1.fr/mytf1-wrd/%s?format=%s'
# videoId, format['hls', 'dash']

URL_LICENCE_KEY = 'https://drm-wide.tf1.fr/proxy?id=%s|Content-Type=&User-Agent=Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3041.0 Safari/537.36&Host=drm-wide.tf1.fr|R{SSM}|'
# videoId

DESIRED_QUALITY = Script.setting['quality']


def replay_entry(plugin, item_id, **kwargs):
    """
    First executed function after replay_bridge
    """
    return list_categories(plugin, item_id)


@Route.register
def list_categories(plugin, item_id, **kwargs):
    """
    Build categories listing
    - Tous les programmes
    - Séries
    - Informations
    - ...
    """
    resp = urlquick.get(URL_ROOT(item_id + '/programmes-tv'))
    root = resp.parse("ul", attrs={"class": "filters_2 contentopen"})

    for category in root.iterfind(".//a"):
        category_name = category.text
        category_url = category.get('data-target')

        item = Listitem()
        item.label = category_name
        item.params['item_id'] = item_id
        item.params['category'] = category_url
        item.set_callback(list_programs)
        item_post_treatment(item)

        yield item


@Route.register
def list_programs(plugin, item_id, category, **kwargs):
    """
    Build programs listing
    - Les feux de l'amour
    - ...
    """

    if category == 'all':
        resp = urlquick.get(URL_ROOT('/programmes-tv/abecedaire/#'))
        root = resp.parse()

        for program in root.iterfind(
                ".//div[@class='program key-list-programs']"):
            is_channel_program = False
            list_channels = program.findall(".//div")
            for channel in list_channels:
                if channel.get('class') == 'channel %s' % item_id:
                    is_channel_program = True
            if is_channel_program:
                item = Listitem()
                program_url = program.find(".//div[@class='description']")
                program_url = program_url.find('.//a').get('href')
                program_name = program.find(".//p[@class='program']").text
                img = program.find('.//img')
                try:
                    img = img.get('data-srcset')
                except Exception:
                    img = img.get('srcset')

                img = 'http:' + img.split(',')[-1].split(' ')[0]

                if 'meteo.tf1.fr/meteo-france' in program_url:
                    item.label = program_name
                    item.art["thumb"] = img
                    item.set_callback(list_videos,
                                      item_id=item_id,
                                      program_category_url=program_url)
                    item_post_treatment(item)
                    yield item

                else:
                    item.label = program_name
                    item.art["thumb"] = img
                    item.set_callback(list_program_categories,
                                      item_id=item_id,
                                      program_url=program_url)
                    item_post_treatment(item)
                    yield item
    else:
        resp = urlquick.get(URL_ROOT(item_id + '/programmes-tv'))
        root = resp.parse("ul", attrs={"id": "js_filter_el_container"})

        for program in root.iterfind('.//li'):
            current_category = program.get('data-type')
            if category == current_category or category == 'all':
                item = Listitem()
                program_url = program.find(".//div[@class='description']")
                program_url = program_url.find('.//a').get('href')
                program_name = program.find(".//p[@class='program']").text
                img = program.find('.//img')
                try:
                    img = img.get('srcset')
                except Exception:
                    img = img.get('src')

                if img is not None:
                    img = 'http:' + img.split(',')[-1].split(' ')[0]

                if 'meteo.tf1.fr/meteo-france' in program_url:
                    item.label = program_name
                    item.art["thumb"] = img
                    item.set_callback(list_videos,
                                      item_id=item_id,
                                      program_category_url=program_url)
                    item_post_treatment(item)
                    yield item

                else:
                    item.label = program_name
                    item.art["thumb"] = img
                    item.set_callback(list_program_categories,
                                      item_id=item_id,
                                      program_url=program_url)
                    item_post_treatment(item)
                    yield item


@Route.register
def list_program_categories(plugin, item_id, program_url, **kwargs):
    """
    Build program categories
    - Toutes les vidéos
    - Tous les replay
    - Saison 1
    - ...
    """
    resp = urlquick.get(program_url + '/videos')
    try:
        program_categories = resp.parse(
            u"ul", attrs={'class': 'filters_1 contentopen'})

        for li in program_categories.iterfind('.//li'):
            item = Listitem()
            item.label = "".join(li.itertext())
            category_id = li.find('a').get('data-filter')
            item.set_callback(list_videos,
                              item_id=item_id,
                              program_category_url=program_url + '/videos?filter=' + category_id)
            item_post_treatment(item)
            yield item
    except Exception:
        plugin.notify(plugin.localize(LABELS['No videos found']), '')
        yield False


@Route.register
def list_videos(plugin, item_id, program_category_url, **kwargs):

    if 'meteo.tf1.fr/meteo-france' in program_category_url:
        resp = urlquick.get(program_category_url)
        root = resp.parse("td", attrs={"class": "textbase"})

        title = root.find('.//h3').text

        program_id = re.compile(r'\; src \= \'(.*?)\'').findall(resp.text)[0]

        item = Listitem()
        item.label = title
        item.params['video_label'] = LABELS[item_id] + ' - ' + item.label

        item.set_callback(get_video_url,
                          item_id=item_id,
                          program_id=program_id,
                          item_dict=item2dict(item))
        item_post_treatment(item, is_playable=True, is_downloadable=True)
        yield item

    else:

        resp = urlquick.get(program_category_url)
        root = resp.parse()
        if root.find(".//div[@class='content']") is not None:
            grid = resp.parse("div", attrs={"class": "content"})
        else:
            grid = resp.parse("div", attrs={"class": "content withPub"})

        if grid is not None:
            for li in grid.findall('.//li'):
                video_type_string = li.find(
                    ".//div[@class='description']").find('.//a').get(
                        'data-xiti-libelle')
                video_type_string = video_type_string.split('-')[0]

                item = Listitem()

                item.label = li.find(".//p[@class='title']").text

                try:
                    stitle = li.find(".//p[@class='stitle']").text
                    item.info['plot'] = stitle
                except Exception:
                    pass

                try:
                    duration_soup = li.find(".//p[@class='uptitle']").find(
                        ".//span[@class='momentDate']")
                    duration = int(duration_soup.text)
                    item.info['duration'] = duration
                except Exception:
                    pass

                img = li.find('.//img')
                try:
                    img = img.get('data-srcset')
                except Exception:
                    img = img.get('srcset')

                item.art["thumb"] = 'http:' + \
                    img.split(',')[-1].split(' ')[0]

                try:
                    date_value = li.find(".//div[@class='text']").find(
                        ".//p[@class='uptitle']").find('.//span')

                    aired = date_value.get('data-date').split('T')[0]
                    item.info.date(aired, '%Y-%m-%d')
                except Exception:
                    pass

                program_id = li.find('.//a').get('href')
                item.params[
                    'video_label'] = LABELS[item_id] + ' - ' + item.label

                callback = get_video_url
                if 'Playlist' in video_type_string:
                    callback = build_playlist

                item.set_callback(callback,
                                  item_id=item_id,
                                  program_id=program_id,
                                  item_dict=item2dict(item))
                item_post_treatment(item,
                                    is_playable=True,
                                    is_downloadable=True)
                yield item

            # Check for any next page
            pagination = resp.parse(
                u"div", attrs={'class': 'clearfix list_pagination'})

            ol = pagination.find('.//ol')
            if ol is not None:
                li_list = ol.findall('.//li')

                for i in range(len(li_list) - 1):
                    li = li_list[i]
                    if 'selected' in li.find('.//a').get('class') and \
                            i < len(li_list):
                        next_li = li_list[i + 1]
                        yield Listitem.next_page(
                            item_id=item_id,
                            program_category_url=next_li.find('.//a').get(
                                'href'))


@Resolver.register
def build_playlist(plugin,
                   item_id,
                   program_id,
                   item_dict=None,
                   video_label=None,
                   **kwargs):
    playlist_html = urlquick.get(program_id)
    playlist = playlist_html.parse()
    reco_videos = playlist.find(".//div[@id='reco-video-content']")
    data_more = ''

    playlist_items = []

    for reco_video in reco_videos:
        if data_more == '':
            data_more = reco_video.get('data-more')
        if reco_video.get('data-more') == data_more:
            video_page_url = reco_video.get('href')

            # Grab the video URL
            video_url = get_video_url(
                plugin=plugin,
                item_id=item_id,
                program_id=video_page_url)
            if video_url is not False:
                item = Listitem()
                if isinstance(video_url, Listitem):
                    item = video_url
                else:
                    item.path = video_url

                # Grab additionnal infos (title, image)
                item.label = reco_video.find(".//div[@class='reco_video_content']").find(".//p[@class='reco_video_title']").text
                img = reco_video.find(".//div[@class='reco_video_image']").find(".//img")
                try:
                    img = img.get('data-srcset')
                except Exception:
                    img = img.get('srcset')

                item.art["thumb"] = 'http:' + \
                    img.split(',')[-1].split(' ')[0]

                print('LABEL: ' + repr(item.label))
                playlist_items.append(item)

    return playlist_items


@Resolver.register
def get_video_url(plugin,
                  item_id,
                  program_id,
                  item_dict=None,
                  download_mode=False,
                  video_label=None,
                  **kwargs):

    if 'www.wat.tv/embedframe' in program_id:
        url = 'http:' + program_id
    elif "http" not in program_id:
        if program_id[0] == '/':
            program_id = program_id[1:]
        url = URL_ROOT(program_id)
    else:
        url = program_id

    video_html = urlquick.get(url)
    root = video_html.parse()

    if 'www.wat.tv/embedframe' in program_id:
        video_id = re.compile('UVID=(.*?)&').findall(video_html.text)[0]
    else:
        iframe_player = root.find(".//div[@class='iframe_player']")
        if iframe_player is not None:
            video_id = iframe_player.get('data-watid')
        else:
            video_id = re.compile(r'\"data\"\:\{\"id\"\:\"(.*?)\"').findall(
                video_html.text)[0]

    video_format = 'hls'
    url_json = URL_VIDEO_STREAM % (video_id, video_format)
    htlm_json = urlquick.get(url_json,
                             headers={'User-Agent': web_utils.get_random_ua},
                             max_age=-1)
    json_parser = json.loads(htlm_json.text)

    if json_parser['code'] >= 400:
        plugin.notify('ERROR', plugin.localize(30716))
        return False

    # Check DRM in the m3u8 file
    manifest = urlquick.get(json_parser["url"],
                            headers={
                                'User-Agent': web_utils.get_random_ua},
                            max_age=-1).text
    if 'drm' in manifest:

        if cqu.get_kodi_version() < 18:
            xbmcgui.Dialog().ok('Info', plugin.localize(30602))
            return False
        else:
            video_format = 'dash'

    if video_format == 'hls':

        root = os.path.dirname(json_parser["url"])

        url_without_max_bitrate_list = json_parser["url"].split(
            '&max_bitrate=')
        if '&' in url_without_max_bitrate_list[1]:
            url_without_max_bitrate = url_without_max_bitrate_list[
                0] + '&' + url_without_max_bitrate_list[1].split('&')[1]
        else:
            url_without_max_bitrate = url_without_max_bitrate_list[0]
        manifest = urlquick.get(
            url_without_max_bitrate,
            headers={'User-Agent': web_utils.get_random_ua},
            max_age=-1)

        lines = manifest.text.splitlines()
        final_video_url = ''
        all_datas_videos_quality = []
        all_datas_videos_path = []
        for k in range(0, len(lines) - 1):
            if 'RESOLUTION=' in lines[k]:
                all_datas_videos_quality.append(
                    re.compile(r'RESOLUTION=(.*?),').findall(lines[k])[0])
                all_datas_videos_path.append(root + '/' + lines[k + 1])
        if DESIRED_QUALITY == "DIALOG":
            seleted_item = xbmcgui.Dialog().select(
                plugin.localize(LABELS['choose_video_quality']),
                all_datas_videos_quality)

            if seleted_item == -1:
                return False

            final_video_url = all_datas_videos_path[seleted_item]
        elif DESIRED_QUALITY == 'BEST':
            # Last video in the Best
            for k in all_datas_videos_path:
                url = k
            final_video_url = url
        else:
            final_video_url = all_datas_videos_path[0]

        if download_mode:
            return download.download_video(final_video_url, video_label)
        return final_video_url

    else:
        if download_mode:
            xbmcgui.Dialog().ok('Info', plugin.localize(30603))
            return False

        url_json = URL_VIDEO_STREAM % (video_id, video_format)
        htlm_json = urlquick.get(
            url_json,
            headers={'User-Agent': web_utils.get_random_ua},
            max_age=-1)
        json_parser = json.loads(htlm_json.text)

        is_helper = inputstreamhelper.Helper('mpd', drm='widevine')
        if not is_helper.check_inputstream():
            return False

        item = Listitem()
        item.path = json_parser["url"]
        item.label = item_dict['label']
        item.info.update(item_dict['info'])
        item.art.update(item_dict['art'])
        item.property['inputstreamaddon'] = 'inputstream.adaptive'
        item.property['inputstream.adaptive.manifest_type'] = 'mpd'
        item.property[
            'inputstream.adaptive.license_type'] = 'com.widevine.alpha'
        item.property[
            'inputstream.adaptive.license_key'] = URL_LICENCE_KEY % video_id

        return item


def live_entry(plugin, item_id, item_dict, **kwargs):
    return get_live_url(plugin, item_id, item_id.upper(), item_dict)


@Resolver.register
def get_live_url(plugin, item_id, video_id, item_dict, **kwargs):
    video_id = 'L_%s' % item_id.upper()

    video_format = 'hls'
    url_json = URL_VIDEO_STREAM % (video_id, video_format)
    htlm_json = urlquick.get(url_json,
                             headers={'User-Agent': web_utils.get_random_ua},
                             max_age=-1)
    json_parser = json.loads(htlm_json.text)

    return json_parser['url'].replace('master_2000000.m3u8',
                                      'master_4000000.m3u8')
