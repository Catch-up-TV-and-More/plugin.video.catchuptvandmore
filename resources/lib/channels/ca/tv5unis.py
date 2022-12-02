# -*- coding: utf-8 -*-
# Copyright: (c) 2017, SylvainCecchetto
# GNU General Public License v2.0+ (see LICENSE.txt or https://www.gnu.org/licenses/gpl-2.0.txt)

# This file is part of Catch-up TV & More

from __future__ import unicode_literals
from builtins import str
import json
import re

from codequick import Listitem, Resolver, Route
import urlquick

from resources.lib import resolver_proxy, web_utils
from resources.lib.menu_utils import item_post_treatment


# TO DO
# Info Videos (date, plot, etc ...)

URL_ROOT = 'https://www.tv5unis.ca'
# Channel Name

URL_VIDEOS_SEASON = URL_ROOT + '/%s/saisons/%s'
# slug_program, number_season
URL_VIDEOS = URL_ROOT + '/%s'
# slug_program

# https://www.tv5unis.ca/videos/canot-cocasse/saisons/4/episodes/8
URL_STREAM_SEASON_EPISODE = URL_ROOT + '/videos/%s/saisons/%s/episodes/%s'
# slug_video, number_season, episode_number
URL_STREAM = URL_ROOT + '/videos/%s'
# slug_video

URL_API = 'https://api.tv5unis.ca/graphql'
GENERIC_HEADERS = {"User-Agent": web_utils.get_random_ua()}

@Route.register
def list_categories(plugin, item_id, **kwargs):
    """
    Build categories listing
    - Tous les programmes
    - Séries
    - Informations
    - ...
    """
    resp = urlquick.get(URL_ROOT, headers=GENERIC_HEADERS)
    json_datas = re.compile(
        r'\/json\"\>\{(.*?)\}\<\/script\>').findall(resp.text)[0]
    json_parser = json.loads('{' + json_datas + '}')

    json_entry = json_parser["props"]["apolloState"]
    for json_key in list(json_entry.keys()):
        if "__typename" in json_entry[json_key]:
            if "ProductSet" in json_entry[json_key]["__typename"]:
                if "slug" in json_entry[json_key]:
                    category_title = json_entry[json_key]["title"]
                    category_slug = json_entry[json_key]["slug"]

                    item = Listitem()
                    item.label = category_title
                    item.set_callback(list_programs, item_id=item_id, category_slug=category_slug)
                    item_post_treatment(item)
                    yield item


@Route.register
def list_programs(plugin, item_id, category_slug, **kwargs):

    resp = urlquick.get(URL_ROOT, headers=GENERIC_HEADERS)
    json_datas = re.compile(
        r'\/json\"\>\{(.*?)\}\<\/script\>').findall(resp.text)[0]
    json_parser = json.loads('{' + json_datas + '}')

    json_entry = json_parser["props"]["apolloState"]
    for json_key in list(json_entry.keys()):
        if "__typename" not in json_entry[json_key]:
            continue

        if "ProductSet" not in json_entry[json_key]["__typename"]:
            continue

        if "slug" not in json_entry[json_key]:
            continue

        if category_slug not in json_entry[json_key]["slug"]:
            continue

        for item_data in json_entry[json_key]["items"]:
            product_ref = item_data["product"]["__ref"]

            product_slug_ref = ''
            if json_entry[product_ref]['collection'] is not None:
                product_slug_ref = json_entry[product_ref]['collection']['__ref']
                program_title = json_entry[product_slug_ref]['title'] + ' - ' + json_entry[product_ref]["title"]
            else:
                program_title = json_entry[product_ref]["title"]

            program_image = json.loads(re.compile(r'Image\:(.*?)$').findall(json_entry[product_ref]["mainLandscapeImage"]['__ref'])[0])['url']
            program_plot = json_entry[product_ref]["shortSummary"]
            program_type = json_entry[product_ref]["productType"]

            item = Listitem()
            item.label = program_title
            item.art['thumb'] = item.art['landscape'] = program_image
            item.info['plot'] = program_plot
            if 'EPISODE' not in program_type and 'MOVIE' not in program_type and 'TRAILER' not in program_type:
                continue

            isVideo = False
            if json_entry[product_ref]['slug'] is not None:
                video_slug = json_entry[product_ref]['slug']
                isVideo = True
            elif json_entry[product_ref]['collection'] is not None:
                video_slug = json_entry[product_slug_ref]['slug']
                isVideo = True
            if isVideo:
                video_duration = ''
                if 'duration' in json_entry[product_ref]:
                    video_duration = json_entry[product_ref]['duration']
                item.info['duration'] = video_duration
                video_season_number = ''
                if json_entry[product_ref]["seasonNumber"] is not None:
                    video_season_number = str(json_entry[product_ref]["seasonNumber"])
                video_episode_number = ''
                if json_entry[product_ref]["episodeNumber"] is not None:
                    video_episode_number = str(json_entry[product_ref]["episodeNumber"])
                item.set_callback(
                    get_video_url,
                    item_id=item_id,
                    video_slug=video_slug,
                    video_season_number=video_season_number,
                    video_episode_number=video_episode_number)
                item_post_treatment(item, is_playable=True, is_downloadable=True)
                yield item
            else:
                if json_entry[product_ref]['slug'] is not None:
                    program_slug = json_entry[product_ref]['slug']
                elif json_entry[product_ref]['collection'] is not None:
                    program_slug = json_entry[product_slug_ref]['slug']
                program_season_number = ''
                if json_entry[product_ref]["seasonNumber"] is not None:
                    program_season_number = str(json_entry[product_ref]["seasonNumber"])
                item.set_callback(
                    list_videos,
                    item_id=item_id,
                    program_slug=program_slug,
                    program_season_number=program_season_number)
                item_post_treatment(item)
                yield item


