import sys
import re

class Walker:
    def __init__(self, pattern:str):
        self.pattern = pattern
        self.count = 0

    def walk(self)->str:
        index = self.count % len(self.pattern)
        self.count += 1
        return self.pattern[index]

class Solver:
    def __init__(self, filename):
        with open(filename) as f:
            instructions = f.readline().strip()
            self.instructions = instructions
            self.nodes: dict[str, dict[str, str]] = {}

            # read over the blank line
            f.readline()
            for line in f.readlines():
                nodes = re.findall('[A-Z][A-Z][A-Z]', line) #cached, no need to compile
                nodename: str = nodes[0]
                left: str = nodes[1]
                right: str = nodes[2]
                self.nodes[nodename] = {'L': left, 'R': right}

    def solve1(self):
        walker = Walker(self.instructions)
        current = 'AAA'
        while current != 'ZZZ':
            current = self.nodes[current][walker.walk()]

        return walker.count

if __name__ == "__main__":
    if len(sys.argv) > 1:
        filename = sys.argv[1]
    else:
        filename = "tiny_input"

    solver = Solver(filename)

    print(f"Steps: {solver.solve1()}")
    #print(f"Total wild winnings: {solver.solve2()}")