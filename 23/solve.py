from __future__ import annotations
from dataclasses import dataclass, field
import sys

type Coord = tuple[int, int]

@dataclass
class Path:
    current: Coord
    history: set[Coord] = field(default_factory=set)

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
            next_walks: list[Path] = []
            
            north = (x-1, y)
            if north in self.paths and north not in path.history:
                tile = self.paths[north]
                if tile == '.':
                    hist = path.history.copy()
                    hist.add(path.current)
                    next_walks.append(Path(north, hist))
            
            west = (x, y-1)
            if west in self.paths and west not in path.history:
                tile = self.paths[west]
                if tile == '.':
                    hist = path.history.copy()
                    hist.add(path.current)
                    next_walks.append(Path(west, hist))

            south = (x+1, y)
            if south in self.paths and south not in path.history:
                tile = self.paths[south]
                if tile == '.':
                    hist = path.history.copy()
                    hist.add(path.current)
                    next_walks.append(Path(south, hist))
                elif tile == 'v':
                    next = (x+2, y)
                    if next not in path.history:
                        hist = path.history.copy()
                        hist.add(path.current)
                        hist.add(south)
                        next_walks.append(Path(next, hist))
            
            east = (x, y+1)
            if east in self.paths and east not in path.history:
                tile = self.paths[east]
                if tile == '.':
                    hist = path.history.copy()
                    hist.add(path.current)
                    next_walks.append(Path(east, hist))
                elif tile == '>':
                    next = (x, y+2)
                    if next not in path.history:
                        hist = path.history.copy()
                        hist.add(path.current)
                        hist.add(east)
                        next_walks.append(Path(next, hist))

            if next_walks:
                walks.extend(next_walks)
            else:
                finished_paths.append(path)
      
        good_paths = list(filter(lambda p: self.end in p.history, finished_paths))
        return max(len(x.history) for x in good_paths)


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
    print(f"Second Solution: {solver2.solve1()}")