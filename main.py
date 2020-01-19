import sc2
from sc2 import run_game, maps, Race, Difficulty
from sc2.player import Bot, Computer
from sc2.constants import NEXUS, PROBE, PYLON, GATEWAY, ZEALOT

class Pylon_AI(sc2.BotAI):

	# Heuristics
	hr_supplyTrigger = 5
	hr_gatewayMultiplier = 3
	hr_expansionTime = 240 # Expansion time in seconds
	hr_buildPriorities = {"PROBE": 0, "NEXUS": 10, "PYLON": 3, "GATEWAY": 2, "ZEALOT": 1} # This should be situational, generalize for now

	# Local Vars
	buildPriority = 0

	async def on_step(self, iteration):
		await self.distribute_workers()
		await self.build_workers()
		await self.build_pylons()
		await self.expand()
		await self.build_gateways()
		await self.build_zealots()

	async def build_workers(self):
		for nexus in self.units(NEXUS).ready.noqueue:
			if self.can_afford(PROBE) and self.hr_buildPriorities["PROBE"] >= self.buildPriority:
				await self.do(nexus.train(PROBE))

	async def build_zealots(self):
		for gateway in self.units(GATEWAY).ready.noqueue:
			if self.can_afford(ZEALOT) and self.hr_buildPriorities["ZEALOT"] >= self.buildPriority:
				await self.do(gateway.train(ZEALOT))

	async def build_pylons(self):
		if self.supply_left < self.hr_supplyTrigger and not self.already_pending(PYLON):
			nexuses = self.units(NEXUS).ready
			if nexuses.exists:
				if(self.buildPriority < self.hr_buildPriorities["PYLON"]):
					self.buildPriority = self.hr_buildPriorities["PYLON"]
				if self.can_afford(PYLON) and self.hr_buildPriorities["PYLON"] >= self.buildPriority:
					await self.build(PYLON, near=nexuses.first)
					self.buildPriority = 0

	async def build_gateways(self):
		pylons = self.units(PYLON).ready
		if pylons.exists:
			if len(self.units(GATEWAY)) < (self.hr_gatewayMultiplier * len(self.units(NEXUS))):
				if(self.buildPriority < self.hr_buildPriorities["GATEWAY"]):
					self.buildPriority = self.hr_buildPriorities["GATEWAY"]
				if self.can_afford(GATEWAY) and self.hr_buildPriorities["GATEWAY"] >= self.buildPriority:
					await self.build(GATEWAY, near=pylons.first)
					self.buildPriority = 0

	async def expand(self):
		if (self.time / self.hr_expansionTime) > len(self.units(NEXUS)):
			if(self.buildPriority < self.hr_buildPriorities["NEXUS"]):
				self.buildPriority = self.hr_buildPriorities["NEXUS"]
			if self.can_afford(NEXUS) and self.hr_buildPriorities["NEXUS"] >= self.buildPriority:
				await self.expand_now()
				self.buildPriority = 0

run_game(maps.get("TritonLE"), [
	    Bot(Race.Protoss, Pylon_AI()),
	    Computer(Race.Terran, Difficulty.Easy)
	], realtime=True)