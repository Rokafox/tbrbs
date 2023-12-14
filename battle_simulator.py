import os
from equip import *
import copy
import pygame
import pygame_gui
import random
import more_itertools as mit
running = False

class Character:
    def __init__(self, name, lvl, exp=0, equip=None, image=None):
        if equip is None:
            equip = []
        self.name = name
        self.lvl = lvl
        self.exp = exp
        self.equip = equip
        self.image = image
        self.initialize_stats()
        self.calculate_equip_effect()

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

    def target_selection(self, keyword="Undefined", keyword2="Undefined", keyword3="Undefined", keyword4="Undefined"):
        # main_character already have .ally and .enemy as list
        # Warning: .isCharmed() and .isConfused() only works for n_random_enemy and n_random_ally, implement this later if needed
        # This function is a generator
        # default : random choice of a single enemy
        if keyword == "yourself":
            yield self

        elif keyword == "Undefined":
            yield random.choice(self.enemy)

        # n random and all
        elif keyword == "n_random_enemy":
            n = int(keyword2)
            print(n)
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
            # we could use a random choice from pairwise
            yield from random.choice(list(mit.pairwise(self.enemy)))

        elif keyword == "random_ally_pair":
            yield from random.choice(list(mit.pairwise(self.ally)))

        else:
            raise Exception("Keyword not found.")


    def attack(self, target_kw1="Undefined", target_kw2="Undefined", 
               target_kw3="Undefined", target_kw4="Undefined", multiplier=2, repeat=1, func_after_dmg=None,
               func_damage_step=None, repeat_seq=1, func_after_miss=None, func_after_crit=None,
               always_crit=False, additional_attack_after_dmg=None, always_hit=False) -> int:
        # Warning: DO NOT MESS WITH repeat and repeat_seq TOGETHER
        # -> damage dealt
        global running, text_box
        damage_dealt = 0
        for i in range(repeat):
            if repeat > 1:
                self.updateAllyEnemy()
            try:
                attack_sequence = list(self.target_selection(target_kw1, target_kw2, target_kw3, target_kw4))
            except Exception as e:
                break
            if repeat_seq > 1:
                attack_sequence = list(mit.repeat_each(attack_sequence, repeat_seq))
            for target in attack_sequence:
                if target.isDead():
                    continue
                if self.isDead():
                    break
                if running:
                    text_box.append_html_text(f"{self.name} is targeting {target.name}.\n")
                print(f"{self.name} is targeting {target.name}.")
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
                        if running:
                            text_box.append_html_text("Critical!\n")
                        print("Critical!")
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
                        damage_dealt += additional_attack_after_dmg(self, target)
                else:
                    if running:
                        text_box.append_html_text(f"Missed! {self.name} attacked {target.name} but missed.\n")
                    print(f"Missed! {self.name} attacked {target.name} but missed.")

        return damage_dealt


    # Action logic
    def action(self):
        if self.canAction():
            self.update_cooldown()
            if self.skill1_cooldown == 0 and not self.isSilenced():
                self.skill1()
            elif self.skill2_cooldown == 0 and not self.isSilenced():
                self.skill2()
            else:
                self.normal_attack()
        else:
            if running:
                text_box.append_html_text(f"{self.name} cannot act.\n")
            print(f"{self.name} cannot act.")

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
            str += effect.print_stats_html()
            str += "\n"
        str += "=" * 20 + "\n"
        for effect in self.debuffs:
            str += effect.print_stats_html()
            str += "\n"
        return str

    def get_equip_stats(self):
        str = ""
        for item in self.equip:
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

    # Level up the character
    def level_up(self):
        if self.lvl >= 1000:
            return
        self.lvl += 1
        self.reset_stats(resetally=False, resetenemy=False)
        self.exp = 0
        self.maxexp = self.calculate_maxexp()
        self.recalculateEffects()

    # Level down the character
    def level_down(self):
        if self.lvl <= 1:
            return
        self.lvl -= 1
        self.reset_stats(resetally=False, resetenemy=False)
        self.exp = 0
        self.maxexp = self.calculate_maxexp()
        self.recalculateEffects()

    # Check if the character is alive
    def isAlive(self):
        return self.hp > 0

    # Check if the character is dead
    def isDead(self):
        return self.hp <= 0

    # Check if charmed
    def isCharmed(self):
        return self.hasEffect("Charm")
    
    # Check if confused
    def isConfused(self):
        return self.hasEffect("Confuse")
    
    # Check if stunned
    def isStunned(self):
        return self.hasEffect("Stun")
    
    # Check if silenced
    def isSilenced(self):
        return self.hasEffect("Silence")
    
    # Check if asleep
    def isAsleep(self):
        return self.hasEffect("Asleep")
    
    # Check if frozen
    def isFrozen(self):
        return self.hasEffect("Frozen")
    
    # Check if can action
    def canAction(self):
        return not self.isStunned() and not self.isAsleep() and not self.isFrozen()
    
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

    def get_neighbor_allies_including_self(self, get_from_self_ally=True):
        # get_from_self_ally: check adjacent allies, if a neighbor is fallen, continue to check the next one until a valid ally is found
        return get_neighbors(self.ally, self) if get_from_self_ally else get_neighbors(self.party, self)

    def get_neighbor_allies_not_including_self(self, get_from_self_ally=True):
        return get_neighbors(self.ally, self, include_self=False) if get_from_self_ally else get_neighbors(self.party, self, include_self=False)

    # Check if the character is the only one alive
    def isOnlyOneAlive(self):
        return len(self.ally) == 1
    
    # Check if the character is the only one dead
    def isOnlyOneDead(self):
        return len(self.enemy) == 1

    # Update the character's spd, flat or multiplicative
    def updateSpd(self, value, is_flat) -> (int, int):
        prev, new = self.spd, self.spd
        if is_flat:
            new += value
            new = int(new)
            if new < 0:
                new = 0
        else:
            new *= value
            new = int(new)
            if new < 0:
                new = 0
        self.spd = new
        return prev, new
 
    # Update the character's atk, flat or multiplicative
    def updateAtk(self, value, is_flat):
        prev, new = self.atk, self.atk
        if is_flat:
            new += value
            new = int(new)
            if new < 0:
                new = 0
        else:
            new *= value
            new = int(new)
            if new < 0:
                new = 0
        self.atk = new
        return prev, new

    # Update the character's def, flat or multiplicative
    def updateDef(self, value, is_flat):
        prev, new = self.defense, self.defense
        if is_flat:
            new += value
            new = int(new)
            if new < 0:
                new = 0
        else:
            new *= value
            new = int(new)
            if new < 0:
                new = 0
        self.defense = new
        return prev, new

    # Update the character's eva, flat or multiplicative
    def updateEva(self, value, is_flat):
        prev, new = self.eva, self.eva
        if is_flat:
            new += value
        else:
            new *= value
        self.eva = new
        return prev, new
    
    # Update the character's acc, flat or multiplicative
    def updateAcc(self, value, is_flat):
        prev, new = self.acc, self.acc
        if is_flat:
            new += value
        else:
            new *= value
        self.acc = new
        return prev, new
    
    # Update the character's crit, flat or multiplicative
    def updateCrit(self, value, is_flat):
        prev, new = self.crit, self.crit
        if is_flat:
            new += value
        else:
            new *= value
        self.crit = new
        return prev, new
    
    # Update the character's critdmg, flat or multiplicative
    def updateCritdmg(self, value, is_flat):
        prev, new = self.critdmg, self.critdmg
        if is_flat:
            new += value
        else:
            new *= value
        self.critdmg = new
        return prev, new

    # Update the character's critdef, flat or multiplicative
    def updateCritdef(self, value, is_flat):
        prev, new = self.critdef, self.critdef
        if is_flat:
            new += value
        else:
            new *= value
        self.critdef = new
        return prev, new

    # Update the character's penetration, flat or multiplicative
    def updatePenetration(self, value, is_flat):
        prev, new = self.penetration, self.penetration
        if is_flat:
            new += value
        else:
            new *= value
        self.penetration = new
        return prev, new

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
        if running:
            text_box.append_html_text(f"{self.name} is healed for {healing} HP.\n")
        print(f"{self.name} is healed for {healing} HP.")
        return healing, healer, overhealing

    # Revive
    def revive(self, hp_to_revive, hp_percentage_to_revive=0):
        if self.isDead():
            self.hp = hp_to_revive
            self.hp += self.maxhp * hp_percentage_to_revive
            self.hp = int(self.hp)
            if running:
                text_box.append_html_text(f"{self.name} is revived for {self.hp} hp.\n")
            print(f"{self.name} is revived for {self.hp} hp.")
        else:
            raise Exception(f"{self.name} is not dead. Cannot revive.")


    # Update the character's maxhp, flat or multiplicative
    def updateMaxhp(self, value, is_flat):
        prev, new = self.maxhp, self.maxhp
        if is_flat:
            new += value
            new = int(new)
            if new < 0:
                new = 0
        else:
            new *= value
            new = int(new)
            if new < 0:
                new = 0
        self.maxhp = new
        return prev, new

    # Update the character's hpregen, flat or multiplicative
    def updateHpregen(self, value, is_flat):
        prev, new = self.hpregen, self.hpregen
        if is_flat:
            new += value
        else:
            new *= value
        self.hpregen = new
        return prev, new
    
    # Heal from regen. This is not a flat heal, but a heal that is based on the character's regen and maxhp/mp
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
            if running:
                text_box.append_html_text(f"{self.name} is healed for {healing} HP.\n")
            print(f"{self.name} is regenerated for {healing} HP.")
        return healing, self, overhealing

    # Update the character's heal efficiency, flat or multiplicative
    def updateHeal_efficiency(self, value, is_flat):
        prev, new = self.heal_efficiency, self.heal_efficiency
        if is_flat:
            new += value
        else:
            new *= value
        self.heal_efficiency = new
        return prev, new

    # Update the character's final damage reduction, flat or multiplicative
    def updateDamage_reduction(self, value, is_flat):
        prev, new = self.final_damage_taken_multipler, self.final_damage_taken_multipler
        if is_flat:
            new += value
        else:
            new *= value
        self.final_damage_taken_multipler = new
        return prev, new

    # Take skill or normal attack damage, flat.
    def takeDamage(self, value, attacker=None, func_after_dmg=None):
        if running:
            text_box.append_html_text(f"{self.name} is about to take {value} damage.\n")
        print(f"{self.name} is about to take {value} damage.")
        if self.isDead():
            print(f"{self.name} is already dead, cannot take damage.")
            raise Exception
        if value < 0:
            value = 0
        # Attention: final_damage_taken_multipler is calculated before shields effects.
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
        if func_after_dmg is not None:
            func_after_dmg(self, damage, attacker)
        self.takeDamage_aftermath(damage, attacker)
        if running:
            text_box.append_html_text(f"{self.name} took {damage} damage.\n")
        print(f"{self.name} took {damage} damage.")
        return damage, attacker
    
    def takeDamage_aftermath(self, damage, attacker):
        pass

    # Take status damage, flat.
    def takeStatusDamage(self, value, attacker=None):
        if running:
            text_box.append_html_text(f"{self.name} is about to take {value} status damage.\n")
        print(f"{self.name} is about to take {value} status damage.")
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
        if running:
            text_box.append_html_text(f"{self.name} took {damage} status damage.\n")
        print(f"{self.name} took {damage} status damage.")
        return damage, attacker

    # Take bypass all damage, flat.
    def takeBypassAllDamage(self, value, attacker=None):
        if running:
            text_box.append_html_text(f"{self.name} is about to take {value} bypass all damage.\n")
        print(f"{self.name} is about to take {value} bypass all damage.")
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
        if running:
            text_box.append_html_text(f"{self.name} took {damage} bypass all damage.\n")
        print(f"{self.name} took {damage} bypass all damage.")
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
                        if running:
                            text_box.append_html_text(f"{effect.name} duration on {self.name} has been refreshed.\n")
                        print(f"{effect.name} duration on {self.name} has been refreshed.")
                        return
            # Check if self has CC immunity
            if effect.name in ["Stun", "Confuse", "Charm", "Silence", "Asleep", "Frozen"]:
                if self.hasCCImmunity():
                    if running:
                        text_box.append_html_text(f"{self.name} is immune to {effect.name}.\n")
                    print(f"{self.name} is immune to {effect.name}.")
                    return
            self.debuffs.append(effect)
        if running:
            text_box.append_html_text(f"{effect.name} has been applied on {self.name}.\n")
        print(f"{effect.name} has been applied on {self.name}.")
        effect.applyEffectOnApply(self)

    # Recalculate effects on the character
    def recalculateEffects(self):
        if self.buffs != []:
            for effect in self.buffs:
                effect.applyEffectOnApply(self)
        if self.debuffs != []:
            for effect in self.debuffs:
                effect.applyEffectOnApply(self)

    # Remove buff or debuff effect from the character
    def removeEffect(self, effect):
        if effect in self.buffs:
            self.buffs.remove(effect)
        elif effect in self.debuffs:
            self.debuffs.remove(effect)
        if running:
            text_box.append_html_text(f"{effect.name} on {self.name} has been removed.\n")
        print(f"{effect.name} on {self.name} has been removed.")
        effect.applyEffectOnRemove(self)

    # Remove all buffs and debuffs from the character
    def removeAllEffects(self):
        for effect in self.buffs:
            effect.applyEffectOnRemove(self)
        for effect in self.debuffs:
            effect.applyEffectOnRemove(self)
        self.buffs = []
        self.debuffs = []

    # Remove set amount buffs effect randomly from the character and return the list of removed effects
    def removeRandomBuffs(self, amount):
        if amount > len(self.buffs):
            amount = len(self.buffs)
        if amount == 0:
            return []
        removed_effects = []
        for i in range(amount):
            effect = random.choice(self.buffs)
            self.removeEffect(effect)
            removed_effects.append(effect)
        return removed_effects

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
    def updateEffects(self):
        for effect in self.buffs:
            if effect.duration == -1:
                if running:
                    text_box.append_html_text(f"{effect.name} on {self.name} is active.\n")
                print(f"{effect.name} on {self.name} is active.")
            effect.decreaseDuration()
            if effect.duration > 0:
                if running:
                    text_box.append_html_text(f"{effect.name} on {self.name} has {effect.duration} turns left.\n")
                print(f"{effect.name} on {self.name} has {effect.duration} turns left.")
            if effect.isExpired():
                if running:
                    text_box.append_html_text(f"{effect.name} on {self.name} has expired.\n")
                print(f"{effect.name} on {self.name} has expired.")
                self.removeEffect(effect)
                effect.applyEffectOnExpire(self)
        for effect in self.debuffs:
            if effect.duration == -1:
                if running:
                    text_box.append_html_text(f"{effect.name} on {self.name} is active.\n")
                print(f"{effect.name} on {self.name} is active.")
            effect.decreaseDuration()
            if effect.duration > 0:
                if running:
                    text_box.append_html_text(f"{effect.name} on {self.name} has {effect.duration} turns left.\n")
                print(f"{effect.name} on {self.name} has {effect.duration} turns left.")
            if effect.isExpired():
                if running:
                    text_box.append_html_text(f"{effect.name} on {self.name} has expired.\n")
                print(f"{effect.name} on {self.name} has expired.")
                self.removeEffect(effect)
                effect.applyEffectOnExpire(self)
    
    # Every turn, calculate applyEffectOnTurn effect of all buffs and debuffs. ie. poison, burn, etc.
    def statusEffects(self):
        for effect in self.buffs:
            effect.applyEffectOnTurn(self)
        for effect in self.debuffs:
            effect.applyEffectOnTurn(self)

    def update_cooldown(self):
        if self.skill1_cooldown > 0:
            self.skill1_cooldown -= 1
        if self.skill2_cooldown > 0:
            self.skill2_cooldown -= 1

    def skill_tooltip(self):
        return ""


