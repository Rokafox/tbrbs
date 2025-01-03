import bisect
from collections.abc import Callable
import copy, random
import re
from typing import Generator, Tuple
from numpy import character
from effect import AbsorptionShield, AntiMultiStrikeReductionShield, BirdShadowEffect, BubbleWorldEffect, CancellationShield, CocoaSleepEffect, ConfuseEffect, ContinuousDamageEffect, ContinuousDamageEffect_Poison, ContinuousHealEffect, CupidLeadArrowEffect, DamageReflect, DamageTypeConvertionEffect, DecayEffect, DurationBonusEffect, EastBoilingWaterEffect, Effect, EffectShield1, EffectShield1_healoncrit, EffectShield2, EffectShield2_HealonDamage, EquipmentSetEffect_Arasaka, EquipmentSetEffect_Bamboo, EquipmentSetEffect_Dawn, EquipmentSetEffect_Flute, EquipmentSetEffect_Freight, EquipmentSetEffect_Grassland, EquipmentSetEffect_KangTao, EquipmentSetEffect_Liquidation, EquipmentSetEffect_Militech, EquipmentSetEffect_NUSA, EquipmentSetEffect_Newspaper, EquipmentSetEffect_OldRusty, EquipmentSetEffect_Purplestar, EquipmentSetEffect_Rainbow, EquipmentSetEffect_Rose, EquipmentSetEffect_Runic, EquipmentSetEffect_Snowflake, EquipmentSetEffect_Sovereign, EquipmentSetEffect_Tigris, FallingPetalEffect, FreyaDuckySilenceEffect, FriendlyFireShield, FrozenEffect, HideEffect, LesterBookofMemoryEffect, LesterExcitingTimeEffect, LuFlappingSoundEffect, NewYearFireworksEffect, NotTakingDamageEffect, OverhealEffect, PineQCEffect, PineQGEffect, ProtectedEffect, RebornEffect, ReductionShield, RenkaEffect, RequinaGreatPoisonEffect, ReservedEffect, ResolveEffect, RikaResolveEffect, ShintouEffect, SilenceEffect, SinEffect, SleepEffect, SmittenEffect, StatsEffect, StingEffect, StunEffect, TauntEffect, UlricInCloudEffect
from equip import Equip, generate_equips_list, adventure_generate_random_equip_with_weight
import more_itertools as mit
import itertools
import global_vars


class Character:
    def __init__(self, name, lvl, exp=0, equip=None, image=None):
        if equip is None:
            equip: dict[str, Equip] = {} # {str Equip.type: Equip}
        if equip is not None and not isinstance(equip, dict):
            raise Exception("Equip must be a dict.")
        self.name = name
        self.lvl = lvl
        self.lvl_max = 1000
        self.exp = exp
        self.equip = equip
        self.image: list['pygame'.Surface] = [] if image is None else image # list of pygame.Surface
        self.initialize_stats()
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
        self.additive_main_stats = [] # A list of dict.
        # Used by update_main_stats_additive, allowing additive stats changes. 
        # Only "maxhp", "hp", "atk", "defense", "spd" is allowed in the dict record.
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
        self.buffs: list[Effect] = []
        self.debuffs: list[Effect] = []
        self.ally: list[Character] = [] if resetally else self.ally
        self.enemy: list[Character] = [] if resetenemy else self.enemy
        self.party: list[Character] = [] if resetally and resetenemy else self.party
        self.enemyparty: list[Character] = [] if resetally and resetenemy else self.enemyparty
        self.calculate_equip_effect(resethp=resethp)
        self.eq_set = self.get_equipment_set()
        self.skill1_cooldown = 0
        self.skill2_cooldown = 0
        self.skill1_can_be_used = True
        self.skill2_can_be_used = True
        self.damage_taken_this_turn: list[tuple[int, Character, str]] = []
        # list of tuples (damage, attacker, dt), damage is int, attacker is Character object, dt is damage type
        # useful for recording damage taken sequence for certain effects
        self.damage_taken_history: list[list[tuple[int, Character, str]]] = [] # list of self.damage_taken_this_turn
        self.healing_received_this_turn = [] # list of tuples (healing, healer), healing is int, healer is Character object
        self.healing_received_history = [] # list of self.healing_received_this_turn

        self.battle_entry = False if reset_battle_entry else self.battle_entry
        self.number_of_attacks = 0 # counts how many attacks the character has made
        self.battle_turns = 0 # counts how many turns the character has been in battle
        self.number_of_take_downs: int = 0 # counts how many enemies the character has taken down
        self.have_taken_action: bool = False # whether the character has taken action in the battle
        self.multiple_target_selection_targets_missing = 0
        self.is_in_iteration_of_status_effects_midturn = False
        self.is_in_iteration_of_status_effects_startturn = False
        self.damage_type_during_attack_method: str = "undefined" # "normal", "status", "bypass", "undefined"
        # When applying buffs, the bonus value is added in apply_effect method, can be negative.
        self.duration_bonus_when_apply_effect_buff: int = 0 
        self.duration_bonus_when_apply_effect_debuff: int = 0

        if self.equip:
            for item in self.equip.values():
                item.owner = self.name

        self.clear_others()

    def reset_stats(self, resethp=True, resetally=True, resetenemy=True, reset_battle_entry=True):
        self.initialize_stats(resethp, resetally, resetenemy, reset_battle_entry)

    def get_self_index(self):
        """
        Get the index of self in the self party.
        """
        for i, char in enumerate(self.party):
            if char == self:
                return i

    def record_damage_taken(self) -> bool: 
        if self.damage_taken_this_turn: # not []
            # we will also return False if the damage is zero.
            # the return value of this method is mainly used for drawing the graph every turn, so the return value will decide
            # whether the graph will be drawn or not, this is important for performance.
            for d, _, _ in self.damage_taken_this_turn:
                if d > 0:
                    return_value = True
                elif d < 0:
                    raise Exception("Negative damage taken recorded.")
                else:
                    return_value = False
        else:
            return_value = False

        self.damage_taken_history.append(self.damage_taken_this_turn)
        self.damage_taken_this_turn = []
        return return_value

    def record_healing_received(self) -> bool: 
        if self.healing_received_this_turn:
            for h, _ in self.healing_received_this_turn:
                if h > 0:
                    return_value = True
                elif h < 0:
                    raise Exception("Negative healing received recorded.")
                else:
                    return_value = False
        else:
            return_value = False
        self.healing_received_history.append(self.healing_received_this_turn)
        self.healing_received_this_turn = []
        return return_value

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
            # print(self.equip)
            # {'Weapon': <equip.Equip object at 0x79335ff22360>, 
            # 'Armor': <equip.Equip object at 0x79331fb83e90>, 
            # 'Accessory': <equip.Equip object at 0x79331f132030>, 
            # 'Boots': <equip.Equip object at 0x79331f132120>}
            for item in self.equip.values():
                self.maxhp += item.maxhp_flat
                self.atk += item.atk_flat
                self.defense += item.def_flat
                self.spd += item.spd_flat

                self.eva += item.eva
                self.acc += item.acc
                self.crit += item.crit
                self.critdmg += item.critdmg
                self.critdef += item.critdef
                self.penetration += item.penetration
                self.heal_efficiency += item.heal_efficiency

            for item in self.equip.values():
                self.maxhp *= 1 + item.maxhp_percent
                self.maxhp = int(self.maxhp)
                self.atk *= 1 + item.atk_percent
                self.defense *= 1 + item.def_percent
                self.spd *= 1 + item.spd

            for item in self.equip.values():
                self.maxhp += int(item.maxhp_extra)
                self.atk += item.atk_extra
                self.defense += item.def_extra
                self.spd += item.spd_extra


            if resethp and self.hp < self.maxhp:
                self.hp = self.maxhp
            if self.hp > self.maxhp:
                self.hp = self.maxhp
            self.set_up_equipment_set_effects()
        return self.equip

    def clear_others(self):
        pass

    def update_skill_cooldown(self, skill):
        """
        Set the cooldown of the skill to its maximum value allowed.
        """
        match skill:
            case 1:
                self.skill1_cooldown = self.skill1_cooldown_max
            case 2:
                self.skill2_cooldown = self.skill2_cooldown_max
            case _:
                raise Exception("Invalid skill number.")

    def normal_attack(self):
        self.attack()

    def skill1(self, update_skillcooldown=True):
        # Warning: Following characters have their own skill1 function:
        # Pepper, Ophelia
        global_vars.turn_info_string += f"{self.name} cast skill 1.\n"
        if self.skill1_cooldown > 0:
            raise Exception
        damage_dealt = self.skill1_logic()
        if update_skillcooldown:
            self.update_skill_cooldown(1)
        if self.get_equipment_set() == "OldRusty" and random.random() < 0.65:
            global_vars.turn_info_string += f"skill cooldown is reset for {self.name} due to Old Rusty set effect.\n"
            self.skill1_cooldown = 0
        return None # for now

    def skill2(self, update_skillcooldown=True):
        # Warning: Following characters have their own skill2 function:
        # Pepper, Ophelia
        global_vars.turn_info_string += f"{self.name} cast skill 2.\n"
        if self.skill2_cooldown > 0:
            raise Exception
        damage_dealt = self.skill2_logic()
        if update_skillcooldown:
            self.update_skill_cooldown(2)
        if self.get_equipment_set() == "Purplestar" and random.random() < 0.85:
            global_vars.turn_info_string += f"skill cooldown is reset for {self.name} due to Purplestar set effect.\n"
            self.skill2_cooldown = 0
        return None # for now
    
    def skill1_logic(self):
        pass

    def skill2_logic(self):
        pass


    def target_selection(self, keyword: str = "Undefined", keyword2: str = "Undefined", keyword3: str = "Undefined", keyword4: str = "Undefined", target_list: list | None = None) -> Generator['Character', None, None]:
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
                # NOTE: We need to handle cases when there are no enemies left,
                # this heppens when all enemies are defeated, but the battle is not over yet because of Reborn effect
                yield random.choice(ts_available_enemy)

            case ("n_random_enemy", n, _, _):
                n = int(n)
                if n >= 5:
                    self.multiple_target_selection_targets_missing = 5 - len(self.enemy)
                    yield from self.enemy
                else:
                    if n > len(ts_available_enemy):
                        n = len(ts_available_enemy)
                    self.multiple_target_selection_targets_missing = n - len(ts_available_enemy)
                    yield from random.sample(ts_available_enemy, n)

            case ("n_random_ally", n, _, _):
                n = int(n)
                if n > len(self.ally):
                    n = len(self.ally)
                yield from random.sample(self.ally, n)

            case ("all_enemy", _, _, _) | ("all_enemies", _, _, _):
                self.multiple_target_selection_targets_missing = 5 - len(self.enemy)
                yield from self.enemy

            case ("all_ally", _, _, _) | ("all_allies", _, _, _):
                yield from self.ally

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
                    self.multiple_target_selection_targets_missing = n - len(ts_available_enemy)
                    yield from sorted(ts_available_enemy, key=lambda x: getattr(x, attr))[:n]

            case ("n_highest_attr", n, attr, party):
                n = int(n)
                if party == "ally":
                    yield from sorted(self.ally, key=lambda x: getattr(x, attr), reverse=True)[:n]
                elif party == "enemy":
                    self.multiple_target_selection_targets_missing = n - len(ts_available_enemy)
                    yield from sorted(ts_available_enemy, key=lambda x: getattr(x, attr), reverse=True)[:n]

            case ("enemy_that_must_have_effect", effect_name, _, _):
                yield from filter(lambda x: x.has_effect_that_named(effect_name), ts_available_enemy)

            case ("enemy_that_must_have_effect_full", effect_name, additional_name, class_name):
                if additional_name == "None":
                    additional_name = None
                if effect_name == "None":
                    effect_name = None
                if class_name == "None":
                    class_name = None
                yield from filter(lambda x: x.has_effect_that_named(effect_name, additional_name, class_name), ts_available_enemy)

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

            case ("ally_that_must_have_effect", effect_name, _, _):
                yield from filter(lambda x: x.has_effect_that_named(effect_name), self.ally)

            case ("ally_that_must_have_effect_full", effect_name, additional_name, class_name):
                if additional_name == "None":
                    additional_name = None
                if effect_name == "None":
                    effect_name = None
                if class_name == "None":
                    class_name = None
                yield from filter(lambda x: x.has_effect_that_named(effect_name, additional_name, class_name), self.ally)

            case ("n_enemy_with_most_buffs", n, _, _):
                n = int(n)
                self.multiple_target_selection_targets_missing = n - len(ts_available_enemy)
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
                    self.multiple_target_selection_targets_missing = n - len(ts_available_enemy)
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
                    self.multiple_target_selection_targets_missing = n - len(ts_available_enemy)
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
                self.multiple_target_selection_targets_missing = n - len(ts_available_enemy)
                yield from sorted(ts_available_enemy, key=lambda x: x.hp/x.maxhp)[:n]

            case ("n_highest_hp_percentage_ally", n, _, _):
                n = int(n)
                yield from sorted(self.ally, key=lambda x: x.hp/x.maxhp, reverse=True)[:n]

            case ("n_highest_hp_percentage_enemy", n, _, _):
                n = int(n)
                self.multiple_target_selection_targets_missing = n - len(ts_available_enemy)
                yield from sorted(ts_available_enemy, key=lambda x: x.hp/x.maxhp, reverse=True)[:n]

            case ("n_dead_allies", n, _, _):
                n = int(n)
                yield from mit.take(n, filter(lambda x: x.is_dead(), self.party))

            case ("n_dead_enemies", n, _, _):
                n = int(n)
                yield from mit.take(n, filter(lambda x: x.is_dead(), self.enemyparty))

            case ("random_enemy_pair", _, _, _):
                if len(ts_available_enemy) < 2:
                    self.multiple_target_selection_targets_missing = 2 - len(ts_available_enemy)
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
                    self.multiple_target_selection_targets_missing = 3 - len(ts_available_enemy)
                    yield from ts_available_enemy
                else:
                    yield from random.choice(list(mit.triplewise(ts_available_enemy)))

            case ("random_ally_triple", _, _, _):
                if len(self.ally) < 3:
                    yield from self.ally
                else:
                    yield from random.choice(list(mit.triplewise(self.ally)))

            case ("furthest_ally", _, _, _):
                if self.ally:
                    fat_d_t = []  # list of tuples (ally, distance to self)
                    for fat_a in self.ally:
                        fat_d_t.append((fat_a, abs(self.get_self_index() - fat_a.get_self_index())))
                    fat_d_t = sorted(fat_d_t, key=lambda x: x[1], reverse=True)
                    yield fat_d_t[0][0]

            case ("n_furthest_ally", n, _, _):
                n = int(n)
                if self.ally:
                    if n > len(self.ally):
                        n = len(self.ally)
                    nfat_d_t = []  # list of tuples (ally, distance to self)
                    for nfat_a in self.ally:
                        nfat_d_t.append((nfat_a, abs(self.get_self_index() - nfat_a.get_self_index())))
                    nfat_d_t = sorted(nfat_d_t, key=lambda x: x[1], reverse=True)
                    yield from [nfat_d_t[i][0] for i in range(n)]

            case ("Undefined_ally", _, _, _):
                yield random.choice(self.ally)

            case ("Undefined_target", _, _, _):
                yield random.choice(self.ally + ts_available_enemy)

            case (_, _, _, _):
                raise Exception(f"Keyword not found. Keyword: {keyword}, Keyword2: {keyword2}, Keyword3: {keyword3}, Keyword4: {keyword4}")


    def attack(self, 
            target_kw1: str = "Undefined", 
            target_kw2: str = "Undefined", 
            target_kw3: str = "Undefined", 
            target_kw4: str = "Undefined", 
            multiplier: float = 2.0, 
            repeat: int = 1, 
            func_after_dmg: Callable[[character, character], None] | None = None,
            func_damage_step: Callable[[character, character, float], float] | None = None,
            repeat_seq: int = 1, 
            func_after_miss: Callable[[character, character], None] | None = None,
            func_after_crit: Callable[[character, character, float, bool], Tuple[float, bool]] | None = None,
            always_crit: bool = False, 
            additional_attack_after_dmg: Callable[[character, character, bool], int] | None = None,
            always_hit: bool = False, 
            target_list: list | None = None,
            force_dmg: float | None = None, 
            ignore_protected_effect: bool = False,
            damage_type: str = "normal",
            damage_is_based_on: str | None = None, 
            can_be_lethal: bool = True,
            func_for_multiplier: Callable[[character, character, int, int], float] | None = None) -> int:
        """
        -> damage_dealt
        WARNING: DO NOT MESS WITH [repeat] AND [repeat_seq] TOGETHER, otherwise the result will be confusing.
        use [repeat] for attacking [repeat] times, use [repeat_seq] for focusing on one target for [repeat_seq] times.
        If [func_for_multiplier] is not None, [multiplier] will be overwritten by the return value of [func_for_multiplier].
        [func_for_multiplier] takes in (attacker, target, number_of_attacks, current_repeat) -> float
        """
        if damage_is_based_on is None:
            damage_is_based_on = self.atk
        elif damage_is_based_on == "maxhp":
            damage_is_based_on = self.maxhp
        elif damage_is_based_on == "hp":
            damage_is_based_on = self.hp
        elif damage_is_based_on == "defense" or damage_is_based_on == "def":
            damage_is_based_on = self.defense
        elif damage_is_based_on == "spd" or damage_is_based_on == "speed":
            damage_is_based_on = self.spd
        else:
            raise Exception("Invalid damage_is_based_on.")

        damage_dealt = 0
        self.multiple_target_selection_targets_missing = 0
        attacker_eq_set = self.get_equipment_set()

        for i in range(repeat):
            if repeat > 1 and i > 0:
                self.update_ally_and_enemy()
            try:
                attack_sequence = list(self.target_selection(target_kw1, target_kw2, target_kw3, target_kw4, target_list))
            except IndexError as e:
                # This should only happen in multistrike, where all targets is fallen and repeat is not exhausted
                # Maybe there is a better solution, just leave it for now
                # if repeat > 1 and not self.enemy:
                if not self.enemy:
                    break
                else:
                    raise e
            if repeat_seq > 1:
                # attack_sequence = list(mit.repeat_each(attack_sequence, repeat_seq))
                attack_sequence: list[Character] = list(mit.repeat_each(attack_sequence, repeat_seq))
            for target in attack_sequence:
                if target.is_dead():
                    continue
                if self.is_dead():
                    break
                if not self.can_take_action():
                    break
                global_vars.turn_info_string += f"{self.name} is targeting {target.name}.\n"
                if not force_dmg and func_for_multiplier is not None:
                    multiplier = func_for_multiplier(self, target, self.number_of_attacks, i) # multiplier is overwritten.
                damage = damage_is_based_on * multiplier - target.defense * (1 - self.penetration) if not force_dmg else force_dmg
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
                        if attacker_eq_set == "Runic" and self.crit > 1.0:
                            crit_over = self.crit - 1.0
                            global_vars.turn_info_string += f"Damage increased by {crit_over * 100:.2f}% due to Runic Set effect.\n"
                            final_damage *= 1 + crit_over
                        if func_after_crit is not None: # Warning: this function may be called multiple times
                            final_damage, always_crit = func_after_crit(self, target, final_damage, always_crit)
                    else:
                        final_damage = damage
                    final_damage *= random.uniform(0.8, 1.2)
                    if func_damage_step is not None:
                        final_damage = func_damage_step(self, target, final_damage)
                    for eff in self.buffs.copy() + self.debuffs.copy():
                        final_damage = eff.apply_effect_in_attack_before_damage_step(self, target, final_damage)
                    if attacker_eq_set == "Rainbow":
                        rainbow_amplifier_dict = {0: 1.60, 1: 1.35, 2: 1.10, 3: 0.85, 4: 0.60}
                        self_target_index_diff = self.get_self_index() - target.get_self_index()
                        self_target_index_diff = abs(self_target_index_diff)
                        final_damage *= rainbow_amplifier_dict[self_target_index_diff]
                    elif attacker_eq_set == "Dawn":
                        if self.get_effect_that_named("Dawn Set", None, "EquipmentSetEffect_Dawn").flag_onetime_damage_bonus_active:
                            final_damage *= 2.20
                            global_vars.turn_info_string += f"Damage increased by 120% due to Dawn Set effect.\n"
                            self.get_effect_that_named("Dawn Set", None, "EquipmentSetEffect_Dawn").flag_onetime_damage_bonus_active = False
                    elif attacker_eq_set == "Newspaper":
                        # if the enemy has more maxhp then self, damage is increased by 15% of the maxhp difference.
                        if target.maxhp > self.maxhp:
                            newspaper_effect_maxhp_diff = (target.maxhp - self.maxhp) * 0.15
                            final_damage += newspaper_effect_maxhp_diff
                            global_vars.turn_info_string += f"Damage increased by {newspaper_effect_maxhp_diff} due to Newspaper Set effect.\n"
                    elif attacker_eq_set == "Tigris":
                        # When targeting multiple enemies, for each enemy that is missing, damage is increased by x%.
                        if self.multiple_target_selection_targets_missing > 0:
                            tigris_effect_damage_bonus = self.multiple_target_selection_targets_missing * 0.90
                            final_damage *= 1 + tigris_effect_damage_bonus
                            global_vars.turn_info_string += f"Damage increased by {tigris_effect_damage_bonus * 100:.2f}% due to Tigris Set effect.\n"
                    if final_damage < 0:
                        final_damage = 0

                    if self.damage_type_during_attack_method == "undefined":
                        if damage_type == "normal":
                            target.take_damage(final_damage, self, is_crit=critical, disable_protected_effect=ignore_protected_effect)
                        elif damage_type == "status":
                            target.take_status_damage(final_damage, self)
                        elif damage_type == "bypass":
                            target.take_bypass_status_effect_damage(final_damage, self)
                        else:
                            raise Exception("Invalid damage type.")
                    elif self.damage_type_during_attack_method == "normal":
                        target.take_damage(final_damage, self, is_crit=critical, disable_protected_effect=ignore_protected_effect)
                    elif self.damage_type_during_attack_method == "status":
                        target.take_status_damage(final_damage, self)
                    elif self.damage_type_during_attack_method == "bypass":
                        target.take_bypass_status_effect_damage(final_damage, self)
                    else:
                        raise Exception("Invalid damage type.")
                    
                    damage_dealt += final_damage
                    if target.is_dead():
                        if attacker_eq_set == "Bamboo":
                            self.get_effect_that_named("Bamboo Set", None, "EquipmentSetEffect_Bamboo").apply_effect_custom(self)
                    self.add_number_of_attacks(1)
                    if func_after_dmg is not None and self.is_alive():
                        func_after_dmg(self, target)
                    if additional_attack_after_dmg is not None:
                        self.update_ally_and_enemy()
                        damage_dealt += additional_attack_after_dmg(self, target, is_crit=critical)
                else:
                    if func_after_miss is not None:
                        func_after_miss(self, target)
                    global_vars.turn_info_string += f"Missed! {self.name} attacked {target.name} but missed.\n"
                    for eff in self.buffs.copy() + self.debuffs.copy():
                        eff.apply_effect_when_missing_attack(self, target)

        self.multiple_target_selection_targets_missing = 0
        return damage_dealt


    def add_number_of_attacks(self, n):
        self.number_of_attacks += n
        if self.get_equipment_set() == "Flute" and self.number_of_attacks % 4 == 0:
            global_vars.turn_info_string += f"Flute activated from {self.name}, all opponent will take status damage.\n"
            for e in self.enemy:
                if e.is_alive():
                    e.take_status_damage(self.atk * 1.30, self)

    def reset_number_of_attacks(self):
        self.number_of_attacks = 0

    def heal(self, target_kw1="Undefined_ally", target_kw2="Undefined", target_kw3="Undefined", target_kw4="Undefined", 
             value=0, repeat=1, func_after_each_heal=None, target_list=None, func_before_heal=None) -> int:
        # -> healing done
        """
        Heal the target(s) for [value] amount of hp.
        [function_after_each_heal]: function that takes in (healer, target, healing, overhealing) -> None
        """
        self.update_ally_and_enemy()
        healing_done = 0
        try:
            targets = list(self.target_selection(target_kw1, target_kw2, target_kw3, target_kw4, target_list))
        # need to handle empty
        except IndexError:
            return 0
        if func_before_heal is not None:
            func_before_heal(self, targets)
        if self.get_equipment_set() == "Rose":
            for t in targets:
                t.apply_effect(StatsEffect("Beloved Girl", 2, True, 
                {"heal_efficiency": self.get_effect_that_named("Rose Set", None, "EquipmentSetEffect_Rose").he_bonus_before_heal}))
            self.apply_effect(StatsEffect("Beloved Girl", 10, True, {"defense": 1.30}))
        for i in range(repeat):
            for t in targets:
                healing, healer, overhealing = t.heal_hp(value, self)
                healing_done += healing
                if func_after_each_heal is not None:
                    func_after_each_heal(self, t, healing, overhealing)
        return healing_done

    # Action logic
    def action(self, skill_priority: int = 1) -> None:
        if self.get_equipment_set() == "Freight":
            skill_priority = 2

        for eff in self.buffs.copy() + self.debuffs.copy():
            eff.apply_effect_before_action(self)

        # Action is not allowed if the character is dead
        if self.is_dead():
            raise Exception("Dead character cannot act.")
        # Action is disabled if no enemies are present
        if not self.enemy:
            global_vars.turn_info_string += f"Waiting for enemies to appear.\n"
            return

        can_act, reason = self.can_take_action()
        if can_act:
            self.update_cooldown()
            if skill_priority == 1:
                if self.skill1_cooldown == 0 and not self.is_silenced() and self.skill1_can_be_used:
                    self.skill1()
                    if not self.have_taken_action:
                        self.have_taken_action = True
                elif self.skill2_cooldown == 0 and not self.is_silenced() and self.skill2_can_be_used:
                    self.skill2()
                    if not self.have_taken_action:
                        self.have_taken_action = True
                else:
                    self.normal_attack()
                    if not self.have_taken_action:
                        self.have_taken_action = True
            elif skill_priority == 2:
                if self.skill2_cooldown == 0 and not self.is_silenced() and self.skill2_can_be_used:
                    self.skill2()
                    if not self.have_taken_action:
                        self.have_taken_action = True
                elif self.skill1_cooldown == 0 and not self.is_silenced() and self.skill1_can_be_used:
                    self.skill1()
                    if not self.have_taken_action:
                        self.have_taken_action = True
                else:
                    self.normal_attack()
                    if not self.have_taken_action:
                        self.have_taken_action = True
        else:
            global_vars.turn_info_string += f"{self.name} cannot act due to {reason}.\n"

        self.reset_number_of_attacks()

        for eff in self.buffs.copy() + self.debuffs.copy():
            eff.apply_effect_after_action(self)


    # Print the character's stats
    def __str__(self):
        base_stats = "{:<20s} MaxHP: {:>5d} HP: {:>5d} ATK: {:>7.2f} DEF: {:>7.2f} Speed: {:>7.2f}".format(self.name, self.maxhp, self.hp, self.atk, self.defense, self.spd)
        effect_eq_set = [str(effect) for effect in self.buffs + self.debuffs if effect.is_set_effect]
        effects_buffs = [str(effect) for effect in self.buffs if not effect.is_set_effect]
        effects_debuffs = [str(effect) for effect in self.debuffs]
        return base_stats + f" Buffs: {effects_buffs} Debuffs: {effects_debuffs} Set Effects: {effect_eq_set}"

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
            # f"battle turns: {self.battle_turns}\n"

    def tooltip_string_jp(self):
        level = self.lvl if self.lvl < self.lvl_max else "MAX"
        return f"{self.name}\n" \
            f"レベル: {level}\n" \
            f"HP: {self.hp}/{self.maxhp}\n" \
            f"攻撃力: {self.atk}\n" \
            f"防御力: {self.defense}\n" \
            f"速度: {self.spd}\n" \
            f"回避: {self.eva*100:.2f}%\n" \
            f"命中: {self.acc*100:.2f}%\n" \
            f"クリティカル: {self.crit*100:.2f}%\n" \
            f"クリティカルダメージ: {self.critdmg*100:.2f}%\n" \
            f"クリティカル防御: {self.critdef*100:.2f}%\n" \
            f"貫通: {self.penetration*100:.2f}%\n" \
            f"回復効率: {self.heal_efficiency*100:.2f}%\n" \
            f"最終ダメージ倍率: {self.final_damage_taken_multipler*100:.2f}%\n" \
            f"最大スキルクールダウン: {self.skill1_cooldown_max}/{self.skill2_cooldown_max}\n" \
            f"経験値/最大経験値/パーセント: {self.exp}/{self.maxexp}/{self.exp/self.maxexp*100:.2f}%\n"
            # f"バトルターン数: {self.battle_turns}\n"

    def tooltip_status_effects(self):
        if global_vars.language == "日本語":
            str_sp = "スペシャル効果:\n"
            str_buff = "バフ効果:\n"
            str_debuff = "デバフ効果:\n"
        elif global_vars.language == "English":
            str_sp = "Special Status Effects:\n"
            str_buff = "Buff Effects:\n"
            str_debuff = "Debuff Effects:\n"
        str_sp += "=" * 20 + "\n"
        str_buff += "=" * 20 + "\n"
        str_debuff += "=" * 20 + "\n"
        
        book_sp = []
        book_buff = []
        book_debuff = []
        # Collect all buffs and debuffs into the book list
        for effect in self.buffs:
            if not effect.is_set_effect:
                if effect.duration == -1 and effect.can_be_removed_by_skill == False:
                    if global_vars.language == "日本語" and hasattr(effect, "print_stats_html_jp"):
                        book_sp.append(effect.print_stats_html_jp())
                    else:
                        book_sp.append(effect.print_stats_html())
                else:
                    if global_vars.language == "日本語" and hasattr(effect, "print_stats_html_jp"):
                        book_buff.append(effect.print_stats_html_jp())
                    else:
                        book_buff.append(effect.print_stats_html())

        for effect in self.debuffs:
            if not effect.is_set_effect:
                if effect.duration == -1 and effect.can_be_removed_by_skill == False:
                    if global_vars.language == "日本語" and hasattr(effect, "print_stats_html_jp"):
                        book_sp.append(effect.print_stats_html_jp())
                    else:
                        book_sp.append(effect.print_stats_html())
                else:
                    if global_vars.language == "日本語" and hasattr(effect, "print_stats_html_jp"):
                        book_debuff.append(effect.print_stats_html_jp())
                    else:
                        book_debuff.append(effect.print_stats_html())
        
        # Process duplicates: merging same effects and counting occurrences
        def process_duplicates(book):
            effect_dict = {}
            for effect_str in book:
                # Extract the core effect description without the duration
                effect_key, duration = extract_effect_key_and_duration(effect_str)
                if effect_key in effect_dict:
                    effect_dict[effect_key]['count'] += 1
                    if duration:
                        effect_dict[effect_key]['durations'].append(duration)
                else:
                    effect_dict[effect_key] = {'count': 1, 'effect_str': effect_str, 'durations': [duration] if duration else []}
            return effect_dict

        def extract_effect_key_and_duration(effect_str):
            # For English
            match_en = re.search(r'(\d+)\s*turn\(s\)', effect_str)
            # For Japanese
            match_jp = re.search(r'(\d+)\s*ターン', effect_str)
            if match_en:
                duration = match_en.group(1)
                effect_key = effect_str.replace(match_en.group(0), 'X turn(s)')
            elif match_jp:
                duration = match_jp.group(1)
                effect_key = effect_str.replace(match_jp.group(0), 'Xターン')
            else:
                duration = None
                effect_key = effect_str
            return effect_key, duration

        sp_count = process_duplicates(book_sp)
        buff_count = process_duplicates(book_buff)
        debuff_count = process_duplicates(book_debuff)

        def build_effect_string(effect_dict, section_str):
            result = section_str
            for effect_key, data in effect_dict.items():
                count = data['count']
                durations = data['durations']
                effect_str = effect_key
                if durations:
                    # If there's only one unique duration, replace 'X' with that duration
                    unique_durations = list(set(durations))
                    if len(unique_durations) == 1:
                        effect_str = effect_key.replace('X', unique_durations[0])
                    else:
                        # Replace 'X' with '?' if multiple durations
                        effect_str = effect_key.replace('X', '?')
                result += effect_str
                if count > 1:
                    color_repeat = "#ff80ff"
                    if durations:
                        # List all durations
                        durations_str = ', '.join(durations)
                        if global_vars.language == "日本語":
                            result += f'\n<font color="{color_repeat}">同じ効果が{count}回適用されている。持続時間: {durations_str}ターン。</font>'
                        else:
                            result += f'\n<font color="{color_repeat}">The same effect is applied {count} times. Durations: {durations_str} turn(s).</font>'
                    else:
                        if global_vars.language == "日本語":
                            result += f'\n<font color="{color_repeat}">同じ効果が{count}回適用されている。</font>'
                        else:
                            result += f'\n<font color="{color_repeat}">The same effect is applied {count} times.</font>'
                result += "\n"
            return result

        str_sp = build_effect_string(sp_count, str_sp)
        str_buff = build_effect_string(buff_count, str_buff)
        str_debuff = build_effect_string(debuff_count, str_debuff)

        return str_sp, str_buff, str_debuff

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
        unequipped_items = list(self.equip.values())
        self.equip.clear()
        self.reset_stats_and_reapply_effects(False)
        return unequipped_items

    def is_alive(self):
        return self.hp > 0

    def is_dead(self):
        return self.hp <= 0

    def is_charmed(self):
        return self.has_effect_that_named("Charm", class_name="CharmEffect")
    
    def is_confused(self):
        return self.has_effect_that_named("Confuse", class_name="ConfuseEffect")
    
    def is_stunned(self):
        return self.has_effect_that_named("Stun", class_name="StunEffect")
    
    def is_silenced(self):
        s1 = self.has_effect_that_named("Silence", class_name="SilenceEffect")
        s2 = self.has_effect_that_named("Ducky Silence")
        return s1 or s2 
    
    def is_sleeping(self):
        return self.has_effect_that_named("Sleep")
    
    def is_frozed(self):
        return self.has_effect_that_named("Frozen", class_name="FrozenEffect")
    
    def is_petrfied(self):
        return self.has_effect_that_named("Petrify", class_name="PetrifyEffect")
    
    def is_hidden(self):
        for e in self.buffs + self.debuffs:
            if e.name == "Hide" and e.is_active:
                return True
        return False

    def is_protected(self):
        return self.has_effect_that_named(None, None, class_name="ProtectedEffect")

    def trigger_hidden_effect_on_allies(self, attacker: 'Character'=None, damage_overkill: int | float=-1, damage_is_taken_by_protector: bool=False):
        self.update_ally_and_enemy()
        for a in self.party:
            if a.is_hidden():
                a.get_effect_that_named("Hide", class_name="HideEffect").apply_effect_on_trigger(a)
        if not self.ally or not self.enemy:
            return
        if attacker is not None and attacker.has_effect_that_named("Dragon Drawing", additional_name="Kyle_Dragon_Drawing") and damage_overkill > 0 \
            and not damage_is_taken_by_protector:
            # Select a ally with the lowest hp percentage
            lowest_hp_ally = min(self.ally, key=lambda x: x.hp/x.maxhp)
            global_vars.turn_info_string += f"Dragon Drawing effect triggered by {attacker.name}.\n"
            lowest_hp_ally.take_damage(damage_overkill, attacker=attacker)


    def can_take_action(self) -> Tuple[bool, str]:
        """
        returns a tuple of (can_act, reason)
        """
        if self.is_dead():
            return False, "Dead"
        if self.is_stunned():
            return False, "Stunned"
        if self.is_sleeping():
            return False, "Sleeping"
        if self.is_frozed():
            return False, "Frozen"
        if self.is_petrfied():
            return False, "Petrified"
        return True, "None"
    
    def can_use_a_skill(self) -> bool:
        condition_a = self.skill1_cooldown == 0 and self.skill1_can_be_used
        condition_b = self.skill2_cooldown == 0 and self.skill2_can_be_used
        return condition_a or condition_b

    def update_ally_and_enemy(self):
        self.ally = [ally for ally in self.party if not ally.is_dead()]
        self.enemy = [enemy for enemy in self.enemyparty if not enemy.is_dead()]
        if self.is_charmed(): 
            # If both charmed and confused, charmed will be prioritized
            self.ally, self.enemy = self.enemy, self.ally
        elif self.is_confused():
            self.ally = list(set(self.ally + self.enemy))
            self.enemy = list(set(self.enemy + self.ally))
            # if len(self.ally) != len(self.enemy):
            #     raise Exception
        elif self.has_effect_that_named("Love Fantasy", additional_name="Cupid_Love_Fantasy"):
            # Allies with Lead Arrow is seen as enemy, only allies with Lead Arrow is seen as ally.
            self.ally = [ally for ally in self.ally if ally.has_effect_that_named("Lead Arrow", additional_name="Cupid_Lead_Arrow")]
            self.enemy = [ally for ally in self.ally if ally.has_effect_that_named("Lead Arrow", additional_name="Cupid_Lead_Arrow")]
        elif self.get_effect_that_named(None, None, "TauntEffect") is not None:
            taunt_effect = self.get_effect_that_named(None, None, "TauntEffect")
            selection = [enemy for enemy in self.enemy if enemy in  [taunt_effect.marked_character]]
            # get rid of character in selection who have Hide effect
            selection = [enemy for enemy in selection if not enemy.is_hidden()]
            if selection is []:
                self.remove_effect(taunt_effect)
            else:
                self.enemy = selection

        
    def has_ally(self, ally_name):
        return ally_name in [ally.name for ally in self.ally]
    
    def has_enemy(self, enemy_name):
        return enemy_name in [enemy.name for enemy in self.enemy]

    def is_middle(self, of_the_party=False):
        """
        Check if self is in the middle position(s) of self.ally.
        self.ally has a length from 0 to 5.
        of_the_party: Check self.party instead. self.party has a fixed length of 5, never changes in one battle.
        Examples:
        [a, b, self, c, d] -> True
        [a, b, c, d, self] -> False
        [a, self, c, d]    -> True
        [a, b, self, d]    -> True
        [self, b]          -> True
        [self]             -> True
        """
        if of_the_party:
            return self.get_self_index() == 2
        ally = self.ally
        n = len(ally)
        if n == 0:
            return False  
        if self not in ally:
            return False  
        # Determine middle index/indices
        if n % 2 == 1:
            # Odd length, single middle index
            middle_indices = [n // 2]
        else:
            # Even length, two middle indices
            middle_indices = [n // 2 - 1, n // 2]
        self_index = ally.index(self)
        return self_index in middle_indices

    def get_distance_to_middle(self, of_the_party=False):
        """
        Get the distance to the middle position of self.ally.

        Examples:
        [a, b, self, c, d] -> 0
        [a, b, c, d, self] -> 2
        [a, self, c, d]    -> 0
        [a, b, self, d]    -> 0
        [self, b]          -> 0
        [self]             -> 0
        """
        if of_the_party:
            return abs(2 - self.get_self_index())
        ally = self.ally
        n = len(ally)
        if n == 0:
            return 0
        if self not in ally:
            return 0
        self_index = ally.index(self)
        if n % 2 == 1:
            # Odd length, single middle index
            middle_indices = [n // 2]
        else:
            # Even length, two middle indices
            middle_indices = [n // 2 - 1, n // 2]
        # Compute the minimum distance to either middle index
        distances = [abs(self_index - mi) for mi in middle_indices]
        return min(distances)

    def get_neighbors(self, party, char, include_self=True, distance=1) -> list['Character']:
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

    def get_neighbor_ally_left(self, get_from_self_ally=True):
        neighbors = self.get_neighbor_allies_not_including_self(get_from_self_ally)
        if neighbors:
            return neighbors[0]
        return None

    def get_neighbor_ally_right(self, get_from_self_ally=True):
        neighbors = self.get_neighbor_allies_not_including_self(get_from_self_ally)
        if neighbors:
            return neighbors[-1]
        return None

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
        # print(f"Stats: {stats}")
        # print(f"Start reversing additive stats:")
        hp_removed = self.update_main_stats_additive(reversed=True)
        # print(f"Reversed additive stats.")
        # {'atk': 1.2, 'defense': 1.2, 'spd': 1.2, 'crit': 0.2, 'critdmg': 0.2}
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
                assert new_value > 0, f"New stat is 0 or below, Does not make sense: {stats}, {attr}, {value}, {new_value}" 
            else:
                if reversed:
                    new_value = getattr(self, attr) - value
                else:
                    new_value = getattr(self, attr) + value
            prev[attr] = getattr(self, attr)
            setattr(self, attr, new_value)
            new[attr] = new_value
            delta[attr] = new_value - prev[attr]
        # print(f"Multiplive stats updated, start updating additive stats.")
        self.update_main_stats_additive()
        # print(f"Additive stats updated.")
        self.hp = min(self.maxhp, self.hp + hp_removed)
        return prev, new, delta

    def update_main_stats_additive(self, reversed=False, effect_pointer=None):
        # update stats from self.additive_main_stats, which is a list of dict, if any.
        # example : [{'hp': 200, 'effect_pointer': a Effect object}, {'atk': 30, 'spd': 50, 'effect_pointer': another Effect object}]
        # effect_pointer: A Effect object. If it is None, update with every records, otherwise, only update with the certain matched record.
        if not self.additive_main_stats: # No dict records
            return 0
        hp_illegally_removed_by_this_operation = 0
        for dict_record in self.additive_main_stats:
            if effect_pointer is not None and dict_record.get('effect_pointer') != effect_pointer:
                continue
            for attr, value in dict_record.items():
                if attr == "effect_pointer":  
                    continue
                if attr not in ["maxhp", "hp", "atk", "defense", "spd"]:
                    raise Exception(f"Unexpected attribute {attr} found in additive stats.")
                if reversed:
                    new_value = getattr(self, attr) - value
                else:
                    new_value = getattr(self, attr) + value
                if attr == "hp":
                    new_value = min(new_value, self.maxhp)
                    new_value = max(new_value, 0)
                if attr == "maxhp":
                    new_value = max(new_value, 1)
                assert new_value >= 0, f"New value is negative: {new_value}, {attr}, {value}"
                maxhp_prev = self.maxhp
                # print(f"maxhp_prev: {maxhp_prev}")
                hp_prev = self.hp
                # print(f"hp_prev: {hp_prev}")
                setattr(self, attr, new_value)
                self.hp = min(self.hp, self.maxhp)
                # print(f"self.hp: {self.hp}")
                maxhp_curr = self.maxhp
                hp_curr = self.hp
                # print(f"maxhp_curr: {maxhp_curr}")
                if maxhp_curr < maxhp_prev:
                    hp_illegally_removed_by_this_operation += hp_prev - hp_curr
                else:
                    pass
        return hp_illegally_removed_by_this_operation

    def heal_hp(self, value, healer, ignore_death=False):
        # Remember the healer can be a Character object or Consumable object or Effect or perhaps other objects
        # if healer is not Character class, give error for now, testing purpose
        if not isinstance(healer, Character):
            # raise Exception(f"Invalid healer: {healer}, {healer.__class__}")
            healer = self
        if self.is_dead() and not ignore_death:
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
        for e in self.buffs.copy() + self.debuffs.copy():
            healing = e.apply_effect_during_heal_step(self, healing, healer, overhealing)
        if healing < 0:
            global_vars.turn_info_string += f"{self.name} failed to receive any healing.\n"
            healing = 0
        else:
            self.hp += healing
            global_vars.turn_info_string += f"{self.name} is healed for {healing} HP.\n"
        healer_for_recording = healer
        if isinstance(healer, Effect) and healer.is_set_effect:
            healer_for_recording = "Equipment"
        self.healing_received_this_turn.append((healing, healer_for_recording))
        for e in self.buffs.copy() + self.debuffs.copy():
            e.apply_effect_after_heal_step(self, healing, overhealing)
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

    def revive(self, hp_to_revive, hp_percentage_to_revive, healer):
        if self.is_dead():
            self.hp += hp_to_revive
            self.hp += self.maxhp * hp_percentage_to_revive
            if self.hp < 1:
                raise Exception(f"{self.name} is not revived. HP is less than 1.")
            if self.hp > self.maxhp:
                self.hp = self.maxhp
            self.hp = int(self.hp)
            self.healing_received_this_turn.append((self.hp, healer))
            global_vars.turn_info_string += f"{self.name} is revived for {self.hp} hp.\n"
            # if character has after_revive method, trigger it
            if hasattr(self, "after_revive"):
                self.after_revive()
        else:
            raise Exception(f"{self.name} is not dead. Cannot revive.")
    

    def regen(self):
        """
        use ContinuousHealEffect instead.
        """
        pass

    def take_damage(self, value, attacker=None, func_after_dmg=None, disable_protected_effect=False, is_crit=False):
        friendly_fire = False
        if attacker is not None and attacker in self.party:
            friendly_fire = True
            global_vars.turn_info_string += f"{self.name} is taking friendly fire from {attacker.name}.\n"

        global_vars.turn_info_string += f"{self.name} is about to take {value} damage.\n"
        if self.is_dead():
            print(global_vars.turn_info_string)
            raise Exception(f"Cannot take damage when dead. {self.name} is already dead. Attacker: {attacker.name}")
        value = max(0, value)
        # Attention: final_damage_taken_multipler is calculated before shields effects.
        damage = value * self.final_damage_taken_multipler
        if damage > 0 and friendly_fire:
            for effect in itertools.chain(self.buffs.copy(), self.debuffs.copy()):
                damage = effect.apply_effect_when_taking_friendly_fire(self, damage, attacker)

        if damage > 0:
            copyed_buffs = self.buffs.copy() # Some effect will try apply other effects during this step, see comments on Effect class for details.
            copyed_debuffs = self.debuffs.copy()
            for effect in copyed_buffs:
                if hasattr(effect, "is_protected_effect") and effect.is_protected_effect and not disable_protected_effect:
                    damage = effect.protected_apply_effect_during_damage_step(self, damage, attacker, func_after_dmg)
                else:
                    # Protected effect is disabled means this damage is taken by the protector.
                    damage = effect.apply_effect_during_damage_step(self, damage, attacker, "normal", attack_is_crit=is_crit,
                                                                    damage_taken_by_protector=disable_protected_effect)
            for effect in copyed_debuffs:
                damage = effect.apply_effect_during_damage_step(self, damage, attacker, "normal", attack_is_crit=is_crit)
                
        damage = self.take_damage_before_calculation(damage, attacker)
        damage = int(damage)
        damage = max(0, damage)
        damage_overkill = -1

        if self.hp - damage < 0:
            dmr = damage
            damage = self.hp
            damage_overkill = dmr - damage
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
        # Also need to handle when the attacker is from the same party, if so, the damage is 'friendlyfire'.
        if friendly_fire:
            self.damage_taken_this_turn.append((damage, attacker, "friendlyfire"))
        else:
            if is_crit:
                self.damage_taken_this_turn.append((damage, attacker, "normal_critical"))
            else:
                self.damage_taken_this_turn.append((damage, attacker, "normal"))
        if self.is_dead():
            self.defeated_by_taken_damage(damage, attacker)
        if self.is_dead():
            self.trigger_hidden_effect_on_allies(attacker=attacker, damage_overkill=damage_overkill, damage_is_taken_by_protector=disable_protected_effect)
            if attacker is not None:
                attacker.number_of_take_downs += 1
        return None
    
    def take_damage_before_calculation(self, damage, attacker):
        """
        Event triggered before taking normal damage, not status nor bypass.
        """
        return damage

    def take_damage_aftermath(self, damage, attacker):
        """
        Event triggered after taking normal damage, not status nor bypass.
        """
        pass

    def defeated_by_taken_damage(self, damage, attacker):
        """
        Event triggered when the character is defeated by taking any type of damage.
        """
        pass

    def take_status_damage(self, value, attacker=None, is_reflect=False):
        if self.is_dead():
            return 0, attacker
        friendly_fire = False
        if attacker is not None and attacker in self.party:
            friendly_fire = True
            global_vars.turn_info_string += f"{self.name} is taking friendly fire from {attacker.name}.\n"
        global_vars.turn_info_string += f"{self.name} is about to take {value} status damage.\n"
        value = max(0, value)
        damage = value * self.final_damage_taken_multipler

        if damage > 0 and friendly_fire:
            for effect in itertools.chain(self.buffs.copy(), self.debuffs.copy()):
                damage = effect.apply_effect_when_taking_friendly_fire(self, damage, attacker)

        if damage > 0:
            copyed_buffs = self.buffs.copy() 
            copyed_debuffs = self.debuffs.copy()
            for effect in copyed_buffs:
                damage = effect.apply_effect_during_damage_step(self, damage, attacker, "status", damage_is_reflect=is_reflect)
            for effect in copyed_debuffs:
                damage = effect.apply_effect_during_damage_step(self, damage, attacker, "status", damage_is_reflect=is_reflect)

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
        if friendly_fire:
            self.damage_taken_this_turn.append((damage, attacker, "friendlyfire"))
        else:
            self.damage_taken_this_turn.append((damage, attacker, "status"))
        if self.is_dead():
            self.defeated_by_taken_damage(damage, attacker)
        # defeated_by_taken_damage may trigger instant revive effect, so need to check again.
        if self.is_dead():
            self.trigger_hidden_effect_on_allies()
            if attacker is not None:
                attacker.number_of_take_downs += 1
        # We do not need the return value yet.
        return None, None 

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
        if attacker is not None and attacker in self.party:
            self.damage_taken_this_turn.append((damage, attacker, "friendlyfire"))
        else:
            self.damage_taken_this_turn.append((damage, attacker, "bypass"))
        if self.is_dead():
            self.defeated_by_taken_damage(damage, attacker)
        if self.is_dead():
            self.trigger_hidden_effect_on_allies()
            if attacker is not None:
                attacker.number_of_take_downs += 1
        return None

    def get_the_amount_of_effect(self) -> tuple[int, int, int]:
        """
        Return the amount of special effects, buffs, and debuffs.
        sp: must not be set_effect, it has -1 duration and cannot be removed by skill.
        buff: must not be set_effect
        debuff: must not be set_effect
        """
        sp = 0
        buff = 0
        debuff = 0
        for effect in self.buffs:
            if effect.is_set_effect:
                continue
            if effect.duration == -1 and not effect.can_be_removed_by_skill:
                sp += 1
            else:
                buff += 1
        for effect in self.debuffs:
            if effect.is_set_effect:
                continue
            if effect.duration == -1 and not effect.can_be_removed_by_skill:
                sp += 1
            else:
                debuff += 1
        return sp, buff, debuff

    def has_effect_that_is(self, effect: Effect):
        """ Check if the character has the same effect object. """
        return effect in self.buffs + self.debuffs

    def has_effect_that_named(self, effect_name: str = None, additional_name: str = None, class_name: str = None) -> bool:
        """
        Given the effect name, additional_name attribute, and class name, check if the character has the effect.
        """
        for effect in self.buffs + self.debuffs:
            if effect_name and effect.name != effect_name:
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

    def get_effect_that_named(self, effect_name: str = None, additional_name: str = None, class_name: str = None) -> Effect:
        """
        Return the first effect found that matches the given effect name.
        """
        for effect in self.buffs + self.debuffs:
            if effect_name and effect.name != effect_name:
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


    def get_all_effect_that_named(self, effect_name: str = None, additional_name: str = None, class_name: str = None) -> list:
        """
        Return a list of all effects found that matches the given effect name.
        """
        effects = []
        for effect in self.buffs + self.debuffs:
            if effect_name and effect.name != effect_name:
                continue

            match (additional_name, class_name):
                case (None, None):
                    effects.append(effect)
                case (_, None):
                    if hasattr(effect, "additional_name") and effect.additional_name == additional_name:
                        effects.append(effect)
                case (None, _):
                    if type(effect).__name__ == class_name:
                        effects.append(effect)
                case (_, _):
                    if hasattr(effect, "additional_name") and effect.additional_name == additional_name and \
                    type(effect).__name__ == class_name:
                        effects.append(effect)
        return effects


    def is_immune_to_cc(self):
        for effect in self.buffs:
            if effect.cc_immunity:
                return True
        for effect in self.debuffs: # Debuff that provide CC immunity? Makes no sense.
            if effect.cc_immunity:
                print(f"Warning: {self.name} has debuff that provide CC immunity. Effect name: {effect.name}")
                return True
        return False

    def apply_effect(self, effect: Effect):
        if effect.already_applied:
            # find out who has the very same effect
            # This prevents attempting to apply the same effect instance multiple times.
            for c in self.party + self.enemyparty:
                if c.has_effect_that_is(effect):
                    global_vars.turn_info_string += f"Warning: {effect.name}, which already applied to someone before, is attempting to apply on {self.name}.\n"
                    global_vars.turn_info_string += f"Warning: {c.name} has the same effect instance.\n"
                    print(f"Warning: {effect.name}, which already applied to someone before, is attempting to apply on {self.name}.")
                    print(f"Warning: {c.name} has the same effect instance.")

        # if self.is_dead():
        #     print(f"Warning: {self.name} is dead, should not be a valid target to apply effect. Effect name: {effect.name}")
        if not effect.is_set_effect:
            global_vars.turn_info_string += f"{effect.name} is about to be applied on {self.name}.\n"
        if effect.name in self.effect_immunity:
            global_vars.turn_info_string += f"{self.name} is immune to {effect.name}.\n"
            return
        if self.is_immune_to_cc() and effect.is_cc_effect:
            global_vars.turn_info_string += f"{self.name} is immune to {effect.name}.\n"
            return
        if effect.apply_rule == "stack":
            for e in self.debuffs.copy() + self.buffs.copy():
                if e.name == effect.name:
                    # if they both have attr additional_name, they must match
                    if hasattr(e, "additional_name") and hasattr(effect, "additional_name") and e.additional_name != effect.additional_name:
                        continue
                    # if only one of them have additional_name, they must not match
                    if (hasattr(e, "additional_name") and not hasattr(effect, "additional_name")) or \
                        (hasattr(effect, "additional_name") and not hasattr(e, "additional_name")):
                        continue
                    
                    if e.duration < effect.duration and e.duration > 0:
                        e.duration = effect.duration
                    e.apply_effect_when_adding_stacks(self, effect.stacks)
                    global_vars.turn_info_string += f"{effect.name} duration on {self.name} has been refreshed.\n"
                    return
        elif effect.apply_rule == "replace":
            for e in self.debuffs.copy() + self.buffs.copy():
                if e.name == effect.name:
                    # if they both have attr additional_name, they must match
                    if hasattr(e, "additional_name") and hasattr(effect, "additional_name") and e.additional_name != effect.additional_name:
                        continue
                    # if only one of them have additional_name, they must not match
                    if (hasattr(e, "additional_name") and not hasattr(effect, "additional_name")) or \
                        (hasattr(effect, "additional_name") and not hasattr(e, "additional_name")):
                        continue
                    # directly remove effect will cause error. Reason: the only effect that use replace is Lester exciting time, who adds atk when being healed.
                    # if heal is during status_effects_midturn method, the list of effect is not being updated constantly.
                    # patched in 3.7.7
                    if self.is_in_iteration_of_status_effects_midturn or self.is_in_iteration_of_status_effects_startturn:
                        e.remove_this_effect_as_it_is_replaced = True
                    else:
                        self.remove_effect(e)
                    effect.apply_effect_when_replacing_old_same_effect(e)
                    global_vars.turn_info_string += f"{e.name} on {self.name} has been replaced by {effect.name}.\n"
                    break
        # if effect is AbsorptionShield and they have the same name and duration and cc_immunity, we can stack them.
        shield_value_prev = self.get_shield_value()
        if isinstance(effect, AbsorptionShield):
            if self.has_effect_that_named("Dating Innovations", "Eddie_Dating_innovations", "Effect"):
                # shield effect scaled heal efficiency
                # print(f"Shield value before scaling: {effect.shield_value}")
                effect.shield_value = effect.shield_value * self.heal_efficiency
                # print(f"Shield value is scaled by heal efficiency: {effect.shield_value}")
                if effect.shield_value <= 0:
                    return
            for e in itertools.chain(self.buffs, self.debuffs):
                if isinstance(e, AbsorptionShield) and e.name == effect.name and e.duration == effect.duration and e.cc_immunity == effect.cc_immunity:
                    e.shield_value += effect.shield_value
                    global_vars.turn_info_string += f"{effect.name} on {self.name} has been stacked.\n"
                    shield_value_curr = self.get_shield_value()
                    assert shield_value_curr > shield_value_prev, f"AbsorptionShield is stacked, but shield value is not increased when trying to stack {effect.name} on {self.name}."
                    return

        # if effect is CancellationShield and they have the same following attributes, we can stack them.
        # self.name = name
        # self.duration = duration
        # self.is_buff = is_buff
        # self.threshold = threshold
        # self.cc_immunity = cc_immunity
        # self.sort_priority = 250
        # self.uses = uses
        # self.cancel_excessive_instead = cancel_excessive_instead
        # self.cancel_below_instead = cancel_below_instead
        # self.remove_this_effect_when_use_is_zero = remove_this_effect_when_use_is_zero
        # self.cover_status_damage = cover_status_damage
        # self.cover_normal_damage = cover_normal_damage

        if isinstance(effect, CancellationShield):
            for e in itertools.chain(self.buffs, self.debuffs):
                if isinstance(e, CancellationShield) and e.name == effect.name and e.is_buff == effect.is_buff and effect.duration == e.duration and \
                e.threshold == effect.threshold and e.cc_immunity == effect.cc_immunity and e.uses == effect.uses and \
                e.cancel_excessive_instead == effect.cancel_excessive_instead and e.cancel_below_instead == effect.cancel_below_instead and \
                e.remove_this_effect_when_use_is_zero == effect.remove_this_effect_when_use_is_zero and \
                e.cover_status_damage == effect.cover_status_damage and e.cover_normal_damage == effect.cover_normal_damage:
                    e.uses += effect.uses
                    global_vars.turn_info_string += f"{effect.name} on {self.name} has been stacked. Uses: {e.uses}.\n"
                    return

        # if the effect is not infinite duration(.duration > 0), the duration is adjusted by character bonus duration
        if effect.duration > 0:
            if effect.is_buff:
                effect.duration += self.duration_bonus_when_apply_effect_buff
            else:
                effect.duration += self.duration_bonus_when_apply_effect_debuff
            # then check duration is valid or not, if not(<=0), do not apply the effect.
            if effect.duration <= 0:
                return
        
        # Do we allow applying effect on dead character? Yes, for some effects.
        # insert the effect in the correct position based on sort_priority
        if effect.is_buff:
            bisect.insort(self.buffs, effect, key=lambda x: x.sort_priority)
        else:
            bisect.insort(self.debuffs, effect, key=lambda x: x.sort_priority)
        effect.already_applied = True
        if not effect.is_set_effect:
            global_vars.turn_info_string += f"{effect.name} has been applied on {self.name}.\n"
        effect.apply_effect_on_apply(self)

    def remove_effect(self, effect: Effect, purge=False, strict=False):
        # purge: effect is removed without triggering apply_effect_on_remove
        # Attention: Character Ophelia does not use this function, but directly temper with self.buffs and self.debuffs
        try:
            if effect.is_buff:
                self.buffs.remove(effect)
            else:
                self.debuffs.remove(effect)
        except ValueError:
            if strict:
                raise Exception(f"Effect not found when attempting to remove effect: {effect}")
            else:
                print(f"Warning: Effect not found when attempting to remove effect: {effect}")
        global_vars.turn_info_string += f"{effect.name} on {self.name} has been removed.\n"
        if not purge:
            effect.apply_effect_on_remove(self)
        effect.already_applied = False

    def try_remove_effect_with_name(self, effect_name: str, strict=False, remove_all_found_effects=False) -> bool:
        """
        Try to remove the effect(s) found with the given effect name.
        Return True if at least one effect is found and removed, False otherwise.
        """
        effects_to_remove = [effect for effect in self.buffs + self.debuffs if effect.name == effect_name]
        
        if not effects_to_remove:
            if strict:
                raise Exception("Effect with name not found.")
            return False
        
        if remove_all_found_effects:
            for effect in effects_to_remove:
                self.remove_effect(effect)
        else:
            self.remove_effect(effects_to_remove[0])
        
        return True

    # Get shield value, all shield effect must have shield_value attribute.
    def get_shield_value(self) -> int:
        total = 0
        for effect in self.buffs + self.debuffs:
            if hasattr(effect, "shield_value"):
                total += effect.shield_value
        return total

    def get_active_removable_effects(self, get_buffs=True, get_debuffs=True) -> list[Effect]:
        active_effects = []
        if get_buffs:
            active_effects += [effect for effect in self.buffs if effect.can_be_removed_by_skill and effect.duration > 0 and not effect.is_set_effect]
        if get_debuffs:
            active_effects += [effect for effect in self.debuffs if effect.can_be_removed_by_skill and effect.duration > 0 and not effect.is_set_effect]
        return active_effects


    def remove_all_effects(self):
        # Not used
        pass

    def remove_random_amount_of_debuffs(self, amount, allow_infinite_duration=True) -> list:
        # -> list of removed effects
        debuffs_filtered = [effect for effect in self.debuffs if not effect.is_set_effect and effect.can_be_removed_by_skill]
        if not allow_infinite_duration:
            debuffs_filtered = [effect for effect in debuffs_filtered if effect.duration != -1]
        amount = min(amount, len(debuffs_filtered))
        if amount == 0:
            return []
        removed_effects = random.sample(debuffs_filtered, amount)
        
        for effect in removed_effects:
            self.remove_effect(effect)
        return removed_effects

    def remove_random_amount_of_buffs(self, amount, allow_infinite_duration=True) -> list:
        # -> list of removed effects
        buffs_filtered = [effect for effect in self.buffs if not effect.is_set_effect and effect.can_be_removed_by_skill]
        if not allow_infinite_duration:
            buffs_filtered = [effect for effect in buffs_filtered if effect.duration != -1]
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
        self.is_in_iteration_of_status_effects_startturn = True
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
        self.is_in_iteration_of_status_effects_startturn = False
        for effect in self.buffs.copy() + self.debuffs.copy():
            if hasattr(effect, "remove_this_effect_as_it_is_replaced") and effect.remove_this_effect_as_it_is_replaced:
                self.remove_effect(effect)
    
    # Every turn, calculate apply_effect_on_turn effect of all buffs and debuffs. ie. poison, burn, etc.
    def status_effects_midturn(self):
        buffs_copy = self.buffs.copy()
        debuffs_copy = self.debuffs.copy()
        self.is_in_iteration_of_status_effects_midturn = True
        for effect in buffs_copy + debuffs_copy:
            effect.apply_effect_on_turn(self)
        self.is_in_iteration_of_status_effects_midturn = False
        # then remove effect that is marked as remove_this_effect_as_it_is_replaced is True
        for effect in self.buffs.copy() + self.debuffs.copy():
            if hasattr(effect, "remove_this_effect_as_it_is_replaced") and effect.remove_this_effect_as_it_is_replaced:
                self.remove_effect(effect)
                # print(f"{effect.name} on {self.name} is removed as it is replaced.")

    def character_specific_at_end_of_turn(self):
        """
        This function is for character specific effect at the end of turn.
        """
        pass

    def status_effects_at_end_of_turn(self):
        # TODO: Change this.
        # The following character/monster has a local implementation of this method:
        # Character: BeastTamer Yuri, Moonrabbit Beacon
        # Monster: Security Guard, Emperor
        self.character_specific_at_end_of_turn()
        buffs_copy = self.buffs.copy()
        debuffs_copy = self.debuffs.copy()
        for effect in buffs_copy + debuffs_copy:
            effect.apply_effect_at_end_of_turn(self)

    def status_effects_after_damage_record(self):
        """
        Please do not trigger and damage related effect in this process.
        """
        buffs_copy = self.buffs.copy()
        debuffs_copy = self.debuffs.copy()
        for effect in buffs_copy + debuffs_copy:
            effect.apply_effect_after_damage_record(self)


    def update_cooldown(self):
        """
        Reduce the cooldown of the character's all skills by 1.
        """
        if self.skill1_cooldown > 0:
            self.skill1_cooldown -= 1
        if self.skill2_cooldown > 0:
            self.skill2_cooldown -= 1

    def skill_tooltip(self):
        return f"Skill 1 : {self.skill1_description}\nCooldown : {self.skill1_cooldown} action(s)\n\nSkill 2 : {self.skill2_description}\nCooldown : {self.skill2_cooldown} action(s)\n\nSkill 3 : {self.skill3_description}\n"

    def skill_tooltip_jp(self):
        return f"スキル1:{self.skill1_description_jp}\nクールダウン:{self.skill1_cooldown}行動\n\nスキル2:{self.skill2_description_jp}\nクールダウン:{self.skill2_cooldown}行動\n\nスキル3:{self.skill3_description_jp}\n"

    def get_equipment_set(self) -> str:
        if not self.equip:
            return "None"
        for e in self.equip.values():
            e.set_effect_is_acive = False
        if len(self.equip) != 4:
            return "None"

        sets = {item.eq_set for item in self.equip.values()}
        # return sets.pop() if len(sets) == 1 else "None"
        if len(sets) == 1:
            for e in self.equip.values():
                e.set_effect_is_acive = True
            return sets.pop()
        else:
            return "None"


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
            highest_stat = max(self.atk, self.defense)
            self.apply_effect(EquipmentSetEffect_KangTao("KangTao Set", -1, True, highest_stat * 9.99, False))
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
            self.apply_effect(EquipmentSetEffect_Dawn("Dawn Set", -1, True, {"atk": 1.24, "crit": 0.24}))
        elif set_name == "Bamboo":
            self.apply_effect(EquipmentSetEffect_Bamboo("Bamboo Set", -1, True, {"atk": 1.90, "defense": 1.90, "spd": 1.90, "crit": 0.45, "critdmg": 0.45}))
        elif set_name == "Rose":
            self.apply_effect(EquipmentSetEffect_Rose("Rose Set", -1, True, he_bonus_before_heal=1.00))
            belove_girl_self_effect = StatsEffect("Beloved Girl", -1, True, {"heal_efficiency": 0.20})
            belove_girl_self_effect.is_set_effect = True
            self.apply_effect(belove_girl_self_effect)
        elif set_name == "OldRusty":
            self.apply_effect(EquipmentSetEffect_OldRusty("OldRusty Set", -1, True))
        elif set_name == "Purplestar":
            self.apply_effect(EquipmentSetEffect_Purplestar("Purplestar Set", -1, True))
        elif set_name == "Liquidation":
            self.apply_effect(EquipmentSetEffect_Liquidation("Liquidation Set", -1, True, 0.20))
        elif set_name == "Cosmic":
            effect_cosmic = StatsEffect("Cosmic Set", -1, True, {"maxhp": 1.018}, condition=lambda char: char.is_alive(),
                                        use_active_flag=False, is_set_effect=True)
            # effect_cosmic.original_maxhp = self.maxhp
            # def new_apply_effect_at_end_of_turn(effect, char):
            #     if char.maxhp > effect.original_maxhp * 200:
            #         effect.flag_for_remove = True
            #         # print(f"{char.name} has reached the max hp limit.")

            # # Bind the new method to the effect_cosmic instance
            # effect_cosmic.apply_effect_at_end_of_turn = new_apply_effect_at_end_of_turn.__get__(effect_cosmic, type(effect_cosmic))
            self.apply_effect(effect_cosmic)
        elif set_name == "Newspaper":
            self.apply_effect(EquipmentSetEffect_Newspaper("Newspaper Set", -1, True))
        elif set_name == "Cloud":
            cloud_hide_effect_spd_boost = StatsEffect("Full Cloud", 10, True, {"spd": 2.00, "final_damage_taken_multipler": -0.40})
            cloud_hide_effect = HideEffect("Hide", 50, True, effect_apply_to_character_on_remove=cloud_hide_effect_spd_boost)
            cloud_hide_effect.is_set_effect = True
            cloud_hide_effect.sort_priority = 2000
            cloud_speed_effect = StatsEffect("Cloudy", -1, True, {"spd": 1.05, "atk": 0.90}, is_set_effect=True)
            self.apply_effect(cloud_hide_effect)
            self.apply_effect(cloud_speed_effect)
        # 1987: Select the highest one from 3 of your main stats: atk, def, spd. 15% of the selected stat is added to the ally
        # who has the lowest value of the selected stat.
        elif set_name == "1987":
            onenineeightseven_effect = Effect("1987 Set", -1, True)
            onenineeightseven_effect.is_set_effect = True
            onenineeightseven_effect.sort_priority = 2000
            self.apply_effect(onenineeightseven_effect)
        elif set_name == "7891":
            seveneightnineone_effect = Effect("7891 Set", -1, True)
            seveneightnineone_effect.is_set_effect = True
            seveneightnineone_effect.sort_priority = 2000
            self.apply_effect(seveneightnineone_effect)
        elif set_name == "Freight":
            self.apply_effect(EquipmentSetEffect_Freight("Freight Set", -1, True))
        elif set_name == "Runic":
            # Critical rate is increased by 100%, critical damage is decreased by 50%. 
            # When dealing damage, any critical rate over 100% is converted to critical damage
            self.apply_effect(StatsEffect("Runic Set", -1, True, {"crit": 1.00, "critdmg": -0.50}, is_set_effect=True))
        elif set_name == "Grassland":
            # If you haven't taken action yet in current battle, speed is increased by 100%, final damage taken is decreased by 30%
            # EquipmentSetEffect_Grassland is a subclass of StatsEffect, removes it self when the character takes action.
            self.apply_effect(EquipmentSetEffect_Grassland("Grassland Set", -1, True, {"spd": 2.40, "final_damage_taken_multipler": -0.30}))
        elif set_name == "Tigris":
            # When targeting multiple enemies, for each enemy that is missing, damage is increased by x%.
            self.apply_effect(EquipmentSetEffect_Tigris("Tigris Set", -1, True))
        elif set_name == "Armygreen":
            # gives some sub stats
            self.apply_effect(StatsEffect("Armygreen Set", -1, True, {"crit": 0.30, "acc": 0.30, "critdmg": 0.30, "penetration": 0.10}, is_set_effect=True))
        elif set_name == "Armydesert":
            # gives some defensive sub stats: critdef, heal_efficiency, eva
            self.apply_effect(StatsEffect("Armydesert Set", -1, True, {"critdef": 0.50, "heal_efficiency": 0.50, "eva": 0.20}, is_set_effect=True))

        # The following are for testing how valable a stat increase is, atk 50%, crit 100%, critdmg 100%....
        elif set_name == "Statstestatk":
            self.apply_effect(StatsEffect("Statstest_atk", -1, True, {"atk": 1.50}, is_set_effect=True))
        elif set_name == "Statstestdef":
            self.apply_effect(StatsEffect("Statstest_def", -1, True, {"defense": 1.50}, is_set_effect=True))
        elif set_name == "Statstestspd":
            self.apply_effect(StatsEffect("Statstest_spd", -1, True, {"spd": 1.50}, is_set_effect=True))
        # maxhp
        elif set_name == "Statstestmaxhp":
            self.apply_effect(StatsEffect("Statstest_maxhp", -1, True, {"maxhp": 1.50}, is_set_effect=True))
            self.hp = self.maxhp
        elif set_name == "Statstestcrit":
            self.apply_effect(StatsEffect("Statstest_crit", -1, True, {"crit": 1.00}, is_set_effect=True))
        elif set_name == "Statstestcritdmg":
            self.apply_effect(StatsEffect("Statstest_critdmg", -1, True, {"critdmg": 1.50}, is_set_effect=True))
        elif set_name == "Statstesthe":
            self.apply_effect(StatsEffect("Statstest_he", -1, True, {"heal_efficiency": 1.50}, is_set_effect=True))
        elif set_name == "Statstestcritdef":
            self.apply_effect(StatsEffect("Statstest_critdef", -1, True, {"critdef": 1.00}, is_set_effect=True))
        # eva, acc, penetration
        elif set_name == "Statstesteva":
            self.apply_effect(StatsEffect("Statstest_eva", -1, True, {"eva": 0.50}, is_set_effect=True))
        elif set_name == "Statstestacc":
            self.apply_effect(StatsEffect("Statstest_acc", -1, True, {"acc": 0.50}, is_set_effect=True))
        elif set_name == "Statstestpen":
            self.apply_effect(StatsEffect("Statstest_pen", -1, True, {"penetration": 0.50}, is_set_effect=True))

        else:
            raise Exception("Effect not implemented.")
        
    def equipment_set_effects_tooltip(self):
        set_name = self.get_equipment_set()
        if set_name == "None" or set_name == "Void":
            return ""
        if global_vars.language == "English":
            str = "Equipment Set Effects:\n"
            if set_name != "None" and set_name != "Void":
                str += self.equip["Weapon"].four_set_effect_description
            else:
                str += "Equipment set effects is not active. Equip 4 items of the same set to receive benefits.\n"
        elif global_vars.language == "日本語":
            str = "装備セット効果:\n"
            if set_name != "None" and set_name != "Void":
                str += self.equip["Weapon"].four_set_effect_description_jp
            else:
                str += "装備セット効果ありません。\n"
        str += "\n"
        str += "=" * 20 + "\n"
        for effect in self.buffs:
            if effect.is_set_effect:
                if global_vars.language == "English":
                    str += effect.print_stats_html()
                elif global_vars.language == "日本語":
                    str += effect.print_stats_html_jp()
                str += "\n"
        str += "=" * 20 + "\n"
        for effect in self.debuffs:
            if effect.is_set_effect:
                if global_vars.language == "English":
                    str += effect.print_stats_html()
                elif global_vars.language == "日本語":
                    str += effect.print_stats_html_jp()
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
            self.battle_entry_effects_eqset()

    def battle_entry_effects_eqset(self):
        """
        This is called after battle_entry_effects, eq set like 1987 needs to trigger here
        """
        if self.get_equipment_set() == "1987":
            the_stat_dict = {"atk": self.atk, "defense": self.defense, "spd": self.spd}
            # select the highest stat
            selected_stat = max(the_stat_dict, key=the_stat_dict.get)
            if selected_stat == "atk":
                ally_to_buff: Character = min(self.ally, key=lambda x: x.atk)
                e = StatsEffect("1987", -1, True, main_stats_additive_dict={"atk": self.atk * (0.2555)}, is_set_effect=True)
                e.can_be_removed_by_skill = False
                ally_to_buff.apply_effect(e)
            elif selected_stat == "defense":
                ally_to_buff: Character = min(self.ally, key=lambda x: x.defense)
                e = StatsEffect("1987", -1, True, main_stats_additive_dict={"defense": self.defense * (0.2555)}, is_set_effect=True)
                e.can_be_removed_by_skill = False
                ally_to_buff.apply_effect(e)
            elif selected_stat == "spd":
                ally_to_buff: Character = min(self.ally, key=lambda x: x.spd)
                e = StatsEffect("1987", -1, True, main_stats_additive_dict={"spd": self.spd * (0.2555)}, is_set_effect=True)
                e.can_be_removed_by_skill = False
                ally_to_buff.apply_effect(e)
        elif self.get_equipment_set() == "7891":
            # "Select the lowest one from 3 of your main stats: atk, def, spd. 55.55% of the selected stat is added to the ally who has the highest value of the selected stat."
            the_stat_dict = {"atk": self.atk, "defense": self.defense, "spd": self.spd}
            # select the lowest stat
            selected_stat = min(the_stat_dict, key=the_stat_dict.get)
            if selected_stat == "atk":
                ally_to_buff: Character = max(self.ally, key=lambda x: x.atk)
                e = StatsEffect("7891", -1, True, main_stats_additive_dict={"atk": self.atk * 0.5555}, is_set_effect=True)
                e.can_be_removed_by_skill = False
                ally_to_buff.apply_effect(e)
            elif selected_stat == "defense":
                ally_to_buff: Character = max(self.ally, key=lambda x: x.defense)
                e = StatsEffect("7891", -1, True, main_stats_additive_dict={"defense": self.defense * 0.5555}, is_set_effect=True)
                e.can_be_removed_by_skill = False
                ally_to_buff.apply_effect(e)
            elif selected_stat == "spd":
                ally_to_buff: Character = max(self.ally, key=lambda x: x.spd)
                e = StatsEffect("7891", -1, True, main_stats_additive_dict={"spd": self.spd * 0.5555}, is_set_effect=True)
                e.can_be_removed_by_skill = False
                ally_to_buff.apply_effect(e)



    def record_battle_turns(self, increment=1):
        self.battle_turns += increment


class Lillia(Character):
    """
    A reference to a dead mobile game character
    Persistant CC immune and damage reduction safe attacker
    Build: crit, critdmg, penetration, atk
    """
    def __init__(self, name, lvl, exp=0, equip=None, image=None):
        super().__init__(name, lvl, exp, equip, image)
        self.name = "Lillia"
        self.is_main_character = True
        self.skill1_description = "12 hits on random enemies, 155% atk each hit. After 1 critical hit, all hits following will be critical and hit nearby targets for 20% of damage dealt as status damage."
        self.skill2_description = "Apply Infinite Spring on self for 30 turns, gain immunity to CC and reduce damage taken by 35%. Refreshes duration if already active. Infinite Spring cannot be removed by skills."
        self.skill3_description = "Heal 8% of your maximum HP when Infinite Spring is active."
        self.skill1_description_jp = "ランダムな敵に攻撃力155%12回攻撃。1回のクリティカルヒット後、その後の全ての攻撃がクリティカルヒットとなり、周囲の敵に先与えたダメージの20%の状態ダメージを与える。"
        self.skill2_description_jp = "自身に無限の泉を30ターン付与し、CC無効、ダメージを35%軽減。効果が既に付与されている場合、効果時間更新される。無限の泉はスキルによって除去されない。"
        self.skill3_description_jp = "行動時、無限の泉が付与されている場合、最大HPの8%回復。"
        self.skill1_cooldown_max = 5
        self.skill2_cooldown_max = 4

    def skill1_logic(self):
        def water_splash(self, target, final_damage, always_crit):
            always_crit = True
            for target in target.get_neighbor_allies_not_including_self():
                if target.is_alive():
                    target.take_status_damage(final_damage * 0.2 * random.uniform(0.8, 1.2), self)
            return final_damage, always_crit
        damage_dealt = self.attack(multiplier=1.55, repeat=12, func_after_crit=water_splash)
        return damage_dealt

    def skill2_logic(self):
        e = ReductionShield("Infinite Spring", 30, True, 0.35, cc_immunity=True)
        e.apply_rule = "stack"
        e.can_be_removed_by_skill = False
        self.apply_effect(e)
        return None

    def skill3(self):
        if self.has_effect_that_named("Infinite Spring"):
            self.heal_hp(self.maxhp * 0.08, self)

    def action(self):
        self.skill3()
        super().action()


class Poppy(Character):
    """
    Many character skill ideas are from afk mobile games, this line is written in 2024/01/18
    Attacker, can be paired with high damage reduction support to utilize burn effect
    Build: atk, crit, critdmg, penetration
    """
    def __init__(self, name, lvl, exp=0, equip=None, image=None):
        super().__init__(name, lvl, exp, equip, image)
        self.name = "Poppy"
        self.skill1_description = "8 hits on random enemies, 240% atk each hit."
        self.skill2_description = "590% atk on enemy with highest speed. Apply Purchased! on target for 20 turns. Purchased!: speed is decreased by 30%."
        self.skill3_description = "On taking normal damage, 60% chance to inflict Burn to attacker for 20 turns. Burn deals 20% atk status damage."
        self.skill1_description_jp = "ランダムな敵に攻撃力240%8回攻撃。"
        self.skill2_description_jp = "速度一番高いの敵に攻撃力590%攻撃。20ターンの間、「注文!」を付与しする。「注文!」:速度を30%減少する。"
        self.skill3_description_jp = "通常ダメージを受けた時、攻撃者に20ターンの間、攻撃力20%の燃焼効果を付与する。"
        self.skill1_cooldown_max = 5
        self.skill2_cooldown_max = 5

    def skill1_logic(self):
        damage_dealt = self.attack(multiplier=2.4, repeat=8)      
        return damage_dealt

    def skill2_logic(self):
        def decrease_speed(self, target):
            stat_dict = {"spd": 0.7}
            target.apply_effect(StatsEffect("Purchased!", 20, False, stat_dict))
        damage_dealt = self.attack(multiplier=5.9, repeat=1, func_after_dmg=decrease_speed, target_kw1="n_highest_attr", target_kw2="1", target_kw3="spd", target_kw4="enemy")
        return damage_dealt

    def skill3(self):
        pass

    def take_damage_aftermath(self, damage, attacker):
        if random.randint(1, 100) <= 60:
            attacker.apply_effect(ContinuousDamageEffect("Burn", 20, False, self.atk * 0.2, self))


class Cate(Character):
    """
    Generic attacker
    Build: atk, penetration
    """    
    def __init__(self, name, lvl, exp=0, equip=None, image=None):
        super().__init__(name, lvl, exp, equip, image)
        self.name = "Cate"
        self.skill1_description = "4 hits on random enemies, 245% atk each hit, each hit has a 50% chance to stun for 10 turns."
        self.skill2_description = "Attack all enemies for 220% atk, damage increases by 60% if you have higher atk than target."
        self.skill3_description = "Apply Cat Ritual for yourself. Cat Ritual: Increases atk and critdmg by 20%. When hp is below 40%, reduce damage taken by 40%."
        self.skill1_description_jp = "ランダムな敵に攻撃力245%4回攻撃。各攻撃50%の確率で10ターンの間スタンさせる。"
        self.skill2_description_jp = "全ての敵に攻撃力220%攻撃。自分の攻撃力が対象より高い場合、ダメージが60%増加する。"
        self.skill3_description_jp = "「猫儀式」を付与する。「猫儀式」:攻撃力とクリティカルダメージを20%増加。HPが40%以下の時、受けるダメージを40%軽減する。"
        self.skill1_cooldown_max = 5
        self.skill2_cooldown_max = 5

    def skill1_logic(self):
        def stun_effect(self, target):
            dice = random.randint(1, 100)
            if dice <= 50:
                target.apply_effect(StunEffect("Stun", 10, False))
        damage_dealt = self.attack(multiplier=2.45, repeat=4, func_after_dmg=stun_effect)
        return damage_dealt

    def skill2_logic(self):
        def bonus_damage(self, target, final_damage):
            if self.atk > target.atk:
                final_damage *= 1.6
            return final_damage
        damage_dealt = self.attack(target_kw1="n_random_enemy",target_kw2="5", multiplier=2.2, repeat=1, func_damage_step=bonus_damage)
        return damage_dealt

    def skill3(self):
        pass

    def battle_entry_effects(self):
        effect = ReductionShield("Cat Ritual", -1, True, 0.4, cc_immunity=False, 
                                 requirement=lambda a, b: a.hp <= a.maxhp * 0.4,
                                 requirement_description="hp below 40%.",
                                 requirement_description_jp="HPが40%以下。")
        effect.can_be_removed_by_skill = False
        self.apply_effect(effect)
        effect2 = StatsEffect("Cat Ritual", -1, True, {"atk": 1.2, "critdmg": 0.2})
        effect2.can_be_removed_by_skill = False
        self.apply_effect(effect2)


class Cattee(Character):
    """
    High accuracy attacker
    Build: atk, penetration
    """    
    def __init__(self, name, lvl, exp=0, equip=None, image=None):
        super().__init__(name, lvl, exp, equip, image)
        self.name = "Cattee"
        self.skill1_description = "Attack 1 random enemy with 480% atk, inflict Stun for 10 turns and Bind for 20 turns."
        " Bind: All main stats except maxhp are reduced by 30%."
        self.skill2_description = "Attack random enemies with 220% atk 6 times, each attack has a 40% chance to inflict Burn for 20 turns," \
        " dealing 10% atk status damage each turn."
        self.skill3_description = "Apply Accurate Lock-On and Cat Ritual on yourself, accuracy is increased by 20%, everytime you miss an attack," \
        " accuracy is increased by 20%. When hp is below 40%, reduce damage taken by 40%."
        self.skill1_description_jp = "ランダムな敵1体に攻撃力の480%で攻撃し、10ターンの間スタンと20ターンの間「束縛」を付与する。束縛：最大HPを除く全ての主要ステータスが30%減少する。"
        self.skill2_description_jp = "ランダムな敵に攻撃力の220%で6回攻撃し、各攻撃に40%の確率で20ターンの間「燃焼」を付与する。燃焼は毎ターン攻撃力の10%分の状態異常ダメージを与える。"
        self.skill3_description_jp = "自身に「精密ロックオン」と「猫の儀式」を付与する。命中率が20%増加し、攻撃をミスするたびに命中率がさらに20%増加する。HPが40%以下の場合、受けるダメージが40%減少する。"
        self.skill1_cooldown_max = 5
        self.skill2_cooldown_max = 5

    def skill1_logic(self):
        def stun_and_bind(self, target):
            target.apply_effect(StunEffect("Stun", 10, False))
            target.apply_effect(StatsEffect("Bind", 20, False, {"atk": 0.70, "defense": 0.70, "spd": 0.70}))
        damage_dealt = self.attack(multiplier=4.8, repeat=1, func_after_dmg=stun_and_bind)
        return damage_dealt

    def skill2_logic(self):
        def burn(self, target):
            if random.randint(1, 100) <= 40:
                target.apply_effect(ContinuousDamageEffect("Burn", 20, False, self.atk * 0.10, self))
        damage_dealt = self.attack(multiplier=2.2, repeat=6, func_after_dmg=burn)
        return damage_dealt

    def skill3(self):
        pass

    def battle_entry_effects(self):
        self.apply_effect(StatsEffect("Accurate Lock-On", -1, True, {"acc": 0.20}, 
                                      stats_dict_value_increase_when_missing_attack=0.2, can_be_removed_by_skill=False))
        e2 = ReductionShield("Cat Ritual", -1, True, 0.4, cc_immunity=False,
                                            requirement=lambda a, b: a.hp <= a.maxhp * 0.4,
                                            requirement_description="hp below 40%.",
                                            requirement_description_jp="HPが40%以下。")
        e2.can_be_removed_by_skill = False
        self.apply_effect(e2)




class Iris(Character):
    """
    Generic attacker, attack all enemies
    Build: atk, crit, critdmg, penetration
    """    
    def __init__(self, name, lvl, exp=0, equip=None, image=None):
        super().__init__(name, lvl, exp, equip, image)
        self.name = "Iris"
        self.skill1_description = "Deals 310% atk damage to all enemies."
        self.skill2_description = "Deals 305% atk damage to all enemies and inflicts Burn, which deals status damage equal to 10% of atk for 30 turns."
        self.skill3_description = "At the start of the battle, applies a Cancellation Shield to the ally with the highest atk." \
                                  "Cancels one attack if the attack damage exceeds 10% of the ally's max HP. While the shield is active, the ally gains immunity to CC effects."
        self.skill1_description_jp = "全ての敵に攻撃力310%のダメージを与える。"
        self.skill2_description_jp = "全ての敵に攻撃力305%のダメージを与え、燃焼効果を付与。燃焼効果は攻撃力の10%の状態異常ダメージを30ターン与える。"
        self.skill3_description_jp = "戦闘開始時、攻撃力が最も高い味方にキャンセルシールドを付与。攻撃ダメージが味方の最大HPの10%を超える場合、1回の攻撃を無効化する。シールドが付与されている間、CC免疫を獲得。"
        self.skill1_cooldown_max = 5
        self.skill2_cooldown_max = 5

    def skill1_logic(self):
        damage_dealt = self.attack(target_kw1="n_random_enemy",target_kw2="5", multiplier=3.1, repeat=1)            
        return damage_dealt

    def skill2_logic(self):
        def burn(self, target):
            target.apply_effect(ContinuousDamageEffect("Burn", 30, False, self.atk * 0.10, self))
        damage_dealt = self.attack(target_kw1="n_random_enemy",target_kw2="5", multiplier=3.05, repeat=1, func_after_dmg=burn)
        return damage_dealt

    def skill3(self):
        pass

    def battle_entry_effects(self):
        ally_with_highest_atk = mit.one(self.target_selection("n_highest_attr", "1", "atk", "ally"))
        ally_with_highest_atk.apply_effect(CancellationShield("Cancellation Shield", -1, True, 0.1, cc_immunity=True))


class Freya(Character): 
    """
    Generic attacker, target specific enemy, silence
    Build: atk, crit, critdmg, penetration, spd
    """
    def __init__(self, name, lvl, exp=0, equip=None, image=None):
        super().__init__(name, lvl, exp, equip, image)
        self.name = "Freya"
        self.skill1_description = "600% atk on 1 enemy, silence the target for 20 turns, always target the enemy with highest atk."
        self.skill2_description = "580% atk on 1 enemy, always target the enemy with lowest hp."
        self.skill3_description = "Apply Absorption Shield on self if an ememy is taken down by your skill 2. Shield will absorb up to 900% of your atk damage."
        self.skill1_description_jp = "1体の敵に攻撃力600%攻撃。対象を20ターンの間、沈黙状態にする。常に攻撃力が最も高い敵を対象とする。"
        self.skill2_description_jp = "1体の敵に攻撃力580%攻撃。常にHPが最も低い敵を対象とする。"
        self.skill3_description_jp = "スキル2で敵を倒した場合、自身に吸収シールドを付与。シールドは攻撃力の900%までのダメージを吸収する。"
        self.skill1_cooldown_max = 4
        self.skill2_cooldown_max = 4

    def skill1_logic(self):
        def silence_effect(self, target):
            target.apply_effect(SilenceEffect("Silence", 20, False))
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


class FreyaSK(Character): 
    """
    Sweets Kingdom version of Freya
    Silence
    Build: 
    """
    def __init__(self, name, lvl, exp=0, equip=None, image=None):
        super().__init__(name, lvl, exp, equip, image)
        self.name = "FreyaSK"
        self.skill1_description = "Attack 1 closest enemy with 500% atk, silence the target for 12 turns. If target already has Silence," \
        " refresh the duration of Silence and" \
        " apply Dilemma on target for 20 turns. Dilemma: critical rate is reduced by 40%."
        self.skill2_description = "Attack 1 closest enemy with 500% atk and silence the target for 12 turns. If target already has Silence," \
        " refresh the duration of Silence and apply Bind on target for 20 turns. Bind: All main stats except maxhp are reduced by 15%."
        self.skill3_description = "Apply Doughnut Guard on yourself. When taking normal damage from an Silenced enemy, damage is reduced by 70%." \
        " If you take down an enemy with a skill, apply Cancellation Shield on yourself, shield will cancel up to 5 normal damage and provide CC immunity."
        self.skill1_description_jp = "最も近い敵1体に攻撃力の500%で攻撃し、12ターンの間「沈黙」を付与する。対象が既に沈黙状態の場合、沈黙の持続時間を更新し、20ターンの間「難局」を付与する。難局：クリティカル率が40%減少する。"
        self.skill2_description_jp = "最も近い敵1体に攻撃力の500%で攻撃し、12ターンの間「沈黙」を付与する。対象が既に沈黙状態の場合、沈黙の持続時間を更新し、20ターンの間「束縛」を付与する。束縛：最大HPを除く全ての主要ステータスが15%減少する。"
        self.skill3_description_jp = "自身に「ドーナツガード」を付与する。沈黙状態の敵から通常ダメージを受けた場合、そのダメージが70%減少する。スキルで敵を倒した場合、自身に「キャンセレーションシールド」を付与し、このシールドは通常ダメージを最大5回無効化し、CC免疫を付与する。"
        self.skill1_cooldown_max = 3
        self.skill2_cooldown_max = 3

    def skill1_logic(self):
        def effect(self, target: Character):
            silenced = target.has_effect_that_named("Silence")
            target.apply_effect(SilenceEffect("Silence", 12, False))
            if silenced:
                target.apply_effect(StatsEffect("Dilemma", 20, False, {"crit": -0.4}))
            if target.is_dead():
                self.apply_effect(CancellationShield("Cancellation Shield", -1, True, 0, cc_immunity=True, uses=5, cover_status_damage=False))
        damage_dealt = self.attack(target_kw1="enemy_in_front", multiplier=5.0, repeat=1, func_after_dmg=effect)
        return damage_dealt

    def skill2_logic(self):
        def effect(self, target: Character):
            silenced = target.has_effect_that_named("Silence")
            target.apply_effect(SilenceEffect("Silence", 12, False))
            if silenced:
                target.apply_effect(StatsEffect("Bind", 20, False, {"atk": 0.85, "defense": 0.85, "spd": 0.85}))
            if target.is_dead():
                self.apply_effect(CancellationShield("Cancellation Shield", -1, True, 0, cc_immunity=True, uses=5, cover_status_damage=False))
        damage_dealt = self.attack(target_kw1="enemy_in_front", multiplier=5.0, repeat=1, func_after_dmg=effect)
        return damage_dealt

    def skill3(self):
        pass

    def battle_entry_effects(self):
        def requirement_func(charac: Character, attacker: Character):
            return attacker.has_effect_that_named("Silence")
        doughnut_guard = ReductionShield("Doughnut Guard", -1, True, 0.7, False, cover_normal_damage=True, cover_status_damage=False,
                                         requirement=requirement_func,
                                         requirement_description="When taking normal damage from an Silenced enemy.",
                                         requirement_description_jp="沈黙状態の敵から通常ダメージを受けた時。")
        doughnut_guard.can_be_removed_by_skill = False
        self.apply_effect(doughnut_guard)


class FreyaBP(Character): 
    """
    Bath Play version of Freya
    Special Silence
    Build: 
    """
    def __init__(self, name, lvl, exp=0, equip=None, image=None):
        super().__init__(name, lvl, exp, equip, image)
        self.name = "FreyaBP"
        self.skill1_description = "Attack 1 random enemy with 570% atk, if target is ducky silenced, apply Bind and Dilemma for 20 turns." \
        " Bind: reduce atk, def, spd by 30%. Dilemma: reduce crit rate by 60%."
        self.skill2_description = "Attack 1 random enemy with 570% atk, apply Ducky Silence for 10 turns." \
        " Ducky Silence: Functions the same as Silence, when this effect is removed, a new Ducky Silence is applied on a random ally." \
        " If target is already Ducky Silenced, cooldown of skill1 is reduced by 2."
        self.skill3_description = "Apply Ducky Guard on yourself. When taking damage from a silenced or ducky silenced enemy, damage is reduced by 70%." \
        " If you take down an enemy with a skill, apply Cancellation Shield and Absorption Shield on yourself." \
        " Cancellation Shield: cancel up to 5 normal damage and provide CC immunity. Absorption Shield: absorb up to 800% of your atk damage."
        # 沈黙のカモ
        self.skill1_description_jp = "ランダムな敵1体に攻撃力の570%で攻撃し、対象がカモ沈黙状態の場合、20ターンの間「束縛」と「難局」を付与する。束縛：攻撃力、防御力、速度を30%減少させる。難局：クリティカル率を60%減少させる。"
        self.skill2_description_jp = "ランダムな敵1体に攻撃力の570%で攻撃し、10ターンの間「カモ沈黙」を付与する。カモ沈黙：沈黙と同じ効果を持ち、この効果が解除されると新たなカモ沈黙がランダムな味方に付与される。対象が既にカモ沈黙状態の場合、スキル1のクールダウンが2減少する。"
        self.skill3_description_jp =  "自身に「カモ防御」を付与する。沈黙またはカモ沈黙状態の敵からダメージを受けた時、そのダメージが70%減少する。スキルで敵を倒した場合、自身に「キャンセルシールド」と「吸収シールド」を付与する。キャンセルシールド：通常ダメージを最大5回無効化し、CC免疫を提供する。吸収シールド：攻撃力の800%分のダメージを吸収する。"
        self.skill1_cooldown_max = 3
        self.skill2_cooldown_max = 3

    def skill1_logic(self):
        def effect(self, target: Character):
            if target.has_effect_that_named(None, None, "FreyaDuckySilenceEffect"):
                target.apply_effect(StatsEffect("Bind", 20, False, {"atk": 0.7, "defense": 0.7, "spd": 0.7}))
                target.apply_effect(StatsEffect("Dilemma", 20, False, {"crit": -0.6}))
                # print("Ducky Silenced, effect applied.")
            if target.is_dead():
                self.apply_effect(CancellationShield("Cancellation Shield", -1, True, 0, cc_immunity=True, uses=5, cover_status_damage=False))
                self.apply_effect(AbsorptionShield("Absorption Shield", -1, True, self.atk * 8, cc_immunity=False))
        damage_dealt = self.attack(multiplier=5.7, repeat=1, func_after_dmg=effect)
        return damage_dealt

    def skill2_logic(self):
        def duckysilence_effect(self: Character, target: Character):
            if target.has_effect_that_named(None, None, "FreyaDuckySilenceEffect"):
                self.skill1_cooldown = max(0, self.skill1_cooldown - 2)
                # print(f"Skill 1 cooldown reduced to {self.skill1_cooldown}")
            target.apply_effect(FreyaDuckySilenceEffect("Ducky Silence", 10, False))
            if target.is_dead():
                self.apply_effect(CancellationShield("Cancellation Shield", -1, True, 0, cc_immunity=True, uses=5, cover_status_damage=False))
                self.apply_effect(AbsorptionShield("Absorption Shield", -1, True, self.atk * 8, cc_immunity=False))
        damage_dealt = self.attack(multiplier=5.7, repeat=1, func_after_dmg=duckysilence_effect)
        return damage_dealt

    def skill3(self):
        pass

    def battle_entry_effects(self):
        def requirement_func(charac: Character, attacker: Character):
            return attacker.has_effect_that_named("Silence") or attacker.has_effect_that_named("Ducky Silence")
        ducky_guard = ReductionShield("Ducky Guard", -1, True, 0.7, False, cover_normal_damage=True, cover_status_damage=True,
                                         requirement=requirement_func,
                                         requirement_description="When taking damage from an Silenced or Ducky Silenced enemy.",
                                         requirement_description_jp="沈黙状態または沈黙のカモ状態の敵からダメージを受けた時。")
        ducky_guard.can_be_removed_by_skill = False
        self.apply_effect(ducky_guard)


class Luna(Character):
    """
    Generic attacker, attack all enemies, heal self
    Build: atk, crit, critdmg, penetration
    """
    def __init__(self, name, lvl, exp=0, equip=None, image=None):
        super().__init__(name, lvl, exp, equip, image)
        self.name = "Luna"
        self.skill1_description = "Attack all enemies with 300% atk, recover 12% of damage dealt as hp."
        self.skill2_description = "Attack all enemies with 300% atk, apply Moonlight on self for next 10 turns, reduce damage taken by 90%."
        self.skill3_description = "Recover 8% hp of maxhp at start of action."
        self.skill1_description_jp = "全ての敵に攻撃力300%攻撃。与えたダメージの12%をHP回復。"
        self.skill2_description_jp = "全ての敵に攻撃力300%攻撃。自身に10ターンの月光を付与し、受けるダメージを90%軽減する。"
        self.skill3_description_jp = "行動時、HPが最大HPの8%分回復する。"
        self.skill1_cooldown_max = 5
        self.skill2_cooldown_max = 5

    def skill1_logic(self):
        damage_dealt = self.attack(target_kw1="n_random_enemy",target_kw2="5", multiplier=3.0, repeat=1)
        if self.is_alive():
            self.heal_hp(damage_dealt * 0.12, self)    
        return damage_dealt

    def skill2_logic(self):
        def moonlight(self):
            e = ReductionShield("Moonlight", 10, True, 0.9, cc_immunity=False)
            e.apply_rule = "stack"
            self.apply_effect(e)
        damage_dealt = self.attack(target_kw1="n_random_enemy",target_kw2="5", multiplier=3.0, repeat=1)
        if self.is_alive():
            moonlight(self)
        return damage_dealt

    def skill3(self):
        self.heal_hp(self.maxhp * 0.08, self)

    def action(self):
        self.skill3()
        super().action()


class Clover(Character):
    """
    Healer, target low hp
    Build: atk, acc
    """
    def __init__(self, name, lvl, exp=0, equip=None, image=None):
        super().__init__(name, lvl, exp, equip, image)
        self.name = "Clover"
        self.skill1_description = "Target 1 ally with lowest hp and 1 closest enemy, deal 460% atk damage to enemy and heal ally for 100% of damage dealt."
        self.skill2_description = "Target 1 ally with lowest hp, heal for 350% atk and grant Absorption Shield, absorb damage up to 350% atk."
        self.skill3_description = "Every time an ally is healed by yourself, heal for 60% of that amount."
        self.skill1_description_jp = "HPが最も低い味方1体と最も近い敵1体を対象に、敵に攻撃力460%のダメージを与え、味方を与えたダメージの100%で治療する。"
        self.skill2_description_jp = "HPが最も低い味方1体を対象に、攻撃力350%で治療し、攻撃力350%吸収シールドを付与する。"
        self.skill3_description_jp = "自分が味方が治療する度、その量の60%で自分を治療する。"
        self.skill1_cooldown_max = 3
        self.skill2_cooldown_max = 2

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


class Ruby(Character): 
    """
    Attacker, stun, target closest
    Build: atk, crit, critdmg, penetration
    """
    def __init__(self, name, lvl, exp=0, equip=None, image=None):
        super().__init__(name, lvl, exp, equip, image)
        self.name = "Ruby"
        self.skill1_description = "350% atk on 3 closest enemies. 70% chance to inflict stun for 10 turns."
        self.skill2_description = "350% focus atk on 1 closest enemy for 3 times. Each attack has 50% chance to inflict stun for 10 turns."
        self.skill3_description = "Skill damage is increased by 30% on stunned targets."
        self.skill1_description_jp = "最も近い敵3体に攻撃力350%攻撃。70%の確率で10ターンの間スタンさせる。"
        self.skill2_description_jp = "最も近い敵1体に攻撃力350%3回集中攻撃。各攻撃50%の確率で10ターンの間スタンさせる。"
        self.skill3_description_jp = "スタン状態の敵に対して、スキルダメージが30%増加。"
        self.skill1_cooldown_max = 5
        self.skill2_cooldown_max = 5

    def skill1_logic(self):
        def stun_effect(self, target):
            dice = random.randint(1, 100)
            if dice <= 70:
                target.apply_effect(StunEffect('Stun', duration=10, is_buff=False))
        def stun_amplify(self, target, final_damage):
            if target.has_effect_that_named("Stun"):
                final_damage *= 1.3
            return final_damage
        damage_dealt = self.attack(target_kw1="n_enemy_in_front",target_kw2="3", multiplier=3.5, repeat=1, func_after_dmg=stun_effect, func_damage_step=stun_amplify)            
        return damage_dealt

    def skill2_logic(self):
        def stun_effect(self, target):
            dice = random.randint(1, 100)
            if dice <= 50:
                target.apply_effect(StunEffect('Stun', duration=10, is_buff=False))
        def stun_amplify(self, target, final_damage):
            if target.has_effect_that_named("Stun"):
                final_damage *= 1.3
            return final_damage
        damage_dealt = self.attack(multiplier=3.5, repeat_seq=3, func_after_dmg=stun_effect, func_damage_step=stun_amplify, target_kw1="enemy_in_front")
        return damage_dealt

    def skill3(self):
        pass


class Olive(Character):
    """
    Generic Attacker or support
    Build: atk, spd
    """
    def __init__(self, name, lvl, exp=0, equip=None, image=None):
        super().__init__(name, lvl, exp, equip, image)
        self.name = "Olive"
        self.skill1_description = "540% atk on 1 enemy with the highest atk. Decrease target's atk by 50% for 20 turns."
        self.skill2_description = "Heal 3 allies with lowest hp by 270% atk and increase their speed by 35% for 20 turns. "
        self.skill3_description = "Normal attack deals 120% more damage if target has less speed than self."
        self.skill1_description_jp = "最も高い攻撃力の敵に攻撃力540%攻撃。対象の攻撃力を20ターンの間、50%減少。"
        self.skill2_description_jp = "HPが最も低い味方3体を攻撃力270%で治療し、20ターンの間、速度を35%増加させる。"
        self.skill3_description_jp = "通常攻撃時、対象の速度が自分より低い場合、ダメージが120%増加する。"
        self.skill1_cooldown_max = 4
        self.skill2_cooldown_max = 4

    def skill1_logic(self):
        def effect(self, target):
            stat_dict = {"atk": 0.5}
            target.apply_effect(StatsEffect("Weaken", 20, False, stat_dict))
        damage_dealt = self.attack(multiplier=5.7, repeat=1, func_after_dmg=effect, target_kw1="n_highest_attr", target_kw2="1", target_kw3="atk", target_kw4="enemy")             
        return damage_dealt

    def skill2_logic(self):
        def effect(self, target, healing, overhealing):
            target.apply_effect(StatsEffect("Tailwind", 20, True, {"spd": 1.35}))
        healing_done = self.heal("n_lowest_attr", "3", "hp", "ally", self.atk * 2.7, 1, func_after_each_heal=effect)
        return None

    def skill3(self):
        pass

    def normal_attack(self):
        def effect(self, target, final_damage):
            if target.spd < self.spd:
                final_damage *= 2.20
            return final_damage
        self.attack(func_damage_step=effect)


class Fenrir(Character):
    """
    Support, pairs will with tanks
    Build: hp, def, spd
    """
    def __init__(self, name, lvl, exp=0, equip=None, image=None):
        super().__init__(name, lvl, exp, equip, image)
        self.name = "Fenrir"
        self.skill1_description = "Focus attack 3 times on closest enemy, 220% atk each hit. Reduce skill cooldown for neighbor allies by 2 turns."
        self.skill2_description = "390% atk on a closest enemy. Remove 2 debuffs for neighbor allies."
        self.skill3_description = "Fluffy protection is applied to neighbor allies at start of battle. When the fluffy protected ally below 40% hp is about to take normal damage, the ally recovers hp by 55% of your current defense."
        self.skill1_description_jp = "最も近い敵に攻撃力220%で3回集中攻撃。隣接する味方のスキルクールダウンを2ターン減少。"
        self.skill2_description_jp = "最も近い敵に攻撃力390%攻撃。隣接する味方のデバフを2つ解除。"
        self.skill3_description_jp = "戦闘開始時、隣接する味方にもふもふ守護を付与。もふもふ守護の味方が40%以下のHPで通常ダメージを受ける時、自身の防御力の55%分味方を回復する。"
        self.skill1_cooldown_max = 5
        self.skill2_cooldown_max = 5

    def skill1_logic(self):
        damage_dealt = self.attack(multiplier=2.2, repeat_seq=3, target_kw1="enemy_in_front")
        neighbors = self.get_neighbor_allies_not_including_self() # list
        for ally in neighbors:
            ally.skill1_cooldown = max(ally.skill1_cooldown - 2, 0)
            ally.skill2_cooldown = max(ally.skill2_cooldown - 2, 0)
            global_vars.turn_info_string += f"{ally.name} skill cooldown reduced by 2.\n"                 
        return damage_dealt

    def skill2_logic(self):
        damage_dealt = self.attack(multiplier=3.9, repeat=1, target_kw1="enemy_in_front")
        neighbors = self.get_neighbor_allies_not_including_self() # list
        for ally in neighbors:
            ally.remove_random_amount_of_debuffs(2)
        return damage_dealt
        
    def skill3(self):
        pass

    def battle_entry_effects(self):
        neighbors = self.get_neighbor_allies_not_including_self()
        for ally in neighbors:
            e = EffectShield1("Fluffy Protection", -1, True, 0.4, lambda x: x.defense * 0.55, False, False, self, cover_status_damage=False)
            e.can_be_removed_by_skill = False
            ally.apply_effect(e)


class Cerberus(Character):
    """
    Attacker, execute, late power spike
    Build: crit, spd, def, atk
    """
    def __init__(self, name, lvl, exp=0, equip=None, image=None, execution_threshold=0.15):
        super().__init__(name, lvl, exp, equip, image)
        self.name = "Cerberus"
        self.execution_threshold = execution_threshold

        self.skill1_description = "5 hits on random enemies, 280% atk each hit. Decrease target's def by 12% for each hit. Effect last 40 turns."
        self.skill2_description = "Focus attack with 290% atk on 1 enemy with lowest hp for 3 times. If target hp is less then 16% during the attack, execute the target."
        self.skill3_description = "On sucessfully executing a target, increase execution threshold by 4%, recover 30% of maxhp and permenently increase atk and critdmg by 30%."
        self.skill1_description_jp = "ランダムな敵に攻撃力280%5回攻撃。各攻撃で対象の防御力を12%減少。効果は40ターン持続。"
        self.skill2_description_jp = "最も低いHPの敵に攻撃力290%で3回集中攻撃。攻撃中に対象のHPが16%以下の場合、対象を処刑する。"
        self.skill3_description_jp = "対象を処刑すると、処刑閾値を4%増加し、最大HPの30%回復、永久的攻撃力とクリティカルダメージを30%増加する。"
        self.skill1_cooldown_max = 5
        self.skill2_cooldown_max = 5

    def clear_others(self):
        self.execution_threshold = 0.16

    def skill_tooltip(self):
        return f"Skill 1 : {self.skill1_description}\nCooldown : {self.skill1_cooldown} action(s)\n\nSkill 2 : {self.skill2_description}\nCooldown : {self.skill2_cooldown} action(s)\n\nSkill 3 : {self.skill3_description}\n\nExecution threshold : {self.execution_threshold*100}%"

    def skill_tooltip_jp(self):
        return f"スキル1:{self.skill1_description_jp}\nクールダウン:{self.skill1_cooldown}行動\n\nスキル2:{self.skill2_description_jp}\nクールダウン:{self.skill2_cooldown}行動\n\nスキル3:{self.skill3_description_jp}\n\n処刑閾値:{self.execution_threshold*100}%"

    def skill1_logic(self):
        def effect(self, target):
            stat_dict = {"defense": 0.88}
            target.apply_effect(StatsEffect("Clawed", 40, False, stat_dict))
        damage_dealt = self.attack(multiplier=2.8, repeat=5, func_after_dmg=effect)             
        return damage_dealt

    def skill2_logic(self):
        def effect(self, target: Character):
            # does not make sense to execute self
            if target is self:
                return
            if target.hp < target.maxhp * self.execution_threshold and not target.is_dead():
                target.take_bypass_status_effect_damage(target.hp, self)
                global_vars.turn_info_string += f"{target.name} is executed by {self.name}.\n"
                self.execution_threshold += 0.04
                self.heal_hp(self.maxhp * 0.3, self)
                stats_dict = {"atk": 1.3, "critdmg": 0.3}
                self.update_stats(stats_dict)
        damage_dealt = self.attack(target_kw1="n_lowest_attr",target_kw2="1",target_kw3="hp",target_kw4="enemy", multiplier=2.9, repeat=1, repeat_seq=3, func_after_dmg=effect)
        return damage_dealt

    def skill3(self):
        pass


class Pepper(Character):
    """
    Generic support, revive
    Build: spd, def, hp
    """
    def __init__(self, name, lvl, exp=0, equip=None, image=None):
        super().__init__(name, lvl, exp, equip, image)
        self.name = "Pepper"
        self.skill1_description = "800% atk on closest enemy, 70% success rate, 20% chance to hit an ally with 300% atk," \
        " 10% chance to hit self with 300% atk. A failed attack resets cooldown, when targeting enemy, this attack cannot miss."
        self.skill2_description = "Heal an ally with lowest hp percentage with 800% atk, 70% success rate, 20% chance to have no effect, 10% chance to damage the ally with 200% atk. A failed healing resets cooldown."
        self.skill3_description = "On a successful healing with skill 2, 80% chance to accidently revive a ally with 80% hp."
        self.skill1_description_jp = "最も近い敵に攻撃力800%攻撃。成功率70%。味方に攻撃力300%攻撃する確率20%。自身に攻撃力300%攻撃する確率10%。失敗した場合、クールダウンがリセットされる。対象が敵の場合、この攻撃は必ず命中する。"
        self.skill2_description_jp = "HP割合が最も低い味方1体を攻撃力800%で治療。成功率70%。効果なしの確率20%。味方に攻撃力200%攻撃する確率10%。失敗した場合、クールダウンがリセットされる。"
        self.skill3_description_jp = "スキル2で治療が成功した時、確率80%で味方1体を80%のHPで復活させる。"
        self.skill1_cooldown_max = 3
        self.skill2_cooldown_max = 3

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
                dead_neighbors = [x for x in self.party if x.is_dead()]
                if dead_neighbors != []:
                    revive_target = random.choice(dead_neighbors)
                    revive_target.revive(0, 0.8, self)
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


class Cliffe(Character): 
    """
    Attacker, damage dealer, debuff
    Build: atk, crit, critdmg, penetration
    """ 
    def __init__(self, name, lvl, exp=0, equip=None, image=None):
        super().__init__(name, lvl, exp, equip, image)
        self.name = "Cliffe"
        self.skill1_description = "Attack 3 closest enemies with 280% atk, increase their damage taken by 20% for 30 turns."
        self.skill2_description = "Attack closest enemy 4 times for 330% atk, each successful attack and successful additional attack has 40% chance to trigger an 270% atk additional attack."
        self.skill3_description = "Recover hp by 10% of maxhp multiplied by targets fallen by skill 2."
        self.skill1_description_jp = "最も近い敵3体に攻撃力280%攻撃。30ターンの間、受けるダメージを20%増加させる。"
        self.skill2_description_jp = "最も近い敵に攻撃力330%4回攻撃。各攻撃と追加攻撃が命中する度、40%の確率で攻撃力270%の追加攻撃を発動する。"
        self.skill3_description_jp = "スキル2で倒した敵の数に最大HPの10%を掛けた値のHPを回復する。"
        self.skill1_cooldown_max = 5
        self.skill2_cooldown_max = 5

    def skill1_logic(self):
        def effect(self, target):
            target.apply_effect(ReductionShield("Crystal Breaker", 30, False, 0.2, False))
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
        damage_dealt = self.attack(multiplier=3.3, repeat=4, additional_attack_after_dmg=more_attacks, target_kw1="enemy_in_front")      
        if downed_target > 0 and self.is_alive():
            self.heal_hp(downed_target * 0.1 * self.maxhp, self)
        return damage_dealt
        
    def skill3(self):
        pass


class Pheonix(Character):
    """
    Status damage attacker
    Build: atk, hp, def, spd
    """
    def __init__(self, name, lvl, exp=0, equip=None, image=None):
        super().__init__(name, lvl, exp, equip, image)
        self.name = "Pheonix"
        self.skill1_description = "Attack all enemies with 160% atk, 80% chance to inflict burn for 25 turns. Burn deals 20% atk damage per turn."
        self.skill2_description = "First time cast: apply Reborn to all neighbor allies. " \
        "Reborn: when defeated, revive with 40% hp. Second and further cast: attack random enemy pair with 260% atk, 80% chance to inflict burn for 25 turns. " \
        "Burn deals 20% atk damage per turn."
        self.skill3_description = "Revive with 80% hp the next turn after fallen. When revived, increase atk by 20% for 30 turns." \
        " This effect cannot be removed by skill."
        self.skill1_description_jp = "全ての敵に190%の攻撃を行い、80%の確率で25ターンの間燃焼を付与する。燃焼は毎ターン攻撃力の20%の状態ダメージを与える。"
        self.skill2_description_jp = "初回発動時: 隣接する全ての味方に新生を付与する。" \
                                    "新生:倒された場合、HP40%で復活する。2回目以降の発動:ランダムな敵のペアに260%の攻撃を行い、80%の確率で25ターンの間燃焼を付与する。" \
                                    "燃焼は毎ターン攻撃力の20%の状態ダメージを与える。"
        self.skill3_description_jp = "倒れた次のターンにHP80%で復活する。復活した場合、攻撃力が30ターンの間20%増加する。" \
                                    "この効果はスキルで取り除くことができない。"
        self.first_time = True
        self.skill1_cooldown_max = 5
        self.skill2_cooldown_max = 5

    def clear_others(self):
        self.first_time = True

    def skill_tooltip(self):
        return f"Skill 1 : {self.skill1_description}\nCooldown : {self.skill1_cooldown} action(s)\n\nSkill 2 : {self.skill2_description}\nCooldown : {self.skill2_cooldown} action(s)\n\nSkill 3 : {self.skill3_description}\n\nFirst time on skill 2: {self.first_time}"

    def skill_tooltip_jp(self):
        return f"スキル1:{self.skill1_description_jp}\nクールダウン:{self.skill1_cooldown}行動\n\nスキル2:{self.skill2_description_jp}\nクールダウン:{self.skill2_cooldown}行動\n\nスキル3:{self.skill3_description_jp}\n\n初回スキル2発動:{self.first_time}"

    def skill1_logic(self):
        def burn_effect(self, target):
            if random.randint(1, 100) <= 80:
                target.apply_effect(ContinuousDamageEffect("Burn", 25, False, self.atk * 0.20, self))
        damage_dealt = self.attack(target_kw1="n_random_enemy",target_kw2="5", multiplier=1.6, repeat=1, func_after_dmg=burn_effect)         
        return damage_dealt

    def skill2_logic(self):
        if self.first_time:
            self.first_time = False
            allies = self.get_neighbor_allies_not_including_self()
            if not allies:
                return 0
            for ally in allies:
                ally.apply_effect(RebornEffect("Reborn", -1, True, 0.40, False, self))
            return 0
        else:
            def burn_effect(self, target):
                if random.randint(1, 100) <= 80:
                    target.apply_effect(ContinuousDamageEffect("Burn", 25, False, self.atk * 0.20, self))
            damage_dealt = self.attack(target_kw1="random_enemy_pair", multiplier=2.6, repeat=1, func_after_dmg=burn_effect)         
            return damage_dealt   

    def skill3(self):
        pass

    def after_revive(self):
        self.apply_effect(StatsEffect("Atk Up", 30, True, {"atk": 1.2}))

    def battle_entry_effects(self):
        e = RebornEffect("Reborn", -1, True, 0.80, False, self)
        e.can_be_removed_by_skill = False
        self.apply_effect(e)


class Tian(Character):
    """
    Attacker, critical chance reduction
    Build: atk, crit, critdmg, penetration, spd
    """
    def __init__(self, name, lvl, exp=0, equip=None, image=None):
        super().__init__(name, lvl, exp, equip, image)
        self.name = "Tian"
        self.skill1_description = "Attack 3 closest enemies with 400% atk and apply Dilemma for 30 turns. Dilemma: Critical chance is reduced by 100%."
        self.skill2_description = "Apply Soul Guard on self for 30 turns, Soul Guard: increase atk by 30% and damage reduction by 30%. If same effect is applied, duration is refleshed." \
        " Apply Sin to 1 enemy with highest atk for 30 turns. Sin: atk and critdmg is reduced by 30%," \
        " if defeated, all allies take status damage equal to 300% of self atk. This effect cannot be removed by skill."
        self.skill3_description = "Normal attack deals 120% more damage, before attacking, for 1 turn, increase critical chance by 40%."
        self.skill1_description_jp = "最も近い3体の敵に400%の攻撃を行い、30ターンの間難局を付与する。難局:クリティカル確率が100%減少する。"
        self.skill2_description_jp = "自身に30ターンの間ソウルガードを付与する。ソウルガード:攻撃力が30%増加し、被ダメージが30%軽減される。同じ効果が付与された場合、効果時間が更新される。" \
                                    "最も攻撃力の高い1体の敵に30ターンの間罪悪を付与する。罪悪:攻撃力とクリティカルダメージが30%減少し、" \
                                    "倒された場合、全ての味方が自身の攻撃力の600%に相当する状態ダメージを受ける。この効果はスキルで取り除くことができない。"
        self.skill3_description_jp = "通常攻撃のダメージが120%増加し、攻撃前に1ターンの間クリティカル確率が40%増加する。"
        self.skill1_cooldown_max = 4
        self.skill2_cooldown_max = 5

    def skill1_logic(self):
        def effect(self, target):
            target.apply_effect(StatsEffect("Dilemma", 30, False, {"crit": -1.0}))
        damage_dealt = self.attack(target_kw1="n_enemy_in_front",target_kw2="3", multiplier=4.0, repeat=1, func_after_dmg=effect)
        return damage_dealt

    def skill2_logic(self):
        soul_guard = StatsEffect("Soul Guard", 30, True, {"atk": 1.3, "final_damage_taken_multipler": -0.3})
        soul_guard.apply_rule = "stack"
        soul_guard.additional_name = "Tian_Soul_Guard"
        self.apply_effect(soul_guard)
        target = mit.one(self.target_selection(keyword="n_highest_attr", keyword2="1", keyword3="atk", keyword4="enemy"))
        target.apply_effect(SinEffect("Sin", 30, False, target.atk * 6.0, {"atk": 0.7, "critdmg": -0.3}, applier=self))
        return None

    def skill3(self):
        pass

    def normal_attack(self):
        self.apply_effect(StatsEffect("Critical Up", 1, True, {"crit": 0.4}))
        def effect(self, target, final_damage):
            final_damage *= 2.2
            return final_damage
        self.attack(func_damage_step=effect)


class Bell(Character):
    """
    Safe attacker, shield, always hit
    Build: atk, crit, critdmg, penetration, acc
    """
    def __init__(self, name, lvl, exp=0, equip=None, image=None):
        super().__init__(name, lvl, exp, equip, image)
        self.name = "Bell"
        self.skill1_description = "Attack 1 closest enemy with 220% atk 5 times."
        self.skill2_description = "Attack 1 closest enemy with 180% atk 6 times. This attack never misses. For each target fallen, trigger an additional attack. Maximum attacks: 8"
        self.skill3_description = "Once per battle, after taking damage that is higher than 0, if hp is below 50%, apply absorption shield, absorb damage up to 400% of damage just taken. For 20 turns, damage taken cannot exceed 20% of maxhp."
        self.skill1_description_jp = "最も近い1体の敵に220%の攻撃を5回行う。"
        self.skill2_description_jp = "最も近い1体の敵に180%の攻撃を6回行う。この攻撃はMISSにならない。敵が倒れるたびに追加攻撃を発動する。最大攻撃回数:8"
        self.skill3_description_jp = "戦闘中1回のみ、0以上のダメージを受けた後、HPが50%以下の場合、吸収シールドを適用し、受けたダメージの440%までを吸収する。20ターンの間、受けるダメージは最大HPの20%を超えない。"
        self.skill3_used = False
        self.skill1_cooldown_max = 5
        self.skill2_cooldown_max = 5

    def clear_others(self):
        self.skill3_used = False

    def skill1_logic(self):
        damage_dealt = self.attack(target_kw1="enemy_in_front", multiplier=2.2, repeat=5)
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
        damage_dealt = self.attack(target_kw1="enemy_in_front", multiplier=1.8, repeat=6, additional_attack_after_dmg=additional_attacks, always_hit=True)
        return damage_dealt

    def skill3(self):
        pass

    def take_damage_aftermath(self, damage, attacker):
        if not damage > 0:
            return
        if self.skill3_used:
            return
        if self.hp < self.maxhp * 0.5:
            self.apply_effect(CancellationShield("Cancellation Shield", 20, True, 0.2, False, cancel_excessive_instead=True, uses=100))
            self.apply_effect(AbsorptionShield("Absorption Shield", -1, True, damage * 4.4, cc_immunity=False))
            self.skill3_used = True



class Roseiri(Character):
    """
    Generic attacker, debuff, cc
    Build: atk, crit, critdmg, penetration
    """    
    def __init__(self, name, lvl, exp=0, equip=None, image=None):
        super().__init__(name, lvl, exp, equip, image)
        self.name = "Roseiri"
        self.skill1_description = "Attack 3 closest enemies for 380% atk, reduce their heal efficiency by 100% for the next 20 turns."
        self.skill2_description = "Attack 3 closest enemies for 360% atk, reduce their def by 40% for 20 turns."
        self.skill3_description = "Every time a skill is used, for 3 turns, reduce damage taken by 99%."
        self.skill1_description_jp = "最も近い3体の敵に攻撃力380%攻撃。20ターン対象の回復効果を100%減少させる。"
        self.skill2_description_jp = "最も近い3体の敵に攻撃力360%攻撃。20ターン対象の防御力を40%減少させる。"
        self.skill3_description_jp = "スキルを使用する度に、3ターンの間、受けるダメージを99%減少させる。"
        self.skill1_cooldown_max = 4
        self.skill2_cooldown_max = 4

    def skill1_logic(self):
        def unhealable_effect(self, target):
            target.apply_effect(StatsEffect("Unhealable", 20, False, {"heal_efficiency": -1.0}))
            immunity = ReductionShield("Immunity", 3, True, 0.99, cc_immunity=False)
            immunity.apply_rule = "stack"
            self.apply_effect(immunity)
        damage_dealt = self.attack(target_kw1="n_enemy_in_front",target_kw2="3", multiplier=3.8, repeat=1, func_after_dmg=unhealable_effect)
        return damage_dealt

    def skill2_logic(self):
        def defdown_effect(self, target):
            target.apply_effect(StatsEffect("Def Down", 20, False, {'defense' : 0.6}))
            immunity = ReductionShield("Immunity", 3, True, 0.99, cc_immunity=False)
            immunity.apply_rule = "stack"
            self.apply_effect(immunity)
        damage_dealt = self.attack(target_kw1="n_enemy_in_front",target_kw2="3", multiplier=3.6, repeat=1, func_after_dmg=defdown_effect)
        return damage_dealt

    def skill3(self):
        pass


class Fox(Character):
    """
    Tanky support, counter status effects
    Build: hp, spd, def
    """    
    def __init__(self, name, lvl, exp=0, equip=None, image=None):
        super().__init__(name, lvl, exp, equip, image)
        self.name = "Fox"
        self.skill1_description = "4 hits on random enemies, 220% atk each. Each attack has a 70% chance to increase the target's damage taken by 10% for 30 turns."
        self.skill2_description = "Using the angelic power gained through the contract, perform magic attack 4 times at" \
        " 160% atk against random enemies. If the number of stacks of 'Memory' is above 20 before the attack," \
        " 'Memory' is removed and Soul Sacrifice is activated instead of Angel Ray. Soul Sacrifice: Attack with" \
        " 180% atk 4 times on random enemies. After that, the skill cooldown count of 2 neighbor allies is reduced by 2 and their atk is increased by 3.6% of your maximum HP, for 30 turns."
        self.skill3_description = "At the end of each turn, if an ally is affected by a debuff effect, granted 1 stack of Memory," \
        " then the number of stacks of Memory increases by the total number of debuff effects you and your allies are affected by (up to a maximum of 20 stacks)." \
        " When Memory is at 20 stacks, apply a Absorption Shield on self that absorb damage up to 30% of maxhp. If shield is active, increase shield value by 1% of maxhp."
        self.skill1_description_jp = "ランダムな敵に220%の攻撃を4回行う。各攻撃には、70%確率で対象が30ターンの間受けるダメージが10%増加する。"
        self.skill2_description_jp = "契約によって得た天使の力を使用して、ランダムな敵に160%の攻撃を4回行う。攻撃前に「記憶」のスタック数が20以上の場合、" \
                                    "「記憶」は消費され、「エンジェルレイ」の代わりに「ソウルサクリファイス」が発動する。" \
                                    "ソウルサクリファイス:ランダムな敵に180%の攻撃を4回行う。その後、隣接する味方2体のスキルクールダウンカウントが2減少し、" \
                                    "攻撃力が自分の最大HPの3.6%増加する。この効果は30ターン続く。"
        self.skill3_description_jp = "各ターン終了時、味方がデバフ効果を受けている場合、1スタックの「記憶」を付与され、" \
                                    "自身および味方が受けているデバフ効果の合計数に応じて「記憶」スタックが増加する（最大20スタックまで）。" \
                                    "「記憶」が20スタックに達すると、自身に最大HPの30%を吸収するシールドを適用する。シールドがある場合、" \
                                    "シールド値が最大HPの1%増加する。"
        self.skill1_cooldown_max = 5
        self.skill2_cooldown_max = 5

    def skill1_logic(self):
        def effect(self, target):
            if random.randint(1, 100) <= 70:
                target.apply_effect(StatsEffect("Vulnerability Up", 30, False, {'final_damage_taken_multipler' : 0.1}))
        damage_dealt = self.attack(multiplier=2.2, repeat=4, func_after_dmg=effect)
        return damage_dealt

    def skill2_logic(self):
        memory = None
        memory = self.get_effect_that_named("Memory", "Fox_Memory")
        if memory and memory.stacks >= 20:
            self.remove_effect(memory)
            damage_dealt = self.attack(multiplier=1.8, repeat=4)
            neighbors = self.get_neighbor_allies_not_including_self()
            for ally in neighbors:
                ally.skill1_cooldown = max(ally.skill1_cooldown - 2, 0)
                ally.skill2_cooldown = max(ally.skill2_cooldown - 2, 0)
                global_vars.turn_info_string += f"{ally.name} skill cooldown reduced by 2.\n"
                ally.apply_effect(StatsEffect("Atk Up", 30, True, main_stats_additive_dict={'atk': int(self.maxhp * 0.036)}))
        else:
            damage_dealt = self.attack(multiplier=1.6, repeat=4)
        return damage_dealt
        

    def skill3(self):
        pass

    def status_effects_at_end_of_turn(self):
        if self.is_dead():
            return super().status_effects_at_end_of_turn()
        stacks_to_gain = 0
        for ally in self.ally:
            stacks_to_gain += len(ally.debuffs)
        memory = self.get_effect_that_named("Memory", "Fox_Memory")
        if memory and memory.stacks >= 20:
            memory.stacks = 20
            if not self.has_effect_that_named("Shield", "Fox_Shield"):
                shield = AbsorptionShield("Shield", -1, True, self.maxhp * 0.30, cc_immunity=False)
                shield.additional_name = "Fox_Shield"
                self.apply_effect(shield)
            else:
                shield = self.get_effect_that_named("Shield", "Fox_Shield")
                shield.shield_value += int(self.maxhp * 0.01)
        if stacks_to_gain > 0:
            if memory:
                memory.stacks += stacks_to_gain
                memory.stacks = min(memory.stacks, 20)
            else:
                new_memory = Effect("Memory", -1, True, False, can_be_removed_by_skill=False, show_stacks=True)
                new_memory.stacks += stacks_to_gain
                new_memory.additional_name = "Fox_Memory"
                new_memory.tooltip_str =  ".Cherished for 200 years."
                new_memory.tooltip_str_jp = "。200年の思い。"
                self.apply_effect(new_memory)
            global_vars.turn_info_string += f"{self.name} gained {stacks_to_gain} memories.\n"
        super().status_effects_at_end_of_turn()


class Taily(Character): 
    """
    A reference to a dead mobile game character
    Protector
    Build: hp, def
    Effect name is rediculous but does not matter
    """
    def __init__(self, name, lvl, exp=0, equip=None, image=None):
        super().__init__(name, lvl, exp, equip, image)
        self.name = "Taily"
        self.skill1_description = "305% atk on 3 closest enemies, Stun the target for 10 turns."
        self.skill2_description = "700% atk on enemy with highest hp, damage increased by 50% if target has more than 90% hp ratio."
        self.skill3_description = "At start of battle, apply Blessing of Firewood to all allies." \
        " When an ally is about to take normal damage, take the damage instead. Damage taken is reduced by 40% when taking damage for an ally." \
        " Cannot protect against status effect and status damage."
        self.skill1_description_jp = "最も近い3体の敵に305%の攻撃を行い、対象を10ターンの間スタンさせる。"
        self.skill2_description_jp = "最もHPが高い敵に700%の攻撃を行う。対象のHP割合が90%以上の場合、ダメージが50%増加する。"
        self.skill3_description_jp = "戦闘開始時に全ての味方に柴の加護を付与する。" \
                                    "味方が通常ダメージを受ける際、そのダメージを代わりに受ける。味方のためにダメージを受ける場合、被ダメージが40%軽減される。" \
                                    "状態異常および状態ダメージからは守れない。"
        self.skill1_cooldown_max = 5
        self.skill2_cooldown_max = 5

    def skill1_logic(self):
        def stun_effect(self, target):
            target.apply_effect(StunEffect('Stun', duration=10, is_buff=False))
        damage_dealt = self.attack(target_kw1="n_enemy_in_front",target_kw2="3", multiplier=3.05, repeat=1, func_after_dmg=stun_effect)
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
            e = ProtectedEffect("Blessing of Firewood", -1, True, False, self, 0.6, can_be_removed_by_skill=False)
            ally.apply_effect(e)


class Nobutuna(Character):
    """
    Protector, crit
    Build: 
    """
    def __init__(self, name, lvl, exp=0, equip=None, image=None):
        super().__init__(name, lvl, exp, equip, image)
        self.name = "Nobutuna"
        self.skill1_description = "Select 2 allies of highest atk, their crit chance is increased by 60%, crit damage is increased by 40% for 28 turns."
        self.skill2_description = "Attack random enemies 6 times with 300% atk."
        self.skill3_description = "At start of battle, apply Floating Moon to all allies." \
        " Floating Moon: When you are about to take normal damage, damage is reduced by 35%, the effect applier takes the 90% of that damage instead."
        self.skill1_description_jp = "攻撃力が最も高い味方2人を選び、28ターンの間、クリティカル率を60%、クリティカルダメージを40%増加させる。"
        self.skill2_description_jp = "ランダムな敵に攻撃力の300%で6回攻撃する。"
        self.skill3_description_jp = "戦闘開始時、全ての味方に「浮舟月影」を付与する。浮舟月影：通常ダメージを受ける際、そのダメージは35%減少し、効果の付与者がそのダメージの90%を代わりに受ける。"
        self.skill1_cooldown_max = 4
        self.skill2_cooldown_max = 4

    def skill1_logic(self):
        allies = self.target_selection(keyword="n_highest_attr", keyword2="2", keyword3="atk", keyword4="ally")
        for ally in allies:
            ally.apply_effect(StatsEffect("Crit Up", 28, True, {"crit": 0.6, "critdmg": 0.4}))
        return 0

    def skill2_logic(self):
        damage_dealt = self.attack(multiplier=3.0, repeat=6)
        return damage_dealt

    def skill3(self):
        pass

    def battle_entry_effects(self):
        allies = [x for x in self.ally if x != self]
        for ally in allies:
            e = ProtectedEffect("Floating Moon", -1, True, False, self, 0.65, 0.9, can_be_removed_by_skill=False)
            ally.apply_effect(e)


class NobutunaAL(Character):
    """
    Protector, critdmg, multi-attack
    Build: 
    """
    def __init__(self, name, lvl, exp=0, equip=None, image=None):
        super().__init__(name, lvl, exp, equip, image)
        self.name = "NobutunaAL"
        self.skill1_description = "Select 3 allies of highest atk, their crit damage is increased by 120% for 28 turns."
        self.skill2_description = "Attack random enemies 13 times with 180% atk."
        self.skill3_description = "At start of battle, apply Floating Moon to all allies." \
        " Floating Moon: When you are about to take normal damage, damage is reduced by 40%, the effect applier takes the 90% of that damage instead."
        self.skill1_description_jp = "攻撃力が最も高い味方3人を選び、28ターンの間、クリティカルダメージを120%増加させる。"
        self.skill2_description_jp = "ランダムな敵に攻撃力の180%で13回攻撃する。"
        self.skill3_description_jp = "戦闘開始時、全ての味方に「浮舟月影」を付与する。浮舟月影：通常ダメージを受ける際、そのダメージは40%減少し、効果の付与者がそのダメージの90%を代わりに受ける。"
        self.skill1_cooldown_max = 4
        self.skill2_cooldown_max = 3

    def skill1_logic(self):
        allies = self.target_selection(keyword="n_highest_attr", keyword2="3", keyword3="atk", keyword4="ally")
        for ally in allies:
            ally.apply_effect(StatsEffect("Crit Up", 28, True, {"critdmg": 1.2}))
        return 0

    def skill2_logic(self):
        damage_dealt = self.attack(multiplier=1.8, repeat=13)
        return damage_dealt

    def skill3(self):
        pass

    def battle_entry_effects(self):
        allies = [x for x in self.ally if x != self]
        for ally in allies:
            e = ProtectedEffect("Floating Moon", -1, True, False, self, 0.60, 0.9, can_be_removed_by_skill=False)
            ally.apply_effect(e)


class Rika(Character): 
    """
    Protector & Status damage
    Build: hp, def
    """
    def __init__(self, name, lvl, exp=0, equip=None, image=None):
        super().__init__(name, lvl, exp, equip, image)
        self.name = "Rika"
        self.skill1_description = "Attack random enemy triple with 160% atk, 80% chance to inflict Burn for 20 turns. Burn deals 20% atk damage per turn."
        self.skill2_description = "Apply Burn on all enemies for 20 turns. Burn deals 20% atk damage per turn."
        self.skill3_description = "Apply Fire & Flower to all allies at the start of battle." \
        " Fire % Flower: Before taking normal damage, damage taken is reduced by 40% and 50% of the damage is taken by the protector." \
        " Apply unremovable Blossom on yourself, Blossom: The first time when about to take lethal damage, all allies have their hp set to 1 and all damage taken is reduced to 0" \
        " for 20 turns. Blossom applied on allies can be removed by skill."
        # 浄火朱華 咲き誇る花
        self.skill1_description_jp = "ランダムな敵3匹に攻撃力の160%で攻撃し、20ターンの間「燃焼」を付与する確率が80%ある。燃焼は毎ターン攻撃力の20%分のダメージを与える。"
        self.skill2_description_jp = "全ての敵に20ターンの間「燃焼」を付与する。燃焼は毎ターン攻撃力の20%分のダメージを与える。"
        self.skill3_description_jp = "戦闘開始時に全ての味方に「浄火朱華」を付与する。浄火朱華：通常ダメージを受ける前に、受けるダメージが40%減少し、そのダメージの50%を守護者が引き受ける。自身に解除不能な「咲き誇る花」を付与する。咲き誇る花：致命的なダメージを受ける際、全ての味方のHPが1に設定され、20ターンの間全てのダメージが0に軽減される。味方に付与された咲き誇る花はスキルによって解除できる。"
        self.skill1_cooldown_max = 4
        self.skill2_cooldown_max = 4


    def skill1_logic(self):
        def burn_effect(self, target):
            if random.randint(1, 100) <= 80:
                target.apply_effect(ContinuousDamageEffect("Burn", 20, False, self.atk * 0.20, self))
        damage_dealt = self.attack(target_kw1="random_enemy_triple", multiplier=1.6, repeat=1, func_after_dmg=burn_effect)
        return damage_dealt

    def skill2_logic(self):
        for enemy in self.enemy:
            enemy.apply_effect(ContinuousDamageEffect("Burn", 20, False, self.atk * 0.20, self))
        return 0
        
    def skill3(self):
        pass

    def battle_entry_effects(self):
        allies = [x for x in self.ally if x != self]
        for ally in allies:
            e = ProtectedEffect("Fire & Flower", -1, True, False, self, 0.6, 0.5)
            e.can_be_removed_by_skill = False
            ally.apply_effect(e)
        blossom = RikaResolveEffect("Blossom", -1, True, False, damage_immune_duration=20)
        blossom.can_be_removed_by_skill = False
        self.apply_effect(blossom)



class Rubin(Character):
    """
    Protector
    Build: spd, def, hp
    """
    def __init__(self, name, lvl, exp=0, equip=None, image=None):
        super().__init__(name, lvl, exp, equip, image)
        self.name = "Rubin"
        self.skill1_description = "For 30 turns, all allies have their accuracy increased by 100% of your evasion." \
        " Minimum accuracy bonus is 10%."
        self.skill2_description = "Focus attack on closest enemy 3 times with 240% atk."
        self.skill3_description = "At start of battle, apply Unnamed Blessing to all allies." \
        " When the ally is about to take damage, damage taken is reduced by 30%, then 30% of the damage is taken by you." \
        " Cannot protect against status effect and status damage."
        self.skill1_description_jp = "30ターンの間、全ての味方の命中率を自分の回避率の100%増加させる。" \
                                    "最低命中率ボーナスは10%。"
        self.skill2_description_jp = "最も近い敵に240%で3回集中攻撃する。"
        self.skill3_description_jp = "戦闘開始時に全ての味方に名無しの加護を付与する。" \
                                    "味方がダメージを受ける前に、受けるダメージが30%軽減され、その30%のダメージを自身が受ける。" \
                                    "状態異常および状態ダメージからは守れない。"
        self.skill1_cooldown_max = 4
        self.skill2_cooldown_max = 5

    def skill1_logic(self):
        for ally in self.ally:
            is_buff = True
            # if ally.eva < 0:
            #     is_buff = False
            eva_bonus = max(0.1, self.eva * 1.0)
            e = StatsEffect("Accuracy Up", 30, is_buff, {"acc": eva_bonus})
            ally.apply_effect(e)
        return 0

    def skill2_logic(self):
        damage_dealt = self.attack(multiplier=2.4, repeat_seq=3, target_kw1="enemy_in_front")
        return damage_dealt

    def skill3(self):
        pass

    def battle_entry_effects(self):
        allies = [x for x in self.ally if x != self]
        for ally in allies:
            e = ProtectedEffect("Unnamed Blessing", -1, True, False, self, 0.7, 0.3)
            e.can_be_removed_by_skill = False
            ally.apply_effect(e)


class RubinPF(Character):
    """
    Peach Festival Rubin
    Build: 
    """
    def __init__(self, name, lvl, exp=0, equip=None, image=None):
        super().__init__(name, lvl, exp, equip, image)
        self.name = "RubinPF"
        self.skill1_description = "For 20 turns, increase accuracy by 30%, all allies have their evasion increased by 10% of" \
        " your accuracy. Minimum evasion bonus is 1%."
        self.skill2_description = "Focus attack on closest enemy 6 times with 170% atk." \
        " Each attack has a 30% chance to apply Disputed Space for 20 turns, increasing damage taken by 20%."
        self.skill3_description = "At start of battle, apply Peach Flip to all allies." \
        " When the ally is about to take damage, damage taken is reduced by 20%, then 30% of the damage is taken by you." \
        " Cannot protect against status effect and status damage. At start of battle, apply Peach Blossoms to an ally of highest defense." \
        " Peach Blossoms: Revive with 40% hp the next turn after defeated."
        # 論外空間 桃返し 桃華満開
        self.skill1_description_jp = "20ターンの間、命中率が30%増加し、全ての味方の回避率が自分の命中率の10%分増加する。最低回避率のボーナスは1%となる。"
        self.skill2_description_jp = "最も近い敵に攻撃力の170%で6回集中攻撃する。各攻撃には、30%の確率で20ターンの間「論外空間」を付与し、受けるダメージを20%増加させる。"
        self.skill3_description_jp = "戦闘開始時に全ての味方に「桃返し」を付与する。味方がダメージを受ける直前に、そのダメージが20%減少し、残りの30%のダメージを自分が引き受ける。状態異常や状態異常ダメージには適用されない。戦闘開始時、防御力が最も高い味方1人に「桃華満開」を付与する。桃華満開：倒された次のターンにHP40%で復活する。"
        self.skill1_cooldown_max = 4
        self.skill2_cooldown_max = 4

    def skill1_logic(self):
        self.apply_effect(StatsEffect("Accuracy Up", 20, True, {"acc": 0.3}))
        for ally in self.ally:
            is_buff = True
            acc_bonus = max(0.01, self.acc * 0.1)
            e = StatsEffect("Evasion Up", 20, is_buff, {"eva": acc_bonus})
            ally.apply_effect(e)
        return 0

    def skill2_logic(self):
        def vulnerability_effect(self, target):
            if random.randint(1, 100) <= 30:
                target.apply_effect(StatsEffect("Disputed Space", 20, False, {"final_damage_taken_multipler": 0.2}))
        damage_dealt = self.attack(multiplier=2.4, repeat_seq=6, target_kw1="enemy_in_front", 
                                   func_after_dmg=vulnerability_effect)
        return damage_dealt

    def skill3(self):
        pass

    def battle_entry_effects(self):
        allies = [x for x in self.ally if x != self]
        a_highest_def = None
        for ally in allies:
            e = ProtectedEffect("Peach Flip", -1, True, False, self, 0.8, 0.3)
            e.can_be_removed_by_skill = False
            ally.apply_effect(e)
            if not a_highest_def or ally.defense > a_highest_def.defense:
                a_highest_def = ally
        if a_highest_def:
            a_highest_def.apply_effect(RebornEffect("Peach Blossoms", -1, True, 0.4, cc_immunity=False, buff_applier=self))


class Seth(Character):
    """
    Generic attacker, late power spike
    Build: atk, critdmg, penetration
    """
    def __init__(self, name, lvl, exp=0, equip=None, image=None):
        super().__init__(name, lvl, exp, equip, image)
        self.name = "Seth"
        self.skill1_description = "Attack closest enemy 4 times with 270% atk. For each attack, a critical strike will trigger an additional attack. Maximum additional attacks: 4"
        self.skill2_description = "Attack all enemies with 250% atk."
        self.skill3_description = "Apply Sky Gunner on yourself. Sky Gunner: Every turn, increase crit rate and crit dmg by 1%."
        self.skill1_description_jp = "最も近い敵に280%の攻撃を4回行う。各攻撃に対してクリティカルが発生すると追加攻撃が発動する。最大追加攻撃回数: 4"
        self.skill2_description_jp = "全ての敵に250%の攻撃を行う。"
        self.skill3_description_jp = "「スカイガンナー」を付与する。「スカイガンナー」:毎ターン、クリティカル率とクリティカルダメージを1%増加する。"
        self.skill1_cooldown_max = 5
        self.skill2_cooldown_max = 5

    def skill1_logic(self):
        def additional_attack(self, target, is_crit):
            if is_crit:
                global_vars.turn_info_string += f"{self.name} triggered additional attack.\n"
                return self.attack(multiplier=2.7, repeat=1, target_kw1="enemy_in_front")
            else:
                return 0
        damage_dealt = self.attack(multiplier=2.7, repeat=4, additional_attack_after_dmg=additional_attack, target_kw1="enemy_in_front")
        return damage_dealt

    def skill2_logic(self):
        damage_dealt = self.attack(target_kw1="n_random_enemy",target_kw2="5", multiplier=2.5, repeat=1) 
        return damage_dealt
        
    def skill3(self):
        pass

    def battle_entry_effects(self):
        passive = StatsEffect("Sky Gunner", -1, True, {"crit": 0.01, "critdmg": 0.01}, 
                              condition=lambda character:character.is_alive(), use_active_flag=False)
        passive.can_be_removed_by_skill = False
        self.apply_effect(passive)


class Chiffon(Character):
    """
    Support for all allies.
    Build: hp, def, spd, atk
    """
    def __init__(self, name, lvl, exp=0, equip=None, image=None):
        super().__init__(name, lvl, exp, equip, image)
        self.name = "Chiffon"
        self.skill1_description = "Increase def by 20%, atk by 10% for 30 turns for all allies. Apply a shield that absorbs damage up to 150% self atk for 20 turns."
        self.skill2_description = "Select random 5 targets, when target is an ally, heal 200% atk, when target is an enemy, attack with 300% atk and apply Sleep for 20 turns with a 80% chance."
        self.skill3_description = "When taking damage that would exceed 10% of maxhp, reduce damage above 10% of maxhp by 80%. For every turn passed, damage reduction effect is reduced by 2%."
        self.skill1_description_jp = "全ての味方の防御力を20%、攻撃力を10%増加させ、30ターンの間持続する。20ターンの間、味方に自身の攻撃力の150%までのダメージを吸収するシールドを付与する。"
        self.skill2_description_jp = "ランダムに5体の対象を選択し、対象が味方の場合は200%の攻撃力で治療し、対象が敵の場合は300%の攻撃力で攻撃し、80%の確率で20ターン睡眠を付与する。"
        self.skill3_description_jp = "最大HPの10%を超えるダメージを受けた場合、最大HPの10%を超えるダメージを80%軽減する。ターンが経過するごとにダメージ軽減効果が2%ずつ減少する。"
        self.skill1_cooldown_max = 5
        self.skill2_cooldown_max = 5

    def skill1_logic(self):
        for ally in self.ally:
            ally.apply_effect(StatsEffect("Woof! Woof! Woof!", 30, True, {"defense": 1.2, "atk": 1.1}))
            ally.apply_effect(AbsorptionShield("Wuf! Wuf! Wuf!", 20, True, self.atk * 1.5, cc_immunity=False))
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
        self.heal(target_list=ally_list, value=self.atk * 2.0)
        def sleep_effect(self, target):
            dice = random.randint(1, 100)
            if dice <= 80:
                target.apply_effect(SleepEffect('Sleep', duration=20, is_buff=False))
        damage_dealt = self.attack(target_list=enemy_list, multiplier=3.0, repeat=1, func_after_dmg=sleep_effect)
        return damage_dealt
        
    def skill3(self):
        pass

    def battle_entry_effects(self):
        effect_shield = EffectShield2("Endurance", -1, True, False, damage_reduction=0.8)
        effect_shield.can_be_removed_by_skill = False
        self.apply_effect(effect_shield)


class Don(Character):  
    """
    hybrid support, nearby crit buff
    Build: atk, hp, def, spd, atk
    """
    def __init__(self, name, lvl, exp=0, equip=None, image=None):
        super().__init__(name, lvl, exp, equip, image)
        self.name = "Don"
        self.skill1_description = "Target random enemy triple, remove 1 random buff effect and deal 280% atk damage," \
        " Apply absorption shield to ally with lowest hp, absorb damage up to 50% of damage dealt for 20 turns."
        self.skill2_description = "Target random ally triple, heal hp by 305% atk," \
        " Apply absorption shield to ally with lowest hp, absorb damage up to 50% of healing for 20 turns."
        self.skill3_description = "At start of battle, for 20 turns, increase critical rate by 40% for neighbor allies."
        self.skill1_description_jp = "ランダムな敵3体を対象に、ランダムなバフ効果を1つ解除し、280%の攻撃力でダメージを与える。" \
                                    "HPが最も低い味方に吸収シールドを付与し、与えたダメージの50%までを吸収する。この効果は20ターン持続する。"
        self.skill2_description_jp = "ランダムな味方3体を対象に、攻撃力の305%でHPを治療する。" \
                                    "HPが最も低い味方に吸収シールドを付与し、回復量の50%までを吸収する。この効果は20ターン持続する。"
        self.skill3_description_jp = "戦闘開始時に、隣接する味方のクリティカル率を20ターンの間40%増加させる。"
        self.skill1_cooldown_max = 5
        self.skill2_cooldown_max = 5

    def skill1_logic(self):
        targets = list(self.target_selection(keyword="random_enemy_triple"))
        for target in targets:
            target.remove_random_amount_of_buffs(1)
        damage_dealt = self.attack(target_list=targets, multiplier=2.80, repeat=1)
        if self.is_alive() and damage_dealt > 0:
            lowest_hp_ally = min(self.ally, key=lambda x: x.hp)
            lowest_hp_ally.apply_effect(AbsorptionShield("Shield", 20, True, damage_dealt * 0.5, cc_immunity=False))
        return damage_dealt

    def skill2_logic(self):
        targets = list(self.target_selection(keyword="random_ally_triple"))
        healing = self.heal(target_list=targets, value=self.atk * 3.05)
        if healing > 0:
            lowest_hp_ally = min(targets, key=lambda x: x.hp)
            lowest_hp_ally.apply_effect(AbsorptionShield("Shield", 20, True, healing * 0.5, cc_immunity=False))
        return 0

    def skill3(self):
        pass

    def battle_entry_effects(self):
        neighbors = self.get_neighbor_allies_not_including_self()
        for ally in neighbors:
            ally.apply_effect(StatsEffect("Critical Up", 20, True, {"crit": 0.4}))


class Season(Character):
    """
    def neighbor support
    Build: spd, def, hp
    """
    def __init__(self, name, lvl, exp=0, equip=None, image=None):
        super().__init__(name, lvl, exp, equip, image)
        self.name = "Season"
        self.skill1_description = "For 25 turns, increase defense of neighbor allies by 30%, every turn, they regenerate hp equal to 30% of their own defense."
        self.skill2_description = "Attack closest enemy 3 times with 95% atk each. If this skill did less damage than" \
        " 1% of the target's max hp, for 3 times, you and your neighbor allies cannot take damage that exceeds 1% of max hp."
        self.skill3_description = "For each neighbor allies you have (max 2), damage taken is reduced by 30%."
        self.skill1_description_jp = "25ターンの間、隣接する味方の防御力を30%増加させ、毎ターン、味方は自身の防御力の30%に相当するHPを再生する。"
        self.skill2_description_jp = "最も近い敵に95%の攻撃力で3回攻撃する。このスキルが対象の最大HPの1%未満のダメージしか与えなかった場合、" \
                                    "3回の間、自身および隣接する味方は最大HPの1%を超えるダメージを受けることがない。"
        self.skill3_description_jp = "隣接する味方1体につき（最大2体）、受けるダメージが30%軽減される。"
        self.skill1_cooldown_max = 5
        self.skill2_cooldown_max = 2

    def skill1_logic(self):
        neighbors = self.get_neighbor_allies_not_including_self()
        if not neighbors:
            return 0
        for ally in neighbors:
            ally.apply_effect(StatsEffect("Defense Up", 25, True, {"defense": 1.3}))
            ally.apply_effect(ContinuousHealEffect("Regeneration", 25, True, lambda x, y: x.defense * 0.3, self, "30% of defense",
                                                   value_function_description_jp="防御力の30%"))
        return 0

    def skill2_logic(self):
        target_to_attack = mit.one(self.target_selection(keyword="enemy_in_front"))
        hp_percentage = target_to_attack.hp / target_to_attack.maxhp
        dt = self.attack(target_list=[target_to_attack], multiplier=0.95, repeat=3)
        hp_percentage_after = target_to_attack.hp / target_to_attack.maxhp
        if abs(hp_percentage_after - hp_percentage) < 0.01:
            neighbors = self.get_neighbor_allies_including_self()
            for ally in neighbors:
                exist_fairy_protection = ally.get_effect_that_named("Fairy Protection", "Season_FairyProtection")
                if not exist_fairy_protection:
                    fairy_protection = CancellationShield("Fairy Protection", -1, True, 0.01, False, uses=3, cancel_excessive_instead=True)
                    fairy_protection.additional_name = "Season_FairyProtection"
                    ally.apply_effect(fairy_protection)
                else:
                    exist_fairy_protection.uses += 3
        return dt

    def skill3(self):
        pass

    def battle_entry_effects(self):
        def the_damage_function(season, b, damage): # b does not matter
            neighbors = season.get_neighbor_allies_not_including_self()
            damage -= damage * 0.3 * len(neighbors)
            return damage

        passive = ReductionShield("Protected", -1, True, 0, False, damage_function=the_damage_function)
        passive.can_be_removed_by_skill = False
        self.apply_effect(passive)


class Raven(Character):
    """
    Burst attacker
    """
    def __init__(self, name, lvl, exp=0, equip=None, image=None):
        super().__init__(name, lvl, exp, equip, image)
        self.name = "Raven"
        self.skill1_description = "Apply Blackbird on your self for 30 turns. For 15 turns, neighbor allies lose 30% of their atk, add the reduced atk to your atk." \
        " If you already have Blackbird, its duration is refreshed, atk lose and gain is not triggered."
        self.skill2_description = "Attack enemy with lowest def 6 times with 285% atk."
        self.skill3_description = "After using 2 times of skill 2, apply a shield on neighbor allies after the skill, absorb damage up to 80% of total" \
        " damage dealt by skill 2."
        self.skill1_description_jp = "自身に30ターンの間ブラックバードを適用する。15ターンの間、隣接する味方の攻撃力が30%減少し、その減少分を自身の攻撃力に加える。" \
                                    "すでにブラックバード状態中の場合、持続時間が更新され、攻撃力の減少および増加は発動しない。"
        self.skill2_description_jp = "最も防御力の低い敵に285%の攻撃力で6回攻撃する。"
        self.skill3_description_jp = "スキル2を2回使用後、スキル使用後に隣接する味方にシールドを適用し、スキル2によって与えた総ダメージの80%までを吸収する。"
        self.skill1_cooldown_max = 5
        self.skill2_cooldown_max = 5
        self.raven_skill2_counter = 0
        self.raven_skill2_damage_dealt = 0

    def clear_others(self):
        self.raven_skill2_counter = 0
        self.raven_skill2_damage_dealt = 0
        super().clear_others()

    def skill_tooltip(self):
        return f"Skill 1 : {self.skill1_description}\nCooldown : {self.skill1_cooldown} action(s)\n\nSkill 2 : {self.skill2_description}\nCooldown : {self.skill2_cooldown} action(s)\n\nSkill 3 : {self.skill3_description}\n Skill 2 counter : {self.raven_skill2_counter}\n Shield value : {self.raven_skill2_damage_dealt}\n"

    def skill_tooltip_jp(self):
        return f"スキル1:{self.skill1_description_jp}\nクールダウン:{self.skill1_cooldown}行動\n\nスキル2:{self.skill2_description_jp}\nクールダウン:{self.skill2_cooldown}行動\n\nスキル3:{self.skill3_description_jp}\n\nシールド値:{self.raven_skill2_damage_dealt}\n"

    def skill1_logic(self):
        blackbird = self.get_effect_that_named("Blackbird", "Raven_Blackbird")
        if blackbird:
            blackbird.duration = blackbird.original_duration
            global_vars.turn_info_string += f"{self.name} refreshed Blackbird.\n"
        else:
            v = 0
            for a in self.get_neighbor_allies_not_including_self():
                v += a.atk * 0.3
                a.apply_effect(StatsEffect("Atk Down", 15, False, {"atk": 0.7}))
            bb = StatsEffect("Blackbird", 30, True, main_stats_additive_dict={"atk": v})
            bb.additional_name = "Raven_Blackbird"
            self.apply_effect(bb)
        return 0

    def skill2_logic(self):
        damage_dealt = self.attack(target_kw1="n_lowest_attr",target_kw2="1",target_kw3="defense",target_kw4="enemy", multiplier=2.85, repeat=6)
        self.raven_skill2_damage_dealt += damage_dealt
        self.raven_skill2_counter += 1
        if self.raven_skill2_counter == 2:
            if self.raven_skill2_damage_dealt > 0:
                neighbors:list[Character] = self.get_neighbor_allies_not_including_self()
                for ally in neighbors:
                    shield = AbsorptionShield("Shield", -1, True, self.raven_skill2_damage_dealt * 0.8, cc_immunity=False)
                    shield.additional_name = "Raven_Shield"
                    ally.apply_effect(shield)
            self.raven_skill2_counter = 0
        return damage_dealt


    def skill3(self):
        pass


class RavenWB(Character):
    """
    Welcome back Version of Raven
    With increased survivability but lower damage
    """
    def __init__(self, name, lvl, exp=0, equip=None, image=None):
        super().__init__(name, lvl, exp, equip, image)
        self.name = "RavenWB"
        self.skill1_description = "Apply Blackbird on your self for 30 turns. For 15 turns, neighbor allies lose 30% of their atk, add the reduced atk to your atk." \
        " If you already have Blackbird, its duration is refreshed, atk lose and gain is not triggered."
        self.skill2_description = "Attack enemy with lowest crit def 6 times with 240% atk." \
        " If you have Blackbird, each attack has a 50% chance to apply Burn for 20 turns, dealing 20% of atk as damage per turn."
        self.skill3_description = "After using 2 times of skill 2, apply a shield on neighbor allies after the skill, absorb damage up to 50% of total" \
        " damage dealt by skill 2. At start of battle, apply unremovable Raccoon! on yourself, when defeated, revive with 1 hp on the next turn."
        " When revived, apply a shield that absorbs damage up to 30% of total damage dealt by skill 2."
        self.skill1_description_jp = "自身に30ターンの間ブラックバードを適用する。15ターンの間、隣接する味方の攻撃力が30%減少し、その減少分を自身の攻撃力に加える。" \
        "すでにブラックバード状態中の場合、持続時間が更新され、攻撃力の減少および増加は発動しない。"
        self.skill2_description_jp = "最もクリティカル防御力の低い敵に230%の攻撃力で6回攻撃する。" \
        "ブラックバード状態中の場合、各攻撃には50%の確率で20ターンの間燃焼を付与する、毎ターン攻撃力の20%のダメージを与える。"
        self.skill3_description_jp = "スキル2を2回使用後、スキル使用後に隣接する味方にシールドを適用し、スキル2で与えた総ダメージの50%までを吸収する。" \
        "戦闘開始時に、自身に解除不可の「洗熊！」を付与し、撃破された場合、次のターンに1HPで復活する。復活した際、スキル2で与えた総ダメージの30%までのシールドを付与する。"
        self.skill1_cooldown_max = 5
        self.skill2_cooldown_max = 5
        self.raven_skill2_counter = 0
        self.raven_skill2_damage_dealt = 0

    def clear_others(self):
        self.raven_skill2_counter = 0
        self.raven_skill2_damage_dealt = 0
        super().clear_others()

    def skill_tooltip(self):
        return f"Skill 1 : {self.skill1_description}\nCooldown : {self.skill1_cooldown} action(s)\n\nSkill 2 : {self.skill2_description}\nCooldown : {self.skill2_cooldown} action(s)\n\nSkill 3 : {self.skill3_description}\n Skill 2 counter : {self.raven_skill2_counter}\n Shield value : {self.raven_skill2_damage_dealt}\n"

    def skill_tooltip_jp(self):
        return f"スキル1:{self.skill1_description_jp}\nクールダウン:{self.skill1_cooldown}行動\n\nスキル2:{self.skill2_description_jp}\nクールダウン:{self.skill2_cooldown}行動\n\nスキル3:{self.skill3_description_jp}\n\nシールド値:{self.raven_skill2_damage_dealt}\n"

    def skill1_logic(self):
        blackbird = self.get_effect_that_named("Blackbird", "Raven_Blackbird")
        if blackbird:
            blackbird.duration = blackbird.original_duration
            global_vars.turn_info_string += f"{self.name} refreshed Blackbird.\n"
        else:
            v = 0
            for a in self.get_neighbor_allies_not_including_self():
                v += a.atk * 0.3
                a.apply_effect(StatsEffect("Atk Down", 15, False, {"atk": 0.7}))
            bb = StatsEffect("Blackbird", 30, True, main_stats_additive_dict={"atk": v})
            bb.additional_name = "Raven_Blackbird"
            self.apply_effect(bb)
        return 0

    def skill2_logic(self):
        def burn_effect(self: Character, target):
            if self.has_effect_that_named("Blackbird"):
                dice = random.randint(1, 100)
                if dice <= 50:
                    target.apply_effect(ContinuousDamageEffect('Burn', duration=20, is_buff=False, value=self.atk * 0.2, imposter=self))
        damage_dealt = self.attack(target_kw1="n_lowest_attr",target_kw2="1",target_kw3="critdef",target_kw4="enemy", multiplier=2.30, repeat=6, 
                                   func_after_dmg=burn_effect)
        self.raven_skill2_damage_dealt += damage_dealt
        self.raven_skill2_counter += 1
        if self.raven_skill2_counter == 2:
            if self.raven_skill2_damage_dealt > 0:
                neighbors = self.get_neighbor_allies_not_including_self()
                for ally in neighbors:
                    shield = AbsorptionShield("Shield", -1, True, self.raven_skill2_damage_dealt * 0.5, cc_immunity=False)
                    ally.apply_effect(shield)
            self.raven_skill2_counter = 0
        return damage_dealt


    def skill3(self):
        pass

    def battle_entry_effects(self):
        passive = RebornEffect("Raccoon!", -1, True, effect_value=0, cc_immunity=False, buff_applier=self, effect_value_constant=1)
        passive.can_be_removed_by_skill = False
        self.apply_effect(passive)

    def after_revive(self):
        if self.raven_skill2_damage_dealt > 0:
            shield = AbsorptionShield("Shield", -1, True, self.raven_skill2_damage_dealt * 0.3, cc_immunity=False)
            self.apply_effect(shield)


class Ophelia(Character):  
    """
    all rounder
    Build: atk, def, spd
    """
    def __init__(self, name, lvl, exp=0, equip=None, image=None):
        super().__init__(name, lvl, exp, equip, image)
        self.name = "Ophelia"
        self.skill1_description = "Attack 1 enemy with highest atk with 460% atk. Consumes a card in possession to gain an additional effect according to the card type." \
        " Death Card: Skill damage increases by 50%, Stun the target for 10 turns." \
        " Love Card: Reduce heal efficiency for 20 turns by 100%." \
        " Luck Card: Skill cooldown does not apply." \
        " Gains Death Card after this skill."
        self.skill2_description = "All allies regenerates 5% of maxhp for 10 turns. Consumes a card in possession to gain an additional effect according to the card type." \
        " Death Card: Increase critical damage by 30% for 20 turns." \
        " Love Card: Heal all allies for 300% atk." \
        " Luck Card: Skill cooldown does not apply." \
        " Gains Love Card after this skill."
        self.skill3_description = "Normal attack and skills has 30% chance to gain Luck Card."
        self.skill1_description_jp = "最も攻撃力の高い敵に460%の攻撃を行う。所持しているカードを消費し、カードの種類に応じた追加効果を得る。" \
                                    "死のカード:スキルダメージが50%増加し、対象を10ターンの間スタンさせる。" \
                                    "愛のカード:20ターンの間回復効率を100%減少させる。" \
                                    "幸運のカード:スキルのクールダウンが適用されない。" \
                                    "このスキルの後、死のカードを得る。"
        self.skill2_description_jp = "全ての味方が10ターンの間、最大HPの5%を再生する。所持しているカードを消費し、カードの種類に応じた追加効果を得る。" \
                                    "死のカード:20ターンの間クリティカルダメージが30%増加する。" \
                                    "愛のカード:全ての味方を攻撃力の300%で治療する。" \
                                    "幸運のカード:スキルのクールダウンが適用されない。" \
                                    "このスキルの後、愛のカードを得る。"
        self.skill3_description_jp = "通常攻撃およびスキルに30%の確率で幸運のカードを得る。"
        self.skill1_cooldown_max = 5
        self.skill2_cooldown_max = 5

    def skill1(self):
        global_vars.turn_info_string += f"{self.name} cast skill 1.\n"
        if self.skill1_cooldown > 0:
            raise Exception
        buff_to_remove_list = []
        def card_effect(self, target):
            for buff in self.buffs:
                if buff.name == "Death Card":
                    target.apply_effect(StunEffect('Stun', duration=10, is_buff=False))
                    buff_to_remove_list.append(buff)
                if buff.name == "Love Card":
                    target.apply_effect(StatsEffect("Unhealable", 20, False, {"heal_efficiency": -1.0}))
                    buff_to_remove_list.append(buff)

        def card_amplify(self, target, final_damage):
            death_card_count = max(sum(1 for buff in self.buffs if buff.name == "Death Card"), 1)
            final_damage *= 1.5 * death_card_count
            return final_damage
        
        damage_dealt = self.attack(multiplier=4.6, repeat=1, func_after_dmg=card_effect, func_damage_step=card_amplify, target_kw1="n_highest_attr", target_kw2="1", target_kw3="atk", target_kw4="enemy")
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
            ally.apply_effect(ContinuousHealEffect("Regeneration", 10, True, lambda x, y: x.maxhp * 0.05, self, "5% of max hp",
                                                   value_function_description_jp="最大HPの5%"))
            for buff in self.buffs:
                if buff.name == "Death Card":
                    ally.apply_effect(StatsEffect("Crit Dmg Up", 20, True, {"critdmg": 0.3}))
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


class Requina(Character):   
    """
    status damage attacker
    build: atk, spd, crit, critdmg, penetration, acc
    """
    def __init__(self, name, lvl, exp=0, equip=None, image=None):
        super().__init__(name, lvl, exp, equip, image)
        self.name = "Requina"
        self.skill1_description = "Attack 3 closest enemies with 170% atk, 50% chance to apply 6 stacks of Great Poison. 50% chance to apply 4 stacks." \
        " Each stack of Great Poison reduces atk, defense, heal efficiency by 1%, Each turn, deals 0.3% maxhp status damage. " \
        " Maximum stacks: 70." \
        " Effect last 20 turns. Same effect applied refreshes the duration."
        self.skill2_description = "Attack 2 closest enemies with 210% atk, if target has Great Poison, apply 6 stacks of Great Poison."
        self.skill3_description = "Normal attack has 95% chance to apply 1 stack of Great Poison."
        self.skill1_description_jp = "最も近い3体の敵に170%の攻撃を行い、50%の確率で猛毒を6スタック付与し、50%の確率で4スタック付与する。" \
                                    "猛毒の各スタックは、攻撃力、防御力、回復効率を1%減少させ、毎ターン最大HPの0.3%の状態異常ダメージを与える。" \
                                    "最大スタック数:70。" \
                                    "効果は20ターン持続し、同じ効果が適用された場合、持続時間が更新される。"
        self.skill2_description_jp = "最も近い2体の敵に210%の攻撃を行い、対象が猛毒の影響を受けている場合、猛毒を6スタック付与する。"
        self.skill3_description_jp = "通常攻撃に95%の確率で猛毒を1スタック付与する。"
        self.skill1_cooldown_max = 3
        self.skill2_cooldown_max = 5

    def skill1_logic(self):
        def effect(self, target):
            dice = random.randint(1, 100)
            if dice <= 50:
                target.apply_effect(RequinaGreatPoisonEffect("Great Poison", 20, False, 0.003, {"atk": 1.00, "defense": 1.00, "heal_efficiency": 0.00}, self, 6))
            else:
                target.apply_effect(RequinaGreatPoisonEffect("Great Poison", 20, False, 0.003, {"atk": 1.00, "defense": 1.00, "heal_efficiency": 0.00}, self, 4))
        damage_dealt = self.attack(target_kw1="n_enemy_in_front",target_kw2="3", multiplier=1.7, repeat=1, func_after_dmg=effect)
        return damage_dealt

    def skill2_logic(self):
        def damage_step_effect(self, target, final_damage):
            if target.has_effect_that_named("Great Poison"):
                target.apply_effect(RequinaGreatPoisonEffect("Great Poison", 20, False, 0.003, {"atk": 1.00, "defense": 1.00, "heal_efficiency": 0.00}, self, 6))
            return final_damage
        damage_dealt = self.attack(target_kw1="n_enemy_in_front",target_kw2="2", multiplier=2.1, repeat=1, func_damage_step=damage_step_effect)
        return damage_dealt
        
    def skill3(self):
        pass

    def normal_attack(self):
        def effect(self, target):
            dice = random.randint(1, 100)
            if dice <= 95:
                target.apply_effect(RequinaGreatPoisonEffect("Great Poison", 20, False, 0.005, {"atk": 1.00, "defense": 1.00, "heal_efficiency": 0.00}, self, 1))
        self.attack(func_after_dmg=effect)


class Dophine(Character):
    """
    pure attacker
    Build: atk, crit, critdmg, penetration
    """
    def __init__(self, name, lvl, exp=0, equip=None, image=None):
        super().__init__(name, lvl, exp, equip, image)
        self.name = "Dophine"
        self.skill1_description = "Attack closest enemy with 300% atk 3 times. All attacks become critical strikes after one critical strike."
        self.skill2_description = "Attack closest enemy with 280% atk 4 times. After one critical strike, the following attacks deals 50% more damage."
        self.skill3_description = "Before skill attack, if hp is below 50%, increase critical rate by 30% for 1 turn."
        self.skill1_description_jp = "最も近い敵に300%の攻撃を3回行う。1回クリティカルが発生すると、以降の攻撃は全てクリティカルになる。"
        self.skill2_description_jp = "最も近い敵に280%の攻撃を4回行う。1回クリティカルが発生すると、以降の攻撃はダメージが50%増加する。"
        self.skill3_description_jp = "スキル攻撃前にHPが50%以下の場合、1ターンの間クリティカル率が30%増加する。"
        self.skill1_cooldown_max = 4
        self.skill2_cooldown_max = 4

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


class Gabe(Character):
    """
    Special character
    skill is a reference to yu-gi-oh card
    Build: atk, hp, def
    """
    def __init__(self, name, lvl, exp=0, equip=None, image=None):
        super().__init__(name, lvl, exp, equip, image)
        self.name = "Gabe"
        self.skill1_description = "Attack 3 closeset enemies with 300% atk. Damage increases by 150% if target has New Year Fireworks effect."
        self.skill2_description = "Apply New Year Fireworks to self for 4 times and heal hp by 400% atk." \
        " New Year Fireworks: Have 6 counters. Every turn, throw a dice, counter decreases by the dice number." \
        " When counter reaches 0, deal 600% of applier atk as status damage to self." \
        " At the end of the turn, this effect is applied to a random enemy." 
        self.skill3_description = "Reduces chances of rolling 1 and 6 on dice by 80%."
        self.skill1_description_jp = "最も近い3体の敵に300%の攻撃を行う。対象が新年花火の効果を受けている場合、ダメージが150%増加する。"
        self.skill2_description_jp = "自身に4回分の新年花火を適用し、攻撃力の400%で自分を治療する。" \
                                    "新年花火:カウンターが6ある。毎ターン、サイコロを振り、カウンターは出た目の数だけ減少する。" \
                                    "カウンターが0になると、自身に付与者の攻撃力の600%の状態異常ダメージを与える。" \
                                    "ターン終了時、この効果がランダムな敵に適用される。"
        self.skill3_description_jp = "サイコロで1と6が出る確率を80%減少する。"
        self.skill1_cooldown_max = 5
        self.skill2_cooldown_max = 3


    def skill1_logic(self):
        def damage_amplify(self, target, final_damage):
            if target.has_effect_that_named("New Year Fireworks"):
                final_damage *= 2.5
            return final_damage
        damage_dealt = self.attack(target_kw1="n_enemy_in_front",target_kw2="3", multiplier=3.0, repeat=1, func_damage_step=damage_amplify)
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
            weights = [20, 100, 100, 100, 100, 20]
        return super().fake_dice(sides, weights)


class Inaba(Character):
    """
    Special character
    Build:
    """
    def __init__(self, name, lvl, exp=0, equip=None, image=None):
        super().__init__(name, lvl, exp, equip, image)
        self.name = "Inaba"
        self.skill1_description = "Heal random allies 3 times by 480% atk, then attack random enemies 5 times with 240% atk."
        self.skill2_description = "Prepare 9 Shintou (Oryza sativa). Apply Shintou to yourself 9 times, Shintou has 9 counters," \
        " each turn, throw a dice, counter decreases by the dice number." \
        " When counter reaches 0, heal by 300% of applier atk and apply Blessing for 20 turns." \
        " At the end of the turn, this effect is applied to a random enemy." \
        " Blessing: Heal efficiency increased by 40%."
        self.skill3_description = "When a Blessing effect by Shintou is about to be applied on yourself while you have 4 or more Blessing effects," \
        " Revive all allies with 100% hp, all enemies takes status damage equal to 500% of your atk, the allies alive are healed by 300% atk."
        # 神稲
        self.skill1_description_jp = "ランダムな味方を攻撃力の480%で3回治療し、その後ランダムな敵を攻撃力の240%で5回攻撃する。"
        self.skill2_description_jp = "9回分の「神稲（イネ）」を準備する。自身に9回分の神稲を適用し、神稲には9つのカウンターがある。各ターン、サイコロを振り、カウンターはその目の数だけ減少する。カウンターが0になると、適用者の攻撃力の300%分を回復し、20ターンの間「祝福」を付与する。ターン終了時、この効果はランダムな敵にも適用される。祝福：回復効果が40%増加する。"
        self.skill3_description_jp = "神稲による祝福効果が自身に適用されようとする際、既に4つ以上の祝福効果を持っている場合、全ての味方をHP100%で復活させ、全ての敵に攻撃力の500%分の状態異常ダメージを与える。生存している味方は攻撃力の300%で回復する。"
        self.skill1_cooldown_max = 5
        self.skill2_cooldown_max = 3
        
    def skill1_logic(self):
        for i in range(3):
            self.heal(value=self.atk * 4.8)
            self.update_ally_and_enemy()
            if not self.enemy:
                break
        damage_dealt = self.attack(multiplier=2.4, repeat=5)
        return damage_dealt

    def skill2_logic(self):
        for i in range(9):
            self.apply_effect(ShintouEffect("Shintou", -1, True, 9, self))
        for shintou in self.buffs:
            if shintou.name == "Shintou":
                shintou.apply_effect_on_trigger(self)
        return 0
        
    def skill3(self):
        pass


class Yuri(Character):     
    """
    Late game attacker, normal attack
    Build: atk, crit, critdmg, penetration
    """
    def __init__(self, name, lvl, exp=0, equip=None, image=None):
        super().__init__(name, lvl, exp, equip, image)
        self.name = "Yuri"
        self.skill1_description = "Summon Bear, Wolf, Eagle, Cat in order. Normal attack gain additional effects according to the summon." \
        " Bear: 20% chance to Stun for 10 turns, normal attack damage increases by 100%." \
        " Wolf: Normal attack attack 3 closest enemies, each attack has 40% chance to inflict burn for 20 turns. Burn deals 50% atk status damage per turn." \
        " Eagle: Each Normal attack gains 4 additional focus attacks on the same target, each attack deals 150% atk damage." \
        " Cat: After normal attack, an ally with highest atk gains 'Gold Card' effect for 8 turns. Gold Card: atk, def, critical damage is increased by 30%." \
        " After 4 summons above, this skill cannot be used."
        self.skill2_description = "This skill cannot be used. For each summon, recover 15% hp and gain buff effect for 20 turns." \
        " Bear: atk increased by 40%." \
        " Wolf: critical rate increased by 40%." \
        " Eagle: speed increased by 40%." \
        " Cat: heal efficiency increased by 40%."
        self.skill3_description = "Normal attack targets closest enemy."
        self.skill1_description_jp = "クマ、オオカミ、ワシ、ネコを順に召喚する。通常攻撃は召喚に応じた追加効果を得る。" \
                                    "クマ:20%の確率で10ターンの間スタンさせ、通常攻撃のダメージが100%増加する。" \
                                    "オオカミ:通常攻撃が最も近い3体の敵を対象とし、各攻撃には40%で5ターンの間燃焼を付与する。燃焼は毎ターン攻撃力の50%の状態異常ダメージを与える。" \
                                    "ワシ:各通常攻撃が同じ対象に追加の4回の集中攻撃を行い、各攻撃は攻撃力の150%のダメージを与える。" \
                                    "ネコ:通常攻撃後、最も攻撃力の高い味方に8ターンの間「ゴールドカード」効果を付与する。ゴールドカード:攻撃力、防御力、クリティカルダメージが30%増加する。" \
                                    "上記の4召喚が完了した後、このスキルは使用できなくなる。"
        self.skill2_description_jp = "このスキルは使用できない。各召喚ごとにHPが15%回復し、20ターンの間バフ効果を得る。" \
                                    "クマ:攻撃力が40%増加する。" \
                                    "オオカミ:クリティカル率が40%増加する。" \
                                    "ワシ:スピードが40%増加する。" \
                                    "ネコ:回復効率が40%増加する。"
        self.skill3_description_jp = "通常攻撃は最も近い敵を対象とする。"
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

    def skill1_logic(self):
        match (self.bt_bear, self.bt_wolf, self.bt_eagle, self.bt_cat) :
            case (False, False, False, False):
                bear_effect = Effect("Bear", -1, True, False,
                                     tooltip_str="Attack damage increases by 100, 20% chance to Stun for 10 turns.",
                                     tooltip_str_jp="攻撃ダメージが100%増加し、20%の確率で10ターンの間スタンさせる。")
                bear_effect.can_be_removed_by_skill = False
                self.apply_effect(bear_effect)
                global_vars.turn_info_string += f"{self.name} summoned Bear.\n"
                self.bt_bear = True
                self.apply_effect(StatsEffect("Bear", 20, True, {"atk": 1.40}))
                self.heal_hp(self.maxhp * 0.15, self)
                return 0
            case (True, False, False, False):
                wolf_effect = Effect("Wolf", -1, True, False,
                                    tooltip_str="Attack 3 closest enemies, each attack has 40% chance to inflict burn for 20 turns.",
                                    tooltip_str_jp="攻撃が最も近い3体の敵を対象とし、各攻撃には確率40%で5ターンの間燃焼を付与する。")
                wolf_effect.can_be_removed_by_skill = False
                self.apply_effect(wolf_effect)
                global_vars.turn_info_string += f"{self.name} summoned Wolf.\n"
                self.bt_wolf = True
                self.apply_effect(StatsEffect("Wolf", 20, True, {"crit": 0.40}))
                self.heal_hp(self.maxhp * 0.15, self)
                return 0
            case (True, True, False, False):
                eagle_effect = Effect("Eagle", -1, True, False,
                                    tooltip_str="Each Normal attack gains 4 additional focus attacks on the same target, each attack deals 150% atk damage.",
                                    tooltip_str_jp="各通常攻撃が同じ対象に追加の4回の集中攻撃を行い、各攻撃は攻撃力の150%のダメージを与える。")
                eagle_effect.can_be_removed_by_skill = False
                self.apply_effect(eagle_effect)
                global_vars.turn_info_string += f"{self.name} summoned Eagle.\n"
                self.bt_eagle = True
                self.apply_effect(StatsEffect("Eagle", 20, True, {"spd": 1.40}))
                self.heal_hp(self.maxhp * 0.15, self)
                return 0
            case (True, True, True, False):
                cat_effect = Effect("Cat", -1, True, False,
                                    tooltip_str="After normal attack, an ally with highest atk gains 'Gold Card'.",
                                    tooltip_str_jp="通常攻撃後、最も攻撃力の高い味方に「ゴールドカード」効果を付与する。")
                cat_effect.can_be_removed_by_skill = False
                self.apply_effect(cat_effect)
                global_vars.turn_info_string += f"{self.name} summoned Cat.\n"
                self.bt_cat = True
                self.apply_effect(StatsEffect("Cat", 20, True, {"heal_efficiency": 0.40}))
                self.heal_hp(self.maxhp * 0.15, self)
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
                        target.apply_effect(StunEffect('Stun', duration=10, is_buff=False))
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
                        target.apply_effect(StunEffect('Stun', duration=10, is_buff=False))
                    dice = random.randint(1, 100)
                    if dice <= 40:
                        target.apply_effect(ContinuousDamageEffect("Burn", 20, False, self.atk * 0.5, self))
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
                        target.apply_effect(StunEffect('Stun', duration=10, is_buff=False))
                    dice = random.randint(1, 100)
                    if dice <= 40:
                        target.apply_effect(ContinuousDamageEffect("Burn", 20, False, self.atk * 0.5, self))
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
                        target.apply_effect(StunEffect('Stun', duration=10, is_buff=False))
                    dice = random.randint(1, 100)
                    if dice <= 40:
                        target.apply_effect(ContinuousDamageEffect("Burn", 20, False, self.atk * 0.5, self))
                def damage_amplify(self, target, final_damage):
                    final_damage *= 2.0
                    return final_damage
                def additional_attacks(self, target, is_crit):
                    global_vars.turn_info_string += f"{self.name} triggered additional attack.\n"
                    return self.attack(multiplier=1.5, repeat_seq=4, target_list=[target])
                damage_dealt = self.attack(target_kw1="n_enemy_in_front", multiplier=2.0, repeat=1, func_after_dmg=extra_effect, 
                                           func_damage_step=damage_amplify, target_kw2="3", additional_attack_after_dmg=additional_attacks)
                if self.is_alive():
                    gold_card = StatsEffect("Gold Card", 8, True, {"atk": 1.3, "defense": 1.3, "critdmg": 0.3})
                    gold_card.additional_name = "bt_gold_card"
                    # gold_card.apply_rule = "stack"
                    ally_to_gold_card = mit.one(self.target_selection(keyword="n_highest_attr", keyword2="1", keyword3="atk", keyword4="ally"))
                    ally_to_gold_card.apply_effect(gold_card)
                    global_vars.turn_info_string += f"{ally_to_gold_card.name} gained Gold Card.\n"

                return damage_dealt
            
            case (_, _, _, _):
                raise Exception("Invalid state")
            

class April(Character):
    """
    special attacker
    Build: generic attack build
    """
    def __init__(self, name, lvl, exp=0, equip=None, image=None):
        super().__init__(name, lvl, exp, equip, image)
        self.name = "April"
        self.skill1_description = "Attack closest enemy with 275% atk 3 times. For each attack, if target has a beneficial effect, create a" \
        " copy of that effect and apply it on self. Effect created this way always have a duration of 36 turns." \
        " Each effect can only be copied once. Equippment set effect cannot be copied. Special effects can also be copied."
        self.skill2_description = "Attack 3 enemy with 330% atk. If you have beneficial effect, for each effect you have," \
        " attack enemy of highest hp with 200% atk."
        self.skill3_description = "Before taking normal damage, for each beneficial effect you have, reduce damage taken by 7%." \
        " Maximum reduction is 70%."
        self.skill1_description_jp = "最も近い敵に300%の攻撃を3回行う。各攻撃ごとに、対象が有益な効果を持っている場合、その効果をコピーして自身に適用する。" \
                                    "この方法で作成された効果の持続時間は常に36ターンとなる。各効果は一度しかコピーできない。装備セット効果はコピーできない、特殊効果もコピーできる。"
        self.skill2_description_jp = "3体の敵に330%の攻撃を行う。自身が有益な効果を持っている場合、効果ごとに、最もHPが高い敵に200%の攻撃を行う。"
        self.skill3_description_jp = "通常ダメージを受ける前に、有益な効果ごとに被ダメージが7%軽減される。最大軽減率は70%。"
        self.skill1_cooldown_max = 4
        self.skill2_cooldown_max = 5

    def skill1_logic(self):
        def copy_effect(self, target: Character):
            for e in target.buffs:
                if not e.is_set_effect and not hasattr(e, "ch_april_mark_as_copied") and not e.is_protected_effect:
                    e.ch_april_mark_as_copied = False
                if not e.is_set_effect and hasattr(e, "ch_april_mark_as_copied") and not e.ch_april_mark_as_copied:
                    e2 = copy.copy(e)
                    e2.duration = 36
                    e.ch_april_mark_as_copied = True
                    global_vars.turn_info_string += f"{self.name} copied {e.name} from {target.name}.\n"
                    self.apply_effect(e2)
                    break
        damage_dealt = self.attack(target_kw1="enemy_in_front", multiplier=2.75, repeat=3, func_after_dmg=copy_effect)
        return damage_dealt

    def skill2_logic(self):
        def additional_attack(self, target, is_crit):
            admg = 0
            for e in self.buffs:
                if e.is_buff and not e.is_set_effect:
                    admg += self.attack(target_kw1="n_highest_attr", target_kw2="1", target_kw3="hp", target_kw4="enemy", multiplier=2.0)
            return admg
            
        damage_dealt = self.attack(target_kw1="n_random_enemy", target_kw2="3",
                                   multiplier=3.3, repeat=1, additional_attack_after_dmg=additional_attack)
        return damage_dealt

    def skill3(self):
        pass

    def take_damage_before_calculation(self, damage, attacker):
        reduction = 0.07 * sum(1 for e in self.buffs if e.is_buff and not e.is_set_effect)
        reduction = min(reduction, 0.7)
        global_vars.turn_info_string += f"{self.name} reduced {reduction * 100}% of damage taken.\n"
        return damage * (1 - reduction)
    

class Nata(Character):
    """
    tank
    Build: heal_efficiency, hp 
    """
    def __init__(self, name, lvl, exp=0, equip=None, image=None):
        super().__init__(name, lvl, exp, equip, image)
        self.name = "Nata"
        self.skill1_description = "Attack random enemies 4 times with 180% atk. All duration of beneficial effects on yourself is increased by 10 turns," \
        " if you have Renka effect, its stack is increased by 1 if less than 4."
        self.skill2_description = "Focus attack 1 enemy of highest crit rate with 190% atk 3 times." \
        " if the enemy falls by this attack, recover 20% hp."
        self.skill3_description = "The first time you are defeated, recover 12% hp and apply Renka status effect on yourself," \
        " Renka has 15 stacks, each time when taking lethal damage, consume 1 stack, cancel the damage and recover 12% hp." \
        " When taking damage, reduce damage taken by 4% + 4% for each stack."
        self.skill1_description_jp = "ランダムな敵に180%の攻撃を4回行う。自身に有益な効果の持続時間が4ターン延長され、" \
                                    "「蓮花」効果を持っている場合、スタックが4未満であれば1増加する。"
        self.skill2_description_jp = "最もクリティカル率の高い敵に190%の攻撃を3回集中して行う。" \
                                    "この攻撃で敵が倒れた場合、HPを20%回復する。"
        self.skill3_description_jp = "初めて敗北した際、HPを12%回復し、自身に「蓮花」状態効果を付与する。" \
                                    "蓮花は15スタックを持ち、致死ダメージを受けるたびに1スタックを消費し、ダメージを無効化してHPを12%回復する。" \
                                    "ダメージを受ける際、被ダメージが4%+スタックごとに4%軽減される。"
        self.skill1_cooldown_max = 4
        self.skill2_cooldown_max = 4
        self.skill3_used = False

    def clear_others(self):
        self.skill3_used = False
        super().clear_others()

    def skill1_logic(self):
        def after_the_attack():
            for e in self.buffs:
                if e.duration > 0:
                    e.duration += 10
            renka = self.get_effect_that_named("Renka", "Nata_Renka", "RenkaEffect")
            if renka:
                if renka.stacks < 4:
                    renka.stacks += 1
                    # print(f"{self.name} gained 1 stack of Renka.")
        damage_dealt = self.attack(multiplier=1.8, repeat=4)
        if self.is_alive():
            after_the_attack()
        return damage_dealt


    def skill2_logic(self):
        def recovery(self, target):
            if target.is_dead():
                self.heal_hp(self.maxhp * 0.2, self)
        damage_dealt = self.attack(target_kw1="n_highest_attr", target_kw2="1", target_kw3="crit", target_kw4="enemy", multiplier=1.9, repeat_seq=3, func_after_dmg=recovery)
        return damage_dealt


    def skill3(self):
        pass

    def defeated_by_taken_damage(self, damage, attacker):
        if not self.skill3_used:
            self.heal_hp(self.maxhp * 0.12, self, ignore_death=True)
            # print(self.hp)
            # print(self.is_alive())
            if self.is_alive():
                renka = RenkaEffect("Renka", -1, True, False, damage_reduction=0.04)
                renka.can_be_removed_by_skill = False
                renka.additional_name = "Nata_Renka"
                self.apply_effect(renka)
                self.skill3_used = True
            return 
        return
    

class Taiyi(Character):
    """
    A better Renka effect, Nata paired with this character can become a damage dealer
    Build: 
    """
    def __init__(self, name, lvl, exp=0, equip=None, image=None):
        super().__init__(name, lvl, exp, equip, image)
        self.name = "Taiyi"
        self.skill1_description = "Attack random enemies 6 times with 150% atk, each attack has a 3% chance to Stun the target for 10 turns."
        self.skill2_description = "Attack random enemy pair 3 times with 150% atk."
        self.skill3_description = "The first time you are defeated, recover 12% hp and apply Renka and Seren on yourself," \
        " Renka has 15 stacks, each time when taking lethal damage, consume 1 stack, cancel the damage and recover 12% hp." \
        " When taking damage, reduce damage taken by 2% + 4% for each stack." \
        " Seren: Critical damage and accuracy is increased by 40%." \
        " At end of turn, apply Seren to all allies who have Renka effect but does not have Seren effect."
        # 蓮花 青蓮
        self.skill1_description_jp = "ランダムな敵に攻撃力の150%で6回攻撃し、各攻撃に3%の確率で10ターンの間スタンさせる。"
        self.skill2_description_jp = "ランダムな敵ペアに攻撃力の150%で3回攻撃する。"
        self.skill3_description_jp = "初めて敗北した際、HPを12%回復し、自身に「蓮花」と「青蓮」を付与する。蓮花には15スタックがあり、致命的なダメージを受けるたびに1スタックを消費してそのダメージを無効化し、HPを12%回復する。ダメージを受けた際、受けるダメージが2%＋スタックごとに4%減少する。青蓮：クリティカルダメージと命中率が40%増加する。ターン終了時、蓮花効果を持つが青蓮効果を持たない味方全員に青蓮を付与する。"
        self.skill1_cooldown_max = 4
        self.skill2_cooldown_max = 4
        self.skill3_used = False

    def clear_others(self):
        self.skill3_used = False
        super().clear_others()

    def skill1_logic(self):
        def stun_effect(self, target):
            dice = random.randint(1, 100)
            if dice <= 3:
                target.apply_effect(StunEffect('Stun', duration=10, is_buff=False))
        damage_dealt = self.attack(multiplier=1.5, repeat=6, func_after_dmg=stun_effect)
        return damage_dealt

    def skill2_logic(self):
        damage_dealt = self.attack(multiplier=1.5, repeat=3, target_kw1="random_enemy_pair")
        return damage_dealt

    def skill3(self):
        pass

    def character_specific_at_end_of_turn(self):
        seren = self.get_effect_that_named("Seren", "Taiyi_Seren", "StatsEffect")
        if seren:
            # ("ally_that_must_have_effect_full", effect_name, additional_name, class_name)
            allies = list(self.target_selection(keyword="ally_that_must_have_effect_full", keyword2="Renka", keyword3="None", keyword4="RenkaEffect"))
            if allies:
                for ally in allies:
                    if not ally.has_effect_that_named("Seren", "Taiyi_Seren"):
                        seren2 = StatsEffect("Seren", -1, True, {"critdmg": 0.4, "acc": 0.4})
                        seren.apply_rule = "stack"
                        seren2.additional_name = "Taiyi_Seren"
                        ally.apply_effect(seren2)
                        # print(f"{ally.name} gained Seren.")
        return


    def defeated_by_taken_damage(self, damage, attacker):
        if not self.skill3_used:
            self.heal_hp(self.maxhp * 0.12, self, ignore_death=True)
            # print(self.hp)
            # print(self.is_alive())
            if self.is_alive():
                renka = RenkaEffect("Renka", -1, True, False, damage_reduction=0.02)
                renka.can_be_removed_by_skill = False
                renka.additional_name = "Taiyi_Renka"
                self.apply_effect(renka)
                seren = StatsEffect("Seren", -1, True, {"critdmg": 0.4, "acc": 0.4})
                seren.apply_rule = "stack"
                seren.additional_name = "Taiyi_Seren"
                self.apply_effect(seren)
                self.skill3_used = True
            return 
        return
    

class Chei(Character):
    """
    damage reflect attacker
    Build: spd
    """
    def __init__(self, name, lvl, exp=0, equip=None, image=None):
        super().__init__(name, lvl, exp, equip, image)
        self.name = "Chei"
        self.skill1_description = "Attack 4 enemies with 300% atk. Apply Assist on yourself for 30 turns." \
        " Assist: reflect 100% of received normal damage that exceeds 15% of maxhp to the attacker as status damage," \
        " Damage taken cannot exceed 15% of maxhp. On applying the same effect, duration is refreshed." \
        " Maximum reflect damage is 100% of your maxhp."
        self.skill2_description = "Attack 3 enemies with 300% atk. 60% chance to inflict Burn for 20 turns." \
        " Burn: deals 50% atk status damage per turn. If Assist is still active, increase its duration by 3 turns."
        self.skill3_description = "At start of battle, apply Assist on yourself for 12 turns."
        self.skill1_description_jp = "4体の敵に300%の攻撃を行い、30ターンの間、自身に援護を付与する。" \
                                    "援護:最大HPの15%を超える通常ダメージを受けた場合、超えた部分の100%を状態異常ダメージとして攻撃者に反射する。" \
                                    "被ダメージは最大HPの15%を超えない。同じ効果が適用された場合、持続時間が更新される。" \
                                    "最大反射ダメージは自身の最大HPの100%。"
        self.skill2_description_jp = "3体の敵に300%の攻撃を行い、60%の確率で20ターンの間燃焼を付与する。" \
                                    "燃焼:毎ターン攻撃力の50%の状態異常ダメージを与える。援護がまだアクティブな場合、その持続時間が3ターン延長される。"
        self.skill3_description_jp = "戦闘開始時に、12ターンの間、自身に援護を付与する。"
        self.skill1_cooldown_max = 5
        self.skill2_cooldown_max = 5
        self.skill3_used = False

    def clear_others(self):
        self.skill3_used = False
        super().clear_others()

    def skill1_logic(self):
        def after_the_attack():
            assist = self.get_effect_that_named("Assist", "Chei_Assist")
            if assist:
                assist.duration = 30
            else:
                assist = EffectShield2("Assist", 30, True, False, damage_reduction=1.0, shrink_rate=0.0, hp_threshold=0.15,
                                       damage_reflect_function=lambda x: x * 1.0, 
                                       damage_reflect_description="reflect 100% of received damage that exceeds 15% of maxhp to the attacker.",
                                       damage_reflect_description_jp="最大HPの15%を超えるダメージを受けた場合、超えた部分の100%を状態異常ダメージとして攻撃者に反射する。")
                assist.additional_name = "Chei_Assist"
                self.apply_effect(assist)
        damage_dealt = self.attack(multiplier=3.0, repeat=1, target_kw1="n_random_enemy", target_kw2="4")
        if self.is_alive():
            after_the_attack()
        return damage_dealt

    def skill2_logic(self):
        def burn_effect(self, target):
            dice = random.randint(1, 100)
            if dice <= 60:
                target.apply_effect(ContinuousDamageEffect("Burn", 20, False, self.atk * 0.5, self))
        damage_dealt = self.attack(multiplier=3.0, repeat=1, target_kw1="n_random_enemy", target_kw2="3", func_after_dmg=burn_effect)
        if self.is_alive():
            assist = self.get_effect_that_named("Assist", "Chei_Assist")
            if assist:
                assist.duration += 3
        return damage_dealt

    def skill3(self):
        pass

    def battle_entry_effects(self):
        e = EffectShield2("Assist", 12, True, False, damage_reduction=1.0, shrink_rate=0.0, hp_threshold=0.15,
                                       damage_reflect_function=lambda x: x * 1.0, 
                                       damage_reflect_description="reflect 100% of received damage that exceeds 15% of maxhp to the attacker.",
                                       damage_reflect_description_jp="最大HPの15%を超えるダメージを受けた場合、超えた部分の100%を状態異常ダメージとして攻撃者に反射する。")
        e.additional_name = "Chei_Assist"
        self.apply_effect(e)


class CheiHW(Character):
    """
    damage reflect attacker, good against enemies with negative effects
    Halloween version
    Build: spd
    """
    def __init__(self, name, lvl, exp=0, equip=None, image=None):
        super().__init__(name, lvl, exp, equip, image)
        self.name = "CheiHW"
        self.skill1_description = "Attack enemy of lowest hp percentage with 220% atk 3 times, damage doubles if the enemy has a active negative effect." \
        " After the attack, apply Reflect on yourself for 20 turns." \
        " Reflect: reflect 30% of received normal damage."
        self.skill2_description = "Attack enemy of lowest hp percentage with 400% atk, if the enemy has a active negative effect, Stun for 10 turns."
        self.skill3_description = "Apply unremovable Surprise Trap on yourself, when defeated, revive with 70% hp. When revived, apply Assist on yourself for 20 turns." \
        " Apply absorption shield Mr. Naughty Ghost on yourself, shield absorbs 70% of maxhp damage, lasts for 20 turns." \
        " Assist: reflect 120% of received normal damage that exceeds 15% of maxhp to the attacker as status damage, damage taken cannot exceed 15% of maxhp." \
        " Maximum reflect damage is 200% of your maxhp."
        self.skill1_description_jp = "HP割合が最も低い敵に攻撃力の220%で3回攻撃する。敵にアクティブなデバフがある場合、ダメージが2倍になる。攻撃後、自身に20ターンの間「キャンディ警告」を付与する。キャンディ警告:受けた通常ダメージの30%を反射する。"
        self.skill2_description_jp = "HP割合が最も低い敵に攻撃力の400%で攻撃する。敵にアクティブなデバフがある場合、10ターンの間スタンさせる。"
        self.skill3_description_jp = "自身に解除不能な「びっくりトラップ」を付与する。撃破された時、HPを70%で復活する。復活した際、20ターンの間「援護」を自身に付与する。自身に「いたずら幽霊さん」の吸収シールドを付与し、このシールドは最大HPの70%分のダメージを吸収し、20ターン持続する。援護:受けた通常ダメージが最大HPの15%を超える場合、そのダメージの120%を状態異常ダメージとして攻撃者に反射する。受けるダメージは最大HPの15%を超えない。最大反射ダメージは自身の最大HPの120%。"
        self.skill1_cooldown_max = 5
        self.skill2_cooldown_max = 5


    def skill1_logic(self):
        def damage_amplify(self, target: Character, final_damage):
            es = target.get_active_removable_effects(get_buffs=False, get_debuffs=True)
            if len(es) > 0:
                final_damage *= 2.0
            return final_damage
        damage_dealt = self.attack(target_kw1="n_lowest_hp_percentage_enemy", target_kw2="1", multiplier=2.2, repeat=3, func_damage_step=damage_amplify)
        if self.is_alive():
            e = DamageReflect("Candy Warning!", 20, True, False, reflect_percentage=0.3)
            self.apply_effect(e)
        return damage_dealt


    def skill2_logic(self):
        def stun_effect(self, target):
            es = target.get_active_removable_effects(get_buffs=False, get_debuffs=True)
            if len(es) > 0:
                target.apply_effect(StunEffect("Stun", 10, False))
        damage_dealt = self.attack(target_kw1="n_lowest_hp_percentage_enemy", target_kw2="1", multiplier=4.0, repeat=1, func_after_dmg=stun_effect)
        return damage_dealt


    def skill3(self):
        pass

    def after_revive(self):
        e = EffectShield2("Assist", 20, True, False, damage_reduction=1.0, shrink_rate=0.0, hp_threshold=0.15,
                                       damage_reflect_function=lambda x: x * 1.2, 
                                       damage_reflect_description="reflect 120% of received damage that exceeds 15% of maxhp to the attacker.",
                                       damage_reflect_description_jp="最大HPの15%を超えるダメージを受けた場合、超えた部分の120%を状態異常ダメージとして攻撃者に反射する。",
                                       max_reflect_hp_percentage=1.2)
        e.additional_name = "Cheihw_Assist"
        e.apply_rule = "stack"
        self.apply_effect(e)
        e2 = AbsorptionShield("Mr. Naughty Ghost", 20, True, self.maxhp * 0.7, False)
        self.apply_effect(e2)

    def battle_entry_effects(self):
        r = RebornEffect("Surprise Trap", -1, True, effect_value=0.7, cc_immunity=False, buff_applier=self)
        r.can_be_removed_by_skill = False
        self.apply_effect(r)


class Cocoa(Character):
    """
    Weak on frequent status damage.
    Burst damage
    Build: 
    """
    def __init__(self, name, lvl, exp=0, equip=None, image=None):
        super().__init__(name, lvl, exp, equip, image)
        self.name = "Cocoa"
        self.skill1_description = "Attack closest enemy with 380% atk 3 times, if you have Sweet Dreams, double the damage."
        self.skill2_description = "Select an ally of highest atk, reduce the allys skill cooldown by 2," \
        " and increase the allys speed by 200% for 2 turns. If the same effect is applied, duration is refreshed." \
        " if the selected ally is Cocoa, hp is also recovered by 300% atk."
        self.skill3_description = "If haven't taken damage for 6 turns, fall asleep. This effect does not reduce evasion." \
        " While asleep, recover 8% hp each turn. When this effect is removed, for 6 turns," \
        " apply Sweet Dreams on yourself, atk, defense, speed is increased by 120%, gain immunity to CC."
        self.skill1_description_jp = "最も近い敵に380%の攻撃を3回行う。幻夢効果がある場合、ダメージが2倍になる。"
        self.skill2_description_jp = "最も攻撃力が高い味方を選択し、その味方のスキルクールダウンを2減少させ、2ターンの間速度を200%増加させる。" \
                                    "同じ効果が適用された場合、持続時間が更新される。" \
                                    "選択された味方が自分である場合、さらに攻撃力の300%でHPが回復する。"
        self.skill3_description_jp = "6ターンの間攻撃されていない場合、睡眠を付与する。この効果は回避率を減少させない。" \
                                    "眠っている間、毎ターンHPを8%回復する。この効果が解除されると、6ターンの間、" \
                                    "自身に幻夢を付与し、攻撃力、防御力、速度が120%増加し、CC耐性を得る。"
        self.skill1_cooldown_max = 4
        self.skill2_cooldown_max = 4


    def skill1_logic(self):
        def damage_amplify(self, target, final_damage):
            if self.has_effect_that_named("Sweet Dreams", "Cocoa_Sweet_Dreams"):
                final_damage *= 2.0
            return final_damage
        damage_dealt = self.attack(target_kw1="enemy_in_front", multiplier=3.8, repeat=3, func_damage_step=damage_amplify)
        return damage_dealt

    def skill2_logic(self):
        def speed_effect(target: Character):
            spd_e = target.get_effect_that_named("Speed Up", "Cocoa_Speed_Up")
            if not spd_e:
                spd_e = StatsEffect("Speed Up", 2, True, {"spd": 3.0})
                spd_e.additional_name = "Cocoa_Speed_Up"
                target.apply_effect(spd_e)
            else:
                spd_e.duration = 3

            target.update_cooldown()
            target.update_cooldown()
            if target == self:
                self.heal_hp(self.atk * 3.0, self)
        ally = mit.one(self.target_selection(keyword="n_highest_attr", keyword2="1", keyword3="atk", keyword4="ally"))
        speed_effect(ally)
        return 0


    def skill3(self):
        pass

    def battle_entry_effects(self):
        cocoa_sleep = CocoaSleepEffect("Sleep", -1, True)
        shda = NotTakingDamageEffect("Shopping Date", -1, True, 6, cocoa_sleep)
        shda.can_be_removed_by_skill = False
        self.apply_effect(shda)


class CocoaRT(Character):
    """
    Rest time version of Cocoa
    Build: 
    """
    def __init__(self, name, lvl, exp=0, equip=None, image=None):
        super().__init__(name, lvl, exp, equip, image)
        self.name = "CocoaRT"
        self.skill1_description = "Focus attack closest enemy with 230% atk 3 times, if you have Sweet Dreams, attack 3 closest enemies 2 times." \
        " If target is alive after the attack, apply Sleep on the target for 20 turns."
        self.skill2_description = "Select an ally of highest defense, reduce the allys skill cooldown by 3," \
        " and increase the allys speed by 300% for 2 turns. If the same effect is applied, duration is refreshed." \
        " if the selected ally is Cocoa, hp also is recovered by 300% atk."
        self.skill3_description = "If haven't taken damage for 6 turns, fall asleep. This effect does not reduce evasion." \
        " While asleep, recover 8% hp each turn. When this effect is removed, for 6 turns," \
        " apply Sweet Dreams on yourself, atk, defense, speed is increased by 120%, gain immunity to CC."
        self.skill1_description_jp = "最も近い敵に230%の集中攻撃を3回行う。幻夢効果がある場合、最も近い敵3体を2回攻撃する。" \
                                    "攻撃後、対象が生存している場合、対象に20ターン睡眠を付与する。"
        self.skill2_description_jp = "最も防御力が高い味方を選択し、その味方のスキルクールダウンを3減少させ、2ターンの間速度を300%増加させる。" \
                                    "同じ効果が適用された場合、持続時間が更新される。" \
                                    "選択された味方が自分である場合、さらに攻撃力の300%でHPが回復する。"
        self.skill3_description_jp = "6ターンの間攻撃されていない場合、睡眠を付与する。この効果は回避率を減少させない。" \
                                    "眠っている間、毎ターンHPを8%回復する。この効果が解除されると、6ターンの間、" \
                                    "自身に幻夢を付与し、攻撃力、防御力、速度が120%増加し、CC耐性を得る。"
        self.skill1_cooldown_max = 4
        self.skill2_cooldown_max = 4

    def skill1_logic(self):
        t = self.target_selection(keyword="enemy_in_front")
        t = mit.one(t)
        t3 = self.target_selection(keyword="n_enemy_in_front", keyword2="3")
        t3 = list(t3)
        if self.has_effect_that_named("Sweet Dreams", "Cocoa_Sweet_Dreams"):
            damage_dealt = self.attack(multiplier=2.3, repeat_seq=2, target_list=t3)
            if self.is_alive():
                for t in t3:
                    if t.is_alive():
                        t.apply_effect(SleepEffect("Sleep", 20, False))
        else:
            damage_dealt = self.attack(multiplier=2.3, repeat_seq=3, target_list=[t])
            if t.is_alive() and self.is_alive():
                t.apply_effect(SleepEffect("Sleep", 20, False))
        return damage_dealt

    def skill2_logic(self):
        def speed_effect(target: Character):
            spd_e = target.get_effect_that_named("Speed Up", "CocoaRT_Speed_Up")
            if not spd_e:
                spd_e = StatsEffect("Speed Up", 2, True, {"spd": 3.0})
                spd_e.additional_name = "CocoaRT_Speed_Up"
                target.apply_effect(spd_e)
            else:
                spd_e.duration = 3

            target.update_cooldown()
            target.update_cooldown()
            target.update_cooldown()
            if target == self:
                self.heal_hp(self.atk * 3.0, self)
        ally = mit.one(self.target_selection(keyword="n_highest_attr", keyword2="1", keyword3="defense", keyword4="ally"))
        speed_effect(ally)

    def skill3(self):
        pass

    def battle_entry_effects(self):
        cocoa_sleep = CocoaSleepEffect("Sleep", -1, True)
        shda = NotTakingDamageEffect("Resting Time", -1, True, 6, cocoa_sleep)
        shda.can_be_removed_by_skill = False
        self.apply_effect(shda)


class Beacon(Character):
    """

    Build: 
    """
    def __init__(self, name, lvl, exp=0, equip=None, image=None):
        super().__init__(name, lvl, exp, equip, image)
        self.name = "Beacon"
        self.skill1_description = "Redistribute hp percentage for all allies, allies with higher hp percentage takes status damage," \
        " allies with lower hp percentage heals hp until equal percentage. If this skill has no effect, apply AbsorptionShield on all allies for 12 turns." \
        " Shield absorbs 500% atk + 500% def damage. When comparing the HP percentages, they can be considered the same with a margin of error of 1% or less."
        self.skill2_description = "Attack 4 enemies with 300% atk, apply Crescent Moon Mark for 20 turns.Crescent Moon Mark: critical defense is reduced by 50%."
        self.skill3_description = "If you are the only one alive, redistributing hp use 400% as base percentage when calculating average," \
        " before redistributing, revive as many allies as possible with 1 hp and apply New Moon for all allies for 24 turns." \
        " New Moon: damage taken is reduced by 65%." \
        " All skill cooldown is reduced by 2 actions at the end of turn if you are the only one alive."
        self.skill1_description_jp = "全ての味方のHP割合を再分配し、HP割合が高い味方は状態異常ダメージを受け、HP割合が低い味方は同じ割合になるまでHPが治療する。" \
                                    "このスキルに効果がない場合、全ての味方に12ターンの間吸収シールドを付与する。" \
                                    "シールドは攻撃力の500%+防御力の500%までのダメージを吸収する。HP割合を比較する際、1%以内の誤差で同じとみなされる。"
        self.skill2_description_jp = "4体の敵に300%の攻撃を行い、20ターンの間「三日月の痕」を付与する。「三日月の痕」:クリティカル防御を50%減少させる。"
        self.skill3_description_jp = "自分だけが生き残っている場合、HP再分配時に基準割合として400%を使用して平均を計算し、再分配前に可能な限り多くの味方をHP1で復活させる。" \
                                    "全ての味方に24ターンの間「芒月新生」を付与する。「芒月新生」:受けるダメージが65%軽減される。" \
                                    "自分だけが生き残っている場合、ターン終了時に全てのスキルクールダウンが2行動分減少する。"
        self.skill1_cooldown_max = 3
        self.skill2_cooldown_max = 4

    def skill1_logic(self):
        # check if all allies has same hp percentage, if so, do nothing
        hp_percentages = [ally.hp / ally.maxhp for ally in self.ally]
        if len(self.ally) > 1 and max(hp_percentages) - min(hp_percentages) <= 0.01:
            for a in self.ally:
                a.apply_effect(AbsorptionShield("Absorption Shield", 12, True, self.atk * 5.0 + self.defense * 5.0, False))
            global_vars.turn_info_string += f"{self.name} skipped the skill as all allies have same hp percentage.\n"
            return 0
        if not len(self.ally) == 1:
            # if not, redistribute hp percentage
            avg_hp_percentage = sum([a.hp / a.maxhp for a in self.ally]) / len(self.ally)
            for a in self.ally:
                target_hp = avg_hp_percentage * a.maxhp
                if a.hp > target_hp:
                    a.take_status_damage(a.hp - target_hp, None)
                elif a.hp < target_hp:
                    self.heal(target_list=[a], value=target_hp - a.hp)
        else:
            # are the only one alive
            for m in self.party:
                if m.is_dead():
                    m.revive(1, 0, self)
            self.update_ally_and_enemy()
            for a in self.ally:
                a.apply_effect(ReductionShield("New Moon", 24, True, 0.65, False))
            avg_hp_percentage = 4.00 / len(self.ally)
            for a in self.ally:
                target_hp = avg_hp_percentage * a.maxhp
                if a.hp > target_hp:
                    a.take_status_damage(a.hp - target_hp, None)
                elif a.hp < target_hp:
                    self.heal(target_list=[a], value=target_hp - a.hp)

    def skill2_logic(self):
        def crit_def_debuff(self, target):
            target.apply_effect(StatsEffect("Crescent Moon Mark", 20, False, {"critdef": -0.5}))
        damage_dealt = self.attack(multiplier=3.0, repeat=1, target_kw1="n_random_enemy", target_kw2="4", func_after_dmg=crit_def_debuff)
        return damage_dealt


    def skill3(self):
        pass

    def status_effects_at_end_of_turn(self):
        self.update_ally_and_enemy()
        if len(self.ally) == 1:
            self.update_cooldown()
            self.update_cooldown()
        return super().status_effects_at_end_of_turn()


class Timber(Character):
    """

    Build: 
    """
    def __init__(self, name, lvl, exp=0, equip=None, image=None):
        super().__init__(name, lvl, exp, equip, image)
        self.name = "Timber"
        self.skill1_description = "For 6 turns, increase accuracy by 40%, and attack 3 closest enemies with 270% atk." \
        " Enemy is poisoned for 20 turns, poison deals 1.0% of maxhp as status damage per turn."
        self.skill2_description = "Attack 1 closest enemy with 240% atk 4 times. If the target has poison or Great Poison effect, deal 40% more damage." \
        " Damage is increased by 2% of target maxhp."
        self.skill3_description = "Normal attack damage increased by 2% of target maxhp."
        self.skill1_description_jp = "6ターンの間命中率を40%増加し、最も近い3体の敵に270%の攻撃を行う。" \
                                    "敵は20ターンの間毒状態となり、毒は毎ターン最大HPの1.0%を状態異常ダメージとして与える。"
        self.skill2_description_jp = "最も近い敵に240%の攻撃を4回行う。対象が毒、猛毒状態であれば、ダメージが40%増加する。" \
                                    "ダメージは対象の最大HPの2%分増加する。"
        self.skill3_description_jp = "通常攻撃のダメージが対象の最大HPの2%分増加する。"
        self.skill1_cooldown_max = 5
        self.skill2_cooldown_max = 5

    def skill1_logic(self):
        self.apply_effect(StatsEffect("Accuracy Up", 6, True, {"acc": 0.4}))
        def poison_effect(self, target):
            target.apply_effect(ContinuousDamageEffect_Poison("Poison", 20, False, ratio=0.01, imposter=self, base="maxhp"))
        damage_dealt = self.attack(multiplier=2.7, repeat=1, target_kw1="n_enemy_in_front", target_kw2="3", func_after_dmg=poison_effect)
        return damage_dealt

    def skill2_logic(self):
        def damage_amplify(self, target, final_damage):
            if target.has_effect_that_named("Poison") or target.has_effect_that_named("Great Poison"):
                final_damage *= 1.4
            final_damage += target.maxhp * 0.02
            return final_damage
        damage_dealt = self.attack(multiplier=2.4, repeat=4, target_kw1="enemy_in_front", func_damage_step=damage_amplify)
        return damage_dealt


    def skill3(self):
        pass

    def normal_attack(self):
        def damage_amplify(self, target, final_damage):
            final_damage += target.maxhp * 0.02
            return final_damage
        damage_dealt = self.attack(func_damage_step=damage_amplify)
        return damage_dealt


class Scout(Character):
    """

    Build: 
    """
    def __init__(self, name, lvl, exp=0, equip=None, image=None):
        super().__init__(name, lvl, exp, equip, image)
        self.name = "Scout"
        self.skill1_description = "Attack all enemies with 250% atk and apply Photo for 20 turns." \
        " Photo: when taking damage, take 30% of your atk as status damage."
        self.skill2_description = "Select one enemy with highest take down number, attack with 600% atk."  \
        " for each ally the enemy has taken down, attack multipler increased by 600%. Depending on the take down number, effect strengthens." \
        " 1: This attack never misses. 2: This attack will guarantee a critical hit. 3: Before attacking, atk and critdmg is increased by 30% for 12 turns, final damage taken is reduced by 80%." \
        " 4: Convert damage to bypass all damage. 5: Attack all enemies." 
        self.skill3_description = "Gain unremovable reborn effect at start of battle." \
        " When defeated, revive with 100 * lvl hp. When revived, apply Eight Camps for 20 turns." \
        " Eight Camps: def and critdef is increased by 40%."
        self.skill1_description_jp = "全ての敵に250%の攻撃を行い、20ターンの間「写真」を付与する。" \
                                    "写真:ダメージを受けた際、自身の攻撃力の30%を状態異常ダメージとして受ける。"
        self.skill2_description_jp = "最も撃破数の多い敵1体を選択し、600%の攻撃力で攻撃する。" \
                                    "敵が撃破した味方の数に応じて攻撃倍率が600%ずつ増加し、効果が強化される。" \
                                    "1:この攻撃は外れない。2:この攻撃は必ずクリティカルになる。3:攻撃前に、12ターンの間、攻撃力とクリティカルダメージが30%増加し、受ける最終ダメージが80%減少する。" \
                                    "4:ダメージが全ての状態無視するように変換される。5:全ての敵を攻撃する。"
        self.skill3_description_jp = "戦闘開始時に解除不可の再生効果を得る。" \
                                    "倒された際、HPがレベル×100で復活する。復活した際、20ターンの間「八陣」を適用する。" \
                                    "八陣:防御力とクリティカル防御が40%増加する。"
        self.skill1_cooldown_max = 5
        self.skill2_cooldown_max = 4

    def skill1_logic(self):
        def sting_effect(self, target):
            target.apply_effect(StingEffect("Photo", 20, False, self.atk * 0.3, self))
        damage_dealt = self.attack(multiplier=2.5, repeat=1, func_after_dmg=sting_effect, target_kw1="n_random_enemy", target_kw2="5")
        return damage_dealt

    def skill2_logic(self):
        selection = max(self.enemy, key=lambda x: x.number_of_take_downs)
        multiplier = 6.0 + 6.0 * selection.number_of_take_downs
        if selection.number_of_take_downs == 0:
            damage_dealt = self.attack(target_list=[selection], multiplier=multiplier)
            return damage_dealt
        elif selection.number_of_take_downs == 1:
            damage_dealt = self.attack(target_list=[selection], multiplier=multiplier, always_hit=True)
            return damage_dealt
        elif selection.number_of_take_downs == 2:
            damage_dealt = self.attack(target_list=[selection], multiplier=multiplier, always_hit=True, always_crit=True)
            return damage_dealt
        elif selection.number_of_take_downs == 3:
            self.apply_effect(StatsEffect("Punishment Sword", 12, True, {"atk": 1.3, "critdmg": 0.3, 'final_damage_taken_multipler': -0.8}))
            damage_dealt = self.attack(target_list=[selection], multiplier=multiplier, always_hit=True, always_crit=True)
            return damage_dealt
        elif selection.number_of_take_downs == 4:
            self.apply_effect(StatsEffect("Punishment Sword", 12, True, {"atk": 1.3, "critdmg": 0.3, 'final_damage_taken_multipler': -0.8}))
            damage_dealt = self.attack(target_list=[selection], multiplier=multiplier, always_hit=True, always_crit=True, damage_type="bypass")
            return damage_dealt
        elif selection.number_of_take_downs >= 5:
            global_vars.turn_info_string += f"True judgement!\n"
            self.apply_effect(StatsEffect("Punishment Sword", 12, True, {"atk": 1.3, "critdmg": 0.3, 'final_damage_taken_multipler': -0.8}))
            damage_dealt = self.attack(multiplier=multiplier, always_hit=True, always_crit=True, damage_type="bypass",
                                       target_kw1="n_random_enemy", target_kw2="5")
            return damage_dealt
        else:
            raise Exception("Invalid take down number")


    def skill3(self):
        pass

    def battle_entry_effects(self):
        self.apply_effect(RebornEffect("Reborn", -1, True, effect_value=0, cc_immunity=False, buff_applier=self, 
                                       effect_value_constant=100 * self.lvl))
        
    def after_revive(self):
        self.apply_effect(StatsEffect("Eight Camps", 20, True, {"defense": 1.4, "critdef": 0.4}))


class Kyle(Character):
    """

    Build: 
    """
    def __init__(self, name, lvl, exp=0, equip=None, image=None):
        super().__init__(name, lvl, exp, equip, image)
        self.name = "Kyle"
        self.skill1_description = "Select 1 neighbor ally of highest atk, apply Dragon Drawing and Atk Up for 30|20 turns." \
        " Dragon Drawing: When taking down an enemy, the remaining damage is dealt to enemy of lowest hp percentage." \
        " Atk Up: atk and speed increased by 40%. Status and bypass damage does not trigger Dragon Drawing." \
        " When same effect is applied, duration is refreshed."
        self.skill2_description = "Select 1 neighbor ally of highest atk, apply Mountain Drawing and Def Up for 30|20 turns." \
        " Mountain Drawing: Damage taken that exceeds 10% of maxhp is reduced by 50%." \
        " Def Up: defense and speed increased by 40%." \
        " When same effect is applied, duration is refreshed."
        self.skill3_description = "Before a normal attack, heal yourself or a neighbor ally of lowest hp percentage by 300% atk." \
        " "
        self.skill1_description_jp = "最も攻撃力が高い隣接する味方1体を選択し、30|20ターンの間「竜の描写」と「攻撃力アップ」を付与する。" \
                                    "竜の描写:敵を撃破した際、残りのダメージが最もHP割合の低い敵に与えられる。" \
                                    "攻撃力アップ:攻撃力と速度が40%増加する。状態異常および異常状態無視ダメージは「竜の描写」を発動しない。" \
                                    "同じ効果が適用された場合、持続時間が更新される。"
        self.skill2_description_jp = "最も攻撃力が高い隣接する味方1体を選択し、30|20ターンの間「山の描写」と「防御力アップ」を付与する。" \
                                    "山の描写:最大HPの10%を超えるダメージを受けた場合、そのダメージが50%軽減される。" \
                                    "防御力アップ:防御力と速度が40%増加する。" \
                                    "同じ効果が適用された場合、持続時間が更新される。"
        self.skill3_description_jp = "通常攻撃の前に、自身またはHP割合が最も低い隣接する味方を攻撃力の300%で治療する。"

        self.skill1_cooldown_max = 4
        self.skill2_cooldown_max = 4

    def skill1_logic(self):
        two_neighbor = self.get_neighbor_allies_not_including_self()
        if len(two_neighbor) == 0:
            return 0
        ally = max(two_neighbor, key=lambda x: x.atk)
        golden_allow_e = Effect("Dragon Drawing", 30, True, False,
                                tooltip_str="When taking down an enemy, the remaining damage is dealt to enemy of lowest hp percentage.",
                                tooltip_str_jp="敵を撃破した際、残りのダメージが最もHP割合の低い敵に与える。")
        golden_allow_e.additional_name = "Kyle_Dragon_Drawing"
        golden_allow_e.apply_rule = "stack"
        ally.apply_effect(golden_allow_e)
        atk_up_e = StatsEffect("Atk Up", 20, True, {"atk": 1.4, "spd": 1.4})
        atk_up_e.additional_name = "Kyle_Atk_Up"
        atk_up_e.apply_rule = "stack"
        ally.apply_effect(atk_up_e)
        return 0

    def skill2_logic(self):
        two_neighbor = self.get_neighbor_allies_not_including_self()
        if len(two_neighbor) == 0:
            return 0
        ally = max(two_neighbor, key=lambda x: x.atk)
        silver_allow_e = EffectShield2("Mountain Drawing", 30, True, False, damage_reduction=0.5, shrink_rate=0.0, hp_threshold=0.1)
        silver_allow_e.additional_name = "Kyle_Mountain_Drawing"
        silver_allow_e.apply_rule = "stack"
        ally.apply_effect(silver_allow_e)
        def_up_e = StatsEffect("Def Up", 20, True, {"defense": 1.4, "spd": 1.4})
        def_up_e.additional_name = "Kyle_Def_Up"
        def_up_e.apply_rule = "stack"
        ally.apply_effect(def_up_e)
        return 0

    def skill3(self):
        pass

    def normal_attack(self):
        two_neighbor = self.get_neighbor_allies_including_self()
        if len(two_neighbor) == 0:
            return 0
        ally = min(two_neighbor, key=lambda x: x.hp / x.maxhp)
        self.heal(target_list=[ally], value=self.atk * 3.0)
        return self.attack()

    # def battle_entry_effects(self):
    #     for a in self.ally:
    #         a.apply_effect(EffectShield2("Mountain Drawing", 12, True, False, damage_reduction=0.5, shrink_rate=0.0, hp_threshold=0.1))


class Lester(Character):
    """
    Support neighbor ally, accuracy buff, hp recovery, overheal to attack bonus
    Build: 
    """
    def __init__(self, name, lvl, exp=0, equip=None, image=None):
        super().__init__(name, lvl, exp, equip, image)
        self.name = "Lester"
        self.skill1_description = "Apply Exciting Time for the ally with Bookmarks of Memories for 24 turns." \
        " Exciting Time: Every time when a hp recovery is received, atk is increased by 15% of the amount of overheal," \
        " Atk bonus effect lasts for 10 turns. If the same effect is applied, atk bonus is accumulated to the new effect." \
        " The atk bonus cannot exceed 5 * your level."
        self.skill2_description = "Remove a maximum of 4 active debuffs from the ally with Bookmarks of Memories and" \
        " heal 10% of maxhp to the ally. For each debuff removed, heal amount is increased by 10% of maxhp."
        self.skill3_description = "Select 1 neighbor ally of highest atk, apply Bookmarks of Memories to that ally." \
        " Bookmarks of Memories: Everytime when missing an attack, atk, spd and accuracy is increased by 10% and recover 10% of maxhp." \
        " When using skills, if the ally with Bookmarks of Memories is defeated, the skill becomes normal attack," \
        " before this normal attack, 30% chance to revive the ally with 50% hp."
        # 思い出のしおり ドキドキタイム
        self.skill1_description_jp = "「思い出のしおり」を持つ味方に24ターンの間「ドキドキタイム」を付与する。ドキドキタイム：HP回復を受けるたびに、超過回復分の15%攻撃力が増加する。この攻撃力のボーナス効果は10ターン持続する。同じ効果が再度適用された場合、攻撃力のボーナスは新しい効果に累積される。" \
        "攻撃力のボーナスは自身のレベル×5を超えることはない。"
        self.skill2_description_jp = "「思い出のしおり」を持つ味方から最大4つのアクティブなデバフを解除し、その味方の最大HPの10%を治療する。解除されたデバフ1つにつき、回復量が最大HPの10%増加する。"
        self.skill3_description_jp = "攻撃力が最も高い隣接する味方1体を選び、その味方に「思い出のしおり」を付与する。思い出のしおり：攻撃が外れるたびに攻撃力、速度と命中率が10%増加し、最大HPの10%を回復する。スキルを使用する際、「思い出のしおり」を持つ味方が倒されている場合、そのスキルは通常攻撃に変わる。" \
        "この通常攻撃の前に、30%の確率でその味方を50%のHPで復活させる。"
        self.skill1_cooldown_max = 3
        self.skill2_cooldown_max = 3


    def skill1_logic(self):
        t = list(self.target_selection(keyword="ally_that_must_have_effect_full", keyword2="Bookmarks of Memories", keyword3="Lester_Bookmarks_of_Memories",
                                          keyword4="LesterBookofMemoryEffect"))
        if not t:
            if random.random() < 0.3:
                dead_t = None
                for a in self.party:
                    if a.has_effect_that_named("Bookmarks of Memories", "Lester_Bookmarks_of_Memories", "LesterBookofMemoryEffect") and a.is_dead():
                        dead_t = a
                        break
                if dead_t:
                    dead_t.revive(0, 0.5, self)
            else:
                return self.attack()
        self.update_ally_and_enemy()
        t = list(self.target_selection(keyword="ally_that_must_have_effect_full", keyword2="Bookmarks of Memories", keyword3="Lester_Bookmarks_of_Memories",
                                          keyword4="LesterBookofMemoryEffect"))
        if not t:
            # This happens when the ally targeting is limited, for example, confuse, charm, etc.
            return self.attack()
        a = t[0]
        if a.is_alive():
            et = LesterExcitingTimeEffect("Exciting Time", 24, True, buff_applier=self)
            et.additional_name = "Lester_Exciting_Time"
            et.apply_rule = "stack"
            a.apply_effect(et)
        return 0

    def skill2_logic(self):
        t = list(self.target_selection(keyword="ally_that_must_have_effect_full", keyword2="Bookmarks of Memories", keyword3="Lester_Bookmarks_of_Memories",
                                          keyword4="LesterBookofMemoryEffect"))
        if not t:
            if random.random() < 0.3:
                dead_t = None
                for a in self.party:
                    if a.has_effect_that_named("Bookmarks of Memories", "Lester_Bookmarks_of_Memories", "LesterBookofMemoryEffect") and a.is_dead():
                        dead_t = a
                        break
                if dead_t:
                    dead_t.revive(0, 0.5, self)
            else:
                return self.attack()
        self.update_ally_and_enemy()
        t = list(self.target_selection(keyword="ally_that_must_have_effect_full", keyword2="Bookmarks of Memories", keyword3="Lester_Bookmarks_of_Memories",
                                          keyword4="LesterBookofMemoryEffect"))
        if not t:
            # This happens when the ally targeting is limited, for example, confuse, charm, etc.
            return self.attack()
        a: Character = t[0]
        if a.is_alive():
            debuffs = a.remove_random_amount_of_debuffs(4, allow_infinite_duration=False)
        if a.is_alive():
            amount = len(debuffs) * a.maxhp * 0.1 + a.maxhp * 0.1
            self.heal(target_list=[a], value=amount)
        return 0

    def skill3(self):
        pass


    def battle_entry_effects(self):
        bom = LesterBookofMemoryEffect("Bookmarks of Memories", -1, True, {'atk': 1.00, 'spd': 1.00, "acc": 0.00}, buff_applier=self)
        bom.can_be_removed_by_skill = False
        bom.additional_name = "Lester_Bookmarks_of_Memories"
        neighbors = self.get_neighbor_allies_not_including_self()
        selected = max(neighbors, key=lambda x: x.atk)
        selected.apply_effect(bom)


class Moe(Character):
    """
    Counter crit and buffs
    Main attacker
    Build: 
    """
    def __init__(self, name, lvl, exp=0, equip=None, image=None):
        super().__init__(name, lvl, exp, equip, image)
        self.name = "Moe"
        self.skill1_description = "Target an ememy of highest crit rate, if target have active buffs, attack with 400% atk," \
        " otherwise attack with 200% atk. Attack 4 times, each attack removes 1 active buff from the target." \
        " After the attack, apply Paradox on target for 24 turns, reduce crit damage by 60%."
        self.skill2_description = "Attack all enemies with 200% atk, if enemy has active buffs, attack with 400% atk."
        self.skill3_description = "When taking critical damage, recover hp by 300% atk, reduced that damage by 50%."
        self.skill1_description_jp = "クリティカル率が最も高い敵を対象にする。対象にアクティブなバフがある場合、攻撃力の400%で攻撃し、ない場合は攻撃力の200%で攻撃する。4回攻撃し、各攻撃で1つのアクティブなバフを解除する。攻撃後、対象に24ターンの間「矛盾」を付与し、クリティカルダメージを60%減少させる。"
        self.skill2_description_jp = "全ての敵に攻撃力の200%で攻撃し、敵にアクティブなバフがある場合は攻撃力の400%で攻撃する。"
        self.skill3_description_jp = "クリティカルダメージを受けた際、攻撃力の300%分HPを回復し、そのダメージを50%軽減する。"

        self.skill1_cooldown_max = 4
        self.skill2_cooldown_max = 4


    def skill1_logic(self):
        # ("n_highest_attr", n, attr, party)
        t:Character = mit.one(self.target_selection(keyword="n_highest_attr", keyword2="1", keyword3="crit", keyword4="enemy"))

        def remove_buffs(self, target: Character):
            target.remove_random_amount_of_buffs(1, allow_infinite_duration=False)

        def multipler_func(self, target, _, __):
            if len(target.get_active_removable_effects(get_buffs=True, get_debuffs=False)) > 0:
                return 4.0
            else:
                return 2.0

        damage_dealt = self.attack(target_list=[t], repeat=4, func_after_dmg=remove_buffs, func_for_multiplier=multipler_func)
        if t.is_alive() and self.is_alive():
            t.apply_effect(StatsEffect("Paradox", 24, False, {"critdmg": -0.6}))

        return damage_dealt


    def skill2_logic(self):
        def multipler_func(self, target, _, __):
            if len(target.get_active_removable_effects(get_buffs=True, get_debuffs=False)) > 0:
                return 4.0
            else:
                return 2.0
        damage_dealt = self.attack(repeat=1, target_kw1="n_random_enemy", target_kw2="5", func_for_multiplier=multipler_func)
        return damage_dealt


    def skill3(self):
        pass

    def battle_entry_effects(self):
        def heal_func(character: Character):
            return character.atk * 3.0
        sf = EffectShield1_healoncrit("Sweets Fluffy", -1, True, 1, effect_applier=self, cc_immunity=False,
                                      heal_function=heal_func, critdmg_reduction=0.50)
        sf.can_be_removed_by_skill = False
        self.apply_effect(sf)


class Mitsuki(Character):
    """
    Counter status damage
    Build: maxhp
    """
    def __init__(self, name, lvl, exp=0, equip=None, image=None):
        super().__init__(name, lvl, exp, equip, image)
        self.name = "Mitsuki"
        self.skill1_description = "Attack closest enemy with 3% of current hp 12 times. Each attack has a 8% chance to Stun the target for 8 turns."
        self.skill2_description = "All allies are healed by 3% of your current hp, remove 2 random debuffs for each ally."
        self.skill3_description = "At start of battle, apply unremovable Azure Sea for all allies." \
        " Azure Sea: Status damage taken is reduced by 70%. Apply unremovable Sea Family for yourself," \
        " When taking status damage, recover hp by 3% of current hp."
        # Japanese: 蒼海 蒼海の眷属
        self.skill1_description_jp = "最も近い敵に現在HPの3%で12回攻撃する。各攻撃には8%の確率で8ターンの間、対象をスタンさせる。"
        self.skill2_description_jp = "全ての味方のHPを自分の現在HPの3%分治療し、各味方からランダムなデバフを2つ解除する。"
        self.skill3_description_jp = "戦闘開始時に全ての味方に解除不能な蒼海を付与する。蒼海:受ける状態異常ダメージが70%減少する。自身には解除不能な蒼海の眷属を付与する。状態異常ダメージを受けた時、現在HPの3%分のHPを回復する。"

        self.skill1_cooldown_max = 5
        self.skill2_cooldown_max = 3


    def skill1_logic(self):
        def stun_effect(self, target):
            dice = random.randint(1, 100)
            if dice <= 8:
                target.apply_effect(StunEffect("Stun", 8, False, False))
        damage_dealt = self.attack(multiplier=0.03, repeat=12, target_kw1="enemy_in_front", func_after_dmg=stun_effect,
                                   damage_is_based_on="hp")
        return damage_dealt


    def skill2_logic(self):
        for a in self.ally:
            self.heal(target_list=[a], value=self.hp * 0.03)
            a.remove_random_amount_of_debuffs(2)

    def skill3(self):
        pass

    def battle_entry_effects(self):
        for a in self.ally:
            azure_sea = ReductionShield("Azure Sea", -1, True, 0.7, False, cover_status_damage=True, cover_normal_damage=False)
            azure_sea.can_be_removed_by_skill = False
            a.apply_effect(azure_sea)
        def heal_func(character: Character):
            return character.hp * 0.03
        sea_family = EffectShield1("Sea Family", -1, True, 1, heal_function=heal_func, cc_immunity=False, effect_applier=self,
                                    cover_status_damage=True, cover_normal_damage=False)
        sea_family.can_be_removed_by_skill = False
        self.apply_effect(sea_family)


class Wenyuan(Character):
    """

    Build: 
    """
    def __init__(self, name, lvl, exp=0, equip=None, image=None):
        super().__init__(name, lvl, exp, equip, image)
        self.name = "Wenyuan"
        self.skill1_description = "Attack enemy of lowest hp percentage with 230% atk 3 times. If this skill takes down an enemy, heal yourself" \
        " by 100% of damage dealt and apply Frost Lull to all allies for 24 turns. Frost Lull: damage taken is reduced by 20%. When the same effect is applied," \
        " duration of the already applied effect is refreshed."
        self.skill2_description = "Attack enemy of lowest hp percentage with 165% atk 6 times. If this skill takes down an enemy, attack" \
        " all enemies with 320% atk, double the damage if target hp percentage is higher than 50%."
        self.skill3_description = "After taking down an enemy with skill, remove 2 random debuffs for yourself. At start of battle, apply unremovable Frost Lull" \
        " to yourself for 12 turns, damage taken is reduced by 70% and provide CC immunity."
        # 霜凪
        self.skill1_description_jp = "HP割合が最も低い敵に攻撃力の230%で3回攻撃する。このスキルで敵を倒した場合、与えたダメージの100%分、自身を治療し、全ての味方に24ターンの間「霜凪」を付与する。霜凪:受けるダメージが20%減少する。同じ効果が再度付与された場合、既に付与されている効果の持続時間が更新される。"
        self.skill2_description_jp = "HP割合が最も低い敵に攻撃力の165%で6回攻撃する。このスキルで敵を倒した場合、全ての敵に攻撃力の320%で攻撃し、対象のHP割合が50%以上の場合、ダメージが2倍になる。"
        self.skill3_description_jp = "スキルで敵を倒した後、自身からランダムなデバフを2つ解除する。戦闘開始時に自身に12ターンの間解除不能な「霜凪」を付与し、受けるダメージが70%減少し、CC免疫を得る。"

        self.skill1_cooldown_max = 4
        self.skill2_cooldown_max = 4


    def skill1_logic(self):
        t = mit.one(self.target_selection(keyword="n_lowest_attr", keyword2="1", keyword3="hp", keyword4="enemy"))
        damage_dealt = self.attack(multiplier=2.3, repeat=3, target_list=[t])
        if t.is_dead() and self.is_alive():
            # test_check = self.get_effect_that_named("Frost Lull", additional_name="Wenyuan_Frost_Lull")
            # if test_check is not None:
            #     print("Wenyuan has Frost Lull") # 1 in 100 chance this happens
            self.update_ally_and_enemy()
            self.heal(target_kw1="yourself", value=damage_dealt * 1.0)
            for a in self.ally:
                fl = ReductionShield("Frost Lull", 24, True, 0.20, False)
                fl.additional_name = "Wenyuan_Frost_Lull"
                fl.apply_rule = "stack"
                a.apply_effect(fl)
            self.remove_random_amount_of_debuffs(2)
        return damage_dealt


    def skill2_logic(self):
        t = mit.one(self.target_selection(keyword="n_lowest_attr", keyword2="1", keyword3="hp", keyword4="enemy"))
        damage_dealt = self.attack(multiplier=1.65, repeat=6, target_list=[t])
        if t.is_dead() and self.is_alive():
            self.update_ally_and_enemy()
            def damage_amplify(self, target, final_damage):
                if target.hp / target.maxhp > 0.5:
                    final_damage *= 2
                return final_damage
            damage_dealt += self.attack(multiplier=3.2, repeat=1, target_kw1="n_random_enemy", target_kw2="5", func_damage_step=damage_amplify)
            self.remove_random_amount_of_debuffs(2)
        return damage_dealt


    def skill3(self):
        pass

    def battle_entry_effects(self):
        fl = ReductionShield("Frost Lull", 12, True, 0.70, True)
        fl.additional_name = "Wenyuan_Frost_Lull"
        fl.apply_rule = "stack"
        fl.can_be_removed_by_skill = False
        self.apply_effect(fl)


class Zhen(Character):
    """
    Stun support
    Build: 
    """
    def __init__(self, name, lvl, exp=0, equip=None, image=None):
        super().__init__(name, lvl, exp, equip, image)
        self.name = "Zhen"
        self.skill1_description = "Attack enemy of highest atk with 240% atk 3 times, each attack has a 40% chance to Stun the target for 12 turns."
        self.skill2_description = "Attack enemy of highest atk with 300% atk, heal all allies by 50% of damage dealt." \
        " If target hp percentage is lower than 20%, 80% chance to Stun the target for 12 turns."
        self.skill3_description = "Apply Dragon Cushion on yourself. When taking normal damage from the enemy who has a stunned ally, damage taken is reduced by 60%." \
        " At start of battle, apply Shadow of Great Bird on all enemies, when taking damage while being stunned," \
        " all damage taken is increased by 50%."
        self.skill1_description_jp = "攻撃力が最も高い敵に攻撃力の240%で3回攻撃する。各攻撃には40%の確率で対象を12ターンの間スタンさせる。"
        self.skill2_description_jp = "攻撃力が最も高い敵に攻撃力の300%で攻撃し、与えたダメージの50%分、全ての味方を回復する。対象のHP割合が20%以下の場合、80%の確率で対象を12ターンの間スタンさせる。"
        self.skill3_description_jp = "自身に「龍クッション」を付与する。スタンしている味方がいる敵から通常ダメージを受けた時、そのダメージが60%減少する。戦闘開始時に全ての敵に「鴻影」を付与する。スタン状態でダメージを受けた時、受ける全てのダメージが50%増加する。"
        self.skill1_cooldown_max = 4
        self.skill2_cooldown_max = 4


    def skill1_logic(self):
        def stun_effect(self, target):
            dice = random.randint(1, 100)
            if dice <= 40:
                target.apply_effect(StunEffect("Stun", 12, False, False))
        damage_dealt = self.attack(multiplier=2.4, repeat=3, target_kw1="n_highest_attr", target_kw2="1", target_kw3="atk", target_kw4="enemy",
                                    func_after_dmg=stun_effect)
        return damage_dealt



    def skill2_logic(self):
        def stun_effect(self, target):
            dice = random.randint(1, 100)
            if dice <= 80 and target.hp / target.maxhp < 0.2:
                target.apply_effect(StunEffect("Stun", 12, False, False))
        damage_dealt = self.attack(multiplier=3.0, repeat=1, target_kw1="n_highest_attr", target_kw2="1", target_kw3="atk", target_kw4="enemy",
                                   func_after_dmg=stun_effect)
        if self.is_alive():
            self.heal(target_kw1="n_random_ally", target_kw2="5", value=damage_dealt * 0.5)
        return damage_dealt


    def skill3(self):
        pass


    def battle_entry_effects(self):
        def requirement_func(charac, attacker):
            for a in attacker.ally:
                if a.is_alive() and a.is_stunned():
                    return True
            return False
        dc = ReductionShield("Dragon Cushion", -1, True, 0.6, False, cover_status_damage=False, cover_normal_damage=True,
                                        requirement=requirement_func,
                                        requirement_description="Taking damage from the enemy who has a stunned ally.",
                                        requirement_description_jp="スタンしている味方がいる敵からダメージを受けた時。")
        dc.can_be_removed_by_skill = False
        self.apply_effect(dc)
        for e in self.enemy:
            shadow_of_great_bird = ReductionShield("Shadow of Great Bird", -1, False, 0.5, False, cover_status_damage=True, cover_normal_damage=True,
                                                requirement=lambda x, y: x.is_stunned(),
                                                requirement_description="Taking damage while being stunned.",
                                                    requirement_description_jp="スタン状態でダメージを受けた時。")
            e.apply_effect(shadow_of_great_bird)


class ZhenAL(Character):
    """
    Stun support
    Build: 
    """
    def __init__(self, name, lvl, exp=0, equip=None, image=None):
        super().__init__(name, lvl, exp, equip, image)
        self.name = "ZhenAL"
        self.skill1_description = "Apply Shadow of Great Bird on 3 enemies of highest hp percentage for indefinite turns." \
        " Shadow of Great Bird: When hp falls below 90%|60%|30%, stun for 7 turns at the start of turn." \
        " Each effect triggers on specific hp percentage can only be applied once." \
        " The previous effect is replaced when the same effect is applied."
        self.skill2_description = "This skill becomes normal attack if no enemies are stunned. Attack stunned enemies 3 times with 270% atk," \
        " each attack removes 1 random active buff from the target."
        self.skill3_description = "Apply Dragon Cushion on yourself. When taking normal damage from the enemy who has a stunned ally, damage taken is reduced by 70%."
        self.skill1_description_jp = "HP割合が最も高い敵3体に無期限で「鴻影」を付与する。鴻影：HPが90%|60%|30%以下になった時、ターン開始時に7ターンの間スタン状態にする。各HP割合に対応する効果は1回のみ発動する。同じ効果が再度適用された場合、前の効果は上書きされる。"
        self.skill2_description_jp = "スタン状態の敵がいない場合、このスキルは通常攻撃になる。スタン状態の敵に攻撃力の270%で3回攻撃し、各攻撃ごとに対象のアクティブなバフを1つ解除する。"
        self.skill3_description_jp = "自身に「龍クッション」を付与する。スタン状態の味方がいる敵から通常ダメージを受ける際、受けるダメージが70%減少する。"
        self.skill1_cooldown_max = 4
        self.skill2_cooldown_max = 4

    def skill1_logic(self):
        targets = list(self.target_selection(keyword="n_highest_hp_percentage_enemy", keyword2="3"))
        for t in targets:
            stun = StunEffect("Stun", 7, False, False)
            sgb = BirdShadowEffect("Shadoww of Great Bird", -1, False, False, self, 
                                   effect_dict={0.9: stun, 0.6: stun, 0.3: stun}, can_be_removed_by_skill=True)
            sgb.additional_name = "ZhenAL_Shadow_of_Great_Bird"
            sgb.apply_rule = "replace"
            t.apply_effect(sgb)
        return 0

    def skill2_logic(self):
        stunned_targets = list(self.target_selection(keyword="enemy_that_must_have_effect", keyword2="Stun"))
        if not stunned_targets:
            return self.normal_attack()
        def remove_buffs(self, target):
            target.remove_random_amount_of_buffs(1, allow_infinite_duration=False)
        damage_dealt = self.attack(multiplier=2.7, repeat=3, func_after_dmg=remove_buffs, target_list=stunned_targets)
        return damage_dealt

    def skill3(self):
        pass

    def battle_entry_effects(self):
        def requirement_func(charac, attacker):
            for a in attacker.ally:
                if a.is_alive() and a.is_stunned():
                    return True
            return False
        dc = ReductionShield("Dragon Cushion", -1, True, 0.7, False, cover_status_damage=False, cover_normal_damage=True,
                                        requirement=requirement_func,
                                        requirement_description="Taking damage from the enemy who has a stunned ally.",
                                        requirement_description_jp="スタンしている味方がいる敵からダメージを受けた時。")
        dc.can_be_removed_by_skill = False
        self.apply_effect(dc)


class Cupid(Character): 
    """
    Very special attacker
    Build: 
    """
    def __init__(self, name, lvl, exp=0, equip=None, image=None):
        super().__init__(name, lvl, exp, equip, image)
        self.name = "Cupid"
        self.skill1_description = "Apply Lead Arrow on 3 enemies of highest atk for 20 turns, apply Gold Arrow on yourself for 20 turns." \
        " Lead Arrow: Critical defense is decreased by 100%, when this effect is removed, take 1 status damage." \
        " Gold Arrow: Critical damage is increased by 100%. When Lead Arrow or Gold Arrow is applied on the same target, duration is refreshed."
        self.skill2_description = "Attack all enemies with 200% atk who have Lead Arrow." \
        " When attacking enemy while you have Gold Arrow and target has Lead Arrow, damage increased by 100%," \
        " but leaves 1 hp for the target if this attack is lethal. On a critical hit, applys Love Fantasy on target for 4 turns and set Lead Arrow duration to its duration." \
        " Love Fantasy: Allies with Lead Arrow is seen as enemy, only allies with Lead Arrow is seen as ally." \
        " When the same effect is applied, duration of the already applied effect is refreshed." \
        " If no enemy has Lead Arrow, heal hp by 200% of atk."
        self.skill3_description = "Normal attack does nothing. Apply For Love 2 times on yourself, when defeated, revive with 50% hp."
        # 鉛矢 金矢 恋愛妄想 愛のために
        self.skill1_description_jp = "攻撃力が最も高い3人の敵に20ターンの間「鉛矢」を付与し、自身に20ターンの間「金矢」を付与する。鉛矢:クリティカル防御が100%減少し、この効果が解除されると状態異常ダメージを1受ける。金矢:クリティカルダメージが100%増加する。鉛矢または金矢が同じ対象に再度適用された場合、持続時間が更新される。"
        self.skill2_description_jp = "鉛矢を持つ全ての敵に攻撃力の200%で攻撃する。自分が金矢を持ち、対象が鉛矢を持っている場合、ダメージが100%増加するが、この攻撃で致命的ダメージを与えた場合、対象のHPは1残る。クリティカルの場合、対象に4ターンの間「恋愛妄想」を付与し、鉛矢の持続時間を恋愛妄想の持続時間に設定する。恋愛妄想:鉛矢を持つ味方は敵として認識され、鉛矢を持つ者だけが味方として認識される。同じ効果が再度適用された場合、既存の効果の持続時間が更新される。敵に鉛矢を持つ者がいない場合、攻撃力の200%分HPを治療する。"
        self.skill3_description_jp = "通常攻撃は何もしない。自身に「愛のために」を2回付与し、撃破された時、HP50%で復活する。"
        self.skill1_cooldown_max = 2
        self.skill2_cooldown_max = 0


    def skill1_logic(self):
        ts = self.target_selection(keyword="n_highest_attr", keyword2="3", keyword3="atk", keyword4="enemy")
        for t in list(ts):
            la = CupidLeadArrowEffect("Lead Arrow", 20, False, {"critdef": -1.0})
            la.additional_name = "Cupid_Lead_Arrow"
            la.apply_rule = "stack"
            t.apply_effect(la)
        ga = StatsEffect("Gold Arrow", 20, True, {"critdmg": 1.0})
        ga.additional_name = "Cupid_Gold_Arrow"
        ga.apply_rule = "stack"
        self.apply_effect(ga)
        return 0

    def skill2_logic(self):
        # The effects are mostly implemented in CupidLeadArrowEffect so it is simple here
        target_list = list(self.target_selection(keyword="enemy_that_must_have_effect", keyword2="Lead Arrow"))
        if not target_list:
            self.heal(target_kw1="yourself", value=self.atk * 2.0)
            return 0
        else:
            damage_dealt = self.attack(multiplier=2.0, target_list=target_list)
        if target_list:
            for t in target_list:
                t.update_ally_and_enemy()
        return damage_dealt

    def skill3(self):
        pass

    def normal_attack(self):
        return 0

    def battle_entry_effects(self):
        for i in range(2):
            for_love = RebornEffect("For Love", -1, True, effect_value=0.5, cc_immunity=False, buff_applier=self, effect_value_constant=0)
            for_love.additional_name = "Cupid_For_Love"
            for_love.can_be_removed_by_skill = False
            self.apply_effect(for_love)


class East(Character):
    """
    Shield melt, High single damage, shield
    Build: 
    """
    def __init__(self, name, lvl, exp=0, equip=None, image=None):
        super().__init__(name, lvl, exp, equip, image)
        self.name = "East"
        self.skill1_description = "Select 3 allies of lowest hp percentage, apply absorption shield that absorbs 300% of atk for 20 turns and remove all Burn effects." \
        " For 20 turns, increase their defense and critdef by 10%." \
        " Select all enemies who have absorption shield, inflict Boiling Water for 20 turns, Boiling Water deals 50% of atk status damage per turn," \
        " this effect is removed when the absorption shield no longer exists. When this effect is removed, deal status damage to the target," \
        " damage equals to 80% of total damage dealt to the absorption shield."
        self.skill2_description = "Attack enemy of highest hp with 600% atk, if target has absorption shield, attack multiplier becomes" \
        " 900% and apply Poison for 20 turns, Poison deals 3% of current hp status damage per turn."
        self.skill3_description = "Apply No Matter Day or Month on yourself. When taking damage, if the target has both of the following effects, reduce damage taken by 100%:"
        " (Poison or Great Poison) and (Burn or Boiling Water)."
        # 煮え滾れ熱湯 日も月も構わず
        self.skill1_description_jp = "HP割合が最も低い3人の味方を選び、20ターンの間、攻撃力の300%分を吸収するシールドを付与し、全ての燃焼効果を解除する。20ターンの間、防御力とクリティカル防御を10%増加させる。吸収シールドを持つ全ての敵を選び、20ターンの間「煮え滾れ熱湯」を付与する。煮え滾れ熱湯は、毎ターン攻撃力の50%分の状態異常ダメージを与え、この効果は吸収シールドが消えると解除される。この効果が解除された時、対象に吸収シールドに与えた総ダメージの80%分の状態異常ダメージを与える。"
        self.skill2_description_jp = "HPが最も高い敵に攻撃力の600%で攻撃する。対象が吸収シールドを持っている場合、攻撃倍率は900%になり、20ターンの間「毒」を付与する。毒は、毎ターン現在のHPの3%分の状態異常ダメージを与える。"
        self.skill3_description_jp = "自身に「日も月も構わず」を付与する。ダメージを受けた際、対象が以下の両方の効果を持っている場合、受けるダメージを100%減少させる:(毒または猛毒) と (燃焼または煮え滾れ熱湯)。"
        self.skill1_cooldown_max = 4
        self.skill2_cooldown_max = 4


    def skill1_logic(self):
        ts = self.target_selection(keyword="n_lowest_hp_percentage_ally", keyword2="3")
        lts: list[Character] = list(ts)
        for a in lts:
            a.apply_effect(AbsorptionShield("Absorption Shield", 20, True, 3.0 * self.atk, False))
            a.apply_effect(StatsEffect("Defense Up", 20, True, {"defense": 1.1, "critdef": 1.1}))
            a.try_remove_effect_with_name("Burn", remove_all_found_effects=True)
        enemy_selection = self.target_selection(keyword="enemy_that_must_have_effect_full", keyword2="None", keyword3="None", keyword4="AbsorptionShield")
        # create a list
        try:
            enemy_list: list[Character] = list(enemy_selection)
        except IndexError: # No enemy has Absorption Shield
            return 0
        for e in enemy_list:
            e.apply_effect(EastBoilingWaterEffect("Boiling Water", 20, False, self.atk * 0.5, self))
        return 0

    def skill2_logic(self):
        def poison_effect(self, target: Character):
            if target.has_effect_that_named(class_name="AbsorptionShield"):
                target.apply_effect(ContinuousDamageEffect_Poison("Poison", 20, False, 0.03, imposter=self, base="hp"))
        def multiplier_func(self, target, _, __):
            if target.has_effect_that_named(class_name="AbsorptionShield"):
                return 9.0
            return 6.0
        damage_dealt = self.attack(multiplier=6.0, target_kw1="n_highest_attr", target_kw2="1", target_kw3="hp", target_kw4="enemy",
                                   func_after_dmg=poison_effect, func_for_multiplier=multiplier_func)
        return damage_dealt


    def skill3(self):
        pass

    def battle_entry_effects(self):
        def requirement_func(charac, attacker: Character):
            poison = attacker.has_effect_that_named("Poison") or attacker.has_effect_that_named("Great Poison")
            burn = attacker.has_effect_that_named("Burn") or attacker.has_effect_that_named("Boiling Water")
            if poison and burn:
                return True
            return False
        nmdm = ReductionShield("No Matter Day or Month", -1, True, 1.0, False, cover_status_damage=True, cover_normal_damage=True,
                               requirement=requirement_func,
                               requirement_description="Attacker is both poisoned and burning.",
                               requirement_description_jp="攻撃側は毒と燃焼状態である。")
        nmdm.can_be_removed_by_skill = False
        self.apply_effect(nmdm)
        

class Lenpo(Character):
    """
    Burst damage, counter single damage
    Build: 
    """
    def __init__(self, name, lvl, exp=0, equip=None, image=None):
        super().__init__(name, lvl, exp, equip, image)
        self.name = "Lenpo"
        self.skill1_description = "Attack enemy of highest hp with 600% atk, if this attack does not take down the enemy, attack" \
        " enemy of highest hp again with 400% atk."
        self.skill2_description = "Attack enemy of highest hp with 800% atk, if this attack does not take down the enemy, apply Regeneration on the target" \
        " for 24 turns, the full duration total healing amount is equal to 100% of the actual damage dealt."
        self.skill3_description = "At start of battle, apply Self Defense on yourself, Self Defense cancel normal damage 12 times, every time skill is used," \
        " Self Defense recharges to provide 3 more cancellations."
        self.skill1_description_jp = "HPが最も高い敵に攻撃力の600%で攻撃し、この攻撃で敵を倒せなかった場合、再度HPが最も高い敵に攻撃力の400%で攻撃する。"
        self.skill2_description_jp = "HPが最も高い敵に攻撃力の800%で攻撃し、この攻撃で敵を倒せなかった場合、対象に24ターンの間「再生」を付与する。持続時間中の総回復量は、与えたダメージの100%に相当する。"
        self.skill3_description_jp = "戦闘開始時に、自身に「自己防衛」を付与する。自己防衛は通常ダメージを12回無効化し、スキルを使用するたびに3回分の無効化がリチャージされる。"
        self.skill1_cooldown_max = 4
        self.skill2_cooldown_max = 4


    def skill1_logic(self):
        t = self.target_selection(keyword="n_highest_attr", keyword2="1", keyword3="hp", keyword4="enemy")
        t = mit.one(t)
        damage_dealt = self.attack(multiplier=6.0, target_list=[t])
        if self.is_alive() and t.is_alive():
            self.update_ally_and_enemy()
            t = self.target_selection(keyword="n_highest_attr", keyword2="1", keyword3="hp", keyword4="enemy")
            t = mit.one(t)
            damage_dealt += self.attack(multiplier=4.0, target_list=[t])
        if self.is_alive():
            sd = self.get_effect_that_named("Self Defense", "Lenpo_Self_Defense")
            sd.uses += 3
        return damage_dealt


    def skill2_logic(self):
        t = self.target_selection(keyword="n_highest_attr", keyword2="1", keyword3="hp", keyword4="enemy")
        t = mit.one(t)
        t_hp_prev = t.hp
        damage_dealt = self.attack(multiplier=8.0, target_list=[t])
        t_hp_after = t.hp
        if t.is_alive():
            def heal_func(char, effect_applier):
                return ((abs(t_hp_after - t_hp_prev)) * 1.00) / 24
            t.apply_effect(ContinuousHealEffect("Regeneration", 24, True, value_function=heal_func, buff_applier=self,
                                                value_function_description=f"{((abs(t_hp_after - t_hp_prev)) * 1.00) / 24}",
                                                value_function_description_jp=f"{((abs(t_hp_after - t_hp_prev)) * 1.00) / 24}"))
        if self.is_alive():
            sd = self.get_effect_that_named("Self Defense", "Lenpo_Self_Defense")
            sd.uses += 3
        return damage_dealt


    def skill3(self):
        pass

    def battle_entry_effects(self):
        self_defense = CancellationShield("Self Defense", -1, True, threshold=0, cc_immunity=False, uses=12,
                                          remove_this_effect_when_use_is_zero=False,
                                          cover_normal_damage=True, cover_status_damage=False)
        self_defense.additional_name = "Lenpo_Self_Defense"
        self_defense.can_be_removed_by_skill = False
        self.apply_effect(self_defense)


class LenpoOG(Character):
    """
    Original. Simply high burst damage 
    Build: 
    """
    def __init__(self, name, lvl, exp=0, equip=None, image=None):
        super().__init__(name, lvl, exp, equip, image)
        self.name = "LenpoOG"
        self.skill1_description = "Target 1 enemy of highest hp percentage, attack with 800% atk."
        self.skill2_description = "Heal hp by 50% of maxhp, then attack a random enemy with 800% atk."
        self.skill3_description = "At start of battle, apply Fujieda on yourself. Fujieda: Normal damage is cancelled 12 times."
        self.skill1_description_jp = "HP割合が最も高い敵1体を対象に、攻撃力の800%で攻撃する。"
        self.skill2_description_jp = "自身のHPを最大HPの50%分治療し、その後、ランダムな敵1体に攻撃力の800%で攻撃する。"
        self.skill3_description_jp = "戦闘開始時に自身に「藤枝」を付与する。藤枝：通常ダメージを12回無効化する。"
        self.skill1_cooldown_max = 4
        self.skill2_cooldown_max = 4

    def skill1_logic(self):
        damage_dealt = self.attack(multiplier=8.0, repeat=1, target_kw1="n_highest_hp_percentage_enemy", target_kw2="1")
        return damage_dealt

    def skill2_logic(self):
        self.heal(target_kw1="yourself", value=self.maxhp * 0.5)
        damage_dealt = self.attack(multiplier=8.0, repeat=1)
        return damage_dealt

    def skill3(self):
        pass

    def battle_entry_effects(self):
        fujieda = CancellationShield("Fujieda", -1, True, threshold=0, cc_immunity=False, uses=12,
                                     remove_this_effect_when_use_is_zero=True,
                                     cover_normal_damage=True, cover_status_damage=False)
        fujieda.can_be_removed_by_skill = False
        self.apply_effect(fujieda)


class George(Character):
    """

    Build: 
    """
    def __init__(self, name, lvl, exp=0, equip=None, image=None):
        super().__init__(name, lvl, exp, equip, image)
        self.name = "George"
        self.skill1_description = "Attack 3 closest enemies with 260% atk and apply Close River for 24 turns. Close River: When targeting an enemy," \
        " only the character in the middle of enemy party can be targeted. Effect is removed when the enemy in middle is defeated." \
        " or you are defeated, or the enemy in the middle cannot be targeted."
        self.skill2_description = "Attack random enemies 7 times with 200% atk each, for each lost ally of the target, damage is increased by 30%."
        self.skill3_description = "Apply Distant Mountain on yourself. Distant Mountain: Before taken action in battle, reduce damage taken by 50%."
        # 遠山 近水
        self.skill1_description_jp = "最も近い3人の敵に攻撃力の260%で攻撃し、24ターンの間「近水」を付与する。近水：敵をターゲットにする際、敵パーティの中央のキャラクターのみを対象にできる。この効果は、中央の敵が倒された時、または自分が倒された時、もしくは中央の敵がターゲットにできない状態になった時に解除される。"
        self.skill2_description_jp = "ランダムな敵に攻撃力の200%で7回攻撃する。対象が失った味方1人につき、ダメージが30%増加する。"
        self.skill3_description_jp = "自身に「遠山」を付与する。遠山：戦闘中、行動する前に受けるダメージが50%減少する。"
        self.skill1_cooldown_max = 4
        self.skill2_cooldown_max = 4


    def skill1_logic(self):
        character_marked = mit.one(self.target_selection(keyword="n_ally_in_middle", keyword2="1"))
        def apply_taunt_effect(self: Character, target: Character):
            target.apply_effect(TauntEffect("Close River", 24, False, False, marked_character=character_marked))
        damage_dealt = self.attack(multiplier=2.6, repeat=1, target_kw1="n_enemy_in_front", target_kw2="3", func_after_dmg=apply_taunt_effect)
        return damage_dealt


    def skill2_logic(self):
        def damage_amplify(self: Character, target, final_damage):
            self.update_ally_and_enemy()
            diff = len(self.enemyparty) - len(self.enemy)
            if diff > 0:
                final_damage *= 1 + (0.3 * diff)
            return final_damage
        damage_dealt = self.attack(multiplier=2.0, repeat=7, func_damage_step=damage_amplify)
        return damage_dealt


    def skill3(self):
        pass

    def battle_entry_effects(self):
        requirement_func = lambda charac, attacker: not charac.have_taken_action
        dm = ReductionShield("Distant Mountain", -1, True, 0.5, False, cover_status_damage=True, cover_normal_damage=True,
                             requirement=requirement_func,
                             requirement_description="Before taken action in battle.",
                             requirement_description_jp="戦闘中に行動をした前。")
        dm.can_be_removed_by_skill = False
        self.apply_effect(dm)


class Heracles(Character):
    """
    Benefit from having high main stats
    Safe attacker
    Build: 
    """
    def __init__(self, name, lvl, exp=0, equip=None, image=None):
        super().__init__(name, lvl, exp, equip, image)
        self.name = "Heracles"
        self.skill1_description = "Attack 3 closest enemies 4 times with 150% atk, defense, spd and maxhp / 20." \
        " Multiplier increases by 30% for each lost ally."
        self.skill2_description = "Remove 3 debuffs on yourself, apply Regeneration and Protection on yourself for 20 turns," \
        " Regeneration: Recover hp by level * 5 each turn. Protection: When taking normal damage and damage exceed 10% of max hp," \
        " The part of damage that exceed 10% of max hp is reduced by 40%. Both effect refreshs duration when applied again."
        self.skill3_description = "Apply Divine Power and on yourself. Divine Power: Before taking damage, if damage exceed 10% of max hp," \
        " recover 8% of max hp. At start of battle, select your lowest main stats, 25% of the selected stats is added" \
        " to all other main stats. Main stats include atk, def, spd and maxhp. Maxhp is devided by 20 during calculation."
        # 授かれし神力
        self.skill1_description_jp = "最も近い3人の敵に、攻撃力、防御力、速度、最大HPの1/20に基づいて150%の攻撃を4回行う。倒れた味方1人ごとに、倍率が30%増加する。"
        self.skill2_description_jp = "自身のデバフを3つ解除し、20ターンの間、自身に「再生」と「保護」を付与する。再生：各ターン、レベル×5のHPを回復する。保護：通常ダメージを受けた時、そのダメージが最大HPの10%を超える場合、超過分のダメージが40%減少する。両方の効果は再度適用された際に持続時間が更新される。"
        self.skill3_description_jp = "自身に「授かれし神力」を付与する。授かれし神力：ダメージを受ける前に、ダメージが最大HPの10%を超える場合、最大HPの8%を回復する。戦闘開始時に、最も低い主要ステータスを選択し、その25%が他の全ての主要ステータスに加算される。主要ステータスには攻撃力、防御力、速度、最大HPが含まれる。最大HPは計算時に1/20に分割される。"
        self.skill1_cooldown_max = 4
        self.skill2_cooldown_max = 4


    def skill1_logic(self):
        a1, a2, a3, a4 = 0, 0, 0, 0
        mp_base = 1.5
        mp = mp_base + (0.3 * (len(self.party) - len(self.ally)))
        mp = max(mp, 1.0)
        a1 = self.attack(multiplier=1.5, repeat=1, target_kw1="n_enemy_in_front", target_kw2="3")
        if self.is_alive():
            a2 = self.attack(multiplier=1.5, repeat=1, target_kw1="n_enemy_in_front", target_kw2="3", damage_is_based_on="defense")
        if self.is_alive():
            a3 = self.attack(multiplier=1.5, repeat=1, target_kw1="n_enemy_in_front", target_kw2="3", damage_is_based_on="spd")
        if self.is_alive():
            a4 = self.attack(multiplier=1.5 / 20, repeat=1, target_kw1="n_enemy_in_front", target_kw2="3", damage_is_based_on="maxhp")
        return a1 + a2 + a3 + a4


    def skill2_logic(self):
        self.remove_random_amount_of_debuffs(3)
        if self.is_alive():
            def heal_func(char, effect_applier):
                return char.lvl * 5
            regen = ContinuousHealEffect("Regeneration", 20, True, value_function=heal_func, buff_applier=self,
                                         value_function_description="level * 5", value_function_description_jp="レベル×5")
            regen.additional_name = "Heracles_Regeneration"
            regen.apply_rule = "stack"
            self.apply_effect(regen)
            protection = EffectShield2("Protection", 20, True, cc_immunity=False, damage_reduction=0.4, shrink_rate=0,
                                       hp_threshold=0.1)
            protection.additional_name = "Heracles_Protection"
            protection.apply_rule = "stack"
            self.apply_effect(protection)



    def skill3(self):
        pass

    def battle_entry_effects(self):
        dp1 = EffectShield2_HealonDamage("Divine Power", -1, True, False, 0.1, self, heal_with_self_maxhp_percentage=0.08)
        dp1.can_be_removed_by_skill = False
        self.apply_effect(dp1)

        the_stat_dict = {"atk": self.atk, "defense": self.defense, "spd": self.spd, "maxhp": int(self.maxhp / 20)}
        selected_stat = min(the_stat_dict, key=the_stat_dict.get)
        v = 0
        m = 0.25
        dp2 = None
        if selected_stat == "atk":
            v = self.atk * m
            dp2 = StatsEffect("Divine Power", -1, True, main_stats_additive_dict={"atk": v, "defense": v, "spd": v, "maxhp": int(v*20)})
        elif selected_stat == "defense":
            v = self.defense * m
            dp2 = StatsEffect("Divine Power", -1, True, main_stats_additive_dict={"atk": v, "defense": v, "spd": v, "maxhp": int(v*20)})
        elif selected_stat == "spd":
            v = self.spd * m
            dp2 = StatsEffect("Divine Power", -1, True, main_stats_additive_dict={"atk": v, "defense": v, "spd": v, "maxhp": int(v*20)})
        elif selected_stat == "maxhp":
            v = self.maxhp * m
            dp2 = StatsEffect("Divine Power", -1, True, main_stats_additive_dict={"atk": v/20, "defense": v/20, "spd": v/20, "maxhp": int(v)})
        dp2.can_be_removed_by_skill = False
        self.apply_effect(dp2)


class Sunny(Character):
    """
    Burn support
    Build: 
    """
    def __init__(self, name, lvl, exp=0, equip=None, image=None):
        super().__init__(name, lvl, exp, equip, image)
        self.name = "Sunny"
        self.skill1_description = "Attack random enemy 4 times with 160% atk, inflict Burn for 20 turns," \
        " Burn deals 25% of atk status damage each turn."
        self.skill2_description = "Attack enemy of lowest hp with 300% atk, inflict another Burn effect for 20 turns if target" \
        " already has Burn effect and inflict Weaken for 20 turns, Weaken reduce atk and def by 30%. If target has more than" \
        " 3 Burn effects, stats reduction is increased to 60%."
        self.skill3_description = "After using a skill, apply Summer Breeze on 2 allies of lowest hp for 10 turns." \
        " Summer Breeze: Recover hp by 20% of your atk each turn, defense and critdef increased by 15%."
        # 薫風
        self.skill1_description_jp = "ランダムな敵に攻撃力の160%で4回攻撃し、20ターンの間「燃焼」を付与する。燃焼は毎ターン攻撃力の30%分の状態異常ダメージを与える。"
        self.skill2_description_jp = "HPが最も低い敵に攻撃力の300%で攻撃し、対象に既に「燃焼」効果がある場合、さらに20ターンの間「燃焼」を付与し、20ターンの間「弱化」を付与する。弱化は攻撃力と防御力を30%減少させる。対象に3つ以上の火傷効果がある場合、ステータス減少は60%になる。"
        self.skill3_description_jp = "スキル使用後、HPが最も低い2人の味方に10ターンの間「薫風」を付与する。薫風：毎ターン攻撃力の20%分のHPを回復し、防御力とクリティカル防御が15%増加する。"
        self.skill1_cooldown_max = 4
        self.skill2_cooldown_max = 4


    def skill1_logic(self):
        def burn_effect(self, target: Character):
            target.apply_effect(ContinuousDamageEffect("Burn", 20, False, 0.25 * self.atk, self))
        damage_dealt = self.attack(multiplier=1.6, repeat=4, func_after_dmg=burn_effect)
        if self.is_alive():
            def heal_func(char, buff_applier):
                return buff_applier.atk * 0.2
            self.update_ally_and_enemy()
            ally_selection = list(self.target_selection(keyword="n_lowest_attr", keyword2="2", keyword3="hp", keyword4="ally"))
            for a in ally_selection:
                summer_breeze = ContinuousHealEffect("Summer Breeze", 10, True, value_function=heal_func, buff_applier=self,
                                                value_function_description="20% of Sunny atk", value_function_description_jp="20%Sunnyの攻撃力")
                summer_breeze_part2 = StatsEffect("Summer Breeze", 10, True, {"defense": 1.15, "critdef": 1.15})
                a.apply_effect(summer_breeze)
                a.apply_effect(summer_breeze_part2)
        return damage_dealt

    def skill2_logic(self):
        def negative_effect(self, target: Character):
            burns = target.get_all_effect_that_named("Burn")
            how_many = len(burns)
            if how_many > 3:
                target.apply_effect(ContinuousDamageEffect("Burn", 20, False, 0.25 * self.atk, self))
                weak = StatsEffect("Weaken", 20, False, {"atk": 0.4, "defense": 0.4})
                target.apply_effect(weak)
            elif how_many > 0:
                target.apply_effect(ContinuousDamageEffect("Burn", 20, False, 0.25 * self.atk, self))
                weak = StatsEffect("Weaken", 20, False, {"atk": 0.7, "defense": 0.7})
                target.apply_effect(weak)
        damage_dealt = self.attack(multiplier=3.0, repeat=1, target_kw1="n_lowest_attr", target_kw2="1", target_kw3="hp", target_kw4="enemy",
                                      func_after_dmg=negative_effect)
        if self.is_alive():
            def heal_func(char, buff_applier):
                return buff_applier.atk * 0.2
            ally_selection = list(self.target_selection(keyword="n_lowest_attr", keyword2="2", keyword3="hp", keyword4="ally"))
            for a in ally_selection:
                summer_breeze = ContinuousHealEffect("Summer Breeze", 10, True, value_function=heal_func, buff_applier=self,
                                                    value_function_description="20% of Sunny atk", value_function_description_jp="20%Sunnyの攻撃力")
                summer_breeze_part2 = StatsEffect("Summer Breeze", 10, True, {"defense": 1.15, "critdef": 1.15})
                a.apply_effect(summer_breeze)
                a.apply_effect(summer_breeze_part2)
        return damage_dealt


    def skill3(self):
        pass


class Sasaki(Character):
    # NOTE: Lester is a support for this character
    """
    Hp recovery based on damage dealt.
    Build: 
    """
    def __init__(self, name, lvl, exp=0, equip=None, image=None):
        super().__init__(name, lvl, exp, equip, image)
        self.name = "Sasaki"
        self.skill1_description = "Attack 1 closest enemy with 600% atk and recover hp by 100% of damage dealt."
        self.skill2_description = "Attack enemy of lowest defense with 260% atk 3 times, recover hp by 100% of damage dealt. Remove 1 active buff on the target." \
        " for each attack."
        self.skill3_description = "Normal attack recover hp by 100% of damage dealt."
        self.skill1_description_jp = "最も近い敵1体に攻撃力の600%で攻撃し、与えたダメージの100%分HPを治療する。"
        self.skill2_description_jp = "防御力が最も低い敵に攻撃力の260%で3回攻撃し、与えたダメージの100%分HPを治療する。各攻撃ごとに、対象のアクティブなバフを1つ解除する。"
        self.skill3_description_jp = "通常攻撃で与えたダメージの100%分HPを治療する。"
        self.skill1_cooldown_max = 3
        self.skill2_cooldown_max = 3


    def skill1_logic(self):
        damage_dealt = self.attack(multiplier=6.0, repeat=1, target_kw1="n_enemy_in_front", target_kw2="1")
        if self.is_alive():
            self.heal(target_kw1="yourself", value=damage_dealt)
        return damage_dealt


    def skill2_logic(self):
        def remove_buff(self, target: Character):
            target.remove_random_amount_of_buffs(1, allow_infinite_duration=False)
        damage_dealt = self.attack(multiplier=2.60, repeat=3, target_kw1="n_lowest_attr", target_kw2="1", target_kw3="defense", target_kw4="enemy",
                                      func_after_dmg=remove_buff)   
        if self.is_alive():
            self.heal(target_kw1="yourself", value=damage_dealt)
        return damage_dealt



    def skill3(self):
        pass

    def normal_attack(self):
        d = self.attack()
        if self.is_alive():
            self.heal(target_kw1="yourself", value=d)
        return d


class Zed(Character):
    """
    Target high defense, burst buff
    Build: 
    """
    def __init__(self, name, lvl, exp=0, equip=None, image=None):
        super().__init__(name, lvl, exp, equip, image)
        self.name = "Zed"
        self.skill1_description = "For 1 turn, increase penetration by 30%, attack enemy of highest defense with 250% atk 3 times." \
        " Each attack inflict Defense Break and Burn for 20 turns, Defense Break reduce defense by 15%, Burn deals 10% of atk status damage each turn."
        self.skill2_description = "For 1 turn, increase atk by 30%, attack enemy of highest defense with 180% atk 6 times." \
        " If this attack does not take down the enemy, attack again, dealing fixed damage equal to 100% of target defense."
        self.skill3_description = "When attacking enemy and the enemy have their defense more than 200% of your attack," \
        " for 1 turn, increase atk by 30% and penetration by 30%."
        self.skill1_description_jp = "1ターンの間、貫通力を30%増加させ、防御力が最も高い敵に攻撃力の250%で3回攻撃する。各攻撃で20ターンの間「防御ダウン」と「燃焼」を付与する。防御ダウンは防御力を15%減少させ、燃焼は毎ターン攻撃力の10%分の状態異常ダメージを与える。"
        self.skill2_description_jp = "1ターンの間、攻撃力を30%増加させ、防御力が最も高い敵に攻撃力の180%で6回攻撃する。この攻撃で敵を倒せなかった場合、追加で対象の防御力の100%に相当する固定ダメージを与える。"
        self.skill3_description_jp = "敵を攻撃する際、敵の防御力が自分の攻撃力の200%以上の場合、1ターンの間、攻撃力を30%と貫通力を30%増加させる。"
        self.skill1_cooldown_max = 4
        self.skill2_cooldown_max = 4


    def skill1_logic(self):
        t = mit.one(self.target_selection(keyword="n_highest_attr", keyword2="1", keyword3="defense", keyword4="enemy"))
        if t.defense > self.atk * 2:
            self.apply_effect(StatsEffect("Escape", 1, True, {"atk": 1.3, "penetration": 0.3}))
        self.apply_effect(StatsEffect("Advisory", 1, True, {"penetration": 0.3}))
        def apply_effect(self, target: Character):
            target.apply_effect(StatsEffect("Defense Break", 20, False, {"defense": 0.85}))
            target.apply_effect(ContinuousDamageEffect("Burn", 20, False, 0.10 * self.atk, self))
        damage_dealt = self.attack(multiplier=2.5, repeat=3, target_list=[t], func_after_dmg=apply_effect)
        return damage_dealt


    def skill2_logic(self):
        t = mit.one(self.target_selection(keyword="n_highest_attr", keyword2="1", keyword3="defense", keyword4="enemy"))
        if t.defense > self.atk * 2:
            self.apply_effect(StatsEffect("Escape", 1, True, {"atk": 1.3, "penetration": 0.3}))
        self.apply_effect(StatsEffect("Advisory", 1, True, {"atk": 1.3}))
        damage_dealt = self.attack(multiplier=1.8, repeat=6, target_list=[t])
        if t.is_alive() and self.is_alive():
            damage_dealt += self.attack(multiplier=1.0, repeat=1, target_list=[t], force_dmg=t.defense)
        return damage_dealt


    def skill3(self):
        pass


class ZedAN(Character):
    """
    午後 Version of Zed
    Target high defense, burst buff
    Build: 
    """
    def __init__(self, name, lvl, exp=0, equip=None, image=None):
        super().__init__(name, lvl, exp, equip, image)
        self.name = "ZedAN"
        self.skill1_description = "For 1 turn, atk is increased by 30%, attack enemy of highest defense with 300% atk 3 times." \
        " If your atk is higher than target defense, damage is increased by 100%, if your atk is 2 times higher than target defense," \
        " damage is increased by 200%."
        self.skill2_description = "For 1 turn, penetration is increased by 30%, attack enemy of highest defense with 200% atk 6 times." \
        " If this attack takes down the enemy, apply Flowers of the Four Seasons on you and 2 neighbor allies for 20 turns," \
        " Flowers of the Four Seasons: Recover hp by 100% of your atk each turn, increase atk, crit, critdmg and penetration by 20%."
        self.skill3_description = "When attacking an enemy of higher defense than your atk with normal attack," \
        " apply Afternoon Sunshine on yourself for 20 turns. Afternoon Sunshine: Penetration is increased by 5%." \
        " Normal attack prioritize enemy of highest defense."
        self.skill1_description_jp = "1ターンの間、攻撃力が30%増加し、防御力が最も高い敵に攻撃力の300%で3回攻撃する。自分の攻撃力が対象の防御力より高い場合、ダメージが100%増加し、攻撃力が対象の防御力の2倍以上の場合、ダメージが200%増加する。"
        self.skill2_description_jp = "1ターンの間、貫通力が30%増加し、防御力が最も高い敵に攻撃力の200%で6回攻撃する。この攻撃で敵を倒した場合、自身と隣接する2人の味方に20ターンの間「四季の花」を付与する。四季の花：毎ターン、自分の攻撃力の100%分のHPを回復し、攻撃力、クリティカル率、クリティカルダメージ、貫通力が20%増加する。"
        self.skill3_description_jp = "通常攻撃で自分の攻撃力を上回る防御力を持つ敵を攻撃した場合、自身に20ターンの間「午後の日差し」を付与する。午後の日差し：貫通力が5%増加する。通常攻撃は防御力が最も高い敵を優先する。"
        self.skill1_cooldown_max = 4
        self.skill2_cooldown_max = 4


    def skill1_logic(self):
        self.apply_effect(StatsEffect("Advisory", 1, True, {"atk": 1.3}))
        def dmg_amplify(self, target, final_damage):
            if self.atk > target.defense:
                final_damage *= 2.0
            elif self.atk > target.defense * 2:
                final_damage *= 3.0
            return final_damage
        damage_dealt = self.attack(multiplier=3.0, repeat=3, target_kw1="n_highest_attr", target_kw2="1", target_kw3="defense", target_kw4="enemy",
                                   func_damage_step=dmg_amplify)
        return damage_dealt


    def skill2_logic(self):
        def after_damage(self: Character, target: Character):
            if target.is_dead():
                def heal_func(char, effect_applier):
                    return effect_applier.atk
                neighbors = self.get_neighbor_allies_including_self()
                for n in neighbors:
                    flowers_part1 = ContinuousHealEffect("Flowers of the Four Seasons", 20, True, value_function=heal_func, buff_applier=self,
                                                value_function_description="100% of ZedAN atk", value_function_description_jp="ZedANの攻撃力の100%")
                    flowers_part2 = StatsEffect("Flowers of the Four Seasons", 20, True, {"atk": 1.2, "crit": 0.2, "critdmg": 0.2, "penetration": 0.2})
                    n.apply_effect(flowers_part1)
                    n.apply_effect(flowers_part2)
        damage_dealt = self.attack(multiplier=2.0, repeat=6, target_kw1="n_highest_attr", target_kw2="1", target_kw3="defense", target_kw4="enemy",
                                   func_after_dmg=after_damage)
        return damage_dealt

    def skill3(self):
        pass

    def normal_attack(self):
        def after_dmg(self, target):
            if target.defense > self.atk:
                self.apply_effect(StatsEffect("Afternoon Sunshine", 20, True, {"penetration": 0.05}))
        damage_dealt = self.attack(target_kw1="n_highest_attr", target_kw2="1", target_kw3="defense", target_kw4="enemy", func_after_dmg=after_dmg)
        return damage_dealt


class Lu(Character):
    """
    Negate skill
    Build: 
    """
    def __init__(self, name, lvl, exp=0, equip=None, image=None):
        super().__init__(name, lvl, exp, equip, image)
        self.name = "Lu"
        self.skill1_description = "Heal one ally of highest atk with 400% of your highest main stats except maxhp," \
        " remove 2 debuffs and apply Regeneration for 15 turns on that ally. Regeneration: Recover hp by 100% of your highest main stats except maxhp each turn." 
        self.skill2_description = "Apply Big Bear on all allies for 20 turns, Big Bear absorbs damage equal to 500% of your" \
        " highest main stats except maxhp. When applied on yourself, the absorption value is increased by 100%."
        self.skill3_description = "Attack start of battle, apply Flapping Sound on the closest enemy," \
        " when the affected enemy takes action and a skill can be used, for 1 turn, silence the enemy by paying hp equal to 100 * level." \
        " Paying hp treats as taking status damage. If you are defeated, the effect on the enemy is removed." 
        # 羽ばたく音
        self.skill1_description_jp = "攻撃力が最も高い味方1人のHPを、自身の最大HPを除く主要ステータスのうち最も高い値の400%分治療し、デバフを2つ解除して、その味方に15ターンの間「再生」を付与する。再生：毎ターン、自身の最大HPを除く最も高い主要ステータスの100%分のHPを回復する。"
        self.skill2_description_jp = "全ての味方に20ターンの間「ビッグベア」を付与する。ビッグベアは、自身の最大HPを除く最も高い主要ステータスの500%分のダメージを吸収する。自分に付与した場合、吸収量が100%増加する。"
        self.skill3_description_jp = "戦闘開始時、最も近い敵に「羽ばたく音」を付与する。この効果を受けた敵が行動を起こし、スキルが使用可能な場合、その敵を1ターンの間「沈黙」させ、自分が100×レベル分のHPを支払われる。HPの支払いは状態異常ダメージとして扱われる。自分が倒された場合、敵にかかっている効果は解除される。"
        self.skill1_cooldown_max = 3
        self.skill2_cooldown_max = 3


    def skill1_logic(self):
        ally = mit.one(self.target_selection(keyword="n_highest_attr", keyword2="1", keyword3="atk", keyword4="ally"))
        heal_value = max(self.atk, self.defense, self.spd)
        self.heal(value=heal_value * 4.00, target_list=[ally])
        if ally.is_alive():
            ally.remove_random_amount_of_debuffs(2)
            def heal_func(char, buff_applier):
                heal_value = max(buff_applier.atk, buff_applier.defense, buff_applier.spd)
                return heal_value * 1.00
            regen = ContinuousHealEffect("Regeneration", 15, True, value_function=heal_func, buff_applier=self,
                                        value_function_description="50% of Lu's highest main stats except maxhp",
                                        value_function_description_jp="Luの最高主要ステータスの50%")
            ally.apply_effect(regen)
        return 0


    def skill2_logic(self):
        for a in self.ally:
            big_bear_value = max(self.atk, self.defense, self.spd) * 5.00
            if a is self:
                big_bear_value *= 2.00
            big_bear = AbsorptionShield("Big Bear", 20, True, big_bear_value, False)
            a.apply_effect(big_bear)


    def skill3(self):
        pass


    def battle_entry_effects(self):
        t = mit.one(self.target_selection(keyword="n_enemy_in_front", keyword2="1"))
        t.apply_effect(LuFlappingSoundEffect("Flapping Sound", -1, False, self, hp_cost=100 * self.lvl))


class Ulric(Character):
    """
    Cloud eq set support 
    Build: 
    """
    def __init__(self, name, lvl, exp=0, equip=None, image=None):
        super().__init__(name, lvl, exp, equip, image)
        self.name = "Ulric"
        self.skill1_description = "Attack 3 closest enemies with 260% atk, 50% chance to apply Bind for 20 turns." \
        " Bind: all main stats except maxhp are reduced by 10%. Heal all allies by 30% of damage dealt."
        self.skill2_description = "Select 2 allies of highest atk, apply Full Cloud for the allies for 2 turns." \
        " Full Cloud: Speed is increased by 12%, final damage taken is reduced by 7%."
        self.skill3_description = "At start of battle, apply unremovable In Cloud for all allies. In Cloud: Speed is increased by 5%, final damage taken is reduced by 3%." \
        " At end of turn, if Full Cloud effect is applied while you have this effect, Full Cloud duration is" \
        " increased by 10 turns, and can no longer be removed by skill." 
        self.skill1_description_jp = "最も近い3人の敵に攻撃力の260%で攻撃し、50%確率で20ターンの間「束縛」を付与する。束縛：最大HPを除く全ての主要ステータスが10%減少する。与えたダメージの30%分、全ての味方を治療する。"
        self.skill2_description_jp = "攻撃力が最も高い味方2人を選択し、2ターンの間「雲満」を付与する。雲満：速度が12%増加し、最終ダメージ倍率が7%減少する。"
        self.skill3_description_jp = "戦闘開始時、全ての味方に解除不能な「雲中」を付与する。雲中：速度が5%増加し、最終ダメージ倍率が3%減少する。ターン終了時、自分にこの効果がある状態で「雲満」効果が適用されている場合、雲満の持続時間が10ターン延長され、スキルで解除できなくなる。"
        self.skill1_cooldown_max = 4
        self.skill2_cooldown_max = 4


    def skill1_logic(self):
        def bind_effect(self, target: Character):
            if random.random() < 0.50:
                target.apply_effect(StatsEffect("Bind", 20, False, {"atk": 0.90, "defense": 0.90, "spd": 0.90}))
        damage_dealt = self.attack(multiplier=2.6, repeat=1, target_kw1="n_enemy_in_front", target_kw2="3", func_after_dmg=bind_effect)
        self.update_ally_and_enemy()
        if self.is_alive():
            self.heal(value=damage_dealt * 0.30, target_kw1="all_ally")
        return damage_dealt

    def skill2_logic(self):
        ally = list(self.target_selection(keyword="n_highest_attr", keyword2="2", keyword3="atk", keyword4="ally"))
        for a in ally:
            a.apply_effect(StatsEffect("Full Cloud", 2, True, {"spd": 1.12, "final_damage_taken_multipler": -0.07}))
        return 0

    def skill3(self):
        pass

    def battle_entry_effects(self):
        # other effects in description is implemented in the effect class
        for a in self.ally:
            in_cloud = UlricInCloudEffect("In Cloud", -1, True, {"spd": 1.05, "final_damage_taken_multipler": -0.03})
            in_cloud.can_be_removed_by_skill = False
            in_cloud.additional_name = "Ulric_In_Cloud"
            a.apply_effect(in_cloud)


class Xunmu(Character):
    """
    Maxhp buff
    Build: 
    """
    def __init__(self, name, lvl, exp=0, equip=None, image=None):
        super().__init__(name, lvl, exp, equip, image)
        self.name = "Xunmu"
        self.skill1_description = "Attack all enemies with 150% atk, 100% chance to inflict Burn for 20 turns." \
        " Burn deals 15% of atk status damage each turn."
        self.skill2_description = "Apply Regeneration for 12 turns for nearby allies including yourself." \
        " Regeneration: Recover hp by 4% of their lost hp each turn."
        self.skill3_description = "Initial Maxhp is increased by 40%. At start of battle, 2 nearby allies have their maxhp increased by 40%" \
        " of your maxhp and their hp is set to 100% of their maxhp. This effect cannot be removed by skill." 
        self.skill1_description_jp = "全ての敵に攻撃力の150%で攻撃し、100%の確率で20ターンの間「燃焼」を付与する。燃焼は毎ターン攻撃力の15%分の状態異常ダメージを与える。"
        self.skill2_description_jp = "自分を含む近くの味方に12ターンの間「再生」を付与する。再生：毎ターン、失ったHPの4%分を回復する。"
        self.skill3_description_jp = "初期最大HPが40%増加する。戦闘開始時、近くの味方2人の最大HPが自分の最大HPの40%増加し、HPが最大HPの100%に設定される。この効果はスキルで解除されない。"
        self.skill1_cooldown_max = 4
        self.skill2_cooldown_max = 4


    def skill1_logic(self):
        def burn_effect(self, target: Character):
            target.apply_effect(ContinuousDamageEffect("Burn", 20, False, 0.15 * self.atk, self))
        damage_dealt = self.attack(multiplier=1.5, repeat=1, target_kw1="all_enemy", func_after_dmg=burn_effect)
        return damage_dealt

    def skill2_logic(self):
        self.update_ally_and_enemy()
        for a in self.get_neighbor_allies_including_self():
            def value_func(char, effect_applier):
                return (char.maxhp - char.hp) * 0.04
            regen = ContinuousHealEffect("Regeneration", 12, True, value_function=value_func, buff_applier=self,
                                         value_function_description="4% of lost hp", value_function_description_jp="失ったHPの4%")
            a.apply_effect(regen)
        return 0

    def skill3(self):
        pass

    def battle_entry_effects(self):
        self.maxhp *= 1.4
        self.maxhp = int(self.maxhp)
        self.hp = self.maxhp
        for a in self.get_neighbor_allies_not_including_self():
            a.apply_effect(StatsEffect("Milk", -1, True, main_stats_additive_dict={"maxhp": int(self.maxhp * 0.4)}, can_be_removed_by_skill=False))
            a.hp = a.maxhp


class XunmuAL(Character):
    """
    Build: 
    """
    def __init__(self, name, lvl, exp=0, equip=None, image=None):
        super().__init__(name, lvl, exp, equip, image)
        self.name = "XunmuAL"
        self.skill1_description = "Attack 3 closest enemies with 240% atk and apply Freeze for 10 turns." \
        " If target has Burn, deal 100% additional damage."
        self.skill2_description = "Apply Regeneration for 12 turns for nearby allies including yourself." \
        " Regeneration: Recover hp by 4% of their lost hp each turn."
        self.skill3_description = "At start of battle, target neighbor ally of lower atk and apply Fine Milk," \
        " Fine Milk: Maxhp is increased by 60% of your maxhp, hp is set to 100% of maxhp. Atk, crit, critdmg is increased by 30% of heal efficiency" \
        " if heal efficiency is above 150%."
        self.skill1_description_jp = "最も近い3人の敵に攻撃力の240%で攻撃し、10ターンの間「凍結」を付与する。対象が「燃焼」状態の場合、追加で100%のダメージを与える。"
        self.skill2_description_jp = "自分を含む隣接する味方に12ターンの間「再生」を付与する。再生：毎ターン、失ったHPの4%分を回復する。"
        self.skill3_description_jp = "戦闘開始時、自分より攻撃力が低い隣接する味方1人に「極上ミルク」を付与する。極上ミルク：最大HPが自身の最大HPの60%分増加し、HPが最大HPの100%に設定される。回復効率が150%以上の場合、攻撃力、クリティカル率、クリティカルダメージが回復効率の30%分増加する。"
        self.skill1_cooldown_max = 5
        self.skill2_cooldown_max = 5


    def skill1_logic(self):
        def freeze_effect(self, target: Character):
            target.apply_effect(FrozenEffect("Freeze", 10, False, self))
        def additional_dmg(self, target: Character, final_damage):
            if target.has_effect_that_named("Burn"):
                final_damage *= 2.0
            return final_damage
        damage_dealt = self.attack(multiplier=2.4, repeat=1, target_kw1="n_enemy_in_front", target_kw2="3", func_after_dmg=freeze_effect,
                                    func_damage_step=additional_dmg)
        return damage_dealt

    def skill2_logic(self):
        self.update_ally_and_enemy()
        for a in self.get_neighbor_allies_including_self():
            def value_func(char, effect_applier):
                return (char.maxhp - char.hp) * 0.04
            regen = ContinuousHealEffect("Regeneration", 12, True, value_function=value_func, buff_applier=self,
                                            value_function_description="4% of lost hp", value_function_description_jp="失ったHPの4%")
            a.apply_effect(regen)
        return 0

    def skill3(self):
        pass

    def battle_entry_effects(self):
        ally_loweratk = min(self.get_neighbor_allies_not_including_self(), key=lambda x: x.atk)
        if ally_loweratk.heal_efficiency > 1.50:
            scale_value = ally_loweratk.heal_efficiency * 0.30
            fine_milk = StatsEffect("Fine Milk", -1, True, {"atk": 1 + scale_value, "crit": scale_value, "critdmg": scale_value},
                                    main_stats_additive_dict={"maxhp": int(self.maxhp * 0.6)}, can_be_removed_by_skill=False)
        else:
            fine_milk = StatsEffect("Fine Milk", -1, True, main_stats_additive_dict={"maxhp": int(self.maxhp * 0.6)}, can_be_removed_by_skill=False)
        ally_loweratk.apply_effect(fine_milk)



class Xunyu(Character):
    """
    Buff support, good against multi strike
    Build: speed, maybe
    """
    def __init__(self, name, lvl, exp=0, equip=None, image=None):
        super().__init__(name, lvl, exp, equip, image)
        self.name = "Xunyu"
        self.skill1_description = "Apply Chord Mixing on all allies for 18 turns, Chord Mixing: All main stats except maxhp are increased by 10%," \
        " crit and critdmg are increased by 10%."
        self.skill2_description = "Apply Wide Range Sound on all allies for 18 turns. Wide Range Sound: Damage taken is reduced by 20%," \
        " damage taken from the same turn is further reduced by 20%."
        self.skill3_description = "When applying effect on a ally who does not have protected effect, effect value is doubled."
        # 音色模倣 広い音域 
        self.skill1_description_jp = "全ての味方に20ターンの間「音色模倣」を付与する。音色模倣：最大HPを除く全ての主要ステータスが10%増加し、クリティカル率とクリティカルダメージが10%増加する。"
        self.skill2_description_jp = "全ての味方に20ターンの間「広い音域」を付与する。広い音域：受けるダメージが20%減少し、同じターン内で受けるダメージがさらに20%減少する。"
        self.skill3_description_jp = "守護効果を持たない味方に効果を適用する際、その効果値が2倍になる。"
        self.skill1_cooldown_max = 4
        self.skill2_cooldown_max = 4

    def skill1_logic(self):
        for a in self.ally:
            chord_mixing_p1 = StatsEffect("Chord Mixing", 18, True, {"atk": 1.10, "defense": 1.10, "spd": 1.10, "crit": 0.10, "critdmg": 0.10})
            if not a.is_protected():
                chord_mixing_p1 = StatsEffect("Chord Mixing", 18, True, {"atk": 1.20, "defense": 1.20, "spd": 1.20, "crit": 0.20, "critdmg": 0.20})
            a.apply_effect(chord_mixing_p1)
        return 0

    def skill2_logic(self):
        for a in self.ally:
            wrs = AntiMultiStrikeReductionShield("Wide Range Sound", 18, True, 0.20, False)
            if not a.is_protected():
                wrs = AntiMultiStrikeReductionShield("Wide Range Sound", 18, True, 0.40, False)
            a.apply_effect(wrs)
        return 0

    def skill3(self):
        pass


class Clarence(Character):
    """

    Build: 
    """
    def __init__(self, name, lvl, exp=0, equip=None, image=None):
        super().__init__(name, lvl, exp, equip, image)
        self.name = "Clarence"
        self.skill1_description = "Attack all enemies with 500% atk, enemy in the middle takes 100% damage, damage reduced by 50%" \
        " for each position away from the middle. If their hp falls below 10% after this attack, they take bypass damage equal to 100% of their current hp."
        self.skill2_description = "Consume all stars to attack random enemies, the first 5 stars deals 200% atk normal damage," \
        " the next 5 stars deals 100% atk status damage, the last 5 stars deals 100% atk bypass damage."
        self.skill3_description = "Start the battle with 5 stacks of Stars, after taking normal damage, consume 1 stack of Stars to reduce damage taken by 20%." \
        " After using a skill, gain 5 stacks of Stars."
        self.skill1_description_jp = "全ての敵に攻撃力の500%で攻撃し、中央の敵は100%のダメージを受ける。中央から離れるごとにダメージが50%減少する。この攻撃の後、敵のHPが10%以下になった場合、現在のHPの100%分の状態異常無視ダメージを受ける。"
        self.skill2_description_jp = "全ての星を消費してランダムな敵に攻撃する。最初の5つは攻撃力の200%の通常ダメージを与え、次の5つは攻撃力の100%の状態異常ダメージを与え、最後の5つは攻撃力の100%の状態異常無視ダメージを与える。"
        self.skill3_description_jp = "戦闘開始時に5スタックの星を持つ。通常ダメージを受けた後、スターを1スタック消費して受けるダメージを20%減少させる。スキルを使用すると、5つの星を獲得する。"
        self.skill1_cooldown_max = 4
        self.skill2_cooldown_max = 4

    def skill1_logic(self):
        def damage_reduction(self, target: Character, final_damage):
            if target.is_middle():
                return final_damage
            else:
                distance = target.get_distance_to_middle()
                return final_damage * (0.50 ** distance)
        def after_dmg(self, target: Character):
            if target.is_alive() and target.hp < target.maxhp * 0.10:
                target.take_bypass_status_effect_damage(target.hp, self)
        damage_dealt = self.attack(multiplier=5.0, repeat=1, target_kw1="all_enemy", func_damage_step=damage_reduction, func_after_dmg=after_dmg)
        self.clarence_gain_stars(5)
        return damage_dealt

    def skill2_logic(self):
        stars = self.get_effect_that_named("Stars", "Clarence_Stars")
        stars_available = max(stars.stacks, 0)
        damage_dealt = 0
        if stars_available:
            if 0 < stars_available <= 5:
                damage_dealt = self.attack(multiplier=2.0, repeat=stars_available)
            elif 5 < stars_available <= 10:
                damage_dealt = self.attack(multiplier=2.0, repeat=5)
                self.update_ally_and_enemy()
                if self.is_alive() and self.enemy:
                    damage_dealt += self.attack(multiplier=1.0, repeat=stars_available - 5, damage_type="status")
            else:
                damage_dealt = self.attack(multiplier=2.0, repeat=5)
                self.update_ally_and_enemy()
                if self.is_alive() and self.enemy:
                    damage_dealt += self.attack(multiplier=1.0, repeat=5, damage_type="status")
                    self.update_ally_and_enemy()
                    if self.is_alive() and self.enemy:
                        damage_dealt += self.attack(multiplier=1.0, repeat=stars_available - 10, damage_type="bypass")
            stars.stacks = 0

        self.clarence_gain_stars(5)
        return damage_dealt

    def skill3(self):
        pass

    def battle_entry_effects(self):
        stars = Effect("Stars", -1, True, show_stacks=True, can_be_removed_by_skill=False)
        stars.additional_name = "Clarence_Stars"
        stars.stacks = 5
        self.apply_effect(stars)

    def take_damage_before_calculation(self, damage, attacker):
        stars = self.get_effect_that_named("Stars", "Clarence_Stars")
        if stars is not None and stars.stacks > 0:
            stars.stacks -= 1
            global_vars.turn_info_string += f"{self.name} consumed 1 stack of Stars to reduce damage taken by 20%.\n"
            return damage * 0.80
        return damage

    def clarence_gain_stars(self, amount):
        stars = self.get_effect_that_named("Stars", "Clarence_Stars")
        if stars is not None:
            stars.stacks += amount
            stars.stacks = min(stars.stacks, 15)


class Jingke(Character):
    """
    Poison and Burn, create protector(low damage redirect)
    Build: 
    """
    def __init__(self, name, lvl, exp=0, equip=None, image=None):
        super().__init__(name, lvl, exp, equip, image)
        self.name = "Jingke"
        self.skill1_description = "Attack enemy with highest hp with 500% atk, inflict Poison and Burn for 20 turns." \
        " Poison deals 1% of target hp status damage each turn, Burn deals 20% of atk status damage each turn."
        self.skill2_description = "Apply Black Cat on yourself for 20 turns, increase evasion and attack and critdmg by 40%, but accuracy is reduced by 40%." \
        " When same effect is applied, duration is refreshed."
        self.skill3_description = "At start of battle, target an ally on the left, if there are none, target right, apply Protected to the rest of" \
        " allies and target becomes protector. Protected: Damage taken is reduced by 30%, 40% of damage is taken by the protector instead."
        self.skill1_description_jp = "HPが最も高い敵に攻撃力の500%で攻撃し、20ターンの間「毒」と「燃焼」を付与する。毒は毎ターン、対象のHPの1%分の状態異常ダメージを与え、燃焼は毎ターン攻撃力の20%分の状態異常ダメージを与える。"
        self.skill2_description_jp = "自身に20ターンの間「黒猫」を付与し、回避率、攻撃力、クリティカルダメージを40%増加させるが、命中率が40%減少する。同じ効果が再度適用された場合、持続時間が更新される。"
        self.skill3_description_jp = "戦闘開始時、左側にいる味方を対象にし、いない場合は右側を対象にする。対象は守護者になり、残りの味方には「守護」を付与する。守護：受けるダメージが30%減少し、ダメージの40%は守護者が代わりに受ける。"
        self.skill1_cooldown_max = 4
        self.skill2_cooldown_max = 4

    def skill1_logic(self):
        def after_dmg(self, target: Character):
            target.apply_effect(ContinuousDamageEffect_Poison("Poison", 20, False, 0.01, imposter=self, base="hp"))
            target.apply_effect(ContinuousDamageEffect("Burn", 20, False, 0.20 * self.atk, self))
        damage_dealt = self.attack(multiplier=5.0, repeat=1, target_kw1="n_highest_attr", target_kw2="1", target_kw3="hp", 
                                                    target_kw4="enemy", func_after_dmg=after_dmg)
        return damage_dealt

    def skill2_logic(self):
        e = StatsEffect("Black Cat", 20, True, {"atk": 1.40, "eva": 0.40,  "critdmg": 0.40, "acc": -0.40})
        e.additional_name = "Jingke_Black_Cat"
        e.apply_rule = "stack"
        self.apply_effect(e)
        return 0

    def skill3(self):
        pass

    def battle_entry_effects(self):
        left = self.get_neighbor_ally_left()
        if left is None:
            left = self
        for a in self.ally:
            if a is not left:
                a.apply_effect(ProtectedEffect("Protected", -1, True, cc_immunity=False, protector=left,
                                               damage_after_reduction_multiplier=0.70, damage_redirect_percentage=0.40,
                                               can_be_removed_by_skill=False))


class Shuijing(Character):
    """
    Enemy take extra damage whenever takes damage.
    Build: 
    """
    def __init__(self, name, lvl, exp=0, equip=None, image=None):
        super().__init__(name, lvl, exp, equip, image)
        self.name = "Shuijing"
        self.skill1_description = "Attack all enemies with 300% atk and inflict Matsu for 20 turns." \
        " Matsu: When taking damage, take status damage equal to 20% of the damage taken."
        self.skill2_description = "Attack all enemies with 300% atk and inflict Tsuru for 20 turns." \
        " Tsuru: When taking status damage, take bypass damage equal to 20% of the status damage taken."
        self.skill3_description = "Normal attack cast 2 times, the second attack deals status damage."
        self.skill1_description_jp = "全ての敵に攻撃力の300%で攻撃し、20ターンの間「松」を付与する。松：ダメージを受けた際、受けたダメージの20%に相当する状態異常ダメージを受ける。"
        self.skill2_description_jp = "全ての敵に攻撃力の300%で攻撃し、20ターンの間「鶴」を付与する。鶴：状態異常ダメージを受けた際、受けた状態異常ダメージの20%に相当する状態異常無視ダメージを受ける。"
        self.skill3_description_jp = "通常攻撃を2回行い、2回目の攻撃は状態異常ダメージを与える。"
        self.skill1_cooldown_max = 4
        self.skill2_cooldown_max = 4

    def skill1_logic(self):
        def after_dmg(self, target: Character):
            def value_func(char, dmg, attacker, effect_applier):
                return dmg * 0.20
            target.apply_effect(StingEffect("Matsu", 20, False, 0, self, value_function_normal_damage_step=value_func))
        damage_dealt = self.attack(multiplier=3.0, repeat=1, target_kw1="all_enemy", func_after_dmg=after_dmg)
        return damage_dealt

    def skill2_logic(self):
        def after_dmg(self, target: Character):
            def value_func(char, dmg, attacker, effect_applier):
                return dmg * 0.20
            target.apply_effect(StingEffect("Tsuru", 20, False, 0, self, value_function_status_damage_step=value_func))
        damage_dealt = self.attack(multiplier=3.0, repeat=1, target_kw1="all_enemy", func_after_dmg=after_dmg)
        return damage_dealt

    def skill3(self):
        pass

    def normal_attack(self):
        damage_dealt = self.attack()
        self.update_ally_and_enemy()
        if self.is_alive() and self.enemy:
            damage_dealt += self.attack(damage_type="status")
        return damage_dealt


class ShuijingAL(Character):
    """
    Support 
    Build: 
    """
    def __init__(self, name, lvl, exp=0, equip=None, image=None):
        super().__init__(name, lvl, exp, equip, image)
        self.name = "ShuijingAL"
        self.skill1_description = "Apply Matsu on all enemies for 30 turns." \
        " Matsu: When taking damage, take status damage equal to 60% of the damage taken. If the same effect is applied, duration is refreshed."
        self.skill2_description = "Apply Tsuru on all enemies for 30 turns." \
        " Tsuru: When taking status damage, take bypass damage equal to 60% of the status damage taken. If the same effect is applied, duration is refreshed."
        self.skill3_description = "At start of battle, apply Delay on a neighbor ally of highest atk for 30 turns. Delay: speed and final damage taken reduced" \
        " by 50%. Apply Ready on yourself for 30 turns. Ready: Increase speed by 100%. After using skill 2 the first time, The above 2 effects are removed, then" \
        " target a neighbor ally of highest atk, apply Ready on that ally for 15 turns."
        # 松 鶴
        self.skill1_description_jp = "全ての敵に30ターンの間「松」を付与する。松：ダメージを受けた際、受けたダメージの60%に相当する状態異常ダメージを受ける。同じ効果が再度付与された場合、持続時間が更新される。"
        self.skill2_description_jp = "全ての敵に30ターンの間「鶴」を付与する。鶴：状態異常ダメージを受けた際、受けた状態異常ダメージの60%に相当する状態異常無視ダメージを受ける。同じ効果が再度付与された場合、持続時間が更新される。"
        self.skill3_description_jp = "戦闘開始時、隣接する攻撃力が最も高い味方1人に30ターンの間「遅延」を付与する。遅延：速度と受ける最終ダメージが50%減少する。自身に30ターンの間「準備万端」を付与する。準備万端：速度が100%増加する。スキル2を初めて使用した後、上記の2つの効果が解除され、その後隣接する攻撃力が最も高い味方を対象に15ターンの間「準備万端」を付与する。"
        self.skill1_cooldown_max = 4
        self.skill2_cooldown_max = 4
        self.shuijingal_marked_ally: Character | None = None
        self.skill2_first_use = True

    def clear_others(self):
        self.shuijingal_marked_ally = None
        self.skill2_first_use = True

    def skill1_logic(self):
        for e in self.enemy:
            def value_func(char, dmg, attacker, effect_applier):
                return dmg * 0.60
            matsu = StingEffect("Matsu", 30, False, 0, self, value_function_normal_damage_step=value_func)
            matsu.additional_name = "ShuijingAL_Matsu"
            matsu.apply_rule = "stack"
            e.apply_effect(matsu)
        return 0

    def skill2_logic(self):
        for e in self.enemy:
            def value_func(char, dmg, attacker, effect_applier):
                return dmg * 0.60
            tsuru = StingEffect("Tsuru", 30, False, 0, self, value_function_status_damage_step=value_func)
            tsuru.additional_name = "ShuijingAL_Tsuru"
            tsuru.apply_rule = "stack"
            e.apply_effect(tsuru)
        if self.skill2_first_use:
            assert self.shuijingal_marked_ally is not None
            self.shuijingal_marked_ally.try_remove_effect_with_name("Delay")
            self.try_remove_effect_with_name("Ready")
            if self.shuijingal_marked_ally.is_alive():
                ready = StatsEffect("Ready", 15, True, {"spd": 2.00})
                ready.additional_name = "ShuijingAL_Ready"
                self.shuijingal_marked_ally.apply_effect(ready)
            self.skill2_first_use = False
        return 0

    def skill3(self):
        pass

    def battle_entry_effects(self):
        neighbors = self.get_neighbor_allies_not_including_self()
        t = max(neighbors, key=lambda x: x.atk)
        # apply delay effect
        delay = StatsEffect("Delay", 30, True, {"spd": 0.50, "final_damage_taken_multipler": -0.50})
        delay.additional_name = "ShuijingAL_Delay"
        t.apply_effect(delay)
        self.shuijingal_marked_ally = t
        ready = StatsEffect("Ready", 30, True, {"spd": 2.00})
        ready.additional_name = "ShuijingAL_Ready"
        self.apply_effect(ready)


class Martin(Character):
    """

    Build: 
    """
    def __init__(self, name, lvl, exp=0, equip=None, image=None):
        super().__init__(name, lvl, exp, equip, image)
        self.name = "Martin"
        self.skill1_description = "Apply Fair Trade to enemies and allies." \
        " Each enemy of lowest atk, def, speed has their selected stats increased by 20% for 20 turns." \
        " Each ally of highest atk, def, speed has their selected stats increased by 24% for 20 turns."
        self.skill2_description = "Attack random enemy 4 times with 240% atk, each attack inflict Defence Break for 20 turns with 30% chance." \
        " Defence Break: Defence is reduced by 40%."
        self.skill3_description = "Apply Maneki-neko to all allies." \
        " Maneki-neko: When taking friendly fire damage, heal hp by the amount of damage instead and reduce damage to 0." \
        " If at full hp, apply a shield that absorbs damage equal to the damage." \
        # " Maneki-neko cannot protect against self-harm damage."
        self.skill1_description_jp = "敵と味方に「大儲け」を付与する。攻撃力、防御力、速度が最も低い各敵の該当ステータスが20ターンの間20%増加する。攻撃力、防御力、速度が最も高い各味方の該当ステータスが20ターンの間24%増加する。"
        self.skill2_description_jp = "ランダムな敵に攻撃力の240%で4回攻撃し、30%確率で20ターンの間「防御ダウン」を付与する。防御ダウン：防御力が40%減少する。"
        self.skill3_description_jp = "全ての味方に「招き猫」を付与する。招き猫：味方からのダメージを受けた際、ダメージ量分のHPを回復し、ダメージを0に軽減する。HPが満タンの場合、そのダメージ量と同じダメージを吸収するシールドを付与する。"
        self.skill1_cooldown_max = 4
        self.skill2_cooldown_max = 3

    def skill1_logic(self):
        low_atk = mit.one(self.target_selection(keyword="n_lowest_attr", keyword2="1", keyword3="atk", keyword4="enemy"))
        low_def = mit.one(self.target_selection(keyword="n_lowest_attr", keyword2="1", keyword3="defense", keyword4="enemy"))
        low_spd = mit.one(self.target_selection(keyword="n_lowest_attr", keyword2="1", keyword3="spd", keyword4="enemy"))
        low_atk.apply_effect(StatsEffect("Fair Trade", 20, True, {"atk": 1.20}))
        low_def.apply_effect(StatsEffect("Fair Trade", 20, True, {"defense": 1.20}))
        low_spd.apply_effect(StatsEffect("Fair Trade", 20, True, {"spd": 1.20}))
        high_atk = mit.one(self.target_selection(keyword="n_highest_attr", keyword2="1", keyword3="atk", keyword4="ally"))
        high_def = mit.one(self.target_selection(keyword="n_highest_attr", keyword2="1", keyword3="defense", keyword4="ally"))
        high_spd = mit.one(self.target_selection(keyword="n_highest_attr", keyword2="1", keyword3="spd", keyword4="ally"))
        high_atk.apply_effect(StatsEffect("Fair Trade", 20, True, {"atk": 1.24}))
        high_def.apply_effect(StatsEffect("Fair Trade", 20, True, {"defense": 1.24}))
        high_spd.apply_effect(StatsEffect("Fair Trade", 20, True, {"spd": 1.24}))
        return 0

    def skill2_logic(self):
        def after_dmg(self, target: Character):
            if random.random() < 0.30:
                target.apply_effect(StatsEffect("Defence Break", 20, False, {"defense": 0.60}))
        damage_dealt = self.attack(multiplier=2.4, repeat=4, func_after_dmg=after_dmg)
        return damage_dealt

    def skill3(self):
        pass

    # FriendlyFireShield
    def battle_entry_effects(self):
        for a in self.ally:
            e = FriendlyFireShield("Maneki-neko", -1, True, cc_immunity=False, effect_applier=self,
                                              damage_reduction=1.0, heal_by_damage=1.0, apply_shield_on_full_hp=True)
            e.can_be_removed_by_skill = False
            a.apply_effect(e)


class Joe(Character):
    """
    Berserk(Increase atk but attack random ally or enemy)
    Build: 
    """
    def __init__(self, name, lvl, exp=0, equip=None, image=None):
        super().__init__(name, lvl, exp, equip, image)
        self.name = "Joe"
        self.skill1_description = "Attack random enemies with 230% atk 5 times."
        self.skill2_description = "Attack random enemies with 230% atk 4 times, 40% chance to inflict Blind for 20 turns each attack." \
        " Blind: acc reduced by 40%."
        self.skill3_description = "When the first time your hp is reaches below 50%, apply Berserk and Confuse to yourself for 40 turns at end of that turn." \
        " Berserk: atk increased by 100%, final damage taken increased by 50%. Confuse: attack random ally or enemy."
        self.skill1_description_jp = "ランダムな敵に攻撃力の230%で5回攻撃する。"
        self.skill2_description_jp = "ランダムな敵に攻撃力の230%で4回攻撃し、各攻撃には40%の確率で20ターンの間「暗闇」を付与する。暗闇：命中率が40%減少する。"
        self.skill3_description_jp = "自身のHPが初めて50%未満になった時、ターン終了の時に40ターンの間「暴走」と「混乱」を自分に付与する。暴走：攻撃力が100%増加し、受ける最終ダメージが50%増加する。混乱：ランダムな味方または敵を攻撃する。"
        self.skill1_cooldown_max = 3
        self.skill2_cooldown_max = 4
        self.skill3_used = False

    def clear_others(self):
        self.skill3_used = False

    def skill1_logic(self):
        damage_dealt = self.attack(multiplier=2.3, repeat=5)
        return damage_dealt

    def skill2_logic(self):
        def blind_effect(self, target: Character):
            if random.random() < 0.40:
                target.apply_effect(StatsEffect("Blind", 20, False, {"acc": -0.40}))
        damage_dealt = self.attack(multiplier=2.3, repeat=4, func_after_dmg=blind_effect)
        return damage_dealt

    def skill3(self):
        pass

    def character_specific_at_end_of_turn(self):
        if not self.skill3_used and self.is_alive() and self.hp < self.maxhp * 0.50:
            berserk = StatsEffect("Berserk", 40, True, {"atk": 2.00, "final_damage_taken_multipler": 0.50})
            berserk.additional_name = "Joe_Berserk"
            confuse = ConfuseEffect("Confuse", 40, False, False)
            self.apply_effect(berserk)
            self.apply_effect(confuse)
            self.skill3_used = True


class Cory(Character):
    """
    Berserk(Increase atk but attack random ally or enemy)
    Build: 
    """
    def __init__(self, name, lvl, exp=0, equip=None, image=None):
        super().__init__(name, lvl, exp, equip, image)
        self.name = "Cory"
        self.skill1_description = "For 20 turns, apply Berserk to yourself, attack random targets with 220% atk 9 times." \
        " Berserk: atk increased by 100%, final damage taken increased by 50%."
        self.skill2_description = "Target yourself and neighbor allies, recover hp by 200% of your atk if not at full hp, apply a shield that absorbs" \
        " damage equal to 200% of your atk. Afterwards, attack random targets with 220% atk 5 times."
        self.skill3_description = "At start of battle, apply Resolve to yourself for 20 turns," \
        " when taking normal damage that exceed your hp, damage is reduced so that it is equal to your hp minus 1."
        self.skill1_description_jp = "20ターンの間、自身に「バーサーク」を付与し、ランダムな対象に攻撃力の220%で9回攻撃する。バーサーク：攻撃力が100%増加し、受ける最終ダメージが50%増加する。"
        self.skill2_description_jp = "自分と隣接する味方を対象に、HPが満タンでない場合、攻撃力の200%分のHPを回復し、攻撃力の200%分のダメージを吸収するシールドを付与する。その後、ランダムな対象に攻撃力の220%で5回攻撃する。"
        self.skill3_description_jp = "戦闘開始時、自身に20ターンの間「覚悟」を付与する。覚悟：通常ダメージが自身のHPを超えた場合、ダメージがHP-1となるように軽減される。"
        self.skill1_cooldown_max = 4
        self.skill2_cooldown_max = 4

    def skill1_logic(self):
        berserk = StatsEffect("Berserk", 20, True, {"atk": 2.00, "final_damage_taken_multipler": 0.50})
        berserk.additional_name = "Cory_Berserk"
        berserk.apply_rule = "stack"
        self.apply_effect(berserk)
        damage_dealt = self.attack(multiplier=2.2, repeat=9, target_kw1="Undefined_target")
        return damage_dealt

    def skill2_logic(self):
        neighbors: list[Character] = self.get_neighbor_allies_including_self()
        for a in neighbors:
            if a.hp < a.maxhp:
                a.heal_hp(self.atk * 2.0, self)
            a.apply_effect(AbsorptionShield("Shield", -1, True, self.atk * 2.0, False))
        damage_dealt = self.attack(multiplier=2.2, repeat=5, target_kw1="Undefined_target")
        return damage_dealt

    def skill3(self):
        pass

    def battle_entry_effects(self):
        e = ResolveEffect("Resolve", 20, True, False)
        self.apply_effect(e)



class Zyl(Character):
    """
    Higher dmg at low hp percentage
    Build: 
    """
    def __init__(self, name, lvl, exp=0, equip=None, image=None):
        super().__init__(name, lvl, exp, equip, image)
        self.name = "Zyl"
        self.skill1_description = "Attack enemy of highest hp with 285% atk 3 times."
        self.skill2_description = "Attack 3 closest enemy with 230% atk 2 times, each attack has 50% chance to inflict Gravity Loss for 20 turns." \
        " Gravity Loss: defense and critdef reduced by 20%."
        self.skill3_description = "When attacking, damage dealt is increased by the percentage of hp lost."
        self.skill1_description_jp = "HPが最も高い敵に攻撃力の285%で3回攻撃する。"
        self.skill2_description_jp = "最も近い敵3体に攻撃力の230%で2回攻撃し、各攻撃には50%の確率で20ターンの間「重力喪失」を付与する。重力喪失：防御力とクリティカル防御が20%減少する。"
        self.skill3_description_jp = "攻撃時、失ったHPの割合に応じて与えるダメージが増加する。"
        self.skill1_cooldown_max = 4
        self.skill2_cooldown_max = 4

    def skill1_logic(self):
        def dmg_amplify(char, target, dmg):
            lost_hp_percentage = (char.maxhp - char.hp) / char.maxhp
            global_vars.turn_info_string += f"Damage increased by {lost_hp_percentage * 100}% due to lost hp.\n"
            return dmg * (1 + lost_hp_percentage)

        damage_dealt = self.attack(multiplier=2.85, repeat=3, target_kw1="n_highest_attr", target_kw2="1", target_kw3="hp", target_kw4="enemy",
                                   func_damage_step=dmg_amplify)
        return damage_dealt

    def skill2_logic(self):
        def dmg_amplify(char, target, dmg):
            lost_hp_percentage = (char.maxhp - char.hp) / char.maxhp
            global_vars.turn_info_string += f"Damage increased by {lost_hp_percentage * 100}% due to lost hp.\n"
            return dmg * (1 + lost_hp_percentage)
        
        def gravity_loss_effect(self, target: Character):
            if random.random() < 0.50:
                target.apply_effect(StatsEffect("Gravity Loss", 20, False, {"defense": 0.80, "critdef": -0.20}))
        damage_dealt = self.attack(multiplier=2.3, repeat=2, target_kw1="n_enemy_in_front", target_kw2="3",
                                   func_damage_step=dmg_amplify, func_after_dmg=gravity_loss_effect)
        return damage_dealt

    def skill3(self):
        pass

    def normal_attack(self):
        def dmg_amplify(char, target, dmg):
            lost_hp_percentage = (char.maxhp - char.hp) / char.maxhp
            global_vars.turn_info_string += f"Damage increased by {lost_hp_percentage * 100}% due to lost hp.\n"
            return dmg * (1 + lost_hp_percentage)
        damage_dealt = self.attack(func_damage_step=dmg_amplify)
        return damage_dealt


class Jerry(Character):
    """
    Sleep
    Build: 
    """
    def __init__(self, name, lvl, exp=0, equip=None, image=None):
        super().__init__(name, lvl, exp, equip, image)
        self.name = "Jerry"
        self.skill1_description = "Heal all allies by 200% of your defense, remove 2 debuffs from each ally. Each enemy has a 50% chance to" \
        " fall asleep for 20 turns."
        self.skill2_description = "Attack all enemies with 200% atk, 20% chance to apply Sleep, 40% chance to apply Slow for 20 turns." \
        " Slow: spd reduced by 20%."
        self.skill3_description = "At start of battle, increase speed by 100% for 3 turns."
        self.skill1_description_jp = "防御力の200%分、全ての味方を回復し、各味方からデバフを2つ解除する。全ての敵に50%の確率で20ターン睡眠状態を付与する。"
        self.skill2_description_jp = "攻撃力の200%で全ての敵に攻撃し、20%の確率で睡眠状態を、40%の確率で20ターンの間「和音」を付与する。和音：速度が20%減少する。"
        self.skill3_description_jp = "戦闘開始時に、3ターンの間速度が100%増加する。"
        self.skill1_cooldown_max = 4
        self.skill2_cooldown_max = 4
        self.skill3_used = False

    def clear_others(self):
        self.skill3_used = False

    def skill1_logic(self):
        self.heal(value=self.defense * 2, target_kw1="all_ally")
        for a in self.ally:
            a.remove_random_amount_of_debuffs(2)
        for e in self.enemy:
            if random.random() < 0.50:
                e.apply_effect(SleepEffect("Sleep", 20, False, False))
        return 0

    def skill2_logic(self):
        def effect(self, target: Character):
            chance = random.random()
            if chance < 0.20:
                target.apply_effect(SleepEffect("Sleep", 20, False, False))
            elif chance < 0.60:
                target.apply_effect(StatsEffect("Slow", 20, False, {"spd": 0.70}))
        damage_dealt = self.attack(multiplier=2.0, repeat=1, target_kw1="all_enemy", func_after_dmg=effect)
        return damage_dealt

    def skill3(self):
        pass

    def battle_entry_effects(self):
        spd = StatsEffect("Poetry", 3, True, {"spd": 2.00})
        self.apply_effect(spd)


class Qimon(Character):
    """
    Sleep Effect Support
    Build: 
    """
    def __init__(self, name, lvl, exp=0, equip=None, image=None):
        super().__init__(name, lvl, exp, equip, image)
        self.name = "Qimon"
        self.skill1_description = "Remove all Sleep effects on all allies and apply Sweet Dreams for 20 turns." \
        " Sweet Dreams: All main stats are increased by 10%. If ally has Sleep effect, effect is tripled."
        self.skill2_description = "Apply Regeneration on all allies who have either Sleep or Sweet Dreams for 12 turns." \
        " Regeneration: Recover hp by 3% of their lost hp each turn. This skill becomes normal attack if" \
        " there are no allies with Sleep or Sweet Dreams."
        self.skill3_description = "At start of battle, apply Bubble World on all enemies." \
        " Bubble World: When falling asleep, 3 active buffs are removed, damage taken that below 10% of maxhp" \
        " cannot remove Sleep effect."
        # Sweat Dreams: "幻夢"
        # "Bubble World", "Qimon_Bubble_World", "BubbleWorldEffect"
        self.skill1_description_jp = "全ての味方から睡眠効果を解除し、20ターンの間「幻夢」を付与する。幻夢：全ての主要ステータスが10%増加する。味方が睡眠状態の場合、この効果は3倍になる。"
        self.skill2_description_jp = "睡眠または幻夢を持つ全ての味方に12ターンの間「再生」を付与する。再生：毎ターン、失われたHPの3%を回復する。味方に睡眠または幻夢が付与されていない場合、このスキルは通常攻撃に変わる。"
        self.skill3_description_jp = "戦闘開始時、全ての敵に「泡沫の世界」を付与する。泡沫の世界：睡眠状態になると、3つのアクティブなバフが解除され、最大HPの10%未満のダメージでは睡眠効果が解除されない。"
        self.skill1_cooldown_max = 4
        self.skill2_cooldown_max = 4
        # test, del later

    def skill1_logic(self):
        for a in self.ally:
            success = a.try_remove_effect_with_name("Sleep", remove_all_found_effects=True)
            if not success:
                a.apply_effect(StatsEffect("Sweet Dreams", 20, True, {"atk": 1.10, "defense": 1.10, "spd": 1.10, "maxhp": 1.10}))
            else:
                a.apply_effect(StatsEffect("Sweet Dreams", 20, True, {"atk": 1.30, "defense": 1.30, "spd": 1.30, "maxhp": 1.30}))
        return 0

    def skill2_logic(self):
        allies_has_effect = 0
        for a in self.ally:
            if a.has_effect_that_named("Sleep") or a.has_effect_that_named("Sweet Dreams"):
                allies_has_effect += 1
                def value_func(char, effect_applier):
                    return (char.maxhp - char.hp) * 0.03
                a.apply_effect(ContinuousHealEffect("Regeneration", 12, True, value_function=value_func, buff_applier=self,
                                                   value_function_description="3% of lost hp", value_function_description_jp="失ったHPの3%"))
        if allies_has_effect == 0:
            damage_dealt = self.attack()
            return damage_dealt
        else:
            return 0

    def skill3(self):
        pass

    def battle_entry_effects(self):
        for e in self.enemy:
            bw = BubbleWorldEffect("Bubble World", -1, False, self)
            bw.additional_name = "Qimon_Bubble_World"
            e.apply_effect(bw)


class QimonNY(Character):
    """
    Sleep Effect Support
    New Year Version
    Build: 
    """
    def __init__(self, name, lvl, exp=0, equip=None, image=None):
        super().__init__(name, lvl, exp, equip, image)
        self.name = "QimonNY"
        self.skill1_description = "Remove all Sleep effects on all allies and apply Fancy Dreams for 20 turns." \
        " Fancy Dreams: When taking damage, the part of damage that exceeds 20% of max hp is reduced by 40%." \
        " If ally has Sleep effect, damage reduction is doubled."
        self.skill2_description = "Remove 3 active debuffs on all allies who have either Sleep or Fancy Dreams," \
        " their hp is recovered by 300% of your atk."
        " This skill becomes normal attack if" \
        " there are no allies with Sleep or Fancy Dreams."
        self.skill3_description = "At start of battle, apply Dream Invitation on all enemies." \
        " Dream Invitation: When falling asleep, 3 active buffs are removed, damage taken is increased by 30% and only have 30% chance to" \
        " remove Sleep effect."
        # Fancy Dreams: "美夢"
        # "Dream Invitation", "QimonNY_Dream_Invitation", "BubbleWorldEffect"
        self.skill1_description_jp = "全ての味方の睡眠効果を解除し、20ターンの間「美夢」を付与する。美夢：ダメージを受けた際、最大HPの20%を超える部分のダメージが40%減少する。味方が睡眠効果を持っている場合、ダメージ軽減効果が2倍になる。"
        self.skill2_description_jp = "睡眠または美夢効果を持つ全ての味方のアクティブなデバフを3つ解除し、攻撃力の300%分のHPを回復させる。味方に睡眠または美夢効果を持つ者がいない場合、このスキルは通常攻撃に変わる。"
        self.skill3_description_jp = "戦闘開始時、全ての敵に「夢の誘い」を付与する。夢の誘い：睡眠状態になると、アクティブなバフが3つ解除され、受けるダメージが30%増加し、睡眠効果を解除する確率が30%になる。"
        self.skill1_cooldown_max = 4
        self.skill2_cooldown_max = 4
        # test, del later

    def skill1_logic(self):
        for a in self.ally:
            success = a.try_remove_effect_with_name("Sleep", remove_all_found_effects=True)
            if not success:
                a.apply_effect(EffectShield2("Fancy Dreams", 20, True, cc_immunity=False, damage_reduction=0.40,
                                             shrink_rate=0, hp_threshold=0.20))
            else:
                a.apply_effect(EffectShield2("Fancy Dreams", 20, True, cc_immunity=False, damage_reduction=0.80,
                                             shrink_rate=0, hp_threshold=0.20))
        return 0

    def skill2_logic(self):
        allies_has_effect = 0
        for a in self.ally:
            if a.has_effect_that_named("Sleep") or a.has_effect_that_named("Fancy Dreams"):
                allies_has_effect += 1
                a.remove_random_amount_of_debuffs(3, False)
                if a.is_alive():
                    a.heal_hp(self.atk * 3.0, healer=self)
        if allies_has_effect == 0:
            damage_dealt = self.attack()
            return damage_dealt
        else:
            return 0

    def skill3(self):
        pass

    def battle_entry_effects(self):
        for e in self.enemy:
            di = BubbleWorldEffect("Dream Invitation", -1, False, self, di=True)
            di.additional_name = "QimonNY_Dream_Invitation"
            e.apply_effect(di)


class Fred(Character):
    """
    Support nearby allies with shield, remove debuff, set at 30% hp
    Build: 
    """
    def __init__(self, name, lvl, exp=0, equip=None, image=None):
        super().__init__(name, lvl, exp, equip, image)
        self.name = "Fred"
        self.skill1_description = "Target 1 neighbor ally of highest atk, that ally takes status damage equal to 75% of their current hp," \
        " apply a Shield that absorbs damage equal to 100% of the damage dealt. For 20 turns, that ally gains 30% atk and 30% speed," \
        " 20 turns later, hp is recovered by the damage taken."
        self.skill2_description = "Target 1 neighbor ally of highest atk, remove all active debuffs, apply a shield that absorbs damage equal to" \
        " 10% of their lost hp. For each debuff removed, shield value increases by 10% of their lost hp."
        self.skill3_description = "At start of battle, target the neighbor ally of highest atk, that ally gains 30% atk."
        self.skill1_description_jp = "隣接する攻撃力が最も高い味方1人を対象とし、その味方に現在のHPの75%分の状態異常ダメージを与える。同時に、そのダメージ量の100%に相当するダメージを吸収するシールドを付与する。その味方は20ターンの間、攻撃力が30%増加し、速度が30%増加する。20ターン後、与えたダメージ分のHPが回復する。"
        self.skill2_description_jp = "隣接する攻撃力が最も高い味方1人を対象とし、その味方の全てのアクティブなデバフを解除する。同時に、失ったHPの10%分のダメージを吸収するシールドを付与する。解除したデバフ1つにつき、シールド値が失ったHPの10%分増加する。"
        self.skill3_description_jp = "戦闘開始時、隣接する攻撃力が最も高い味方1人を対象とし、その味方の攻撃力を30%増加させる。"
        self.skill1_cooldown_max = 4
        self.skill2_cooldown_max = 4

    def skill1_logic(self):
        neighbor = self.get_neighbor_allies_not_including_self()
        if not neighbor:
            return 0
        target: Character = max(neighbor, key=lambda x: x.atk)
        target_hp_prev = target.hp
        target.take_status_damage(target.hp * 0.75, None)
        target_hp_current = target.hp
        if target_hp_prev - target_hp_current > 0 and target.is_alive():
            shield = AbsorptionShield("Shield", -1, True, target_hp_prev - target_hp_current, False)
            target.apply_effect(shield)
            target.apply_effect(ReservedEffect("Recovery", 20, True, False, self, heal_hp=target_hp_prev - target_hp_current))
        if target.is_alive():
            target.apply_effect(StatsEffect("Injected", 20, True, {"atk": 1.30, "spd": 1.30}))
        return 0

    def skill2_logic(self):
        neighbor = self.get_neighbor_allies_not_including_self()
        if not neighbor:
            return 0
        target: Character = max(neighbor, key=lambda x: x.atk)
        removed_debuffs = target.remove_random_amount_of_debuffs(999, False)
        target_lost_hp = target.maxhp - target.hp
        shield_value = target_lost_hp * 0.10 + target_lost_hp * 0.10 * len(removed_debuffs)
        if target.is_alive() and shield_value > 0:
            shield = AbsorptionShield("Shield", -1, True, shield_value, False)
            target.apply_effect(shield)
        return 0

    def skill3(self):
        pass

    def battle_entry_effects(self):
        neighbor = self.get_neighbor_allies_not_including_self()
        if not neighbor:
            raise Exception("No neighbor found at start of battle?")
        target: Character = max(neighbor, key=lambda x: x.atk)
        target.apply_effect(StatsEffect("Boosted", -1, True, {"atk": 1.30}, can_be_removed_by_skill=False))


class Waldo(Character):
    """
    Speed Supremacy
    Build: 
    """
    def __init__(self, name, lvl, exp=0, equip=None, image=None):
        super().__init__(name, lvl, exp, equip, image)
        self.name = "Waldo"
        self.skill1_description = "Attack enemy of highest speed with 260% atk 3 times, if target has lower speed than you, damage is increased by 50%."
        self.skill2_description = "Focus attack on closest enemy with 260% atk 3 times, if target has lower speed than you, guaranteed critical hit."
        self.skill3_description = "At start of battle, target one enemy of 2nd highest speed, apply Dash to allies that have speed lower than that enemy," \
        " they have their speed increased to almost match that enemy."
        self.skill1_description_jp = "速度が最も高い敵に攻撃力の260%で3回攻撃し、対象の速度が自分より低い場合、ダメージが50%増加する。"
        self.skill2_description_jp = "最も近い敵に攻撃力の260%で3回集中攻撃し、対象の速度が自分より低い場合、必ずクリティカルヒットする。"
        self.skill3_description_jp = "戦闘開始時、速度が2番目に高い敵を対象に選択し、その敵より速度が低い味方に「疾走」を付与する。疾走を付与された味方は、速度がその敵とほぼ同じになるまで増加する。"
        self.skill1_cooldown_max = 4
        self.skill2_cooldown_max = 4

    def skill1_logic(self):
        def dmg_amplify(char, target, dmg):
            if char.spd > target.spd:
                global_vars.turn_info_string += f"Damage increased by 50% due to higher speed.\n"
                return dmg * 1.50
            return dmg
        damage_dealt = self.attack(multiplier=2.6, repeat=3, target_kw1="n_highest_attr", target_kw2="1", target_kw3="spd", target_kw4="enemy",
                                   func_damage_step=dmg_amplify)
        return damage_dealt

    def skill2_logic(self):
        target = mit.one(self.target_selection(keyword="enemy_in_front"))
        if self.spd > target.spd:
            crit = True
        else:
            crit = False
        damage_dealt = self.attack(multiplier=2.6, repeat_seq=3, target_list=[target], always_crit=crit)
        return damage_dealt

    def skill3(self):
        pass

    def battle_entry_effects(self):
        enemy = list(self.target_selection(keyword="n_highest_attr", keyword2="2", keyword3="spd", keyword4="enemy"))[-1]
        for a in self.ally:
            if a.spd < enemy.spd:
                delta = enemy.spd - a.spd
                delta = delta * (1 + random.uniform(-0.05, 0.05))
                a.apply_effect(StatsEffect("Dash", -1, True, main_stats_additive_dict={"spd": delta}, can_be_removed_by_skill=False))


class Toby(Character):
    """
    Waldo makes characters viable with low speed build, Tody makes characters viable with high speed build
    Build: 
    """
    def __init__(self, name, lvl, exp=0, equip=None, image=None):
        super().__init__(name, lvl, exp, equip, image)
        self.name = "Toby"
        self.skill1_description = "Attack all enemies with 280% atk, apply Race! on them for 30 turns," \
        " Race!: When taking damage from enemy with higher speed, damage is increased by 50%." \
        " If same effect is applied, duration is refreshed."
        self.skill2_description = "All nearby allies gain atk equal to 40% of their speed, for 20 turns."
        self.skill3_description = "Apply Cheering Flag to all allies at start of battle." \
        " Cheering Flag: Speed is increased by 10%."
        self.skill1_description_jp = "全ての敵に攻撃力の280%で攻撃し、30ターンの間「レース！」を付与する。レース！：速度が高い敵からダメージを受けると、受けるダメージが50%増加する。同じ効果が再度付与された場合、持続時間が更新される。"
        self.skill2_description_jp = "隣接する全ての味方の攻撃力を、自身の速度の40%分増加させる。この効果は20ターン持続する。"
        self.skill3_description_jp = "戦闘開始時に全ての味方に「応援の旗」を付与する。応援の旗：速度が10%増加する。"
        self.skill1_cooldown_max = 4
        self.skill2_cooldown_max = 4

    def skill1_logic(self):
        def race_effect(self, target: Character):
            race = ReductionShield("Race!", 30, False, 0.5, False, requirement=lambda char, attacker: char.spd < attacker.spd,
                                                requirement_description="taking damage from enemy with higher speed", 
                                                requirement_description_jp="速度が高い敵からダメージを受ける時。")
            race.apply_rule = "stack"
            race.additional_name = "Toby_Race!"
            target.apply_effect(race)
        damage_dealt = self.attack(multiplier=2.8, repeat=1, target_kw1="all_enemy", func_after_dmg=race_effect)
        return damage_dealt

    def skill2_logic(self):
        neighbors = self.get_neighbor_allies_not_including_self()
        for a in neighbors:
            a.apply_effect(StatsEffect("Speedy", 20, True, main_stats_additive_dict={"atk": a.spd * 0.40}))
        return 0

    def skill3(self):
        pass

    def battle_entry_effects(self):
        for a in self.ally:
            a.apply_effect(StatsEffect("Cheering Flag", -1, True, {"spd": 1.10}, can_be_removed_by_skill=False))


class TobyRT(Character):
    """
    Enables low speed build
    Build: 
    """
    def __init__(self, name, lvl, exp=0, equip=None, image=None):
        super().__init__(name, lvl, exp, equip, image)
        self.name = "TobyRT"
        self.skill1_description = "Attack all enemies with 240% atk, apply Jump! on them for 30 turns," \
        " Jump!: When taking damage from enemy with lower speed, damage is increased by 75%." \
        " If same effect is applied, duration is refreshed."
        self.skill2_description = "Attack all enemies with 320% atk."
        self.skill3_description = "Normal attack attack all enemies."
        self.skill1_description_jp = "全ての敵に攻撃力の240%で攻撃し、30ターンの間「ジャンプ！」を付与する。ジャンプ！：速度が低い敵からダメージを受けると、そのダメージが75%増加する。同じ効果が再度付与された場合、持続時間が更新される。"
        self.skill2_description_jp = "全ての敵に攻撃力の320%で攻撃する。"
        self.skill3_description_jp = "通常攻撃が全ての敵を対象にする。"
        self.skill1_cooldown_max = 4
        self.skill2_cooldown_max = 4

    def skill1_logic(self):
        def race_effect(self, target: Character):
            race = ReductionShield("Jump!", 30, False, 0.75, False, requirement=lambda char, attacker: char.spd > attacker.spd,
                                                requirement_description="taking damage from enemy with lower speed", 
                                                requirement_description_jp="速度が低い敵からダメージを受ける時。")
            race.apply_rule = "stack"
            race.additional_name = "TobyRT_Jump!"
            target.apply_effect(race)
        damage_dealt = self.attack(multiplier=2.4, repeat=1, target_kw1="all_enemy", func_after_dmg=race_effect)
        return damage_dealt

    def skill2_logic(self):
        damage_dealt = self.attack(multiplier=3.2, repeat=1, target_kw1="all_enemy")
        return damage_dealt

    def skill3(self):
        pass

    def normal_attack(self):
        damage_dealt = self.attack(target_kw1="all_enemy")
        return damage_dealt


class Imada(Character):
    """
    Far close ally support, overheal support    
    Build: 
    """
    def __init__(self, name, lvl, exp=0, equip=None, image=None):
        super().__init__(name, lvl, exp, equip, image)
        self.name = "Imada"
        self.skill1_description = "Target 1 furthest ally, that ally gains 30% atk and 60% penetration for 20 turns.," \
        " Target 1 closest ally of highest defense, that ally gains 20% defense and 40% critdef for 20 turns." \
        " Before applying effects, remove 2 active debuffs from the target."
        self.skill2_description = "Apply Clear Spring to 1 furthest ally and 2 closest allies for 20 turns." \
        " Clear Spring: Overhealing becomes absorption shield, shield value is equal to 60% of overhealing. When the same effect is applied, duration is refreshed." \
        " After applying effects, heal the affected allies by 200% of your defense."
        self.skill3_description = "Apply Gift of Lake to the furthest ally at start of battle." \
        " Gift of Lake: accuracy, penetration, critrate, critdamage increased by 12%."
        self.skill1_description_jp = "最も遠い味方1人を対象に、その味方の攻撃力を30%と貫通力を60%20ターンの間増加させる。防御力が最も高い最も近い味方1人を対象に、その味方の防御力20%とクリティカル防御40%を20ターンの間増加させる。効果を適用する前に、対象からアクティブなデバフを2つ解除する。"
        self.skill2_description_jp = "最も遠い味方1人と最も近い味方2人に20ターンの間「澄んだ泉」を付与する。澄んだ泉：過剰回復分が吸収シールドとなり、そのシールドの値は過剰回復量の60%に相当する。同じ効果を適用した際、持続時間を更新される。効果を適用した後、その味方たちを防御力の200%分治療する。"
        self.skill3_description_jp = "戦闘開始時、最も遠い味方1人に「湖の贈り物」を付与する。湖の贈り物：命中率、貫通力、クリティカル率、クリティカルダメージが12%増加する。"
        self.skill1_cooldown_max = 3
        self.skill2_cooldown_max = 4

    def skill1_logic(self):
        fur_ally = mit.one(self.target_selection(keyword="furthest_ally"))
        fur_ally.remove_random_amount_of_debuffs(2, False)
        fur_ally.apply_effect(StatsEffect("Red Wave", 20, True, {"atk": 1.30, "penetration": 0.60}))
        neighbors: list[Character] = self.get_neighbor_allies_not_including_self()
        if not neighbors:
            return 0
        neighbor_def = max(neighbors, key=lambda x: x.defense)
        neighbor_def.remove_random_amount_of_debuffs(2, False)
        neighbor_def.apply_effect(StatsEffect("Blue Wave", 20, True, {"defense": 1.20, "critdef": 0.40}))
        return 0

    def skill2_logic(self):
        fur_ally = mit.one(self.target_selection(keyword="furthest_ally"))
        neighbors = self.get_neighbor_allies_not_including_self()
        def apply_clear_spring(char):
            cs = OverhealEffect("Clear Spring", 20, True, self, overheal_bonus=0.60, absorption_shield_ratio=1.0)
            cs.additional_name = "Imada_Clear_Spring"
            cs.apply_rule = "stack"
            char.apply_effect(cs)
        apply_clear_spring(fur_ally)
        self.heal(value=self.defense * 2.0, target_list=[fur_ally])
        if not neighbors:
            return 0
        for a in neighbors:
            apply_clear_spring(a)
            self.heal(value=self.defense * 2.0, target_list=[a])
        return 0

    def skill3(self):
        pass

    def battle_entry_effects(self):
        fur_ally = mit.one(self.target_selection(keyword="furthest_ally"))
        fur_ally.apply_effect(StatsEffect("Gift of Lake", -1, True, {"acc": 0.12, "penetration": 0.12, "crit": 0.12, "critdmg": 0.12}, can_be_removed_by_skill=False))


class Lancelot(Character):
    """
    Good against high maxhp enemies and absorption shield
    Build: 
    """
    def __init__(self, name, lvl, exp=0, equip=None, image=None):
        super().__init__(name, lvl, exp, equip, image)
        self.name = "Lancelot"
        self.skill1_description = "Attack all enemies with 220% atk."
        self.skill2_description = "Attack random enemies 5 times with 220% atk."
        self.skill3_description = "When attacking with a skill, damage is increased by 8% of enemy's max hp." \
        " If enemy has absorption shield, damage is increased by 80%."
        self.skill1_description_jp = "全ての敵に攻撃力の220%で攻撃する。"
        self.skill2_description_jp = "ランダムな敵に攻撃力の220%で5回攻撃する。"
        self.skill3_description_jp = "スキルで攻撃する際、ダメージが敵の最大HPの8%分増加する。敵が吸収シールドを持っている場合、ダメージが80%増加する。"
        self.skill1_cooldown_max = 4
        self.skill2_cooldown_max = 4

    def skill1_logic(self):
        def damage_amplify(char, target: Character, dmg):
            new_dmg = dmg + target.maxhp * 0.08
            if target.has_effect_that_named(None, None, "AbsorptionShield"):
                new_dmg *= 1.80
            return new_dmg
        damage_dealt = self.attack(multiplier=2.20, repeat=1, target_kw1="all_enemy", func_damage_step=damage_amplify)
        return damage_dealt

    def skill2_logic(self):
        def damage_amplify(char, target: Character, dmg):
            new_dmg = dmg + target.maxhp * 0.08
            if target.has_effect_that_named(None, None, "AbsorptionShield"):
                new_dmg *= 1.80
            return new_dmg
        damage_dealt = self.attack(multiplier=2.20, repeat=5, func_damage_step=damage_amplify)
        return damage_dealt

    def skill3(self):
        pass



class Glass(Character):
    """
    Cause low accuracy, attack low accuracy
    Build: 
    """
    def __init__(self, name, lvl, exp=0, equip=None, image=None):
        super().__init__(name, lvl, exp, equip, image)
        self.name = "Glass"
        self.skill1_description = "Target 3 closest enemies, attack with 300% atk and apply Old Eyes for 20 turns." \
        " Old Eyes: Accuracy is reduced by 80%, when same effect is applied, duration is refreshed. Then target 2 neighbor allies, apply Old Eyes for 20 turns."
        self.skill2_description = "Remove Old Eyes effect on neighbor allies. If their accuracy is more than 150%," \
        " for 20 turns, their atk and defense is increased by the difference between their accuracy and 150%." \
        " Attack 1 enemy who has lowest accuracy with 400% atk, if target has accuracy lower than 20%, Stun for 10 turns."
        self.skill3_description = "When using skill2, if the ally has more than 200% accuracy, crit, critdmg, penetration is increased by the" \
        " difference between their accuracy and 150%."
        self.skill1_description_jp = "最も近い3人の敵を対象に、攻撃力の300%で攻撃し、20ターンの間「老眼」を付与する。老眼：命中率が80%減少し、同じ効果が再度付与された場合、持続時間が更新される。その後、隣接する2人の味方を対象に、20ターンの間「老眼」を付与する。"
        self.skill2_description_jp = "隣接する味方の「老眼」効果を解除する。味方の命中率が150%以上の場合、20ターンの間、命中率と150%の差分に応じて攻撃力と防御力が増加する。命中率が最も低い敵1体を対象に、攻撃力の400%で攻撃し、対象の命中率が20%未満の場合、10ターンの間スタンさせる。"
        self.skill3_description_jp = "スキル2を使用する際、味方の命中率が200%以上の場合、命中率と150%の差分に応じて、クリティカル率、クリティカルダメージ、貫通力が増加する。"
        self.skill1_cooldown_max = 4
        self.skill2_cooldown_max = 4

    def skill1_logic(self):
        def old_eyes(char, target: Character):
            oe = StatsEffect("Old Eyes", 20, False, {"acc": -0.80})
            oe.additional_name = "Glass_Old_Eyes"
            oe.apply_rule = "stack"
            target.apply_effect(oe)
        damage_dealt = self.attack(multiplier=3.0, repeat=1, target_kw1="n_enemy_in_front", target_kw2="3", func_after_dmg=old_eyes)
        if self.is_alive():
            neighbors = self.get_neighbor_allies_not_including_self()
            if neighbors:
                for a in neighbors:
                    oe = StatsEffect("Old Eyes", 20, False, {"acc": -0.80})
                    oe.additional_name = "Glass_Old_Eyes"
                    oe.apply_rule = "stack"
                    a.apply_effect(oe)
        return damage_dealt

    def skill2_logic(self):
        neighbors: list[Character] = self.get_neighbor_allies_not_including_self()
        if neighbors:
            for a in neighbors:
                a.try_remove_effect_with_name("Old Eyes", remove_all_found_effects=True)
                if a.acc > 1.5:
                    a.apply_effect(StatsEffect("Sharp Eyes", 20, True, {"atk": 1 + a.acc - 1.5, "defense": 1 + a.acc - 1.5}))
                if a.acc > 2.0:
                    a.apply_effect(StatsEffect("Sharp Eyes", 20, True, {"crit": a.acc - 1.5, "critdmg": a.acc - 1.5, "penetration": a.acc - 1.5}))
        def stun_logic(char, target: Character):
            if target.acc < 0.20:
                target.apply_effect(StunEffect("Stun", 10, False))
        # case ("n_lowest_attr", n, attr, party)
        damage_dealt = self.attack(multiplier=4.0, repeat=1, target_kw1="n_lowest_attr", target_kw2="1", target_kw3="acc", target_kw4="enemy",
                                    func_after_dmg=stun_logic)
        return damage_dealt

    def skill3(self):
        pass



class Gawain(Character):
    """

    Build: 
    """
    def __init__(self, name, lvl, exp=0, equip=None, image=None):
        super().__init__(name, lvl, exp, equip, image)
        self.name = "Gawain"
        self.skill1_description = "Target enemy of lowest atk, defense and speed, attack with 250%|300%|350% atk," \
        " after each attack, if your hp is lower than 10%, recover hp by 100% of damage dealt."
        self.skill2_description = "Target enemy of lowest atk, attack with 200% atk 5 times, if you have Absorption Shield," \
        " attack with 300% atk 5 times."
        self.skill3_description = "At start of battle, apply Brilliance on yourself for 10 turns." \
        " Brilliance: Damage taken is reduced by 60%, immune to CC effects."
        self.skill1_description_jp = "攻撃力、防御力、速度が最も低い敵を対象に、それぞれ攻撃力の250%|300%|350%で攻撃する。各攻撃後、自分のHPが10%未満の場合、与えたダメージの100%分HPを回復する。"
        self.skill2_description_jp = "攻撃力が最も低い敵を対象に、攻撃力の200%で5回攻撃する。自分が吸収シールドを持っている場合、攻撃力の300%で5回攻撃する。"
        self.skill3_description_jp = "戦闘開始時に、自身に10ターンの間「輝光」を付与する。輝光：受けるダメージが60%減少し、CC効果を無効化する。"
        self.skill1_cooldown_max = 3
        self.skill2_cooldown_max = 3

    def skill1_logic(self):
        damage_dealt = self.attack(multiplier=2.5, repeat=1, target_kw1="n_lowest_attr", target_kw2="1", target_kw3="atk", target_kw4="enemy")
        if self.hp < 0.10 and self.is_alive():
            self.heal_hp(damage_dealt, healer=self)
        if self.is_alive():
            damage_dealt += self.attack(multiplier=3.0, repeat=1, target_kw1="n_lowest_attr", target_kw2="1", target_kw3="defense", target_kw4="enemy")
        if self.hp < 0.10 and self.is_alive():
            self.heal_hp(damage_dealt, healer=self)
        if self.is_alive():
            damage_dealt += self.attack(multiplier=3.5, repeat=1, target_kw1="n_lowest_attr", target_kw2="1", target_kw3="spd", target_kw4="enemy")
        if self.hp < 0.10 and self.is_alive():
            self.heal_hp(damage_dealt, healer=self)
        return damage_dealt

    def skill2_logic(self):
        if self.has_effect_that_named(None, None, "AbsorptionShield"):
            multiplier = 3.0
        else:
            multiplier = 2.0
        damage_dealt = self.attack(multiplier=multiplier, repeat=5, target_kw1="n_lowest_attr", target_kw2="1", target_kw3="atk", target_kw4="enemy")
        return damage_dealt

    def skill3(self):
        pass

    def battle_entry_effects(self):
        bri = ReductionShield("Brilliance", 10, True, 0.60, cc_immunity=True)
        bri.additional_name = "Gawain_Brilliance"
        self.apply_effect(bri)


class Pinee(Character):
    """

    Build: 
    """
    def __init__(self, name, lvl, exp=0, equip=None, image=None):
        super().__init__(name, lvl, exp, equip, image)
        self.name = "Pinee"
        self.skill1_description = "Select the ally on the right, apply QG for 20 turns and heal the ally by 300% atk." \
        " Then choose 2 allies of lowest hp percentage, apply Smitten for 20 turns." \
        " QG: Normal damage taken is reduced by 50%, after action, copy random 2 buffs, apply them to allies who has QC effect." \
        " If the selected buff is QG or QC, its duration is set to the original duration." \
        " When same effect is applied, duration is refreshed." \
        " Smitten: After action, recover hp by 300% atk of the effect applier."
        self.skill2_description = "Target 1 ally with highest atk, apply QG for 20 turns, heal the ally by 300% atk and apply Crit Up for 20 turns." \
        " Crit Up: Critrate is increased by 80%."
        self.skill3_description = "Normal attack multiplier is increased by 120% atk."
        self.skill1_description_jp = "右側の味方を選択し、20ターンの間「傾国」を付与し、攻撃力の300%分その味方を治療する。その後、HP割合が最も低い味方2人に20ターンの間「傾心」を付与する。" \
        "傾国：通常ダメージを50%軽減し、行動後、ランダムなバフ2つをコピーして、傾城効果を持つ味方に付与する。選択されたバフが傾国または傾城の場合、その持続時間は元の持続時間に設定される。同じ効果が再度付与された場合、持続時間が更新される。" \
        "傾心：行動後、効果を付与したキャラクターの攻撃力の300%分HPを回復する。"
        self.skill2_description_jp = "攻撃力が最も高い味方1人を対象に、20ターンの間「傾国」を付与し、攻撃力の300%分その味方を治療し、20ターンの間「クリティカル率アップ」を付与する。" \
        "クリティカル率アップ：クリティカル率が80%増加する。"
        self.skill3_description_jp = "通常攻撃の倍率が攻撃力の120%増加する。"
        self.skill1_cooldown_max = 4
        self.skill2_cooldown_max = 4
        # test

    def skill1_logic(self):
        target_ally: Character = self.get_neighbor_ally_right()
        if not target_ally:
            return 0
        # PineQGEffect
        target_ally.apply_effect(PineQGEffect("QG", 20, True, 0.5, False, cover_normal_damage=True, 
                                              cover_status_damage=False))
        self.heal(value=self.atk * 3.0, target_list=[target_ally])
        two_lowest_hp = self.target_selection(keyword="n_lowest_hp_percentage_ally", keyword2="2")
        two_lowest_hp = list(two_lowest_hp)
        for a in two_lowest_hp:
            a.apply_effect(SmittenEffect("Smitten", 20, True, False, heal_value=self.atk * 3.0, effect_applier=self))
        return 0

    def skill2_logic(self):
        target_ally: Character = max(self.ally, key=lambda x: x.atk)
        self.heal(value=self.atk * 3.0, target_list=[target_ally])
        target_ally.apply_effect(PineQGEffect("QG", 20, True, 0.5, False, cover_normal_damage=True, 
                                              cover_status_damage=False))
        target_ally.apply_effect(StatsEffect("Crit Up", 20, True, {"crit": 0.80}))
        return 0

    def skill3(self):
        pass

    def normal_attack(self):
        return self.attack(multiplier=3.2)


class Pine(Character):
    """

    Build: 
    """
    def __init__(self, name, lvl, exp=0, equip=None, image=None):
        super().__init__(name, lvl, exp, equip, image)
        self.name = "Pine"
        self.skill1_description = "Select the ally on the left, apply QC for 20 turns and heal the ally by 300% atk." \
        " Then choose 2 allies of lowest hp percentage, apply Grace for 20 turns." \
        " QC: Status damage taken is reduced by 50%, after action, copy random 2 buffs, apply them to allies who has QG effect." \
        " If the selected buff is QG or QC, its duration is set to the original duration." \
        " When same effect is applied, duration is refreshed." \
        " Grace: Atk and defense is increased by 30%."
        self.skill2_description = "Target 1 ally with highest atk, apply QC for 20 turns, heal the ally by 300% atk and apply Critdmg Up for 20 turns." \
        " Critdmg Up: Critdmg is increased by 100%."
        self.skill3_description = "Normal attack multiplier is increased by 120% atk."
        self.skill1_description_jp = "左側の味方を選択し、20ターンの間「傾城」を付与して攻撃力の300%分その味方を治療する。その後、HP割合が最も低い味方2人を選び、20ターンの間「恩寵」を付与する。傾城：受ける状態異常ダメージが50%減少し、行動後、ランダムなバフを2つコピーして「傾国」効果を持つ味方に適用する。選択されたバフが傾国または傾城の場合、その持続時間は元の持続時間に設定される。同じ効果が再度付与された場合、持続時間が更新される。恩寵：攻撃力と防御力が30%増加する。"
        self.skill2_description_jp = "攻撃力が最も高い味方1人を対象に、20ターンの間「傾城」を付与し、攻撃力の300%分その味方を治療し、20ターンの間「クリティカルダメージアップ」を付与する。クリティカルダメージアップ：クリティカルダメージが100%増加する。"
        self.skill3_description_jp = "通常攻撃の倍率が攻撃力の120%増加する。"
        self.skill1_cooldown_max = 4
        self.skill2_cooldown_max = 4
        # test

    def skill1_logic(self):
        target_ally: Character = self.get_neighbor_ally_left()
        if not target_ally:
            return 0
        # PineQCEffect
        target_ally.apply_effect(PineQCEffect("QC", 20, True, 0.5, False, cover_normal_damage=False, 
                                              cover_status_damage=True))
        self.heal(value=self.atk * 3.0, target_list=[target_ally])
        two_lowest_hp = self.target_selection(keyword="n_lowest_hp_percentage_ally", keyword2="2")
        two_lowest_hp = list(two_lowest_hp)
        for a in two_lowest_hp:
            a.apply_effect(StatsEffect("Grace", 20, True, {"atk": 1.30, "defense": 1.30}))
        return 0

    def skill2_logic(self):
        target_ally: Character = max(self.ally, key=lambda x: x.atk)
        self.heal(value=self.atk * 3.0, target_list=[target_ally])
        target_ally.apply_effect(PineQCEffect("QC", 20, True, 0.5, False, cover_normal_damage=False, 
                                              cover_status_damage=True))
        target_ally.apply_effect(StatsEffect("Critdmg Up", 20, True, {"critdmg": 1.00}))
        return 0

    def skill3(self):
        pass

    def normal_attack(self):
        return self.attack(multiplier=3.2)


class Percival(Character):
    """
    More damage when having absorption shield
    Apply buff to allies that have absorption shield
    Protect all allies
    Build: 
    """
    def __init__(self, name, lvl, exp=0, equip=None, image=None):
        super().__init__(name, lvl, exp, equip, image)
        self.name = "Percival"
        self.skill1_description = "Attack 1 enemy of highest atk with 280% atk 3 times. If you have Absorption Shield, every attack has a 50% chance to" \
        " inflict vulnerability for 20 turns. Vulnerability: final damage taken is increased by 50%."
        self.skill2_description = "Heal all allies by 240% atk, if the ally has Absorption Shield, apply Atk Up to that ally for 24 turns. Atk Up: Atk and Accuracy is increased by 30%."
        self.skill3_description = "At start of battle, apply Dawn Armor to all allies." \
        " When the ally is about to take damage, damage taken is reduced by 25%, then 60% of the damage is taken by you." \
        " Cannot protect against status effect and status damage."
        self.skill1_description_jp = "攻撃力が最も高い敵1体に攻撃力の280%で3回攻撃する。自身に吸収シールドがある場合、各攻撃に50%の確率で対象に20ターンの間「脆弱」を付与する。脆弱：最終ダメージ倍率が50%増加する。"
        self.skill2_description_jp = "全ての味方のHPを攻撃力の240%分回復する。味方に吸収シールドがある場合、その味方に24ターンの間「攻撃力アップ」を付与する。攻撃力アップ：攻撃力と命中が30%増加する。"
        self.skill3_description_jp = "戦闘開始時、全ての味方に「黎明の鎧」を付与する。味方がダメージを受ける際、受けるダメージが25%減少し、その後、ダメージの60%を自分が引き受ける。状態異常および状態異常ダメージに対しては保護できない。"
        self.skill1_cooldown_max = 4
        self.skill2_cooldown_max = 4

    def skill1_logic(self):
        def vulnerability_logic(char, target: Character):
            if char.has_effect_that_named(None, None, "AbsorptionShield"):
                if random.random() < 0.50:
                    target.apply_effect(StatsEffect("Vulnerability", 20, False, {"final_damage_taken_multipler": 0.50}))
        damage_dealt = self.attack(multiplier=2.8, repeat=3, target_kw1="n_highest_attr", target_kw2="1", target_kw3="atk", target_kw4="enemy",
                                   func_after_dmg=vulnerability_logic)
        return damage_dealt

    def skill2_logic(self):
        def func_aeh(healer, target, healing, overhealing):
            if target.has_effect_that_named(None, None, "AbsorptionShield"):
                target.apply_effect(StatsEffect("Atk Up", 24, True, {"atk": 1.30, 'acc': 0.30}))
        self.heal(value=self.atk * 2.4, target_kw1="all_ally", func_after_each_heal=func_aeh)
        return 0

    def skill3(self):
        pass

    def battle_entry_effects(self):
        allies = [x for x in self.ally if x != self]
        for ally in allies:
            e = ProtectedEffect("Dawn Armor", -1, True, False, self, 0.75, 0.6)
            e.can_be_removed_by_skill = False
            ally.apply_effect(e)


class Gareth(Character):
    """
    great with Inaba
    Against high heal efficiency
    Build: 
    """
    def __init__(self, name, lvl, exp=0, equip=None, image=None):
        super().__init__(name, lvl, exp, equip, image)
        self.name = "Gareth"
        self.skill1_description = "Attack 3 close enemies 2 times with 250% atk, if the enemy has more than 150% heal efficiency," \
        " inflict Vulnerability for 20 turns, Vulnerability:" \
        " final damage taken is increased by the difference between their heal efficiency and 150%, the value does not update overtime. If the enemy has more than 300% heal efficiency," \
        " Stun the target for 12 turns and final damage taken is further increased by 50%."
        self.skill2_description = "Target 2 allies of highest atk, if they have more than 150% heal efficiency,"  \
        " their atk is scaled by their heal efficiency for 22 turns, if heal efficiency is more than 300%, defense and speed is also scaled by 50% of heal efficiency."
        self.skill3_description = "After using a skill, heal hp by 200% of defense. At start of battle, apply Very Food to all allies." \
        " When the ally is about to take damage, damage taken is reduced by 25%, then 60% of the damage is taken by you." \
        " Cannot protect against status effect and status damage."
        self.skill1_description_jp = "最も近い敵3体に攻撃力の250%で2回攻撃する。敵の回復効率が150%以上の場合、20ターンの間「脆弱」を付与し、回復効率と150%の差分で最終ダメージ倍率が増加する。この値はターンごとに変化しない。さらに、敵の回復効率が300%以上の場合、対象を12ターンの間スタンさせ、最終ダメージ倍率がさらに50%増加する。"
        self.skill2_description_jp = "攻撃力が最も高い味方2人を対象とし、その回復効率が150%以上の場合、22ターンの間、その攻撃力が回復効率に基づいて比例する。回復効率が300%以上の場合、防御力と速度も回復効率の50%に基づいて比例する。"
        self.skill3_description_jp = "スキル使用後、防御力の200%分HPを回復する。戦闘開始時、全ての味方に「非常食」を付与する。味方がダメージを受ける際、そのダメージが25%減少し、その後のダメージの60%を自分が引き受ける。ただし、状態異常効果および状態異常ダメージからは保護されない。"
        self.skill1_cooldown_max = 4
        self.skill2_cooldown_max = 4

    def skill1_logic(self):
        def stun_logic(char, target: Character):
            if target.heal_efficiency > 1.5 and target.heal_efficiency <= 3.0:
                target.apply_effect(StatsEffect("Vulnerability", 20, False, {"final_damage_taken_multipler": target.heal_efficiency - 1.5}))
            if target.heal_efficiency > 3.0:
                target.apply_effect(StatsEffect("Vulnerability", 20, False, {"final_damage_taken_multipler": target.heal_efficiency - 1.0}))
                target.apply_effect(StunEffect("Stun", 12, False))
        damage_dealt = self.attack(multiplier=2.5, repeat=2, target_kw1="n_enemy_in_front", target_kw2="3", func_after_dmg=stun_logic)
        if self.is_alive():
            self.heal(target_list=[self], value=self.defense * 2.0)
        return damage_dealt

    def skill2_logic(self):
        targets = list(self.target_selection(keyword="n_highest_attr", keyword2="2", keyword3="atk", keyword4="ally"))
        for a in targets:
            if a.heal_efficiency > 1.5:
                a.apply_effect(StatsEffect("Atk Up", 22, True, {"atk": a.heal_efficiency}))
            if a.heal_efficiency > 3.0:
                # 300% heal efficiency: 50% def and spd buff
                a.apply_effect(StatsEffect("Extra Stats Up", 22, True, {"defense": a.heal_efficiency * 0.5, "spd": a.heal_efficiency * 0.5}))

        if self.is_alive():
            self.heal(target_list=[self], value=self.defense * 2.0)
        return 0

    def skill3(self):
        pass

    def battle_entry_effects(self):
        allies = [x for x in self.ally if x != self]
        for ally in allies:
            e = ProtectedEffect("Very Food", -1, True, False, self, 0.75, 0.6)
            e.can_be_removed_by_skill = False
            ally.apply_effect(e)


class Eddie(Character):
    """
    Support ally: when shield apllied, shield value increases by heal efficiency
    Build: 
    """
    def __init__(self, name, lvl, exp=0, equip=None, image=None):
        super().__init__(name, lvl, exp, equip, image)
        self.name = "Eddie"
        self.skill1_description = "Attack 3 closest enemies with 300% atk and inflict Defense Down for 20 turns." \
        " Defense Down: Defense is reduced by 30%."
        self.skill2_description = "Apply a Shield on neighbor allies and an ally of highest atk." \
        " Shield absorbs damage up to 280% of your atk, shield value is scaled 2 times by the percentage of hp lost by the target."
        self.skill3_description = "At start of battle, apply Dating Innovations on all allies." \
        " Dating Innovations: When Absorption Shield is applied on yourself, shield value scales by heal efficiency."
        self.skill1_description_jp = "最も近い3匹の敵に攻撃力の300%で攻撃し、20ターンの間「防御ダウン」を付与する。防御ダウン：防御力が30%減少する。"
        self.skill2_description_jp = "隣接する味方と攻撃力が最も高い味方に「シールド」を付与する。シールドは攻撃力の280%分までのダメージを吸収する。シールドの値は、ターゲットが失ったHPの割合で2回調整される。"
        self.skill3_description_jp = "戦闘開始時、すべての味方に「デートの工夫」を付与する。デートの工夫：自身に吸収シールドが適用される際、シールドの値が回復効率に基づいて増加する。"
        self.skill1_cooldown_max = 3
        self.skill2_cooldown_max = 3

    def skill1_logic(self):
        def defense_down(char, target: Character):
            target.apply_effect(StatsEffect("Defense Down", 20, False, {"defense": 0.70}))
        damage_dealt = self.attack(multiplier=3.00, repeat=1, target_kw1="n_enemy_in_front", target_kw2="3", func_after_dmg=defense_down)
        return damage_dealt

    def skill2_logic(self):
        neighbors = self.get_neighbor_allies_not_including_self()
        if not neighbors:
            return 0
        ally_high_atk = max(self.ally, key=lambda x: x.atk)
        for a in itertools.chain(neighbors, [ally_high_atk]):
            shield_value = self.atk * 2.80
            for i in range(2):
                shield_value *= 1 + (1 - a.hp/a.maxhp)
            a.apply_effect(AbsorptionShield("Shield", -1, True, shield_value, cc_immunity=False))
        return 0

    def skill3(self):
        pass

    def battle_entry_effects(self):
        for a in self.ally:
            di = Effect("Dating Innovations", -1, True, False)
            di.tooltip_str = "When Absorption Shield is applied on yourself, shield value scales by heal efficiency."
            di.tooltip_str_jp = "自分に吸収シールドが付与された場合、シールドの値が回復効率によって比例する。"
            di.can_be_removed_by_skill = False
            di.additional_name = "Eddie_Dating_innovations"
            a.apply_effect(di)


class Brandon(Character):
    """
    Anti heal
    Build: 
    """
    def __init__(self, name, lvl, exp=0, equip=None, image=None):
        super().__init__(name, lvl, exp, equip, image)
        self.name = "Brandon"
        self.skill1_description = "Apply Cat's Gaze on 3 closest enemies for 10 turns," \
        " Cat's Gaze: When healing is received, heal amount is reduced to 0, take damage equal to the 50% of amount of healing in the next turn." \
        " Effect duration is refreshed when same effect is applied."
        self.skill2_description = "Attack 3 closest enemies with 220% atk 2 times, if the enemy has Cat's Gaze, attack with 330% atk 2 times," \
        " remove 1 random active buff and inflict Burn for 20 turns. Burn: Every turn, take damage equal to 30% of atk of effect applier."
        self.skill3_description = "When applying Cat's Gaze, if target hp is above 50%, effect duration is increased by 2 turns."
        self.skill1_description_jp = "最も近い3人の敵に10ターンの間「猫の視線」を付与する。猫の視線：回復を受けた際、回復量が0に減少し、次のターンに回復量の50%に相当するダメージを受ける。同じ効果が再度付与された場合、持続時間が更新される。"
        self.skill2_description_jp = "最も近い3人の敵に攻撃力の220%で2回攻撃する。敵が「猫の視線」を持っている場合、攻撃力の330%で2回攻撃し、ランダムなアクティブバフを1つ解除し、20ターンの間「燃焼」を付与する。燃焼：毎ターン、効果を付与した者の攻撃力の30%に相当するダメージを受ける。"
        self.skill3_description_jp = "「猫の視線」を付与する際、対象のHPが50%以上の場合、効果の持続時間が2ターン延長される。"
        self.skill1_cooldown_max = 4
        self.skill2_cooldown_max = 4

    def skill1_logic(self):
        # DecayEffect
        targets = self.target_selection(keyword="n_enemy_in_front", keyword2="3")
        for t in targets:
            duration = 10
            if t.hp / t.maxhp > 0.50:
                duration += 2
            t.apply_effect(DecayEffect("Cat's Gaze", duration, False, effect_applier=self, damage_transfer_rate=0.50))
        return 0

    def skill2_logic(self):
        def cat_gaze_effect(char, target: Character):
            if target.has_effect_that_named("Cat's Gaze", None, "DecayEffect"):
                target.remove_random_amount_of_buffs(1, allow_infinite_duration=False)
                target.apply_effect(ContinuousDamageEffect("Burn", 20, False, self.atk * 0.30, imposter=self))
        def attack_multiplier_function(attacker, target, number_of_attacks, current_repeat):
            if target.has_effect_that_named("Cat's Gaze", None, "DecayEffect"):
                return 3.30
            return 2.20
        damage_dealt = self.attack(repeat=2, target_kw1="n_enemy_in_front", target_kw2="3", func_after_dmg=cat_gaze_effect,
                                   func_for_multiplier=attack_multiplier_function)
        return damage_dealt


    def skill3(self):
        pass


class Snow(Character):
    """

    Build: 
    """
    def __init__(self, name, lvl, exp=0, equip=None, image=None):
        super().__init__(name, lvl, exp, equip, image)
        self.name = "Snow"
        self.skill1_description = "Attack closest enemy with 300% atk 3 times, if the enemy has Burn, damage is increased by 100%,"
        " otherwise, each attack has a 50% chance to inflict Frozen for 10 turns."
        self.skill2_description = "Attack enemy of highest hp with 200% atk 6 times, each attack has a 25% to freeze the target" \
        " for 10 turns, if the target is already frozen, inflict Weaken for 20 turns and damage is increased by 15% of target's current hp." \
        " Weaken: Atk is reduced by 40%. After the attack, heal yourself by the extra damage dealt."
        self.skill3_description = "Apply Reborn on yourself, when defeated, revive with 100% hp the next turn." \
        " When revived, apply Frozen on yourself for 10 turns."
        self.skill1_description_jp = "最も近い敵に攻撃力の300%で3回攻撃し、対象が「燃焼」を持っている場合、ダメージが100%増加する。それ以外の場合、各攻撃に50%の確率で対象に10ターンの間「氷結」を付与する。"
        self.skill2_description_jp = "HPが最も高い敵に攻撃力の200%で6回攻撃し、各攻撃に25%の確率で対象を10ターンの間「氷結」状態にする。対象が既に氷結状態の場合、20ターンの間「弱化」を付与し、ダメージが対象の現在HPの15%分増加する。弱化：攻撃力が40%減少する。攻撃後、追加ダメージ分のHPを自分が回復する。"
        self.skill3_description_jp = "自身に「新生」を付与する。倒された際、次のターンにHP100%で復活する。復活時、自分に10ターンの間「氷結」を付与する。"
        self.skill1_cooldown_max = 5
        self.skill2_cooldown_max = 5
        self.skill2_extra_damage = 0

    def clear_others(self):
        self.skill2_extra_damage = 0

    def skill1_logic(self):
        def damage_amplify(char, target: Character, damage):
            if target.has_effect_that_named("Burn", None, "ContinuousDamageEffect"):
                return damage * 2.0
            return damage
        def frozen_logic(char, target: Character):
            if random.random() < 0.50:
                target.apply_effect(FrozenEffect("Frozen", 10, False, imposter=self))
        damage_dealt = self.attack(multiplier=3.0, repeat=3, target_kw1="enemy_in_front", func_after_dmg=frozen_logic,
                                   func_damage_step=damage_amplify)
        return damage_dealt

    def skill2_logic(self):
        def damage_amplify(char, target: Character, damage):
            if target.has_effect_that_named("Frozen", None, "FrozenEffect"):
                damage += target.hp * 0.15
                self.skill2_extra_damage += target.hp * 0.15
            return damage
        def freeze_logic(char, target: Character):
            if target.has_effect_that_named("Frozen", None, "FrozenEffect"):
                target.apply_effect(StatsEffect("Weaken", 20, False, {"atk": 0.60}))
            if random.random() < 0.25:
                target.apply_effect(FrozenEffect("Frozen", 10, False, imposter=self))
        damage_dealt = self.attack(multiplier=2.0, repeat=6, func_after_dmg=freeze_logic,
                                   func_damage_step=damage_amplify, target_kw1="n_highest_attr", target_kw2="1", target_kw3="hp", target_kw4="enemy")
        if self.is_alive() and self.skill2_extra_damage > 0:
            self.heal(value=self.skill2_extra_damage, target_list=[self])
            # print(f"Extra damage dealt: {self.skill2_extra_damage}")
        self.skill2_extra_damage = 0
        return damage_dealt

    def skill3(self):
        pass

    def battle_entry_effects(self):
        for i in range(1):
            reborn_eff = RebornEffect("Reborn", -1, True, 1, cc_immunity=False, buff_applier=self)
            reborn_eff.additional_name = "Snow_Reborn"
            reborn_eff.can_be_removed_by_skill = False
            self.apply_effect(reborn_eff)

    def after_revive(self):
        self.apply_effect(FrozenEffect("Frozen", 10, False, self))


class Wyatt(Character):
    """
    Target nearby ally of high atk, when attacking, convert the damage to status damage, atk and acc increased
    Heal ally of low hp 2 times.
    Build: 
    """
    def __init__(self, name, lvl, exp=0, equip=None, image=None):
        super().__init__(name, lvl, exp, equip, image)
        self.name = "Wyatt"
        self.skill1_description = "Select a neighbor ally of highest atk, apply Atk Up and Perfect Disguise for 30 turns." \
        " Atk Up: Atk and Accuracy is increased by 40%." \
        " Perfect Disguise: When attacking and dealing damage with normal damage, convert the damage to status damage. When the same effect is applied, duration is refreshed."
        self.skill2_description = "Target 2 allies of lowest hp percentage, heal the ally with 240% atk 2 times."
        self.skill3_description = "Before normal attack, target a random neighbor ally, reduce all skill cooldown by 1 turn for that ally."
        self.skill1_description_jp = "隣接する味方のうち攻撃力が最も高い1人を選択し、30ターンの間「攻撃アップ」と「完璧な変装」を付与する。攻撃アップ：攻撃力と命中率が40%増加する。完璧な変装：通常ダメージで攻撃し、ダメージを与える際、そのダメージを状態異常ダメージに変換する。同じ効果が再度付与された場合、持続時間が更新される。"
        self.skill2_description_jp = "HP割合が最も低い味方2人を対象にし、攻撃力の240%分でHPを2回回復する。"
        self.skill3_description_jp = "通常攻撃の前に、ランダムな隣接する味方1人を対象にし、その味方の全てのスキルのクールダウンを1ターン短縮する。"
        self.skill1_cooldown_max = 4
        self.skill2_cooldown_max = 4

    def skill1_logic(self):
        neighbor = self.get_neighbor_allies_not_including_self()
        if not neighbor:
            return 0
        ally_high_atk = max(neighbor, key=lambda x: x.atk)
        ally_high_atk.apply_effect(StatsEffect("Atk Up", 30, True, {"atk": 1.40, "acc": 0.40}))
        pd = DamageTypeConvertionEffect("Perfect Disguise", 30, True, False, effect_applier=self, new_damage_type="status")
        pd.additional_name = "Wyatt_Perfect_Disguise"
        ally_high_atk.apply_effect(pd)
        return 0

    def skill2_logic(self):
        self.heal(value=self.atk * 2.4, target_kw1="n_lowest_hp_percentage_ally", target_kw2="2", repeat=2)
        return 0

    def skill3(self):
        pass

    def normal_attack(self):
        neigbor = self.get_neighbor_allies_not_including_self()
        if neigbor:
            target = random.choice(neigbor)
            target.update_cooldown()
            global_vars.turn_info_string += f"{self.name} reduced skill cooldown of {target.name} by 1 turn.\n"
        super().normal_attack()
        return 0


class Galahad(Character):
    """
    
    Build: 
    """
    def __init__(self, name, lvl, exp=0, equip=None, image=None):
        super().__init__(name, lvl, exp, equip, image)
        self.name = "Galahad"
        self.skill1_description = "Apply Dominion on all allies for 30 turns." \
        " Dominion: If your index in party is even(0, 2, 4), atk is decreased by 50%, if your index is odd(1, 3), atk is increased by 50%."
        self.skill2_description = "Attack all enemies whose index in party is odd(1, 3) with 600% atk and Stun the target for 6 turns," \
        " enemies near the attacked targets have their defense reduced by 24% for 24 turns." \
        " If there are no enemies whose index is odd, attack all enemies with 600% atk."
        self.skill3_description = "When defeated, apply Shining Will on 2 allies of lowest hp percentage for 20 turns, damage taken is reduced by 50%."
        self.skill1_description_jp = "全ての味方に30ターンの間「天下縦横」を付与する。天下縦横：自分がパーティ内のインデックスが偶数（0、2、4）の場合、攻撃力が50%減少し、奇数（1、3）の場合、攻撃力が50%増加する。"
        self.skill2_description_jp = "パーティ内のインデックスが奇数（1、3）の全ての敵に攻撃力の600%で攻撃し、6ターンの間「スタン」を付与する。攻撃対象の近くにいる敵は24ターンの間、防御力が24%減少する。奇数インデックスの敵がいない場合、全ての敵に攻撃力の600%で攻撃する。"
        self.skill3_description_jp = "撃破された時、HP割合が最も低い味方2人に20ターンの間「輝く神意」を付与する。輝く神意：受けるダメージが50%減少する。"
        self.skill1_cooldown_max = 4
        self.skill2_cooldown_max = 3

    def skill1_logic(self):
        for a in self.ally:
            if a.get_self_index() % 2 == 0:
                a.apply_effect(StatsEffect("Dominion", 30, False, {"atk": 0.50}))
            else:
                a.apply_effect(StatsEffect("Dominion", 30, True, {"atk": 1.50}))
        return 0

    def skill2_logic(self):
        def defense_down(char, target: Character):
            target.apply_effect(StunEffect("Stun", 6, False))
            neighor = target.get_neighbor_allies_not_including_self()
            if not neighor:
                return
            for n in neighor:
                n.apply_effect(StatsEffect("Defense Down", 24, False, {"defense": 0.76}))
        target_list = [x for x in self.enemyparty if x.get_self_index() % 2 == 1]
        final_list = list(set([enemy for enemy in self.enemy if not enemy.is_hidden()]).intersection(set(target_list)))
        assert len(final_list) <= 2
        if not final_list:
            damage_dealt = self.attack(multiplier=6.0, repeat=1, target_kw1="all_enemy")
            return damage_dealt
        damage_dealt = self.attack(multiplier=6.0, repeat=1, func_after_dmg=defense_down, target_list=final_list)
        return damage_dealt

    def skill3(self):
        pass

    def defeated_by_taken_damage(self, damage, attacker):
        self.update_ally_and_enemy()
        allies = list(self.target_selection(keyword="n_lowest_hp_percentage_ally", keyword2="2"))
        if allies:
            for a in allies:
                a.apply_effect(ReductionShield("Shining Will", 20, True, 0.50, False))


class Ace(Character):
    """
    
    Build: 
    """
    def __init__(self, name, lvl, exp=0, equip=None, image=None):
        super().__init__(name, lvl, exp, equip, image)
        self.name = "Ace"
        self.skill1_description = "All allies have their defense increased by 40% of your defense for 24 turns."
        self.skill2_description = "Apply Sword Art on all enemies for 20 turns." \
        " Sword Art: Whenever taking normal damage, take status damage equal to 30% of the defense of the effect applier."
        self.skill3_description = "At start of battle, apply Judgment on an ally of highest atk." \
        " Judgment: crit, critdmg, accuracy increased by 30%, penetration increased by 10%."
        self.skill1_description_jp = "全ての味方の防御力を、自身の防御力の40%分増加させる。効果は24ターン持続する。"
        self.skill2_description_jp = "全ての敵に20ターンの間「剣舞」を付与する。剣舞：通常ダメージを受けるたびに、この効果を付与した者の防御力の30%分の状態異常ダメージを受ける。"
        self.skill3_description_jp = "戦闘開始時、攻撃力が最も高い味方1人に「審判」を付与する。審判：クリティカル率、クリティカルダメージ、命中率が30%増加し、貫通力が10%増加する。"
        self.skill1_cooldown_max = 4
        self.skill2_cooldown_max = 4

    def skill1_logic(self):
        for a in self.ally:
            a.apply_effect(StatsEffect("Defense Up", 24, True, main_stats_additive_dict={"defense": self.defense * 0.40}))
        return 0

    def skill2_logic(self):
        for e in self.enemy:
            e.apply_effect(StingEffect("Sword Art", 20, False, self.defense * 0.30, self))
        return 0

    def skill3(self):
        pass

    def battle_entry_effects(self):
        ally_high_atk = max(self.ally, key=lambda x: x.atk)
        ally_high_atk.apply_effect(StatsEffect("Judgment", -1, True, {"crit": 0.30, "critdmg": 0.30, "acc": 0.30, "penetration": 0.10}, can_be_removed_by_skill=False))


class AceAL(Character):
    """
    
    Build: 
    """
    def __init__(self, name, lvl, exp=0, equip=None, image=None):
        super().__init__(name, lvl, exp, equip, image)
        self.name = "AceAL"
        self.skill1_description = "All allies have their defense increased by 15% of your defense for 20 turns," \
        " for each ally missing, effect is increased by 15%."
        self.skill2_description = "Apply Sword Art on enemy of highest atk for 20 turns." \
        " Sword Art: Whenever taking normal damage, take status damage equal to 100% of the defense of the effect applier."
        self.skill3_description = "At start of battle, apply Judgment on an ally of highest atk." \
        " Judgment: crit, critdmg, accuracy increased by 40%, atk and penetration increased by 20%."
        self.skill1_description_jp = "全ての味方の防御力を、自身の防御力の15%分増加させる。効果は20ターン持続する。撃破された味方1人につき、効果が15%増加する。"
        self.skill2_description_jp = "攻撃力が最も高い敵に20ターンの間「剣舞」を付与する。剣舞：通常ダメージを受けるたびに、この効果を付与した者の防御力の100%分の状態異常ダメージを受ける。"
        self.skill3_description_jp = "戦闘開始時、攻撃力が最も高い味方1人に「審判」を付与する。審判：クリティカル率、クリティカルダメージ、命中率が40%増加し、攻撃力と貫通力が20%増加する。"
        self.skill1_cooldown_max = 4
        self.skill2_cooldown_max = 4

    def skill1_logic(self):
        missing_allies = 5 - len(self.ally) + 1
        for a in self.ally:
            a.apply_effect(StatsEffect("Defense Up", 20, True, main_stats_additive_dict={"defense": self.defense * 0.15 * missing_allies}))
        return 0

    def skill2_logic(self):
        target = mit.one(self.target_selection(keyword="n_highest_attr", keyword2="1", keyword3="atk", keyword4="enemy"))
        target.apply_effect(StingEffect("Sword Art", 20, False, self.defense, self))
        return 0

    def skill3(self):
        pass

    def battle_entry_effects(self):
        ally_high_atk = max(self.ally, key=lambda x: x.atk)
        ally_high_atk.apply_effect(StatsEffect("Judgment", -1, True, {"crit": 0.40, "critdmg": 0.40, "acc": 0.40, "penetration": 0.20, "atk": 1.20},
                                               can_be_removed_by_skill=False))


class Tom(Character):
    """
    Build: 
    """
    def __init__(self, name, lvl, exp=0, equip=None, image=None):
        super().__init__(name, lvl, exp, equip, image)
        self.name = "Tom"
        self.skill1_description = "Attack random enemies 6 times with 200% atk, each attack has a 20% chance to inflict Defense Down for 20 turns." \
        " Defense Down: Defense is reduced by 30%."
        self.skill2_description = "Attack random enemies 3 times with 300% atk, if target has Burn, damage is increased by 50%."
        self.skill3_description = "Normal attack attack 2 times. At start of battle, apply Falling Petal on yourself and another ally of highest atk." \
        " Falling Petal: The first time when hp falls below 50%, for 30 turns, damage taken is reduced by 90%, " \
        " when this effect triggers, silence for 30 turns."
        self.skill1_description_jp = "ランダムな敵に攻撃力の200%で6回攻撃し、各攻撃には20%の確率で20ターンの間「防御ダウン」を付与する。防御ダウン：防御力が30%減少する。"
        self.skill2_description_jp = "ランダムな敵に攻撃力の300%で3回攻撃し、対象が「燃焼」状態の場合、ダメージが50%増加する。"
        self.skill3_description_jp = "通常攻撃が2回攻撃になる。戦闘開始時、自身と攻撃力が最も高いもう1人の味方に「落桜」を付与する。落桜：初めてHPが50%未満になった時、30ターンの間受けるダメージが90%減少する。この効果が発動すると、30ターンの間「沈黙」状態になる。"
        self.skill1_cooldown_max = 4
        self.skill2_cooldown_max = 4

    def skill1_logic(self):
        def defense_down(char, target: Character):
            target.apply_effect(StatsEffect("Defense Down", 20, False, {"defense": 0.70}))
        damage_dealt = self.attack(multiplier=2.0, repeat=6, func_after_dmg=defense_down)
        return damage_dealt

    def skill2_logic(self):
        def damage_amplify(char, target: Character, damage):
            if target.has_effect_that_named("Burn", None, None):
                return damage * 1.50
            return damage
        damage_dealt = self.attack(multiplier=3.0, repeat=3, func_damage_step=damage_amplify)
        return damage_dealt

    def skill3(self):
        pass

    def normal_attack(self):
        return self.attack(repeat=2)

    def battle_entry_effects(self):
        ally_except_self = [x for x in self.ally if x != self]
        assert len(ally_except_self) < 5
        ally_high_atk = max(ally_except_self, key=lambda x: x.atk)
        eff_to_apply_a = ReductionShield("Harmony", 30, True, 0.9, False)
        eff_to_apply_b = SilenceEffect("Silence", 30, False, False)
        ally_high_atk.apply_effect(FallingPetalEffect("Falling Petal", -1, True, False, self, 0.5,
                                                      effect_to_apply=eff_to_apply_a, another_effect_to_apply=eff_to_apply_b, can_be_removed_by_skill=False))
        self.apply_effect(FallingPetalEffect("Falling Petal", -1, True, False, self, 0.5,
                                            effect_to_apply=eff_to_apply_a, another_effect_to_apply=eff_to_apply_b, can_be_removed_by_skill=False))


class Wolf(Character):
    """
    Build: 
    """
    def __init__(self, name, lvl, exp=0, equip=None, image=None):
        super().__init__(name, lvl, exp, equip, image)
        self.name = "Wolf"
        self.skill1_description = "Attack closest enemy with 700% atk, after the attack, select a neighbor ally of highest atk," \
        " apply Cloud and Rain for 30 turns, Cloud and Rain: maxhp increase by 100%, heal efficiency increase by 50%," \
        " when the same effect is applied, duration is refreshed."
        self.skill2_description = "Attack enemy of lowest hp with 300% atk 2 times, after the attack, heal hp for 2 allies of lowest hp percentage" \
        " by 33% of damage dealt."
        self.skill3_description = "Normal attack attack 3 times, after the attack, for 3 turns, apply Lonesome Rain on yourself," \
        " Lonesome Rain: atk increases by 40%, when the same effect is applied, duration is refreshed."
        self.skill1_description_jp = "最も近い敵に攻撃力の700%で攻撃し、攻撃後、隣接する味方のうち攻撃力が最も高い味方を選び、30ターンの間「雲雨御召」を付与する。雲雨御召：最大HPが100%増加し、回復効率が50%増加する。同じ効果が再度適用された場合、持続時間が更新される。"
        self.skill2_description_jp =  "HPが最も低い敵に攻撃力の300%で2回攻撃し、攻撃後、HP割合が最も低い味方2人のHPを、与えたダメージの33%分回復する。"
        self.skill3_description_jp = "通常攻撃で3回攻撃し、攻撃後、自身に3ターンの間「寂寥の雨」を付与する。寂寥の雨：攻撃力が40%増加する。同じ効果が再度適用された場合、持続時間が更新される。"
        self.skill1_cooldown_max = 4
        self.skill2_cooldown_max = 4

    def skill1_logic(self):
        damage_dealt = self.attack(multiplier=7.0, repeat=1, target_kw1="enemy_in_front")
        neighbor = self.get_neighbor_allies_not_including_self()
        if not neighbor:
            return damage_dealt
        ally_high_atk = max(neighbor, key=lambda x: x.atk)
        cloud_and_rain = StatsEffect("Cloud and Rain", 30, True, {"maxhp": 2.00, "heal_efficiency": 0.50})
        cloud_and_rain.additional_name = "Wolf_Cloud_and_Rain"
        cloud_and_rain.apply_rule = "stack"
        ally_high_atk.apply_effect(cloud_and_rain)
        return damage_dealt

    def skill2_logic(self):
        damage_dealt = self.attack(multiplier=3.0, repeat=2, target_kw1="n_lowest_hp_percentage_enemy", target_kw2="1")
        self.update_ally_and_enemy()
        if self.is_alive():
            allies = list(self.target_selection(keyword="n_lowest_hp_percentage_ally", keyword2="2"))
            if allies:
                self.heal(value=damage_dealt * 0.33, target_list=allies)
        return damage_dealt

    def skill3(self):
        pass

    def normal_attack(self):
        damage_dealt = self.attack(repeat=3)
        if self.is_alive():
            lonesome_rain = StatsEffect("Lonesome Rain", 3, True, {"atk": 1.40})
            lonesome_rain.additional_name = "Wolf_Lonesome_Rain"
            lonesome_rain.apply_rule = "stack"
            self.apply_effect(lonesome_rain)
        return damage_dealt


class Niles(Character):
    """
    Build: 
    """
    def __init__(self, name, lvl, exp=0, equip=None, image=None):
        super().__init__(name, lvl, exp, equip, image)
        self.name = "Niles"
        self.skill1_description = "Apply Apple Wine on ally of highest atk and ally of lowest atk for 25 turns." \
        " Apple Wine: When a active buff effect is applied, its duration is increased by 4 turns."
        self.skill2_description = "Attack enemy of highest hp with 270% atk, for each ally alive, attack 2 more times."
        self.skill3_description = "After using skill2, apply Flower on all allies for 4 turns," \
        " Flower: Damage taken is reduced by 40%, each subsequent damage taken in the same turn is further reduced by 40%."
        self.skill1_description_jp = "攻撃力が最も高い味方と最も低い味方に25ターンの間「林檎酒」を付与する。林檎酒：アクティブなバフ効果が付与された際、その持続時間が4ターン延長される。"
        self.skill2_description_jp = "HPが最も高い敵に攻撃力の270%で攻撃し、生存している味方1人につき、さらに2回攻撃する。"
        self.skill3_description_jp = "スキル2を使用した後、全ての味方に4ターンの間「花」を付与する。花：受けるダメージが40%減少し、同じターン内での2回目以降のダメージはさらに40%減少する。"
        self.skill1_cooldown_max = 4
        self.skill2_cooldown_max = 4

    def skill1_logic(self):
        high_atk = max(self.ally, key=lambda x: x.atk)
        low_atk = min(self.ally, key=lambda x: x.atk)
        apple_wine = DurationBonusEffect("Apple Wine", 25, True, False, self, buff_value=4)
        high_atk.apply_effect(apple_wine)
        low_atk.apply_effect(copy.copy(apple_wine))
        return 0

    def skill2_logic(self):
        amount_of_allies = len(self.ally) * 2
        damage_dealt = self.attack(multiplier=2.7, repeat=amount_of_allies, target_kw1="n_highest_attr", 
                                   target_kw2="1", target_kw3="hp", target_kw4="enemy")
        if self.is_alive():
            for a in self.ally:
                shield = AntiMultiStrikeReductionShield("Flower", 4, True, 0.40, False)
                a.apply_effect(shield)
        return damage_dealt

    def skill3(self):
        pass














# Eqset ideas
# As long as you are alive, damage reduction for allies
# After using a skill, 20% chance to recast the skill
# After using skill1, if skill2 can be used, use skill2
# After using a skill, reset cooldown of the other skill










# class NC(Character):
#     """
#     Character Template
#     Build: 
#     """
#     def __init__(self, name, lvl, exp=0, equip=None, image=None):
#         super().__init__(name, lvl, exp, equip, image)
#         self.name = "NC"
#         self.skill1_description = ""
#         self.skill2_description = ""
#         self.skill3_description = ""
#         self.skill1_description_jp = ""
#         self.skill2_description_jp = ""
#         self.skill3_description_jp = ""
#         self.skill1_cooldown_max = 4
#         self.skill2_cooldown_max = 4

#     def skill1_logic(self):
#         return 0

#     def skill2_logic(self):
#         return 0

#     def skill3(self):
#         pass












































































































































































































