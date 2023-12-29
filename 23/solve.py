from __future__ import annotations
from dataclasses import dataclass, field
import sys

type Coord = tuple[int, int]

@dataclass
class Path:
    current: Coord
    history: list[set[Coord]] = field(default_factory=list)

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
        return sum(len(x) for x in self.history) - 1
    
    def fork(self)->Path:
        return Path(self.current, self.history.copy())

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
        walks: list[Path] = []
        finished_paths: list[Path] = []
        walks.append(Path(self.start))
        
        while walks:
            path = walks.pop()
            (x, y) = path.current
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
                if len(next_walks) == 1: # Just keep using the same path object
                    t = next_walks[0]
                    if len(t) == 1:
                        path.current = t[0]
                        walks.append(path)
                    else:
                        path.see(t[0])
                        path.current = t[1]
                        walks.append(path)
                else:
                    for t in next_walks:
                        p = path.fork()
                        if len(t) == 1:
                            p.current = t[0]
                            walks.append(p)
                        else:
                            p.see(t[0])
                            p.current = t[1]
                            walks.append(p)
            else:
                finished_paths.append(path)
      
        good_paths = list(filter(lambda p: not p.unseen(self.end), finished_paths))
        return max(x.steps() for x in good_paths)


    def solve2(self):
        pass

if __name__ == "__main__":
    if len(sys.argv) > 1:
        filename = sys.argv[1]
    else:
        filename = "tiny_input"

    solver = Solver(filename)
    solver2 = Solver(filename, True)

    print(f"First Solution: {solver.solve1()}")
    #print(f"Second Solution: {solver2.solve1()}")