class Lillia(Character):
    def __init__(self, name, lvl, exp=0, equip=None, image=None):
        super().__init__(name, lvl, exp, equip, image)
        self.name = "Lillia"
        self.skill1_description = "12 hits on random enemies, 180% atk each hit. After 1 critical hit, all hits following will be critical and hit nearby targets for 30% of damage."
        self.skill2_description = "For 8 turns, cast Infinite Oasis on self gain immunity to CC and reduce damage taken by 35%."
        self.skill3_description = "Heal 8% of max hp on action when Infinite Oasis is active."

    def skill_tooltip(self):
        return f"Skill 1 : {self.skill1_description}\nCooldown : {self.skill1_cooldown} action(s)\n\nSkill 2 : {self.skill2_description}\nCooldown : {self.skill2_cooldown} action(s)\n\nSkill 3 : {self.skill3_description}\n"

    def skill1(self):
        # 12 hits on random enemies, 180% atk each hit.
        # After 1 critical hit, all hits following will be critical.
        # Nearby targets take 30% damage when critical.
        if running:
            text_box.append_html_text(f"{self.name} cast skill 1.\n")
        print(f"{self.name} cast skill 1.")
        if self.skill1_cooldown > 0:
            raise Exception
        def lillia_effect(self, target, final_damage, always_crit):
            always_crit = True
            for target in target.get_neighbor_allies_not_including_self():
                if target.isAlive():
                    target.takeDamage(final_damage * 0.3 * random.uniform(0.8, 1.2), self)
            return final_damage, always_crit
        damage_dealt = self.attack(multiplier=1.8, repeat=12, func_after_crit=lillia_effect)
        self.skill1_cooldown = 5
        return damage_dealt

    def skill2(self):
        # For 8 turns, gain immunity to CC and reduce damage taken by 35%.
        if self.skill2_cooldown > 0:
            raise Exception
        if running:
            text_box.append_html_text(f"{self.name} cast skill 2.\n")
        print(f"{self.name} cast skill 2.")
        self.applyEffect(ReductionShield("Infinite Oasis", 8, True, 0.35, cc_immunity=True))
        self.skill2_cooldown = 5

    def skill3(self):
        # Heal 8% of max hp on action turn when "Infinite Oasis" is active.
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
        # 8 hits on random enemies, 280% atk each hit.
        if running:
            text_box.append_html_text(f"{self.name} cast skill 1.\n")
        print(f"{self.name} cast skill 1.")
        if self.skill1_cooldown > 0:
            raise Exception
        damage_dealt = self.attack(multiplier=2.8, repeat=8)      
        self.skill1_cooldown = 5
        return damage_dealt

    def skill2(self):
        # 610% atk on random enemy. Target speed -30% for 5 turns.
        if self.skill2_cooldown > 0:
            raise Exception
        if running:
            text_box.append_html_text(f"{self.name} cast skill 2.\n")
        print(f"{self.name} cast skill 2.")
        def decrease_speed(self, target):
            target.applyEffect(SpeedEffect("Speed Down", 5, False, 0.7, False))
        damage_dealt = self.attack(multiplier=6.1, repeat=1, func_after_dmg=decrease_speed)
        self.skill2_cooldown = 5
        return damage_dealt

    def skill3(self):
        # When take normal attack or skill damage, 30% chance to inflict 50% atk continuous damage to attacker for 3 turns.
        pass

    def takeDamage_aftermath(self, damage, attacker):
        if random.randint(1, 100) <= 30:
            attacker.applyEffect(ContinuousDamageEffect("Burn", 3, False, self.atk * 0.5))


