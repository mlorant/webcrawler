# -*- coding: utf8 -*-
"""
    manage.py tool for the webcrawler project.
    Allows to manage database schema and run the crawler

    Type `python manage.py -h` in a terminal for more information
"""
from __future__ import print_function
import argparse
import peewee
import inspect
import sys

from robot import models
from robot.crawler import Crawler
from robot.pagerank import compute_pagerank
from robot.tfidf import compute_tfidf, tfdidf_query, boolean_query
import settings


def get_model_classes():
    clsmembers = inspect.getmembers(models, inspect.isclass)
    return [(k, v) for k, v in clsmembers if k in models.__all__]


# Commands definition
def syncdb(data):
    """ Synchronize the database by creating tables """
    print("Creating tables...")

    try:
        models.Page.create_table()
        models.Word.create_table()
        models.Link.create_table()
        models.WordPage.create_table()
        models.User.create_table()
        models.UserQuery.create_table()
    except peewee.OperationalError as e:
        print("An error occured: ", end='')
        print(e)

    print("Done!")


def cleandb(data):
    """ Remove every old entries """
    print("Cleaning old database...")
    try:
        models.WordPage.delete().execute()
        models.Link.delete().execute()
        models.Word.delete().execute()
        models.Page.delete().execute()
        models.UserQuery.delete().execute()
        models.User.delete().execute()
    except peewee.OperationalError as e:
        print("An error occured: ", end='')
        print(e)
    print("Done!")


def fill_user_database(data):
    # Create users
    maxime = models.User.get_or_create(name='maxime')
    xavier = models.User.get_or_create(name='xavier')
    marc = models.User.get_or_create(name='marc')

    # Create word preferences
    models.UserQuery.create(user=maxime, word='python', frequency=5)
    models.UserQuery.create(user=maxime, word='php', frequency=3)
    models.UserQuery.create(user=xavier, word='tarantino', frequency=4)
    models.UserQuery.create(user=xavier, word='creative', frequency=4)
    models.UserQuery.create(user=xavier, word='commons', frequency=4)
    models.UserQuery.create(user=marc, word='paris', frequency=3)
    models.UserQuery.create(user=marc, word='c++', frequency=6)
    models.UserQuery.create(user=marc, word='reinhardt', frequency=4)


def run(data):
    """
    Set up database connection, clean log file if needed
    and run the crawler
    """

    settings.DATABASE.connect()
    # Clean the old log file if we don't want to keep it
    if not data['keeplogs']:
        with open(data['logfile'], 'w'):
            pass

    a = Crawler()
    a.set_logfile(data['logfile'])
    try:
        a.start()
    except KeyboardInterrupt:
        print("Stopping the crawler in few seconds...")
        a.stop = True
        sys.exit(0)


def tfidf(data):
    print("Start computing TF/IDF...")
    compute_tfidf()
    print("Done!")


def query(data):
    if data['method'] == 'tfidf':
        sim = tfdidf_query(sum([x.split(' ') for x in data['words']], []))
    else:
        query = ' '.join(data['words'])
        sim = boolean_query(query)

    for item in sim:
        print(item)


def pagerank(data):
    print("Start computing Pagerank...")
    compute_pagerank()
    print("Done! Results available in logs/")


# List of commands available
commands = {'syncdb': syncdb, 'cleandb': cleandb, 'run': run,
            'tfidf': tfidf, 'query': query, 'pagerank': pagerank,
            'filluser': fill_user_database}

# Argument parser definition
parser = argparse.ArgumentParser(
    description='Allows to manage database schema and run the crawler')
parser.add_argument('command', type=str, choices=commands.keys(),
                    help='Command to execute')
parser.add_argument('words', type=str, nargs='*',
                    help='words')
parser.add_argument('--method', dest='method', default="tfidf",
                    help='Query method', choices=['tfidf', 'boolean'])
parser.add_argument('--keep-logs', dest='keeplogs', action='store_true',
                    help='Keep previous logs of the crawler')
parser.add_argument('--logfile', dest='logfile', default=settings.LOGFILE,
                    help='Log file destination')

# Parse and execute the command asked
args = parser.parse_args()
data = {'logfile': args.logfile, 'keeplogs': args.keeplogs,
        'method': args.method, 'words': args.words}
commands[args.command](data)
