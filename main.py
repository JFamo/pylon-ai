import sc2
from sc2 import run_game, maps, Race, Difficulty
from sc2.player import Bot, Computer
from sc2.constants import NEXUS, PROBE, PYLON, GATEWAY, ZEALOT

class Pylon_AI(sc2.BotAI):

	supplyTrigger = 5

	async def on_step(self, iteration):
		await self.distribute_workers()
		await self.build_workers()
		await self.build_pylons()
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
		if self.supply_left < self.supplyTrigger and not self.already_pending(PYLON):
			nexuses = self.units(NEXUS).ready
			if nexuses.exists:
				if self.can_afford(PYLON):
					await self.build(PYLON, near=nexuses.first)

	async def build_gateways(self):
		pylons = self.units(PYLON).ready
		if pylons.exists:
			if self.can_afford(GATEWAY):
				await self.build(GATEWAY, near=pylons.first)

run_game(maps.get("TritonLE"), [
	    Bot(Race.Protoss, Pylon_AI()),
	    Computer(Race.Terran, Difficulty.Easy)
	], realtime=True)