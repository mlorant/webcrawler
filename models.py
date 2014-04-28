# -*- coding: utf8 -*-
from datetime import datetime
import glob
import os
import peewee
from settings import DATABASE


class Page(peewee.Model):
    url = peewee.CharField(unique=True)
    date_update = peewee.DateTimeField(default=datetime.now)
    content_hash = peewee.CharField()

    class Meta:
        database = DATABASE


class WordCount(peewee.Model):
    page = peewee.ForeignKeyField(Page)
    word = peewee.CharField()
    occurences = peewee.IntegerField()
    tfidf = peewee.DecimalField(default=0)

    class Meta:
        database = DATABASE
