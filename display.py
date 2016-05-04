import sys
import os
import math
import pygame
from pygame.locals import *

# This class represents one square on the board. It stores the value of the Square and which players Square it is
class Square:
	# when the splot on the board is empty, the Square will just have the value 0
	def __init__(self, value=0, player=0):
		self.value = value
		self.player = player

# When the mouse is clicked, function returns which piece is selected. It returns the piece. Otherwise, it returns None.
def getCurrent(pieces):
	mx, my = pygame.mouse.get_pos()
	for piece in pieces:
		px, py = piece.rect.center
		dx = mx - px
		dy = my - py
		if abs(dx) < 40 and abs(dy) < 40:
			return piece
	return None

# Class that contains all the information and functions for the board
class Board(pygame.sprite.Sprite):
	def __init__(self, x, y, src, player, gs):
		# initialize the grid to a 8x8 array of 0
		self.grid = [ [ 0 for i in range(y) ] for j in range(x) ]
		self.setup = True # true when the board has been setup
		self.image = pygame.image.load(src) # load the background image
		self.rect = self.image.get_rect() # get the rect for the background image
		self.rect.center = (400, 400) # center the background image to 400,400
		self.player = player # initialize the player
		self.gs = gs # game state 
		# get the colour for the player 
		colour = "red" 
		if self.player == 2:
			colour = "blue"
		# the array of pieces (players own pieces)
		self.pieces = []
		# create all the starting pieces and add them to the array
		pieceF = Piece(40, 760, "pieces/F"+colour+".png", 'f', self)
		self.pieces.append(pieceF)
		pieceS = Piece(120, 760, "pieces/S"+colour+".png", 's', self)
		self.pieces.append(pieceS)
		piece9a = Piece(200, 760, "pieces/9"+colour+".png", '9', self)
		self.pieces.append(piece9a)
		piece9b = Piece(280, 760, "pieces/9"+colour+".png", '9', self)
		self.pieces.append(piece9b)
		piece8a = Piece(360, 760, "pieces/8"+colour+".png", '8', self)
		self.pieces.append(piece8a)
		piece8b = Piece(440, 760, "pieces/8"+colour+".png", '8', self)
		self.pieces.append(piece8b)
		piece2 = Piece(520, 760, "pieces/2"+colour+".png", '2', self)
		self.pieces.append(piece2)
		piece1 = Piece(600, 760, "pieces/1"+colour+".png", '1', self)
		self.pieces.append(piece1)
		pieceBa = Piece(680, 760, "pieces/B"+colour+".png", 'b', self)
		self.pieces.append(pieceBa)
		pieceBb = Piece(760, 760, "pieces/B"+colour+".png", 'b', self)
		self.pieces.append(pieceBb)

	# used when first placing the pieces. returns false when the piece cannot be placed and true otherwise
	def checkMove(self, movePiece):
		if self.setup is True:
			# go through all the pieces and make sure the piece being placed is not being places on any of them
			for piece in self.pieces:
				if movePiece.name != piece.name and movePiece.xLoc == piece.xLoc and movePiece.yLoc == piece.yLoc:
					return False
				elif movePiece.name == piece.name and movePiece.xLoc == piece.xLoc and movePiece.yLoc == piece.yLoc and movePiece.xHome != piece.xHome:
					return False
			# check the bounds of the board. If outside of the, return false
			if movePiece.yLoc < 6 or movePiece.yLoc > 8 or movePiece.xLoc < 1 or movePiece.xLoc > 8:
				return False
			else:
				return True

	# calls tick on every pieve
	def tick(self):
		for piece in self.pieces:
				piece.tick()

	# checks if all pieces in the board are placed. If they are return true, false otherwise
	def checkFull(self):
		count = 0 # stores the number of pieces in the board
		for i, line in enumerate(self.grid):
			if i < 6 or i >8:
				continue
			else:
				for piece in line:
					if piece != 0:
						count += 1
		if count == 10:
			return True
		else:
			return False

	# function that makes opponent display
	def setUpOpponent(self):
		# initialize opponent pieces to an empty array
		self.opponentpieces = []
		# go through the whole board. If there is a square with a player different to self.player, it is an opponents piece
		# add that piece to opponent pieces
		yLoc = 0
		for row in self.grid:
			yLoc += 1
			xLoc = 0
			for spot in row:
				xLoc += 1
				# compare to self.player to get the correct colour to place
				if spot.player == 2 and self.player == 1:
					opponent = Piece(xLoc*80+40, yLoc*80+40, "pieces/BLANKblue.png", 'f', self)
					self.opponentpieces.append(opponent)
				elif self.player == 2 and spot.player == 1:
					opponent = Piece(xLoc*80+40, yLoc*80+40, "pieces/BLANKred.png", 'f', self)
					self.opponentpieces.append(opponent)

		# check if any of players own pieces have been removed
		# go through all pieces and pop from array of pieces if any have been removed
		i = 0
		for piece in self.pieces:
			# use board coordinates to get the Square
			spot = self.grid[piece.yLoc-1][piece.xLoc-1]
			if spot.player != self.player or (spot.player == self.player and spot.value != piece.name):
				self.pieces.pop(i)
			i += 1

