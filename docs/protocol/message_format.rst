Message format
==============

Client to Dana
--------------

Dana belong an unique queue where all the client put their requests.
In order to let Dana know who is sending it a message, all message send to Dana have to respect the following format :
msg = (<client_id>, <msg>)

Dana to client
--------------

Each client thread create is own queue object and send it to Dana so
Dana is able to transmit data to these thread which will send data to
client accross the network.
