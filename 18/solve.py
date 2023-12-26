from __future__ import annotations
import sys

type Coord = tuple[int, int]


class Cube:
    """Represents a single cubic meter of space."""

    def __init__(self, coord: Coord):
        self.coord = coord


class Segment:
    """A segment that is made of cubes"""

    def __init__(
        self,
        start: Coord,
        length: int,
        direction: str,
        color: str,
        previous: Segment | None,
    ):
        self.start = start
        if direction == "R":
            self.end: Coord = (start[0], start[1] + length)
        elif direction == "L":
            self.end: Coord = (start[0], start[1] - length)
        elif direction == "U":
            self.end: Coord = (start[0] - length, start[1])
        elif direction == "D":
            self.end: Coord = (start[0] + length, start[1])
        else:
            assert False, "Encountered an unexpected direction"

        self.length = length
        self.direction = direction
        self.color = color
        self.previous = previous
        self.next: Segment = None

    def min_x(self) -> int:
        """Minimum x value in the segment"""
        return min(self.start[0], self.end[0])

    def min_y(self) -> int:
        """Minimum y value in the segment"""
        return min(self.start[1], self.end[1])

    def max_x(self) -> int:
        """Maximum x value in the segment"""
        return max(self.start[0], self.end[0])

    def max_y(self) -> int:
        """Maximum y value in the segment"""
        return max(self.start[1], self.end[1])

    def shift(self, dx: int, dy: int):
        """Change (x, y) by (dx, dy) respectively"""
        (start_x, start_y) = self.start
        (end_x, end_y) = self.end
        self.start = (start_x + dx, start_y + dy)
        self.end = (end_x + dx, end_y + dy)

    def cubes(self) -> list[Cube]:
        """Get the list of cubes in the segment"""
        if self.direction == "R":
            return [
                Cube((self.start[0], self.start[1] + x)) for x in range(self.length)
            ]
        if self.direction == "L":
            return [
                Cube((self.start[0], self.start[1] - x)) for x in range(self.length)
            ]
        if self.direction == "U":
            return [
                Cube((self.start[0] - x, self.start[1])) for x in range(self.length)
            ]
        if self.direction == "D":
            return [
                Cube((self.start[0] + x, self.start[1])) for x in range(self.length)
            ]

        assert False, "Encountered an unexpected direction"

    def isNub(self, handedness: str)->bool:
        """Returns true if the segment is the middle segment of a nub"""
        sequence = ''.join(self.previous.direction, self.direction, self.next.direction)
        nub_sequences = {
            'R': ['URD', 'RDL', 'DLU', 'LUR'],
            'L': ['ULD', 'RUL', 'DRU', 'LDR']
        }
        return sequence in nub_sequences[handedness]

    def getInternalNubArea(self)->tuple[Coord, Coord]:
        """Returns a pair of coordinates with the *internal* area of the nub"""
        previousDir = self.previous.direction

        if previousDir == 'U': # Then the current segment is left or right
            y1, y2 = self.min_y() + 1, self.max_y - 1
            x1 = self.min_x() # Same as max_x
            x2 = min(self.previous.max_x(), self.next.max_x())

        elif previousDir == 'D': # Then the current segment is left or right
            y1, y2 = self.min_y() + 1, self.max_y() - 1
            x1 = self.min_x()
            x2 = max(self.previous.min_x(), self.next.min_x())

        elif previousDir == 'L': # Current segment is up or down
            x1, x2 = self.min_x() + 1, self.max_x - 1
            y1 = self.min_y()
            y2 = max(self.previous.min_y(), self.next.min_y())

        elif previousDir == 'R': # Current segment us up or down
            x1, x2 = self.min_x() + 1, self.max_x - 1
            y1 = self.min_y()
            y2 = min(self.previous.max_y(), self.next.max_x())

        else:
            assert False, 'Unexpected direction found'

        return ((x1, y1), (x2, y2))
    
    def extend(self, distance: int):
        """If distance is positive, grow the end. If negative, shrink the start."""
        if self.direction == 'R':
            if distance > 0:
                self.end = (self.end[0], self.end[1] + distance)
            else:
                self.start = (self.start[0], self.start[1] - distance)
        elif self.direction == 'L':
            if distance > 0:
                self.end = (self.end[0], self.end[1] - distance)
            else:
                self.start = (self.start[0], self.start[1] + distance)
        elif self.direction == 'D':
            if distance > 0:
                self.end = (self.end[0] + distance, self.end[1])
            else:
                self.start = (self.start[0] - distance, self.start[1])
        else: #self.direction == 'U'
            if distance > 0:
                self.end = (self.end[0] - distance, self.end[1])
            else:
                self.start = (self.end[0] + distance, self.start[1])
        
        self.length += distance


