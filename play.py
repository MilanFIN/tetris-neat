import os
import time
import pygame

from tetris import *






game = Game()

while True:
	events = pygame.event.get()
	for event in events:
		if event.type == pygame.KEYDOWN:
			if event.key == pygame.K_LEFT:
				game.command("left")
			elif event.key == pygame.K_RIGHT:
				game.command("right")
			elif (event.key == pygame.K_UP):
				game.command("rotate")
	if (pygame.key.get_pressed()[pygame.K_DOWN]):
				game.command("down")

	game.tick()
	game.draw()

	gameState = game.getState()


	if (game.gameover()):
		break

	time.sleep(0.1)
