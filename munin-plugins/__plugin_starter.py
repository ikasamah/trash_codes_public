#!/usr/bin/env python
# -*- encoding: utf-8 -*-

import os
import sys

def main():
    # to get values set in plugin-conf.d
    # var = os.environ['key']
    if len(sys.argv) < 2:
        print_plugin_values()
    elif sys.argv[1] == "config":
        print_config()
    elif sys.argv[1] == "autoconf":
        print_autoconf()
    sys.exit()

def print_plugin_values():
    print 'current.value 100'
    print 'total.value 100'

def print_config() :
    print 'graph_category MyPlugin'
    print 'graph_title MyPlugin1'
    print 'graph_vlabel byte'
    #print 'graph_args --base 1024 -l'
    print 'graph_info MyPlugin - description here'
    print 'current.label current value'
    print 'total.label total value'
    #print 'total.draw LINE2'

def print_autoconf():
    print 'yes'


if __name__ == '__main__':
    main()

