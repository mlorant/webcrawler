# -*- coding: utf8 -*-
"""
    manage.py tool for the webcrawler project.
    Allows to manage database schema and run the crawler

    Type `python manage.py -h` in a terminal for more information
"""
from __future__ import print_function
import argparse
import peewee

from crawler import Crawler
from models import *
from tfidf import compute_tfidf
import settings


# Commands definition
def syncdb(data):
    """ Synchronize the database by creating tables """
    print("Creating tables...")
    try:
        Page.create_table()
        WordPage.create_table()
        Word.create_table()
    except peewee.OperationalError as e:
        print("An error occured: ", end='')
        print(e)
    else:
        print("Done!")


def cleandb(data):
    """ Remove every old entries """
    print("Cleaning old database...")
    WordPage.delete().execute()
    Page.delete().execute()
    Word.delete().execute()
    print("Done!")


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
    a.start()


def tfidf(data):
    print("Start computing TF/IDF...")
    compute_tfidf()
    print("Done!")


# List of commands available
commands = {'syncdb': syncdb, 'cleandb': cleandb, 'run': run, 'tfidf': tfidf}

# Argument parser definition
parser = argparse.ArgumentParser(
    description='Allows to manage database schema and run the crawler')
parser.add_argument('command', type=str, choices=commands.keys(),
                    help='Command to execute')
parser.add_argument('--keep-logs', dest='keeplogs', action='store_true',
                    help='Keep previous logs of the crawler')
parser.add_argument('--logfile', dest='logfile', default=settings.LOGFILE,
                    help='Log file destination')

# Parse and execute the command asked
args = parser.parse_args()
data = {'logfile': args.logfile, 'keeplogs': args.keeplogs}
commands[args.command](data)
