from effect import *
import more_itertools as mit
import random


class Character:
    def __init__(self, name, lvl, exp=0, equip=None, image=None, running=False, logging=False, text_box=None, fineprint_mode="default"):
        if equip is None:
            equip = []
        self.name = name
        self.lvl = lvl
        self.exp = exp
        self.equip = equip
        self.image = [] if image is None else image
        try:
            self.featured_image = self.image[0]
        except IndexError:
            self.featured_image = None
        self.initialize_stats()
        self.calculate_equip_effect()
        self.running = running
        self.logging = logging
        self.text_box = text_box
        self.fineprint_mode = fineprint_mode

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
        self.calculate_equip_effect()
        self.eq_set = self.get_equipment_set()
        self.skill1_cooldown = 0
        self.skill2_cooldown = 0
        self.clear_others()

    def reset_stats(self, resethp=True, resetally=True, resetenemy=True):
        self.initialize_stats(resethp, resetally, resetenemy)

    def calculate_equip_effect(self, resethp=True):
        if self.equip != []:
            for item in self.equip:
                self.maxhp += item.maxhp_flat
                self.atk += item.atk_flat
                self.defense += item.def_flat
                self.spd += item.spd_flat

                self.maxhp *= 1 + item.maxhp_percent
                self.maxhp = int(self.maxhp)
                self.atk *= 1 + item.atk_percent
                self.atk = int(self.atk)
                self.defense *= 1 + item.def_percent
                self.defense = int(self.defense)
                self.spd *= 1 + item.spd
                self.spd = int(self.spd)

                self.maxhp += int(item.maxhp_extra)
                self.atk += int(item.atk_extra)
                self.defense += int(item.def_extra)
                self.spd += int(item.spd_extra)

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

    # Normal attack logic
    def normal_attack(self):
        self.attack("n_random_enemy", "1", "Undefined", 2)

    def skill1(self):
        self.attack("n_random_enemy", "1", "Undefined", 2)

    def skill2(self):
        self.attack("n_random_enemy", "1", "Undefined", 2)

    def target_selection(self, keyword="Undefined", keyword2="Undefined", keyword3="Undefined", keyword4="Undefined", target_list=None):
        # main_character already have .ally and .enemy as list
        # Warning: .isCharmed() and .isConfused() only works for n_random_enemy and n_random_ally, implement this later if needed
        # This function is a generator
        # default : random choice of a single enemy
        if target_list is None:
            target_list = []

        if target_list:
            yield from target_list

        if keyword == "yourself":
            yield self

        elif keyword == "Undefined":
            yield random.choice(self.enemy)

        # n random and all
        elif keyword == "n_random_enemy":
            n = int(keyword2)
            if n > len(self.enemy):
                n = len(self.enemy)
            if self.isCharmed():
                yield from random.sample(self.ally, n)
            elif self.isConfused():
                yield from random.sample(self.enemy + self.ally, n)
            else:
                yield from random.sample(self.enemy, n)
        
        elif keyword == "n_random_ally":
            n = int(keyword2)
            if n > len(self.ally):
                n = len(self.ally)
            if self.isCharmed():
                yield from random.sample(self.enemy, n)
            elif self.isConfused():
                yield from random.sample(self.enemy + self.ally, n)
            else:
                yield from random.sample(self.ally, n)

        elif keyword == "n_random_target":
            n = int(keyword2)
            if n > len(self.ally) + len(self.enemy):
                n = len(self.ally) + len(self.enemy)
            yield from random.sample(self.ally + self.enemy, n)

        # target with low attribute among one party
        elif keyword == "n_lowest_attr":
            n = int(keyword2)
            attr = keyword3
            party = keyword4
            if party == "ally":
                yield from sorted(self.ally, key=lambda x: getattr(x, attr))[:n]
            elif party == "enemy":
                yield from sorted(self.enemy, key=lambda x: getattr(x, attr))[:n]

        elif keyword == "n_highest_attr":
            n = int(keyword2)
            attr = keyword3
            party = keyword4
            if party == "ally":
                yield from sorted(self.ally, key=lambda x: getattr(x, attr), reverse=True)[:n]
            elif party == "enemy":
                yield from sorted(self.enemy, key=lambda x: getattr(x, attr), reverse=True)[:n]

        elif keyword == "n_dead_allies":
            n = int(keyword2)
            yield from mit.take(n, filter(lambda x: x.isDead(), self.party))

        elif keyword == "n_dead_enemies":
            n = int(keyword2)
            yield from mit.take(n, filter(lambda x: x.isDead(), self.enemyparty))

        elif keyword == "random_enemy_pair":
            if len(self.enemy) < 2:
                yield from self.enemy
            else:
                yield from random.choice(list(mit.pairwise(self.enemy)))

        elif keyword == "random_ally_pair":
            if len(self.ally) < 2:
                yield from self.ally
            else:
                yield from random.choice(list(mit.pairwise(self.ally)))

        elif keyword == "random_enemy_triple":
            if len(self.enemy) < 3:
                yield from self.enemy
            else:
                yield from random.choice(list(mit.triplewise(self.enemy)))

        elif keyword == "random_ally_triple":
            if len(self.ally) < 3:
                yield from self.ally
            else:
                yield from random.choice(list(mit.triplewise(self.ally)))

        else:
            raise Exception("Keyword not found.")


    def attack(self, target_kw1="Undefined", target_kw2="Undefined", 
               target_kw3="Undefined", target_kw4="Undefined", multiplier=2, repeat=1, func_after_dmg=None,
               func_damage_step=None, repeat_seq=1, func_after_miss=None, func_after_crit=None,
               always_crit=False, additional_attack_after_dmg=None, always_hit=False, target_list=None) -> int:
        # Warning: DO NOT MESS WITH repeat and repeat_seq TOGETHER
        # -> damage dealt
        global running, text_box
        damage_dealt = 0
        for i in range(repeat):
            if repeat > 1:
                self.updateAllyEnemy()
            try:
                attack_sequence = list(self.target_selection(target_kw1, target_kw2, target_kw3, target_kw4, target_list))
            except Exception as e:
                break
            if repeat_seq > 1:
                attack_sequence = list(mit.repeat_each(attack_sequence, repeat_seq))
            for target in attack_sequence:
                if target.isDead():
                    continue
                if self.isDead():
                    break
                if self.running and self.logging:
                    self.text_box.append_html_text(f"{self.name} is targeting {target.name}.\n")
                fine_print(f"{self.name} is targeting {target.name}.", mode=self.fineprint_mode)
                damage = self.atk * multiplier - target.defense * (1-self.penetration)
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
                    target.takeDamage(final_damage, self)
                    damage_dealt += final_damage
                    if func_after_dmg is not None:
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
            if self.skill1_cooldown == 0 and not self.isSilenced():
                self.skill1()
            elif self.skill2_cooldown == 0 and not self.isSilenced():
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
        return "{:<20s} MaxHP: {:>5d} HP: {:>5d} ATK: {:>4d} DEF: {:>4d} Speed: {:>4d}".format(self.name, self.maxhp, self.hp, self.atk, self.defense, self.spd)

    def tooltip_string(self):
        return f"{self.name}\n" \
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
            f"final damage taken: {self.final_damage_taken_multipler*100:.2f}%\n"

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

    def get_equip_stats(self, ribbon=False):
        str = ""
        if not ribbon:
            for item in self.equip[:2]:
                str += item.print_stats_html()
                str += "\n"
        else:
            for item in self.equip[2:]:
                str += item.print_stats_html()
                str += "\n"
        return str

    # Calculate the max exp for the character
    def calculate_maxexp(self):
        if self.lvl <= 300:
            return self.lvl * 100
        else:
            scaling_factor = (self.lvl - 300) * 0.05  
            return int(100 * self.lvl * (1 + scaling_factor))

    # Level up or down the character
    def level_change(self, increment):
        if increment > 0:
            if self.lvl >= 1000:
                return
        elif increment < 0:
            if self.lvl <= 1:
                return
        
        self.lvl += increment
        buff_copy = [effect for effect in self.buffs if not hasattr(effect, "is_set_effect") or not effect.is_set_effect]
        debuff_copy = [effect for effect in self.debuffs if not hasattr(effect, "is_set_effect") or not effect.is_set_effect]
        self.reset_stats(resetally=False, resetenemy=False)
        self.exp = 0
        self.maxexp = self.calculate_maxexp()
        for effect in buff_copy:
            self.applyEffect(effect)
        for effect in debuff_copy:
            self.applyEffect(effect)

    def isAlive(self):
        return self.hp > 0

    def isDead(self):
        return self.hp <= 0

    def isCharmed(self):
        return self.hasEffect("Charm")
    
    def isConfused(self):
        return self.hasEffect("Confuse")
    
    def isStunned(self):
        return self.hasEffect("Stun")
    
    def isSilenced(self):
        return self.hasEffect("Silence")
    
    def is_sleeping(self):
        return self.hasEffect("Sleep")
    
    def is_frozed(self):
        return self.hasEffect("Frozen")
    
    def can_take_action(self) -> (bool, str):
        if self.isStunned():
            return False, "Stunned"
        if self.is_sleeping():
            return False, "Sleeping"
        if self.is_frozed():
            return False, "Frozen"
        return True, "None"
    
    # Update allies and enemies
    def updateAllyEnemy(self):
        self.ally = [ally for ally in self.ally if not ally.isDead()]
        self.enemy = [enemy for enemy in self.enemy if not enemy.isDead()]

    # Calculate targets
    def checkTargets(self):
        if self.isCharmed():
            return self.ally
        elif self.isConfused():
            return self.ally + self.enemy
        else:
            return self.enemy
        
    # Check if have certain ally
    def hasAlly(self, ally_name):
        return ally_name in [ally.name for ally in self.ally]
    
    # Check if have certain enemy
    def hasEnemy(self, enemy_name):
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
    
    # Check if the character is the only one alive
    def isOnlyOneAlive(self):
        return len(self.ally) == 1
    
    # Check if the character is the only one dead
    def isOnlyOneDead(self):
        return len(self.enemy) == 1

    def updateStats(self, stats, reversed=False) -> (dict, dict, dict):
        prev = {}
        new = {}
        delta = {}
        for attr, value in stats.items():
            if attr in ["maxhp", "hp", "atk", "defense", "spd"]:
                if reversed:
                    new_value = getattr(self, attr) / value
                else:
                    new_value = getattr(self, attr) * value
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

    # Heal the character hp, flat, independent of updateHp
    def healHp(self, value, healer):
        if self.isDead():
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
        return healing, healer, overhealing

    # Revive
    def revive(self, hp_to_revive, hp_percentage_to_revive=0):
        if self.isDead():
            self.hp = hp_to_revive
            self.hp += self.maxhp * hp_percentage_to_revive
            self.hp = int(self.hp)
            if self.running and self.logging:
                self.text_box.append_html_text(f"{self.name} is revived for {self.hp} hp.\n")
            fine_print(f"{self.name} is revived for {self.hp} hp.", mode=self.fineprint_mode)
        else:
            raise Exception(f"{self.name} is not dead. Cannot revive.")
    
    # Heal from regen. This is not a flat heal, but a heal that is based on the character's regen and maxhp/mp, not used
    def regen(self):
        if self.isDead():
            raise Exception
        healing = int(self.maxhp * self.hpregen)
        overhealing = 0
        if self.hp + healing > self.maxhp:
            overhealing = self.hp + healing - self.maxhp
            healing = self.maxhp - self.hp
        self.hp += healing
        if healing > 0:
            if self.running and self.logging:
                self.text_box.append_html_text(f"{self.name} is healed for {healing} HP.\n")
            fine_print(f"{self.name} is regenerated for {healing} HP.", mode=self.fineprint_mode)
        return healing, self, overhealing

    # Take skill or normal attack damage, flat.
    def takeDamage(self, value, attacker=None, func_after_dmg=None):
        if self.running and self.logging:
            self.text_box.append_html_text(f"{self.name} is about to take {value} damage.\n")
        fine_print(f"{self.name} is about to take {value} damage.", mode=self.fineprint_mode)
        if self.isDead():
            fine_print(f"{self.name} is already dead, cannot take damage.", mode=self.fineprint_mode)
            raise Exception
        if value < 0:
            value = 0
        # Attention: final_damage_taken_multipler is calculated before shields effects.
        damage = value * self.final_damage_taken_multipler
        if damage > 0:
            for effect in self.buffs:
                if isinstance(effect, ProtectedEffect):
                    damage = effect.protected_applyEffectDuringDamageStep(self, damage, attacker, func_after_dmg)
                else:
                    damage = effect.applyEffectDuringDamageStep(self, damage)
            for effect in self.debuffs:
                damage = effect.applyEffectDuringDamageStep(self, damage)
        damage = int(damage)
        if damage < 0:
            damage = 0
        if self.hp - damage < 0:
            damage = self.hp
        self.hp -= damage
        if func_after_dmg is not None:
            func_after_dmg(self, damage, attacker)
        self.takeDamage_aftermath(damage, attacker)
        if self.running and self.logging:
            self.text_box.append_html_text(f"{self.name} took {damage} damage.\n")
        fine_print(f"{self.name} took {damage} damage.", mode=self.fineprint_mode)
        return damage, attacker
    
    def takeDamage_aftermath(self, damage, attacker):
        pass

    # Take status damage, flat.
    def takeStatusDamage(self, value, attacker=None):
        if self.running and self.logging:
            self.text_box.append_html_text(f"{self.name} is about to take {value} status damage.\n")
        fine_print(f"{self.name} is about to take {value} status damage.", mode=self.fineprint_mode)
        if self.isDead():
            return 0, attacker
        if value < 0:
            value = 0
        damage = value * self.final_damage_taken_multipler
        if damage > 0:
            for effect in self.buffs:
                damage = effect.applyEffectDuringDamageStep(self, damage)
            for effect in self.debuffs:
                damage = effect.applyEffectDuringDamageStep(self, damage)
        damage = int(damage)
        if damage < 0:
            damage = 0
        if self.hp - damage < 0:
            damage = self.hp
        self.hp -= damage
        if self.running and self.logging:
            self.text_box.append_html_text(f"{self.name} took {damage} status damage.\n")
        fine_print(f"{self.name} took {damage} status damage.", mode=self.fineprint_mode)
        return damage, attacker

    # Take bypass all damage, flat.
    def takeBypassAllDamage(self, value, attacker=None):
        if self.running and self.logging:
            self.text_box.append_html_text(f"{self.name} is about to take {value} bypass all damage.\n")
        fine_print(f"{self.name} is about to take {value} bypass all damage.", mode=self.fineprint_mode)
        if self.isDead():
            raise Exception
        if value < 0:
            value = 0
        damage = value
        damage = int(damage)
        if self.hp - damage < 0:
            damage = self.hp
        if damage < 0:
            raise Exception("damage cannot be negative.")
        self.hp -= damage
        if self.running and self.logging:
            self.text_box.append_html_text(f"{self.name} took {damage} bypass all damage.\n")
        fine_print(f"{self.name} took {damage} bypass all damage.", mode=self.fineprint_mode)
        return damage, attacker

    # Check if character have certain effect.
    def hasEffect(self, effect_name):
        if type(effect_name) != str:
            raise Exception("effect_name must be a string.")
        for effect in self.buffs:
            if effect.name == effect_name:
                return True
        for effect in self.debuffs:
            if effect.name == effect_name:
                return True
        return False

    # Check if character have CC immunity.
    def hasCCImmunity(self):
        for effect in self.buffs:
            if effect.cc_immunity:
                return True
        for effect in self.debuffs:
            if effect.cc_immunity:
                return True
        return False

    # Apply buff or debuff effect to the character
    def applyEffect(self, effect):
        if self.isAlive() and effect.is_buff:
            self.buffs.append(effect)
        elif self.isAlive() and not effect.is_buff:
            # Stun on stunned target will not stack, but refresh the duration
            if effect.name == "Stun" and self.isStunned():
                for d in self.debuffs:
                    if d.name == "Stun":
                        d.duration = effect.duration
                        if self.running and self.logging:
                            self.text_box.append_html_text(f"{effect.name} duration on {self.name} has been refreshed.\n")
                        fine_print(f"{effect.name} duration on {self.name} has been refreshed.", mode=self.fineprint_mode)
                        return
            # Check if self has CC immunity
            if effect.name in ["Stun", "Confuse", "Charm", "Silence", "Sleep", "Frozen"]:
                if self.hasCCImmunity():
                    if self.running and self.logging:
                        self.text_box.append_html_text(f"{self.name} is immune to {effect.name}.\n")
                    fine_print(f"{self.name} is immune to {effect.name}.", mode=self.fineprint_mode)
                    return
            self.debuffs.append(effect)
        if self.running and self.logging:
            self.text_box.append_html_text(f"{effect.name} has been applied on {self.name}.\n")
        fine_print(f"{effect.name} has been applied on {self.name}.", mode=self.fineprint_mode)
        effect.applyEffectOnApply(self)

    # Remove buff or debuff effect from the character
    def removeEffect(self, effect, purge=False):
        # purge: effect is removed without triggering applyEffectOnRemove
        if effect in self.buffs:
            self.buffs.remove(effect)
        elif effect in self.debuffs:
            self.debuffs.remove(effect)
        else:
            raise Exception("Effect not found.")
        if self.running and self.logging:
            self.text_box.append_html_text(f"{effect.name} on {self.name} has been removed.\n")
        fine_print(f"{effect.name} on {self.name} has been removed.", mode=self.fineprint_mode)
        if not purge:
            effect.applyEffectOnRemove(self)

    def try_remove_effect_with_name(self, effect_name, strict=False):
        for effect in self.buffs + self.debuffs:
            if effect.name == effect_name:
                self.removeEffect(effect)
                return True
        if strict:
            raise Exception("Effect with name not found.")
        return False

    # Remove all buffs and debuffs from the character
    def removeAllEffects(self):
        for effect in self.buffs:
            effect.applyEffectOnRemove(self)
        for effect in self.debuffs:
            effect.applyEffectOnRemove(self)
        self.buffs = []
        self.debuffs = []

    # Remove set amount debuffs effect randomly from the character and return the list of removed effects
    def removeRandomDebuffs(self, amount):
        if amount > len(self.debuffs):
            amount = len(self.debuffs)
        if amount == 0:
            return []
        removed_effects = []
        for i in range(amount):
            effect = random.choice(self.debuffs)
            self.removeEffect(effect)
            removed_effects.append(effect)
        return removed_effects

    # Every turn, decrease the duration of all buffs and debuffs by 1. If the duration is 0, remove the effect.
    # And other things.
    def updateEffects(self):
        # Currently, effects are not removed and continue to receive updates even if character is dead. 
        # If we want to do this, remember: Reborn effect should not be removed.
        for effect in self.buffs + self.debuffs:
            if effect.flag_for_remove:
                if self.running and self.logging:
                    self.text_box.append_html_text(f"Condition no longer met: {effect.name} on {self.name}.\n")
                fine_print(f"Condition no longer met: {effect.name} on {self.name}.", mode=self.fineprint_mode)
                self.removeEffect(effect)
                continue
            if effect.duration == -1:
                # if self.running and self.logging:
                #     self.text_box.append_html_text(f"{effect.name} on {self.name} is active.\n")
                # print(f"{effect.name} on {self.name} is active.")
                continue
            effect.decreaseDuration()
            if effect.duration > 0:
                if self.running and self.logging:
                    self.text_box.append_html_text(f"{effect.name} on {self.name} has {effect.duration} turns left.\n")
                fine_print(f"{effect.name} on {self.name} has {effect.duration} turns left.", mode=self.fineprint_mode)
                continue
            if effect.isExpired():
                if self.running and self.logging:
                    self.text_box.append_html_text(f"{effect.name} on {self.name} has expired.\n")
                fine_print(f"{effect.name} on {self.name} has expired.", mode=self.fineprint_mode)
                self.removeEffect(effect)
                effect.applyEffectOnExpire(self)
    
    # Every turn, calculate applyEffectOnTurn effect of all buffs and debuffs. ie. poison, burn, etc.
    def statusEffects(self):
        for effect in self.buffs + self.debuffs:
            effect.applyEffectOnTurn(self)

    def status_effects_at_end_of_turn(self):
        for effect in self.buffs + self.debuffs:
            effect.apply_effect_at_end_of_turn(self)

    def update_cooldown(self):
        if self.skill1_cooldown > 0:
            self.skill1_cooldown -= 1
        if self.skill2_cooldown > 0:
            self.skill2_cooldown -= 1

    def skill_tooltip(self):
        return ""

    def get_equipment_set(self):
        if len(self.equip) != 4:
            return "None"
        if len(set([item.eq_set for item in self.equip])) != 1:
            return "None"
        return self.equip[0].eq_set

    def set_up_equipment_set_effects(self):
        # first, check if self.equip have 4 items. Then, check if the 4 items attribute .eq_set is the same string.
        # After that, we grab that string and apply if if if if if if if if
        # This function is called at the start of the battle. We expect it just do self.applyEffect(some_effect), the effect have -1 duration.
        set_name = self.get_equipment_set()
        for effects in self.buffs + self.debuffs:
            if effects.is_set_effect:
                self.removeEffect(effects)
        if set_name == "None":
            return
        elif set_name == "Arasaka": 
            self.applyEffect(EquipmentSetEffect_Arasaka("Arasaka Set", -1, True, False, running=self.running, logging=self.logging, text_box=self.text_box))
        elif set_name == "KangTao":
            self.applyEffect(EquipmentSetEffect_KangTao("KangTao Set", -1, True, self.atk * 6, False, running=self.running, logging=self.logging, text_box=self.text_box))
        elif set_name == "Militech":
            def condition_func(self):
                return self.hp <= self.maxhp * 0.25
            self.applyEffect(EquipmentSetEffect_Militech("Militech Set", -1, True, {"spd": 2.0}, condition_func))
        elif set_name == "NUSA":
            def stats_dict_function() -> dict:
                allies_alive = len(self.ally) 
                return {"atk": 0.06 * allies_alive + 1 , "defense": 0.06 * allies_alive + 1, "maxhp": 0.06 * allies_alive + 1}
            self.applyEffect(EquipmentSetEffect_NUSA("NUSA Set", -1, True, {"atk": 1.30, "defense": 1.30, "maxhp": 1.30}, stats_dict_function))
        elif set_name == "Sovereign":
            self.applyEffect(EquipmentSetEffect_Sovereign("Sovereign Set", -1, True, {"atk": 1.20}))
        elif set_name == "Snowflake":
            self.applyEffect(EquipmentSetEffect_Snowflake("Snowflake Set", -1, True))
        else:
            raise Exception("Effect not implemented.")
        
    def equipment_set_effects_tooltip(self):
        set_name = self.equip[0].eq_set
        str = "Equipment Set Effects:\n"
        if len(self.equip) != 4 or len(set([item.eq_set for item in self.equip])) != 1:
            str += "Equipment set effects is not active. Equip 4 items of the same set to receive benefits.\n"
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
                "Accumulate 1 stack of Sovereign when taking damage. Each stack increase atk by 20% and last 4 turns. Max 5 stacks.\n"
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
        sides = [i for i in range(1, sides+1)]
        if weights is None:
            weights = [1 for i in range(sides)]
        return random.choices(sides, weights=weights, k=1)[0]

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

    def skill_tooltip(self):
        return f"Skill 1 : {self.skill1_description}\nCooldown : {self.skill1_cooldown} action(s)\n\nSkill 2 : {self.skill2_description}\nCooldown : {self.skill2_cooldown} action(s)\n\nSkill 3 : {self.skill3_description}\n"

    def skill1(self):
        if self.running and self.logging:
            self.text_box.append_html_text(f"{self.name} cast skill 1.\n")
        fine_print(f"{self.name} cast skill 1.", mode=self.fineprint_mode)
        if self.skill1_cooldown > 0:
            raise Exception
        def lillia_effect(self, target, final_damage, always_crit):
            always_crit = True
            for target in target.get_neighbor_allies_not_including_self():
                if target.isAlive():
                    target.takeStatusDamage(final_damage * 0.3 * random.uniform(0.8, 1.2), self)
            return final_damage, always_crit
        damage_dealt = self.attack(multiplier=1.8, repeat=12, func_after_crit=lillia_effect)
        self.skill1_cooldown = 5
        return damage_dealt

    def skill2(self):
        if self.skill2_cooldown > 0:
            raise Exception
        if self.running and self.logging:
            self.text_box.append_html_text(f"{self.name} cast skill 2.\n")
        fine_print(f"{self.name} cast skill 2.", mode=self.fineprint_mode)
        self.applyEffect(ReductionShield("Infinite Oasis", 8, True, 0.35, cc_immunity=True))
        self.skill2_cooldown = 5

    def skill3(self):
        if self.hasEffect("Infinite Oasis"):
            self.healHp(self.maxhp * 0.08, self)

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

    def skill_tooltip(self):
        return f"Skill 1 : {self.skill1_description}\nCooldown : {self.skill1_cooldown} action(s)\n\nSkill 2 : {self.skill2_description}\nCooldown : {self.skill2_cooldown} action(s)\n\nSkill 3 : {self.skill3_description}\n"

    def skill1(self):
        if self.running and self.logging:
            self.text_box.append_html_text(f"{self.name} cast skill 1.\n")
        fine_print(f"{self.name} cast skill 1.", mode=self.fineprint_mode)
        if self.skill1_cooldown > 0:
            raise Exception
        damage_dealt = self.attack(multiplier=2.8, repeat=8)      
        self.skill1_cooldown = 5
        return damage_dealt

    def skill2(self):
        if self.skill2_cooldown > 0:
            raise Exception
        if self.running and self.logging:
            self.text_box.append_html_text(f"{self.name} cast skill 2.\n")
        fine_print(f"{self.name} cast skill 2.", mode=self.fineprint_mode)
        def decrease_speed(self, target):
            stat_dict = {"spd": 0.7}
            target.applyEffect(StatsEffect("Purchased!", 6, False, stat_dict))
        damage_dealt = self.attack(multiplier=6.1, repeat=1, func_after_dmg=decrease_speed)
        self.skill2_cooldown = 5
        return damage_dealt

    def skill3(self):
        pass

    def takeDamage_aftermath(self, damage, attacker):
        if random.randint(1, 100) <= 30:
            attacker.applyEffect(ContinuousDamageEffect("Burn", 3, False, self.atk * 0.5))


