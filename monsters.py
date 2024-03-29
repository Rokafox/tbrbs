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
        self.skill2_description = "Attack 1 closest enemy with 700% atk and 70% chance to stun the target for 5 turns."
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
                target.apply_effect(StunEffect('Stun', duration=5, is_buff=False))
        damage_dealt = self.attack(multiplier=7.0, repeat=1, func_after_dmg=stun_effect, target_kw1="enemy_in_front")
        return damage_dealt
        
    def skill3(self):
        pass

    def battle_entry_effects(self):
        self.apply_effect(StatsEffect('Fat', -1, True, {'maxhp' : 1.5}, can_be_removed_by_skill=False))
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
        self.apply_effect(StatsEffect('MoHawk Passive', -1, True, {'atk' : 1.2}, can_be_removed_by_skill=False))


class Earth(character.Character):
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
        self.apply_effect(StatsEffect('Earth Passive', -1, True, {'maxhp' : 2.0}, can_be_removed_by_skill=False))
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
        self.apply_effect(StatsEffect('Golem Passive', -1, True, {'maxhp' : 3.0}, can_be_removed_by_skill=False))
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
        self.skill2_description = "Attack 5 enemies with 200% atk and 50% chance to inflict Curse for 6 turns. Curse: atk is reduced by 40%, unstackable."
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
                curse = StatsEffect('Curse', duration=6, is_buff=False, stats_dict={'atk' : 0.6})
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
    def __init__(self, name, lvl, exp=0, equip=None, image=None):
        super().__init__(name, lvl, exp, equip, image)
        self.original_name = "Pharaoh"
        self.skill1_description = "Attack 3 closest enemies with 320% atk. If target is cursed, damage is increased by 100%."
        self.skill2_description = "Attack 3 closest enemies with 320% atk and 80% chance to inflict Curse for 8 turns. If target is cursed, damage is increased by 100%. Curse: atk is reduced by 40%, unstackable."
        self.skill3_description = "hp, atk, def, spd is increased by 20%. When taking damage, 40% chance to inflict Curse on attacker for 3 turns. At the end of turn, if there is a cursed enemy, increase atk by 30% for 3 turns."
        self.skill1_cooldown_max = 5
        self.skill2_cooldown_max = 3
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
                curse = StatsEffect('Curse', duration=8, is_buff=False, stats_dict={'atk' : 0.7})
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
        self.apply_effect(StatsEffect('Strong', -1, True, {'maxhp' : 1.2, 'atk' : 1.2, 'defense' : 1.2, 'spd' : 1.2}, can_be_removed_by_skill=False))
        self.hp = self.maxhp
        passive = PharaohPassiveEffect('Passive Effect', -1, True, 1.3)
        passive.can_be_removed_by_skill = False
        self.apply_effect(passive)


class PoisonSlime(character.Character):
    def __init__(self, name, lvl, exp=0, equip=None, image=None):
        super().__init__(name, lvl, exp, equip, image)
        self.original_name = "Poison_Slime"
        self.skill1_description = "Attack 5 enemies with 150% atk and 66% chance to inflict Poison for 6 turns. Poison: takes 7% of current hp status damage per turn."
        self.skill2_description = "Attack 5 enemies with 150% atk and 66% chance to inflict Poison for 6 turns. Poison: takes 7% of lost hp status damage per turn."
        self.skill3_description = "Reduce damage taken by 10%."
        self.skill1_cooldown_max = 5
        self.skill2_cooldown_max = 5
        self.is_boss = False

    def skill_tooltip(self):
        return f"Skill 1 : {self.skill1_description}\nCooldown : {self.skill1_cooldown} action(s)\n\nSkill 2 : {self.skill2_description}\nCooldown : {self.skill2_cooldown} action(s)\n\nSkill 3 : {self.skill3_description}\n"

    def skill1_logic(self):
        def poison_effect(self, target):
            dice = random.randint(1, 100)
            if dice <= 66:
                target.apply_effect(PoisonDamageEffect('Poison', duration=6, is_buff=False, value=0.07, imposter=self, base="hp"))
        damage_dealt = self.attack(target_kw1="n_random_enemy",target_kw2="5", multiplier=1.5, repeat=1, func_after_dmg=poison_effect)
        return damage_dealt

    def skill2_logic(self):
        def poison_effect(self, target):
            dice = random.randint(1, 100)
            if dice <= 66:
                target.apply_effect(PoisonDamageEffect('Poison', duration=6, is_buff=False, value=0.07, imposter=self, base="losthp"))
        damage_dealt = self.attack(target_kw1="n_random_enemy",target_kw2="5", multiplier=1.5, repeat=1, func_after_dmg=poison_effect)
        return damage_dealt
        
    def skill3(self):
        pass

    def battle_entry_effects(self):
        self.apply_effect(StatsEffect('Slimy', -1, True, {'final_damage_taken_multipler' : -0.1}, can_be_removed_by_skill=False))


class MadScientist(character.Character):
    def __init__(self, name, lvl, exp=0, equip=None, image=None):
        super().__init__(name, lvl, exp, equip, image)
        self.original_name = "MadScientist"
        self.skill1_description = "Attack all enemies with 210% atk and inflict plague for 12 turns with 50% chance each. Plague: at end of turn, 30% chance to apply the same effect to a neighbor ally, every turn, take 7% of lost hp as status damage."
        self.skill2_description = "Attack 3 closest enemies with 300% atk, if target is inflicted with plague, healing efficiency is reduced by 50% for 12 turns."
        self.skill3_description = "Normal attack have 10% chance to inflict plague for 12 turns and deals 30% more damage."
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
        damage_dealt = self.attack(target_kw1="n_random_enemy", target_kw2="5", multiplier=2.1, repeat=1, func_after_dmg=plague_effect)
        return damage_dealt

    def skill2_logic(self):
        def plague_effect(self, target):
            if target.has_effect_that_named("Plague", None, "PlagueEffect"):
                target.apply_effect(StatsEffect('Healing Down', duration=12, is_buff=False, stats_dict={'heal_efficiency' : -0.5}))
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
            final_damage *= 1.3
            return final_damage
        self.attack(func_after_dmg=plague_effect, func_damage_step=amplify)


class Ghost(character.Character):
    def __init__(self, name, lvl, exp=0, equip=None, image=None):
        super().__init__(name, lvl, exp, equip, image)
        self.original_name = "Ghost"
        self.skill1_description = "Attack 5 enemies with 200% atk and apply Fear on targets for 7 turns. Apply chance is 100%, 80%, 60%, 30%, 0% for each enemy depending on how many allies the enemy has. The fewer allies the enemy has, the higher the chance."
        self.skill2_description = "Attack closest enemy 4 times with 200% atk. For 8 turns, all allies takes 40% less damage."
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
                target.apply_effect(FearEffect('Fear', duration=7, is_buff=False))
        damage_dealt = self.attack(target_kw1="n_random_enemy",target_kw2="5", multiplier=2.0, repeat=1, func_after_dmg=fear_effect)
        return damage_dealt

    def skill2_logic(self):
        damage_dealt = self.attack(target_kw1="enemy_in_front", multiplier=2.0, repeat=4)
        if self.is_alive():
            for a in self.ally:
                a.apply_effect(StatsEffect('Misty', duration=8, is_buff=True, stats_dict={'final_damage_taken_multipler' : -0.40}))
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
    def __init__(self, name, lvl, exp=0, equip=None, image=None):
        super().__init__(name, lvl, exp, equip, image)
        self.original_name = "Death"
        self.skill1_description = "Attack 5 enemies with 360% atk and apply Fear on targets for 9 turns. Apply chance is 100%, 80%, 60%, 30%, 0% for each enemy depending on how many allies the enemy has. The fewer allies the enemy has, the higher the chance."
        self.skill2_description = "Attack 3 enemies with lowest hp with 400% atk. If target hp is below 15%, execute target and recover for 20% hp of maxhp. If enemy survived the attack and has Fear, the enemy is confused for 5 turns."
        self.skill3_description = "Normal attack have 15% chance to inflict Fear for 9 turns. maxhp, defense and atk is increased by 20%. As long as you are alive, Fear effect gain the following effect: atk - 40%, accuracy - 40%."
        self.skill1_cooldown_max = 4
        self.skill2_cooldown_max = 4
        self.is_boss = True
        self.fear_effect_dict = {"acc": -0.40, "atk": 0.6}

    def skill_tooltip(self):
        return f"Skill 1 : {self.skill1_description}\nCooldown : {self.skill1_cooldown} action(s)\n\nSkill 2 : {self.skill2_description}\nCooldown : {self.skill2_cooldown} action(s)\n\nSkill 3 : {self.skill3_description}\n"

    def skill1_logic(self):
        chance_dict = dict(zip_longest(range(1, 11), [100, 80, 60, 30, 0], fillvalue=0))
        def fear_effect(self, target):
            dice = random.randint(1, 100)
            if dice <= chance_dict[len(self.enemy)]:
                target.apply_effect(FearEffect('Fear', duration=9, is_buff=False))
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
                    target.apply_effect(ConfuseEffect('Confuse', duration=5, is_buff=False))
        damage_dealt = self.attack(target_kw1="n_lowest_attr",target_kw2="3",target_kw3="hp",target_kw4="enemy", multiplier=4.0, repeat=1, func_after_dmg=execute)
        return damage_dealt

        
    def skill3(self):
        pass

    def normal_attack(self):
        def fear_effect(self, target):
            dice = random.randint(1, 100)
            if dice <= 15:
                target.apply_effect(FearEffect('Fear', duration=9, is_buff=False))
        self.attack(func_after_dmg=fear_effect)

    def battle_entry_effects(self):
        self.apply_effect(StatsEffect('Ugly', -1, True, {'maxhp' : 1.2, 'atk' : 1.2, 'defense' : 1.2}, can_be_removed_by_skill=False))
        self.hp = self.maxhp


class Gargoyle(character.Character):
    def __init__(self, name, lvl, exp=0, equip=None, image=None):
        super().__init__(name, lvl, exp, equip, image)
        self.original_name = "Gargoyle"
        self.skill1_description = "Attack closest enemy 3 times with 210% atk."
        self.skill2_description = "Attack closest enemy 3 times with 210% atk."
        self.skill3_description = "Reduce damage taken by 10%. When taking damage, 60% chance to inflict Bleed and Poison on attacker for 5 turns. Bleed: take 80% of applier atk as status damage each turn. Poison: takes 5% of current hp as status damage per turn."
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
        self.apply_effect(StatsEffect('Gargoyle Passive', -1, True, {'final_damage_taken_multipler' : -0.1}, can_be_removed_by_skill=False))

    def take_damage_aftermath(self, damage, attacker):
        if random.randint(1, 100) <= 60:
            attacker.apply_effect(PoisonDamageEffect('Poison', duration=5, is_buff=False, value=0.05, imposter=self, base="hp"))
        if random.randint(1, 100) <= 60:
            attacker.apply_effect(ContinuousDamageEffect('Bleed', duration=5, is_buff=False, value=0.8 * self.atk, imposter=self))


class MachineGolem(character.Character):
    def __init__(self, name, lvl, exp=0, equip=None, image=None):
        super().__init__(name, lvl, exp, equip, image)
        self.original_name = "MachineGolem"
        self.skill1_description = "Install 2 timed bombs on all enemies. Bomb will explode after 8 turns, dealing 400% self atk as status damage."
        self.skill2_description = "Attack all enemies with 275% atk, 75% chance to inflict Burn for 8 turns. Burn deals 25% of self atk as status damage each turn."
        self.skill3_description = "Increase atk by 20%, maxhp by 20%."
        self.skill1_cooldown_max = 5
        self.skill2_cooldown_max = 5
        self.is_boss = True

    def skill_tooltip(self):
        return f"Skill 1 : {self.skill1_description}\nCooldown : {self.skill1_cooldown} action(s)\n\nSkill 2 : {self.skill2_description}\nCooldown : {self.skill2_cooldown} action(s)\n\nSkill 3 : {self.skill3_description}\n"

    def skill1_logic(self):
        for e in self.enemy:
            e.apply_effect(TimedBombEffect('Timed Bomb', duration=8, is_buff=False, damage=4.00 * self.atk, imposter=self, cc_immunity=False))
            e.apply_effect(TimedBombEffect('Timed Bomb', duration=8, is_buff=False, damage=4.00 * self.atk, imposter=self, cc_immunity=False))
        return 0
    
    def skill2_logic(self):
        def burn_effect(self, target):
            dice = random.randint(1, 100)
            if dice <= 75:
                target.apply_effect(ContinuousDamageEffect('Burn', duration=8, is_buff=False, value=0.25 * self.atk, imposter=self))
        damage_dealt = self.attack(multiplier=2.75, repeat=1, func_after_dmg=burn_effect, target_kw1="n_random_enemy", target_kw2="5")
        return damage_dealt
        
    def skill3(self):
        pass

    def battle_entry_effects(self):
        self.apply_effect(StatsEffect('MachineGolem Passive', -1, True, {'maxhp' : 1.2, 'atk' : 1.2}, can_be_removed_by_skill=False))
        self.hp = self.maxhp


