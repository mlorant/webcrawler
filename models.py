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

class Word(peewee.Model):
    word = peewee.CharField()
    frequency = peewee.DecimalField()

    class Meta:
        database = DATABASE


class WordPage(peewee.Model):
    page = peewee.ForeignKeyField(Page)
    word = peewee.CharField()
    frequency = peewee.DecimalField()
    tfidf = peewee.DecimalField(default=0)

    class Meta:
        database = DATABASE
