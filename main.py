import sc2
from sc2 import run_game, maps, Race, Difficulty
from sc2.player import Bot, Computer
from sc2.constants import NEXUS, PROBE, PYLON, GATEWAY, ZEALOT

class Pylon_AI(sc2.BotAI):

	# Heuristics
	hr_supplyTrigger = 5
	hr_gatewayMultiplier = 3
	hr_expansionTime = 240 # Expansion time in seconds
	hr_buildPriorities = {"PROBE": 1, "NEXUS": 10, "PYLON": 3, "GATEWAY": 2, "ZEALOT": 2} # This should be situational, generalize for now

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
			if self.can_afford(PROBE):
				await self.do(nexus.train(PROBE))

	async def build_zealots(self):
		for gateway in self.units(GATEWAY).ready.noqueue:
			if self.can_afford(ZEALOT):
				await self.do(gateway.train(ZEALOT))

	async def build_pylons(self):
		if self.supply_left < self.hr_supplyTrigger and not self.already_pending(PYLON):
			nexuses = self.units(NEXUS).ready
			if nexuses.exists:
				if self.can_afford(PYLON):
					await self.build(PYLON, near=nexuses.first)

	async def build_gateways(self):
		pylons = self.units(PYLON).ready
		if pylons.exists:
			if self.can_afford(GATEWAY) and len(self.units(GATEWAY)) < (self.hr_gatewayMultiplier * len(self.units(NEXUS))):
				await self.build(GATEWAY, near=pylons.first)

	async def expand(self):
		if self.can_afford(NEXUS) and (self.time / self.hr_expansionTime) > len(self.units(NEXUS)):
			await self.expand_now()

run_game(maps.get("TritonLE"), [
	    Bot(Race.Protoss, Pylon_AI()),
	    Computer(Race.Terran, Difficulty.Easy)
	], realtime=True)