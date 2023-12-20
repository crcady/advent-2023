import unittest
from solve import Almanac, Map, OffsetMap

class TestAlmanac(unittest.TestCase):

    def setUp(self):
        self.almanac = Almanac('tiny_input')

    def test_part1(self):
        res = self.almanac.solve1()
        self.assertEqual(res, 35, "Didn't get the right first answer")

    def test_offset1(self):
        offset = OffsetMap(self.almanac.maps[0:1])
        res = [offset.lookup(seed) for seed in self.almanac.seeds]
        self.assertEqual(res, [81, 14, 57, 13])

    def test_offset2(self):
        offset = OffsetMap(self.almanac.maps[0:2])
        res = [offset.lookup(seed) for seed in self.almanac.seeds]
        self.assertEqual(res, [81, 53, 57, 52])

    def test_offset3(self):
        offset = OffsetMap(self.almanac.maps[0:3])
        res = [offset.lookup(seed) for seed in self.almanac.seeds]
        self.assertEqual(res, [81, 49, 53, 41])

    def test_offset4(self):
        offset = OffsetMap(self.almanac.maps[0:4])
        res = [offset.lookup(seed) for seed in self.almanac.seeds]
        self.assertEqual(res, [74, 42, 46, 34])

    def test_offset5(self):
        offset = OffsetMap(self.almanac.maps[0:5])
        res = [offset.lookup(seed) for seed in self.almanac.seeds]
        self.assertEqual(res, [78, 42, 82, 34])

    def test_offset6(self):
        offset = OffsetMap(self.almanac.maps[0:6])
        res = [offset.lookup(seed) for seed in self.almanac.seeds]
        self.assertEqual(res, [78, 43, 82, 35])

    def test_offset7(self):
        offset = OffsetMap(self.almanac.maps[0:7])
        res = [offset.lookup(seed) for seed in self.almanac.seeds]
        self.assertEqual(res, [82, 43, 86, 35])

if __name__ == "__main__":
    unittest.main()