import json

with open("data/terrain_type.json") as f:
    terrain_type_data = json.load(f)

terrain_ascii = {"0": ".",
              "1": "#",
              "2": "T",
              "3": "w",
              "4": "M",
              "5": "_",
              "6": "-"
              }

inverted_terrain_ascii = {v:k for k,v in terrain_ascii.items()}

class Point(object):
    def __init__(self,x=0,y=0):
        self.x = x
        self.y = y

    @staticmethod
    def from_list(l):
        p = Point(l[0],l[1])
        return p

    def distance(self,p):
        return ((p.x - self.x) ** 2 + (p.y - self.y) ** 2) ** .5

class Terrain(object):
    land = "0"
    wall = "1"
    tree = "2"
    water = "3"
    mountain = "4"
    breakable_wall_1 = "5"
    breakable_wall_2 = "6"



    def output(self):
        return terrain_ascii.get(self.terrain_type," ")

    def __init__(self, terrain_type):
        self.hits_to_break = 0
        self.terrain_type = terrain_type
        self.set_type(self.terrain_type)

    @staticmethod
    def from_map_ascii(char):
        terrain_type = inverted_terrain_ascii.get(char)
        return Terrain(terrain_type)

    def set_type(self, terrain_type):
        if terrain_type not in terrain_type_data:
            raise Exception("%s not in terrain_type_data" % terrain_type)

        for key in terrain_type_data[terrain_type]:
            setattr(self, key, terrain_type_data[terrain_type][key])
        if self.breakable:
            self.hits_to_break = self.breakable


    def is_infantry_passable(self):
        return self.infantry_passable and not self.hits_to_break

    def is_flier_passable(self):
        return self.flier_passable and not self.hits_to_break

    def is_horse_passable(self):
        return self.horse_passable and not self.hits_to_break

    def can_hit(self):
        return self.hits_to_break > 0

    def hit(self):
        if self.hits_to_break > 0:
            self.hits_to_break -= 1

    def move_cost(self):
        return self.move_cost


sample_map_str ="""T..TT.
......
.T.T.T
...T..
T.T..T
..T.T.
......
T.T..T
"""

# 0 1 2 3 4 5 6
# 7
#
#
#
#
#
#


class Map(object):
    def __init__(self, map_str = None):
        if map_str:
            self.height = len(map_str.splitlines())
            self.width = len(map_str.splitlines()[0])
            self.map = [Terrain.from_map_ascii(x) for x in map_str if x != "\n"]

        else:
            self.width = 6
            self.height = 8
            self.map = [Terrain(Terrain.land) for _ in range(self.width * self.height)]

        self.team1_location = []
        self.team2_location = []

    def get_terrain_at_position(self,x,y):
        return self.map[y * self.height + x]

    def print_map(self):
        for count, t in enumerate(self.map):
            if count != 0 and count % self.width == 0:
                print("\n",end="")
            print(t.output(),end="")

if __name__ == "__main__":
    m = Map(sample_map_str)
    m.print_map()
    print("")
    print(m.get_terrain_at_position(4,0).is_horse_passable())