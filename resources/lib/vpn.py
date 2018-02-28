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

import os
from resources.lib import utils
from resources.lib import common
from resources.lib import openvpn as vpnlib

ip = "127.0.0.1"
port = 1337


def disconnect_openvpn():
    storage = common.sp.MemStorage('vpn')
    common.PLUGIN.log_debug('Disconnecting OpenVPN')
    try:
        storage['status'] = "disconnecting"
        response = vpnlib.is_running(ip, port)
        if response[0]:
            vpnlib.disconnect(ip, port)
            if response[1] is not None:
                utils.send_notification(
                    common.GETTEXT('Stopped VPN connection'), title="OpenVPN", time=3000)
        storage['status'] = "disconnected"
        common.PLUGIN.log_debug('Disconnect OpenVPN successful')
    except vpnlib.OpenVPNError as exception:
        common.sp.xbmcgui.Dialog().ok(
            'OpenVPN',
            common.GETTEXT('An error has occurred whilst trying to connect OpenVPN'))

        storage['status'] = "failed"


def connect_openvpn(config, restart=False, sudopassword=None):
    storage = common.sp.MemStorage('vpn')
    common.PLUGIN.log_debug('Connecting OpenVPN configuration: [%s]' % config)

    if common.PLUGIN.get_setting('vpn.sudo') and \
            common.PLUGIN.get_setting('vpn.sudopsw') and sudopassword is None:

        keyboard = common.sp.xbmc.Keyboard(
            default='',
            heading=common.GETTEXT('Enter your sudo password'),
            hidden=True)
        keyboard.doModal()
        if keyboard.isConfirmed():
            sudopassword = keyboard.getText()

    openvpn = vpnlib.OpenVPN(
        common.PLUGIN.get_setting('vpn.openvpnfilepath'),
        config,
        ip=ip,
        port=port,
        args=common.PLUGIN.get_setting('vpn.args'),
        sudo=common.PLUGIN.get_setting('vpn.sudo'),
        sudopwd=sudopassword,
        debug=True)

    try:
        if restart:
            openvpn.disconnect()
            storage['status'] = "disconnected"
        openvpn.connect()
        utils.send_notification(
            common.GETTEXT('Started VPN connection'), title="OpenVPN", time=3000)

        storage['status'] = "connected"
    except vpnlib.OpenVPNError as exception:
        if exception.errno == 1:
            storage['status'] = "connected"

            if common.sp.xbmcgui.Dialog().yesno(
                    'OpenVPN',
                    common.GETTEXT('An existing OpenVPN instance appears to be running.'),
                    common.GETTEXT('Disconnect it?')):

                common.PLUGIN.log_debug('User has decided to restart OpenVPN')
                connect_openvpn(config, True, sudopassword)
            else:
                common.PLUGIN.log_debug(
                    'User has decided not to restart OpenVPN')
        else:
            common.sp.xbmcgui.Dialog().ok(
                'OpenVPN',
                common.GETTEXT('An error has occurred whilst trying to connect OpenVPN'))
            storage['status'] = "failed"


def import_ovpn():
    path = common.sp.xbmcgui.Dialog().browse(
        1,
        common.GETTEXT('Import OpenVPN configuration file'),
        'files',
        mask='.ovpn|.conf',
        enableMultiple=False
    )

    if path and os.path.exists(path) and os.path.isfile(path):
        common.PLUGIN.log_debug('Import: [%s]' % path)

        keyboard = common.sp.xbmc.Keyboard(
            default='',
            heading=common.GETTEXT('Choose a name for OpenVPN configuration'),
            hidden=False)
        keyboard.doModal()
        if keyboard.isConfirmed() and len(keyboard.getText()) > 0:
            name = keyboard.getText()

            ovpnfiles = {}
            with common.PLUGIN.get_storage() as storage:
                ovpnfiles = storage['ovpnfiles']

            if name in ovpnfiles and not common.sp.xbmcgui.Dialog().yesno(
                    'OpenVPN',
                    common.GETTEXT('This OpenVPN configuration '
                        'name already exists. Overwrite?')):
                common.sp.xbmcgui.Dialog().ok('OpenVPN', common.GETTEXT('Import cancelled'))

            else:
                ovpnfiles[name] = path
                with common.PLUGIN.get_storage() as storage:
                    storage['ovpnfiles'] = ovpnfiles
        else:
            common.sp.xbmcgui.Dialog().ok(
                'OpenVPN',
                common.GETTEXT('Import failed. You must specify a '
                    'name for the OpenVPN configuration'))


