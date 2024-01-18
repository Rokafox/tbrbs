from itertools import zip_longest
import random
from effect import *
import character
import global_vars


# NOTE: use cw.py to estimate winrate
# Normal monsters should have winrate around 40% - 50%
# Boss monsters should have winrate around 65% - 70%


# ====================================
# Heavy Attack
# ====================================

class Panda(character.Character):
    def __init__(self, name, lvl, exp=0, equip=None, image=None):
        super().__init__(name, lvl, exp, equip, image)
        self.original_name = "Panda"
        self.skill1_description = "Attack 1 closest enemy with 800% atk."
        self.skill2_description = "Attack 1 closest enemy with 700% atk and 70% chance to stun the target for 4 turns."
        self.skill3_description = "Increase maxhp by 50%."
        self.skill1_cooldown_max = 5
        self.skill2_cooldown_max = 5
        self.is_boss = False
        self.monster_role = "Heavy Attack"

    def skill_tooltip(self):
        return f"Skill 1 : {self.skill1_description}\nCooldown : {self.skill1_cooldown} action(s)\n\nSkill 2 : {self.skill2_description}\nCooldown : {self.skill2_cooldown} action(s)\n\nSkill 3 : {self.skill3_description}\n"

    def skill1_logic(self):
        damage_dealt = self.attack(multiplier=8.0, repeat=1, target_kw1="enemy_in_front")
        return damage_dealt

    def skill2_logic(self):
        def stun_effect(self, target):
            dice = random.randint(1, 100)
            if dice <= 70:
                target.apply_effect(StunEffect('Stun', duration=4, is_buff=False))
        damage_dealt = self.attack(multiplier=7.0, repeat=1, func_after_dmg=stun_effect, target_kw1="enemy_in_front")
        return damage_dealt
        
    def skill3(self):
        pass

    def battle_entry_effects(self):
        self.apply_effect(StatsEffect('Fat', -1, True, {'maxhp' : 1.5}))
        self.hp = self.maxhp


class Mimic(character.Character):
    def __init__(self, name, lvl, exp=0, equip=None, image=None):
        super().__init__(name, lvl, exp, equip, image)
        self.original_name = "Mimic"
        self.skill1_description = "Attack 1 closest enemy with 1000% atk."
        self.skill2_description = "Attack 1 closest enemy with 1000% atk."
        self.skill3_description = "Skill attack have 10% chance to inflict Stun for 3 turns."
        self.skill1_cooldown_max = 4
        self.skill2_cooldown_max = 4
        self.is_boss = False
        self.monster_role = "Heavy Attack"

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


class MoHawk(character.Character):
    def __init__(self, name, lvl, exp=0, equip=None, image=None):
        super().__init__(name, lvl, exp, equip, image)
        self.original_name = "MoHawk"
        self.skill1_description = "Attack 1 closest enemy with 680% atk and inflict bleed for 4 turns. Bleed: take 120% of applier atk as status damage each turn."
        self.skill2_description = "Attack 1 closest enemy with 680% atk and inflict bleed for 4 turns."
        self.skill3_description = "Increase atk by 20%."
        self.skill1_cooldown_max = 5
        self.skill2_cooldown_max = 5
        self.is_boss = False
        self.monster_role = "Heavy Attack"

    def skill_tooltip(self):
        return f"Skill 1 : {self.skill1_description}\nCooldown : {self.skill1_cooldown} action(s)\n\nSkill 2 : {self.skill2_description}\nCooldown : {self.skill2_cooldown} action(s)\n\nSkill 3 : {self.skill3_description}\n"

    def skill1_logic(self):
        def bleed_effect(self, target):
            target.apply_effect(ContinuousDamageEffect('Bleed', duration=4, is_buff=False, value=1.2 * self.atk, imposter=self))
        damage_dealt = self.attack(multiplier=6.8, repeat=1, func_after_dmg=bleed_effect, target_kw1="enemy_in_front")
        return damage_dealt

    def skill2_logic(self):
        def bleed_effect(self, target):
            target.apply_effect(ContinuousDamageEffect('Bleed', duration=4, is_buff=False, value=1.2 * self.atk, imposter=self))
        damage_dealt = self.attack(multiplier=6.8, repeat=1, func_after_dmg=bleed_effect, target_kw1="enemy_in_front")
        return damage_dealt
        
    def skill3(self):
        pass

    def battle_entry_effects(self):
        self.apply_effect(StatsEffect('MoHawk Passive', -1, True, {'atk' : 1.2}))


class Earth(character.Character):
    # tag: CC, stun, high hp
    # Winrate: 53%
    def __init__(self, name, lvl, exp=0, equip=None, image=None):
        super().__init__(name, lvl, exp, equip, image)
        self.original_name = "Earth"
        self.skill1_description = "Attack all enemies with 240% atk, 50% chance to inflict Stun for 3 turns."
        self.skill2_description = "Attack 1 closest enemy with 700% atk, 70% chance to inflict Stun for 3 turns."
        self.skill3_description = "hp is increased by 100%."
        self.skill1_cooldown_max = 5
        self.skill2_cooldown_max = 5
        self.is_boss = False
        self.monster_role = "Heavy Attack"

    def skill_tooltip(self):
        return f"Skill 1 : {self.skill1_description}\nCooldown : {self.skill1_cooldown} action(s)\n\nSkill 2 : {self.skill2_description}\nCooldown : {self.skill2_cooldown} action(s)\n\nSkill 3 : {self.skill3_description}\n"

    def skill1_logic(self):
        def stun_effect(self, target):
            dice = random.randint(1, 100)
            if dice <= 50:
                target.apply_effect(StunEffect('Stun', duration=3, is_buff=False))
        damage_dealt = self.attack(multiplier=2.4, repeat=1, func_after_dmg=stun_effect, target_kw1="n_random_enemy", target_kw2="5")
        return damage_dealt


    def skill2_logic(self):
        def stun_effect(self, target):
            dice = random.randint(1, 100)
            if dice <= 70:
                target.apply_effect(StunEffect('Stun', duration=3, is_buff=False))
        damage_dealt = self.attack(multiplier=7.0, repeat=1, func_after_dmg=stun_effect, target_kw1="enemy_in_front")
        return damage_dealt

    def skill3(self):
        pass

    def battle_entry_effects(self):
        self.apply_effect(StatsEffect('Earth Passive', -1, True, {'maxhp' : 2.0}))
        self.hp = self.maxhp


class Golem(character.Character):
    def __init__(self, name, lvl, exp=0, equip=None, image=None):
        super().__init__(name, lvl, exp, equip, image)
        self.original_name = "Golem"
        self.skill1_description = "Attack all enemies with 500% atk."
        self.skill2_description = "Attack 1 closest enemy with 700% atk. Damage increased by target's hp percentage. Max bonus damage: 100%."
        self.skill3_description = "Increase hp by 200%."
        self.skill1_cooldown_max = 5
        self.skill2_cooldown_max = 5
        self.is_boss = True
        self.monster_role = "Heavy Attack"

    def skill_tooltip(self):
        return f"Skill 1 : {self.skill1_description}\nCooldown : {self.skill1_cooldown} action(s)\n\nSkill 2 : {self.skill2_description}\nCooldown : {self.skill2_cooldown} action(s)\n\nSkill 3 : {self.skill3_description}\n"

    def skill1_logic(self):
        damage_dealt = self.attack(multiplier=5.0, repeat=1, target_kw1="n_random_enemy", target_kw2="5")
        return damage_dealt

    def skill2_logic(self):
        def amplify(self, target, final_damage):
            final_damage *= min(2.0, 1.0 + (1.0 - target.hp / target.maxhp))
            return final_damage
        damage_dealt = self.attack(multiplier=7.0, repeat=1, func_damage_step=amplify, target_kw1="enemy_in_front")
        return damage_dealt
        
    def skill3(self):
        pass

    def battle_entry_effects(self):
        self.apply_effect(StatsEffect('Golem Passive', -1, True, {'maxhp' : 3.0}))
        self.hp = self.maxhp


