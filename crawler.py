# -*- coding: utf8 -*-
import logging
import threading
import urlparse
import sys
import sqlite3

# Third-parties
import bs4 as BeautifulSoup
from peewee import *
import requests

try:
    from robotparser import RobotFileParser
except NameError:
    from urllib.robotparser import RobotFileParser

# Own files
from mangeur import URL_processer
import settings


class Crawler(object):

    def __init__(self):
        self.queue = list(settings.START_URLS)
        self.nb_threads = 0
        self.nb_crawled = 0
        self.urls_crawled = []

    def set_logfile(self, path, level=logging.DEBUG):
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.DEBUG)

        stream_handler = logging.StreamHandler()
        file_handler = logging.FileHandler(path)
        file_handler.setLevel(logging.DEBUG)

        fmt = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        file_handler.setFormatter(fmt)
        self.logger.addHandler(file_handler)
        self.logger.addHandler(stream_handler)

    def start(self):
        """
        Start to run the crawl with start URL defined.
        """
        while self.nb_threads < settings.MAX_THREADS and len(self.queue) > 0:
            self.start_thread()

    def start_thread(self):
        """
        Run a new thread by popping the first URL of the queue
        """
        url = self.queue.pop()
        a = threading.Thread(None, Crawler.fetch_page, None, (self, url))
        a.start()
        self.nb_threads += 1

    def on_thread_finished(self):
        """
        Callback called at the end of the fetching of one page
        """
        self.nb_crawled += 1

        if len(self.queue) > 0 and self.nb_crawled < settings.MAX_PAGES_TO_CRAWL:
            self.start_thread()

    def fetch_page(self, url):
        """
        Fetch and parse the page. Returns a BeautifulSoup object
        """

        self.urls_crawled.append(url)
        scheme = urlparse.urlparse(url).scheme
        hostname = urlparse.urlparse(url).hostname
        rp = RobotFileParser(url="%s://%s/robots.txt" % (scheme, hostname))

        try:
            rp.read()

            if rp.can_fetch(settings.USER_AGENT, url):
                headers = {
                    'User-Agent': settings.USER_AGENT,
                }



                req = requests.get(url, headers=headers)

                if req.status_code == 200:
                    self.logger.debug("Start fetching %s" % url)
                    urls = URL_processer(req)

                    # Add only url not already crawled
                    not_crawled = [u for u in urls if u not in self.urls_crawled]
                    self.queue.extend(not_crawled)
                    self.logger.info("%s crawled, %s outlink retrieved" %
                                (url, len(not_crawled)))
                else:
                    self.logger.warning("Error when requesting %s: HTTP response %s" % (url, req.status_code))
            else:
                self.logger.info("Crawling %s is forbidden by robots.txt rules" % url)
        except:
            self.logger.info("Erros when reading robots.txt from %s" % url)

        self.on_thread_finished()
