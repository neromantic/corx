=======
Barista
=======

.. image:: https://img.shields.io/badge/License-MIT-blue.svg
    :target: https://opensource.org/licenses/MIT
    :alt: License

.. image:: https://badge.fury.io/py/corx.svg
    :target: https://badge.fury.io/py/corx
    :alt: PyPI version



Barista is a Python package designed to simplify the implementation of the Command Query Responsibility Segregation (CQRS) and Event Sourcing (ES) patterns. It provides essential components and utilities for developing systems that adhere to these patterns.

Installation
------------

Install Barista using pip::

    pip install corx


Architecture
------------

The core components of the Barista architecture include:

- **Command**: Represents a request or intention to change the state of the system.

- **CommandBus**: Responsible for handling and routing commands to the appropriate command handlers.

- **CommandHandler**: Handles specific types of commands, executing the logic associated with each command.

- **Event**: Represents an occurrence or state change in the system, often triggered by the successful handling of a command.

- **EventBus**: Manages events and notifies registered event listeners or sagas.

- **EventListener**: Reacts to specific events by executing custom logic.

- **Saga**: Orchestrates complex workflows by reacting to events and potentially issuing new commands.

License
-------

.. include:: LICENSE.txt