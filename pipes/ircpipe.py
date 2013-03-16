#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright © 2011-2013 Binet Réseau
# See the LICENCE file for more informations

# This file is a part of Kaoz, a free irc notifier

import optparse
import os
import re
import shlex
import socket
import sys

try:
    import ssl
    has_ssl = True
except ImportError:
    has_ssl = False


#   Need review: which solution ?
CLIENTS_PATH = os.environ.get('KAOZ_CLIENTS_PATH', '/usr/share/kaoz-clients')
CLIENTS_PATH = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CONFIG_FILE = os.path.join(CLIENTS_PATH, 'config.sh')
STYLE_FILE = os.path.join(CLIENTS_PATH, 'irc-style.sh')


class OptionError(BaseException):
    def __str__(self):
        return "No {} was specified and a fallback value was not found in {}".format(self.args[0], CONFIG_FILE)


class ConfigParser(dict):
    """Parse bash scripts to extract variables"""
    VARIABLE = re.compile(r'(?P<replace>\$(\{)?(?P<name>[a-zA-Z0-9_-]+)(?(2)\}|))')
    UNICODE_CHAR = re.compile(r'(?P<replace>\\x(?P<char>[0-9a-f]{2}))', re.I)
    def __init__(self, path):
        with open(path, 'r') as f:
            lexer = shlex.shlex(f.read())
        lexer.wordchars += '.'
        lexer.source = 'source'
            # some shlex magic: the config file can contain 'source other.sh'
            # and 'other.sh' will be parsed.

        tokens = list(lexer)
        for i in [i for i,t in enumerate(tokens) if t == '=']:
            val = tokens[i+1]
            if val == '$' and i+2 < len(tokens):
                val = tokens[i+2]
            val = val.strip().strip('\'').strip('"')
            val = self.replace_variables(val)
            val = self.replace_unicode(val)
            self[tokens[i-1]] = val

    def replace_variables(self, s, missing_value=''):
        ret = s
        for match in ConfigParser.VARIABLE.finditer(s):
            d = match.groupdict()
            if d['name'] in self or missing_value is not None:
                ret = ret.replace(d['replace'], self.get(d['name'], missing_value))
        return ret

    @staticmethod
    def replace_unicode(s):
        ret = s
        for match in ConfigParser.UNICODE_CHAR.finditer(s):
            d = match.groupdict()
            ret = ret.replace(d['replace'], chr(int(d['char'], 16)))
        return ret


class IrcPipe:
    """Kaoz client"""
    def __init__(self, hostname=None, port=None, channel=None, password=None, use_ssl=None, ssl_cert=None):
        self.config = ConfigParser(CONFIG_FILE)

        if hostname is None:
            hostname = self.config.get('LISTENER_HOST', 'localhost')
        if port is None:
            port = self.config.get('LISTENER_PORT', 9010)
        if password is None:
            password = self.config.get('LISTENER_PASSWORD', None)
        if use_ssl is None:
            use_ssl = self.config.get('LISTENER_SSL', False) == 'true'
        if ssl_cert is None:
            ssl_cert = self.config.get('LISTENER_CRT', None)

        if not password:
            raise OptionError('password')

        self._password = password
        self._sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.host = (hostname,int(port))
        self.use_ssl = use_ssl
        self.ssl_cert = ssl_cert

    def __enter__(self):
        self._sock.connect(self.host)
        if self.use_ssl:
            assert has_ssl, "SSL support requested but not available"
            try:
                if self.ssl_cert is None:
                    self._sock = ssl.wrap_socket(self._sock)
                else:
                    self._sock = ssl.wrap_socket(self._sock,
                                                 cert_reqs=ssl.CERT_REQUIRED,
                                                 ca_certs=self.ssl_cert)
            except ssl.SSLError as e:
                sys.stderr.write('SSL error: is python-openssl correctly installed ?\n')
                raise e
        return self

    def __exit__(self, type, value, traceback):
        self._sock.close()

    def send_line(self, line, channel=None):
        if channel is None:
            try:
                channel = self.config['DEFAULT_CHANNEL']
            except KeyError:
                raise OptionError('channel')
        self._sock.sendall('{}:{}:({}) {}'.format(self._password, channel, socket.gethostname(), line).encode())


def ircstyle(path=STYLE_FILE):
    return ConfigParser(path)


def main():
    parser = optparse.OptionParser(
        usage="Usage: %prog [#channel] [options]\nOptions can also be read from {}".format(CONFIG_FILE))
    parser.add_option('-H', '--hostname', dest='hostname',
        help="Server hostname", default=None)
    parser.add_option('-P', '--port', dest='port',
        help="Server port", default=None)
    parser.add_option('-p', '--password', dest='password',
        help="Server password", default=None)
    parser.add_option('-s', '--ssl', action='store_true', dest='use_ssl',
        help="Use SSL", default=None)
    parser.add_option('-c', '--cert', dest='ssl_cert',
        help="SSL certificate or CA", default=None)
    parser.add_option('-m', '--message', dest='message',
        help="Read message from command line instead of standard input", default=None)

    opts, args = parser.parse_args()
    if len(args) > 1:
        parser.error("Invalid number of arguments: {} > 1".format(len(args)))

    channel = args[0] if len(args) == 1 else None

    try:
        with IrcPipe(opts.hostname, opts.port, opts.password, opts.use_ssl, opts.ssl_cert) as client:
            if opts.message:
                client.send_line(opts.message, channel)
            else:
                for line in sys.stdin:
                    client.send_line(line, channel)
    except OptionError as e:
        parser.error(str(e))


if __name__ == '__main__':
    main()
