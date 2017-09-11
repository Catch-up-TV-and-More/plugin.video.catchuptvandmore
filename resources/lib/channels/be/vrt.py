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

# Initialize GNU gettext emulation in addon
# This allows to use UI strings from addon’s English
# strings.po file instead of numeric codes
_ = common.ADDON.initialize_gettext()

URL_JSON_LIVES = 'https://services.vrt.be/videoplayer/r/live.json'
# All lives in this JSON

#To get videoid :
# Authentication
# https://accounts.vrt.be/accounts.login?context=%s&saveResponseID=%s % (contextid)
        # FORM DATA
        #loginID: ***********
        #password:**********
        #sessionExpiration:-2
        #targetEnv:jssdk
        #include:profile,data
        #includeUserInfo:true
        #APIKey:3_qhEcPa5JGFROVwu5SWKqJ4mVOIkwlFNMSKwzPDAh8QZOtHqu6L4nD5Q7lk0eXOOG (how to get?)
        #includeSSOToken:true
        #sdk:js_7.3.30
        #authMode:cookie
        #pageURL:https://www.vrt.be/vrtnu/a-z/100-jaar-slag-bij-passendale/2017/100-jaar-slag-bij-passendale-s2017/
        #format:jsonp
        #callback:gigya.callback
        #context:%s (how to get ?)
        #utf8:✓
# https://accounts.vrt.be/socialize.getSavedResponse?APIKey=3_qhEcPa5JGFROVwu5SWKqJ4mVOIkwlFNMSKwzPDAh8QZOtHqu6L4nD5Q7lk0eXOOG&saveResponseID=%s&noAuth=true&sdk=js_7.3.30&format=jsonp&callback=gigya.callback&context=%s
#  Context id,
## https://token.vrt.be/
# https://token.vrt.be/

#After Authentification (go to this url)
#(go to this url) https://www.vrt.be/vrtnu/a-z/ (select a show)
# url_show + .securevideo.json
# exemple https://www.vrt.be/vrtnu/a-z/100-jaar-slag-bij-passendale/2017/100-jaar-slag-bij-passendale-s2017.securevideo.json => get videoid
URL_VIDEO_VOD_JSON = 'https://mediazone.vrt.be/api/v1/vrtvideo/assets/%s'
# Video ID

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
    else:
        return None

#@common.plugin.cached(common.cache_time)
def root(params):
    modes = []

    # Add Replay
    #modes.append({
    #        'label' : 'Replay',
    #        'url': common.plugin.get_url(
    #            action='channel_entry',
    #            next='list_shows_1',
    #            category='%s Replay' % params.channel_name.upper(),
    #            window_title='%s Replay' % params.channel_name.upper()
    #        ),
    #})

    # Add Live
    modes.append({
        'label' : 'Live TV',
        'url': common.PLUGIN.get_url(
            action='channel_entry',
            next='live_cat',
            category='%s Live TV' % params.channel_name.upper(),
            window_title='%s Live TV' % params.channel_name.upper()
        ),
    })

    return common.PLUGIN.create_listing(
        modes,
        sort_methods=(
            common.sp.xbmcplugin.SORT_METHOD_UNSORTED,
            common.sp.xbmcplugin.SORT_METHOD_LABEL
        ),
    )

#@common.plugin.cached(common.cache_time)
def list_shows(params):
    shows = []

    return None

#@common.plugin.cached(common.cache_time)
def list_videos(params):
    videos = []

    return None

#@common.plugin.cached(common.cache_time)
def list_live(params):
    lives = []

    title = ''
    subtitle = ' - '
    plot = ''
    duration = 0
    img = ''
    url_live = ''

    file_path = utils.download_catalog(
        URL_JSON_LIVES,
        '%s_live.json' % (params.channel_name))
    lives_json = open(file_path).read()
    lives_json = lives_json.replace(')','').replace('parseLiveJson(','')
    lives_jsonparser = json.loads(lives_json)

    url_live = lives_jsonparser["vualto_%s" % (params.channel_name)]["hls"]

    title = '%s Live' % params.channel_name.upper()

    info = {
        'video': {
            'title': title,
            'plot': plot,
            'duration': duration
        }
    }

    lives.append({
        'label': title,
        'fanart': img,
        'thumb': img,
        'url' : common.PLUGIN.get_url(
            action='channel_entry',
            next='play_l',
            url_live=url_live,
        ),
        'is_playable': True,
        'info': info
    })

    return common.PLUGIN.create_listing(
        lives,
        sort_methods=(
            common.sp.xbmcplugin.SORT_METHOD_UNSORTED,
            common.sp.xbmcplugin.SORT_METHOD_LABEL
        )
    )

#@common.plugin.cached(common.cache_time)
def get_video_url(params):
    if params.next == 'play_l':
        return params.url_live
