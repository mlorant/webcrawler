# -*- coding: utf8 -*-
from datetime import datetime
import glob
import os
import peewee
from settings import DATABASE

__all__ = ['Page', 'Word', 'WordPage', 'Link']


# URL max size:
# http://stackoverflow.com/questions/417142/what-is-the-maximum-length-of-a-url-in-different-browsers # noqa
class Page(peewee.Model):
    """ Represent one page of the web """
    url = peewee.CharField(max_length=2048)
    date_update = peewee.DateTimeField(default=datetime.now)
    content_hash = peewee.CharField(default='')
    crawled = peewee.BooleanField(default=False)
    title = peewee.CharField(max_length=1024, default='')

    class Meta:
        database = DATABASE


class Word(peewee.Model):
    """ Represent word available on the web and the number
    of documents where they appear """
    word = peewee.CharField()
    frequency = peewee.IntegerField()

    class Meta:
        database = DATABASE


class WordPage(peewee.Model):
    """ List every word available on pages on their frequency
    the page. Also store the computed TF/IDF score for it"""
    page = peewee.ForeignKeyField(Page)
    word = peewee.CharField()
    frequency = peewee.IntegerField()
    tfidf = peewee.DecimalField(auto_round=True, default=0)

    class Meta:
        database = DATABASE


class Link(peewee.Model):
    """ Store every link between pages """
    inbound = peewee.ForeignKeyField(Page, related_name="inbound")
    target = peewee.ForeignKeyField(Page, related_name="target")
    title = peewee.CharField(default='')

    class Meta:
        database = DATABASE


class User(peewee.Model):
    """ Store every link between pages """
    name = peewee.CharField()

    class Meta:
        database = DATABASE


class UserQuery(peewee.Model):
    user = peewee.ForeignKeyField(User)
    word = peewee.CharField()
    frequency = peewee.IntegerField()

    class Meta:
        database = DATABASE