class Iris(Character):
    def __init__(self, name, lvl, exp=0, equip=None, image=None):
        super().__init__(name, lvl, exp, equip, image)
        self.name = "Iris"
        self.skill1_description = "320% atk on all enemies."
        self.skill2_description = "340% atk on all enemies, inflict 35% atk continuous damage for 3 turns."
        self.skill3_description = "At start of battle, apply Cancellation Shield to ally with highest atk. Cancellation shield: cancel 1 attack if attack damage exceed 10% of max hp. When the shield is active, gain immunity to CC."

    def skill_tooltip(self):
        return f"Skill 1 : {self.skill1_description}\nCooldown : {self.skill1_cooldown} action(s)\n\nSkill 2 : {self.skill2_description}\nCooldown : {self.skill2_cooldown} action(s)\n\nSkill 3 : {self.skill3_description}\n"


    def skill1(self):
        # 330% atk on all enemies.
        if running:
            text_box.append_html_text(f"{self.name} cast skill 1.\n")
        print(f"{self.name} cast skill 1.")
        if self.skill1_cooldown > 0:
            raise Exception
        damage_dealt = self.attack(target_kw1="n_random_enemy",target_kw2="5", multiplier=3.2, repeat=1)            
        self.skill1_cooldown = 5
        return damage_dealt

    def skill2(self):
        # 350% atk on all enemies, inflict 35% atk continuous damage for 3 turns.
        if self.skill2_cooldown > 0:
            raise Exception
        if running:
            text_box.append_html_text(f"{self.name} cast skill 2.\n")
        print(f"{self.name} cast skill 2.")
        def bleed(self, target):
            target.applyEffect(ContinuousDamageEffect("Burn", 3, False, self.atk * 0.35))
        damage_dealt = self.attack(target_kw1="n_random_enemy",target_kw2="5", multiplier=3.4, repeat=1, func_after_dmg=bleed)
        self.skill2_cooldown = 5
        return damage_dealt

    def skill3(self):
        # At start of battle, apply cancellation shield to ally with highest atk.
        # Cancellation shield: cancel 1 attack if attack damage exceed 10% of max hp.
        # When the shield is active, gain immunity to CC.
        pass


class Freya(Character):
    def __init__(self, name, lvl, exp=0, equip=None, image=None):
        super().__init__(name, lvl, exp, equip, image)
        self.name = "Freya"
        self.skill1_description = "580% atk on 1 enemy, 75% chance to silence for 3 turns, always target the enemy with highest ATK."
        self.skill2_description = "520% atk on 1 enemy, always target the enemy with lowest HP."
        self.skill3_description = "Apply Absorption Shield on self if target is fallen by skill 2. Shield will absorb up to 900% of ATK of damage."

    def skill_tooltip(self):
        return f"Skill 1 : {self.skill1_description}\nCooldown : {self.skill1_cooldown} action(s)\n\nSkill 2 : {self.skill2_description}\nCooldown : {self.skill2_cooldown} action(s)\n\nSkill 3 : {self.skill3_description}\n"

    def skill1(self):
        # 580% atk on 1 enemy, 75% chance to silence for 3 turns, always target the enemy with highest ATK.
        if running:
            text_box.append_html_text(f"{self.name} cast skill 1.\n")
        print(f"{self.name} cast skill 1.")
        if self.skill1_cooldown > 0:
            raise Exception
        def silence_effect(self, target):
            dice = random.randint(1, 100)
            if dice <= 75:
                target.applyEffect(Effect("Silence", 3, False))
        damage_dealt = self.attack(target_kw1="n_highest_attr",target_kw2="1",target_kw3="atk",target_kw4="enemy", multiplier=5.8, repeat=1, func_after_dmg=silence_effect)
        self.skill1_cooldown = 5
        return damage_dealt

    def skill2(self):
        # 480% atk on 1 enemy, always target the enemy with lowest HP. Apply Shield on self if target is fallen. Shield will absorb up to 900% of ATK of damage.
        if self.skill2_cooldown > 0:
            raise Exception
        if running:
            text_box.append_html_text(f"{self.name} cast skill 2.\n")
        print(f"{self.name} cast skill 2.")
        def apply_shield(self, target):
            if target.isDead():
                self.applyEffect(AbsorptionShield("Absorption Shield", -1, True, self.atk * 9, cc_immunity=False))
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
        # attack all targets with 300% atk, recover 10% of damage dealt as hp.
        if running:
            text_box.append_html_text(f"{self.name} cast skill 1.\n")
        print(f"{self.name} cast skill 1.")
        if self.skill1_cooldown > 0:
            raise Exception
        damage_dealt = self.attack(target_kw1="n_random_enemy",target_kw2="5", multiplier=3.0, repeat=1)
        self.healHp(damage_dealt * 0.1, self)    
        self.skill1_cooldown = 5
        return damage_dealt

    def skill2(self):
        # Attack all targets with 300% atk, for next 3 turns, reduce damage taken by 90%.
        if self.skill2_cooldown > 0:
            raise Exception
        if running:
            text_box.append_html_text(f"{self.name} cast skill 2.\n")
        print(f"{self.name} cast skill 2.")
        def moonlight(self):
            self.applyEffect(ReductionShield("Moonlight", 3, True, 0.9, cc_immunity=False))
        damage_dealt = self.attack(target_kw1="n_random_enemy",target_kw2="5", multiplier=3.0, repeat=1)
        moonlight(self)
        self.skill2_cooldown = 5
        return damage_dealt

    def skill3(self):
        # Recover 8% hp of maxhp at start of action. 
        pass


class Clover(Character):
    def __init__(self, name, lvl, exp=0, equip=None, image=None):
        super().__init__(name, lvl, exp, equip, image)
        self.name = "Clover"
        self.skill1_description = "Target 1 ally with lowest hp and 1 random enemy, deal 430% atk damage to enemy and heal ally for 100% of damage dealt."
        self.skill2_description = "Target 1 ally with lowest hp, heal for 350% atk and grant Absorption Shield, absorb damage up to 350% atk."
        self.skill3_description = "Every time an ally is healed by Clover, heal Clover for 40% of that amount."

    def skill_tooltip(self):
        return f"Skill 1 : {self.skill1_description}\nCooldown : {self.skill1_cooldown} action(s)\n\nSkill 2 : {self.skill2_description}\nCooldown : {self.skill2_cooldown} action(s)\n\nSkill 3 : {self.skill3_description}\n"


    def skill1(self):
        # target 1 ally with lowest hp and 1 random enemy, deal 400% atk damage to enemy and heal ally for 100% of damage dealt.
        if running:
            text_box.append_html_text(f"{self.name} cast skill 1.\n")
        print(f"{self.name} cast skill 1.")
        if self.skill1_cooldown > 0:
            raise Exception
        damage_dealt = self.attack(multiplier=4.3, repeat=1)
        ally_to_heal = mit.one(self.target_selection(keyword="n_lowest_attr", keyword2="1", keyword3="hp", keyword4="ally"))
        healing, x, y = ally_to_heal.healHp(damage_dealt, self)
        self.healHp(healing * 0.6, self)

        self.skill1_cooldown = 5
        return damage_dealt

    def skill2(self):
        # target 1 ally with lowest hp, heal for 350% atk grant AbsorptionShield, absorb damage up to 350% atk.
        if self.skill2_cooldown > 0:
            raise Exception
        if running:
            text_box.append_html_text(f"{self.name} cast skill 2.\n")
        print(f"{self.name} cast skill 2.")
        ally_to_heal = mit.one(self.target_selection(keyword="n_lowest_attr", keyword2="1", keyword3="hp", keyword4="ally"))
        healing, x, y = ally_to_heal.healHp(self.atk * 3.5, self)
        self.healHp(healing * 0.6, self)
        ally_to_heal.applyEffect(AbsorptionShield("Shield", -1, True, self.atk * 3.5, cc_immunity=False))
        self.skill2_cooldown = 5
        return 0

    def skill3(self):
        # Every time ally is healed by Clover, heal for 60% of that amount.
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
        # 400% atk on 3 enemies. 70% chance to stun for 3 turns.
        if running:
            text_box.append_html_text(f"{self.name} cast skill 1.\n")
        print(f"{self.name} cast skill 1.")
        if self.skill1_cooldown > 0:
            raise Exception
        def stun_effect(self, target):
            dice = random.randint(1, 100)
            if dice <= 70:
                target.applyEffect(StunEffect(duration=3))
        def stun_amplify(self, target, final_damage):
            if target.hasEffect("Stun"):
                final_damage *= 1.3
            return final_damage
        damage_dealt = self.attack(target_kw1="n_random_enemy",target_kw2="3", multiplier=4.0, repeat=1, func_after_dmg=stun_effect, func_damage_step=stun_amplify)            
        self.skill1_cooldown = 5
        return damage_dealt

    def skill2(self):
        # 400% focus atk on 1 enemy for 3 times. Each attack has 50% chance to stun for 3 turns.
        if self.skill2_cooldown > 0:
            raise Exception
        if running:
            text_box.append_html_text(f"{self.name} cast skill 2.\n")
        print(f"{self.name} cast skill 2.")
        def stun_effect(self, target):
            dice = random.randint(1, 100)
            if dice <= 50:
                target.applyEffect(StunEffect(duration=3))
        def stun_amplify(self, target, final_damage):
            if target.hasEffect("Stun"):
                final_damage *= 1.3
            return final_damage
        damage_dealt = self.attack(multiplier=4.0, repeat_seq=3, func_after_dmg=stun_effect, func_damage_step=stun_amplify)
        self.skill2_cooldown = 5
        return damage_dealt

    def skill3(self):
        # Skill damage is increased by 30% on stunned targets. Not yet implemented.
        pass


class Olive(Character):
    def __init__(self, name, lvl, exp=0, equip=None, image=None):
        super().__init__(name, lvl, exp, equip, image)
        self.name = "Olive"
        self.skill1_description = "530% atk on 1 enemy. Decrease target's atk by 50% for 4 turns."
        self.skill2_description = "Heal 3 allies with lowest hp by 260% atk and increase their speed by 30% for 4 turns. "
        self.skill3_description = "Normal attack deals 65% more damage if target has less speed than self."

    def skill_tooltip(self):
        return f"Skill 1 : {self.skill1_description}\nCooldown : {self.skill1_cooldown} action(s)\n\nSkill 2 : {self.skill2_description}\nCooldown : {self.skill2_cooldown} action(s)\n\nSkill 3 : {self.skill3_description}\n"

    def skill1(self):
        # 480% atk on 1 enemy. Decrease target's atk by 50% for 4 turns.
        if running:
            text_box.append_html_text(f"{self.name} cast skill 1.\n")
        print(f"{self.name} cast skill 1.")
        if self.skill1_cooldown > 0:
            raise Exception
        def effect(self, target):
            target.applyEffect(AttackEffect("ATK Down", 4, False, 0.5, False))
        damage_dealt = self.attack(multiplier=5.3, repeat=1, func_after_dmg=effect)             
        self.skill1_cooldown = 5
        return damage_dealt

    def skill2(self):
        # heal 3 allies by 240% atk with lowest hp and increase their speed by 30% for 4 turns. 
        if self.skill2_cooldown > 0:
            raise Exception
        print(f"{self.name} cast skill 2.")
        if running:
            text_box.append_html_text(f"{self.name} cast skill 2.\n")
        ally_to_heal = list(self.target_selection(keyword="n_lowest_attr", keyword2="3", keyword3="hp", keyword4="ally"))
        for ally in ally_to_heal:
            ally.healHp(self.atk * 2.6, self)
            ally.applyEffect(SpeedEffect("Speed Up", 4, True, 1.3, False))

        self.skill2_cooldown = 5
        return 0

    def skill3(self):
        # Normal attack deals 65% more damage if target has less speed than Olive.
        pass

    def normal_attack(self):
        def effect(self, target, final_damage):
            if target.spd < self.spd:
                final_damage *= 1.65
            return final_damage
        self.attack(func_damage_step=effect)


