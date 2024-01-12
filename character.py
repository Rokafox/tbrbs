from effect import *
from equip import Equip, generate_equips_list, adventure_generate_random_equip_with_weight
import more_itertools as mit
import random


class Character:
    def __init__(self, name, lvl, exp=0, equip=None, image=None, running=False, logging=False, text_box=None, fineprint_mode="default"):
        if equip is None:
            equip = {} # {str Equip.type: Equip}
        if equip is not None and not isinstance(equip, dict):
            raise Exception("Equip must be a dict.")
        self.name = name
        self.lvl = lvl
        self.lvl_max = 1000
        self.exp = exp
        self.equip = equip
        self.image = [] if image is None else image # list of pygame.Surface
        self.initialize_stats()
        self.calculate_equip_effect()
        self.running = running
        self.logging = logging
        self.text_box = text_box
        self.fineprint_mode = fineprint_mode


    def set_up_featured_image(self):
        try:
            self.featured_image = self.image[0]
        except IndexError:
            if hasattr(self, "original_name"):
                print(f"Image not found: {self.original_name.lower()}")
            else:
                print(f"Image not found: {self.name.lower()}")
            self.featured_image = None

    def to_dict(self): # Will only save lvl, exp, equip
        return {
            "object": str(self.__class__),
            "name": self.name,
            "lvl": self.lvl,
            "exp": self.exp,
            "equip": [item.to_dict() for item in self.equip.values()]
        }

    def initialize_stats(self, resethp=True, resetally=True, resetenemy=True):
        self.maxhp = self.lvl * 100
        self.hp = self.lvl * 100 if resethp else self.hp
        self.atk = self.lvl * 5
        self.defense = self.lvl * 5
        self.spd = self.lvl * 5
        self.eva = 0.05
        self.acc = 0.95
        self.crit = 0.05
        self.critdmg = 2.00
        self.critdef = 0.00
        self.penetration = 0.05
        self.maxexp = self.calculate_maxexp()
        self.maxmp = self.lvl * 50
        self.mp = self.lvl * 50
        self.hpregen = 0.00
        self.mpregen = 0.00
        self.hpdrain = 0.00
        self.thorn = 0.00
        self.heal_efficiency = 1.00
        self.final_damage_taken_multipler = 1.00
        self.buffs = []
        self.debuffs = []
        self.ally = [] if resetally else self.ally
        self.enemy = [] if resetenemy else self.enemy
        self.party = [] if resetally and resetenemy else self.party
        self.enemyparty = [] if resetally and resetenemy else self.enemyparty
        self.calculate_equip_effect(resethp=resethp)
        self.eq_set = self.get_equipment_set()
        self.skill1_cooldown = 0
        self.skill2_cooldown = 0
        self.skill1_cooldown_max = 5 # default
        self.skill2_cooldown_max = 5
        self.damage_taken_this_turn = [] # list of tuples (damage, attacker), damage is int, attacker is Character object
        # useful for recording damage taken sequence for certain effects
        self.damage_taken_history = [] # list of self.damage_taken_this_turn
        self.healing_received_this_turn = [] # list of tuples (healing, healer), healing is int, healer is Character object
        self.healing_received_history = [] # list of self.healing_received_this_turn
        self.clear_others()

    def reset_stats(self, resethp=True, resetally=True, resetenemy=True):
        self.initialize_stats(resethp, resetally, resetenemy)


    def record_damage_taken(self): 
        self.damage_taken_history.append(self.damage_taken_this_turn)
        self.damage_taken_this_turn = []

    def record_healing_received(self):
        self.healing_received_history.append(self.healing_received_this_turn)
        self.healing_received_this_turn = []

    def get_num_of_turns_not_taken_damage(self) -> int:
        # get the last few records of self.damage_taken_history, if are empty, return the number of records
        count = 0
        for record in self.damage_taken_history[::-1]:
            if not record:
                count += 1
            else:
                for (damage, attacker) in record:
                    if damage > 0:
                        count += 1
                        break
                break
        return count
                
    def calculate_equip_effect(self, resethp=True):
        if self.equip:
            for item in self.equip.values():
                self.maxhp += item.maxhp_flat
                self.atk += item.atk_flat
                self.defense += item.def_flat
                self.spd += item.spd_flat

                self.maxhp *= 1 + item.maxhp_percent
                self.maxhp = int(self.maxhp)
                self.atk *= 1 + item.atk_percent
                self.defense *= 1 + item.def_percent
                self.spd *= 1 + item.spd

                self.maxhp += int(item.maxhp_extra)
                self.atk += item.atk_extra
                self.defense += item.def_extra
                self.spd += item.spd_extra

                self.eva += item.eva
                self.acc += item.acc
                self.crit += item.crit
                self.critdmg += item.critdmg
                self.critdef += item.critdef
                self.penetration += item.penetration
                self.heal_efficiency += item.heal_efficiency
            if resethp and self.hp < self.maxhp:
                self.hp = self.maxhp
            if self.hp > self.maxhp:
                self.hp = self.maxhp
            self.set_up_equipment_set_effects()
        return self.equip

    def clear_others(self):
        pass

    def update_skill_cooldown(self, skill):
        match skill:
            case 1:
                self.skill1_cooldown = self.skill1_cooldown_max
            case 2:
                self.skill2_cooldown = self.skill2_cooldown_max
            case _:
                raise Exception("Invalid skill number.")

    def normal_attack(self):
        self.attack()

    def skill1(self):
        # Warning: Following characters have their own skill1 function:
        # Ophelia
        if self.running and self.logging:
            self.text_box.append_html_text(f"{self.name} cast skill 1.\n")
        fine_print(f"{self.name} cast skill 1.", mode=self.fineprint_mode)
        if self.skill1_cooldown > 0:
            raise Exception
        damage_dealt = self.skill1_logic()
        self.update_skill_cooldown(1)
        return None # for now

    def skill2(self):
        # Warning: Following characters have their own skill2 function:
        # Pepper, Ophelia
        if self.running and self.logging:
            self.text_box.append_html_text(f"{self.name} cast skill 2.\n")
        fine_print(f"{self.name} cast skill 2.", mode=self.fineprint_mode)
        if self.skill2_cooldown > 0:
            raise Exception
        damage_dealt = self.skill2_logic()
        self.update_skill_cooldown(2)
        return None # for now
    
    def skill1_logic(self):
        pass

    def skill2_logic(self):
        pass

    def target_selection(self, keyword="Undefined", keyword2="Undefined", keyword3="Undefined", keyword4="Undefined", target_list=None):
        # main_character already have .ally and .enemy as list
        # Warning: .is_charmed() and .is_confused() only works for n_random_enemy and n_random_ally, implement this later if needed,
        # or consider confused and charmed character can only normal attack
        # This function is a generator
        # default : random choice of a single enemy
        if target_list is None:
            target_list = []

        if target_list:
            yield from target_list

        match (keyword, keyword2, keyword3, keyword4):
            case ("yourself", _, _, _):
                yield self

            case ("Undefined", _, _, _):
                if self.is_charmed():
                    yield random.choice(self.ally)
                elif self.is_confused():
                    yield random.choice(self.enemy + self.ally)
                else:
                    yield random.choice(self.enemy)

            case ("n_random_enemy", n, _, _):
                n = int(n)
                if n > len(self.enemy):
                    n = len(self.enemy)
                if self.is_charmed():
                    yield from random.sample(self.ally, n)
                elif self.is_confused():
                    yield from random.sample(self.enemy + self.ally, n)
                else:
                    yield from random.sample(self.enemy, n)

            case ("n_random_ally", n, _, _):
                n = int(n)
                if n > len(self.ally):
                    n = len(self.ally)
                if self.is_charmed():
                    yield from random.sample(self.enemy, n)
                elif self.is_confused():
                    yield from random.sample(self.enemy + self.ally, n)
                else:
                    yield from random.sample(self.ally, n)

            case ("n_random_target", n, _, _):
                n = int(n)
                if n > len(self.ally) + len(self.enemy):
                    n = len(self.ally) + len(self.enemy)
                yield from random.sample(self.ally + self.enemy, n)

            case ("n_lowest_attr", n, attr, party):
                n = int(n)
                if party == "ally":
                    yield from sorted(self.ally, key=lambda x: getattr(x, attr))[:n]
                elif party == "enemy":
                    yield from sorted(self.enemy, key=lambda x: getattr(x, attr))[:n]

            case ("n_highest_attr", n, attr, party):
                n = int(n)
                if party == "ally":
                    yield from sorted(self.ally, key=lambda x: getattr(x, attr), reverse=True)[:n]
                elif party == "enemy":
                    yield from sorted(self.enemy, key=lambda x: getattr(x, attr), reverse=True)[:n]

            case ("n_enemy_with_effect", n, effect_name, _):
                n = int(n)
                list = mit.take(n, filter(lambda x: x.has_effect_that_named(effect_name), self.enemy))
                if len(list) < n:
                    list += random.sample(self.enemy, n - len(list))
                yield from list

            case ("n_ally_with_effect", n, effect_name, _):
                n = int(n)
                list = mit.take(n, filter(lambda x: x.has_effect_that_named(effect_name), self.ally))
                if len(list) < n:
                    list += random.sample(self.ally, n - len(list))
                yield from list

            case ("enemy_in_front", _, _, _):
                # get the self position at self.party, then get the enemy at the same position at self.enemyparty
                # if target.is_dead(), try index +- 1, +- 2, until a .is_alive target is found before self.enemyparty is exhausted
                # get the self position at self.party
                if len(self.enemy) == 1:
                    yield from self.enemy
                self_pos = 0
                for i, char in enumerate(self.party):
                    if char == self:
                        self_pos = i
                        break
                # get the enemy at the same position at self.enemyparty
                target = self.enemyparty[self_pos]
                if target.is_dead():
                    max_offset = min(self_pos, len(self.enemyparty) - self_pos - 1)
                    for offset in range(1, max_offset + 1):
                        if not self.enemyparty[self_pos + offset].is_dead():
                            target = self.enemyparty[self_pos + offset]
                            break
                        elif not self.enemyparty[self_pos - offset].is_dead():
                            target = self.enemyparty[self_pos - offset]
                            break
                yield target

            case ("n_enemy_in_front", n, _, _):
                n = int(n)
                if len(self.enemy) <= n:
                    yield from self.enemy
                else:
                    self_pos = 0
                    for i, char in enumerate(self.party):
                        if char == self:
                            self_pos = i
                            break
                    # get the enemy at the same position and closest at self.enemyparty until n is reached
                    target = self.enemyparty[self_pos]
                    list_to_yield = []
                    if not target.is_dead():
                        list_to_yield.append(target)
                    max_offset = min(self_pos, len(self.enemyparty) - self_pos - 1)
                    for offset in range(1, max_offset + 1):
                        if len(list_to_yield) == n:
                            break
                        if not self.enemyparty[self_pos + offset].is_dead():
                            list_to_yield.append(self.enemyparty[self_pos + offset])
                        if len(list_to_yield) == n:
                            break
                        if not self.enemyparty[self_pos - offset].is_dead():
                            list_to_yield.append(self.enemyparty[self_pos - offset])
                    yield from list_to_yield


            case ("n_lowest_hp_percentage_ally", n, _, _):
                n = int(n)
                yield from sorted(self.ally, key=lambda x: x.hp/x.maxhp)[:n]

            case ("n_lowest_hp_percentage_enemy", n, _, _):
                n = int(n)
                yield from sorted(self.enemy, key=lambda x: x.hp/x.maxhp)[:n]

            case ("n_dead_allies", n, _, _):
                n = int(n)
                yield from mit.take(n, filter(lambda x: x.is_dead(), self.party))

            case ("n_dead_enemies", n, _, _):
                n = int(n)
                yield from mit.take(n, filter(lambda x: x.is_dead(), self.enemyparty))

            case ("random_enemy_pair", _, _, _):
                if len(self.enemy) < 2:
                    yield from self.enemy
                else:
                    yield from random.choice(list(mit.pairwise(self.enemy)))

            case ("random_ally_pair", _, _, _):
                if len(self.ally) < 2:
                    yield from self.ally
                else:
                    yield from random.choice(list(mit.pairwise(self.ally)))

            case ("random_enemy_triple", _, _, _):
                if len(self.enemy) < 3:
                    yield from self.enemy
                else:
                    yield from random.choice(list(mit.triplewise(self.enemy)))

            case ("random_ally_triple", _, _, _):
                if len(self.ally) < 3:
                    yield from self.ally
                else:
                    yield from random.choice(list(mit.triplewise(self.ally)))

            case (_, _, _, _):
                raise Exception("Keyword not found.")


    def attack(self, target_kw1="Undefined", target_kw2="Undefined", 
               target_kw3="Undefined", target_kw4="Undefined", multiplier=2, repeat=1, func_after_dmg=None,
               func_damage_step=None, repeat_seq=1, func_after_miss=None, func_after_crit=None,
               always_crit=False, additional_attack_after_dmg=None, always_hit=False, target_list=None) -> int:
        # Warning: DO NOT MESS WITH repeat and repeat_seq TOGETHER, otherwise the result will be confusing
        # -> damage dealt
        global running, text_box
        damage_dealt = 0
        for i in range(repeat):
            if repeat > 1:
                self.update_ally_and_enemy()
            try:
                attack_sequence = list(self.target_selection(target_kw1, target_kw2, target_kw3, target_kw4, target_list))
            except Exception as e:
                break
            if repeat_seq > 1:
                attack_sequence = list(mit.repeat_each(attack_sequence, repeat_seq))
            for target in attack_sequence:
                if target.is_dead():
                    continue
                if self.is_dead():
                    break
                if self.running and self.logging:
                    self.text_box.append_html_text(f"{self.name} is targeting {target.name}.\n")
                fine_print(f"{self.name} is targeting {target.name}.", mode=self.fineprint_mode)
                damage = self.atk * multiplier - target.defense * (1 - self.penetration)
                final_accuracy = self.acc - target.eva
                dice = random.randint(1, 100)
                miss = False if dice <= final_accuracy * 100 else True
                if not miss or always_hit:
                    dice = random.randint(1, 100)
                    critical = True if dice <= self.crit * 100 else False
                    critical = True if always_crit else critical
                    if critical:
                        final_damage = damage * (self.critdmg - target.critdef)
                        if self.running and self.logging:
                            self.text_box.append_html_text("Critical!\n")
                        fine_print("Critical!", mode=self.fineprint_mode)
                        if func_after_crit is not None: # Warning: this function may be called multiple times
                            final_damage, always_crit = func_after_crit(self, target, final_damage, always_crit)
                    else:
                        final_damage = damage
                    final_damage *= random.uniform(0.8, 1.2)
                    if func_damage_step is not None:
                        final_damage = func_damage_step(self, target, final_damage)
                    if final_damage < 0:
                        final_damage = 0
                    target.take_damage(final_damage, self)
                    damage_dealt += final_damage
                    if func_after_dmg is not None and self.is_alive():
                        func_after_dmg(self, target)
                    if additional_attack_after_dmg is not None:
                        damage_dealt += additional_attack_after_dmg(self, target, is_crit=critical)
                else:
                    if self.running and self.logging:
                        self.text_box.append_html_text(f"Missed! {self.name} attacked {target.name} but missed.\n")
                    fine_print(f"Missed! {self.name} attacked {target.name} but missed.", mode=self.fineprint_mode)

        return damage_dealt


    # Action logic
    def action(self):
        can_act, reason = self.can_take_action()
        if can_act:
            self.update_cooldown()
            if self.skill1_cooldown == 0 and not self.is_silenced():
                self.skill1()
            elif self.skill2_cooldown == 0 and not self.is_silenced():
                self.skill2()
            else:
                self.normal_attack()
        else:
            if self.running and self.logging:
                self.text_box.append_html_text(f"{self.name} cannot act due to {reason}.\n")
            fine_print(f"{self.name} cannot act due to {reason}.", mode=self.fineprint_mode)
        # Snowflake set effect
        set_name = self.get_equipment_set()
        if set_name == "Snowflake":
            for buff in self.buffs:
                if buff.name == "Snowflake Set":
                    buff.apply_effect_custom()

    # Print the character's stats
    def __str__(self):
        return "{:<20s} MaxHP: {:>5d} HP: {:>5d} ATK: {:>7.2f} DEF: {:>7.2f} Speed: {:>7.2f}".format(self.name, self.maxhp, self.hp, self.atk, self.defense, self.spd)

    def tooltip_string(self):
        level = self.lvl if self.lvl < self.lvl_max else "MAX"
        return f"{self.name}\n" \
            f"level: {level}\n" \
            f"hp: {self.hp}/{self.maxhp}\n" \
            f"atk: {self.atk}\n" \
            f"def: {self.defense}\n" \
            f"speed: {self.spd}\n" \
            f"eva: {self.eva*100:.2f}%\n" \
            f"acc: {self.acc*100:.2f}%\n" \
            f"crit: {self.crit*100:.2f}%\n" \
            f"critdmg: {self.critdmg*100:.2f}%\n" \
            f"critdef: {self.critdef*100:.2f}%\n" \
            f"penetration: {self.penetration*100:.2f}%\n" \
            f"heal efficiency: {self.heal_efficiency*100:.2f}%\n" \
            f"final damage taken: {self.final_damage_taken_multipler*100:.2f}%\n" \
            f"exp/maxexp/perc: {self.exp}/{self.maxexp}/{self.exp/self.maxexp*100:.2f}%\n" \

    def tooltip_status_effects(self):
        str = "Status Effects:\n"
        str += "=" * 20 + "\n"
        for effect in self.buffs:
            if not effect.is_set_effect:
                str += effect.print_stats_html()
                str += "\n"
        str += "=" * 20 + "\n"
        for effect in self.debuffs:
            if not effect.is_set_effect:
                str += effect.print_stats_html()
                str += "\n"
        return str

    def calculate_maxexp(self):
        base_exp = 10  
        for i in range(2, self.lvl + 1):
            base_exp += i + 7  
        return base_exp

    def gain_exp(self, gained_exp):
        if not isinstance(gained_exp, int) or gained_exp <= 0:
            raise ValueError("Experience gained must be a positive integer")

        self.exp += gained_exp

        while self.exp >= self.maxexp:
            self.level_up_on_max_exp()

    def level_up_on_max_exp(self):
        while self.exp >= self.maxexp:
            self.exp -= self.maxexp  # Deduct the max exp for the level up
            self.level_change(1)
            
            if self.running and self.logging:
                self.text_box.append_html_text(f"{self.name} leveled up!\n")
            fine_print(f"{self.name} leveled up!", mode=self.fineprint_mode)

    def reset_stats_and_reapply_effects(self, reset_hp=True):
        buff_copy = [effect for effect in self.buffs if not effect.is_set_effect]
        debuff_copy = [effect for effect in self.debuffs if not effect.is_set_effect]
        self.reset_stats(resethp=reset_hp, resetally=False, resetenemy=False) # We are probably doing this during battle
        for effect in buff_copy:
            self.apply_effect(effect)
        for effect in debuff_copy:
            self.apply_effect(effect)

    def level_change(self, increment):
        if increment > 0:
            if self.lvl >= self.lvl_max:
                return
        elif increment < 0:
            if self.lvl <= 1:
                return
        
        self.lvl += increment
        self.reset_stats_and_reapply_effects()
        self.maxexp = self.calculate_maxexp()

    def equip_item(self, item: Equip):
        old_item = self.equip.pop(item.type, None)
        self.equip[item.type] = item
        self.reset_stats_and_reapply_effects(False)
        return old_item

    def equip_item_from_list(self, item_list: list):
        # the items in item_list must not exist more than once of the same item.type
        item_type_seen = []
        for item in item_list:
            if item.type in item_type_seen:
                raise Exception("Cannot equip more than one of the same item type.")
            item_type_seen.append(item.type)

        old_item_list = []
        for item in item_list:
            old_item = self.equip.pop(item.type, None)
            self.equip[item.type] = item
            old_item_list.append(old_item)
        self.reset_stats_and_reapply_effects(False)
        return old_item_list

    def unequip_item(self, item_type: str, strict):
        if strict and item_type not in self.equip:
            raise ValueError(f"No {item_type} equipped")
        
        unequipped_item = self.equip.pop(item_type, None)
        self.reset_stats_and_reapply_effects(False)
        return unequipped_item

    def is_alive(self):
        return self.hp > 0

    def is_dead(self):
        return self.hp <= 0

    def is_charmed(self):
        return self.has_effect_that_named("Charm")
    
    def is_confused(self):
        return self.has_effect_that_named("Confuse")
    
    def is_stunned(self):
        return self.has_effect_that_named("Stun")
    
    def is_silenced(self):
        return self.has_effect_that_named("Silence")
    
    def is_sleeping(self):
        return self.has_effect_that_named("Sleep")
    
    def is_frozed(self):
        return self.has_effect_that_named("Frozen")
    
    def can_take_action(self) -> (bool, str):
        if self.is_stunned():
            return False, "Stunned"
        if self.is_sleeping():
            return False, "Sleeping"
        if self.is_frozed():
            return False, "Frozen"
        return True, "None"
    
    def update_ally_and_enemy(self):
        self.ally = [ally for ally in self.ally if not ally.is_dead()]
        self.enemy = [enemy for enemy in self.enemy if not enemy.is_dead()]
        
    def has_ally(self, ally_name):
        return ally_name in [ally.name for ally in self.ally]
    
    def has_enemy(self, enemy_name):
        return enemy_name in [enemy.name for enemy in self.enemy]

    def get_neighbors(self, party, char, include_self=True, distance=1) -> list:
        neighbors = []
        for is_adj, item in mit.adjacent(lambda x: x == char, party, distance):
            if is_adj and item != char:
                neighbors.append(item)
            elif is_adj and item == char and include_self:
                neighbors.append(item)
        return neighbors

    def get_neighbor_allies_including_self(self, get_from_self_ally=True):
        # get_from_self_ally: check adjacent allies, if a neighbor is fallen, continue to check the next one until a valid ally is found
        return self.get_neighbors(self.ally, self) if get_from_self_ally else self.get_neighbors(self.party, self)

    def get_neighbor_allies_not_including_self(self, get_from_self_ally=True):
        return self.get_neighbors(self.ally, self, False) if get_from_self_ally else self.get_neighbors(self.party, self, False)

    def has_neighbor(self, character_name, get_from_self_ally=True):
        neighbors = self.get_neighbor_allies_not_including_self(get_from_self_ally)
        for n in neighbors:
            if n.name == character_name:
                return True
        return False
    
    def is_only_one_alive(self):
        return len(self.ally) == 1

    def update_stats(self, stats, reversed=False) -> (dict, dict, dict):
        prev = {}
        new = {}
        delta = {}
        for attr, value in stats.items():
            if attr in ["maxhp", "hp", "atk", "defense", "spd"]:
                if reversed:
                    new_value = getattr(self, attr) / value
                else:
                    new_value = getattr(self, attr) * value
                if attr == "maxhp" or attr == "hp":
                    new_value = int(new_value)
                if attr == "hp":
                    new_value = min(new_value, self.maxhp)
                elif attr == "maxhp":
                    self.hp = min(self.hp, new_value)
                if new_value <= 0:
                    raise Exception("Cannot multiply stats by 0 or below. Does not make sense.") 
            else:
                if reversed:
                    new_value = getattr(self, attr) - value
                else:
                    new_value = getattr(self, attr) + value
            prev[attr] = getattr(self, attr)
            setattr(self, attr, new_value)
            new[attr] = new_value
            delta[attr] = new_value - prev[attr]
        return prev, new, delta

    def heal_hp(self, value, healer):
        if self.is_dead():
            raise Exception("Cannot heal a dead character.")
        if value < 0:
            value = 0
        healing = value * self.heal_efficiency
        healing = int(healing)
        overhealing = 0
        if self.hp + healing > self.maxhp:
            overhealing = self.hp + healing - self.maxhp
            healing = self.maxhp - self.hp
        self.hp += healing
        if self.running and self.logging:
            self.text_box.append_html_text(f"{self.name} is healed for {healing} HP.\n")
        fine_print(f"{self.name} is healed for {healing} HP.", mode=self.fineprint_mode)
        self.healing_received_this_turn.append((healing, healer))
        return healing, healer, overhealing

    def revive(self, hp_to_revive, hp_percentage_to_revive=0):
        if self.is_dead():
            self.hp = hp_to_revive
            self.hp += self.maxhp * hp_percentage_to_revive
            self.hp = int(self.hp)
            self.healing_received_this_turn.append((self.hp, self))
            if self.running and self.logging:
                self.text_box.append_html_text(f"{self.name} is revived for {self.hp} hp.\n")
            fine_print(f"{self.name} is revived for {self.hp} hp.", mode=self.fineprint_mode)
        else:
            raise Exception(f"{self.name} is not dead. Cannot revive.")
    
    # Not used for now
    def regen(self):
        if self.is_dead():
            raise Exception
        healing = int(self.maxhp * self.hpregen)
        overhealing = 0
        if self.hp + healing > self.maxhp:
            overhealing = self.hp + healing - self.maxhp
            healing = self.maxhp - self.hp
        self.hp += healing
        self.healing_received_this_turn.append((healing, self))
        if healing > 0:
            if self.running and self.logging:
                self.text_box.append_html_text(f"{self.name} is healed for {healing} HP.\n")
            fine_print(f"{self.name} is regenerated for {healing} HP.", mode=self.fineprint_mode)
        return healing, self, overhealing

    def take_damage(self, value, attacker=None, func_after_dmg=None):
        if self.running and self.logging:
            self.text_box.append_html_text(f"{self.name} is about to take {value} damage.\n")
        fine_print(f"{self.name} is about to take {value} damage.", mode=self.fineprint_mode)
        if self.is_dead():
            fine_print(f"{self.name} is already dead, cannot take damage.", mode=self.fineprint_mode)
            raise Exception
        value = max(0, value)
        # Attention: final_damage_taken_multipler is calculated before shields effects.
        damage = value * self.final_damage_taken_multipler

        if damage > 0:
            copyed_buffs = self.buffs.copy() # Some effect will try apply other effects during this step, see comments on Effect class for details.
            copyed_debuffs = self.debuffs.copy()
            for effect in copyed_buffs:
                if hasattr(effect, "is_protected_effect") and effect.is_protected_effect:
                    damage = effect.protected_apply_effect_during_damage_step(self, damage, attacker, func_after_dmg)
                else:
                    damage = effect.apply_effect_during_damage_step(self, damage, attacker)
            for effect in copyed_debuffs:
                damage = effect.apply_effect_during_damage_step(self, damage, attacker)
                
        damage = int(damage)
        damage = max(0, damage)
        if self.hp - damage < 0:
            damage = self.hp
        self.hp -= damage
        if func_after_dmg is not None:
            func_after_dmg(self, damage, attacker)
        self.take_damage_aftermath(damage, attacker)

        copyed_buffs = self.buffs.copy() 
        copyed_debuffs = self.debuffs.copy()
        for effect in copyed_buffs:
            effect.apply_effect_after_damage_step(self, damage, attacker)
        for effect in copyed_debuffs:
            effect.apply_effect_after_damage_step(self, damage, attacker)

        if self.running and self.logging:
            self.text_box.append_html_text(f"{self.name} took {damage} damage.\n")
        fine_print(f"{self.name} took {damage} damage.", mode=self.fineprint_mode)
        self.damage_taken_this_turn.append((damage, attacker))
        return None
    
    def take_damage_aftermath(self, damage, attacker):
        pass

    def take_status_damage(self, value, attacker=None):
        if self.running and self.logging:
            self.text_box.append_html_text(f"{self.name} is about to take {value} status damage.\n")
        fine_print(f"{self.name} is about to take {value} status damage.", mode=self.fineprint_mode)
        if self.is_dead():
            return 0, attacker
        value = max(0, value)
        damage = value * self.final_damage_taken_multipler
        if damage > 0:
            copyed_buffs = self.buffs.copy() 
            copyed_debuffs = self.debuffs.copy()
            for effect in copyed_buffs:
                damage = effect.apply_effect_during_damage_step(self, damage, attacker)
            for effect in copyed_debuffs:
                damage = effect.apply_effect_during_damage_step(self, damage, attacker)
        damage = int(damage)
        damage = max(0, damage)
        if self.hp - damage < 0:
            damage = self.hp
        self.hp -= damage
        if self.running and self.logging:
            self.text_box.append_html_text(f"{self.name} took {damage} status damage.\n")
        fine_print(f"{self.name} took {damage} status damage.", mode=self.fineprint_mode)
        self.damage_taken_this_turn.append((damage, attacker))
        return None

    def take_bypass_status_effect_damage(self, value, attacker=None):
        if self.running and self.logging:
            self.text_box.append_html_text(f"{self.name} is about to take {value} bypass status effect damage.\n")
        fine_print(f"{self.name} is about to take {value} bypass status effect damage.", mode=self.fineprint_mode)
        if self.is_dead():
            raise Exception("Cannot take damage when dead.")
        value = max(0, value)
        damage = value
        damage = int(damage)
        if self.hp - damage < 0:
            damage = self.hp
        if damage < 0:
            raise Exception("damage cannot be negative.")
        self.hp -= damage
        if self.running and self.logging:
            self.text_box.append_html_text(f"{self.name} took {damage} bypass status effect damage.\n")
        fine_print(f"{self.name} took {damage} bypass status effect damage.", mode=self.fineprint_mode)
        self.damage_taken_this_turn.append((damage, attacker))
        return None

    def has_effect_that_named(self, effect_name: str, additional_name: str=None):
        for effect in self.buffs:
            if effect.name == effect_name:
                if additional_name:
                    if hasattr(effect, "additional_name") and effect.additional_name == additional_name:
                        return True
                else:
                    return True
        for effect in self.debuffs:
            if effect.name == effect_name:
                if additional_name:
                    if hasattr(effect, "additional_name") and effect.additional_name == additional_name:
                        return True
                else:
                    return True
        return False

    def is_immune_to_cc(self):
        for effect in self.buffs:
            if effect.cc_immunity:
                return True
        for effect in self.debuffs: # Debuff that provide CC immunity? Make no sense.
            if effect.cc_immunity:
                print(f"Warning: {self.name} has debuff that provide CC immunity. Effect name: {effect.name}")
                return True
        return False

    def apply_effect(self, effect):
        # For effects that can stack, reflesh the duration
        if effect.apply_rule == "stack" and self.is_alive():
            for e in self.debuffs + self.buffs:
                if e.name == effect.name:
                    e.duration = effect.duration
                    e.apply_effect_when_adding_stacks(self, effect.stacks)
                    if self.running and self.logging:
                        self.text_box.append_html_text(f"{effect.name} duration on {self.name} has been refreshed.\n")
                    fine_print(f"{effect.name} duration on {self.name} has been refreshed.", mode=self.fineprint_mode)
                    return
        if self.is_alive() and effect.is_buff:
            self.buffs.append(effect)
            self.buffs.sort(key=lambda x: x.sort_priority)
        elif self.is_alive() and not effect.is_buff:
            # deal with cc effect
            if self.is_immune_to_cc() and effect.is_cc_effect:
                if self.running and self.logging:
                    self.text_box.append_html_text(f"{self.name} is immune to {effect.name}.\n")
                fine_print(f"{self.name} is immune to {effect.name}.", mode=self.fineprint_mode)
                return
            self.debuffs.append(effect)
            self.debuffs.sort(key=lambda x: x.sort_priority)
        if self.running and self.logging:
            self.text_box.append_html_text(f"{effect.name} has been applied on {self.name}.\n")
        fine_print(f"{effect.name} has been applied on {self.name}.", mode=self.fineprint_mode)
        effect.apply_effect_on_apply(self)

    def remove_effect(self, effect: Effect, purge=False, strict=False):
        # purge: effect is removed without triggering apply_effect_on_remove
        # Attention: Character Ophelia does not use this function, but directly temper with self.buffs and self.debuffs
        if effect in self.buffs:
            self.buffs.remove(effect)
        elif effect in self.debuffs:
            self.debuffs.remove(effect)
        else:
            raise Exception("Effect not found.") if strict else None
        if self.running and self.logging:
            self.text_box.append_html_text(f"{effect.name} on {self.name} has been removed.\n")
        fine_print(f"{effect.name} on {self.name} has been removed.", mode=self.fineprint_mode)
        if not purge:
            effect.apply_effect_on_remove(self)

    def try_remove_effect_with_name(self, effect_name: str, strict=False) -> bool:
        # used for add_cheat_effect() in bs
        for effect in self.buffs + self.debuffs:
            if effect.name == effect_name:
                self.remove_effect(effect)
                return True
        if strict:
            raise Exception("Effect with name not found.")
        return False

    # Get shield value, all shield effect must have shield_value attribute.
    def get_shield_value(self) -> int:
        total = 0
        for effect in self.buffs + self.debuffs:
            if hasattr(effect, "shield_value"):
                total += effect.shield_value
        return total

    def remove_all_effects(self):
        # Not used
        pass

    def remove_random_amount_of_debuffs(self, amount) -> list:
        # -> list of removed effects
        if amount > len(self.debuffs):
            amount = len(self.debuffs)
        if amount == 0:
            return []
        removed_effects = []
        for i in range(amount):
            effect = random.choice(self.debuffs)
            self.remove_effect(effect)
            removed_effects.append(effect)
        return removed_effects

    # Every turn, decrease the duration of all buffs and debuffs by 1. If the duration is 0, remove the effect.
    # And other things.
    def status_effects_start_of_turn(self):
        # Currently, effects are not removed and continue to receive updates even if character is dead. 
        # If we want to do this, remember: Reborn effect should not be removed.
        for effect in self.buffs + self.debuffs:
            if effect.flag_for_remove:
                if self.running and self.logging:
                    self.text_box.append_html_text(f"Condition no longer met: {effect.name} on {self.name}.\n")
                fine_print(f"Condition no longer met: {effect.name} on {self.name}.", mode=self.fineprint_mode)
                self.remove_effect(effect)
                continue
            if effect.duration == -1:
                # if self.running and self.logging:
                #     self.text_box.append_html_text(f"{effect.name} on {self.name} is active.\n")
                # print(f"{effect.name} on {self.name} is active.")
                continue
            effect.decrease_duration()
            if effect.duration > 0:
                if self.running and self.logging:
                    self.text_box.append_html_text(f"{effect.name} on {self.name} has {effect.duration} turns left.\n")
                fine_print(f"{effect.name} on {self.name} has {effect.duration} turns left.", mode=self.fineprint_mode)
                continue
            if effect.is_expired():
                if self.running and self.logging:
                    self.text_box.append_html_text(f"{effect.name} on {self.name} has expired.\n")
                fine_print(f"{effect.name} on {self.name} has expired.", mode=self.fineprint_mode)
                self.remove_effect(effect)
                effect.apply_effect_on_expire(self)
    
    # Every turn, calculate apply_effect_on_turn effect of all buffs and debuffs. ie. poison, burn, etc.
    def status_effects_midturn(self):
        buffs_copy = self.buffs.copy()
        debuffs_copy = self.debuffs.copy()
        for effect in buffs_copy + debuffs_copy:
            effect.apply_effect_on_turn(self)

    def status_effects_at_end_of_turn(self):
        buffs_copy = self.buffs.copy()
        debuffs_copy = self.debuffs.copy()
        for effect in buffs_copy + debuffs_copy:
            effect.apply_effect_at_end_of_turn(self)

    def update_cooldown(self):
        if self.skill1_cooldown > 0:
            self.skill1_cooldown -= 1
        if self.skill2_cooldown > 0:
            self.skill2_cooldown -= 1

    def skill_tooltip(self):
        return ""

    def get_equipment_set(self):
        if not self.equip or len(self.equip) != 4:
            return "None"

        sets = {item.eq_set for item in self.equip.values()}
        return sets.pop() if len(sets) == 1 else "None"

    def set_up_equipment_set_effects(self):
        # This function is called at the start of the battle. We expect item set effect
        # is just some status effect. just do self.apply_effect(some_effect), the effect have -1 duration.
        set_name = self.get_equipment_set()
        for effects in self.buffs + self.debuffs:
            if effects.is_set_effect:
                self.remove_effect(effects)
        if set_name == "None":
            return
        elif set_name == "Arasaka": 
            self.apply_effect(EquipmentSetEffect_Arasaka("Arasaka Set", -1, True, False, running=self.running, logging=self.logging, text_box=self.text_box))
        elif set_name == "KangTao":
            self.apply_effect(EquipmentSetEffect_KangTao("KangTao Set", -1, True, self.atk * 6, False, running=self.running, logging=self.logging, text_box=self.text_box))
        elif set_name == "Militech":
            def condition_func(self):
                return self.hp <= self.maxhp * 0.25
            self.apply_effect(EquipmentSetEffect_Militech("Militech Set", -1, True, {"spd": 2.0}, condition_func))
        elif set_name == "NUSA":
            def stats_dict_function() -> dict:
                allies_alive = len(self.ally) 
                return {"atk": 0.06 * allies_alive + 1 , "defense": 0.06 * allies_alive + 1, "maxhp": 0.06 * allies_alive + 1}
            self.apply_effect(EquipmentSetEffect_NUSA("NUSA Set", -1, True, {"atk": 1.30, "defense": 1.30, "maxhp": 1.30}, stats_dict_function))
        elif set_name == "Sovereign":
            self.apply_effect(EquipmentSetEffect_Sovereign("Sovereign Set", -1, True, {"atk": 1.20}))
        elif set_name == "Snowflake":
            self.apply_effect(EquipmentSetEffect_Snowflake("Snowflake Set", -1, True))
        else:
            raise Exception("Effect not implemented.")
        
    def equipment_set_effects_tooltip(self):
        set_name = self.get_equipment_set()
        str = "Equipment Set Effects:\n"
        if set_name == "None":
            str += "Equipment set effects is not active. Equip 4 items of the same set to receive benefits.\n"
            return ""
        elif set_name == "Arasaka":
            str += "Arasaka\n" \
                "Once per battle, leave with 1 hp when taking fatal damage, when triggered, gain immunity to damage for 3 turns.\n"
        elif set_name == "KangTao":
            str += "Kang Tao\n" \
                "At start of battle, apply absorption shield on self. Shield value is 600% of atk.\n"
        elif set_name == "Militech":
            str += "Militech\n" \
                "Increase speed by 100% when hp falls below 25%.\n"
        elif set_name == "NUSA":
            str += "NUSA\n" \
                "Increase atk by 6%, def by 6%, and maxhp by 6% for each ally alive including self.\n"
        elif set_name == "Sovereign":
            str += "Sovereign\n" \
                "Apply Sovereign effect when taking damage, Sovereign increases atk by 20% and last 4 turns. Max 5 active effects.\n"
        elif set_name == "Snowflake":
            str += "Snowflake\n" \
                "Gain 1 piece of Snowflake at the end of action. When 6 pieces are accumulated, heal 25% hp and gain the following effect for 6 turns:\n" \
                "atk, def, maxhp, spd are increased by 25%.\n" \
                "Each activation of this effect increases the stats bonus and healing by 25%.\n"
        else:
            str += "Unknown set effect."

        str += "=" * 20 + "\n"
        for effect in self.buffs:
            if effect.is_set_effect:
                str += effect.print_stats_html()
                str += "\n"
        str += "=" * 20 + "\n"
        for effect in self.debuffs:
            if effect.is_set_effect:
                str += effect.print_stats_html()
                str += "\n"
        return str

    def fake_dice(self, sides=6, weights=None):
        sides_list = [i for i in range(1, sides+1)]
        if weights is None:
            weights = [100 for i in range(sides)]
        result = random.choices(sides_list, weights=weights, k=1)[0]
        if self.running and self.logging:
            self.text_box.append_html_text(f"{self.name} rolled {result} on a dice.\n")
        fine_print(f"{self.name} rolled {result} on a dice.", mode=self.fineprint_mode)
        return result

    def battle_entry_effects(self):
        # Plan: handles passive status effects applied when entering battle here.
        pass



