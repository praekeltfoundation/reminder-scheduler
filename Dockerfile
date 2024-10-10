FROM ghcr.io/praekeltfoundation/docker-django-bootstrap-nw:py3.9

COPY ./requirements.txt /app/
COPY ./setup.py /app/

RUN pip install poetry==1.8.3
COPY . /app
RUN poetry config virtualenvs.create false \
    && poetry install --no-dev --no-interaction --no-ansi --no-cache
    
# temporary untill there is a new PyCap Release
ENV DJANGO_SETTINGS_MODULE "config.settings.production"
RUN SECRET_KEY=placeholder ALLOWED_HOSTS=placeholder python manage.py collectstatic --noinput
CMD ["config.wsgi:application"]