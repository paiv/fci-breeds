#!/usr/bin/env python
import csv
import sys
import template
from datetime import datetime, UTC
from pathlib import Path
from urllib.parse import urlparse


def gen_id(row, name='id'):
    code = row.get(name)
    if (link := row.get('url')):
        return f'<div><a href="{link}">{code}</a></div>\n'
    return f'<div>{code}</div>\n'


def gen_link(row, name='url'):
    if (link := row.get(name)):
        url = urlparse(link)
        fn = Path(url.path).name
        return f'<div><a href="{link}">{fn}</a></div>\n'
    return '<div></div>\n'


def gen_th(name):
    return f'<div class="th">{name}</div>\n'


def gen_(row, name):
    value = row.get(name, '')
    return f'<div>{value}</div>\n'


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

    gens = dict(id=gen_id, url=gen_link, image=gen_link, pdf=gen_link)
    
    fieldnames = list(reader.fieldnames)

    def row_entries(row):
        for k in fieldnames:
            gen = gens.get(k, gen_)
            yield gen(row, k)

    def entries():
        rpl = '<div>\n&entries\n</div>'
        for row in reader:
            yield template.format(rpl, entries=row_entries(row))

    context = dict()
    context['timestamp'] = datetime.now(UTC).date().isoformat()
    context['ncols'] = len(fieldnames)
    context['fieldnames'] = map(gen_th, fieldnames)
    context['entries'] = entries()

    tpl = '''\
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>FCI Breeds</title>
<style>
:root { color-scheme: light dark; --hi: #eef; }
@media (prefers-color-scheme: dark) {
:root { --hi: #433; }
}
.table {
  display: grid;
  gap: 0;
  grid-template-columns: repeat(&ncols, 1fr);
  white-space: nowrap;
}
.table .th {
  font-weight: bolder;
  text-align: center;
}
.table > div {
  display: contents;
}
.table > div > div {
  border-right: 1px solid #ccc;
  padding: 0.1rem 1rem;
}
.table > div:hover > div {
    background-color: var(--hi);
}
</style>
</head>
<body>
<div class="info">
<h1>FCI Breeds</h1>
<p><a href="https://ukrainewar.carrd.co/"><img src="StandWithUkraine.svg" alt="standwithukraine"></a></p>
<p>Data compiled from <a href="https://www.fci.be/en/nomenclature/">https://www.fci.be/en/nomenclature/</a>.</p>
<p>Generated on &{timestamp}</p>
<p>Download: <a href="https://github.com/paiv/fci-breeds/releases/latest/download/fci-breeds.tar.gz">CSV</a></p>
</div>
<div class="table">
<div>
&{fieldnames}
</div>
&{entries}
</div>
</body>
</html>
'''
    template.print(tpl, context, file=fout)


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description='HTML page generator for the fci-breeds.csv')
    parser.add_argument('file', nargs='?', default='fci-breeds.csv', help='the CSV file to process, default is fci-breeds.csv')
    parser.add_argument('-o', '--output', help='destination file name')
    args = parser.parse_args()
    main(args)
