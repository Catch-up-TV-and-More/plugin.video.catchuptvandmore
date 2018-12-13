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
from resources.lib import resolver_proxy
import resources.lib.cq_utils as cqu

import json
import time
import urlquick

try:
    from itertools import zip_longest as zip_longest
except:
    from itertools import izip_longest as zip_longest

'''
Channels:
    * France 2
    * France 3 Nationale
    * France 4
    * France Ô
    * France 5
'''

URL_API = utils.urljoin_partial('http://api-front.yatta.francetv.fr')

URL_LIVE_JSON = URL_API('standard/edito/directs')

HEADERS_YATTA = {
    'X-Algolia-API-Key': '80d9c91958fc448dd20042d399ebdf16',
    'X-Algolia-Application-Id': 'VWDLASHUFE'
}


'''
URL_SEARCH_VIDEOS = 'https://vwdlashufe-dsn.algolia.net/1/indexes/' \
                    'yatta_prod_contents/query'

URL_YATTA_VIDEO = URL_API + '/standard/publish/contents/%s'
# Param : id_yatta

URL_VIDEOS = URL_API + '/standard/publish/taxonomies/%s/contents'
# program
'''


def replay_entry(plugin, item_id):
    """
    First executed function after replay_bridge
    """
    return list_categories(plugin, item_id)


@Route.register
def list_categories(plugin, item_id):
    """
    Build categories listing
    - actualités & société
    - vie quotidienne
    - jeux & divertissement
    - ...
    """
    # URL example: http://api-front.yatta.francetv.fr/standard/publish/channels/france-2/categories/
    # category_part_url example: actualites-et-societe

    url_categories = 'standard/publish/channels/%s/categories/' % item_id
    resp = urlquick.get(URL_API(url_categories))
    json_parser = json.loads(resp.text)

    for category in json_parser["result"]:
        item = Listitem()

        item.label = category["label"]
        category_part_url = category["url"]

        item.set_callback(
            list_programs,
            item_id=item_id,
            category_part_url=category_part_url)
        yield item

    '''
    Seems to be broken in current CodeQuick version
    yield Listitem.recent(
        list_videos_last,
        item_id=item_id)
    '''
    item = Listitem()
    item.label = 'Recent'
    item.set_callback(
        list_videos_last,
        item_id=item_id)
    yield item

    item = Listitem.search(
        list_videos_search,
        item_id=item_id)
    yield item


@Route.register
def list_programs(plugin, item_id, category_part_url, page=0):
    """
    Build programs listing
    - Journal de 20H
    - Cash investigation
    """
    # URL example: http://api-front.yatta.francetv.fr/standard/publish/categories/actualites-et-societe/programs/france-2/?size=20&page=0&filter=with-no-vod,only-visible&sort=begin_date:desc
    # program_part_url example: france-2_cash-investigation
    url_programs = 'standard/publish/categories/%s/programs/%s/' % (
        category_part_url, item_id)
    resp = urlquick.get(
        URL_API(url_programs),
        params={
            'size': 20,
            'page': page,
            'filter': 'with-no-vod,only-visible',
            'sort': 'begin_date:desc'})
    json_parser = json.loads(resp.text)

    for program in json_parser["result"]:
        item = Listitem()
        item.info["mediatype"] = "tvshow"

        item.label = program["label"]
        if 'media_image' in program:
            if program["media_image"] is not None:
                for image_datas in program["media_image"]["patterns"]:
                    if "vignette_16x9" in image_datas["type"]:
                        item.art['thumb'] = URL_API(
                            image_datas["urls"]["w:1024"])

        if 'description' in program:
            item.info['plot'] = program['description']

        program_part_url = program["url_complete"].replace('/', '_')

        item.set_callback(
            list_videos,
            item_id=item_id,
            program_part_url=program_part_url)
        yield item

    # Next page
    if json_parser["cursor"]["next"] is not None:
        yield Listitem.next_page(
            item_id=item_id,
            category_part_url=category_part_url,
            page=json_parser["cursor"]["next"])


@Route.register
def list_videos_last(plugin, item_id, page=1):
    url_last = 'standard/publish/channels/%s/contents/' % item_id
    resp = urlquick.get(
        URL_API(url_last),
        params={
            'size': 20,
            'page': page,
            'filter': 'with-no-vod,only-visible',
            'sort': 'begin_date:desc'})
    json_parser = json.loads(resp.text)

    for video_datas in json_parser["result"]:
        item = Listitem()
        id_diffusion = populate_item(item, video_datas, True)

        item.context.script(
            get_video_url,
            plugin.localize(LABELS['Download']),
            item_id=item_id,
            id_diffusion=id_diffusion,
            video_label=LABELS[item_id] + ' - ' + item.label,
            download_mode=True)

        item.set_callback(
            get_video_url,
            item_id=item_id,
            id_diffusion=id_diffusion,
            item_dict=cqu.item2dict(item))
        yield item

    # More videos...
    if json_parser["cursor"]["next"] is not None:
        yield Listitem.next_page(
            item_id=item_id,
            page=json_parser["cursor"]["next"])


