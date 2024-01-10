import random
from effect import *
from character import Character

# generic skill template:
# 1.attack type:
# Very heavy attack
# heavy attack
# balanced
# multi strike
# multi multi strike

# 2. focus
# lowest hp
# highest hp
# lowest def
# highest def
# lowest atk
# highest atk
# lowest spd
# highest spd

# 3. status effects
# poison
# stun
# burn
# sleep
# blind

# NOTE: use cw.py to estimate winrate
# Normal monsters should have winrate around 40% - 50%
# Boss monsters should have winrate around 65% - 70%


class Panda(Character):
    # 50% winrate after testing
    def __init__(self, name, lvl, exp=0, equip=None, image=None):
        super().__init__(name, lvl, exp, equip, image)
        self.original_name = "Panda"
        self.skill1_description = "Attack 1 enemy with 800% atk."
        self.skill2_description = "Attack 1 enemy with 700% atk and 70% chance to stun the target for 4 turns."
        self.skill3_description = "Increase maxhp by 50%."
        self.skill1_cooldown_max = 5
        self.skill2_cooldown_max = 5
        self.is_boss = False

    def skill_tooltip(self):
        return f"Skill 1 : {self.skill1_description}\nCooldown : {self.skill1_cooldown} action(s)\n\nSkill 2 : {self.skill2_description}\nCooldown : {self.skill2_cooldown} action(s)\n\nSkill 3 : {self.skill3_description}\n"

    def skill1_logic(self):
        damage_dealt = self.attack(multiplier=8.0, repeat=1)
        return damage_dealt

    def skill2_logic(self):
        def stun_effect(self, target):
            dice = random.randint(1, 100)
            if dice <= 70:
                target.apply_effect(StunEffect('Stun', duration=4, is_buff=False))
        damage_dealt = self.attack(multiplier=7.0, repeat=1, func_after_dmg=stun_effect)
        return damage_dealt
        
    def skill3(self):
        pass

    def battle_entry_effects(self):
        self.apply_effect(StatsEffect('Fat', -1, True, {'maxhp' : 1.5}))
        self.hp = self.maxhp



class Samurai(Character):
    # 46% winrate after testing
    def __init__(self, name, lvl, exp=0, equip=None, image=None):
        super().__init__(name, lvl, exp, equip, image)
        self.original_name = "Samurai"
        self.skill1_description = "Attack enemy 7 times with 200% atk."
        self.skill2_description = "Attack enemy with lowest hp 3 times with 300% atk."
        self.skill3_description = "Skill have 30% chance to inflict bleed on target for 3 turns. Bleed deals 30% of atk as damage per turn."
        self.skill1_cooldown_max = 5
        self.skill2_cooldown_max = 5
        self.is_boss = False

    def skill_tooltip(self):
        return f"Skill 1 : {self.skill1_description}\nCooldown : {self.skill1_cooldown} action(s)\n\nSkill 2 : {self.skill2_description}\nCooldown : {self.skill2_cooldown} action(s)\n\nSkill 3 : {self.skill3_description}\n"

    def skill1_logic(self):
        def bleed_effect(self, target):
            dice = random.randint(1, 100)
            if dice <= 30:
                target.apply_effect(ContinuousDamageEffect('Bleed', duration=3, is_buff=False, value=0.3 * self.atk, imposter=self))
        damage_dealt = self.attack(multiplier=2.0, repeat=7, func_after_dmg=bleed_effect)
        return damage_dealt

    def skill2_logic(self):
        def bleed_effect(self, target):
            dice = random.randint(1, 100)
            if dice <= 30:
                target.apply_effect(ContinuousDamageEffect('Bleed', duration=3, is_buff=False, value=0.3 * self.atk, imposter=self))
        damage_dealt = damage_dealt = self.attack(target_kw1="n_lowest_attr",target_kw2="1",target_kw3="hp",target_kw4="enemy", multiplier=3.0, repeat=3, func_after_dmg=bleed_effect)
        return damage_dealt
        
    def skill3(self):
        pass