class Dullahan(character.Character):
    def __init__(self, name, lvl, exp=0, equip=None, image=None):
        super().__init__(name, lvl, exp, equip, image)
        self.original_name = "Dullahan"
        self.skill1_description = "Attack 3 closest enemies with 300% atk. Inflict Deep Wound on target for 8 turns. Deep Wound: take 200% of applier atk as status damage each turn, can be removed by healing." \
        " If target hp is below 50%, inflict 2 Deep Wound instead."
        self.skill2_description = "Attack 3 closest enemies with 300% atk, if target hp is below 50%, reduce their healing efficiency by 30% for 8 turns."
        self.skill3_description = "Increase spd by 20%."
        self.skill1_cooldown_max = 5
        self.skill2_cooldown_max = 5
        self.is_boss = True

    def skill_tooltip(self):
        return f"Skill 1 : {self.skill1_description}\nCooldown : {self.skill1_cooldown} action(s)\n\nSkill 2 : {self.skill2_description}\nCooldown : {self.skill2_cooldown} action(s)\n\nSkill 3 : {self.skill3_description}\n"

    def skill1_logic(self):
        def wound(self, target):
            if target.hp < target.maxhp * 0.5:
                target.apply_effect(ContinuousDamageEffect('Deep Wound', duration=8, is_buff=False, value=2.0 * self.atk, imposter=self, remove_by_heal=True))
                target.apply_effect(ContinuousDamageEffect('Deep Wound', duration=8, is_buff=False, value=2.0 * self.atk, imposter=self, remove_by_heal=True))
            else:
                target.apply_effect(ContinuousDamageEffect('Deep Wound', duration=8, is_buff=False, value=2.0 * self.atk, imposter=self, remove_by_heal=True))
        damage_dealt = self.attack(multiplier=3.0, repeat=1, func_after_dmg=wound, target_kw1="n_enemy_in_front", target_kw2="3")
        return damage_dealt
    
    def skill2_logic(self):
        def wound(self, target):
            if target.hp < target.maxhp * 0.5:
                target.apply_effect(StatsEffect('Healing Down', duration=8, is_buff=False, stats_dict={'heal_efficiency' : -0.3}))
        damage_dealt = self.attack(multiplier=3.0, repeat=1, func_after_dmg=wound, target_kw1="n_enemy_in_front", target_kw2="3")
        return damage_dealt

    def skill3(self):
        pass

    def battle_entry_effects(self):
        self.apply_effect(StatsEffect('Dullahan Passive', -1, True, {'spd' : 1.2}, can_be_removed_by_skill=False))


class Salamander(character.Character):
    def __init__(self, name, lvl, exp=0, equip=None, image=None):
        super().__init__(name, lvl, exp, equip, image)
        self.original_name = "Salamander"
        self.skill1_description = "Attack enemies with 170% atk 8 times, each attack has a 66% chance to inflict Burn for 6 turns." \
        " Burn deals 33% of self atk as status damage each turn."
        self.skill2_description = "Attack all enemies with 170% atk, each attack has a 75% chance to inflict Burn for 6 turns."
        self.skill3_description = "Recover hp by 3% of maxhp each turn."
        self.skill1_cooldown_max = 5
        self.skill2_cooldown_max = 5
        self.is_boss = False

    def skill_tooltip(self):
        return f"Skill 1 : {self.skill1_description}\nCooldown : {self.skill1_cooldown} action(s)\n\nSkill 2 : {self.skill2_description}\nCooldown : {self.skill2_cooldown} action(s)\n\nSkill 3 : {self.skill3_description}\n"

    def skill1_logic(self):
        def burn_effect(self, target):
            dice = random.randint(1, 100)
            if dice <= 66:
                target.apply_effect(ContinuousDamageEffect('Burn', duration=6, is_buff=False, value=0.33 * self.atk, imposter=self))
        damage_dealt = self.attack(multiplier=1.7, repeat=8, func_after_dmg=burn_effect)
        return damage_dealt

    def skill2_logic(self):
        def burn_effect(self, target):
            dice = random.randint(1, 100)
            if dice <= 75:
                target.apply_effect(ContinuousDamageEffect('Burn', duration=6, is_buff=False, value=0.33 * self.atk, imposter=self))
        damage_dealt = self.attack(multiplier=1.7, repeat=1, func_after_dmg=burn_effect, target_kw1="n_random_enemy", target_kw2="5")
        return damage_dealt

    def skill3(self):
        pass

    def battle_entry_effects(self):
        e = ContinuousHealEffect('Salamander Passive', -1, True, 0.03, True)
        e.can_be_removed_by_skill = False
        self.apply_effect(e)


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
        self.skill2_description = "For 4 turns, increase evasion by 50%. Attack closest enemy 8 times with 150% atk."
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
        self.skill3_description = "Skill attack inflict Sting on target for 6 turns. Sting: every time target take damage, take 35% of applier atk as status damage. Does not trigger for status damage."
        self.skill1_cooldown_max = 4
        self.skill2_cooldown_max = 4
        self.is_boss = False

    def skill_tooltip(self):
        return f"Skill 1 : {self.skill1_description}\nCooldown : {self.skill1_cooldown} action(s)\n\nSkill 2 : {self.skill2_description}\nCooldown : {self.skill2_cooldown} action(s)\n\nSkill 3 : {self.skill3_description}\n"

    def skill1_logic(self):
        def sting_effect(self, target):
            target.apply_effect(StingEffect('Sting', duration=6, is_buff=False, value=0.35 * self.atk, imposter=self))
        damage_dealt = self.attack(multiplier=3.0, repeat=4, func_after_dmg=sting_effect, target_kw1="enemy_in_front")
        return damage_dealt

    def skill2_logic(self):
        def sting_effect(self, target):
            target.apply_effect(StingEffect('Sting', duration=6, is_buff=False, value=0.35 * self.atk, imposter=self))
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
        self.skill3_description = "Skill have 30% chance to inflict bleed on target for 6 turns. Bleed deals 30% of atk as damage per turn."
        self.skill1_cooldown_max = 5
        self.skill2_cooldown_max = 5
        self.is_boss = False

    def skill_tooltip(self):
        return f"Skill 1 : {self.skill1_description}\nCooldown : {self.skill1_cooldown} action(s)\n\nSkill 2 : {self.skill2_description}\nCooldown : {self.skill2_cooldown} action(s)\n\nSkill 3 : {self.skill3_description}\n"

    def skill1_logic(self):
        def bleed_effect(self, target):
            dice = random.randint(1, 100)
            if dice <= 30:
                target.apply_effect(ContinuousDamageEffect('Bleed', duration=6, is_buff=False, value=0.3 * self.atk, imposter=self))
        damage_dealt = self.attack(multiplier=2.0, repeat=7, func_after_dmg=bleed_effect, target_kw1="enemy_in_front")
        return damage_dealt

    def skill2_logic(self):
        def bleed_effect(self, target):
            dice = random.randint(1, 100)
            if dice <= 30:
                target.apply_effect(ContinuousDamageEffect('Bleed', duration=6, is_buff=False, value=0.3 * self.atk, imposter=self))
        damage_dealt = damage_dealt = self.attack(target_kw1="n_lowest_attr",target_kw2="1",target_kw3="hp",target_kw4="enemy", multiplier=3.0, repeat=3, func_after_dmg=bleed_effect)
        return damage_dealt
        
    def skill3(self):
        pass


class BlackKnight(character.Character):
    def __init__(self, name, lvl, exp=0, equip=None, image=None):
        super().__init__(name, lvl, exp, equip, image)
        self.original_name = "BlackKnight"
        self.skill1_description = "Attack random enemies 12 times with 250% atk. At the end of all attack, if hp is below 40%," \
        " Increase atk and crit rate by 40% for self and neighboring allies, effect last for 6 turns."
        self.skill2_description = "For 4 turns, increase atk by 30%. Attack closest enemy 6 times with 220% atk."
        self.skill3_description = "atk increased by 40% if hp is below 40%."
        self.skill1_cooldown_max = 4
        self.skill2_cooldown_max = 4
        self.is_boss = True

    def skill_tooltip(self):
        return f"Skill 1 : {self.skill1_description}\nCooldown : {self.skill1_cooldown} action(s)\n\nSkill 2 : {self.skill2_description}\nCooldown : {self.skill2_cooldown} action(s)\n\nSkill 3 : {self.skill3_description}\n"

    def skill1_logic(self):
        damage_dealt = self.attack(multiplier=2.5, repeat=12)
        if self.is_alive() and self.hp < self.maxhp * 0.4:
            self.apply_effect(StatsEffect('Atk Up', 6, True, {'atk' : 1.4, 'crit' : 0.4}))
            for n in self.get_neighbor_allies_not_including_self():
                n.apply_effect(StatsEffect('Atk Up', 6, True, {'atk' : 1.4, 'crit' : 0.4}))
        return damage_dealt

    def skill2_logic(self):
        self.apply_effect(StatsEffect('Atk Up', 4, True, {'atk' : 1.3}))
        damage_dealt = self.attack(multiplier=2.2, repeat=6, target_kw1="enemy_in_front")
        return damage_dealt

    def skill3(self):
        pass

    def battle_entry_effects(self):
        self.apply_effect(StatsEffect('BlackKnight Passive', -1, True, {'atk' : 1.4}, 
                                      condition=lambda self: self.hp < self.maxhp * 0.4, can_be_removed_by_skill=False)) 


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
        self.skill2_description = "Each enemy has a 50% chance to be put asleep."
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
        self.apply_effect(StatsEffect('Smoke', 10, True, {'eva' : 0.5}))


# Stun machine
class MultiLegTank(character.Character):
    def __init__(self, name, lvl, exp=0, equip=None, image=None):
        super().__init__(name, lvl, exp, equip, image)
        self.original_name = "MultiLegTank"
        self.skill1_description = "Attack all enemies with 130% atk and 80% chance to Stun for 4 turns."
        self.skill2_description = "Attack 3 closest enemies with 190% atk and 80% chance to Stun for 4 turns."
        self.skill3_description = "Normal attack target closest enemy with 270% atk and 80% chance to Stun for 4 turns."
        self.skill1_cooldown_max = 5
        self.skill2_cooldown_max = 5
        self.is_boss = False

    def skill_tooltip(self):
        return f"Skill 1 : {self.skill1_description}\nCooldown : {self.skill1_cooldown} action(s)\n\nSkill 2 : {self.skill2_description}\nCooldown : {self.skill2_cooldown} action(s)\n\nSkill 3 : {self.skill3_description}\n"

    def skill1_logic(self):
        def stun_effect(self, target):
            dice = random.randint(1, 100)
            if dice <= 80:
                target.apply_effect(StunEffect('Stun', duration=4, is_buff=False))
        damage_dealt = self.attack(multiplier=1.3, repeat=1, func_after_dmg=stun_effect, target_kw1="n_random_enemy",target_kw2="5")
        return damage_dealt

    def skill2_logic(self):
        def stun_effect(self, target):
            dice = random.randint(1, 100)
            if dice <= 80:
                target.apply_effect(StunEffect('Stun', duration=4, is_buff=False))
        damage_dealt = self.attack(multiplier=1.9, repeat=1, func_after_dmg=stun_effect, target_kw1="n_enemy_in_front",target_kw2="3")
        return damage_dealt
        
    def skill3(self):
        pass

    def normal_attack(self):
        def stun_effect(self, target):
            dice = random.randint(1, 100)
            if dice <= 80:
                target.apply_effect(StunEffect('Stun', duration=4, is_buff=False))
        self.attack(multiplier=2.7, func_after_dmg=stun_effect, target_kw1="enemy_in_front")