@Route.register
def list_videos(plugin, item_id, program_slug, program_season_number, **kwargs):

    if program_season_number == '':
        resp = urlquick.get(URL_VIDEOS % program_slug, headers=GENERIC_HEADERS)
    else:
        resp = urlquick.get(URL_VIDEOS_SEASON % (program_slug, program_season_number), headers=GENERIC_HEADERS)

    json_datas = re.compile(
        r'\/json\"\>\{(.*?)\}\<\/script\>').findall(resp.text)[0]
    json_parser = json.loads('{' + json_datas + '}')

    json_entry = json_parser["props"]["apolloState"]
    for json_key in list(json_entry.keys()):
        if "productType" not in json_entry[json_key]:
            continue

        if "EPISODE" not in json_entry[json_key]["productType"] and "TRAILER" not in json_entry[json_key]["productType"]:
            continue

        video_episode_number = ''
        if json_entry[json_key]["episodeNumber"] is not None:
            video_episode_number = str(json_entry[json_key]["episodeNumber"])
        product_slug_ref = ''
        if json_entry[json_key]['collection'] is not None:
            product_slug_ref = json_entry[json_key]['collection']['__ref']
            video_title = json_entry[product_slug_ref]['title']
            if program_season_number != '':
                video_title = video_title + ' - S%sE%s' % (program_season_number, video_episode_number)
            if json_entry[json_key]["title"] is not None:
                video_title = video_title + ' - ' + json_entry[json_key]['title']
        else:
            video_title = json_entry[json_key]["title"]
        video_image = program_image = json.loads(re.compile(r'Image\:(.*?)$').findall(json_entry[product_ref]["mainLandscapeImage"]['__ref'])[0])['url']
        video_plot = ''
        if 'shortSummary' in json_entry[json_key]:
            video_plot = json_entry[json_key]["shortSummary"]
        video_duration = ''
        if 'duration' in json_entry[json_key]:
            video_duration = json_entry[json_key]['duration']

        item = Listitem()
        item.label = video_title
        item.art['thumb'] = item.art['landscape'] = video_image
        item.info['plot'] = video_plot
        item.info['duration'] = video_duration
        item.set_callback(
            get_video_url,
            item_id=item_id,
            video_slug=program_slug,
            video_season_number=program_season_number,
            video_episode_number=video_episode_number)
        item_post_treatment(item, is_playable=True, is_downloadable=True)
        yield item


