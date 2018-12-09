#!/usr/bin/env python
"""
author: paiv, https://github.com/paiv/
"""

import csv
import json
import os


def export_from(datadir, tofile):
    data = []
    for (root,dirs,files) in os.walk(datadir):
        for fn in [os.path.join(root,x) for x in files if x == 'entry.json']:
            with open(fn, 'r') as fd:
                entry = json.load(fd)
                data.append(entry)

    data = sorted(data, key=lambda x: int(x['refid']))

    writer = csv.DictWriter(tofile, ['id','name','section','provisional','country','url','image','pdf'])
    writer.writeheader()

    for entry in data:
        # for n in ['name', 'section', 'country']:
        #   entry[n] = unicode(entry[n]).encode('utf-8')
        entry['id'] = entry['refid']
        entry.pop('refid')
        entry['image'] = None
        if 'thumb' in entry:
            entry['image'] = entry['thumb']
            entry.pop('thumb')

        writer.writerow(entry)


if __name__ == '__main__':
    import argparse
    import sys

    parser = argparse.ArgumentParser()
    parser.add_argument('--data-dir', default='data', help='Data directory')
    parser.add_argument('outfile', nargs='?', default=sys.stdout, type=argparse.FileType('w'))
    args = parser.parse_args()

    export_from(args.data_dir, args.outfile)