class Assassin(character.Character):
    def __init__(self, name, lvl, exp=0, equip=None, image=None):
        super().__init__(name, lvl, exp, equip, image)
        self.original_name = "Assassin"
        self.skill1_description = "Increase atk and spd by 15% for 7 turns, recover hp by 200% atk."
        self.skill2_description = "Attack closest enemy with 321% atk 8 times, target is confused for 6 turns if target has lower spd than you." \
        " If target is confused, damage is increased by 100%."
        self.skill3_description = "Normal attack target closest enemy and attack 2 times, 40% chance to inflict Bleed for 6 turns. Bleed deals 40% of atk as damage per turn."
        self.skill1_cooldown_max = 5
        self.skill2_cooldown_max = 3
        self.is_boss = True

    def skill_tooltip(self):
        return f"Skill 1 : {self.skill1_description}\nCooldown : {self.skill1_cooldown} action(s)\n\nSkill 2 : {self.skill2_description}\nCooldown : {self.skill2_cooldown} action(s)\n\nSkill 3 : {self.skill3_description}\n"

    def skill1_logic(self):
        self.apply_effect(StatsEffect('Fast', 7, True, {'atk' : 1.15, 'spd' : 1.15}))
        self.heal_hp(2.0 * self.atk, self)

    def skill2_logic(self):
        def confuse_effect(self, target):
            if target.spd < self.spd:
                target.apply_effect(ConfuseEffect('Confuse', duration=6, is_buff=False))
        def amplify(self, target, final_damage):
            if target.is_confused():
                final_damage *= 2.0
            return final_damage
        damage_dealt = self.attack(multiplier=3.21, repeat=8, func_after_dmg=confuse_effect, target_kw1="enemy_in_front", func_damage_step=amplify)
        return damage_dealt

    def skill3(self):
        pass

    def normal_attack(self):
        def bleed_effect(self, target):
            dice = random.randint(1, 100)
            if dice <= 40:
                target.apply_effect(ContinuousDamageEffect('Bleed', duration=6, is_buff=False, value=0.4 * self.atk, imposter=self))
        self.attack(target_kw1="enemy_in_front", func_after_dmg=bleed_effect, repeat=2)


class Shenlong(character.Character):
    def __init__(self, name, lvl, exp=0, equip=None, image=None):
        super().__init__(name, lvl, exp, equip, image)
        self.original_name = "Shenlong"
        self.skill1_description = "All enemies are stunned for 4 turns. Attack all enemies 3 times with 220%/240%/260% atk each."
        self.skill2_description = "Increase atk and accuracy for all allies by 30% for 6 turns." \
        " Apply Trial of the Dragon on closest enemy for 12 turns if the same effect is not already on the target." \
        " Trial of the Dragon: atk and crit rate increased by 30%. If this effect expires, target takes 1 status damage is stunned for 12 turns." \
        " Trial of the Dragon cannot be removed by skill."
        self.skill3_description = "Increase hp by 222%."
        self.skill1_cooldown_max = 5
        self.skill2_cooldown_max = 5
        self.is_boss = True

    def skill_tooltip(self):
        return f"Skill 1 : {self.skill1_description}\nCooldown : {self.skill1_cooldown} action(s)\n\nSkill 2 : {self.skill2_description}\nCooldown : {self.skill2_cooldown} action(s)\n\nSkill 3 : {self.skill3_description}\n"

    def skill1_logic(self):
        for e in self.enemy:
            e.apply_effect(StunEffect('Stun', duration=4, is_buff=False))
        damage_dealt = self.attack(multiplier=2.2, repeat=1, target_kw1="n_random_enemy",target_kw2="5")
        damage_dealt += self.attack(multiplier=2.4, repeat=1, target_kw1="n_random_enemy",target_kw2="5")
        damage_dealt += self.attack(multiplier=2.6, repeat=1, target_kw1="n_random_enemy",target_kw2="5")
        return damage_dealt


    def skill2_logic(self):
        for a in self.ally:
            a.apply_effect(StatsEffect('Atk Acc Up', 6, True, {'atk' : 1.3, 'acc' : 1.3}))
        target = next(self.target_selection("enemy_in_front"))
        if not target.has_effect_that_named("Trial of the Dragon"):
            target.apply_effect(TrialofDragonEffect('Trial of the Dragon', duration=12, is_buff=False, stats_dict={'atk' : 1.3, 'crit' : 0.3},
                                                    damage=1, imposter=self, stun_duration=12))

    def skill3(self):
        pass

    def battle_entry_effects(self):
        self.apply_effect(StatsEffect('Shenlong Passive', -1, True, {'maxhp' : 3.22}, can_be_removed_by_skill=False))
        self.hp = self.maxhp


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
        self.skill3_description = "Skill attack inflict both Burn and Bleed for 5 turns, deals 30% of atk as status damage per turn."
        self.skill1_cooldown_max = 5
        self.skill2_cooldown_max = 5
        self.is_boss = False

    def skill_tooltip(self):
        return f"Skill 1 : {self.skill1_description}\nCooldown : {self.skill1_cooldown} action(s)\n\nSkill 2 : {self.skill2_description}\nCooldown : {self.skill2_cooldown} action(s)\n\nSkill 3 : {self.skill3_description}\n"

    def skill1_logic(self):
        def burn_effect(self, target):
            target.apply_effect(ContinuousDamageEffect('Burn', duration=5, is_buff=False, value=0.3 * self.atk, imposter=self))
            target.apply_effect(ContinuousDamageEffect('Bleed', duration=5, is_buff=False, value=0.3 * self.atk, imposter=self))
        damage_dealt = self.attack(multiplier=3.0, repeat_seq=2, func_after_dmg=burn_effect, target_kw1="n_lowest_attr", target_kw2="1", target_kw3="hp", target_kw4="enemy")
        return damage_dealt

    def skill2_logic(self):
        def burn_effect(self, target):
            target.apply_effect(ContinuousDamageEffect('Burn', duration=5, is_buff=False, value=0.3 * self.atk, imposter=self))
            target.apply_effect(ContinuousDamageEffect('Bleed', duration=5, is_buff=False, value=0.3 * self.atk, imposter=self))
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


class BlackDragon(character.Character):
    def __init__(self, name, lvl, exp=0, equip=None, image=None):
        super().__init__(name, lvl, exp, equip, image)
        self.original_name = "BlackDragon"
        self.skill1_description = "Attack enemy with lowest hp with 340% atk 2 times and inflict Bleed for 5 turns. Bleed deals 50% of atk as status damage per turn."
        self.skill2_description = "Attack all enemies with 220% atk, inflict Burn on all enemies with hp lower than 50% for 5 turns." \
        "If target hp is lower than 25%, inflict an additional Burn for 10 turns."
        "Burn deals 100% of atk as status damage per turn. This attack does not miss."
        self.skill3_description = "Increase hp by 200%"
        self.skill1_cooldown_max = 4
        self.skill2_cooldown_max = 4
        self.is_boss = True

    def skill_tooltip(self):
        return f"Skill 1 : {self.skill1_description}\nCooldown : {self.skill1_cooldown} action(s)\n\nSkill 2 : {self.skill2_description}\nCooldown : {self.skill2_cooldown} action(s)\n\nSkill 3 : {self.skill3_description}\n"

    def skill1_logic(self):
        def bleed_effect(self, target):
            target.apply_effect(ContinuousDamageEffect('Bleed', duration=5, is_buff=False, value=0.5 * self.atk, imposter=self))
        damage_dealt = self.attack(multiplier=3.4, repeat_seq=2, func_after_dmg=bleed_effect, target_kw1="n_lowest_attr", target_kw2="1", target_kw3="hp", target_kw4="enemy")
        return damage_dealt

    def skill2_logic(self):
        def burn_effect(self, target):
            if target.hp < target.maxhp * 0.5:
                target.apply_effect(ContinuousDamageEffect('Burn', duration=5, is_buff=False, value=1.0 * self.atk, imposter=self))
            if target.hp < target.maxhp * 0.25:
                target.apply_effect(ContinuousDamageEffect('Burn', duration=10, is_buff=False, value=1.0 * self.atk, imposter=self))
        damage_dealt = self.attack(multiplier=2.2, repeat=1, func_after_dmg=burn_effect, target_kw1="n_random_enemy", target_kw2="5", always_hit=True)
        return damage_dealt

    def skill3(self):
        pass

    def battle_entry_effects(self):
        self.apply_effect(StatsEffect('BlackDragon Passive', -1, True, {'maxhp' : 3.0}, can_be_removed_by_skill=False))
        self.hp = self.maxhp


class BakeNeko(character.Character):
    def __init__(self, name, lvl, exp=0, equip=None, image=None):
        super().__init__(name, lvl, exp, equip, image)
        self.original_name = "BakeNeko"
        self.skill1_description = "Increase maxhp by 30% for all allies for 8 turns and Heal all allies by 300% atk."
        self.skill2_description = "Heal 1 ally with lowest hp by 200% atk." \
        " Apply Supression on all allies for 6 turns. Supression: During damage calculation," \
        " damage increased by the ratio of self hp to target hp if self has more hp than target. Max bonus damage: 1000%."
        self.skill3_description = "Increase maxhp and def by 30%, evasion by 15%."
        self.skill1_cooldown_max = 5
        self.skill2_cooldown_max = 5
        self.is_boss = False

    def skill_tooltip(self):
        return f"Skill 1 : {self.skill1_description}\nCooldown : {self.skill1_cooldown} action(s)\n\nSkill 2 : {self.skill2_description}\nCooldown : {self.skill2_cooldown} action(s)\n\nSkill 3 : {self.skill3_description}\n"

    def skill1_logic(self):
        for a in self.ally:
            a.apply_effect(StatsEffect('Maxhp Up', 8, True, {'maxhp' : 1.3}))
        self.heal("n_random_ally", "5", value=3.0 * self.atk)

    def skill2_logic(self):
        self.heal("n_lowest_attr", "1", "hp", "ally", value=2.0 * self.atk)
        for a in self.ally:
            a.apply_effect(BakeNekoSupressionEffect('Supression', 6, True))
    
    def skill3(self):
        pass

    def battle_entry_effects(self):
        self.apply_effect(StatsEffect('BakeNeko Passive', -1, True, {'maxhp' : 1.3, 'defense' : 1.3, 'eva' : 0.15}, can_be_removed_by_skill=False))
        self.hp = self.maxhp


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
        self.skill1_description = "Attack 3 closest enemies 2 times and deal 265% atk. For 70% chance each attack, reduce target spd by 30% for 6 turns."
        self.skill2_description = "Attack closest enemy with 200% atk, if target has lower spd than you, deal 120% more damage and reduce target spd by 30% for 6 turns."
        self.skill3_description = "Increase spd by 20%. Nearby allies have their spd increased by 20% for 15 turns."
        self.skill1_cooldown_max = 4
        self.skill2_cooldown_max = 5
        self.is_boss = False

    def skill_tooltip(self):
        return f"Skill 1 : {self.skill1_description}\nCooldown : {self.skill1_cooldown} action(s)\n\nSkill 2 : {self.skill2_description}\nCooldown : {self.skill2_cooldown} action(s)\n\nSkill 3 : {self.skill3_description}\n"

    def skill1_logic(self):
        def slow_effect(self, target):
            dice = random.randint(1, 100)
            if dice <= 70:
                target.apply_effect(StatsEffect('Slow', duration=6, is_buff=False, stats_dict={'spd' : 0.7}))
        damage_dealt = self.attack(multiplier=2.65, repeat_seq=2, func_after_dmg=slow_effect, target_kw1="n_enemy_in_front", target_kw2="3")
        return damage_dealt

    def skill2_logic(self):
        def slow_effect(self, target):
            if target.spd < self.spd:
                target.apply_effect(StatsEffect('Slow', duration=6, is_buff=False, stats_dict={'spd' : 0.7}))
        def spd_penalty(self, target, final_damage):
            if target.spd < self.spd:
                final_damage *= 2.2
            return final_damage
        damage_dealt = self.attack(multiplier=2.0, repeat=1, func_after_dmg=slow_effect, func_damage_step=spd_penalty, target_kw1="enemy_in_front")
        return damage_dealt

    def skill3(self):
        pass

    def battle_entry_effects(self):
        self.apply_effect(StatsEffect('Wyvern Passive', -1, True, {'spd' : 1.2}, can_be_removed_by_skill=False))
        for neighbor in self.get_neighbor_allies_not_including_self():
            neighbor.apply_effect(StatsEffect('Spd Up', 15, True, {'spd' : 1.2}))


