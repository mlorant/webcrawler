# -*- coding: utf8 -*-
import logging
import threading
import urlparse

# Third-parties
import bs4 as BeautifulSoup
import requests

try:
    from robotparser import RobotFileParser
except NameError:
    from urllib.robotparser import RobotFileParser

# Own files
import settings


class Crawler(object):

    def __init__(self):
        self.queue = list(settings.START_URLS)
        self.nb_threads = 0

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
        print "done"
        if len(self.queue) > 0:
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
                urls = []  # mangeurDURL(req)

                self.queue.extend(urls)
            else:
                print "HTTP response: %s" % req.status_code
        else:
            print "Forbidden: %s" % url

        self.on_thread_finished()


if __name__ == "__main__":
    a = Crawler()
    a.start()
