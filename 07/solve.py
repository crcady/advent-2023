import sys

class Solver:
    def __init__(self, filename: str):
        hands: list[tuple[str, int]] = []

        with open(filename, 'r') as f:
            for line in f.readlines():
                hand, bid = line.split()
                hands.append((hand, int(bid)))

        self.hands = hands

    def cardValue(self, card: str)->int:
        if card.isnumeric():
            return int(card)
        
        if card == 'T':
            return 10
        
        if card == 'J':
            return 11
        
        if card == 'Q':
            return 12
        
        if card == 'K':
            return 13
        
        if card == 'A':
            return 14
        
        assert(False)

    def cardValue2(self, card: str)->int:
        if card.isnumeric():
            return int(card)
        
        if card == 'T':
            return 10
        
        if card == 'J':
            return 1
        
        if card == 'Q':
            return 12
        
        if card == 'K':
            return 13
        
        if card == 'A':
            return 14
        
        assert(False)

    def handValue(self, hand: str)->int:
        cards: list[str] = []
        cards.extend(str(x) for x in range (2, 10))
        cards.extend(['T', 'J', 'Q', 'K', 'A'])


        counts = [hand.count(card) for card in cards]

        if counts.count(5) > 0:
            return 7 # Five of a kind
        
        if counts.count(4) > 0:
            return 6 # Four of a kind
        
        if counts.count(3) > 0:
            if counts.count(2) > 0:
                return 5 # Full House
            else:
                return 4 # Three of a kind
            
        return counts.count(2) + 1 # Two Pair, One Pair, High Card
    
    def handValue2(self, hand:str)->int:
        cards: list[str] = []
        cards.extend(str(x) for x in range (2, 10))
        cards.extend(['T', 'Q', 'K', 'A'])

        counts = [hand.count(card) for card in cards]
        jokerCount = hand.count('J')

        if counts.count(5) > 0 or jokerCount >= 4:
            return 7 # Five of a kind
        
        if counts.count(4) > 0:
            return 6 + jokerCount # Four of a kind (or upgrade to 5)
        
        if counts.count(3) > 0: #Max Jokers is 2
            if counts.count(2) > 0:
                return 5 + jokerCount # Full House/4kind/5kind
            else:
                if jokerCount == 0:
                    return 4 # Three of a kind
                else:
                    return 5 + jokerCount # Convert three of a kind to 4/5 of a kind
            
        if counts.count(2) == 2: #Two pairs, max joker is 1
            if jokerCount == 0:
                return 3 #2pair
            if jokerCount == 1:
                return 5 #Full House

            
        if counts.count(2) == 1: # One Pair, max joker is 3
            if jokerCount == 0:
                return 2 #OnePair
            if jokerCount == 1:
                return 4 #ThreeKind
            if jokerCount == 2:
                return 6 #4kind
            if jokerCount == 3:
                return 7 #FiveKind

        # No pairs if we get here, but max 3 jokers    
        if jokerCount == 0:
            return 1 #Highcard
        if jokerCount == 1:
            return 2 #Onepair
        if jokerCount == 2:
            return 4 #ThreeKind
        if jokerCount == 3:
            return 6 #FourKind
            
    def digitmap(self, digit: int, max_value: int)->str:
        """Maps max_value to 'a', max_value -1 to 'b', and so on"""
        return chr(ord('a') + max_value - digit)
    
    def handkey(self, hand: str):
        key = ''
        hv = self.handValue(hand)
        key += self.digitmap(hv, 7)

        for card in hand:
            cv = self.cardValue(card)
            key += self.digitmap(cv, 14)

        return key
    
    def handkey2(self, hand: str):
        key = ''
        hv = self.handValue2(hand)
        key += self.digitmap(hv, 7)

        for card in hand:
            cv = self.cardValue2(card)
            key += self.digitmap(cv, 14)

        return key
    
    def solve1(self):
        bids = [(self.handkey(h), bid) for (h, bid) in self.hands]
        bids.sort(key = lambda x: x[0])
        total = 0
        for i in range(len(bids)):
            rank = len(bids) - i
            winnings = rank * bids[i][1]
            total += winnings

        return total
    
    def solve2(self):
        bids = [(self.handkey2(h), bid) for (h, bid) in self.hands]
        bids.sort(key = lambda x: x[0])
        total = 0
        for i in range(len(bids)):
            rank = len(bids) - i
            winnings = rank * bids[i][1]
            total += winnings

        return total

        
if __name__ == "__main__":
    if len(sys.argv) > 1:
        filename = sys.argv[1]
    else:
        filename = "tiny_input"

    solver = Solver(filename)

    print(f"Total winnings: {solver.solve1()}")
    print(f"Total wild winnings: {solver.solve2()}")
