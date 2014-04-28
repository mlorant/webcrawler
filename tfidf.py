from collections import defaultdict

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
