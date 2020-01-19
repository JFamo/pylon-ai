import sc2
from sc2 import run_game, maps, Race, Difficulty
from sc2.player import Bot, Computer
from sc2.constants import NEXUS, PROBE, PYLON, GATEWAY, ZEALOT

class Pylon_AI(sc2.BotAI):

	# Heuristics
	hr_supplyTrigger = 5
	hr_gatewayMultiplier = 3
	hr_expansionTime = 240 # Expansion time in seconds
<<<<<<< HEAD
	hr_workersPerBase = 24
	hr_buildPriorities = {"PROBE": 1, "NEXUS": 10, "PYLON": 4, "GATEWAY": 3, "ZEALOT": 2} # This should be situational, generalize for now
=======
	hr_buildPriorities = {"PROBE": 0, "NEXUS": 10, "PYLON": 3, "GATEWAY": 2, "ZEALOT": 1} # This should be situational, generalize for now
>>>>>>> parent of 4ad5183... Implement queue-based building

	# Local Vars
	buildPlans = Queue()

	async def on_step(self, iteration):
		await self.distribute_workers()
<<<<<<< HEAD
		await self.assess_builds()
		await self.attempt_build()

	async def attempt_build(self):
		print(self.can_afford(self.buildPlans.peek()))
		if(self.can_afford(self.buildPlans.peek())):
			thisUnit = self.buildPlans.dequeue()
			print("trying build unit : " + thisUnit)
			await self.build_unit(thisUnit)

	async def assess_builds(self):
		# Assess workers using multiplier by num of bases
		if len(self.units(PROBE)) + self.buildPlans.countOf(PROBE) < self.hr_workersPerBase * len(self.units(NEXUS)):
			self.buildPlans.enqueue(PROBE, self.hr_buildPriorities["PROBE"])
			print(self.buildPlans)
		# Assess pylons using heurustic threshold approaching max supply
		if self.supply_left < self.hr_supplyTrigger and not self.already_pending(PYLON) and not self.buildPlans.contains(PYLON):
			self.buildPlans.enqueue(PYLON, self.hr_buildPriorities["PYLON"])
			print(self.buildPlans)
		# Assess gateways checking for complete pylon and using heuristic threshold based on num of bases
		pylons = self.units(PYLON).ready
		if pylons.exists:
			if len(self.units(GATEWAY)) + self.buildPlans.countOf(GATEWAY) < (self.hr_gatewayMultiplier * len(self.units(NEXUS))):
				self.buildPlans.enqueue(GATEWAY, self.hr_buildPriorities["GATEWAY"])
				print(self.buildPlans)
		# Assess expansion by checking heuristic predictive expansion time
		if (self.time / self.hr_expansionTime) > len(self.units(NEXUS)) + self.buildPlans.countOf(NEXUS):
			self.buildPlans.enqueue(NEXUS, self.hr_buildPriorities["NEXUS"])
			print(self.buildPlans)

	# Generic method to handle dequeuing unit from build plans
	async def build_unit(self, unit):
		if(unit == PROBE):
			await self.do(self.units(NEXUS).ready.first.train(PROBE))
		if(unit == PYLON):
			await  self.build_pylons()
		if(unit == GATEWAY):
			await self.build(GATEWAY, near=self.units(PYLON).ready.first)
		if(unit == NEXUS):
			await self.expand_now()

	# Method to place and build pylons or nexus if required
=======
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

>>>>>>> parent of 4ad5183... Implement queue-based building
	async def build_pylons(self):
		if self.supply_left < self.hr_supplyTrigger and not self.already_pending(PYLON):
			nexuses = self.units(NEXUS).ready
			if nexuses.exists:
<<<<<<< HEAD
				await self.build(PYLON, near=nexuses.first)
			elif not self.buildPlans.contains(NEXUS):
				self.buildPlans.enqueue(NEXUS, self.hr_buildPriorities["NEXUS"])
