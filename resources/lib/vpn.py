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

# Initialize GNU gettext emulation in addon
# This allows to use UI strings from addon’s English
# strings.po file instead of numeric codes
_ = common.ADDON.initialize_gettext()

# 'enum' of connection states
(disconnected, failed, connecting, disconnecting, connected) = range(5)
state = disconnected

ip = "127.0.0.1"
port = 1337


def connect_openvpn(config, params, restart=False, sudopassword=None):
    common.PLUGIN.log_debug('Connecting OpenVPN configuration: [%s]' % config)

    if common.PLUGIN.get_setting('vpn.sudo') and \
            common.PLUGIN.get_setting('vpn.sudopsw') and sudopassword is None:

        keyboard = common.sp.xbmc.Keyboard(
            default='',
            heading=_('Enter your sudo password'),
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
            params.status = "disconnected"
        openvpn.connect()
        utils.send_notification(
            _('Started VPN connection'), title="OpenVPN", time=3000)

        params.status = "connected"
    except vpnlib.OpenVPNError as exception:
        if exception.errno == 1:
            params.status = "connected"

            if common.sp.xbmcgui.Dialog().yesno(
                    'OpenVPN',
                    _('An existing OpenVPN instance appears to be running'),
                    _('Disconnect it?')):

                common.PLUGIN.log_debug('User has decided to restart OpenVPN')
                connect_openvpn(config, True, sudopassword)
            else:
                common.PLUGIN.log_debug(
                    'User has decided not to restart OpenVPN')
        else:
            common.sp.xbmcgui.Dialog().ok(
                'OpenVPN',
                _('An error has occurred whilst trying to connect OpenVPN'))
            params.status = "failed"


def import_ovpn():
    path = common.sp.xbmcgui.Dialog().browse(
        1,
        _('Import OpenVPN configuration file'),
        'files',
        mask='.ovpn|.conf',
        enableMultiple=False
    )

    if path and os.path.exists(path) and os.path.isfile(path):
        common.PLUGIN.log_debug('Import: [%s]' % path)

        keyboard = common.sp.xbmc.Keyboard(
            default='',
            heading=_('Choose a name for OpenVPN configuration'),
            hidden=False)
        keyboard.doModal()
        if keyboard.isConfirmed() and len(keyboard.getText()) > 0:
            name = keyboard.getText()

            ovpnfiles = {}
            with common.PLUGIN.get_storage() as storage:
                ovpnfiles = storage['ovpnfiles']

            if name in ovpnfiles and not common.sp.xbmcgui.Dialog().yesno(
                    'OpenVPN', _('This OpenVPN configuration name already exists. Overwrite?')):
                common.sp.xbmcgui.Dialog().ok('OpenVPN', _('Import cancelled'))

            else:
                ovpnfiles[name] = path
                with common.PLUGIN.get_storage() as storage:
                    storage['ovpnfiles'] = ovpnfiles
        else:
            common.sp.xbmcgui.Dialog().ok('OpenVPN', _('Import failed. You must specify a name for the OpenVPN configuration'))


def select_ovpn():
    global _state
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
            print 'VPN Encore connecté, pas normal'

        configs = []
        ovpnfileslist = []
        for name, configfilepath in ovpnfiles.iteritems():
            configs.append(name)
            ovpnfileslist.append(configfilepath)

        idx = common.sp.xbmcgui.Dialog().select(
            _('Select OpenVPN configuration to run'), configs)
        if idx >= 0:
            common.PLUGIN.log_debug('Select: [%s]' % ovpnfileslist[idx])
            return ovpnfileslist[idx]
        else:
            return ''


def root(params):
    if params.status is None or params.status is not "connected":
        ovpn = select_ovpn()
        if ovpn is None:
            import_ovpn()

        if len(ovpn) > 0:
            connect_openvpn(ovpn, params)