@Route.register
def list_videos(plugin, item_id, program_part_url, page=0):

    # URL example: http://api-front.yatta.francetv.fr/standard/publish/taxonomies/france-2_cash-investigation/contents/?size=20&page=0&sort=begin_date:desc&filter=with-no-vod,only-visible
    url_program = 'standard/publish/taxonomies/%s/contents/' % program_part_url
    resp = urlquick.get(
        URL_API(url_program),
        params={
            'size': 20,
            'page': page,
            'filter': 'with-no-vod,only-visible',
            'sort': 'sort=begin_date:desc'})
    json_parser = json.loads(resp.text)

    for video_datas in json_parser["result"]:
        item = Listitem()
        id_diffusion = populate_item(item, video_datas)

        item.context.script(
            get_video_url,
            plugin.localize(LABELS['Download']),
            item_id=item_id,
            id_diffusion=id_diffusion,
            video_label=LABELS[item_id] + ' - ' + item.label,
            download_mode=True)

        item.set_callback(
            get_video_url,
            item_id=item_id,
            id_diffusion=id_diffusion,
            item_dict=cqu.item2dict(item))
        yield item

    # More videos...
    if json_parser["cursor"]["next"] is not None:
        yield Listitem.next_page(
            item_id=item_id,
            program_part_url=program_part_url,
            page=json_parser["cursor"]["next"])


@Route.register
def list_videos_search(plugin, item_id, search_query, page=0):
    has_item = False

    while not has_item:
        url_search = 'https://vwdlashufe-dsn.algolia.net/1/indexes/yatta_prod_contents/'
        resp = urlquick.get(
            url_search,
            params={
                'page': page,
                'filters': 'class:video',
                'query': search_query},
            headers=HEADERS_YATTA)

        json_parser = json.loads(resp.text)

        nb_pages = json_parser['nbPages']

        for show in json_parser['hits']:
            item_id_found = False
            for channel in show['channels']:
                if channel['url'] == item_id:
                    item_id_found = True
                    break

            if not item_id_found:
                continue

            has_item = True

            title = show['title']
            label = ''
            program_name = None
            if 'program' in show:
                program_name = show['program']['label']
                label += program_name + ' - '
                
                # What about "teaser" and "resume"?
                # E.g. http://api-front.yatta.francetv.fr/standard/publish/taxonomies/france-3_plus-belle-la-vie/contents/?size=20&page=0&sort=begin_date:desc&filter=with-no-vod,only-visible
                if show['type'] == "extrait":
                    label += "[extrait] "
            
            label += title
            
            headline = show['headline_title']
            plot = ''
            if headline:
                plot += headline + '\n'
            
            plot += show['text']
            
            last_publication_date = show['dates']['last_publication_date']
            publication_date = time.strftime(
                '%Y-%m-%d', time.localtime(last_publication_date))

            image_400 = ''
            image_1024 = ''
            if 'image' in show:
                image_400 = show['image']['formats']['vignette_16x9']['urls']['w:400']
                image_1024 = show['image']['formats']['vignette_16x9']['urls']['w:1024']
                
            rating = show["rating_csa_code"]
            # Add a dash before the numbers, instead of e.g. "TP",
            # to simulate the CSA logo instead of having the long description
            if rating.isdigit():
                rating = '-' + rating
            
            item = Listitem()
            item.label = label
            item.info["title"] = label
            item.info["tvshowtitle"] = program_name
            item.art['fanart'] = URL_API(image_1024)
            item.art['thumb'] = URL_API(image_400)
            item.info.date(publication_date, '%Y-%m-%d')
            item.info['plot'] = plot
            item.info['duration'] = show['duration']
            item.info['director'] = show['director']
            item.info['season'] = show['season_number']
            item.info['mpaa'] = rating
            
            if 'episode_number' in show and show['episode_number']:
                item.info["mediatype"] = "episode"
                item.info['episode'] = show['episode_number']

            actors = []
            if 'casting' in show and show["casting"]:
                actors = [actor.strip() for actor in show["casting"].split(',')]
            elif 'presenter' in show and show['presenter']:
                actors.append(show['presenter'])
            
            item.info["cast"] = actors

            if 'characters' in show and show["characters"]:
                characters = [role.strip() for role in show["characters"].split(',')]
                if len(actors) > 0 and len(characters) > 0:
                    item.info["castandrole"] = list(zip_longest(actors, characters))

            item.context.script(
                get_video_url,
                plugin.localize(LABELS['Download']),
                item_id=item_id,
                id_yatta=show['id'],
                video_label=LABELS[item_id] + ' - ' + item.label,
                download_mode=True)

            item.set_callback(
                get_video_url,
                item_id=item_id,
                id_yatta=show['id'],
                item_dict=cqu.item2dict(item))
            yield item
        page = page + 1


    # More videos...
    if page != nb_pages - 1:
        yield Listitem.next_page(
            search_query=search_query,
            item_id=item_id,
            page=page + 1)