=======
				if(self.buildPriority < self.hr_buildPriorities["PYLON"]):
					self.buildPriority = self.hr_buildPriorities["PYLON"]
				if self.can_afford(PYLON) and self.hr_buildPriorities["PYLON"] >= self.buildPriority:
					self.buildPriority = 0
					await self.build(PYLON, near=nexuses.first)

	async def build_gateways(self):
		pylons = self.units(PYLON).ready
		if pylons.exists:
			if len(self.units(GATEWAY)) < (self.hr_gatewayMultiplier * len(self.units(NEXUS))):
				if(self.buildPriority < self.hr_buildPriorities["GATEWAY"]):
					self.buildPriority = self.hr_buildPriorities["GATEWAY"]
				if self.can_afford(GATEWAY) and self.hr_buildPriorities["GATEWAY"] >= self.buildPriority:
					self.buildPriority = 0
					await self.build(GATEWAY, near=pylons.first)

	async def expand(self):
		if (self.time / self.hr_expansionTime) > len(self.units(NEXUS)):
			if(self.buildPriority < self.hr_buildPriorities["NEXUS"]):
				self.buildPriority = self.hr_buildPriorities["NEXUS"]
			if self.can_afford(NEXUS) and self.hr_buildPriorities["NEXUS"] >= self.buildPriority:
				self.buildPriority = 0
				await self.expand_now()
>>>>>>> parent of 4ad5183... Implement queue-based building

run_game(maps.get("TritonLE"), [
		Bot(Race.Protoss, Pylon_AI()),
		Computer(Race.Terran, Difficulty.Easy)
	], realtime=True)

class Queue():

	self.tail = None
	self.head = None

class Node:

	def __init__(self, value):
		self.value = value  
		self.next = None 
	
	def __str__(self):
		return "Node({})".format(self.value) 

	__repr__ = __str__

class Queue:

	def __init__(self):
		self.head=None
		self.tail=None
		self.count=0

	def __str__(self):
		temp=self.head
		out=[]
		while temp:
			out.append(str(temp.value))
			temp=temp.next
		out=' '.join(out)
		return f'Head:{self.head}\nTail:{self.tail}\nQueue:{out}'

	__repr__=__str__

	def isEmpty(self):

		# Use length to get whether we are empty
		if self.count == 0 :
			return True
		else :
			return False

	def enqueue(self, x):

		# Create node
		newNode = Node(x)

		# Case for first node
		if self.count == 0:
			self.head = newNode
		else:
			self.tail.next = newNode
		
		self.tail = newNode

		# Update count
		self.count += 1

	def dequeue(self):

		# Check list size, cases for last removal and empty list
		if self.count == 0 :
			return None # NOTE the two different doctests provided use 'queue is empty' and none here, not sure which is correct for prompt
		elif self.count == 1 :
			returnValue = self.head.value
			self.head = None
			self.tail = None
			self.count = 0
			return returnValue
		else:
			returnValue = self.head.value
			self.head = self.head.next
			self.count -= 1
			return returnValue

	def __len__(self):

		return self.count

	def reverse(self): 

		# We do not need to reverse length 1 or less
		if self.count > 1 :

			# Save all elements to list
			nodeList = []
			thisNode = self.head

			while(thisNode.next):
				nodeList.append(thisNode)
				if thisNode.next == self.tail:
					nodeList.append(self.tail)
					break
				thisNode = thisNode.next

			# Iterate and re-build
			for index in range(self.count - 1, -1, -1):
				nodeList[index].next = nodeList[index-1]

			# Set new head and tail
			self.tail = nodeList[0]
			self.tail.next = None
			self.head = nodeList[self.count - 1]

	def contains(self, item):

		# Handle empty queue
		if(self.count == 0):
			return False

		# Iterate and search for value
		thisNode = self.head
		while(thisNode.next):
			if(thisNode.value == item):
				return True
			else:
				thisNode = thisNode.next

		# Check tail
		if(self.tail.value == item):
			return True

		# Except false
		return False