class Agent(character.Character):
    def __init__(self, name, lvl, exp=0, equip=None, image=None):
        super().__init__(name, lvl, exp, equip, image)
        self.original_name = "Agent"
        self.skill1_description = "Attack 1 enemy with lowest spd with 330% atk 3 times, each attack has 100% chance to inflict Bleed for 6 turns. Bleed deals 80% of atk as status damage per turn."
        self.skill2_description = "Increase evasion and accuracy by 50% for 5 turns."
        self.skill3_description = "Normal attack target enemy with lowest spd and deals 100% more damage."
        self.skill1_cooldown_max = 4
        self.skill2_cooldown_max = 5
        self.is_boss = False

    def skill_tooltip(self):
        return f"Skill 1 : {self.skill1_description}\nCooldown : {self.skill1_cooldown} action(s)\n\nSkill 2 : {self.skill2_description}\nCooldown : {self.skill2_cooldown} action(s)\n\nSkill 3 : {self.skill3_description}\n"

    def skill1_logic(self):
        def bleed_effect(self, target):
            target.apply_effect(ContinuousDamageEffect('Bleed', duration=6, is_buff=False, value=0.8 * self.atk, imposter=self))
        damage_dealt = self.attack(multiplier=3.3, repeat=3, func_after_dmg=bleed_effect, target_kw1="n_lowest_attr", target_kw2="1", target_kw3="spd", target_kw4="enemy")
        return damage_dealt

    def skill2_logic(self):
        self.apply_effect(StatsEffect('Ready Up', 5, True, {'eva' : 0.5, 'acc' : 0.5}))
        return 0

    def skill3(self):
        pass

    def normal_attack(self):
        def damage_increase(self, target, final_damage):
            final_damage *= 2.0
            return final_damage
        self.attack(func_damage_step=damage_increase, target_kw1="n_lowest_attr", target_kw2="1", target_kw3="spd", target_kw4="enemy")


# ====================================
# End of spd
# ====================================
# Crit
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
        self.apply_effect(StatsEffect('SoldierB Passive', -1, True, {'crit' : 0.3, 'critdmg' : 0.3}, can_be_removed_by_skill=False))


class Queen(character.Character):
    # Boss
    def __init__(self, name, lvl, exp=0, equip=None, image=None):
        super().__init__(name, lvl, exp, equip, image)
        self.original_name = "Queen"
        self.skill1_description = "Attack random ememies with 260% atk 8 times, after each successful attack, increase critical damage by 20% for 3 turns."
        self.skill2_description = "Attack 3 front enemies with 300% atk, decrease their critical defense by 30%, for 8 turns. After this skill, increase critical damage by 20% for 6 turns."
        self.skill3_description = "Critical chance is increased by 60%. Speed is increased by 20%."
        self.skill1_cooldown_max = 5
        self.skill2_cooldown_max = 3
        self.is_boss = True

    def skill_tooltip(self):
        return f"Skill 1 : {self.skill1_description}\nCooldown : {self.skill1_cooldown} action(s)\n\nSkill 2 : {self.skill2_description}\nCooldown : {self.skill2_cooldown} action(s)\n\nSkill 3 : {self.skill3_description}\n"

    def skill1_logic(self):
        def critdmg_increase(self, target):
            self.apply_effect(StatsEffect('Control', 3, True, {'critdmg' : 0.20}))
        damage_dealt = self.attack(multiplier=2.6, repeat=8, func_after_dmg=critdmg_increase)
        return damage_dealt

    def skill2_logic(self):
        def critdef_decrease(self, target):
            target.apply_effect(StatsEffect('Compliance', 8, True, {'critdef' : -0.3}))
        damage_dealt = self.attack(multiplier=3.0, repeat=1, func_after_dmg=critdef_decrease, target_kw1="n_enemy_in_front", target_kw2="3")
        if self.is_alive():
            self.apply_effect(StatsEffect('Control', 6, True, {'critdmg' : 0.20}))
        return damage_dealt

    def skill3(self):
        pass

    def battle_entry_effects(self):
        self.apply_effect(StatsEffect('Queen Passive', -1, True, {'crit' : 0.6, 'spd' : 1.2}, can_be_removed_by_skill=False))


class KungFuA(character.Character):
    def __init__(self, name, lvl, exp=0, equip=None, image=None):
        super().__init__(name, lvl, exp, equip, image)
        self.original_name = "KungFuA"
        self.skill1_description = "Focus attack on enemy with lowest crit defense with 280% atk 4 times, each attack increases" \
        " self crit rate and critdmg by 20% and decrease target crit defense by 10% for 6 turns."
        self.skill2_description = "For 2 turns, increase critdmg by 100%, focus attack on enemy with lowest crit defense with 440% atk 2 times."
        self.skill3_description = "Increase accuracy and crit rate by 40%, all allies have increased accuracy by 20%."
        self.skill1_cooldown_max = 4
        self.skill2_cooldown_max = 4
        self.is_boss = True

    def skill_tooltip(self):
        return f"Skill 1 : {self.skill1_description}\nCooldown : {self.skill1_cooldown} action(s)\n\nSkill 2 : {self.skill2_description}\nCooldown : {self.skill2_cooldown} action(s)\n\nSkill 3 : {self.skill3_description}\n"

    def skill1_logic(self):
        def critdmg_increase(self, target):
            self.apply_effect(StatsEffect('Crit Up', 6, True, {'critdmg' : 0.2, 'crit' : 0.2}))
            target.apply_effect(StatsEffect('Critdef Down', 6, True, {'critdef' : -0.1}))
        damage_dealt = self.attack(multiplier=2.6, repeat_seq=4, func_after_dmg=critdmg_increase, 
                                   target_kw1="n_lowest_attr", target_kw2="1", target_kw3="critdef", target_kw4="enemy")
        return damage_dealt

    def skill2_logic(self):
        self.apply_effect(StatsEffect('Critdmg Up', 2, True, {'critdmg' : 1.0}))
        damage_dealt = self.attack(multiplier=4.4, repeat_seq=2, target_kw1="n_lowest_attr", target_kw2="1", target_kw3="critdef", target_kw4="enemy")
        return damage_dealt
        
    def skill3(self):
        pass

    def battle_entry_effects(self):
        self.apply_effect(StatsEffect('KungFuA Passive', -1, True, {'acc' : 0.4, 'crit' : 0.4}, can_be_removed_by_skill=False))
        for a in self.ally:
            a.apply_effect(StatsEffect('KungFuA Passive', -1, True, {'acc' : 0.2}, can_be_removed_by_skill=False))


# ====================================
# End of Crit
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
        shield = EffectShield3('Shielded', -1, True, 0.5, 0.3)
        shield.can_be_removed_by_skill = False
        self.apply_effect(shield)
         

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
        shield = CancellationShield3('Guidance', -1, True, 0.1, False, uses=300)
        shield.can_be_removed_by_skill = False
        self.apply_effect(shield)
        self.apply_effect(StatsEffect('Father Passive', -1, True, {'final_damage_taken_multipler' : -0.20}, can_be_removed_by_skill=False))
         

class Kobold(character.Character):
    def __init__(self, name, lvl, exp=0, equip=None, image=None):
        super().__init__(name, lvl, exp, equip, image)
        self.original_name = "Kobold"
        self.skill1_description = "Recover hp by 30% of maxhp and increase defense by 50% for 7 turns. If you are the only one alive, effect is increased by 100%."
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
            self.apply_effect(StatsEffect('Kobold Power', 7, True, {'defense' : 2.0}))
        else:
            self.heal_hp(self.maxhp * 0.3, self)
            self.apply_effect(StatsEffect('Kobold Power', 7, True, {'defense' : 1.5}))
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
        self.apply_effect(StatsEffect('Kobold Passive', -1, True, {'defense' : 1.25, 'maxhp' : 1.25}, can_be_removed_by_skill=False))


class SoldierA(character.Character):
    def __init__(self, name, lvl, exp=0, equip=None, image=None):
        super().__init__(name, lvl, exp, equip, image)
        self.original_name = "SoldierA"
        self.skill1_description = "Focus attack on enemy with highest defense with 360% atk 3 times, each attack will reduce target defense by 20% for 7 turns."
        self.skill2_description = "Attack all enemies with 200% atk and reduce defense by 35% for 7 turns."
        self.skill3_description = "Skill attack have 30% chance to inflict Bleed for 6 turns. Bleed: takes 30% of atk as status damage per turn."
        self.skill1_cooldown_max = 4
        self.skill2_cooldown_max = 4
        self.is_boss = False

    def skill_tooltip(self):
        return f"Skill 1 : {self.skill1_description}\nCooldown : {self.skill1_cooldown} action(s)\n\nSkill 2 : {self.skill2_description}\nCooldown : {self.skill2_cooldown} action(s)\n\nSkill 3 : {self.skill3_description}\n"

    def skill1_logic(self):
        def bleed_effect_defence_break(self, target):
            dice = random.randint(1, 100)
            if dice <= 30:
                target.apply_effect(ContinuousDamageEffect('Bleed', duration=6, is_buff=False, value=0.3 * self.atk, imposter=self))
            target.apply_effect(StatsEffect('Defence Break', 7, False, {'defense' : 0.80}))
        damage_dealt = self.attack(multiplier=3.6, repeat_seq=3, func_after_dmg=bleed_effect_defence_break, target_kw1="n_highest_attr", target_kw2="1", target_kw3="defense", target_kw4="enemy")
        return damage_dealt

    def skill2_logic(self):
        def bleed_effect_defence_break(self, target):
            dice = random.randint(1, 100)
            if dice <= 30:
                target.apply_effect(ContinuousDamageEffect('Bleed', duration=6, is_buff=False, value=0.3 * self.atk, imposter=self))
            target.apply_effect(StatsEffect('Defence Break', 7, False, {'defense' : 0.65}))
        damage_dealt = self.attack(multiplier=2.0, repeat=1, func_after_dmg=bleed_effect_defence_break, target_kw1="n_random_enemy", target_kw2="5")
        return damage_dealt
        
    def skill3(self):
        pass


class FutureSoldier(character.Character):
    def __init__(self, name, lvl, exp=0, equip=None, image=None):
        super().__init__(name, lvl, exp, equip, image)
        self.original_name = "FutureSoldier"
        self.skill1_description = "Attack random enemies 5 times with 200% atk, each attack reduces target defense by 25% for 6 turns." # 0.7**5 = 0.168
        self.skill2_description = "Attack random enemies 7 times with 150% atk, if target has lower defense than self, increase damage by 100%."
        self.skill3_description = "Normal attack deals double damage if target has lower defense than self."
        self.skill1_cooldown_max = 4
        self.skill2_cooldown_max = 4
        self.is_boss = False

    def skill_tooltip(self):
        return f"Skill 1 : {self.skill1_description}\nCooldown : {self.skill1_cooldown} action(s)\n\nSkill 2 : {self.skill2_description}\nCooldown : {self.skill2_cooldown} action(s)\n\nSkill 3 : {self.skill3_description}\n"

    def skill1_logic(self):
        def defence_break(self, target):
            target.apply_effect(StatsEffect('Defence Break', 6, False, {'defense' : 0.75}))
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
        self.apply_effect(StatsEffect('FutureElite Passive', -1, True, {'defense' : 1.3}, can_be_removed_by_skill=False))


