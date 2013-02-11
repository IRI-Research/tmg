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

- Setup `celery` by specifying a broker and initializing code:

  # RabbitMQ
  BROKER_URL = 'amqp://guest:guest@localhost:5672//'
  
  import djcelery
  djcelery.setup_loader()

- Add TMG urls:

  url(r'^', include('tmg.urls')),

How to run
==========

To run the application, `celeryd` must be running. In development
configuration, run in 2 different terminals:

  ./manage.py celeryd

and

  ./manage.py runserver
 