class Iris(Character):
    def __init__(self, name, lvl, exp=0, equip=None, image=None):
        super().__init__(name, lvl, exp, equip, image)
        self.name = "Iris"
        self.skill1_description = "320% atk on all enemies."
        self.skill2_description = "320% atk on all enemies, inflict 35% atk continuous damage for 3 turns."
        self.skill3_description = "At start of battle, apply Cancellation Shield to ally with highest atk. Cancellation shield: cancel 1 attack if attack damage exceed 10% of max hp. When the shield is active, gain immunity to CC."

    def skill_tooltip(self):
        return f"Skill 1 : {self.skill1_description}\nCooldown : {self.skill1_cooldown} action(s)\n\nSkill 2 : {self.skill2_description}\nCooldown : {self.skill2_cooldown} action(s)\n\nSkill 3 : {self.skill3_description}\n"

    def skill1(self):
        if self.running and self.logging:
            self.text_box.append_html_text(f"{self.name} cast skill 1.\n")
        fine_print(f"{self.name} cast skill 1.", mode=self.fineprint_mode)
        if self.skill1_cooldown > 0:
            raise Exception
        damage_dealt = self.attack(target_kw1="n_random_enemy",target_kw2="5", multiplier=3.2, repeat=1)            
        self.skill1_cooldown = 5
        return damage_dealt

    def skill2(self):
        if self.skill2_cooldown > 0:
            raise Exception
        if self.running and self.logging:
            self.text_box.append_html_text(f"{self.name} cast skill 2.\n")
        fine_print(f"{self.name} cast skill 2.", mode=self.fineprint_mode)
        def bleed(self, target):
            target.applyEffect(ContinuousDamageEffect("Burn", 3, False, self.atk * 0.35))
        damage_dealt = self.attack(target_kw1="n_random_enemy",target_kw2="5", multiplier=3.2, repeat=1, func_after_dmg=bleed)
        self.skill2_cooldown = 5
        return damage_dealt

    def skill3(self):
        pass

    def battle_entry_effects(self):
        ally_with_highest_atk = mit.one(self.target_selection("n_highest_attr", "1", "atk", "ally"))
        ally_with_highest_atk.applyEffect(CancellationShield("Cancellation Shield", -1, True, 0.1, cc_immunity=True, running=self.running, logging=self.logging, text_box=self.text_box))


