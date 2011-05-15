======================
Protocol documentation
======================

This documentation cover network protocol which is used in Dana (server) and Etain (client) communication.

step 1 : the client open two communication channel : (1) receive, (2) send
step 2 : Dana confirm the connection by sending an unique client id that the client will have to join to its message in order to allow Dana to recognize it.
step 3 : the client send data (+ client id) in the "send channel" and receive data in the "receive channel" in parallel. The client has to react to request of the server in real time.

.. toctree::
   :maxdepth: 2

   message_format

.. seealso::

   Dana is based on the SocketServer_ standard library.

   .. _SocketServer: http://docs.python.org/library/socketserver.html
