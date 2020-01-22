import sc2
import random
try:
	import cPickle as pickle
except ModuleNotFoundError:
	import pickle

from queue import *
from sc2 import run_game, maps, Race, Difficulty
from sc2.position import Point2
from sc2.player import Bot, Computer
from sc2.constants import *
from sc2.game_data import AbilityData, GameData
from sc2.game_state import GameState
from sc2.ids.unit_typeid import UnitTypeId
from sc2.unit import Unit
from sc2.units import Units
from sc2.unit_command import UnitCommand
from sc2.ids.upgrade_id import UpgradeId

class Pylon_AI(sc2.BotAI):

	# Heuristics
	hr_supplyTrigger = 5 # Remaining supply to build pylon
	hr_gatewayConstant = 2 # Number of gateways for first nexus
	hr_stargateConstant = 2 # Number of stargates for first nexus
	hr_roboticsConstant = 1 # Number of robotics facilities for first nexus
	hr_gatewayCoeffecient = 1 # Number of gateways per nexus
	hr_stargateCoeffecient = 1 # Number of stargates per nexus
	hr_roboticsCoeffecient = 0.5 # Number of robotics facilities per nexus
	hr_expansionTime = 260 # Expansion time in seconds
	hr_workersPerBase = 22 # Number of workers per nexus
	hr_buildDistance = 6.0 # Average build distance around target
	hr_attackSupply = 50 # Supply to launch attack
	hr_defendSupply = 10 # Supply to attempt defense
	hr_gasDetector = 10.0 # Range to detect assimilators
	hr_defendDistance = 25.0 # Distance to nexus to defend

	# Priority values for all units and structures
	hr_buildPriorities = {PROBE: 1, NEXUS: 10, PYLON: 4, GATEWAY: 3, STARGATE: 3, ZEALOT: 1, SENTRY: 1, STALKER: 1, ASSIMILATOR: 2, CYBERNETICSCORE: 5, FORGE: 5, VOIDRAY: 2, COLOSSUS: 2, FLEETBEACON: 4, TWILIGHTCOUNCIL: 5, PHOTONCANNON: 2, TEMPLARARCHIVE: 4, DARKSHRINE: 4, ROBOTICSBAY: 4, ROBOTICSFACILITY: 3, HIGHTEMPLAR: 2, DARKTEMPLAR: 2, PHOENIX: 2.5, CARRIER: 3, WARPPRISM: 2, OBSERVER: 4, IMMORTAL: 2, ADEPT: 1, ORACLE: 1, TEMPEST: 2, DISRUPTOR: 1} # This should be situational, generalize for now
	# Priority values for all upgrades
	hr_upgradePriorities = {"DEFAULT": 5}

	# Supply ratio of units for build
	hr_unitRatio = {}
	hr_unitRatio[ZEALOT] = 0.15
	hr_unitRatio[STALKER] = 0.30
	hr_unitRatio[SENTRY] = 0.05
	hr_unitRatio[VOIDRAY] = 0.15
	hr_unitRatio[COLOSSUS] = 0.1
	hr_unitRatio[HIGHTEMPLAR] = 0.1
	hr_unitRatio[DARKTEMPLAR] = 0
	hr_unitRatio[PHOENIX] = 0
	hr_unitRatio[CARRIER] = 0
	hr_unitRatio[WARPPRISM] = 0
	hr_unitRatio[OBSERVER] = 0
	hr_unitRatio[IMMORTAL] = 0.1
	hr_unitRatio[ADEPT] = 0
	hr_unitRatio[ORACLE] = 0
	hr_unitRatio[TEMPEST] = 0

	# Expected timing of upgrades
	hr_upgradeTime = {}
	hr_upgradeTime[FORGERESEARCH_PROTOSSGROUNDWEAPONSLEVEL1] = [FORGE,240]
	hr_upgradeTime[FORGERESEARCH_PROTOSSGROUNDARMORLEVEL1] = [FORGE,340]
	hr_upgradeTime[FORGERESEARCH_PROTOSSGROUNDWEAPONSLEVEL2] = [FORGE,600]
	hr_upgradeTime[FORGERESEARCH_PROTOSSGROUNDARMORLEVEL2] = [FORGE,700]
	hr_upgradeTime[FORGERESEARCH_PROTOSSGROUNDWEAPONSLEVEL3] = [FORGE,800]
	hr_upgradeTime[FORGERESEARCH_PROTOSSGROUNDARMORLEVEL3] = [FORGE,900]
	hr_upgradeTime[FORGERESEARCH_PROTOSSSHIELDSLEVEL1] = [FORGE,440]
	hr_upgradeTime[FORGERESEARCH_PROTOSSSHIELDSLEVEL2] = [FORGE,650]
	hr_upgradeTime[FORGERESEARCH_PROTOSSSHIELDSLEVEL3] = [FORGE,750]
	hr_upgradeTime[CYBERNETICSCORERESEARCH_PROTOSSAIRWEAPONSLEVEL1] = [CYBERNETICSCORE,440]
	hr_upgradeTime[CYBERNETICSCORERESEARCH_PROTOSSAIRWEAPONSLEVEL2] = [CYBERNETICSCORE,1000]
	hr_upgradeTime[CYBERNETICSCORERESEARCH_PROTOSSAIRWEAPONSLEVEL3] = [CYBERNETICSCORE,1200]
	hr_upgradeTime[CYBERNETICSCORERESEARCH_PROTOSSAIRARMORLEVEL1] = [CYBERNETICSCORE,540]
	hr_upgradeTime[CYBERNETICSCORERESEARCH_PROTOSSAIRARMORLEVEL2] = [CYBERNETICSCORE,1100]
	hr_upgradeTime[CYBERNETICSCORERESEARCH_PROTOSSAIRARMORLEVEL3] = [CYBERNETICSCORE,1300]

	# Expected timing of high tech
	hr_techTime = {}
	hr_techTime[FORGE] = [0]
	hr_techTime[CYBERNETICSCORE] = [0]
	hr_techTime[STARGATE] = [300,450,600,750]
	hr_techTime[ROBOTICSFACILITY] = [400,550,800,1000]
	hr_techTime[TWILIGHTCOUNCIL] = [500]
	hr_techTime[FLEETBEACON] = [900]
	hr_techTime[ROBOTICSBAY] = [800]
	hr_techTime[TEMPLARARCHIVE] = [1100]
	hr_techTime[DARKSHRINE] = [1200]

	# Local Vars
	buildPlans = Queue()
	armyUnits = {UnitTypeId.ZEALOT, UnitTypeId.SENTRY, UnitTypeId.STALKER, UnitTypeId.VOIDRAY, UnitTypeId.COLOSSUS, UnitTypeId.HIGHTEMPLAR, UnitTypeId.DARKTEMPLAR, UnitTypeId.PHOENIX, UnitTypeId.CARRIER, UnitTypeId.DISRUPTOR, UnitTypeId.WARPPRISM, UnitTypeId.OBSERVER, UnitTypeId.IMMORTAL, UnitTypeId.ARCHON, UnitTypeId.ADEPT, UnitTypeId.ORACLE, UnitTypeId.TEMPEST}
	pendingUpgrades = []
	score = 0

	# Bot AI class startup async
	async def on_start_async(self):
		await self.chat_send("(glhf)")

	# Bot AI class step async
	async def on_step(self, iteration):
		if(self.time % 5 == 0):
			await self.distribute_workers()
		await self.assess_builds()
		await self.attempt_build()
		await self.activate_abilities()
		if(self.time % 10 == 0) and self.supply_army > 0:
			await self.amass()
		if self.supply_army > 0:
			await self.attack()

	# Attempt to build by dequeuing from build plans if I can afford it
	async def attempt_build(self):
		if(len(self.buildPlans) > 0):
			if(self.can_afford(self.buildPlans.peek())):
				nextUnit = self.buildPlans.dequeue()
				await self.build_unit(nextUnit)

	# Get accurate unit count by including build plans and pending
	def getUnitCount(self, unit):

		return self.units(unit).amount + self.buildPlans.countOf(unit) + self.already_pending(unit)

	# Returns false if an upgrade is not researched or pending, true otherwise
	def getUpgradeStatus(self, upgrade):

		if self.buildPlans.countOf(upgrade) == 0 and upgrade not in self.pendingUpgrades:
			return False
		return True

	# Switch for priority of upgrade from upgrade priorities heuristic, include default case
	def getUpgradePriority(self, upgrade):

		if upgrade in self.hr_upgradePriorities:
			return self.hr_upgradePriorities[upgrade]
		return self.hr_upgradePriorities["DEFAULT"]

	# Assess what we need to add to build plans this step
	async def assess_builds(self):

		# Assess workers using multiplier by num of bases
		if self.getUnitCount(PROBE) < self.hr_workersPerBase * self.units(NEXUS).amount:
			self.buildPlans.enqueue(PROBE, self.hr_buildPriorities[PROBE])

		# Assess pylons using heurustic threshold approaching max supply
		if self.supply_left < self.hr_supplyTrigger and not self.already_pending(PYLON) and not self.buildPlans.contains(PYLON):
			self.buildPlans.enqueue(PYLON, self.hr_buildPriorities[PYLON])

		# Assess gateways checking for complete pylon and using heuristic threshold based on num of bases
		pylons = self.units(PYLON).ready
		if pylons.exists:
			if self.getUnitCount(GATEWAY) < self.get_gateway_multiplier():
				self.buildPlans.enqueue(GATEWAY, self.hr_buildPriorities[GATEWAY])

		# Assess stargates checking for complete pylon and using heuristic threshold based on num of bases
		cyberneticscores = self.units(CYBERNETICSCORE).ready
		if cyberneticscores.exists:
			if self.getUnitCount(STARGATE) < self.get_stargate_multiplier():
				if self.get_tech_time(STARGATE) < self.time:
					self.buildPlans.enqueue(STARGATE, self.hr_buildPriorities[STARGATE])

		# Assess robotics facilities checking for complete pylon and using heuristic threshold based on num of bases
		cyberneticscores = self.units(CYBERNETICSCORE).ready
		if cyberneticscores.exists:
			if self.getUnitCount(ROBOTICSFACILITY) < self.get_robotics_multiplier():
				if self.get_tech_time(ROBOTICSFACILITY) < self.time:
					self.buildPlans.enqueue(ROBOTICSFACILITY, self.hr_buildPriorities[ROBOTICSFACILITY])

		# Assess expansion by checking heuristic predictive expansion time
		if (self.time / self.hr_expansionTime) > self.getUnitCount(NEXUS):
			self.buildPlans.enqueue(NEXUS, self.hr_buildPriorities[NEXUS])

		# Assess assimilator build by checking for empty gas by Nexus
		openGeyserCount = 0
		for nexus in self.units(NEXUS).ready:
			for vespene in self.state.vespene_geyser.closer_than(self.hr_gasDetector, nexus):
				if not self.units(ASSIMILATOR).closer_than(1.0, vespene).exists:
					openGeyserCount += 1
		if(openGeyserCount > self.buildPlans.countOf(ASSIMILATOR)):
			self.buildPlans.enqueue(ASSIMILATOR, self.hr_buildPriorities[ASSIMILATOR])
		elif(self.buildPlans.peek() == ASSIMILATOR):
			self.buildPlans.dequeue()

		self.assess_techstructure(FORGE, [GATEWAY])
		self.assess_techstructure(CYBERNETICSCORE, [GATEWAY])
		self.assess_techstructure(ROBOTICSBAY, [ROBOTICSFACILITY])
		self.assess_techstructure(FLEETBEACON, [STARGATE])
		self.assess_techstructure(TEMPLARARCHIVE, [TWILIGHTCOUNCIL])
		self.assess_techstructure(TWILIGHTCOUNCIL, [CYBERNETICSCORE])
		self.assess_techstructure(DARKSHRINE, [TWILIGHTCOUNCIL])

		self.assess_army(ZEALOT, [GATEWAY])
		self.assess_army(STALKER, [GATEWAY, CYBERNETICSCORE])
		self.assess_army(SENTRY, [GATEWAY, CYBERNETICSCORE])
		self.assess_army(VOIDRAY, [GATEWAY, CYBERNETICSCORE, STARGATE])

		self.assess_upgrades()

		# Escape case for misplaced pylons
		if self.minerals > 750:
			if self.supply_left > 20 and self.units(GATEWAY).ready.idle.amount > 0:
				self.buildPlans.enqueue(ZEALOT, 90)
				self.buildPlans.enqueue(PROBE, 90)
			else:
				self.buildPlans.enqueue(PYLON, 100)
			await self.chat_send("If you see this it means I got confused. help.")

	# Get heurisitic time after which we can research a certain upgrade
	def get_tech_time(self,unit):

		if self.getUnitCount(unit) >= len(self.hr_techTime[unit]):
			return self.hr_techTime[unit][len(self.hr_techTime[unit]) - 1]
		elif not unit in self.hr_techTime:
			return 0
		else:
			return self.hr_techTime[unit][self.getUnitCount(unit)]

	# Iterate army units and add to build plans trying to match unit ratio
	def assess_army(self, unit, requirements):

		meet_requirements = True

		for structure in requirements:
			if not self.units(structure).ready.exists:
				meet_requirements = False

		if meet_requirements:
			if (self._game_data.units[unit.value]._proto.food_required * self.getUnitCount(unit)) / self.supply_cap < self.hr_unitRatio[unit] :
					self.buildPlans.enqueue(unit, self.hr_buildPriorities[unit])

	# Iterate tech structures and build if we don't have them and we're past their heuristic build time
	def assess_techstructure(self, unit, requirements):

		meet_requirements = True

		for structure in requirements:
			if not self.units(structure).ready.exists:
				meet_requirements = False

		if meet_requirements:
			if self.getUnitCount(unit) < 1 and self.time > self.get_tech_time(unit):
				self.buildPlans.enqueue(unit, self.hr_buildPriorities[unit])

	# Iterate ugrades and add to plans if we're past their heuristic research time
	def assess_upgrades(self):

		for upgrade in self.hr_upgradeTime:
			if self.time > self.hr_upgradeTime[upgrade][1]:
				if self.units(self.hr_upgradeTime[upgrade][0]).ready.exists:
					if not self.getUpgradeStatus(upgrade):
						self.pendingUpgrades.append(upgrade)
						self.buildPlans.enqueue(upgrade, self.getUpgradePriority(upgrade))

	# Generic method to handle dequeuing unit from build plans
	async def build_unit(self, unit):
		if(unit == PROBE):
			nexuses = self.units(NEXUS).ready.idle
			if nexuses:
				await self.do(nexuses.first.train(PROBE))
		if(unit == PYLON):
			await  self.build_pylons()
		if(unit == GATEWAY):
			await self.build(GATEWAY, near=self.units(PYLON).ready.random)
		if(unit == STARGATE):
			await self.build(STARGATE, near=self.units(PYLON).ready.random)
		if(unit == NEXUS):
			await self.expand_now()
		if(unit == ZEALOT):
			gateways = self.units(GATEWAY).ready.idle
			if gateways:
				await self.do(gateways.first.train(ZEALOT))
		if(unit == STALKER):
			gateways = self.units(GATEWAY).ready.idle
			if gateways:
				await self.do(gateways.first.train(STALKER))
		if(unit == SENTRY):
			gateways = self.units(GATEWAY).ready.idle
			if gateways:
				await self.do(gateways.first.train(SENTRY))
		if(unit == VOIDRAY):
			stargates = self.units(STARGATE).ready.idle
			if stargates:
				await self.do(stargates.first.train(VOIDRAY))
		if(unit == ASSIMILATOR):
			await self.build_assimilator()
		# Handle tech structures
		if unit in self.hr_techTime:
			await self.build(unit, near=self.units(PYLON).ready.random)
		# Handle upgrades
		if unit in self.hr_upgradeTime:
			buildings = self.units(self.hr_upgradeTime[unit][0]).ready.prefer_idle
			if buildings:
				await self.do(buildings.first(unit))

	# Method to place and build pylons or nexus if required
	async def build_pylons(self):
			nexuses = self.units(NEXUS).ready
			if nexuses.exists:
				await self.build(PYLON, near=self.generate_pylon_position())
			elif not self.buildPlans.contains(NEXUS):
				self.buildPlans.enqueue(NEXUS, self.hr_buildPriorities[NEXUS])
				print(self.buildPlans)

	# Method to build gas on open geyser
	async def build_assimilator(self):
		for nexus in self.units(NEXUS).ready:
			vespenes = self.state.vespene_geyser.closer_than(self.hr_gasDetector, nexus)
			for vespene in vespenes:
				worker = self.select_build_worker(vespene.position)
				if worker is None:
					break
				if not self.units(ASSIMILATOR).closer_than(1.0, vespene).exists:
					await self.do(worker.build(ASSIMILATOR, vespene))

	# Method to identify an attacking target
	def find_target(self, state):
		if len(self.known_enemy_units) > 0:
			return random.choice(self.known_enemy_units).position
		elif len(self.known_enemy_structures) > 0:
			return random.choice(self.known_enemy_structures).position
		else:
			return self.enemy_start_locations[0]

	# Method to amass army if not attacking
	async def amass(self):
		if self.supply_army < self.hr_attackSupply:
			for s in self.units.of_type(self.armyUnits):
				if not s.is_attacking:
					await self.do(s.move(self.main_base_ramp.top_center))

	# Method to make attack decisions
	async def attack(self):
		if self.supply_army > self.hr_attackSupply:
			for s in self.units.of_type(self.armyUnits):
				await self.do(s.attack(self.find_target(self.state)))

		elif self.supply_army > self.hr_defendSupply:
			if len(self.known_enemy_units) > 0:
				nearest_enemy = self.enemy_near_nexus()
				if nearest_enemy[0] < self.hr_defendDistance:
					for s in self.units.of_type(self.armyUnits):
						await self.do(s.attack(nearest_enemy[1].position))

	# Return object containing unit ID and distance of enemy closest to friendly nexus
	def enemy_near_nexus(self):

		dist = 9000
		unit = None
		if len(self.known_enemy_units) > 0:
			for nexus in self.units(NEXUS):
				if self.known_enemy_units.closest_distance_to(nexus.position) < dist:
					dist = self.known_enemy_units.closest_distance_to(nexus.position)
					unit = self.known_enemy_units.closest_to(nexus.position)
		return [dist, unit]

	# Handler for activating unit abilities in combat
	async def activate_abilities(self):
		
		# Handle sentry abilities
		for sentry in self.units(SENTRY):
			if sentry.is_attacking and sentry.energy >= 75:
				await self.do(sentry(GUARDIANSHIELD_GUARDIANSHIELD))

	# Generate pylon placement position
	def generate_pylon_position(self):
		#if self.units(PYLON).amount == 0 :-
		#	return self.main_base_ramp.top_center.random_on_distance(self.hr_buildDistance)
		#else :
			nexusPosition = self.units(NEXUS).random.position.to2.random_on_distance(self.hr_buildDistance)
			closest = None
			closest_dist = 9000
			for mineral in self.state.mineral_field:
				dist = nexusPosition.distance_to(mineral.position.to2)
				if closest == None or dist < closest_dist:
					closest_dist = dist
					closest = mineral.position.to2
			newX = nexusPosition.x - (closest.x - nexusPosition.x)
			newY = nexusPosition.y - (closest.y - nexusPosition.y)
			return Point2((newX, newY))

	# Return expected number of gateways
	def get_gateway_multiplier(self):

		return self.hr_gatewayConstant + (self.hr_gatewayCoeffecient * (self.units(NEXUS).amount - 1))

	# Return expected number of stargates
	def get_stargate_multiplier(self):

		return self.hr_stargateConstant + (self.hr_stargateCoeffecient * (self.units(NEXUS).amount - 1))

	# Return expected number of robotic facilities
	def get_robotics_multiplier(self):

		return self.hr_roboticsConstant + (self.hr_roboticsCoeffecient * (self.units(NEXUS).amount - 1))

	# On end of game, save to population
	def on_end(self, game_result):
		self.score = self.state.score.score
		self.buildPlans = None
		self.armyUnits = None
		self.pendingUpgrades = None

		print(game_result)

		with open('pylon_population.pkl', 'wb') as data:
			pickle.dump(self, data, pickle.HIGHEST_PROTOCOL)