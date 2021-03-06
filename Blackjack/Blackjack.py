from CardClass import Card
from HelperFunctions import *
from GameState import *
import numpy as np
import pickle
import sys, os, io

def betBeforeHand(players):
    for player in players:
        validBet = False
        while(not validBet):
            try:
                betAmount = 5
                # betAmount = int(input("How much do you want to bet? "))
                # print("Betting: " + str(betAmount))
                validBet = player.bet(betAmount, player.hands[0])
            except:
                print("Invalid Bet. Please enter a number")
                validBet = False

def payout(player, hand, position):
    # print(player.bankroll)
    if position == 'WIN':
        player.recievePayout(hand, 1)
    elif position == 'PUSH':
        player.recievePayout(hand, 0)
    elif position == 'BLACKJACK':
        player.recievePayout(hand, 1.5)
    # print(player.bankroll)
    #else we have lost. The bet was already removed from the our bankroll

'''
@param list object of a single player
@return void

Pops 1 card off the cardShoe and adds it to a hand
If the cutCard is dealt, this will be the last hand. Set isShuffleTime to true
'''
def hit(hand):
    card = cardShoe.pop()
    if(card.rank == 0):
        # print("----------------------CUT CARD----------------------")
        global isShuffleTime
        isShuffleTime = True
        card = cardShoe.pop()
    #card count here I think
    hand.addCard(card)

'''
@param list of all players
@return void

Gives 2 cards to all players.
Dealer should be the last index of the players
'''
def deal(table):
    for i in range(0,2):
        for player in table:
            for hand in player.hands:
                hit(hand)

def playHand(player):
    global totalHands
    for hand in player.hands:
        totalHands += 1
        if len(hand.cards) < 2:
            hit(hand)
        hand.checkBlackjack()
        # print(player, hand.getSoftScore(), hand.getHardScore(), hand)
        choice = ''
        while choice != 's' and hand.getSoftScore() != 21:
            options = "[H]it or [S]tand"
            doubleDownEnabled = False
            splitEnabled = False
            if hand.canSplit and player.hasEnoughFunds():
                options +=  " or Spli[T]"
                splitEnabled = True
            if hand.canDoubleDown and player.hasEnoughFunds():
                options +=  " or [D]oubledown"
                doubleDownEnabled = True
            options += ": "
            # choice = input(options).lower()
            choice = getModelPrediction(dealer, hand)
            # if(choice == 'd' and doubleDownEnabled == False): #correct decisions that are not game legal
            #     choice = 'h'
            #     print("switching to hit")
            # if(choice == 't' and hand.canSplit == False): #correct decisions that are not game legal
            #     choice = 'h'
            #     print("switching to hit")
            if(hand.splitAces): #Only get 1 card on split Aces
                choice = 's'
            if choice == 's':
                pass
            elif choice == 'h':
                hit(hand)
                # print(player, hand.getSoftScore(), hand.getHardScore(), hand)
                if hand.getHardScore() >= 21:
                    choice = 's'
            elif choice == 'd' and doubleDownEnabled:
                player.doubleDown(hand)
                hit(hand)
                # print(player, hand.getSoftScore(), hand.getHardScore(), hand)
                choice = 's'
            elif choice == 't' and splitEnabled:
                player.splitHand(hand)
                hit(hand)
                if(hand.splitAces): #Only get 1 card on split Aces
                    choice = 's'
                # print(player, hand.getSoftScore(), hand.getHardScore(), hand)
            else:
                print("Invalid Input")