class Freya(Character):
    def __init__(self, name, lvl, exp=0, equip=None, image=None):
        super().__init__(name, lvl, exp, equip, image)
        self.name = "Freya"
        self.skill1_description = "620% atk on 1 enemy, 75% chance to silence for 3 turns, always target the enemy with highest ATK."
        self.skill2_description = "520% atk on 1 enemy, always target the enemy with lowest HP."
        self.skill3_description = "Apply Absorption Shield on self if target is fallen by skill 2. Shield will absorb up to 900% of ATK of damage."

    def skill_tooltip(self):
        return f"Skill 1 : {self.skill1_description}\nCooldown : {self.skill1_cooldown} action(s)\n\nSkill 2 : {self.skill2_description}\nCooldown : {self.skill2_cooldown} action(s)\n\nSkill 3 : {self.skill3_description}\n"

    def skill1(self):
        if self.running and self.logging:
            self.text_box.append_html_text(f"{self.name} cast skill 1.\n")
        fine_print(f"{self.name} cast skill 1.", mode=self.fineprint_mode)
        if self.skill1_cooldown > 0:
            raise Exception
        def silence_effect(self, target):
            dice = random.randint(1, 100)
            if dice <= 75:
                target.applyEffect(Effect("Silence", 3, False))
        damage_dealt = self.attack(target_kw1="n_highest_attr",target_kw2="1",target_kw3="atk",target_kw4="enemy", multiplier=6.2, repeat=1, func_after_dmg=silence_effect)
        self.skill1_cooldown = 4
        return damage_dealt

    def skill2(self):
        if self.skill2_cooldown > 0:
            raise Exception
        if self.running and self.logging:
            self.text_box.append_html_text(f"{self.name} cast skill 2.\n")
        fine_print(f"{self.name} cast skill 2.", mode=self.fineprint_mode)
        def apply_shield(self, target):
            if target.isDead():
                self.applyEffect(AbsorptionShield("Absorption Shield", -1, True, self.atk * 9, cc_immunity=False, running=self.running, logging=self.logging, text_box=self.text_box))
        damage_dealt = self.attack(target_kw1="n_lowest_attr",target_kw2="1",target_kw3="hp",target_kw4="enemy", multiplier=5.2, repeat=1, func_after_dmg=apply_shield)

        self.skill2_cooldown = 4
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

    def skill_tooltip(self):
        return f"Skill 1 : {self.skill1_description}\nCooldown : {self.skill1_cooldown} action(s)\n\nSkill 2 : {self.skill2_description}\nCooldown : {self.skill2_cooldown} action(s)\n\nSkill 3 : {self.skill3_description}\n"

    def skill1(self):
        if self.running and self.logging:
            self.text_box.append_html_text(f"{self.name} cast skill 1.\n")
        fine_print(f"{self.name} cast skill 1.", mode=self.fineprint_mode)
        if self.skill1_cooldown > 0:
            raise Exception
        damage_dealt = self.attack(target_kw1="n_random_enemy",target_kw2="5", multiplier=3.0, repeat=1)
        self.healHp(damage_dealt * 0.1, self)    
        self.skill1_cooldown = 5
        return damage_dealt

    def skill2(self):
        if self.skill2_cooldown > 0:
            raise Exception
        if self.running and self.logging:
            self.text_box.append_html_text(f"{self.name} cast skill 2.\n")
        fine_print(f"{self.name} cast skill 2.", mode=self.fineprint_mode)
        def moonlight(self):
            self.applyEffect(ReductionShield("Moonlight", 3, True, 0.9, cc_immunity=False))
        damage_dealt = self.attack(target_kw1="n_random_enemy",target_kw2="5", multiplier=3.0, repeat=1)
        moonlight(self)
        self.skill2_cooldown = 5
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

    def skill_tooltip(self):
        return f"Skill 1 : {self.skill1_description}\nCooldown : {self.skill1_cooldown} action(s)\n\nSkill 2 : {self.skill2_description}\nCooldown : {self.skill2_cooldown} action(s)\n\nSkill 3 : {self.skill3_description}\n"


    def skill1(self):
        if self.running and self.logging:
            self.text_box.append_html_text(f"{self.name} cast skill 1.\n")
        fine_print(f"{self.name} cast skill 1.", mode=self.fineprint_mode)
        if self.skill1_cooldown > 0:
            raise Exception
        damage_dealt = self.attack(multiplier=4.6, repeat=1)
        ally_to_heal = mit.one(self.target_selection(keyword="n_lowest_attr", keyword2="1", keyword3="hp", keyword4="ally"))
        healing, x, y = ally_to_heal.healHp(damage_dealt, self)
        self.healHp(healing * 0.6, self)

        self.skill1_cooldown = 5
        return damage_dealt

    def skill2(self):
        if self.skill2_cooldown > 0:
            raise Exception
        if self.running and self.logging:
            self.text_box.append_html_text(f"{self.name} cast skill 2.\n")
        fine_print(f"{self.name} cast skill 2.", mode=self.fineprint_mode)
        ally_to_heal = mit.one(self.target_selection(keyword="n_lowest_attr", keyword2="1", keyword3="hp", keyword4="ally"))
        healing, x, y = ally_to_heal.healHp(self.atk * 3.5, self)
        self.healHp(healing * 0.6, self)
        ally_to_heal.applyEffect(AbsorptionShield("Shield", -1, True, self.atk * 3.5, cc_immunity=False,running=self.running, logging=self.logging, text_box=self.text_box))
        self.skill2_cooldown = 5
        return 0

    def skill3(self):
        pass


