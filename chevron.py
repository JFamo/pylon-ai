import sc2
import random
try:
	import cPickle as pickle
except ModuleNotFoundError:
	import pickle

from sc2.constants import *

class Chevron:

	def __init__(self):

		# Heuristics
		self.hr_static = {}
		self.hr_static['supplyTrigger'] = 5 # Remaining supply to build pylon
		self.hr_static['gatewayConstant'] = 2 # Number of gateways for first nexus
		self.hr_static['stargateConstant'] = 2 # Number of stargates for first nexus
		self.hr_static['roboticsConstant'] = 1 # Number of robotics facilities for first nexus
		self.hr_static['gatewayCoeffecient'] = 1 # Number of gateways per nexus
		self.hr_static['stargateCoeffecient'] = 1 # Number of stargates per nexus
		self.hr_static['roboticsCoeffecient'] = 0.5 # Number of robotics facilities per nexus
		self.hr_static['expansionTime'] = 260 # Expansion time in seconds
		self.hr_static['workersPerBase'] = 22 # Number of workers per nexus
		self.hr_static['buildDistance'] = 6.0 # Average build distance around target
		self.hr_static['attackSupply'] = 40 # Supply to launch attack
		self.hr_static['defendSupply'] = 10 # Supply to attempt defense
		self.hr_static['gasDetector'] = 10.0 # Range to detect assimilators
		self.hr_static['defendDistance'] = 25.0 # Distance to nexus to defend

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

		# Random name to identify self
		first = random.choice(["Antimony","Arsenic","Aluminum","Selenium","Lead","Oxygen","Nitrogen","Rhenium","Neodynium","Neptunium","Germanium","Iron","Silver","Gold","Tin","Americium","Uranium","Plutonium","Boron","Carbon","Hydrogen","Helium"])
		last = random.choice(["Alpha","Beta","Gamma","Delta","Epsilon","Zeta","Eta","Theta","Iota","Kappa","Lambda","Mu","Nu","Omikron","Xi","Pi","Rho","Sigma","Tau","Upsilon","Phi","Psi","Chi","Omega"])
		self.name = first + " " + last

	def copy_pylon(self, pylon):

		self.hr_static = pylon.hr_static
		self.hr_buildPriorities = pylon.hr_buildPriorities
		self.hr_upgradePriorities = pylon.hr_upgradePriorities
		self.hr_unitRatio = pylon.hr_unitRatio
		self.hr_upgradeTime = pylon.hr_upgradeTime
		self.hr_techTime = pylon.hr_techTime
		self.score = pylon.score

	def copy_chevron(self, pylon):

		pylon.hr_static = self.hr_static
		pylon.hr_buildPriorities = self.hr_buildPriorities
		pylon.hr_upgradePriorities = self.hr_upgradePriorities
		pylon.hr_unitRatio = self.hr_unitRatio
		pylon.hr_upgradeTime = self.hr_upgradeTime
		pylon.hr_techTime = self.hr_techTime
		pylon.score = self.score

	def commit(self):
		with open('chevron_population.pkl', 'ab') as data:
			pickle.dump(self, data, pickle.HIGHEST_PROTOCOL)

		print("Committed " + self.name)