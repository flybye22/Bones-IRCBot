Installation
============

Getting a copy of the source
----------------------------
There's basically two ways to install Bones, the version-controlled way and the
uncontrolled way. The version-controlled way is recommended because it makes upgrading
and pull request merging easier, in case you'd want to try out something that haven't
arrived yet or want to try out a development-version.

.. warning::

    Development releases must **always** be installed from version-controlled source
    from the branch :code:`develop`, or from an archived copy of the :code:`develop`
    branch. This is partly because there will be no tags for releases which is
    currently under development. You should always use VCS for development versions
    to make it easier to update your local copy.

Using version-control
~~~~~~~~~~~~~~~~~~~~~

Using :code:`git` we'll clone the repository where the Bones IRC Bot source code is
contained, and then check out a copy of the source of the current Bones release,
v\ |release|.

.. parsed-literal::

    git clone https://github.com/404d/Bones-IRCBot
    cd Bones-IRCBot
    git checkout tags/v\ |release|

If the release you're trying to install is a development version, you should run this
instead of the last step above:

.. parsed-literal::

    git checkout develop

Using archived releases
~~~~~~~~~~~~~~~~~~~~~~~
We'll just download an archived and compressed copy of the source code from Github and
uncompress that. If you're installing a released version, run these commands in your
shell:

.. parsed-literal::

    wget ht\ tps://github.com/404d/Bones-IRCBot/archive/v\ |release|.tar.gz
    tar -xzf v\ |release|.tar.gz
    cd Bones-IRCBot-v\ |release|

If you're installing a development version, run these commands instead:

.. parsed-literal::
    
    wget https://github.com/404d/Bones-IRCBot/archive/develop.tar.gz
    tar -xzf develop.tar.gz
    cd Bones-IRCBot-develop

Installing Requirements and Dependencies
----------------------------------------
From now on we'll assume you already have a working environment with pip installed.
The dependency tree for Bones may look weird for some, but basically just skip the
headers that doesn't look like they're for you.

.. note::

    :term:`Module` usually refers to Bones modules, which is Python classes that
    add functionality to the bot. However it may also refer to Python modules
    which may contain Python code and classes. All Bones modules are contained
    within a Python module, so be sure that you know which one of the two you're
    talking/reading about.

Installing base dependencies
~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Bones IRC Bot is based on Twisted, mainly because the aim of the Bones bot is to
provide an easily usable and extensive API in order to make scripting easier for
developers. However SSL is not supported by default and as such :term:`pyOpenSSL`
is a dependency for SSL connections to work.

.. code::

    pip install twisted pyopenssl

If you really don't care for SSL support you can just remove :code:`pyOpenSSL`
from the command above. Bones isn't stupid and will only try to do anything
with :term:`pyOpenSSL` if it is available on the system and just carry on
if it's unneeded.

Installing module dependencies
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Bones by itself does next to nothing; all functionality is provided by modules,
and some of these modules have dependencies of themselves, maybe Python modules,
Bones modules or something in between.

When it comes to all the default modules, there's about two dependencies you
need to think of. All the modules who parses and fetches information from
websites uses BeautifulSoup 4 for parsing the HTML trees, and a lot of the
plugins that work with some sort of data storage uses a database for storage
through the :class:`bones.modules.storage.Database` :term:`Bones module` and
the :term:`SQLAlchemy` Python module. To install the dependencies of the
bundled modules, run this command in your shell:

.. code::

    pip install beautifulsoup4 sqlalchemy

.. note::

    SQLAlchemy may require additional dependencies depending on what kind of
    database you're going to use. For more information about this, read about
    `SQLAlchemy Dialects <http://docs.sqlalchemy.org/en/rel_0_8/dialects/index.html>`_.

