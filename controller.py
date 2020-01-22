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
from sc2.ids.unit_typeid import UnitTypeId

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

	pylon.hr_static = breed_dictionary(parent1.hr_static, parent2.hr_static)
	pylon.hr_buildPriorities = breed_dictionary(parent1.hr_buildPriorities, parent2.hr_buildPriorities)
	pylon.hr_upgradePriorities = breed_dictionary(parent1.hr_upgradePriorities, parent2.hr_upgradePriorities)
	pylon.hr_unitRatio = breed_dictionary(parent1.hr_unitRatio, parent2.hr_unitRatio)
	pylon.hr_upgradeTime = breed_dictionary(parent1.hr_upgradeTime, parent2.hr_upgradeTime)
	pylon.hr_techTime = breed_dictionary(parent1.hr_techTime, parent2.hr_techTime)

def breed_dictionary(p1, p2):

	new = {}

	for x in p1:

		new[x] = breed_heuristic(p1[x], p2[x])

	return new

def breed_list(p1, p2):

	new = []

	for x in range(len(p1)):

		new.append(breed_heuristic(p1[x], p2[x]))

	return new

def breed_heuristic(h1, h2):

	if isinstance(h1, (int, float)):

		return avg(h1,h2)

	elif isinstance(h1, (dict)):

		return breed_dictionary(h1,h2)

	elif isinstance(h1, (list)):

		return breed_list(h1, h2)

	else:

		if h1 != h2:

			print("Heuristic " + str(h1) + " was inconsistent for parents!")

		return h1

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
	return default

pylon = Pylon_AI()
parents = find_parents()

if(parents):

	cross_breed(pylon, parents[0], parents[1])

else:

	default = commit_default_chevron()
	default.copy_chevron(pylon)

run_game(maps.get(random_map()), [
		Bot(Race.Protoss, pylon),
		Computer(random_race(), Difficulty.Easy)
	], realtime=True)