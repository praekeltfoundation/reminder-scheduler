===================
Reminder Scheduler
===================
.. image:: https://travis-ci.com/praekeltfoundation/reminder-scheduler.svg?branch=develop
    :target: https://travis-ci.com/praekeltfoundation/reminder-scheduler
    :alt: Build Passing/Failing on TravisCI.com

.. image:: https://img.shields.io/badge/code%20style-black-000000.svg
    :target: https://github.com/ambv/black
    :alt: Code Style: Black


.. image:: https://codecov.io/gh/praekeltfoundation/reminder-scheduler/branch/develop/graph/badge.svg
  :target: https://codecov.io/gh/praekeltfoundation/reminder-scheduler
  :alt: Code Coverage


.. image:: https://img.shields.io/docker/automated/jrottenberg/ffmpeg.svg
    :target: https://hub.docker.com/r/praekeltfoundation/reminder-scheduler/tags/
    :alt: Docker Automated build

The Reminder Scheduler is a Django application for scheduling reminder messages that need to be sent at a later date. Currently messages are sent over WhatsApp via Turn.
The reminder and scheduled date is stored in a database and a background task checks regularly for any messages due to be sent.

-----
Usage
-----


------------------
Local installation
------------------
To set up and run ``reminder-scheduler`` locally, do the following::

    $ git clone git@github.com:praekeltfoundation/reminder-scheduler.git
    $ cd reminder-scheduler
    $ virtualenv ve
    $ source ve/bin/activate
    $ pip install -e .
    $ pip install -r requirements-dev.txt

-----
Tools
-----
- PostgreSQL
- Redis
- `black`_ - this repository uses an opinionated python code formatter. See ``pyproject.toml`` for config.

------------
Contributing
------------

See our `ways of working`_ for a guide on how to contribute to ``reminder-scheduler``.

.. _black: https://github.com/ambv/black
.. _ways of working: ./docs/ways-of-working.md

------------
Deprecation
------------

The following endpoints of ``reminder-scheduler`` will be deprecated:
- scheduler/
- ''