# piece class that stores information on the piece
class Piece(pygame.sprite.Sprite):
	def __init__(self, x, y, src, name, board):
		self.name = name # stores values of the piece
		self.image = pygame.image.load(src) # stores the image of the piece
		self.rect = self.image.get_rect() # rect of the piece
		self.xHome = x # stores the starting x position
		self.xCoor = x # x coordinate of piece
		self.yCoor = y # y coordinate of piece
		self.xCoorPrev = self.xCoor # previous x coordinate of piece
		self.yCoorPrev = self.yCoor # previous y coordinate of piece
		self.xLoc = x/80 # x location of piece (x position on array)
		self.yLoc = y/80 # y location of piece
		self.rect.center = (self.xCoor, self.yCoor) # center the piece to the x and y coordinates
		self.board = board # save the instance of the board
		self.move = False

	# reveals the image of the opponent when the opponent is attacked
	def revealImage(self):
		colour = "red"
		value = self.board.grid[self.yLoc-1][self.xLoc-1].value
		if self.board.player == 1:
			colour = "blue"
		if value == 'f':
			value = "F"
		elif value == 'b':
			value = "B"
		elif value == 's':
			value = "S"
		image_src = "pieces/"+value+colour+".png"
		self.image = pygame.image.load(image_src)

	# called when you let go of the mouse
	# snaps piece into place
	def drop(self, init=True):
		# get x and y coordinates and scale them
		self.xCoor, self.yCoor = self.rect.center
		self.xCoor = (self.xCoor / 80) * 80 + 40
		self.yCoor = (self.yCoor / 80) * 80 + 40
		# set previous locations to new location
		self.xLocPrev = self.xLoc
		self.yLocPrev = self.yLoc
		# set new locations
		self.xLoc = self.xCoor/80
		self.yLoc = self.yCoor/80

		# for initializing, make sure the move is valid
		if init == True and self.board.checkMove(self):
			# if so, change the grid and the x and y coordinates
			self.rect.center = (self.xCoor, self.yCoor)			
			self.board.grid[self.yLocPrev][self.xLocPrev] = 0
			self.board.grid[self.yLoc][self.xLoc] = self.name
			self.xCoorPrev = self.xCoor
			self.yCoorPrev = self.yCoor
		# for moving check if the move is valid
		elif init == False and self.checkValid():
			# if so move piece
			self.rect.center = (self.xCoor, self.yCoor)	
			self.xCoorPrev = self.xCoor
			self.yCoorPrev = self.yCoor
			return True
		# if both arent valid, move is not allowed so move the piece back
		else:
			self.xLoc = self.xLocPrev
			self.yLoc = self.yLocPrev
			self.rect.center = (self.xCoorPrev, self.yCoorPrev)
		return False

	# checks whether the move is valid. return false if not, true otherwise
	def checkValid(self):
		piecetype =  self.board.grid[self.yLocPrev-1][self.xLocPrev-1].value
		# bombs and flags cannot move
		if piecetype == 'b' or piecetype == 'f':
			return False
		# make sure not the same square
		if abs(self.xLoc-self.xLocPrev)==0 and abs(self.yLoc-self.yLocPrev)==0:
			return False
		# make sure newposition is not in the lake
		if (self.xLoc == 3 and self.yLoc == 5) or (self.xLoc == 3 and self.yLoc == 4) or (self.xLoc == 6 and self.yLoc == 5) or (self.xLoc == 6 and self.yLoc == 4):
			return False
		# make sure there is a Square there
		if self.board.grid[self.yLocPrev-1][self.xLocPrev-1].value == "0":
			return False
		# check the bounds of the new position
		if (self.xLoc < 1 or self.xLoc > 8 or self.yLoc < 1 or self.yLoc > 8):
			return False
		# make sure it only moved by one position
		if self.board.grid[self.yLocPrev-1][self.xLocPrev-1].value != "9":
			if abs(self.xLoc-self.xLocPrev) + abs(self.yLoc-self.yLocPrev) != 1:
				return False
		else:
			# check if 9 is moving in a straight line
			if abs(self.xLoc-self.xLocPrev)==0 or abs(self.yLoc-self.yLocPrev)==0:
				# the x value stays the same
				if abs(self.xLoc-self.xLocPrev)==0:
					# check conditions for the lakes
					if (self.xLoc == 3 or self.xLoc == 6) and ((self.yLoc > 5 and self.yLocPrev < 4) or (self.yLocPrev > 5 and self.yLoc < 4)):
						return False
					# make sure 9 can't jump over other players
					if self.yLoc > self.yLocPrev:
						if self.yLocPrev != self.yLoc-1:
							for row in self.board.grid[self.yLocPrev:self.yLoc-1]:
								space = row[self.xLoc-1]
								if space.player != 0:
									return False
					elif self.yLoc < self.yLocPrev:
						if self.yLoc != self.yLocPrev-1:
							for row in self.board.grid[self.yLoc:self.yLocPrev-1]:
								space = row[self.xLoc-1]
								if space.player != 0:
									return False
				# the y value stays the same
				else:
					# check lake conditions
					if (self.yLoc == 5 or self.yLoc == 4) and ((((self.xLoc > 3 and self.xLoc < 6) or self.xLoc > 6) and self.xLocPrev < 3) or ((self.xLocPrev > 3 and self.xLocPrev < 6) and self.xLoc > 6) or (((self.xLocPrev > 3 and self.xLocPrev < 6) or self.xLocPrev > 6) and self.xLoc < 3) or ((self.xLoc > 3 and self.xLoc < 6) and self.xLocPrev > 6)):
						return False
					# make sure 9 can't jump over ther players
					if self.xLoc > self.xLocPrev:
						if self.xLoc-1 != self.xLocPrev:
							for space in self.board.grid[self.yLoc-1][self.xLocPrev:self.xLoc-1]:
								if space.player != 0:
									return False
					elif self.xLoc < self.xLocPrev:
						if self.xLocPrev-1 != self.xLoc:
							for space in self.board.grid[self.yLoc-1][self.xLoc:self.xLocPrev-1]:
								if space.player != 0:
									return False
			else:
				return False
		# check if a Square is already in that position
		old_pos_player = self.board.grid[self.yLocPrev-1][self.xLocPrev-1].player
		new_pos_player = self.board.grid[self.yLoc-1][self.xLoc-1].player

		# make sure the piece is not moving onto another piece on the same team
		if new_pos_player == old_pos_player:
			return False
		# there is a collision with the other player
		elif new_pos_player != 0:
			# we want to show the player
			for piece in self.board.opponentpieces:
				if piece.xLoc == self.xLoc and piece.yLoc == self.yLoc:
					piece.revealImage()
					# if the image is being changed the board images should be refreshed
					self.board.gs.screen.fill(self.board.gs.black)
					self.board.gs.screen.blit(self.board.image, self.board.rect)
					for piece in self.board.pieces:
						self.board.gs.screen.blit(piece.image, piece.rect)
					for piece in self.board.opponentpieces:
						self.board.gs.screen.blit(piece.image, piece.rect)
					pygame.display.flip()
		return True

	# returns coordinates. a list of two tuples. First has old position, second has new position
	def get_coordinates(self):
		return [(self.yLocPrev-1,self.xLocPrev-1),(self.yLoc-1,self.xLoc-1)]

	# move the piece to the position of the mouse if move is true
	def tick(self):
		self.xCoor, self.yCoor = pygame.mouse.get_pos()
		if self.move is True:
			self.rect.center = (self.xCoor, self.yCoor)