class Lillia(Character):
    def __init__(self, name, lvl, exp=0, equip=None, image=None):
        super().__init__(name, lvl, exp, equip, image)
        self.name = "Lillia"
        self.skill1_description = "12 hits on random enemies, 180% atk each hit. After 1 critical hit, all hits following will be critical and hit nearby targets for 30% of damage as status damage."
        self.skill2_description = "For 8 turns, cast Infinite Oasis on self gain immunity to CC and reduce damage taken by 35%."
        self.skill3_description = "Heal 8% of max hp on action when Infinite Oasis is active."
        self.skill1_cooldown_max = 5
        self.skill2_cooldown_max = 5

    def skill_tooltip(self):
        return f"Skill 1 : {self.skill1_description}\nCooldown : {self.skill1_cooldown} action(s)\n\nSkill 2 : {self.skill2_description}\nCooldown : {self.skill2_cooldown} action(s)\n\nSkill 3 : {self.skill3_description}\n"

    def skill1_logic(self):
        def lillia_effect(self, target, final_damage, always_crit):
            always_crit = True
            for target in target.get_neighbor_allies_not_including_self():
                if target.is_alive():
                    target.take_status_damage(final_damage * 0.3 * random.uniform(0.8, 1.2), self)
            return final_damage, always_crit
        damage_dealt = self.attack(multiplier=1.8, repeat=12, func_after_crit=lillia_effect)
        return damage_dealt

    def skill2_logic(self):
        self.apply_effect(ReductionShield("Infinite Oasis", 8, True, 0.35, cc_immunity=True))
        return None

    def skill3(self):
        if self.has_effect_that_named("Infinite Oasis"):
            self.heal_hp(self.maxhp * 0.08, self)

    def action(self):
        self.skill3()
        super().action()


