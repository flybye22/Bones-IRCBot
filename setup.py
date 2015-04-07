#!/usr/bin/env python

from distutils.core import setup

setup(
    name="Bones IRC Bot",
    version="0.2.0-DEV",
    description="""A \"barebones\" modular IRC Bot providing a framework for
bot development using modules able to handle e.g. triggers and such.""",
    author="Simen Lybekk",
    author_email="simen4000+github-bones@gmail.com",
    url="http://github.com/404d/Bones-IRCBot",
    packages=["bones"],
    install_requires=[
        'Twisted==15.0.0',
        'zope.interface==4.1.2',
    ],
    entry_points={
        "console_scripts": [
            'bones = bones.__main__:main',
        ],
    },
)
