import json
from pprint import pprint

from feh_mods import ALL_MODS

with open("data/special.json") as f:
    special_data = json.load(f)


class Special(object):
    def __init__(self, special_type):
        if special_type not in special_data:
            raise Exception("%s not in special data" % special_type)

        self.name = special_type

        for key in ALL_MODS:
            setattr(self, key, None)

        for key in special_data[special_type]:
            setattr(self, key, special_data[special_type][key])

        self.curr_cooldown = self.cooldown
        self.reset()

    def __str__(self):
        return "%s (%s, %s)" % (self.name, self.curr_cooldown, self.cooldown)

    def reset(self, unit = None):
        adjustment = 0
        if unit:
            adjustment = unit.cooldown_adjustment()
        self.curr_cooldown = self.cooldown + adjustment

if __name__ == "__main__":
    w = Special("Astra")
    print(w)
    pprint(w.__dict__)