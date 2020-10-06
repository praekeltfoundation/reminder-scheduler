FROM praekeltfoundation/django-bootstrap:py3.6

COPY ./requirements.txt /app/
COPY ./setup.py /app/

RUN pip install -r /app/requirements.txt

COPY . /app

# temporary untill there is a new PyCap Release
ENV DJANGO_SETTINGS_MODULE "config.settings.production"
RUN SECRET_KEY=placeholder ALLOWED_HOSTS=placeholder python manage.py collectstatic --noinput
CMD ["config.wsgi:application"]