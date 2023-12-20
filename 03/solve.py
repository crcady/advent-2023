class square:
    """Holds a single space on the schematic"""
    def __init__(self, content: str):
        self.character = content
        self.is_numeric = content.isdigit()
        self.is_adjacent = False
        self.is_symbol = (not content.isdigit()) and content != "."
        self.is_star = content == "*"
        self.adjacency_list: list[tuple[int, int]] = []

class schematic:
    """A part schematic with numbers and symbols"""

    def __init__(self, lines: list[str]):
        self.height = len(lines)
        self.width = len(lines[0].strip())
        self.rows:list[list[square]] = []

        for line in lines:
            row = []
            for char in line.strip():
                row.append(square(char))
            self.rows.append(row)

    def __get_adjacent_coords(self, row:int, col:int)->list[tuple[int, int]]:
        """Internal function to get a list of (row, col) indexes that are adjacent and legal"""
        coords = []
        first_row = max(0, row - 1)
        last_row = min(self.height - 1, row + 1)
        first_col = max(0, col - 1)
        last_col = min(self.width - 1, col + 1)

        for r in range(first_row, last_row + 1):
            for c in range(first_col, last_col + 1):
                if r != row or c != col:
                    coords.append((r, c))
        
        return coords

    def compute_adjacencies(self):
        """Makes one passe through the schematic and sets the adjacency of each square"""
        # First pass to compute all simple adjacencies
        for row in range(self.height):
            for col in range(self.width):
                if not self.get(row, col).is_numeric:
                    continue

                has_adjacent_symbol = False
                adjacenty_list: list[tuple[int, int]] = []

                for (r, c) in self.__get_adjacent_coords(row, col):
                    neighbor = self.get(r,c)
                    if neighbor.is_symbol:
                        has_adjacent_symbol = True
                        adjacenty_list = list(set(adjacenty_list).union([(r, c)]))

                self.get(row, col).is_adjacent = has_adjacent_symbol
                self.get(row, col).adjacency_list = adjacenty_list
            

    def scan_numbers(self)->list[tuple[int, list[tuple[int, int]]]]:
        """Makes a pass through each line and finds numbers, and returns two list: those that are adjacent to a symbol and those that aren't"""
        numbers:list[tuple[int, list[tuple[int, int]]]] = []
        part_numbers: list[int] = []
        other_numbers: list[int] = []

        for row in self.rows:
            num = 0
            adj = False
            adj_set:set[tuple[int,int]] = set()
            for col in row:
                if col.is_numeric:
                    num = num*10+int(col.character)
                    adj = adj or col.is_adjacent
                    adj_set = adj_set.union(set(col.adjacency_list))
                else:
                    if num > 0:
                        if adj:
                            part_numbers.append(num)
                        else:
                            other_numbers.append(num)
                        numbers.append((num, list(adj_set)))
                    num = 0
                    adj = False
                    adj_set = set()

            # Need to cover the case where a number was right-aligned on the board
            if num > 0:
                if adj:
                    part_numbers.append(num)
                else:
                    other_numbers.append(num)

                numbers.append((num, list(adj_set)))

        return numbers
    
    def get(self, row:int, col:int)->square:
        """Retuns a square object at a given row, col (zero indexed)"""
        return self.rows[row][col]
    
with open('input', 'r') as f:
    lines = f.readlines()

sch = schematic(lines)
print(f"Opened a schematic with {sch.height} rows and {sch.width} columns")
print(f"Schematic has {len(sch.rows)} rows and {len(sch.rows[0])} columns")
symbols = 0
for row in range(sch.height):
    for col in range(sch.width):
        if sch.get(row, col).is_symbol:
            symbols += 1

print(f"There were {symbols} symbols in the schematic")

sch.compute_adjacencies()
part_numbers: list[int] = []
skipped_numbers: list[int] = []
numbers = sch.scan_numbers()
for (num, adj_list) in numbers:
    if len(adj_list) > 0:
        part_numbers.append(num)
    else:
        skipped_numbers.append(num)

stars:list[tuple[int, int]] = []
for row in range(sch.height):
    for col in range(sch.width):
        if sch.get(row, col).is_star:
            stars.append((row, col))

star_dict = dict()
for star in stars:
    star_dict[star] = []


for (num, adj_set) in numbers:
    for adj in adj_set:
        if adj in stars:
            star_dict[adj].append(num)

ratios:list[int] = []

for value in star_dict.values():
    if len(value) == 2:
        ratios.append(value[0]*value[1])

print(f"Part Numbers: {len(part_numbers)}")
print(f"Other Numbers: {len(skipped_numbers)}")
print(f"The sum of the part numbers is {sum(part_numbers)}")

print(f"Found {len(ratios)} gears with a ratio sum of {sum(ratios)}")

