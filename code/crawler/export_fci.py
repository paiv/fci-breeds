#!/usr/bin/env python
"""
author: paiv, https://github.com/paiv/
"""

import csv
import json
from pathlib import Path


def export_from(datadir, tofile):
    data = []
    for fn in Path(datadir).glob('**/entry.json'):
        with open(fn, 'r') as fp:
            entry = json.load(fp)
            data.append(entry)

    data = sorted(data, key=lambda x: int(x['refid']))

    writer = csv.DictWriter(tofile, ['id','name','group','section','provisional','country','url','image','pdf'])
    writer.writeheader()

    for entry in data:
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
