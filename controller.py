import sc2
import random
try:
    import cPickle as pickle
except ModuleNotFoundError:
    import pickle

from sc2 import run_game, maps, Race, Difficulty
from sc2.player import Bot, Computer
from main import Pylon_AI
from sc2.constants import *

class Chevron:

	def __init__(self):

		# Heuristics
		self.hr_supplyTrigger = 5 # Remaining supply to build pylon
		self.hr_gatewayConstant = 2 # Number of gateways for first nexus
		self.hr_stargateConstant = 2 # Number of stargates for first nexus
		self.hr_roboticsConstant = 1 # Number of robotics facilities for first nexus
		self.hr_gatewayCoeffecient = 1 # Number of gateways per nexus
		self.hr_stargateCoeffecient = 1 # Number of stargates per nexus
		self.hr_roboticsCoeffecient = 0.5 # Number of robotics facilities per nexus
		self.hr_expansionTime = 260 # Expansion time in seconds
		self.hr_workersPerBase = 22 # Number of workers per nexus
		self.hr_buildDistance = 6.0 # Average build distance around target
		self.hr_attackSupply = 30 # Supply to launch attack
		self.hr_defendSupply = 10 # Supply to attempt defense
		self.hr_gasDetector = 10.0 # Range to detect assimilators
		self.hr_defendDistance = 25.0 # Distance to nexus to defend

		# Priority values for all units and structures
		self.hr_buildPriorities = {PROBE: 1, NEXUS: 10, PYLON: 4, GATEWAY: 3, STARGATE: 3, ZEALOT: 1, SENTRY: 1, STALKER: 1, ASSIMILATOR: 2, CYBERNETICSCORE: 5, FORGE: 5, VOIDRAY: 2, COLOSSUS: 2, FLEETBEACON: 4, TWILIGHTCOUNCIL: 5, PHOTONCANNON: 2, TEMPLARARCHIVE: 4, DARKSHRINE: 4, ROBOTICSBAY: 4, ROBOTICSFACILITY: 3, HIGHTEMPLAR: 2, DARKTEMPLAR: 2, PHOENIX: 2.5, CARRIER: 3, WARPPRISM: 2, OBSERVER: 4, IMMORTAL: 2, ADEPT: 1, ORACLE: 1, TEMPEST: 2, DISRUPTOR: 1} # This should be situational, generalize for now
		# Priority values for all upgrades
		self.hr_upgradePriorities = {"DEFAULT": 5}

		# Supply ratio of units for build
		self.hr_unitRatio = {}
		self.hr_unitRatio[ZEALOT] = 0.15
		self.hr_unitRatio[STALKER] = 0.30
		self.hr_unitRatio[SENTRY] = 0.05
		self.hr_unitRatio[VOIDRAY] = 0.15
		self.hr_unitRatio[COLOSSUS] = 0.1
		self.hr_unitRatio[HIGHTEMPLAR] = 0.1
		self.hr_unitRatio[DARKTEMPLAR] = 0
		self.hr_unitRatio[PHOENIX] = 0
		self.hr_unitRatio[CARRIER] = 0
		self.hr_unitRatio[WARPPRISM] = 0
		self.hr_unitRatio[OBSERVER] = 0
		self.hr_unitRatio[IMMORTAL] = 0.1
		self.hr_unitRatio[ADEPT] = 0
		self.hr_unitRatio[ORACLE] = 0
		self.hr_unitRatio[TEMPEST] = 0

		# Expected timing of upgrades
		self.hr_upgradeTime = {}
		self.hr_upgradeTime[FORGERESEARCH_PROTOSSGROUNDWEAPONSLEVEL1] = [FORGE,240]
		self.hr_upgradeTime[FORGERESEARCH_PROTOSSGROUNDARMORLEVEL1] = [FORGE,340]
		self.hr_upgradeTime[FORGERESEARCH_PROTOSSGROUNDWEAPONSLEVEL2] = [FORGE,600]
		self.hr_upgradeTime[FORGERESEARCH_PROTOSSGROUNDARMORLEVEL2] = [FORGE,700]
		self.hr_upgradeTime[FORGERESEARCH_PROTOSSGROUNDWEAPONSLEVEL3] = [FORGE,800]
		self.hr_upgradeTime[FORGERESEARCH_PROTOSSGROUNDARMORLEVEL3] = [FORGE,900]
		self.hr_upgradeTime[FORGERESEARCH_PROTOSSSHIELDSLEVEL1] = [FORGE,440]
		self.hr_upgradeTime[FORGERESEARCH_PROTOSSSHIELDSLEVEL2] = [FORGE,650]
		self.hr_upgradeTime[FORGERESEARCH_PROTOSSSHIELDSLEVEL3] = [FORGE,750]
		self.hr_upgradeTime[CYBERNETICSCORERESEARCH_PROTOSSAIRWEAPONSLEVEL1] = [CYBERNETICSCORE,440]
		self.hr_upgradeTime[CYBERNETICSCORERESEARCH_PROTOSSAIRWEAPONSLEVEL2] = [CYBERNETICSCORE,1000]
		self.hr_upgradeTime[CYBERNETICSCORERESEARCH_PROTOSSAIRWEAPONSLEVEL3] = [CYBERNETICSCORE,1200]
		self.hr_upgradeTime[CYBERNETICSCORERESEARCH_PROTOSSAIRARMORLEVEL1] = [CYBERNETICSCORE,540]
		self.hr_upgradeTime[CYBERNETICSCORERESEARCH_PROTOSSAIRARMORLEVEL2] = [CYBERNETICSCORE,1100]
		self.hr_upgradeTime[CYBERNETICSCORERESEARCH_PROTOSSAIRARMORLEVEL3] = [CYBERNETICSCORE,1300]

		# Expected timing of high tech
		self.hr_techTime = {}
		self.hr_techTime[FORGE] = [0]
		self.hr_techTime[CYBERNETICSCORE] = [0]
		self.hr_techTime[STARGATE] = [300,450,600,750]
		self.hr_techTime[ROBOTICSFACILITY] = [400,550,800,1000]
		self.hr_techTime[TWILIGHTCOUNCIL] = [500]
		self.hr_techTime[FLEETBEACON] = [900]
		self.hr_techTime[ROBOTICSBAY] = [800]
		self.hr_techTime[TEMPLARARCHIVE] = [1100]
		self.hr_techTime[DARKSHRINE] = [1200]

		# Score identifier
		self.score = 0

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
	parent1_score = 0
	parent2_score = 0

	for chevron in population_chevrons('chevron_population.pkl'):

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

commit_default_chevron()

#if(find_parents()):

	#cross_breed(this_pylon, parent1, parent2)

run_game(maps.get(random_map()), [
		Bot(Race.Protoss, pylon),
		Computer(random_race(), Difficulty.Easy)
	], realtime=True)