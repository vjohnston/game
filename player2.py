# player 2 file

# Mitchell Patin

from twisted.internet.protocol import ClientFactory
from twisted.internet.protocol import Protocol
from twisted.internet import reactor


# defines server host name and port number
#SERVER_HOST = 'student00.cse.nd.edu'
SERVER_HOST = 'localhost'
SERVER_PORT = 32016


# class creates protocol that allows connection updates in an asynchronous manner
# class methods are executed as events occur in the server
class ClientConnection(Protocol):
	# connection with server created based on global variables SERVER_HOST and SERVER_PORT 
	# GET request written to this server
	def connectionMade(self):
		print 'new connection made to' , SERVER_HOST , 'port' , SERVER_PORT
		self.transport.write("test write")

	# print the data received by the server to the console
	# end connection with the server
	def dataReceived(self, data):
		print 'received data:' , data
		self.transport.loseConnection()

	# when connection is ended, print the info of matching server
	# reactor stops receiving events
	def connectionLost(self, reason):
		print 'lost connection to' , SERVER_HOST , 'port' , SERVER_PORT
		reactor.stop()

# creates an instance of the ClientConnection protocol and stores the persistent configuration
# allows the protocol to access this configuration and receive events about the connection
class ClientConnFactory(ClientFactory):
	def buildProtocol(self, addr):
		return ClientConnection()

# use the event processor 'reactor' to start the event loop
# create a client connection by instantiating ClientConnFactory
# then create a TCP connection with it
reactor.connectTCP(SERVER_HOST, SERVER_PORT, ClientConnFactory())
reactor.run()