# ====================================
# End of Heavy Attack
# ====================================
# Negative Status
# Negative status by those monsters are either lethal or high status damage or annoying
# ====================================

class Mummy(character.Character):
    def __init__(self, name, lvl, exp=0, equip=None, image=None):
        super().__init__(name, lvl, exp, equip, image)
        self.original_name = "Mummy"
        self.skill1_description = "Attack 3 closest enemies with 300% atk."
        self.skill2_description = "Attack 5 enemies with 200% atk and 50% chance to inflict Curse for 4 turns. Curse: atk is reduced by 40%, unstackable."
        self.skill3_description = "When taking damage, 30% chance to inflict Curse on attacker for 4 turns. Curse: atk is reduced by 40%, unstackable."
        self.skill1_cooldown_max = 5
        self.skill2_cooldown_max = 5
        self.is_boss = False

    def skill_tooltip(self):
        return f"Skill 1 : {self.skill1_description}\nCooldown : {self.skill1_cooldown} action(s)\n\nSkill 2 : {self.skill2_description}\nCooldown : {self.skill2_cooldown} action(s)\n\nSkill 3 : {self.skill3_description}\n"

    def skill1_logic(self):
        damage_dealt = self.attack(target_kw1="n_enemy_in_front",target_kw2="3", multiplier=3.0, repeat=1)
        return damage_dealt

    def skill2_logic(self):
        def curse_effect(self, target):
            dice = random.randint(1, 100)
            if dice <= 50:
                curse = StatsEffect('Curse', duration=4, is_buff=False, stats_dict={'atk' : 0.6})
                curse.apply_rule = "stack"
                target.apply_effect(curse)
        damage_dealt = self.attack(target_kw1="n_random_enemy",target_kw2="5", multiplier=2.0, repeat=1, func_after_dmg=curse_effect)
        return damage_dealt
        
    def skill3(self):
        pass

    def take_damage_aftermath(self, damage, attacker):
        if random.randint(1, 100) <= 30:
            curse = StatsEffect('Curse', duration=4, is_buff=False, stats_dict={'atk' : 0.6})
            curse.apply_rule = "stack"
            attacker.apply_effect(curse)


class Pharaoh(character.Character):
    # Boss
    def __init__(self, name, lvl, exp=0, equip=None, image=None):
        super().__init__(name, lvl, exp, equip, image)
        self.original_name = "Pharaoh"
        self.skill1_description = "Attack 3 closest enemies with 320% atk. If target is cursed, damage is increased by 100%."
        self.skill2_description = "Attack 3 closest enemies with 320% atk and 80% chance to inflict Curse for 4 turns. If target is cursed, damage is increased by 100%. Curse: atk is reduced by 40%, unstackable."
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
        damage_dealt = self.attack(target_kw1="n_enemy_in_front",target_kw2="3", multiplier=3.2, repeat=1, func_damage_step=curse_amplify)
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
        damage_dealt = self.attack(target_kw1="n_enemy_in_front",target_kw2="3", multiplier=3.2, repeat=1, func_damage_step=curse_amplify, func_after_dmg=curse_effect)
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


class PoisonSlime(character.Character):
    def __init__(self, name, lvl, exp=0, equip=None, image=None):
        super().__init__(name, lvl, exp, equip, image)
        self.original_name = "Poison_Slime"
        self.skill1_description = "Attack 5 enemies with 150% atk and 66% chance to inflict Poison for 4 turns. Poison: takes 7% of current hp status damage per turn."
        self.skill2_description = "Attack 5 enemies with 150% atk and 66% chance to inflict Poison for 4 turns. Poison: takes 7% of lost hp status damage per turn."
        self.skill3_description = "Reduce damage taken by 10%"
        self.skill1_cooldown_max = 5
        self.skill2_cooldown_max = 5
        self.is_boss = False

    def skill_tooltip(self):
        return f"Skill 1 : {self.skill1_description}\nCooldown : {self.skill1_cooldown} action(s)\n\nSkill 2 : {self.skill2_description}\nCooldown : {self.skill2_cooldown} action(s)\n\nSkill 3 : {self.skill3_description}\n"

    def skill1_logic(self):
        def poison_effect(self, target):
            dice = random.randint(1, 100)
            if dice <= 66:
                target.apply_effect(PoisonDamageEffect('Poison', duration=4, is_buff=False, value=0.07, imposter=self, base="hp"))
        damage_dealt = self.attack(target_kw1="n_random_enemy",target_kw2="5", multiplier=1.5, repeat=1, func_after_dmg=poison_effect)
        return damage_dealt

    def skill2_logic(self):
        def poison_effect(self, target):
            dice = random.randint(1, 100)
            if dice <= 66:
                target.apply_effect(PoisonDamageEffect('Poison', duration=4, is_buff=False, value=0.07, imposter=self, base="losthp"))
        damage_dealt = self.attack(target_kw1="n_random_enemy",target_kw2="5", multiplier=1.5, repeat=1, func_after_dmg=poison_effect)
        return damage_dealt
        
    def skill3(self):
        pass

    def battle_entry_effects(self):
        self.apply_effect(StatsEffect('Slimy', -1, True, {'final_damage_taken_multipler' : -0.1}))


class MadScientist(character.Character):
    # Boss
    def __init__(self, name, lvl, exp=0, equip=None, image=None):
        super().__init__(name, lvl, exp, equip, image)
        self.original_name = "MadScientist"
        self.skill1_description = "Attack all enemies with 200% atk and inflict plague for 12 turns with 50% chance each. Plague: at end of turn, 30% chance to apply the same effect to a neighbor ally, every turn, take 7% of lost hp as status damage."
        self.skill2_description = "Attack 3 closest enemies with 300% atk, if target is inflicted with plague, healing efficiency is reduced by 50% for 6 turns."
        self.skill3_description = "Normal attack have 10% chance to inflict plague for 12 turns and deals 20% more damage."
        self.skill1_cooldown_max = 5
        self.skill2_cooldown_max = 4
        self.is_boss = True

    def skill_tooltip(self):
        return f"Skill 1 : {self.skill1_description}\nCooldown : {self.skill1_cooldown} action(s)\n\nSkill 2 : {self.skill2_description}\nCooldown : {self.skill2_cooldown} action(s)\n\nSkill 3 : {self.skill3_description}\n"

    def skill1_logic(self):
        def plague_effect(self, target):
            dice = random.randint(1, 100)
            if dice <= 50:
                target.apply_effect(PlagueEffect('Plague', duration=12, is_buff=False, value=0.07, imposter=self, base="losthp", transmission_chance=0.3))
        damage_dealt = self.attack(target_kw1="n_random_enemy", target_kw2="5", multiplier=2.0, repeat=1, func_after_dmg=plague_effect)
        return damage_dealt

    def skill2_logic(self):
        def plague_effect(self, target):
            if target.has_effect_that_named("Plague", None, "PlagueEffect"):
                target.apply_effect(StatsEffect('Healing Down', duration=6, is_buff=False, stats_dict={'heal_efficiency' : -0.5}))
        damage_dealt = self.attack(target_kw1="n_enemy_in_front", target_kw2="3", multiplier=3.0, repeat=1, func_after_dmg=plague_effect)
        return damage_dealt
        
    def skill3(self):
        pass

    def normal_attack(self):
        def plague_effect(self, target):
            dice = random.randint(1, 100)
            if dice <= 10:
                target.apply_effect(PlagueEffect('Plague', duration=12, is_buff=False, value=0.07, imposter=self, base="losthp", transmission_chance=0.3))
        def amplify(self, target, final_damage):
            final_damage *= 1.2
            return final_damage
        self.attack(func_after_dmg=plague_effect, func_damage_step=amplify)


