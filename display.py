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

	# returns true if the spot does not have a Square on it, false otherwise
	def isEmpty(self):
		if self.player != 0:
			return false
		else:
			return true

def getCurrent(pieces):
	mx, my = pygame.mouse.get_pos()
	for piece in pieces:
		px, py = piece.rect.center
		dx = mx - px
		dy = my - py
		if abs(dx) < 40 and abs(dy) < 40:
			return piece
	return None

class Board(pygame.sprite.Sprite):
	def __init__(self, x, y, src, player, gs):
		self.grid = [ [ 0 for i in range(y) ] for j in range(x) ]
		self.setup = True
		self.image = pygame.image.load(src)
		self.original = self.image
		self.rect = self.image.get_rect()
		self.rect.center = (400, 400)
		self.player = player
		self.gs = gs
		colour = "red"
		if self.player == 2:
			colour = "blue"

		self.pieces = []

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

	def checkMove(self, movePiece):
		if self.setup is True:
			for piece in self.pieces:
				if movePiece.name != piece.name and movePiece.xLoc == piece.xLoc and movePiece.yLoc == piece.yLoc:
					#print movePiece.name , piece.name , movePiece.xLoc , piece.xLoc , movePiece.yLoc , piece.yLoc
					return False
			if movePiece.yLoc < 6 or movePiece.yLoc > 8 or movePiece.xLoc < 1 or movePiece.xLoc > 8:
				return False
			else:
				return True

	def tick(self):
		for piece in self.pieces:
				piece.tick()

	def checkFull(self):
		count = 0
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

	def setUpOpponent(self):
		# load opponent pieces
		self.opponentpieces = []
		yLoc = 0
		for row in self.grid:
			yLoc += 1
			xLoc = 0
			for spot in row:
				xLoc += 1
				if spot.player == 2 and self.player == 1:
					print spot.value, xLoc, yLoc
					opponent = Piece(xLoc*80+40, yLoc*80+40, "pieces/BLANKblue.png", 'f', self)
					self.opponentpieces.append(opponent)
				elif self.player == 2 and spot.player == 1:
					print spot.value, xLoc, yLoc
					opponent = Piece(xLoc*80+40, yLoc*80+40, "pieces/BLANKred.png", 'f', self)
					self.opponentpieces.append(opponent)

		# check if any pieces have been removed
		i = 0
		for piece in self.pieces:
			# use board coordinates to get the Square
			spot = self.grid[piece.yLoc-1][piece.xLoc-1]
			if spot.player != self.player or (spot.player == self.player and spot.value != piece.name):
				self.pieces.pop(i)
			i += 1

