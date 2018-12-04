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
import xbmc
import xbmcgui
from resources.lib import openvpn as vpnlib
from resources.lib.labels import LABELS
from codequick import Route, utils, Script, storage


ip = "127.0.0.1"
port = 1337


def disconnect_openvpn():
    with storage.PersistentDict('vpn') as db:
        Script.log('OpenVPN: Disconnecting OpenVPN')
        try:
            db['status'] = "disconnecting"
            response = vpnlib.is_running(ip, port)
            if response[0]:
                vpnlib.disconnect(ip, port)
                if response[1] is not None:
                    Script.notify(
                        'OpenVPN',
                        Script.localize(LABELS['Stopped VPN connection']))
            db['status'] = "disconnected"
            Script.log('OpenVPN: Disconnect OpenVPN successful')
        except vpnlib.OpenVPNError as exception:
            xbmcgui.Dialog().ok(
                'OpenVPN',
                Script.localize(LABELS['An error has occurred whilst trying to connect OpenVPN']))
            Script.log('OpenVPN: OpenVPN error: ' + str(exception))
            db['status'] = "failed"
        db.flush()


def connect_openvpn(config, restart=False, sudopassword=None):
    with storage.PersistentDict('vpn') as db:
        Script.log('OpenVPN: Connecting OpenVPN configuration: [%s]' % config)

        if Script.setting.get_boolean('vpn.sudo') and \
                Script.setting.get_boolean('vpn.sudopsw') and sudopassword is None:

            keyboard = xbmc.Keyboard(
                default='',
                heading=Script.localize(LABELS['Enter your sudo password']),
                hidden=True)
            keyboard.doModal()
            if keyboard.isConfirmed():
                sudopassword = keyboard.getText()

        openvpn = vpnlib.OpenVPN(
            Script.setting.get_string('vpn.openvpnfilepath'),
            config,
            ip=ip,
            port=port,
            args=Script.setting.get_string('vpn.args'),
            sudo=Script.setting.get_boolean('vpn.sudo'),
            sudopwd=sudopassword,
            debug=True)

        try:
            if restart:
                openvpn.disconnect()
                db['status'] = "disconnected"
            openvpn.connect()
            utils.send_notification(
                Script.localize(LABELS['Started VPN connection']), title="OpenVPN", time=3000)

            db['status'] = "connected"
        except vpnlib.OpenVPNError as exception:
            if exception.errno == 1:
                db['status'] = "connected"

                if xbmcgui.Dialog().yesno(
                        'OpenVPN',
                        Script.localize(LABELS['An existing OpenVPN instance appears to be running.']),
                        Script.localize(LABELS['Disconnect it?'])):

                    Script.log('OpenVPN: User has decided to restart OpenVPN')
                    connect_openvpn(config, True, sudopassword)
                else:
                    Script.log(
                        'OpenVPN: User has decided not to restart OpenVPN')
            else:
                xbmcgui.Dialog().ok(
                    'OpenVPN',
                    Script.localize(LABELS['An error has occurred whilst trying to connect OpenVPN']))
                db['status'] = "failed"
        db.flush()


def import_ovpn():
    path = xbmcgui.Dialog().browse(
        1,
        Script.localize(LABELS['Import OpenVPN configuration file']),
        'files',
        mask='.ovpn|.conf',
        enableMultiple=False
    )

    if path and os.path.exists(path) and os.path.isfile(path):
        Script.log('OpenVPN: Import: [%s]' % path)

        keyboard = xbmc.Keyboard(
            default='',
            heading=Script.localize(LABELS['Choose a name for OpenVPN configuration']),
            hidden=False)
        keyboard.doModal()
        if keyboard.isConfirmed() and len(keyboard.getText()) > 0:
            name = keyboard.getText()

            ovpnfiles = {}
            with storage.PersistentDict('vpn') as db:
                ovpnfiles = db['ovpnfiles']
                db.flush()

            if name in ovpnfiles and not xbmcgui.Dialog().yesno(
                    'OpenVPN',
                    Script.localize(LABELS['This OpenVPN configuration name already exists. Overwrite?'])):
                xbmcgui.Dialog().ok('OpenVPN', Script.localize(LABELS['Import cancelled']))

            else:
                ovpnfiles[name] = path
                with storage.PersistentDict('vpn') as db:
                    db['ovpnfiles'] = ovpnfiles
                    db.flush()
        else:
            xbmcgui.Dialog().ok(
                'OpenVPN',
                Script.localize(LABELS['Import failed. You must specify a name for the OpenVPN configuration']))


def select_ovpn():
    ovpnfiles = {}
    with storage.PersistentDict('vpn') as db:
        try:
            ovpnfiles = db['ovpnfiles']
        except KeyError:
            db['ovpnfiles'] = ovpnfiles
        db.flush()

    if len(ovpnfiles) == 0:
        return None

    else:
        response = vpnlib.is_running(ip, port)
        Script.log('OpenVPN: Response from is_running: [%s] [%s] [%s]' % (
            response[0], response[1], response[2]))
        if response[0]:
            # Le VPN est connecté
            disconnect_openvpn()

        configs = []
        ovpnfileslist = []
        for name, configfilepath in ovpnfiles.iteritems():
            configs.append(name)
            ovpnfileslist.append(configfilepath)

        idx = xbmcgui.Dialog().select(
            Script.localize(LABELS['Select OpenVPN configuration to run']), configs)
        if idx >= 0:
            Script.log('OpenVPN: Select conf: [%s]' % ovpnfileslist[idx])
            return ovpnfileslist[idx]
        else:
            return ''


def delete_ovpn():
    ovpnfiles = {}
    with storage.PersistentDict('vpn') as db:
        try:
            ovpnfiles = db['ovpnfiles']
        except KeyError:
            db['ovpnfiles'] = ovpnfiles
        db.flush()

    if len(ovpnfiles) == 0:
        return None

    else:
        response = vpnlib.is_running(ip, port)
        Script.log('OpenVPN: Response from is_running: [%s] [%s] [%s]' % (
            response[0], response[1], response[2]))
        if response[0]:
            # Le VPN est connecté
            Script.log('OpenVPN: VPN still connected, we disconnect it')
            disconnect_openvpn()

        configs = []
        ovpnfileslist = []
        for name, configfilepath in ovpnfiles.iteritems():
            configs.append(name)
            ovpnfileslist.append(configfilepath)

        idx = xbmcgui.Dialog().select(
            Script.localize(LABELS['Select OpenVPN configuration to delete']), configs)
        if idx >= 0:
            Script.log('Select: [%s]' % ovpnfileslist[idx])
            new_ovpnfiles = {}
            for name, configfilepath in ovpnfiles.iteritems():
                if configfilepath != ovpnfileslist[idx]:
                    new_ovpnfiles[name] = configfilepath
            with storage.PersistentDict('vpn') as db:
                db['ovpnfiles'] = new_ovpnfiles
                db.flush()
        else:
            return ''


@Route.register
def vpn_item_callback(plugin):
    with storage.PersistentDict('vpn') as db:
        if 'status' not in db:
            db['status'] = "disconnected"

        elif db['status'] != "connected":
            ovpn = select_ovpn()
            if ovpn is None:
                import_ovpn()

            # Case when the user cancel the import dialog
            if ovpn is None:
                return False

            if len(ovpn) > 0:
                connect_openvpn(ovpn)

        elif db['status'] == "connected":
            disconnect_openvpn()
        db.flush()

        # xbmc.executebuiltin('XBMC.Container.Refresh()')
    return False