class Mandrake(character.Character):
    def __init__(self, name, lvl, exp=0, equip=None, image=None):
        super().__init__(name, lvl, exp, equip, image)
        self.original_name = "Mandrake"
        self.skill1_description = "Heal 2 neighbor allies by 100% def and increase their defense by 30% for 6 turns."
        self.skill2_description = "2 neighbor allies gain regeneration for 6 turns, heal 100% of self def per turn." \
        " For 6 turns, their critical defense is increased by 30%."
        self.skill3_description = "Maxhp is increased by 15%, defense is increased by 150%."
        self.skill1_cooldown_max = 5
        self.skill2_cooldown_max = 5
        self.is_boss = False

    def skill_tooltip(self):
        return f"Skill 1 : {self.skill1_description}\nCooldown : {self.skill1_cooldown} action(s)\n\nSkill 2 : {self.skill2_description}\nCooldown : {self.skill2_cooldown} action(s)\n\nSkill 3 : {self.skill3_description}\n"

    def skill1_logic(self):
        neighbors = self.get_neighbor_allies_not_including_self()
        def effect(self, target, healing, overhealing):
            target.apply_effect(StatsEffect('Defense Up', 6, True, {'defense' : 1.3}))
        self.heal(target_list=neighbors, value=1.0 * self.defense, func_after_each_heal=effect)
        return 0

    def skill2_logic(self):
        neighbors = self.get_neighbor_allies_not_including_self()
        for n in neighbors:
            n.apply_effect(ContinuousHealEffect('Regeneration', 6, True, 1.0 * self.defense, False))
            n.apply_effect(StatsEffect('Critical Defense Up', 6, True, {'critdef' : 0.3}))
        return 0
    
    def skill3(self):
        pass

    def battle_entry_effects(self):
        self.apply_effect(StatsEffect('Mandrake Passive', -1, True, {'maxhp' : 1.15, 'defense' : 2.5}, can_be_removed_by_skill=False))
        self.hp = self.maxhp



# ====================================
# End of Defence
# ====================================
# Evasion
# ====================================


class Gryphon(character.Character):
    def __init__(self, name, lvl, exp=0, equip=None, image=None):
        super().__init__(name, lvl, exp, equip, image)
        self.original_name = "Gryphon"
        self.skill1_description = "Self and 2 neighboring allies gain 40% evasion for 5 turns."
        self.skill2_description = "Attack 3 closest enemies with 250% atk 2 times, each attack has 70% chance to inflict Bleed for 4 turns." \
        "Bleed deals 50% of atk as status damage per turn."
        self.skill3_description = "Evasion is increased by 50%, speed is increased by 5%."
        self.skill1_cooldown_max = 5
        self.skill2_cooldown_max = 5
        self.is_boss = False

    def skill_tooltip(self):
        return f"Skill 1 : {self.skill1_description}\nCooldown : {self.skill1_cooldown} action(s)\n\nSkill 2 : {self.skill2_description}\nCooldown : {self.skill2_cooldown} action(s)\n\nSkill 3 : {self.skill3_description}\n"

    def skill1_logic(self):
        self_and_neighbor = self.get_neighbor_allies_including_self() # list
        for ally in self_and_neighbor:
            ally.apply_effect(StatsEffect('Evasion Up', 5, True, {'eva' : 0.4}))
        return 0

    def skill2_logic(self):
        def bleed_effect(self, target):
            dice = random.randint(1, 100)
            if dice <= 70:
                target.apply_effect(ContinuousDamageEffect('Bleed', duration=4, is_buff=False, value=0.5 * self.atk, imposter=self))
        damage_dealt = self.attack(multiplier=2.5, repeat_seq=2, func_after_dmg=bleed_effect, target_kw1="n_enemy_in_front", target_kw2="3")
        return damage_dealt

    def skill3(self):
        pass

    def battle_entry_effects(self):
        self.apply_effect(StatsEffect('Gryphon Passive', -1, True, {'eva' : 0.5, 'spd' : 1.05}, can_be_removed_by_skill=False))


class Hermit(character.Character):
    def __init__(self, name, lvl, exp=0, equip=None, image=None):
        super().__init__(name, lvl, exp, equip, image)
        self.original_name = "Hermit"
        self.skill1_description = "Attack 3 closest enemies with 235% atk 4 times, damage increased by the percentage of evasion rate." \
        " After the attack, increase evasion by 20% for 4 turns."
        self.skill2_description = "Attack all enemies with 500% atk, if evasion rate is higher than 70%, this attack will not miss and guarantee" \
        " to be a critical hit. Inflict Blind for 5 turns, Blind: reduce accuracy by 50%."
        self.skill3_description = "Evasion increased by 50%. Final damage taken is reduced by 15%."
        self.skill1_cooldown_max = 5
        self.skill2_cooldown_max = 5
        self.is_boss = True

    def skill_tooltip(self):
        return f"Skill 1 : {self.skill1_description}\nCooldown : {self.skill1_cooldown} action(s)\n\nSkill 2 : {self.skill2_description}\nCooldown : {self.skill2_cooldown} action(s)\n\nSkill 3 : {self.skill3_description}\n"

    def skill1_logic(self):
        def damage_amplify(self, target, final_damage):
            final_damage *= max(1 + self.eva, 1.0)
            return final_damage
        damage_dealt = self.attack(multiplier=2.35, repeat_seq=4, func_damage_step=damage_amplify, target_kw1="n_enemy_in_front", target_kw2="3")
        self.apply_effect(StatsEffect('Evasion Up', 4, True, {'eva' : 0.2}))
        return damage_dealt

    def skill2_logic(self):
        if self.eva > 0.7:
            def blind_effect(self, target):
                target.apply_effect(StatsEffect('Blind', 5, False, {'acc' : -0.5}))
            damage_dealt = self.attack(multiplier=5.0, repeat=1, func_after_dmg=blind_effect, always_hit=True, always_crit=True)
        else:
            def blind_effect(self, target):
                target.apply_effect(StatsEffect('Blind', 5, False, {'acc' : -0.5}))
            damage_dealt = self.attack(multiplier=5.0, repeat=1, func_after_dmg=blind_effect)
        return damage_dealt

    def skill3(self):
        pass

    def battle_entry_effects(self):
        self.apply_effect(StatsEffect('Hermit Passive', -1, True, {'eva' : 0.5, 'final_damage_taken_multipler' : -0.15}, can_be_removed_by_skill=False))


class KungFuB(character.Character):
    def __init__(self, name, lvl, exp=0, equip=None, image=None):
        super().__init__(name, lvl, exp, equip, image)
        self.original_name = "KungFuB"
        self.skill1_description = "For 1 turn, increase accuracy by 25%," \
        " attack enemy with highest evasion with 240% atk 4 times. Each attack has 100% chance to Stun for 4 turns," \
        " 40% chance to inflict Bleed for 6 turns. Bleed: takes 40% of atk as status damage per turn."
        self.skill2_description = "For 5 turns, all allies gain atk equal to 100% of their current evasion rate if their evasion rate is higher than 0%."
        self.skill3_description = "All allies have increased evasion by 20% and accuracy by 40%."
        self.skill1_cooldown_max = 5
        self.skill2_cooldown_max = 5
        self.is_boss = True

    def skill_tooltip(self):
        return f"Skill 1 : {self.skill1_description}\nCooldown : {self.skill1_cooldown} action(s)\n\nSkill 2 : {self.skill2_description}\nCooldown : {self.skill2_cooldown} action(s)\n\nSkill 3 : {self.skill3_description}\n"

    def skill1_logic(self):
        self.apply_effect(StatsEffect('KungFu', 1, True, {'acc' : 0.25}))
        def bleed_stun_effect(self, target):
            dice = random.randint(1, 100)
            if dice <= 40:
                target.apply_effect(ContinuousDamageEffect('Bleed', duration=6, is_buff=False, value=0.4 * self.atk, imposter=self))
            target.apply_effect(StunEffect('Stun', 4, False))
        damage_dealt = self.attack(multiplier=2.4, repeat=4, func_after_dmg=bleed_stun_effect, target_kw1="n_highest_attr", target_kw2="1", target_kw3="eva", target_kw4="enemy")
        return damage_dealt

    def skill2_logic(self):
        for a in self.ally:
            if a.eva > 0:
                a.apply_effect(StatsEffect('KungFu', 5, True, {'atk' : a.eva + 1.0}))
        return 0
        
    def skill3(self):
        pass

    def battle_entry_effects(self):
        for a in self.ally:
            a.apply_effect(StatsEffect('KungFu', -1, True, {'eva' : 0.2, 'acc' : 0.4}, can_be_removed_by_skill=False))


class HauntedTree(character.Character):
    def __init__(self, name, lvl, exp=0, equip=None, image=None):
        super().__init__(name, lvl, exp, equip, image)
        self.original_name = "HauntedTree"
        self.skill1_description = "3 closest enemies are Rooted for 9 turns. Rooted: evasion is reduced by 55%, def and critdef is reduced by 20%." \
        " Effect duration refreshes if same effect is applied again."
        self.skill2_description = "If no enemy is Rooted, this skill has no effect." \
        " Attack all Rooted enemies with 360% atk 3 times, each attack deals additional damage equal to 5% of self maxhp."
        self.skill3_description = "Damage taken is reduced by 60% from Rooted enemies. maxhp, def and critdef is increased by 30%."
        self.skill1_cooldown_max = 4
        self.skill2_cooldown_max = 4
        self.is_boss = False

    def skill_tooltip(self):
        return f"Skill 1 : {self.skill1_description}\nCooldown : {self.skill1_cooldown} action(s)\n\nSkill 2 : {self.skill2_description}\nCooldown : {self.skill2_cooldown} action(s)\n\nSkill 3 : {self.skill3_description}\n"

    def skill1_logic(self):
        targets = self.target_selection("n_enemy_in_front", "3")
        eff = StatsEffect('Rooted', 9, False, {'eva' : -0.55, 'defense' : 0.8, 'critdef' : -0.2})
        eff.additional_name = "HauntedTree_Rooted"
        eff.apply_rule = 'stack'
        for target in targets:
            target.apply_effect(eff)
        return 0

    def skill2_logic(self):
        rooted_enemies = list(self.target_selection("enemy_that_must_have_effect", "Rooted"))
        if not rooted_enemies:
            return 0
        def additional_damage(self, target, final_damage):
            final_damage += 0.05 * self.maxhp
            return final_damage
        damage_dealt = self.attack(multiplier=3.6, repeat=3, func_damage_step=additional_damage, target_list=rooted_enemies)
        return damage_dealt

    def skill3(self):
        pass

    def take_damage_before_calculation(self, damage, attacker):
        if attacker.has_effect_that_named('Rooted', additional_name='HauntedTree_Rooted'):
            global_vars.turn_info_string += f"{self.name} toke 60% less damage from {attacker.name}.\n"
            return damage * 0.4
        return damage

    def battle_entry_effects(self):
        self.apply_effect(StatsEffect('HauntedTree Passive', -1, True, {'defense' : 1.30, 'critdef' : 0.30, 'maxhp' : 1.30}))
        self.hp = self.maxhp


# ====================================
# End of Evasion
# ====================================
# Negative Status
# ====================================
        
class Mage(character.Character):
    def __init__(self, name, lvl, exp=0, equip=None, image=None):
        super().__init__(name, lvl, exp, equip, image)
        self.original_name = "Mage"
        self.skill1_description = "Attack 3 closest enemies with 300% atk and inflict Burn for 6 turns. Burn deals 40% of atk as status damage per turn. If target has negative status, inflict 3 Burn effects."
        self.skill2_description = "Attack closest enemy 3 times with 320% atk, if target has negative status, each attack inflict 3 Burn effects for 6 turns."
        self.skill3_description = "Increase atk by 10%"
        self.skill1_cooldown_max = 5
        self.skill2_cooldown_max = 5
        self.is_boss = False

    def skill_tooltip(self):
        return f"Skill 1 : {self.skill1_description}\nCooldown : {self.skill1_cooldown} action(s)\n\nSkill 2 : {self.skill2_description}\nCooldown : {self.skill2_cooldown} action(s)\n\nSkill 3 : {self.skill3_description}\n"

    def skill1_logic(self):
        def burn_effect(self, target):
            if len(target.debuffs) > 0:
                target.apply_effect(ContinuousDamageEffect('Burn', duration=6, is_buff=False, value=0.4 * self.atk, imposter=self))
                target.apply_effect(ContinuousDamageEffect('Burn', duration=6, is_buff=False, value=0.4 * self.atk, imposter=self))
                target.apply_effect(ContinuousDamageEffect('Burn', duration=6, is_buff=False, value=0.4 * self.atk, imposter=self))
            else:
                target.apply_effect(ContinuousDamageEffect('Burn', duration=6, is_buff=False, value=0.4 * self.atk, imposter=self))
        damage_dealt = self.attack(multiplier=3.0, repeat=1, func_after_dmg=burn_effect, target_kw1="n_enemy_in_front", target_kw2="3")
        return damage_dealt

    def skill2_logic(self):
        def burn_effect(self, target):
            if len(target.debuffs) > 0:
                target.apply_effect(ContinuousDamageEffect('Burn', duration=6, is_buff=False, value=0.4 * self.atk, imposter=self))
                target.apply_effect(ContinuousDamageEffect('Burn', duration=6, is_buff=False, value=0.4 * self.atk, imposter=self))
                target.apply_effect(ContinuousDamageEffect('Burn', duration=6, is_buff=False, value=0.4 * self.atk, imposter=self))
        damage_dealt = self.attack(multiplier=3.2, repeat=3, func_after_dmg=burn_effect, target_kw1="enemy_in_front")
        return damage_dealt

    def skill3(self):
        pass

    def battle_entry_effects(self):
        self.apply_effect(StatsEffect('Mage Passive', -1, True, {'atk' : 1.1}, can_be_removed_by_skill=False))