class Poppy(Character):
    def __init__(self, name, lvl, exp=0, equip=None, image=None):
        super().__init__(name, lvl, exp, equip, image)
        self.name = "Poppy"
        self.skill1_description = "8 hits on random enemies, 280% atk each hit."
        self.skill2_description = "610% atk on random enemy. Target speed is decreased by 30% for 6 turns."
        self.skill3_description = "On taking normal attack or skill damage, 30% chance to inflict 50% atk continuous damage to attacker for 3 turns."
        self.skill1_cooldown_max = 5
        self.skill2_cooldown_max = 5

    def skill_tooltip(self):
        return f"Skill 1 : {self.skill1_description}\nCooldown : {self.skill1_cooldown} action(s)\n\nSkill 2 : {self.skill2_description}\nCooldown : {self.skill2_cooldown} action(s)\n\nSkill 3 : {self.skill3_description}\n"

    def skill1_logic(self):
        damage_dealt = self.attack(multiplier=2.8, repeat=8)      
        return damage_dealt

    def skill2_logic(self):
        def decrease_speed(self, target):
            stat_dict = {"spd": 0.7}
            target.apply_effect(StatsEffect("Purchased!", 6, False, stat_dict))
        damage_dealt = self.attack(multiplier=6.1, repeat=1, func_after_dmg=decrease_speed)
        return damage_dealt

    def skill3(self):
        pass

    def take_damage_aftermath(self, damage, attacker):
        if random.randint(1, 100) <= 30:
            attacker.apply_effect(ContinuousDamageEffect("Burn", 3, False, self.atk * 0.5, self))


