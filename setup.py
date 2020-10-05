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
        "Django>=2.2.2,<2.3",
        "django-environ>=0.4.5,<0.5",
        "djangorestframework",
        "dj-database-url",
        "psycopg2==2.8.4",
        "raven>=6.10.0,<7",
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
