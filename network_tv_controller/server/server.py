#!/usr/bin/env python
# -*- coding: utf-8 -*-
#

# require: python 2.6

import os
import pickle
import base64
import uuid
import subprocess
import SocketServer
from ConfigParser import SafeConfigParser
from optparse import OptionParser

DEFAULT_PORT = 39763

def main():
    usage = 'usage: %s [options]' % os.path.basename(__file__)
    p = OptionParser(usage = usage)
    p.add_option('-c', '--config', metavar='FILE', help='specify config file to control pt1. default: %s' % PT1Controller.config_file)
    p.add_option('-p', '--port', metavar='PORT', default=DEFAULT_PORT, type="int", help='set the port number to listen. default: %d' % DEFAULT_PORT)
    opts, args = p.parse_args()
    if opts.config:
        PT1Controller.config_file = opts.config
    SocketServer.ForkingTCPServer.allow_reuse_address = True
    server = SocketServer.ForkingTCPServer(('', opts.port), TVControlHandler)
    server.serve_forever()


class TVControlHandler(SocketServer.StreamRequestHandler):

    def setup(self):
        SocketServer.StreamRequestHandler.setup(self)
        self.tv = PT1Controller()

    def finish(self):
        self.tv.cleanup()
        SocketServer.StreamRequestHandler.finish(self)

    def _output(self, o):
        serialized = pickle.dumps(o)
        self.wfile.write('%s\n' % base64.b64encode(serialized))

    def handle(self):
        while True:
            cmd = self.rfile.readline().strip()
            if not cmd:
                continue
            print cmd
            args = cmd.split()
            control = args.pop(0)
            method = 'tv_%s' % control
            if hasattr(self, method):
                try:
                    result = apply(getattr(self, method), args)
                    self._output(result)
                except StandardError, e:
                    self._output({'status': 2, 'error': e})
            elif control == 'bye':
                break
            else:
                pass  # TODO: help message

    def tv_list(self):
        return self.tv.channel_list()

    def tv_start(self, channel=None):
        return self.tv.start(self.client_address[0], channel)

    def tv_available(self, id):
        return self.tv.available(id)

    def tv_stop(self, id):
        return self.tv.stop(id)

    def tv_change(self, channel, id):
        return self.tv.change_channel(id, channel)


class PT1Controller(object):

    config_file = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'pt1conf.ini')

    def __init__(self):
        self.config = SafeConfigParser()
        self.config.read(self.config_file)
        _port_available = {}
        port_range = map(int, self.config.get('recpt1', 'port_range').split('-'))
        if len(port_range) < 2:
            _port_available[port_range[0]] = True
        else:
            for p in range(port_range[0], port_range[1] + 1):
                _port_available[p] = True
        self._port_available = _port_available
        self.sessions = {}

    def start(self, ip, ch=None):
        try:
            if ch is None:
                ch = self._default_channel()
            recpt1 = self.config.get('recpt1', 'recpt1')
            opts_temp = self.config.get('recpt1', 'recpt1_opts')
            port = self._rent_port()
            opts = opts_temp % (ip, port, ch)
            cmd =  '%s %s' % (recpt1, opts)
            p = subprocess.Popen(cmd.split(), shell=False, stdout=subprocess.PIPE)
            id = uuid.uuid4().hex
            self.sessions[id] = (p, ip, port)
            return {'status': 0, 'id': id, 'ip': ip, 'port': port}
        except StandardError, e:
            return {'status': 1, 'error': e}

    def stop(self, id):
        try:
            p, ip, port = self.sessions[id]
            p.kill()
            p.wait()  # resolve <defunct>
            self._return_port(port)
            return {'status': 0}
        except StandardError, e:
            return {'status': 1, 'error': e}

    def available(self, id):
        try:
            p, ip, port = self.sessions[id]
            r = False
            if p.returncode is None:
                r = True
            return {'status': 0, 'available': r}
        except StandardError, e:
            return {'status': 1, 'error': e}

    def change_channel(self, id, ch):
        try:
            recpt1ctl = self.config.get('recpt1', 'recpt1ctl')
            opts_temp = self.config.get('recpt1', 'change_ch_opts')
            p, ip, port = self.sessions[id]
            opts = opts_temp % (p.pid, ch)
            cmd =  '%s %s' % (recpt1ctl, opts)
            p = subprocess.Popen(cmd.split(), shell=False, stdout=subprocess.PIPE)
            return {'status': 0}
        except StandardError, e:
            return {'status': 1, 'error': e}

    def restart(self):
        """not implemented"""
        pass

    def channel_list(self):
        """channel list"""
        try:
            r = {}
            for section in self._ch_sections():
                r[section] = []
                for item in self.config.items(section):
                    r[section].append(item)
            return {'status': 0, 'data': r}
        except StandardError, e:
            return {'status': 1, 'error': e}

    def cleanup(self):
        for sessid in self.sessions:
            self.stop(sessid)

    def _rent_port(self):
        for port, available in self._port_available.items():
            if available:
                self._port_available[port] = False
                return port
        raise PT1ControllerError('no port available')

    def _return_port(self, port):
        if port in self._port_available:
            self._port_available[port] = True

    def _ch_sections(self):
        f = lambda s: s[-3:] == '_ch'
        return filter(f, self.config.sections())

    def _default_channel(self):
        for section in self._ch_sections():
            for ch, name in self.config.items(section):
                return ch

class PT1ControllerError(Exception):
    pass

if __name__ == '__main__':
    main()

