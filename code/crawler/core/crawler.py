#!/usr/bin/env python
"""
author: paiv, https://github.com/paiv/
"""

import json
import requests
import sys
import time
from lxml import html
from pathlib import Path
from urllib.parse import urlsplit, urlunsplit


def jsondump(obj, fn):
    if not fn.parent.is_dir():
        fn.parent.mkdir(parents=True)
    with open(fn, 'w') as fp:
        json.dump(obj, fp, ensure_ascii=False, sort_keys=True, indent=2, separators=[',', ': '])
    return fn


class Crawler:
    def __init__(self, name, dir, url, parser, dumper, delay=0.01, user_agent=None):
        self.name = name or dir.name
        self.dumpDir = dir
        self.rootUrl = url
        self.parser = parser
        self.dumper = dumper
        self.delay = delay
        self.user_agent = user_agent
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
                print('%d %s' % (r.status_code, url), file=sys.stderr)

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
        if self.user_agent:
            headers['User-Agent'] = self.user_agent

        print(url, file=sys.stderr)
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
        fn = crawler.dumpDir / self.fileName
        state = {
            'rootUrl': crawler.rootUrl,
            'fringe': crawler.fringe,
            'visited': list(crawler.visited)
        }
        jsondump(state, fn)

    def restore(self, crawler):
        fn = crawler.dumpDir / self.fileName
        if fn.is_file():
            with open(fn, 'r') as fp:
                state = json.load(fp)
            crawler.rootUrl = state['rootUrl']
            crawler.fringe = state['fringe']
            crawler.visited = set(state['visited'])

    def reset(self, crawler):
        crawler.fringe = [crawler.rootUrl]
        crawler.visited = set()

        fn = crawler.dumpDir / self.fileName
        if fn.is_file():
            fn.unlink()


class Dumper:
    def __init__(self, dir):
        self.dumpDir = Path(dir)

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