class Iris(Character):
    def __init__(self, name, lvl, exp=0, equip=None, image=None):
        super().__init__(name, lvl, exp, equip, image)
        self.name = "Iris"
        self.skill1_description = "320% atk on all enemies."
        self.skill2_description = "320% atk on all enemies, inflict 35% atk continuous damage for 3 turns."
        self.skill3_description = "At start of battle, apply Cancellation Shield to ally with highest atk. Cancellation shield: cancel 1 attack if attack damage exceed 10% of max hp. When the shield is active, gain immunity to CC."
        self.skill1_cooldown_max = 5
        self.skill2_cooldown_max = 5

    def skill_tooltip(self):
        return f"Skill 1 : {self.skill1_description}\nCooldown : {self.skill1_cooldown} action(s)\n\nSkill 2 : {self.skill2_description}\nCooldown : {self.skill2_cooldown} action(s)\n\nSkill 3 : {self.skill3_description}\n"

    def skill1_logic(self):
        damage_dealt = self.attack(target_kw1="n_random_enemy",target_kw2="5", multiplier=3.2, repeat=1)            
        return damage_dealt

    def skill2_logic(self):
        def bleed(self, target):
            target.apply_effect(ContinuousDamageEffect("Burn", 3, False, self.atk * 0.35, self))
        damage_dealt = self.attack(target_kw1="n_random_enemy",target_kw2="5", multiplier=3.2, repeat=1, func_after_dmg=bleed)
        return damage_dealt

    def skill3(self):
        pass

    def battle_entry_effects(self):
        ally_with_highest_atk = mit.one(self.target_selection("n_highest_attr", "1", "atk", "ally"))
        ally_with_highest_atk.apply_effect(CancellationShield("Cancellation Shield", -1, True, 0.1, cc_immunity=True, running=self.running, logging=self.logging, text_box=self.text_box))