@Resolver.register
def get_video_url(plugin, item_id, video_slug, video_season_number,
                  video_episode_number, download_mode=False, **kwargs):

    if video_season_number == '':
        resp = urlquick.get(URL_STREAM % video_slug, headers=GENERIC_HEADERS)
    else:
        resp = urlquick.get(
            URL_STREAM_SEASON_EPISODE % (
                video_slug, video_season_number, video_episode_number), headers=GENERIC_HEADERS)

    json_datas = {
        'operationName': 'VideoPlayerPage',
        'variables': {},
        'query': 'query VideoPlayerPage($collectionSlug: String!, $seasonNumber: Int, $episodeNumber: Int) {\n  videoPlayerPage(\n    rootProductSlug: $collectionSlug\n    seasonNumber: $seasonNumber\n    episodeNumber: $episodeNumber\n  ) {\n    blocks {\n      id\n      blockType\n      ...PageMetaDataFragment\n      ... on ArtisanBlocksVideoPlayer {\n        blockConfiguration {\n          pauseAdsConfiguration\n          product {\n            ...ProductWithVideo\n            __typename\n          }\n          __typename\n        }\n        __typename\n      }\n      __typename\n    }\n    __typename\n  }\n}\n\nfragment PageMetaDataFragment on ArtisanBlocksPageMetaData {\n  id\n  blockConfiguration {\n    pageMetaDataConfiguration {\n      title\n      description\n      keywords\n      language\n      canonicalUrl\n      jsonLd\n      robots\n      productMetaData {\n        title\n        seasonName\n        seasonNumber\n        episodeName\n        episodeNumber\n        category\n        channel\n        keywords\n        kind\n        fmcApplicationId\n        productionCompany\n        productionCountry\n        francolabObjective\n        francolabTargetAudience\n        francolabDifficulties\n        francolabThemes\n        __typename\n      }\n      ogTags {\n        property\n        content\n        __typename\n      }\n      adContext {\n        slug\n        channel\n        category\n        genre\n        keywords\n        productionCountry\n        __typename\n      }\n      __typename\n    }\n    __typename\n  }\n  __typename\n}\n\nfragment ProductWithVideo on Product {\n  id\n  externalKey\n  title\n  slug\n  episodeNumber\n  seasonNumber\n  seasonName\n  productionCompany\n  productionCountry\n  productType\n  shortSummary\n  duration\n  tags\n  category {\n    id\n    label\n    __typename\n  }\n  collection {\n    id\n    title\n    slug\n    __typename\n  }\n  keywords {\n    label\n    __typename\n  }\n  kind {\n    label\n    __typename\n  }\n  mainLandscapeImage {\n    url\n    __typename\n  }\n  channel {\n    id\n    name\n    identity\n    __typename\n  }\n  nextViewableProduct {\n    id\n    slug\n    episodeNumber\n    seasonNumber\n    seasonName\n    productType\n    collection {\n      id\n      slug\n      __typename\n    }\n    __typename\n  }\n  rating {\n    id\n    type\n    __typename\n  }\n  season {\n    id\n    title\n    productionCompany\n    productionCountry\n    rating {\n      id\n      type\n      __typename\n    }\n    collection {\n      title\n      __typename\n    }\n    category {\n      label\n      __typename\n    }\n    keywords {\n      label\n      __typename\n    }\n    kind {\n      label\n      __typename\n    }\n    channel {\n      identity\n      __typename\n    }\n    __typename\n  }\n  trailerParent {\n    id\n    seasonNumber\n    episodeNumber\n    productionCompany\n    productionCountry\n    productType\n    slug\n    collection {\n      id\n      title\n      slug\n      __typename\n    }\n    category {\n      label\n      __typename\n    }\n    keywords {\n      label\n      __typename\n    }\n    kind {\n      label\n      __typename\n    }\n    channel {\n      identity\n      __typename\n    }\n    __typename\n  }\n  videoElement {\n    ... on Video {\n      id\n      duration\n      mediaId\n      creditsTimestamp\n      ads {\n        format\n        url\n        __typename\n      }\n      encodings {\n        dash {\n          url\n          __typename\n        }\n        hls {\n          url\n          __typename\n        }\n        progressive {\n          url\n          __typename\n        }\n        smooth {\n          url\n          __typename\n        }\n        __typename\n      }\n      subtitles {\n        language\n        url\n        __typename\n      }\n      __typename\n    }\n    ... on RestrictedVideo {\n      mediaId\n      code\n      reason\n      __typename\n    }\n    __typename\n  }\n  upcomingBroadcasts {\n    id\n    startsAt\n    __typename\n  }\n  activeNonLinearProgram {\n    id\n    startsAt\n    __typename\n  }\n  viewedProgress {\n    id\n    timestamp\n    __typename\n  }\n  __typename\n}',
    }

    dic_variables = {}
    variables = json.loads(re.compile(r'\"query\"\:(.*?)\}').findall(resp.text)[0] + '}')
    if 'episodeNumber' in variables.keys():
        dic_variables['episodeNumber'] = int(variables['episodeNumber'])
    if 'seasonNumber' in variables.keys():
        dic_variables['seasonNumber'] = int(variables['seasonNumber'])
    if 'collectionSlug' in variables.keys():
        dic_variables['collectionSlug'] = variables['collectionSlug']
    json_datas['variables'] = dic_variables

    resp = urlquick.post(URL_API, headers=GENERIC_HEADERS, json=json_datas, max_age=-1)
    data = json.loads(resp.text)
    video_url = data['data']['videoPlayerPage']['blocks'][1]['blockConfiguration']['product']['videoElement']['encodings']['hls']['url']

    return resolver_proxy.get_stream_with_quality(plugin, video_url)
