from twisted.internet import reactor
from twisted.internet.protocol import Protocol
from twisted.internet.protocol import Factory
import pygame
import sys
import math
from pygame.locals import *

PLAYER_ONE_PORT = 32015
PLAYER_TWO_PORT = 32016

class PlayerConnection(Protocol):
	def connectionMade(self):
		print "player connected"

	def dataReceived(self, data):
		print 'received data:' , data		
	
class PlayerConnectionFactory(Factory):
	def buildProtocol(self, addr):
		return PlayerConnection()

if __name__ == '__main__':
	reactor.listenTCP(PLAYER_ONE_PORT, PlayerConnectionFactory())
	reactor.listenTCP(PLAYER_TWO_PORT, PlayerConnectionFactory())
	reactor.run()
