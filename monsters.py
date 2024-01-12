import random
from effect import *
from character import Character


# NOTE: use cw.py to estimate winrate
# Normal monsters should have winrate around 40% - 50%
# Boss monsters should have winrate around 65% - 70%


# ====================================
# Heavy Attack Related Monsters
# ====================================

class Panda(Character):
    # 50% winrate after testing
    # tag: heavy attack, stun
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


class Mimic(Character):
    # Tag: Heavy attack, front attack
    # Winrate : near 49%
    def __init__(self, name, lvl, exp=0, equip=None, image=None):
        super().__init__(name, lvl, exp, equip, image)
        self.original_name = "Mimic"
        self.skill1_description = "Attack 1 closest enemy with 1000% atk."
        self.skill2_description = "Attack 1 closest enemy with 1000% atk."
        self.skill3_description = "Skill attack have 10% chance to inflict Stun for 3 turns."
        self.skill1_cooldown_max = 4
        self.skill2_cooldown_max = 4
        self.is_boss = False

    def skill_tooltip(self):
        return f"Skill 1 : {self.skill1_description}\nCooldown : {self.skill1_cooldown} action(s)\n\nSkill 2 : {self.skill2_description}\nCooldown : {self.skill2_cooldown} action(s)\n\nSkill 3 : {self.skill3_description}\n"

    def skill1_logic(self):
        def stun_effect(self, target):
            dice = random.randint(1, 100)
            if dice <= 10:
                target.apply_effect(StunEffect('Stun', duration=3, is_buff=False))
        damage_dealt = self.attack(multiplier=10.0, repeat=1, func_after_dmg=stun_effect, target_kw1="enemy_in_front")
        return damage_dealt

    def skill2_logic(self):
        def stun_effect(self, target):
            dice = random.randint(1, 100)
            if dice <= 10:
                target.apply_effect(StunEffect('Stun', duration=3, is_buff=False))
        damage_dealt = self.attack(multiplier=10.0, repeat=1, func_after_dmg=stun_effect, target_kw1="enemy_in_front")
        return damage_dealt
        
    def skill3(self):
        pass


# ====================================
# End of Heavy Attack Related Monsters
# ====================================
# Negative Status Effect Related Monsters
# ====================================

class Mummy(Character):
    # 45% winrate after testing
    # tag: negative status effect
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
    # tag: boss, negative status effect
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
    # tag: Strong status damage, low damage
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


class Ghost(Character):
    # Tag: Negative status effect, fear
    # Winrate 42% after testing
    def __init__(self, name, lvl, exp=0, equip=None, image=None):
        super().__init__(name, lvl, exp, equip, image)
        self.original_name = "Ghost"
        self.skill1_description = "Attack 5 enemies with 200% atk and apply Fear on targets for 5 turns. Apply chance is 100%, 80%, 60%, 40%, 20% for each enemy depending on how many allies the enemy has. The fewer allies the enemy has, the higher the chance."
        self.skill2_description = "Attack random enemies 4 times with 270% atk."
        self.skill3_description = "Normal attack will try target enemy with Fear first. damage increased by 100% if target has Fear. As long as you are alive, Fear effect gain the following effect: accuracy - 10%."
        self.skill1_cooldown_max = 5
        self.skill2_cooldown_max = 5
        self.is_boss = False
        self.fear_effect_dict = {"acc": -0.1}

    def skill_tooltip(self):
        return f"Skill 1 : {self.skill1_description}\nCooldown : {self.skill1_cooldown} action(s)\n\nSkill 2 : {self.skill2_description}\nCooldown : {self.skill2_cooldown} action(s)\n\nSkill 3 : {self.skill3_description}\n"

    def skill1_logic(self):
        chance_dict = dict(zip(range(1, 6), [100, 80, 60, 40, 20]))
        def fear_effect(self, target):
            dice = random.randint(1, 100)
            if dice <= chance_dict[len(self.enemy)]:
                target.apply_effect(FearEffect('Fear', duration=5, is_buff=False))
        damage_dealt = self.attack(target_kw1="n_random_enemy",target_kw2="5", multiplier=2.0, repeat=1, func_after_dmg=fear_effect)
        return damage_dealt

    def skill2_logic(self):
        damage_dealt = self.attack(multiplier=2.7, repeat=4)
        return damage_dealt
        
    def skill3(self):
        pass

    def normal_attack(self):
        def fear_amplify(self, target, final_damage):
            if target.has_effect_that_named("Fear"):
                final_damage *= 2.0
            return final_damage
        self.attack(func_damage_step=fear_amplify, target_kw1="n_enemy_with_effect", target_kw2="1", target_kw3="Fear")


