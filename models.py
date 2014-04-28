# -*- coding: utf8 -*-
from datetime import datetime
import glob
import os
import peewee
from settings import DATABASE

__all__ = ['Page', 'Word', 'WordPage']


# URL max size:
# http://stackoverflow.com/questions/417142/what-is-the-maximum-length-of-a-url-in-different-browsers # noqa
class Page(peewee.Model):
    url = peewee.CharField(max_length=2048)
    date_update = peewee.DateTimeField(default=datetime.now)
    content_hash = peewee.CharField()

    class Meta:
        database = DATABASE


class Word(peewee.Model):
    word = peewee.CharField()
    frequency = peewee.DecimalField(auto_round=True)

    class Meta:
        database = DATABASE


class WordPage(peewee.Model):
    page = peewee.ForeignKeyField(Page)
    word = peewee.CharField()
    frequency = peewee.DecimalField(auto_round=True)
    tfidf = peewee.DecimalField(auto_round=True, default=0)

    class Meta:
        database = DATABASE
