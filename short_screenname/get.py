#!/usr/bin/env python
# -*- coding:utf-8 -*-

# require python 2.6

import sys
import urllib2
import json
import time

API_URL = 'http://twitter.com/users/username_available?username='
VALID_CHARS = '0123456789abcdefghijklmnopqrstuvwxyz_'
INTERVAL = 0.2  # sec

def main():
    screen_name = VALID_CHARS[0]
    while True:
        result = available(screen_name)
        print "%s: %s" % (screen_name, result)
        if (result):
            break
        screen_name = increment_string(screen_name)
        time.sleep(INTERVAL)

def available(name):
    url = API_URL + name
    try:
        res = urllib2.urlopen(url).read()
        res = json.loads(res)
        return res['valid']
    except BaseException, e:
        print e
        if isinstance(e, KeyboardInterrupt):
            sys.exit()
        time.sleep(INTERVAL)
        available(name)

def increment_string(s):
    pos = VALID_CHARS.find(s[-1])
    if pos == len(VALID_CHARS) - 1:
        if len(s) == 1:
            return VALID_CHARS[0] * 2
        else:
            return increment_string(s[:-1]) + VALID_CHARS[0]
        pass
    else:
        return s[:-1] + VALID_CHARS[pos+1]


if __name__ == '__main__':
    main()