def select_ovpn():
    ovpnfiles = {}
    with common.PLUGIN.get_storage() as storage:
        try:
            ovpnfiles = storage['ovpnfiles']
        except KeyError:
            storage['ovpnfiles'] = ovpnfiles

    if len(ovpnfiles) == 0:
        return None

    else:
        response = vpnlib.is_running(ip, port)
        common.PLUGIN.log_debug('Response from is_running: [%s] [%s] [%s]' % (
            response[0], response[1], response[2]))
        if response[0]:
            # Le VPN est connecté
            print 'VPN Encore connecté, pas normal, je vais le déco'
            disconnect_openvpn()

        configs = []
        ovpnfileslist = []
        for name, configfilepath in ovpnfiles.iteritems():
            configs.append(name)
            ovpnfileslist.append(configfilepath)

        idx = common.sp.xbmcgui.Dialog().select(
            common.GETTEXT('Select OpenVPN configuration to run'), configs)
        if idx >= 0:
            common.PLUGIN.log_debug('Select: [%s]' % ovpnfileslist[idx])
            return ovpnfileslist[idx]
        else:
            return ''


def delete_ovpn():
    ovpnfiles = {}
    with common.PLUGIN.get_storage() as storage:
        try:
            ovpnfiles = storage['ovpnfiles']
        except KeyError:
            storage['ovpnfiles'] = ovpnfiles

    if len(ovpnfiles) == 0:
        return None

    else:
        response = vpnlib.is_running(ip, port)
        common.PLUGIN.log_debug('Response from is_running: [%s] [%s] [%s]' % (
            response[0], response[1], response[2]))
        if response[0]:
            # Le VPN est connecté
            print 'VPN Encore connecté, pas normal, je vais le déco'
            disconnect_openvpn()

        configs = []
        ovpnfileslist = []
        for name, configfilepath in ovpnfiles.iteritems():
            configs.append(name)
            ovpnfileslist.append(configfilepath)

        idx = common.sp.xbmcgui.Dialog().select(
            common.GETTEXT('Select OpenVPN configuration to delete'), configs)
        if idx >= 0:
            common.PLUGIN.log_debug('Select: [%s]' % ovpnfileslist[idx])
            new_ovpnfiles = {}
            for name, configfilepath in ovpnfiles.iteritems():
                if configfilepath != ovpnfileslist[idx]:
                    new_ovpnfiles[name] = configfilepath
            with common.PLUGIN.get_storage() as storage:
                storage['ovpnfiles'] = new_ovpnfiles
        else:
            return ''


def root(params):
    storage = common.sp.MemStorage('vpn')
    if 'status' not in storage:
        storage['status'] = "disconnected"

    if "from_settings" in params:
        if params.from_settings == "import":
            import_ovpn()
            return None
        elif params.from_settings == "delete":
            delete_ovpn()
            return None
        elif params.from_settings == "connectdisconnect":
            if storage['status'] != "connected":
                ovpn = select_ovpn()
                if ovpn is None:
                    import_ovpn()

                if len(ovpn) > 0:
                    connect_openvpn(ovpn)
            else:
                disconnect_openvpn()

    elif storage['status'] != "connected":
        ovpn = select_ovpn()
        if ovpn is None:
            import_ovpn()

        if len(ovpn) > 0:
            connect_openvpn(ovpn)

    elif storage['status'] == "connected":
        disconnect_openvpn()

    common.sp.xbmc.executebuiltin('XBMC.Container.Refresh()')
