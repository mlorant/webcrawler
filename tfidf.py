from collections import defaultdict
from math import log

from peewee import UpdateQuery

from models import *
import settings


def compute_tfidf():
    nb_documents = float(Page.select().count())
    wordpage = WordPage.select()

    # Count how many times each word appears in documents
    words = defaultdict(int)
    for wp in wordpage:
        words[wp.word] += 1

    # Insert in Word table
    Word.delete().execute()
    Word.insert_many(
        {'word': word, 'frequency': (count / nb_documents) * 100}
        for word, count in words.iteritems()
    ).execute()

    def idf(x):
        print str(x)
        return x
    #idf = lambda x: x     #log(nb_documents) / words[x]
    tfidf = {}
    import time
    t1 = time.time()
    for wp in wordpage.naive():
        tfidf[wp.page, wp.word] = float(wp.frequency) * log(nb_documents / words[wp.word])

    print "TFIDF update: %s" % (time.time() - t1)

    #for wp in wordpage:
    #    wp.update(tfidf=float(wp.frequency) * log(nb_documents / words[wp.word])).execute()

    #print "TFIDF update: %s" (time.time() - t1)
    #settings.DATABASE.execute_sql("""
     #   UPDATE wordpage wp JOIN word w ON wp.word = w.word SET tfidf=wp.frequency + LOG(%s / w.frequency)
      #  """ % nb_documents)
    #WordPage.update(tfidf=WordPage.frequency * log(nb_documents) / Word.frequency) \
     #   .join(Word, on=(
    #WordPage.word == Word.word)).execute()