class Ghost(character.Character):
    def __init__(self, name, lvl, exp=0, equip=None, image=None):
        super().__init__(name, lvl, exp, equip, image)
        self.original_name = "Ghost"
        self.skill1_description = "Attack 5 enemies with 200% atk and apply Fear on targets for 6 turns. Apply chance is 100%, 80%, 60%, 30%, 0% for each enemy depending on how many allies the enemy has. The fewer allies the enemy has, the higher the chance."
        self.skill2_description = "Attack closest enemy 4 times with 200% atk."
        self.skill3_description = "Normal attack will try target enemy with Fear first. damage increased by 100% if target has Fear. As long as you are alive, Fear effect gain the following effect: accuracy - 20%."
        self.skill1_cooldown_max = 5
        self.skill2_cooldown_max = 5
        self.is_boss = False
        self.fear_effect_dict = {"acc": -0.20}

    def skill_tooltip(self):
        return f"Skill 1 : {self.skill1_description}\nCooldown : {self.skill1_cooldown} action(s)\n\nSkill 2 : {self.skill2_description}\nCooldown : {self.skill2_cooldown} action(s)\n\nSkill 3 : {self.skill3_description}\n"

    def skill1_logic(self):
        chance_dict = dict(zip_longest(range(1, 11), [100, 80, 60, 30, 0], fillvalue=0))
        def fear_effect(self, target):
            dice = random.randint(1, 100)
            if dice <= chance_dict[len(self.enemy)]:
                target.apply_effect(FearEffect('Fear', duration=6, is_buff=False))
        damage_dealt = self.attack(target_kw1="n_random_enemy",target_kw2="5", multiplier=2.0, repeat=1, func_after_dmg=fear_effect)
        return damage_dealt

    def skill2_logic(self):
        damage_dealt = self.attack(target_kw1="enemy_in_front", multiplier=2.0, repeat=4)
        return damage_dealt
        
    def skill3(self):
        pass

    def normal_attack(self):
        def fear_amplify(self, target, final_damage):
            if target.has_effect_that_named("Fear"):
                final_damage *= 2.0
            return final_damage
        self.attack(func_damage_step=fear_amplify, target_kw1="n_enemy_with_effect", target_kw2="1", target_kw3="Fear")


class Death(character.Character):
    # Boss
    def __init__(self, name, lvl, exp=0, equip=None, image=None):
        super().__init__(name, lvl, exp, equip, image)
        self.original_name = "Death"
        self.skill1_description = "Attack 5 enemies with 360% atk and apply Fear on targets for 7 turns. Apply chance is 100%, 80%, 60%, 30%, 0% for each enemy depending on how many allies the enemy has. The fewer allies the enemy has, the higher the chance."
        self.skill2_description = "Attack 3 enemies with lowest hp with 400% atk. If target hp is below 15%, execute target and heal for 20% hp of maxhp. If enemy survived the attack and has Fear, the enemy is confused for 4 turns."
        self.skill3_description = " Normal attack have 10% chance to inflict Fear for 7 turns. maxhp, defense and atk is increased by 20%. As long as you are alive, Fear effect gain the following effect: atk - 20%, accuracy - 40%."
        self.skill1_cooldown_max = 4
        self.skill2_cooldown_max = 4
        self.is_boss = True
        self.fear_effect_dict = {"acc": -0.40, "atk": 0.7}

    def skill_tooltip(self):
        return f"Skill 1 : {self.skill1_description}\nCooldown : {self.skill1_cooldown} action(s)\n\nSkill 2 : {self.skill2_description}\nCooldown : {self.skill2_cooldown} action(s)\n\nSkill 3 : {self.skill3_description}\n"

    def skill1_logic(self):
        chance_dict = dict(zip_longest(range(1, 11), [100, 80, 60, 30, 0], fillvalue=0))
        def fear_effect(self, target):
            dice = random.randint(1, 100)
            if dice <= chance_dict[len(self.enemy)]:
                target.apply_effect(FearEffect('Fear', duration=7, is_buff=False))
        damage_dealt = self.attack(target_kw1="n_random_enemy",target_kw2="5", multiplier=3.6, repeat=1, func_after_dmg=fear_effect)
        return damage_dealt


    def skill2_logic(self):
        def execute(self, target):
            if target.hp < target.maxhp * 0.15 and not target.is_dead():
                target.take_bypass_status_effect_damage(target.hp, self)
                if self.is_alive():
                    self.heal_hp(self.maxhp * 0.2, self)
            else:
                if target.has_effect_that_named("Fear"):
                    target.apply_effect(ConfuseEffect('Confuse', duration=4, is_buff=False))
        damage_dealt = self.attack(target_kw1="n_lowest_attr",target_kw2="3",target_kw3="hp",target_kw4="enemy", multiplier=4.0, repeat=1, func_after_dmg=execute)
        return damage_dealt

        
    def skill3(self):
        pass

    def normal_attack(self):
        def fear_effect(self, target):
            dice = random.randint(1, 100)
            if dice <= 10:
                target.apply_effect(FearEffect('Fear', duration=7, is_buff=False))
        self.attack(func_after_dmg=fear_effect)

    def battle_entry_effects(self):
        self.apply_effect(StatsEffect('Strong', -1, True, {'maxhp' : 1.2, 'atk' : 1.2, 'defense' : 1.2}))
        self.hp = self.maxhp


class Gargoyle(character.Character):
    def __init__(self, name, lvl, exp=0, equip=None, image=None):
        super().__init__(name, lvl, exp, equip, image)
        self.original_name = "Gargoyle"
        self.skill1_description = "Attack closest enemy 3 times with 210% atk."
        self.skill2_description = "Attack closest enemy 3 times with 210% atk."
        self.skill3_description = "Reduce damage taken by 10%. When taking damage, 60% chance to inflict Bleed and Poison on attacker for 4 turns. Bleed: take 80% of applier atk as status damage each turn. Poison: takes 5% of current hp as status damage per turn."
        self.skill1_cooldown_max = 5
        self.skill2_cooldown_max = 5
        self.is_boss = False

    def skill_tooltip(self):
        return f"Skill 1 : {self.skill1_description}\nCooldown : {self.skill1_cooldown} action(s)\n\nSkill 2 : {self.skill2_description}\nCooldown : {self.skill2_cooldown} action(s)\n\nSkill 3 : {self.skill3_description}\n"

    def skill1_logic(self):
        damage_dealt = self.attack(multiplier=2.1, repeat=3, target_kw1="enemy_in_front")
        return damage_dealt

    def skill2_logic(self):
        damage_dealt = self.attack(multiplier=2.1, repeat=3, target_kw1="enemy_in_front")
        return damage_dealt
        
    def skill3(self):
        pass

    def battle_entry_effects(self):
        self.apply_effect(StatsEffect('Gargoyle Passive', -1, True, {'final_damage_taken_multipler' : -0.1}))

    def take_damage_aftermath(self, damage, attacker):
        if random.randint(1, 100) <= 60:
            attacker.apply_effect(PoisonDamageEffect('Poison', duration=4, is_buff=False, value=0.05, imposter=self, base="hp"))
        if random.randint(1, 100) <= 60:
            attacker.apply_effect(ContinuousDamageEffect('Bleed', duration=4, is_buff=False, value=0.8 * self.atk, imposter=self))


# ====================================
# End of Negative Status
# ====================================
# Multistrike
# ====================================


class Ninja(character.Character):
    def __init__(self, name, lvl, exp=0, equip=None, image=None):
        super().__init__(name, lvl, exp, equip, image)
        self.original_name = "Ninja"
        self.skill1_description = "Attack closest enemy 12 times with 150% atk."
        self.skill2_description = "For 4 turns, increase evasion by 50%. Attack closest enemy 8 times with 150% atk"
        self.skill3_description = "Normal attack have 30% chance to reduce all skill cooldown by 1 turn."
        self.skill1_cooldown_max = 4
        self.skill2_cooldown_max = 4
        self.is_boss = False

    def skill_tooltip(self):
        return f"Skill 1 : {self.skill1_description}\nCooldown : {self.skill1_cooldown} action(s)\n\nSkill 2 : {self.skill2_description}\nCooldown : {self.skill2_cooldown} action(s)\n\nSkill 3 : {self.skill3_description}\n"

    def skill1_logic(self):
        damage_dealt = self.attack(multiplier=1.5, repeat=12, target_kw1="enemy_in_front")
        return damage_dealt

    def skill2_logic(self):
        self.apply_effect(StatsEffect('Evasion', 4, True, {'eva' : 0.5}))
        damage_dealt = self.attack(multiplier=1.5, repeat=8, target_kw1="enemy_in_front")
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


