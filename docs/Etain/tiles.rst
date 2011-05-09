Tiles
=====

Disposal
--------

When placing tiles the render engine can use two method :
    - Normal mapping
    - Random mapping

When normal mapping, the engine just select the sprite and repeat it along X and Y axis as many times as needed, no more processing is done.

When Random mapping, the engine select a random sprite among a given list for each square to map and then rotate it (1/4, 1/2 or 3/4 of a complete turn) before mapping it on the square.

The normal mapping is more suited for regular tiles like cobblestone, while random mapping give less repetitive pattern for grass or dirt area.
