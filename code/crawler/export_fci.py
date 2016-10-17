#!/usr/bin/env python
# author: paiv, https://github.com/paiv/

from __future__ import print_function
import csv
import json
import os
from io import open


def export_from(datadir, tofile='out.csv'):
  data = []
  for (root,dirs,files) in os.walk(datadir):
    for fn in [os.path.join(root,x) for x in files if x == 'entry.json']:
      with open(fn, 'r', encoding='utf-8') as fd:
        entry = json.load(fd)
        data.append(entry)

  data = sorted(data, lambda a,b: int(a['refid']) - int(b['refid']))

  with open(tofile, 'wb') as csvfile:
    writer = csv.DictWriter(csvfile, ['id','name','section','provisional','country','url','image','pdf'])
    writer.writeheader()

    for entry in data:
      for n in ['name', 'section', 'country']:
        entry[n] = unicode(entry[n]).encode('utf-8')
      entry['id'] = entry['refid']
      entry.pop('refid')
      entry['image'] = None
      if 'thumb' in entry:
        entry['image'] = entry['thumb']
        entry.pop('thumb')

      writer.writerow(entry)


if __name__ == '__main__':
  import sys

  if len(sys.argv) < 2:
    print('usage: export_fci.py <datadir> [out.csv]')
  else:
    datadir = sys.argv[1]
    tofile = sys.argv[2] if len(sys.argv) > 2 else 'out.csv'
    export_from(datadir, tofile)
