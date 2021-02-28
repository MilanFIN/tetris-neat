import os
import time
import pygame

import random
import copy



#TODO:


pygame.init()

WIDTH = 300
HEIGHT = 600

BOARDWIDTH = 10
BOARDHEIGHT = 20

class Block():
	def __init__(self, x, y, color, center=(0,0)):
		self.size = 30
		self.border = 1 #pixels
		self.borderDarkness = 0.5
		self.x = x
		self.y = y
		self.centerX = center[0]
		self.centerY = center[1]


		self.colorString = color

		if (color == "yellow"):
			self.color = (255, 255, 0)
		elif (color == "red"):
			self.color = (255, 0,0)
		elif (color == "green"):
			self.color = (0,255,0)
		elif (color == "blue"):
			self.color = (0,0,255)
		elif (color == "violet"):
			self.color = (127,0,255)
		elif (color == "orange"):
			self.color = (255,140,0)
		elif (color == "cyan"):
			self.color = (0,255,255)
		else:
			self.color = (100,100,100)

	def rotateAroundCenter(self):
		x = self.x - self.centerX
		y = self.y - self.centerY
		self.x = -y + self.centerX
		self.y = x + self.centerY

		self.x = int(self.x)
		self.y = int(self.y)

	def draw(self, screen):
		borderColor = tuple([self.borderDarkness*x for x in self.color])
		pygame.draw.rect(screen, borderColor, (self.x*self.size, self.y*self.size, self.size, self.size))
		
		pygame.draw.rect(screen, self.color, (self.x*self.size + self.border, self.y*self.size + self.border, self.size - 2*self.border, self.size - 2*self.border))