class KillerBee(character.Character):
    def __init__(self, name, lvl, exp=0, equip=None, image=None):
        super().__init__(name, lvl, exp, equip, image)
        self.original_name = "Killerbee"
        self.skill1_description = "Attack closest enemy 4 times with 250% atk"
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
        damage_dealt = self.attack(multiplier=3.0, repeat=4, func_after_dmg=sting_effect, target_kw1="enemy_in_front")
        return damage_dealt

    def skill2_logic(self):
        def sting_effect(self, target):
            target.apply_effect(StingEffect('Sting', duration=4, is_buff=False, value=0.35 * self.atk, imposter=self))
        damage_dealt = self.attack(target_kw1="n_random_enemy",target_kw2="5", multiplier=2.0, repeat=1, func_after_dmg=sting_effect)
        return damage_dealt
        
    def skill3(self):
        pass 


class Samurai(character.Character):
    def __init__(self, name, lvl, exp=0, equip=None, image=None):
        super().__init__(name, lvl, exp, equip, image)
        self.original_name = "Samurai"
        self.skill1_description = "Attack closest enemy 7 times with 200% atk."
        self.skill2_description = "Attack enemy with lowest hp 3 times with 300% atk."
        self.skill3_description = "Skill have 30% chance to inflict bleed on target for 4 turns. Bleed deals 30% of atk as damage per turn."
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
        damage_dealt = self.attack(multiplier=2.0, repeat=7, func_after_dmg=bleed_effect, target_kw1="enemy_in_front")
        return damage_dealt

    def skill2_logic(self):
        def bleed_effect(self, target):
            dice = random.randint(1, 100)
            if dice <= 30:
                target.apply_effect(ContinuousDamageEffect('Bleed', duration=4, is_buff=False, value=0.3 * self.atk, imposter=self))
        damage_dealt = damage_dealt = self.attack(target_kw1="n_lowest_attr",target_kw2="1",target_kw3="hp",target_kw4="enemy", multiplier=3.0, repeat=3, func_after_dmg=bleed_effect)
        return damage_dealt
        
    def skill3(self):
        pass


# ====================================
# End of Multistrike
# ====================================
# CC
# ====================================    

class MagicPot(character.Character):
    def __init__(self, name, lvl, exp=0, equip=None, image=None):
        super().__init__(name, lvl, exp, equip, image)
        self.original_name = "MagicPot"
        self.skill1_description = "Attack all enemies with 300% atk."
        self.skill2_description = "50% chance to put all enemies to sleep."
        self.skill3_description = "Evasion is increased by 50% for 10 turns."
        self.skill1_cooldown_max = 5
        self.skill2_cooldown_max = 5
        self.is_boss = False

    def skill_tooltip(self):
        return f"Skill 1 : {self.skill1_description}\nCooldown : {self.skill1_cooldown} action(s)\n\nSkill 2 : {self.skill2_description}\nCooldown : {self.skill2_cooldown} action(s)\n\nSkill 3 : {self.skill3_description}\n"

    def skill1_logic(self):
        damage_dealt = self.attack(multiplier=3.0, target_kw1="n_random_enemy",target_kw2="5", repeat=1)
        return damage_dealt

    def skill2_logic(self):
        for t in self.enemy:
            dice = random.randint(1, 100)
            if dice <= 50:
                t.apply_effect(SleepEffect('Sleep', duration=-1, is_buff=False))
        pass
        
    def skill3(self):
        pass

    def battle_entry_effects(self):
        self.apply_effect(StatsEffect('MagicPot Passive', 10, True, {'eva' : 0.5}))





# ====================================
# End of CC
# ====================================
# hp
# ====================================

class Skeleton(character.Character):
    def __init__(self, name, lvl, exp=0, equip=None, image=None):
        super().__init__(name, lvl, exp, equip, image)
        self.original_name = "Skeleton"
        self.skill1_description = "Attack enemy with highest hp with 300% atk 3 times."
        self.skill2_description = "Attack enemy with highest hp with 900%, 80% chance to Stun for 3 turns."
        self.skill3_description = "Normal attack has 5% chance to Stun for 2 turns."
        self.skill1_cooldown_max = 5
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


class Ork(character.Character):
    def __init__(self, name, lvl, exp=0, equip=None, image=None):
        super().__init__(name, lvl, exp, equip, image)
        self.original_name = "Ork"
        self.skill1_description = "Focus attack on enemy with lowest hp with 300% atk 2 times."
        self.skill2_description = "Focus attack on enemy with lowest hp with 300% atk 2 times."
        self.skill3_description = "Skill attack inflict both Burn and Bleed for 3 turns, deals 30% of atk as status damage per turn."
        self.skill1_cooldown_max = 5
        self.skill2_cooldown_max = 5
        self.is_boss = False

    def skill_tooltip(self):
        return f"Skill 1 : {self.skill1_description}\nCooldown : {self.skill1_cooldown} action(s)\n\nSkill 2 : {self.skill2_description}\nCooldown : {self.skill2_cooldown} action(s)\n\nSkill 3 : {self.skill3_description}\n"

    def skill1_logic(self):
        def burn_effect(self, target):
            target.apply_effect(ContinuousDamageEffect('Burn', duration=3, is_buff=False, value=0.3 * self.atk, imposter=self))
            target.apply_effect(ContinuousDamageEffect('Bleed', duration=3, is_buff=False, value=0.3 * self.atk, imposter=self))
        damage_dealt = self.attack(multiplier=3.0, repeat_seq=2, func_after_dmg=burn_effect, target_kw1="n_lowest_attr", target_kw2="1", target_kw3="hp", target_kw4="enemy")
        return damage_dealt

    def skill2_logic(self):
        def burn_effect(self, target):
            target.apply_effect(ContinuousDamageEffect('Burn', duration=3, is_buff=False, value=0.3 * self.atk, imposter=self))
            target.apply_effect(ContinuousDamageEffect('Bleed', duration=3, is_buff=False, value=0.3 * self.atk, imposter=self))
        damage_dealt = self.attack(multiplier=3.0, repeat_seq=2, func_after_dmg=burn_effect, target_kw1="n_lowest_attr", target_kw2="1", target_kw3="hp", target_kw4="enemy")
        return damage_dealt
    
    def skill3(self):
        pass


class Minotaur(character.Character):
    def __init__(self, name, lvl, exp=0, equip=None, image=None):
        super().__init__(name, lvl, exp, equip, image)
        self.original_name = "Minotaur"
        self.skill1_description = "Focus attack enemy with lowest hp with 300% atk 2 times."
        self.skill2_description = "Focus attack enemy with lowest hp with 200% atk 2 times. Damage increased by 10% of target lost hp."
        self.skill3_description = "Skill damage increased by 50% if target has less than 50% hp."
        self.skill1_cooldown_max = 4
        self.skill2_cooldown_max = 5
        self.is_boss = False

    def skill_tooltip(self):
        return f"Skill 1 : {self.skill1_description}\nCooldown : {self.skill1_cooldown} action(s)\n\nSkill 2 : {self.skill2_description}\nCooldown : {self.skill2_cooldown} action(s)\n\nSkill 3 : {self.skill3_description}\n"

    def skill1_logic(self):
        def damage_increase(self, target, final_damage):
            if target.hp < target.maxhp * 0.5:
                final_damage *= 1.5
            return final_damage
        damage_dealt = self.attack(multiplier=3.0, repeat_seq=2, func_damage_step=damage_increase, target_kw1="n_lowest_attr", target_kw2="1", target_kw3="hp", target_kw4="enemy")
        return damage_dealt

    def skill2_logic(self):
        def damage_increase(self, target, final_damage):
            if target.hp < target.maxhp * 0.5:
                final_damage *= 1.5
            final_damage += 0.1 * (target.maxhp - target.hp)
            return final_damage
        damage_dealt = self.attack(multiplier=2.0, repeat_seq=2, func_damage_step=damage_increase, target_kw1="n_lowest_attr", target_kw2="1", target_kw3="hp", target_kw4="enemy")
        return damage_dealt

    def skill3(self):
        pass