# ====================================
# End of Negative Status Effect Related Monsters
# ====================================
# Multistrike Related Monsters
# ====================================


class Ninja(Character):
    # Tag: Multi multi strike
    # Winrate: 45%
    def __init__(self, name, lvl, exp=0, equip=None, image=None):
        super().__init__(name, lvl, exp, equip, image)
        self.original_name = "Ninja"
        self.skill1_description = "Attack 12 times with 150% atk."
        self.skill2_description = "For 4 turns, increase evasion by 50%. Attack 8 times with 150% atk"
        self.skill3_description = "Normal attack have 30% chance to reduce all skill cooldown by 1 turn."
        self.skill1_cooldown_max = 4
        self.skill2_cooldown_max = 4
        self.is_boss = False

    def skill_tooltip(self):
        return f"Skill 1 : {self.skill1_description}\nCooldown : {self.skill1_cooldown} action(s)\n\nSkill 2 : {self.skill2_description}\nCooldown : {self.skill2_cooldown} action(s)\n\nSkill 3 : {self.skill3_description}\n"

    def skill1_logic(self):
        damage_dealt = self.attack(multiplier=1.5, repeat=12)
        return damage_dealt

    def skill2_logic(self):
        self.apply_effect(StatsEffect('Evasion', 4, True, {'eva' : 0.5}))
        damage_dealt = self.attack(multiplier=1.5, repeat=8)
        return damage_dealt
        
    def skill3(self):
        pass 

    def normal_attack(self):
        def reduce_cd(self, target):
            dice = random.randint(1, 100)
            if dice <= 30:
                self.skill1_cooldown -= 1
                self.skill2_cooldown -= 1
                self.skill1_cooldown = max(0, self.skill1_cooldown)
                self.skill2_cooldown = max(0, self.skill2_cooldown)
        self.attack(func_after_dmg=reduce_cd)


class KillerBee(Character):
    # Tag: Negative effect, multi multi strike buff, status damage
    # Winrate: 45%
    def __init__(self, name, lvl, exp=0, equip=None, image=None):
        super().__init__(name, lvl, exp, equip, image)
        self.original_name = "Killerbee"
        self.skill1_description = "Attack 4 times with 300% atk"
        self.skill2_description = "Attack 5 enemies with 200% atk"
        self.skill3_description = "Skill attack inflict Sting on target for 4 turns. Sting: every time target take damage, take 35% of applier atk as status damage. Does not trigger for status damage."
        self.skill1_cooldown_max = 4
        self.skill2_cooldown_max = 4
        self.is_boss = False

    def skill_tooltip(self):
        return f"Skill 1 : {self.skill1_description}\nCooldown : {self.skill1_cooldown} action(s)\n\nSkill 2 : {self.skill2_description}\nCooldown : {self.skill2_cooldown} action(s)\n\nSkill 3 : {self.skill3_description}\n"

    def skill1_logic(self):
        def sting_effect(self, target):
            target.apply_effect(StingEffect('Sting', duration=4, is_buff=False, value=0.35 * self.atk, imposter=self))
        damage_dealt = self.attack(multiplier=3.0, repeat=4, func_after_dmg=sting_effect)
        return damage_dealt

    def skill2_logic(self):
        def sting_effect(self, target):
            target.apply_effect(StingEffect('Sting', duration=4, is_buff=False, value=0.35 * self.atk, imposter=self))
        damage_dealt = self.attack(target_kw1="n_random_enemy",target_kw2="5", multiplier=2.0, repeat=1, func_after_dmg=sting_effect)
        return damage_dealt
        
    def skill3(self):
        pass 


