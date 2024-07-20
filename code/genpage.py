#!/usr/bin/env python
import csv
import sys
from datetime import datetime, UTC
from pathlib import Path
from urllib.parse import urlparse


def gen_id(row, name='id'):
    code = row.get(name)
    if (link := row.get('url')):
        return f'<div><a href="{link}">{code}</a></div>'
    return f'<div>{code}</div>'


def gen_link(row, name='url'):
    if (link := row.get(name)):
        url = urlparse(link)
        fn = Path(url.path).name
        return f'<div><a href="{link}">{fn}</a></div>'
    return '<div></div>'


def gen_(row, name):
    value = row.get(name, '')
    return f'<div>{value}</div>'


def main(args):
    filename = args.file if (args.file is not None) else '-'
    if filename == '-':
        fin = sys.stdin
    else:
        fin = Path(filename).open('r')

    reader = csv.DictReader(fin)

    fileto = args.output if (args.output is not None) else '-'
    if fileto == '-':
        fout = sys.stdout
    else:
        fout = Path(fileto).open('w')

    ts = datetime.now(UTC)
    timestamp = ts.isoformat()

    gens = dict(id=gen_id, url=gen_link, image=gen_link, pdf=gen_link)
    
    fieldnames = list(reader.fieldnames)
    nf = len(fieldnames)
    cssgc = f'repeat({nf}, 1fr)'

    print(f'''<!DOCTYPE html>
<html>
<head>
  <meta charset="utf8">
  <meta name="viewport" content="width:device-width, initial-scale=1">
  <title>FCI Breeds</title>
<style>
:root {{ color-scheme: light dark; }}
.table {{
  display: grid;
  gap: 0.1rem 1rem;
  grid-template-columns: {cssgc};
  white-space: nowrap;
}}
.table .th {{
  font-weight: bolder;
  text-align: center;
}}
.table > div {{
  border-right: 1px solid #ccc;
  padding-right: 0.5rem;
}}
</style>
</head>
<body>
<div class="info">
<h1>FCI Breeds</h1>
<p><a href="https://ukrainewar.carrd.co/"><img src="StandWithUkraine.svg" alt="standwithukraine"></a></p>
<p>Data compiled from <a href="https://www.fci.be/en/nomenclature/">https://www.fci.be/en/nomenclature/</a>.</p>
<p>Generated at {timestamp}</p>
<p>Download: <a href="https://github.com/paiv/fci-breeds/releases/latest/download/fci-breeds.csv.tar.gz">CSV</a></p>
</div>
<div class="table">''', file=fout)

    for k in fieldnames:
        print(f'<div class="th">{k}</div>', file=fout)

    for row in reader:
        for k in fieldnames:
            gen = gens.get(k, gen_)
            val = gen(row, k)
            print(val, file=fout)

    print(f'''</div>
</body>
</html>''', file=fout)


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description='HTML page generator for the fci-breeds.csv')
    parser.add_argument('file', nargs='?', default='fci-breeds.csv', help='the CSV file to process, default is fci-breeds.csv')
    parser.add_argument('-o', '--output', help='destination file name')
    args = parser.parse_args()
    main(args)
