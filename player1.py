from twisted.internet import reactor
from twisted.internet.protocol import Protocol
from twisted.internet.protocol import ClientFactory
import cPickle as pickle
from display import GameSpace

PLAYER_ONE_PORT = 32025


# This class represents one square on the board. It stores the value of the Square and which players Square it is
class Square:
	# when the splot on the board is empty, the Square will just have the value 0
	def __init__(self, value=0, player=0):
		self.value = value
		self.player = player

class PlayerConnection(Protocol):
	# create a gamespace to load the initial players setup
	def connectionMade(self):
		self.gs = GameSpace(1)
		self.initboard = self.gs.playerSetup()
		# send setup to server
		pd = pickle.dumps(self.initboard)
		self.transport.write(pd)
		self.turn = 0

	def dataReceived(self, data):
		# check if turn is sent
		change_turn = False
		if "turn" in data:
			change_turn = True
			data = data.replace("turn","")
		# check for a win or lost, otherwise load board
		if "win" in data:
			self.gs.end("winner")
		elif "lose" in data:
			self.gs.end("loser")
		else:
			# if Square is in the data, we know that the board is being sent in
			if "Square" in data:
				self.board = pickle.loads(data)
				self.gs.updateBoard(self.board)

			# after updating the board, if turn has been sent allow player to submit next move
			if change_turn == True:
				self.turn = 1
				coordinates = self.gs.main()
				self.submitMove(coordinates)
	
	# get the move from the gamespace and send it to the server
	def submitMove(self, coordinates):
		pd = pickle.dumps(coordinates)
		self.transport.write(pd)
		self.turn = 0

	# if the connection is lost, stop the reactor and exit the gamespace
	def connectionLost(self, reason):
		self.gs.exit()
		reactor.stop()

class PlayerConnectionFactory(ClientFactory):
	def buildProtocol(self, addr):
		return PlayerConnection()

if __name__ == '__main__':
	reactor.connectTCP('localhost',PLAYER_ONE_PORT, PlayerConnectionFactory())
	reactor.run()
