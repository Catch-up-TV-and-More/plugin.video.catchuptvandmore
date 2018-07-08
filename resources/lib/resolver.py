# -*- coding: utf-8 -*-
"""
    Catch-up TV & More
    Copyright (C) 2017  SylvainCecchetto

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

import json
import re
from resources.lib import utils
from resources.lib import common

# TO DO
# Quality VIMEO
# Download Mode with Facebook (the video has no audio)


DESIRED_QUALITY = common.PLUGIN.get_setting('quality')

URL_DAILYMOTION_EMBED = 'http://www.dailymotion.com/embed/video/%s'
# Video_id

URL_VIMEO_BY_ID = 'https://player.vimeo.com/video/%s?autoplay=1'
# Video_id

URL_FACEBOOK_BY_ID = 'https://www.facebook.com/allocine/videos/%s'
# Video_id

URL_YOUTUBE = 'https://www.youtube.com/embed/%s?&autoplay=0'
# Video_id

URL_BRIGHTCOVE_POLICY_KEY = 'http://players.brightcove.net/%s/%s_default/index.min.js'
# AccountId, PlayerId

URL_BRIGHTCOVE_VIDEO_JSON = 'https://edge.api.brightcove.com/'\
                            'playback/v1/accounts/%s/videos/%s'
# AccountId, VideoId

URL_MTVNSERVICES_STREAM = 'https://media-utils.mtvnservices.com/services/' \
                          'MediaGenerator/%s?&format=json&acceptMethods=hls'
# videoURI

def ytdl_resolver(url_stream):
    
    YDStreamExtractor = __import__('YDStreamExtractor')

    quality = 0
    if DESIRED_QUALITY == "DIALOG":
        all_quality = ['SD', '720p', '1080p', 'Highest available']
        seleted_item = common.sp.xbmcgui.Dialog().select(
            common.GETTEXT('Choose video quality'),
            all_quality)

        if seleted_item > -1:
            selected_quality_string = all_quality[seleted_item]
            quality_string = {
                'SD': 0,
                '720p': 1,
                '1080p': 2,
                'Highest available': 3
            }
            quality = quality_string[selected_quality_string]
        else:
            return None
    elif DESIRED_QUALITY == "BEST":
        quality = 3

    vid = YDStreamExtractor.getVideoInfo(
        url_stream,
        quality=quality,
        resolve_redirects=True
    )
    if vid is None:
        # TODO catch the error (geo-blocked, deleted, etc ...)
        utils.send_notification(
            common.ADDON.get_localized_string(30716))
        return None
    else:
        return vid.streamURL()
    

# Kaltura Part
def get_stream_kaltura(video_url, isDownloadVideo):

    if isDownloadVideo == True:
        return video_url
    return ytdl_resolver(video_url)

# DailyMotion Part
def get_stream_dailymotion(video_id, isDownloadVideo):

    url_dmotion = URL_DAILYMOTION_EMBED % (video_id)

    if isDownloadVideo == True:
        return url_dmotion
    return ytdl_resolver(url_dmotion)

# Vimeo Part
def get_stream_vimeo(video_id, isDownloadVideo):

    url_vimeo = URL_VIMEO_BY_ID % (video_id)

    if isDownloadVideo == True:
        return url_vimeo

    html_vimeo = utils.get_webcontent(url_vimeo)
    # TODO Find a better way to get JSON of VIMEO
    json_vimeo = json.loads(re.compile('var a=(.*?);').findall(
        html_vimeo)[0])
    hls_json = json_vimeo["request"]["files"]["hls"]
    default_cdn = hls_json["default_cdn"]
    return hls_json["cdns"][default_cdn]["url"]

# Facebook Part
def get_stream_facebook(video_id, isDownloadVideo):

    url_facebook = URL_FACEBOOK_BY_ID % (video_id)

    if isDownloadVideo == True:
        return url_facebook

    html_facebook = utils.get_webcontent(url_facebook)

    if len(re.compile(
        r'hd_src_no_ratelimit:"(.*?)"').findall(
        html_facebook)) > 0:
        if DESIRED_QUALITY == "DIALOG":
            all_datas_videos_quality = []
            all_datas_videos_path = []
            all_datas_videos_quality.append('SD')
            all_datas_videos_path.append(re.compile(
                r'sd_src_no_ratelimit:"(.*?)"').findall(
                html_facebook)[0])
            all_datas_videos_quality.append('HD')
            all_datas_videos_path.append(re.compile(
                r'hd_src_no_ratelimit:"(.*?)"').findall(
                html_facebook)[0])
            seleted_item = common.sp.xbmcgui.Dialog().select(
                common.GETTEXT('Choose video quality'),
                all_datas_videos_quality)
            if selected_item > -1:
                return all_datas_videos_path[seleted_item].encode(
                    'utf-8')
            else:
                return None
        elif DESIRED_QUALITY == 'BEST':
            return re.compile(
                r'hd_src_no_ratelimit:"(.*?)"').findall(
                html_facebook)[0]
        else:
            return re.compile(
                r'sd_src_no_ratelimit:"(.*?)"').findall(
                html_facebook)[0]
    else:
        return re.compile(
            r'sd_src_no_ratelimit:"(.*?)"').findall(
            html_facebook)[0]


# Youtube Part
def get_stream_youtube(video_id, isDownloadVideo):
    url_youtube = URL_YOUTUBE % video_id

    if isDownloadVideo is True:
        return url_youtube

    return ytdl_resolver(url_youtube)


# BRIGHTCOVE Part
def get_brightcove_policy_key(data_account, data_player):
    """Get policy key"""
    file_js = utils.get_webcontent(
        URL_BRIGHTCOVE_POLICY_KEY % (data_account, data_player))
    return re.compile('policyKey:"(.+?)"').findall(file_js)[0]


def get_brightcove_video_json(data_account, data_player, data_video_id):

    # Method to get JSON from 'edge.api.brightcove.com'
    file_json = utils.download_catalog(
        URL_BRIGHTCOVE_VIDEO_JSON % (data_account, data_video_id),
        '%s_%s_replay.json' % (data_account, data_video_id),
        force_dl=False,
        request_type='get',
        post_dic={},
        random_ua=False,
        specific_headers={'Accept': 'application/json;pk=%s' % (
            get_brightcove_policy_key(data_account, data_player))},
        params={})
    video_json = open(file_json).read()
    json_parser = json.loads(video_json)

    video_url = ''
    if 'sources' in json_parser:
        for url in json_parser["sources"]:
            if 'src' in url:
                if 'm3u8' in url["src"]:
                    video_url = url["src"]
    else:
        if json_parser[0]['error_code'] == "ACCESS_DENIED":
            utils.send_notification(
                common.ADDON.get_localized_string(30713))
            return None
    return video_url

def get_mtvnservices_stream(video_uri):
    json_video_stream = utils.get_webcontent(
        URL_MTVNSERVICES_STREAM % video_uri)
    json_video_stream_parser = json.loads(json_video_stream)
    return json_video_stream_parser["package"]["video"]["item"][0]["rendition"][0]["src"]
