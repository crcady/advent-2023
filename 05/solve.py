from __future__ import annotations

import sys
import logging
import os

class Loggable:
    def __init__(self, logger_name):
        self.logger = logging.getLogger(logger_name)
        self.logger.setLevel(os.getenv('LOG_LEVEL', 'INFO'))

        self.info = self.logger.info
        self.debug = self.logger.debug

    @classmethod
    def initLogger(cls):
        Loggable.__init__(cls, cls.__name__)


class Map(Loggable):
    """
    source-to-dest map:
    dst_range, src_range, len
    """
    def __init__(self, lines):
        self.initLogger()
        src_dst, m = lines[0].split()
        assert(m == "map:")
        src, _, dst = src_dst.split("-")
        self.src: str = src
        self.dst: str = dst

        ranges: list[tuple[int, int, int]] = []
        for line in lines[1:]:
            (dst_range, src_range, len) = line.split()
            ranges.append((int(dst_range), int(src_range), int(len)))

        self.ranges = ranges

    def lookup(self, src_num: int)->int:
        for (dst_range, src_range, len) in self.ranges:
            if src_num >= src_range and src_num < src_range + len:
                return dst_range + (src_num - src_range)
        
        # source numbers that aren't mapped correspond to the same destination number
        return src_num
    
    def ordered_ranges(self, pad:bool = False)->list[tuple[int, int, int]]:
        # Assumes:
        # 1. There's no overlap between ranges
        # 2. All indexes start at 0
        ranges = list(self.ranges)
        ranges.sort(key=lambda x: x[1])
        if pad:
            new_ranges = []
            last = 0
            for r in ranges:
                # Either we insert a new range to fill the gap, or we insert the next range we found
                (dst, src, len) = r
                if last < src: # need to fill some space
                    new_ranges.append((last, last, src - last))
                new_ranges.append(r)
                last = src + len

            ranges = new_ranges

        return ranges
    
class OffsetMap(Loggable):
    def __init__(self, maps: list[Map]):
        super().__init__(__class__.__name__)
        offsets = [self.toOffsets(m) for m in maps]
        self.debug(offsets)
        self.partial_offsets = []
        combined_offset = []

        for offset in offsets:
            combined_offset = self.combineOffsets(combined_offset, offset)
            self.partial_offsets.append(combined_offset)

        self.offsets = combined_offset
        
    def toOffsets(self, m: Map)->list[tuple[int, int, int]]:
        ranges = m.ordered_ranges(pad=True)
        offsets: list[tuple[int, int, int]] = []
        for r in ranges:
            (dst, src, len) = r
            offset = dst - src
            end = src + len - 1
            offsets.append((src, end, offset))

        # print("Map:")
        # print(m.ranges)
        # print("Ordered:")
        # print(m.ordered_ranges(pad=True))
        # print("Offset:")
        # print(offsets)

        return offsets
    
    def combineOffsetsOld(self, m1: list[tuple[int, int, int]], m2: list[tuple[int, int, int]])->list[tuple[int, int, int]]:
        i = 0
        j = 0
        current = -1
        offsets: list[tuple[int, int, int]] = []
        # print("Combining offsets")
        # print(m1)
        # print(m2)

        while i < len(m1) or j < len(m2):
            # This loop iterates until we've used every item in both m1 and m2
            if i >= len(m1):
                while j < len(m2):
                    right = m2[j]
                    start = current+1
                    current = right[1]
                    offset = right[2]
                    offsets.append((start, current, offset))
                    j += 1
                break

            if j >= len(m2):
                while i < len(m1):
                    left = m1[i]
                    start = current+1
                    current = left[1]
                    offset = left[2]
                    offsets.append((start, current, offset))
                    i += 1
                break

            # If we get here, there are ranges left in both the left and the right
            left = m1[i]
            right = m2[j]
            if left[1] < right[1]:
                # Add a new interval to the map
                start = current+1
                current = left[1]
                offset = left[2] + right[2]
                offsets.append((start, current, offset))
                i += 1
            else:
                # Add a new interval to the map
                start = current+1
                current = right[1]
                offset = left[2] + right[2]
                offsets.append((start, current, offset))
                j += 1

        self.debug(offsets)
        return offsets
    
    def combineOffsets(self, m1: list[tuple[int, int, int]], m2: list[tuple[int, int, int]])->list[tuple[int, int, int]]:
        """
        Takes an existing mapping m1 that consists of (start, end, offset) lists and a second map m2 that.
        Returns a list of maps that is the result of applying m1 and then m2.
        Assumes that m1 and m2 are ordered (offsets are generated using an ordered_ranges call so that should be fine)
        """
        self.debug(f"Entered combineOffsets with {len(m1)} left offsets and {len(m2)} right offsets")
        offsets: list[tuple[int, int, int]] = [] # the return value

        if len(m1) == 0:
            return list(m2)

        for (m1_start, m1_end, m1_offset) in m1:
            self.debug(f"Handling a left offset: {m1_start}-{m1_end}->{m1_offset}")
            current = m1_start
            while current <= m1_end:
                self.debug(f"Hit the outer while, starting from {current}")
                new_start = current
                i = 0
                self.debug(f"Looking at {len(m2)} right offsets")
                while i < len(m2):
                    (m2_start, m2_end, m2_offset) = m2[i]
                    if m2_start <= current+m1_offset and m2_end >= current+m1_offset:
                        new_end = min(m1_end, m2_end-m1_offset)
                        self.debug(f"Found a matching right offset, through {new_end}")
                        new_offset = m1_offset + m2_offset
                        break
                    else:
                        self.debug(f"Skipping {m2_start}-{m2_end}")
                        i += 1

                if i >= len(m2): # We're past the last offset in m2
                    self.debug(f"Went past the end of the right loop")
                    new_end = m1_end
                    new_offset = m1_offset

                self.debug(f"Created a new offset: {new_start}-{new_end}->{new_offset}")
                offsets.append((new_start, new_end, new_offset))
                current = new_end+1

        return offsets

    def lookup(self, num:int)->int:
        for i in range(len(self.offsets)):
            (first, last, offset) = self.offsets[i]
            if num >= first and num <= last:
                return num + offset
        
        # If we fall through this far, we're beyong the mapping
        return num
    
    def __str__(self)->str:
        res = "Offset Map:\n"
        for offset in self.partial_offsets:
            for r in offset:
                res += f"({r[0]}-{r[1]}->{r[2]})\n"
        return res
                
