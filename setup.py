#!/usr/bin/env python

from setuptools import setup

setup(
    name="ddpserver",
    version="0.0.1",
    description="DDP server implemented in Python. "
                "Building Meteor microservices with Python.",
    author="Adrian Liaw",
    author_email="adrianliaw2000@gmail.com",
    license="Apache 2",
    url="https://github.com/adrianliaw/python-ddp-server",
    packages=["ddpserver"],
    install_requires=[
        "aiohttp>=0.15.1",
        "sockjs>=0.2",
        "meteor-ejson>=1.0.0",
        ],
    classifiers=[
        "Development Status :: 1 - Planning",
        "Programming Language :: Python :: 3.4",
        ],
    )
