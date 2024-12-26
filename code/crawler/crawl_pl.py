#!/usr/bin/env python
import core
import re
from collections import defaultdict
from lxml import html
from pathlib import Path
from urllib.parse import urljoin
from crawl_fci import FciCrawler, FciDumper


class PlParser(core.Parser):

    def getcontent(self, request):
        return {'url': request.url, 'body': html.fromstring(request.content)}

    def items(self, page):
        def text(body, xpath):
            exslt = {'re': 'http://exslt.org/regular-expressions'}
            s = ' '.join([s.strip() for s in body.xpath(xpath, namespaces=exslt)])
            if s:
                return ' '.join(s.split())

        def merge(a, b):
            ps, qs = a.split(), b.split()
            n = min(len(ps), len(qs))
            cs = list()
            i = next((i for i,(x,y) in enumerate(zip(ps, qs)) if x != y), n)
            if i:
                cs.append(' '.join(ps[:i]))
            i = next((i for i,(x,y) in enumerate(zip(ps[::-1], qs[::-1])) if x != y), n)
            if i:
                cs.append(' '.join(ps[-i:]))
            res = ' '.join(cs) if cs else a
            ps = res.split()
            while ps and len(ps[-1]) < 3:
                ps.pop()
            return ' '.join(ps) if ps else res

        group = None
        section = None

        patch = {
            '59': 'Gończy szwajcarski',
            '60': 'Gończy szwajcarski krótkonożny',
            '97': 'Szpic niemiecki',
        }

        for group_el in page['body'].xpath('//div[@class = "card"]'):
            group = text(group_el, 'descendant::div[@class = "card-header"]/descendant::*/text()')
            group = re.split(r'\d+\s*', group, maxsplit=1)[-1]

            card, = group_el.xpath('descendant::div[@class = "card-body"]')
            names = defaultdict(list)
            seen = dict()
            urls = dict()

            for row in card.xpath('descendant::a'):
                href = row.attrib['href']
                rid = Path(href).stem
                if not rid.isdigit():
                    raise Exception(f'invalid id {rid!r}')

                name = row.text
                if (p := patch.get(rid)):
                    name = p
                elif (prev := seen.get(rid)):
                    name = merge(name, prev)
                names[rid].append(name)

                seen[rid] = name.strip()
                urls[rid] = urljoin(page['url'], href)

            for rid, name in seen.items():
                item = dict()
                item['refid'] = rid
                item['url'] = page['url']
                item['group'] = group
                item['name'] = name
                if (irl := urls[rid]).lower().endswith('.pdf'):
                    item['pdf'] = irl
                else:
                    item['url'] = irl
                yield item

    def parse(self, item, page):
        raise Exception()

    def links(self, page):
        return list()


def main(args):
    craw = FciCrawler(url=args.url, basedir=args.data_dir, parser=PlParser())
    if args.reset:
        craw.reset()
    craw.crawl()


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument('--reset', action='store_true', help='Reset data')
    parser.add_argument('-o', '--data-dir', default='data', help='Data directory')
    parser.add_argument('-l', '--language', default='pl', help='Language identifier')
    parser.add_argument('url', nargs='?', help='Base URL',
        default='https://www.zkwp.pl/wzorce.php')
    args = parser.parse_args()
    main(args)