class Ruby(Character):
    def __init__(self, name, lvl, exp=0, equip=None, image=None):
        super().__init__(name, lvl, exp, equip, image)
        self.name = "Ruby"
        self.skill1_description = "400% atk on 3 enemies. 70% chance to inflict stun for 3 turns."
        self.skill2_description = "400% focus atk on 1 enemy for 3 times. Each attack has 50% chance to inflict stun for 3 turns."
        self.skill3_description = "Skill damage is increased by 30% on stunned targets."

    def skill_tooltip(self):
        return f"Skill 1 : {self.skill1_description}\nCooldown : {self.skill1_cooldown} action(s)\n\nSkill 2 : {self.skill2_description}\nCooldown : {self.skill2_cooldown} action(s)\n\nSkill 3 : {self.skill3_description}\n"

    def skill1(self):
        if self.running and self.logging:
            self.text_box.append_html_text(f"{self.name} cast skill 1.\n")
        fine_print(f"{self.name} cast skill 1.", mode=self.fineprint_mode)
        if self.skill1_cooldown > 0:
            raise Exception
        def stun_effect(self, target):
            dice = random.randint(1, 100)
            if dice <= 70:
                target.applyEffect(StunEffect('Stun', duration=3, is_buff=False))
        def stun_amplify(self, target, final_damage):
            if target.hasEffect("Stun"):
                final_damage *= 1.3
            return final_damage
        damage_dealt = self.attack(target_kw1="n_random_enemy",target_kw2="3", multiplier=4.0, repeat=1, func_after_dmg=stun_effect, func_damage_step=stun_amplify)            
        self.skill1_cooldown = 5
        return damage_dealt

    def skill2(self):
        if self.skill2_cooldown > 0:
            raise Exception
        if self.running and self.logging:
            self.text_box.append_html_text(f"{self.name} cast skill 2.\n")
        fine_print(f"{self.name} cast skill 2.", mode=self.fineprint_mode)
        def stun_effect(self, target):
            dice = random.randint(1, 100)
            if dice <= 50:
                target.applyEffect(StunEffect('Stun', duration=3, is_buff=False))
        def stun_amplify(self, target, final_damage):
            if target.hasEffect("Stun"):
                final_damage *= 1.3
            return final_damage
        damage_dealt = self.attack(multiplier=4.0, repeat_seq=3, func_after_dmg=stun_effect, func_damage_step=stun_amplify)
        self.skill2_cooldown = 5
        return damage_dealt

    def skill3(self):
        pass


