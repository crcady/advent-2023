from __future__ import annotations
import sys

class cubegame():
    """Handles lines!"""
    def __init__(self, line: str):
        # Split into the game identifier and the sets
        game, data = line.split(':', 1)
        # Store the game ID
        self.id = int(game.split()[1])
        # Split up the sets and store how many we had
        textsets = data.split(';')
        self.sets = [cubeset(text) for text in textsets] #NB: probably not safe if there's only one set in the game

    def minset(self)->cubeset:
        red = 0
        green = 0
        blue = 0

        for s in self.sets:
            red = max(red, s.red)
            green = max(green, s.green)
            blue = max(blue, s.blue)
        
        return cubeset(f"{red} red, {green} green, {blue} blue")

class cubeset():
    """A random assortment of cubes"""
    def __init__(self, cubes: str):
        # Initialize the numbers to zero because we aren't guaranteed to see every color
        self.red = 0
        self.green = 0
        self.blue = 0

        # Split up the balls
        counts = cubes.split(',')

        # Iterate through and find the counts
        for cube in counts:
            count, color = cube.split()
            if color == "red":
                self.red = int(count)
            elif color == "green":
                self.green = int(count)
            elif color == "blue":
                self.blue = int(count)

    def power(self)->int:
        return self.blue * self.green * self.red

def check_possible(game: cubegame, red_max=12, green_max=13, blue_max=14):
    def check_set(cubes: cubeset, red_max:int, green_max: int, blue_max:int):
        return cubes.red <= red_max and cubes.blue <= blue_max and cubes.green <= green_max
    
    return_value = True
    for s in game.sets:
        return_value = return_value and check_set(s, red_max, green_max, blue_max)

    return return_value

if __name__ == "__main__":
    if len(sys.argv) < 2:
        fname = 'input'
    else:
        fname = sys.argv[1]

    with open(fname, 'r') as f:
        games = [cubegame(line) for line in f.readlines()]

        print("Found " + str(len(games)) + " games")
        possible_game_ids = [g.id for g in games if check_possible(g)]
        print(str(len(possible_game_ids)) + " games were possible")
        print(str(sum(possible_game_ids)) + " was the sum of their IDs")

        print("***************")

        for g in games:
            continue
            m = g.minset()
            print(f"Game {g.id} required at least {m.red} red cubes, {m.green} green cubes, and {m.blue} blue cubes for a power of {m.power()}")

        
        print(f"The sum of the powers was {sum([g.minset().power() for g in games])}")

