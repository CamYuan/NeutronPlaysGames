from CardClass import Card
import random
import math


'''
@param list object of a single player
@return void

Pops 1 card off the cardShoe and adds it to the player's hand
If the cutCard is dealt, this will be the last hand. Set isShuffleTime to true
'''
def hit(player):
    card = cardShoe.pop()
    if(card.rank == 0):
        global isShuffleTime
        isShuffleTime = True
        card = cardShoe.pop()
        print("----CUT CARD----")
    player.hitHand(card)

'''
@param list of all players
@return void

Gives 2 cards to all players.
Dealer should be the last index of the players
'''
def deal(table):
    for i in range(0,2):
        for player in table:
            hit(player)
    


        


'''
@param list object of all person's hands
@return void

Discard's all player's hands and the dealer's hand. If we hit the cutCard
then we also discard the rest of the shoe and generate a new shoe
'''
def clearTable(table):
    for hand in table:
        hand.clear()
    for i in range(tableCount):
         tableScores[i] = "Null"

'''
@param void
@return void

Clear out the rest of the shoe. Reset isShuffleTime to False. This can be
used for continuous gaming or set a game count.
'''
def newDeck():
    cardShoe.clear()
    global isShuffleTime
    isShuffleTime = False
    loadShoe()

'''
@param list object of players
@param dealer hand
@return void

First confirm the dealer's score and whether or not they busted.
If the player busted first, they lose.
If the dealer busted, all remaining players should win
If the players hand is higher than the dealers, they should win
If the players hand is the same as the dealers, they PUSH
If the players hand is less than the dealers, they lose

Players' hands and dealer's should not be higher than 21
as it should have been caught by BUST logic

Also give an easier readout for the print object
'''
def scoreTable(players, dealer):
    global tableScores
    dealerHand = getSoftScore(dealer)
    

    print()
    if tableScores[dealerIndex] != "BUST":
        tableScores[dealerIndex] = dealerHand
    print("DEALER : ", tableScores[tableCount-1])
    playerIndex = 0
    for player in players:
        playerScore = getSoftScore(player)
        if tableScores[playerIndex] != "BUST":
            if tableScores[playerIndex] == "BlackJack!":
                pass
            elif  tableScores[dealerIndex] == "BUST":
                tableScores[playerIndex] = "WIN"
            elif playerScore > dealerHand:
                tableScores[playerIndex] = "WIN"
            elif playerScore == dealerHand:
                tableScores[playerIndex] = "PUSH"
            else:
                tableScores[playerIndex] = 'LOSS'
    printWinLoss()



'''
@param list object of players
@param dealer hand
@return void

Check if the dealer has blackjack. If true, all players lose immediately
UNLESS a player also has blackjack, then they PUSH.

If a player has blackjack and the dealer does not, they win with Blackjack
'''
def checkBlackjacks(players,dealer, tableScores):
    global tableScores
    dealerScore = getSoftScore(dealer)
    if dealerScore == 21:
        tableScores[dealerIndex] = "BlackJack!"
    playerIndex = 0
    for player in players:
        playerScore = getSoftScore(player)
        if playerScore == 21:
            tableScores[playerIndex] = "BlackJack!"
            print("BlackJack!")
        playerIndex += 1
    #Blackjack Win/Loss
    if tableScores[dealerIndex] == "BlackJack!":
        playerIndex = 0
        for player in players:
            if tableScores[playerIndex] == "BlackJack!":
                tableScores[playerIndex] = "PUSH"
            else:
                tableScores[playerIndex] = "LOSE"
    
                
                
        
    
                



'''
Runs through the hand:
1) TODO: Bet
2) Deal the hand
3) Check for blackjacks -> Not offering insurance
4) Let each player make hit/stand/split/doubledown decisions
5) Play out the dealer hand
6) Calculate scores
7) TODO: Payout
8) Clear the hands/table

If the dealer gets a blackjack, the whole table loses automatically UNLESS
the player also has blackjack, then they PUSH
If a player has blackjack, they win immediately 1.5x the amount they bet

Each player makes a series of decisions. For now it is only [Hit] and [S]tand
Hitting gives the player a new card and they can then make the same decision
When they choose to stand, they will not get any more cards
If they BUST, they lose immediately
After the players make their choices, the dealer then hits based on
predetermined rules. In this case, they will stay on a Soft 17 or higher

After the dealer makes all their choices, score the table to determine winners
Discard all the cards and get ready for the next hand

'''
def playHand():
    #1
    deal(table) #2
    checkBlackjacks(players,dealer) #3
    if tableScores[tableCount-1] != "BlackJack!": #4
        print("Dealer's up Card: " , dealer[0])
        playerIndex = 0
        for player in players:
            print(getSoftScore(player), getHardScore(player), player)
            choice = ''
            while choice != 's':
                choice = input("[H]it or [S]tand ").lower()
                if choice == 'h':
                    hit(player)
                    print(getSoftScore(player), getHardScore(player), player)
                    if getHardScore(player) > 21:
                        tableScores[playerIndex] = "BUST"
                        choice = 's'
                print(player)
            playerIndex += 1
        #dealer stays on soft 17
        while getSoftScore(dealer) < 17: #5
            hit(dealer)
            print("DealerHand", dealer)
            if getHardScore(dealer) > 21:
                tableScores[tableCount-1] = "BUST"
        scoreTable(players, dealer) #6
    #7
    clearTable(table) #8
    print("--------------------------------")
    
            




'''
Run the game. Put this in a for loop if you want to run the game
X times in a row
'''
def game():
    newDeck()
    while not isShuffleTime:
        playHand()
        #print(isShuffleTime)
game()
print("Good Games!")

'''
TODO: Generate Test data for basic Feed Forward Neural Net
    -Feed forward networks have no 'memory' so each hand state
    will act like an independent hand
TODO: Train Neural Net on test data
TODO: Train Neural Net based on Win/Loss to see if it comes up with the same basic strategy
TODO: Add logic for double downs and splits
TODO: Re-do Neural Net with new information
TODO: Implement Hi-Lo Card Count and other card counting systems
TODO: Test Nueral net efficiency with new information
TODO: Implement RNN with all information.
TODO: Test different training strategies and see what is best
TODO: Build Neural Net for betting strategies
TODO: Throw it all together in a DQRNN maybe
'''