@Resolver.register
def get_video_url(
        plugin, item_id, id_diffusion=None,
        id_yatta=None, item_dict=None, download_mode=False, video_label=None):

    if id_yatta is not None:
        url_yatta_video = 'standard/publish/contents/%s' % id_yatta
        resp = urlquick.get(URL_API(url_yatta_video), max_age=-1)
        json_parser = json.loads(resp.text)
        for media in json_parser['content_has_medias']:
            if 'si_id' in media['media']:
                id_diffusion = media['media']['si_id']
                break

    return resolver_proxy.get_francetv_video_stream(
        plugin, id_diffusion, item_dict, download_mode, video_label)


def live_entry(plugin, item_id, item_dict):
    return get_live_url(plugin, item_id, item_id.upper(), item_dict)


@Resolver.register
def get_live_url(plugin, item_id, video_id, item_dict):

    resp = urlquick.get(
        URL_LIVE_JSON,
        headers={'User-Agent': web_utils.get_random_ua},
        max_age=-1)
    json_parser = json.loads(resp.text)

    for live in json_parser["result"]:
        if live["channel"] == item_id:
            live_datas = live["collection"][0]["content_has_medias"]
            liveId = ''
            for live_data in live_datas:
                if "si_direct_id" in live_data["media"]:
                    liveId = live_data["media"]["si_direct_id"]
            return resolver_proxy.get_francetv_live_stream(plugin, liveId)


def populate_item(item, video_data, include_program_name = False): 
    program_name = ''
    for program_data in video_data["content_has_taxonomys"]:
        if program_data["type"] == 'program':
            program_name = program_data['taxonomy']['label']
    
    item.label = ''
    if program_name:
        item.info["tvshowtitle"] = program_name
        
        if include_program_name:
            item.label += program_name + ' - '
    
    # What about "teaser" and "resume"?
    # E.g. http://api-front.yatta.francetv.fr/standard/publish/taxonomies/france-3_plus-belle-la-vie/contents/?size=20&page=0&sort=begin_date:desc&filter=with-no-vod,only-visible
    if video_data["type"] == 'extrait':
        item.label += '[extrait] '

    item.label += video_data["title"]
    
    # It's too bad item.info["title"] overrules item.label everywhere
    # so there's no difference between what is shown in the video list 
    # and what is shown in the video details
    #item.info["title"] = video_data["title"]
    item.info["title"] = item.label
    
    image = ''
    for video_media in video_data["content_has_medias"]:
        if video_media["type"] == "main":
            id_diffusion = video_media["media"]["si_id"]
            if video_data["type"] != 'extrait':
                item.info['duration'] = int(video_media["media"]["duration"])
            
            rating = video_media["media"]["rating_csa_code"]
            # Add a dash before the numbers, instead of e.g. "TP",
            # to simulate the CSA logo instead of having the long description
            if rating.isdigit():
                item.info['mpaa'] = '-' + rating
            else:
                # Not using video_media["media"]["rating_csa"] here, 
                # to be consistent with the search results that only include a code
                item.info['mpaa'] = rating
        elif video_media["type"] == "image":
            for image_datas in video_media["media"]["patterns"]:
                if image_datas["type"] == "vignette_16x9":
                    image = URL_API(image_datas["urls"]["w:1024"])
    
    # 2018-09-20T05:03:01+02:00
    publication_date = video_data['first_publication_date'].split('T')[0]
    item.info.date(publication_date, '%Y-%m-%d')

    if "text" in video_data and video_data["text"]:
        item.info['plot'] = video_data["text"]
        
    if "director" in video_data and video_data["director"]:
        item.info['director'] = video_data["director"]
    
    if "saison" in video_data and video_data["saison"]:
        item.info['season'] = video_data["saison"]
        
    if "episode" in video_data and video_data["episode"]:
        # Now we know for sure we are dealing with an episode
        item.info["mediatype"] = "episode"
        item.info['episode'] = video_data["episode"]
    
    actors = []
    if "casting" in video_data and video_data["casting"]:
        actors = [actor.strip() for actor in video_data["casting"].split(',')]
    elif "presenter" in video_data and video_data["presenter"]:
        actors.append(video_data['presenter'])
    
    item.info["cast"] = actors
    
    if "characters" in video_data and video_data["characters"]:
        characters = [role.strip() for role in video_data["characters"].split(',')]
        if len(actors) > 0 and len(characters) > 0:
            item.info["castandrole"] = list(zip_longest(actors, characters))

    item.art['fanart'] = image
    item.art['thumb'] = image

    return id_diffusion