# class for the start button to begin the game
class StartButton(pygame.sprite.Sprite):
	def __init__(self):
		self.image = pygame.image.load("images/ready.png")
		self.rect = self.image.get_rect()
		self.rect.center = (400, 400)

	# checks bounds of button, returns true if clicked
	def checkClick(self):
		mx, my = pygame.mouse.get_pos()
		if mx > 260 and mx < 540 and my > 330 and my < 470:
			return True
		return False

# The main game space function
class GameSpace(object):
	
	def __init__(self, player):
		# 1 - basic initialization
		pygame.init()
		self.size = self.width, self.heigth = 800, 800
		self.black = 0, 0, 0

		self.screen = pygame.display.set_mode(self.size)

		self.player = player # save which player is instantiating the gamespace
		self.board = Board(10, 10, "images/board.png", self.player, self) # create the board
		self.startbutton = StartButton() # initialize the start button
		self.showstart = False # tracks whether the start button is showing

		self.waitingImage = pygame.image.load("images/waiting.png") # load the waiting for opponent image
		self.waitingRect = self.waitingImage.get_rect() # waiting for opponent rect
		self.waitingRect.center = (400, 400)

		# 2 - set up game objects
		self.clock = pygame.time.Clock()

	# function used when the player is first placing his pieces
	def playerSetup(self):
		# 3 - start game loop
		while 1:
			# 4 - clock tick regulation (framerate)
			self.clock.tick(60)

			# 5 - handle user inputs
			for event in pygame.event.get():

				# check if all pieces are placed. If they are show the start button
				if self.board.checkFull() == True:
					self.showstart = True
				else:
					self.showstart = False

				# if the mouse is down, get the clicked piece and set move to true
				if event.type == MOUSEBUTTONDOWN:
					self.currentPiece = getCurrent(self.board.pieces)
					if self.currentPiece:
						self.currentPiece.move = True
				
				# when mouse is up, drop the piece is a piece is moving
				if event.type == MOUSEBUTTONUP:
					if self.currentPiece:
						self.currentPiece.move = False
						self.currentPiece.drop()
					# if the start button is clicked send over the board
					if self.showstart == True and self.startbutton.checkClick():
						self.finalboard = []
						# show the board before sending it
						for row in self.board.grid[6:9]:
							self.finalboard.append(row[1:9])
						self.screen.fill(self.black)
						self.screen.blit(self.board.image, self.board.rect)
						for piece in self.board.pieces:
							self.screen.blit(piece.image, piece.rect)
						self.screen.blit(self.waitingImage, self.waitingRect)
						pygame.display.flip()
						# send final board
						return self.finalboard
				if event.type == QUIT:
					os._exit(1)

			# 6 - send a tick to every game object
			self.board.tick()


			# 7 - display the game objects
			self.screen.fill(self.black)
			self.screen.blit(self.board.image, self.board.rect)
			for piece in self.board.pieces:
				self.screen.blit(piece.image, piece.rect)
			if self.showstart == True:
				self.screen.blit(self.startbutton.image,self.startbutton.rect)
			pygame.display.flip()

	# called when a player makes a move
	def main(self):
		# 3 - start game loop
		while 1:
			# 4 - clock tick regulation (framerate)
			self.clock.tick(60)

			# 5 - handle user inputs
			for event in pygame.event.get():
				# select the piece to move
				if event.type == MOUSEBUTTONDOWN:
					self.currentPiece = getCurrent(self.board.pieces)
					if self.currentPiece:
						self.currentPiece.move = True

				if event.type == MOUSEBUTTONUP:
					# drop the piece if a piece is selected
					if self.currentPiece:
						self.currentPiece.move = False
						if self.currentPiece.drop(False) == True:
							# display the board
							self.screen.fill(self.black)
							self.screen.blit(self.board.image, self.board.rect)
							for piece in self.board.pieces:
								self.screen.blit(piece.image, piece.rect)
							for piece in self.board.opponentpieces:
								self.screen.blit(piece.image, piece.rect)
							self.screen.blit(self.waitingImage, self.waitingRect)
							pygame.display.flip()
							# send the move to the player
							return self.currentPiece.get_coordinates()
				if event.type == QUIT:
					os._exit(1)

			# 6 - send a tick to every game object
			self.board.tick()

			# 7 - display the game objects
			self.screen.fill(self.black)
			self.screen.blit(self.board.image, self.board.rect)
			for piece in self.board.pieces:
				self.screen.blit(piece.image, piece.rect)
			for piece in self.board.opponentpieces:
				self.screen.blit(piece.image, piece.rect)
			pygame.display.flip()

	# update the grid 8x8 array of board and load the opponents pieces
	def updateBoard(self, board):
		self.board.grid = board
		self.board.setUpOpponent()

	# called at the end of the game
	def end(self, status):
		# load ending image
		filename = "images/" + status + ".png"
		self.endimage = pygame.image.load(filename)
		self.endrect = self.endimage.get_rect()
		self.endrect.center = (400, 400)
		while 1:
			self.clock.tick(60)
			for event in pygame.event.get():
				if event.type == QUIT:
						os._exit(1)
			# show board and ending image
			self.screen.fill(self.black)
			self.screen.blit(self.board.image, self.board.rect)
			for piece in self.board.pieces:
				self.screen.blit(piece.image, piece.rect)
			for piece in self.board.opponentpieces:
				self.screen.blit(piece.image, piece.rect)
			self.screen.blit(self.endimage, self.endrect)
			pygame.display.flip()

	# closes the window
	def exit(self):
		os._exit(1)