class Almanac:
    """
    seeds: 79 14 55 13

    seed-to-soil map:
    50 98 2
    52 50 48

    ...

    humidity-to-location map:
    60 56 37
    56 93 4
    """
    def __init__(self, filename):
        self.maps: list[Map] = []
        with open(filename, 'r') as f:
            current_block: list[str] = []
            for line in f:
                next_line = line.strip()
                if next_line != "":
                    current_block.append(next_line)
                else:
                    self.parse_block(current_block)
                    current_block = []
            
            if len(current_block) > 0:
                self.parse_block(current_block)

        self.make_lookup_list()

    def make_lookup_list(self):
        maps_dict: dict[str, map] = {m.src: m for m in self.maps}
        lookup_list = []
        src = "seed"

        while src != "location":
            m = maps_dict[src]
            lookup_list.append(m)
            src = m.dst

        self.lookup_list = lookup_list
        
    def parse_block(self, block):
        if len(block) == 1: # assumes no empty maps...
            label, seeds = block[0].split(":")
            assert(label == "seeds")
            self.seeds = [int(seed) for seed in seeds.split()]
        else: # must be a map block
            self.maps.append(Map(block))

    def lookup_old(self, seed: int)-> int:
        maps_dict: dict[str, Map] = {}
        # Make the maps easy to look up by source

        for m in self.maps:
            maps_dict[m.src] = m
        current_lookup = "seed"
        current_value = seed
        while current_lookup != "location":
            current_map = maps_dict[current_lookup]
            current_lookup = current_map.dst
            current_value = current_map.lookup(current_value)

        return current_value
    
    def lookup(self, seed: int)-> int:
        val = seed
        for m in self.lookup_list:
            val = m.lookup(val)

        return val
    
    def solve1(self)->int:
        maps_dict: dict[str, Map] = {}
        # Make the maps easy to look up by source
        for m in self.maps:
            maps_dict[m.src] = m

        locations = []
        
        for seed in self.seeds:
            locations.append(self.lookup(seed))

        return min(locations)
    
    def old_solve2(self)->int:
        min_value = sys.maxsize
        i = 0
        j = 1
        while j < len(self.seeds):
            seed_start = self.seeds[i]
            seed_length = self.seeds[j]
            i += 2
            j += 2

            print(f"Starting to look up {seed_length} locations...", end="", flush=True)
            for seed in range(seed_start, seed_start +seed_length):
                new_value = self.lookup(seed)
                min_value = min(min_value, new_value)
            print("done.")

        return min_value
    
    def solve2(self)->int:
        om = OffsetMap(self.maps)
        offsets = om.offsets

        minimum_loc = self.lookup(self.seeds[0])

        seed_ranges:list[tuple[int, int]] = []
        i = 0
        while i < len(self.seeds):
            seed_ranges.append((self.seeds[i], self.seeds[i] + self.seeds[i + 1]))
            i += 2

        for (seed_start, seed_end) in seed_ranges:
            search_next = seed_start # search_next is the next number we're looking for
            i = 0
            while search_next <= seed_end and i < len(offsets):
                #print(f"Looking at {search_next} in the {i}th offset")
                (offset_min, offset_max, offset_num) = offsets[i]
                if offset_min <= search_next and offset_max >= search_next: # our next number is inside of offset[i]
                    loc = search_next + offset_num
                    minimum_loc = min(loc, minimum_loc)
                    search_next = min(seed_end+1, offset_max+1)
                else:
                    i += 1
            
        return minimum_loc
    
if __name__ == "__main__":
    logging.basicConfig()
    logging.getLogger().setLevel(os.getenv('LOG_LEVEL', 'INFO'))
    logger = logging.getLogger(__name__)
    if len(sys.argv) > 1:
        filename = sys.argv[1]
    else:
        filename = 'tiny_input'
    alm = Almanac(filename)
    logger.debug(f"The seed array is {alm.seeds}")
    logger.info(f"Parsed {len(alm.maps)} maps")
    sol1 = alm.solve1()
    logger.info(f"The starting location number was {sol1}")
    sol2 = alm.solve2()
    logger.info(f"The new starting location number was {sol2}")