class Freya(Character):
    def __init__(self, name, lvl, exp=0, equip=None, image=None):
        super().__init__(name, lvl, exp, equip, image)
        self.name = "Freya"
        self.skill1_description = "620% atk on 1 enemy, 75% chance to silence for 3 turns, always target the enemy with highest ATK."
        self.skill2_description = "520% atk on 1 enemy, always target the enemy with lowest HP."
        self.skill3_description = "Apply Absorption Shield on self if target is fallen by skill 2. Shield will absorb up to 900% of ATK of damage."
        self.skill1_cooldown_max = 5
        self.skill2_cooldown_max = 5

    def skill_tooltip(self):
        return f"Skill 1 : {self.skill1_description}\nCooldown : {self.skill1_cooldown} action(s)\n\nSkill 2 : {self.skill2_description}\nCooldown : {self.skill2_cooldown} action(s)\n\nSkill 3 : {self.skill3_description}\n"

    def skill1_logic(self):
        def silence_effect(self, target):
            dice = random.randint(1, 100)
            if dice <= 75:
                target.apply_effect(SilenceEffect("Silence", 3, False))
        damage_dealt = self.attack(target_kw1="n_highest_attr",target_kw2="1",target_kw3="atk",target_kw4="enemy", multiplier=6.2, repeat=1, func_after_dmg=silence_effect)
        return damage_dealt

    def skill2_logic(self):
        def apply_shield(self, target):
            if target.is_dead():
                self.apply_effect(AbsorptionShield("Absorption Shield", -1, True, self.atk * 9, cc_immunity=False, running=self.running, logging=self.logging, text_box=self.text_box))
        damage_dealt = self.attack(target_kw1="n_lowest_attr",target_kw2="1",target_kw3="hp",target_kw4="enemy", multiplier=5.2, repeat=1, func_after_dmg=apply_shield)
        return damage_dealt

    def skill3(self):
        # No effect 
        pass


class Luna(Character):
    def __init__(self, name, lvl, exp=0, equip=None, image=None):
        super().__init__(name, lvl, exp, equip, image)
        self.name = "Luna"
        self.skill1_description = "Attack all targets with 300% atk, recover 10% of damage dealt as hp."
        self.skill2_description = "Attack all targets with 300% atk, apply Moonlight on self for next 3 turns, reduce damage taken by 90%."
        self.skill3_description = "Recover 8% hp of maxhp at start of action."
        self.skill1_cooldown_max = 5
        self.skill2_cooldown_max = 5

    def skill_tooltip(self):
        return f"Skill 1 : {self.skill1_description}\nCooldown : {self.skill1_cooldown} action(s)\n\nSkill 2 : {self.skill2_description}\nCooldown : {self.skill2_cooldown} action(s)\n\nSkill 3 : {self.skill3_description}\n"

    def skill1_logic(self):
        damage_dealt = self.attack(target_kw1="n_random_enemy",target_kw2="5", multiplier=3.0, repeat=1)
        if self.is_alive():
            self.heal_hp(damage_dealt * 0.1, self)    
        return damage_dealt

    def skill2_logic(self):
        def moonlight(self):
            self.apply_effect(ReductionShield("Moonlight", 3, True, 0.9, cc_immunity=False))
        damage_dealt = self.attack(target_kw1="n_random_enemy",target_kw2="5", multiplier=3.0, repeat=1)
        if self.is_alive():
            moonlight(self)
        return damage_dealt

    def skill3(self):
        pass


class Clover(Character):
    def __init__(self, name, lvl, exp=0, equip=None, image=None):
        super().__init__(name, lvl, exp, equip, image)
        self.name = "Clover"
        self.skill1_description = "Target 1 ally with lowest hp and 1 random enemy, deal 460% atk damage to enemy and heal ally for 100% of damage dealt."
        self.skill2_description = "Target 1 ally with lowest hp, heal for 350% atk and grant Absorption Shield, absorb damage up to 350% atk."
        self.skill3_description = "Every time an ally is healed by Clover, heal Clover for 60% of that amount."
        self.skill1_cooldown_max = 5
        self.skill2_cooldown_max = 5

    def skill_tooltip(self):
        return f"Skill 1 : {self.skill1_description}\nCooldown : {self.skill1_cooldown} action(s)\n\nSkill 2 : {self.skill2_description}\nCooldown : {self.skill2_cooldown} action(s)\n\nSkill 3 : {self.skill3_description}\n"


    def skill1_logic(self):
        damage_dealt = self.attack(multiplier=4.6, repeat=1)
        ally_to_heal = mit.one(self.target_selection(keyword="n_lowest_attr", keyword2="1", keyword3="hp", keyword4="ally"))
        if self.is_alive():
            self.update_ally_and_enemy()
            healing, x, y = ally_to_heal.heal_hp(damage_dealt, self)
            self.heal_hp(healing * 0.6, self)
        return damage_dealt

    def skill2_logic(self):
        ally_to_heal = mit.one(self.target_selection(keyword="n_lowest_attr", keyword2="1", keyword3="hp", keyword4="ally"))
        healing, x, y = ally_to_heal.heal_hp(self.atk * 3.5, self)
        self.heal_hp(healing * 0.6, self)
        ally_to_heal.apply_effect(AbsorptionShield("Shield", -1, True, self.atk * 3.5, cc_immunity=False,running=self.running, logging=self.logging, text_box=self.text_box))
        return None

    def skill3(self):
        pass


class Ruby(Character):
    def __init__(self, name, lvl, exp=0, equip=None, image=None):
        super().__init__(name, lvl, exp, equip, image)
        self.name = "Ruby"
        self.skill1_description = "400% atk on 3 enemies. 70% chance to inflict stun for 3 turns."
        self.skill2_description = "400% focus atk on 1 enemy for 3 times. Each attack has 50% chance to inflict stun for 3 turns."
        self.skill3_description = "Skill damage is increased by 30% on stunned targets."
        self.skill1_cooldown_max = 5
        self.skill2_cooldown_max = 5

    def skill_tooltip(self):
        return f"Skill 1 : {self.skill1_description}\nCooldown : {self.skill1_cooldown} action(s)\n\nSkill 2 : {self.skill2_description}\nCooldown : {self.skill2_cooldown} action(s)\n\nSkill 3 : {self.skill3_description}\n"

    def skill1_logic(self):
        def stun_effect(self, target):
            dice = random.randint(1, 100)
            if dice <= 70:
                target.apply_effect(StunEffect('Stun', duration=3, is_buff=False))
        def stun_amplify(self, target, final_damage):
            if target.has_effect_that_named("Stun"):
                final_damage *= 1.3
            return final_damage
        damage_dealt = self.attack(target_kw1="n_random_enemy",target_kw2="3", multiplier=4.0, repeat=1, func_after_dmg=stun_effect, func_damage_step=stun_amplify)            
        return damage_dealt

    def skill2_logic(self):
        def stun_effect(self, target):
            dice = random.randint(1, 100)
            if dice <= 50:
                target.apply_effect(StunEffect('Stun', duration=3, is_buff=False))
        def stun_amplify(self, target, final_damage):
            if target.has_effect_that_named("Stun"):
                final_damage *= 1.3
            return final_damage
        damage_dealt = self.attack(multiplier=4.0, repeat_seq=3, func_after_dmg=stun_effect, func_damage_step=stun_amplify)
        return damage_dealt

    def skill3(self):
        pass


