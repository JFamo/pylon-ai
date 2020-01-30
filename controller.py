import sc2
import random
import os.path
try:
    import cPickle as pickle
except ModuleNotFoundError:
    import pickle

from sc2 import run_game, maps, Race, Difficulty
from sc2.player import Bot, Human, Computer
from sc2.constants import *
from main import Pylon_AI
from chevron import Chevron
from sc2.ids.unit_typeid import UnitTypeId
from os import path

def population_chevrons(file):

	with open(file, "rb") as reader:
		while True:
			try:
				yield pickle.load(reader)
			except EOFError:
				break

def set_pylon_heritage(pylon, n1, n2, s1, s2):

	pylon.parent1_name = n1
	pylon.parent2_name = n2
	pylon.parent1_score = s1
	pylon.parent2_score = s2

def find_parents():

	parents = [None, None]
	chevrons = []

	for chevron in population_chevrons('chevron_population.pkl'):

		chevrons.append(chevron)

	scores = [chevron.score for chevron in chevrons]

	if len(chevrons) < 2:
		return None
	else:
		while(parents[0] == parents[1]):
			parents = random.choices(chevrons, weights=scores, k=2)
		return parents

def cull_population(culling_threshold):

	saved = []

	for chevron in population_chevrons('chevron_population.pkl'):

		if chevron.score >= culling_threshold:

			saved.append(chevron)

	default = commit_default_chevron()

	for chevron in saved:

		chevron.commit()

	del saved

def cross_breed(pylon, parent1, parent2):

	pylon.hr_static = breed_dictionary(parent1.hr_static, parent2.hr_static, "normal")
	#pylon.hr_buildPriorities = breed_dictionary(parent1.hr_buildPriorities, parent2.hr_buildPriorities, "priority")
	# Hard set this for now, it's holding him back alot and needs to be situational
	pylon.hr_buildPriorities = {PROBE: 1, NEXUS: 10, PYLON: 4, GATEWAY: 3, STARGATE: 3, ZEALOT: 1, SENTRY: 1, STALKER: 1, ASSIMILATOR: 2, CYBERNETICSCORE: 5, FORGE: 5, VOIDRAY: 2, COLOSSUS: 2, FLEETBEACON: 5, TWILIGHTCOUNCIL: 5, PHOTONCANNON: 2, TEMPLARARCHIVE: 5, DARKSHRINE: 5, ROBOTICSBAY: 5, ROBOTICSFACILITY: 3, HIGHTEMPLAR: 2, DARKTEMPLAR: 2, PHOENIX: 2, CARRIER: 2, WARPPRISM: 2, OBSERVER: 2, IMMORTAL: 2, ADEPT: 1, ORACLE: 1, TEMPEST: 2, DISRUPTOR: 1} # This should be situational, generalize for now
	pylon.hr_upgradePriorities = breed_dictionary(parent1.hr_upgradePriorities, parent2.hr_upgradePriorities, "priority")
	pylon.hr_unitRatio = breed_dictionary(parent1.hr_unitRatio, parent2.hr_unitRatio, "ratio")
	pylon.hr_upgradeTime = breed_dictionary(parent1.hr_upgradeTime, parent2.hr_upgradeTime, "time")
	pylon.hr_techTime = breed_dictionary(parent1.hr_techTime, parent2.hr_techTime, "time")

	set_pylon_heritage(pylon, parent1.name, parent2.name, parent1.score, parent2.score)

def breed_dictionary(p1, p2, mutation_type):

	new = {}

	for x in p1:

		new[x] = breed_heuristic(p1[x], p2[x], mutation_type)

	return new

def breed_list(p1, p2, mutation_type):

	new = []

	for x in range(len(p1)):

		new.append(breed_heuristic(p1[x], p2[x], mutation_type))

	return new

def breed_heuristic(h1, h2, mutation_type):

	if isinstance(h1, (int, float)):

		return mutate(avg(h1,h2), diff(h1,h2), mutation_type)

	elif isinstance(h1, (dict)):

		return breed_dictionary(h1,h2, mutation_type)

	elif isinstance(h1, (list)):

		return breed_list(h1, h2, mutation_type)

	else:

		if h1 != h2:

			print("Heuristic " + str(h1) + " was inconsistent for parents!")

		return h1

def avg(n1, n2):

	return (n1 + n2) / 2

def diff(n1, n2):

	return 0 + abs(n1 - n2)

def random_map():

	return random.choice(["TritonLE","AcropolisLE","EphemeronLE","WintersGateLE","WorldofSleepersLE"])

def random_race():

	return random.choice([Race.Terran, Race.Protoss, Race.Zerg])

def commit_default_chevron():

	default = Chevron()
	with open('chevron_population.pkl', 'wb') as data:
		pickle.dump(default, data, pickle.HIGHEST_PROTOCOL)
	return default

def run_genetics():

	if not path.exists('chevron_population.pkl'):
		commit_default_chevron()

	pylon = Pylon_AI()
	parents = find_parents()

	if(parents):

		cross_breed(pylon, parents[0], parents[1])

	else:

		default = commit_default_chevron()
		default.copy_chevron(pylon)
		set_pylon_heritage(pylon, default.name, "nonexistent", default.score, 0)

	culling_threshold = 10000
	cull_population(culling_threshold)

	pylon.print_heuristics()

	return pylon

def mutate(num, dif, type):

	if not num == 0:
		n = dif / num * 3 / 2
	else:
		n = 0.00001

	# Try to increase spontaneous mutability
	if random.random() < 0.15:
		n = 1.5

	if type=="ratio":

		return num + (n*((random.random() - 0.5) / 5.0))

	elif type=="priority":

		return int(num + (n*((random.random() - 0.5) * 4)))

	elif type=="time":

		return num + (n*((random.random() - 0.5) * num / 10))

	else:

		return num + (n*((random.random() - 0.5) * num))

while True:	

	this_pylon = run_genetics()

	run_game(maps.get(random_map()), [
			Bot(Race.Protoss, this_pylon),
			Computer(random_race(), Difficulty.Hard)
		], realtime=False)