======================
Protocol documentation
======================

This documentation cover network protocol which is used in Dana (server) and Etain (client) communication.

step 1 : the client register at Dana which assign it a client unique identifier
step 2 : the client open two communication channel : (1) receive, (2) send
step 3 : the client send data in the "send channel" and receive data in the "receive channel" in parallel. The client have to react to request of the server in real time.

.. toctree::
   :maxdepth: 2

   player_connexion
   network_communication
   world

.. seealso::

   Dana is based on the SocketServer_ standard library.

   .. _SocketServer: http://docs.python.org/library/socketserver.html
