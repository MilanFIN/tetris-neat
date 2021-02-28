from tetris import *
import os
import neat
import time
import pickle
import sys





def simulate(game, pos, rot, version):
	state = False
	state2 = False
	if (version == "small"):
		state = game.board.simulateDrop(pos, rot)
		state2 =  []
	elif (version == "big"):
		state = []
		state2 =  game.board.simulateDrop2(pos, rot)
	elif (version == "superbig"):
		state = game.board.simulateDrop(pos, rot)
		state2 =  game.board.simulateDrop2(pos, rot)

	if (state == False or state2 == False):
		return False
	else:
		return state+state2


def playGameWithGenome(genome, config, game, version):
	net = neat.nn.FeedForwardNetwork.create(genome, config)
	game.reset()
	failed = False
	while (not failed):
		state = game.getState()

		directions = [-6,-5,-4,-3,-2,-1,0,1,2,3,4,5,6]
		orientations = [0,1,2,3]
		choises = {}
		for i in directions:
			for j in orientations:
				simulatedState = simulate(game, i, j, version)
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
			game.draw()
			time.sleep(0.02)
			failed = game.gameover()


def run(config_file, model, version):
	config = neat.Config(neat.DefaultGenome, neat.DefaultReproduction,
						neat.DefaultSpeciesSet, neat.DefaultStagnation,
						config_file)

	winner2 = pickle.load( open(model , 'rb' ))
	game = Game()
	while (True):
		playGameWithGenome(winner2, config, game, version)




def main(args):
	if (len(sys.argv) < 2):
		print("usage: python3 test.py <version(small/big/superbig)>")
		return
	version = sys.argv[1]
	

	if (version == "small"):
		local_dir = os.path.dirname(__file__)
		config_path = os.path.join(local_dir+"/config/", 'config-feedforward-small')
		model = "./models/small.pkl"
	elif (version == "big"):
		local_dir = os.path.dirname(__file__)
		config_path = os.path.join(local_dir+"/config/", 'config-feedforward-big')
		model = "./models/big.pkl"
	elif (version == "superbig"):
		local_dir = os.path.dirname(__file__)
		config_path = os.path.join(local_dir+"/config/", 'config-feedforward-superbig')
		model = "./models/superbig.pkl"

	else:
		print("usage: python3 test.py <version(small/big/superbig)>")
		return

	run(config_path, model, version)


if __name__ == '__main__':

	main(sys.argv)