class Mummy(Character):
    # 45% winrate after testing
    def __init__(self, name, lvl, exp=0, equip=None, image=None):
        super().__init__(name, lvl, exp, equip, image)
        self.original_name = "Mummy"
        self.skill1_description = "Attack 3 enemies with 300% atk."
        self.skill2_description = "Attack 5 enemies with 200% atk and 50% chance to inflict Curse for 3 turns. Curse: atk is reduced by 30%."
        self.skill3_description = "When taking damage, 30% chance to inflict Curse on attacker for 3 turns."
        self.skill1_cooldown_max = 5
        self.skill2_cooldown_max = 5
        self.is_boss = False

    def skill_tooltip(self):
        return f"Skill 1 : {self.skill1_description}\nCooldown : {self.skill1_cooldown} action(s)\n\nSkill 2 : {self.skill2_description}\nCooldown : {self.skill2_cooldown} action(s)\n\nSkill 3 : {self.skill3_description}\n"

    def skill1_logic(self):
        damage_dealt = self.attack(target_kw1="n_random_enemy",target_kw2="3", multiplier=3.0, repeat=1)
        return damage_dealt

    def skill2_logic(self):
        def curse_effect(self, target):
            dice = random.randint(1, 100)
            if dice <= 50:
                curse = StatsEffect('Curse', duration=3, is_buff=False, stats_dict={'atk' : 0.7})
                curse.apply_rule = "stack"
                target.apply_effect(curse)
        damage_dealt = self.attack(target_kw1="n_random_enemy",target_kw2="5", multiplier=2.0, repeat=1, func_after_dmg=curse_effect)
        return damage_dealt
        
    def skill3(self):
        pass

    def take_damage_aftermath(self, damage, attacker):
        if random.randint(1, 100) <= 30:
            curse = StatsEffect('Curse', duration=3, is_buff=False, stats_dict={'atk' : 0.7})
            curse.apply_rule = "stack"
            attacker.apply_effect(curse)


class Pharaoh(Character):
    # 65% winrate after testing, boss monsters in later designs should have similar winrate
    def __init__(self, name, lvl, exp=0, equip=None, image=None):
        super().__init__(name, lvl, exp, equip, image)
        self.original_name = "Pharaoh"
        self.skill1_description = "Attack 3 enemies with 300% atk. If target is cursed, damage is increased by 100%."
        self.skill2_description = "Attack 5 enemies with 200% atk and 80% chance to inflict Curse for 4 turns. If target is cursed, damage is increased by 100%. Curse: atk is reduced by 30%."
        self.skill3_description = "hp, atk, def, spd is increased by 20%. When taking damage, 40% chance to inflict Curse on attacker for 3 turns. At the end of turn, if there is a cursed enemy, increase atk by 30% for 3 turns."
        self.skill1_cooldown_max = 5
        self.skill2_cooldown_max = 5
        self.is_boss = True

    def skill_tooltip(self):
        return f"Skill 1 : {self.skill1_description}\nCooldown : {self.skill1_cooldown} action(s)\n\nSkill 2 : {self.skill2_description}\nCooldown : {self.skill2_cooldown} action(s)\n\nSkill 3 : {self.skill3_description}\n"

    def skill1_logic(self):
        def curse_amplify(self, target, final_damage):
            if target.has_effect_that_named("Curse"):
                final_damage *= 2.0
            return final_damage
        damage_dealt = self.attack(target_kw1="n_random_enemy",target_kw2="3", multiplier=3.0, repeat=1, func_damage_step=curse_amplify)
        return damage_dealt

    def skill2_logic(self):
        def curse_amplify(self, target, final_damage):
            if target.has_effect_that_named("Curse"):
                final_damage *= 2.0
            return final_damage
        def curse_effect(self, target):
            dice = random.randint(1, 100)
            if dice <= 80:
                curse = StatsEffect('Curse', duration=4, is_buff=False, stats_dict={'atk' : 0.7})
                curse.apply_rule = "stack"
                target.apply_effect(curse)
        damage_dealt = self.attack(target_kw1="n_random_enemy",target_kw2="5", multiplier=2.0, repeat=1, func_damage_step=curse_amplify, func_after_dmg=curse_effect)
        return damage_dealt
        
    def skill3(self):
        pass

    def take_damage_aftermath(self, damage, attacker):
        if random.randint(1, 100) <= 40:
            curse = StatsEffect('Curse', duration=3, is_buff=False, stats_dict={'atk' : 0.7})
            curse.apply_rule = "stack"
            attacker.apply_effect(curse)

    def battle_entry_effects(self):
        self.apply_effect(StatsEffect('Strong', -1, True, {'maxhp' : 1.2, 'atk' : 1.2, 'defense' : 1.2, 'spd' : 1.2}))
        self.hp = self.maxhp
        self.apply_effect(PharaohPassiveEffect('Passive Effect', -1, True, 1.3))



