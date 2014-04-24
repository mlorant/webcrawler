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
    comments = soup.findAll(text=lambda text:isinstance(text, Comment))
    [comment.extract() for comment in comments]

    # Get all text
    data = soup.findAll(text=True)

    # Transform to string
    string = unicode.join(u'\n', map(unicode, data))
    string = string.replace('\n', ' ')

    # Count words
    counts = Counter()
    counts.update(word.strip('.,?!"\'').lower() for word in string.split())

    # Update DB woth counts
    page = Page()
    page.url = my_url
    page.content_hash = ""
    Page.save(page)
    print "start word count"
    for key, value in counts.iteritems():
        wordcnt = WordCount()
        wordcnt.word = key
        wordcnt.occurences = value 
        wordcnt.page_id = page.id
        WordCount.save(wordcnt)
    print "end wc"

    # get URLs
    urls = soup.findAll("a")
    regex = re.compile(r'^http')
    filtered = [i['href'] for i in urls if regex.search(i['href'])]


    return filtered

if __name__ == "__main__":   
    database = SqliteDatabase('peewee.db')
    database.connect()

    url = 'http://www.d8.tv/d8-series/pid6654-d8-longmire.html'
    r = requests.get(url)
    urls = URL_processer(r)

    for url in urls:
        print(url)