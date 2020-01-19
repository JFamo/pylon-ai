import sc2
from sc2 import run_game, maps, Race, Difficulty
from sc2.player import Bot, Computer
from sc2.constants import NEXUS, PROBE

class Pylon_AI(sc2.BotAI):

	async def on_step(self, iteration):
		await self.distribute_workers()

run_game(maps.get("TritonLE"), [
	    Bot(Race.Protoss, Pylon_AI()),
	    Computer(Race.Terran, Difficulty.Easy)
	], realtime=True)