class Olive(Character):
    def __init__(self, name, lvl, exp=0, equip=None, image=None):
        super().__init__(name, lvl, exp, equip, image)
        self.name = "Olive"
        self.skill1_description = "540% atk on 1 enemy. Decrease target's atk by 50% for 4 turns."
        self.skill2_description = "Heal 3 allies with lowest hp by 270% atk and increase their speed by 40% for 4 turns. "
        self.skill3_description = "Normal attack deals 100% more damage if target has less speed than self."

    def skill_tooltip(self):
        return f"Skill 1 : {self.skill1_description}\nCooldown : {self.skill1_cooldown} action(s)\n\nSkill 2 : {self.skill2_description}\nCooldown : {self.skill2_cooldown} action(s)\n\nSkill 3 : {self.skill3_description}\n"

    def skill1(self):
        if self.running and self.logging:
            self.text_box.append_html_text(f"{self.name} cast skill 1.\n")
        fine_print(f"{self.name} cast skill 1.", mode=self.fineprint_mode)
        if self.skill1_cooldown > 0:
            raise Exception
        def effect(self, target):
            stat_dict = {"atk": 0.5}
            target.applyEffect(StatsEffect("Weaken", 4, False, stat_dict))
        damage_dealt = self.attack(multiplier=5.4, repeat=1, func_after_dmg=effect)             
        self.skill1_cooldown = 5
        return damage_dealt

    def skill2(self):
        if self.skill2_cooldown > 0:
            raise Exception
        fine_print(f"{self.name} cast skill 2.", mode=self.fineprint_mode)
        if self.running and self.logging:
            self.text_box.append_html_text(f"{self.name} cast skill 2.\n")
        ally_to_heal = list(self.target_selection(keyword="n_lowest_attr", keyword2="3", keyword3="hp", keyword4="ally"))
        for ally in ally_to_heal:
            ally.healHp(self.atk * 2.7, self)
            stat_dict = {"spd": 1.4}
            ally.applyEffect(StatsEffect("Tailwind", 4, True, stat_dict))

        self.skill2_cooldown = 5
        return 0

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

    def skill_tooltip(self):
        return f"Skill 1 : {self.skill1_description}\nCooldown : {self.skill1_cooldown} action(s)\n\nSkill 2 : {self.skill2_description}\nCooldown : {self.skill2_cooldown} action(s)\n\nSkill 3 : {self.skill3_description}\n"

    def skill1(self):
        if self.running and self.logging:
            self.text_box.append_html_text(f"{self.name} cast skill 1.\n")
        fine_print(f"{self.name} cast skill 1.", mode=self.fineprint_mode)
        if self.skill1_cooldown > 0:
            raise Exception
        damage_dealt = self.attack(multiplier=2.2, repeat=3)

        neighbors = self.get_neighbor_allies_not_including_self() # list
        for ally in neighbors:
            ally.skill1_cooldown = max(ally.skill1_cooldown - 2, 0)
            ally.skill2_cooldown = max(ally.skill2_cooldown - 2, 0)
            if self.running and self.logging:
                self.text_box.append_html_text(f"{ally.name} skill cooldown reduced by 2.\n")                 
        self.skill1_cooldown = 5
        return damage_dealt

    def skill2(self):
        if self.skill2_cooldown > 0:
            raise Exception
        if self.running and self.logging:
            self.text_box.append_html_text(f"{self.name} cast skill 2.\n")
        fine_print(f"{self.name} cast skill 2.", mode=self.fineprint_mode)
        damage_dealt = self.attack(multiplier=3.5, repeat=1)
        neighbors = self.get_neighbor_allies_not_including_self() # list
        for ally in neighbors:
            ally.removeRandomDebuffs(2)
        self.skill2_cooldown = 5
        return damage_dealt
        
    def skill3(self):
        pass

    def battle_entry_effects(self):
        neighbors = self.get_neighbor_allies_not_including_self()
        for ally in neighbors:
            ally.applyEffect(EffectShield1("Fluffy Protection", -1, True, 0.4, self.atk, False))



