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
			return None
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

	def peek(self):

		if self.count == 0 :
			return None
		else:
			return self.head.value

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

	def countOf(self, item):

		# Handle empty queue
		if(self.count == 0):
			return 0

		self.counter = 0

		# Iterate and search for value
		thisNode = self.head
		while(thisNode.next):
			if(thisNode.value == item):
				self.counter += 1
			thisNode = thisNode.next

		# Check tail
		if(self.tail.value == item):
			self.counter += 1

		# Except false
		return self.counter