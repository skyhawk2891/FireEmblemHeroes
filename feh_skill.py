import json

from feh_mods import ALL_MODS

with open("data/skill.json") as f:
    skill_data = json.load(f)

skill_slots = ["a","b","c","s"]

class Skill(object):

    def __init__(self, slot, skill_name):
        if slot not in skill_slots:
            raise Exception("%s is not a valid skill slot" % slot)

        self.slot = slot
        self.name = skill_name

        if skill_name not in skill_data[slot]:
            raise Exception("%s not in skill data for slot %s" % (skill_name,slot))

        for key in ALL_MODS:
            setattr(self, key, None)

        for key in skill_data[slot][skill_name]:
            setattr(self, key, skill_data[slot][skill_name][key])

    def __str__(self):
        return "%s" % (self.name)

    def __repr__(self):
        return "%s" % (self.name)

ALL_SKILLS = {"a": [], "b": [], "c": [], "s": []}
for slot in skill_data:
    for skill in skill_data[slot]:
        ALL_SKILLS[slot].append(Skill(slot, skill))

USEFUL_SKILLS = {"a": [],"b": [],"c":[], "s": []}
# all s skills are useful:
for skill in skill_data["s"]:
    USEFUL_SKILLS["s"].append(Skill("s",skill))
a_skills = ["Armored Blow 3","Attack +3","Attack/Def +2",
            "Close Counter","Darting Blow 3","Defense +3",
            "Defiant Atk 3","Defiant Def 3","Defiant Res 3",
            "Defiant Spd 3","Distant Counter","Fortress Def 3",
            "Fury 3","Grani's Shield" ,
            #"Heavy Blade 3",
            "HP +5","Iote's Shield","Life and Death 3",
            "Resistance +3","Speed +3","Svalinn Shield",
            "Swift Sparrow 2","Triangle Adept 3",
            "Warding Blow 3",
            ]
b_skills = ["Axebreaker 3","Bowbreaker 3","B Tomebreaker 3",
            "Brash Assault 3","Daggerbreaker 3","Desperation 3",
            "Drag Back","Escape Route 3","G Tomebreaker 3",
            "Guard 3","Hit and Run","Knock Back",
            "Lancebreaker 3","Live to Serve 3","Lunge",
            "Obstruct 3","Pass 3","Poison Strike 3",
            "Quick Riposte 3","R Tomebreaker 3","Renewal 3",
            "Seal Atk 3","Seal Def 3","Seal Res 3","Seal Spd 3",
            "Swordbreaker 3","Vantage 3","Wary Fighter 3",
            "Watersweep 3","Windsweep 3","Wings of Mercy 3"

            ]
c_skills = ["Breath of Life 3","Fortify Armor","Fortify Cavalry",
            "Fortify Def 3","Fortify Dragons","Fortify Fliers",
            "Fortify Res 3","Goad Armor","Goad Cavalry","Goad Fliers",
            "Hone Armor","Hone Atk 3","Hone Cavalry","Hone Fliers",
            "Hone Spd 3","Savage Blow 3","Spur Atk 3","Spur Def 3",
            "Spur Def/Res 2","Spur Res 3","Spur Spd 3","Threaten Atk 3",
            "Threaten Def 3","Threaten Res 3","Threaten Spd 3","Ward Armor",
            "Ward Cavalry","Ward Fliers",
            ]
for skill in a_skills:
    USEFUL_SKILLS["a"].append(Skill("a", skill))
for skill in b_skills:
    USEFUL_SKILLS["b"].append(Skill("b", skill))
for skill in c_skills:
    USEFUL_SKILLS["c"].append(Skill("c", skill))


if __name__ == "__main__":
    #pprint(skill_data)
    w = Skill("c","Threaten Atk 2")
    # print(w)
    # pprint(w.__dict__)