# Increase debuff duration
class Orklord(character.Character):
    def __init__(self, name, lvl, exp=0, equip=None, image=None):
        super().__init__(name, lvl, exp, equip, image)
        self.original_name = "Orklord"
        self.skill1_description = "Attack closest enemy with 300% atk 3 times. If target has negative status effect, increase effect duration by 4 turns."
        self.skill2_description = "Attack 5 enemies with 400% atk and inflict Bleed for 10 turns. Bleed deals 55% of atk as status damage per turn."
        self.skill3_description = "Normal attack deals 200% more damage to target with Bleed. Increase maxhp and defense by 50%."
        self.skill1_cooldown_max = 3
        self.skill2_cooldown_max = 3
        self.is_boss = True

    def skill_tooltip(self):
        return f"Skill 1 : {self.skill1_description}\nCooldown : {self.skill1_cooldown} action(s)\n\nSkill 2 : {self.skill2_description}\nCooldown : {self.skill2_cooldown} action(s)\n\nSkill 3 : {self.skill3_description}\n"

    def skill1_logic(self):
        target = next(self.target_selection(keyword="enemy_in_front"))
        damage_dealt = self.attack(multiplier=3.0, repeat=3, target_list=[target])
        if self.is_alive() and target.is_alive():
            for debuff in target.debuffs:
                if debuff.duration > 0:
                    debuff.duration += 4
        return damage_dealt

    def skill2_logic(self):
        def bleed_effect(self, target):
            target.apply_effect(ContinuousDamageEffect('Bleed', duration=10, is_buff=False, value=0.55 * self.atk, imposter=self))
        damage_dealt = self.attack(multiplier=3.0, repeat=1, func_after_dmg=bleed_effect, target_kw1="n_random_enemy", target_kw2="5")
        return damage_dealt

    def skill3(self):
        pass

    def normal_attack(self):
        def damage_amplify(self, target, final_damage):
            if target.has_effect_that_named('Bleed'):
                final_damage *= 3.0
            return final_damage
        self.attack(func_damage_step=damage_amplify)

    def battle_entry_effects(self):
        self.apply_effect(StatsEffect('Orklord Passive', -1, True, {'maxhp' : 1.50, 'defense' : 1.50}, can_be_removed_by_skill=False))
        self.hp = self.maxhp



# # Increase damage taken for debuffed target, always attack debuffed target
# class SubjectA2(character.Character):
#     pass


# ====================================
# End of Negative Status
# ====================================
# Positive Status
# Damage increases and others if target has active buffs
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
        self.apply_effect(StatsEffect('Goliath Passive', -1, True, {'atk' : 1.3, 'defense' : 1.3, 'maxhp' : 1.3}, can_be_removed_by_skill=False))
        self.hp = self.maxhp


# ====================================
# End of Positive Status
# ====================================
# No Status
# Damage increases and others if target has no active buffs
# ====================================
        

class ReconMecha(character.Character): 
    def __init__(self, name, lvl, exp=0, equip=None, image=None):
        super().__init__(name, lvl, exp, equip, image)
        self.original_name = "ReconnaissanceMecha"
        self.skill1_description = "Attack closest enemy with 280% atk 2 times, if target has no active buff, increase damage by 100%."
        self.skill2_description = "Attack closest enemy with 280% atk 2 times, if target has no active buff, target defense is reduced by 40% for 8 turns."
        self.skill3_description = "Every turn, at the end of turn, if an enemy is fallen in this turn, recover hp by 30% of maxhp."
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
        self.apply_effect(StatsEffect('SecurityRobot Passive', -1, True, {'maxhp' : 1.3}, can_be_removed_by_skill=False))
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


class Emperor(character.Character):
    def __init__(self, name, lvl, exp=0, equip=None, image=None):
        super().__init__(name, lvl, exp, equip, image)
        self.original_name = "Emperor"
        self.skill1_description = "Attack closest enemy with 280% atk 2 times, for each alive ally, damage increased by 20%."
        self.skill2_description = "Attack closest enemy with 560% atk, for each alive ally, damage increased by 20%."
        self.skill3_description = "If has not taken damage for 5 turns, apply Pride to all allies for 6 turns at end of turn. Pride: increase atk by 30% and spd by 30%."
        self.skill1_cooldown_max = 5
        self.skill2_cooldown_max = 5
        self.is_boss = True

    def skill_tooltip(self):
        return f"Skill 1 : {self.skill1_description}\nCooldown : {self.skill1_cooldown} action(s)\n\nSkill 2 : {self.skill2_description}\nCooldown : {self.skill2_cooldown} action(s)\n\nSkill 3 : {self.skill3_description}\n"

    def skill1_logic(self):
        def damage_amplify(self, target, final_damage):
            final_damage *= 1 + 0.2 * len(self.ally)
            return final_damage
        damage_dealt = self.attack(multiplier=2.8, repeat=2, func_damage_step=damage_amplify, target_kw1="enemy_in_front")
        return damage_dealt

    def skill2_logic(self):
        def damage_amplify(self, target, final_damage):
            final_damage *= 1 + 0.2 * len(self.ally)
            return final_damage
        damage_dealt = self.attack(multiplier=5.6, repeat=1, func_damage_step=damage_amplify, target_kw1="enemy_in_front")
        return damage_dealt

    def skill3(self):
        pass

    def status_effects_at_end_of_turn(self):
        if self.get_num_of_turns_not_taken_damage() >= 5:
            for ally in self.ally:
                if not ally.has_effect_that_named('Emperor Pride'):
                    ally.apply_effect(StatsEffect('Emperor Pride', 6, True, {'atk' : 1.3, 'spd' : 1.3}))
        super().status_effects_at_end_of_turn()


# ====================================
# End of Stealth
# ====================================
# Attack
# ====================================
    

class Tanuki(character.Character):
    def __init__(self, name, lvl, exp=0, equip=None, image=None):
        super().__init__(name, lvl, exp, equip, image)
        self.original_name = "Tanuki"
        self.skill1_description = "Boost atk for two allies with highest atk by 60% for 8 turns."
        self.skill2_description = "Attack closest enemy with 1 damage, increase self evasion by 50% for 6 turns."
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
        self.apply_effect(StatsEffect('Tanuki Evasion', 6, True, {'eva' : 0.5}))
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
        self.skill3_description = "Increase atk by 15%. At start of battle, increase atk by 15% for 15 turns for self and neighboring allies."
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
        self.apply_effect(StatsEffect('Werewolf Passive', -1, True, {'atk' : 1.15}, can_be_removed_by_skill=False))
        self_and_neighbors = self.get_neighbor_allies_including_self()
        for ally in self_and_neighbors:
            ally.apply_effect(StatsEffect('Strong', 15, True, {'atk' : 1.15}))


class Kunoichi(character.Character):
    def __init__(self, name, lvl, exp=0, equip=None, image=None):
        super().__init__(name, lvl, exp, equip, image)
        self.original_name = "Kunoichi"
        self.skill1_description = "For 4 turns, increase accuracy by 20%, attack 3 closest enemies with 240% atk 2 times." \
        " For 8 turns, target has 15% decreased atk."
        self.skill2_description = "For 4 turns, increase atk by 20%, attack closest enemy with 450% atk." \
        " For 8 turns, target has 30% decreased atk."
        self.skill3_description = "Self and neighboring allies have increased penetration by 20%."
        self.skill1_cooldown_max = 5
        self.skill2_cooldown_max = 5
        self.is_boss = False

    def skill_tooltip(self):
        return f"Skill 1 : {self.skill1_description}\nCooldown : {self.skill1_cooldown} action(s)\n\nSkill 2 : {self.skill2_description}\nCooldown : {self.skill2_cooldown} action(s)\n\nSkill 3 : {self.skill3_description}\n"

    def skill1_logic(self):
        self.apply_effect(StatsEffect('Acc Up', 4, True, {'acc' : 0.2}))
        def atk_down(self, target):
            target.apply_effect(StatsEffect('Atk Down', 8, False, {'atk' : 0.85}))
        damage_dealt = self.attack(multiplier=2.4, repeat_seq=2, func_after_dmg=atk_down, target_kw1="n_enemy_in_front", target_kw2="3")
        return damage_dealt

    def skill2_logic(self):
        self.apply_effect(StatsEffect('Atk Up', 4, True, {'atk' : 1.2}))
        def atk_down(self, target):
            target.apply_effect(StatsEffect('Atk Down', 8, False, {'atk' : 0.70}))
        damage_dealt = self.attack(multiplier=4.5, repeat=1, func_after_dmg=atk_down, target_kw1="enemy_in_front")
        return damage_dealt

    def skill3(self):
        pass

    def battle_entry_effects(self):
        self_and_neighbors = self.get_neighbor_allies_including_self()
        for ally in self_and_neighbors:
            ally.apply_effect(StatsEffect('Sharp', -1, True, {'penetration' : 0.2}, can_be_removed_by_skill=False))


class ArabianSoldier(character.Character):
    def __init__(self, name, lvl, exp=0, equip=None, image=None):
        super().__init__(name, lvl, exp, equip, image)
        self.original_name = "ArabianSoldier"
        self.skill1_description = "For 10 turns, increase atk by 20%, focus attack on enemy with highest atk with 300% atk 2 times."
        self.skill2_description = "For 10 turns, increase def by 20%, recover hp by 30% of maxhp."
        self.skill3_description = "At start of battle, increase atk and def by 20% for 15 turns for self and neighboring allies."
        self.skill1_cooldown_max = 4
        self.skill2_cooldown_max = 4
        self.is_boss = False

    def skill_tooltip(self):
        return f"Skill 1 : {self.skill1_description}\nCooldown : {self.skill1_cooldown} action(s)\n\nSkill 2 : {self.skill2_description}\nCooldown : {self.skill2_cooldown} action(s)\n\nSkill 3 : {self.skill3_description}\n"

    def skill1_logic(self):
        self.apply_effect(StatsEffect('Atk Up', 10, True, {'atk' : 1.20}))
        damage_dealt = self.attack(multiplier=3.0, repeat_seq=2, target_kw1="n_highest_attr", target_kw2="1", target_kw3="atk", target_kw4="enemy")
        return damage_dealt

    def skill2_logic(self):
        self.apply_effect(StatsEffect('Def Up', 10, True, {'defense' : 1.20}))
        self.heal_hp(self.maxhp * 0.3, self)
        return 0

    def skill3(self):
        pass

    def battle_entry_effects(self):
        self_and_neighbors = self.get_neighbor_allies_including_self()
        for ally in self_and_neighbors:
            ally.apply_effect(StatsEffect('Atk and Def Up', 15, True, {'atk' : 1.20, 'defense' : 1.20}))


# ====================================
# End of Attack
# ====================================
# Regeneration & Revival
# ====================================
        
class Mushroom(character.Character):
    def __init__(self, name, lvl, exp=0, equip=None, image=None):
        super().__init__(name, lvl, exp, equip, image)
        self.original_name = "Mushroom"
        self.skill1_description = "Focus attack on 3 closest enemies with 240% atk 2 times."
        self.skill2_description = "Heal 30% hp of maxhp and increase defense by 20% for 7 turns."
        self.skill3_description = "After taking non zero damage and hp is lower than maxhp, recover hp by 5% of maxhp."
        self.skill1_cooldown_max = 5
        self.skill2_cooldown_max = 5
        self.is_boss = False

    def skill_tooltip(self):
        return f"Skill 1 : {self.skill1_description}\nCooldown : {self.skill1_cooldown} action(s)\n\nSkill 2 : {self.skill2_description}\nCooldown : {self.skill2_cooldown} action(s)\n\nSkill 3 : {self.skill3_description}\n"

    def skill1_logic(self):
        damage_dealt = self.attack(multiplier=2.4, repeat_seq=2, target_kw1="n_enemy_in_front", target_kw2="3")
        return damage_dealt

    def skill2_logic(self):
        self.heal_hp(self.maxhp * 0.3, self)
        self.apply_effect(StatsEffect('Mushroom Buff', 7, True, {'defense' : 1.2}))
        return 0

    def skill3(self):
        pass

    def take_damage_aftermath(self, damage, attacker):
        if damage > 0 and self.is_alive():
            self.heal_hp(self.maxhp * 0.05, self)


