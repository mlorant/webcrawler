# -*- coding: utf8 -*-
from datetime import datetime
import glob
import os
import peewee


class Page(peewee.Model):
    url = peewee.CharField()
    date_update = peewee.DateTimeField(default=datetime.now)
    content_hash = peewee.CharField()


class WordCount(peewee.Model):
    page_id = peewee.ForeignKeyField(Page)
    word = peewee.CharField()
    occurences = peewee.IntegerField()


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
        print("Deleting old database...")
        map(lambda x: os.remove(x), glob.glob('*.db'))
        print("Recreating fresh database...")
        create_database()
        print("Done!")