class Olive(Character):
    def __init__(self, name, lvl, exp=0, equip=None, image=None):
        super().__init__(name, lvl, exp, equip, image)
        self.name = "Olive"
        self.skill1_description = "570% atk on 1 enemy. Decrease target's atk by 50% for 4 turns."
        self.skill2_description = "Heal 3 allies with lowest hp by 270% atk and increase their speed by 40% for 4 turns. "
        self.skill3_description = "Normal attack deals 100% more damage if target has less speed than self."
        self.skill1_cooldown_max = 5
        self.skill2_cooldown_max = 5

    def skill_tooltip(self):
        return f"Skill 1 : {self.skill1_description}\nCooldown : {self.skill1_cooldown} action(s)\n\nSkill 2 : {self.skill2_description}\nCooldown : {self.skill2_cooldown} action(s)\n\nSkill 3 : {self.skill3_description}\n"

    def skill1_logic(self):
        def effect(self, target):
            stat_dict = {"atk": 0.5}
            target.apply_effect(StatsEffect("Weaken", 4, False, stat_dict))
        damage_dealt = self.attack(multiplier=5.7, repeat=1, func_after_dmg=effect)             
        return damage_dealt

    def skill2_logic(self):
        ally_to_heal = list(self.target_selection(keyword="n_lowest_attr", keyword2="3", keyword3="hp", keyword4="ally"))
        for ally in ally_to_heal:
            ally.heal_hp(self.atk * 2.7, self)
            stat_dict = {"spd": 1.4}
            ally.apply_effect(StatsEffect("Tailwind", 4, True, stat_dict))
        return None

    def skill3(self):
        pass

    def normal_attack(self):
        def effect(self, target, final_damage):
            if target.spd < self.spd:
                final_damage *= 2.00
            return final_damage
        self.attack(func_damage_step=effect)


class Fenrir(Character):
    def __init__(self, name, lvl, exp=0, equip=None, image=None):
        super().__init__(name, lvl, exp, equip, image)
        self.name = "Fenrir"
        self.skill1_description = "3 hits on random enemies, 220% atk each hit. Reduce skill cooldown for neighbor allies by 2 turns."
        self.skill2_description = "350% atk on a random enemy. Remove 2 debuffs for neighbor allies."
        self.skill3_description = "Fluffy protection is applied to neighbor allies. When the protected ally below 40% hp is about to take damage, heal the ally for 100% atk."
        self.skill1_cooldown_max = 5
        self.skill2_cooldown_max = 5

    def skill_tooltip(self):
        return f"Skill 1 : {self.skill1_description}\nCooldown : {self.skill1_cooldown} action(s)\n\nSkill 2 : {self.skill2_description}\nCooldown : {self.skill2_cooldown} action(s)\n\nSkill 3 : {self.skill3_description}\n"

    def skill1_logic(self):
        damage_dealt = self.attack(multiplier=2.2, repeat=3)
        neighbors = self.get_neighbor_allies_not_including_self() # list
        for ally in neighbors:
            ally.skill1_cooldown = max(ally.skill1_cooldown - 2, 0)
            ally.skill2_cooldown = max(ally.skill2_cooldown - 2, 0)
            if self.running and self.logging:
                self.text_box.append_html_text(f"{ally.name} skill cooldown reduced by 2.\n")                 
        return damage_dealt

    def skill2_logic(self):
        damage_dealt = self.attack(multiplier=3.5, repeat=1)
        neighbors = self.get_neighbor_allies_not_including_self() # list
        for ally in neighbors:
            ally.remove_random_amount_of_debuffs(2)
        return damage_dealt
        
    def skill3(self):
        pass

    def battle_entry_effects(self):
        neighbors = self.get_neighbor_allies_not_including_self()
        for ally in neighbors:
            ally.apply_effect(EffectShield1("Fluffy Protection", -1, True, 0.4, self.atk, False))



class Cerberus(Character):
    def __init__(self, name, lvl, exp=0, equip=None, image=None, execution_threshold=0.15):
        super().__init__(name, lvl, exp, equip, image)
        self.name = "Cerberus"
        self.execution_threshold = execution_threshold

        self.skill1_description = "5 hits on random enemies, 300% atk each hit. Decrease target's def by 10% for each hit. Effect last 3 turns."
        self.skill2_description = "290% focus atk on 1 enemy with lowest hp for 3 times. If target hp is less then 15% during the attack, execute the target."
        self.skill3_description = "On sucessfully executing a target, increase execution threshold by 3%, heal 30% of maxhp and increase atk and critdmg by 30%."
        self.skill1_cooldown_max = 5
        self.skill2_cooldown_max = 5

    def clear_others(self):
        self.execution_threshold = 0.15

    def skill_tooltip(self):
        return f"Skill 1 : {self.skill1_description}\nCooldown : {self.skill1_cooldown} action(s)\n\nSkill 2 : {self.skill2_description}\nCooldown : {self.skill2_cooldown} action(s)\n\nSkill 3 : {self.skill3_description}\n\nExecution threshold : {self.execution_threshold*100}%"

    def skill1_logic(self):
        def effect(self, target):
            stat_dict = {"defense": 0.9}
            target.apply_effect(StatsEffect("Clawed", 3, False, stat_dict))
        damage_dealt = self.attack(multiplier=3.0, repeat=5, func_after_dmg=effect)             
        return damage_dealt

    def skill2_logic(self):
        def effect(self, target):
            if target.hp < target.maxhp * self.execution_threshold and not target.is_dead():
                target.take_bypass_status_effect_damage(target.hp, self)
                if self.running and self.logging:
                    self.text_box.append_html_text(f"Biribiri! {target.name} is executed by {self.name}.\n")
                fine_print(f"Biribiri! {target.name} is executed by {self.name}.", mode=self.fineprint_mode)
                self.execution_threshold += 0.03
                self.heal_hp(self.maxhp * 0.3, self)
                stats_dict = {"atk": 1.3, "critdmg": 0.3}
                self.update_stats(stats_dict)
        damage_dealt = self.attack(target_kw1="n_lowest_attr",target_kw2="1",target_kw3="hp",target_kw4="enemy", multiplier=2.9, repeat=1, repeat_seq=3, func_after_dmg=effect)
        return damage_dealt

    def skill3(self):
        pass


class Pepper(Character):
    def __init__(self, name, lvl, exp=0, equip=None, image=None):
        super().__init__(name, lvl, exp, equip, image)
        self.name = "Pepper"
        self.skill1_description = "800% atk on 1 enemy, 70% success rate, 20% chance to hit an ally with 300% atk, 10% chance to hit self with 300% atk."
        self.skill2_description = "Heal an ally with lowest hp percentage with 800% atk, 70% success rate, 20% chance to have no effect, 10% chance to damage the ally with 200% atk. A failed healing will not apply cooldown."
        self.skill3_description = "On a successful healing with skill 2, 80% chance to accidently revive a neighbor ally with 80% hp."
        self.skill1_cooldown_max = 4
        self.skill2_cooldown_max = 4

    def skill_tooltip(self):
        return f"Skill 1 : {self.skill1_description}\nCooldown : {self.skill1_cooldown} action(s)\n\nSkill 2 : {self.skill2_description}\nCooldown : {self.skill2_cooldown} action(s)\n\nSkill 3 : {self.skill3_description}\n"

    def skill1_logic(self):
        dice = random.randint(1, 100)
        if dice <= 70:
            damage_dealt = self.attack(multiplier=8.0, repeat=1)
        elif dice <= 90 and dice > 70:
            damage_dealt = self.attack(target_kw1="n_random_ally", target_kw2="1", multiplier=3.0, repeat=1)
        else:
            damage_dealt = self.attack(target_kw1="yourself", multiplier=3.0, repeat=1)
        return damage_dealt

    def skill2(self):
        if self.skill2_cooldown > 0:
            raise Exception
        if self.running and self.logging:
            self.text_box.append_html_text(f"{self.name} cast skill 2.\n")
        fine_print(f"{self.name} cast skill 2.", mode=self.fineprint_mode)
        target = mit.one(self.target_selection(keyword="n_lowest_attr", keyword2="1", keyword3="hp", keyword4="ally"))
        pondice = random.randint(1, 100)
        if pondice <= 70:
            target.heal_hp(self.atk * 8.0, self)
            revivedice = random.randint(1, 100)
            if revivedice <= 80:
                neighbors = self.get_neighbor_allies_not_including_self(False) 
                dead_neighbors = [x for x in neighbors if x.is_dead()]
                if dead_neighbors != []:
                    revive_target = random.choice(dead_neighbors)
                    revive_target.revive(1, 0.8)
        elif pondice <= 90 and pondice > 70:
            if self.running and self.logging:
                self.text_box.append_html_text(f"No effect!\n")
            fine_print(f"No effect.", mode=self.fineprint_mode)
            return 0
        else:
            target.take_damage(self.atk * 2.0, self)
            return 0

        self.update_skill_cooldown(2)
        return 0
        

    def skill3(self):
        pass


class Cliffe(Character): 
    def __init__(self, name, lvl, exp=0, equip=None, image=None):
        super().__init__(name, lvl, exp, equip, image)
        self.name = "Cliffe"
        self.skill1_description = "Attack 3 enemies with 300% atk, increase their damage taken by 20% for 3 turns."
        self.skill2_description = "Attack random enemies 4 times for 340% atk, each successful attack and successful additional attack has 40% chance to trigger an 270% atk additional attack."
        self.skill3_description = "Heal hp by 10% of maxhp multiplied by targets fallen by skill 2."
        self.skill1_cooldown_max = 5
        self.skill2_cooldown_max = 5

    def skill_tooltip(self):
        return f"Skill 1 : {self.skill1_description}\nCooldown : {self.skill1_cooldown} action(s)\n\nSkill 2 : {self.skill2_description}\nCooldown : {self.skill2_cooldown} action(s)\n\nSkill 3 : {self.skill3_description}\n"

    def skill1_logic(self):
        def effect(self, target):
            target.apply_effect(ReductionShield("Crystal Breaker", 3, False, 0.2, False))
        damage_dealt = self.attack(target_kw1="n_random_enemy",target_kw2="3", multiplier=3.0, repeat=1, func_after_dmg=effect)            
        return damage_dealt

    def skill2_logic(self):
        downed_target = 0
        def more_attacks(self, target, is_crit):
            nonlocal downed_target
            if target.is_dead():
                downed_target += 1
            dice = random.randint(1, 100)
            if dice <= 40:
                if self.running and self.logging:
                    self.text_box.append_html_text(f"{self.name} triggered additional attack.\n")
                fine_print(f"{self.name} triggered additional attack.", mode=self.fineprint_mode)
                return self.attack(multiplier=2.7, repeat=1, additional_attack_after_dmg=more_attacks)
            else:
                return 0
        damage_dealt = self.attack(multiplier=3.4, repeat=4, additional_attack_after_dmg=more_attacks)      
        if downed_target > 0 and self.is_alive():
            self.heal_hp(downed_target * 0.1 * self.maxhp, self)
        return damage_dealt
        
    def skill3(self):
        pass