'''
If all players have busted or have blackjack, the hand is over.
Don't deal any cards for the dealer
'''
def deadHand(players):
    deadHand = True #allBustOrBlackjack
    for player in players:
        for hand in player.hands:
            if hand.hasBlackjack or not hand.bust:
                deadHand = False
    return deadHand

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
    dealerScore = dealer.hands[0].getSoftScore()
    # print("DEALER : ", dealerScore, dealer.hands[0])
    '''
    Check if the dealer has blackjack. If true, all players lose immediately
    UNLESS a player also has blackjack, then they PUSH.
    '''
    if dealer.hands[0].hasBlackjack:
        for player in players:
            for hand in player.hands:
                if hand.hasBlackjack:
                    currHand = "PUSH"
                    player.pushes += 1
                else:
                    currHand = "LOSS"
                    player.losses += 1
                # print(player, currHand, hand)
                payout(player, hand, currHand)
    else:
        for player in players:
            for hand in player.hands:
                handScore = hand.getSoftScore()
                if not hand.bust:
                    if hand.hasBlackjack:
                        currHand = "BLACKJACK"#implement 1.5x
                        player.wins += 1
                    elif dealer.hands[0].bust:
                        currHand = "WIN"
                        player.wins += 1
                    elif handScore > dealerScore:
                        currHand = "WIN"
                        player.wins += 1
                    elif handScore == dealerScore:
                        currHand = "PUSH"
                        player.pushes += 1
                    else:
                        currHand = "LOSS"
                        player.losses += 1
                else:
                    currHand = "BUST"
                    player.losses += 1
                # print(player, currHand, handScore, hand)
                payout(player, hand, currHand)


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

def playRound(table, players):
    betBeforeHand(players) #1
    deal(table) #2
    '''if the dealer has blackjack, the hand is over. No insurance (currently?)
    Move to scoring/payout
    '''
    if not dealer.hands[0].checkBlackjack(): #3
        # print("Dealer's up Card: " , dealerUpCard(dealer))
        for player in players: #4
            playHand(player)

        if not deadHand(players):
            while dealer.hands[0].getSoftScore() < 17: #5 #dealer stays on soft 17
                hit(dealer.hands[0])
                # print("DealerHand", dealer.hands[0])
    scoreTable(players, dealer) #6 #7
    resetTable(table) #8
    # print("--------------------------------")

alldecisions = []
def getModelPrediction(dealer, hand):
    inputs = [hand.getSoftScore(), hand.getHardScore(), dealerUpCard(dealer).rank, hand.cards[0].rank, hand.canSplit, hand.canDoubleDown, len(hand.cards)]
    normalizedInputs =[inputs[0]/21, inputs[1]/21, inputs[2]/13, inputs[3]/13, int(inputs[4])/1.0, int(inputs[5])/1.0, inputs[6]/14]
    output = model.predict(np.expand_dims(normalizedInputs, axis=0))
    choice = choices[np.argmax(output)].lower()
    # print(inputs, choice)
    inputs.append(choice)
    alldecisions.append(inputs)
    return choice
'''
Clear out the rest of the shoe. Reset isShuffleTime to False. This can be
used for continuous gaming or set a game count.

Run the game. Put this in a for loop if you want to run the game
X times in a row
'''
totalHands = 0
def game(numSessions):
    for i in range(0, numSessions):
        print("Game",i)
        cardShoe.clear()
        global isShuffleTime
        isShuffleTime = False
        loadShoe(num_decks, cardShoe)
        while not isShuffleTime:
            playRound(table, players)
        #print(isShuffleTime)


# text_trap = io.StringIO()
# sys.stdout = text_trap

game(500)
# sys.stdout = sys.__stdout__

print(player1.wins, "-", player1.losses, "-", player1.pushes, "/", totalHands )
print("{:.3%}".format(player1.wins/totalHands), "-", "{:.3%}".format(player1.losses/totalHands), "-", "{:.3%}".format(player1.pushes/totalHands) )

totalHands = totalHands - player1.pushes
print("\nExcluding ties")
print("{W:^9}-{L:^9}/{T:^9}".format(W="Wins", L="Loss",T="Total"))
print("{W:^9}-{L:^9}/{T:^9}".format(W=player1.wins, L=player1.losses,T=totalHands))
print("{Wins:.2%}-{Losses:.2%}".format(Wins=player1.wins/totalHands,Losses=player1.losses/totalHands))
print("Good Games!")

pickle_out = open("500_alldecisions.pickle", "wb")
pickle.dump(alldecisions, pickle_out)
pickle_out.close()