class Cerberus(Character):
    def __init__(self, name, lvl, exp=0, equip=None, image=None, execution_threshold=0.15):
        super().__init__(name, lvl, exp, equip, image)
        self.name = "Cerberus"
        self.execution_threshold = execution_threshold

        self.skill1_description = "5 hits on random enemies, 300% atk each hit. Decrease target's def by 10% for each hit. Effect last 3 turns."
        self.skill2_description = "290% focus atk on 1 enemy with lowest hp for 3 times. If target hp is less then 15% during the attack, execute the target."
        self.skill3_description = "On sucessfully executing a target, increase execution threshold by 3%, heal 30% of maxhp and increase atk and critdmg by 30%."

    def clear_others(self):
        self.execution_threshold = 0.15

    def skill_tooltip(self):
        return f"Skill 1 : {self.skill1_description}\nCooldown : {self.skill1_cooldown} action(s)\n\nSkill 2 : {self.skill2_description}\nCooldown : {self.skill2_cooldown} action(s)\n\nSkill 3 : {self.skill3_description}\n\nExecution threshold : {self.execution_threshold*100}%"

    def skill1(self):
        if self.running and self.logging:
            self.text_box.append_html_text(f"{self.name} cast skill 1.\n")
        fine_print(f"{self.name} cast skill 1.", mode=self.fineprint_mode)
        if self.skill1_cooldown > 0:
            raise Exception
        def effect(self, target):
            stat_dict = {"defense": 0.9}
            target.applyEffect(StatsEffect("Clawed", 3, False, stat_dict))
        damage_dealt = self.attack(multiplier=3.0, repeat=5, func_after_dmg=effect)             
        self.skill1_cooldown = 5
        return damage_dealt

    def skill2(self):
        if self.skill2_cooldown > 0:
            raise Exception
        if self.running and self.logging:
            self.text_box.append_html_text(f"{self.name} cast skill 2.\n")
        fine_print(f"{self.name} cast skill 2.", mode=self.fineprint_mode)
        def effect(self, target):
            if target.hp < target.maxhp * self.execution_threshold and not target.isDead():
                target.takeBypassAllDamage(target.hp, self)
                if self.running and self.logging:
                    self.text_box.append_html_text(f"Biribiri! {target.name} is executed by {self.name}.\n")
                fine_print(f"Biribiri! {target.name} is executed by {self.name}.", mode=self.fineprint_mode)
                self.execution_threshold += 0.03
                self.healHp(self.maxhp * 0.3, self)
                stats_dict = {"atk": 1.3, "critdmg": 0.3}
                self.updateStats(stats_dict)
        damage_dealt = self.attack(target_kw1="n_lowest_attr",target_kw2="1",target_kw3="hp",target_kw4="enemy", multiplier=2.9, repeat=1, repeat_seq=3, func_after_dmg=effect)
        self.skill2_cooldown = 5
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

    def skill_tooltip(self):
        return f"Skill 1 : {self.skill1_description}\nCooldown : {self.skill1_cooldown} action(s)\n\nSkill 2 : {self.skill2_description}\nCooldown : {self.skill2_cooldown} action(s)\n\nSkill 3 : {self.skill3_description}\n"

    def skill1(self):
        if self.running and self.logging:
            self.text_box.append_html_text(f"{self.name} cast skill 1.\n")
        fine_print(f"{self.name} cast skill 1.", mode=self.fineprint_mode)
        if self.skill1_cooldown > 0:
            raise Exception
        dice = random.randint(1, 100)
        if dice <= 70:
            damage_dealt = self.attack(multiplier=8.0, repeat=1)
        elif dice <= 90 and dice > 70:
            damage_dealt = self.attack(target_kw1="n_random_ally", target_kw2="1", multiplier=3.0, repeat=1)
        else:
            damage_dealt = self.attack(target_kw1="yourself", multiplier=3.0, repeat=1)
        self.skill1_cooldown = 4
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
            target.healHp(self.atk * 8.0, self)
            revivedice = random.randint(1, 100)
            if revivedice <= 80:
                neighbors = self.get_neighbor_allies_not_including_self(False) 
                dead_neighbors = [x for x in neighbors if x.isDead()]
                if dead_neighbors != []:
                    revive_target = random.choice(dead_neighbors)
                    revive_target.revive(1, 0.8)
        elif pondice <= 90 and pondice > 70:
            if self.running and self.logging:
                self.text_box.append_html_text(f"No effect!\n")
            fine_print(f"No effect.", mode=self.fineprint_mode)
            return 0
        else:
            target.takeDamage(self.atk * 2.0, self)
            return 0

        self.skill2_cooldown = 4
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

    def skill_tooltip(self):
        return f"Skill 1 : {self.skill1_description}\nCooldown : {self.skill1_cooldown} action(s)\n\nSkill 2 : {self.skill2_description}\nCooldown : {self.skill2_cooldown} action(s)\n\nSkill 3 : {self.skill3_description}\n"

    def skill1(self):
        if self.running and self.logging:
            self.text_box.append_html_text(f"{self.name} cast skill 1.\n")
        fine_print(f"{self.name} cast skill 1.", mode=self.fineprint_mode)
        if self.skill1_cooldown > 0:
            raise Exception
        def effect(self, target):
            target.applyEffect(ReductionShield("Crystal Breaker", 3, False, 0.2, False))
        damage_dealt = self.attack(target_kw1="n_random_enemy",target_kw2="3", multiplier=3.0, repeat=1, func_after_dmg=effect)            
        self.skill1_cooldown = 5
        return damage_dealt

    def skill2(self):
        if self.running and self.logging:
            self.text_box.append_html_text(f"{self.name} cast skill 2.\n")
        fine_print(f"{self.name} cast skill 2.", mode=self.fineprint_mode)
        if self.skill2_cooldown > 0:
            raise Exception
        downed_target = 0
        def more_attacks(self, target, is_crit):
            nonlocal downed_target
            if target.isDead():
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
        self.skill2_cooldown = 5
        if downed_target > 0:
            self.healHp(downed_target * 0.1 * self.maxhp, self)
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

    def clear_others(self):
        self.first_time = True

    def skill_tooltip(self):
        return f"Skill 1 : {self.skill1_description}\nCooldown : {self.skill1_cooldown} action(s)\n\nSkill 2 : {self.skill2_description}\nCooldown : {self.skill2_cooldown} action(s)\n\nSkill 3 : {self.skill3_description}\n\nFirst time on skill 2: {self.first_time}"

    def skill1(self):
        if self.running and self.logging:
            self.text_box.append_html_text(f"{self.name} cast skill 1.\n")
        fine_print(f"{self.name} cast skill 1.", mode=self.fineprint_mode)
        if self.skill1_cooldown > 0:
            raise Exception
        def burn_effect(self, target):
            if random.randint(1, 100) <= 80:
                target.applyEffect(ContinuousDamageEffect("Burn", 3, False, self.atk * 0.5))
        damage_dealt = self.attack(target_kw1="n_random_enemy",target_kw2="5", multiplier=2.3, repeat=1, func_after_dmg=burn_effect)         
        self.skill1_cooldown = 5
        return damage_dealt

    def skill2(self):
        if self.running and self.logging:
            self.text_box.append_html_text(f"{self.name} cast skill 2.\n")
        fine_print(f"{self.name} cast skill 2.", mode=self.fineprint_mode)
        if self.skill2_cooldown > 0:
            raise Exception
        if self.first_time:
            self.first_time = False
            for ally in self.ally:
                if ally != self:
                    if random.randint(1, 100) <= 65:
                        ally.applyEffect(RebornEffect("Reborn", -1, True, 0.15, False))
            self.skill2_cooldown = 5
            return 0
        else:
            def burn_effect(self, target):
                if random.randint(1, 100) <= 80:
                    target.applyEffect(ContinuousDamageEffect("Burn", 3, False, self.atk * 0.5))
            damage_dealt = self.attack(target_kw1="random_enemy_pair", multiplier=3.2, repeat=1, func_after_dmg=burn_effect)         
            self.skill2_cooldown = 5
            return damage_dealt   

    def skill3(self):
        pass

    def after_revive(self):
        stat_dict = {"atk": 1.5}
        self.applyEffect(StatsEffect("Reborn", 3, True, stat_dict))

    def battle_entry_effects(self):
        self.applyEffect(RebornEffect("Reborn", -1, True, 0.4, False))