class Pheonix(Character): 
    def __init__(self, name, lvl, exp=0, equip=None, image=None):
        super().__init__(name, lvl, exp, equip, image)
        self.name = "Pheonix"
        self.skill1_description = "Attack all enemies with 230% atk, 80% chance to inflict burn for 3 turns. Burn deals 50% atk damage per turn."
        self.skill2_description = "First time cast: apply Reborn to all allies with 65% chance each, however, allies can only revive with 15% hp and receive no buff effects. Second and further cast: attack random enemy pair with 320% atk, 80% chance to inflict burn for 3 turns. Burn deals 50% atk damage per turn."
        self.skill3_description = "Revive with 40% hp the next turn after fallen. When revived, increase atk by 50% for 3 turns."
        self.first_time = True
        self.skill1_cooldown_max = 5
        self.skill2_cooldown_max = 5

    def clear_others(self):
        self.first_time = True

    def skill_tooltip(self):
        return f"Skill 1 : {self.skill1_description}\nCooldown : {self.skill1_cooldown} action(s)\n\nSkill 2 : {self.skill2_description}\nCooldown : {self.skill2_cooldown} action(s)\n\nSkill 3 : {self.skill3_description}\n\nFirst time on skill 2: {self.first_time}"

    def skill1_logic(self):
        def burn_effect(self, target):
            if random.randint(1, 100) <= 80:
                target.apply_effect(ContinuousDamageEffect("Burn", 3, False, self.atk * 0.5, self))
        damage_dealt = self.attack(target_kw1="n_random_enemy",target_kw2="5", multiplier=2.3, repeat=1, func_after_dmg=burn_effect)         
        return damage_dealt

    def skill2_logic(self):
        if self.first_time:
            self.first_time = False
            for ally in self.ally:
                if ally != self:
                    if random.randint(1, 100) <= 65:
                        ally.apply_effect(RebornEffect("Reborn", -1, True, 0.15, False))
            return 0
        else:
            def burn_effect(self, target):
                if random.randint(1, 100) <= 80:
                    target.apply_effect(ContinuousDamageEffect("Burn", 3, False, self.atk * 0.5, self))
            damage_dealt = self.attack(target_kw1="random_enemy_pair", multiplier=3.2, repeat=1, func_after_dmg=burn_effect)         
            return damage_dealt   

    def skill3(self):
        pass

    def after_revive(self):
        stat_dict = {"atk": 1.5}
        self.apply_effect(StatsEffect("Reborn", 3, True, stat_dict))

    def battle_entry_effects(self):
        self.apply_effect(RebornEffect("Reborn", -1, True, 0.4, False))


class Bell(Character):
    def __init__(self, name, lvl, exp=0, equip=None, image=None):
        super().__init__(name, lvl, exp, equip, image)
        self.name = "Bell"
        self.skill1_description = "Attack 1 enemy with highest atk 170% atk 5 times."
        self.skill2_description = "Attack 1 enemy with lowest hp 170% atk 6 times. This attack never misses. For each target fallen, trigger an additional attack. Maximum attacks: 8"
        self.skill3_description = "Once per battle, after taking damage, if hp is below 50%, apply absorption shield, absorb damage up to 400% of damage just taken. For 5 turns, damage taken cannot exceed 20% of maxhp."
        self.skill3_used = False
        self.skill1_cooldown_max = 5
        self.skill2_cooldown_max = 5

    def skill_tooltip(self):
        return f"Skill 1 : {self.skill1_description}\nCooldown : {self.skill1_cooldown} action(s)\n\nSkill 2 : {self.skill2_description}\nCooldown : {self.skill2_cooldown} action(s)\n\nSkill 3 : {self.skill3_description}\n"

    def clear_others(self):
        self.skill3_used = False

    def skill1_logic(self):
        damage_dealt = self.attack(target_kw1="n_highest_attr",target_kw2="1",target_kw3="atk",target_kw4="enemy", multiplier=1.7, repeat=5)
        return damage_dealt

    def skill2_logic(self):
        downed_target = 0
        def additional_attacks(self, target, is_crit):
            nonlocal downed_target
            if target.is_dead() and downed_target < 3:
                downed_target += 1
                if self.running and self.logging:
                    self.text_box.append_html_text(f"{self.name} triggered additional attack.\n")
                fine_print(f"{self.name} triggered additional attack.", mode=self.fineprint_mode)
                return self.attack(target_kw1="n_lowest_attr",target_kw2="1",target_kw3="hp",target_kw4="enemy", multiplier=1.7, repeat=1, additional_attack_after_dmg=additional_attacks, always_hit=True)
            else:
                return 0
        damage_dealt = self.attack(target_kw1="n_lowest_attr",target_kw2="1",target_kw3="hp",target_kw4="enemy", multiplier=1.7, repeat=6, additional_attack_after_dmg=additional_attacks, always_hit=True)
        return damage_dealt

    def skill3(self):
        pass

    def take_damage_aftermath(self, damage, attacker):
        if self.skill3_used:
            pass
        else:
            if self.hp < self.maxhp * 0.5:
                self.apply_effect(CancellationShield2("Cancellation Shield", 5, True, 0.2, False))
                self.apply_effect(AbsorptionShield("Shield", -1, True, damage * 4.0, cc_immunity=False, running=self.running, logging=self.logging, text_box=self.text_box))
                self.skill3_used = True
            return damage


class Taily(Character):
    def __init__(self, name, lvl, exp=0, equip=None, image=None):
        super().__init__(name, lvl, exp, equip, image)
        self.name = "Taily"
        self.skill1_description = "350% atk on random enemy pair, inflict stun for 2 turns."
        self.skill2_description = "700% atk on enemy with highest hp, damage is scaled to 150% if target has more than 90% hp percentage."
        self.skill3_description = "At start of battle, apply Blessing of Firewood to all allies." \
        " When an ally is about to take normal attack or skill damage, take the damage instead. Damage taken is reduced by 40% when taking damage for an ally." \
        " Cannot protect against status effect and status damage."
        self.skill1_cooldown_max = 5
        self.skill2_cooldown_max = 5

    def skill_tooltip(self):
        return f"Skill 1 : {self.skill1_description}\nCooldown : {self.skill1_cooldown} action(s)\n\nSkill 2 : {self.skill2_description}\nCooldown : {self.skill2_cooldown} action(s)\n\nSkill 3 : {self.skill3_description}\n"

    def skill1_logic(self):
        def stun_effect(self, target):
            target.apply_effect(StunEffect('Stun', duration=2, is_buff=False))
        damage_dealt = self.attack(target_kw1="random_enemy_pair", multiplier=3.5, repeat=1, func_after_dmg=stun_effect)     
        return damage_dealt

    def skill2_logic(self):
        def effect(self, target, final_damage):
            if target.hp > target.maxhp * 0.9:
                final_damage *= 1.5
            return final_damage
        damage_dealt = self.attack(target_kw1="n_highest_attr",target_kw2="1",target_kw3="hp",target_kw4="enemy", multiplier=7.0, repeat=1, func_damage_step=effect)   
        return damage_dealt
        
    def skill3(self):
        pass

    def battle_entry_effects(self):
        allies = [x for x in self.ally if x != self]
        for ally in allies:
            ally.apply_effect(ProtectedEffect("Blessing of Firewood", -1, True, False, self, 0.6))


class Seth(Character):
    def __init__(self, name, lvl, exp=0, equip=None, image=None):
        super().__init__(name, lvl, exp, equip, image)
        self.name = "Seth"
        self.skill1_description = "Attack random enemies 3 times with 280% atk. For each attack, a critical strike will trigger an additional attack. Maximum additional attacks: 3"
        self.skill2_description = "Attack all enemies with 250% atk."
        self.skill3_description = "Every turn, increase crit rate and crit dmg by 1%."
        self.skill1_cooldown_max = 5
        self.skill2_cooldown_max = 5

    def skill_tooltip(self):
        return f"Skill 1 : {self.skill1_description}\nCooldown : {self.skill1_cooldown} action(s)\n\nSkill 2 : {self.skill2_description}\nCooldown : {self.skill2_cooldown} action(s)\n\nSkill 3 : {self.skill3_description}\n"

    def skill1_logic(self):
        def additional_attack(self, target, is_crit):
            if is_crit:
                if self.running and self.logging:
                    self.text_box.append_html_text(f"{self.name} triggered additional attack.\n")
                fine_print(f"{self.name} triggered additional attack.", mode=self.fineprint_mode)
                return self.attack(multiplier=2.8, repeat=1)
            else:
                return 0
        damage_dealt = self.attack(multiplier=2.8, repeat=3, additional_attack_after_dmg=additional_attack)
        return damage_dealt

    def skill2_logic(self):
        damage_dealt = self.attack(target_kw1="n_random_enemy",target_kw2="5", multiplier=2.5, repeat=1) 
        return damage_dealt
        
    def skill3(self):
        pass

    def battle_entry_effects(self):
        self.apply_effect(SethEffect("Passive Effect", -1, True, 0.01))


class Chiffon(Character):
    def __init__(self, name, lvl, exp=0, equip=None, image=None):
        super().__init__(name, lvl, exp, equip, image)
        self.name = "Chiffon"
        self.skill1_description = "Increase def by 20%, atk by 10% for 5 turns for all allies. Apply a shield that absorbs damage up to 150% self atk for 3 turns."
        self.skill2_description = "Select random 5 targets, when target is an ally, heal 150% atk, when target is an enemy, attack with 400% atk and apply Sleep with a 50% chance."
        self.skill3_description = "When taking damage that would exceed 10% of maxhp, reduce damage above 10% of maxhp by 60%. For every turn passed, damage reduction effect is reduced by 2%."
        self.skill1_cooldown_max = 5
        self.skill2_cooldown_max = 5

    def skill_tooltip(self):
        return f"Skill 1 : {self.skill1_description}\nCooldown : {self.skill1_cooldown} action(s)\n\nSkill 2 : {self.skill2_description}\nCooldown : {self.skill2_cooldown} action(s)\n\nSkill 3 : {self.skill3_description}\n"

    def skill1_logic(self):
        for ally in self.ally:
            ally.apply_effect(StatsEffect("Woof! Woof! Woof!", 5, True, {"defense": 1.2, "atk": 1.1}))
            ally.apply_effect(AbsorptionShield("Woof! Woof! Woof!", 3, True, self.atk * 1.5, cc_immunity=False, running=self.running, logging=self.logging, text_box=self.text_box))
        return 0

    def skill2_logic(self):
        targets = list(self.target_selection(keyword="n_random_target", keyword2="5"))
        enemy_list = []
        for target in targets:
            if target in self.ally:
                target.heal_hp(self.atk * 1.5, self)
            else:
                enemy_list.append(target)
        def sleep_effect(self, target):
            dice = random.randint(1, 100)
            if dice <= 50:
                target.apply_effect(SleepEffect('Sleep', duration=-1, is_buff=False))
        damage_dealt = self.attack(target_list=enemy_list, multiplier=4.0, repeat=1, func_after_dmg=sleep_effect)
        return damage_dealt
        
    def skill3(self):
        pass

    def battle_entry_effects(self):
        self.apply_effect(EffectShield2("Passive Effect", -1, True, False, damage_reduction=0.6))