class Samurai(Character):
    # 46% winrate after testing
    # tag: multi strike, bleed, low hp strike
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


# ====================================
# End of Multistrike Related Monsters
# ====================================
# Counter High hp Releted Monsters
# ====================================


class Skeleton(Character):
    # Tag: Strong damage against high hp target
    # Winrate: 44%
    def __init__(self, name, lvl, exp=0, equip=None, image=None):
        super().__init__(name, lvl, exp, equip, image)
        self.original_name = "Skeleton"
        self.skill1_description = "Attack enemy with highest hp with 300% atk 3 times."
        self.skill2_description = "Attack enemy with highest hp with 900%, 80% chance to Stun for 3 turns."
        self.skill3_description = "Normal attack has 5% chance to Stun for 2 turns."
        self.skill1_cooldown_max = 3
        self.skill2_cooldown_max = 4
        self.is_boss = False

    def skill_tooltip(self):
        return f"Skill 1 : {self.skill1_description}\nCooldown : {self.skill1_cooldown} action(s)\n\nSkill 2 : {self.skill2_description}\nCooldown : {self.skill2_cooldown} action(s)\n\nSkill 3 : {self.skill3_description}\n"

    def skill1_logic(self):
        damage_dealt = self.attack(multiplier=3.0, repeat=3, target_kw1="n_highest_attr", target_kw2="1", target_kw3="hp", target_kw4="enemy")
        return damage_dealt

    def skill2_logic(self):
        def stun_effect(self, target):
            dice = random.randint(1, 100)
            if dice <= 80:
                target.apply_effect(StunEffect('Stun', duration=3, is_buff=False))
        damage_dealt = self.attack(multiplier=9.0, repeat=1, func_after_dmg=stun_effect, target_kw1="n_highest_attr", target_kw2="1", target_kw3="hp", target_kw4="enemy")
        return damage_dealt
        
    def skill3(self):
        pass

    def normal_attack(self):
        def stun_effect(self, target):
            dice = random.randint(1, 100)
            if dice <= 5:
                target.apply_effect(StunEffect('Stun', duration=2, is_buff=False))
        self.attack(func_after_dmg=stun_effect)


# ====================================
# End of Counter High hp Related Monsters
# ====================================
# Critical Related Monsters
# ====================================


class SoldierB(Character):
    # Tag: Strong critical damage
    # Winrate: 53%
    def __init__(self, name, lvl, exp=0, equip=None, image=None):
        super().__init__(name, lvl, exp, equip, image)
        self.original_name = "SoldierB"
        self.skill1_description = "Attack 4 times with 300% atk."
        self.skill2_description = "Attack 4 times with 270% atk, each attack will trigger the same attack if critical."
        self.skill3_description = "Increase critical rate and critical damage by 30%."
        self.skill1_cooldown_max = 4
        self.skill2_cooldown_max = 3
        self.is_boss = False

    def skill_tooltip(self):
        return f"Skill 1 : {self.skill1_description}\nCooldown : {self.skill1_cooldown} action(s)\n\nSkill 2 : {self.skill2_description}\nCooldown : {self.skill2_cooldown} action(s)\n\nSkill 3 : {self.skill3_description}\n"

    def skill1_logic(self):
        damage_dealt = self.attack(multiplier=3.0, repeat=4)
        return damage_dealt

    def skill2_logic(self):
        def additional_attack(self, target, is_crit):
            if is_crit:
                if self.running and self.logging:
                    self.text_box.append_html_text(f"{self.name} triggered additional attack.\n")
                fine_print(f"{self.name} triggered additional attack.", mode=self.fineprint_mode)
                return self.attack(multiplier=2.7, repeat=1)
            else:
                return 0
        damage_dealt = self.attack(multiplier=2.7, repeat=3, additional_attack_after_dmg=additional_attack)
        return damage_dealt
        
    def skill3(self):
        pass

    def battle_entry_effects(self):
        self.apply_effect(StatsEffect('SoldierB Passive', -1, True, {'crit' : 0.3, 'critdmg' : 0.3}))