# ====================================
# End of hp
# ====================================
# spd
# ====================================

class Merman(character.Character):
    def __init__(self, name, lvl, exp=0, equip=None, image=None):
        super().__init__(name, lvl, exp, equip, image)
        self.original_name = "Merman"
        self.skill1_description = "Target 1 enemy with the lowest spd, attack 3 times with 250% atk."
        self.skill2_description = "Target 1 enemy, if it is the same enemy as in skill 1, attack 3 times with 250% atk and Stun the target for 4 turns. This skill has no effect otherwise."
        self.skill3_description = "Normal attack attacks 2 times."
        self.skill1_cooldown_max = 5
        self.skill2_cooldown_max = 5
        self.is_boss = False
        self.s1target = None

    def skill_tooltip(self):
        return f"Skill 1 : {self.skill1_description}\nCooldown : {self.skill1_cooldown} action(s)\n\nSkill 2 : {self.skill2_description}\nCooldown : {self.skill2_cooldown} action(s)\n\nSkill 3 : {self.skill3_description}\n"

    def skill1_logic(self):
        t = next(self.target_selection(keyword="n_lowest_attr", keyword2="1", keyword3="spd", keyword4="enemy"))
        self.s1target = t
        l = [t]
        damage_dealt = self.attack(multiplier=2.5, repeat=3, target_list=l)
        return damage_dealt

    def skill2_logic(self):
        if self.s1target is None:
            return 0
        else:
            t = next(self.target_selection(keyword="n_lowest_attr", keyword2="1", keyword3="spd", keyword4="enemy"))
            if t == self.s1target:
                l = [t]
                def stun_effect(self, target):
                    target.apply_effect(StunEffect('Stun', duration=4, is_buff=False))
                damage_dealt = self.attack(multiplier=2.5, repeat=3, target_list=l, func_after_dmg=stun_effect)
                return damage_dealt
            else:
                return 0

    def skill3(self):
        pass

    def normal_attack(self):
        self.attack(repeat=2)


class Wyvern(character.Character):
    def __init__(self, name, lvl, exp=0, equip=None, image=None):
        super().__init__(name, lvl, exp, equip, image)
        self.original_name = "Wyvern"
        self.skill1_description = "Attack 3 closest enemies 2 times and deal 300% atk. For 70% chance each attack, reduce target spd by 30% for 4 turns."
        self.skill2_description = "Attack closest enemy with 200% atk, if target has lower spd than you, deal 120% more damage and reduce target spd by 30% for 4 turns."
        self.skill3_description = "Increase spd by 30%."
        self.skill1_cooldown_max = 4
        self.skill2_cooldown_max = 5
        self.is_boss = False

    def skill_tooltip(self):
        return f"Skill 1 : {self.skill1_description}\nCooldown : {self.skill1_cooldown} action(s)\n\nSkill 2 : {self.skill2_description}\nCooldown : {self.skill2_cooldown} action(s)\n\nSkill 3 : {self.skill3_description}\n"

    def skill1_logic(self):
        def slow_effect(self, target):
            dice = random.randint(1, 100)
            if dice <= 70:
                target.apply_effect(StatsEffect('Slow', duration=4, is_buff=False, stats_dict={'spd' : 0.7}))
        damage_dealt = self.attack(multiplier=3.0, repeat_seq=2, func_after_dmg=slow_effect, target_kw1="n_enemy_in_front", target_kw2="3")
        return damage_dealt

    def skill2_logic(self):
        def slow_effect(self, target):
            if target.spd < self.spd:
                target.apply_effect(StatsEffect('Slow', duration=4, is_buff=False, stats_dict={'spd' : 0.7}))
        def spd_penalty(self, target, final_damage):
            if target.spd < self.spd:
                final_damage *= 2.2
            return final_damage
        damage_dealt = self.attack(multiplier=2.0, repeat=1, func_after_dmg=slow_effect, func_damage_step=spd_penalty, target_kw1="enemy_in_front")
        return damage_dealt


    def skill3(self):
        pass

    def battle_entry_effects(self):
        self.apply_effect(StatsEffect('Wyvern Passive', -1, True, {'spd' : 1.3}))


# ====================================
# End of spd
# ====================================
# Critical
# ====================================


class SoldierB(character.Character):
    def __init__(self, name, lvl, exp=0, equip=None, image=None):
        super().__init__(name, lvl, exp, equip, image)
        self.original_name = "SoldierB"
        self.skill1_description = "Attack random enemies 4 times with 300% atk."
        self.skill2_description = "Attack random enemies 4 times with 270% atk, each attack will trigger the same attack if critical."
        self.skill3_description = "Increase critical rate and critical damage by 30%."
        self.skill1_cooldown_max = 5
        self.skill2_cooldown_max = 5
        self.is_boss = False

    def skill_tooltip(self):
        return f"Skill 1 : {self.skill1_description}\nCooldown : {self.skill1_cooldown} action(s)\n\nSkill 2 : {self.skill2_description}\nCooldown : {self.skill2_cooldown} action(s)\n\nSkill 3 : {self.skill3_description}\n"

    def skill1_logic(self):
        damage_dealt = self.attack(multiplier=3.0, repeat=4)
        return damage_dealt

    def skill2_logic(self):
        def additional_attack(self, target, is_crit):
            if is_crit:
                global_vars.turn_info_string += f"{self.name} triggered additional attack.\n"
                return self.attack(multiplier=2.7, repeat=1)
            else:
                return 0
        damage_dealt = self.attack(multiplier=2.7, repeat=3, additional_attack_after_dmg=additional_attack)
        return damage_dealt
        
    def skill3(self):
        pass

    def battle_entry_effects(self):
        self.apply_effect(StatsEffect('SoldierB Passive', -1, True, {'crit' : 0.3, 'critdmg' : 0.3}))


class Queen(character.Character):
    # Boss
    def __init__(self, name, lvl, exp=0, equip=None, image=None):
        super().__init__(name, lvl, exp, equip, image)
        self.original_name = "Queen"
        self.skill1_description = "Attack random ememies with 260% atk 8 times, after each successful attack, increase critical damage by 35% for 1 turn."
        self.skill2_description = "Attack 3 front enemies with 300% atk, decrease their critical defense by 30%, for 8 turns. After this skill, increase critical damage by 35% for 3 turns."
        self.skill3_description = "Critical chance is increased by 60%. Speed is increased by 20%."
        self.skill1_cooldown_max = 5
        self.skill2_cooldown_max = 3
        self.is_boss = True

    def skill_tooltip(self):
        return f"Skill 1 : {self.skill1_description}\nCooldown : {self.skill1_cooldown} action(s)\n\nSkill 2 : {self.skill2_description}\nCooldown : {self.skill2_cooldown} action(s)\n\nSkill 3 : {self.skill3_description}\n"

    def skill1_logic(self):
        def critdmg_increase(self, target):
            self.apply_effect(StatsEffect('Control', 1, True, {'critdmg' : 0.35}))
        damage_dealt = self.attack(multiplier=2.6, repeat=8, func_after_dmg=critdmg_increase)
        return damage_dealt

    def skill2_logic(self):
        def critdef_decrease(self, target):
            target.apply_effect(StatsEffect('Compliance', 8, True, {'critdef' : -0.3}))
        damage_dealt = self.attack(multiplier=3.0, repeat=1, func_after_dmg=critdef_decrease, target_kw1="n_enemy_in_front", target_kw2="3")
        if self.is_alive():
            self.apply_effect(StatsEffect('Control', 3, True, {'critdmg' : 0.35}))
        return damage_dealt

    def skill3(self):
        pass

    def battle_entry_effects(self):
        self.apply_effect(StatsEffect('Queen Passive', -1, True, {'crit' : 0.6, 'spd' : 1.2}))


# ====================================
# End of Critical
# ====================================
# Defence
# ====================================
        

