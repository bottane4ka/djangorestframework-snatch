from os.path import join, dirname

from setuptools import setup

import snatch

setup(
    name="djangorestframework-snatch",
    version=snatch.__version__,
    description="Special library for DRF",
    author="Anna Bott",
    author_email="bottane4ka@yandex.ru",
    packages=["snatch", "snatch.options", "snatch.search", "snatch.search.operators"],
    install_requires=[
        "Django==3.2.4",
        "django-rest-framework==0.1.0",
        "psycopg2-binary==2.8.6",
        "pydantic==1.7.2",
    ],
    long_description=open(join(dirname(__file__), "README.md")).read(),
)
