#!/usr/bin/env python
#coding: utf-8

import datetime, imp, ipaddress, os, re
from pyinotify import WatchManager, Notifier, ThreadedNotifier, EventsCodes, ProcessEvent

CLIENTS_PATH = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ircpipe = imp.load_source('ircpipe', os.path.join(CLIENTS_PATH, 'pipes', 'ircpipe.py'))
IRC_STYLE = ircpipe.ircstyle()


WATCH_DIR = '/var/log/httpd/'
CHANNEL = r'#monit-http' # '' for default channel defined in ircpipe

# LogFormat "%h %l %u %t \"%r\" %>s %b \"%{Referer}i\" \"%{User-Agent}i\"" combined
# 10.0.0.2 - - [24/Feb/2013:22:58:31 +0100] "GET /api/xx/static/images/icon.edit.png HTTP/1.1" 304 - "https://my.tld/" "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.17 (KHTML, like Gecko) Chrome/24.0.1312.70 Safari/537.17"
ACCESS_LINE = re.compile(r'^(?P<ip>[:.0-9a-f]+) - (?P<user>[a-z]+|-) (?P<date>\[[0-9a-zA-Z /:+]+\]) "(?P<request>.*)" (?P<resp>[0-9]{3}) (?P<size>[0-9]+|-) "(?P<referer>.*)" "(?P<useragent>.*)"$')
# [Wed Feb 20 21:53:14 2013] [warn] Init: Name-based SSL virtual hosts only work for clients with TLS server name indication support (RFC 4366)
ERROR_LINE = re.compile(r'^\[(?P<date>[0-9a-zA-Z :]+)\] \[(?P<level>[a-z]+)\](?: \[client (?P<ip>[0-9:.a-f]+)\])? (?P<msg>.*)$')

WATCHED_VHOSTS = [] # empty for wildcard
EXCEPT_USERAGENTS = []
EXCEPT_404 = ['/robots.txt', '/favicon.ico']
EXCEPT_NETWORKS = ['10.0.0.0/8', '127.0.0.0/8']

class ParseError(BaseException):
    def __str__(self):
        return '{IRC_AQUA}Parse error{IRC_O}'.format(**IRC_STYLE)

def truncate(s, length=30):
    return (s[:length] + u'…') if len(s)>length else s

current_clients = {}
SPAM_RATE = datetime.timedelta(seconds=60)
def parse_access(vhost, line):
    if len(WATCHED_VHOSTS) > 0 and vhost not in WATCHED_VHOSTS:
        return None

    data = ACCESS_LINE.match(line)
    if data is None:
        raise ParseError
    data = data.groupdict()

    if data['useragent'] in EXCEPT_USERAGENTS:
        return None
    for net in EXCEPT_NETWORKS:
        if ipaddress.ip_address(data['ip']) in ipaddress.ip_network(net):
            return None

    resp = int(data['resp'])
    resp_col = '09' if resp < 400 else ('08' if resp < 500 else '04')

    file = ' '.join(data['request'].split(' ')[1:-1])
    if resp == 404 and file in EXCEPT_404:
        return None

    now = datetime.datetime.now()
    if data['ip'] in current_clients and now-current_clients[data['ip']] < SPAM_RATE and resp < 400:
        return None
    current_clients[data['ip']] = now

    user = '{IRC_OLIVE}{} '.format(data['user'], **IRC_STYLE) if data['user'] != '-' else ''

    return '{}{IRC_K}{}{} {IRC_LIGHTGRAY}{}{IRC_O} {} ; {}'.format(user, resp_col, resp, data['ip'], truncate(data['request']), truncate(data['useragent']), **IRC_STYLE)

def parse_error(vhost, line):
    data = ERROR_LINE.match(line)
    if data is None:
        raise ParseError
    data = data.groupdict()
    if 'File does not exist' in data['msg']:
        for s in EXCEPT_404:
            if data['msg'].endswith(s):
                return None
    return '({IRC_RED}{}{IRC_O}) {IRC_LIGHTGRAY}{}{IRC_O}{}'.format(data['level'], data['ip']+' ' if data['ip'] else '', data['msg'], **IRC_STYLE)

def process_change(path):
    with open(path, 'r') as f:
        line = f.readlines()[-1][:-1]
    vhost,type = path.rsplit('/', 1)[1].split('_',1)
    type = type.rsplit('.',1)[0]
    try:
        f = parse_error if type == 'error' else parse_access
        line = f(vhost, line)
    except ParseError as e:
        line = '{}: {}'.format(str(e), repr(line))
    if line is not None:
        msg = '{IRC_PURPLE}[httpd]{IRC_O} ({IRC_NAVY}{}{IRC_O}) {}'.format(vhost, line, **IRC_STYLE).replace('\\', '\\\\').replace('"', '\\"')
        with ircpipe.IrcPipe() as pipe:
            pipe.send_line(msg, CHANNEL)



class PTmp(ProcessEvent):
    def process_IN_MODIFY(self, event):
        process_change(os.path.join(event.path, event.name))

wm = WatchManager()
notifier = Notifier(wm, PTmp())
wm.add_watch(WATCH_DIR, EventsCodes.OP_FLAGS['IN_MODIFY'], rec=True)
try:
    while True:
        notifier.process_events()
        if notifier.check_events():
            notifier.read_events()
except KeyboardInterrupt:
    notifier.stop()
