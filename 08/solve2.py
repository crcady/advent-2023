import sys
import re
from math import lcm

class Walker:
    def __init__(self, pattern:str):
        pattern = pattern.replace('L', '0')
        pattern = pattern.replace('R', '1')
        self.pattern = [int(x) for x in pattern]
        self.count = 0
        self.num = len(pattern)

    def walk(self)->int:
        index = self.count % self.num
        self.count += 1
        return self.pattern[index]
    
class Solver:
    def __init__(self, filename):
        with open(filename) as f:
            instructions = f.readline().strip()
            self.instructions = instructions
            self.nodes: dict[str, tuple[str, str]] = {}

            # read over the blank line
            f.readline()
            for line in f.readlines():
                nodes = re.findall('[A-Z][A-Z][A-Z]', line) #cached, no need to compile
                nodename: str = nodes[0]
                left: str = nodes[1]
                right: str = nodes[2]
                self.nodes[nodename] = (left, right)

    def solve1(self):
        current:list[str] = [x for x in self.nodes.keys() if x[2] == 'A']
        satisfied: list[list[tuple[str, int]]] = [[[(x, 0)]] for x in current]
        walker = Walker(self.instructions)
        numghosts = len(current)
        print(f"Starting walking on {numghosts} nodes...")
        while min([len(x) for x in satisfied]) < 2:
            step = walker.walk()
            #current = [self.nodes[c][step] for c in current]
            sat = True
            for i in range(numghosts):
                next = self.nodes[current[i]][step]
                sat = sat and next[2] == 'Z'
                if next[2] == 'A' or next[2] == 'Z':
                    satisfied[i].append((next, walker.count))
                current[i] = next
            #satisfied = [x[2] == 'Z' for x in current]
            #if satisfied.count(True) == numghosts:
            if sat:
                break
            
        seconds = [x[1] for x in satisfied]
        periods = [x[1] for x in seconds]

        solution = lcm(*periods)
        
        return solution

if __name__ == "__main__":
    if len(sys.argv) > 1:
        filename = sys.argv[1]
    else:
        filename = "tiny_input"

    solver = Solver(filename)

    print(f"Steps: {solver.solve1()}")
    #print(f"Total wild winnings: {solver.solve2()}")