#!/usr/bin/env python
# -*- coding: utf-8 --
#

import os
import time
import socket
import pickle
import base64
import subprocess
import SocketServer
from optparse import OptionParser
from threading import Timer

DEFAULT_PORT = 39763
POLL_INTERVAL = 5  # seconds
TIMEOUT = 5  #seconds


if os.name == 'nt':
    PLAYER = r"C:\Program Files\VlieoLAN\VLC\VLC.exe --quiet"  # windows
else:
    PLAYER = "/Applications/VLC.app/Contents/MacOS/VLC --quiet --open"


def open_player(client, ip, port):
    stream = 'udp://@:%s' % port
    cmd = '%s %s' % (PLAYER, stream)
    print cmd
    p = subprocess.Popen(cmd.split())
    def _check():
        if p.poll() is None:
            Timer(POLL_INTERVAL, _check).start()
        else:
            print "detected player's process terminated: status %s" % p.returncode
            client.stop()
    _check()

def main():
    usage = 'usage: %s [options]' % os.path.basename(__file__)
    p = OptionParser(usage = usage)
    p.add_option('-a', '--address', metavar='ADDR', default='localhost', help='server address to connect default: localhost')
    p.add_option('-p', '--port', metavar='PORT', default=DEFAULT_PORT, type="int", help='port number to connect. default: %d' % DEFAULT_PORT)
    opts, args = p.parse_args()

    client = NetworkTVClient()
    client.connect((opts.address, opts.port))
    try:
        main_loop(client)
    except Exception, e:
        print e
    client.close()

def main_loop(client):
    p = Prompt(client)
    player = None
    while True:
        p.print_menu()
        method = p.menu_input('input number what you want to do')
        if method in ['start', 'change']:
            p.print_list()
            ch = p.ch_input()
        if method == 'exit':
            break
        elif method == 'start':
            ip, port = client.start(ch)
            time.sleep(2)  # FIXME
            if client.available():
                open_player(client, ip, port)
            else:
                print 'could not open tuner'
        elif method == 'change':
            client.change(ch)
        elif method == 'stop':
            client.stop()
        elif method == 'list':
            p.print_list()
            print '\n',

class Prompt(object):

    def __init__(self, client):
        self.client = client

    def print_list(self):
        data = self.client.list()
        current_ch = self.client.current_ch
        for name, chs in data['data'].items():
            if chs:
                print '%s:' % name
            for ch_num, station_name in chs:
                if current_ch == ch_num:
                    print '> %s: %s' % (ch_num, station_name)
                else:
                    print '  %s: %s' % (ch_num, station_name)

    def print_menu(self):
        for i, element in enumerate(self.client.menu()):
            print i+1, element.title()
        print 0, 'Exit'

    def menu_input(self, desc):
        try:
            s = raw_input('%s > ' % desc)
            num = int(s.strip())
            if num == 0:
                return 'exit'
            menu = self.client.menu()
            selected = menu[num-1]
            return selected
        except StandardError, e:
            print e
            return self.menu_input(desc)

    def ch_input(self):
        try:
            ch = raw_input('channel? > ').strip()
            data = self.client.list()
            for name, chs in data['data'].items():
                for ch_num, station_name in chs:
                    if ch == ch_num:
                        return ch
            return self.ch_input()
        except StandardError, e:
            return self.ch_input()



STATE_NOCONNECT = -1
STATE_READY = 0
STATE_STARTED = 1

class NetworkTVClient(object):
    sessid = None
    state = STATE_NOCONNECT
    current_ch = ''

    def __init__(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(TIMEOUT)
        self.sock = sock

    def connect(self, host):
        self.sock.connect(host)
        self.state = STATE_READY

    def close(self):
        self._send('bye')
        self.sock.close()

    def list(self):
        self._send('list')
        return self._receive()

    def start(self, ch):
        self._send('start %s' % ch)
        data = self._receive()
        if not data:
            return None
        self.sessid = data['id']
        self.state = STATE_STARTED
        self.current_ch = ch
        return (data['ip'], data['port'])

    def change(self, ch):
        self._send('change %s %s' % (ch, self.sessid))
        data = self._receive()
        if not data:
            return False
        self.current_ch = ch
        return True

    def stop(self):
        self._send('stop %s' % self.sessid)
        data = self._receive()
        if not data:
            return False
        self.state = STATE_READY
        self.current_ch = ''
        return True

    def available(self):
        if self.state == STATE_STARTED:
            self._send('available %s' % self.sessid)
            r = self._receive()
            if r['available']:
                return True
        return False

    def menu(self):
        state = self.state
        menu = []
        if state == STATE_NOCONNECT:
            menu.append('connect')
        elif state == STATE_READY:
            menu.append('list')
            menu.append('start')
        elif state == STATE_STARTED:
            menu.append('list')
            menu.append('change')
            menu.append('stop')
        return menu

    def _send(self, s):
        self.sock.send('%s\r\n' % s)

    def _receive(self, sf=None):
        if sf is None:
            sf = self.sock.makefile()
        raw = sf.readline()
        data = pickle.loads(base64.b64decode(raw))
        if 'status' not in data:
            return None
        if data['status'] > 0:
            print data['error']
            return None
        return data


if __name__ == '__main__':
    main()

