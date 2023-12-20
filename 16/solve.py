from __future__ import annotations
import sys

type Coord = tuple[int, int]

class Solver():
    def __init__(self, filename: str):
        self.board: list[list[str]] = []
        with open(filename, 'r') as f:
            for line in f.readlines():
                self.board.append(list(line.strip()))

        self.height = len(self.board)
        self.width = len(self.board[0])

    def lookup(self, coord: Coord)->str:
        x, y = coord
        return self.board[x][y]

    def step(self, coord: Coord, direction: str)->list[tuple[Coord, str]]:
        steps: list[Coord] = []
        char = self.lookup(coord)

        # Empty space is easy, it just continues on the same direction
        if char == '.':
            next = self.direction(coord, direction)
            if self.legal(next):
                steps.append((next, direction))

        # Splitters either continue, or change direction
        elif char == '|':
            if direction in ["up", "down"]:
                next = self.direction(coord, direction)
                if self.legal(next):
                    steps.append((next, direction))
            elif direction in ["left", "right"]:
                up = self.direction(coord, "up")
                if self.legal(up):
                    steps.append((up, "up"))

                down = self.direction(coord, "down")
                if self.legal(down):
                    steps.append((down, "down"))

            else:
                assert False, f"Invalid direction: {direction}"

        elif char == '-':
            if direction in ["left", "right"]:
                next = self.direction(coord, direction)
                if self.legal(next):
                    steps.append((next, direction))
            elif direction in ["up", "down"]:
                left = self.direction(coord, "left")
                if self.legal(left):
                    steps.append((left, "left"))

                right = self.direction(coord, "right")
                if self.legal(right):
                    steps.append((right, "right"))
            else:
                assert False, f"Invalid direction: {direction}"

        # Mirrors always change direction
        elif char == '/':
            if direction == "right":
                next = self.direction(coord, "up")
                if self.legal(next):
                    steps.append((next, "up"))
            
            elif direction == "left":
                next = self.direction(coord, "down")
                if self.legal(next):
                    steps.append((next, "down"))

            elif direction == "up":
                next = self.direction(coord, "right")
                if self.legal(next):
                    steps.append((next, "right"))

            elif direction == "down":
                next = self.direction(coord, "left")
                if self.legal(next):
                    steps.append((next, "left"))
            else:
                assert False, f"Invalid direction: {direction}"

        elif char == '\\':
            if direction == "left":
                next = self.direction(coord, "up")
                if self.legal(next):
                    steps.append((next, "up"))
            
            elif direction == "right":
                next = self.direction(coord, "down")
                if self.legal(next):
                    steps.append((next, "down"))

            elif direction == "down":
                next = self.direction(coord, "right")
                if self.legal(next):
                    steps.append((next, "right"))

            elif direction == "up":
                next = self.direction(coord, "left")
                if self.legal(next):
                    steps.append((next, "left"))
            else:
                assert False, f"Invalid direction: {direction}"

        return steps

    def legal(self, coord: Coord)->bool:
        x, y = coord
        return x >= 0 and y >= 0 and x < self.height and y < self.width
    
    def direction(self, coord: Coord, direction: str)->Coord:
        x, y = coord
        if direction == "left":
            return (x, y - 1)
        elif direction == "right":
            return (x, y + 1)
        elif direction == "up":
            return (x - 1, y)
        elif direction == "down":
            return (x + 1, y)
        else:
            assert False, f"Invalid direction: {direction}"

    
    def count(self, start: tuple[Coord, str]):
        energized: list[Coord] = []
        found: list[tuple[Coord, str]] = [start]
        handled = set()

        while len(found) > 0:
            coord, direction = found.pop()
            if (coord, direction) in handled:
                continue
            handled.add((coord, direction))
            energized.append(coord)
            steps = self.step(coord, direction)
            # print(f"Stepped from {coord} to {steps}")
            found.extend(self.step(coord, direction))
        
        return len(set(energized))

    def solve1(self):
        return self.count(((0, 0), "right"))

    def solve2(self):
        starts: list[tuple[Coord, str]] = []

        for i in range(self.width):
            starts.append(((0, i), "down"))
            starts.append(((self.height - 1, i), "up"))

        for j in range(self.height):
            starts.append(((j, 0), "right"))
            starts.append(((j, self.width - 1), "left"))

        energized = [self.count(start) for start in starts]
        return max(energized)

if __name__ == "__main__":
    if len(sys.argv) > 1:
        filename = sys.argv[1]
    else:
        filename = "tiny_input"

    solver = Solver(filename)

    print(f"First Solution: {solver.solve1()}")
    print(f"Second Solution: {solver.solve2()}")