class Piece(pygame.sprite.Sprite):
	def __init__(self, x, y, src, name, board):
		self.name = name
		self.image = pygame.image.load(src)
		self.rect = self.image.get_rect()
		self.xCoor = x
		self.yCoor = y
		self.xCoorPrev = self.xCoor
		self.yCoorPrev = self.yCoor
		self.xLoc = x/80
		self.yLoc = y/80
		self.rect.center = (self.xCoor, self.yCoor)
		self.board = board

	def move(self, x, y):
		self.rect.center = (x*80+40, y*80+40)

	def revealImage(self):
		colour = "red"
		value = self.board.grid[self.yLoc-1][self.xLoc-1].value
		print 'value ', value
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
		print image_src

	def drop(self, init=True):
		self.xCoor, self.yCoor = self.rect.center
		self.xCoor = (self.xCoor / 80) * 80 + 40
		self.yCoor = (self.yCoor / 80) * 80 + 40
		self.xLocPrev = self.xLoc
		self.yLocPrev = self.yLoc
		self.xLoc = self.xCoor/80
		self.yLoc = self.yCoor/80

		print "2old: ", self.xLocPrev, self.yLocPrev
		print "2new: ", self.xLoc, self.yLoc

		#print "Coordinates:" , self.xCoor, self.yCoor, self.xLoc, self.yLoc
		if init == True and self.board.checkMove(self):
			self.rect.center = (self.xCoor, self.yCoor)			
			self.board.grid[self.yLocPrev][self.xLocPrev] = 0
			self.board.grid[self.yLoc][self.xLoc] = self.name
			self.xCoorPrev = self.xCoor
			self.yCoorPrev = self.yCoor
		elif init == False and self.checkValid():
			print "in"
			self.rect.center = (self.xCoor, self.yCoor)	
			self.xCoorPrev = self.xCoor
			self.yCoorPrev = self.yCoor
			return True
		else:
			self.xLoc = self.xLocPrev
			self.yLoc = self.yLocPrev
			self.rect.center = (self.xCoorPrev, self.yCoorPrev)
		
		print "3old: ", self.xLocPrev, self.yLocPrev
		print "3new: ", self.xLoc, self.yLoc
		return False

	def checkValid(self):
		print self.xLocPrev, self.yLocPrev
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
			#self.xLoc = self.xLocPrev
			#self.yLoc = self.yLocPrev
			return False
		# check the bounds of the new position
		if (self.xLoc < 1 or self.xLoc > 8 or self.yLoc < 1 or self.yLoc > 8):
			#self.xLoc = self.xLocPrev
			#self.yLoc = self.yLocPrev
			return False
		# make sure it only moved by one position
		print self.xLocPrev, self.yLocPrev, self.xLoc, self.yLoc
		print self.board.grid[self.yLocPrev-1][self.xLocPrev-1].value
		if self.board.grid[self.yLocPrev-1][self.xLocPrev-1].value != "9":
			if abs(self.xLoc-self.xLocPrev) + abs(self.yLoc-self.yLocPrev) != 1:
				print "moved by more than one"
				return False
		else:
			print "number 9"
			# check if 9 is moving in a straight line
			if abs(self.xLoc-self.xLocPrev)==0 or abs(self.yLoc-self.yLocPrev)==0:
				# the x value stays the same
				if abs(self.xLoc-self.xLocPrev)==0:
					if (self.xLoc == 3 or self.xLoc == 6) and ((self.yLoc > 5 and self.yLocPrev < 4) or (self.yLocPrev > 5 and self.yLoc < 4)):
						return False
					if self.yLoc > self.yLocPrev:
						print "x1", self.xLoc-1, self.yLocPrev, self.yLoc-2
						if self.yLocPrev != self.yLoc-1:
							for row in self.board.grid[self.yLocPrev:self.yLoc-1]:
								space = row[self.xLoc-1]
								if space.player != 0:
									return False
					elif self.yLoc < self.yLocPrev:
						print "x2", self.xLoc-1, self.yLoc, self.yLocPrev-1
						if self.yLoc != self.yLocPrev-1:
							for row in self.board.grid[self.yLoc:self.yLocPrev-1]:
								space = row[self.xLoc-1]
								print space.value
								if space.player != 0:
									return False
				# the y value stays the same
				else:
					if (self.yLoc == 5 or self.yLoc == 4) and ((((self.xLoc > 3 and self.xLoc < 6) or self.xLoc > 6) and self.xLocPrev < 3) or ((self.xLocPrev > 3 and self.xLocPrev < 6) and self.xLoc > 6) or (((self.xLocPrev > 3 and self.xLocPrev < 6) or self.xLocPrev > 6) and self.xLoc < 3) or ((self.xLoc > 3 and self.xLoc < 6) and self.xLocPrev > 6)):
						return False
					if self.xLoc > self.xLocPrev:
						print "y1", self.yLoc-1, self.xLocPrev, self.xLoc-2
						if self.xLoc-1 != self.xLocPrev:
							for space in self.board.grid[self.yLoc-1][self.xLocPrev:self.xLoc-1]:
								print "spot", space.player, space.value
								if space.player != 0:
									return False
					elif self.xLoc < self.xLocPrev:
						print "y2", self.yLoc-1, self.xLoc, self.xLocPrev-2
						if self.xLocPrev-1 != self.xLoc:
							for space in self.board.grid[self.yLoc-1][self.xLoc:self.xLocPrev-1]:
								if space.player != 0:
									return False
			else:
				print "not 1 direction"
				return False
		print "moved by 1"
		# check if a Square is already in that position
		old_pos_player = self.board.grid[self.yLocPrev-1][self.xLocPrev-1].player
		new_pos_player = self.board.grid[self.yLoc-1][self.xLoc-1].player
		print "old", self.board.grid[self.yLocPrev-1][self.xLocPrev-1].player,"new", self.board.grid[self.yLoc-1][self.xLoc-1].player
		if new_pos_player == old_pos_player:
			#self.xLoc = self.xLocPrev
			#self.yLoc = self.yLocPrev
			return False
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

	def get_coordinates(self):
		#return [(self.xLocPrev-1,self.yLocPrev-1),(self.xLoc-1,self.yLoc-1)]
		return [(self.yLocPrev-1,self.xLocPrev-1),(self.yLoc-1,self.xLoc-1)]

	def tick(self):
		self.xCoor, self.yCoor = pygame.mouse.get_pos()
		if self.move is True:
			self.rect.center = (self.xCoor, self.yCoor)

