import json
from pprint import pprint

from feh_mods import ALL_MODS

with open("data/weapon.json") as f:
    weapon_data = json.load(f)

class Weapon(object):
    def __init__(self,weapon_type):
        if weapon_type not in weapon_data:
            raise Exception("%s not in weapon data" % weapon_type)

        self.name = weapon_type

        for key in ALL_MODS:
            setattr(self, key, None)

        for key in weapon_data[weapon_type]:
            setattr(self, key, weapon_data[weapon_type][key])

    def __str__(self):
        return "%s" % (self.name,)

    def __repr__(self):
        return "%s" % (self.name,)

ALL_WEAPONS = [Weapon(k) for k in weapon_data]

_useful_weapons = ["Absorb","Armads","Armorslayer+",
                   # "Assassin's Bow+","Assault",
                   # "Aura","Binding Blade","Blárblade+",
                   # "Blárraven+","Blárwolf+","Blue Egg+",
                   # "Bolganone+","Brave Axe+","Brave Bow+",
                   # "Brave Lance+","Brave Sword+","Brynhildr",
                   # "Carrot Axe+","Carrot Lance+","Cymbeline",
                   # "Dark Breath+ (Blue)","Dark Breath+ (Green)",
                   # "Dark Breath+ (Red)","Deathly Dagger","Dire Thunder",
                   # "Durandal","Eckesachs","Elfire","Élivágar",
                   # "Elthunder","Elwind","Emerald Axe+","Excalibur",
                   # "Falchion","Fear","Fenrir+","Fensalir","Fire",
                   # "Fire Breath+ (Blue)","Fire Breath+ (Green)",
                   # "Fire Breath+ (Red)","Firesweep Bow+","Flametongue+ (Blue)",
                   # "Flametongue+ (Green)","Flametongue+ (Red)","Fujin Yumi",
                   # "Fólkvangr","Gradivus","Gravity","Green Egg+","Gronnblade+",
                   # "Gronnraven+","Gronnwolf+","Hammer+","Hauteclere","Heavy Spear+",
                   # "Killer Axe+","Killer Bow+","Killer Lance+","Killing Edge+",
                   # "Light Breath+ (Blue)","Light Breath+ (Green)","Light Breath+ (Red)",
                   # "Lightning Breath+ (Blue)","Lightning Breath+ (Green)","Lightning Breath+ (Red)",
                   # "Mystletainn","Naga","Nóatún","Pain","Panic","Parthia","Poison Dagger+",
                   # "Ragnell","Raijinto","Rauðrblade+","Rauðrraven+","Rauðrwolf+","Rexcalibur+",
                   # "Rogue Dagger+","Ruby Sword+","Sapphire Lance+","Siegfried","Sieglinde",
                   # "Siegmund","Silver Axe+","Silver Bow+","Silver Dagger+","Silver Lance+",
                   # "Silver Sword+","Slow","Smoke Dagger+","Sol Katti","Thoron+","Tyrfing",
                   # "Valaskjálf","Wo Dao+","Yato",
                   ]

USEFUL_WEAPONS = [Weapon(k) for k in _useful_weapons]

if __name__ == "__main__":
    w = Weapon("Armads")
    print(w)
    pprint(w.__dict__)
    print (w.color)