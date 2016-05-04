# player 2 file
from twisted.internet import reactor
from twisted.internet.protocol import Protocol
from twisted.internet.protocol import ClientFactory
import cPickle as pickle
from display import GameSpace

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
		#self.board = [[i for i in range(8)] for j in range(3)]
		self.gs = GameSpace(2)
		self.initboard = self.gs.playerSetup()
		pd = pickle.dumps(self.initboard)
		self.transport.write(pd)
		self.turn = 0
		#self.gs.waitingForOpponent()

	def dataReceived(self, data):
		# check if turn is sent
		change_turn = False
		if "turn" in data:
			change_turn = True
			data = data.replace("turn","")
		if "win" in data:
			self.gs.end("winner")
		elif "lose" in data:
			self.gs.end("loser")
		else:
			# if Square is in the data, we know that the board is being sent in
			if "Square" in data:
				self.rotboard = pickle.loads(data)
				# make sure the board is rotated for player2
				self.board = list(reversed(zip(*list(reversed(zip(*self.rotboard))))))
				self.gs.updateBoard(self.board)

			# after updating the board, if turn has been sent allow player to submit next move
			if change_turn == True:
				self.turn = 1
				rot_coordinates = self.gs.main()
				rot_old = (7-rot_coordinates[0][0],7-rot_coordinates[0][1])
				rot_new = (7-rot_coordinates[1][0],7-rot_coordinates[1][1])
				coordinates = [rot_old,rot_new]
				self.submitMove(coordinates)

	def submitMove(self, coordinates):
		pd = pickle.dumps(coordinates)
		self.transport.write(pd)
		self.turn = 0

	def connectionLost(self, reason):
		self.gs.exit()
		reactor.stop()

class PlayerConnectionFactory(ClientFactory):
	def buildProtocol(self, addr):
		return PlayerConnection()

if __name__ == '__main__':
	reactor.connectTCP('localhost',PLAYER_TWO_PORT, PlayerConnectionFactory())
	reactor.run()
