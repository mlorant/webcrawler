from collections import defaultdict
from numpy import dot
from numpy import linalg as LA

from models import *
import settings
from peewee import MySQLDatabase
from math import log
from decimal import Decimal
from operator import itemgetter


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
        {'word': word, 'frequency': count}
        for word, count in words.iteritems()
    ).execute()

    # Computing tfidf
    wordpage = defaultdict(int)
    for wp in WordPage.select().iterator():
        val = wp.frequency * log(nb_documents/words[wp.word])
        update_query = WordPage.update(tfidf=val).where(WordPage.id == wp.id)
        update_query.execute()


def tfdidf_query(query):
    nb_documents = Page.select(Page.url).count()
    size_query = Word.select().where(Word.word << query).count()

    q = []
    word_pos = {}
    i = 0
    for word in Word.select().where(Word.word << query).iterator():
        q.append(log(float(nb_documents)/float(word.frequency)))
        word_pos[word.word] = i
        i += 1

    norm_q = LA.norm(q)
    similarity = {}

    for url in Page.select(Page.url).iterator():
        dj = [0] * size_query
        for words in WordPage.select().join(Page).where(Page.url == url.url, Word.word << query).iterator():
            dj[word_pos[words.word]] = float(words.tfidf)
        norm_dj = LA.norm(dj)
        if (norm_dj == 0):
            similarity[url.url] = 0
        else:
            similarity[url.url] = dot(q, dj) / (norm_q * norm_dj)

    sorted_sim = sorted(similarity.iteritems(), key=itemgetter(1), reverse=True)
    return sorted_sim


def boolean_query(query):
    nb_documents = Page.select(Page.url).count()

    parsed_query = query.replace("or", "").replace("and", "").replace("(", "").replace(")", "")
    word_query = parsed_query.split()

    word_pos = {}
    i = 0
    for word in word_query:
        word_pos[word] = i
        i += 1

    similarity = []
    for url in Page.select(Page.url).iterator():
        dj = [False] * len(word_query)
        for words in WordPage.select().join(Page).where(Page.url == url.url, Word.word <<  word_query).iterator():
            dj[word_pos[words.word]] = True
        to_eval = ''.join(query)

        for key in word_query:
            to_eval = to_eval.replace(key, str(dj[word_pos[key]]))
        res = eval(to_eval)
        if (res):
            similarity.append(url.url)

    return similarity