

import multiprocessing
import os
from tetris import *
import pickle
import neat


#configurable parameters:
#use 0, to use all available cores automatically
CORES = 0
#number of generations for training
GENERATIONS = 100
#which version to train on
#small/big/superbig
VERSION = "big"

#small = only using 5 properties derived from the gamestate
#big = using the actual state of the board, (10x20 array)
#superbig = combined input vector from both



def simulate(game, pos, rot):
	state = False
	state2 = False
	if (VERSION == "small"):
		state = game.board.simulateDrop(pos, rot)
		state2 =  []
	elif (VERSION == "big"):
		state = []
		state2 =  game.board.simulateDrop2(pos, rot)
	elif (VERSION == "superbig"):
		state = game.board.simulateDrop(pos, rot)
		state2 =  game.board.simulateDrop2(pos, rot)

	if (state == False or state2 == False):
		return False
	else:
		return state+state2


	
def eval_genome(genome, config):

	game = Game(False)
	fitness = 0
	net = neat.nn.FeedForwardNetwork.create(genome, config)

	for i in range(3):
		game.reset()
		failed = False
		while (not failed):
			#slicing, as no need to know current rotation
			state = game.getState()

			directions = [-6,-5,-4,-3,-2,-1,0,1,2,3,4,5,6]
			orientations = [0,1,2,3]
			choises = {}
			for i in directions:
				for j in orientations:
					simulatedState = simulate(game, i, j)
					if (simulatedState != False):
						choises[i, j] = simulatedState

			for i in choises:
				stateList = choises[i]
				score = net.activate(stateList)[0]
				choises[i] = score

			#find the pos/rot with the highest score
			bestPair = None
			bestScore = None
			for i in choises:
				if (bestScore == None):
					bestPair = i
					bestScore = choises[i]
				elif (choises[i] > bestScore):
					bestPair = i
					bestScore = choises[i]
			if (bestPair == None):
				bestPair = (0,0)
			goalPosition = game.board.spawnPoint[0] + bestPair[0]
			goalRotation = bestPair[1]

			#print(goalPosition)
			#goalState = net.activate(state[:-2] )

			while (not game.newBlock() and not failed):
				state = game.getState()
				position = state[0] #x position
				rotation = state[1] #rotation
				#need to rotate to reach same rotation
				
				if (rotation != goalRotation): 
					game.command("rotate")
				if (position > goalPosition):
					game.command("left")
				elif (position < goalPosition):
					game.command("right")

				

				game.tick()
				failed = game.gameover()


			if (game.getScore() > 40000):
				failed = True

		score = game.getScore()
		fitness += score
	fitness = fitness / 3


	return fitness




def run(config_file):
	# Load configuration.
	config = neat.Config(neat.DefaultGenome, neat.DefaultReproduction,
						neat.DefaultSpeciesSet, neat.DefaultStagnation,
						config_file)

	p = neat.Population(config)


	p.add_reporter(neat.StdOutReporter(True))
	stats = neat.StatisticsReporter()
	p.add_reporter(stats)

	corecount = 1
	if (CORES == 0):
		corecount = multiprocessing.cpu_count()
	else:
		corecount = CORES
	pe = neat.ParallelEvaluator(corecount, eval_genome)
	# Run for up to x generations.
	winner = p.run(pe.evaluate, GENERATIONS)

	#save winning version

	pickle.dump( winner , open( './models/model.pkl' , 'wb' ) )

	

if __name__ == '__main__':
	# Determine path to configuration file. This path manipulation is
	# here so that the script will run successfully regardless of the
	# current working directory.
	local_dir = os.path.dirname(__file__)

	if (VERSION == "small"):
		config_path = os.path.join("./config/", 'config-feedforward-small')
	elif (VERSION == "big"):
		config_path = os.path.join("./config/", 'config-feedforward-big')
	elif (VERSION == "superbig"):
		config_path = os.path.join("./config/", 'config-feedforward-superbig')

	run(config_path)