class Paladin(character.Character):
    def __init__(self, name, lvl, exp=0, equip=None, image=None):
        super().__init__(name, lvl, exp, equip, image)
        self.original_name = "paladin"
        self.skill1_description = "Attack 1 closest enemy with 800% atk."
        self.skill2_description = "Attack 1 closest enemy 3 times with 300% atk."
        self.skill3_description = "When taking damage and damage is exceed 10% of maxhp, reduce damage taken by 50%. The attacker takes 30% of damage reduced."
        self.skill1_cooldown_max = 5
        self.skill2_cooldown_max = 5
        self.is_boss = False

    def skill_tooltip(self):
        return f"Skill 1 : {self.skill1_description}\nCooldown : {self.skill1_cooldown} action(s)\n\nSkill 2 : {self.skill2_description}\nCooldown : {self.skill2_cooldown} action(s)\n\nSkill 3 : {self.skill3_description}\n"

    def skill1_logic(self):
        damage_dealt = self.attack(multiplier=8.0, repeat=1, target_kw1="enemy_in_front")
        return damage_dealt

    def skill2_logic(self):
        damage_dealt = self.attack(multiplier=3.0, repeat=3, target_kw1="enemy_in_front")
        return damage_dealt
        
    def skill3(self):
        pass

    def battle_entry_effects(self):
        self.apply_effect(EffectShield3('Shielded', -1, True, 0.5, 0.3))
         

class Father(character.Character):
    def __init__(self, name, lvl, exp=0, equip=None, image=None):
        super().__init__(name, lvl, exp, equip, image)
        self.original_name = "Father"
        self.skill1_description = "Apply Cancellation Shield on 3 allies with lowest hp, all damage lower than 10% of maxhp is reduced to 0. Shield last 4 turns and provide 4 uses."
        self.skill2_description = "Attack 3 closest enemies with 450% atk."
        self.skill3_description = "All damage taken is reduced by 20%, damage taken lower than 10% of maxhp is reduced to 0 for 300 times."
        self.skill1_cooldown_max = 5
        self.skill2_cooldown_max = 5
        self.is_boss = False

    def skill_tooltip(self):
        return f"Skill 1 : {self.skill1_description}\nCooldown : {self.skill1_cooldown} action(s)\n\nSkill 2 : {self.skill2_description}\nCooldown : {self.skill2_cooldown} action(s)\n\nSkill 3 : {self.skill3_description}\n"

    def skill1_logic(self):
        targets = self.target_selection(keyword="n_lowest_attr", keyword2="3", keyword3="hp", keyword4="ally")
        for target in targets:
            target.apply_effect(CancellationShield3('Cancellation Shield', 4, True, 0.1, False, uses=4))

    def skill2_logic(self):
        damage_dealt = self.attack(multiplier=4.5, repeat=1, target_kw1="n_enemy_in_front", target_kw2="3")
        return damage_dealt
        
    def skill3(self):
        pass

    def battle_entry_effects(self):
        self.apply_effect(CancellationShield3('Father Guidance', -1, True, 0.1, False, uses=300))
        self.apply_effect(StatsEffect('Father Passive', -1, True, {'final_damage_taken_multipler' : -0.20}))
         

class Kobold(character.Character):
    def __init__(self, name, lvl, exp=0, equip=None, image=None):
        super().__init__(name, lvl, exp, equip, image)
        self.original_name = "Kobold"
        self.skill1_description = "Recover hp by 30% of maxhp and increase defense by 50% for 5 turns. If you are the only one alive, effect is increased by 100%."
        self.skill2_description = "Attack 1 closest enemy with 800% atk, if you are the only one alive, increase damage by 100%."
        self.skill3_description = "Defence and maxhp is increased by 25%."
        self.skill1_cooldown_max = 5
        self.skill2_cooldown_max = 5
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
        damage_dealt = self.attack(multiplier=8.0, repeat=1, func_damage_step=additional_damage, target_kw1="enemy_in_front")
        return damage_dealt

    def skill3(self):
        pass

    def battle_entry_effects(self):
        self.apply_effect(StatsEffect('Kobold Passive', -1, True, {'defense' : 1.25, 'maxhp' : 1.25}))


class SoldierA(character.Character):
    def __init__(self, name, lvl, exp=0, equip=None, image=None):
        super().__init__(name, lvl, exp, equip, image)
        self.original_name = "SoldierA"
        self.skill1_description = "Focus attack on enemy with highest defense with 400% atk 3 times, each attack will reduce target defense by 20% for 3 turns."
        self.skill2_description = "Attack all enemies with 200% atk and reduce defense by 35% for 5 turns."
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
            target.apply_effect(StatsEffect('Defence Break', 3, False, {'defense' : 0.80}))
        damage_dealt = self.attack(multiplier=4.0, repeat_seq=3, func_after_dmg=bleed_effect_defence_break, target_kw1="n_highest_attr", target_kw2="1", target_kw3="defense", target_kw4="enemy")
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


class FutureSoldier(character.Character):
    def __init__(self, name, lvl, exp=0, equip=None, image=None):
        super().__init__(name, lvl, exp, equip, image)
        self.original_name = "FutureSoldier"
        self.skill1_description = "Attack random enemies 5 times with 200% atk, each attack reduces target defense by 25% for 4 turns." # 0.7**5 = 0.168
        self.skill2_description = "Attack random enemies 7 times with 150% atk, if target has lower defense than self, increase damage by 100%."
        self.skill3_description = "Normal attack deals double damage if target has lower defense than self."
        self.skill1_cooldown_max = 4
        self.skill2_cooldown_max = 4
        self.is_boss = False

    def skill_tooltip(self):
        return f"Skill 1 : {self.skill1_description}\nCooldown : {self.skill1_cooldown} action(s)\n\nSkill 2 : {self.skill2_description}\nCooldown : {self.skill2_cooldown} action(s)\n\nSkill 3 : {self.skill3_description}\n"

    def skill1_logic(self):
        def defence_break(self, target):
            target.apply_effect(StatsEffect('Defence Break', 4, False, {'defense' : 0.75}))
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


class FutureElite(character.Character):
    # Boss
    def __init__(self, name, lvl, exp=0, equip=None, image=None):
        super().__init__(name, lvl, exp, equip, image)
        self.original_name = "FutureElite"
        self.skill1_description = "Attack all enemies with 400% atk, reduce defense by 40% for 6 turns."
        self.skill2_description = "Attack random enemies 8 times with 200% atk, if target has lower defense than self, damage increased by a percentage equal to the ratio between self and target defense."
        # for example: self.defense = 100, target.defense = 50, damage increased by 100%
        self.skill3_description = "defense is increased by 30%."
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
# End of Defence
# ====================================
# Negative Status
# ====================================
        
class Mage(character.Character):
    def __init__(self, name, lvl, exp=0, equip=None, image=None):
        super().__init__(name, lvl, exp, equip, image)
        self.original_name = "Mage"
        self.skill1_description = "Attack 3 closest enemies with 300% atk and inflict Burn for 4 turns. Burn deals 40% of atk as status damage per turn. If target has negative status, inflict 3 Burn effects."
        self.skill2_description = "Attack closest enemy 3 times with 320% atk, if target has negative status, each attack inflict 3 Burn effects for 4 turns."
        self.skill3_description = "Increase atk by 10%"
        self.skill1_cooldown_max = 5
        self.skill2_cooldown_max = 5
        self.is_boss = False

    def skill_tooltip(self):
        return f"Skill 1 : {self.skill1_description}\nCooldown : {self.skill1_cooldown} action(s)\n\nSkill 2 : {self.skill2_description}\nCooldown : {self.skill2_cooldown} action(s)\n\nSkill 3 : {self.skill3_description}\n"

    def skill1_logic(self):
        def burn_effect(self, target):
            if len(target.debuffs) > 0:
                target.apply_effect(ContinuousDamageEffect('Burn', duration=4, is_buff=False, value=0.4 * self.atk, imposter=self))
                target.apply_effect(ContinuousDamageEffect('Burn', duration=4, is_buff=False, value=0.4 * self.atk, imposter=self))
                target.apply_effect(ContinuousDamageEffect('Burn', duration=4, is_buff=False, value=0.4 * self.atk, imposter=self))
            else:
                target.apply_effect(ContinuousDamageEffect('Burn', duration=4, is_buff=False, value=0.4 * self.atk, imposter=self))
        damage_dealt = self.attack(multiplier=3.0, repeat=1, func_after_dmg=burn_effect, target_kw1="n_enemy_in_front", target_kw2="3")
        return damage_dealt

    def skill2_logic(self):
        def burn_effect(self, target):
            if len(target.debuffs) > 0:
                target.apply_effect(ContinuousDamageEffect('Burn', duration=4, is_buff=False, value=0.4 * self.atk, imposter=self))
                target.apply_effect(ContinuousDamageEffect('Burn', duration=4, is_buff=False, value=0.4 * self.atk, imposter=self))
                target.apply_effect(ContinuousDamageEffect('Burn', duration=4, is_buff=False, value=0.4 * self.atk, imposter=self))
        damage_dealt = self.attack(multiplier=3.2, repeat=3, func_after_dmg=burn_effect, target_kw1="enemy_in_front")
        return damage_dealt

    def skill3(self):
        pass

    def battle_entry_effects(self):
        self.apply_effect(StatsEffect('Mage Passive', -1, True, {'atk' : 1.1}))


