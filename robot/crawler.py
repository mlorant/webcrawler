# -*- coding: utf8 -*-
import logging
import threading
import urlparse
import socket
import sqlite3
import time

# Third-parties
import bs4 as BeautifulSoup
from peewee import *
import requests

try:
    from robotparser import RobotFileParser
except NameError:
    from urllib.robotparser import RobotFileParser

# Own files
from htmlparser import URL_processer
import settings

# Force timeout to 5 seconds
socket.setdefaulttimeout(settings.TIMEOUT)


class Crawler(object):

    def __init__(self):
        self.queue = list(settings.START_URLS)
        self.nb_threads = 0
        self.nb_crawled = 0
        self.urls_crawled = []
        self.robotstxt = {}    # TODO: a routine to empty this list sometimes
        self.stop = False

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
        while self.can_start_thread():
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
        self.nb_threads -= 1
        while self.can_start_thread():
            self.start_thread()

    def can_start_thread(self):
        return (len(self.queue) > 0
                and self.nb_crawled < settings.MAX_PAGES_TO_CRAWL
                and self.nb_threads < settings.MAX_THREADS
                and not self.stop)

    def fetch_page(self, url):
        """
        Fetch and parse the page. Returns a BeautifulSoup object
        """
        self.urls_crawled.append(url)
        scheme = urlparse.urlparse(url).scheme
        hostname = urlparse.urlparse(url).hostname

        # Check if the robots.txt allows us to crawl this url
        rp = self.get_robot_parser(scheme, hostname)
        if rp.can_fetch(settings.USER_AGENT, url.encode('utf8')):
            headers = {
                'User-Agent': settings.USER_AGENT,
            }

            self.logger.debug("Start fetching %s" % url)
            try:
                req = requests.get(url,
                                   headers=headers,
                                   timeout=settings.TIMEOUT)
            except Exception as e:
                self.logger.info("Unable to request %s (type: %s)" %
                                 (url, type(e).__name__))
                self.on_thread_finished()
                return None

            if req.status_code == 200:
                urls = URL_processer(req)

                # Add only url not already crawled
                not_crawled = set(u for u in urls if u not in self.urls_crawled)

                inlink = set(u for u in not_crawled if urlparse.urlparse(u).hostname == hostname)
                outlink = [u for u in not_crawled if u not in inlink]
                self.queue = list(inlink) + self.queue + outlink

                self.logger.info(
                    "%s crawled, <%s inlink, %s outlink>" %
                    (url, len(inlink), len(outlink))
                )
            else:
                self.logger.warning(
                    "Error when requesting %s: HTTP response %s" %
                    (url, req.status_code)
                )
        else:
            self.logger.info("Crawling %s is forbidden by robots.txt rules" % url)

        self.on_thread_finished()

    def get_robot_parser(self, scheme, hostname):
        """
        Returns the robot parser object for the hostname given. If the domain
        has already been indexed, we check if the robots.txt is up to date,
        otherwise we fetch it again.
        """
        rp = self.robotstxt.get(hostname, None)

        if rp:
            # If a robotparser already exists but his last
            # update time is old, we update it
            if rp.mtime() < (time.time() - settings.ROBOTS_TXT_CACHE):
                self.logger.info("Refresh %s/robots.txt cache" % hostname)
                try:
                    rp.read()
                except Exception, e:
                    print(e)
                    self.logger.info("Unable to get or parse %s/robots.txt" % hostname)
                    rp.disallow_all = False
                    rp.allow_all = True
            else:
                self.logger.debug("Retrieve cached %s/robots.txt" % hostname)
        else:
            # First (or very long) time we see this domain, create a new
            # RobotFileParser and read it once
            self.logger.info("First hit on %s/robots.txt" % hostname)
            rp = RobotFileParser(url="%s://%s/robots.txt" % (scheme, hostname))
            try:
                rp.read()
            except Exception, e:
                print(e)
                self.logger.info("Unable to get or parse %s/robots.txt" % hostname)
                rp.disallow_all = False
                rp.allow_all = True

        # In any case, we update the last robotstxt fetched time
        rp.modified()
        self.robotstxt[hostname] = rp

        return rp