# ====================================
# End of Critical Related Monsters
# ====================================
# Defence Related Monsters
# ====================================
        

class Paladin(Character):
    # Tag: Defense and Counter against high damage
    # Winrate: 48.6%
    def __init__(self, name, lvl, exp=0, equip=None, image=None):
        super().__init__(name, lvl, exp, equip, image)
        self.original_name = "paladin"
        self.skill1_description = "Attack 1 enemy with 800% atk."
        self.skill2_description = "Attack 1 enemy 3 times with 300% atk."
        self.skill3_description = "When taking damage and damage is exceed 10% of maxhp, reduce damage taken by 50%. The attacker takes 30% of damage reduced."
        self.skill1_cooldown_max = 4
        self.skill2_cooldown_max = 4
        self.is_boss = False

    def skill_tooltip(self):
        return f"Skill 1 : {self.skill1_description}\nCooldown : {self.skill1_cooldown} action(s)\n\nSkill 2 : {self.skill2_description}\nCooldown : {self.skill2_cooldown} action(s)\n\nSkill 3 : {self.skill3_description}\n"

    def skill1_logic(self):
        damage_dealt = self.attack(multiplier=8.0, repeat=1)
        return damage_dealt

    def skill2_logic(self):
        damage_dealt = self.attack(multiplier=3.0, repeat=3)
        return damage_dealt
        
    def skill3(self):
        pass

    def battle_entry_effects(self):
        self.apply_effect(EffectShield3('Shielded', -1, True, 0.5, 0.3))
         

class Father(Character):
    # Tag: Buff: Cancellation shield against low damage
    # Winrate: 44%
    def __init__(self, name, lvl, exp=0, equip=None, image=None):
        super().__init__(name, lvl, exp, equip, image)
        self.original_name = "Father"
        self.skill1_description = "Apply Cancellation Shield on 3 allies with lowest hp, all damage lower than 10% of maxhp is reduced to 0. Shield last 4 turns."
        self.skill2_description = "Attack 3 random enemies with 500% atk."
        self.skill3_description = "All damage taken is reduced by 20%, damage taken lower than 10% of maxhp is reduced to 0."
        self.skill1_cooldown_max = 4
        self.skill2_cooldown_max = 3
        self.is_boss = False

    def skill_tooltip(self):
        return f"Skill 1 : {self.skill1_description}\nCooldown : {self.skill1_cooldown} action(s)\n\nSkill 2 : {self.skill2_description}\nCooldown : {self.skill2_cooldown} action(s)\n\nSkill 3 : {self.skill3_description}\n"

    def skill1_logic(self):
        targets = self.target_selection(keyword="n_lowest_attr", keyword2="3", keyword3="hp", keyword4="ally")
        for target in targets:
            target.apply_effect(CancellationShield3('Cancellation Shield', 4, True, 0.1, False))

    def skill2_logic(self):
        damage_dealt = self.attack(multiplier=5.0, repeat=1, target_kw1="n_random_enemy", target_kw2="3")
        return damage_dealt
        
    def skill3(self):
        pass

    def battle_entry_effects(self):
        self.apply_effect(CancellationShield3('Father Passive', -1, True, 0.1, False))
        self.apply_effect(StatsEffect('Father Passive', -1, True, {'final_damage_taken_multipler' : -0.20}))
         