# ====================================
# End of Negative Status
# ====================================
# Positive Status
# ====================================
    

class Thief(character.Character):
    def __init__(self, name, lvl, exp=0, equip=None, image=None):
        super().__init__(name, lvl, exp, equip, image)
        self.original_name = "Thief"
        self.skill1_description = "Attack 1 closest enemy with 600% atk."
        self.skill2_description = "Attack 2 closest enemies with 330% atk 2 times."
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
        damage_dealt = self.attack(multiplier=6.0, repeat=1, func_damage_step=buffed_target_amplify, target_kw1="enemy_in_front")
        return damage_dealt

    def skill2_logic(self):
        def buffed_target_amplify(self, target, final_damage):
            buffs = [e for e in target.buffs if not e.is_set_effect and not e.duration == -1]
            return final_damage * (1 + 0.6 * len(buffs))
        damage_dealt = self.attack(target_kw1="n_enemy_in_front", target_kw2="2", multiplier=3.3, repeat_seq=2, func_damage_step=buffed_target_amplify)
        return damage_dealt
        
    def skill3(self):
        pass


class Goliath(character.Character):
    # Boss
    def __init__(self, name, lvl, exp=0, equip=None, image=None):
        super().__init__(name, lvl, exp, equip, image)
        self.original_name = "Goliath"
        self.skill1_description = "Strike the enemy with the most active buff effects with 600% atk, for each active buff effect, strike again with 400% atk."
        self.skill2_description = "Reset skill cooldown of skill 1 and increase spd by 100% for 3 turns. Attack closest enemy 3 times with 300% atk. For each active buff on target, increase damage by 30%."
        self.skill3_description = "Increase atk, def, maxhp by 30%."
        self.skill1_cooldown_max = 4
        self.skill2_cooldown_max = 2
        self.is_boss = True

    def skill_tooltip(self):
        return f"Skill 1 : {self.skill1_description}\nCooldown : {self.skill1_cooldown} action(s)\n\nSkill 2 : {self.skill2_description}\nCooldown : {self.skill2_cooldown} action(s)\n\nSkill 3 : {self.skill3_description}\n"

    def skill1_logic(self):
        def buffed_target_amplify(self, target, is_crit):
            buffs = len([e for e in target.buffs if not e.is_set_effect and not e.duration == -1])
            return self.attack(multiplier=4.0, repeat=buffs, target_list=[target])
        damage_dealt = self.attack(multiplier=6.0, repeat=1, target_kw1="n_enemy_with_most_buffs", target_kw2="1", additional_attack_after_dmg=buffed_target_amplify)
        return damage_dealt


    def skill2_logic(self):
        self.skill1_cooldown = 0
        self.apply_effect(StatsEffect('Judgement', 3, True, {'spd' : 2.0}))
        def buff_amplify(self, target, final_damage):
            buffs = len([e for e in target.buffs if not e.is_set_effect and not e.duration == -1])
            return final_damage * (1 + 0.3 * buffs)
        damage_dealt = self.attack(multiplier=3.0, repeat=3, target_kw1="enemy_in_front", func_damage_step=buff_amplify)
        return damage_dealt

        
    def skill3(self):
        pass

    def battle_entry_effects(self):
        self.apply_effect(StatsEffect('Goliath Passive', -1, True, {'atk' : 1.3, 'defense' : 1.3, 'maxhp' : 1.3}))
        self.hp = self.maxhp


# ====================================
# End of Positive Status
# ====================================
# No Status
# Damage increases and others if target has no active buffs
# ====================================
        

class ReconMecha(character.Character): # Change the name later
    def __init__(self, name, lvl, exp=0, equip=None, image=None):
        super().__init__(name, lvl, exp, equip, image)
        self.original_name = "ReconnaissanceMecha"
        self.skill1_description = "Attack closest enemy with 280% atk 2 times, if target has no active buff, increase damage by 100%."
        self.skill2_description = "Attack closest enemy with 280% atk 2 times, if target has no active buff, target defense is reduced by 40% for 8 turns."
        self.skill3_description = "Every turn, at the end of turn, if an enemy is fallen in this turn, heal hp by 30% of maxhp."
        self.skill1_cooldown_max = 4
        self.skill2_cooldown_max = 4
        self.is_boss = False
        self.enemycounter = len(self.enemy)

    def skill_tooltip(self):
        return f"Skill 1 : {self.skill1_description}\nCooldown : {self.skill1_cooldown} action(s)\n\nSkill 2 : {self.skill2_description}\nCooldown : {self.skill2_cooldown} action(s)\n\nSkill 3 : {self.skill3_description}\n"

    def skill1_logic(self):
        def damage_amplify(self, target, final_damage):
            if len([e for e in target.buffs if not e.is_set_effect and not e.duration == -1]) == 0:
                final_damage *= 2.0
            return final_damage
        damage_dealt = self.attack(multiplier=2.8, repeat=2, func_damage_step=damage_amplify, target_kw1="enemy_in_front")
        return damage_dealt

    def skill2_logic(self):
        def defence_break(self, target):
            if len([e for e in target.buffs if not e.is_set_effect and not e.duration == -1]) == 0:
                target.apply_effect(StatsEffect('Defence Break', 8, False, {'defense' : 0.6}))
        damage_dealt = self.attack(multiplier=2.8, repeat=2, func_after_dmg=defence_break, target_kw1="enemy_in_front")
        return damage_dealt
        
    def skill3(self):
        pass

    def status_effects_at_end_of_turn(self):
        if self.enemycounter > len(self.enemy) and self.is_alive():
            self.heal_hp(self.maxhp * 0.3, self)
            self.enemycounter = len(self.enemy)
        else:
            self.enemycounter = len(self.enemy)
        super().status_effects_at_end_of_turn()


class SecurityRobot(character.Character): 
    def __init__(self, name, lvl, exp=0, equip=None, image=None):
        super().__init__(name, lvl, exp, equip, image)
        self.original_name = "SecurityRobot"
        self.skill1_description = "All enemies that without active buffs have their defense reduced by 20% for 8 turns, critical defense reduced by 40% for 8 turns."
        self.skill2_description = "Attack closest enemy for 300% atk 3 times, if target has no active buff, strike a critical hit."
        self.skill3_description = "Maxhp increased by 30%."
        self.skill1_cooldown_max = 4
        self.skill2_cooldown_max = 4
        self.is_boss = False
        self.enemycounter = len(self.enemy)

    def skill_tooltip(self):
        return f"Skill 1 : {self.skill1_description}\nCooldown : {self.skill1_cooldown} action(s)\n\nSkill 2 : {self.skill2_description}\nCooldown : {self.skill2_cooldown} action(s)\n\nSkill 3 : {self.skill3_description}\n"

    def skill1_logic(self):
        for e in self.enemy:
            if len([e for e in e.buffs if not e.is_set_effect and not e.duration == -1]) == 0:
                e.apply_effect(StatsEffect('Analyzed', 8, False, {'defense' : 0.8, 'critdef' : -0.4}))
        return 0

    def skill2_logic(self):
        if len([e for e in self.enemy[0].buffs if not e.is_set_effect and not e.duration == -1]) == 0:
            damage_dealt = self.attack(multiplier=3.0, repeat=3, target_kw1="enemy_in_front", always_crit=True)
        else:
            damage_dealt = self.attack(multiplier=3.0, repeat=3, target_kw1="enemy_in_front")
        return damage_dealt

        
    def skill3(self):
        pass

    def battle_entry_effects(self):
        self.apply_effect(StatsEffect('SecurityRobot Passive', -1, True, {'maxhp' : 1.3}))
        self.hp = self.maxhp


