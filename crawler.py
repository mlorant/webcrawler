# -*- coding: utf8 -*-
import logging
import threading
import urlparse
import sys

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

# Clean the log file
if not "--no-clean-log" in sys.argv:
    with open(settings.LOG_FILE, 'w'):
        pass

# Set up logger file
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

stream_handler = logging.StreamHandler()
file_handler = logging.FileHandler(settings.LOG_FILE)
file_handler.setLevel(logging.DEBUG)

fmt = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
file_handler.setFormatter(fmt)
logger.addHandler(file_handler)
logger.addHandler(stream_handler)


class Crawler(object):

    def __init__(self):
        self.queue = list(settings.START_URLS)
        self.nb_threads = 0
        self.nb_crawled = 0

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

        scheme = urlparse.urlparse(url).scheme
        hostname = urlparse.urlparse(url).hostname
        rp = RobotFileParser(url="%s://%s/robots.txt" % (scheme, hostname))
        rp.read()

        if rp.can_fetch(settings.USER_AGENT, url):
            headers = {
                'User-Agent': settings.USER_AGENT,
            }

            req = requests.get(url, headers=headers)

            if req.status_code == 200:
                logger.debug("Start fetching %s" % url)
                urls = URL_processer(req)
                logger.info("%s crawled, %s outlink retrieved" % (url, len(urls)))
                self.queue.extend(urls)
            else:
                logger.warning("Error when requesting %s: HTTP response %s" % (url, req.status_code))
        else:
            logger.info("Crawling %s is forbidden by robots.txt rules" % url)

        self.on_thread_finished()


if __name__ == "__main__":
    database = SqliteDatabase('peewee.db')
    database.connect()

    a = Crawler()
    a.start()
