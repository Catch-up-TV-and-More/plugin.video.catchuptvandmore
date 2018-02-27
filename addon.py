# -*- coding: utf-8 -*-
"""
    Catch-up TV & More
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

import imp
import YDStreamUtils
import YDStreamExtractor
from resources.lib import skeleton
from resources.lib import common
from resources.lib import vpn
from resources.lib import utils


# Useful path
LIB_PATH = common.sp.xbmc.translatePath(
    common.sp.os.path.join(
        common.ADDON.path,
        "resources",
        "lib"
    )
)

MEDIA_PATH = (
    common.sp.xbmc.translatePath(
        common.sp.os.path.join(
            common.ADDON.path,
            "resources",
            "media"
        )
    )
)

# Initialize GNU gettext emulation in addon
# This allows to use UI strings from addon’s English
# strings.po file instead of numeric codes
_ = common.ADDON.initialize_gettext()


@common.PLUGIN.action()
def root(params):
    """
    Build a generic addon menu
    with all not hidden items
    """
    current_skeleton = skeleton.SKELETON[('root', 'root')]
    current_path = ['root']

    if 'item_skeleton' in params:
        current_skeleton = eval(params.item_skeleton)
        current_path = eval(params.item_path)

    # First we sort the current menu
    menu = []
    for value in current_skeleton:
        item_id = value[0]
        item_next = value[1]
        # If menu item isn't disable
        if common.PLUGIN.get_setting(item_id):
            # Get order value in settings file
            item_order = common.PLUGIN.get_setting(item_id + '.order')

            # Get english item title in LABELS dict in skeleton file
            # and check if this title has any translated version
            item_title = ''
            try:
                item_title = common.PLUGIN.get_localized_string(
                    skeleton.LABELS[item_id])
            except TypeError:
                item_title = skeleton.LABELS[item_id]

            # Build step by step the module pathfile
            item_path = list(current_path)
            if item_id in skeleton.FOLDERS:
                item_path.append(skeleton.FOLDERS[item_id])
            else:
                item_path.append(item_id)

            item_skeleton = {}
            try:
                item_skeleton = current_skeleton[value]
            except TypeError:
                item_skeleton = {}

            item = (item_order, item_id, item_title, item_path, item_next,
                    item_skeleton)
            menu.append(item)

    menu = sorted(menu, key=lambda x: x[0])

    # If only one item is present, directly open this item
    only_one_item = False
    if len(menu) == 1:
        only_one_item = True
        item = menu[0]
        item_id = item[1]
        item_title = item[2]
        item_path = item[3]
        item_next = item[4]
        item_skeleton = item[5]

        params['item_id'] = item_id
        params['item_path'] = str(item_path)
        params['item_skeleton'] = str(item_skeleton)
        params['window_title'] = item_title

        if item_next == 'root':
            return root(params)
        elif item_next == 'replay_entry':
            return replay_entry(params)
        elif item_next == 'build_live_tv_menu':
            return build_live_tv_menu(params)
        else:
            only_one_item = False

    if not only_one_item:
        listing = []
        for index, (item_order, item_id, item_title, item_path, item_next,
                    item_skeleton) in enumerate(menu):

            # Build context menu (Move up, move down, ...)
            context_menu = []

            item_down = (
                _('Move down'),
                'XBMC.RunPlugin(' + common.PLUGIN.get_url(
                    action='move',
                    direction='down',
                    item_id_order=item_id + '.order',
                    displayed_items=menu) + ')'
            )
            item_up = (
                _('Move up'),
                'XBMC.RunPlugin(' + common.PLUGIN.get_url(
                    action='move',
                    direction='up',
                    item_id_order=item_id + '.order',
                    displayed_items=menu) + ')'
            )

            if index == 0:
                context_menu.append(item_down)
            elif index == len(menu) - 1:
                context_menu.append(item_up)
            else:
                context_menu.append(item_up)
                context_menu.append(item_down)

            hide = (
                _('Hide'),
                'XBMC.RunPlugin(' + common.PLUGIN.get_url(
                    action='hide',
                    item_id=item_id) + ')'
            )
            context_menu.append(hide)

            context_menu.append(utils.vpn_context_menu_item())

            media_item_path = common.sp.xbmc.translatePath(
                common.sp.os.path.join(
                    MEDIA_PATH,
                    *(item_path)
                )
            )

            media_item_path = media_item_path.decode(
                "utf-8").encode(common.FILESYSTEM_CODING)

            icon = media_item_path + '.png'
            fanart = media_item_path + '_fanart.jpg'

            listing.append({
                'icon': icon,
                'fanart': fanart,
                'label': item_title,
                'url': common.PLUGIN.get_url(
                    action=item_next,
                    item_id=item_id,
                    item_path=str(item_path),
                    item_skeleton=str(item_skeleton),
                    window_title=item_title
                ),
                'context_menu': context_menu
            })

        return common.PLUGIN.create_listing(
            listing,
            sort_methods=(
                common.sp.xbmcplugin.SORT_METHOD_UNSORTED,),
            category=common.get_window_title()
        )


def get_module(params):
    if 'module_name' in params and \
            'module_path' in params:
        storage = common.sp.MemStorage('last_module')
        storage['last_module_path'] = params.module_path
        storage['last_module_name'] = params.module_name
    else:
        storage = common.sp.MemStorage('last_module')
        params['module_path'] = storage['last_module_path']
        params['module_name'] = storage['last_module_name']

    module_path = common.sp.xbmc.translatePath(
        common.sp.os.path.join(
            LIB_PATH,
            *(eval(params.module_path))
        )
    )
    module_filepath = module_path + ".py"
    module_filepath = module_filepath.decode(
        "utf-8").encode(common.FILESYSTEM_CODING)

    return imp.load_source(
        params.module_name,
        module_filepath
    )


@common.PLUGIN.action()
def replay_entry(params):
    if 'item_id' in params:
        params['module_name'] = params.item_id  # w9
        module_path = eval(params.item_path)
        module_path.pop()
        module_path.append(skeleton.CHANNELS[params.module_name])

        # ['root', 'channels', 'fr', '6play']
        params['module_path'] = str(module_path)
        params['next'] = 'replay_entry'

    # Legacy fix (il faudrait remplacer channel_name par
    # module_name dans tous les .py des chaines)
    params['channel_name'] = params.module_name

    channel = get_module(params)

    # Let's go to the channel python file ...
    return channel.channel_entry(params)


@common.PLUGIN.action()
def build_live_tv_menu(params):
    listing = []

    folder_path = eval(params.item_path)
    for channel in eval(params.item_skeleton):
        channel_name = channel[0]
        channel_path = list(folder_path)
        channel_path.append(skeleton.CHANNELS[channel_name])

        params['module_path'] = str(channel_path)
        params['module_name'] = channel_name
        params['channel_label'] = skeleton.LABELS[channel_name]
        print "CURRENT CHANNEL : " + channel_name


        # Legacy fix (il faudrait remplacer channel_name par
        # module_name dans tous les .py des chaines)
        params['channel_name'] = params.module_name

        channel = get_module(params)

        listing = channel.get_live_item(params, listing)

    return common.PLUGIN.create_listing(
        listing,
        sort_methods=(
            common.sp.xbmcplugin.SORT_METHOD_UNSORTED,
            common.sp.xbmcplugin.SORT_METHOD_LABEL
        ),
        category=common.get_window_title()
    )


@common.PLUGIN.action()
def start_live_tv_stream(params):
    # Legacy fix (il faudrait remplacer channel_name par
    # module_name dans tous les .py des chaines)
    params['channel_name'] = params.module_name

    channel = get_module(params)

    return channel.get_video_url(params)


@common.PLUGIN.action()
def website_entry(params):
    if 'item_id' in params:
        params['module_name'] = params.item_id
        params['module_path'] = params.item_path
        params['next'] = 'root'

    website = get_module(params)

    # Let's go to the website python file ...
    return website.website_entry(params)


@common.PLUGIN.action()
def move(params):
    if params.direction == 'down':
        offset = + 1
    elif params.direction == 'up':
        offset = - 1

    for k in range(0, len(params.displayed_items)):
        item = eval(params.displayed_items[k])
        item_order = item[0]
        item_id = item[1]
        if item_id + '.order' == params.item_id_order:
            item_swaped = eval(params.displayed_items[k + offset])
            item_swaped_order = item_swaped[0]
            item_swaped_id = item_swaped[1]
            common.PLUGIN.set_setting(
                params.item_id_order,
                item_swaped_order)
            common.PLUGIN.set_setting(
                item_swaped_id + '.order',
                item_order)
            common.sp.xbmc.executebuiltin('XBMC.Container.Refresh()')
            return None


@common.PLUGIN.action()
def hide(params):
    if common.PLUGIN.get_setting('show_hidden_items_information'):
        common.sp.xbmcgui.Dialog().ok(
            _('Information'),
            _('To re-enable hidden items go to the plugin settings'))
        common.PLUGIN.set_setting('show_hidden_items_information', False)

    common.PLUGIN.set_setting(params.item_id, False)
    common.sp.xbmc.executebuiltin('XBMC.Container.Refresh()')
    return None


@common.PLUGIN.action()
def download_video(params):
    #  Ici on a seulement le lien de la page web où se trouve la video
    #  Il faut appeller la fonction get_video_url de la chaine concernée
    #  pour avoir l'URL finale de la vidéo
    channel = get_channel_module(params)
    params.next = 'download_video'
    url_video = channel.get_video_url(params)

    #  Maintenant on peut télécharger la vidéo

    print 'URL_VIDEO to download ' + url_video

    vid = YDStreamExtractor.getVideoInfo(url_video, quality=3)
    path = common.PLUGIN.get_setting('dlFolder')
    path = path.decode(
        "utf-8").encode(common.FILESYSTEM_CODING)

    with YDStreamUtils.DownloadProgress() as prog:
        try:
            YDStreamExtractor.setOutputCallback(prog)
            result = YDStreamExtractor.downloadVideo(vid, path)
            if result:
                # success
                full_path_to_file = result.filepath
            elif result.status != 'canceled':
                # download failed
                error_message = result.message
        finally:
            YDStreamExtractor.setOutputCallback(None)

    return None


@common.PLUGIN.action()
def vpn_entry(params):
    vpn.root(params)
    return None


@common.PLUGIN.action()
def clear_cache():
    utils.clear_cache()
    return None


if __name__ == '__main__':
    common.PLUGIN.run()