# ====================================
# End of No Status
# ====================================
# Stealth
# ====================================
        

class Cockatorice(character.Character):
    def __init__(self, name, lvl, exp=0, equip=None, image=None):
        super().__init__(name, lvl, exp, equip, image)
        self.original_name = "Cockatorice"
        self.skill1_description = "Attack 3 closest enemies, with 330% atk."
        self.skill2_description = "Focus attack on closest enemy 3 times with 330% atk."
        self.skill3_description = "For 4 turns, if not taking damage, increase atk by 66% and spd by 66% for 4 turns at the end of turn. Same effect cannot be applied twice."
        self.skill1_cooldown_max = 5
        self.skill2_cooldown_max = 5
        self.is_boss = False

    def skill_tooltip(self):
        return f"Skill 1 : {self.skill1_description}\nCooldown : {self.skill1_cooldown} action(s)\n\nSkill 2 : {self.skill2_description}\nCooldown : {self.skill2_cooldown} action(s)\n\nSkill 3 : {self.skill3_description}\n"

    def skill1_logic(self):
        damage_dealt = self.attack(multiplier=3.3, repeat=1, target_kw1="n_enemy_in_front", target_kw2=3)
        return damage_dealt

    def skill2_logic(self):
        damage_dealt = self.attack(multiplier=3.3, repeat_seq=3, target_kw1="enemy_in_front")
        return damage_dealt
        
    def skill3(self):
        pass

    def battle_entry_effects(self):
        self.apply_effect(NotTakingDamageEffect("Cockatorice Passive", -1, True, {'atk' : 1.33, 'spd' : 1.33}, "default", 4, "Cockatorice Fanatic", 4))


class Fanatic(character.Character):
    def __init__(self, name, lvl, exp=0, equip=None, image=None):
        super().__init__(name, lvl, exp, equip, image)
        self.original_name = "Fanatic"
        self.skill1_description = "Attack closest enemy with 340% atk 3 times. If has not taken damage for 4 turns, land critical strikes."
        self.skill2_description = "Attack closest enemy with 340% atk 3 times. If has not taken damage for 4 turns, damage is increased by 5% of target maxhp."
        self.skill3_description = "Recover hp by 30% of damage dealt in skill attacks."
        self.skill1_cooldown_max = 5
        self.skill2_cooldown_max = 5
        self.is_boss = False

    def skill_tooltip(self):
        return f"Skill 1 : {self.skill1_description}\nCooldown : {self.skill1_cooldown} action(s)\n\nSkill 2 : {self.skill2_description}\nCooldown : {self.skill2_cooldown} action(s)\n\nSkill 3 : {self.skill3_description}\n"

    def skill1_logic(self):
        if self.get_num_of_turns_not_taken_damage() < 4:
            damage_dealt = self.attack(multiplier=3.4, repeat=3, target_kw1="enemy_in_front")
        else:
            damage_dealt = self.attack(multiplier=3.4, repeat=3, target_kw1="enemy_in_front", always_crit=True)
        if self.is_alive():
            self.heal_hp(damage_dealt * 0.3, self)
        return damage_dealt

    def skill2_logic(self):
        def damage_amplify(self, target, final_damage):
            if self.get_num_of_turns_not_taken_damage() >= 4:
                final_damage += target.maxhp * 0.05
            return final_damage
        damage_dealt = self.attack(multiplier=3.4, repeat=3, target_kw1="enemy_in_front", func_damage_step=damage_amplify)
        if self.is_alive():
            self.heal_hp(damage_dealt * 0.3, self)
        return damage_dealt

        
    def skill3(self):
        pass


# ====================================
# End of Stealth
# ====================================
# Attack
# ====================================
    

class Tanuki(character.Character):
    def __init__(self, name, lvl, exp=0, equip=None, image=None):
        super().__init__(name, lvl, exp, equip, image)
        self.original_name = "Tanuki"
        self.skill1_description = "Boost two allies with highest atk by 60% for 8 turns."
        self.skill2_description = "Attack closest enemy with 1 damage, increase self evasion by 50% for 5 turns."
        self.skill3_description = "Normal attack resets cooldown of skill 1 and deals 400% atk damage instead of 200% and attack 2 times."
        self.skill1_cooldown_max = 5
        self.skill2_cooldown_max = 5
        self.is_boss = False

    def skill_tooltip(self):
        return f"Skill 1 : {self.skill1_description}\nCooldown : {self.skill1_cooldown} action(s)\n\nSkill 2 : {self.skill2_description}\nCooldown : {self.skill2_cooldown} action(s)\n\nSkill 3 : {self.skill3_description}\n"

    def skill1_logic(self):
        self.update_ally_and_enemy()
        targets = self.target_selection(keyword="n_highest_attr", keyword2="2", keyword3="atk", keyword4="ally")
        for target in targets:
            target.apply_effect(StatsEffect('Tanuki Buff', 8, True, {'atk' : 1.6}))

    def skill2_logic(self):
        damage_dealt = self.attack(repeat=1, target_kw1="enemy_in_front", func_damage_step=lambda self, target, final_damage : 1)
        self.apply_effect(StatsEffect('Tanuki Evasion', 5, True, {'eva' : 0.5}))
        return damage_dealt
        
    def skill3(self):
        pass

    def normal_attack(self):
        self.skill1_cooldown = 0
        self.attack(multiplier=4.0, repeat=2)
        

class Werewolf(character.Character):
    def __init__(self, name, lvl, exp=0, equip=None, image=None):
        super().__init__(name, lvl, exp, equip, image)
        self.original_name = "Werewolf"
        self.skill1_description = "Focus attack 1 enemy with highest atk with 250% atk 3 times. Each attack decreases target atk by 15% for 4 turns."
        self.skill2_description = "Attack 3 enemies with highest atk with 220% atk 2 times. If target has lower atk than self, increase damage by 40%."
        self.skill3_description = "Increase atk by 15%."
        self.skill1_cooldown_max = 5
        self.skill2_cooldown_max = 5
        self.is_boss = False

    def skill_tooltip(self):
        return f"Skill 1 : {self.skill1_description}\nCooldown : {self.skill1_cooldown} action(s)\n\nSkill 2 : {self.skill2_description}\nCooldown : {self.skill2_cooldown} action(s)\n\nSkill 3 : {self.skill3_description}\n"

    def skill1_logic(self):
        def atk_down(self, target):
            target.apply_effect(StatsEffect('Atk Down', 4, False, {'atk' : 0.85}))
        damage_dealt = self.attack(multiplier=2.5, repeat_seq=3, func_after_dmg=atk_down, target_kw1="n_highest_attr", target_kw2="1", target_kw3="atk", target_kw4="enemy")
        return damage_dealt

    def skill2_logic(self):
        def damage_amplify(self, target, final_damage):
            if target.atk < self.atk:
                final_damage *= 1.4
            return final_damage
        damage_dealt = self.attack(multiplier=2.2, repeat_seq=2, func_damage_step=damage_amplify, target_kw1="n_highest_attr", target_kw2="3", target_kw3="atk", target_kw4="enemy")
        return damage_dealt

    def skill3(self):
        pass

    def battle_entry_effects(self):
        self.apply_effect(StatsEffect('Werewolf Passive', -1, True, {'atk' : 1.15}))

# ====================================
# End of Attack
# ====================================
# Regeneration
# ====================================
        

# class Vampire(character.Character):
#     pass


# class Lich(character.Character):
#     pass


# ====================================
# End of Regeneration
# ====================================