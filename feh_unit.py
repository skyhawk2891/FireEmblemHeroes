import itertools
import json

from feh_skill import Skill, ALL_SKILLS
from feh_util import round_num
from feh_weapon import Weapon, ALL_WEAPONS

from feh_special import Special
from vcbenchmark import VCBenchmark

with open("data/unit.json") as f:
    unit_data = json.load(f)

#stat growth amounts from lvl 1 to lvl 40
statGrowths = [[4, 6, 8, 10, 12, 14, 16, 18, 20, 22, 24, 26],
              [5, 7, 9, 11, 13, 15, 17, 19, 21, 23, 25, 27],
              [7, 9, 11, 13, 15, 17, 19, 21, 23, 25, 27, 29],
              [8, 10, 12, 14, 16, 18, 20, 22, 24, 26, 28, 30],
              [8, 10, 13, 15, 17, 19, 22, 24, 26, 28, 30, 33]
              ]

verbose = True


class Unit(object):
    def __init__(self, unit_name):
        if unit_name not in unit_data:
            raise Exception("%s not in unit data" % unit_name)

        self.name = unit_name

        self.weapon = None
        self.special = None
        self.passive_a = None
        self.passive_b = None
        self.passive_c = None
        self.base_stat = None
        self.weapon_type = None
        
        for key in unit_data[unit_name]:
            setattr(self, key, unit_data[unit_name][key])

        self.level = 40
        self.stat_total = {}
        self.stat_current = {}
        self.rarity = 5
        self.merged = 0
        self.boon_stat = None
        self.bane_stat = None

        self.equipped_weapon = None # type: Weapon

        self.equipped_assist = None

        self.equipped_special = None # type: Special

        self.equipped_passive_a = None #type: Skill
        self.equipped_passive_b = None #type: Skill
        self.equipped_passive_c = None #type: Skill
        self.equipped_passive_s = None #type: Skill

        self.holders = []

        # temporary as long as unit is within range
        self.spur_mods = []
        # lasts for 2 "turns"
        self.round_mods = []
        # temporary buffs that occur within the attack phase
        self.temp_buffs = []

        self.init_total_stats()

    @staticmethod
    def from_dict(d):
        u = Unit(d["name"])
        u.merged = d["merged"]
        u.boon_stat = d["boon_stat"]
        u.bane_stat = d["bane_stat"]
        u.level = d["level"]
        if d["weapon"]:
            u.equipped_weapon = Weapon(d["weapon"])
        if d["passive_a"]:
            u.equipped_passive_a = Skill("a",d["passive_a"])
        if d["passive_b"]:
            u.equipped_passive_a = Skill("b",d["passive_b"])
        if d["passive_c"]:
            u.equipped_passive_a = Skill("c",d["passive_c"])
        if d["passive_s"]:
            u.equipped_passive_a = Skill("s",d["passive_s"])
        u.init_total_stats()
        return u

    @staticmethod
    def from_encoding(str):
        arr = str.split("_")
        u = Unit(arr[0])
        if arr[1]:
            u.equipped_weapon = Weapon(arr[1])
        if arr[2]:
            u.equipped_special = Special(arr[2])
        if arr[3]:
            u.equipped_passive_a = Skill("a",arr[3])
        if arr[4]:
            u.equipped_passive_b = Skill("b",arr[4])
        if arr[5]:
            u.equipped_passive_c = Skill("c",arr[5])
        if arr[6]:
            u.equipped_passive_s = Skill("s",arr[6])
        return u

    @staticmethod
    def max_from_base(unit_name, merged = 0, boon_stat = None, bane_stat = None):
        #print(unit_name)
        u = Unit(unit_name)
        u.merged = merged
        u.boon_stat = boon_stat
        u.bane_stat = bane_stat
        u.equipped_weapon = Weapon(u.weapon[0])
        if u.special:
            u.equipped_special = Special(u.special[0])
        if u.passive_a:
            u.equipped_passive_a = Skill("a",u.passive_a[0])
        if u.passive_b:
            u.equipped_passive_b = Skill("b",u.passive_b[0])
        if u.passive_c:
            u.equipped_passive_c = Skill("c",u.passive_c[0])
        u.init_total_stats()
        return u

    def __str__(self):
        str = "Name: %s\n" % self.name
        str += "Color: %s\n" % self.color
        str += "MoveType: %s\n" % self.move_type
        str += "Weapon: %s\n" % self.equipped_weapon
        str += "Assist: %s\n" % self.equipped_assist
        str += "Special: %s\n" % self.equipped_special
        str += "Passive A: %s\n" % self.equipped_passive_a
        str += "Passive B: %s\n" % self.equipped_passive_b
        str += "Passive C: %s\n" % self.equipped_passive_c
        str += "Passive S: %s\n" % self.equipped_passive_s
        str += "HP: %s/%s\n" % (self.stat_current["hp"], self.stat_total["hp"])
        str += "ATK: %s\n" % (self.stat_current["atk"])
        str += "SPD: %s\n" % (self.stat_current["spd"])
        str += "DEF: %s\n" % (self.stat_current["def"])
        str += "RES: %s\n" % (self.stat_current["res"])
        #str += "%s\n" % self.temp_buffs
        return str

    def encode_for_key(self):
        def n_or_b(n):
            return n.name if n else ""
        return "%s_%s_%s_%s_%s_%s_%s" % \
              (self.name,
               n_or_b(self.equipped_weapon),
               n_or_b(self.equipped_special),
               n_or_b(self.equipped_passive_a),
               n_or_b(self.equipped_passive_b),
               n_or_b(self.equipped_passive_c),
               n_or_b(self.equipped_passive_s)
               )

    def mod_holders(self):
        """
        return a list of equipped character things that can hold mods on them
        :return: 
        """
        return self.holders

    def equippable_weapons(self, weaponset= None):
        weapons = []
        if weaponset is None:
            weaponset = ALL_WEAPONS
        for w in weaponset:
            if w.type == self.weapon_type:
                if w.char_unique and w.name in self.weapon:
                    weapons.append(w)
                elif not w.char_unique:
                    weapons.append(w)
        return weapons

    def is_dragon(self):
        return self.weapon_type in ["Red Breath","Green Breath","Blue Breath"]

    def range(self):
        if self.weapon_type in ["Red Tome","Green Tome","Blue Tome","Bow","Dagger","Staff"]:
            return 2
        else:
            return 1

    def equippable_skills(self,slot, skillset=None):
        skills = []
        if skillset is None:
            skillset = ALL_SKILLS
        for s in skillset[slot]:
            if s.weapon_restrict and s.weapon_restrict != self.weapon_type:
                skills.append(s)
            elif s.weapon_unique and s.weapon_unique == self.weapon_type:
                skills.append(s)
            elif s.move_unique and s.move_unique == self.move_type:
                skills.append(s)
            elif s.dragon_unique and self.is_dragon():
                skills.append(s)
            elif s.color_restrict and s.color_restrict != self.color:
                skills.append(s)
            elif s.range_unique and s.range_unique == self.range():
                skills.append(s)
            elif not s.weapon_restrict and not s.weapon_unique \
                    and not s.move_unique and not s.dragon_unique \
                    and not s.color_restrict and not s.range_unique:
                skills.append(s)
        return skills

    def permutations(self, weapons, skills):
        a_w = self.equippable_weapons(weapons)
        a_a = self.equippable_skills("a", skills)
        a_b = self.equippable_skills("b", skills)
        a_c = self.equippable_skills("c", skills)
        a_s = self.equippable_skills("s", skills)
        print("%s combinations" % (len(a_w) * len(a_a) * len(a_b) * len(a_c) * len(a_s)))
        return itertools.product(a_w, a_a, a_b, a_c, a_s)

    def clamp_stats(self):
        """
        prevents total and current stats from going over expected values
        :return: 
        """
        for stat in self.stat_total:
            if self.stat_total[stat] < 0:
                self.stat_total[stat] = 0
            if self.stat_total[stat] > 99:
                self.stat_total[stat] = 99
        
        for stat in self.stat_current:
            if self.stat_current[stat] < 0:
                self.stat_current[stat] = 0
            if self.stat_current[stat] > 99:
                self.stat_current[stat] = 99

    def init_total_stats(self):
        # reset everything
        self.stat_total = {}
        self.round_mods = []
        self.spur_mods = []
        if self.equipped_special:
            self.equipped_special.reset(self)

        # base stats
        if self.base_stat:
            self.stat_total["hp"] = self.base_stat["star-" + str(self.rarity)]["hp"]
            self.stat_total["atk"] = self.base_stat["star-" + str(self.rarity)]["atk"]
            self.stat_total["spd"] = self.base_stat["star-" + str(self.rarity)]["spd"]
            self.stat_total["def"] = self.base_stat["star-" + str(self.rarity)]["def"]
            self.stat_total["res"] = self.base_stat["star-" + str(self.rarity)]["res"]
        else:
            self.stat_total["hp"] = self.hp
            self.stat_total["atk"] = self.atk
            self.stat_total["spd"] = self.spd
            self.stat_total["def"] = self.__getattribute__("def")
            self.stat_total["res"] = self.res

        if self.boon_stat:
            self.stat_total[self.boon_stat] += 1

        if self.bane_stat:
            self.bane_stat[self.bane_stat] -= 1


        # how many units have been merged into this one
        if self.merged > 0:
            stat_names =["hp", "atk", "spd", "def", "res"]
            merge_bonus_order =["hp", "atk", "spd", "def", "res"]

            # sort stats from highest to lowest with insertion sort haha
            for stat_index in range(1,5):
                inserted = False
                for order_index in range(0,stat_index):
                    if self.stat_total[stat_names[stat_index]] > self.stat_total[merge_bonus_order[order_index]]:
                        # push back
                        for push_index in range(stat_index -1, order_index, -1):
                            merge_bonus_order[push_index + 1] = merge_bonus_order[push_index]
                        # insert
                        merge_bonus_order[order_index] = stat_names[stat_index]
                        inserted = True
                        break

                if not inserted:
                    merge_bonus_order[stat_index] = stat_names[stat_index]

            # apply bonuses
            bonus_index = 0
            for merge_count in range(0,self.merged):
                for i in range(0,2):
                    self.stat_total[merge_bonus_order[bonus_index]] += 1
                    bonus_index = (bonus_index + 1) % 5

        if self.level == 40 and self.base_stat:
            self.stat_total["hp"] += statGrowths[self.rarity-1][self.base_stat["growth"]["hp"]]
            self.stat_total["atk"] += statGrowths[self.rarity-1][self.base_stat["growth"]["atk"]]
            self.stat_total["spd"] += statGrowths[self.rarity-1][self.base_stat["growth"]["spd"]]
            self.stat_total["def"] += statGrowths[self.rarity-1][self.base_stat["growth"]["def"]]
            self.stat_total["res"] += statGrowths[self.rarity-1][self.base_stat["growth"]["res"]]

            if self.boon_stat:
                self.stat_total[self.boon_stat] += 1

            if self.bane_stat:
                self.bane_stat[self.bane_stat] -= 1

        # add weapon might
        if self.equipped_weapon:
            self.stat_total["atk"] += self.equipped_weapon.might

        self.holders = []
        if self.equipped_weapon:
            self.holders.append(self.equipped_weapon)
        if self.equipped_passive_a:
            self.holders.append(self.equipped_passive_a)
        if self.equipped_passive_b:
            self.holders.append(self.equipped_passive_b)
        if self.equipped_passive_c:
            self.holders.append(self.equipped_passive_c)
        if self.equipped_passive_s:
            self.holders.append(self.equipped_passive_s)

        # apply stat mods
        for holder in self.mod_holders():
            if holder.stat_mod:
                self.add_stat_mod_to_total(holder.stat_mod)

        self.stat_current = self.stat_total.copy()

        self.clamp_stats()

    def add_stat_mod_to_total(self,stat_mod):
        for stat, value in stat_mod.items():
            self.stat_total[stat] += value

    def is_alive(self):
        return self.stat_current["hp"] > 0

    def add_temp_mod(self,mod):
        # add to temp buffs
        self.temp_buffs.append(mod)
        # adjust current stats
        for stat,value in mod.items():
            self.stat_current[stat] += value

    def remove_all_temp_mods(self):
        for mod in self.temp_buffs:
            for stat, value in mod.items():
                self.stat_current[stat] -= value
        self.temp_buffs = []

    def cooldown_adjustment(self):
        adjustment = 0
        for holder in self.mod_holders():
            if holder.spec_cooldown_mod:
                adjustment += holder.spec_cooldown_mod
        return adjustment

    def can_activate_sweep(self,enemy):
        for holder in self.mod_holders():
            if holder.sweep:
                if self.stat_current["spd"] - enemy.stat_current["spd"] >= holder.sweep["spd_adv"] and enemy.equipped_weapon.type in holder.sweep["weapon_type"]:
                    return True
        return False

    def can_counter_regardless_range(self):
        return any([1 for holder in self.mod_holders() if holder.counter])

    def can_activate_brash(self,enemy_can_counter):
        for holder in self.mod_holders():
            if holder.brash and self.stat_current["hp"] <= self.stat_total["hp"] * holder.brash["threshold"] and enemy_can_counter:
                return True
        return False

    def can_activate_riposte(self,enemy_can_counter):
        for holder in self.mod_holders():
            if holder.riposte and self.stat_current["hp"] >= self.stat_total["hp"] * holder.riposte["threshold"] and enemy_can_counter:
                return True
        return False

    def can_activate_wary(self):
        for holder in self.mod_holders():
            if holder.wary and self.stat_current["hp"] >= self.stat_total["hp"] * holder.wary["threshold"]:
                return True
        return False

    def can_activate_vantage(self):
        for holder in self.mod_holders():
            if holder.vantage and self.stat_current["hp"] <= self.stat_total["hp"] * holder.vantage["threshold"]:
                return True
        return False

    def can_activate_desperation(self):
        for holder in self.mod_holders():
            if holder.desperation and self.stat_current["hp"] <= self.stat_total["hp"] * holder.desperation["threshold"]:
                return True
        return False

    def can_break_enemy(self,enemy):
        for holder in self.mod_holders():
            if holder.breaker:
                if holder.breaker["weapon_type"] == enemy.equipped_weapon.type and self.stat_current["hp"] > self.stat_total["hp"] * holder.breaker["threshold"]:
                    return True
        return False

    def has_weapon_color_advantage(self,enemy):
        if self.equipped_weapon.color_effective == enemy.color:
            return 1
        elif enemy.equipped_weapon.color_effective == self.color:
            return -1
        return 0

    def has_weapon_triangle_advantage(self,enemy):
        if self.equipped_weapon.color == enemy.color or self.color == "Colorless" or enemy.color == "Colorless":
            return 0
        elif (self.equipped_weapon.color == "Red" and enemy.color == "Green") or (self.equipped_weapon.color == "Green" and enemy.color == "Blue") or (self.equipped_weapon.color == "Blue" and enemy.color == "Red"):
            return 1
        return -1

    def triangle_advantage_mod(self, enemy):
        for holder in self.mod_holders():
            if holder.tri_advantage:
                return holder.tri_advantage

    def can_cancel_effective(self):
        return any([1 for holder in self.mod_holders() if holder.cancel_effective])

    def in_range_of(self,enemy):
        if self.equipped_weapon and enemy.equipped_weapon and self.equipped_weapon.range == enemy.equipped_weapon.range:
            return True
        return False

    def has_no_follow(self):
        return any([1 for holder in self.mod_holders() if holder.no_follow])

    def _after_combat_effects(self, poison, recoil, heal):
        oldhp = self.stat_current["hp"]
        if poison > 0 and (poison + recoil > heal):
            self.stat_current["hp"] = max(oldhp - poison - recoil + heal, 1)
        elif recoil > 0 and recoil > heal:
            self.stat_current["hp"] = max(oldhp - recoil + heal, 1)
        elif heal > 0:
            self.stat_current["hp"] = min(oldhp - poison - recoil + heal, self.stat_total["hp"])


    def _single_combat(self,enemy, initiator, second_brave_attack = False):
        """
        
        :param enemy: Unit
        :param second_brave_attack:
        :return: 
        """

        atk_special = False
        def_special = False
        atk_power = self.stat_current["atk"]
        enemy_old_hp = enemy.stat_current["hp"]

        # move effectiveness
        for holder in self.mod_holders():
            if holder.move_effective and holder.move_effective == enemy.move_type:
                if not enemy.can_cancel_effective():
                    atk_power = round_num(atk_power * 1.5, False)
                    break

        # dragon effectiveness
        for holder in self.mod_holders():
            if holder.dragon_effective and enemy.weapon_type in ("Red Breath","Green Breath","Blue Breath") :
                if not enemy.can_cancel_effective():
                    atk_power = round_num(atk_power * 1.5, False)
                    break

        weapon_color_advantage = self.has_weapon_color_advantage(enemy)
        tri_advantage = self.has_weapon_triangle_advantage(enemy)
        atkmod = 1
        if weapon_color_advantage > 0:
            atkmod = 1.2
        elif weapon_color_advantage < 0:
            atkmod = .8
        elif tri_advantage > 0:
            atkmod =1.2
        elif tri_advantage < 0:
            atkmod = .8

        if atkmod > 1:
            if self.equipped_weapon.tri_advantage:
                atkmod += .2
            elif enemy.equipped_weapon.tri_advantage:
                atkmod += .2
            elif self.equipped_passive_a and self.equipped_passive_a.tri_advantage:
                atkmod += self.equipped_passive_a.tri_advantage
            elif enemy.equipped_passive_a and enemy.equipped_passive_a.tri_advantage:
                atkmod += enemy.equipped_passive_a.tri_advantage
            atk_power = round_num(atk_power * atkmod, False)

        elif atkmod < 1:
            if self.equipped_weapon.tri_advantage:
                atkmod -= .2
            elif enemy.equipped_weapon.tri_advantage:
                atkmod -= .2
            elif self.equipped_passive_a and self.equipped_passive_a.tri_advantage:
                atkmod -= self.equipped_passive_a.tri_advantage
            elif enemy.equipped_passive_a and enemy.equipped_passive_a.tri_advantage:
                atkmod -= enemy.equipped_passive_a.tri_advantage
            atk_power = round_num(atk_power * atkmod, True)

        def_reduction = 0
        if self.equipped_weapon.magical:
            def_reduction = enemy.stat_current["res"]
        else:
            def_reduction = enemy.stat_current["def"]

        if self.equipped_special and self.equipped_special.enemy_def_res_mod and self.equipped_special.curr_cooldown <= 0:
            def_reduction -= round_num(self.equipped_special.enemy_def_res_mod * def_reduction, False)
            atk_special = True
        #print("atk: %s def: %s" % (atk_power, def_reduction))
        dmg = atk_power - def_reduction

        if self.equipped_special and self.equipped_special.dmg_buff_by_stat and self.equipped_special.curr_cooldown <= 0:
            dmg += round_num(self.equipped_special.dmg_buff_by_stat["buff"] * self.stat_current[self.equipped_special.dmg_buff_by_stat["stat"]],False)
            atk_special = True

        if self.equipped_special and self.equipped_special.dmg_suffer_buff and self.equipped_special.curr_cooldown <= 0:
            dmg += round_num((self.stat_total["hp"] - self.stat_current["hp"]) * self.equipped_special.dmg_suffer_buff,False)
            atk_special = True

        # cap damage at 0
        dmg = max(dmg,0)

        # halve staff damage
        if self.weapon_type == "Staff":
            dmg = round_num(dmg / 2, False)

        # todo: should read from all mod_holder types
        if self.equipped_weapon.spec_damage_bonus and (atk_special or (self.equipped_special and self.equipped_special.heal_dmg and self.equipped_special.curr_cooldown <= 0)):
            dmg += self.equipped_weapon.spec_damage_bonus

        # damage reduction from defender
        if enemy.equipped_special and enemy.equipped_special.reduce_dmg and enemy.equipped_special.curr_cooldown <= 0 and enemy.equipped_special.reduce_dmg["range"] == self.equipped_weapon.range:
            dmg -= round_num(dmg * enemy.equipped_special.reduce_dmg["dmg_mod"], False)
            def_special = True

        dmg = max(dmg, 0)

        # check for miracle
        if enemy.stat_current["hp"] - dmg <= 0 and enemy.stat_current["hp"] > 1 and enemy.equipped_special and enemy.equipped_special.survive and enemy.equipped_special.curr_cooldown <= 0:
            enemy.stat_current["hp"] = 1
            def_special = True
        else:
            enemy.stat_current["hp"] = max(enemy.stat_current["hp"] - dmg, 0)

        if verbose:
            print("%s does %s damage to %s" % (self.name, dmg, enemy.name))


        # check for healing
        did_heal = False
        atk_old_hp = self.stat_current["hp"]
        heal_amount = 0
        if self.equipped_weapon.heal_dmg:
            heal_amount += round_num((enemy_old_hp - enemy.stat_current["hp"]) * self.equipped_weapon.heal_dmg, False)
            did_heal = True

        if self.equipped_special and self.equipped_special.heal_dmg and self.equipped_special.curr_cooldown <= 0:
            heal_amount += round_num((enemy_old_hp - enemy.stat_current["hp"]) * self.equipped_special.heal_dmg, False)
            did_heal = True
            atk_special = True

        if did_heal:
            self.stat_current["hp"] = min(self.stat_total["hp"], self.stat_current["hp"] + heal_amount)

        if atk_special:
            self.equipped_special.reset(self)
        elif self.equipped_special and self.equipped_special.curr_cooldown > 0:
            self.equipped_special.curr_cooldown -= 1
            if verbose:
                print("%s's cooldown reduced by 1 to %s" % (self.name, self.equipped_special.curr_cooldown))

        if def_special:
            enemy.equipped_special.reset(enemy)
        elif enemy.equipped_special and enemy.equipped_special.curr_cooldown > 0:
            enemy.equipped_special.curr_cooldown -= 1

        # we only brave weapon if we're the initiator
        if initiator and self.equipped_weapon.brave and not second_brave_attack and enemy.stat_current["hp"] > 0:
            self._single_combat(enemy,initiator, True)

    def attack_unit(self,enemy):
        # aoe before combat
        # TODO: affect others on map
        if self.equipped_special and self.equipped_special.before_combat_aoe and self.equipped_special.curr_cooldown <= 0:
            self.equipped_special.reset(self)

            # TODO: is aoe affected by buffs?
            aoe_dmg = self.stat_current["atk"]
            if self.equipped_weapon and self.equipped_weapon.magical:
                aoe_dmg -= enemy.stat_current["res"]
            else:
                aoe_dmg -= enemy.stat_current["def"]

            if self.equipped_special.aoe_dmg_mod:
                aoe_dmg = round_num(aoe_dmg * self.equipped_special.aoe_dmg_mod,False)

            # cap damage at 0
            aoe_dmg = max(aoe_dmg,0)

            # apply aoe damage
            oldhp = enemy.stat_current["hp"]
            enemy.stat_current["hp"] = max(enemy.stat_current["hp"] - aoe_dmg,1)
            if verbose:
                print("%s deals aoe damage before combat [%s]. %s damage dealt. %s HP: %s -> %s" %
                    (self.name, self.equipped_special.name, aoe_dmg, enemy.name,oldhp, enemy.stat_current["hp"]))


        # attacker initiate bonus
        for holder in self.mod_holders():
            if holder.initiate_mod:
                self.add_temp_mod(holder.initiate_mod)

        # attacker below hp threshold bonus
        for holder in self.mod_holders():
            if holder.below_threshold_mod and self.stat_current["hp"] <= holder.below_threshold_mod["threshold"] * self.stat_total["hp"]:
                self.add_temp_mod(holder.below_threshold_mod["stat_mod"])

        # attacker blade tome bonuses
        for holder in self.mod_holders():
            if holder.add_bonus:
                # bonuses are equal to the number of non-temporary buffs
                atkbuff = len(self.spur_mods) + len(self.round_mods)
                self.add_temp_mod({"atk": atkbuff})

        # defending bonuses
        for holder in enemy.mod_holders():
            if holder.defend_mod:
                enemy.add_temp_mod(holder.defend_mod)

        # defending below hp threshold bonus
        for holder in enemy.mod_holders():
            if holder.below_threshold_mod and enemy.stat_current["hp"] <= holder.below_threshold_mod["threshold"] * enemy.stat_total["hp"]:
                enemy.add_temp_mod(holder.below_threshold_mod["stat_mod"])

        # defender blade tome bonuses
        for holder in enemy.mod_holders():
            if holder.add_bonus:
                # bonuses are equal to the number of non-temporary buffs
                atkbuff = len(enemy.spur_mods) + len(enemy.round_mods)
                enemy.add_temp_mod({"atk": atkbuff})

        # can defender counter?
        enemy_can_counter = enemy.equipped_weapon and self.equipped_weapon \
                            and (self.in_range_of(enemy)or any([1 for holder in enemy.mod_holders() if holder.counter])) \
                            and not any([1 for holder in self.mod_holders() if holder.prevent_counter]) and not any([1 for holder in enemy.mod_holders() if holder.prevent_counter]) \
                            and not self.can_activate_sweep(enemy)
        enemy_attacks = False

        # can unit make a follow up
        can_follow_up = not enemy.has_no_follow()

        # these checks must be done before we potentially get damaged
        desperation_passive = self.can_activate_desperation()
        def_desperation_passive = enemy.can_activate_desperation()
        wary_passive = self.can_activate_wary()
        brash_passive = self.can_activate_brash(enemy_can_counter)
        breaker_passive = self.can_break_enemy(enemy)
        def_wary_passive = enemy.can_activate_wary()
        def_riposte_passive = enemy.can_activate_riposte(enemy_can_counter)
        def_vantage_passive = enemy.can_activate_vantage()
        def_breaker_passive = enemy.can_break_enemy(self)

        outspeed = self.stat_current["spd"] > enemy.stat_current["spd"] + 5
        enemy_outspeed = enemy.stat_current["spd"] >= self.stat_current["spd"] + 5

        def_attacks = False
        vantage = False
        desperation = False

        # START OF COMBAT

        # vantage
        if def_vantage_passive and enemy_can_counter:
            if enemy.in_range_of(self):
                enemy._single_combat(self,False, False)
                def_attacks = True
                vantage = True
            elif enemy.can_counter_regardless_range():
                enemy._single_combat(self,False, False)
                def_attacks = True
                vantage = True

        # attacker initiates
        if self.stat_current["hp"] > 0:
            self._single_combat(enemy, True, False )

        # desperation
        if desperation_passive and self.stat_current["hp"] > 0 and enemy.stat_current["hp"] > 0 and can_follow_up:
            if not def_desperation_passive and not def_breaker_passive and not def_wary_passive:
                if breaker_passive:
                    desperation = True
                    can_follow_up = False
                    if def_riposte_passive and enemy_outspeed:
                        self._single_combat(enemy,True, False)
                    else:
                        self._single_combat(enemy, False)
                elif outspeed:
                    desperation = True
                    can_follow_up = False
                    self._single_combat(enemy, True, False)
                elif brash_passive:
                    desperation = True
                    can_follow_up = False
                    self._single_combat(enemy,True, False)
                # defender cancels follow up
            elif (def_wary_passive or def_breaker_passive) and not wary_passive and outspeed:
                if not breaker_passive:
                    desperation = True
                    can_follow_up = False
                    self._single_combat(enemy, True, False)
                elif brash_passive:
                    desperation = True
                    can_follow_up = False
                    self._single_combat(enemy, True, False)

        # defender counter attack
        if self.stat_current["hp"] > 0 and enemy.stat_current["hp"] > 0:
            # !vantage
            if not def_vantage_passive:
                if enemy.in_range_of(self) and enemy_can_counter:
                    enemy._single_combat(self,False, False)
                    def_attacks = True
                elif enemy.can_counter_regardless_range() and enemy_can_counter:
                    enemy._single_combat(self,False, False)
                    def_attacks = True
                # logs about preventing counters via sweep or prevent_counter

            if self.has_no_follow():
                pass
            # if attacker alive
            if self.stat_current["hp"] > 0:
                # attacker wary?
                if wary_passive:
                    if def_breaker_passive and enemy_can_counter and enemy_outspeed:
                        enemy._single_combat(self,False,False)
                    elif def_riposte_passive and enemy_outspeed:
                        enemy._single_combat(self,False, False)
                    else:
                        # no follow ups
                        pass
                # defender wary?
                elif def_wary_passive:
                    if breaker_passive and outspeed and can_follow_up:
                        self._single_combat(enemy, True, False)
                    elif brash_passive and outspeed and can_follow_up:
                        self._single_combat(enemy,True, False)
                    elif can_follow_up or def_riposte_passive:
                        # no follow ups
                        pass
                # breaker?
                elif breaker_passive and def_breaker_passive:
                    if outspeed and can_follow_up:
                        self._single_combat(enemy,True, False)
                    elif enemy_outspeed:
                        if enemy_can_counter:
                            enemy._single_combat(self,False,False)
                        elif can_follow_up:
                            pass
                    elif can_follow_up:
                        pass
                elif breaker_passive:
                    if def_riposte_passive and enemy_outspeed:
                        if can_follow_up:
                            self._single_combat(enemy, True, False)
                        if enemy.stat_current["hp"] > 0:
                            enemy._single_combat(self,False, False)
                    elif can_follow_up:
                        self._single_combat(enemy, True, False)
                elif def_breaker_passive:
                    brashact = False
                    if brash_passive and outspeed and can_follow_up:
                        self._single_combat(enemy, True, False)
                        brashact = True
                    if enemy_can_counter and enemy.stat_current["hp"] > 0:
                        if brashact or desperation:
                            enemy._single_combat(self, False, False)
                        else:
                            # it's different? yes?
                            enemy._single_combat(self, False, False)
                    elif can_follow_up and enemy.stat_current["hp"] > 0:
                        pass
                # regular follow ups
                else:
                    defend_follow = False
                    # vantage
                    if def_vantage_passive and enemy_outspeed:
                        enemy._single_combat(self, False, False)
                        defend_follow = True
                    # brash
                    if brash_passive and can_follow_up and self.stat_current["hp"] > 0:
                        self._single_combat(enemy, True, False)
                        can_follow_up = False

                    # regular follow up
                    if can_follow_up and outspeed and self.stat_current["hp"] > 0 and enemy.stat_current["hp"] > 0:
                        self._single_combat(enemy, True, False)
                    elif not defend_follow and enemy_outspeed and enemy_can_counter and self.stat_current["hp"] > 0 and enemy.stat_current["hp"] > 0:
                        enemy._single_combat(self, False, True)
                        defend_follow = True
                    # riposte
                    if def_riposte_passive and enemy.stat_current["hp"] > 0 and not defend_follow:
                        enemy._single_combat(self, False, False)

        after_heal = 0
        poison = 0
        def_poison = 0
        recoil = 0
        def_recoil = 0
        # after combat healing
        if self.stat_current["hp"] > 0:
            for holder in self.mod_holders():
                if holder.initiate_heal:
                    after_heal += holder.initiate_heal
        # poison
        if enemy.stat_current["hp"] > 0:
            for holder in self.mod_holders():
                if holder.poison:
                    poison += holder.poison
                if holder.initiate_poison:
                    poison += holder.initiate_poison
        if self.stat_current["hp"] > 0 and def_attacks:
            for holder in enemy.mod_holders():
                if holder.poison:
                    def_poison += holder.poison

        # recoil
        if self.stat_current["hp"] > 0:
            for holder in self.mod_holders():
                if holder.recoil_dmg:
                    recoil += holder.recoil_dmg
        if enemy.stat_current["hp"] > 0:
            for holder in enemy.mod_holders():
                if holder.recoil_dmg:
                    def_recoil += holder.recoil_dmg
        self._after_combat_effects(poison, recoil, after_heal)
        enemy._after_combat_effects(def_poison, def_recoil, 0)

        self.remove_all_temp_mods()
        enemy.remove_all_temp_mods()

    def assist_unit(self,ally):
        pass


