import sc2
from queue import *
from sc2 import run_game, maps, Race, Difficulty
from sc2.player import Bot, Computer
from sc2.constants import NEXUS, PROBE, PYLON, GATEWAY, ZEALOT, ASSIMILATOR
from sc2.game_data import AbilityData, GameData
from sc2.unit import Unit
from sc2.units import Units

class Pylon_AI(sc2.BotAI):

	# Heuristics
	hr_supplyTrigger = 5
	hr_gatewayMultiplier = 2
	hr_expansionTime = 240 # Expansion time in seconds
	hr_workersPerBase = 22
	hr_zealotratio = 0.5
	hr_buildPriorities = {"PROBE": 1, "NEXUS": 10, "PYLON": 4, "GATEWAY": 3, "ZEALOT": 1, "ASSIMILATOR": 2} # This should be situational, generalize for now

	# Local Vars
	buildPlans = Queue()

	async def on_step(self, iteration):
		await self.distribute_workers()
		await self.assess_builds()
		await self.attempt_build()

	async def attempt_build(self):
		if(len(self.buildPlans) > 0):
			if(self.can_afford(self.buildPlans.peek())):
				await self.build_unit(self.buildPlans.dequeue())

	def getUnitCount(self, unit):
		return len(self.units(unit)) + self.buildPlans.countOf(unit)

	async def assess_builds(self):

		# Assess workers using multiplier by num of bases
		if self.getUnitCount(PROBE) < self.hr_workersPerBase * len(self.units(NEXUS)):
			self.buildPlans.enqueue(PROBE, self.hr_buildPriorities["PROBE"])

		# Assess pylons using heurustic threshold approaching max supply
		if self.supply_left < self.hr_supplyTrigger and not self.already_pending(PYLON) and not self.buildPlans.contains(PYLON):
			self.buildPlans.enqueue(PYLON, self.hr_buildPriorities["PYLON"])

		# Assess gateways checking for complete pylon and using heuristic threshold based on num of bases
		pylons = self.units(PYLON).ready
		if pylons.exists:
			if self.getUnitCount(GATEWAY) < (self.hr_gatewayMultiplier * len(self.units(NEXUS))):
				self.buildPlans.enqueue(GATEWAY, self.hr_buildPriorities["GATEWAY"])

		# Assess expansion by checking heuristic predictive expansion time
		if (self.time / self.hr_expansionTime) > self.getUnitCount(NEXUS):
			self.buildPlans.enqueue(NEXUS, self.hr_buildPriorities["NEXUS"])

		# Assess zealot build by checking heuristic for army composition
		if self.units(GATEWAY).ready.exists:
			if (self._game_data.units[ZEALOT.value]._proto.food_required * self.getUnitCount(ZEALOT)) / self.supply_cap < self.hr_zealotratio :
				self.buildPlans.enqueue(ZEALOT, self.hr_buildPriorities["ZEALOT"])

		# Assess assimilator build by checking for empty gas by Nexus
		for nexus in self.units(NEXUS).ready:
			vespenes = self.state.vespene_geyser.closer_than(25.0, nexus)
			if(len(vespenes) > self.buildPlans.countOf(ASSIMILATOR)):
				self.buildPlans.enqueue(ASSIMILATOR, self.hr_buildPriorities["ASSIMILATOR"])

	# Generic method to handle dequeuing unit from build plans
	async def build_unit(self, unit):
		if(unit == PROBE):
			nexuses = self.units(NEXUS).ready.idle
			if nexuses:
				await self.do(nexuses.first.train(PROBE))
		if(unit == PYLON):
			await  self.build_pylons()
		if(unit == GATEWAY):
			await self.build(GATEWAY, near=self.units(PYLON).ready.first)
		if(unit == NEXUS):
			await self.expand_now()
		if(unit == ZEALOT):
			gateways = self.units(GATEWAY).ready.idle
			if gateways:
				await self.do(gateways.first.train(ZEALOT))
		if(unit == ASSIMILATOR):
			await self.build_assimilator()

	# Method to place and build pylons or nexus if required
	async def build_pylons(self):
			nexuses = self.units(NEXUS).ready
			if nexuses.exists:
				await self.build(PYLON, near=self.main_base_ramp.top_center)
			elif not self.buildPlans.contains(NEXUS):
				self.buildPlans.enqueue(NEXUS, self.hr_buildPriorities["NEXUS"])
				print(self.buildPlans)

	# Method to build gas on open geyser
	async def build_assimilator(self):
		for nexus in self.units(NEXUS).ready:
			vespenes = self.state.vespene_geyser.closer_than(25.0, nexus)
			for vespene in vespenes:
				worker = self.select_build_worker(vespene.position)
				if worker is None:
					break
				if not self.units(ASSIMILATOR).closer_than(1.0, vespene).exists:
					await self.do(worker.build(ASSIMILATOR, vespene))

run_game(maps.get("TritonLE"), [
		Bot(Race.Protoss, Pylon_AI()),
		Computer(Race.Terran, Difficulty.Easy)
	], realtime=True)

