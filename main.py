import sc2
import random

from queue import *
from chevron import Chevron
from sc2 import run_game, maps, Race, Difficulty, Result
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

	def __init__(self):

		# Heuristics
		# Static multipliers and constants
		self.hr_static = {}
		# Priority values for all units and structures
		self.hr_buildPriorities = {}
		# Priority values for all upgrades
		self.hr_upgradePriorities = {}
		# Supply ratio of units for build
		self.hr_unitRatio = {}
		# Expected timing of upgrades
		self.hr_upgradeTime = {}
		# Expected timing of high tech
		self.hr_techTime = {}

		# Algorithm tracking
		self.parent1_name = "ERROR"
		self.parent2_name = "ERROR"
		self.parent1_score = -99999
		self.parent2_score = -99999

		# Local Vars
		self.buildPlans = Queue()
		self.armyUnits = {UnitTypeId.ZEALOT, UnitTypeId.SENTRY, UnitTypeId.STALKER, UnitTypeId.VOIDRAY, UnitTypeId.COLOSSUS, UnitTypeId.HIGHTEMPLAR, UnitTypeId.DARKTEMPLAR, UnitTypeId.PHOENIX, UnitTypeId.CARRIER, UnitTypeId.DISRUPTOR, UnitTypeId.WARPPRISM, UnitTypeId.OBSERVER, UnitTypeId.IMMORTAL, UnitTypeId.ARCHON, UnitTypeId.ADEPT, UnitTypeId.ORACLE, UnitTypeId.TEMPEST}
		self.pendingUpgrades = []
		self.score = 0

		# Unit build structures
		self.build_structures = {}
		self.build_structures[ZEALOT] = GATEWAY
		self.build_structures[STALKER] = GATEWAY
		self.build_structures[SENTRY] = GATEWAY
		self.build_structures[ADEPT] = GATEWAY
		self.build_structures[VOIDRAY] = STARGATE
		self.build_structures[PHOENIX] = STARGATE
		self.build_structures[ORACLE] = STARGATE
		self.build_structures[TEMPEST] = STARGATE
		self.build_structures[CARRIER] = STARGATE
		self.build_structures[OBSERVER] = ROBOTICSFACILITY
		self.build_structures[IMMORTAL] = ROBOTICSFACILITY
		self.build_structures[WARPPRISM] = ROBOTICSFACILITY
		self.build_structures[COLOSSUS] = ROBOTICSFACILITY
		self.build_structures[DISRUPTOR] = ROBOTICSFACILITY
		self.build_structures[HIGHTEMPLAR] = GATEWAY
		self.build_structures[DARKTEMPLAR] = GATEWAY

	# Print my heuristics
	def print_heuristics(self):
		print(str(self.hr_static))
		print(str(self.hr_buildPriorities))
		print(str(self.hr_upgradePriorities))
		print(str(self.hr_unitRatio))
		print(str(self.hr_upgradeTime))
		print(str(self.hr_techTime))

	# Bot AI class startup async
	async def on_start_async(self):
		await self.chat_send("My name is Pylon! My parents were " + self.parent1_name + " with a score of " + str(self.parent1_score) + " and " + self.parent2_name + " with a score of " + str(self.parent2_score) + ".")
		await self.chat_send("(glhf)")

	# Bot AI class step async
	async def on_step(self, iteration):
		if(int(self.time) % 10 == 0):
			await self.distribute_workers()
		if(int(self.time) % 3 == 0):	
			await self.assess_builds()
		if(int(self.time) % 3 == 0):	
			await self.attempt_build()
		if(int(self.time) % 3 == 0):	
			await self.activate_abilities()
		if(int(self.time) % 15 == 0) and self.supply_army > 0:
			await self.amass()
		if(int(self.time) % 3 == 0) and self.supply_army > 0:
			await self.attack()
		if(int(self.time) % 180 == 0) and self.known_enemy_structures.amount == 0:
			await self.scout()

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
		if self.getUnitCount(PROBE) < self.hr_static['workersPerBase'] * self.units(NEXUS).amount:
			self.buildPlans.enqueue(PROBE, self.hr_buildPriorities[PROBE])

		# Assess pylons using heurustic threshold approaching max supply
		if self.supply_left < self.hr_static['supplyTrigger'] and not self.already_pending(PYLON) and not self.buildPlans.contains(PYLON):
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
		if (self.time / self.hr_static['expansionTime']) > self.getUnitCount(NEXUS):
			self.buildPlans.enqueue(NEXUS, self.hr_buildPriorities[NEXUS])

		# Assess assimilator build by checking for empty gas by Nexus
		openGeyserCount = 0
		for nexus in self.units(NEXUS).ready:
			for vespene in self.state.vespene_geyser.closer_than(self.hr_static['gasDetector'], nexus):
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
		self.assess_army(ADEPT, [GATEWAY, CYBERNETICSCORE])
		self.assess_army(VOIDRAY, [STARGATE])
		self.assess_army(PHOENIX, [STARGATE])
		self.assess_army(ORACLE, [STARGATE])
		self.assess_army(TEMPEST, [STARGATE, FLEETBEACON])
		self.assess_army(CARRIER, [STARGATE, FLEETBEACON])
		self.assess_army(OBSERVER, [ROBOTICSFACILITY])
		self.assess_army(IMMORTAL, [ROBOTICSFACILITY])
		self.assess_army(WARPPRISM, [ROBOTICSFACILITY])
		self.assess_army(COLOSSUS, [ROBOTICSFACILITY, ROBOTICSBAY])
		#self.assess_army(DISRUPTOR, [ROBOTICSFACILITY, ROBOTICSBAY])
		self.assess_army(HIGHTEMPLAR, [GATEWAY, TWILIGHTCOUNCIL, TEMPLARARCHIVE])
		self.assess_army(DARKTEMPLAR, [GATEWAY, TWILIGHTCOUNCIL, DARKSHRINE])

		self.assess_upgrades()

		# Escape case for misplaced pylons
		if self.minerals > 750:

			if self.supply_left > 20 and self.units(GATEWAY).ready.idle.amount > 0:

				self.buildPlans.enqueue(ZEALOT, 90)

			else:

				self.buildPlans.enqueue(PYLON, 100)

			for nexus in self.units(NEXUS).ready.idle:
				self.buildPlans.enqueue(PROBE, 90)

		# Escape case for confusion
		if self.minerals > 1000 and self.vespene > 1000:

			await self.chat_send("If you see this message I got confused. help.")
			print(self.buildPlans)


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
		if unit in self.hr_unitRatio:
			structures = self.units(self.build_structures[unit]).ready.idle
			if structures:
				await self.do(structures.first.train(unit))
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
			vespenes = self.state.vespene_geyser.closer_than(self.hr_static['gasDetector'], nexus)
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
		if self.supply_army < self.hr_static['attackSupply']:
			for s in self.units.of_type(self.armyUnits):
				if not s.is_attacking:
					await self.do(s.move(self.main_base_ramp.top_center))

	# Method to make attack decisions
	async def attack(self):
		if self.supply_army > self.hr_static['attackSupply']:
			for s in self.units.of_type(self.armyUnits):
				if not s.is_attacking:
					await self.do(s.attack(self.find_target(self.state)))

		elif self.supply_army > self.hr_static['defendSupply']:
			if len(self.known_enemy_units) > 0:
				nearest_enemy = self.enemy_near_nexus()
				if nearest_enemy[0] < self.hr_static['defendDistance']:
					for s in self.units.of_type(self.armyUnits):
						if not s.is_attacking:
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

	# Method to scout expansion locations if we don't see an enemy
	async def scout(self):

		if self.known_enemy_structures.amount == 0:

			if self.units(PROBE).amount != 0:

				haveScout = False

				for probe in self.units(PROBE):

					if probe.is_attacking:

						haveScout = True

				if not haveScout:

					scoutProbe = self.units(PROBE).prefer_idle.first

					await self.do(scoutProbe.attack(self.enemy_start_locations[0], True))

					for base in self.expansion_locations:

						await self.do(scoutProbe.attack(base, True))

	# Handler for activating unit abilities in combat
	async def activate_abilities(self):
		
		# Handle sentry abilities
		for sentry in self.units(SENTRY):
			if sentry.is_attacking and sentry.energy >= 75:
				await self.do(sentry(GUARDIANSHIELD_GUARDIANSHIELD))

	# Generate pylon placement position
	def generate_pylon_position(self):

		return self.units(NEXUS).random.position.to2.random_on_distance(self.hr_static['buildDistance'])

	# Return expected number of gateways
	def get_gateway_multiplier(self):

		return self.hr_static['gatewayConstant'] + (self.hr_static['gatewayCoeffecient'] * (self.units(NEXUS).amount - 1))

	# Return expected number of stargates
	def get_stargate_multiplier(self):

		return self.hr_static['stargateConstant'] + (self.hr_static['stargateCoeffecient'] * (self.units(NEXUS).amount - 1))

	# Return expected number of robotic facilities
	def get_robotics_multiplier(self):

		return self.hr_static['roboticsConstant'] + (self.hr_static['roboticsCoeffecient'] * (self.units(NEXUS).amount - 1))

	# On end of game, save to population
	def on_end(self, game_result):
		self.score = self.state.score.score
		self.buildPlans = None
		self.armyUnits = None
		self.pendingUpgrades = None

		c = Chevron()
		c.copy_pylon(self)
		c.commit()