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


def create_database(path=''):
    try:
        Page.create_table()
        WordCount.create_table()
    except peewee.OperationalError:
        print("An error occured, too bad.")

if __name__ == "__main__":
    import sys
    if "create" in sys.argv:
        print("Creating tables...")
        create_database()
        print("Done!")
    elif "clean" in sys.argv:
        print("Cleaning old database...")
        delete_query = WordCount.delete()
        delete_query.execute()
        delete_query = Page.delete()
        delete_query.execute()
        print("Done!")
