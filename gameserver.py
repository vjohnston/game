from twisted.internet import reactor
from twisted.internet.protocol import Protocol
from twisted.internet.protocol import Factory
import pygame
import sys
import math
import cPickle as pickle
from pygame.locals import *

PLAYER_ONE_PORT = 32015
PLAYER_TWO_PORT = 32016
board_width = 8
board_height = 8
player_height = 3

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

# this connection keeps track of the second players moves
class SecondConnection(Protocol):
	# the instance of the main connection should be saved
	def __init__(self, mainconnection):
		self.mainconnection = mainconnection
		self.initplayer = False # keeps track of whether the player has initialized the board

	# once the connection is made, tell the main connection that the second connection was successful
	def connectionMade(self):
		print "player 2 connected"
		self.mainconnection.ackSecondPlayer(self)

	def dataReceived(self, data_string):
		data = pickle.loads(data_string)
		print data_string
		if isinstance(data[0], list):
			# set up players 1 positions on board
			# if a Square has a value 0, that spot is empty
			piece_count = 0
			for i in range(player_height):
				for j in range(board_width):
					if (data[i][j]!=0):
						self.mainconnection.board[player_height-1-i][board_width-1-j] = Square(data[i][j],2)
						piece_count += 1
						if piece_count == 10:
							self.initplayer = True
			self.mainconnection.printBoard()
			if self.initplayer and self.mainconnection.initplayer == True:
				self.mainconnection.startGame()

		elif type(data[0]) is tuple:
			fight_status = ""
			if self.mainconnection.board[data[1][0]][data[1][1]].player == 1:
				fight_status = self.mainconnection.fight(data[0],data[1])
				if fight_status == "EOG":
					self.mainconnection.endGame(2)
			else:
				self.mainconnection.board[data[1][0]][data[1][1]] = self.mainconnection.board[data[0][0]][data[0][1]]
				self.mainconnection.board[data[0][0]][data[0][1]] = Square()
			board_string = pickle.dumps(self.mainconnection.board)
			self.transport.write(board_string)
			self.mainconnection.transport.write(board_string)
			self.mainconnection.transport.write('turn')
			# change turn
			#self.mainconnection.transport.getHandle().sendall("turn")
			print "end of player 2 turn"
			self.mainconnection.printBoard()
		elif data.isdigit():
			pass

class SecondConnectionFactory(Factory):
	def __init__(self, mainconnection):
		self.mainconnection = mainconnection

	def buildProtocol(self, addr):
		return SecondConnection(self.mainconnection)

# The main connection contains most of the game logic. It is also connected to player1
class MainConnection(Protocol):
	# create the 2d array for board
	# the board is an 8x8
	def __init__(self):
		self.board = [[Square() for i in range(board_width)] for j in range(board_height)]
		self.initplayer = False # keeps track of whether the player has initialized the board

	# once player one connects, start listening for player 2
	# send an instance of self to the second connection
	def connectionMade(self):
		print "player 1 connected"
		reactor.listenTCP(PLAYER_TWO_PORT, SecondConnectionFactory(self))

	# receive an acknoledgement that the second player has connected and save instance of second player
	def ackSecondPlayer(self, secondplayer):
		print "both players connected"
		self.secondplayer = secondplayer	

	# the data can either come in three forms
	# 1. the initial player setup (3x10 array)
	# 2. the next move (list of two tuples) old coordinate and new coordinate
	# 3. a guess of the other players number (number)
	def dataReceived(self, data_string):
		data = pickle.loads(data_string)
		if isinstance(data[0], list):
			# set up players 1 positions on board
			# if a Square has a value 0, that spot is empty
			piece_count = 0
			for i in range(player_height):
				for j in range(board_width):
					if (data[i][j]!=0):
						self.board[i+board_height-player_height][j] = Square(data[i][j],1)
						piece_count += 1
						if piece_count == 10:
							self.initplayer = True
						self.initplayer = True
			self.printBoard()
			if hasattr(self,'secondplayer'):
				if self.secondplayer.initplayer == True and self.initplayer == True:
					self.startGame()
		elif type(data[0]) is tuple:
			#self.secondplayer.transport.write("turn")
			# check if there is a collision between the two players
			print "data", data
			if self.board[data[1][0]][data[1][1]].player == 2:
				fight_status = self.fight(data[0],data[1])
				if fight_status == "EOG":
					self.endGame(1)
			else:
				# just a regular move
				print data
				self.printBoard()
				self.board[data[1][0]][data[1][1]] = self.board[data[0][0]][data[0][1]]
				self.board[data[0][0]][data[0][1]] = Square()
				print
				self.printBoard()
				print
			# update the board for both player
			board_string = pickle.dumps(self.board)
			self.secondplayer.transport.write(board_string)
			self.transport.write(board_string)

			# change turn
			self.secondplayer.transport.write('turn')
			print "player 1 end of turn"
			self.printBoard()
		elif data.isdigit():
			pass

	def fight(self, attacker, defender):
		attacking_value = self.board[attacker[0]][attacker[1]].value
		defending_value = self.board[defender[0]][defender[1]].value
		print "values", attacking_value, defending_value
		# deal with special cases
		# if attacker is a spy and defender is a marshall 
		if defending_value == 'f':
			return "EOG"
		elif attacking_value == 's' and defending_value == "1":
			self.board[defender[0]][defender[1]] = self.board[attacker[0]][attacker[1]]
			self.board[attacker[0]][attacker[1]] = Square()
			return "win" # attacker wins
		elif defending_value == 'b':
			# the defense is a bomb
			if attacking_value == "8":
				self.board[defender[0]][defender[1]] = self.board[attacker[0]][attacker[1]]
				self.board[attacker[0]][attacker[1]] = Square()
				return "win" # attacker diffuses bomb and wins fight
			else:
				self.board[attacker[0]][attacker[1]] = Square()
				return "lost" # defender wins
		elif defending_value == 's':
			defending_value = 10
		elif attacking_value == 's':
			attacking_value = 10

		attacking_value = int(attacking_value)
		defending_value = int(defending_value)

		if attacking_value < defending_value:
			# attacker wins
			self.board[defender[0]][defender[1]] = self.board[attacker[0]][attacker[1]]
			self.board[attacker[0]][attacker[1]] = Square()
			return "win"
		elif attacking_value > defending_value:
			self.board[attacker[0]][attacker[1]] = Square()
			return "lost" # defender wins
		else:
			self.board[defender[0]][defender[1]] = Square()
			self.board[attacker[0]][attacker[1]] = Square()
			return "tie" # both of them lose

	def endGame(self, winner):
		if winner == 1:
			self.transport.write("win")
			self.secondplayer.transport.write("lose")
		else:
			self.transpot.write("lose")
			self.secondplayer.transport.write("win")
		#reactor.stop()

	def startGame(self):
		self.turn = 1 # keep track of which players turn it is
		# send starting board to both players
		self.printBoard()
		pickle_board = pickle.dumps(self.board)
		self.secondplayer.transport.write(pickle_board)
		self.transport.write(pickle_board)
		self.transport.write('turn')

	# use for debugging print board
	def printBoard(self):
		for row in self.board:
 			for square in row:
				print '{:4}'.format(square.value),
			print

	def connectionLost(self, reason):
		print "gameserver connection lost"

	
class MainConnectionFactory(Factory):
	def buildProtocol(self, addr):
		return MainConnection()

if __name__ == '__main__':
	reactor.listenTCP(PLAYER_ONE_PORT, MainConnectionFactory())
	reactor.run()
