#!/usr/bin/env python
"""
author: paiv, https://github.com/paiv/
"""

import json
import os
import requests
import sys
import time
from lxml import html
from urllib.parse import urlsplit, urlunsplit


def jsonpp(obj):
    return json.dumps(obj, sort_keys=True, indent=2, separators=[',', ': '])


def jsondump(obj, fn):
    sj = json.dumps(obj, ensure_ascii=False, sort_keys=True, indent=2, separators=[',', ': '])
    if not os.path.isdir(os.path.dirname(fn)):
        os.makedirs(os.path.dirname(fn))
    with open(fn, 'w') as fp:
        fp.write(sj)
    return fn


class Crawler:
    def __init__(self, name, dir, url, parser, dumper, delay=0.01, userAgent=None):
        self.name = name or os.path.basename(dir)
        self.dumpDir = dir
        self.rootUrl = url
        self.parser = parser
        self.dumper = dumper
        self.delay = delay
        self.userAgent = userAgent
        self.fringe = [self.rootUrl]
        self.visited = set()
        self.state = CrawlerState(fileName= '-'.join([self.name, 'crawler-state.json']))
        self.state.restore(self)
        self.req = requests.Session()

    def crawl(self):
        while self.fringe:
            url = self.norm(self.fringe.pop(0))

            if url in self.visited:
                continue

            r = self.get(url)
            if r.status_code == 200:
                page = self.parser.getcontent(r)

                self.fringe.extend(self.parser.links(page))

                for item in self.parser.items(page):

                    if self.dumper.exists(item):
                        continue

                    r = self.get(item['url'])
                    item_page = self.parser.getcontent(r)
                    item = self.parser.parse(item, item_page)

                    self.dumper.dump(item, self)

            else:
                print('%d %s' % (r.status_code, url), file=sys.stdout)

            self.visited.add(url)
            self.state.save(self)

    def reset(self):
        self.state.reset(self)
        self.dumper.reset()

    def norm(self, url):
        return urlunsplit(urlsplit(url))

    def get(self, url):
        time.sleep(self.delay)

        headers = {}
        if self.userAgent:
            headers['User-Agent'] = self.userAgent

        print(url)
        return self.req.get(url, headers=headers)

    def download(self, url, fn):
        if url is None:
            return
        r = self.get(url)
        if r.status_code == 200:
            with open(fn, 'wb') as fp:
                fp.write(r.content)
        else:
            print('%d %s' % (r.status_code, url), file=sys.stderr)


class CrawlerState:
    def __init__(self, fileName='crawler-state.json'):
        self.fileName = fileName

    def save(self, crawler):
        fn = os.path.join(crawler.dumpDir, self.fileName)
        state = {
            'rootUrl': crawler.rootUrl,
            'fringe': crawler.fringe,
            'visited': list(crawler.visited)
        }
        jsondump(state, fn)

    def restore(self, crawler):
        fn = os.path.join(crawler.dumpDir, self.fileName)
        if os.path.isfile(fn):
            with open(fn, 'r') as fp:
                state = json.load(fp)
            crawler.rootUrl = state['rootUrl']
            crawler.fringe = state['fringe']
            crawler.visited = set(state['visited'])

    def reset(self, crawler):
        crawler.fringe = [crawler.rootUrl]
        crawler.visited = set()

        fn = os.path.join(crawler.dumpDir, self.fileName)
        if os.path.isfile(fn):
            os.remove(fn)


class Dumper:
    def __init__(self, dir):
        self.dumpDir = dir

    def exists(self, item):
        return False

    def dump(self, item):
        pass


class Parser:
    def getcontent(self, request):
        return html.fromstring(request.content)

    def items(self, page):
        return []

    def links(self, page):
        return []

    def parse(self, item, page):
        return item
