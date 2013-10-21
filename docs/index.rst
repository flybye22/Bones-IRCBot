Welcome to Bones IRC Bot's documentation!
=========================================
The Bones IRC Bot is a bare bones IRC Bot made with extensibility
in mind. It provides an easy to use API for writing :term:`Bones modules`
which is the base of the bot itself. The bot is by default an empty shell
which does work like managing connections, configurations, error handling
and providing and implementing the API itself.

A basic :term:`Bones module` may be made in as few lines as this:

.. code-block:: python
    :linenos:

    import bones.bot
    import bones.event

    class Greeter(bones.bot.Module):
        
        @bones.event.handler(event="UserJoinEvent")
        def greet_user(self, event):
            event.client.msg(
                event.user.nickname,
                "Welcome to %s, %s!" % (event.channel, event.user.nickname)
            )

The documentation on this page is just as much documentation of the API
as it is of the bot itself. No matter whether you just want to make
something new or if you want to help out, this documentation will cover
most of it. Note that internal methods may appear here because of this
even though they're not meant to be used and/or a part of the public API.

Getting Started
---------------

.. toctree::
   :glob:

   intro/installation
   intro/module
   intro/events

API Documentation
-----------------

.. toctree::
   :glob:

   api/*

Indices and tables
==================

* :ref:`genindex`
* :ref:`glossary`
* :ref:`modindex`
* :ref:`search`