def fight_to_death(attacker, defender):
    """

    :param attacker: Unit 
    :param defender: Unit
    :return: 
    """
    attacker.init_total_stats()
    defender.init_total_stats()

    rounds = 0
    while attacker.is_alive() and defender.is_alive() and rounds < 99:
        if verbose:
            print("===============")
        attacker.attack_unit(defender)
        if defender.is_alive():
            if verbose:
                print("===============")
            defender.attack_unit(attacker)
        rounds +=1
    if attacker.is_alive() and defender.is_alive():
        #print("Draws %s" % defender.name)
        return 0
    elif attacker.is_alive() and not defender.is_alive():
        #print("Wins against %s" % defender.name)
        return 1
    else:
        #print("Loses against %s" % defender.name)
        return -1


def print_round(attacker, defender):
    print("===========================")
    print("%s: %s/%s %s: %s/%s" % (attacker.name, attacker.stat_current["hp"], attacker.stat_total["hp"],
                                       defender.name, defender.stat_current["hp"], defender.stat_total["hp"]))
if __name__ == "__main__":
    timer = VCBenchmark()
    timer.start("TOTAL")

    attacker = Unit.max_from_base("Jeorge")
    defender = Unit.max_from_base("Setsuna")
    fight_to_death(attacker,defender)

    # attackers = [Unit.max_from_base(name) for name in unit_data if name != "Custom"]
    # defenders = [Unit.max_from_base(name) for name in unit_data if name != "Custom"]
    # record = {"defense":{"wins": 0,"loss": 0}, "attack": {"wins": 0, "loss": 0}}
    # stats = {u.name:{} for u in attackers}
    # count = 0
    # for attacker in attackers:
    #     print("Attacker: %s" % attacker.name)
    #     for (a_w, a_a, a_b, a_c, a_s) in attacker.permutations(ALL_WEAPONS, USEFUL_SKILLS):
    #         attacker.equipped_weapon = a_w
    #         attacker.equipped_passive_a = a_a
    #         attacker.equipped_passive_b = a_b
    #         attacker.equipped_passive_c = a_c
    #         attacker.equipped_passive_s = a_s
    #         attacker_encoding = attacker.encode_for_key()
    #         print(attacker_encoding)
    #         if attacker_encoding not in stats[attacker.name]:
    #             stats[attacker.name][attacker_encoding] = record.copy()
    #
    #         for defender in defenders:
    #             print("Defender: %s" % defender.name)
    #             # alot of permutations
    #             for (d_w,d_a,d_b,d_c,d_s) in defender.permutations(ALL_WEAPONS, USEFUL_SKILLS):
    #                 count += 1
    #                 #timer.start("one round")
    #                 defender.equipped_weapon = d_w
    #                 defender.equipped_passive_a = d_a
    #                 defender.equipped_passive_b = d_b
    #                 defender.equipped_passive_c = d_c
    #                 defender.equipped_passive_s = d_s
    #                 defender_encoding = defender.encode_for_key()
    #                 if defender_encoding not in stats[defender.name]:
    #                     stats[defender.name][defender_encoding] = record.copy()
    #                 outcome = fight_to_death(attacker,defender)
    #                 if outcome == 1:
    #                     stats[attacker.name][attacker_encoding]["attack"]["wins"] += 1
    #                     stats[defender.name][defender_encoding]["defense"]["loss"] += 1
    #                 elif outcome == -1:
    #                     stats[attacker.name][attacker_encoding]["attack"]["loss"] += 1
    #                     stats[defender.name][defender_encoding]["defense"]["wins"] += 1
    #                 #timer.stop("one round")
    #
    #             #pprint(stats)
    #             with open("fights.json","w") as f:
    #                 json.dump(stats,f)

            # stats = {"wins": [], "losses": [], "draws": []}
    # for defender in defenders:
    #     outcome = fight_to_death(attacker,defender)
    #     if outcome == 1:
    #         stats["wins"].append(defender.name)
    #     elif outcome == -1:
    #         stats["losses"].append(defender.name)
    #     else:
    #         stats["draws"].append(defender.name)
    #
    # print("wins: %s" % len(stats["wins"]))
    # print("draws: %s" % len(stats["draws"]))
    # print("losses: %s" % len(stats["losses"]))

    timer.stop("TOTAL")
    timer.PrintTimingAnalysis()