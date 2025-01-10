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

   
if __name__ == "__main__":
    steps = 256
    if len(sys.argv) > 1:
        filename = sys.argv[1]
    else:
        filename = "tiny_input"

    solver = Solver(filename)

    print(f"First Solution: {solver.solve1(steps)}")
    start = timer()
    ans2 = solver.solve2(steps)
    end = timer()
    print(f"Took {steps} steps in {end - start} seconds, got {ans2}")