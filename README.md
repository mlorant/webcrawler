webcrawler
==========

Requirements
------------

 - Python >= 2.7
 - PIP
 - Any database system: PostgreSQL, MySQL, SQLite...

Also run `pip -r requirements.txt` to install third-parties modules.

Usage of manage.py
------------------

Extract from `python manage.py -h`:

    usage: manage.py [-h] [--method {tfidf,boolean}] [--keep-logs]
                     [--logfile LOGFILE]
                     {run,filluser,tfidf,cleandb,pagerank,query,syncdb}
                     [words [words ...]]

    Allows to manage database schema and run the crawler

    positional arguments:
      {run,filluser,tfidf,cleandb,pagerank,query,syncdb}
                            Command to execute
      words                 words

    optional arguments:
      -h, --help            show this help message and exit
      --method {tfidf,boolean}
                            Query method
      --keep-logs           Keep previous logs of the crawler
      --logfile LOGFILE     Log file destination


Examples
--------

    python manage.py syncdb          # Will create tables
    python manage.py filluser        # Fill default user profiles
    python manage.py run             # Starts the crawler
    python manage.py tfidf           # Compute TF/IDF
    python manage.py query django    # Make a query using the TF/IDF method
    python manage.py pagerank        # Output pagerank results in logs/