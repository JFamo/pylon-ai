import sc2
import random

from queue import *
from sc2 import run_game, maps, Race, Difficulty
from sc2.position import Point2
from sc2.player import Bot, Computer
from sc2.constants import *
from sc2.game_data import AbilityData, GameData
from sc2.ids.unit_typeid import UnitTypeId
from sc2.unit import Unit
from sc2.units import Units
from sc2.unit_command import UnitCommand

class Pylon_AI(sc2.BotAI):

	# Heuristics
	hr_supplyTrigger = 5
	hr_gatewayMultiplier = 2
	hr_expansionTime = 240 # Expansion time in seconds
	hr_workersPerBase = 22
	hr_unitRatio = {}
	hr_unitRatio[ZEALOT] = 0.25
	hr_unitRatio[STALKER] = 0.40
	hr_unitRatio[SENTRY] = 0.1
	hr_buildDistance = 10.0
	hr_attackSupply = 50
	hr_defendSupply = 10
	hr_gasDetector = 15.0
	hr_buildPriorities = {"PROBE": 1, "NEXUS": 10, "PYLON": 4, "GATEWAY": 3, "ZEALOT": 1, "SENTRY": 1, "STALKER": 1, "ASSIMILATOR": 2, "CYBERNETICSCORE": 5, "FORGE": 5} # This should be situational, generalize for now

	# Local Vars
	buildPlans = Queue()
	armyUnits = {UnitTypeId.ZEALOT, UnitTypeId.SENTRY, UnitTypeId.STALKER}

	async def on_step(self, iteration):
		await self.distribute_workers()
		await self.assess_builds()
		await self.attempt_build()
		await self.activate_abilities()
		await self.attack()

	async def attempt_build(self):
		if(len(self.buildPlans) > 0):
			if(self.can_afford(self.buildPlans.peek())):
				nextUnit = self.buildPlans.dequeue()
				await self.build_unit(nextUnit)

	def getUnitCount(self, unit):

		return self.units(unit).amount + self.buildPlans.countOf(unit) + self.already_pending(unit)

	async def assess_builds(self):

		# Assess workers using multiplier by num of bases
		if self.getUnitCount(PROBE) < self.hr_workersPerBase * self.units(NEXUS).amount:
			self.buildPlans.enqueue(PROBE, self.hr_buildPriorities["PROBE"])

		# Assess pylons using heurustic threshold approaching max supply
		if self.supply_left < self.hr_supplyTrigger and not self.already_pending(PYLON) and not self.buildPlans.contains(PYLON):
			self.buildPlans.enqueue(PYLON, self.hr_buildPriorities["PYLON"])

		# Assess gateways checking for complete pylon and using heuristic threshold based on num of bases
		pylons = self.units(PYLON).ready
		if pylons.exists:
			if self.getUnitCount(GATEWAY) < (self.hr_gatewayMultiplier * self.units(NEXUS).amount):
				self.buildPlans.enqueue(GATEWAY, self.hr_buildPriorities["GATEWAY"])

		# Assess expansion by checking heuristic predictive expansion time
		if (self.time / self.hr_expansionTime) > self.getUnitCount(NEXUS):
			self.buildPlans.enqueue(NEXUS, self.hr_buildPriorities["NEXUS"])

		# Assess zealot build by checking heuristic for army composition
		if self.units(GATEWAY).ready.exists:
			if (self._game_data.units[ZEALOT.value]._proto.food_required * self.getUnitCount(ZEALOT)) / self.supply_cap < self.hr_unitRatio[ZEALOT] :
				self.buildPlans.enqueue(ZEALOT, self.hr_buildPriorities["ZEALOT"])

		# Assess stalker build by checking heuristic for army composition
		if self.units(GATEWAY).ready.exists and self.units(CYBERNETICSCORE).ready.exists:
			if (self._game_data.units[STALKER.value]._proto.food_required * self.getUnitCount(STALKER)) / self.supply_cap < self.hr_unitRatio[STALKER] :
				self.buildPlans.enqueue(STALKER, self.hr_buildPriorities["STALKER"])

		# Assess sentry build by checking heuristic for army composition
		if self.units(GATEWAY).ready.exists and self.units(CYBERNETICSCORE).ready.exists:
			if (self._game_data.units[SENTRY.value]._proto.food_required * self.getUnitCount(SENTRY)) / self.supply_cap < self.hr_unitRatio[SENTRY] :
				self.buildPlans.enqueue(SENTRY, self.hr_buildPriorities["SENTRY"])

		# Assess assimilator build by checking for empty gas by Nexus
		openGeyserCount = 0
		for nexus in self.units(NEXUS).ready:
			for vespene in self.state.vespene_geyser.closer_than(25.0, nexus):
				if not self.units(ASSIMILATOR).closer_than(1.0, vespene).exists:
					openGeyserCount += 1
		if(openGeyserCount > self.buildPlans.countOf(ASSIMILATOR)):
			self.buildPlans.enqueue(ASSIMILATOR, self.hr_buildPriorities["ASSIMILATOR"])
		elif(self.buildPlans.peek() == ASSIMILATOR):
			self.buildPlans.dequeue()

		# Assess cybernetics core build
		if self.units(GATEWAY).ready.exists:
			if self.getUnitCount(CYBERNETICSCORE) < 1:
				self.buildPlans.enqueue(CYBERNETICSCORE, self.hr_buildPriorities["CYBERNETICSCORE"])

		# Assess forge build
		if self.units(GATEWAY).ready.exists:
			if self.getUnitCount(FORGE) < 1:
				self.buildPlans.enqueue(FORGE, self.hr_buildPriorities["FORGE"])

		# Escape case for misplaced pylons
		if self.minerals > 600:
			self.buildPlans.enqueue(PYLON, 100)

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
		if(unit == ASSIMILATOR):
			await self.build_assimilator()
		if(unit == CYBERNETICSCORE):
			await self.build(CYBERNETICSCORE, near=self.units(PYLON).ready.random)
		if(unit == FORGE):
			await self.build(FORGE, near=self.units(PYLON).ready.random)

	# Method to place and build pylons or nexus if required
	async def build_pylons(self):
			nexuses = self.units(NEXUS).ready
			if nexuses.exists:
				await self.build(PYLON, near=self.generate_pylon_position())
			elif not self.buildPlans.contains(NEXUS):
				self.buildPlans.enqueue(NEXUS, self.hr_buildPriorities["NEXUS"])
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
			return random.choice(self.known_enemy_units)
		elif len(self.known_enemy_structures) > 0:
			return random.choice(self.known_enemy_structures)
		else:
			return self.enemy_start_locations[0]

	# Method to make attack decisions
	async def attack(self):
		if self.supply_army > self.hr_attackSupply:
			for s in self.units.of_type(self.armyUnits):
				await self.do(s.attack(self.find_target(self.state)))

		elif self.supply_army > self.hr_defendSupply:
			if len(self.known_enemy_units) > 0:
				for s in self.units.of_type(self.armyUnits):
					await self.do(s.attack(random.choice(self.known_enemy_units)))

	async def activate_abilities(self):
		
		# Handle sentry abilities
		for sentry in self.units(SENTRY):
			if sentry.is_attacking and sentry.energy >= 75:
				await self.do(sentry(GUARDIANSHIELD_GUARDIANSHIELD))

	def generate_pylon_position(self):
		#if self.units(PYLON).amount == 0 :
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

run_game(maps.get("TritonLE"), [
		Bot(Race.Protoss, Pylon_AI()),
		Computer(Race.Terran, Difficulty.Medium)
	], realtime=True)

