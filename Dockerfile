FROM ghcr.io/praekeltfoundation/docker-django-bootstrap-nw:py3.9-bullseye as builder

RUN apt-get-install.sh build-essential libpq-dev

COPY setup.py requirements.txt ./

# Remove the pip config to re-enable caching.
RUN rm /etc/pip.conf
RUN pip install -e .
RUN mkdir /wheels
# Copy any binary wheels we've built into /wheels for installation in the
# runtime image.
RUN for f in $(find /root/.cache/pip/wheels -type f | grep -v 'none-any.whl$'); do cp $f /wheels/; done


FROM ghcr.io/praekeltfoundation/docker-django-bootstrap-nw:py3.9-bullseye

COPY . /app

COPY --from=builder /wheels /wheels
RUN pip install -f /wheels -e .

# temporary untill there is a new PyCap Release
ENV DJANGO_SETTINGS_MODULE "config.settings.production"
RUN SECRET_KEY=placeholder ALLOWED_HOSTS=placeholder python manage.py collectstatic --noinput
CMD ["config.wsgi:application"]
