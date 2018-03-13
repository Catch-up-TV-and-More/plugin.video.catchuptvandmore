# /*
# *
# * OpenVPN for Kodi.
# *
# * Copyright (C) 2015 Brian Hornsby
# *
# * This program is free software: you can redistribute it and/or modify
# * it under the terms of the GNU General Public License as published by
# * the Free Software Foundation, either version 3 of the License, or
# * (at your option) any later version.
# *
# * This program is distributed in the hope that it will be useful,
# * but WITHOUT ANY WARRANTY; without even the implied warranty of
# * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# * GNU General Public License for more details.
# *
# * You should have received a copy of the GNU General Public License
# * along with this program.  If not, see <http://www.gnu.org/licenses/>.
# *
# */


import os
import subprocess
import time
import socket


class OpenVPNManagementInterface:

    def __init__(self, ip, port, openvpn=None):
        self.openvpn = openvpn
        self.ip = ip
        self.port = port
        #self.openvpn._log_debug('OpenVPNManagementInterface: IP: [%s]' % ip)
        #self.openvpn._log_debug(
        #    'OpenVPNManagementInterface: Port: [%s]' % port)
        self.buf = ''
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def connect(self):
        self.sock.connect((self.ip, self.port))

    def disconnect(self):
        self.sock.close()

    def send(self, msg):
        #self.openvpn._log_debug('Sending: [%s]' % msg)
        sent = self.sock.send(msg)
        #self.openvpn._log_debug('Sent: [%d]' % sent)

    def receive(self):
        buf = ''
        data = ''
        while data != '\n':
            data = self.sock.recv(1)
            buf += data
        if len(buf) > 0:
            buf += '\n'
        return buf


def is_running(ip, port):
    interface = OpenVPNManagementInterface(ip, port)
    config = None
    state = None
    try:
        interface.connect()
        interface.send('pid\n')
        interface.send('state\n')
        if interface.receive().startswith('>INFO:'):
            data = interface.receive()
            if data.startswith('SUCCESS: pid='):
                pid = int(data.split('=')[1])
                cmdline = 'ps -fp %d' % pid
                ps = subprocess.Popen(cmdline, shell=True, stdout=subprocess.PIPE)
                cmdline = ps.stdout.read()
                ps.stdout.close()
                output = cmdline.split('--config')
                if len(output) > 1:
                    config = output[1].lstrip().split('--')[0].rstrip()
                else:
                    cmdline = 'ps | grep -w %d | grep -vw grep' % pid
                    ps = subprocess.Popen(cmdline, shell=True, stdout=subprocess.PIPE)
                    cmdline = ps.stdout.read()
                    ps.stdout.close()
                    output = cmdline.split('--config')
                    if len(output) > 1:
                        config = output[1].lstrip().split('--')[0].rstrip()

            data = interface.receive().split(',')
            if len(data) > 1:
                state = data[1]
    except socket.error as exception:
        return False, None, None
    return True, config, state


def disconnect(ip, port):
    interface = OpenVPNManagementInterface(ip, port)
    try:
        interface.connect()
        interface.send('signal SIGTERM\n')
        interface.disconnect()
    except socket.error as exception:
        raise OpenVPNError(3, 'Unable to disconnect OpenVPN')


class OpenVPNError(Exception):

    def __init__(self, errno, string):
        self.errno = errno
        self.string = string

    def __str__(self):
        return '[%d]: %s' % (self.errno, self.string)


class OpenVPN:

    def __init__(self, openvpn, ovpnconfig, ip='127.0.0.1', port=1337, sudo=False, sudopwd=None, args=None, timeout=1, debug=False):
        self.openvpn = openvpn
        self.ovpnconfig = ovpnconfig
        self.ip = ip
        self.port = int(port)
        self.args = args
        self.timeout = timeout
        self.sudo = sudo
        self.sudopwd = sudopwd
        self.debug = debug

        self._log_debug('OpenVPN: [%s]' % self.openvpn)
        self._log_debug('OpenVPN Configuration: [%s]' % self.ovpnconfig)
        self._log_debug('OpenVPN Management IP: [%s]' % self.ip)
        self._log_debug('OpenVPN Management Port: [%d]' % self.port)
        if self.args is not None:
            self._log_debug('Additional Arguments: [%s]' % self.args)

        if self.openvpn is None or not os.path.exists(self.openvpn) or not os.path.isfile(self.openvpn):
            self._log_error('OpenVPN: ERROR: Specified OpenVPN does not exist')

        if self.ovpnconfig is None or not os.path.exists(self.ovpnconfig) or not os.path.isfile(self.ovpnconfig):
            self._log_error(
                'OpenVPN: ERROR: Specified OpenVPN configuration file does not exist')

        self.interface = None
        self.workdir = os.path.dirname(ovpnconfig)
        self.logfile = os.path.join(self.workdir, 'openvpn.log')

    def _log_debug(self, msg):
        if self.debug:
            print 'OpenVPN: DEBUG: %s' % msg

    def _log_error(self, msg):
        print 'OpenVPN: ERROR: %s' % msg

    def connect_to_interface(self, logerror):
        if self.interface is None:
            self.interface = OpenVPNManagementInterface(self.ip, self.port, self)
        try:
            self.interface.connect()
        except socket.error as exception:
            if logerror:
                self._log_error(exception)
            else:
                self._log_debug(exception)
            self.interface = None
            return False
        return True

    def disconnect(self):
        self.connect_to_interface(False)
        self._log_debug('Disconnecting OpenVPN')
        self.interface.send('signal SIGTERM\n')
        time.sleep(self.timeout)
        self.interface.disconnect()
        self.interface = None
        self._log_debug('Disconnect OpenVPN successful')

    def connect(self):
        self._log_debug('Connecting OpenVPN')

        isrunning = self.connect_to_interface(False)
        if isrunning:
            self._log_debug('OpenVPN is already running')
            self.interface.disconnect()
            raise OpenVPNError(1, 'OpenVPN is already running')

        cmdline = '\'%s\' --cd \'%s\' --daemon --management %s %d --config \'%s\' --log \'%s\'' % (
            self.openvpn, self.workdir, self.ip, self.port, self.ovpnconfig, self.logfile)
        if self.args is not None:
            cmdline = '%s %s' % (cmdline, self.args)

        self._log_debug('Command line: [%s]' % cmdline)

        if self.sudo:
            self._log_debug('Using sudo')
            if self.sudopwd:
                cmdline = 'echo \'%s\' | sudo -S %s' % (self.sudopwd, cmdline)
            else:
                cmdline = 'sudo %s' % (cmdline)

        self.process = subprocess.Popen(cmdline, cwd=self.workdir, shell=True,
                                        stdout=subprocess.PIPE, stdin=subprocess.PIPE, stderr=subprocess.PIPE)
        time.sleep(self.timeout)
        if not self.connect_to_interface(True):
            self._log_debug('Connect OpenVPN failed')
            raise OpenVPNError(
                2, 'Unable to connect to OpenVPN management interface')

        self._log_debug('Connect OpenVPN successful')