#!/usr/bin/env python
# -*- coding:utf8 -*-

import os
import sys
import pickle
from optparse import OptionParser
from zlib import crc32
from mutagen.mp4 import MP4

MP4_EXTS = ['.m4a', '.m4p']
SPLIT_TAGS = [
    'sonm',  # 曲名
    'soal',  # アルバム
    'soar',  # アーティスト
    'soaa',  # アルバムアーティスト
    'soco',  # 作曲者
    'sosn',  # 番組
]

# options
DRY_RUN = False
VERBOSE = False


def main():
    usage  = "usage: %s [options] iTunes_library_path" % os.path.basename(__file__)
    p = OptionParser(usage=usage)
    p.add_option("-o", default='./phonetics.dump', metavar='FILE', help='Place dumped data into FILE (default: ./phonetics.dump)')
    p.add_option("-r", metavar='FILE', help='Revert iTunes library with this dumped FILE')
    p.add_option("-n", "--dry-run", action='store_true', help="Don't actually do anyting")
    p.add_option("-v", "--verbose", action='store_true', help='Run verbosely')
    opts, args = p.parse_args()
    if not args:
        p.print_help()
        sys.exit()
    target_path = args[0]
    if not os.path.isdir(target_path):
        die("%s is not a directory." % target_path)
    if opts.dry_run:
        global DRY_RUN
        DRY_RUN = True
    if opts.verbose:
        global VERBOSE
        VERBOSE = True
    if opts.r:
        # revert
        dumped_data = pickle.load(open(opts.r))
        revert(target_path, dumped_data)
        sys.exit()
    if not DRY_RUN:
        f = open(opts.o, 'w')  # check writeable first
    dumpdata = split(target_path)
    if not DRY_RUN:
        pickle.dump(dumpdata, f)
        f.close()
    print "splited phonetic-data from %s files" % len(dumpdata)
    print "this data is stored in %s" % opts.o
    print "use -r %s to revert these changes." % opts.o


def split(dir):
    pwd = os.getcwd()
    os.chdir(dir)
    deleted = []
    for root, dirs, files in os.walk('.'):
        for filename in files:
            basename, ext = os.path.splitext(filename)
            if ext in MP4_EXTS:
                file = os.path.join(root, filename)
                try:
                    tags = split_tags(file)
                except:
                    tags = {}
                if (tags):
                    # store file's metadata
                    deleted.append({
                        'file': file,
                        'crc32': get_crc32(file),
                        'tags': tags
                    })
    os.chdir(pwd)  # back to old working dir
    return deleted


def split_tags(file):
    mp4 = MP4(file)
    deleted = {}
    for key in SPLIT_TAGS:
        if key in mp4:
            deleted[key] = mp4.pop(key)
            _out('%s: tags [%s] deleted' % (file, key))
    if (deleted):
        if not DRY_RUN:
            mp4.save()
    return deleted


def revert(dir, dumped_data):
    pwd = os.getcwd()
    os.chdir(dir)
    deleted = []
    for d in dumped_data:
        if os.path.isfile(d['file']):
            #check crc
            crc = get_crc32(d['file'])
            if crc == d['crc32']:
                revert_tags(d['file'], d['tags'])
            else:
                print "%s has unmatched CRC. skipping..." % d['file']
        else:
            print "could not find file: %s" % d['file']

    os.chdir(pwd)  # back to old working dir


def revert_tags(file, tags):
    mp4 = MP4(file)
    for key, value in tags.items():
        mp4[key] = value
        _out('%s: tags [%s] reverted' % (file, key))
    if not DRY_RUN:
        mp4.save()


def get_crc32(file):
    return crc32(open(file).read())


def _out(msg):
    if VERBOSE:
        print msg


def die(msg):
    print msg
    sys.exit(1)


if __name__ == '__main__':
    main()

