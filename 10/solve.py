from __future__ import annotations
import sys

type Coordinate = tuple[int, int]
type Path = list[Coordinate]
type Area = set[Coordinate]

class Solver():
    def __init__(self, filename: str):
        with open(filename, 'r') as f:
            self.board = [line for line in f.readlines()]

    def start(self)->Coordinate:
        for i in range(len(self.board)):
            line = self.board[i]
            for j in range(len(line)):
                if line[j] == 'S':
                    return (i, j)
        
        assert(False) #If we got here, we didn't have a starting point

    def lookup(self, coordinate: Coordinate)->str:
        return self.board[coordinate[0]][coordinate[1]]
    
    def set(self, coordinate: Coordinate, val: str)->None:
        self.board[coordinate[0]][coordinate[1]] = val
    
    def north(self, c: Coordinate)->Coordinate:
        return (c[0] - 1, c[1])
    def east(self, c: Coordinate)->Coordinate:
        return (c[0], c[1] + 1)
    def south(self, c: Coordinate)->Coordinate:
        return (c[0] + 1, c[1])
    def west(self, c: Coordinate)->Coordinate:
        return (c[0], c[1] - 1)
    def legal(self, c:Coordinate)->bool:
        if c[0] < 0 or c[1] < 0 or c[0] >= self.height() or c[1] >= self.width():
            return False
        else:
            return True
        
    def height(self)->int:
        return len(self.board)
    
    def width(self)->int:
        return len(self.board[0])
    

    def adjacents(self, coordinate: Coordinate)->list[Coordinate]:
        
        symbol = self.lookup(coordinate)
        if symbol == '|':
            c1 = self.north(coordinate)
            c2 = self.south(coordinate)
        
        elif symbol == '-':
            c1 = self.east(coordinate)
            c2 = self.west(coordinate)

        elif symbol == 'L':
            c1 = self.north(coordinate)
            c2 = self.east(coordinate)

        elif symbol == 'J':
            c1 = self.north(coordinate)
            c2 = self.west(coordinate)

        elif symbol == '7':
            c1 = self.west(coordinate)
            c2 = self.south(coordinate)

        elif symbol == 'F':
            c1 = self.east(coordinate)
            c2 = self.south(coordinate)

        elif symbol == '.':
            return []
        
        return [x for x in [c1, c2] if self.legal(x)]    

    def extend(self, path: Path)->Path:
        current = path[-1]
        last = path[-2]
        adjacent = self.adjacents(current)
        assert(len(adjacent) == 2)
        if adjacent[0] == last:
            path.append(adjacent[1])
        else:
            assert(adjacent[1] == last)
            path.append(adjacent[0])
        
        return path
    
    def is_outside(self, coord: Coordinate)->bool:
        if self.legal(coord):
            return self.lookup(coord) == 'O'
        else:
            return True


    def starting_paths(self)->list[Path]:
        paths:list[Path] = []
        start_square = self.start()
        north  = self.north(start_square)
        east  = self.east(start_square)
        south  = self.south(start_square)
        west = self.west(start_square)

        if self.legal(north) and start_square in self.adjacents(north):
            paths.append([start_square, north])
        if self.legal(east) and start_square in self.adjacents(east):
            paths.append([start_square, east])
        if self.legal(south) and start_square in self.adjacents(south):
            paths.append([start_square, south])
        if self.legal(west) and start_square in self.adjacents(west):
            paths.append([start_square, west])

        return paths

    def solve1(self)->int:
        (p1, p2) = self.starting_paths()
        while p1[-1] != p2[-1]:
            p1 = self.extend(p1)
            p2 = self.extend(p2)

        return len(p1)-1
    
    def solve2(self)->int:
        start = self.start()
        path = self.starting_paths()[0]
        while path[-1] != start:
            path = self.extend(path)

        pArea: Area = set(path)
        assert(len(pArea) == len(path) - 1)
        
        # Clean the board up
        for i in range(self.height()):
            row = self.board[i]
            newRow = ''
            for j in range(self.width()):
                if (i, j) not in pArea:
                    newRow += '.'
                else:
                    newRow += row[j]
            self.board[i] = list(newRow)

        for row in self.board:
            print(''.join(row))

        # Build the initial list of areas
        accountedFor: Area = set()
        areaList: list[Area] = []
        for i in range(self.height()):
            for j in range(self.width()):
                c: Coordinate = (i, j)
                symbol = self.lookup(c)

                #print(f"Checking {c}")
                #print(f"areaList: {areaList}")
                #print(f"accountedFor: {accountedFor}")
                
                # If we're looking at the path, we don't need to do anything
                if symbol != '.':
                    #print(f"skipping {c}\n")
                    continue

                # Mark this square as handled
                accountedFor.add(c)

                # Look up the legal neighbors that are empty
                neighbors:Area = set([x for x in [self.north(c), self.east(c), self.west(c), self.south(c)] if self.legal(x) and self.lookup(x) == '.'])

                # See if we've seen any neighbors before
                found_neighbors = accountedFor.intersection(neighbors)

                # Mark all the neighbors complete, since we handle them below
                accountedFor = accountedFor.union(neighbors)

                if len(found_neighbors) == 0:
                    # Cool, a whole new area
                    neighbors.add(c)
                    #print(f"Creating new area: {neighbors}")
                    areaList.append(neighbors)

                elif len(found_neighbors) == 1:
                    # This is easy, just add to an existing area
                    # Note that we add not just the found one, but all the neighbors

                    found = found_neighbors.pop() # Removes and returns a random element, but there's only one
                    for k in range(len(areaList)):
                        candidate = areaList[k]
                        #print(f"Checking for {found} in {candidate}")
                        if found in candidate:
                            neighbors.add(c)
                            #print(f"Adding {neighbors} to {candidate}")
                            candidate = candidate.union(neighbors)
                            areaList[k] = candidate
                            break #no need to keep looking

                else:
                    # More than one neighbor was found in the list, so we need to check and see if we need to combine areas
                    #print(f"Found multiple neighbors: {found_neighbors}")
                    newAreaList:list[Area] = []
                    newArea: Area = neighbors
                    newArea.add(c)

                    for area in areaList:
                        if len(area.intersection(found_neighbors)) == 0:
                            #print(f"Didn't find any of those in {area}, adding it to the new list")
                            newAreaList.append(area)

                        else:
                            newArea = newArea.union(area)

                    newAreaList.append(newArea)
                    #print(f"Updating {areaList} to {newAreaList}")
                    areaList = newAreaList

                #print()

        # Mark everything touching the edge of the board as "outside"
        outsideList: list[Area] = []
        unknownList: list[Area] = []
        for area in areaList:
            x = set(p[0] for p in area)
            y = set(p[1] for p in area)
            if 0 in x or 0 in y or self.height()-1 in x or self.width()-1 in y:
                outsideList.append(area)
            else:
                unknownList.append(area)

        sizes = [len(area) for area in unknownList]
        print({i:sizes.count(i) for i in sizes})

        for area in outsideList:
            for coord in area:
                self.set(coord, 'O')

        for row in self.board:
            print(''.join(row))

        outside_side = None
        def facing(coords)->str:
            a = coords[0]
            b = coords[1]
            if b == self.north(a):
                return "north"
            if b == self.east(a):
                return "east"
            if b == self.south(a):
                return "south"
            if b == self.west(a):
                return "west"
            assert(False)

        def left(coord: Coordinate, facing:str)->list[Coordinate]:
            current = self.lookup(coord)

            if current == "L":
                if facing == "south":
                    return [self.east(self.north(coord))]
                if facing == "west":
                    return [self.south(coord), self.west(coord), self.south(self.west(coord))]
                assert False, "Facing wrong way!"

            elif current == "J":
                if facing == "south":
                    return [self.east(coord), self.south(coord), self.south(self.east(coord))]
                if facing == "east":
                    return [self.west(self.north(coord))]
                assert False, "Facing wrong way!"

            elif current == "7":
                if facing == "north":
                    return [self.west(self.south(coord))]
                if facing == "east":
                    return [self.north(coord), self.east(coord), self.east(self.north(coord))]
                assert False, "Facing wrong way!"

            elif current == "F":
                if facing == "north":
                    return [self.west(coord), self.north(coord), self.west(self.north(coord))]
                if facing == "west":
                    return [self.east(self.south(coord))]
                assert False, "Facing wrong way!"

            if facing == "north":             
                return [self.west(coord)]
            if facing == "south":
                return [self.east(coord)]
            if facing == "east":
                return [self.north(coord)]
            if facing == "west":
                return [self.south(coord)]
            
            assert(False)

        def right(coord: Coordinate, facing:str)->list[Coordinate]:
            current = self.lookup(coord)

            if current == "L":
                if facing == "west":
                    return [self.east(self.north(coord))]
                if facing == "south":
                    return [self.south(coord), self.west(coord), self.south(self.west(coord))]
                assert False, "Facing wrong way!"

            elif current == "J":
                if facing == "east":
                    return [self.east(coord), self.south(coord), self.south(self.east(coord))]
                if facing == "south":
                    return [self.west(self.north(coord))]
                assert False, "Facing wrong way!"

            elif current == "7":
                if facing == "east":
                    return [self.west(self.south(coord))]
                if facing == "north":
                    return [self.north(coord), self.east(coord), self.east(self.north(coord))]
                assert False, "Facing wrong way!" 

            elif current == "F":
                if facing == "west":
                    return [self.west(coord), self.north(coord), self.west(self.north(coord))]
                if facing == "north":
                    return [self.east(self.south(coord))]
                assert False, "Facing wrong way!"

            if facing == "north":             
                return [self.east(coord)]
            if facing == "south":
                return [self.west(coord)]
            if facing == "east":
                return [self.south(coord)]
            if facing == "west":
                return [self.north(coord)]
            
            assert(False)

        i = 0
        while outside_side is None:
            coords = path[i:i+2]
            direction = facing(coords)
            left_coord = left(path[i+1], direction)[0]
            right_coord = right(path[i+1], direction)[0]
            if self.is_outside(left_coord):
                assert(not self.is_outside(right_coord))
                outside_side = "left"
            elif self.is_outside(right_coord):
                outside_side = "right"

            i += 1

            if i % 500 == 0:
                print(f"{i}, ", end=None)

        print(f"\nThe outside is on the {outside_side} of the loop")
        inside_seen:set[Coordinate] = set()

        for i in range(len(path)-1):
            coords = path[i:i+2]
            direction = facing(coords)

            if outside_side == "left":
                outside_coords = left(path[i+1], direction)
                inside_coords = right(path[i+1], direction)
            else:
                outside_coords = right(path[i+1], direction)
                inside_coords = left(path[i+1], direction)

            for inside_coord in inside_coords:
                if self.legal(inside_coord):
                    if self.lookup(inside_coord) == '.':
                        inside_seen.add(inside_coord)
                    if self.lookup(inside_coord) == 'O':
                        assert(False)
            
            for outside_coord in outside_coords:
                if self.legal(outside_coord):
                    seen = self.lookup(outside_coord)
                    if seen == '.':
                        # We have a previously unseen patch of ground on our outside side
                        j = 0
                        while outside_coord not in unknownList[j]:
                            j += 1

                        area = unknownList[j]
                        outsideList.append(area)
                        for coord in area:
                            self.set(coord, 'O')

                        assert(area == unknownList.pop(j))

        sizes = [len(area) for area in unknownList]
        print({i:sizes.count(i) for i in sizes})

        for row in self.board:
            print(''.join(row))

        inside = set()
        for coord in inside_seen:
            for area in areaList:
                if coord in area:
                    inside = inside.union(area)
        
        return sum(sizes), len(inside)
    

if __name__ == "__main__":
    if len(sys.argv) > 1:
        filename = sys.argv[1]
    else:
        filename = "tiny_input"

    solver = Solver(filename)

    print(f"First Solution: {solver.solve1()}")
    print(f"Second Solution: {solver.solve2()}")