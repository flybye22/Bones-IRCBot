.. _intro-events:

Using Events
=============
Bones, and the Bones API is heavily based on events. Whenever something happens
you'll be able to find out in one way or another. To make your method listen to
and act upon events, you should use the :func:`bones.event.handler` decorator.
This decorator takes one of two keyword arguments, :code:`trigger` and
:code:`event`, but we'll explain this soon.

Creating an event handler
-------------------------
Event handlers in Bones is simply a method that is hooked up to an event. Event
handlers should take 1 argument, :code:`event` which will be an object
containing stuff relevant to the event, like the current bot instance or the
user that sent a message.

We will now create a module that will greet a user when he joins the channel.
To start off, create a new module like you did in the previous example, but
name it :code:`WelcomeBack`. Now you'll have something that looks like this:

.. code-block:: python
    :linenos:

    import bones.bot

    class WelcomeBack(bones.bot.Module):
         pass

So far so good, but we want to make this module actually do something. To start
off, we should import the package :mod:`bones.event`. Add the following line
just below the import you've already got:

.. code:: python
    import bones.event

Now we're getting close to something, but it's still not doing anything. Now,
make a method on the class and that takes two arguments, :code:`self` and
:code:`event`:

.. code:: python

    def greetUser(self, event):
        pass

Now we'll take off on a tangent in order to explain something. :code:`event`
will contain everything we need. In our module, or to be specific this method,
:code:`event` will be an instance of :class:`bones.event.UserJoinEvent`. This
this object will have two attributes that are of importance to us; first being
:code:`user` and the other being :code:`channel`.
:class:`~bones.event.User` will give us access to the user's nickname, and
:class:`~bones.event.Channel` will let us send messages to the channel. I
advice you to click on those two links to read about the attributes and
methods available on those two objects.

Ok, so what we need to do is 1) get the user's nickname and 2) send a message
to the channel. The first problem can be solved by making use of
:code:`event.user.nickname`, and the other can be solved by using
:code:`event.channel.msg()`. To start off we should build our string:

.. code:: python

    greeting = "Welcome back, %s!" % event.user.nickname

Now that our message is ready, all that's left is sending it to our channel:

.. code:: python

    event.channel.msg(greeting)

We're almost done! There's just one problem left though: If you were to load
your module now, nothing would happen when the user joins despite you having
written code that should do something when that happens. But why is this? The
answer isn't far away: you haven't turned your method into an event handler
yet.

Event handlers are regular methods that gets tied to an even by using a
decorator, in this case :func:`bones.event.handler`. In  other to register
this method as an event handler we need to know one thing: What is the class
of the event we want to use? In this case we want to do something with
:class:`bones.event.UserJoinEvent`, so what we'll do is we'll pass that class
as the :code:`event` argument to :func:`bones.event.handler` and place the
decorator above our method, like this:

.. code:: python

    @bones.event.handler(event=bones.event.UserJoinEvent)
    def greetUser(self, event):
        ...

All that's left now is to add the new module to your configuration:

.. code:: ini

    modules = bones.modules.utilities.Utilities
        tutorial.module.DummyModule
        tutorial.module.WelcomeBack

And you should be all set. For reference, here's what your file should look
like, if we look away from the dummy module we made in our previous tutorial:

.. code-block:: python
    :linenos:

    import bones.bot
    import bones.event

    class WelcomeBack(bones.bot.Module):

        @bones.event.handler(event=bones.event.UserJoinEvent)
        def greetUser(self, event):
            greeting = "Welcome back, %s!" % event.user.nickname
            event.channel.msg(greeting)


.. seealso::

    :ref:`api-events`