class Fenrir(Character):
    def __init__(self, name, lvl, exp=0, equip=None, image=None):
        super().__init__(name, lvl, exp, equip, image)
        self.name = "Fenrir"
        self.skill1_description = "3 hits on random enemies, 220% atk each hit. Reduce skill cooldown for neighbor allies by 2 turns."
        self.skill2_description = "350% atk on a random enemy. Remove 2 debuffs for neighbor allies."
        self.skill3_description = "Every turn, apply protection to neighbor allies for 1 turn. When the protected ally below 40% hp is about to take damage, heal the ally for 100% atk."

    def skill_tooltip(self):
        return f"Skill 1 : {self.skill1_description}\nCooldown : {self.skill1_cooldown} action(s)\n\nSkill 2 : {self.skill2_description}\nCooldown : {self.skill2_cooldown} action(s)\n\nSkill 3 : {self.skill3_description}\n"

    def skill1(self):
        # 3 hits on random enemies, 220% atk each hit. Reduce skill cooldown for neighbor allies by 2 turns.
        if running:
            text_box.append_html_text(f"{self.name} cast skill 1.\n")
        print(f"{self.name} cast skill 1.")
        if self.skill1_cooldown > 0:
            raise Exception
        damage_dealt = self.attack(multiplier=2.2, repeat=3)

        neighbors = self.get_neighbor_allies_not_including_self() # list
        for ally in neighbors:
            ally.skill1_cooldown = max(ally.skill1_cooldown - 2, 0)
            ally.skill2_cooldown = max(ally.skill2_cooldown - 2, 0)
            if running:
                text_box.append_html_text(f"{ally.name} skill cooldown reduced by 2.\n")                 
        self.skill1_cooldown = 5
        return damage_dealt

    def skill2(self):
        # 350% atk on random enemy. Remove 2 debuffs for neighbor allies.
        if self.skill2_cooldown > 0:
            raise Exception
        if running:
            text_box.append_html_text(f"{self.name} cast skill 2.\n")
        print(f"{self.name} cast skill 2.")
        damage_dealt = self.attack(multiplier=3.5, repeat=1)
        neighbors = self.get_neighbor_allies_not_including_self() # list
        for ally in neighbors:
            ally.removeRandomDebuffs(2)
        self.skill2_cooldown = 5
        return damage_dealt
        

    def skill3(self):
        # Every turn, apply protection to neighbor allies for 1 turn. When the neighbor ally below 40% hp is about to
        # take damage, heal the ally for 100% atk.
        pass


class Cerberus(Character):
    def __init__(self, name, lvl, exp=0, equip=None, image=None, execution_threshold=0.15):
        super().__init__(name, lvl, exp, equip, image)
        self.name = "Cerberus"
        self.execution_threshold = execution_threshold

        self.skill1_description = "5 hits on random enemies, 300% atk each hit. Decrease target's def by 10% for each hit."
        self.skill2_description = "290% focus atk on 1 enemy with lowest hp for 3 times. If target hp is less then 15% during the attack, execute the target."
        self.skill3_description = "On sucessfully executing a target, increase execution threshold by 3%, heal 30% of maxhp and increase atk and critdmg by 30%."

    def clear_others(self):
        self.execution_threshold = 0.15

    def skill_tooltip(self):
        return f"Skill 1 : {self.skill1_description}\nCooldown : {self.skill1_cooldown} action(s)\n\nSkill 2 : {self.skill2_description}\nCooldown : {self.skill2_cooldown} action(s)\n\nSkill 3 : {self.skill3_description}\n\nExecution threshold : {self.execution_threshold*100}%"

    def skill1(self):
        # 5 hits on random enemies, 320% atk each hit. Decrease target's def by 10% for each sucessful hit after the attack.
        if running:
            text_box.append_html_text(f"{self.name} cast skill 1.\n")
        print(f"{self.name} cast skill 1.")
        if self.skill1_cooldown > 0:
            raise Exception
        def effect(self, target):
            target.applyEffect(DefenseEffect("Defence Down", 5, False, 0.9, False))
        damage_dealt = self.attack(multiplier=3.0, repeat=5, func_after_dmg=effect)             
        self.skill1_cooldown = 5
        return damage_dealt

    def skill2(self):
        # 300% focus atk on 1 enemy with lowest hp for 3 times. 
        # If target hp is less then 15% during the attack, execute the target.
        if self.skill2_cooldown > 0:
            raise Exception
        if running:
            text_box.append_html_text(f"{self.name} cast skill 2.\n")
        print(f"{self.name} cast skill 2.")
        def effect(self, target):
            if target.hp < target.maxhp * self.execution_threshold and not target.isDead():
                target.takeBypassAllDamage(target.hp, self)
                if running:
                    text_box.append_html_text(f"Biribiri! {target.name} is executed by {self.name}.\n")
                print(f"Biribiri! {target.name} is executed by {self.name}.")
                self.execution_threshold += 0.03
                self.healHp(self.maxhp * 0.3, self)
                self.updateAtk(1.3, False)
                self.updateCritdmg(0.3, True)
        damage_dealt = self.attack(target_kw1="n_lowest_attr",target_kw2="1",target_kw3="hp",target_kw4="enemy", multiplier=2.9, repeat=1, repeat_seq=3, func_after_dmg=effect)
        self.skill2_cooldown = 5
        return damage_dealt

    def skill3(self):
        # On sucessfully executing a target, increase execution threshold by 3%,
        # heal 30% of maxhp and increase atk and critdmg by 30%.
        pass


class Pepper(Character):
    def __init__(self, name, lvl, exp=0, equip=None, image=None):
        super().__init__(name, lvl, exp, equip, image)
        self.name = "Pepper"
        self.skill1_description = "770% atk on 1 enemy, 70% success rate, 20% chance to hit an ally with 300% atk, 10% chance to hit self with 300% atk."
        self.skill2_description = "Heal an ally with lowest hp percentage with 770% atk, 70% success rate, 20% chance to have no effect, 10% chance to damage the ally with 200% atk."
        self.skill3_description = "On a successful healing with skill 2, 80% chance to accidently revive a neighbor ally with 80% hp."

    def skill_tooltip(self):
        return f"Skill 1 : {self.skill1_description}\nCooldown : {self.skill1_cooldown} action(s)\n\nSkill 2 : {self.skill2_description}\nCooldown : {self.skill2_cooldown} action(s)\n\nSkill 3 : {self.skill3_description}\n"

    def skill1(self):
        if running:
            text_box.append_html_text(f"{self.name} cast skill 1.\n")
        print(f"{self.name} cast skill 1.")
        if self.skill1_cooldown > 0:
            raise Exception
        dice = random.randint(1, 100)
        if dice <= 70:
            damage_dealt = self.attack(multiplier=7.7, repeat=1)
        elif dice <= 90 and dice > 70:
            damage_dealt = self.attack(target_kw1="n_random_ally", target_kw2="1", multiplier=3.0, repeat=1)
        else:
            damage_dealt = self.attack(target_kw1="yourself", multiplier=3.0, repeat=1)
        self.skill1_cooldown = 4
        return damage_dealt

    def skill2(self):
        if self.skill2_cooldown > 0:
            raise Exception
        if running:
            text_box.append_html_text(f"{self.name} cast skill 2.\n")
        print(f"{self.name} cast skill 2.")
        target = mit.one(self.target_selection(keyword="n_lowest_attr", keyword2="1", keyword3="hp", keyword4="ally"))
        pondice = random.randint(1, 100)
        if pondice <= 70:
            target.healHp(self.atk * 7.7, self)
            revivedice = random.randint(1, 100)
            if revivedice <= 80:
                neighbors = self.get_neighbor_allies_not_including_self(False) 
                dead_neighbors = [x for x in neighbors if x.isDead()]
                if dead_neighbors != []:
                    revive_target = random.choice(dead_neighbors)
                    revive_target.revive(1, 0.8)
        elif pondice <= 90 and pondice > 70:
            if running:
                text_box.append_html_text(f"No effect!\n")
            print(f"No effect.")
            return 0
        else:
            target.takeDamage(self.atk * 2.0, self)

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
        if running:
            text_box.append_html_text(f"{self.name} cast skill 1.\n")
        print(f"{self.name} cast skill 1.")
        if self.skill1_cooldown > 0:
            raise Exception
        def effect(self, target):
            target.applyEffect(ReductionShield("Crystal Breaker", 3, False, 0.2, False))
        damage_dealt = self.attack(target_kw1="n_random_enemy",target_kw2="3", multiplier=3.0, repeat=1, func_after_dmg=effect)            
        self.skill1_cooldown = 5
        return damage_dealt

    def skill2(self):
        if running:
            text_box.append_html_text(f"{self.name} cast skill 2.\n")
        print(f"{self.name} cast skill 2.")
        if self.skill2_cooldown > 0:
            raise Exception
        downed_target = 0
        def more_attacks(self, target):
            nonlocal downed_target
            if target.isDead():
                downed_target += 1
            dice = random.randint(1, 100)
            if dice <= 40:
                if running:
                    text_box.append_html_text(f"{self.name} triggered additional attack.\n")
                print(f"{self.name} triggered additional attack.")
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
        if running:
            text_box.append_html_text(f"{self.name} cast skill 1.\n")
        print(f"{self.name} cast skill 1.")
        if self.skill1_cooldown > 0:
            raise Exception
        def burn_effect(self, target):
            if random.randint(1, 100) <= 80:
                target.applyEffect(ContinuousDamageEffect("Burn", 3, False, self.atk * 0.5))
        damage_dealt = self.attack(target_kw1="n_random_enemy",target_kw2="5", multiplier=2.3, repeat=1, func_after_dmg=burn_effect)         
        self.skill1_cooldown = 5
        return damage_dealt

    def skill2(self):
        if running:
            text_box.append_html_text(f"{self.name} cast skill 2.\n")
        print(f"{self.name} cast skill 2.")
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
        if running:
            text_box.append_html_text(f"{self.name} cast skill 1.\n")
        print(f"{self.name} cast skill 1.")
        if self.skill1_cooldown > 0:
            raise Exception
        damage_dealt = self.attack(target_kw1="n_highest_attr",target_kw2="1",target_kw3="atk",target_kw4="enemy", multiplier=1.7, repeat=5)
        self.skill1_cooldown = 5
        return damage_dealt

    def skill2(self):
        if self.skill2_cooldown > 0:
            raise Exception
        if running:
            text_box.append_html_text(f"{self.name} cast skill 2.\n")
        print(f"{self.name} cast skill 2.")
        downed_target = 0
        def additional_attacks(self, target):
            nonlocal downed_target
            if target.isDead() and downed_target < 3:
                downed_target += 1
                if running:
                    text_box.append_html_text(f"{self.name} triggered additional attack.\n")
                print(f"{self.name} triggered additional attack.")
                return self.attack(target_kw1="n_lowest_attr",target_kw2="1",target_kw3="hp",target_kw4="enemy", multiplier=1.7, repeat=1, additional_attack_after_dmg=additional_attacks, always_hit=True)
            else:
                return 0
        damage_dealt = self.attack(target_kw1="n_lowest_attr",target_kw2="1",target_kw3="hp",target_kw4="enemy", multiplier=1.7, repeat=6, additional_attack_after_dmg=additional_attacks, always_hit=True)
        self.skill2_cooldown = 5    
        return damage_dealt

    def skill3(self):
        # No effect 
        pass

    def takeDamage_aftermath(self, damage, attacker):
        if self.skill3_used:
            pass
        else:
            if self.hp < self.maxhp * 0.5:
                self.applyEffect(CancellationShield2("Cancellation Shield", 5, True, 0.2, False))
                self.applyEffect(AbsorptionShield("Shield", -1, True, damage * 4.0, cc_immunity=False))
                self.skill3_used = True
            return damage

