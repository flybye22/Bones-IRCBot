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
    packages=["bones", "bones.modules"],
    install_requires=[
        'Twisted>=15.2.1',
    ],
    extras_requires={
        'all': [
            'Bones-IRC-Bot[db]',
            'Bones-IRC-Bot[modules]',
            'Bones-IRC-Bot[ssl]',
        ],
        'modules': [
            'Bones-IRC-Bot[twitter]',
            'Bones-IRC-Bot[qdb]',
            'Bones-IRC-Bot[youtube]',
        ],

        'db': ['SQLAlchemy>=1.0.5'],
        'ssl': ['pyOpenSSL>=0.15.1'],

        'qdb': ['beautifulsoup4>=4.3.2'],
        'youtube': ['beautifulsoup4>=4.3.2'],
        'twitter': ['beautifulsoup4>=4.3.2'],
        'lastfm': ['Bones-IRC-Bot[db]'],
        'factoid': ['Bones-IRC-Bot[db]'],
        'quotes': ['Bones-IRC-Bot[db]'],
    },
    entry_points={
        "console_scripts": [
            'bones = bones.__main__:main',
        ],
    },
)
