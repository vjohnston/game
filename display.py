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
	def __init__(self, x, y, src):
		self.grid = [ [ 0 for i in range(y) ] for j in range(x) ]
		self.setup = True
		self.image = pygame.image.load(src)
		self.original = self.image
		self.rect = self.image.get_rect()
		self.rect.center = (400, 400)

		self.pieces = []

		pieceF = Piece(40, 760, "pieces/f.png", 'f', self)
		self.pieces.append(pieceF)
		pieceS = Piece(120, 760, "pieces/s.png", 's', self)
		self.pieces.append(pieceS)
		piece9a = Piece(200, 760, "pieces/9.png", '9', self)
		self.pieces.append(piece9a)
		piece9b = Piece(280, 760, "pieces/9.png", '9', self)
		self.pieces.append(piece9b)
		piece8a = Piece(360, 760, "pieces/8.png", '8', self)
		self.pieces.append(piece8a)
		piece8b = Piece(440, 760, "pieces/8.png", '8', self)
		self.pieces.append(piece8b)
		piece2 = Piece(520, 760, "pieces/2.png", '2', self)
		self.pieces.append(piece2)
		piece1 = Piece(600, 760, "pieces/1.png", '1', self)
		self.pieces.append(piece1)
		pieceBa = Piece(680, 760, "pieces/b.png", 'b', self)
		self.pieces.append(pieceBa)
		pieceBb = Piece(760, 760, "pieces/b.png", 'b', self)
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

	def drop(self, init=True):
		self.xCoor, self.yCoor = self.rect.center
		self.xCoor = (self.xCoor / 80) * 80 + 40
		self.yCoor = (self.yCoor / 80) * 80 + 40
		self.xLocPrev = self.xLoc
		self.yLocPrev = self.yLoc
		self.xLoc = self.xCoor/80
		self.yLoc = self.yCoor/80

		#print "Coordinates:" , self.xCoor, self.yCoor, self.xLoc, self.yLoc
		if init == True and self.board.checkMove(self):
			self.rect.center = (self.xCoor, self.yCoor)			
			self.board.grid[self.yLocPrev][self.xLocPrev] = 0
			self.board.grid[self.yLoc][self.xLoc] = self.name
			self.xCoorPrev = self.xCoor
			self.yCoorPrev = self.yCoor
		elif init == False and self.checkValid():
			self.rect.center = (self.xCoor, self.yCoor)			
			self.board.grid[self.yLocPrev][self.xLocPrev] = Square
			self.board.grid[self.yLoc][self.xLoc] = Square(self.name,1)
			self.xCoorPrev = self.xCoor
			self.yCoorPrev = self.yCoor
		else:
			self.rect.center = (self.xCoorPrev, self.yCoorPrev)
		
		#print self.checkFull()

		#print self.board.grid[6]
		#print self.board.grid[7]
		#print self.board.grid[8]
		#print
		#board[self.x][self.y] = self.name
		#print board
		#print self.name , self.x , self.y

	def checkValid(self):
		print self.xLocPrev, self.yLocPrev
		# make sure there is a Square there
		if self.board.grid[self.xLocPrev][self.yLocPrev].value == 0:
			#self.xLoc = self.xLocPrev
			#self.yLoc = self.yLocPrev
			return False
		# check the bounds of the new position
		if (self.xLoc < 0 or self.xLoc > 7 or self.yLoc < 0 or self.yLoc > 7):
			#self.xLoc = self.xLocPrev
			#self.yLoc = self.yLocPrev
			return False
		# make sure it only moved by one position
		if self.board.grid[self.xLocPrev][self.yLocPrev].value != 9:
			if not ((abs(self.xLoc-self.xLocPrev)==1 and abs(self.yLoc-self.yLocPrev)==0)) or ((abs(self.xLoc-self.xLocPrev)==0 and abs(self.yLoc-self.yLocPrev)==1)):
				#self.xLoc = self.xLocPrev
				#self.yLoc = self.yLocPrev
				return False
		# check if a Square is already in that position
		new_pos_player = self.board.grid[self.xLoc][self.yLoc].player
		if new_pos_player == 1:
			#self.xLoc = self.xLocPrev
			#self.yLoc = self.yLocPrev
			return False
		elif new_pos_player == 2:
			# we want to show the player
			pass
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
		self.image = pygame.image.load("start.png")
		self.rect = self.image.get_rect()
		self.rect.center = (400, 400)

	def checkClick(self):
		mx, my = pygame.mouse.get_pos()
		if mx > 350 and mx < 450 and my > 350 and my < 450:
			return True
		return False

class GameSpace(object):
	
	def __init__(self):
		# 1 - basic initialization
		pygame.init()
		self.size = self.width, self.heigth = 800, 800
		self.black = 0, 0, 0

		self.screen = pygame.display.set_mode(self.size)

		self.board = Board(10, 10, "boardV3.png")
		self.startbutton = StartButton()
		self.showstart = False

		# 2 - set up game objects
		self.clock = pygame.time.Clock()

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
					if self.showstart == True and self.startbutton.checkClick():
						self.finalboard = []
						for row in self.board.grid[6:9]:
							self.finalboard.append(row[1:9])
						return self.finalboard

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
			if self.showstart == True:
				self.screen.blit(self.startbutton.image,self.startbutton.rect)
			pygame.display.flip()

	def main(self):
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
						self.currentPiece.drop(False)
						print "hi2"
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
			pygame.display.flip()

	def updateBoard(self, board):
		#self.board.grid = board
		yLoc = 0
		for row in board:
			yLoc += 1
			xLoc = 0
			for spot in row:
				xLoc +=1
				if spot != 0:
					for piece in self.board.pieces:
						if piece.name == spot:
							print yLoc , xLoc
							piece.move(yLoc, xLoc)



if __name__ == '__main__':
	pass
	#gs = GameSpace()
	#print gs.main()
