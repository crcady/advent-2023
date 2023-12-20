import sys

class card:
    """Handles one card"""
    def __init__(self, text):
        label, numbers = text.split(":")
        _, id = label.split()
        winning_numbers, card_numbers = numbers.split("|")

        self.id = int(id)
        self.winning_numbers = [int(n) for n in winning_numbers.split()]
        self.card_numbers = [int(n) for n in card_numbers.split()]

    def score(self):
        """The first match makes the card with one point and each match after the first doubles the value of that card"""
        num_matches = self.num_matches()
        if num_matches > 0:
            score = pow(2, num_matches - 1)
        else:
            score = 0
        return score
    
    def num_matches(self):
        matched_numbers = set(self.winning_numbers).intersection(set(self.card_numbers))
        num_matches = len(matched_numbers)
        return num_matches

    
class cardtable:
    """
    Handles a table of cards and winning numbers:
    Card 1: 41 48 83 86 17 | 83 86  6 31 17  9 48 53
    """
    def __init__(self, filename):
        with open(filename, 'r') as f:
            self.cards = [card(line) for line in f.readlines()]
    
    def score(self):
        scores = [c.score() for c in self.cards]
        return sum(scores)
    
    def score2(self):
        table_length = len(self.cards)
        counts = [1 for i in range(table_length)]

        for i in range(table_length):
            count = counts[i]
            matches = self.cards[i].num_matches()
            for j in range(i+1, i+matches+1):
                if j == table_length: # Don't go past the end of the table!
                    break
                counts[j] += count
        
        return sum(counts)
    
if __name__ == "__main__":
    if len(sys.argv) > 1:
        filename = sys.argv[1]
    else:
        filename = "input"

    table = cardtable(filename)

    print(f"Scored {table.score()} points")
    print(f"After reading the rules, scored {table.score2()} points")