class Kobold(Character):
    # Tag: High defence
    # Winrate: 44%
    def __init__(self, name, lvl, exp=0, equip=None, image=None):
        super().__init__(name, lvl, exp, equip, image)
        self.original_name = "Kobold"
        self.skill1_description = "Recover hp by 30% of maxhp and increase defence by 50% for 5 turns. If you are the only one alive, effect is increased by 100%."
        self.skill2_description = "Attack 1 enemy with 800% atk, if you are the only one alive, increase damage by 100%."
        self.skill3_description = "Defence and maxhp is increased by 25%."
        self.skill1_cooldown_max = 4
        self.skill2_cooldown_max = 3
        self.is_boss = False

    def skill_tooltip(self):
        return f"Skill 1 : {self.skill1_description}\nCooldown : {self.skill1_cooldown} action(s)\n\nSkill 2 : {self.skill2_description}\nCooldown : {self.skill2_cooldown} action(s)\n\nSkill 3 : {self.skill3_description}\n"

    def skill1_logic(self):
        if len(self.ally) == 1:
            self.heal_hp(self.maxhp * 0.6, self)
            self.apply_effect(StatsEffect('Kobold Power', 5, True, {'defense' : 2.0}))
        else:
            self.heal_hp(self.maxhp * 0.3, self)
            self.apply_effect(StatsEffect('Kobold Power', 5, True, {'defense' : 1.5}))
        return 0

    def skill2_logic(self):
        def additional_damage(self, target, final_damage):
            if len(self.ally) == 1:
                final_damage *= 2.0
            return final_damage
        damage_dealt = self.attack(multiplier=8.0, repeat=1, func_damage_step=additional_damage)
        return damage_dealt

    def skill3(self):
        pass

    def battle_entry_effects(self):
        self.apply_effect(StatsEffect('Kobold Passive', -1, True, {'defense' : 1.25, 'maxhp' : 1.25}))


class SoldierA(Character):
    # Tag: Defence Break
    # Winrate: 46%
    def __init__(self, name, lvl, exp=0, equip=None, image=None):
        super().__init__(name, lvl, exp, equip, image)
        self.original_name = "SoldierA"
        self.skill1_description = "Attack enemy with highest defence with 400% atk 3 times, each attack will reduce target defence by 35% for 3 turns."
        self.skill2_description = "Attack all enemies with 200% atk and reduce defence by 35% for 5 turns."
        self.skill3_description = "Skill attack have 30% chance to inflict Bleed for 3 turns. Bleed: takes 30% of atk as status damage per turn."
        self.skill1_cooldown_max = 4
        self.skill2_cooldown_max = 4
        self.is_boss = False

    def skill_tooltip(self):
        return f"Skill 1 : {self.skill1_description}\nCooldown : {self.skill1_cooldown} action(s)\n\nSkill 2 : {self.skill2_description}\nCooldown : {self.skill2_cooldown} action(s)\n\nSkill 3 : {self.skill3_description}\n"

    def skill1_logic(self):
        def bleed_effect_defence_break(self, target):
            dice = random.randint(1, 100)
            if dice <= 30:
                target.apply_effect(ContinuousDamageEffect('Bleed', duration=3, is_buff=False, value=0.3 * self.atk, imposter=self))
            target.apply_effect(StatsEffect('Defence Break', 3, False, {'defense' : 0.65}))
        damage_dealt = self.attack(multiplier=4.0, repeat=3, func_after_dmg=bleed_effect_defence_break, target_kw1="n_highest_attr", target_kw2="1", target_kw3="defense", target_kw4="enemy")
        return damage_dealt

    def skill2_logic(self):
        def bleed_effect_defence_break(self, target):
            dice = random.randint(1, 100)
            if dice <= 30:
                target.apply_effect(ContinuousDamageEffect('Bleed', duration=3, is_buff=False, value=0.3 * self.atk, imposter=self))
            target.apply_effect(StatsEffect('Defence Break', 5, False, {'defense' : 0.65}))
        damage_dealt = self.attack(multiplier=2.0, repeat=1, func_after_dmg=bleed_effect_defence_break, target_kw1="n_random_enemy", target_kw2="5")
        return damage_dealt
        
    def skill3(self):
        pass


