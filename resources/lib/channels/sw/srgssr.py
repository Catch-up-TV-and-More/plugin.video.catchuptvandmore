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

# TO DO
# RTR (JSON empty ? for category)
# Live TV
# Add More Video_button (for category)
# Add all emission (All channels)
# Add Info Video
# Add Quality Mode / test Download Mode

# Initialize GNU gettext emulation in addon
# This allows to use UI strings from addon’s English
# strings.po file instead of numeric codes
_ = common.ADDON.initialize_gettext()

URL_ROOT = 'https://%s.%s.ch'
# (www or play), channel_name

# Replay
URL_CATEGORIES_JSON = 'https://%s.%s.ch/play/v2/tv/topicList?layout=json'
# (www or play), channel_name

URL_TOKEN = 'https://tp.srgssr.ch/akahd/token?acl=/i/%s/*'
# channel_name

URL_INFO_VIDEO = 'https://il.srgssr.ch/integrationlayer' \
                 '/2.0/%s/mediaComposition/video/%s.json' \
                 '?onlyChapters=true&vector=portalplay'
# channel_name, video_id

def channel_entry(params):
    """Entry function of the module"""
    if 'root' in params.next:
        return root(params)
    elif 'list_shows' in params.next:
        return list_shows(params)
    elif 'list_videos' in params.next:
        return list_videos(params)
    elif 'live' in params.next:
        return list_live(params)
    elif 'play' in params.next:
        return get_video_url(params)
    return None

@common.PLUGIN.mem_cached(common.CACHE_TIME)
def root(params):
    """Add Replay and Live in the listing"""
    modes = []

    # Add Replay
    modes.append({
        'label': 'Replay',
        'url': common.PLUGIN.get_url(
            action='channel_entry',
            next='list_shows_1',
            page='0',
            category='%s Replay' % params.channel_name.upper(),
            window_title='%s Replay' % params.channel_name
        ),
    })

    # Add Live
    #if params.channel_name != 'swissinfo':
        #modes.append({
            #'label': _('Live TV'),
            #'url': common.PLUGIN.get_url(
                #action='channel_entry',
                #next='live_cat',
                #category='%s Live TV' % params.channel_name.upper(),
                #window_title='%s Live TV' % params.channel_name
            #),
        #})

    return common.PLUGIN.create_listing(
        modes,
        sort_methods=(
            common.sp.xbmcplugin.SORT_METHOD_UNSORTED,
            common.sp.xbmcplugin.SORT_METHOD_LABEL
        ),
        category=common.get_window_title()
    )


@common.PLUGIN.mem_cached(common.CACHE_TIME)
def list_shows(params):
    """Build categories listing"""
    shows = []

    if params.next == 'list_shows_1':

        if params.channel_name == 'swissinfo':
            first_part_fqdn = 'play'
        else:
            first_part_fqdn = 'www'

        file_path = utils.get_webcontent(
            URL_CATEGORIES_JSON % (first_part_fqdn,
                params.channel_name)
        )
        replay_categories_json = json.loads(file_path)

        for category in replay_categories_json:

            show_title = category["title"].encode('utf-8')
            show_url = URL_ROOT % (first_part_fqdn,
                params.channel_name) + \
                category["latestModuleUrl"].encode('utf-8')

            shows.append({
                'label': show_title,
                'url': common.PLUGIN.get_url(
                    action='channel_entry',
                    next='list_videos_1',
                    title=show_title,
                    show_url=show_url,
                    window_title=show_title
                )
            })

    return common.PLUGIN.create_listing(
        shows,
        sort_methods=(
            common.sp.xbmcplugin.SORT_METHOD_UNSORTED,
            common.sp.xbmcplugin.SORT_METHOD_LABEL
        ),
        category=common.get_window_title()
    )


@common.PLUGIN.mem_cached(common.CACHE_TIME)
def list_videos(params):
    """Build videos listing"""
    videos = []

    file_path = utils.get_webcontent(params.show_url)
    datas_videos = re.compile(
        r'data-teaser=\"(.*?)\"').findall(file_path)[0]
    datas_videos = datas_videos.replace('&quot;', '"')
    datas_videos_json = json.loads(datas_videos)

    for episode in datas_videos_json:

        video_title = ''
        if 'showTitle' in episode:
            video_title = episode["showTitle"].encode('utf-8') + \
            ' - ' + episode["title"].encode('utf-8')
        else:
            video_title = episode["title"].encode('utf-8')
        video_duration = 0
        video_plot = ''
        if 'description' in episode:
            video_plot = episode["description"].encode('utf-8')
        video_img = episode["imageUrl"].encode('utf-8') + \
            '/scale/width/448'
        video_url = episode["absoluteDetailUrl"].encode('utf-8')

        info = {
            'video': {
                'title': video_title,
                # 'aired': aired,
                # 'date': date,
                'duration': video_duration,
                'plot': video_plot,
                # 'year': year,
                'mediatype': 'tvshow'
            }
        }

        context_menu = []
        download_video = (
            _('Download'),
            'XBMC.RunPlugin(' + common.PLUGIN.get_url(
                action='download_video',
                video_url=video_url) + ')'
        )
        context_menu.append(download_video)

        videos.append({
            'label': video_title,
            'thumb': video_img,
            'fanart': video_img,
            'url': common.PLUGIN.get_url(
                action='channel_entry',
                next='play_r',
                video_url=video_url
            ),
            'is_playable': True,
            'info': info  # ,
            # 'context_menu': context_menu
        })

    return common.PLUGIN.create_listing(
        videos,
        sort_methods=(
            common.sp.xbmcplugin.SORT_METHOD_UNSORTED,
            common.sp.xbmcplugin.SORT_METHOD_DURATION,
            common.sp.xbmcplugin.SORT_METHOD_LABEL_IGNORE_THE,
            common.sp.xbmcplugin.SORT_METHOD_GENRE,
            common.sp.xbmcplugin.SORT_METHOD_UNSORTED
        ),
        content='tvshows',
        update_listing='update_listing' in params,
        category=common.get_window_title()
    )


@common.PLUGIN.mem_cached(common.CACHE_TIME)
def list_live(params):
    """Build live listing"""
    return None


@common.PLUGIN.mem_cached(common.CACHE_TIME)
def get_video_url(params):
    """Get video URL and start video player"""
    if params.next == 'play_r' or params.next == 'download_video':
        video_id = params.video_url.split('=')[1]
        print 'video_id :'  + video_id
        if params.channel_name == 'swissinfo':
            channel_name_value = 'swi'
        else :
            channel_name_value = params.channel_name
        streams_datas = utils.get_webcontent(
            URL_INFO_VIDEO % (channel_name_value, video_id))
        print 'streams_datas :'  + streams_datas
        streams_json = json.loads(streams_datas)
        token_datas = utils.get_webcontent(
            URL_TOKEN % channel_name_value)
        token_json = json.loads(token_datas)

        # build url
        token = token_json["token"]["authparams"]
        url = ''
        for stream in streams_json["chapterList"]:
            if video_id in stream["id"]:
                for url_stream in stream["resourceList"]:
                    if url_stream["quality"] == 'HD' and \
                       'mpegURL' in url_stream["mimeType"]:
                        url = url_stream["url"]
        return url + '?' + token