class Board():
	def __init__(self):
		#finess related stuff
		self.linesCleared = 0
		self.blocksAdded = 0
		self.surroundingBlocks = 0

		self.blocks = []
		self.shapeMid = [0,0] #x,y
		self.shapesSpawned = 0


		for x in range(0, 10):
			for y in range(20, 21):
				self.blocks.append(Block(x, y, "gray"))

		self.blockMap = {}
		self.resetBlockMap()
		
		self.spawnPoint = (4,1) #x,y

		self.shapeType = 0
		self.shape = self.makeShape()

		self.shapeRotation = 0
		self.gameover = False

		#stuff related to rating moves
		self.tickDone = False
		self.previousHeight = 0


	def resetBlockMap(self):
		self.blockMap = {}
		for i in self.blocks:
			self.blockMap[(i.x, i.y)] = 1


	def countVerticalLines(self):
		lines = 0
		for x in range(BOARDWIDTH):
			lineLength = 0
			for y in range(BOARDHEIGHT):
				if ((x, y) in self.blockMap):
					lineLength = 0
				else:
					lineLength += 1
				if (lineLength >= 3):
					lines += 1
					lineLength = 0
		return lines

	def getHeight(self, blockMap):
		y = 20
		for i in blockMap.keys():
			if (i[1] < y):
				y = i[1]
		return y
	def countHoles(self, blockMap):
		#counts all free spots that are covered by a block 
		#from above
		"""
		holes = 0
		for x in range(0, 10):
			for y in range(0, 20):
				if ((x, y) in blockMap):
					holes += 1
		return holes
		"""
		holes = 0
		for x in range(0,10):
			for y in range(0, 20):
				if (not (x, y) in blockMap):
					#found a free spot, should check if there is a
					#block somewhere above it shading it
					shaded = False
					for i in range(y, 0, -1):
						if ((x, i) in blockMap):
							shaded = True
							break
					if (shaded):
						holes += 1
		return holes


	def countHLines(self, blockMap):
		lines = 0
		for y in range(0,20):
			line = True
			for x in range(0, 10):
				if (not (x, y) in blockMap):
					line = False
			if (line):
				lines += 1
		return lines
	#total vertical variability by column
	def getRoughness(self, blockMap):
		#find highest points in each column
		heights = [20]*10 #20 is the bottom row coordinate
		for y in range(0,20):
			for x in range (0, 10):
				if ((x, y) in blockMap):
					if (y < heights[x]):
						heights[x] = y
		#count total height difference between columns
		gain = 0
		for i in range(1, 10):
			gain += abs(heights[i] - heights[i-1] )
		return gain
	
	def countSurroundingBlocks(self, shape, blockMap):
		surrounding = {} #(x, y) = 1
		for i in shape:
			#check  left, right, down
			directions = [(i.x-1, i.y), (i.x-1, i.y), (i.x, i.y+1)] #(i.x, i.y-1), 
			for d in directions:
				if (d in blockMap):
					surrounding[d] = 1
				#include edges as surrounding blocks
				elif (d[0] == -1 or d[0] == 20):
					surrounding[d] = 1
		return len(surrounding.keys())

	#same as the next, but for 10x20 array representation of
	#the actual game state instead of a few properties
	def simulateDrop2(self, x, orientation):#

		blocks = copy.deepcopy(self.blockMap)
		shape = copy.deepcopy(self.shape)
		originalHeight = self.getHeight(blocks)
		originalHoles = self.countHoles(blocks)
		originalRoughness = self.getRoughness(blocks)
		#rotate x times based on orientation
		for i in shape:
			for j in range(orientation):
				i.rotateAroundCenter()
		#move to x direction
		for i in shape:
			i.x += x
			i.centerX += x
		#check if target position is inside play area
		legal = True
		for i in shape:
			if (i.x < 0 or i.x > 9):
				legal = False
				break
		#check if block can fit in the target position
		for i in shape:
			if ((i.x, i.y) in blocks):
				legal = False
		if (not legal):#illegal move, should return a false
			return False
		else:
			for i in range(0, 25):#moving down until touchdown
				touching = False
				for i in shape:
					if ((i.x, i.y+1) in blocks):
						touching = True
						break
				if (touching):
					break
				for i in shape:
					i.y += 1
			for i in shape:
				blocks[(i.x, i.y)] = 1

		stateArray = [[0]*20]*10
		for i in blocks:
			if (i[0] > -1 and i[0] < 10 and i[1] > -1 and i[1] < 20):
				stateArray[i[0]][i[1]] = 1

		stateVector = [item for sublist in stateArray for item in sublist]

		return stateVector


	def simulateDrop(self, x, orientation):#dir (x blocks left or right), orientation 0-3 (rotations)

		#self.simulateDrop2(x, orientation)

		blocks = copy.deepcopy(self.blockMap)
		shape = copy.deepcopy(self.shape)
		originalHeight = self.getHeight(blocks)
		originalHoles = self.countHoles(blocks)
		originalRoughness = self.getRoughness(blocks)
		#rotate x times based on orientation
		for i in shape:
			for j in range(orientation):
				i.rotateAroundCenter()
		#move to x direction
		for i in shape:
			i.x += x
			i.centerX += x
		#check if target position is inside play area
		legal = True
		for i in shape:
			if (i.x < 0 or i.x > 9):
				legal = False
				break
		#check if block can fit in the target position
		for i in shape:
			if ((i.x, i.y) in blocks):
				legal = False
		if (not legal):#illegal move, should return a false
			return False
		else:
			for i in range(0, 25):#moving down until touchdown
				touching = False
				for i in shape:
					if ((i.x, i.y+1) in blocks):
						touching = True
						break
				if (touching):
					break
				for i in shape:
					i.y += 1
			#now that the shape is touching the ground
			#check how many blocks it's touching directly
			surroundingBlocks = self.countSurroundingBlocks(shape, blocks)




			#add blocks in the shape to the static blocks
			for i in shape:
				blocks[(i.x, i.y)] = 1
			#check for height, amount of holes and amount of horizontal lines
			heightAdded = self.getHeight(blocks) - originalHeight
			holesAdded = self.countHoles(blocks) - originalHoles
			#dont have to detect originals as there can't be any when new block is added
			linesAdded = self.countHLines(blocks) 
			#check how much the block changes the surface roughness
			roughness = self.getRoughness(blocks) - originalRoughness

			#return [heightAdded, holesAdded, linesAdded, roughness, surroundingBlocks]
			return [heightAdded, holesAdded, linesAdded, roughness, surroundingBlocks]
	def getScore(self):
		return 1000*self.linesCleared + self.blocksAdded

	def makeShape(self):
		self.shapesSpawned += 1


		a = random.randint(0,6)
		points = []
		color = "gray"
		center = 0.0
		newType = 0
		if (a == 0):
			points = [(0,0), (0,1), (1,1), (1,0)]
			color = "yellow"
			center = (0.5,0.5)
		elif (a == 1):
			points = [(-1,0), (0,0), (1,0), (0,1)]
			center = (0,0)
			color = "violet"
		elif (a == 2):
			points = [(-1,-1),(0,-1),(0,0),(1,0)]
			center = (0,0)
			color = "red"
		elif (a == 3):
			points = [(-1,0),(0,0),(0,-1),(1,-1)]
			center = (0,0)
			color = "green"
		elif (a == 4):
			points = [(-1,0),(0,0),(1,0),(1,-1)]
			center = (0,0)
			color = "orange"
		elif (a == 5):
			points = [(-1,-1),(-1,0),(0,0),(1,0)]
			center = (0,0)
			color = "blue"
		elif (a == 6):
			points = [(-1,0),(0,0),(1,0),(2,0)]
			center = (0.5,0.5)
			color = "cyan"
		
		newType = a

		self.shapeType = newType
		shape = []
		for i in points:
			shape.append(Block(self.spawnPoint[0]+i[0], self.spawnPoint[1]+i[1], color,(self.spawnPoint[0]+center[0], self.spawnPoint[1]+center[1])))
		self.shapeMid = [self.spawnPoint[0], self.spawnPoint[1]]
		return shape


	def fixHeight(self):
		#check overlapping bottom
		while True:
			overlapping = False
			for i in self.shape:
				if ((i.x, i.y) in self.blockMap):
					overlapping = True
					break
			if (overlapping):
				for i in self.shape:
					i.y -= 1
					i.centerY -= 1
				self.shapeMid[1] -= 1
			else: 
				break



	def rotateShape(self):
		for i in self.shape:
			i.rotateAroundCenter()
		self.fixHeight
		self.shapeRotation = (self.shapeRotation + 1)%4

	def move(self, direction):
		clearToMove = True
		for i in self.shape:
			if (i.x + direction < 0 or i.x + direction >= BOARDWIDTH):
				clearToMove = False
			for b in self.blocks:
				if (b.x == i.x + direction and b.y == i.y):
					clearToMove = False
		if (clearToMove):
			for i in self.shape:
				i.x += direction
				i.centerX += direction
			self.shapeMid[0] += direction

	def moveLeft(self):
		self.move(-1)
	
	def moveRight(self):
		self.move(1)

	def moveDown(self, ticks):
		if (ticks <= 0):
			return
		clearToMove = True
		for i in self.shape:
			for b in self.blocks:
				if (b.x == i.x and b.y == i.y + 1):
					clearToMove = False
		if (clearToMove):
			for i in self.shape:
				i.y += 1
				i.centerY += 1
			self.shapeMid[1] += 1

	def removeLine(self, y):
		remainingBlocks = []
		for i in self.blocks:
			if (i.y != y):
				remainingBlocks.append(i)
		self.blocks = remainingBlocks

	def moveAboveDown(self, y):
		for i in self.blocks:
			if (i.y < y):
				i.y += 1
				i.centerY += 1

	def clearLines(self):
		for y in range(0, BOARDHEIGHT):
			blocksPerLine = 0
			for b in (self.blocks):
				if (b.y == y):
					blocksPerLine += 1
			if (blocksPerLine >= BOARDWIDTH):
				self.removeLine(y)
				self.moveAboveDown(y)
				self.linesCleared += 1	

				self.previousHeight = self.calculateHighPoint()
				
		self.resetBlockMap()		


	def getStateVector(self):
		#distance of middle of the block to each column
		columns = [21]*10
		for i in self.blocks:
			if (i.y < columns[i.x]):
				columns[i.x] = i.y
		for i in range(len(columns)):
			columns[i] -= self.shapeMid[1]
		
		#make average the zero level with actual values a difference from that
		avg = sum(columns)/len(columns)
		for i in range(len(columns)):
			columns[i] = columns[i] - avg


		return  [self.shapeMid[0], self.shapeRotation]


	def calculateHighPoint(self):
		highestYCoord = 20
		for i in self.blocks:
			if (i.y < highestYCoord):
				highestYCoord = i.y
		highPoint = 20-highestYCoord
		return highPoint

	def tick(self):

		#keep shape between left and right edge
		while True:
			outOfBounds = False
			for i in self.shape:
				if (i.x < 0):
					outOfBounds = True
			if (outOfBounds):
				for i in self.shape:
					i.x += 1
					i.centerX += 1
				self.shapeMid[0] += 1
			else: 
				break

		while True:
			outOfBounds = False
			for i in self.shape:
				if (i.x >= BOARDWIDTH):
					outOfBounds = True
			if (outOfBounds):
				for i in self.shape:
					i.x -= 1
					i.centerX -= 1
				self.shapeMid[0] -= 1
			else: 
				break


		for i in self.shape:
			pass
			i.y += 1 
			i.centerY += 1
		self.shapeMid[1] += 1
		pass


		self.fixHeight()

		for i in self.shape:
			if (i.y < -1):
				self.gameover = True
				return

		ex = False

		for shape in self.shape:
			if ex:
				break
			if ((shape.x, shape.y + 1) in self.blockMap):
				#scoring
				self.surroundingBlocks += self.countSurroundingBlocks(self.shape, self.blockMap)

				#should create new shape
				for i in self.shape:
					self.blocksAdded += 1
					self.blocks.append(Block(i.x, i.y, i.colorString))
					self.blockMap[(i.x, i.y)] = 1
					self.shape = self.makeShape()
					ex = True
		self.clearLines()


		self.tickDone = True

	

	def draw(self, screen):
		for block in self.blocks:
			block.draw(screen)
		for s in self.shape:
			s.draw(screen)