class Vampire(character.Character):
    def __init__(self, name, lvl, exp=0, equip=None, image=None):
        super().__init__(name, lvl, exp, equip, image)
        self.original_name = "Vampire"
        self.skill1_description = "Focus attack on 3 closest enemies with 300% atk 2 times, recover hp by 30% of damage dealt."
        self.skill2_description = "Pay 20% of current hp, attack 3 closest enemies with 100% of the amount of hp paid as fixed damage. This skill has no effect if hp is lower than 20% of maxhp. Paying hp counts as taking status damage."
        self.skill3_description = "Every turn, recover hp by 5% of maxhp."
        self.skill1_cooldown_max = 5
        self.skill2_cooldown_max = 5
        self.is_boss = True

    def skill_tooltip(self):
        return f"Skill 1 : {self.skill1_description}\nCooldown : {self.skill1_cooldown} action(s)\n\nSkill 2 : {self.skill2_description}\nCooldown : {self.skill2_cooldown} action(s)\n\nSkill 3 : {self.skill3_description}\n"

    def skill1_logic(self):
        damage_dealt = self.attack(multiplier=3.0, repeat_seq=2, target_kw1="n_enemy_in_front", target_kw2="3")
        if self.is_alive():
            self.heal_hp(damage_dealt * 0.3, self)
        return damage_dealt

    def skill2_logic(self):
        if self.hp < self.maxhp * 0.2:
            global_vars.turn_info_string += f"{self.name} tried to use skill 2 but has no effect.\n"
            return 0
        else:
            value = self.pay_hp(self.hp * 0.2)
            if self.is_alive():
                damage_dealt = self.attack(target_kw1="n_enemy_in_front", target_kw2="3", force_dmg=value)
            return damage_dealt

    def skill3(self):
        pass

    def battle_entry_effects(self):
        heal = ContinuousHealEffect('Vampire Passive', -1, True, 0.05, True)
        heal.can_be_removed_by_skill = False
        self.apply_effect(heal)


class Lich(character.Character):
    def __init__(self, name, lvl, exp=0, equip=None, image=None):
        super().__init__(name, lvl, exp, equip, image)
        self.original_name = "Lich"
        self.skill1_description = "Attack closest enemy with 400% atk 3 times."
        self.skill2_description = "Attack closest enemy with 900% atk, reduce target heal efficiency by 50% for 5 turns."
        self.skill3_description = "Gain immunity to CC effect as long as having Undead effect. When defeated, revive with 100% hp next turn."
        self.skill1_cooldown_max = 4
        self.skill2_cooldown_max = 4
        self.is_boss = True

    def skill_tooltip(self):
        return f"Skill 1 : {self.skill1_description}\nCooldown : {self.skill1_cooldown} action(s)\n\nSkill 2 : {self.skill2_description}\nCooldown : {self.skill2_cooldown} action(s)\n\nSkill 3 : {self.skill3_description}\n"

    def skill1_logic(self):
        damage_dealt = self.attack(multiplier=4.0, repeat=3, target_kw1="enemy_in_front")
        return damage_dealt

    def skill2_logic(self):
        def heal_efficiency_down(self, target):
            target.apply_effect(StatsEffect('Heal Efficiency Down', 5, False, {'heal_efficiency' : -0.5}))
        damage_dealt = self.attack(multiplier=9.0, repeat=1, func_after_dmg=heal_efficiency_down, target_kw1="enemy_in_front")
        return damage_dealt

    def skill3(self):
        pass

    def battle_entry_effects(self):
        reborn = RebornEffect('Undead', -1, True, 1.0, True)
        reborn.can_be_removed_by_skill = False
        self.apply_effect(reborn)


class Cleric(character.Character):
    def __init__(self, name, lvl, exp=0, equip=None, image=None):
        super().__init__(name, lvl, exp, equip, image)
        self.original_name = "Cleric"
        self.skill1_description = "Heal 3 allies with lowest hp by 600% atk."
        self.skill2_description = "Target 3 allies with lowest hp, apply a shield that absorbs up to 300% atk damage for 6 turns."
        self.skill3_description = "Heal efficiency increased by 30%."
        self.skill1_cooldown_max = 4
        self.skill2_cooldown_max = 4
        self.is_boss = False

    def skill_tooltip(self):
        return f"Skill 1 : {self.skill1_description}\nCooldown : {self.skill1_cooldown} action(s)\n\nSkill 2 : {self.skill2_description}\nCooldown : {self.skill2_cooldown} action(s)\n\nSkill 3 : {self.skill3_description}\n"

    def skill1_logic(self):
        targets = list(self.target_selection(keyword="n_lowest_hp_percentage_ally", keyword2="3"))
        for target in targets:
            target.heal_hp(self.atk * 6, self)

    def skill2_logic(self):
        targets = list(self.target_selection(keyword="n_lowest_hp_percentage_ally", keyword2="3"))
        for target in targets:
            target.apply_effect(AbsorptionShield('Cleric Shield', 6, True, 3 * self.atk, self))

    def skill3(self):
        pass

    def battle_entry_effects(self):
        self.apply_effect(StatsEffect('Cleric Passive', -1, True, {'heal_efficiency' : 0.3}, can_be_removed_by_skill=False))



# ====================================
# End of Regeneration & Revival
# ====================================
# Benefit from attribute condition
# ====================================
        

class Infantry(character.Character):
    def __init__(self, name, lvl, exp=0, equip=None, image=None):
        super().__init__(name, lvl, exp, equip, image)
        self.original_name = "Infantry"
        self.skill1_description = "Attack closest enemy with 280% atk 3 times, 30% chance to inflict Atk Down for 6 turns, atk is decreased by 30%."
        self.skill2_description = "Attack closest enemy with 280% atk 4 times."
        self.skill3_description = "Skill damage increased by 50% if target atk is lower than self."
        self.skill1_cooldown_max = 5
        self.skill2_cooldown_max = 5
        self.is_boss = False

    def skill_tooltip(self):
        return f"Skill 1 : {self.skill1_description}\nCooldown : {self.skill1_cooldown} action(s)\n\nSkill 2 : {self.skill2_description}\nCooldown : {self.skill2_cooldown} action(s)\n\nSkill 3 : {self.skill3_description}\n"

    def skill1_logic(self):
        def atk_down(self, target):
            if random.random() < 0.3:
                target.apply_effect(StatsEffect('Atk Down', 6, False, {'atk' : 0.7}))
        def high_atk(self, target, final_damage):
            if target.atk < self.atk:
                global_vars.turn_info_string += f"{self.name} deals additional 50% damage to {target.name}.\n"
                final_damage *= 1.5
            return final_damage
        damage_dealt = self.attack(multiplier=2.8, repeat=3, func_after_dmg=atk_down, func_damage_step=high_atk, target_kw1="enemy_in_front")
        return damage_dealt

    def skill2_logic(self):
        def high_atk(self, target, final_damage):
            if target.atk < self.atk:
                global_vars.turn_info_string += f"{self.name} deals additional 50% damage to {target.name}.\n"
                final_damage *= 1.5
            return final_damage
        damage_dealt = self.attack(multiplier=2.8, repeat=4, target_kw1="enemy_in_front", func_damage_step=high_atk)
        return damage_dealt

    def skill3(self):
        pass


class Biobird(character.Character):
    def __init__(self, name, lvl, exp=0, equip=None, image=None):
        super().__init__(name, lvl, exp, equip, image)
        self.original_name = "Biobird"
        self.skill1_description = "Attack closest enemy with 400% atk 2 times, 35% chance to inflict Def Down for 6 turns, def is decreased by 30%."
        self.skill2_description = "Attack closest enemy with 400% atk 2 times. If hp is below 20%, for 10 turns," \
        " Increase maxhp by 40% and recover 8% of maxhp each turn."
        self.skill3_description = "Skill damage increased by 100% if hp is below 20%."
        self.skill1_cooldown_max = 5
        self.skill2_cooldown_max = 5
        self.is_boss = False

    def skill_tooltip(self):
        return f"Skill 1 : {self.skill1_description}\nCooldown : {self.skill1_cooldown} action(s)\n\nSkill 2 : {self.skill2_description}\nCooldown : {self.skill2_cooldown} action(s)\n\nSkill 3 : {self.skill3_description}\n"

    def skill1_logic(self):
        def def_down(self, target):
            if random.random() < 0.35:
                target.apply_effect(StatsEffect('Def Down', 6, False, {'defense' : 0.7}))
        def low_hp(self, target, final_damage):
            if self.hp < self.maxhp * 0.2:
                global_vars.turn_info_string += f"{self.name} deals additional 100% damage to {target.name}.\n"
                final_damage *= 2.0
            return final_damage
        damage_dealt = self.attack(multiplier=4.0, repeat=2, func_after_dmg=def_down, func_damage_step=low_hp, target_kw1="enemy_in_front")
        return damage_dealt


    def skill2_logic(self):
        def low_hp(self, target, final_damage):
            if self.hp < self.maxhp * 0.2:
                global_vars.turn_info_string += f"{self.name} deals additional 100% damage to {target.name}.\n"
                final_damage *= 2.0
            return final_damage
        damage_dealt = self.attack(multiplier=4.0, repeat=2, target_kw1="enemy_in_front", func_damage_step=low_hp)
        if self.is_alive() and self.hp < self.maxhp * 0.2:
            self.apply_effect(StatsEffect('Maxhp Up', 10, True, {'maxhp' : 1.4}))
            self.apply_effect(ContinuousHealEffect('Regen', 10, True, 0.08, True))
        return damage_dealt

    def skill3(self):
        pass


# ====================================
# End of Benefit from attribute condition
# ====================================
# Support
# ====================================
        

class ArchAngel(character.Character):
    def __init__(self, name, lvl, exp=0, equip=None, image=None):
        super().__init__(name, lvl, exp, equip, image)
        self.original_name = "ArchAngel"
        self.skill1_description = "Heal all allies with 300% atk, for 9 turns, increase their atk by 40% and spd by 20%."
        self.skill2_description = "Target 1 ally with lowest hp, apply Absorption Shield that absorbs up to 600% atk damage for 8 turns."
        self.skill3_description = "Normal attack deals 400% damage and attack random enemy pair. At start of battle, apply Absorption Shield that absorbs up to 1500% atk damage."
        self.skill1_cooldown_max = 4
        self.skill2_cooldown_max = 4
        self.is_boss = True

    def skill_tooltip(self):
        return f"Skill 1 : {self.skill1_description}\nCooldown : {self.skill1_cooldown} action(s)\n\nSkill 2 : {self.skill2_description}\nCooldown : {self.skill2_cooldown} action(s)\n\nSkill 3 : {self.skill3_description}\n"

    def skill1_logic(self):
        self.update_ally_and_enemy()
        for target in self.ally:
            target.heal_hp(self.atk * 3.0, self)
            target.apply_effect(StatsEffect('ArchAngel Buff', 9, True, {'atk' : 1.4, 'spd' : 1.2}))

    def skill2_logic(self):
        target = next(self.target_selection(keyword="n_lowest_hp_percentage_ally", keyword2="1"))
        target.apply_effect(AbsorptionShield('Shield', 8, True, 6 * self.atk, False))

    def skill3(self):
        pass

    def normal_attack(self):
        self.attack(multiplier=4.0, repeat=1, target_kw1="random_enemy_pair")

    def battle_entry_effects(self):
        shield = AbsorptionShield('Shield', -1, True, 15 * self.atk, False)
        shield.can_be_removed_by_skill = False
        self.apply_effect(shield)


