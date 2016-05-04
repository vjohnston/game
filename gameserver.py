from twisted.internet import reactor
from twisted.internet.protocol import Protocol
from twisted.internet.protocol import Factory
import pygame
import sys
import math
import cPickle as pickle
from pygame.locals import *

PLAYER_ONE_PORT = 32025
PLAYER_TWO_PORT = 32026
board_width = 8
board_height = 8
player_height = 3

# This class represents one square on the board. It stores the value of the Square and which players Square it is
class Square:
	# when the splot on the board is empty, the Square will just have the value 0
	def __init__(self, value=0, player=0):
		self.value = value
		self.player = player

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
		# turn the string of data received back into an object
		data = pickle.loads(data_string)
		# if data[0] is a list this means that the data sent is a 2D array
		# this is the initial 3x8 array of player 2's starting positions
		if isinstance(data[0], list):
			# set up players 2 positions on board
			# if a Square has a value 0, that spot is empty so the piece can be placed
			piece_count = 0
			for i in range(player_height):
				for j in range(board_width):
					if (data[i][j]!=0):
						# place the piece. The piece will be a square storing the piece value and indicating it is player 2
						self.mainconnection.board[player_height-1-i][board_width-1-j] = Square(data[i][j],2)
						piece_count += 1
						# when 10 players are placed, set initplayer on player2 to true
						if piece_count == 10:
							self.initplayer = True
			# if player1 has already finished placing, its initplayer will be true
			# if both initplayers are true, start the game
			if self.initplayer and self.mainconnection.initplayer == True:
				self.mainconnection.startGame()
		# if data[0] is a tuple this means that a move is being sent during game play.
		# The input will be a list of two tuples. The first tuple is the old position and the second is the new position after the move
		elif type(data[0]) is tuple:
			fight_status = ""
			# if the new position is a player the two pieces will fight
			if self.mainconnection.board[data[1][0]][data[1][1]].player == 1:
				fight_status = self.mainconnection.fight(data[0],data[1])
				if fight_status == "EOG":
					self.mainconnection.endGame(2)
			# otherwise the new position is a blank square and the piece should move normally
			else:
				self.mainconnection.board[data[1][0]][data[1][1]] = self.mainconnection.board[data[0][0]][data[0][1]]
				self.mainconnection.board[data[0][0]][data[0][1]] = Square()
			# create a sendable string of the board
			board_string = pickle.dumps(self.mainconnection.board)
			# send the new board to both players
			self.transport.write(board_string)
			self.mainconnection.transport.write(board_string)
			# player 2 has finished its turn now send turn to player 1
			self.mainconnection.transport.write('turn')

	# if player 2 loses connection, make sure 1 loses connection too
	def connectionLost(self, reason):
		print "player 2 connection lost"
		self.mainconnection.transport.loseConnection()

# the factory used to insantiate the SecondConnection
class SecondConnectionFactory(Factory):
	def __init__(self, mainconnection):
		self.mainconnection = mainconnection

	def buildProtocol(self, addr):
		return SecondConnection(self.mainconnection)

# The main connection contains most of the game logic. It is also connected to player1
class MainConnection(Protocol):
	# create the 2d array for board
	# the board is an 8x8 of empty squares
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
						# when 10 pieces are placed, set initplayer to true
						if piece_count == 10:
							self.initplayer = True
						self.initplayer = True
			# if both initplayers are true start the game
			if hasattr(self,'secondplayer'):
				if self.secondplayer.initplayer == True and self.initplayer == True:
					self.startGame()
		# a move has been sent over from player 1
		elif type(data[0]) is tuple:
			# check if there is a collision between the two players. if there is fight
			if self.board[data[1][0]][data[1][1]].player == 2:
				fight_status = self.fight(data[0],data[1])
				if fight_status == "EOG":
					self.endGame(1)
			else:
				# just a regular move
				self.board[data[1][0]][data[1][1]] = self.board[data[0][0]][data[0][1]]
				self.board[data[0][0]][data[0][1]] = Square()

			# update the board for both players
			board_string = pickle.dumps(self.board)
			self.secondplayer.transport.write(board_string)
			self.transport.write(board_string)

			# change turn
			self.secondplayer.transport.write('turn')

	# attacker stores the coordinates of the attacking piece and defender stores coordinates of defending piece
	# function determines the outcome for the attacking piece
	def fight(self, attacker, defender):
		# get the values for the attacker and defender
		attacking_value = self.board[attacker[0]][attacker[1]].value
		defending_value = self.board[defender[0]][defender[1]].value
		# deal with special cases
		# if the defender is the flag, the game should end
		if defending_value == 'f':
			return "EOG"
		# if attacker is the spy and defender 1, spy should win
		elif attacking_value == 's' and defending_value == "1":
			self.board[defender[0]][defender[1]] = self.board[attacker[0]][attacker[1]]
			self.board[attacker[0]][attacker[1]] = Square()
			return "win" # attacker wins
		# case for when the defender is a bomb
		elif defending_value == 'b':
			# when the attacker is an 8 the attacker should win, othewise it will lose
			if attacking_value == "8":
				self.board[defender[0]][defender[1]] = self.board[attacker[0]][attacker[1]]
				self.board[attacker[0]][attacker[1]] = Square()
				return "win" # attacker diffuses bomb and wins fight
			else:
				self.board[attacker[0]][attacker[1]] = Square()
				return "lost" # defender wins
		# convert s to a value of 10 so it can be compared to the other numbers
		elif defending_value == 's':
			defending_value = 10
		elif attacking_value == 's':
			attacking_value = 10

		# turn the remaining attacking and defending values to ints
		attacking_value = int(attacking_value)
		defending_value = int(defending_value)

		# the lower value should win. If there is a tie, both should lose
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

	# called at the end of the game. based on the winner, the game status is sent out to both players
	def endGame(self, winner):
		if winner == 1:
			self.transport.write("win")
			self.secondplayer.transport.write("lose")
		else:
			self.transport.write("lose")
			self.secondplayer.transport.write("win")

	# run when both players boards are initialized
	def startGame(self):
		# send starting board to both players
		pickle_board = pickle.dumps(self.board)
		self.secondplayer.transport.write(pickle_board)
		self.transport.write(pickle_board)
		# player 1 should start first so send turn to it
		self.transport.write('turn')

	# if player 1 loses connection, player 2 should too
	def connectionLost(self, reason):
		print "gameserver connection lost"
		self.secondplayer.transport.loseConnection()

# Factory used to create instance of MainConnection
class MainConnectionFactory(Factory):
	def buildProtocol(self, addr):
		return MainConnection()

# start listening for player 1 first
if __name__ == '__main__':
	reactor.listenTCP(PLAYER_ONE_PORT, MainConnectionFactory())
	reactor.run()
