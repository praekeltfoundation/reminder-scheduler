from setuptools import find_packages, setup

setup(
    name="reminder-scheduler",
    version="1.0.0",
    url="http://github.com/praekeltfoundation/reminder-scheduler",
    license="BSD",
    author="Praekelt Foundation",
    author_email="dev@praekeltfoundation.org",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        "celery==4.4.2",
        "Django~=3.1.0",
        "django-celery-beat==2.0.0",
        "django-environ>=0.4.5,<0.5",
        "djangorestframework",
        "dj-database-url",
        "psycopg2==2.8.4",
        "sentry-sdk==0.16.3",
        "redis==4.5.3",
        "requests>=2.24.0",
        "phonenumbers",
        "pytz"
    ],
    classifiers=[
        "Development Status :: 4 - Beta",
        "Framework :: Django",
        "License :: OSI Approved :: BSD License",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3.6",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
)