class FutureSoldier(Character):
    # Tag: Against low defence target
    # Winrate: 48%
    def __init__(self, name, lvl, exp=0, equip=None, image=None):
        super().__init__(name, lvl, exp, equip, image)
        self.original_name = "FutureSoldier"
        self.skill1_description = "Attack enemies 5 times with 200% atk, each attack reduces target defence by 30% for 4 turns." # 0.7**5 = 0.168
        self.skill2_description = "Attack enemies 7 times with 150% atk, if target has lower defence than self, increase damage by 100%."
        self.skill3_description = "Normal attack deals double damage if target has lower defence than self."
        self.skill1_cooldown_max = 4
        self.skill2_cooldown_max = 4
        self.is_boss = False

    def skill_tooltip(self):
        return f"Skill 1 : {self.skill1_description}\nCooldown : {self.skill1_cooldown} action(s)\n\nSkill 2 : {self.skill2_description}\nCooldown : {self.skill2_cooldown} action(s)\n\nSkill 3 : {self.skill3_description}\n"

    def skill1_logic(self):
        def defence_break(self, target):
            target.apply_effect(StatsEffect('Defence Break', 4, False, {'defense' : 0.7}))
        damage_dealt = self.attack(multiplier=2.0, repeat=5, func_after_dmg=defence_break)
        return damage_dealt

    def skill2_logic(self):
        def damage_amplify(self, target, final_damage):
            if target.defense < self.defense:
                final_damage *= 2.0
            return final_damage
        damage_dealt = self.attack(multiplier=1.5, repeat=7, func_damage_step=damage_amplify)
        return damage_dealt
        
    def skill3(self):
        pass

    def normal_attack(self):
        def damage_amplify(self, target, final_damage):
            if target.defense < self.defense:
                final_damage *= 2.0
            return final_damage
        self.attack(func_damage_step=damage_amplify)


class FutureElite(Character):
    # Tag: Against low defence target
    # Winrate: 70.6%
    def __init__(self, name, lvl, exp=0, equip=None, image=None):
        super().__init__(name, lvl, exp, equip, image)
        self.original_name = "FutureElite"
        self.skill1_description = "Attack all enemies with 400% atk, reduce defence by 40% for 6 turns."
        self.skill2_description = "Attack enemies 8 times with 200% atk, if target has lower defence than self, damage increased by a percentage equal to the ratio between self and target defence."
        # for example: self.defence = 100, target.defence = 50, damage increased by 100%
        self.skill3_description = "defence is increased by 30%."
        self.skill1_cooldown_max = 4
        self.skill2_cooldown_max = 4
        self.is_boss = True

    def skill_tooltip(self):
        return f"Skill 1 : {self.skill1_description}\nCooldown : {self.skill1_cooldown} action(s)\n\nSkill 2 : {self.skill2_description}\nCooldown : {self.skill2_cooldown} action(s)\n\nSkill 3 : {self.skill3_description}\n"

    def skill1_logic(self):
        def defence_break(self, target):
            target.apply_effect(StatsEffect('Defence Break', 6, False, {'defense' : 0.6}))
        damage_dealt = self.attack(multiplier=4.0, repeat=1, func_after_dmg=defence_break, target_kw1="n_random_enemy", target_kw2="5")
        return damage_dealt

    def skill2_logic(self):
        def damage_amplify(self, target, final_damage):
            if target.defense < self.defense:
                final_damage *= 1 + (self.defense / target.defense)
            return final_damage
        damage_dealt = self.attack(multiplier=2.0, repeat=8, func_damage_step=damage_amplify)
        return damage_dealt
        
    def skill3(self):
        pass

    def battle_entry_effects(self):
        self.apply_effect(StatsEffect('FutureElite Passive', -1, True, {'defense' : 1.3}))


# ====================================
# End of Defence Related Monsters
# ====================================
# Status Damage Burn Related Monsters
# ====================================
        