class Solver:
    """Parses the input and solves the problem"""

    def __init__(self, filename: str):
        self.segments: list[Segment] = []
        with open(filename, "r") as f:
            current: Segment = None
            for line in f.readlines():
                (direction, length, color) = self._lineToSegment(line)

                if current is None:
                    next_start: Coord = (0, 0)
                else:
                    next_start = current.end

                self.segments.append(
                    Segment(next_start, length, direction, color, current)
                )
                if current is not None:
                    current.next = self.segments[-1]
                current = self.segments[-1]

        assert current.end == (0, 0), "Failed to make a loop"
        self.segments[0].previous = current

        # Determine handedness
        top_segments: list[Segment] = []
        min_x = float('inf')

        for s in self.segments:
            x = s.min_x()
            if x < min_x:
                top_segments = [s]
                min_x = x
            elif x == min_x:
                top_segments.append(s)

        assert len(top_segments) >= 3, "Not enough segments found to compute handedness"
        horizontal_segments = [s for s in top_segments if s.direction in ['L', 'R']]
        assert len(top_segments) > 0, "No horizontal segments found"

        if horizontal_segments[0].direction == 'L':
            for s in horizontal_segments:
                assert s.direction == 'L', 'Inconsistent handedness'
            self.handedness = 'L'
        else:
            for s in horizontal_segments:
                assert s.direction == 'R', 'Inconsistent handedness'
            self.handedness = 'R'
            

    def _lineToSegment(self, line:str)->tuple[str, int, str]:
        """Process a line of the input"""
        (direction, length_text, color_text) = line.strip().split()
        length = int(length_text)
        color = color_text[1:-1] # Strip the curly braces, keep the hash
        return (direction, length, color)

    def checkArea(self, coords: tuple[Coord, Coord])->bool:
        """Returns True if an area is clear"""
        (c1, c2) = coords
        (x1, y1) = c1
        (x2, y2) = c2
        min_x = min(x1, x2)
        min_y = min(y1, y2)
        max_x = max(x1, x2)
        max_y = max(y1, y2)

        for s in self.segments:
            for c in [s.start, s.end]:
                (x, y) = c
                if x >= min_x and x<=max_x and y >= min_y and y <= max_y:
                    return False
        
        return True

    def combineStraightPaths(self):
        """Combines any pairs of segments going in the same direction into a single segment"""

        def combineWithNext(a: Segment)->bool:
            b = a.next
            if a.direction == b.direction:
                a.length = a.length + b.length
                a.end = b.end
                self.segments.remove(b)
                return True
            return False

        base = self.segments[0]
        current = base
        while current.next != base:
            if not combineWithNext(current):
                current = current.next

        combineWithNext(current)


    def solve1(self):
        """Counts the total volume (aread) dug out"""
        min_x = min(s.min_x() for s in self.segments)
        min_y = min(s.min_y() for s in self.segments)
        max_x = max(s.max_x() for s in self.segments)
        max_y = max(s.max_y() for s in self.segments)

        for s in self.segments:
            s.shift(-min_x + 1, -min_y + 1)

        board: list[list[str]] = [
            list("." * (max_y - min_y + 3)) for _ in range(min_x, max_x + 3)
        ]

        for s in self.segments:
            for c in s.cubes():
                (x, y) = c.coord
                board[x][y] = "#"

        for row in board:
            print("".join(row))

        print("\n---\n")

        # The board is padded on each edge with empty spaces
        # So, we how that (0, 0) is definitely empty and we can propagate out from there
        height = len(board)
        width = len(board[0])
        visited: set[Coord] = set()
        work_queue: list[Coord] = [(0, 0)]

        while work_queue:
            current = work_queue.pop()
            visited.add(current)

            (x, y) = current
            if board[x][y] == "#":
                continue

            board[x][y] = "0"
            if x > 0:  # Up is realistic
                coord = (x - 1, y)
                if coord not in visited:
                    work_queue.append(coord)

            if x < height - 1:  # Down is realistic
                coord = (x + 1, y)
                if coord not in visited:
                    work_queue.append(coord)

            if y > 0:  # Left is realistic
                coord = (x, y - 1)
                if coord not in visited:
                    work_queue.append(coord)

            if y < width - 1:  # Up is realistic
                coord = (x, y + 1)
                if coord not in visited:
                    work_queue.append(coord)

        for row in board:
            print("".join(row))

        return sum(row.count("#") + row.count(".") for row in board)

    def solve2(self):
        print(f"Starting with {len(self.segments)} segments")
        self.combineStraightPaths()
        print(f"After combining: {len(self.segments)} segments")

        area = 0
        # Iterate until we get down to a rectangle
        while len(self.segments) > 4:
            candidates = sorted(self.segments, key=lambda x: x.length, reverse=True)
            s = candidates.pop()
            while not (s.isNub(self.handedness) and self.checkArea(s.getInternalNubArea)):
                s = candidates.pop()

            # Increase the found area
            area += s.length * (min(s.previous.length, s.next.length) - 1)

            # Delete the nub
            if s.previous.length == s.next.length:
                # Need to delete both segments
                s.previous.previous.end = s.next.next.start
                s.previous.previous.length += s.length
                s.previous.previous.next = s.next.next
                s.next.next.previous = s.previous.previous

                self.segments.remove(s)
                self.segments.remove(s.previous)
                self.segments.remove(s.next)

            elif s.previous.length < s.next.length:
                # Delete the previous segment, resize the next one
                s.previous.previous.extend(s.length)
                s.next.extend(-s.previous.length)

                s.previous.previous.next = s.next
                s.next.previous = s.previous.previous

                self.segments.remove(s)
                self.segments.remove(s.previous)

            else: # s.previous.length > s.next.length
                # Delete the next segment, resize the previous one
                


            # Combine straight paths
            self.combineStraightPaths()


class Solver2(Solver):
    """Uses the color hex as the direction and length"""

    def _lineToSegment(self, line: str) -> tuple[str, int, str]:
        (_, _, color_text) = line.strip().split()
        color_hex = color_text[1:-1]
        length = int(color_hex[1:6], base=16)
        direction = ["R", "D", "L", "U"][int(color_hex[6])]
        return (direction, length, color_hex)


if __name__ == "__main__":
    if len(sys.argv) > 1:
        filename = sys.argv[1]
    else:
        filename = "tiny_input"

    solver = Solver(filename)
    solver2 = Solver2(filename)

    print(f"First Solution: {solver.solve1()}")
    print(f"Second Solution: {solver2.solve2()}")
