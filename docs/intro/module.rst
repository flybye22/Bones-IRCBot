.. _intro-module:

Getting started with modules
============================
:term:`Bones modules` are basically just normal Python classes with
a familiar interface so that the bot may load them on initialization.


Creating a dummy module
-----------------------
We'll start off with something easy; a module that can be loaded by
the bot but does absolutely nothing. To do this we'll import the
Python module :mod:`bones.bot` and write a class that inherits from
the class :class:`~bones.bot.Module`. The class itself will be empty.
The class will be saved as :file:`module.py` inside a directory named
:file:`tutorial`.

.. code::

    import bones.bot

    class DummyModule(bones.bot.Module):
        pass

.. note::
    Make sure there exists a file named :file:`__init__.py` inside the
    :file:`tutorial` folder, if not the module won't load because
    Python won't recognize :file:`tutorial` as a package.

Loading the dummy module
------------------------
Now that the module is ready to be used we'll need to tell the bot to
load it. First up open up your configuration file and find the line
that starts with :code:`modules =`. This is where we'll add the module
path in order to load it.

Now if you followed the previous section to every little detail you'll
have the module inside the file :file:`tutorial/module.py`. To find out
what your module path is, we'll use dot-notation. Dot-notation is the
way you refer to modules and classes in :code:`import` statements, so
the name of each folder, file and class in the path is separated by a
punctuation mark (therefore dot-notation). As the module is named
:code:`DummyModule` inside the file :file:`tutorial/module.py`, the
path to it is :code:`tutorial.module.DummyModule`

To load the module into Bones we'll append the path to the
:code:`modules` list in your configuration file. Let's take this example
here:

.. code::

    [bot]
    nickname = Bones
    username = bones
    realname = Bones IRC Bot
    channel = #Gameshaft
        #Temporals

    modules = bones.modules.utilities.Utilities
    ;    bones.modules.services.NickServ
    ;    bones.modules.services.HostServ

In this configuration file the :code:`modules` list already contains the
module :class:`bones.modules.utilities.Utilities`, so we'll need to add
a new line beneath this one and indent it with 4 spaces. After that you
can just add the module path, and the result will be this:

.. code::

    modules = bones.modules.utilities.Utilities
        tutorial.module.DummyModule

Save the file, boot the bot and you should see something like this in your log:

.. code::

    2013-10-20 22:45:02,865 - bones.bot - INFO - Loaded module bones.modules.funserv.UselessResponses
    2013-10-20 22:45:02,866 - bones.bot - INFO - Loaded module tutorial.module.DummyModule
    2013-10-20 22:45:02,868 - bones.bot - INFO - Connecting to server irc.chatno.de:+6697
    2013-10-20 22:45:04,045 - bones.bot - INFO - Signed on as Bones_.

If one of the lines read :code:`Loaded module tutorial.module.DummyModule` you've
successfully "written" a working module!
