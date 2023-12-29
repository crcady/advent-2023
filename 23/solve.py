from __future__ import annotations
from dataclasses import dataclass, field
import sys

type Coord = tuple[int, int]

@dataclass
class Path:
    current: Coord
    history: list[set[Coord]] = field(default_factory=list)
    coord_stack: list[list[tuple[Coord]]] = field(default_factory=list, init=False)

    def __post_init__(self):
        self.history.append(set())

    def unseen(self, coord: Coord)->bool:
        for s in self.history:
            if coord in s:
                return False
        return True
    
    def see(self, coord: Coord):
        self.history[-1].add(coord)

    def steps(self)->int:
        return sum(len(x) for x in self.history)
    
    def fork(self, next_steps: list[Coord]):
        next = next_steps.pop()
        self.history.append(set())
        if len(next) == 1:
            self.current = next[0]
        else:
            self.see(next[0])
            self.current = next[1]

        self.coord_stack.append(next_steps)
    
    def backtrack(self)->bool:
        """Returns True if we can keep going"""
        if len(self.coord_stack) == 0:
            return False
        
        next_steps = self.coord_stack[-1]
        if len(next_steps) == 0:
            self.history.pop()
            self.coord_stack.pop()
            return self.backtrack()
        
        next = next_steps.pop()
        self.history[-1].clear()
        if len(next) == 1:
            self.current = next[0]
        else:
            self.see(next[0])
            self.current = next[1]

        return True


class Solver():
    
    def __init__(self, filename: str, climb: bool = False):
        self.paths: dict[Coord, str] = {}
        
        with open(filename, 'r') as f:
            x = 0
            for line in f:
                y = 0
                for c in line:
                    if c in ['.', '<', '>', 'v', '^']:
                        if climb:
                            self.paths[(x, y)] = '.'
                        else:
                            self.paths[(x, y)] = c
                    y += 1
                x += 1
        
        self.start: Coord = (0, 1)
        self.end: Coord = ((x-2, y-3))

    def solve1(self):
        path = Path(self.start)
        longest_walk = 0
        print(f'The longest theoretical path length is {len(self.paths)}')
        
        keep_going = True
        while keep_going:
            (x, y) = path.current
            if path.current == self.end:
                steps = path.steps()
                if steps > longest_walk:
                    print(f'Longest path to date: {steps+2}')
                    longest_walk = steps

            path.see(path.current)

            next_walks: list[tuple[Coord]] = []
            
            north = (x-1, y)
            if north in self.paths and path.unseen(north):
                tile = self.paths[north]
                if tile == '.':
                    next_walks.append((north,))
            
            west = (x, y-1)
            if west in self.paths and path.unseen(west):
                tile = self.paths[west]
                if tile == '.':
                    next_walks.append((west,))

            south = (x+1, y)
            if south in self.paths and path.unseen(south):
                tile = self.paths[south]
                if tile == '.':
                    next_walks.append((south,))
                elif tile == 'v':
                    next = (x+2, y)
                    if path.unseen(next):
                        next_walks.append((south, next))
            
            east = (x, y+1)
            if east in self.paths and path.unseen(east):
                tile = self.paths[east]
                if tile == '.':
                    next_walks.append((east,))
                elif tile == '>':
                    next = (x, y+2)
                    if path.unseen(next):
                        next_walks.append((east, next))

            if next_walks:
                if len(next_walks) == 1:
                    t = next_walks[0]
                    if len(t) == 1:
                        path.current = t[0]
                    else:
                        path.see(t[0])
                        path.current = t[1]
                else:
                    path.fork(next_walks)

            else:
                keep_going = path.backtrack()
      
        return longest_walk+2


    def solve2(self):
        pass

if __name__ == "__main__":
    if len(sys.argv) > 1:
        filename = sys.argv[1]
    else:
        filename = "tiny_input"

    solver = Solver(filename)
    solver2 = Solver(filename, True)

    #print(f"First Solution: {solver.solve1()}")
    print(f"Second Solution: {solver2.solve1()}")