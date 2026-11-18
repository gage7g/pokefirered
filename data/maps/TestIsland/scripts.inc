TestIsland_MapScripts::
	.byte 0

@ Test hooks. Walking onto the trigger tile in Pallet Town sends you here, and back.
TestIsland_EventScript_WarpIn::
	warp MAP_TEST_ISLAND, 9, 7
	waitstate
	end

TestIsland_EventScript_WarpOut::
	warp MAP_PALLET_TOWN, 5, 10
	waitstate
	end