class PoisonSlime(Character):
    # Strong status damage, low damage
    # 49.4% winrate after testing
    def __init__(self, name, lvl, exp=0, equip=None, image=None):
        super().__init__(name, lvl, exp, equip, image)
        self.original_name = "Poison_Slime"
        self.skill1_description = "Attack 5 enemies with 200% atk and 50% chance to inflict Poison for 4 turns. Poison: takes 7% of current hp status damage per turn."
        self.skill2_description = "Attack 5 enemies with 200% atk and 50% chance to inflict Poison for 4 turns. Poison: takes 7% of lost hp status damage per turn."
        self.skill3_description = "Reduce damage taken by 10%"
        self.skill1_cooldown_max = 5
        self.skill2_cooldown_max = 5
        self.is_boss = False

    def skill_tooltip(self):
        return f"Skill 1 : {self.skill1_description}\nCooldown : {self.skill1_cooldown} action(s)\n\nSkill 2 : {self.skill2_description}\nCooldown : {self.skill2_cooldown} action(s)\n\nSkill 3 : {self.skill3_description}\n"

    def skill1_logic(self):
        def poison_effect(self, target):
            dice = random.randint(1, 100)
            if dice <= 50:
                target.apply_effect(PoisonDamageEffect('Poison', duration=4, is_buff=False, value=0.07, imposter=self, base="hp"))
        damage_dealt = self.attack(target_kw1="n_random_enemy",target_kw2="5", multiplier=2.0, repeat=1, func_after_dmg=poison_effect)
        return damage_dealt

    def skill2_logic(self):
        def poison_effect(self, target):
            dice = random.randint(1, 100)
            if dice <= 50:
                target.apply_effect(PoisonDamageEffect('Poison', duration=4, is_buff=False, value=0.07, imposter=self, base="losthp"))
        damage_dealt = self.attack(target_kw1="n_random_enemy",target_kw2="5", multiplier=2.0, repeat=1, func_after_dmg=poison_effect)
        return damage_dealt
        
    def skill3(self):
        pass

    def battle_entry_effects(self):
        self.apply_effect(StatsEffect('Slimy', -1, True, {'final_damage_taken_multipler' : -0.1}))



class Thief(Character):
    # Strong damage on buffed targets
    # Winrate 45% after testing
    def __init__(self, name, lvl, exp=0, equip=None, image=None):
        super().__init__(name, lvl, exp, equip, image)
        self.original_name = "Thief"
        self.skill1_description = "Attack 1 enemies with 600% atk."
        self.skill2_description = "Attack random enemy pair with 330% atk 2 times."
        self.skill3_description = "Skill damage increased by 60% for each active buff on target." 
        self.skill1_cooldown_max = 4
        self.skill2_cooldown_max = 4
        self.is_boss = False

    def skill_tooltip(self):
        return f"Skill 1 : {self.skill1_description}\nCooldown : {self.skill1_cooldown} action(s)\n\nSkill 2 : {self.skill2_description}\nCooldown : {self.skill2_cooldown} action(s)\n\nSkill 3 : {self.skill3_description}\n"

    def skill1_logic(self):
        def buffed_target_amplify(self, target, final_damage):
            buffs = [e for e in target.buffs if not e.is_set_effect and not e.duration == -1]
            new_final_damage = final_damage * (1 + 0.6 * len(buffs))
            # if len(buffs) > 0:
            #     print(f"Previous damage : {final_damage}, new damage : {new_final_damage}, buff count : {len(buffs)}")
            return new_final_damage
        damage_dealt = self.attack(multiplier=6.0, repeat=1, func_damage_step=buffed_target_amplify)
        return damage_dealt

    def skill2_logic(self):
        def buffed_target_amplify(self, target, final_damage):
            buffs = [e for e in target.buffs if not e.is_set_effect and not e.duration == -1]
            return final_damage * (1 + 0.6 * len(buffs))
        damage_dealt = self.attack(target_kw1="random_enemy_pair", multiplier=3.3, repeat=2, func_damage_step=buffed_target_amplify)
        return damage_dealt
        
    def skill3(self):
        pass