#-----------------------------------------
#-----------------------------------------
class Effect:
    def __init__(self, name, duration, is_buff, cc_immunity=False, delay_trigger=0,**kwargs):
        self.name = name
        self.duration = duration
        self.is_buff = bool(is_buff)
        self.cc_immunity = bool(cc_immunity)
        self.delay_trigger = delay_trigger # number of turns before effect is triggered
    
    def isPermanent(self):
        return self.duration == -1
    
    def isExpired(self):
        return self.duration == 0
    
    def isNotExpired(self):
        return self.duration > 0
    
    def decreaseDuration(self):
        if self.duration > 0:
            self.duration -= 1
    
    def applyEffectOnApply(self, character):
        pass
    
    def applyEffectOnTurn(self, character):
        self.delay_trigger = max(self.delay_trigger - 1, 0)
        if self.delay_trigger == 0:
            self.applyEffectOnTrigger(character)

    def applyEffectOnTrigger(self, character):
        pass

    def applyEffectOnExpire(self, character):
        pass
    
    def applyEffectOnRemove(self, character):
        pass

    def applyEffectDuringDamageStep(self, character, damage):
        return damage

    def __str__(self):
        return self.name
    
    def print_stats_html(self):
        color_buff = "#659a00"
        color_debuff = "#ff0000"
        if self.is_buff:
            if self.duration == -1:
                string = "<font color=" + color_buff + ">" + self.name + ": Permanent</font>" + "\n"
            else:
                string = "<font color=" + color_buff + ">" + self.name + ": " + str(self.duration) + " turn(s) remaining</font>" + "\n"
        else:
            if self.duration == -1:
                string = "<font color=" + color_debuff + ">" + self.name + ": Permanent</font>" + "\n"
            else:
                string = "<font color=" + color_debuff + ">" + self.name + ": " + str(self.duration) + " turn(s) remaining</font>" + "\n"
        if self.cc_immunity:
            string += "This effect grants CC immunity.\n"
        if self.delay_trigger > 0:
            string += "Trigger in " + str(self.delay_trigger) + " turn(s)\n"
        string += self.tooltip_description()
        return string
    
    def tooltip_description(self):
        return "No description available."
    

# Some common effects
# ---------------------------------------------------------
# Stun effect
class StunEffect(Effect):
    def __init__(self, duration, cc_immunity=False, delay_trigger=0):
        self.duration = duration
        self.name = "Stun"
        self.is_buff = False
        self.cc_immunity = cc_immunity
        self.delay_trigger = delay_trigger
    
    def applyEffectOnApply(self, character):
        character.updateEva(-1, True) # Eva can be lower than 0, which makes sense.

    def applyEffectOnRemove(self, character):
        character.updateEva(1, True)
    
    def tooltip_description(self):
        return "Cannot take action and evade is reduced by 100%."


# Speed effect
class SpeedEffect(Effect):
    def __init__(self, name, duration, is_buff, value, is_flat):
        super().__init__(name, duration, is_buff)
        self.value = value
        self.is_flat = is_flat
    
    def applyEffectOnApply(self, character):
        character.updateSpd(self.value, self.is_flat)
    
    def applyEffectOnRemove(self, character):
        if self.is_flat:
            character.updateSpd(-self.value, self.is_flat)
        else:
            character.updateSpd(1/self.value, self.is_flat)

    def tooltip_description(self):
        if self.is_flat:
            return f"Speed is increased by {self.value}."
        else:
            return f"Speed is scaled to {self.value*100}%."

# ---------------------------------------------------------
# Attack effect
class AttackEffect(Effect):
    def __init__(self, name, duration, is_buff, value, is_flat):
        super().__init__(name, duration, is_buff)
        self.value = value
        self.is_flat = is_flat
    
    def applyEffectOnApply(self, character):
        character.updateAtk(self.value, self.is_flat)
    
    def applyEffectOnRemove(self, character):
        if self.is_flat:
            character.updateAtk(-self.value, self.is_flat)
        else:
            character.updateAtk(1/self.value, self.is_flat)
    
    def tooltip_description(self):
        if self.is_flat:
            return f"Attack is increased by {self.value}."
        else:
            return f"Attack is scaled to {self.value*100}%."

# ---------------------------------------------------------
# Defense effect
class DefenseEffect(Effect):
    def __init__(self, name, duration, is_buff, value, is_flat):
        super().__init__(name, duration, is_buff)
        self.value = value
        self.is_flat = is_flat
    
    def applyEffectOnApply(self, character):
        character.updateDef(self.value, self.is_flat)
    
    def applyEffectOnRemove(self, character):
        if self.is_flat:
            character.updateDef(-self.value, self.is_flat)
        else:
            character.updateDef(1/self.value, self.is_flat)

    def tooltip_description(self):
        if self.is_flat:
            return f"Defense is increased by {self.value}."
        else:
            return f"Defense is scaled to {self.value*100}%."


# ---------------------------------------------------------
# Continuous Damage effect
class ContinuousDamageEffect(Effect):
    def __init__(self, name, duration, is_buff, value):
        super().__init__(name, duration, is_buff)
        self.value = float(value)
        self.is_buff = is_buff
    
    def applyEffectOnTrigger(self, character):
        print(f"{character.name} is taking {self.value} status damage")
        character.takeStatusDamage(self.value, self)
    
    def tooltip_description(self):
        return f"Take {int(self.value)} status damage each turn."

#---------------------------------------------------------
# Absorption Shield effect
class AbsorptionShield(Effect):
    def __init__(self, name, duration, is_buff, shield_value, cc_immunity):
        super().__init__(name, duration, is_buff, cc_immunity=False)
        self.shield_value = shield_value
        self.is_buff = is_buff
        self.cc_immunity = cc_immunity

    def applyEffectDuringDamageStep(self, character, damage):
        if damage > self.shield_value:
            remaining_damage = damage - self.shield_value
            if running:
                text_box.append_html_text(f"{character.name}'s shield is broken!\n{remaining_damage} damage is dealt to {character.name}.\n")
            print(f"{character.name}'s shield is broken! {remaining_damage} damage is dealt to {character.name}.")
            character.removeEffect(self)
            return remaining_damage
        else:
            self.shield_value -= damage
            if running:
                text_box.append_html_text(f"{character.name}'s shield absorbs {damage} damage.\nRemaining shield: {self.shield_value}\n")
            print(f"{character.name}'s shield absorbs {damage} damage. Remaining shield: {self.shield_value}")
            return 0
        
    def tooltip_description(self):
        return f"Absorbs up to {self.shield_value} damage."

#---------------------------------------------------------
# Reduction Shield and Damage Amplify effect (reduces/increase damage taken by a certain percentage)
class ReductionShield(Effect):
    def __init__(self, name, duration, is_buff, effect_value, cc_immunity):
        super().__init__(name, duration, is_buff, cc_immunity=False)
        self.is_buff = is_buff
        self.effect_value = effect_value
        self.cc_immunity = cc_immunity

    def applyEffectDuringDamageStep(self, character, damage):
        if self.is_buff:
            damage = damage * (1 - self.effect_value)
        else:
            damage = damage * (1 + self.effect_value)
        return damage
    
    def tooltip_description(self):
        if self.is_buff:
            return f"Reduces damage taken by {self.effect_value*100}%."
        else:
            return f"Increases damage taken by {self.effect_value*100}%."
    