class StartButton(pygame.sprite.Sprite):
	def __init__(self):
		self.image = pygame.image.load("images/ready.png")
		self.rect = self.image.get_rect()
		self.rect.center = (400, 400)

	def checkClick(self):
		mx, my = pygame.mouse.get_pos()
		if mx > 350 and mx < 450 and my > 350 and my < 450:
			return True
		return False

class GameSpace(object):
	
	def __init__(self, player):
		# 1 - basic initialization
		pygame.init()
		self.size = self.width, self.heigth = 800, 800
		self.black = 0, 0, 0

		self.screen = pygame.display.set_mode(self.size)

		self.player = player
		self.board = Board(10, 10, "images/board.png", self.player, self)
		self.startbutton = StartButton()
		self.showstart = False

		# 2 - set up game objects
		self.clock = pygame.time.Clock()
		self.waiting = False

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

				#if event.type == KEYDOWN and pygame.key.get_pressed():
				#	self.player.submit()

				if event.type == MOUSEBUTTONDOWN:
					self.currentPiece = getCurrent(self.board.pieces)
					if self.currentPiece:
						self.currentPiece.move = True

				if event.type == MOUSEBUTTONUP:
					if self.currentPiece:
						self.currentPiece.move = False
						self.currentPiece.drop()
					if self.showstart == True and self.startbutton.checkClick():
						self.finalboard = []
						for row in self.board.grid[6:9]:
							self.finalboard.append(row[1:9])
						self.waiting = True
						return self.finalboard
				if event.type == QUIT:
					sys.exit()

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

	def waitingForOpponent(self):
		while self.waiting == True:
			self.clock.tick(60)
			for event in pygame.event.get():
				if event.type == QUIT:
						sys.exit()
			self.screen.fill(self.black)
			self.screen.blit(self.board.image, self.board.rect)
			for piece in self.board.pieces:
				self.screen.blit(piece.image, piece.rect)
			pygame.display.flip()

	def main(self):
		print "self waiting false"
		self.waiting = False
		# 3 - start game loop
		while 1:
			# 4 - clock tick regulation (framerate)
			self.clock.tick(60)

			# 5 - handle user inputs
			for event in pygame.event.get():
				if event.type == MOUSEBUTTONDOWN:
					self.currentPiece = getCurrent(self.board.pieces)
					if self.currentPiece:
						self.currentPiece.move = True

				if event.type == MOUSEBUTTONUP:
					print "hi"
					if self.currentPiece:
						self.currentPiece.move = False
						if self.currentPiece.drop(False) == True:
							print "hi2"
							self.screen.fill(self.black)
							self.screen.blit(self.board.image, self.board.rect)
							for piece in self.board.pieces:
								self.screen.blit(piece.image, piece.rect)
							for piece in self.board.opponentpieces:
								self.screen.blit(piece.image, piece.rect)
							pygame.display.flip()
							return self.currentPiece.get_coordinates()
				if event.type == QUIT:
					sys.exit()

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

	def updateBoard(self, board):
		self.board.grid = board
		self.board.setUpOpponent()

	def end(self, status):
		filename = "images" + status + ".png"
		print filename
		self.endimage = pygame.image.load(filename)
		self.endrect = self.endimage.get_rect()
		self.endrect.center = (400, 400)
		while 1:
			self.clock.tick(60)
			for event in pygame.event.get():
				if event.type == QUIT:
						sys.exit()
			self.screen.fill(self.black)
			self.screen.blit(self.board.image, self.board.rect)
			for piece in self.board.pieces:
				self.screen.blit(piece.image, piece.rect)
			for piece in self.board.opponentpieces:
				self.screen.blit(piece.image, piece.rect)
			self.screen.blit(self.endimage, self.endrect)
			pygame.display.flip()

if __name__ == '__main__':
	pass
	#gs = GameSpace()
	#print gs.main()
