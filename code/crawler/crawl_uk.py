#!/usr/bin/env python
import core
import re
import string
from lxml import html
from pathlib import Path
from urllib.parse import urljoin
from crawl_fci import FciCrawler, FciDumper


class UkParser(core.Parser):

    def getcontent(self, request):
        return {'url': request.url, 'body': html.fromstring(request.content)}

    def items(self, page):
        def text(body, xpath):
            exslt = {'re': 'http://exslt.org/regular-expressions'}
            s = ' '.join([s.strip() for s in body.xpath(xpath, namespaces=exslt)])
            if s:
                return ' '.join(s.split())

        def filter_rows(page):
            xp = '//table[child::tr/td[contains(@class, "breed_tx")]]'
            for table in page['body'].xpath(xp):
                yield from table.xpath('tr')

            xp = '//table[child::tbody/tr/td[contains(@class, "breed_tx")]]'
            for table in page['body'].xpath(xp):
                yield from table.xpath('tbody/tr')

        group = None
        section = None

        if page['url'].endswith('09.html'):
            group = 'Собаки-компаньйони та декоративні собаки'

        for tr in filter_rows(page):
            ps = [text(td, 'descendant::text()') for td in tr.xpath('td')]
            if not ps: continue

            if (s := ps[0]) and re.match(r'^\s*Group', s, flags=re.I):
                group = ps[-1]
                if '-' in group:
                    group = ' '.join(group.split('-', maxsplit=1)[-1].split())
                group = self._normalize(group)

            if (s := ps[0]) and re.match(r'^\s*(?:S\s*\d+|Section)', s, flags=re.I) and ('.' not in s):
                section = ps[-1]
                if '-' in section:
                    section = ' '.join(section.split('-', maxsplit=1)[-1].split())
                section = self._normalize(section)

            if (rid := ps[1]) and rid.isdigit() and (rid != '0'):
                item = dict()
                item['refid'] = rid
                item['url'] = page['url']
                item['group'] = group
                item['section'] = section
                item['name'] = self._normalize(ps[4])
                item['country'] = self._normalize(ps[2])
                for a in tr.xpath('td/a'):
                    if a.text == 'UA':
                        href = urljoin(page['url'], a.attrib['href'])
                        if href.lower().endswith('.pdf'):
                            item['pdf'] = href
                        else:
                            item['url'] = href
                yield item

    def parse(self, item, page):
        raise Exception()

    def links(self, page):
        return [urljoin(page['url'], x) for x in page['body'].xpath('//td[contains(@class, "tx_osnova_mid")]/a/@href')]

    _abcs = set(string.ascii_letters)
    _apos = re.compile(r"['`]")

    def _normalize(self, text):
        if not text: return text
        text = self._apos.sub('’', text)
        #if self._abcs & set(text):
        #    raise Exception('latin in uk', repr(text))
        return text


def main(args):
    craw = FciCrawler(url=args.url, basedir=args.data_dir, parser=UkParser())
    if args.reset:
        craw.reset()
    craw.crawl()


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument('--reset', action='store_true', help='Reset data')
    parser.add_argument('-o', '--data-dir', default='data', help='Data directory')
    parser.add_argument('-l', '--language', default='uk', help='Language identifier')
    parser.add_argument('url', nargs='?', help='Base URL',
        default='https://uku.com.ua/plem_work/breed_fci/')
    args = parser.parse_args()
    main(args)
