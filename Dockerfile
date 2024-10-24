FROM ghcr.io/praekeltfoundation/docker-django-bootstrap-nw:py3.10-buster

COPY . /app
RUN pip install poetry
RUN poetry config virtualenvs.create false \
    && poetry install --no-dev --no-interaction --no-ansi --no-cache

# temporary untill there is a new PyCap Release
ENV DJANGO_SETTINGS_MODULE "config.settings.production"
RUN SECRET_KEY=placeholder ALLOWED_HOSTS=placeholder python manage.py collectstatic --noinput
CMD ["config.wsgi:application"]