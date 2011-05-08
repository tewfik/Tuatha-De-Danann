================
Tuatha de Danann
================

Dana is the server which support connection of players and which maintains a representation of the virtual world.
Most of game events, actions and verifications are managed by Dana. The client (Etain) is basically devoted to graphics displaying. All game events are calculated by Dana and then transmitted to Etain which only display it.
Etain also managed keyboard and mouse event and then send the commands to Dana to be processed.

Contents:

.. toctree::
   :maxdepth: 2

   game_design/index.rst
   Dana/index.rst
   Etain/index.rst
   protocol/index.rst

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