class Unicorn(character.Character):
    def __init__(self, name, lvl, exp=0, equip=None, image=None):
        super().__init__(name, lvl, exp, equip, image)
        self.original_name = "Unicorn"
        self.skill1_description = "Attack closest enemy with 555% atk and cause Deep Wound for 7 turns. Deep Wound: deals 100% atk status damage per turn, can be removed by healing."
        self.skill2_description = "Apply Absorption Shield for ally in the middle, shield absorbs up to 500% of self atk damage for 5 turns."
        self.skill3_description = "Increase hp by 30%."
        self.skill1_cooldown_max = 4
        self.skill2_cooldown_max = 4
        self.is_boss = False

    def skill_tooltip(self):
        return f"Skill 1 : {self.skill1_description}\nCooldown : {self.skill1_cooldown} action(s)\n\nSkill 2 : {self.skill2_description}\nCooldown : {self.skill2_cooldown} action(s)\n\nSkill 3 : {self.skill3_description}\n"

    def skill1_logic(self):
        def deep_wound(self, target):
            target.apply_effect(ContinuousDamageEffect('Deep Wound', 7, False, self.atk, self, remove_by_heal=True))
        damage_dealt = self.attack(multiplier=5.55, repeat=1, func_after_dmg=deep_wound, target_kw1="enemy_in_front")
        return damage_dealt

    def skill2_logic(self):
        t = next(self.target_selection(keyword="n_ally_in_middle", keyword2="1"))
        t.apply_effect(AbsorptionShield('Shield', 5, True, 5 * self.atk, False))

    def skill3(self):
        pass

    def battle_entry_effects(self):
        self.apply_effect(StatsEffect('Unicorn Passive', -1, True, {'maxhp' : 1.3}, can_be_removed_by_skill=False))
        self.hp = self.maxhp


class Zhenniao(character.Character):
    def __init__(self, name, lvl, exp=0, equip=None, image=None):
        super().__init__(name, lvl, exp, equip, image)
        self.original_name = "Zhenniao"
        self.skill1_description = "Ally in the middle gains 20% evasion and 20% spd for 10 turns and recover hp by 200% of self atk."
        self.skill2_description = "Ally in the middle gains 20% crit rate and 40% crit damage for 10 turns and recover hp by 100% of self atk."
        self.skill3_description = "Normal attack damage increased by 120% and attack 2 times. maxhp is increased by 30%."
        self.skill1_cooldown_max = 5
        self.skill2_cooldown_max = 5
        self.is_boss = False

    def skill_tooltip(self):
        return f"Skill 1 : {self.skill1_description}\nCooldown : {self.skill1_cooldown} action(s)\n\nSkill 2 : {self.skill2_description}\nCooldown : {self.skill2_cooldown} action(s)\n\nSkill 3 : {self.skill3_description}\n"

    def skill1_logic(self):
        t = next(self.target_selection(keyword="n_ally_in_middle", keyword2="1"))
        t.apply_effect(StatsEffect('Evasion Buff', 10, True, {'eva' : 0.20, 'spd' : 1.20}))
        t.heal_hp(self.atk * 2, self)
        return 0

    def skill2_logic(self):
        t = next(self.target_selection(keyword="n_ally_in_middle", keyword2="1"))
        t.apply_effect(StatsEffect('Crit Rate Buff', 10, True, {'crit' : 0.20, 'critdmg' : 0.40}))
        t.heal_hp(self.atk, self)
        return 0

    def skill3(self):
        pass

    def normal_attack(self):
        self.attack(multiplier=2.0, repeat=2, func_damage_step=lambda self, target, final_damage : final_damage * 2.2)

    def battle_entry_effects(self):
        self.apply_effect(StatsEffect('Zhenniao Passive', -1, True, {'maxhp' : 1.3}, can_be_removed_by_skill=False))
        self.hp = self.maxhp


class YataGarasu(character.Character):
    def __init__(self, name, lvl, exp=0, equip=None, image=None):
        super().__init__(name, lvl, exp, equip, image)
        self.original_name = "YataGarasu"
        self.skill1_description = "Ally in the middle gains 100% speed for 4 turns."
        self.skill2_description = "Apply Shield to 3 allies in the middle for 6 turns. Shield: the part of damage that exceeds 10% of maxhp is reduced by 50%."
        self.skill3_description = "Speed is increased by 10%. Normal attack inflict Burn for 5 turns. Burn: deals 150% atk status damage per turn."
        self.skill1_cooldown_max = 5
        self.skill2_cooldown_max = 5
        self.is_boss = False

    def skill_tooltip(self):
        return f"Skill 1 : {self.skill1_description}\nCooldown : {self.skill1_cooldown} action(s)\n\nSkill 2 : {self.skill2_description}\nCooldown : {self.skill2_cooldown} action(s)\n\nSkill 3 : {self.skill3_description}\n"

    def skill1_logic(self):
        t = next(self.target_selection(keyword="n_ally_in_middle", keyword2="1"))
        t.apply_effect(StatsEffect('Speed Buff', 4, True, {'spd' : 2.0}))
        return 0

    def skill2_logic(self):
        targets = list(self.target_selection(keyword="n_ally_in_middle", keyword2="3"))
        for target in targets:
            target.apply_effect(EffectShield2('Shield', 6, True, False, damage_reduction=0.5, shrink_rate=0, threshold=0.1))
        return 0

    def skill3(self):
        pass

    def normal_attack(self):
        def burn(self, target):
            target.apply_effect(ContinuousDamageEffect('Burn', 5, False, self.atk * 1.5, self))
        self.attack(multiplier=2.0, repeat=1, func_after_dmg=burn)

    def battle_entry_effects(self):
        self.apply_effect(StatsEffect('YataGarasu Passive', -1, True, {'spd' : 1.1}, can_be_removed_by_skill=False))


class Anubis(character.Character):
    def __init__(self, name, lvl, exp=0, equip=None, image=None):
        super().__init__(name, lvl, exp, equip, image)
        self.original_name = "Anubis"
        self.skill1_description = "Attack 3 closest enemies with 270% atk, increase atk and def for all allies by 20% for 10 turns."
        self.skill2_description = "Attack random enemies 3 times with 240% atk, increase penetration for all allies by 20% for 10 turns."
        self.skill3_description = "When taking non zero damage, 12% chance to increase def for all allies by 12% for 10 turns."
        self.skill1_cooldown_max = 4
        self.skill2_cooldown_max = 4
        self.is_boss = False

    def skill_tooltip(self):
        return f"Skill 1 : {self.skill1_description}\nCooldown : {self.skill1_cooldown} action(s)\n\nSkill 2 : {self.skill2_description}\nCooldown : {self.skill2_cooldown} action(s)\n\nSkill 3 : {self.skill3_description}\n"

    def skill1_logic(self):
        damage_dealt = self.attack(multiplier=2.7, repeat=1, target_kw1="n_enemy_in_front", target_kw2="3")
        for a in self.ally:
            a.apply_effect(StatsEffect('Anubis Buff', 10, True, {'atk' : 1.2, 'defense' : 1.2}))
        return damage_dealt

    def skill2_logic(self):
        damage_dealt = self.attack(multiplier=2.4, repeat=3)
        for a in self.ally:
            a.apply_effect(StatsEffect('Anubis Buff', 10, True, {'penetration' : 0.2}))
        return damage_dealt

    def skill3(self):
        pass

    def take_damage_aftermath(self, damage, attacker):
        if random.randint(1, 100) <= 12 and damage > 0:
            print(f"{self.name} triggers skill 3.")
            for a in self.ally:
                a.apply_effect(StatsEffect('Anubis Buff', 10, True, {'defense' : 1.12}))


# ====================================
# End of Support
# ====================================
# Early Game Powercreep
# ====================================
        
class FootSoldier(character.Character):
    def __init__(self, name, lvl, exp=0, equip=None, image=None):
        super().__init__(name, lvl, exp, equip, image)
        self.original_name = "FootSoldier"
        self.skill1_description = "Attack closest enemy with 250% atk 3 times."
        self.skill2_description = "Attack closest enemy with 550% atk, 80% chance to Cripple for 7 turns,"
        " Cripple: atk decreased by 10%, spd decreased by 20%, evasion decreased by 30%."
        self.skill3_description = "Increase atk and spd by 100%, every turn pass, effect decreases by 4% until 35th turn."
        self.skill1_cooldown_max = 5
        self.skill2_cooldown_max = 5
        self.is_boss = False

    def skill_tooltip(self):
        return f"Skill 1 : {self.skill1_description}\nCooldown : {self.skill1_cooldown} action(s)\n\nSkill 2 : {self.skill2_description}\nCooldown : {self.skill2_cooldown} action(s)\n\nSkill 3 : {self.skill3_description}\n"

    def skill1_logic(self):
        damage_dealt = self.attack(multiplier=2.5, repeat=3, target_kw1="enemy_in_front")
        return damage_dealt

    def skill2_logic(self):
        def cripple(self, target):
            if random.random() < 0.8:
                target.apply_effect(StatsEffect('Cripple', 7, False, {'atk' : 0.9, 'spd' : 0.8, 'eva' : -0.3}))
        damage_dealt = self.attack(multiplier=5.5, repeat=1, func_after_dmg=cripple, target_kw1="enemy_in_front")
        return damage_dealt

    def skill3(self):
        pass

    def battle_entry_effects(self):
        def condition(self) -> bool:
            return True
        def decrease_func() -> dict:
            value = min(35, self.battle_turns)
            new_dict = {'atk' : 2.0 - 0.04 * value, 'spd' : 2.0 - 0.04 * value}
            return new_dict
        self.apply_effect(StatsEffect('FootSoldier Passive', -1, True, {'atk' : 2.0, 'spd' : 2.0}, use_active_flag=False, 
                                      stats_dict_function=decrease_func, condition=condition, can_be_removed_by_skill=False))


class Daji(character.Character):
    def __init__(self, name, lvl, exp=0, equip=None, image=None):
        super().__init__(name, lvl, exp, equip, image)
        self.original_name = "Daji"
        self.skill1_description = "Increase atk by 111%, accuracy by 10%, penetration by 10% for 8 turns for all allies." \
        " Every time this skill is used, atk bonus is decreased by 33%."
        self.skill2_description = "All allies are healed by 200% of atk, apply a shield that absorbs up to 300% of atk damage for 8 turns." \
        " Every time this skill is used, shield amount is decreased by 100% of atk."
        self.skill3_description = "At end of turn, if the alive allies are more than the alive enemies, apply Pride to all allies for 8 turns." \
        " Pride: increase atk by 45%. The same effect cannot be applied more than once."
        self.skill1_cooldown_max = 4
        self.skill2_cooldown_max = 4
        self.is_boss = True
        self.current_atk_bonus = 1.0
        self.current_shield_bonus = 3

    def skill_tooltip(self):
        return f"Skill 1 : {self.skill1_description}\nCooldown : {self.skill1_cooldown} action(s)\n\nSkill 2 : {self.skill2_description}\nCooldown : {self.skill2_cooldown} action(s)\n\nSkill 3 : {self.skill3_description}\n"

    def clear_others(self):
        self.current_atk_bonus = 1.11
        self.current_shield_bonus = 3

    def get_atk_bonus(self):
        return max(0, self.current_atk_bonus)

    def get_shield_bonus(self):
        return max(0, self.current_shield_bonus)

    def skill1_logic(self):
        if self.get_atk_bonus() > 0:
            for a in self.ally:
                a.apply_effect(StatsEffect('Atk Up', 8, True, {'atk' : 1.0 + self.get_atk_bonus(), 'acc' : 0.1, 'penetration' : 0.1}))
            self.current_atk_bonus -= 0.33
        else:
            for a in self.ally:
                a.apply_effect(StatsEffect('Atk Up', 8, True, {'acc' : 0.1, 'penetration' : 0.1}))
        return 0

    def skill2_logic(self):
        if self.get_shield_bonus() > 0:
            def fun_after_heal(self, target, healing, overhealing):
                target.apply_effect(AbsorptionShield('Shield', 8, True, self.get_shield_bonus() * self.atk, False))
            self.heal("n_random_ally", "5", value=self.atk * 2, func_after_each_heal=fun_after_heal)
            self.current_shield_bonus -= 1
        else:
            self.heal("n_random_ally", "5", value=self.atk * 2)
        return 0

    def skill3(self):
        pass

    def status_effects_at_end_of_turn(self):
        self.update_ally_and_enemy()
        if len(self.ally) > len(self.enemy):
            for ally in self.ally:
                if not ally.has_effect_that_named('Daji Pride'):
                    ally.apply_effect(StatsEffect('Daji Pride', 8, True, {'atk' : 1.45}))
        super().status_effects_at_end_of_turn()



# ====================================
# End of Early Game Powercreep
# ====================================
# Late Game Powercreep
# ====================================
        





# ====================================
# End of Late Game Powercreep
# ====================================