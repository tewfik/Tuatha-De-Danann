Player connection
=================

Registration
------------

pass

Connection
----------

When a client connects to Dana, it must first open a socket to Dana sending 'register 0' to query an identifier. Dana then send an unique id for the connection. The client then close this socket and open two new socket to Dana, sending 'receive ID' and 'send ID', where ID is the unique id given by Dana.
Dana can then send data on the socket which send 'receive ID' and the client can send data to Dana on the socket on which he sent 'send ID'.

Time out
--------

pass

Deconnection
------------

pass
