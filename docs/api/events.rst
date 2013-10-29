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

.. autoclass:: bones.event.BotInitializedEvent
    :show-inheritance:

.. autoclass:: bones.event.BotJoinEvent
    :show-inheritance:

.. autoclass:: bones.event.BotKickedEvent
    :show-inheritance:

.. autoclass:: bones.event.BotModuleLoaded
    :show-inheritance:

.. autoclass:: bones.event.BotNickChangedEvent
    :show-inheritance:

.. autoclass:: bones.event.BotNoticeReceivedEvent
    :show-inheritance:

.. autoclass:: bones.event.BotPreJoinEvent
    :show-inheritance:

.. autoclass:: bones.event.PreNicknameInUseError
    :show-inheritance:

.. autoclass:: bones.event.BotSignedOnEvent
    :show-inheritance:

.. autoclass:: bones.event.BounceEvent
    :show-inheritance:

.. autoclass:: bones.event.ChannelTopicChangedEvent
    :show-inheritance:

.. autoclass:: bones.event.CTCPVersionEvent
    :show-inheritance:

.. autoclass:: bones.event.CTCPPongEvent
    :show-inheritance:

.. autoclass:: bones.event.IRCUnknownCommandEvent
    :show-inheritance:

.. autoclass:: bones.event.ModeChangedEvent
    :show-inheritance:

.. autoclass:: bones.event.PrivmsgEvent
    :show-inheritance:

.. autoclass:: bones.event.ServerChannelCountEvent
    :show-inheritance:

.. autoclass:: bones.event.ServerCreatedEvent
    :show-inheritance:

.. autoclass:: bones.event.ServerClientInfoEvent
    :show-inheritance:

.. autoclass:: bones.event.ServerHostInfoEvent
    :show-inheritance:

.. autoclass:: bones.event.ServerInfoEvent
    :show-inheritance:

.. autoclass:: bones.event.ServerLocalInfoEvent
    :show-inheritance:

.. autoclass:: bones.event.ServerMOTDReceivedEvent
    :show-inheritance:

.. autoclass:: bones.event.ServerOpCountEvent
    :show-inheritance:

.. autoclass:: bones.event.ServerSupportEvent
    :show-inheritance:

.. autoclass:: bones.event.TriggerEvent
    :show-inheritance:

.. autoclass:: bones.event.UserActionEvent
    :show-inheritance:

.. autoclass:: bones.event.UserJoinEvent
    :show-inheritance:

.. autoclass:: bones.event.UserKickedEvent
    :show-inheritance:

.. autoclass:: bones.event.UserNickChangedEvent
    :show-inheritance:

.. autoclass:: bones.event.UserPartEvent
    :show-inheritance:

.. autoclass:: bones.event.UserQuitEvent
    :show-inheritance:

Utility Classes
---------------

.. autoclass:: bones.event.Channel
.. autoclass:: bones.event.User