#---------------------------------------------------------
# Effect shield 1 (before damage calculation, if character hp is below certain threshold, healhp for certain amount)
class EffectShield1(Effect):
    def __init__(self, name, duration, is_buff, threshold, heal_value, cc_immunity):
        super().__init__(name, duration, is_buff, cc_immunity=False)
        self.is_buff = is_buff
        self.threshold = threshold
        self.heal_value = heal_value
        self.cc_immunity = cc_immunity

    def applyEffectDuringDamageStep(self, character, damage):
        if character.hp < character.maxhp * self.threshold:
            character.healHp(self.heal_value, self)
        return damage
    
    def tooltip_description(self):
        return f"When hp is below {self.threshold*100}%, heal for {self.heal_value} hp before damage calculation."
    

#---------------------------------------------------------
# Reborn effect (revive with certain amount of hp)
class RebornEffect(Effect):
    def __init__(self, name, duration, is_buff, effect_value, cc_immunity):
        super().__init__(name, duration, is_buff, cc_immunity=False)
        self.is_buff = is_buff
        self.effect_value = effect_value
        self.cc_immunity = cc_immunity
    
    def applyEffectOnTrigger(self, character):
        if character.isDead():
            character.revive(1, hp_percentage_to_revive=self.effect_value)
            if isinstance(character, Pheonix):
                character.applyEffect(AttackEffect("ATK Up", 3, True, 0.5, False))
            character.removeEffect(self)

    def tooltip_description(self):
        return f"Revive with {self.effect_value*100}% hp the turn after fallen."

#---------------------------------------------------------
# Cancellation Shield effect (cancel 1 attack if attack damage exceed certain amount of max hp)
class CancellationShield(Effect):
    def __init__(self, name, duration, is_buff, threshold, cc_immunity):
        super().__init__(name, duration, is_buff, cc_immunity=False)
        self.is_buff = is_buff
        self.threshold = threshold
        self.cc_immunity = cc_immunity

    def applyEffectDuringDamageStep(self, character, damage):
        if damage > character.maxhp * self.threshold:
            character.removeEffect(self)
            if running:
                text_box.append_html_text(f"{character.name} shielded the attack!\n")
            print(f"{character.name} shielded the attack!")
            return 0
        else:
            return damage
        
    def tooltip_description(self):
        return f"Cancel 1 attack if damage exceed {self.threshold*100}% of max hp."


# Cancellation Shield 2 effect (cancel the damage that exceed certain amount of max hp)
class CancellationShield2(Effect):
    def __init__(self, name, duration, is_buff, threshold, cc_immunity):
        super().__init__(name, duration, is_buff, cc_immunity=False)
        self.is_buff = is_buff
        self.threshold = threshold
        self.cc_immunity = cc_immunity

    def applyEffectDuringDamageStep(self, character, damage):
        damage = min(damage, character.maxhp * self.threshold)
        return damage
        
    def tooltip_description(self):
        return f"Cancel the damage that exceed {self.threshold*100}% of max hp."
    
#--------------------------------------------------------- 
#---------------------------------------------------------
def is_someone_alive(party):
    for character in party:
        if character.isAlive():
            return True
    return False

def get_neighbors(party, char, include_self=True) -> list:
    if char not in party:
        return []

    index = party.index(char)
    start = max(index - 1, 0)
    end = min(index + 2, len(party))

    neighbors = party[start:end]
    if not include_self:
        neighbors.remove(char)
    return neighbors

def start_of_battle_effects(party):
    # Iris effect
    if any(isinstance(character, Iris) for character in party):
        character_with_highest_atk = max(party, key=lambda char: getattr(char, 'atk', 0))
        character_with_highest_atk.applyEffect(CancellationShield("Cancellation Shield", -1, True, 0.1, cc_immunity=True))
    # Pheonix effect
    for character in party:
        if isinstance(character, Pheonix):
            character.applyEffect(RebornEffect("Reborn", -1, True, 0.4, False))
        

def mid_turn_effects(party1, party2): 
    # Fenrir effect
    for party in [party1, party2]:
        for character in party:
            neighbors = character.get_neighbor_allies_not_including_self()
            fenrir = next((ally for ally in neighbors if isinstance(ally, Fenrir)), None)
            if fenrir:
                if not character.hasEffect("Fluffy Protection"):
                    character.applyEffect(EffectShield1("Fluffy Protection", -1, True, 0.4, fenrir.atk, False))
            else:
                for buff in character.buffs:
                    if buff.name == "Fluffy Protection":
                        character.removeEffect(buff) 

# Reset characters.ally and characters.enemy
def reset_ally_enemy_attr(party1, party2):
    for character in party1:
        character.ally = copy.copy(party1)
        character.enemy = copy.copy(party2)
        character.party = party1
        character.enemyparty = party2
    for character in party2:
        character.ally = copy.copy(party2)
        character.enemy = copy.copy(party1)
        character.party = party2
        character.enemyparty = party1

#--------------------------------------------------------- 
#---------------------------------------------------------

average_party_level = 40
character1 = Cerberus("Cerberus", average_party_level, 0, generate_equips_list(4))
character2 = Fenrir("Fenrir", average_party_level, 0, generate_equips_list(4))
character3 = Clover("Clover", average_party_level, 0, generate_equips_list(4))
character4 = Ruby("Ruby", average_party_level, 0, generate_equips_list(4))
character5 = Olive("Olive", average_party_level, 0, generate_equips_list(4))
character6 = Luna("Luna", average_party_level, 0, generate_equips_list(4))
character7 = Freya("Freya", average_party_level, 0, generate_equips_list(4))
character8 = Poppy("Poppy", average_party_level, 0, generate_equips_list(4))
character9 = Lillia("Lillia", average_party_level, 0, generate_equips_list(4))
character10 = Iris("Iris", average_party_level, 0, generate_equips_list(4))
character11 = Pepper("Pepper", average_party_level, 0, generate_equips_list(4))
character12 = Cliffe("Cliffe", average_party_level, 0, generate_equips_list(4))
character13 = Pheonix("Pheonix", average_party_level, 0, generate_equips_list(4))
character14 = Bell("Bell", average_party_level, 0, generate_equips_list(4))

all_characters = [character1, character2, character3, character4, character5,
                    character6, character7, character8, character9, character10,
                        character11, character12, character13, character14]

