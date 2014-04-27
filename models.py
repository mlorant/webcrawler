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
    page_id = peewee.ForeignKeyField(Page)
    word = peewee.CharField()
    occurences = peewee.IntegerField()

    class Meta:
        database = DATABASE