# ====================================
# End of Status Damage Burn Related Monsters
# ====================================
# Unclassifiable Monsters
# ====================================
        

class Cockatorice(Character):
    # Tag: Buff when not receiving damage for 4 turns
    # Winrate: 48.7%
    def __init__(self, name, lvl, exp=0, equip=None, image=None):
        super().__init__(name, lvl, exp, equip, image)
        self.original_name = "Cockatorice"
        self.skill1_description = "Attack 3 enemies at front, with 330% atk."
        self.skill2_description = "Attack random enemies 3 times with 330% atk."
        self.skill3_description = "For 4 turns, if not taking damage, increase atk by 66% and spd by 66% for 4 turns at the end of turn. Same effect cannot be applied twice."
        self.skill1_cooldown_max = 4
        self.skill2_cooldown_max = 4
        self.is_boss = False

    def skill_tooltip(self):
        return f"Skill 1 : {self.skill1_description}\nCooldown : {self.skill1_cooldown} action(s)\n\nSkill 2 : {self.skill2_description}\nCooldown : {self.skill2_cooldown} action(s)\n\nSkill 3 : {self.skill3_description}\n"

    def skill1_logic(self):
        damage_dealt = self.attack(multiplier=3.3, repeat=3, target_kw1="n_ememy_in_front", target_kw2="3")
        return damage_dealt

    def skill2_logic(self):
        damage_dealt = self.attack(multiplier=3.3, repeat=3)
        return damage_dealt
        
    def skill3(self):
        pass

    def battle_entry_effects(self):
        self.apply_effect(NotTakingDamageEffect("Cockatorice Passive", -1, True, {'atk' : 1.66, 'spd' : 1.66}, "default", 4, "Cockatorice Fanatic", 4))


class Thief(Character):
    # Tag: Strong damage on buffed targets
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


class Fanatic(Character):
    # Tag: Strong damage when not receiving damage for 4 turns
    # Winrate: 51%
    def __init__(self, name, lvl, exp=0, equip=None, image=None):
        super().__init__(name, lvl, exp, equip, image)
        self.original_name = "Fanatic"
        self.skill1_description = "Attack front enemy with 350% atk 3 times. If has not taken damage for 4 turns, land critical strikes."
        self.skill2_description = "Attack front enemy with 350% atk 3 times. If has not taken damage for 4 turns, damage is increased by 5% of target maxhp."
        self.skill3_description = "Recover hp by 30% of damage dealt in skill attacks."
        self.skill1_cooldown_max = 4
        self.skill2_cooldown_max = 4
        self.is_boss = False

    def skill_tooltip(self):
        return f"Skill 1 : {self.skill1_description}\nCooldown : {self.skill1_cooldown} action(s)\n\nSkill 2 : {self.skill2_description}\nCooldown : {self.skill2_cooldown} action(s)\n\nSkill 3 : {self.skill3_description}\n"

    def skill1_logic(self):
        if self.get_num_of_turns_not_taken_damage() < 4:
            damage_dealt = self.attack(multiplier=3.5, repeat=3, target_kw1="enemy_in_front")
        else:
            damage_dealt = self.attack(multiplier=3.5, repeat=3, target_kw1="enemy_in_front", always_crit=True)
        if self.is_alive():
            self.heal_hp(damage_dealt * 0.3, self)
        return damage_dealt

    def skill2_logic(self):
        def damage_amplify(self, target, final_damage):
            if self.get_num_of_turns_not_taken_damage() >= 4:
                final_damage += target.maxhp * 0.05
            return final_damage
        damage_dealt = self.attack(multiplier=3.5, repeat=3, target_kw1="enemy_in_front", func_damage_step=damage_amplify)
        if self.is_alive():
            self.heal_hp(damage_dealt * 0.3, self)
        return damage_dealt

        
    def skill3(self):
        pass


# ====================================
# End of Unclassifiable Monsters
# ====================================