class Ophelia(Character):
    def __init__(self, name, lvl, exp=0, equip=None, image=None):
        super().__init__(name, lvl, exp, equip, image)
        self.name = "Ophelia"
        self.skill1_description = "Attack 1 enemy with 430% atk. Consumes a card in possession to gain an additional effect according to the card type." \
        " Death Card: Skill damage increases by 50%, Stun the target for 3 turns." \
        " Love Card: Reduce heal efficiency for 3 turns by 100%." \
        " Luck Card: Skill cooldown does not apply." \
        " Gains Death Card after this skill."
        self.skill2_description = "All allies regenerates 5% of maxhp for 4 turns. Consumes a card in possession to gain an additional effect according to the card type." \
        " Death Card: Increase critical damage by 30% for 3 turns." \
        " Love Card: Heal all allies for 300% atk." \
        " Luck Card: Skill cooldown does not apply." \
        " Gains Love Card after this skill."
        self.skill3_description = "Normal attack and skills has 30% chance to gain Luck Card."
        self.skill1_cooldown_max = 5
        self.skill2_cooldown_max = 5

    def skill_tooltip(self):
        return f"Skill 1 : {self.skill1_description}\nCooldown : {self.skill1_cooldown} action(s)\n\nSkill 2 : {self.skill2_description}\nCooldown : {self.skill2_cooldown} action(s)\n\nSkill 3 : {self.skill3_description}\n"

    def skill1(self):
        if self.running and self.logging:
            self.text_box.append_html_text(f"{self.name} cast skill 1.\n")
        fine_print(f"{self.name} cast skill 1.", mode=self.fineprint_mode)
        if self.skill1_cooldown > 0:
            raise Exception
        buff_to_remove_list = []
        def card_effect(self, target):
            for buff in self.buffs:
                if buff.name == "Death Card":
                    target.apply_effect(StunEffect('Stun', duration=3, is_buff=False))
                    buff_to_remove_list.append(buff)
                if buff.name == "Love Card":
                    target.apply_effect(StatsEffect("Unhealable", 3, False, {"heal_efficiency": -1.0}))
                    buff_to_remove_list.append(buff)

        def card_amplify(self, target, final_damage):
            death_card_count = max(sum(1 for buff in self.buffs if buff.name == "Death Card"), 1)
            final_damage *= 1.5 * death_card_count
            return final_damage
        
        damage_dealt = self.attack(multiplier=4.3, repeat=1, func_after_dmg=card_effect, func_damage_step=card_amplify)
        lucky_card_found = False
        for buff in self.buffs:
            if buff.name == "Luck Card":
                buff_to_remove_list.append(buff)
                lucky_card_found = True
                break
        self.buffs = [buff for buff in self.buffs if buff not in buff_to_remove_list]
        self.apply_effect(Effect("Death Card", -1, True, False))
        if lucky_card_found:
            self.skill1_cooldown = 0
        else:
            self.update_skill_cooldown(1)
        dice = random.randint(1, 100)
        if dice <= 30:
            self.apply_effect(Effect("Luck Card", -1, True, False))
            if self.running and self.logging:
                self.text_box.append_html_text(f"{self.name} gained Luck Card.\n")
            fine_print(f"{self.name} gained Luck Card.", mode=self.fineprint_mode)
        
        return damage_dealt

    def skill2(self):
        if self.running and self.logging:
            self.text_box.append_html_text(f"{self.name} cast skill 2.\n")
        fine_print(f"{self.name} cast skill 2.", mode=self.fineprint_mode)
        if self.skill2_cooldown > 0:
            raise Exception
        buff_to_remove_list = []
        for ally in self.ally:
            ally.apply_effect(ContinuousHealEffect("Regeneration", 4, True, 0.05, True))
            for buff in self.buffs:
                if buff.name == "Death Card":
                    ally.apply_effect(StatsEffect("Crit Dmg Up", 3, True, {"critdmg": 0.3}))
                    buff_to_remove_list.append(buff)
                if buff.name == "Love Card":
                    ally.heal_hp(self.atk * 3.0, self)
                    buff_to_remove_list.append(buff)
        lucky_card_found = False
        for buff in self.buffs:
            if buff.name == "Luck Card":
                buff_to_remove_list.append(buff)
                lucky_card_found = True
                break
        if lucky_card_found:
            self.skill2_cooldown = 0
        else:
            self.update_skill_cooldown(2)
        self.buffs = [buff for buff in self.buffs if buff not in buff_to_remove_list]
        self.apply_effect(Effect("Love Card", -1, True, False))
        dice = random.randint(1, 100)
        if dice <= 30:
            self.apply_effect(Effect("Luck Card", -1, True, False))
            if self.running and self.logging:
                self.text_box.append_html_text(f"{self.name} gained Luck Card.\n")
            fine_print(f"{self.name} gained Luck Card.", mode=self.fineprint_mode)
        return 0
        
    def skill3(self):
        pass

    def normal_attack(self):
        def effect(self, target):
            # gain card
            dice = random.randint(1, 100)
            if dice <= 30:
                self.apply_effect(Effect("Luck Card", -1, True, False))
                if self.running and self.logging:
                    self.text_box.append_html_text(f"{self.name} gained Luck Card.\n")
                fine_print(f"{self.name} gained Luck Card.", mode=self.fineprint_mode)

        self.attack(func_after_dmg=effect)


class Requina(Character):
    def __init__(self, name, lvl, exp=0, equip=None, image=None):
        super().__init__(name, lvl, exp, equip, image)
        self.name = "Requina"
        self.skill1_description = "Attack 3 random enemies with 300% atk, 50% chance to apply 6 stacks of Great Poison. 50% chance to apply 4 stacks." \
        " Each stack of Great Poison reduces atk, defence, heal efficiency by 1%, Each turn, deals 0.5% maxhp status damage. " \
        " Maximum stacks: 70" \
        # " Each healing effect will remove 1 stack of Great Poison. " \
        " Effect last 7 turns. Same effect applied refreshes the duration."
        self.skill2_description = "Attack 2 random enemies with 360% atk, if target has Great Poison, deal 50% more damage and apply 5 stacks of Great Poison."
        self.skill3_description = "Normal attack has 80% chance to apply 1 stack of Great Poison."
        self.skill1_cooldown_max = 5
        self.skill2_cooldown_max = 5

    def skill_tooltip(self):
        return f"Skill 1 : {self.skill1_description}\nCooldown : {self.skill1_cooldown} action(s)\n\nSkill 2 : {self.skill2_description}\nCooldown : {self.skill2_cooldown} action(s)\n\nSkill 3 : {self.skill3_description}\n"

    def skill1_logic(self):
        def effect(self, target):
            dice = random.randint(1, 100)
            if dice <= 50:
                target.apply_effect(GreatPoisonEffect("Great Poison", 7, False, 0.005, {"atk": 1.00, "defense": 1.00, "heal_efficiency": 0.00}, self, 6))
            else:
                target.apply_effect(GreatPoisonEffect("Great Poison", 7, False, 0.005, {"atk": 1.00, "defense": 1.00, "heal_efficiency": 0.00}, self, 4))
        damage_dealt = self.attack(target_kw1="n_random_enemy",target_kw2="3", multiplier=3.0, repeat=1, func_after_dmg=effect)
        return damage_dealt

    def skill2_logic(self):
        def damage_step_effect(self, target, final_damage):
            if target.has_effect_that_named("Great Poison"):
                final_damage *= 1.5
                target.apply_effect(GreatPoisonEffect("Great Poison", 7, False, 0.005, {"atk": 1.00, "defense": 1.00, "heal_efficiency": 0.00}, self, 5))
            return final_damage
        damage_dealt = self.attack(target_kw1="n_random_enemy",target_kw2="2", multiplier=3.6, repeat=1, func_damage_step=damage_step_effect)
        return damage_dealt
        
    def skill3(self):
        pass

    def normal_attack(self):
        def effect(self, target):
            dice = random.randint(1, 100)
            if dice <= 80:
                target.apply_effect(GreatPoisonEffect("Great Poison", 7, False, 0.005, {"atk": 1.00, "defense": 1.00, "heal_efficiency": 0.00}, self, 1))
        self.attack(func_after_dmg=effect)


class Gabe(Character):
    def __init__(self, name, lvl, exp=0, equip=None, image=None):
        super().__init__(name, lvl, exp, equip, image)
        self.name = "Gabe"
        self.skill1_description = "Attack 3 random enemies with 420% atk. Damage increases by 20% if target has New Year Fireworks effect."
        self.skill2_description = "Apply New Year Fireworks to self for 4 times and heal hp by 400% atk." \
        " New Year Fireworks: Have 6 counters. Every turn, throw a dice, counter decreases by the dice number." \
        " When counter reaches 0, deal 600% of applier atk as status damage to self." \
        " At the end of the turn, this effect is applied to a random enemy." 
        self.skill3_description = "Reduces chances of rolling 6 on dice by 50%."
        self.skill1_cooldown_max = 5
        self.skill2_cooldown_max = 4

    def skill_tooltip(self):
        return f"Skill 1 : {self.skill1_description}\nCooldown : {self.skill1_cooldown} action(s)\n\nSkill 2 : {self.skill2_description}\nCooldown : {self.skill2_cooldown} action(s)\n\nSkill 3 : {self.skill3_description}\n"

    def skill1_logic(self):
        def damage_amplify(self, target, final_damage):
            if target.has_effect_that_named("New Year Fireworks"):
                final_damage *= 1.2
            return final_damage
        damage_dealt = self.attack(target_kw1="n_random_enemy",target_kw2="3", multiplier=4.2, repeat=1, func_damage_step=damage_amplify)
        return damage_dealt

    def skill2_logic(self):
        self.apply_effect(NewYearFireworksEffect("New Year Fireworks", -1, False, 6, self, self.running, self.logging, self.text_box))
        self.apply_effect(NewYearFireworksEffect("New Year Fireworks", -1, False, 6, self, self.running, self.logging, self.text_box))
        self.apply_effect(NewYearFireworksEffect("New Year Fireworks", -1, False, 6, self, self.running, self.logging, self.text_box))
        self.apply_effect(NewYearFireworksEffect("New Year Fireworks", -1, False, 6, self, self.running, self.logging, self.text_box))
        for fireworks in self.debuffs:
            if fireworks.name == "New Year Fireworks":
                fireworks.apply_effect_on_trigger(self)
        if self.is_alive():
            self.heal_hp(self.atk * 4.0, self)
        return 0
        
    def skill3(self):
        pass

    def fake_dice(self, sides=6, weights=None):
        if sides == 6:
            weights = [100, 100, 100, 100, 100, 50]
        return super().fake_dice(sides, weights)