# ---------------------------------------------------------
# ---------------------------------------------------------
if __name__ == "__main__":
    pygame.init()
    clock = pygame.time.Clock()

    antique_white = pygame.Color("#FAEBD7")
    deep_dark_blue = pygame.Color("#000022")
    light_yellow = pygame.Color("#FFFFE0")

    display_surface = pygame.display.set_mode((1200, 900))
    ui_manager = pygame_gui.UIManager((1200, 900), "theme_light_yellow.json", starting_language='ja')

    pygame.display.set_caption("Battle Simulator")

    # Some Invisible Sprites for health bar, useless
    # =====================================
    class InvisibleSprite(pygame.sprite.Sprite):
        def __init__(self, color, width, height, health_capacity, current_health, *groups: pygame.sprite.AbstractGroup):
            super().__init__()
            self.image = pygame.Surface([width, height])
            self.image.fill(color)
            self.rect = self.image.get_rect()
            self.health_capacity = health_capacity
            self.current_health = current_health

        def update(self):
            pass


    for i in range(1, 11):
        exec(f"invisible_sprite{i} = InvisibleSprite(deep_dark_blue, 1200, 900, 1000, 100)")

    sprite_party1 = [invisible_sprite1, invisible_sprite2, invisible_sprite3, invisible_sprite4, invisible_sprite5]
    sprite_party2 = [invisible_sprite6, invisible_sprite7, invisible_sprite8, invisible_sprite9, invisible_sprite10]

    health_bar1 = pygame_gui.elements.UIScreenSpaceHealthBar(pygame.Rect((75, 220), (200, 30)),ui_manager,
                                                            invisible_sprite1)
    health_bar2 = pygame_gui.elements.UIScreenSpaceHealthBar(pygame.Rect((275, 220), (200, 30)),ui_manager,
                                                            invisible_sprite2)
    health_bar3 = pygame_gui.elements.UIScreenSpaceHealthBar(pygame.Rect((475, 220), (200, 30)),ui_manager,
                                                            invisible_sprite3)
    health_bar4 = pygame_gui.elements.UIScreenSpaceHealthBar(pygame.Rect((675, 220), (200, 30)),ui_manager,
                                                            invisible_sprite4)
    health_bar5 = pygame_gui.elements.UIScreenSpaceHealthBar(pygame.Rect((875, 220), (200, 30)),ui_manager,
                                                            invisible_sprite5)
    health_bar6 = pygame_gui.elements.UIScreenSpaceHealthBar(pygame.Rect((75, 825), (200, 30)),ui_manager,
                                                            invisible_sprite6)
    health_bar7 = pygame_gui.elements.UIScreenSpaceHealthBar(pygame.Rect((275, 825), (200, 30)),ui_manager,
                                                            invisible_sprite7)
    health_bar8 = pygame_gui.elements.UIScreenSpaceHealthBar(pygame.Rect((475, 825), (200, 30)),ui_manager,
                                                            invisible_sprite8)
    health_bar9 = pygame_gui.elements.UIScreenSpaceHealthBar(pygame.Rect((675, 825), (200, 30)),ui_manager,
                                                            invisible_sprite9)
    health_bar10 = pygame_gui.elements.UIScreenSpaceHealthBar(pygame.Rect((875, 825), (200, 30)),ui_manager,
                                                            invisible_sprite10)

    health_bar_party1 = [health_bar1, health_bar2, health_bar3, health_bar4, health_bar5]
    health_bar_party2 = [health_bar6, health_bar7, health_bar8, health_bar9, health_bar10]

    all_healthbar = health_bar_party1 + health_bar_party2

    # Some Images
    # =====================================
    # load all images in ./image directory
    image_files = [x[:-4] for x in os.listdir("./image") if x[-4:] == ".jpg" or x[-4:] == ".png"]
    images = {name: pygame.image.load(f"image/{name}.jpg") for name in image_files}


    image_slot1 = pygame_gui.elements.UIImage(pygame.Rect((100, 50), (156, 156)),
                                        pygame.Surface((156, 156)),
                                        ui_manager)
    image_slot2 = pygame_gui.elements.UIImage(pygame.Rect((300, 50), (156, 156)),
                                        pygame.Surface((156, 156)),
                                        ui_manager)
    image_slot3 = pygame_gui.elements.UIImage(pygame.Rect((500, 50), (156, 156)),
                                        pygame.Surface((156, 156)),
                                        ui_manager)
    image_slot4 = pygame_gui.elements.UIImage(pygame.Rect((700, 50), (156, 156)),
                                        pygame.Surface((156, 156)),
                                        ui_manager)
    image_slot5 = pygame_gui.elements.UIImage(pygame.Rect((900, 50), (156, 156)),
                                        pygame.Surface((156, 156)),
                                        ui_manager)
    image_slot6 = pygame_gui.elements.UIImage(pygame.Rect((100, 650), (156, 156)),
                                        pygame.Surface((156, 156)),
                                        ui_manager)
    image_slot7 = pygame_gui.elements.UIImage(pygame.Rect((300, 650), (156, 156)),
                                        pygame.Surface((156, 156)),
                                        ui_manager)
    image_slot8 = pygame_gui.elements.UIImage(pygame.Rect((500, 650), (156, 156)),
                                        pygame.Surface((156, 156)),
                                        ui_manager)
    image_slot9 = pygame_gui.elements.UIImage(pygame.Rect((700, 650), (156, 156)),
                                        pygame.Surface((156, 156)),
                                        ui_manager)
    image_slot10 = pygame_gui.elements.UIImage(pygame.Rect((900, 650), (156, 156)),
                                        pygame.Surface((156, 156)),
                                        ui_manager)

    image_slots_party1 = [image_slot1, image_slot2, image_slot3, image_slot4, image_slot5]
    image_slots_party2 = [image_slot6, image_slot7, image_slot8, image_slot9, image_slot10]

    # Equip Slots
    # ==============================
    equip_slota1 = pygame_gui.elements.UIImage(pygame.Rect((75, 50), (20, 20)),pygame.Surface((20, 20)),ui_manager)

    equip_slotsb1 = pygame_gui.elements.UIImage(pygame.Rect((275, 50), (20, 20)),pygame.Surface((20, 20)),ui_manager)

    equip_slotsc1 = pygame_gui.elements.UIImage(pygame.Rect((475, 50), (20, 20)),pygame.Surface((20, 20)),ui_manager)

    equip_slotsd1 = pygame_gui.elements.UIImage(pygame.Rect((675, 50), (20, 20)),pygame.Surface((20, 20)),ui_manager)

    equip_slotse1 = pygame_gui.elements.UIImage(pygame.Rect((875, 50), (20, 20)),pygame.Surface((20, 20)),ui_manager)

    equip_slotsf1 = pygame_gui.elements.UIImage(pygame.Rect((75, 650), (20, 20)),pygame.Surface((20, 20)),ui_manager)

    equip_slotsg1 = pygame_gui.elements.UIImage(pygame.Rect((275, 650), (20, 20)),pygame.Surface((20, 20)),ui_manager)

    equip_slotsh1 = pygame_gui.elements.UIImage(pygame.Rect((475, 650), (20, 20)),pygame.Surface((20, 20)),ui_manager)

    equip_slotsi1 = pygame_gui.elements.UIImage(pygame.Rect((675, 650), (20, 20)),pygame.Surface((20, 20)),ui_manager)

    equip_slotsj1 = pygame_gui.elements.UIImage(pygame.Rect((875, 650), (20, 20)),pygame.Surface((20, 20)),ui_manager)

                                            
    equip_slot_party1 = [equip_slota1, equip_slotsb1, equip_slotsc1, equip_slotsd1, equip_slotse1]
    equip_slot_party2 = [equip_slotsf1, equip_slotsg1, equip_slotsh1, equip_slotsi1, equip_slotsj1]
    for slot in equip_slot_party1 + equip_slot_party2:
        slot.set_image(images["wood"])                                  

    # Character Names and Level Labels
    # ==========================
    label1 = pygame_gui.elements.UILabel(pygame.Rect((75, 10), (200, 50)),
                                        "label",
                                        ui_manager)

    label2 = pygame_gui.elements.UILabel(pygame.Rect((275, 10), (200, 50)),
                                        "label",
                                        ui_manager)

    label3 = pygame_gui.elements.UILabel(pygame.Rect((475, 10), (200, 50)),
                                        "label",
                                        ui_manager)

    label4 = pygame_gui.elements.UILabel(pygame.Rect((675, 10), (200, 50)),
                                        "label",
                                        ui_manager)

    label5 = pygame_gui.elements.UILabel(pygame.Rect((875, 10), (200, 50)),
                                        "label",
                                        ui_manager)

    label6 = pygame_gui.elements.UILabel(pygame.Rect((75, 610), (200, 50)),
                                        "label",
                                        ui_manager)

    label7 = pygame_gui.elements.UILabel(pygame.Rect((275, 610), (200, 50)),
                                        "label",
                                        ui_manager)

    label8 = pygame_gui.elements.UILabel(pygame.Rect((475, 610), (200, 50)),
                                        "label",
                                        ui_manager)

    label9 = pygame_gui.elements.UILabel(pygame.Rect((675, 610), (200, 50)),
                                        "label",
                                        ui_manager)

    label10 = pygame_gui.elements.UILabel(pygame.Rect((875, 610), (200, 50)),
                                        "label",
                                        ui_manager)

    label_party1 = [label1, label2, label3, label4, label5]
    label_party2 = [label6, label7, label8, label9, label10]

    # Some buttons
    # ==========================
    button1 = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((100, 300), (156, 50)),
                                        text='Shuffle Party',
                                        manager=ui_manager,
                                        tool_tip_text = "Shuffle party and restart the battle")

    button2 = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((100, 360), (156, 50)),
                                        text='Next Turn',
                                        manager=ui_manager,
                                        tool_tip_text = "Simulate the next turn")

    button3 = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((100, 420), (156, 50)),
                                        text='All Turns',
                                        manager=ui_manager,
                                        tool_tip_text = "Skip to the end of the battle. May take a while.")

    button4 = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((100, 480), (156, 50)),
                                        text='Restart Battle',
                                        manager=ui_manager,
                                        tool_tip_text = "Restart battle")

    button5 = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((100, 540), (156, 50)),
                                        text='Quit',
                                        manager=ui_manager,
                                        tool_tip_text = "Quit")

    character_selection_menu = pygame_gui.elements.UIDropDownMenu(["Option 1", "Option 2", "Option 3", "Option 4", "Option 5"],
                                                            "Option 1",
                                                            pygame.Rect((900, 300), (156, 35)),
                                                            ui_manager)

    reserve_character_selection_menu = pygame_gui.elements.UIDropDownMenu(["Option1"],
                                                            "Option1",
                                                            pygame.Rect((900, 340), (156, 35)),
                                                            ui_manager)

    eq_selection_menu = pygame_gui.elements.UIDropDownMenu(["Weapon", "Armor", "Accessory", "Boots"],
                                                            "Weapon",
                                                            pygame.Rect((900, 420), (156, 35)),
                                                            ui_manager)

    eq_reroll_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((900, 460), (78, 35)),
                                        text='Reroll',
                                        manager=ui_manager,
                                        tool_tip_text = "Reroll item")

    eq_upgrade_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((980, 460), (37, 35)),
                                        text='+',
                                        manager=ui_manager,
                                        tool_tip_text = "Upgrade item")

    eq_downgrade_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((1017, 460), (37, 35)),
                                            text='-',
                                            manager=ui_manager,
                                            tool_tip_text = "Downgrade item")

    character_replace_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((900, 380), (156, 35)),
                                        text='Replace',
                                        manager=ui_manager,
                                        tool_tip_text = "Replace selected character with reserve character")

    levelup_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((900, 515), (156, 35)),
                                        text='Level Up',
                                        manager=ui_manager,
                                        tool_tip_text = "Level up")

    leveldown_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((900, 555), (156, 35)),
                                        text='Level Down',
                                        manager=ui_manager,
                                        tool_tip_text = "Level down")


    def next_turn(party1, party2):
        if not is_someone_alive(party1) or not is_someone_alive(party2):
            text_box.append_html_text("Battle is over.\n")
            return False
        text_box.append_html_text("=====================================\n")
        text_box.append_html_text(f"Turn {turn}\n")
        for character in party1:
            character.updateEffects()
        for character in party2:
            character.updateEffects()
        if not is_someone_alive(party1) or not is_someone_alive(party2):
            return False
        
        for character in party1:
            character.statusEffects()
            if character.isAlive():
                character.regen()
        for character in party2:
            character.statusEffects()
            if character.isAlive():
                character.regen()

        reset_ally_enemy_attr(party1, party2)
        for character in party1:
            character.updateAllyEnemy()
        for character in party2:
            character.updateAllyEnemy()

        mid_turn_effects(party1, party2)

        if not is_someone_alive(party1) or not is_someone_alive(party2):
            return False
        alive_characters = [x for x in party1 + party2 if x.isAlive()]
        weight = [x.spd for x in alive_characters]
        the_chosen_one = random.choices(alive_characters, weights=weight, k=1)[0]
        text_box.append_html_text(f"{the_chosen_one.name}'s turn.\n")
        the_chosen_one.action()

        redraw_ui(party1, party2, refill_image=False, main_char=the_chosen_one)

        if not is_someone_alive(party1) or not is_someone_alive(party2):
            return False
        return True

    def all_turns(party1, party2):
        global turn
        while turn < 300 and is_someone_alive(party1) and is_someone_alive(party2):
            text_box.set_text("Welcome to the battle simulator!\n")
            text_box.append_html_text("=====================================\n")
            text_box.append_html_text(f"Turn {turn}\n")
            for character in party1:
                character.updateEffects()
            for character in party2:
                character.updateEffects()
            if not is_someone_alive(party1) or not is_someone_alive(party2):
                break
            for character in party1:
                character.statusEffects()
                if character.isAlive():
                    character.regen()
            for character in party2:
                character.statusEffects()
                if character.isAlive():
                    character.regen()

            reset_ally_enemy_attr(party1, party2)
            for character in party1:
                character.updateAllyEnemy()
            for character in party2:
                character.updateAllyEnemy()
            
            mid_turn_effects(party1, party2)

            alive_characters = [x for x in party1 + party2 if x.isAlive()]
            weight = [x.spd for x in alive_characters]
            the_chosen_one = random.choices(alive_characters, weights=weight, k=1)[0]
            text_box.append_html_text(f"{the_chosen_one.name}'s turn.\n")
            the_chosen_one.action()
            turn += 1

        redraw_ui(party1, party2)

        if turn >= 300:
            text_box.append_html_text("Battle is taking too long.\n")
        elif not is_someone_alive(party1) and not is_someone_alive(party2):
            text_box.append_html_text("Both parties are defeated.\n")
        elif not is_someone_alive(party1):
            text_box.append_html_text("Party 1 is defeated.\n")
        elif not is_someone_alive(party2):
            text_box.append_html_text("Party 2 is defeated.\n")

    def restart_battle():
        global turn
        for character in all_characters:
            character.reset_stats()

        start_of_battle_effects(party1)
        start_of_battle_effects(party2)

        redraw_ui(party1, party2)

        reset_ally_enemy_attr(party1, party2)
        turn = 1

    def set_up_characters() -> (list, list):
        global character_selection_menu, reserve_character_selection_menu, all_characters

        for character in all_characters:
            character.reset_stats()

        party1 = []
        party2 = []
        list_of_characters = random.sample(all_characters, 10)

        remaining_characters = [character for character in all_characters if character not in list_of_characters]

        random.shuffle(list_of_characters)

        party1 = list_of_characters[:5]
        party2 = list_of_characters[5:]

        start_of_battle_effects(party1)
        start_of_battle_effects(party2)

        character_selection_menu.kill()
        character_selection_menu = pygame_gui.elements.UIDropDownMenu([character.name for character in party1] + [character.name for character in party2],
                                                                party1[0].name,
                                                                pygame.Rect((900, 300), (156, 35)),
                                                                ui_manager)

        reserve_character_selection_menu.kill()
        reserve_character_selection_menu = pygame_gui.elements.UIDropDownMenu([character.name for character in remaining_characters],
                                                                remaining_characters[0].name,
                                                                pygame.Rect((900, 340), (156, 35)),
                                                                ui_manager)

        redraw_ui(party1, party2)
        reset_ally_enemy_attr(party1, party2)
        return party1, party2

    def replace_character_with_reserve_member(character_name, new_character_name):
        global party1, party2, all_characters, character_selection_menu, reserve_character_selection_menu

        def replace_in_party(party):
            for i, character in enumerate(party):
                if character.name == character_name:
                    new_character = next((char for char in all_characters if char.name == new_character_name), None)
                    if new_character:
                        party[i] = new_character
                        return True
            return False

        replaced = replace_in_party(party1)
        if not replaced:
            replace_in_party(party2)

        character_selection_menu.kill()
        character_selection_menu = pygame_gui.elements.UIDropDownMenu([character.name for character in party1] + [character.name for character in party2],
                                                                party1[0].name,
                                                                pygame.Rect((900, 300), (156, 35)),
                                                                ui_manager)

        remaining_characters = [character for character in all_characters if character not in party1 and character not in party2]

        reserve_character_selection_menu.kill()
        reserve_character_selection_menu = pygame_gui.elements.UIDropDownMenu([character.name for character in remaining_characters],
                                                                remaining_characters[0].name,
                                                                pygame.Rect((900, 340), (156, 35)),
                                                                ui_manager)
        redraw_ui(party1, party2)
        reset_ally_enemy_attr(party1, party2)
        text_box.append_html_text(f"{character_name} has been replaced with {new_character_name}.\n")

    def redraw_ui(party1, party2, refill_image=True, rebuild_healthbar=True, main_char=None):
        def redraw_party(party, image_slots, equip_slots, sprites, labels, healthbar):
            for i, character in enumerate(party):
                if refill_image:
                    try:
                        image_slots[i].set_image(images[character.name.lower()])
                    except Exception:
                        image_slots[i].set_image(images["error"])

                image_slots[i].set_tooltip(character.tooltip_string(), delay=0.1, wrap_width=250)
                equip_slots[i].set_tooltip(character.get_equip_stats(), delay=0.1, wrap_width=250)
                sprites[i].current_health = character.hp
                sprites[i].health_capacity = character.maxhp
                labels[i].set_text(f"lv {character.lvl} {character.name}")
                labels[i].set_tooltip(character.skill_tooltip(), delay=0.1, wrap_width=250)
                healthbar[i].set_tooltip(character.tooltip_status_effects(), delay=0.1, wrap_width=250)
                if main_char == character:
                    labels[i].set_text(f"--> lv {character.lvl} {character.name}")

        redraw_party(party1, image_slots_party1, equip_slot_party1, sprite_party1, label_party1, health_bar_party1)
        redraw_party(party2, image_slots_party2, equip_slot_party2, sprite_party2, label_party2, health_bar_party2)

        if rebuild_healthbar:
            for healthbar in all_healthbar:
                healthbar.rebuild()

    def reroll_eq(eq_index):
        all_characters = party1 + party2
        for character in all_characters:
            if character.name == character_selection_menu.selected_option and character.isAlive():
                character.equip[eq_index] = generate_equips_list(4)[eq_index]
                text_box.append_html_text("====================================\n")
                text_box.append_html_text(f"Rerolling {character.equip[eq_index].type} for {character.name}\n")
                text_box.append_html_text(character.equip[eq_index].print_stats())
                print(character.equip[eq_index])
                character.reset_stats(resethp=False, resetally=False, resetenemy=False)
                character.recalculateEffects()
        redraw_ui(party1, party2)

    def eq_upgrade(eq_index, is_upgrade):
        for character in all_characters:
            if character.name == character_selection_menu.selected_option and character.isAlive():
                item_to_upgrade = character.equip[eq_index]
                a, b = item_to_upgrade.upgrade_stars_func(is_upgrade) 
                text_box.append_html_text("====================================\n")
                text_box.append_html_text(f"Upgrading equipment {character.equip[eq_index].type} for {character.name}\n")
                text_box.append_html_text(f"Stars: {int(a)} -> {int(b)}\n")
                if int(b) == 15:
                    text_box.append_html_text(f"Max stars reached\n")
                if int(b) == 0:
                    text_box.append_html_text(f"Min stars reached\n")
                character.reset_stats(resethp=False, resetally=False, resetenemy=False)
                character.recalculateEffects()
        redraw_ui(party1, party2)

    def character_level_button(up=True):
        all_characters = party1 + party2
        for character in all_characters:
            if character.name == character_selection_menu.selected_option and character.isAlive():
                if up:
                    character.level_up()
                    text_box.append_html_text(f"Leveling up {character.name}, New level: {character.lvl}\n")
                else:
                    character.level_down()
                    text_box.append_html_text(f"Leveling down {character.name}. New level: {character.lvl}\n")
        redraw_ui(party1, party2, refill_image=False, rebuild_healthbar=True)

    # Text entry box
    # ==========================
    text_box = pygame_gui.elements.UITextEntryBox(pygame.Rect((300, 300), (556, 290)),"", ui_manager)
    text_box.set_text("Hover over character name to show skill information.\n")
    text_box.append_html_text("If lower cased character_name.jpg is not found in ./image directory, error.jpg will be used instead.\n")
    text_box.append_html_text("Hover over character image to show attributes.\n")
    text_box.append_html_text("Hover over character health bar to show status effects.\n")
    text_box.append_html_text("Hover over wood icon to show item information.\n\n")

    # Event loop
    # ==========================
    running = True 
    party1 = []
    party2 = []
    party1, party2 = set_up_characters()
    turn = 1
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame_gui.UI_BUTTON_PRESSED:
                if event.ui_element == button1:
                    text_box.set_text("Welcome to the battle simulator!\n")
                    party1, party2 = set_up_characters()
                    turn = 1
                if event.ui_element == button2:
                    text_box.set_text("Welcome to the battle simulator!\n")
                    if next_turn(party1, party2):
                        turn += 1
                if event.ui_element == button3:
                    all_turns(party1, party2)
                if event.ui_element == button4:
                    text_box.set_text("Welcome to the battle simulator!\n")
                    restart_battle()
                if event.ui_element == button5:
                    running = False
                if event.ui_element == eq_reroll_button:
                    if eq_selection_menu.selected_option == "Weapon":
                        reroll_eq(0)
                    elif eq_selection_menu.selected_option == "Armor":
                        reroll_eq(1)
                    elif eq_selection_menu.selected_option == "Accessory":
                        reroll_eq(2)
                    elif eq_selection_menu.selected_option == "Boots":
                        reroll_eq(3)
                if event.ui_element == eq_upgrade_button:
                    if eq_selection_menu.selected_option == "Weapon":
                        eq_upgrade(0, True)
                    elif eq_selection_menu.selected_option == "Armor":
                        eq_upgrade(1, True)
                    elif eq_selection_menu.selected_option == "Accessory":
                        eq_upgrade(2, True)
                    elif eq_selection_menu.selected_option == "Boots":
                        eq_upgrade(3, True)
                if event.ui_element == eq_downgrade_button:
                    if eq_selection_menu.selected_option == "Weapon":
                        eq_upgrade(0, False)
                    elif eq_selection_menu.selected_option == "Armor":
                        eq_upgrade(1, False)
                    elif eq_selection_menu.selected_option == "Accessory":
                        eq_upgrade(2, False)
                    elif eq_selection_menu.selected_option == "Boots":
                        eq_upgrade(3, False)
                if event.ui_element == character_replace_button:
                    replace_character_with_reserve_member(character_selection_menu.selected_option, reserve_character_selection_menu.selected_option)
                if event.ui_element == levelup_button:
                    character_level_button(up=True)
                if event.ui_element == leveldown_button:
                    character_level_button(up=False)

            ui_manager.process_events(event)

        ui_manager.update(1/60)
        display_surface.fill(light_yellow)
        # all_sprites.draw(display_surface)
        # all_sprites.update()

        ui_manager.draw_ui(display_surface)

        pygame.display.update()
        clock.tick(60)

    pygame.quit()
