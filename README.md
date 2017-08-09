# Maxibooking billing
Maxibooking billing django rest backend

## urls
* two-factor setup url: account/two_factor/setup/
* admin: admin/
* all urls: ./manage.py show_urls --format=table

## minimum requirements
* python >= 3.6
* postgresql >= 9.6
* redis >= 4.0

## after installation
* local_settings.py.dist -> local_settings.py
* ./manage.py migrate
* ./manage.py createsuperuser
* ./manage.py cities_light
* ./manage.py citytranslate

## start project in dev
* first terminal: ./manage.py runserver_plus
* second terminal: ./manage.py celery

