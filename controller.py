import sc2
try:
    import cPickle as pickle
except ModuleNotFoundError:
    import pickle

from sc2 import run_game, maps, Race, Difficulty
from sc2.player import Bot, Computer
from main import Pylon_AI



run_game(maps.get("TritonLE"), [
		Bot(Race.Protoss, Pylon_AI()),
		Computer(Race.Terran, Difficulty.Hard)
	], realtime=True)