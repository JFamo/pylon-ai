import sc2
from queue import *
from sc2 import run_game, maps, Race, Difficulty
from sc2.player import Bot, Computer
from sc2.constants import NEXUS, PROBE, PYLON, GATEWAY, ZEALOT
from sc2.game_data import AbilityData, GameData

class Pylon_AI(sc2.BotAI):

	# Heuristics
	hr_supplyTrigger = 5
	hr_gatewayMultiplier = 3
	hr_expansionTime = 240 # Expansion time in seconds
	hr_workersPerBase = 24
	hr_zealotratio = 0.5
	hr_buildPriorities = {"PROBE": 0, "NEXUS": 10, "PYLON": 3, "GATEWAY": 2, "ZEALOT": 1} # This should be situational, generalize for now

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
			if (self._game_data.units[ZEALOT]._proto.food_required * self.getUnitCount(ZEALOT)) / self.supply_cap < self.hr_zealotratio :
				self.buildPlans.enqueue(ZEALOT, self.hr_buildPriorities["ZEALOT"])

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
			await self.do(self.units(GATEWAY).ready.idle.first.train(ZEALOT))

	# Method to place and build pylons or nexus if required
	async def build_pylons(self):
			nexuses = self.units(NEXUS).ready
			if nexuses.exists:
				await self.build(PYLON, near=nexuses.first)
			elif not self.buildPlans.contains(NEXUS):
				self.buildPlans.enqueue(NEXUS, self.hr_buildPriorities["NEXUS"])
				print(self.buildPlans)

run_game(maps.get("TritonLE"), [
		Bot(Race.Protoss, Pylon_AI()),
		Computer(Race.Terran, Difficulty.Easy)
	], realtime=True)

