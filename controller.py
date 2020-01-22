import sc2
try:
    import cPickle as pickle
except ModuleNotFoundError:
    import pickle

from sc2 import run_game, maps, Race, Difficulty
from sc2.player import Bot, Computer
from main import Pylon_AI

this_pylon = Pylon_AI()

run_game(maps.get("TritonLE"), [
		Bot(Race.Protoss, this_pylon),
		Computer(Race.Terran, Difficulty.Hard)
	], realtime=True)