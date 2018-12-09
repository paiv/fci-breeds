#!/usr/bin/env python
"""
author: paiv, https://github.com/paiv/
"""

import core
import glob
import os
import re
from lxml import html
from urllib.parse import urlsplit, urlunsplit, urljoin


class FciParser(core.Parser):
    def __init__(self):
        self.rxfciid = re.compile(r'\((\d+)\)')

    def getcontent(self, request):
        return {'url': request.url, 'body': html.fromstring(request.content)}

    def items(self, page):
        breeds = [self.item(x, page['url']) for x in page['body'].xpath('//td[contains(@class, "race")]/a[contains(@class, "nom")]')]
        return breeds

    def item(self, el, baseurl):
        m = self.rxfciid.search(''.join(el.itertext()))
        if m:
            refid = m.group(1)
        url = el.get('href')
        if url:
            url = urljoin(baseurl, url)
        return {'refid':refid, 'url':url}

    def parse(self, item, page):
        body = page['body']

        def text(xpath):
            el = ' '.join([s.strip() for s in body.xpath(xpath)])
            if el:
                return el.strip()

        def url(xpath):
            el = (body.xpath(xpath) or [None])[0]
            if el:
                return urljoin(page['url'], el)

        item['name'] = text('//span[@id="ContentPlaceHolder1_NomEnLabel"]/text()')
        item['section'] = text('//span[@id="ContentPlaceHolder1_SectionLabel"]/text()')
        item['country'] = text('//span[@id="ContentPlaceHolder1_PaysOrigineLabel"]/text()')

        imgUrl = url('//img[@id="ContentPlaceHolder1_IllustrationsRepeater_Image1_0"]/@src')
        if imgUrl: item['thumb'] = imgUrl

        pdfUrl = url('//a[@id="ContentPlaceHolder1_StandardENHyperLink"]/@href')
        if pdfUrl: item['pdf'] = pdfUrl

        provDate = text('//span[@id="ContentPlaceHolder1_DateReconnaissanceProvisoireLabel"]/text()')
        status = text('//span[@id="ContentPlaceHolder1_StatutLabel"]/text()')
        if 'provisional' in status and provDate: item['provisional'] = provDate

        return item

    def links(self, page):
        return [urljoin(page['url'], x) for x in page['body'].xpath('//div[contains(@class, "group")]/a/@href')]


class FciDumper(core.Dumper):
    def dump(self, item, crawler):
        if not item:
            return

        todir = self.todir(item)
        if not os.path.isdir(todir):
            os.makedirs(todir)

        self.meta(item, todir, crawler)

    def exists(self, item):
        todir = self.todir(item)
        fn = os.path.join(todir, 'entry.json')
        return os.path.isfile(fn)

    def todir(self, item):
        return os.path.join(self.dumpDir, 'dump', item['refid'])

    def meta(self, item, todir, crawler):
        fn = os.path.join(todir, 'entry.json')
        core.jsondump(item, fn)

    def reset(self):
        for fn in glob.glob(os.path.join(self.dumpDir, '**/entry.json'), recursive=True):
            os.remove(fn)

class FciCrawler:
    def __init__(self, basedir):
        todir = os.path.join(basedir, 'fci')
        self.craw = core.Crawler(name='fci', dir=todir, url='http://www.fci.be/en/nomenclature/',
            parser=FciParser(), dumper=FciDumper(todir))

    def crawl(self):
        return self.craw.crawl()

    def reset(self):
        self.craw.reset()


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument('--reset', action='store_true', help='Reset data')
    parser.add_argument('--data-dir', default='data', help='Data directory')
    args = parser.parse_args()

    craw = FciCrawler(basedir=args.data_dir)
    if args.reset:
        craw.reset()
    craw.crawl()