class Game():
	def __init__(self, graphics = True):
		pass
		if (graphics):
			self.screen = pygame.display.set_mode((WIDTH,HEIGHT))
			pygame.display.set_caption('tetris')

		self.board = Board()

		self.nextCommand = ""
		self.totalTicks = 5
		self.ticks = 5
		self.newShape = True
		self.shapeCount = self.board.shapesSpawned

	def getScore(self):
		return self.board.getScore()

	def reset(self):
		self.board = Board()

		self.nextCommand = ""
		self.totalTicks = 5
		self.ticks = 5
		self.newShape = True
		self.shapeCount = self.board.shapesSpawned


	def command(self, command):
		self.nextCommand = command

	def getState(self):
		return self.board.getStateVector()

	def newBlock(self):
		if (self.newShape): #initial
			self.newShape = False
			return True
		elif (self.shapeCount != self.board.shapesSpawned):
			self.shapeCount = self.board.shapesSpawned
			self.newShape = False
			return True
		else:
			return False

	def tick(self):
		if (not self.board.gameover):
			self.ticks -= 1
			if (self.nextCommand == "rotate"):
				self.board.rotateShape()
			if (self.nextCommand == "left"):
				self.board.moveLeft()
			if (self.nextCommand == "right"):
				self.board.moveRight()
			if (self.nextCommand == "down"):
				self.board.moveDown(self.ticks)
			if (self.ticks <= 0):
				self.board.tick()
				self.ticks = self.totalTicks
			self.nextCommand = ""
		else:
			print("gameover")
	def draw(self):
		self.screen.fill((0,0,0))
		self.board.draw(self.screen)
		pygame.display.flip()

	def gameover(self):
		return self.board.gameover
