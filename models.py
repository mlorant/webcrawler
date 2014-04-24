# -*- coding: utf8 -*-
from datetime import datetime
import peewee


class Page(peewee.Model):
    url = peewee.CharField()
    date_update = peewee.DateTimeField(default=datetime.now)
    content_hash = peewee.CharField()


class WordCount(peewee.Model):
    page_id = peewee.ForeignKeyField(Page)
    word = peewee.CharField()
    occurences = peewee.IntegerField()

if __name__ == "__main__":
    import sys
    if "create" in sys.argv:
        print("Creating tables...")
        try:
            Page.create_table()
            WordCount.create_table()
        except peewee.OperationalError:
            print("An error occured, too bad.")
            return -1

        print("Done!")
