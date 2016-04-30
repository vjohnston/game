import sys
import os
import math
import pygame
from pygame.locals import *


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
	def __init__(self, x, y, src):
		self.grid = [ [ 0 for i in range(y) ] for j in range(x) ]
		self.setup = True
		self.image = pygame.image.load(src)
		self.original = self.image
		self.rect = self.image.get_rect()
		self.rect.center = (400, 400)

		self.pieces = []

		pieceF = Piece(40, 760, "pieces/f.png", 'F', self)
		self.pieces.append(pieceF)
		pieceS = Piece(120, 760, "pieces/s.png", 'S', self)
		self.pieces.append(pieceS)
		piece9a = Piece(200, 760, "pieces/9.png", '9a', self)
		self.pieces.append(piece9a)
		piece9b = Piece(280, 760, "pieces/9.png", '9b', self)
		self.pieces.append(piece9b)
		piece8a = Piece(360, 760, "pieces/8.png", '8a', self)
		self.pieces.append(piece8a)
		piece8b = Piece(440, 760, "pieces/8.png", '8b', self)
		self.pieces.append(piece8b)
		piece2 = Piece(520, 760, "pieces/2.png", '2', self)
		self.pieces.append(piece2)
		piece1 = Piece(600, 760, "pieces/1.png", '1', self)
		self.pieces.append(piece1)
		pieceBa = Piece(680, 760, "pieces/b.png", 'Ba', self)
		self.pieces.append(pieceBa)
		pieceBb = Piece(760, 760, "pieces/b.png", 'Bb', self)
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
		self.rect.center = (x, y)

	def drop(self):
		self.xCoor, self.yCoor = self.rect.center
		self.xCoor = (self.xCoor / 80) * 80 + 40
		self.yCoor = (self.yCoor / 80) * 80 + 40
		self.xLocPrev = self.xLoc
		self.yLocPrev = self.yLoc
		self.xLoc = self.xCoor/80
		self.yLoc = self.yCoor/80

		#print "Coordinates:" , self.xCoor, self.yCoor, self.xLoc, self.yLoc
		if self.board.checkMove(self):
			self.rect.center = (self.xCoor, self.yCoor)			
			self.board.grid[self.yLocPrev][self.xLocPrev] = 0
			self.board.grid[self.yLoc][self.xLoc] = self.name
			self.xCoorPrev = self.xCoor
			self.yCoorPrev = self.yCoor
		else:
			self.rect.center = (self.xCoorPrev, self.yCoorPrev)
		
		self.checkFull()

		print self.board.grid[6]
		print self.board.grid[7]
		print self.board.grid[8]
		print
		#board[self.x][self.y] = self.name
		#print board
		#print self.name , self.x , self.y

	def checkFull(self):
		count = 0
		for i, line in enumerate(self.board.grid):
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

	def tick(self):
		self.xCoor, self.yCoor = pygame.mouse.get_pos()
		if self.move is True:
			self.rect.center = (self.xCoor, self.yCoor)



class GameSpace(object):
	
	def main(self):
		# 1 - basic initialization
		pygame.init()
		self.size = self.width, self.heigth = 800, 800
		self.black = 0, 0, 0

		self.screen = pygame.display.set_mode(self.size)

		self.board = Board(10, 10, "boardV3.png")

		# 2 - set up game objects
		self.clock = pygame.time.Clock()

		# 3 - start game loop
		while 1:
			# 4 - clock tick regulation (framerate)
			self.clock.tick(60)

			# 5 - handle user inputs
			for event in pygame.event.get():

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
				if event.type == QUIT:
					sys.exit()

			# 6 - send a tick to every game object
			self.board.tick()


			# 7 - display the game objects
			self.screen.fill(self.black)
			self.screen.blit(self.board.image, self.board.rect)
			for piece in self.board.pieces:
				self.screen.blit(piece.image, piece.rect)
			pygame.display.flip()

if __name__ == '__main__':
	gs = GameSpace()
	gs.main()
