from urllib2 import urlopen
import urlparse
from bs4 import BeautifulSoup, Comment
from collections import Counter
import re
import requests
from models import *
from peewee import *


def URL_processer(request):
    # Fetch
    soup = BeautifulSoup(request.text)
    my_url = request.request.url

    # Remove <script>
    [x.extract() for x in soup.findAll('script')]

    # Remove comments
    comments = soup.findAll(text=lambda text: isinstance(text, Comment))
    [comment.extract() for comment in comments]

    # Get all text
    data = soup.findAll(text=True)

    title = soup.findAll('title')
    if title:
        title = title[0]
    else:
        title = ''

    # Transform to string
    string = unicode.join(u'\n', map(unicode, data))
    string = string.replace('\n', ' ')

    # Count words
    counts = Counter()
    counts.update(word.lower() for word in string.split() if re.match('^[a-zA-Z0-9_-]+$', word))

    # Update DB with counts
    page = Page.get_or_create(url=my_url)

    total_words = float(sum(v for k, v in counts.iteritems()))

    WordPage.insert_many(
        [{'word': word, 'frequency': nb, 'page': page.id}
            for (word, nb) in counts.iteritems()]
    ).execute()

    # get URLs
    urls = soup.findAll("a")

    filtered = [(urlparse.urljoin(my_url, i['href']), i.text) for i in urls
                if i.has_attr('href') and not i['href'].startswith('mailto:')]

    out_pages = {}
    for href, text in filtered:
        out_pages[href] = (Page.get_or_create(url=href), text)

    if out_pages:
        already_links = Link.select().where(Link.inbound == page.id)
        excluded = [l.target.id for l in already_links]
        links = [{'inbound': page.id, 'target': tgt.id}
                for (tgt, title) in out_pages.values() if tgt.id not in excluded]
        if links:
            Link.insert_many(links).execute()

    page.crawled = True
    #page.title = title
    page.save()

    return out_pages.keys()

if __name__ == "__main__":
    database = SqliteDatabase('peewee.db')
    database.connect()

    url = 'http://www.d8.tv/d8-series/pid6654-d8-longmire.html'
    r = requests.get(url)
    urls = URL_processer(r)

    for url in urls:
        print(url)
