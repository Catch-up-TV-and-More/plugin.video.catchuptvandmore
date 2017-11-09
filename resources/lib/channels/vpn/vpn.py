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
from resources.lib import openvpn as vpn

# Initialize GNU gettext emulation in addon
# This allows to use UI strings from addon’s English
# strings.po file instead of numeric codes
_ = common.ADDON.initialize_gettext()

# 'enum' of connection states
(disconnected, failed, connecting, disconnecting, connected) = range(5)
_state = disconnected

def channel_entry(params):
    """Entry function of the module"""
    if 'root' in params.next:
        return root(params)
    return None


def which(program, path_var):
    def is_exe(fpath):
        return os.path.isfile(fpath) and os.access(fpath, os.X_OK)

    fpath, fname = os.path.split(program)
    if fpath:
        if is_exe(program):
            return program
    else:
        for path in path_var.split(os.pathsep):
            path = path.strip('"')
            exe_file = os.path.join(path, program)
            if is_exe(exe_file):
                return exe_file

    return None


def root(params):
    print "Je suis dans le root vpn"

    openvpn_folderpath = common.PLUGIN.get_setting('openvpn_folderpath')
    path = os.environ['PATH']
    if openvpn_folderpath is not "":
        path = common.PLUGIN.get_setting('openvpn_folderpath')

    # tempo
    path = "/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin:/usr/local/MacGPG2/bin:/Library/TeX/texbin:/Applications/Wireshark.app/Contents/MacOS"

    openvpn_filepath = which("openvpn", path)

    openvpn_config_filepath = common.PLUGIN.get_setting('openvpn_config_filepath')
    if openvpn_config_filepath is "":
        common.sp.xbmcgui.Dialog().ok(
            _('Information'),
            _('Specify OpenVPN config file in addon settings'))
        return

    global _state

    openvpn = vpn.OpenVPN(
        openvpn_filepath,
        openvpn_config_filepath,
        args=None,
        sudo=False,
        sudopwd=None,
        debug=True
    )

    try:
        openvpn.connect()
        print "Try to connect"
        _state = connected
    except vpn.OpenVPNError as exception:
        print "loupé %s" % exception




