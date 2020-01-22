import sc2
import random
try:
    import cPickle as pickle
except ModuleNotFoundError:
    import pickle

from sc2 import run_game, maps, Race, Difficulty
from sc2.player import Bot, Computer
from main import Pylon_AI
from chevron import Chevron

def population_chevrons(file):

	with open(file, "rb") as reader:
		while True:
			try:
				yield pickle.load(reader)
			except EOFError:
				break

def find_parents():

	parent1 = None
	parent2 = None
	parent1_score = -1
	parent2_score = -1

	for chevron in population_chevrons('chevron_population.pkl'):

		print(chevron.name + " : " + str(chevron.score))

		if chevron.score > parent2_score:
			parent2_score = chevron.score
			parent2 = chevron

		if chevron.score > parent1_score:
			parent2 = parent1
			parent2_score = parent1_score
			parent1 = chevron
			parent1_score = chevron.score

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

def commit_default_chevron():

	default = Chevron()
	with open('chevron_population.pkl', 'wb') as data:
		pickle.dump(default, data, pickle.HIGHEST_PROTOCOL)

pylon = Pylon_AI()

if(find_parents()):

	print("Found parents")

	#cross_breed(this_pylon, parent1, parent2)

run_game(maps.get(random_map()), [
		Bot(Race.Protoss, pylon),
		Computer(random_race(), Difficulty.Easy)
	], realtime=True)