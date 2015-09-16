#!/usr/bin/env python

from setuptools import setup

setup(
    name="meteorish",
    version="0.0.0",
    description="DDP server implemented in Python. "
                "Build Meteor microservices with Python.",
    long_description="This is a placeholder package",
    author="Adrian Liaw",
    author_email="adrianliaw2000@gmail.com",
    license="Apache 2",
    url="https://github.com/adrianliaw/meteorish.py",
    packages=["meteorish"],
    install_requires=[
        "aiohttp>=0.15.1",
        "sockjs>=0.2",
        "meteor-ejson>=1.0.0",
        ],
    classifiers=[
        "Development Status :: 1 - Planning",
        "Programming Language :: Python :: 3.4",
        "Programming Language :: Python :: 3.5",
        ],
    )
