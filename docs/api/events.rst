.. _api-events:

Events API
==========
.. currentmodule:: bones.event
.. automodule:: bones.event

This section details how events and the event system in the Bones IRC Bot works.
For more detailed information regarding the IRC protocol, please read :rfc:`1459`.

.. seealso::

    :ref:`intro-events`

Methods
-------
.. autofunction:: bones.event.fire
.. autofunction:: bones.event.register

Decorators
----------
.. autofunction:: bones.event.handler

Base Events
-----------
Base events are used as building blocks to add attributes and functions to other
events. The event :class:`bones.event.ChannelMessageEvent` for example inherits
from both :class:`bones.event.EventWithSource` and
:class:`bones.event.EventWithTarget`.

.. autoclass:: bones.event.Event

    .. attribute:: client

        A :class:`bones.bot.BonesBot` instance representing the server connection
        which received this event.

Events
------
All events inherits the attributes of its parents in addition to its own
attributes. The class :class:`UserJoinEvent` for example inherits the
attribute :attr:`client` from the class :class:`Event` even though that
attribute may not be mentioned in the :class:`UserJoinEvent` documentation.

.. autoclass:: bones.event.BotNoticeReceivedEvent
    :show-inheritance:

    .. note::
        
        The event identifier for this event is :code:`BotNoticeReceived`.

.. autoclass:: bones.event.BotJoinEvent
    :show-inheritance:

    .. note::
        
        The event identifier for this event is :code:`BotJoin`.

.. autoclass:: bones.event.BotKickedEvent
    :show-inheritance:

    .. note::
        
        The event identifier for this event is :code:`BotKicked`.

.. autoclass:: bones.event.BotNickChangedEvent
    :show-inheritance:

    .. note::
        
        The event identifier for this event is :code:`BotNickChanged`.

.. autoclass:: bones.event.BotPreJoinEvent
    :show-inheritance:

    .. note::
        
        The event identifier for this event is :code:`BotPreJoin`.

.. autoclass:: bones.event.PreNicknameInUseError
    :show-inheritance:

    .. note::
        
        The event identifier for this event is :code:`PreNicknameInUseError`.

.. autoclass:: bones.event.BotSignedOnEvent
    :show-inheritance:

    .. note::
        
        The event identifier for this event is :code:`BotSignedOn`.

.. autoclass:: bones.event.BounceEvent
    :show-inheritance:

    .. note::
        
        The event identifier for this event is :code:`Bounce`.

.. autoclass:: bones.event.ChannelTopicChangedEvent
    :show-inheritance:

    .. note::
        
        The event identifier for this event is :code:`ChannelTopicChanged`.

.. autoclass:: bones.event.CTCPVersionEvent
    :show-inheritance:

    .. note::
        
        The event identifier for this event is :code:`CTCPVersionReceived`.

.. autoclass:: bones.event.CTCPPongEvent
    :show-inheritance:

    .. note::
        
        The event identifier for this event is :code:`CTCPPong`.

.. autoclass:: bones.event.ModeChangedEvent
    :show-inheritance:

    .. note::
        
        The event identifier for this event is :code:`ModeChanged`.

.. autoclass:: bones.event.PrivmsgEvent
    :show-inheritance:

    .. note::
        
        The event identifier for this event is :code:`Privmsg`.

.. autoclass:: bones.event.ServerChannelCountEvent
    :show-inheritance:

    .. note::
        
        The event identifier for this event is :code:`ServerChannelCount`.

.. autoclass:: bones.event.ServerCreatedEvent
    :show-inheritance:

    .. note::
        
        The event identifier for this event is :code:`ServerCreated`.

.. autoclass:: bones.event.ServerClientInfoEvent
    :show-inheritance:

    .. note::
        
        The event identifier for this event is :code:`ServerClientInfo`.

.. autoclass:: bones.event.ServerHostInfoEvent
    :show-inheritance:

    .. note::
        
        The event identifier for this event is :code:`ServerHostInfo`.

.. autoclass:: bones.event.ServerInfoEvent
    :show-inheritance:

    .. note::
        
        The event identifier for this event is :code:`ServerInfo`.

.. autoclass:: bones.event.ServerLocalInfoEvent
    :show-inheritance:

    .. note::
        
        The event identifier for this event is :code:`ServerLocalInfo`.

.. autoclass:: bones.event.ServerMOTDReceivedEvent
    :show-inheritance:

    .. note::
        
        The event identifier for this event is :code:`ServerMOTDReceived`.

.. autoclass:: bones.event.ServerOpCountEvent
    :show-inheritance:

    .. note::
        
        The event identifier for this event is :code:`ServerOpCount`.

.. autoclass:: bones.event.ServerSupportEvent
    :show-inheritance:

    .. note::
        
        The event identifier for this event is :code:`ServerSupport`.

.. autoclass:: bones.event.TriggerEvent
    :show-inheritance:

    .. note::
       
        Trigger event handlers are registered through the :attr:`trigger`
        keyword instead of an event identifier.

.. autoclass:: bones.event.UserActionEvent
    :show-inheritance:

    .. note::
        
        The event identifier for this event is :code:`UserAction`.

.. autoclass:: bones.event.UserJoinEvent
    :show-inheritance:

    .. note::
        
        The event identifier for this event is :code:`UserJoin`.

.. autoclass:: bones.event.UserKickedEvent
    :show-inheritance:

    .. note::
        
        The event identifier for this event is :code:`UserKicked`.

.. autoclass:: bones.event.UserNickChangedEvent
    :show-inheritance:

.. autoclass:: bones.event.UserPartEvent
    :show-inheritance:

    .. note::
        
        The event identifier for this event is :code:`UserPart`.

.. autoclass:: bones.event.UserQuitEvent
    :show-inheritance:

    .. note::
        
        The event identifier for this event is :code:`UserQuit`.

Utility Classes
---------------

.. autoclass:: bones.event.User