class Bell(Character):
    def __init__(self, name, lvl, exp=0, equip=None, image=None):
        super().__init__(name, lvl, exp, equip, image)
        self.name = "Bell"
        self.skill1_description = "Attack 1 enemy with highest atk 170% atk 5 times."
        self.skill2_description = "Attack 1 enemy with lowest hp 170% atk 6 times. This attack never misses. For each target fallen, trigger an additional attack. Maximum attacks: 8"
        self.skill3_description = "Once per battle, after taking damage, if hp is below 50%, apply absorption shield, absorb damage up to 400% of damage just taken. For 5 turns, damage taken cannot exceed 20% of maxhp."
        self.skill3_used = False

    def skill_tooltip(self):
        return f"Skill 1 : {self.skill1_description}\nCooldown : {self.skill1_cooldown} action(s)\n\nSkill 2 : {self.skill2_description}\nCooldown : {self.skill2_cooldown} action(s)\n\nSkill 3 : {self.skill3_description}\n"

    def clear_others(self):
        self.skill3_used = False

    def skill1(self):
        if self.running and self.logging:
            self.text_box.append_html_text(f"{self.name} cast skill 1.\n")
        fine_print(f"{self.name} cast skill 1.", mode=self.fineprint_mode)
        if self.skill1_cooldown > 0:
            raise Exception
        damage_dealt = self.attack(target_kw1="n_highest_attr",target_kw2="1",target_kw3="atk",target_kw4="enemy", multiplier=1.7, repeat=5)
        self.skill1_cooldown = 5
        return damage_dealt

    def skill2(self):
        if self.skill2_cooldown > 0:
            raise Exception
        if self.running and self.logging:
            self.text_box.append_html_text(f"{self.name} cast skill 2.\n")
        fine_print(f"{self.name} cast skill 2.", mode=self.fineprint_mode)
        downed_target = 0
        def additional_attacks(self, target, is_crit):
            nonlocal downed_target
            if target.isDead() and downed_target < 3:
                downed_target += 1
                if self.running and self.logging:
                    self.text_box.append_html_text(f"{self.name} triggered additional attack.\n")
                fine_print(f"{self.name} triggered additional attack.", mode=self.fineprint_mode)
                return self.attack(target_kw1="n_lowest_attr",target_kw2="1",target_kw3="hp",target_kw4="enemy", multiplier=1.7, repeat=1, additional_attack_after_dmg=additional_attacks, always_hit=True)
            else:
                return 0
        damage_dealt = self.attack(target_kw1="n_lowest_attr",target_kw2="1",target_kw3="hp",target_kw4="enemy", multiplier=1.7, repeat=6, additional_attack_after_dmg=additional_attacks, always_hit=True)
        self.skill2_cooldown = 5    
        return damage_dealt

    def skill3(self):
        pass

    def takeDamage_aftermath(self, damage, attacker):
        if self.skill3_used:
            pass
        else:
            if self.hp < self.maxhp * 0.5:
                self.applyEffect(CancellationShield2("Cancellation Shield", 5, True, 0.2, False))
                self.applyEffect(AbsorptionShield("Shield", -1, True, damage * 4.0, cc_immunity=False, running=self.running, logging=self.logging, text_box=self.text_box))
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

    def skill_tooltip(self):
        return f"Skill 1 : {self.skill1_description}\nCooldown : {self.skill1_cooldown} action(s)\n\nSkill 2 : {self.skill2_description}\nCooldown : {self.skill2_cooldown} action(s)\n\nSkill 3 : {self.skill3_description}\n"

    def skill1(self):
        if self.running and self.logging:
            self.text_box.append_html_text(f"{self.name} cast skill 1.\n")
        fine_print(f"{self.name} cast skill 1.", mode=self.fineprint_mode)
        if self.skill1_cooldown > 0:
            raise Exception
        def stun_effect(self, target):
            target.applyEffect(StunEffect('Stun', duration=2, is_buff=False))
        damage_dealt = self.attack(target_kw1="random_enemy_pair", multiplier=3.5, repeat=1, func_after_dmg=stun_effect)     
        self.skill1_cooldown = 5
        return damage_dealt

    def skill2(self):
        if self.running and self.logging:
            self.text_box.append_html_text(f"{self.name} cast skill 2.\n")
        fine_print(f"{self.name} cast skill 2.", mode=self.fineprint_mode)
        if self.skill2_cooldown > 0:
            raise Exception
        def effect(self, target, final_damage):
            if target.hp > target.maxhp * 0.9:
                final_damage *= 1.5
            return final_damage
        damage_dealt = self.attack(target_kw1="n_highest_attr",target_kw2="1",target_kw3="hp",target_kw4="enemy", multiplier=7.0, repeat=1, func_damage_step=effect)   
        self.skill2_cooldown = 5
        return damage_dealt
        
    def skill3(self):
        pass

    def battle_entry_effects(self):
        allies = [x for x in self.ally if x != self]
        for ally in allies:
            ally.applyEffect(ProtectedEffect("Blessing of Firewood", -1, True, False, self, 0.6))


