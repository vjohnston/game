# player 2 file
<<<<<<< HEAD
from twisted.internet import reactor
from twisted.internet.protocol import Protocol
from twisted.internet.protocol import ClientFactory
import cPickle as pickle

PLAYER_TWO_PORT = 32016

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

class PlayerConnection(Protocol):
	def connectionMade(self):
		print "player 1 connected"
		self.board = [[i for i in range(8)] for j in range(3)]
		pd = pickle.dumps(self.board)
		self.transport.write(pd)
		self.turn = 0

	def dataReceived(self, data):
		# check if turn is sent
		change_turn = False
		if "turn" in data:
			print "player 2 turn"
			change_turn = True
			data = data.replace("turn","")
		# if Square is in the data, we know that the board is being sent in
		if "Square" in data:
			print "update board"
			self.rotboard = pickle.loads(data)
			# make sure the board is rotated for player2
			self.board = list(reversed(zip(*list(reversed(zip(*self.rotboard))))))
			self.updateBoard()

		# after updating the board, if turn has been sent allow player to submit next move
		if change_turn == True:
			self.turn = 1
			old, new = self.getMove()
			if (self.checkValid(old,new)):
				rot_old = (7-old[0],7-old[1])
				rot_new = (7-new[0],7-new[1])
				self.submitMove(rot_old,rot_new)

	def updateBoard(self):
		
		self.printBoard()
		pass

	def getMove(self):
		old = (3,4)
		new = (2,4)
		return old, new

	def submitMove(self, old, new):
		data = [old,new]
		pd = pickle.dumps(data)
		self.transport.write(pd)
		self.turn = 0

	def checkValid(self, old_pos, new_pos):
		# make sure there is a Square there
		if self.board[old_pos[0]][old_pos[1]].value == 0:
			return False
		# check the bounds of the new position
		if (new_pos[0] < 0 or new_pos[0] > 7 or new_pos[1] < 0 or new_pos[1] > 7):
			return False
		# make sure it only moved by one position
		if self.board[old_pos[0]][old_pos[1]].value != 9:
			if not (abs(new_pos[0]-old_pos[0])==1 and abs(new_pos[1]-old_pos[1])==0) or (abs(new_pos[0]-old_pos[0])==0 and abs(new_pos[1]-old_pos[1])==1):
				return False
		# check if a Square is already in that position
		new_pos_player = self.board[new_pos[0]][new_pos[1]].player
		if new_pos_player == 1:
			return False
		elif new_pos_player == 2:
			# we want to show the player
			pass
		return True

	def connectionLost(self, reason):
		print "player 2 connection lost"
		reactor.stop()

	# use for debugging print board
	def printBoard(self):
		for row in self.board:
 			for square in row:
				print '{:4}'.format(square.value),
			print

class PlayerConnectionFactory(ClientFactory):
	def buildProtocol(self, addr):
		return PlayerConnection()

if __name__ == '__main__':
	reactor.connectTCP('localhost',PLAYER_TWO_PORT, PlayerConnectionFactory())
	reactor.run()
