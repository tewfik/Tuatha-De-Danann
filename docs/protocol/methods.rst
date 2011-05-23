Methods
=======

Methods' protocol.


GET_ENTITIES
------------

A client can use GET_ENTITIES method to ask Dana to return the list of entities which are on the field.

client request:
	GET_ENTITIES

Dana reponse:
	ENTITY type faction_id entity_id x y hpmax hp


GET_BATTLE_STATE
----------------

The client ask for the battle state (PLAYERS_CONNECTION | ACTIONS_CHOICE | RENDER_FIGHT | WAIT_RENDER_OK).

client request:
	GET_BATTLE_STATE

Dana response:
	BATTLE_STATE state round_number
