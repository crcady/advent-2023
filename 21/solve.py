from __future__ import annotations
import sys
from timeit import default_timer as timer

type Coord = tuple[int, int]
type Plot = frozenset[Coord]

def initial_plot(start: Coord) -> Plot:
    return frozenset([start])

def neighbors(plot: Plot) -> Plot:
    n: list[Coord] = []
    for c in plot:
        n.append((c[0]-1, c[1]))
        n.append((c[0]+1, c[1]))
        n.append((c[0], c[1]-1))
        n.append((c[0], c[1]+1))

    return frozenset(n)

def next_plot(current_plot: Plot, open_areas: Plot) -> Plot:
    return open_areas.intersection(neighbors(current_plot))

class Solver():
    def __init__(self, filename: str):
        self.reachable:set[Coord] = set()
        row_number = 0
        with open(filename, 'r') as f:
            for line in f:
                line = line.strip()
                col_number = 0
                for char in line:
                    if char == 'S':
                        self.start = (row_number, col_number)
                        self.reachable.add((row_number, col_number))

                    elif char == '.':
                        self.reachable.add((row_number, col_number))

                    col_number += 1
                row_number += 1

        self.height = row_number
        self.width = col_number

    def solve1(self, steps: int) -> int:
        """Naive solver for part 1"""
        reachable_sets: list[set[Coord]] = [set([self.start])]
        for i in range(steps):
            new_set = set()
            for (x, y) in reachable_sets[-1]:
                for coord in [(x-1, y), (x+1, y), (x, y-1), (x, y+1)]:
                    if coord in self.reachable:
                        new_set.add(coord)
            reachable_sets.append(new_set)

        return len(reachable_sets[-1])
    
    def solve2(self, steps: int) -> int:
        """Memoizing solver for part 1"""
        current = initial_plot(self.start)
        reachable = frozenset(self.reachable)

        cache: dict[Plot, Plot] = {}

        for _ in range(steps):
            if current in cache:
                current = cache[current]
            else:
                next = next_plot(current, reachable)
                cache[current] = next
                current = next

        return len(current)
    
    def solve3(self, seconds: int) -> int:
        # Begin with the starting point in the (0, 0) quadrant
        last_dict: dict[Coord, set[Coord]] = {self.start: set([(0, 0)])}
        

        file = open("tiny_output.csv", "w")
        steps = 1

        start_time = timer()
        last_time = start_time
        while steps < 5000:
            new_dict: dict[Coord, set[Coord]] = {}
            for (x, y), s in last_dict.items():

                # (x-1, y)
                if x > 0:
                    p = (x-1, y)
                    if p in self.reachable:
                        if p in new_dict:
                            new_dict[p].update(s)
                        else:
                            new_dict[p] = s.copy()
                else:
                    p = (self.height-1, y)
                    if p in self.reachable:
                        if p in new_dict:
                            new_dict[p].update((i-1, j) for (i, j) in s)
                        else:
                            new_dict[p] = set((i-1, j) for (i, j) in s)

                # (x+1, y)
                if x+1 < self.height:
                    p = (x+1, y)
                    if p in self.reachable:
                        if p in new_dict:
                            new_dict[p].update(s)
                        else:
                            new_dict[p] = s.copy()
                else:
                    p = (0, y)
                    if p in self.reachable:
                        if p in new_dict:
                            new_dict[p].update((i+1, j) for (i, j) in s)
                        else:
                            new_dict[p] = set((i+1, j) for (i, j) in s)

                # (x, y-1)
                if y > 0:
                    p = (x, y-1)
                    if p in self.reachable:
                        if p in new_dict:
                            new_dict[p].update(s)
                        else:
                            new_dict[p] = s.copy()
                else:
                    p = (x, self.width-1)
                    if p in self.reachable:
                        if p in new_dict:
                            new_dict[p].update((i, j-1) for (i, j) in s)
                        else:
                            new_dict[p] = set((i, j-1) for (i, j) in s)

                # (x, y+1)
                if y+1 < self.width:
                    p = (x, y+1)
                    if p in self.reachable:
                        if p in new_dict:
                            new_dict[p].update(s)
                        else:
                            new_dict[p] = s.copy()
                else:
                    p = (x, 0)
                    if p in self.reachable:
                        if p in new_dict:
                            new_dict[p].update((i, j+1) for (i, j) in s)
                        else:
                            new_dict[p] = set((i, j+1) for (i, j) in s)

            count = sum(len(x) for x in new_dict.values())
            new_time = timer()
            file.write(",".join(str(x) for x in [steps, count, new_time-last_time]) + "\n")

            last_dict = new_dict
            last_time = new_time
            steps += 1

        file.close()
        return steps - 1
   
if __name__ == "__main__":
    steps = 3600
    if len(sys.argv) > 1:
        filename = sys.argv[1]
    else:
        filename = "tiny_input"

    solver = Solver(filename)

    #print(f"First Solution: {solver.solve1(steps)}")
    print(f"{solver.solve3(steps)} steps taken in {steps} seconds")
