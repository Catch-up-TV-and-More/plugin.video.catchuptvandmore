# -*- coding: utf-8 -*-
# Copyright: (c) 2020, SylvainCecchetto, wwark
# GNU General Public License v2.0+ (see LICENSE.txt or https://www.gnu.org/licenses/gpl-2.0.txt)

# This file is part of Catch-up TV & More
import re
import requests
import sys
import ssl
import xbmcvfs
import pickle

from kodi_six import xbmc, xbmcaddon

try:  # Python 3
    from http.server import BaseHTTPRequestHandler
except ImportError:  # Python 2
    from BaseHTTPServer import BaseHTTPRequestHandler

try:  # Python 3
    from socketserver import TCPServer
except ImportError:  # Python 2
    from SocketServer import TCPServer

addon = xbmcaddon.Addon(id='plugin.video.catchuptvandmore')

requests.packages.urllib3.disable_warnings()
requests.packages.urllib3.util.ssl_.DEFAULT_CIPHERS += ':HIGH:!DH:!aNULL'

try:
    _create_unverified_https_context = ssl._create_unverified_context
except AttributeError:
    pass
else:
    ssl._create_default_https_context = _create_unverified_https_context

PY3 = sys.version_info >= (3, 0, 0)


class SimpleHTTPRequestHandler(BaseHTTPRequestHandler):

    def do_POST(self):
        """Handle http post requests, used for license"""
        path = self.path  # Path with parameters received from request e.g. "/license?id=234324"
        fPath = xbmcvfs.translatePath("special://userdata/addon_data/plugin.video.catchuptvandmore/headersCanal")

        if '/license' not in path:
            self.send_response(404)
            self.end_headers()
            return

        length = int(self.headers.get('content-length', 0))
        isa_data = self.rfile.read(length).decode('utf-8').split('!')
        challenge = isa_data[0]
        if 'cense=' in path:
            path2 = path.split('cense=')[-1]

            with open(fPath, 'rb') as f1:
                ab = pickle.load(f1)

            result = requests.post(url=path2, headers=ab, data=challenge, verify=False).text

            licens = re.findall('ontentid=".+?">(.+?)<', result)[0]
            if PY3:
                licens = licens.encode(encoding='utf-8', errors='strict')

        self.send_response(200)
        self.end_headers()
        self.wfile.write(licens)


address = '127.0.0.1'  # Localhost

port = 5057

server_inst = TCPServer((address, port), SimpleHTTPRequestHandler)
# The follow line is only for test purpose, you have to implement a way to stop the http service!
server_inst.serve_forever()


def autorun_addon():
    if xbmcaddon.Addon().getSetting("auto_run") == "true":
        xbmc.executebuiltin('RunAddon(plugin.video.catchuptvandmore)')
    return


autorun_addon()
