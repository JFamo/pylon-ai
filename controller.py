import sc2
import random
try:
    import cPickle as pickle
except ModuleNotFoundError:
    import pickle

from sc2 import run_game, maps, Race, Difficulty
from sc2.player import Bot, Computer
from main import Pylon_AI

def population_pylons(file):

	with open(file, "rb") as reader:
		while True:
			try:
				yield pickle.load(reader)
			except EOFError:
				break

def find_parents():

	parent1 = None
	parent2 = None
	parent1_score = 0
	parent2_score = 0

	for pylon in population_pylons('pylon_population.pkl'):

		if pylon.score > parent2_score:
			parent2_score = pylon.score
			parent2 = pylon

		if pylon.score > parent1_score:
			parent2 = parent1
			parent2_score = parent1_score
			parent1 = pylon
			parent1_score = pylon.score

	if parent1 == None or parent2 == None:
		return None
	else:
		return [parent1, parent2]

def cross_breed(pylon, parent1, parent2):

	return None
	# TODO ~ avg all heuristics in child

def avg(n1, n2):

	return (n1 + n2) / 2

def random_map():

	return random.choice(["TritonLE","AcropolisLE","EphemeronLE","ThunderbirdLE","WintersGateLE","WorldofSleepersLE"])

def random_race():

	return random.choice([Race.Terran, Race.Protoss, Race.Zerg])

this_pylon = Pylon_AI()
with open('pylon_population.pkl', 'wb') as data:
	pickle.dump(this_pylon, data, pickle.HIGHEST_PROTOCOL)

if(find_parents()):

	cross_breed(this_pylon, parent1, parent2)

run_game(maps.get(random_map()), [
		Bot(Race.Protoss, this_pylon),
		Computer(random_race(), Difficulty.Easy)
	], realtime=True)