from effect import *
from equip import Equip, generate_equips_list, adventure_generate_random_equip_with_weight
import more_itertools as mit
import itertools
import global_vars


class Character:
    def __init__(self, name, lvl, exp=0, equip=None, image=None):
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
        self.skill1_cooldown_max = 5 
        self.skill2_cooldown_max = 5
        self.effect_immunity = [] # list of str effect names


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

    def initialize_stats(self, resethp=True, resetally=True, resetenemy=True, reset_battle_entry=True):
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
        self.skill1_can_be_used = True
        self.skill2_can_be_used = True
        self.damage_taken_this_turn = []
        # list of tuples (damage, attacker, dt), damage is int, attacker is Character object, dt is damage type
        # useful for recording damage taken sequence for certain effects
        self.damage_taken_history = [] # list of self.damage_taken_this_turn
        self.healing_received_this_turn = [] # list of tuples (healing, healer), healing is int, healer is Character object
        self.healing_received_history = [] # list of self.healing_received_this_turn

        self.battle_entry = False if reset_battle_entry else self.battle_entry
        self.number_of_attacks = 0 # counts how many attacks the character has made
        self.battle_turns = 0 # counts how many turns the character has been in battle

        self.clear_others()

    def reset_stats(self, resethp=True, resetally=True, resetenemy=True, reset_battle_entry=True):
        self.initialize_stats(resethp, resetally, resetenemy, reset_battle_entry)

    def get_self_index(self):
        for i, char in enumerate(self.party):
            if char == self:
                return i

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
                for (damage, *_) in record:
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
        # Pepper, Ophelia
        global_vars.turn_info_string += f"{self.name} cast skill 1.\n"
        if self.skill1_cooldown > 0:
            raise Exception
        damage_dealt = self.skill1_logic()
        self.update_skill_cooldown(1)
        if self.get_equipment_set() == "OldRusty" and random.random() < 0.65:
            global_vars.turn_info_string += f"skill cooldown is reset for {self.name} due to Old Rusty set effect.\n"
            self.skill1_cooldown = 0
        return None # for now

    def skill2(self):
        # Warning: Following characters have their own skill2 function:
        # Pepper, Ophelia
        global_vars.turn_info_string += f"{self.name} cast skill 2.\n"
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
        # This function is a generator
        # default : random choice of a single enemy

        # get rid of hidden enemies
        ts_available_enemy = [enemy for enemy in self.enemy if not enemy.is_hidden()]

        if target_list is None:
            target_list = []

        if target_list:
            yield from target_list
            return

        match (keyword, keyword2, keyword3, keyword4):
            case ("yourself", _, _, _):
                yield self

            case ("Undefined", _, _, _):
                yield random.choice(ts_available_enemy)

            case ("n_random_enemy", n, _, _):
                n = int(n)
                if n >= 5:
                    yield from self.enemy
                else:
                    if n > len(ts_available_enemy):
                        n = len(ts_available_enemy)
                    yield from random.sample(ts_available_enemy, n)

            case ("n_random_ally", n, _, _):
                n = int(n)
                if n > len(self.ally):
                    n = len(self.ally)
                yield from random.sample(self.ally, n)

            case ("n_random_target", n, _, _):
                n = int(n)
                if n >= 5:
                    if n > len(self.ally) + len(self.enemy):
                        n = len(self.ally) + len(self.enemy)
                    yield from random.sample(self.ally + self.enemy, n)
                    # Should be good enough for dealing with hide effect, it does not make sense to use any of the following to target all enemies
                else:
                    if n > len(self.ally) + len(ts_available_enemy):
                        n = len(self.ally) + len(ts_available_enemy)
                    yield from random.sample(self.ally + ts_available_enemy, n)

            case ("n_lowest_attr", n, attr, party):
                n = int(n)
                if party == "ally":
                    yield from sorted(self.ally, key=lambda x: getattr(x, attr))[:n]
                elif party == "enemy":
                    yield from sorted(ts_available_enemy, key=lambda x: getattr(x, attr))[:n]

            case ("n_highest_attr", n, attr, party):
                n = int(n)
                if party == "ally":
                    yield from sorted(self.ally, key=lambda x: getattr(x, attr), reverse=True)[:n]
                elif party == "enemy":
                    yield from sorted(ts_available_enemy, key=lambda x: getattr(x, attr), reverse=True)[:n]

            case ("enemy_that_must_have_effect", effect_name, _, _):
                yield from filter(lambda x: x.has_effect_that_named(effect_name), ts_available_enemy)

            case ("n_enemy_with_effect", n, effect_name, _):
                n = int(n)
                targets_with_effects = mit.take(n, filter(lambda x: x.has_effect_that_named(effect_name), ts_available_enemy))
                if len(targets_with_effects) < n:
                    targets_with_effects += random.sample(ts_available_enemy, n - len(targets_with_effects))
                yield from targets_with_effects

            case ("n_ally_with_effect", n, effect_name, _):
                n = int(n)
                targets_with_effects = mit.take(n, filter(lambda x: x.has_effect_that_named(effect_name), self.ally))
                if len(targets_with_effects) < n:
                    targets_with_effects += random.sample(self.ally, n - len(targets_with_effects))
                yield from targets_with_effects

            case ("n_enemy_with_most_buffs", n, _, _):
                n = int(n)
                yield from sorted(ts_available_enemy, key=lambda x: len([e for e in x.buffs if not e.is_set_effect and not e.duration == -1]), reverse=True)[:n]

            case ("enemy_in_front", _, _, _):
                if len(ts_available_enemy) == 1:
                    yield from ts_available_enemy
                else:
                    eif_t_d_t = [] # list of tuples (enemy, distance to self)
                    for eif_e in ts_available_enemy:
                        eif_t_d_t.append((eif_e, abs(self.get_self_index() - eif_e.get_self_index())))
                    eif_t_d_t = sorted(eif_t_d_t, key=lambda x: x[1])
                    # print(eif_t_d_t[0][0])
                    yield from [eif_t_d_t[0][0]]

            case ("n_enemy_in_front", n, _, _):
                n = int(n)
                if len(ts_available_enemy) <= n:
                    yield from ts_available_enemy
                else:
                    neif_t_d_t = [] # list of tuples (enemy, distance to self)
                    for neif_e in ts_available_enemy:
                        neif_t_d_t.append((neif_e, abs(self.get_self_index() - neif_e.get_self_index())))
                    neif_t_d_t = sorted(neif_t_d_t, key=lambda x: x[1])
                    yield from [neif_t_d_t[i][0] for i in range(n)]

            case ("n_enemy_in_middle", n, _, _):
                n = int(n)
                if len(ts_available_enemy) <= n:
                    yield from ts_available_enemy
                else:
                    all_windows = list(mit.windowed(ts_available_enemy, n))
                    # choose the middle window
                    yield from all_windows[len(all_windows)//2]

            case ("n_ally_in_middle", n, _, _):
                n = int(n)
                if len(self.ally) <= n:
                    yield from self.ally
                else:
                    all_windows = list(mit.windowed(self.ally, n))
                    # choose the middle window
                    yield from all_windows[len(all_windows)//2]

            case ("n_lowest_hp_percentage_ally", n, _, _):
                n = int(n)
                yield from sorted(self.ally, key=lambda x: x.hp/x.maxhp)[:n]

            case ("n_lowest_hp_percentage_enemy", n, _, _):
                n = int(n)
                yield from sorted(ts_available_enemy, key=lambda x: x.hp/x.maxhp)[:n]

            case ("n_dead_allies", n, _, _):
                n = int(n)
                yield from mit.take(n, filter(lambda x: x.is_dead(), self.party))

            case ("n_dead_enemies", n, _, _):
                n = int(n)
                yield from mit.take(n, filter(lambda x: x.is_dead(), self.enemyparty))

            case ("random_enemy_pair", _, _, _):
                if len(ts_available_enemy) < 2:
                    yield from ts_available_enemy
                else:
                    yield from random.choice(list(mit.pairwise(ts_available_enemy)))

            case ("random_ally_pair", _, _, _):
                if len(self.ally) < 2:
                    yield from self.ally
                else:
                    yield from random.choice(list(mit.pairwise(self.ally)))

            case ("random_enemy_triple", _, _, _):
                if len(ts_available_enemy) < 3:
                    yield from ts_available_enemy
                else:
                    yield from random.choice(list(mit.triplewise(ts_available_enemy)))

            case ("random_ally_triple", _, _, _):
                if len(self.ally) < 3:
                    yield from self.ally
                else:
                    yield from random.choice(list(mit.triplewise(self.ally)))

            case (_, _, _, _):
                raise Exception(f"Keyword not found. Keyword: {keyword}, Keyword2: {keyword2}, Keyword3: {keyword3}, Keyword4: {keyword4}")


    def attack(self, target_kw1="Undefined", target_kw2="Undefined", 
               target_kw3="Undefined", target_kw4="Undefined", multiplier=2, repeat=1, func_after_dmg=None,
               func_damage_step=None, repeat_seq=1, func_after_miss=None, func_after_crit=None,
               always_crit=False, additional_attack_after_dmg=None, always_hit=False, target_list=None,
               force_dmg=None) -> int:
        # Warning: DO NOT MESS WITH repeat and repeat_seq TOGETHER, otherwise the result will be confusing
        # -> damage dealt
        damage_dealt = 0
        for i in range(repeat):
            if repeat > 1 and i > 0:
                self.update_ally_and_enemy()
            try:
                attack_sequence = list(self.target_selection(target_kw1, target_kw2, target_kw3, target_kw4, target_list))
            except IndexError as e:
                # This should only happen in multistrike, where all targets is fallen and repeat is not exhausted
                # Maybe there is a better solution, just leave it for now
                if repeat > 1 and not self.enemy:
                    break
                else:
                    raise e
            if repeat_seq > 1:
                attack_sequence = list(mit.repeat_each(attack_sequence, repeat_seq))
            for target in attack_sequence:
                if target.is_dead():
                    continue
                if self.is_dead():
                    break
                global_vars.turn_info_string += f"{self.name} is targeting {target.name}.\n"
                damage = self.atk * multiplier - target.defense * (1 - self.penetration) if not force_dmg else force_dmg
                final_accuracy = self.acc - target.eva
                dice = random.randint(1, 100)
                miss = False if dice <= final_accuracy * 100 else True
                if not miss or always_hit:
                    dice = random.randint(1, 100)
                    critical = True if dice <= self.crit * 100 else False
                    critical = True if always_crit else critical
                    if critical:
                        final_damage = damage * (self.critdmg - target.critdef)
                        global_vars.turn_info_string += f"Critical!\n"
                        if func_after_crit is not None: # Warning: this function may be called multiple times
                            final_damage, always_crit = func_after_crit(self, target, final_damage, always_crit)
                    else:
                        final_damage = damage
                    final_damage *= random.uniform(0.8, 1.2)
                    if func_damage_step is not None:
                        final_damage = func_damage_step(self, target, final_damage)
                    for eff in self.buffs.copy() + self.debuffs.copy():
                        final_damage = eff.apply_effect_in_attack_before_damage_step(self, target, final_damage)
                    if self.get_equipment_set() == "Rainbow":
                        rainbow_amplifier_dict = {0: 1.60, 1: 1.30, 2: 1.00, 3: 0.70, 4: 0.40}
                        self_target_index_diff = self.get_self_index() - target.get_self_index()
                        self_target_index_diff = abs(self_target_index_diff)
                        final_damage *= rainbow_amplifier_dict[self_target_index_diff]
                    if self.get_equipment_set() == "Dawn":
                        if self.get_effect_that_named("Dawn Set", None, "EquipmentSetEffect_Dawn").flag_onetime_damage_bonus_active:
                            final_damage *= 2.20
                            global_vars.turn_info_string += f"Damage increased by 120% due to Dawn Set effect.\n"
                            self.get_effect_that_named("Dawn Set", None, "EquipmentSetEffect_Dawn").flag_onetime_damage_bonus_active = False
                    if final_damage < 0:
                        final_damage = 0
                    target.take_damage(final_damage, self, is_crit=critical)
                    damage_dealt += final_damage
                    if target.is_dead():
                        if self.get_equipment_set() == "Bamboo":
                            self.get_effect_that_named("Bamboo Set", None, "EquipmentSetEffect_Bamboo").apply_effect_custom(self)
                    self.add_number_of_attacks(1)
                    if func_after_dmg is not None and self.is_alive():
                        func_after_dmg(self, target)
                    if additional_attack_after_dmg is not None:
                        damage_dealt += additional_attack_after_dmg(self, target, is_crit=critical)
                else:
                    global_vars.turn_info_string += f"Missed! {self.name} attacked {target.name} but missed.\n"

        return damage_dealt


    def add_number_of_attacks(self, n):
        self.number_of_attacks += n
        if self.get_equipment_set() == "Flute" and self.number_of_attacks % 4 == 0:
            for e in self.enemy:
                if e.is_alive():
                    e.take_status_damage(self.atk * 1.30, self)

    def reset_number_of_attacks(self):
        self.number_of_attacks = 0

    def heal(self, target_kw1="Undefined", target_kw2="Undefined", target_kw3="Undefined", target_kw4="Undefined", 
             value=0, repeat=1, func_after_each_heal=None, target_list=None, func_before_heal=None) -> int:
        # -> healing done
        healing_done = 0
        targets = list(self.target_selection(target_kw1, target_kw2, target_kw3, target_kw4, target_list))
        if func_before_heal is not None:
            func_before_heal(self, targets)
        if self.get_equipment_set() == "Rose":
            for t in targets:
                t.apply_effect(StatsEffect("Beloved Girl", 2, True, 
                {"heal_efficiency": self.get_effect_that_named("Rose Set", None, "EquipmentSetEffect_Rose").he_bonus_before_heal}))
        for i in range(repeat):
            for t in targets:
                healing, healer, overhealing = t.heal_hp(value, self)
                healing_done += healing
                if func_after_each_heal is not None:
                    func_after_each_heal(self, t, healing, overhealing)
        return healing_done

    # Action logic
    def action(self) -> None:
        can_act, reason = self.can_take_action()
        if can_act:
            self.update_cooldown()
            if self.skill1_cooldown == 0 and not self.is_silenced() and self.skill1_can_be_used:
                self.skill1()
            elif self.skill2_cooldown == 0 and not self.is_silenced() and self.skill2_can_be_used:
                self.skill2()
            else:
                self.normal_attack()
        else:
            global_vars.turn_info_string += f"{self.name} cannot act due to {reason}.\n"

        self.reset_number_of_attacks()
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
            f"max skill cooldown: {self.skill1_cooldown_max}/{self.skill2_cooldown_max}\n" \
            f"exp/maxexp/perc: {self.exp}/{self.maxexp}/{self.exp/self.maxexp*100:.2f}%\n"

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
            
            global_vars.turn_info_string += f"{self.name} leveled up!\n"

    def reset_stats_and_reapply_effects(self, reset_hp=True):
        buff_copy = [effect for effect in self.buffs if not effect.is_set_effect]
        debuff_copy = [effect for effect in self.debuffs if not effect.is_set_effect]
        self.reset_stats(resethp=reset_hp, resetally=False, resetenemy=False, reset_battle_entry=False) # We are probably doing this during battle
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

    def unequip_all(self, strict):
        if not self.equip:
            if strict:
                raise ValueError("No equipment equipped")
            else:
                return {}
        unequipped_items = self.equip.copy()
        self.equip = {}
        self.reset_stats_and_reapply_effects(False)
        return unequipped_items

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
    
    def is_hidden(self):
        for e in self.buffs + self.debuffs:
            if e.name == "Hide" and e.is_active:
                return True
        return False

    def can_take_action(self):
        if self.is_stunned():
            return False, "Stunned"
        if self.is_sleeping():
            return False, "Sleeping"
        if self.is_frozed():
            return False, "Frozen"
        return True, "None"
    
    def update_ally_and_enemy(self):
        self.ally = [ally for ally in self.party if not ally.is_dead()]
        self.enemy = [enemy for enemy in self.enemyparty if not enemy.is_dead()]
        if self.is_charmed():
            self.ally, self.enemy = self.enemy, self.ally
        elif self.is_confused():
            self.ally += self.enemy
            self.enemy += self.ally
        
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

    def update_stats(self, stats, reversed=False):
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
        # Remember the healer can be a Character object or Consumable object or perhaps other objects
        if self.is_dead():
            print(global_vars.turn_info_string)
            raise Exception(f"Cannot heal a dead character: {self.name}")
        if value < 0:
            value = 0
        healing = value * self.heal_efficiency
        healing = int(healing)
        overhealing = 0
        if self.hp + healing > self.maxhp:
            overhealing = self.hp + healing - self.maxhp
            healing = self.maxhp - self.hp
        if healing < 0:
            global_vars.turn_info_string += f"{self.name} failed to receive any healing.\n"
            healing = 0
        else:
            self.hp += healing
            global_vars.turn_info_string += f"{self.name} is healed for {healing} HP.\n"
        self.healing_received_this_turn.append((healing, healer))
        for e in self.buffs.copy() + self.debuffs.copy():
            e.apply_effect_after_heal_step(self, healing)
        return healing, healer, overhealing

    def pay_hp(self, value):
        if self.is_dead():
            raise Exception("Cannot pay HP when dead.")
        if value < 0:
            value = 0
        value = int(value)
        if self.hp - value < 0:
            raise Exception("Cannot pay more HP than current HP.")
        self.hp -= value
        global_vars.turn_info_string += f"{self.name} paid {value} HP.\n"
        self.damage_taken_this_turn.append((value, self, "status"))
        return value

    def revive(self, hp_to_revive, hp_percentage_to_revive=0):
        if self.is_dead():
            self.hp = hp_to_revive
            self.hp += self.maxhp * hp_percentage_to_revive
            if self.hp > self.maxhp:
                self.hp = self.maxhp
            self.hp = int(self.hp)
            self.healing_received_this_turn.append((self.hp, self))
            global_vars.turn_info_string += f"{self.name} is revived for {self.hp} hp.\n"
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
            global_vars.turn_info_string += f"{self.name} is regenerated for {healing} HP.\n"
        return healing, self, overhealing

    def take_damage(self, value, attacker=None, func_after_dmg=None, disable_protected_effect=False, is_crit=False):
        global_vars.turn_info_string += f"{self.name} is about to take {value} damage.\n"
        if self.is_dead():
            print(global_vars.turn_info_string)
            raise Exception(f"Cannot take damage when dead. {self.name} is already dead. Attacker: {attacker.name}")
        value = max(0, value)
        # Attention: final_damage_taken_multipler is calculated before shields effects.
        damage = value * self.final_damage_taken_multipler

        if damage > 0:
            copyed_buffs = self.buffs.copy() # Some effect will try apply other effects during this step, see comments on Effect class for details.
            copyed_debuffs = self.debuffs.copy()
            for effect in copyed_buffs:
                if hasattr(effect, "is_protected_effect") and effect.is_protected_effect and not disable_protected_effect:
                    damage = effect.protected_apply_effect_during_damage_step(self, damage, attacker, func_after_dmg)
                else:
                    damage = effect.apply_effect_during_damage_step(self, damage, attacker)
            for effect in copyed_debuffs:
                damage = effect.apply_effect_during_damage_step(self, damage, attacker)
                
        damage = self.take_damage_before_calculation(damage, attacker)
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

        global_vars.turn_info_string += f"{self.name} took {damage} damage.\n"
        if is_crit:
            self.damage_taken_this_turn.append((damage, attacker, "normal_critical"))
        else:
            self.damage_taken_this_turn.append((damage, attacker, "normal"))
        return None
    
    def take_damage_before_calculation(self, damage, attacker):
        return damage

    def take_damage_aftermath(self, damage, attacker):
        pass

    def take_status_damage(self, value, attacker=None):
        global_vars.turn_info_string += f"{self.name} is about to take {value} status damage.\n"
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

        copyed_buffs = self.buffs.copy() 
        copyed_debuffs = self.debuffs.copy()
        for effect in copyed_buffs:
            effect.apply_effect_after_status_damage_step(self, damage, attacker)
        for effect in copyed_debuffs:
            effect.apply_effect_after_status_damage_step(self, damage, attacker)

        global_vars.turn_info_string += f"{self.name} took {damage} status damage.\n"
        self.damage_taken_this_turn.append((damage, attacker, "status"))
        return None

    def take_bypass_status_effect_damage(self, value, attacker=None):
        global_vars.turn_info_string += f"{self.name} is about to take {value} bypass status effect damage.\n"
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
        global_vars.turn_info_string += f"{self.name} took {damage} bypass status effect damage.\n"
        self.damage_taken_this_turn.append((damage, attacker, "bypass"))
        return None

    def has_effect_that_named(self, effect_name: str, additional_name: str = None, class_name: str = None):
        for effect in self.buffs + self.debuffs:
            if effect.name != effect_name:
                continue

            match (additional_name, class_name):
                case (None, None):
                    return True
                case (_, None):
                    if hasattr(effect, "additional_name") and effect.additional_name == additional_name:
                        return True
                case (None, _):
                    if type(effect).__name__ == class_name:
                        return True
                case (_, _):
                    if hasattr(effect, "additional_name") and effect.additional_name == additional_name and \
                    type(effect).__name__ == class_name:
                        return True
        return False

    def get_effect_that_named(self, effect_name: str, additional_name: str = None, class_name: str = None):
        for effect in self.buffs + self.debuffs:
            if effect.name != effect_name:
                continue

            match (additional_name, class_name):
                case (None, None):
                    return effect
                case (_, None):
                    if hasattr(effect, "additional_name") and effect.additional_name == additional_name:
                        return effect
                case (None, _):
                    if type(effect).__name__ == class_name:
                        return effect
                case (_, _):
                    if hasattr(effect, "additional_name") and effect.additional_name == additional_name and \
                    type(effect).__name__ == class_name:
                        return effect
        return None


    def is_immune_to_cc(self):
        for effect in self.buffs:
            if effect.cc_immunity:
                return True
        for effect in self.debuffs: # Debuff that provide CC immunity? Makes no sense.
            if effect.cc_immunity:
                print(f"Warning: {self.name} has debuff that provide CC immunity. Effect name: {effect.name}")
                return True
        return False

    def apply_effect(self, effect):
        # if self.is_dead():
        #     print(f"Warning: {self.name} is dead, should not be a valid target to apply effect. Effect name: {effect.name}")
        if effect.name in self.effect_immunity:
            global_vars.turn_info_string += f"{self.name} is immune to {effect.name}.\n"
            return
        if self.is_immune_to_cc() and effect.is_cc_effect:
            global_vars.turn_info_string += f"{self.name} is immune to {effect.name}.\n"
            return
        if effect.apply_rule == "stack" and self.is_alive():
            for e in self.debuffs.copy() + self.buffs.copy():
                if e.name == effect.name:
                    if e.duration < effect.duration and e.duration > 0:
                        e.duration = effect.duration
                    e.apply_effect_when_adding_stacks(self, effect.stacks)
                    global_vars.turn_info_string += f"{effect.name} duration on {self.name} has been refreshed.\n"
                    return
        if self.is_alive() and effect.is_buff:
            self.buffs.append(effect)
            self.buffs.sort(key=lambda x: x.sort_priority)
        elif self.is_alive() and not effect.is_buff:
            self.debuffs.append(effect)
            self.debuffs.sort(key=lambda x: x.sort_priority)
        global_vars.turn_info_string += f"{effect.name} has been applied on {self.name}.\n"
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
        global_vars.turn_info_string += f"{effect.name} on {self.name} has been removed.\n"
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
        debuffs_filtered = [effect for effect in self.debuffs if not effect.is_set_effect and effect.can_be_removed_by_skill]
        amount = min(amount, len(debuffs_filtered))
        if amount == 0:
            return []
        removed_effects = random.sample(debuffs_filtered, amount)
        
        for effect in removed_effects:
            self.remove_effect(effect)
        return removed_effects

    def remove_random_amount_of_buffs(self, amount) -> list:
        # -> list of removed effects
        buffs_filtered = [effect for effect in self.buffs if not effect.is_set_effect and effect.can_be_removed_by_skill]
        amount = min(amount, len(buffs_filtered))
        if amount == 0:
            return []
        removed_effects = random.sample(buffs_filtered, amount)
        
        for effect in removed_effects:
            self.remove_effect(effect)
        return removed_effects

    # Every turn, decrease the duration of all buffs and debuffs by 1. If the duration is 0, remove the effect.
    # And other things.
    def status_effects_start_of_turn(self):
        # Currently, effects are not removed and continue to receive updates even if character is dead. 
        # If we want to do this, remember: Reborn effect should not be removed.
        for effect in self.buffs.copy() + self.debuffs.copy():
            if effect.flag_for_remove:
                global_vars.turn_info_string += f"Effect condition no longer met: {effect.name} on {self.name}.\n"
                self.remove_effect(effect)
                continue
            if effect.duration == -1:
                continue
            effect.decrease_duration()
            if effect.duration > 0:
                global_vars.turn_info_string += f"{effect.name} on {self.name} has {effect.duration} turns left.\n"
                continue
            if effect.is_expired():
                global_vars.turn_info_string += f"{effect.name} on {self.name} has expired.\n"
                self.remove_effect(effect)
                effect.apply_effect_on_expire(self)
    
    # Every turn, calculate apply_effect_on_turn effect of all buffs and debuffs. ie. poison, burn, etc.
    def status_effects_midturn(self):
        buffs_copy = self.buffs.copy()
        debuffs_copy = self.debuffs.copy()
        for effect in buffs_copy + debuffs_copy:
            effect.apply_effect_on_turn(self)

    def status_effects_at_end_of_turn(self):
        # The following character/monster has a local implementation of this function:
        # Character: BeastTamer
        # Monster: Security Guard, Emperor
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
        if set_name == "None" or set_name == "Void":
            return
        elif set_name == "Arasaka": 
            self.apply_effect(EquipmentSetEffect_Arasaka("Arasaka Set", -1, True, False))
        elif set_name == "KangTao":
            self.apply_effect(EquipmentSetEffect_KangTao("KangTao Set", -1, True, self.atk * 6, False))
        elif set_name == "Militech":
            def condition_func(self):
                return self.hp <= self.maxhp * 0.30
            self.apply_effect(EquipmentSetEffect_Militech("Militech Set", -1, True, {"spd": 2.2}, condition_func))
        elif set_name == "NUSA":
            def stats_dict_function() -> dict:
                allies_alive = len(self.ally)
                return {"atk": 0.06 * allies_alive + 1 , "defense": 0.06 * allies_alive + 1, "maxhp": 0.06 * allies_alive + 1}
            self.apply_effect(EquipmentSetEffect_NUSA("NUSA Set", -1, True, {"atk": 1.30, "defense": 1.30, "maxhp": 1.30}, stats_dict_function))
        elif set_name == "Sovereign":
            self.apply_effect(EquipmentSetEffect_Sovereign("Sovereign Set", -1, True, {"atk": 1.20}))
        elif set_name == "Snowflake":
            self.apply_effect(EquipmentSetEffect_Snowflake("Snowflake Set", -1, True))
        elif set_name == "Flute":
            self.apply_effect(EquipmentSetEffect_Flute("Flute Set", -1, True))
        elif set_name == "Rainbow":
            self.apply_effect(EquipmentSetEffect_Rainbow("Rainbow Set", -1, True))
        elif set_name == "Dawn":
            self.apply_effect(EquipmentSetEffect_Dawn("Dawn Set", -1, True, {"atk": 1.24, "crit": 0.12}))
        elif set_name == "Bamboo":
            self.apply_effect(EquipmentSetEffect_Bamboo("Bamboo Set", -1, True, {"atk": 1.66, "defense": 1.66, "spd": 1.66, "crit": 0.33, "critdmg": 0.33}))
        elif set_name == "Rose":
            self.apply_effect(EquipmentSetEffect_Rose("Rose Set", -1, True, he_bonus_before_heal=0.88))
            belove_girl_self_effect = StatsEffect("Beloved Girl", -1, True, {"heal_efficiency": 0.22, "defense": 1.11})
            belove_girl_self_effect.is_set_effect = True
            self.apply_effect(belove_girl_self_effect)
        elif set_name == "OldRusty":
            self.apply_effect(EquipmentSetEffect_OldRusty("OldRusty Set", -1, True))
        elif set_name == "Liquidation":
            self.apply_effect(EquipmentSetEffect_Liquidation("Liquidation Set", -1, True, 0.20))
        else:
            raise Exception("Effect not implemented.")
        
    def equipment_set_effects_tooltip(self):
        set_name = self.get_equipment_set()
        str = "Equipment Set Effects:\n"
        if set_name == "None" or set_name == "Void":
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
                "Increase speed by 120% when hp falls below 30%.\n"
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
        elif set_name == "Flute":
            str += "Flute\n" \
                "On one action, when successfully attacking enemy for 4 times, all enemies take status damage equal to 130% of self atk.\n"
        elif set_name == "Rainbow":
            str += "Rainbow\n" \
                "While attacking, damage increases by 60%/30%/0%/-30%/-60% depending on the proximity of the target.\n"
        elif set_name == "Dawn":
            str += "Dawn\n" \
                "Atk increased by 24%, crit increased by 12% when hp is full.\n" \
                "One time only, when dealing normal or skill attack damage, damage is increased by 120%.\n" 
        elif set_name == "Bamboo":
            str += "Bamboo\n" \
                "After taking down an enemy with normal or skill attack, for 5 turns," \
                " recovers 16% of max hp each turn and increases atk, def, spd by 66%, crit and crit damage by 33%." \
                " Cannot be triggered when buff effect is active.\n"
        elif set_name == "Rose":
            str += "Rose\n" \
                "Heal efficiency is increased by 22%, def is increased by 11%. Before heal, increase target's heal efficiency by 88% for 2 turns." \
                " Cannot be triggered by hp recover.\n"
        elif set_name == "OldRusty":
            str += "Old Rusty\n" \
                "After using skill 1, 65% chance to reset cooldown of that skill.\n"
        elif set_name == "Liquidation":
            str += "Liquidation\n" \
                "When taking damage, for each of the following stats that is lower than attacker's, damage is reduced by 20%: hp, atk, def, spd.\n"
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
        global_vars.turn_info_string += f"{self.name} rolled {result} on a dice.\n"
        return result

    def battle_entry_effects(self):
        # Plan: handles passive status effects applied when entering battle here.
        pass

    def battle_entry_effects_activate(self):
        # Battle entry effect can only activate once until self.initialize_stats() is called.
        if not self.battle_entry:
            self.battle_entry_effects()
            self.battle_entry = True

    def record_battle_turns(self, increment=1):
        self.battle_turns += increment


class Lillia(Character):    # Damage dealer, non close targets, multi strike, critical
    # A reference to a dead mobile game character
    def __init__(self, name, lvl, exp=0, equip=None, image=None):
        super().__init__(name, lvl, exp, equip, image)
        self.name = "Lillia"
        self.is_main_character = True
        self.skill1_description = "12 hits on random enemies, 180% atk each hit. After 1 critical hit, all hits following will be critical and hit nearby targets for 30% of damage as status damage."
        self.skill2_description = "Apply Infinite Spring on self for 12 turns, gain immunity to CC and reduce damage taken by 35%."
        self.skill3_description = "Heal 8% of max hp on action when Infinite Spring is active."
        self.skill1_cooldown_max = 5
        self.skill2_cooldown_max = 5

    def skill_tooltip(self):
        return f"Skill 1 : {self.skill1_description}\nCooldown : {self.skill1_cooldown} action(s)\n\nSkill 2 : {self.skill2_description}\nCooldown : {self.skill2_cooldown} action(s)\n\nSkill 3 : {self.skill3_description}\n"

    def skill1_logic(self):
        def water_splash(self, target, final_damage, always_crit):
            always_crit = True
            for target in target.get_neighbor_allies_not_including_self():
                if target.is_alive():
                    target.take_status_damage(final_damage * 0.3 * random.uniform(0.8, 1.2), self)
            return final_damage, always_crit
        damage_dealt = self.attack(multiplier=1.8, repeat=12, func_after_crit=water_splash)
        return damage_dealt

    def skill2_logic(self):
        self.apply_effect(ReductionShield("Infinite Spring", 12, True, 0.35, cc_immunity=True))
        return None

    def skill3(self):
        if self.has_effect_that_named("Infinite Spring"):
            self.heal_hp(self.maxhp * 0.08, self)

    def action(self):
        self.skill3()
        super().action()


class Poppy(Character):    # Damage dealer, non close targets, multi strike
    # Many character skill ideas are from afk mobile games, this line is written in 2024/01/18
    def __init__(self, name, lvl, exp=0, equip=None, image=None):
        super().__init__(name, lvl, exp, equip, image)
        self.name = "Poppy"
        self.skill1_description = "8 hits on random enemies, 280% atk each hit."
        self.skill2_description = "610% atk on enemy with highest speed. Target speed is decreased by 30% for 8 turns."
        self.skill3_description = "On taking normal attack or skill damage, 30% chance to inflict Burn to attacker for 6 turns. Burn deals 50% atk status damage."
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
            target.apply_effect(StatsEffect("Purchased!", 8, False, stat_dict))
        damage_dealt = self.attack(multiplier=6.1, repeat=1, func_after_dmg=decrease_speed, target_kw1="n_highest_attr", target_kw2="1", target_kw3="spd", target_kw4="enemy")
        return damage_dealt

    def skill3(self):
        pass

    def take_damage_aftermath(self, damage, attacker):
        if random.randint(1, 100) <= 30:
            attacker.apply_effect(ContinuousDamageEffect("Burn", 6, False, self.atk * 0.5, self))


class Iris(Character):    # Damage dealer, non close targets, multi targets
    def __init__(self, name, lvl, exp=0, equip=None, image=None):
        super().__init__(name, lvl, exp, equip, image)
        self.name = "Iris"
        self.skill1_description = "Deals 310% atk damage to all enemies."
        self.skill2_description = "Deals 310% atk damage to all enemies and inflicts Burn, which deals status damage equal to 35% of atk for 7 turns."
        self.skill3_description = "At the start of the battle, applies a Cancellation Shield to the ally with the highest atk. Cancellation Shield: Cancels one attack if the attack damage exceeds 10% of the ally's max HP. While the shield is active, the ally gains immunity to CC effects."
        self.skill1_cooldown_max = 5
        self.skill2_cooldown_max = 5

    def skill_tooltip(self):
        return f"Skill 1 : {self.skill1_description}\nCooldown : {self.skill1_cooldown} action(s)\n\nSkill 2 : {self.skill2_description}\nCooldown : {self.skill2_cooldown} action(s)\n\nSkill 3 : {self.skill3_description}\n"

    def skill1_logic(self):
        damage_dealt = self.attack(target_kw1="n_random_enemy",target_kw2="5", multiplier=3.1, repeat=1)            
        return damage_dealt

    def skill2_logic(self):
        def burn(self, target):
            target.apply_effect(ContinuousDamageEffect("Burn", 7, False, self.atk * 0.35, self))
        damage_dealt = self.attack(target_kw1="n_random_enemy",target_kw2="5", multiplier=3.1, repeat=1, func_after_dmg=burn)
        return damage_dealt

    def skill3(self):
        pass

    def battle_entry_effects(self):
        ally_with_highest_atk = mit.one(self.target_selection("n_highest_attr", "1", "atk", "ally"))
        ally_with_highest_atk.apply_effect(CancellationShield("Cancellation Shield", -1, True, 0.1, cc_immunity=True))


class Freya(Character):    # Damage dealer, non close targets, heavy attack
    def __init__(self, name, lvl, exp=0, equip=None, image=None):
        super().__init__(name, lvl, exp, equip, image)
        self.name = "Freya"
        self.skill1_description = "600% atk on 1 enemy, 75% chance to silence for 6 turns, always target the enemy with highest atk."
        self.skill2_description = "580% atk on 1 enemy, always target the enemy with lowest hp."
        self.skill3_description = "Apply Absorption Shield on self if target is fallen by skill 2. Shield will absorb up to 900% of atk of damage."
        self.skill1_cooldown_max = 4
        self.skill2_cooldown_max = 4

    def skill_tooltip(self):
        return f"Skill 1 : {self.skill1_description}\nCooldown : {self.skill1_cooldown} action(s)\n\nSkill 2 : {self.skill2_description}\nCooldown : {self.skill2_cooldown} action(s)\n\nSkill 3 : {self.skill3_description}\n"

    def skill1_logic(self):
        def silence_effect(self, target):
            dice = random.randint(1, 100)
            if dice <= 75:
                target.apply_effect(SilenceEffect("Silence", 6, False))
        damage_dealt = self.attack(target_kw1="n_highest_attr",target_kw2="1",target_kw3="atk",target_kw4="enemy", multiplier=6.0, repeat=1, func_after_dmg=silence_effect)
        return damage_dealt

    def skill2_logic(self):
        def apply_shield(self, target):
            if target.is_dead():
                self.apply_effect(AbsorptionShield("Absorption Shield", -1, True, self.atk * 9, cc_immunity=False))
        damage_dealt = self.attack(target_kw1="n_lowest_attr",target_kw2="1",target_kw3="hp",target_kw4="enemy", multiplier=5.8, repeat=1, func_after_dmg=apply_shield)
        return damage_dealt

    def skill3(self):
        pass


class Luna(Character):    # Damage dealer, non close targets, multi targets
    def __init__(self, name, lvl, exp=0, equip=None, image=None):
        super().__init__(name, lvl, exp, equip, image)
        self.name = "Luna"
        self.skill1_description = "Attack all targets with 300% atk, recover 10% of damage dealt as hp."
        self.skill2_description = "Attack all targets with 300% atk, apply Moonlight on self for next 4 turns, reduce damage taken by 90%."
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
            self.apply_effect(ReductionShield("Moonlight", 4, True, 0.9, cc_immunity=False))
        damage_dealt = self.attack(target_kw1="n_random_enemy",target_kw2="5", multiplier=3.0, repeat=1)
        if self.is_alive():
            moonlight(self)
        return damage_dealt

    def skill3(self):
        self.heal_hp(self.maxhp * 0.08, self)

    def action(self):
        self.skill3()
        super().action()


class Clover(Character):    # Healer
    def __init__(self, name, lvl, exp=0, equip=None, image=None):
        super().__init__(name, lvl, exp, equip, image)
        self.name = "Clover"
        self.skill1_description = "Target 1 ally with lowest hp and 1 closest enemy, deal 460% atk damage to enemy and heal ally for 100% of damage dealt."
        self.skill2_description = "Target 1 ally with lowest hp, heal for 350% atk and grant Absorption Shield, absorb damage up to 350% atk."
        self.skill3_description = "Every time an ally is healed by Clover, heal Clover for 60% of that amount."
        self.skill1_cooldown_max = 4
        self.skill2_cooldown_max = 5

    def skill_tooltip(self):
        return f"Skill 1 : {self.skill1_description}\nCooldown : {self.skill1_cooldown} action(s)\n\nSkill 2 : {self.skill2_description}\nCooldown : {self.skill2_cooldown} action(s)\n\nSkill 3 : {self.skill3_description}\n"


    def skill1_logic(self):
        damage_dealt = self.attack(multiplier=4.6, repeat=1, target_kw1="enemy_in_front")
        self.update_ally_and_enemy()
        healing_done_a = self.heal("n_lowest_attr", "1", "hp", "ally", damage_dealt, 1)
        if self.is_alive():
            healing_done_b = self.heal("yourself", value=healing_done_a * 0.6)
        return damage_dealt

    def skill2_logic(self):
        def effect(self, target, healing, overhealing):
            target.apply_effect(AbsorptionShield("Shield", -1, True, self.atk * 3.5, cc_immunity=False))
        healing_done_a = self.heal("n_lowest_attr", "1", "hp", "ally", self.atk * 3.5, 1, func_after_each_heal=effect)
        if self.is_alive():
            healing_done_b = self.heal("yourself", value=healing_done_a * 0.6)
        return None

    def skill3(self):
        pass


class Ruby(Character):   # Damage dealer, close targets, stun
    def __init__(self, name, lvl, exp=0, equip=None, image=None):
        super().__init__(name, lvl, exp, equip, image)
        self.name = "Ruby"
        self.skill1_description = "400% atk on 3 closest enemies. 70% chance to inflict stun for 3 turns."
        self.skill2_description = "400% focus atk on 1 closest enemy for 3 times. Each attack has 50% chance to inflict stun for 3 turns."
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
        damage_dealt = self.attack(target_kw1="n_enemy_in_front",target_kw2="3", multiplier=4.0, repeat=1, func_after_dmg=stun_effect, func_damage_step=stun_amplify)            
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
        damage_dealt = self.attack(multiplier=4.0, repeat_seq=3, func_after_dmg=stun_effect, func_damage_step=stun_amplify, target_kw1="enemy_in_front")
        return damage_dealt

    def skill3(self):
        pass


class Olive(Character):     # Support
    def __init__(self, name, lvl, exp=0, equip=None, image=None):
        super().__init__(name, lvl, exp, equip, image)
        self.name = "Olive"
        self.skill1_description = "570% atk on 1 enemy with the highest atk. Decrease target's atk by 50% for 5 turns."
        self.skill2_description = "Heal 3 allies with lowest hp by 270% atk and increase their speed by 40% for 5 turns. "
        self.skill3_description = "Normal attack deals 100% more damage if target has less speed than self."
        self.skill1_cooldown_max = 4
        self.skill2_cooldown_max = 4

    def skill_tooltip(self):
        return f"Skill 1 : {self.skill1_description}\nCooldown : {self.skill1_cooldown} action(s)\n\nSkill 2 : {self.skill2_description}\nCooldown : {self.skill2_cooldown} action(s)\n\nSkill 3 : {self.skill3_description}\n"

    def skill1_logic(self):
        def effect(self, target):
            stat_dict = {"atk": 0.5}
            target.apply_effect(StatsEffect("Weaken", 5, False, stat_dict))
        damage_dealt = self.attack(multiplier=5.7, repeat=1, func_after_dmg=effect, target_kw1="n_highest_attr", target_kw2="1", target_kw3="atk", target_kw4="enemy")             
        return damage_dealt

    def skill2_logic(self):
        def effect(self, target, healing, overhealing):
            target.apply_effect(StatsEffect("Tailwind", 5, True, {"spd": 1.4}))
        healing_done = self.heal("n_lowest_attr", "3", "hp", "ally", self.atk * 2.7, 1, func_after_each_heal=effect)
        return None

    def skill3(self):
        pass

    def normal_attack(self):
        def effect(self, target, final_damage):
            if target.spd < self.spd:
                final_damage *= 2.00
            return final_damage
        self.attack(func_damage_step=effect)


class Fenrir(Character):    # Support
    def __init__(self, name, lvl, exp=0, equip=None, image=None):
        super().__init__(name, lvl, exp, equip, image)
        self.name = "Fenrir"
        self.skill1_description = "Focus attack 3 times on closest enemy, 220% atk each hit. Reduce skill cooldown for neighbor allies by 2 turns."
        self.skill2_description = "350% atk on a closest enemy. Remove 2 debuffs for neighbor allies."
        self.skill3_description = "Fluffy protection is applied to neighbor allies at start of battle. When the protected ally below 40% hp is about to take damage, the ally recovers hp by 100% of self base atk."
        self.skill1_cooldown_max = 5
        self.skill2_cooldown_max = 5

    def skill_tooltip(self):
        return f"Skill 1 : {self.skill1_description}\nCooldown : {self.skill1_cooldown} action(s)\n\nSkill 2 : {self.skill2_description}\nCooldown : {self.skill2_cooldown} action(s)\n\nSkill 3 : {self.skill3_description}\n"

    def skill1_logic(self):
        damage_dealt = self.attack(multiplier=2.2, repeat_seq=3, target_kw1="enemy_in_front")
        neighbors = self.get_neighbor_allies_not_including_self() # list
        for ally in neighbors:
            ally.skill1_cooldown = max(ally.skill1_cooldown - 2, 0)
            ally.skill2_cooldown = max(ally.skill2_cooldown - 2, 0)
            global_vars.turn_info_string += f"{ally.name} skill cooldown reduced by 2.\n"                 
        return damage_dealt

    def skill2_logic(self):
        damage_dealt = self.attack(multiplier=3.5, repeat=1, target_kw1="enemy_in_front")
        neighbors = self.get_neighbor_allies_not_including_self() # list
        for ally in neighbors:
            ally.remove_random_amount_of_debuffs(2)
        return damage_dealt
        
    def skill3(self):
        pass

    def battle_entry_effects(self):
        neighbors = self.get_neighbor_allies_not_including_self()
        for ally in neighbors:
            e = EffectShield1("Fluffy Protection", -1, True, 0.4, self.atk, False)
            e.can_be_removed_by_skill = False
            ally.apply_effect(e)


class Cerberus(Character):    # Damage dealer, non close targets, execution
    def __init__(self, name, lvl, exp=0, equip=None, image=None, execution_threshold=0.15):
        super().__init__(name, lvl, exp, equip, image)
        self.name = "Cerberus"
        self.execution_threshold = execution_threshold

        self.skill1_description = "5 hits on random enemies, 280% atk each hit. Decrease target's def by 12% for each hit. Effect last 7 turns."
        self.skill2_description = "Focus attack with 290% atk on 1 enemy with lowest hp for 3 times. If target hp is less then 15% during the attack, execute the target."
        self.skill3_description = "On sucessfully executing a target, increase execution threshold by 3%, recover 30% of maxhp and increase atk and critdmg by 30%."
        self.skill1_cooldown_max = 5
        self.skill2_cooldown_max = 5

    def clear_others(self):
        self.execution_threshold = 0.15

    def skill_tooltip(self):
        return f"Skill 1 : {self.skill1_description}\nCooldown : {self.skill1_cooldown} action(s)\n\nSkill 2 : {self.skill2_description}\nCooldown : {self.skill2_cooldown} action(s)\n\nSkill 3 : {self.skill3_description}\n\nExecution threshold : {self.execution_threshold*100}%"

    def skill1_logic(self):
        def effect(self, target):
            stat_dict = {"defense": 0.88}
            target.apply_effect(StatsEffect("Clawed", 7, False, stat_dict))
        damage_dealt = self.attack(multiplier=2.8, repeat=5, func_after_dmg=effect)             
        return damage_dealt

    def skill2_logic(self):
        def effect(self, target):
            # does not make sense to execute self
            if target is self:
                return
            if target.hp < target.maxhp * self.execution_threshold and not target.is_dead():
                target.take_bypass_status_effect_damage(target.hp, self)
                global_vars.turn_info_string += f"{target.name} is executed by {self.name}.\n"
                self.execution_threshold += 0.03
                self.heal_hp(self.maxhp * 0.3, self)
                stats_dict = {"atk": 1.3, "critdmg": 0.3}
                self.update_stats(stats_dict)
        damage_dealt = self.attack(target_kw1="n_lowest_attr",target_kw2="1",target_kw3="hp",target_kw4="enemy", multiplier=2.9, repeat=1, repeat_seq=3, func_after_dmg=effect)
        return damage_dealt

    def skill3(self):
        pass


class Pepper(Character):    # Support
    def __init__(self, name, lvl, exp=0, equip=None, image=None):
        super().__init__(name, lvl, exp, equip, image)
        self.name = "Pepper"
        self.skill1_description = "800% atk on closest enemy, 70% success rate, 20% chance to hit an ally with 300% atk," \
        " 10% chance to hit self with 300% atk. A failed attack resets cooldown, when targeting enemy, this attack cannot miss."
        self.skill2_description = "Heal an ally with lowest hp percentage with 800% atk, 70% success rate, 20% chance to have no effect, 10% chance to damage the ally with 200% atk. A failed healing resets cooldown."
        self.skill3_description = "On a successful healing with skill 2, 80% chance to accidently revive a neighbor ally with 80% hp."
        self.skill1_cooldown_max = 4
        self.skill2_cooldown_max = 4

    def skill_tooltip(self):
        return f"Skill 1 : {self.skill1_description}\nCooldown : {self.skill1_cooldown} action(s)\n\nSkill 2 : {self.skill2_description}\nCooldown : {self.skill2_cooldown} action(s)\n\nSkill 3 : {self.skill3_description}\n"

    def skill1(self):
        global_vars.turn_info_string += f"{self.name} cast skill 1.\n"
        if self.skill1_cooldown > 0:
            raise Exception
        dice = random.randint(1, 100)
        if dice <= 70:
            damage_dealt = self.attack(multiplier=8.0, repeat=1, target_kw1="enemy_in_front", always_hit=True)
            self.update_skill_cooldown(1)
        elif dice <= 90 and dice > 70:
            damage_dealt = self.attack(target_kw1="n_random_ally", target_kw2="1", multiplier=3.0, repeat=1)
            global_vars.turn_info_string += f"{self.name} damaged an ally by accident.\n"
            self.skill1_cooldown = 0
        else:
            damage_dealt = self.attack(target_kw1="yourself", multiplier=3.0, repeat=1)
            global_vars.turn_info_string += f"{self.name} damaged self by accident.\n"
            self.skill1_cooldown = 0
        if self.get_equipment_set() == "OldRusty" and random.random() < 0.65:
            global_vars.turn_info_string += f"skill cooldown is reset for {self.name} due to Old Rusty set effect.\n"
            self.skill1_cooldown = 0
        return damage_dealt

    def skill2(self):
        if self.skill2_cooldown > 0:
            raise Exception
        global_vars.turn_info_string += f"{self.name} cast skill 2.\n"
        target = mit.one(self.target_selection(keyword="n_lowest_attr", keyword2="1", keyword3="hp", keyword4="ally"))
        pondice = random.randint(1, 100)
        if pondice <= 70:
            self.heal(target_list=[target], value=self.atk * 8.0)
            revivedice = random.randint(1, 100)
            if revivedice <= 80:
                neighbors = self.get_neighbor_allies_not_including_self(False) 
                dead_neighbors = [x for x in neighbors if x.is_dead()]
                if dead_neighbors != []:
                    revive_target = random.choice(dead_neighbors)
                    revive_target.revive(1, 0.8)
        elif pondice <= 90 and pondice > 70:
            global_vars.turn_info_string += f"No effect! {self.name} failed to heal.\n"
            self.skill2_cooldown = 0
            return 0
        else:
            target.take_damage(self.atk * 2.0, self)
            global_vars.turn_info_string += f"{self.name} damaged {target.name} by accident.\n"
            self.skill2_cooldown = 0
            return 0
        self.update_skill_cooldown(2)
        return 0
        

    def skill3(self):
        pass


class Cliffe(Character):     # Damage dealer, close targets
    def __init__(self, name, lvl, exp=0, equip=None, image=None):
        super().__init__(name, lvl, exp, equip, image)
        self.name = "Cliffe"
        self.skill1_description = "Attack 3 closest enemies with 280% atk, increase their damage taken by 20% for 7 turns."
        self.skill2_description = "Attack closest enemy 4 times for 340% atk, each successful attack and successful additional attack has 40% chance to trigger an 270% atk additional attack."
        self.skill3_description = "Recover hp by 10% of maxhp multiplied by targets fallen by skill 2."
        self.skill1_cooldown_max = 5
        self.skill2_cooldown_max = 5

    def skill_tooltip(self):
        return f"Skill 1 : {self.skill1_description}\nCooldown : {self.skill1_cooldown} action(s)\n\nSkill 2 : {self.skill2_description}\nCooldown : {self.skill2_cooldown} action(s)\n\nSkill 3 : {self.skill3_description}\n"

    def skill1_logic(self):
        def effect(self, target):
            target.apply_effect(ReductionShield("Crystal Breaker", 7, False, 0.2, False))
        damage_dealt = self.attack(target_kw1="n_enemy_in_front",target_kw2="3", multiplier=2.8, repeat=1, func_after_dmg=effect)            
        return damage_dealt

    def skill2_logic(self):
        downed_target = 0
        def more_attacks(self, target, is_crit):
            nonlocal downed_target
            if target.is_dead():
                downed_target += 1
            dice = random.randint(1, 100)
            if dice <= 40:
                global_vars.turn_info_string += f"{self.name} triggered additional attack.\n"
                return self.attack(multiplier=2.7, repeat=1, additional_attack_after_dmg=more_attacks, target_kw1="enemy_in_front")
            else:
                return 0
        damage_dealt = self.attack(multiplier=3.4, repeat=4, additional_attack_after_dmg=more_attacks, target_kw1="enemy_in_front")      
        if downed_target > 0 and self.is_alive():
            self.heal_hp(downed_target * 0.1 * self.maxhp, self)
        return damage_dealt
        
    def skill3(self):
        pass


class Pheonix(Character):    # Support, damage dealer, non close targets, status damage
    def __init__(self, name, lvl, exp=0, equip=None, image=None):
        super().__init__(name, lvl, exp, equip, image)
        self.name = "Pheonix"
        self.skill1_description = "Attack all enemies with 190% atk, 80% chance to inflict burn for 8 turns. Burn deals 50% atk damage per turn."
        self.skill2_description = "First time cast: apply Reborn to all neighbor allies. however, allies can only revive with 25% hp " \
        "and receive no buff effects. Second and further cast: attack random enemy pair with 260% atk, 80% chance to inflict burn for 8 turns. " \
        "Burn deals 50% atk damage per turn."
        self.skill3_description = "Revive with 40% hp the next turn after fallen. When revived, increase atk by 50% for 5 turns." \
        " This effect cannot be removed by skill."
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
                target.apply_effect(ContinuousDamageEffect("Burn", 8, False, self.atk * 0.5, self))
        damage_dealt = self.attack(target_kw1="n_random_enemy",target_kw2="5", multiplier=1.9, repeat=1, func_after_dmg=burn_effect)         
        return damage_dealt

    def skill2_logic(self):
        if self.first_time:
            self.first_time = False
            allies = self.get_neighbor_allies_not_including_self()
            if not allies:
                return 0
            for ally in allies:
                ally.apply_effect(RebornEffect("Reborn", -1, True, 0.25, False))
            return 0
        else:
            def burn_effect(self, target):
                if random.randint(1, 100) <= 80:
                    target.apply_effect(ContinuousDamageEffect("Burn", 8, False, self.atk * 0.5, self))
            damage_dealt = self.attack(target_kw1="random_enemy_pair", multiplier=2.6, repeat=1, func_after_dmg=burn_effect)         
            return damage_dealt   

    def skill3(self):
        pass

    def after_revive(self):
        self.apply_effect(StatsEffect("Atk Up", 5, True, {"atk": 1.5}))

    def battle_entry_effects(self):
        e = RebornEffect("Reborn", -1, True, 0.4, False)
        e.can_be_removed_by_skill = False
        self.apply_effect(e)


class Tian(Character):    # Support, damage dealer
    def __init__(self, name, lvl, exp=0, equip=None, image=None):
        super().__init__(name, lvl, exp, equip, image)
        self.name = "Tian"
        self.skill1_description = "Attack 3 closest enemies with 460% atk and apply Dilemma for 4 turns. Dilemma: Critical chance is reduced by 70%."
        self.skill2_description = "Apply Soul Guard on self for 8 turns, Soul Guard: increase atk by 60% and damage reduction by 30%." \
        " Apply Sin to 1 enemy with highest atk for 7 turns. Sin: atk and critdmg is reduced by 30%," \
        " if defeated, all allies take status damage equal to 300% of self atk. This effect cannot be removed by skill."
        self.skill3_description = "Normal attack deals 120% more damage, before attacking, for 1 turn, increase critical chance by 80%."
        self.skill1_cooldown_max = 4
        self.skill2_cooldown_max = 5

    def skill_tooltip(self):
        return f"Skill 1 : {self.skill1_description}\nCooldown : {self.skill1_cooldown} action(s)\n\nSkill 2 : {self.skill2_description}\nCooldown : {self.skill2_cooldown} action(s)\n\nSkill 3 : {self.skill3_description}\n"

    def skill1_logic(self):
        def effect(self, target):
            target.apply_effect(StatsEffect("Dilemma", 4, False, {"crit": -0.7}))
        damage_dealt = self.attack(target_kw1="n_enemy_in_front",target_kw2="3", multiplier=4.6, repeat=1, func_after_dmg=effect)
        return damage_dealt

    def skill2_logic(self):
        self.apply_effect(StatsEffect("Soul Guard", 8, True, {"atk": 1.6, "final_damage_taken_multipler": -0.3}))
        target = mit.one(self.target_selection(keyword="n_highest_attr", keyword2="1", keyword3="atk", keyword4="enemy"))
        target.apply_effect(SinEffect("Sin", 6, False, target.atk * 3.0, {"atk": 0.7, "critdmg": -0.3}))
        return None

    def skill3(self):
        pass

    def normal_attack(self):
        self.apply_effect(StatsEffect("Critical Up", 1, True, {"crit": 0.8}))
        def effect(self, target, final_damage):
            final_damage *= 2.2
            return final_damage
        self.attack(func_damage_step=effect)


class Bell(Character):    # Damage dealer, close targets, multi strike, counter high damage
    def __init__(self, name, lvl, exp=0, equip=None, image=None):
        super().__init__(name, lvl, exp, equip, image)
        self.name = "Bell"
        self.skill1_description = "Attack 1 closest enemy with 190% atk 5 times."
        self.skill2_description = "Attack 1 closest enemy with 170% atk 6 times. This attack never misses. For each target fallen, trigger an additional attack. Maximum attacks: 8"
        self.skill3_description = "Once per battle, after taking damage, if hp is below 50%, apply absorption shield, absorb damage up to 400% of damage just taken. For 7 turns, damage taken cannot exceed 20% of maxhp."
        self.skill3_used = False
        self.skill1_cooldown_max = 5
        self.skill2_cooldown_max = 5

    def skill_tooltip(self):
        return f"Skill 1 : {self.skill1_description}\nCooldown : {self.skill1_cooldown} action(s)\n\nSkill 2 : {self.skill2_description}\nCooldown : {self.skill2_cooldown} action(s)\n\nSkill 3 : {self.skill3_description}\n"

    def clear_others(self):
        self.skill3_used = False

    def skill1_logic(self):
        damage_dealt = self.attack(target_kw1="enemy_in_front", multiplier=1.9, repeat=5)
        return damage_dealt

    def skill2_logic(self):
        downed_target = 0
        def additional_attacks(self, target, is_crit):
            nonlocal downed_target
            if target.is_dead() and downed_target < 3:
                downed_target += 1
                global_vars.turn_info_string += f"{self.name} triggered additional attack.\n"
                return self.attack(target_kw1="n_lowest_attr",target_kw2="1",target_kw3="hp",target_kw4="enemy", multiplier=1.7, repeat=1, additional_attack_after_dmg=additional_attacks, always_hit=True)
            else:
                return 0
        damage_dealt = self.attack(target_kw1="enemy_in_front", multiplier=1.7, repeat=6, additional_attack_after_dmg=additional_attacks, always_hit=True)
        return damage_dealt

    def skill3(self):
        pass

    def take_damage_aftermath(self, damage, attacker):
        if self.skill3_used:
            pass
        else:
            if self.hp < self.maxhp * 0.5:
                self.apply_effect(CancellationShield2("Cancellation Shield", 7, True, 0.2, False))
                self.apply_effect(AbsorptionShield("Shield", -1, True, damage * 4.0, cc_immunity=False))
                self.skill3_used = True
            return damage


class Taily(Character):    # Frontline, damage reduction, protect allies
    # A reference to a dead mobile game character
    def __init__(self, name, lvl, exp=0, equip=None, image=None):
        super().__init__(name, lvl, exp, equip, image)
        self.name = "Taily"
        self.skill1_description = "300% atk on 3 closest enemies, Stun the target for 2 turns."
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
        damage_dealt = self.attack(target_kw1="n_enemy_in_front",target_kw2="3", multiplier=3.0, repeat=1, func_after_dmg=stun_effect)
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
            e = ProtectedEffect("Blessing of Firewood", -1, True, False, self, 0.6)
            e.can_be_removed_by_skill = False
            ally.apply_effect(e)


class Seth(Character):    # Damage dealer, critical
    def __init__(self, name, lvl, exp=0, equip=None, image=None):
        super().__init__(name, lvl, exp, equip, image)
        self.name = "Seth"
        self.skill1_description = "Attack closest enemy 3 times with 280% atk. For each attack, a critical strike will trigger an additional attack. Maximum additional attacks: 3"
        self.skill2_description = "Attack all enemies with 250% atk."
        self.skill3_description = "Every turn, increase crit rate and crit dmg by 1%."
        self.skill1_cooldown_max = 5
        self.skill2_cooldown_max = 5

    def skill_tooltip(self):
        return f"Skill 1 : {self.skill1_description}\nCooldown : {self.skill1_cooldown} action(s)\n\nSkill 2 : {self.skill2_description}\nCooldown : {self.skill2_cooldown} action(s)\n\nSkill 3 : {self.skill3_description}\n"

    def skill1_logic(self):
        def additional_attack(self, target, is_crit):
            if is_crit:
                global_vars.turn_info_string += f"{self.name} triggered additional attack.\n"
                return self.attack(multiplier=2.8, repeat=1, target_kw1="enemy_in_front")
            else:
                return 0
        damage_dealt = self.attack(multiplier=2.8, repeat=3, additional_attack_after_dmg=additional_attack, target_kw1="enemy_in_front")
        return damage_dealt

    def skill2_logic(self):
        damage_dealt = self.attack(target_kw1="n_random_enemy",target_kw2="5", multiplier=2.5, repeat=1) 
        return damage_dealt
        
    def skill3(self):
        pass

    def battle_entry_effects(self):
        passive = SethEffect("Passive Effect", -1, True, 0.01)
        passive.can_be_removed_by_skill = False
        self.apply_effect(passive)


class Chiffon(Character):   # Support, healer, self damage reduction
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
            ally.apply_effect(AbsorptionShield("Woof! Woof! Woof!", 3, True, self.atk * 1.5, cc_immunity=False))
        return 0

    def skill2_logic(self):
        targets = list(self.target_selection(keyword="n_random_target", keyword2="5"))
        ally_list = []
        enemy_list = []
        for target in targets:
            if target in self.ally:
                ally_list.append(target)
            else:
                enemy_list.append(target)
        self.heal(target_list=ally_list, value=self.atk * 1.5)
        def sleep_effect(self, target):
            dice = random.randint(1, 100)
            if dice <= 50:
                target.apply_effect(SleepEffect('Sleep', duration=-1, is_buff=False))
        damage_dealt = self.attack(target_list=enemy_list, multiplier=4.0, repeat=1, func_after_dmg=sleep_effect)
        return damage_dealt
        
    def skill3(self):
        pass

    def battle_entry_effects(self):
        effect_shield = EffectShield2("Passive Effect", -1, True, False, damage_reduction=0.6)
        effect_shield.can_be_removed_by_skill = False
        self.apply_effect(effect_shield)


class Don(Character):   # Hybrid
    # No reference
    def __init__(self, name, lvl, exp=0, equip=None, image=None):
        super().__init__(name, lvl, exp, equip, image)
        self.name = "Don"
        self.skill1_description = "Target random enemy triple, remove 1 random buff effect and deal 333% atk damage," \
        " Apply absorption shield to self, absorb damage up to 50% of damage dealt for 8 turns."
        self.skill2_description = "Target random ally triple, heal hp by 333% atk," \
        " Apply absorption shield to ally with lowest hp, absorb damage up to 50% of healing for 8 turns."
        self.skill3_description = "At start of battle, for 15 turns, increase critical rate by 30% for neighbor allies."
        self.skill1_cooldown_max = 5
        self.skill2_cooldown_max = 5

    def skill_tooltip(self):
        return f"Skill 1 : {self.skill1_description}\nCooldown : {self.skill1_cooldown} action(s)\n\nSkill 2 : {self.skill2_description}\nCooldown : {self.skill2_cooldown} action(s)\n\nSkill 3 : {self.skill3_description}\n"

    def skill1_logic(self):
        targets = list(self.target_selection(keyword="random_enemy_triple"))
        for target in targets:
            target.remove_random_amount_of_buffs(1)
        damage_dealt = self.attack(target_list=targets, multiplier=3.33, repeat=1)
        if self.is_alive():
            self.apply_effect(AbsorptionShield("Shield", 8, True, damage_dealt * 0.5, cc_immunity=False))
        return damage_dealt

    def skill2_logic(self):
        targets = list(self.target_selection(keyword="random_ally_triple"))
        healing = self.heal(target_list=targets, value=self.atk * 3.33)
        lowest_hp_ally = min(targets, key=lambda x: x.hp)
        lowest_hp_ally.apply_effect(AbsorptionShield("Shield", 8, True, healing * 0.5, cc_immunity=False))
        return 0

    def skill3(self):
        pass

    def battle_entry_effects(self):
        neighbors = self.get_neighbor_allies_not_including_self()
        for ally in neighbors:
            ally.apply_effect(StatsEffect("Critical Up", 15, True, {"crit": 0.3}))


class Ophelia(Character):   # Damage dealer, non close targets, healer
    # A reference to a dead mobile game character
    def __init__(self, name, lvl, exp=0, equip=None, image=None):
        super().__init__(name, lvl, exp, equip, image)
        self.name = "Ophelia"
        self.skill1_description = "Attack 1 enemy with highest atk with 430% atk. Consumes a card in possession to gain an additional effect according to the card type." \
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
        global_vars.turn_info_string += f"{self.name} cast skill 1.\n"
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
        
        damage_dealt = self.attack(multiplier=4.3, repeat=1, func_after_dmg=card_effect, func_damage_step=card_amplify, target_kw1="n_highest_attr", target_kw2="1", target_kw3="atk", target_kw4="enemy")
        lucky_card_found = False
        for buff in self.buffs:
            if buff.name == "Luck Card":
                buff_to_remove_list.append(buff)
                lucky_card_found = True
                break
        self.buffs = [buff for buff in self.buffs if buff not in buff_to_remove_list]
        self.apply_effect(Effect("Death Card", -1, True, False, can_be_removed_by_skill=False))
        if lucky_card_found:
            self.skill1_cooldown = 0
        else:
            self.update_skill_cooldown(1)
        dice = random.randint(1, 100)
        if dice <= 30:
            self.apply_effect(Effect("Luck Card", -1, True, False, can_be_removed_by_skill=False))
            global_vars.turn_info_string += f"{self.name} gained Luck Card.\n"
        if self.get_equipment_set() == "OldRusty" and random.random() < 0.65:
            global_vars.turn_info_string += f"skill cooldown is reset for {self.name} due to Old Rusty set effect.\n"
            self.skill1_cooldown = 0
        return damage_dealt

    def skill2(self):
        global_vars.turn_info_string += f"{self.name} cast skill 2.\n"
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
                    self.heal(target_list=[ally], value=self.atk * 3.0)
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
        self.apply_effect(Effect("Love Card", -1, True, False, can_be_removed_by_skill=False))
        dice = random.randint(1, 100)
        if dice <= 30:
            self.apply_effect(Effect("Luck Card", -1, True, False, can_be_removed_by_skill=False))
            global_vars.turn_info_string += f"{self.name} gained Luck Card.\n"
        return 0
        
    def skill3(self):
        pass

    def normal_attack(self):
        def effect(self, target):
            # gain card
            dice = random.randint(1, 100)
            if dice <= 30:
                self.apply_effect(Effect("Luck Card", -1, True, False, can_be_removed_by_skill=False))
                global_vars.turn_info_string += f"{self.name} gained Luck Card.\n"
        self.attack(func_after_dmg=effect)


class Requina(Character):   # Damage dealer, close targets, status damage
    # A reference to a dead mobile game character
    def __init__(self, name, lvl, exp=0, equip=None, image=None):
        super().__init__(name, lvl, exp, equip, image)
        self.name = "Requina"
        self.skill1_description = "Attack 3 closest enemies with 300% atk, 50% chance to apply 6 stacks of Great Poison. 50% chance to apply 4 stacks." \
        " Each stack of Great Poison reduces atk, defense, heal efficiency by 1%, Each turn, deals 0.5% maxhp status damage. " \
        " Maximum stacks: 70." \
        " Effect last 7 turns. Same effect applied refreshes the duration."
        self.skill2_description = "Attack 2 closest enemies with 350% atk, if target has Great Poison, deal 50% more damage and apply 5 stacks of Great Poison."
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
        damage_dealt = self.attack(target_kw1="n_enemy_in_front",target_kw2="3", multiplier=3.0, repeat=1, func_after_dmg=effect)
        return damage_dealt

    def skill2_logic(self):
        def damage_step_effect(self, target, final_damage):
            if target.has_effect_that_named("Great Poison"):
                final_damage *= 1.5
                target.apply_effect(GreatPoisonEffect("Great Poison", 7, False, 0.005, {"atk": 1.00, "defense": 1.00, "heal_efficiency": 0.00}, self, 5))
            return final_damage
        damage_dealt = self.attack(target_kw1="n_enemy_in_front",target_kw2="2", multiplier=3.5, repeat=1, func_damage_step=damage_step_effect)
        return damage_dealt
        
    def skill3(self):
        pass

    def normal_attack(self):
        def effect(self, target):
            dice = random.randint(1, 100)
            if dice <= 80:
                target.apply_effect(GreatPoisonEffect("Great Poison", 7, False, 0.005, {"atk": 1.00, "defense": 1.00, "heal_efficiency": 0.00}, self, 1))
        self.attack(func_after_dmg=effect)


class Dophine(Character):   # Damage dealer, closest target
    # No reference
    def __init__(self, name, lvl, exp=0, equip=None, image=None):
        super().__init__(name, lvl, exp, equip, image)
        self.name = "Dophine"
        self.skill1_description = "Attack closest enemy with 300% atk 3 times. All attacks become critical strikes after one critical strike."
        self.skill2_description = "Attack closest enemy with 280% atk 4 times. After one critical strike, the following attacks deals 50% more damage."
        self.skill3_description = "Before skill attack, if hp is below 50%, increase critical rate by 30% for 1 turn."
        self.skill1_cooldown_max = 5
        self.skill2_cooldown_max = 5

    def skill_tooltip(self):
        return f"Skill 1 : {self.skill1_description}\nCooldown : {self.skill1_cooldown} action(s)\n\nSkill 2 : {self.skill2_description}\nCooldown : {self.skill2_cooldown} action(s)\n\nSkill 3 : {self.skill3_description}\n"

    def skill1_logic(self):
        if self.hp < self.maxhp * 0.5:
            self.apply_effect(StatsEffect("Critical Rate Up", 1, True, {"crit": 0.3}))
        def crit_effect(self, target, final_damage, always_crit):
            always_crit = True
            return final_damage, always_crit
        damage_dealt = self.attack(target_kw1="enemy_in_front", multiplier=3.0, repeat=3, func_after_crit=crit_effect)
        return damage_dealt

    def skill2_logic(self):
        if self.hp < self.maxhp * 0.5:
            self.apply_effect(StatsEffect("Critical Rate Up", 1, True, {"crit": 0.3}))
        crit_count = 0
        def crit_effect(self, target, final_damage, always_crit):
            nonlocal crit_count
            crit_count += 1
            return final_damage, always_crit
        def damage_step_effect(self, target, final_damage):
            if crit_count > 0:
                final_damage *= 1 + 0.5 * crit_count
            return final_damage
        damage_dealt = self.attack(target_kw1="enemy_in_front", multiplier=2.8, repeat=4, func_after_crit=crit_effect, func_damage_step=damage_step_effect)
        return damage_dealt

    def skill3(self):
        pass


class Gabe(Character):    # Damage dealer, close targets, status damage, special
    # skill is a reference to yu-gi-oh card
    def __init__(self, name, lvl, exp=0, equip=None, image=None):
        super().__init__(name, lvl, exp, equip, image)
        self.name = "Gabe"
        self.skill1_description = "Attack 3 closeset enemies with 420% atk. Damage increases by 20% if target has New Year Fireworks effect."
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
        damage_dealt = self.attack(target_kw1="n_enemy_in_front",target_kw2="3", multiplier=4.2, repeat=1, func_damage_step=damage_amplify)
        return damage_dealt

    def skill2_logic(self):
        self.apply_effect(NewYearFireworksEffect("New Year Fireworks", -1, False, 6, self))
        self.apply_effect(NewYearFireworksEffect("New Year Fireworks", -1, False, 6, self))
        self.apply_effect(NewYearFireworksEffect("New Year Fireworks", -1, False, 6, self))
        self.apply_effect(NewYearFireworksEffect("New Year Fireworks", -1, False, 6, self))
        for fireworks in self.debuffs:
            if fireworks.name == "New Year Fireworks":
                fireworks.apply_effect_on_trigger(self)
        if self.is_alive():
            self.heal(target_kw1="yourself", value=self.atk * 4.0)
        return 0
        
    def skill3(self):
        pass

    def fake_dice(self, sides=6, weights=None):
        if sides == 6:
            weights = [100, 100, 100, 100, 100, 50]
        return super().fake_dice(sides, weights)


class Yuri(Character):    # Damage dealer, close targets, normal attack, special
    # A reference to a dead game character
    def __init__(self, name, lvl, exp=0, equip=None, image=None):
        super().__init__(name, lvl, exp, equip, image)
        self.name = "Yuri"
        self.skill1_description = "Summon Bear, Wolf, Eagle, Cat in order. Normal attack gain additional effects according to the summon." \
        " Bear: 20% chance to Stun for 2 turns, normal attack damage increases by 100%." \
        " Wolf: Normal attack attack 3 closest enemies, each attack has 40% chance to inflict burn for 5 turns. Burn deals 50% atk status damage per turn." \
        " Eagle: Each Normal attack gains 4 additional focus attacks on the same target, each attack deals 150% atk damage." \
        " Cat: After normal attack, an ally with highest atk gains 'Gold Card' effect for 6 turns. Gold Card: atk, def, critical damage is increased by 30%." \
        " After 4 summons above, this skill cannot be used."
        self.skill2_description = "This skill cannot be used. For each summon, gain buff effect for 12 turns." \
        " Bear: atk increased by 40%." \
        " Wolf: critical rate increased by 40%." \
        " Eagle: speed increased by 40%." \
        " Cat: heal efficiency increased by 40%."
        self.skill3_description = "Normal attack targets closest enemy."
        self.skill1_cooldown_max = 2
        self.skill2_cooldown_max = 0
        self.bt_bear = False
        self.bt_wolf = False
        self.bt_eagle = False
        self.bt_cat = False
        self.skill2_can_be_used = False

    def clear_others(self):
        self.bt_bear = False
        self.bt_wolf = False
        self.bt_eagle = False
        self.bt_cat = False
        self.skill2_can_be_used = False

    def status_effects_at_end_of_turn(self):
        if self.skill1_can_be_used and self.bt_bear and self.bt_wolf and self.bt_eagle and self.bt_cat:
            self.skill1_can_be_used = False
        super().status_effects_at_end_of_turn()

    def skill_tooltip(self):
        return f"Skill 1 : {self.skill1_description}\nCooldown : {self.skill1_cooldown} action(s)\n\nSkill 2 : {self.skill2_description}\nCooldown : {self.skill2_cooldown} action(s)\n\nSkill 3 : {self.skill3_description}\n"

    def skill1_logic(self):
        match (self.bt_bear, self.bt_wolf, self.bt_eagle, self.bt_cat) :
            case (False, False, False, False):
                bear_effect = Effect("Bear", -1, True, False)
                bear_effect.can_be_removed_by_skill = False
                self.apply_effect(bear_effect)
                global_vars.turn_info_string += f"{self.name} summoned Bear.\n"
                self.bt_bear = True
                self.apply_effect(StatsEffect("Bear", 12, True, {"atk": 1.40}))
                return 0
            case (True, False, False, False):
                wolf_effect = Effect("Wolf", -1, True, False)
                wolf_effect.can_be_removed_by_skill = False
                self.apply_effect(wolf_effect)
                global_vars.turn_info_string += f"{self.name} summoned Wolf.\n"
                self.bt_wolf = True
                self.apply_effect(StatsEffect("Wolf", 12, True, {"crit": 0.40}))
                return 0
            case (True, True, False, False):
                eagle_effect = Effect("Eagle", -1, True, False)
                eagle_effect.can_be_removed_by_skill = False
                self.apply_effect(eagle_effect)
                global_vars.turn_info_string += f"{self.name} summoned Eagle.\n"
                self.bt_eagle = True
                self.apply_effect(StatsEffect("Eagle", 12, True, {"spd": 1.40}))
                return 0
            case (True, True, True, False):
                cat_effect = Effect("Cat", -1, True, False)
                cat_effect.can_be_removed_by_skill = False
                self.apply_effect(cat_effect)
                global_vars.turn_info_string += f"{self.name} summoned Cat.\n"
                self.bt_cat = True
                self.apply_effect(StatsEffect("Cat", 12, True, {"heal_efficiency": 0.40}))
                return 0
            case (True, True, True, True):
                raise Exception("Skill can not be used. Should be already handled in status_effects_at_end_of_turn")
            case (_, _, _, _):
                raise Exception("Invalid state")

    def skill2_logic(self):
        return 0
        
    def skill3(self):
        pass

    def normal_attack(self):
        match (self.bt_bear, self.bt_wolf, self.bt_eagle, self.bt_cat) :

            case (False, False, False, False):
                return super().normal_attack()
            
            case (True, False, False, False):
                def stun_effect(self, target):
                    dice = random.randint(1, 100)
                    if dice <= 20:
                        target.apply_effect(StunEffect('Stun', duration=2, is_buff=False))
                def damage_amplify(self, target, final_damage):
                    final_damage *= 2.0
                    return final_damage
                damage_dealt = self.attack(target_kw1="enemy_in_front", multiplier=2.0, repeat=1, func_after_dmg=stun_effect, 
                                           func_damage_step=damage_amplify)
                return damage_dealt
            
            case (True, True, False, False):
                def extra_effect(self, target):
                    dice = random.randint(1, 100)
                    if dice <= 20:
                        target.apply_effect(StunEffect('Stun', duration=2, is_buff=False))
                    dice = random.randint(1, 100)
                    if dice <= 40:
                        target.apply_effect(ContinuousDamageEffect("Burn", 4, False, self.atk * 0.5, self))
                def damage_amplify(self, target, final_damage):
                    final_damage *= 2.0
                    return final_damage
                damage_dealt = self.attack(target_kw1="n_enemy_in_front", multiplier=2.0, repeat=1, func_after_dmg=extra_effect, 
                                           func_damage_step=damage_amplify, target_kw2="3")
                return damage_dealt
            
            case (True, True, True, False):
                def extra_effect(self, target):
                    dice = random.randint(1, 100)
                    if dice <= 20:
                        target.apply_effect(StunEffect('Stun', duration=2, is_buff=False))
                    dice = random.randint(1, 100)
                    if dice <= 40:
                        target.apply_effect(ContinuousDamageEffect("Burn", 5, False, self.atk * 0.5, self))
                def damage_amplify(self, target, final_damage):
                    final_damage *= 2.0
                    return final_damage
                def additional_attacks(self, target, is_crit):
                    return self.attack(multiplier=1.5, repeat_seq=4, target_list=[target])
                damage_dealt = self.attack(target_kw1="n_enemy_in_front", multiplier=2.0, repeat=1, func_after_dmg=extra_effect, 
                                           func_damage_step=damage_amplify, target_kw2="3", additional_attack_after_dmg=additional_attacks)
                return damage_dealt
            
            case (True, True, True, True):
                def extra_effect(self, target):
                    dice = random.randint(1, 100)
                    if dice <= 20:
                        target.apply_effect(StunEffect('Stun', duration=2, is_buff=False))
                    dice = random.randint(1, 100)
                    if dice <= 40:
                        target.apply_effect(ContinuousDamageEffect("Burn", 5, False, self.atk * 0.5, self))
                def damage_amplify(self, target, final_damage):
                    final_damage *= 2.0
                    return final_damage
                def additional_attacks(self, target, is_crit):
                    global_vars.turn_info_string += f"{self.name} triggered additional attack.\n"
                    return self.attack(multiplier=1.5, repeat_seq=4, target_list=[target])
                damage_dealt = self.attack(target_kw1="n_enemy_in_front", multiplier=2.0, repeat=1, func_after_dmg=extra_effect, 
                                           func_damage_step=damage_amplify, target_kw2="3", additional_attack_after_dmg=additional_attacks)
                if self.is_alive():
                    gold_card = StatsEffect("Gold Card", 6, True, {"atk": 1.3, "defense": 1.3, "critdmg": 0.3})
                    gold_card.additional_name = "bt_gold_card"
                    ally_to_gold_card = mit.one(self.target_selection(keyword="n_highest_attr", keyword2="1", keyword3="atk", keyword4="ally"))
                    ally_to_gold_card.apply_effect(gold_card)
                    global_vars.turn_info_string += f"{ally_to_gold_card.name} gained Gold Card.\n"

                return damage_dealt
            
            case (_, _, _, _):
                raise Exception("Invalid state")