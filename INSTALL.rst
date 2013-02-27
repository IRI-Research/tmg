Installation instructions
=========================

- Install requirements.pip dependencies (rest-framework)
- Make sure that MEDIA_ROOT/MEDIA_URL are correctly defined.
- Add `tmg`, `rest_framework` and `djcelery` to  INSTALLED_APPS

  INSTALLED_APPS = ([...]
  # Note: the application using rest-framework must be placed
  # *before* rest-framework so that customized templates can be
  # found.
  'tmg',
  'rest_framework',
  'djcelery',
  [...])

- Setup `celery` by specifying a RabbitMQ broker (which must be
  installed and configured, of course), a result backend and
  initializing code:

  # RabbitMQ
  BROKER_URL = 'amqp://guest:guest@localhost:5672//'
  CELERY_RESULT_BACKEND = 'amqp'

  import djcelery
  djcelery.setup_loader()

- Add TMG urls:

  url(r'^', include('tmg.urls')),

How to run
==========

To run the application, at least a **local** celery worker must be
running (it is in charge of updating the Django DB upon task
completion), configured to handle both `celery` and `tmg` queues. In
development configuration, run in 2 different terminals:

  ./manage.py celery worker -E -l INFO --queues celery,tmg

and

  ./manage.py runserver

To monitor the task activity in real-time, install the `flower`
application.

General architecture
====================

The underlying principle is that workers do not have access to the DB:
they should be independent from the Process model.

Since handling events from the producer is cumbersome, the task of
updating the Process DB is delegated to workers running in the `tmg`
queue, which must be local and have access to the Process model.
