from urllib2 import urlopen
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

    # Transform to string
    string = unicode.join(u'\n', map(unicode, data))
    string = string.replace('\n', ' ')

    # Count words
    counts = Counter()
    counts.update(word.lower() for word in string.split() if re.match('^[a-zA-Z0-9_-]+$', word))

    # Update DB woth counts
    page = Page.get_or_create(
        url=my_url,
        content_hash='',
    )

    total_words = float(sum(v for k, v in counts.iteritems()))

    WordPage.insert_many(
        [{'word': word, 'frequency': (nb / total_words) * 100, 'page': page.id}
            for (word, nb) in counts.iteritems()]
    ).execute()

    # get URLs
    urls = soup.findAll("a")
    regex = re.compile(r'^http')
    filtered = [i['href'] for i in urls if i.has_attr('href') and regex.search(i['href'])]

    return filtered

if __name__ == "__main__":
    database = SqliteDatabase('peewee.db')
    database.connect()

    url = 'http://www.d8.tv/d8-series/pid6654-d8-longmire.html'
    r = requests.get(url)
    urls = URL_processer(r)

    for url in urls:
        print(url)