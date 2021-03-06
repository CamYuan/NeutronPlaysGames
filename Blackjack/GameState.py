from PlayerClass import Player
from BlackjackHandClass import BlackjackHand
from HelperFunctions import *

'''
[

]
'''
'''
Player Objects. This table can hold a max of 5 players.
'''
player1 = Player("p1", 10000000)
player2 = Player("p2")
player3 = Player("p3")
player4 = Player("p4")
player5 = Player("p5")
dealer = Player("dealer")


#Global objects
'''
table list and players list are sort of duplicates because it makes looping a
bit easier, but I should consider consolidating...

Generating tableScores list based on the number of players
'''
tableMinBet = 10
tableMaxBet = 1000
players = [player1]
table = [player1, dealer]
cardShoe = []
isShuffleTime = False
num_decks = 6 #cardShoes generally have between 6-8 decks

#Card Counting
RunningCount = 0
SuitCounts = [0,0,0,0]

choices = ["S", "H", "D", "T"] #choices 0-3
from Model_128_64_4 import *
model = create_model()
model.load_weights('./checkpoints/TrainedModel')