class Seth(Character):
    def __init__(self, name, lvl, exp=0, equip=None, image=None):
        super().__init__(name, lvl, exp, equip, image)
        self.name = "Seth"
        self.skill1_description = "Attack random enemies 3 times with 280% atk. For each attack, a critical strike will trigger an additional attack. Maximum additional attacks: 3"
        self.skill2_description = "Attack all enemies with 250% atk."
        self.skill3_description = "Every turn, increase crit rate and crit dmg by 1%."

    def skill_tooltip(self):
        return f"Skill 1 : {self.skill1_description}\nCooldown : {self.skill1_cooldown} action(s)\n\nSkill 2 : {self.skill2_description}\nCooldown : {self.skill2_cooldown} action(s)\n\nSkill 3 : {self.skill3_description}\n"

    def skill1(self):
        if self.running and self.logging:
            self.text_box.append_html_text(f"{self.name} cast skill 1.\n")
        fine_print(f"{self.name} cast skill 1.", mode=self.fineprint_mode)
        if self.skill1_cooldown > 0:
            raise Exception
        def additional_attack(self, target, is_crit):
            if is_crit:
                if self.running and self.logging:
                    self.text_box.append_html_text(f"{self.name} triggered additional attack.\n")
                fine_print(f"{self.name} triggered additional attack.", mode=self.fineprint_mode)
                return self.attack(multiplier=2.8, repeat=1)
            else:
                return 0
        damage_dealt = self.attack(multiplier=2.8, repeat=3, additional_attack_after_dmg=additional_attack)
        self.skill1_cooldown = 5
        return damage_dealt

    def skill2(self):
        if self.running and self.logging:
            self.text_box.append_html_text(f"{self.name} cast skill 2.\n")
        fine_print(f"{self.name} cast skill 2.", mode=self.fineprint_mode)
        if self.skill2_cooldown > 0:
            raise Exception
        damage_dealt = self.attack(target_kw1="n_random_enemy",target_kw2="5", multiplier=2.5, repeat=1) 
        self.skill2_cooldown = 5
        return damage_dealt
        
    def skill3(self):
        pass

    def battle_entry_effects(self):
        self.applyEffect(SethEffect("Passive Effect", -1, True, 0.01))


class Chiffon(Character):
    def __init__(self, name, lvl, exp=0, equip=None, image=None):
        super().__init__(name, lvl, exp, equip, image)
        self.name = "Chiffon"
        self.skill1_description = "Increase def by 20%, atk by 10% for 5 turns for all allies. Apply a shield that absorbs damage up to 150% self atk for 3 turns."
        self.skill2_description = "Select random 5 targets, when target is an ally, heal 150% atk, when target is an enemy, attack with 400% atk and apply Sleep with a 50% chance."
        self.skill3_description = "When taking damage that would exceed 10% of maxhp, reduce damage above 10% of maxhp by 60%. For every turn passed, damage reduction effect is reduced by 2%."

    def skill_tooltip(self):
        return f"Skill 1 : {self.skill1_description}\nCooldown : {self.skill1_cooldown} action(s)\n\nSkill 2 : {self.skill2_description}\nCooldown : {self.skill2_cooldown} action(s)\n\nSkill 3 : {self.skill3_description}\n"

    def skill1(self):
        if self.running and self.logging:
            self.text_box.append_html_text(f"{self.name} cast skill 1.\n")
        fine_print(f"{self.name} cast skill 1.", mode=self.fineprint_mode)
        if self.skill1_cooldown > 0:
            raise Exception
        for ally in self.ally:
            ally.applyEffect(StatsEffect("Woof! Woof! Woof!", 5, True, {"defense": 1.2, "atk": 1.1}))
            ally.applyEffect(AbsorptionShield("Woof! Woof! Woof!", 3, True, self.atk * 1.5, cc_immunity=False, running=self.running, logging=self.logging, text_box=self.text_box))
        self.skill1_cooldown = 5
        return 0

    def skill2(self):
        if self.running and self.logging:
            self.text_box.append_html_text(f"{self.name} cast skill 2.\n")
        fine_print(f"{self.name} cast skill 2.", mode=self.fineprint_mode)
        if self.skill2_cooldown > 0:
            raise Exception
        targets = list(self.target_selection(keyword="n_random_target", keyword2="5"))
        enemy_list = []
        for target in targets:
            if target in self.ally:
                target.healHp(self.atk * 1.5, self)
            else:
                enemy_list.append(target)
        def sleep_effect(self, target):
            dice = random.randint(1, 100)
            if dice <= 50:
                target.applyEffect(SleepEffect('Sleep', duration=-1, is_buff=False))
        damage_dealt = self.attack(target_list=enemy_list, multiplier=4.0, repeat=1, func_after_dmg=sleep_effect)
        self.skill2_cooldown = 5
        return damage_dealt
        
    def skill3(self):
        pass

    def battle_entry_effects(self):
        self.applyEffect(EffectShield2("Passive Effect", -1, True, False, damage_reduction=0.6))


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
                    target.applyEffect(StunEffect('Stun', duration=3, is_buff=False))
                    buff_to_remove_list.append(buff)
                if buff.name == "Love Card":
                    target.applyEffect(StatsEffect("Unhealable", 3, False, {"heal_efficiency": -1.0}))
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
        self.applyEffect(Effect("Death Card", -1, True, False))
        if lucky_card_found:
            self.skill1_cooldown = 0
        else:
            self.skill1_cooldown = 5
        dice = random.randint(1, 100)
        if dice <= 30:
            self.applyEffect(Effect("Luck Card", -1, True, False))
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
            ally.applyEffect(ContinuousHealEffect("Regeneration", 4, True, 0.05, True))
            for buff in self.buffs:
                if buff.name == "Death Card":
                    ally.applyEffect(StatsEffect("Crit Dmg Up", 3, True, {"critdmg": 0.3}))
                    buff_to_remove_list.append(buff)
                if buff.name == "Love Card":
                    ally.healHp(self.atk * 3.0, self)
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
            self.skill2_cooldown = 5
        self.buffs = [buff for buff in self.buffs if buff not in buff_to_remove_list]
        self.applyEffect(Effect("Love Card", -1, True, False))
        dice = random.randint(1, 100)
        if dice <= 30:
            self.applyEffect(Effect("Luck Card", -1, True, False))
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
                self.applyEffect(Effect("Luck Card", -1, True, False))
                if self.running and self.logging:
                    self.text_box.append_html_text(f"{self.name} gained Luck Card.\n")
                fine_print(f"{self.name} gained Luck Card.", mode=self.fineprint_mode)

        self.attack(func_after_dmg=effect)

# Other characters not yet implemented:
# Chiffon Cake