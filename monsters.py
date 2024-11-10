from itertools import zip_longest
import random
from effect import *
import character
import global_vars


# NOTE: use cw.py to estimate winrate
# Normal monsters should have winrate around 40% - 50%
# Boss monsters should have winrate around 50% - 70%


class Monster(character.Character):
    def __init__(self, name, lvl, exp=0, equip=None, image=None):
        super().__init__(name, lvl, exp, equip, image)
        self.is_boss = False
        self.is_monster = True

    def skill_tooltip(self):
        return f"Skill 1 : {self.skill1_description}\nCooldown : {self.skill1_cooldown} action(s)\n\nSkill 2 : {self.skill2_description}\nCooldown : {self.skill2_cooldown} action(s)\n\nSkill 3 : {self.skill3_description}\n"

    def skill_tooltip_jp(self):
        try:
            s = f"スキル 1 : {self.skill1_description_jp}\nクールダウン : {self.skill1_cooldown} 行動\n\nスキル 2 : {self.skill2_description_jp}\nクールダウン : {self.skill2_cooldown} 行動\n\nスキル 3 : {self.skill3_description_jp}\n"
        except AttributeError:
            s = f"スキル 1 : {self.skill1_description}\nクールダウン : {self.skill1_cooldown} 行動\n\nスキル 2 : {self.skill2_description}\nクールダウン : {self.skill2_cooldown} 行動\n\nスキル 3 : {self.skill3_description}\n"
        return s


# ====================================
# Heavy Attack
# ====================================

class Panda(Monster):
    def __init__(self, name, lvl, exp=0, equip=None, image=None):
        super().__init__(name, lvl, exp, equip, image)
        self.original_name = "Panda"
        self.skill1_description = "Attack 1 closest enemy with 800% atk."
        self.skill2_description = "Attack 1 closest enemy with 700% atk and 70% chance to stun the target for 10 turns."
        self.skill3_description = "Increase maxhp by 50%."
        self.skill1_description_jp = "最も近い敵に攻撃力800%のダメージを与える。"
        self.skill2_description_jp = "最も近い敵に攻撃力700%のダメージを与え、確率70%で10ターンの間スタンさせる。"
        self.skill3_description_jp = "最大HPを50%増加させる。"
        self.skill1_cooldown_max = 5
        self.skill2_cooldown_max = 5
        self.is_boss = False
        self.monster_role = "Heavy Attack"

    

    def skill1_logic(self):
        damage_dealt = self.attack(multiplier=8.0, repeat=1, target_kw1="enemy_in_front")
        return damage_dealt

    def skill2_logic(self):
        def stun_effect(self, target):
            dice = random.randint(1, 100)
            if dice <= 70:
                target.apply_effect(StunEffect('Stun', duration=10, is_buff=False))
        damage_dealt = self.attack(multiplier=7.0, repeat=1, func_after_dmg=stun_effect, target_kw1="enemy_in_front")
        return damage_dealt
        
    def skill3(self):
        pass

    def battle_entry_effects(self):
        self.apply_effect(StatsEffect('Fat', -1, True, {'maxhp' : 1.5}, can_be_removed_by_skill=False))
        self.hp = self.maxhp


class Mimic(Monster):
    def __init__(self, name, lvl, exp=0, equip=None, image=None):
        super().__init__(name, lvl, exp, equip, image)
        self.original_name = "Mimic"
        self.skill1_description = "Attack 1 closest enemy with 1000% atk."
        self.skill2_description = "Attack 1 closest enemy with 1000% atk."
        self.skill3_description = "Skill attack have 10% chance to inflict Stun for 10 turns."
        self.skill1_description_jp = "最も近い敵に攻撃力1000%のダメージを与える。"
        self.skill2_description_jp = "最も近い敵に攻撃力1000%のダメージを与える。"
        self.skill3_description_jp = "スキル攻撃に10%の確率で10ターンの間スタンさせる。"
        self.skill1_cooldown_max = 4
        self.skill2_cooldown_max = 4
        self.is_boss = False
        self.monster_role = "Heavy Attack"

    

    def skill1_logic(self):
        def stun_effect(self, target):
            dice = random.randint(1, 100)
            if dice <= 10:
                target.apply_effect(StunEffect('Stun', duration=10, is_buff=False))
        damage_dealt = self.attack(multiplier=10.0, repeat=1, func_after_dmg=stun_effect, target_kw1="enemy_in_front")
        return damage_dealt

    def skill2_logic(self):
        def stun_effect(self, target):
            dice = random.randint(1, 100)
            if dice <= 10:
                target.apply_effect(StunEffect('Stun', duration=10, is_buff=False))
        damage_dealt = self.attack(multiplier=10.0, repeat=1, func_after_dmg=stun_effect, target_kw1="enemy_in_front")
        return damage_dealt
        
    def skill3(self):
        pass


class MoHawk(Monster):
    def __init__(self, name, lvl, exp=0, equip=None, image=None):
        super().__init__(name, lvl, exp, equip, image)
        self.original_name = "MoHawk"
        self.skill1_description = "Attack 1 closest enemy with 680% atk and inflict bleed for 20 turns. Bleed: take 40% of applier atk as status damage each turn."
        self.skill2_description = "Attack 1 closest enemy with 680% atk and inflict bleed for 20 turns."
        self.skill3_description = "Increase atk by 20%."
        self.skill1_description_jp = "最も近い敵に攻撃力680%のダメージを与え、20ターンの間出血状態にする。出血:毎ターン、付与者の攻撃力の40%を状態ダメージとして受ける。"
        self.skill2_description_jp = "最も近い敵に攻撃力680%のダメージを与え、20ターンの間出血状態にする。"
        self.skill3_description_jp = "攻撃力を20%増加する。"
        self.skill1_cooldown_max = 5
        self.skill2_cooldown_max = 5
        self.is_boss = False
        self.monster_role = "Heavy Attack"

    

    def skill1_logic(self):
        def bleed_effect(self, target):
            target.apply_effect(ContinuousDamageEffect('Bleed', duration=20, is_buff=False, value=0.4 * self.atk, imposter=self))
        damage_dealt = self.attack(multiplier=6.8, repeat=1, func_after_dmg=bleed_effect, target_kw1="enemy_in_front")
        return damage_dealt

    def skill2_logic(self):
        def bleed_effect(self, target):
            target.apply_effect(ContinuousDamageEffect('Bleed', duration=20, is_buff=False, value=0.4 * self.atk, imposter=self))
        damage_dealt = self.attack(multiplier=6.8, repeat=1, func_after_dmg=bleed_effect, target_kw1="enemy_in_front")
        return damage_dealt
        
    def skill3(self):
        pass

    def battle_entry_effects(self):
        self.apply_effect(StatsEffect('MoHawk Passive', -1, True, {'atk' : 1.2}, can_be_removed_by_skill=False))


class Earth(Monster):
    def __init__(self, name, lvl, exp=0, equip=None, image=None):
        super().__init__(name, lvl, exp, equip, image)
        self.original_name = "Earth"
        self.skill1_description = "Attack all enemies with 240% atk, 30% chance to inflict Stun for 10 turns."
        self.skill2_description = "Attack 1 closest enemy with 700% atk, 50% chance to inflict Stun for 10 turns."
        self.skill3_description = "hp is increased by 100%."
        self.skill1_description_jp = "全ての敵に攻撃力240%のダメージを与え、確率30%で10ターンの間スタンさせる。"
        self.skill2_description_jp = "最も近い敵に攻撃力700%のダメージを与え、確率50%で10ターンの間スタンさせる。"
        self.skill3_description_jp = "最大HPを100%増加させる。"
        self.skill1_cooldown_max = 5
        self.skill2_cooldown_max = 5
        self.is_boss = False
        self.monster_role = "Heavy Attack"

    

    def skill1_logic(self):
        def stun_effect(self, target):
            dice = random.randint(1, 100)
            if dice <= 30:
                target.apply_effect(StunEffect('Stun', duration=10, is_buff=False))
        damage_dealt = self.attack(multiplier=2.4, repeat=1, func_after_dmg=stun_effect, target_kw1="n_random_enemy", target_kw2="5")
        return damage_dealt


    def skill2_logic(self):
        def stun_effect(self, target):
            dice = random.randint(1, 100)
            if dice <= 50:
                target.apply_effect(StunEffect('Stun', duration=10, is_buff=False))
        damage_dealt = self.attack(multiplier=7.0, repeat=1, func_after_dmg=stun_effect, target_kw1="enemy_in_front")
        return damage_dealt

    def skill3(self):
        pass

    def battle_entry_effects(self):
        self.apply_effect(StatsEffect('Earth Passive', -1, True, {'maxhp' : 2.0}, can_be_removed_by_skill=False))
        self.hp = self.maxhp


class Golem(Monster):
    def __init__(self, name, lvl, exp=0, equip=None, image=None):
        super().__init__(name, lvl, exp, equip, image)
        self.original_name = "Golem"
        self.skill1_description = "Attack all enemies with 500% atk."
        self.skill2_description = "Attack 1 closest enemy with 700% atk. Damage increased by target's hp percentage. Max bonus damage: 100%."
        self.skill3_description = "Increase hp by 200%."
        self.skill1_description_jp = "全ての敵に攻撃力500%のダメージを与える。"
        self.skill2_description_jp = "最も近い敵に攻撃力700%のダメージを与える。ダメージは対象のHP割合によって増加する。最大ボーナスダメージ:100%。"
        self.skill3_description_jp = "最大HPを200%増加させる。"
        self.skill1_cooldown_max = 5
        self.skill2_cooldown_max = 4
        self.is_boss = True
        self.monster_role = "Heavy Attack"

    

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


class Yeti(Monster):
    def __init__(self, name, lvl, exp=0, equip=None, image=None):
        super().__init__(name, lvl, exp, equip, image)
        self.original_name = "Yeti"
        self.skill1_description = "Attack 1 closest enemy with 800% atk."
        self.skill2_description = "Attack 1 closest enemy with 800% atk."
        self.skill3_description = "Increase hp by 200%. After taking down an enemy with skill, recover hp by 50% of maxhp, for 20 turns," \
        " increase atk by 30% and reduce damage taken by 30%."
        self.skill1_description_jp = "最も近い敵に攻撃力800%のダメージを与える。"
        self.skill2_description_jp = "最も近い敵に攻撃力800%のダメージを与える。"
        self.skill3_description_jp = "最大HPを200%増加させる。スキルで敵を倒した後、最大HPの50%を回復し、20ターンの間攻撃力を30%増加し、受けるダメージを30%減少させる。"
        self.skill1_cooldown_max = 5
        self.skill2_cooldown_max = 5
        self.is_boss = True
        self.monster_role = "Heavy Attack"

    

    def skill1_logic(self):
        def recoverhp(self, target):
            if target.is_dead():
                self.heal_hp(self.maxhp * 0.5, self)
                self.apply_effect(StatsEffect('Full', 20, True, {'atk' : 1.3, 'final_damage_taken_multipler' : -0.3}))
        damage_dealt = self.attack(multiplier=8.0, repeat=1, func_after_dmg=recoverhp, target_kw1="enemy_in_front")
        return damage_dealt

    def skill2_logic(self):
        def recoverhp(self, target):
            if target.is_dead():
                self.heal_hp(self.maxhp * 0.5, self)
                self.apply_effect(StatsEffect('Full', 20, True, {'atk' : 1.3, 'final_damage_taken_multipler' : -0.3}))
        damage_dealt = self.attack(multiplier=8.0, repeat=1, func_after_dmg=recoverhp, target_kw1="enemy_in_front")
        return damage_dealt
        
    def skill3(self):
        pass

    def battle_entry_effects(self):
        self.apply_effect(StatsEffect('Yeti Passive', -1, True, {'maxhp' : 3.0}, can_be_removed_by_skill=False))
        self.hp = self.maxhp


class Giant(Monster):
    """
    High damage is generally countered by EffectShield2, Chei, Bell
    """
    def __init__(self, name, lvl, exp=0, equip=None, image=None):
        super().__init__(name, lvl, exp, equip, image)
        self.original_name = "Giant"
        self.skill1_description = "Attack 1 closest enemy with 400% atk, damage is increased by 20% of current hp."
        self.skill2_description = "Attack all enemies with 400% atk, this attack cannot miss and bypasses protected effects."
        self.skill3_description = "Max hp is increased by 50%, atk is increased by 2% of base maxhp."
        self.skill1_description_jp = "最も近い敵に攻撃力400%のダメージを与え、ダメージは現在のHPの20%増加する。"
        self.skill2_description_jp = "全ての敵に攻撃力400%のダメージを与える。この攻撃は外れず、守護者からの保護効果を無視する。"
        self.skill3_description_jp = "最大HPを50%増加させ、攻撃力を基本最大HPの2%増加させる。"
        self.skill1_cooldown_max = 5
        self.skill2_cooldown_max = 5
        self.is_boss = True
        self.monster_role = "Heavy Attack"

    

    def skill1_logic(self):
        def amplify(self, target, final_damage):
            final_damage += 0.2 * self.hp
            return final_damage
        damage_dealt = self.attack(multiplier=4.0, repeat=1, func_damage_step=amplify, target_kw1="enemy_in_front")
        return damage_dealt

    def skill2_logic(self):
        damage_dealt = self.attack(multiplier=4.0, repeat=1, target_kw1="n_random_enemy", target_kw2="5", ignore_protected_effect=True, always_hit=True)
        return damage_dealt

    def skill3(self):
        pass

    def battle_entry_effects(self):
        self.apply_effect(StatsEffect('Giant Passive', -1, True, {'maxhp' : 1.5}, can_be_removed_by_skill=False, main_stats_additive_dict={'atk' : self.maxhp * 0.02}))
        self.hp = self.maxhp




# ====================================
# End of Heavy Attack
# ====================================
# Negative Status
# Negative status by those monsters are either lethal or high status damage or annoying
# ====================================

class Mummy(Monster):
    def __init__(self, name, lvl, exp=0, equip=None, image=None):
        super().__init__(name, lvl, exp, equip, image)
        self.original_name = "Mummy"
        self.skill1_description = "Attack 3 closest enemies with 300% atk."
        self.skill2_description = "Attack 5 enemies with 200% atk and 50% chance to inflict Curse for 45 turns. Curse: atk is reduced by 20%, unstackable."
        self.skill3_description = "When taking damage, 30% chance to inflict Curse on attacker for 45 turns. Curse: atk is reduced by 20%, unstackable."
        self.skill1_description_jp = "最も近い敵3体に攻撃力300%のダメージを与える。"
        self.skill2_description_jp = "全ての敵に攻撃力200%のダメージを与え、確率50%で45ターンの間呪いを付与。呪い:攻撃力が20%減少する。"
        self.skill3_description_jp = "ダメージを受けた時、30%の確率で攻撃者に45ターンの間呪いを付与。呪い:攻撃力が20%減少する。"
        self.skill1_cooldown_max = 5
        self.skill2_cooldown_max = 5
        self.is_boss = False

    

    def skill1_logic(self):
        damage_dealt = self.attack(target_kw1="n_enemy_in_front",target_kw2="3", multiplier=3.0, repeat=1)
        return damage_dealt

    def skill2_logic(self):
        def curse_effect(self, target):
            dice = random.randint(1, 100)
            if dice <= 50:
                curse = StatsEffect('Curse', duration=45, is_buff=False, stats_dict={'atk' : 0.8})
                curse.apply_rule = "stack"
                target.apply_effect(curse)
        damage_dealt = self.attack(target_kw1="n_random_enemy",target_kw2="5", multiplier=2.0, repeat=1, func_after_dmg=curse_effect)
        return damage_dealt
        
    def skill3(self):
        pass

    def take_damage_aftermath(self, damage, attacker):
        if random.randint(1, 100) <= 30:
            curse = StatsEffect('Curse', duration=45, is_buff=False, stats_dict={'atk' : 0.8})
            curse.apply_rule = "stack"
            attacker.apply_effect(curse)


class Pharaoh(Monster):
    """
    Countered by debuff removal
    """
    def __init__(self, name, lvl, exp=0, equip=None, image=None):
        super().__init__(name, lvl, exp, equip, image)
        self.original_name = "Pharaoh"
        self.skill1_description = "Attack 3 closest enemies with 320% atk. If target is cursed, damage is increased by 100%."
        self.skill2_description = "Attack 3 closest enemies with 320% atk and 80% chance to inflict Curse for 45 turns. If target is cursed, damage is increased by 100%. Curse: atk is reduced by 30%, unstackable."
        self.skill3_description = "hp, atk, def, spd is increased by 20%. When taking damage, 40% chance to inflict Curse on attacker for 45 turns. At the end of turn, if there is a cursed enemy, increase atk by 30% for 3 turns."
        self.skill1_description_jp = "最も近い敵3体に攻撃力320%のダメージを与える。対象が呪われている場合、ダメージが100%増加する。"
        self.skill2_description_jp = "最も近い敵3体に攻撃力320%のダメージを与え、確率80%で45ターンの間呪いを付与。対象が呪われている場合、ダメージが100%増加する。呪い:攻撃力が30%減少する。"
        self.skill3_description_jp = "最大HP、攻撃力、防御力、速度を20%増加させる。ダメージを受けた時、40%の確率で攻撃者に45ターンの間呪いをかける。ターン終了時、呪われた敵がいる場合、攻撃力を30%増加させる。"
        self.skill1_cooldown_max = 5
        self.skill2_cooldown_max = 3
        self.is_boss = True

    

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
                curse = StatsEffect('Curse', duration=45, is_buff=False, stats_dict={'atk' : 0.7})
                curse.apply_rule = "stack"
                target.apply_effect(curse)
        damage_dealt = self.attack(target_kw1="n_enemy_in_front",target_kw2="3", multiplier=3.2, repeat=1, func_damage_step=curse_amplify, func_after_dmg=curse_effect)
        return damage_dealt
        
    def skill3(self):
        pass

    def take_damage_aftermath(self, damage, attacker):
        if random.randint(1, 100) <= 40:
            curse = StatsEffect('Curse', duration=45, is_buff=False, stats_dict={'atk' : 0.7})
            curse.apply_rule = "stack"
            attacker.apply_effect(curse)

    def battle_entry_effects(self):
        self.apply_effect(StatsEffect('Strong', -1, True, {'maxhp' : 1.2, 'atk' : 1.2, 'defense' : 1.2, 'spd' : 1.2}, can_be_removed_by_skill=False))
        self.hp = self.maxhp
        passive = PharaohPassiveEffect('Passive Effect', -1, True, 1.3)
        passive.can_be_removed_by_skill = False
        self.apply_effect(passive)


class PoisonSlime(Monster):
    def __init__(self, name, lvl, exp=0, equip=None, image=None):
        super().__init__(name, lvl, exp, equip, image)
        self.original_name = "Poison_Slime"
        self.skill1_description = "Attack 5 enemies with 150% atk and 66% chance to inflict Poison for 20 turns. Poison: takes 2.5% of current hp status damage per turn."
        self.skill2_description = "Attack 5 enemies with 150% atk and 66% chance to inflict Poison for 20 turns. Poison: takes 2.5% of lost hp status damage per turn."
        self.skill3_description = "Reduce damage taken by 10%."
        self.skill1_description_jp = "全ての敵に攻撃力150%のダメージを与え、確率66%で20ターンの間毒を付与。毒:毎ターン、現在のHPの2.5%を状態ダメージとして受ける。"
        self.skill2_description_jp = "全ての敵に攻撃力150%のダメージを与え、確率66%で20ターンの間毒を付与。毒:毎ターン、失われたHPの2.5%を状態ダメージとして受ける。"
        self.skill3_description_jp = "受けるダメージを10%減少させる。"
        self.skill1_cooldown_max = 5
        self.skill2_cooldown_max = 5
        self.is_boss = False

    

    def skill1_logic(self):
        def poison_effect(self, target):
            dice = random.randint(1, 100)
            if dice <= 66:
                target.apply_effect(ContinuousDamageEffect_Poison('Poison', duration=20, is_buff=False, ratio=0.025, imposter=self, base="hp"))
        damage_dealt = self.attack(target_kw1="n_random_enemy",target_kw2="5", multiplier=1.5, repeat=1, func_after_dmg=poison_effect)
        return damage_dealt

    def skill2_logic(self):
        def poison_effect(self, target):
            dice = random.randint(1, 100)
            if dice <= 66:
                target.apply_effect(ContinuousDamageEffect_Poison('Poison', duration=20, is_buff=False, ratio=0.025, imposter=self, base="losthp"))
        damage_dealt = self.attack(target_kw1="n_random_enemy",target_kw2="5", multiplier=1.5, repeat=1, func_after_dmg=poison_effect)
        return damage_dealt
        
    def skill3(self):
        pass

    def battle_entry_effects(self):
        self.apply_effect(StatsEffect('Slimy', -1, True, {'final_damage_taken_multipler' : -0.1}, can_be_removed_by_skill=False))


class MadScientist(Monster):
    """
    Countered by debuff removal
    """
    def __init__(self, name, lvl, exp=0, equip=None, image=None):
        super().__init__(name, lvl, exp, equip, image)
        self.original_name = "MadScientist"
        self.skill1_description = "Attack all enemies with 250% atk and inflict plague for 20 turns with 60% chance each. Plague: at end of turn, 30% chance to apply the same effect to a neighbor ally, every turn, take 9% of lost hp as status damage."
        self.skill2_description = "Attack 3 closest enemies with 300% atk, if target is inflicted with plague, healing efficiency is reduced by 60% for 20 turns."
        self.skill3_description = "Normal attack have 30% chance to inflict plague for 20 turns and deals 40% more damage."
        self.skill1_description_jp = "全ての敵に攻撃力250%のダメージを与え、確率60%で20ターンの間疫病を付与。疫病:ターン終了時、30%の確率で隣接する味方を伝染し、毎ターン、失われたHPの9%を状態ダメージとして受ける。"
        self.skill2_description_jp = "最も近い敵3体に攻撃力300%のダメージを与え、対象が疫病効果がある場合、20ターンの間回復効率が60%減少する。"
        self.skill3_description_jp = "通常攻撃に30%の確率で20ターンの間疫病を付与、ダメージが40%増加する。"
        self.skill1_cooldown_max = 4
        self.skill2_cooldown_max = 4
        self.is_boss = True

    

    def skill1_logic(self):
        def plague_effect(self, target):
            dice = random.randint(1, 100)
            if dice <= 60:
                plague = ContinuousDamageEffect_Poison('Plague', duration=20, is_buff=False, ratio=0.09, imposter=self, base="losthp", is_plague=True, is_plague_transmission_chance=0.3)
                plague.additional_name = "MadScientist_Plague"
                target.apply_effect(plague)
        damage_dealt = self.attack(target_kw1="n_random_enemy", target_kw2="5", multiplier=2.5, repeat=1, func_after_dmg=plague_effect)
        return damage_dealt

    def skill2_logic(self):
        def plague_effect(self, target):
            if target.has_effect_that_named("Plague", "MadScientist_Plague", "ContinuousDamageEffect_Poison"):
                target.apply_effect(StatsEffect('Healing Down', duration=20, is_buff=False, stats_dict={'heal_efficiency' : -0.6}))
        damage_dealt = self.attack(target_kw1="n_enemy_in_front", target_kw2="3", multiplier=3.0, repeat=1, func_after_dmg=plague_effect)
        return damage_dealt
        
    def skill3(self):
        pass

    def normal_attack(self):
        def plague_effect(self, target):
            dice = random.randint(1, 100)
            if dice <= 30:
                plague = ContinuousDamageEffect_Poison('Plague', duration=20, is_buff=False, ratio=0.09, imposter=self, base="losthp", is_plague=True, is_plague_transmission_chance=0.3)
                plague.additional_name = "MadScientist_Plague"
                target.apply_effect(plague)
        def amplify(self, target, final_damage):
            final_damage *= 1.4
            return final_damage
        self.attack(func_after_dmg=plague_effect, func_damage_step=amplify)


class Ghost(Monster):
    def __init__(self, name, lvl, exp=0, equip=None, image=None):
        super().__init__(name, lvl, exp, equip, image)
        self.original_name = "Ghost"
        self.skill1_description = "Attack 5 enemies with 200% atk and apply Fear on targets for 30 turns. Apply chance is 100%, 80%, 60%, 30%, 0% for each enemy depending on how many allies the enemy has. The fewer allies the enemy has, the higher the chance."
        self.skill2_description = "Attack closest enemy 4 times with 200% atk. For 20 turns, all allies takes 40% less damage."
        self.skill3_description = "Normal attack will try target enemy with Fear first. damage increased by 100% if target has Fear. As long as you are alive, Fear effect gain the following effect: accuracy - 20%, atk - 20%."
        self.skill1_description_jp = "全ての敵に攻撃力200%のダメージを与え、確率100%、80%、60%、30%、0%で30ターンの間恐怖を付与。敵が味方の数によって確率が異なる。味方が少ないほど、確率が高くなる。"
        self.skill2_description_jp = "最も近い敵に4回攻撃力200%のダメージを与える。20ターンの間、全ての味方は40%のダメージを受ける。"
        self.skill3_description_jp = "通常攻撃は恐怖を付与された敵を狙う。対象が恐怖を持っている場合、ダメージが100%増加する。自分が生存している間、恐怖効果は以下の効果を得る:命中率-20%、攻撃力-20%。"
        self.skill1_cooldown_max = 5
        self.skill2_cooldown_max = 5
        self.is_boss = False
        self.fear_effect_dict = {"acc": -0.20, "atk": 0.8}

    

    def skill1_logic(self):
        chance_dict = dict(zip_longest(range(1, 11), [100, 80, 60, 30, 0], fillvalue=0))
        def fear_effect(self, target):
            dice = random.randint(1, 100)
            if dice <= chance_dict[len(self.enemy)]:
                target.apply_effect(FearEffect('Fear', duration=30, is_buff=False))
        damage_dealt = self.attack(target_kw1="n_random_enemy",target_kw2="5", multiplier=2.0, repeat=1, func_after_dmg=fear_effect)
        return damage_dealt

    def skill2_logic(self):
        damage_dealt = self.attack(target_kw1="enemy_in_front", multiplier=2.0, repeat=4)
        if self.is_alive():
            for a in self.ally:
                a.apply_effect(StatsEffect('Misty', duration=20, is_buff=True, stats_dict={'final_damage_taken_multipler' : -0.40}))
        return damage_dealt
        
    def skill3(self):
        pass

    def normal_attack(self):
        def fear_amplify(self, target, final_damage):
            if target.has_effect_that_named("Fear"):
                final_damage *= 2.0
            return final_damage
        self.attack(func_damage_step=fear_amplify, target_kw1="n_enemy_with_effect", target_kw2="1", target_kw3="Fear")


class Death(Monster):
    """
    Countered by debuff removal
    """
    def __init__(self, name, lvl, exp=0, equip=None, image=None):
        super().__init__(name, lvl, exp, equip, image)
        self.original_name = "Death"
        self.skill1_description = "Attack 5 enemies with 380% atk and apply Fear on targets for 30 turns. Apply chance is 100%, 80%, 60%, 30%, 0% for each enemy depending on how many allies the enemy has. The fewer allies the enemy has, the higher the chance."
        self.skill2_description = "Attack 3 enemies with lowest hp with 400% atk. If target hp is below 15%, execute target and recover for 20% hp of maxhp. If enemy survived the attack and has Fear, the enemy is confused for 10 turns."
        self.skill3_description = "Maxhp, defense and atk is increased by 20%. As long as you are alive, Fear effect gain the following effect: atk - 40%, accuracy - 40%, spd - 40%."
        self.skill1_description_jp = "全ての敵に攻撃力380%のダメージを与え、確率100%、80%、60%、30%、0%で30ターンの間恐怖を付与。敵が味方の数によって確率が異なる。味方が少ないほど、確率が高くなる。"
        self.skill2_description_jp = "最もHPが少ない敵3体に攻撃力400%のダメージを与える。対象のHPが15%以下の場合、対象を即死させ、最大HPの20%回復する。攻撃を生き延びた敵が恐怖を持っている場合、その敵を10ターンの間混乱させる。"
        self.skill3_description_jp = "最大HP、防御力、攻撃力を20%増加させる。自分が生存している間、恐怖効果は以下の効果を得る:攻撃力-40%、命中率-40%、速度-40%。"
        self.skill1_cooldown_max = 4
        self.skill2_cooldown_max = 4
        self.is_boss = True
        self.fear_effect_dict = {"acc": -0.40, "atk": 0.6, "spd": 0.6}

    

    def skill1_logic(self):
        chance_dict = dict(zip_longest(range(1, 11), [100, 80, 60, 30, 0], fillvalue=0))
        def fear_effect(self, target):
            dice = random.randint(1, 100)
            if dice <= chance_dict[len(self.enemy)]:
                target.apply_effect(FearEffect('Fear', duration=30, is_buff=False))
        damage_dealt = self.attack(target_kw1="n_random_enemy",target_kw2="5", multiplier=3.8, repeat=1, func_after_dmg=fear_effect)
        return damage_dealt


    def skill2_logic(self):
        def execute(self, target):
            if target.hp < target.maxhp * 0.15 and not target.is_dead():
                target.take_bypass_status_effect_damage(target.hp, self)
                if self.is_alive():
                    self.heal_hp(self.maxhp * 0.2, self)
            else:
                if target.has_effect_that_named("Fear"):
                    target.apply_effect(ConfuseEffect('Confuse', duration=10, is_buff=False))
        damage_dealt = self.attack(target_kw1="n_lowest_attr",target_kw2="3",target_kw3="hp",target_kw4="enemy", multiplier=4.0, repeat=1, func_after_dmg=execute)
        return damage_dealt

        
    def skill3(self):
        pass

    def battle_entry_effects(self):
        self.apply_effect(StatsEffect('Ugly', -1, True, {'maxhp' : 1.2, 'atk' : 1.2, 'defense' : 1.2}, can_be_removed_by_skill=False))
        self.hp = self.maxhp


class Gargoyle(Monster):
    def __init__(self, name, lvl, exp=0, equip=None, image=None):
        super().__init__(name, lvl, exp, equip, image)
        self.original_name = "Gargoyle"
        self.skill1_description = "Attack closest enemy 3 times with 210% atk."
        self.skill2_description = "Attack closest enemy 3 times with 210% atk."
        self.skill3_description = "Reduce damage taken by 10%. When taking damage, 60% chance to inflict Bleed and Poison on attacker for 20 turns. Bleed: take 12% of applier atk as status damage each turn. Poison: takes 1% of current hp as status damage per turn."
        self.skill1_description_jp = "最も近い敵に攻撃力210%のダメージを3回与える。"
        self.skill2_description_jp = "最も近い敵に攻撃力210%のダメージを3回与える。"
        self.skill3_description_jp = "受けるダメージを10%減少させる。ダメージを受けた時、60%の確率で攻撃者に20ターンの間出血と毒を付与。出血:攻撃力の12%を状態ダメージとして受ける。毒:毎ターン、現在のHPの1%を状態ダメージとして受ける。"
        self.skill1_cooldown_max = 5
        self.skill2_cooldown_max = 5
        self.is_boss = False

    

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
            attacker.apply_effect(ContinuousDamageEffect_Poison('Poison', duration=20, is_buff=False, ratio=0.01, imposter=self, base="hp"))
        if random.randint(1, 100) <= 60:
            attacker.apply_effect(ContinuousDamageEffect('Bleed', duration=20, is_buff=False, value=0.12 * self.atk, imposter=self))


class MachineGolem(Monster):
    """
    Countered by buff removal or burst damage that ensures early win
    """
    def __init__(self, name, lvl, exp=0, equip=None, image=None):
        super().__init__(name, lvl, exp, equip, image)
        self.original_name = "MachineGolem"
        self.skill1_description = "Install 2 timed bombs on all enemies. Bomb will explode after 32 turns, dealing 444% self atk as status damage."
        self.skill2_description = "Attack all enemies with 275% atk, 75% chance to inflict Burn for 20 turns. Burn deals 30% of self atk as status damage each turn."
        self.skill3_description = "Increase atk by 20%, maxhp by 20%, defense by 30%."
        self.skill1_description_jp = "全ての敵に時限爆弾2つを設置。32ターン後に爆発し、攻撃力444%の状態ダメージを与える。"
        self.skill2_description_jp = "全ての敵に攻撃力275%で攻撃し、確率75%で20ターンの間燃焼を付与。燃焼は攻撃力の30%を状態ダメージとして毎ターン受ける。"
        self.skill3_description_jp = "攻撃力を20%、最大HPを20%、防御力30%増加させる。"
        self.skill1_cooldown_max = 5
        self.skill2_cooldown_max = 5
        self.is_boss = True

    

    def skill1_logic(self):
        for e in self.enemy:
            e.apply_effect(TimedBombEffect('Timed Bomb', duration=32, is_buff=False, damage=4.44 * self.atk, imposter=self, cc_immunity=False))
            e.apply_effect(TimedBombEffect('Timed Bomb', duration=32, is_buff=False, damage=4.44 * self.atk, imposter=self, cc_immunity=False))
        return 0
    
    def skill2_logic(self):
        def burn_effect(self, target):
            dice = random.randint(1, 100)
            if dice <= 75:
                target.apply_effect(ContinuousDamageEffect('Burn', duration=20, is_buff=False, value=0.30 * self.atk, imposter=self))
        damage_dealt = self.attack(multiplier=2.75, repeat=1, func_after_dmg=burn_effect, target_kw1="n_random_enemy", target_kw2="5")
        return damage_dealt
        
    def skill3(self):
        pass

    def battle_entry_effects(self):
        self.apply_effect(StatsEffect('MachineGolem Passive', -1, True, {'maxhp' : 1.2, 'atk' : 1.2, 'defense' : 1.3}, 
                                      can_be_removed_by_skill=False))
        self.hp = self.maxhp


class Dullahan(Monster):
    """
    Countered by healing
    """
    def __init__(self, name, lvl, exp=0, equip=None, image=None):
        super().__init__(name, lvl, exp, equip, image)
        self.original_name = "Dullahan"
        self.skill1_description = "Attack 3 closest enemies with 300% atk. Inflict Deep Wound on target for 24 turns. Deep Wound: take 66% of applier atk as status damage each turn, can be removed by healing." \
        " If target hp is below 50%, inflict 2 Deep Wound instead."
        self.skill2_description = "Attack 3 closest enemies with 300% atk, if target hp is below 50%, reduce their healing efficiency by 30% for 24 turns."
        self.skill3_description = "Increase spd by 20%."
        self.skill1_description_jp = "最も近い敵3体に攻撃力300%のダメージを与える。24ターンの間対象に重傷を付与。" \
        "重傷:攻撃力の66%を状態ダメージを毎ターン受ける。HP回復によって解除できる。対象のHPが50%以下の場合、2つの重傷を付与。"
        self.skill2_description_jp = "最も近い敵3体に攻撃力300%のダメージを与え、対象のHPが50%以下の場合、20ターンの間回復効率を30%減少させる。"
        self.skill3_description_jp = "速度を20%増加する。"
        self.skill1_cooldown_max = 5
        self.skill2_cooldown_max = 5
        self.is_boss = True

    

    def skill1_logic(self):
        def wound(self, target):
            if target.hp < target.maxhp * 0.5:
                target.apply_effect(ContinuousDamageEffect('Deep Wound', duration=24, is_buff=False, value=0.66 * self.atk, imposter=self, remove_by_heal=True))
                target.apply_effect(ContinuousDamageEffect('Deep Wound', duration=24, is_buff=False, value=0.66 * self.atk, imposter=self, remove_by_heal=True))
            else:
                target.apply_effect(ContinuousDamageEffect('Deep Wound', duration=24, is_buff=False, value=0.66 * self.atk, imposter=self, remove_by_heal=True))
        damage_dealt = self.attack(multiplier=3.0, repeat=1, func_after_dmg=wound, target_kw1="n_enemy_in_front", target_kw2="3")
        return damage_dealt
    
    def skill2_logic(self):
        def wound(self, target):
            if target.hp < target.maxhp * 0.5:
                target.apply_effect(StatsEffect('Healing Down', duration=24, is_buff=False, stats_dict={'heal_efficiency' : -0.3}))
        damage_dealt = self.attack(multiplier=3.0, repeat=1, func_after_dmg=wound, target_kw1="n_enemy_in_front", target_kw2="3")
        return damage_dealt

    def skill3(self):
        pass

    def battle_entry_effects(self):
        self.apply_effect(StatsEffect('Dullahan Passive', -1, True, {'spd' : 1.2}, can_be_removed_by_skill=False))


class Salamander(Monster):
    def __init__(self, name, lvl, exp=0, equip=None, image=None):
        super().__init__(name, lvl, exp, equip, image)
        self.original_name = "Salamander"
        self.skill1_description = "Attack enemies with 150% atk 8 times, each attack has a 66% chance to inflict Burn for 22 turns." \
        " Burn deals 12% of self atk as status damage each turn."
        self.skill2_description = "Attack all enemies with 150% atk, each attack has a 75% chance to inflict Burn for 22 turns."
        self.skill3_description = "Recover hp by 2% of maxhp each turn."
        self.skill1_description_jp = "敵に攻撃力150%のダメージを8回与え、それぞれの攻撃に66%の確率で22ターンの間燃焼を付与。" \
        "燃焼は攻撃力の12%を状態ダメージ毎ターン受ける。"
        self.skill2_description_jp = "全ての敵に攻撃力150%のダメージを与え、それぞれの攻撃に75%の確率で22ターンの間燃焼を付与。"
        self.skill3_description_jp = "毎ターンHPが最大HPの2%回復する。"
        self.skill1_cooldown_max = 5
        self.skill2_cooldown_max = 5
        self.is_boss = False

    

    def skill1_logic(self):
        def burn_effect(self, target):
            dice = random.randint(1, 100)
            if dice <= 66:
                target.apply_effect(ContinuousDamageEffect('Burn', duration=22, is_buff=False, value=0.12 * self.atk, imposter=self))
        damage_dealt = self.attack(multiplier=1.5, repeat=8, func_after_dmg=burn_effect)
        return damage_dealt

    def skill2_logic(self):
        def burn_effect(self, target):
            dice = random.randint(1, 100)
            if dice <= 75:
                target.apply_effect(ContinuousDamageEffect('Burn', duration=22, is_buff=False, value=0.12 * self.atk, imposter=self))
        damage_dealt = self.attack(multiplier=1.5, repeat=1, func_after_dmg=burn_effect, target_kw1="n_random_enemy", target_kw2="5")
        return damage_dealt

    def skill3(self):
        pass

    def battle_entry_effects(self):
        e = ContinuousHealEffect('Salamander Passive', -1, True, lambda x, y: x.maxhp * 0.02, self, "2% of maxhp",
                                 value_function_description_jp="最大HPの2%")
        e.can_be_removed_by_skill = False
        self.apply_effect(e)


class Witch(Monster):
    def __init__(self, name, lvl, exp=0, equip=None, image=None):
        super().__init__(name, lvl, exp, equip, image)
        self.original_name = "Witch"
        self.skill1_description = "Attack closest enemy with 200% atk, 100% chance to inflict Burn if target does not have any Burn effect, Burn deals 20% of self atk as" \
        " status damage each turn. If target already has Burn that is not permanent, increase the first burn effect duration by 15 turns."
        self.skill2_description = "Revive an random dead ally to 100% of your current hp. Otherwise, this skill has no effect." 
        self.skill3_description = "At start of battle, reduce all damage taken by 60% for 12 turns."
        self.skill1_description_jp = "最も近い敵に攻撃力200%のダメージを与え、対象が燃焼効果を持っていない場合確率100%で燃焼を付与。" \
        "燃焼は攻撃力の20%を状態ダメージとして毎ターン受ける。対象が既に燃焼効果を持っている場合、最初の燃焼効果の持続時間を15ターン増加。"
        self.skill2_description_jp = "ランダムな撃破された味方を100%HPで復活させる。撃破された味方が無い場合、このスキルは効果がない。"
        self.skill3_description_jp = "戦闘開始時、12ターンの間受けるダメージを60%減少させる。"
        self.skill1_cooldown_max = 4
        self.skill2_cooldown_max = 5
        self.is_boss = False

    

    def skill1_logic(self):
        def burn(self, target):
            if not target.has_effect_that_named("Burn"):
                target.apply_effect(ContinuousDamageEffect('Burn', duration=-1, is_buff=False, value=0.2 * self.atk, imposter=self))
            else:
                burn_effect = target.get_effect_that_named("Burn")
                if burn_effect.duration > 0:
                    burn_effect.duration += 15
        damage_dealt = self.attack(multiplier=2.0, repeat=1, func_after_dmg=burn, target_kw1="enemy_in_front")
        return damage_dealt

    def skill2_logic(self):
        the_dead = [x for x in self.party if x.is_dead()]
        if the_dead:
            revive_target = random.choice(the_dead)
            revive_target.revive(self.hp, 0, self)
        return 0

    def skill3(self):
        pass

    def battle_entry_effects(self):
        self.apply_effect(StatsEffect('Witchcraft', 12, True, {'final_damage_taken_multipler' : -0.5}))


# ====================================
# End of Negative Status
# ====================================
# Anti Status Damage
# ====================================


class WaterSpirit(Monster):
    """
    Can be countered by normal damage, no status damage.
    """
    def __init__(self, name, lvl, exp=0, equip=None, image=None):
        super().__init__(name, lvl, exp, equip, image)
        self.original_name = "WaterSpirit"
        self.skill1_description = "3 enemies in the front are stunned and poisoned for 5 turns." \
        " Water Poison: take 4% of current hp as status damage per turn. Ally of lowest hp percentage is healed by 20% of your maxhp."
        self.skill2_description = "Attack all enemies with 150% atk and apply Water Poison for 5 turns." \
        " Water Poison: take 4% of current hp as status damage per turn. If target already has Water Poison," \
        " target takes 35% of its maxhp as status damage."
        self.skill3_description = "Increase maxhp by 30%. At start of battle, apply Water for all allies." \
        " Water: When hp is not full, status damage taken is reduced to 0," \
        " heal hp by 6% of your maxhp when taking status damage."
        self.skill1_description_jp = "前方の敵3体を5ターン気絶させ、水毒を付与する。" \
        "水毒:毎ターン現在のHPの4%を状態ダメージとして受ける。最もHP割合が低い味方は最大HPの20%回復する。"
        self.skill2_description_jp = "全ての敵に攻撃力150%のダメージを与え、5ターンの間水毒を付与する。" \
        "水毒:毎ターン現在のHPの4%を状態ダメージとして受ける。対象が既に水毒を持っている場合、対象は最大HPの35%を状態ダメージ受ける。"
        self.skill3_description_jp = "最大HPを30%増加させる。戦闘開始時、全ての味方に水を付与する。" \
        "水:HPが満タンでない場合、受ける状態ダメージを0にし、状態ダメージを受けた時、最大HPの6%回復する。"
        self.skill1_cooldown_max = 5
        self.skill2_cooldown_max = 5
        self.is_boss = True

    

    def skill1_logic(self):
        targets = self.target_selection("n_enemy_in_front", "3")
        for t in targets:
            t.apply_effect(StunEffect('Stun', duration=5, is_buff=False))
            t.apply_effect(ContinuousDamageEffect_Poison('Water Poison', duration=5, is_buff=False, ratio=0.04, imposter=self, base="hp"))
        if self.is_alive():
            lowest_hp_ally = min(self.ally, key=lambda x: x.hp / x.maxhp)
            lowest_hp_ally.heal_hp(self.maxhp * 0.2, self)

    def skill2_logic(self):
        def water_poison(self, target: character.Character):
            if target.has_effect_that_named("Water Poison"):
                target.take_status_damage(target.maxhp * 0.35, self)
            else:
                target.apply_effect(ContinuousDamageEffect_Poison('Water Poison', duration=5, is_buff=False, ratio=0.04, imposter=self, base="hp"))
        damage_dealt = self.attack(multiplier=1.5, repeat=1, func_after_dmg=water_poison, target_kw1="n_random_enemy", target_kw2="5")
        return damage_dealt
    
    def skill3(self):
        pass

    def battle_entry_effects(self):
        self.apply_effect(StatsEffect('WaterSpirit Passive', -1, True, {'maxhp' : 1.3}, can_be_removed_by_skill=False))
        self.hp = self.maxhp
        for a in self.ally:
            def heal_func(c):
                return c.maxhp * 0.06
            water = EffectShield1('Water', -1, True, 1, heal_function=heal_func, cc_immunity=False, effect_applier=self,
                                         cover_normal_damage=False, cover_status_damage=True, cancel_damage=True)
            water.can_be_removed_by_skill = False
            a.apply_effect(water)




# ====================================
# End of Anti Status Damage
# ====================================
# Anti Normal Damage
# ====================================


class Sylphid(Monster):
    """
    Can be countered by status damage.
    """
    def __init__(self, name, lvl, exp=0, equip=None, image=None):
        super().__init__(name, lvl, exp, equip, image)
        self.original_name = "Sylphid"
        self.skill1_description = "Increase atk and defense by 20% for all allies for 24 turns, however, their heal efficiency is reduced by 40% for 24 turns."
        self.skill2_description = "Attack enemies 7 times with 180% atk each."
        self.skill3_description = "At start of battle, apply unremovable Air shield to all allies." \
        " Air Shield: When taking normal damage, reduce damage taken by 45%."
        self.skill1_description_jp = "全ての味方の攻撃力と防御力を24ターンの間、20%増加させる。ただし、回復効率が24ターンの間、40%減少する。"
        self.skill2_description_jp = "敵を7回攻撃し、それぞれの攻撃は攻撃力の180%で行う。"
        self.skill3_description_jp = "戦闘開始時に全ての味方に解除不能なエアシールドを付与する。エアシールド: 通常ダメージを受けた際、受けるダメージを45%減少させる。"
        self.skill1_cooldown_max = 5
        self.skill2_cooldown_max = 3
        self.is_boss = True

    

    def skill1_logic(self):
        for a in self.ally:
            a.apply_effect(StatsEffect('Force', 24, True, {'atk' : 1.2, 'defense' : 1.2}))
            a.apply_effect(StatsEffect('Weakness', 24, False, {'heal_efficiency' : -0.4}))
        return 0

    def skill2_logic(self):
        damage_dealt = self.attack(multiplier=1.8, repeat=7)
        return damage_dealt

    def skill3(self):
        pass

    def battle_entry_effects(self):
        for a in self.ally:
            ashield = ReductionShield('Air Shield', -1, True, 0.45, False,
                                        cover_status_damage=False, cover_normal_damage=True)
            ashield.can_be_removed_by_skill = False
            a.apply_effect(ashield)













# ====================================
# End of Anti Normal Damage
# ====================================
# Multistrike
# ====================================


class Ninja(Monster):
    def __init__(self, name, lvl, exp=0, equip=None, image=None):
        super().__init__(name, lvl, exp, equip, image)
        self.original_name = "Ninja"
        self.skill1_description = "Attack closest enemy 12 times with 150% atk."
        self.skill2_description = "For 4 turns, increase evasion by 50%. Attack closest enemy 8 times with 150% atk."
        self.skill3_description = "Normal attack have 30% chance to reduce all skill cooldown by 1 turn."
        self.skill1_description_jp = "最も近い敵に攻撃力150%のダメージを12回与える。"
        self.skill2_description_jp = "4ターンの間、回避率を50%増加する。最も近い敵に攻撃力150%のダメージを8回与える。"
        self.skill3_description_jp = "通常攻撃に30%の確率で全てのスキルのクールダウンを1ターン減少させる。"
        self.skill1_cooldown_max = 4
        self.skill2_cooldown_max = 4
        self.is_boss = False

    

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


class KillerBee(Monster):
    def __init__(self, name, lvl, exp=0, equip=None, image=None):
        super().__init__(name, lvl, exp, equip, image)
        self.original_name = "Killerbee"
        self.skill1_description = "Attack closest enemy 4 times with 250% atk"
        self.skill2_description = "Attack 5 enemies with 200% atk"
        self.skill3_description = "Skill attack inflict Sting on target for 24 turns. Sting: every time target take damage, take 9% of applier atk as status damage. Does not trigger for status damage."
        self.skill1_description_jp = "最も近い敵に攻撃力250%のダメージを4回与える。"
        self.skill2_description_jp = "全ての敵に攻撃力200%のダメージを与える。"
        self.skill3_description_jp = "スキル攻撃は対象に24ターンの間毒針を付与。" \
        "毒針:対象がダメージを受ける度、攻撃力の9%を状態ダメージとして受ける。状態ダメージの場合、効果は発動しない。"
        self.skill1_cooldown_max = 4
        self.skill2_cooldown_max = 4
        self.is_boss = False

    

    def skill1_logic(self):
        def sting_effect(self, target):
            target.apply_effect(StingEffect('Sting', duration=24, is_buff=False, value=0.09 * self.atk, imposter=self))
        damage_dealt = self.attack(multiplier=3.0, repeat=4, func_after_dmg=sting_effect, target_kw1="enemy_in_front")
        return damage_dealt

    def skill2_logic(self):
        def sting_effect(self, target):
            target.apply_effect(StingEffect('Sting', duration=24, is_buff=False, value=0.09 * self.atk, imposter=self))
        damage_dealt = self.attack(target_kw1="n_random_enemy",target_kw2="5", multiplier=2.0, repeat=1, func_after_dmg=sting_effect)
        return damage_dealt
        
    def skill3(self):
        pass 


class Samurai(Monster):
    def __init__(self, name, lvl, exp=0, equip=None, image=None):
        super().__init__(name, lvl, exp, equip, image)
        self.original_name = "Samurai"
        self.skill1_description = "Attack closest enemy 7 times with 200% atk."
        self.skill2_description = "Attack enemy with lowest hp 3 times with 300% atk."
        self.skill3_description = "Skill have 30% chance to inflict bleed on target for 24 turns. Bleed deals 8% of atk as damage per turn."
        self.skill1_description_jp = "最も近い敵に攻撃力200%のダメージを7回与える。"
        self.skill2_description_jp = "最もHPが低い敵に攻撃力300%のダメージを3回与える。"
        self.skill3_description_jp = "スキルに30%の確率で対象に24ターンの間出血を付与。出血は攻撃力の8%を状態ダメージとして毎ターン受ける。"
        self.skill1_cooldown_max = 5
        self.skill2_cooldown_max = 5
        self.is_boss = False

    

    def skill1_logic(self):
        def bleed_effect(self, target):
            dice = random.randint(1, 100)
            if dice <= 30:
                target.apply_effect(ContinuousDamageEffect('Bleed', duration=24, is_buff=False, value=0.08 * self.atk, imposter=self))
        damage_dealt = self.attack(multiplier=2.0, repeat=7, func_after_dmg=bleed_effect, target_kw1="enemy_in_front")
        return damage_dealt

    def skill2_logic(self):
        def bleed_effect(self, target):
            dice = random.randint(1, 100)
            if dice <= 30:
                target.apply_effect(ContinuousDamageEffect('Bleed', duration=24, is_buff=False, value=0.08 * self.atk, imposter=self))
        damage_dealt = damage_dealt = self.attack(target_kw1="n_lowest_attr",target_kw2="1",target_kw3="hp",target_kw4="enemy", multiplier=3.0, repeat=3, func_after_dmg=bleed_effect)
        return damage_dealt
        
    def skill3(self):
        pass


class BlackKnight(Monster):
    """
    Taily + Fenrir would be a good counter
    """
    def __init__(self, name, lvl, exp=0, equip=None, image=None):
        super().__init__(name, lvl, exp, equip, image)
        self.original_name = "BlackKnight"
        self.skill1_description = "Attack random enemies 12 times with 250% atk. At the end of all attack, if hp is below 40%," \
        " Increase atk and crit rate by 10% for self and neighboring allies, effect last for 30 turns."
        self.skill2_description = "For 8 turns, increase atk by 30%. Attack closest enemy 6 times with 220% atk."
        self.skill3_description = "atk increased by 40% if hp is below 40%."
        self.skill1_description_jp = "ランダムな敵に攻撃力250%で12回攻撃。全ての攻撃の終わりに、自分HPが40%以下の場合、自身と隣接する味方の攻撃力とクリティカル率を10%増加させ、効果は30ターン持続。"
        self.skill2_description_jp = "8ターンの間、攻撃力を30%増加。最も近い敵に攻撃力220%で6回攻撃。"
        self.skill3_description_jp = "HPが40%以下の場合、攻撃力が40%増加。"
        self.skill1_cooldown_max = 4
        self.skill2_cooldown_max = 4
        self.is_boss = True

    

    def skill1_logic(self):
        damage_dealt = self.attack(multiplier=2.5, repeat=12)
        if self.is_alive() and self.hp < self.maxhp * 0.4:
            self.apply_effect(StatsEffect('Atk Up', 30, True, {'atk' : 1.1, 'crit' : 0.1}))
            for n in self.get_neighbor_allies_not_including_self():
                n.apply_effect(StatsEffect('Atk Up', 30, True, {'atk' : 1.1, 'crit' : 0.1}))
        return damage_dealt

    def skill2_logic(self):
        self.apply_effect(StatsEffect('Atk Up', 8, True, {'atk' : 1.3}))
        damage_dealt = self.attack(multiplier=2.2, repeat=6, target_kw1="enemy_in_front")
        return damage_dealt

    def skill3(self):
        pass

    def battle_entry_effects(self):
        self.apply_effect(StatsEffect('BlackKnight Passive', -1, True, {'atk' : 1.4}, 
                                      condition=lambda self: self.hp < self.maxhp * 0.4, can_be_removed_by_skill=False)) 


class AssassinB(Monster):
    def __init__(self, name, lvl, exp=0, equip=None, image=None):
        super().__init__(name, lvl, exp, equip, image)
        self.original_name = "AssassinB"
        self.skill1_description = "Attack enemy with lowest hp 5 times with 220% atk. If target hp is below 20%, attack with 320% atk instead."
        self.skill2_description = "Attack random enemies 5 times with 200% atk, each attack has 40% chance to inflict Bleed" \
        " for 24 turns. Bleed deals 10% of self atk as status damage each turn."
        self.skill3_description = "Atk is increased by 10%."
        self.skill1_description_jp = "最もHPが低い敵に攻撃力220%で5回攻撃。対象のHPが20%以下の場合、代わりに攻撃力320%で攻撃。"
        self.skill2_description_jp = "ランダムな敵に攻撃力200%で5回攻撃、それぞれの攻撃に40%の確率で24ターンの間出血を付与。" \
        "出血は攻撃力の10%を状態ダメージとして毎ターン受ける。"
        self.skill3_description_jp = "攻撃力が10%増加する。"
        self.skill1_cooldown_max = 5
        self.skill2_cooldown_max = 5
        self.is_boss = False

    

    def skill1_logic(self):
        new_multiplier_func = lambda self, target, x, y: 3.2 if target.hp < target.maxhp * 0.2 else 2.2
        damage_dealt = self.attack(multiplier=2.2, repeat=5, target_kw1="n_lowest_attr", 
                                   target_kw2="1", target_kw3="hp", target_kw4="enemy", 
                                   func_for_multiplier=new_multiplier_func)
        return damage_dealt

    def skill2_logic(self):
        def bleed_effect(self, target):
            dice = random.randint(1, 100)
            if dice <= 40:
                target.apply_effect(ContinuousDamageEffect('Bleed', duration=24, is_buff=False, value=0.1 * self.atk, imposter=self))
        damage_dealt = self.attack(multiplier=2.0, repeat=5, func_after_dmg=bleed_effect)
        return damage_dealt

    def skill3(self):
        pass

    def battle_entry_effects(self):
        self.apply_effect(StatsEffect('AssassinB Passive', -1, True, {'atk' : 1.1}, can_be_removed_by_skill=False))


class Asura(Monster):
    """
    Can be countered by multi hit
    """
    def __init__(self, name, lvl, exp=0, equip=None, image=None):
        super().__init__(name, lvl, exp, equip, image)
        self.original_name = "Asura"
        self.skill1_description = "Attack random enemies 6 times with 220% atk. 50% chance to apply vulnerable for 30 turns." \
        " Vulnerable: take 12% more damage from all sources."
        self.skill2_description = "Attack random enemies 6 times with 240% atk. Before attacking, increase accuracy by 12% for 24 turns."
        self.skill3_description = "At start of battle, gain 6 uses of cancellation shield, shield will cancel all damage." \
        " Everytime you use a skill, shield uses is recharged to 6."
        self.skill1_description_jp = "敵に攻撃力220%のダメージを6回与え、それぞれの攻撃に50%の確率で30ターンの間脆弱を付与。" \
        "脆弱:最終ダメージ倍率12%増加する。"
        self.skill2_description_jp = "敵に攻撃力240%のダメージを6回与える。攻撃前に24ターンの間命中率を12%増加。"
        self.skill3_description_jp = "戦闘開始時、6回のキャンセルシールドを獲得。シールドは全てのダメージをキャンセルする。" \
        "スキルを使用する度、シールドの使用回数が6回にリチャージされる。"
        self.skill1_cooldown_max = 4
        self.skill2_cooldown_max = 4
        self.is_boss = True

    

    def skill1_logic(self):
        def vulnerable_effect(self, target):
            dice = random.randint(1, 100)
            if dice <= 50:
                target.apply_effect(StatsEffect('Vulnerable', 30, False, {'final_damage_taken_multipler' : 0.12}))
        damage_dealt = self.attack(multiplier=2.2, repeat=6, func_after_dmg=vulnerable_effect)
        shield = self.get_effect_that_named(effect_name="Asura Passive", class_name="CancellationShield")
        if not shield:
            raise Exception("Cancellation Shield not found on Asura.")
        shield.uses = 6
        return damage_dealt


    def skill2_logic(self):
        self.apply_effect(StatsEffect('Accuracy Up', 24, True, {'acc' : 0.12}))
        damage_dealt = self.attack(multiplier=2.4, repeat=6)
        shield = self.get_effect_that_named(effect_name="Asura Passive", class_name="CancellationShield")
        if not shield:
            raise Exception("Cancellation Shield not found on Asura.")
        shield.uses = 6
        return damage_dealt


    def skill3(self):
        pass

    def battle_entry_effects(self):
        cancellation_shield = CancellationShield("Asura Passive", -1, True, 0, False, uses=6, remove_this_effect_when_use_is_zero=False)
        cancellation_shield.can_be_removed_by_skill = False
        self.apply_effect(cancellation_shield)




# ====================================
# End of Multistrike
# ====================================
# Counter Multistrike
# ====================================


class WarriorB(Monster):
    """
    Can be countered by single damage
    """
    def __init__(self, name, lvl, exp=0, equip=None, image=None):
        super().__init__(name, lvl, exp, equip, image)
        self.original_name = "WarriorB"
        self.skill1_description = "Attack enemy of highest atk 4 times with 250% atk. Each attack inflict Dilemma, reducing crit rate by 30% for 25 turns."
        self.skill2_description = "Attack enemy of highest atk with 600% atk, ignore protected effects."
        self.skill3_description = "Increase maxhp by 100% and defense by 30%. After taking normal damage, apply Guard on all allies for 1 turn, reducing damage taken by 70%."
        self.skill1_description_jp = "最も攻撃力が高い敵に攻撃力250%のダメージを4回与える。" \
        "それぞれの攻撃に難局を付与、25ターンの間クリティカル率を30%減少させる。"
        self.skill2_description_jp = "最も攻撃力が高い敵に攻撃力600%のダメージを与える。" \
        "対象の守護者からの保護効果を無視。"
        self.skill3_description_jp = "最大HP100%、防御力30%増加させる。通常ダメージを受けた後、全ての味方に1ターンの間ガードを付与。" \
        "ガード:受けるダメージを70%減少させる。"
        self.skill1_cooldown_max = 4
        self.skill2_cooldown_max = 4
        self.is_boss = True

    

    def skill1_logic(self):
        def dilemma_effect(self, target):
            target.apply_effect(StatsEffect('Dilemma', 25, False, {'crit' : -0.3}))
        damage_dealt = self.attack(multiplier=2.5, repeat=4, target_kw1="n_highest_attr", target_kw2="1", target_kw3="atk", target_kw4="enemy", func_after_dmg=dilemma_effect)
        return damage_dealt

    def skill2_logic(self):
        damage_dealt = self.attack(multiplier=6.0, repeat=1, target_kw1="n_highest_attr", target_kw2="1", target_kw3="atk", target_kw4="enemy", ignore_protected_effect=True)
        return damage_dealt

    
    def skill3(self):
        pass

    def take_damage_aftermath(self, damage, attacker):
        self.update_ally_and_enemy()
        for a in self.ally:
            if a.is_alive():
                a.apply_effect(ReductionShield('Guard', 1, True, 0.7, cc_immunity=False))
        return damage

    def battle_entry_effects(self):
        self.apply_effect(StatsEffect('WarriorB Passive', -1, True, {'maxhp' : 2.0, 'defense' : 1.3}, 
                                      can_be_removed_by_skill=False))
        self.hp = self.maxhp


class Angel(Monster):
    """
    Can be countered by single damage
    """
    def __init__(self, name, lvl, exp=0, equip=None, image=None):
        super().__init__(name, lvl, exp, equip, image)
        self.original_name = "Angel"
        self.skill1_description = "Attack all enemies with 280% atk, 50% chance to apply Weaken and Blind for 24 turns." \
        " Weaken: reduce atk by 10%. Blind: reduce accuracy by 10%."
        self.skill2_description = "Heal all allies by 280% of your atk, 50% chance to apply Absorption Shield for 16 turns," \
        " Shield absorbs damage equal to 280% of your atk."
        self.skill3_description = "At start of battle, apply unremovable Heaven Shield on all allies." \
        " Heaven Shield: All damage taken is reduced by 30%, the subsequent damage taken on the same turn is further reduced by 30%."
        self.skill1_description_jp = "全ての敵に攻撃力280%のダメージを与え、50%の確率で24ターンの間脆弱と盲目を付与。" \
        "脆弱:攻撃力を10%減少。盲目:命中率を10%減少。"
        self.skill2_description_jp = "全ての味方を攻撃力280%で回復し、50%の確率で16ターンの間吸収シールドを付与。" \
        "シールドは攻撃力280%分のダメージを吸収する。"
        self.skill3_description_jp = "戦闘開始時、全ての味方に解除不可能な天国の盾を付与。" \
        "天国の盾:受ける全てのダメージを30%減少し、同じターンに受ける後続ダメージをさらに30%減少。"
        self.skill1_cooldown_max = 4
        self.skill2_cooldown_max = 4
        self.is_boss = True

    

    def skill1_logic(self):
        def weaken_blind_effect(self, target):
            if random.randint(1, 100) <= 50:
                target.apply_effect(StatsEffect('Weaken', 24, False, {'atk' : 0.9}))
            if random.randint(1, 100) <= 50:
                target.apply_effect(StatsEffect('Blind', 24, False, {'acc' : -0.1}))
        damage_dealt = self.attack(multiplier=2.8, repeat=1, func_after_dmg=weaken_blind_effect, target_kw1="n_random_enemy", target_kw2="5")
        return damage_dealt

    def skill2_logic(self):
        for a in self.ally:
            a.heal_hp(self.atk * 2.8, self)
            if a.is_alive():
                if random.randint(1, 100) <= 50:
                    shield = AbsorptionShield('Absorption Shield', 16, True, 2.8 * self.atk, False)
                    a.apply_effect(shield)
        return 0

    def skill3(self):
        pass

    def battle_entry_effects(self):
        for a in self.ally:
            heaven_shield = AntiMultiStrikeReductionShield('Heaven Shield', -1, True, 0.3, cc_immunity=False)
            heaven_shield.can_be_removed_by_skill = False
            a.apply_effect(heaven_shield)


# ====================================
# End of Counter Multistrike
# ====================================
# Ignore Protected Effect
# ====================================


class Valkyrie(Monster):
    def __init__(self, name, lvl, exp=0, equip=None, image=None):
        super().__init__(name, lvl, exp, equip, image)
        self.original_name = "Valkyrie"
        self.skill1_description = "Focus attack on the closest enemy with 280% atk 2 times, ignore their protected effects. If target does not have protected effect, damage increases by 100%."
        self.skill2_description = "Focus attack on the closest enemy with 340% atk 3 times, ignore their protected effects."
        self.skill3_description = "Normal attack inflict 2 bleed on target that does not have protected effect for 30 turns. Bleed deals 12% of atk status damage per turn."
        self.skill1_description_jp = "最も近い敵に集中攻撃し攻撃力280%のダメージを2回与える。対象の守護者からの守護効果を無視。" \
        "対象が守護効果を持っていない場合、ダメージが100%増加。"
        self.skill2_description_jp = "最も近い敵に集中攻撃し攻撃力340%のダメージを3回与える。対象の守護者からの守護効果を無視。"
        self.skill3_description_jp = "通常攻撃は守護効果を持っていない対象に2つの出血を付与。出血は攻撃力の12%を状態ダメージとして毎ターン受ける。"
        self.skill1_cooldown_max = 4
        self.skill2_cooldown_max = 4
        self.is_boss = False

    

    def skill1_logic(self):
        def damage_amplify(self, target, final_damage):
            if not target.has_effect_that_named(class_name="ProtectedEffect"):
                final_damage *= 2.0
            return final_damage
        damage_dealt = self.attack(multiplier=2.8, repeat_seq=2, target_kw1="enemy_in_front", ignore_protected_effect=True)
        return damage_dealt

    def skill2_logic(self):
        damage_dealt = self.attack(multiplier=3.4, repeat_seq=3, target_kw1="enemy_in_front", ignore_protected_effect=True)
        return damage_dealt

    
    def skill3(self):
        pass

    def normal_attack(self):
        def bleed_effect(self, target):
            if not target.has_effect_that_named(class_name="ProtectedEffect"):
                target.apply_effect(ContinuousDamageEffect("Bleed", 30, False, self.atk * 0.12, self))
                target.apply_effect(ContinuousDamageEffect("Bleed", 30, False, self.atk * 0.12, self))
        self.attack(func_after_dmg=bleed_effect)


class Cavalier(Monster):
    """
    No specific counter, just a reminder that protected effect does not work on this monster.
    """
    def __init__(self, name, lvl, exp=0, equip=None, image=None):
        super().__init__(name, lvl, exp, equip, image)
        self.original_name = "Cavalier"
        self.skill1_description = "Attack random enemies 6 times with 270% atk each, ignoring protected effects. Target is blinded for 20 turns, reducing accuracy by 15%."
        self.skill2_description = "Attack closest enemy 6 times with 260% atk each, ignoring protected effects, damage increased by 30% for every fallen enemy."
        self.skill3_description = "Increase maxhp by 60%. When taking damage, if you have a higher speed than your opponent, the damage you take is reduced by 30%."
        self.skill1_description_jp = "ランダムな敵に攻撃力270%のダメージを6回与える。対象は20ターンの間盲目になり、命中率が15%減少。" \
        "守護者からの守護効果を無視。"
        self.skill2_description_jp = "最も近い敵に攻撃力260%のダメージを6回与える。対象の守護者からの守護効果を無視。" \
        "倒れた敵1体につきダメージが30%増加。"
        self.skill3_description_jp = "最大HPを60%増加。ダメージを受けた時、速度が相手よりも高い場合、受けるダメージを30%減少。"
        self.skill1_cooldown_max = 5
        self.skill2_cooldown_max = 4
        self.is_boss = True

    

    def skill1_logic(self):
        def blind_effect(self, target):
            target.apply_effect(StatsEffect('Blind', 20, False, {'acc' : -0.15}))
        damage_dealt = self.attack(multiplier=2.7, repeat=6, func_after_dmg=blind_effect, ignore_protected_effect=True)
        return damage_dealt

    def skill2_logic(self):
        def bonus_damage(self, target, final_damage):
            b = 5 - len(target.ally)
            a = 0.3
            final_damage *= 1 + a * b
            return final_damage
        damage_dealt = self.attack(multiplier=2.6, repeat=6, target_kw1="enemy_in_front", func_damage_step=bonus_damage, ignore_protected_effect=True)
        return damage_dealt

    def skill3(self):
        pass

    def battle_entry_effects(self):
        effect = ReductionShield("Cavalier Passive", -1, True, 0.3, cc_immunity=False, 
                                 requirement=lambda a, b: a.spd > b.spd,
                                 requirement_description="Have higher spd than attacker.",
                                 requirement_description_jp="攻撃者よりも速度が高い。")
        effect.can_be_removed_by_skill = False
        self.apply_effect(effect)
        self.apply_effect(StatsEffect('Cavalier Passive', -1, True, {'maxhp' : 1.6}, can_be_removed_by_skill=False))
        self.hp = self.maxhp


class Warrior(Monster):
    """
    Can be countered by high single damage
    """
    def __init__(self, name, lvl, exp=0, equip=None, image=None):
        super().__init__(name, lvl, exp, equip, image)
        self.original_name = "Warrior"
        self.skill1_description = "Attack enemy of highest atk 4 times with 250% atk. Ignore protected effects."
        self.skill2_description = "Attack enemy of highest atk with 500% atk, inflict Weaken and Bleed for 25 turns." \
        " Weaken: reduce atk by 70%. Bleed: take 30% of applier atk as status damage each turn."
        self.skill3_description = "Increase maxhp by 80%, defense by 20%. After taking damage, apply Guard on self for 1 turn, reducing damage taken by 70%."
        self.skill1_description_jp = "最も高い攻撃力の敵に攻撃力250%のダメージを4回与える。守護者からの守護効果を無視。"
        self.skill2_description_jp = "最も高い攻撃力の敵に攻撃力500%のダメージを与える。25ターンの間衰弱と出血を付与。" \
        "衰弱:攻撃力を70%減少。出血:攻撃力の30%を状態ダメージとして毎ターン受ける。"
        self.skill3_description_jp = "最大HP80%、防御力20%増加。ダメージを受けた後、自身に1ターンの間ガードを付与。受けるダメージを70%減少。"
        self.skill1_cooldown_max = 4
        self.skill2_cooldown_max = 4
        self.is_boss = True

    

    def skill1_logic(self):
        damage_dealt = self.attack(multiplier=2.5, repeat=4, target_kw1="n_highest_attr", target_kw2="1", target_kw3="atk", target_kw4="enemy", ignore_protected_effect=True)
        return damage_dealt

    def skill2_logic(self):
        def weaken_and_bleed(self, target):
            target.apply_effect(StatsEffect('Weaken', 25, False, {'atk' : 0.3}))
            target.apply_effect(ContinuousDamageEffect('Bleed', 25, False, 0.3 * self.atk, self))
        damage_dealt = self.attack(multiplier=5.0, repeat=1, target_kw1="n_highest_attr", target_kw2="1", target_kw3="atk", target_kw4="enemy", func_after_dmg=weaken_and_bleed)
        return damage_dealt
    
    def skill3(self):
        pass

    def take_damage_aftermath(self, damage, attacker):
        self.apply_effect(ReductionShield('Guard', 1, True, 0.7, cc_immunity=False))
        return damage

    def battle_entry_effects(self):
        self.apply_effect(StatsEffect('Warrior Passive', -1, True, {'maxhp' : 1.8, 'defense' : 1.2}, 
                                      can_be_removed_by_skill=False))
        self.hp = self.maxhp


class Kerberos(Monster):
    """
    Countered not having low hp percentage or many reborn effects
    """
    def __init__(self, name, lvl, exp=0, equip=None, image=None):
        super().__init__(name, lvl, exp, equip, image)
        self.original_name = "Kerberos"
        self.skill1_description = "Attack 3 closest enemies with 240% atk 6 times."
        self.skill2_description = "Attack enemy with lowest hp percentage with 240% atk 9 times."
        self.skill3_description = "During skill attack, if enemy hp is falls below 30%, execute the target, dealing target hp * 100% bypass status damage."
        # 処刑
        self.skill1_description_jp = "最も近い3人の敵に攻撃力の240%で6回攻撃する。"
        self.skill2_description_jp = "HP割合が最も低い敵に攻撃力の240%で9回攻撃する。"
        self.skill3_description_jp = "スキル攻撃中、敵のHPが30%以下になった場合、対象を処刑し、対象のHPの100%分の状態異常無視ダメージを与える。"
        self.skill1_cooldown_max = 4
        self.skill2_cooldown_max = 4
        self.is_boss = True

    

    def skill1_logic(self):
        def execute(self, target: character.Character):
            if target.is_alive() and target.hp < target.maxhp * 0.3 and self.is_alive():
                target.take_bypass_status_effect_damage(target.hp, self)
        damage_dealt = self.attack(multiplier=2.4, repeat=6, target_kw1="n_enemy_in_front", target_kw2="3", func_after_dmg=execute)
        return damage_dealt

    def skill2_logic(self):
        def execute(self, target: character.Character):
            if target.is_alive() and target.hp < target.maxhp * 0.3 and self.is_alive():
                target.take_bypass_status_effect_damage(target.hp, self)
        damage_dealt = self.attack(multiplier=2.4, repeat=9, target_kw1="n_lowest_hp_percentage_enemy", target_kw2="1", func_after_dmg=execute)
        return damage_dealt

    def skill3(self):
        pass





# ====================================
# End of Ignore Protected Effect
# ====================================
# CC: Stun
# ====================================    


class MultiLegTank(Monster):
    def __init__(self, name, lvl, exp=0, equip=None, image=None):
        super().__init__(name, lvl, exp, equip, image)
        self.original_name = "MultiLegTank"
        self.skill1_description = "Attack all enemies with 130% atk and 80% chance to Stun for 8 turns."
        self.skill2_description = "Attack 3 closest enemies with 190% atk and 80% chance to Stun for 8 turns."
        self.skill3_description = "Normal attack target closest enemy with 270% atk and 80% chance to Stun for 8 turns."
        self.skill1_description_jp = "全ての敵に攻撃力130%のダメージを与え、80%の確率で8ターンの間スタンを付与。"
        self.skill2_description_jp = "最も近い敵3体に攻撃力190%のダメージを与え、80%の確率で8ターンの間スタンを付与。"  
        self.skill3_description_jp = "通常攻撃が最も近い敵に攻撃力270%のダメージを与え、80%の確率で8ターンの間スタンを付与。"
        self.skill1_cooldown_max = 5
        self.skill2_cooldown_max = 5
        self.is_boss = False

    

    def skill1_logic(self):
        def stun_effect(self, target):
            dice = random.randint(1, 100)
            if dice <= 80:
                target.apply_effect(StunEffect('Stun', duration=8, is_buff=False))
        damage_dealt = self.attack(multiplier=1.3, repeat=1, func_after_dmg=stun_effect, target_kw1="n_random_enemy",target_kw2="5")
        return damage_dealt

    def skill2_logic(self):
        def stun_effect(self, target):
            dice = random.randint(1, 100)
            if dice <= 80:
                target.apply_effect(StunEffect('Stun', duration=8, is_buff=False))
        damage_dealt = self.attack(multiplier=1.9, repeat=1, func_after_dmg=stun_effect, target_kw1="n_enemy_in_front",target_kw2="3")
        return damage_dealt
        
    def skill3(self):
        pass

    def normal_attack(self):
        def stun_effect(self, target):
            dice = random.randint(1, 100)
            if dice <= 80:
                target.apply_effect(StunEffect('Stun', duration=8, is_buff=False))
        self.attack(multiplier=2.7, func_after_dmg=stun_effect, target_kw1="enemy_in_front")


class Shenlong(Monster):
    """
    Can be countered by CC Immunity.
    """
    def __init__(self, name, lvl, exp=0, equip=None, image=None):
        super().__init__(name, lvl, exp, equip, image)
        self.original_name = "Shenlong"
        self.skill1_description = "All enemies are stunned for 10 turns. Attack all enemies 3 times with 220%/240%/260% atk each."
        self.skill2_description = "Increase atk and accuracy for all allies by 15% for 24 turns." \
        " Apply Trial of the Dragon on closest enemy for 12 turns if the same effect is not already on the target." \
        " Trial of the Dragon: atk and crit rate increased by 30%. If this effect expires, target takes 1 status damage is stunned for 12 turns." \
        " Trial of the Dragon cannot be removed by skill."
        self.skill3_description = "Increase hp by 222%."
        self.skill1_description_jp = "全ての敵を10ターンの間スタンさせる。全ての敵に攻撃力220%/240%/260%で3回攻撃。"
        self.skill2_description_jp = "全ての味方の攻撃力と命中率を24ターンの間15%増加させる。最も近い敵龍の試練に付与されていない場合に龍の試練を付与。" \
        "龍の試練:攻撃力とクリティカル率が30%増加。この効果が切れた場合、対象は1の状態ダメージを受け、12ターンの間スタンされる。" \
        "龍の試練はスキルで解除されない。"
        self.skill3_description_jp = "最大HPを222%増加させる。"
        self.skill1_cooldown_max = 5
        self.skill2_cooldown_max = 5
        self.is_boss = True

    

    def skill1_logic(self):
        for e in self.enemy:
            e.apply_effect(StunEffect('Stun', duration=10, is_buff=False))
        damage_dealt = self.attack(multiplier=2.2, repeat=1, target_kw1="n_random_enemy",target_kw2="5")
        damage_dealt += self.attack(multiplier=2.4, repeat=1, target_kw1="n_random_enemy",target_kw2="5")
        damage_dealt += self.attack(multiplier=2.6, repeat=1, target_kw1="n_random_enemy",target_kw2="5")
        return damage_dealt


    def skill2_logic(self):
        for a in self.ally:
            a.apply_effect(StatsEffect('Atk Acc Up', 24, True, {'atk' : 1.15, 'acc' : 1.15}))
        target = next(self.target_selection("enemy_in_front"))
        if not target.has_effect_that_named("Trial of the Dragon"):
            target.apply_effect(TrialofDragonEffect('Trial of the Dragon', duration=12, is_buff=False, stats_dict={'atk' : 1.3, 'crit' : 0.3},
                                                    damage=1, imposter=self, stun_duration=12))
        return 0

    def skill3(self):
        pass

    def battle_entry_effects(self):
        self.apply_effect(StatsEffect('Shenlong Passive', -1, True, {'maxhp' : 3.22}, can_be_removed_by_skill=False))
        self.hp = self.maxhp


# ====================================
# End of CC: Stun
# ====================================
# CC: Confuse
# ====================================


class Assassin(Monster):
    """
    Can be countered by CC Immunity.
    """
    def __init__(self, name, lvl, exp=0, equip=None, image=None):
        super().__init__(name, lvl, exp, equip, image)
        self.original_name = "Assassin"
        self.skill1_description = "Increase atk and spd by 33% for 24 turns, recover hp by 444% atk."
        self.skill2_description = "Attack closest enemy with 177% atk 8 times, each attack inflict confuse for 12 turns with a 20% chance." \
        " If target is confused, damage is increased by 100%." # with a 83.22% chance to confuse the target.
        self.skill3_description = "Normal attack target closest enemy and attack 2 times, 20% chance to confuse the target for 6 turns."
        self.skill1_description_jp = "攻撃力と速度を24ターンの間33%増加させ、攻撃力444%分のHPを回復。"
        self.skill2_description_jp = "最も近い敵に攻撃力177%のダメージを8回与え、それぞれの攻撃に20%の確率で12ターンの間混乱を付与。" \
        "対象が混乱している場合、ダメージが100%増加。" 
        self.skill3_description_jp = "通常攻撃は最も近い敵に2回攻撃。20%の確率で6ターンの間混乱を付与。"
        self.skill1_cooldown_max = 5
        self.skill2_cooldown_max = 3
        self.is_boss = True

    

    def skill1_logic(self):
        self.apply_effect(StatsEffect('Fast', 24, True, {'atk' : 1.33, 'spd' : 1.33}))
        self.heal_hp(4.44 * self.atk, self)

    def skill2_logic(self):
        def confuse_effect(self, target):
            if random.randint(1, 100) <= 20:
                target.apply_effect(ConfuseEffect('Confuse', duration=12, is_buff=False))
        def amplify(self, target, final_damage):
            if target.is_confused():
                final_damage *= 2.0
            return final_damage
        damage_dealt = self.attack(multiplier=1.77, repeat=8, func_after_dmg=confuse_effect, target_kw1="enemy_in_front", func_damage_step=amplify)
        return damage_dealt

    def skill3(self):
        pass

    def normal_attack(self):
        def confuse_effect(self, target):
            if random.randint(1, 100) <= 20:
                target.apply_effect(ConfuseEffect('Confuse', duration=6, is_buff=False)) 
        self.attack(target_kw1="enemy_in_front", func_after_dmg=confuse_effect, repeat=2)


class Fairy(Monster):
    def __init__(self, name, lvl, exp=0, equip=None, image=None):
        super().__init__(name, lvl, exp, equip, image)
        self.original_name = "Fairy"
        self.skill1_description = "Attack 4 random targets with 300% atk, confuse them for 8 turns."
        self.skill2_description = "Attack 1 enemy with 400% atk 3 times, each hit has 33% chance to confuse the target for 8 turns."
        self.skill3_description = "When taking damage from anyone who is confused," \
        " recover hp by 300% atk, increase atk by 30% and reduce damage taken multiplier by 40% for 8 turns." \
        " When the same effect is applied again, the duration is refreshed."
        self.skill1_description_jp = "ランダムなターゲット4体に攻撃力300%のダメージを与え、8ターンの間混乱を付与する。"
        self.skill2_description_jp = "1体の敵に攻撃力400%のダメージを3回与え、それぞれの攻撃に33%の確率で8ターンの間混乱を付与する。"
        self.skill3_description_jp = "混乱している相手からダメージを受けた時、攻撃力300%分のHPを回復し、攻撃力を30%増加し、8ターンの間受けるダメージを40%減少。" \
        "同じ効果が再度付与された場合、効果時間が更新される。"
        self.skill1_cooldown_max = 4
        self.skill2_cooldown_max = 4
        self.is_boss = False

    

    def skill1_logic(self):
        def confuse_effect(self, target):
            target.apply_effect(ConfuseEffect('Confuse', duration=8, is_buff=False))
        damage_dealt = self.attack(multiplier=3.0, repeat=1, func_after_dmg=confuse_effect, target_kw1="n_random_target",target_kw2="4")
        return damage_dealt


    def skill2_logic(self):
        def confuse_effect(self, target):
            dice = random.randint(1, 100)
            if dice <= 33:
                target.apply_effect(ConfuseEffect('Confuse', duration=8, is_buff=False))
        damage_dealt = self.attack(multiplier=4.0, repeat_seq=3, func_after_dmg=confuse_effect)
        return damage_dealt


    def skill3(self):
        pass

    def take_damage_aftermath(self, damage, attacker):
        if attacker.is_confused() and self.is_alive():
            self.heal_hp(3.0 * self.atk, self)
            play = self.get_effect_that_named(effect_name="Playful", additional_name="Fairy_Playful")
            if not play:
                play = StatsEffect('Playful', 8, True, {'atk' : 1.3, 'final_damage_taken_multipler' : -0.4})
                play.additional_name = "Fairy_Playful"
                self.apply_effect(play)
            else:
                play.duration = 8













# ====================================
# End of CC: Confuse
# ====================================
# CC: Sleep
# ====================================


class MagicPot(Monster):
    def __init__(self, name, lvl, exp=0, equip=None, image=None):
        super().__init__(name, lvl, exp, equip, image)
        self.original_name = "MagicPot"
        self.skill1_description = "Attack all enemies with 300% atk."
        self.skill2_description = "Each enemy has a 50% chance to be put asleep."
        self.skill3_description = "Evasion is increased by 50% for 10 turns."
        self.skill1_description_jp = "全ての敵に攻撃力300%のダメージを与える。"
        self.skill2_description_jp = "全ての敵にそれぞれ50%の確率で睡眠を付与。"
        self.skill3_description_jp = "回避率を10ターンの間50%増加。"
        self.skill1_cooldown_max = 5
        self.skill2_cooldown_max = 5
        self.is_boss = False


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


class Werewolfb(Monster):
    """
    Very nasty Sleep effect, can be countered by CC Immunity.
    """
    def __init__(self, name, lvl, exp=0, equip=None, image=None):
        super().__init__(name, lvl, exp, equip, image)
        self.original_name = "Werewolfb"
        self.skill1_description = "Attack all enemies with 300% atk, if their hp is above 60%, they are put to sleep."
        self.skill2_description = "Recover hp by 30% of maxhp, increase atk by 30% for 12 turns." \
        " All enemies that have lower atk than you are put to sleep."
        self.skill3_description = "At start of battle, apply Acc Up and Eva Up for you and neighboring allies for 40 turns." \
        " Increase accuracy and evasion by 30%."
        self.skill1_description_jp = "全ての敵に攻撃力の300%で攻撃し、敵のHPが60%以上の場合、睡眠状態にする。"
        self.skill2_description_jp = "最大HPの30%分のHPを回復し、12ターンの間、攻撃力を30%増加させる。自分より攻撃力が低い全ての敵を睡眠状態にする。"
        self.skill3_description_jp = "戦闘開始時、自分と隣接する味方に40ターンの間「命中アップ」と「回避アップ」を付与する。命中率と回避率を30%増加させる。"
        self.skill1_cooldown_max = 3
        self.skill2_cooldown_max = 3
        self.is_boss = True


    def skill1_logic(self):
        def sleep_effect(self, target):
            if target.hp > 0.6 * target.maxhp:
                target.apply_effect(SleepEffect('Sleep', duration=-1, is_buff=False))
        damage_dealt = self.attack(multiplier=3.0, target_kw1="n_random_enemy",target_kw2="5", repeat=1, func_after_dmg=sleep_effect)
        return damage_dealt


    def skill2_logic(self):
        self.heal_hp(0.3 * self.maxhp, self)
        if self.is_alive():
            self.apply_effect(StatsEffect('Strong', 12, True, {'atk' : 1.3}))
            for t in self.enemy:
                if t.atk < self.atk:
                    t.apply_effect(SleepEffect('Sleep', duration=-1, is_buff=False))
        return 0


    def skill3(self):
        pass

    def battle_entry_effects(self):
        neighbors = self.get_neighbor_allies_including_self()
        for n in neighbors:
            n.apply_effect(StatsEffect('Passive Aggressive', 40, True, {'acc' : 0.3, 'eva' : 0.3}))





# ====================================
# End of CC: Sleep
# ====================================
# CC: Freeze and Petrify
# ====================================


class Icelady(Monster):
    def __init__(self, name, lvl, exp=0, equip=None, image=None):
        super().__init__(name, lvl, exp, equip, image)
        self.original_name = "Icelady"
        self.skill1_description = "Attack 3 closest enemies with 300% atk 2 times, if you have higher atk than target," \
        " freeze the target for 10 turns."
        self.skill2_description = "Apply Regeneration and Crit Def Up for all allies for 20 turns." \
        " Regeneration: recover 8% of maxhp each turn. Crit Def Up: critdef increased by 60%."
        self.skill3_description = "If you have higher atk than target, normal attack freeze the target for 10 turns."
        self.skill1_description_jp = "最も近い3人の敵に攻撃力の300%で2回攻撃し、自分の攻撃力が対象より高い場合、対象を10ターンの間「凍結」させる。"
        self.skill2_description_jp = "全ての味方に20ターンの間「再生」と「クリティカル防御アップ」を付与する。再生：毎ターン最大HPの8%を回復する。クリティカル防御アップ：クリティカル防御が60%増加する。"
        self.skill3_description_jp = "自分の攻撃力が対象より高い場合、通常攻撃で対象を10ターンの間「凍結」させる。"
        self.skill1_cooldown_max = 3
        self.skill2_cooldown_max = 4
        self.is_boss = True

    def skill1_logic(self):
        def freeze_effect(self, target):
            if self.atk > target.atk:
                target.apply_effect(FrozenEffect('Freeze', duration=10, is_buff=False, imposter=self))
        damage_dealt = self.attack(multiplier=3.0, repeat=2, func_after_dmg=freeze_effect, target_kw1="n_enemy_in_front",target_kw2="3")
        return damage_dealt

    def skill2_logic(self):
        for a in self.ally:
            def value_func(char, buff_applier):
                return 0.08 * char.maxhp
            a.apply_effect(ContinuousHealEffect('Regeneration', 20, True, value_function=value_func,
                                                value_function_description="8% of maxhp",
                                                value_function_description_jp="最大HPの8%"))
            a.apply_effect(StatsEffect('Crit Def Up', 20, True, {'critdef' : 0.6}))
        return 0
        
    def skill3(self):
        pass

    def normal_attack(self):
        def freeze_effect(self, target):
            if self.atk > target.atk:
                target.apply_effect(FrozenEffect('Freeze', duration=10, is_buff=False, imposter=self))
        self.attack(func_after_dmg=freeze_effect)


class GargoyleB(Monster):
    def __init__(self, name, lvl, exp=0, equip=None, image=None):
        super().__init__(name, lvl, exp, equip, image)
        self.original_name = "GargoyleB"
        self.skill1_description = "Attack closest enemy 3 times with 210% atk."
        self.skill2_description = "Attack closest enemy 3 times with 210% atk."
        self.skill3_description = "Each skill attack and normal attack has 10% chance to petrify the target for 35 turns." \
        " Normal attack will target closest enemy."
        # PetrifyEffect
        self.skill1_description_jp = "最も近い敵に攻撃力の210%で3回攻撃する。"
        self.skill2_description_jp = "最も近い敵に攻撃力の210%で3回攻撃する。"
        self.skill3_description_jp = "各スキル攻撃および通常攻撃には、10%の確率で対象を35ターンの間「石化」させる。通常攻撃は最も近い敵を対象とする。"
        self.skill1_cooldown_max = 5
        self.skill2_cooldown_max = 5
        self.is_boss = False


    def skill1_logic(self):
        def petrify_effect(self, target):
            dice = random.randint(1, 100)
            if dice <= 10:
                target.apply_effect(PetrifyEffect('Petrify', duration=35, is_buff=False, imposter=self))
        damage_dealt = self.attack(multiplier=2.1, repeat=3, target_kw1="enemy_in_front", func_after_dmg=petrify_effect)
        return damage_dealt

    def skill2_logic(self):
        def petrify_effect(self, target):
            dice = random.randint(1, 100)
            if dice <= 10:
                target.apply_effect(PetrifyEffect('Petrify', duration=35, is_buff=False, imposter=self))
        damage_dealt = self.attack(multiplier=2.1, repeat=3, target_kw1="enemy_in_front", func_after_dmg=petrify_effect)
        return damage_dealt

    def skill3(self):
        pass

    def normal_attack(self):
        def petrify_effect(self, target):
            dice = random.randint(1, 100)
            if dice <= 10:
                target.apply_effect(PetrifyEffect('Petrify', duration=35, is_buff=False, imposter=self))
        self.attack(func_after_dmg=petrify_effect, target_kw1="enemy_in_front")


# ====================================
# End of CC: Freeze and Petrify
# ====================================
# hp　related
# ====================================

class Skeleton(Monster):
    def __init__(self, name, lvl, exp=0, equip=None, image=None):
        super().__init__(name, lvl, exp, equip, image)
        self.original_name = "Skeleton"
        self.skill1_description = "Attack enemy with highest hp with 300% atk 3 times."
        self.skill2_description = "Attack enemy with highest hp with 900% atk, 80% chance to Stun for 8 turns." \
        " Before attacking, increase accuracy by 30% for 8 turns."
        self.skill3_description = "Normal attack has 5% chance to Stun for 8 turns."
        self.skill1_description_jp = "最も高いHPの敵に攻撃力300%のダメージを3回与える。"
        self.skill2_description_jp = "最も高いHPの敵に攻撃力900%のダメージを与え、80%の確率で8ターンの間スタンを付与。" \
        "攻撃前に命中率を8ターンの間30%増加。"
        self.skill3_description_jp = "通常攻撃は5%の確率で8ターンの間スタンを付与。"
        self.skill1_cooldown_max = 5
        self.skill2_cooldown_max = 4
        self.is_boss = False

    

    def skill1_logic(self):
        damage_dealt = self.attack(multiplier=3.0, repeat=3, target_kw1="n_highest_attr", target_kw2="1", target_kw3="hp", target_kw4="enemy")
        return damage_dealt

    def skill2_logic(self):
        self.apply_effect(StatsEffect('Acc Up', 8, True, {'acc' : 0.3}))
        def stun_effect(self, target):
            dice = random.randint(1, 100)
            if dice <= 80:
                target.apply_effect(StunEffect('Stun', duration=8, is_buff=False))
        damage_dealt = self.attack(multiplier=9.0, repeat=1, func_after_dmg=stun_effect, target_kw1="n_highest_attr", target_kw2="1", target_kw3="hp", target_kw4="enemy")
        return damage_dealt
        
    def skill3(self):
        pass

    def normal_attack(self):
        def stun_effect(self, target):
            dice = random.randint(1, 100)
            if dice <= 5:
                target.apply_effect(StunEffect('Stun', duration=8, is_buff=False))
        self.attack(func_after_dmg=stun_effect)


class Ork(Monster):
    def __init__(self, name, lvl, exp=0, equip=None, image=None):
        super().__init__(name, lvl, exp, equip, image)
        self.original_name = "Ork"
        self.skill1_description = "Focus attack on enemy with lowest hp with 300% atk 2 times."
        self.skill2_description = "Focus attack on enemy with lowest hp with 300% atk 2 times."
        self.skill3_description = "Skill attack inflict both Burn and Bleed for 24 turns, deals 10% of atk as status damage per turn."
        self.skill1_description_jp = "最も低いHPの敵に攻撃力300%のダメージを2回与える。"
        self.skill2_description_jp = "最も低いHPの敵に攻撃力300%のダメージを2回与える。"
        self.skill3_description_jp = "スキル攻撃は24ターンの間燃焼と出血を付与し、毎ターン攻撃力の10%を状態ダメージとして与える。"
        self.skill1_cooldown_max = 5
        self.skill2_cooldown_max = 5
        self.is_boss = False

    

    def skill1_logic(self):
        def burn_effect(self, target):
            target.apply_effect(ContinuousDamageEffect('Burn', duration=24, is_buff=False, value=0.1 * self.atk, imposter=self))
            target.apply_effect(ContinuousDamageEffect('Bleed', duration=24, is_buff=False, value=0.1 * self.atk, imposter=self))
        damage_dealt = self.attack(multiplier=3.0, repeat_seq=2, func_after_dmg=burn_effect, target_kw1="n_lowest_attr", target_kw2="1", target_kw3="hp", target_kw4="enemy")
        return damage_dealt

    def skill2_logic(self):
        def burn_effect(self, target):
            target.apply_effect(ContinuousDamageEffect('Burn', duration=24, is_buff=False, value=0.1 * self.atk, imposter=self))
            target.apply_effect(ContinuousDamageEffect('Bleed', duration=24, is_buff=False, value=0.1 * self.atk, imposter=self))
        damage_dealt = self.attack(multiplier=3.0, repeat_seq=2, func_after_dmg=burn_effect, target_kw1="n_lowest_attr", target_kw2="1", target_kw3="hp", target_kw4="enemy")
        return damage_dealt
    
    def skill3(self):
        pass


class Minotaur(Monster):
    def __init__(self, name, lvl, exp=0, equip=None, image=None):
        super().__init__(name, lvl, exp, equip, image)
        self.original_name = "Minotaur"
        self.skill1_description = "Focus attack enemy with lowest hp with 300% atk 2 times. After attack, apply Def Up for 20 turns." \
        " Def Up: increase defense by 20%."
        self.skill2_description = "Focus attack enemy with lowest hp with 200% atk 2 times. Damage increased by 10% of target lost hp."
        self.skill3_description = "Skill damage increased by 50% if target has less than 50% hp."
        self.skill1_description_jp = "最も低いHPの敵に攻撃力300%のダメージを2回与える。攻撃後、20ターンの間防御力を20%増加。"
        self.skill2_description_jp = "最も低いHPの敵に攻撃力200%のダメージを2回与える。ダメージが対象の失ったHPの10%増加。"
        self.skill3_description_jp = "対象のHPが50%未満の場合、スキルダメージが50%増加。"
        self.skill1_cooldown_max = 4
        self.skill2_cooldown_max = 5
        self.is_boss = False

    

    def skill1_logic(self):
        def damage_increase(self, target, final_damage):
            if target.hp < target.maxhp * 0.5:
                final_damage *= 1.5
            return final_damage
        damage_dealt = self.attack(multiplier=3.0, repeat_seq=2, func_damage_step=damage_increase, target_kw1="n_lowest_attr", target_kw2="1", target_kw3="hp", target_kw4="enemy")
        if self.is_alive():
            self.apply_effect(StatsEffect('Def Up', 20, True, {'defense' : 1.2}))
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


class BlackDragon(Monster):
    """
    Can be countered by having a protector
    """
    def __init__(self, name, lvl, exp=0, equip=None, image=None):
        super().__init__(name, lvl, exp, equip, image)
        self.original_name = "BlackDragon"
        self.skill1_description = "Attack enemy with lowest hp with 340% atk 2 times and inflict Bleed for 20 turns. Bleed deals 20% of atk as status damage per turn."
        self.skill2_description = "Attack all enemies with 220% atk, inflict Burn on all enemies with hp lower than 50% for 20 turns." \
        " If target hp is lower than 25%, inflict an additional Burn for 20 turns." \
        " Burn deals 40% of atk as status damage per turn. This attack does not miss." \
        " During damage step, if target hp is lower than 50%, increase damage by 150%."
        self.skill3_description = "Increase hp by 200%"
        self.skill1_description_jp = "HPが最も低い敵に攻撃力340%のダメージを2回与え、20ターンの間出血を付与。出血は攻撃力の20%を状態ダメージとして毎ターン受ける。"
        self.skill2_description_jp = "全ての敵に攻撃力220%のダメージを与え、HPが50%未満の敵に20ターンの間燃焼を付与。" \
        "HPが25%未満の場合、追加で20ターンの間燃焼を付与。燃焼は攻撃力の40%を状態ダメージとして毎ターン受ける。" \
        "ダメージ計算時、対象のHPが50%未満の場合、ダメージが150%増加。"
        self.skill3_description_jp = "最大HPを200%増加。"
        self.skill1_cooldown_max = 4
        self.skill2_cooldown_max = 4
        self.is_boss = True

    

    def skill1_logic(self):
        def bleed_effect(self, target):
            target.apply_effect(ContinuousDamageEffect('Bleed', duration=20, is_buff=False, value=0.2 * self.atk, imposter=self))
        damage_dealt = self.attack(multiplier=3.4, repeat_seq=2, func_after_dmg=bleed_effect, target_kw1="n_lowest_attr", target_kw2="1", target_kw3="hp", target_kw4="enemy")
        return damage_dealt

    def skill2_logic(self):
        def burn_effect(self, target):
            if target.hp < target.maxhp * 0.5:
                target.apply_effect(ContinuousDamageEffect('Burn', duration=20, is_buff=False, value=0.4 * self.atk, imposter=self))
            if target.hp < target.maxhp * 0.25:
                target.apply_effect(ContinuousDamageEffect('Burn', duration=20, is_buff=False, value=0.4 * self.atk, imposter=self))
        def burn_damage_increase(self, target, final_damage):
            if target.hp < target.maxhp * 0.5:
                final_damage *= 2.5
            return final_damage
        damage_dealt = self.attack(multiplier=2.2, repeat=1, func_after_dmg=burn_effect, target_kw1="n_random_enemy", 
                                   target_kw2="5", always_hit=True, func_damage_step=burn_damage_increase)
        return damage_dealt

    def skill3(self):
        pass

    def battle_entry_effects(self):
        self.apply_effect(StatsEffect('BlackDragon Passive', -1, True, {'maxhp' : 3.0}, can_be_removed_by_skill=False))
        self.hp = self.maxhp


class BakeNeko(Monster):
    def __init__(self, name, lvl, exp=0, equip=None, image=None):
        super().__init__(name, lvl, exp, equip, image)
        self.original_name = "BakeNeko"
        self.skill1_description = "Increase maxhp by 15% for all allies for 24 turns and Heal all allies by 300% atk."
        self.skill2_description = "Heal 1 ally with lowest hp by 200% atk." \
        " Apply Supression on all allies for 10 turns. Supression: During damage calculation," \
        " damage increased by the ratio of self hp to target hp if self has more hp than target. Max bonus damage: 1000%."
        self.skill3_description = "Increase maxhp and def by 20%, evasion by 15%."
        self.skill1_description_jp = "全ての味方の最大HPを24ターンの間15%増加させ、全ての味方に攻撃力300%分のHPを回復。"
        self.skill2_description_jp = "最も低いHPの味方に攻撃力200%分のHPを回復。全ての味方に10ターンの間制圧を付与。" \
        "抑制:ダメージ計算時、自分のHPが対象のHPより多い場合、自分のHPと対象のHPの比率に応じてダメージが増加。最大ボーナスダメージ:1000%。"
        self.skill3_description_jp = "最大HPと防御力を20%、回避率を15%増加。"
        self.skill1_cooldown_max = 5
        self.skill2_cooldown_max = 4
        self.is_boss = False

    

    def skill1_logic(self):
        for a in self.ally:
            a.apply_effect(StatsEffect('Maxhp Up', 20, True, {'maxhp' : 1.15}))
        self.heal("n_random_ally", "5", value=3.0 * self.atk)

    def skill2_logic(self):
        self.heal("n_lowest_attr", "1", "hp", "ally", value=2.0 * self.atk)
        for a in self.ally:
            a.apply_effect(BakeNekoSupressionEffect('Supression', 10, True))
    
    def skill3(self):
        pass

    def battle_entry_effects(self):
        self.apply_effect(StatsEffect('BakeNeko Passive', -1, True, {'maxhp' : 1.2, 'defense' : 1.2, 'eva' : 0.15}, can_be_removed_by_skill=False))
        self.hp = self.maxhp


class Biobird(Monster):
    def __init__(self, name, lvl, exp=0, equip=None, image=None):
        super().__init__(name, lvl, exp, equip, image)
        self.original_name = "Biobird"
        self.skill1_description = "Attack closest enemy with 400% atk 2 times, 35% chance to inflict Def Down for 24 turns, def is decreased by 10%." \
        " 25% chance to remove a active buff from target."
        self.skill2_description = "Attack closest enemy with 400% atk 2 times. If hp is below 20%, for 20 turns," \
        " Increase maxhp by 40% and recover 4% of maxhp each turn."
        self.skill3_description = "Skill damage increased by 100% if hp is below 20%."
        self.skill1_description_jp = "最も近い敵に攻撃力400%のダメージを2回与え、35%の確率で24ターンの間防御力を10%減少。" \
        "25%の確率で対象のアクティブバフを1つ解除する。"
        self.skill2_description_jp = "最も近い敵に攻撃力400%のダメージを2回与える。攻撃後、自分のHPが20%未満の場合、20ターンの間最大HPを40%増加し、毎ターン最大HPの4%を回復。"
        self.skill3_description_jp = "HPが20%未満の場合、スキルダメージが100%増加。"
        self.skill1_cooldown_max = 5
        self.skill2_cooldown_max = 4
        self.is_boss = False

    

    def skill1_logic(self):
        def def_down(self, target: character.Character):
            if random.random() < 0.35:
                target.apply_effect(StatsEffect('Def Down', 24, False, {'defense' : 0.9}))
            if random.random() < 0.25:
                target.remove_random_amount_of_buffs(1)

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
            self.apply_effect(StatsEffect('Maxhp Up', 20, True, {'maxhp' : 1.4}))
            self.apply_effect(ContinuousHealEffect('Regen', 20, True, lambda x, y: x.maxhp * 0.04, self, "4% of maxhp",
                                                   value_function_description_jp="最大HPの4%"))
        return damage_dealt

    def skill3(self):
        pass


class Captain(Monster):
    def __init__(self, name, lvl, exp=0, equip=None, image=None):
        super().__init__(name, lvl, exp, equip, image)
        self.original_name = "Captain"
        self.skill1_description = "Attack 1 enemy with highest hp percentage with 320% atk 2 times, if target is at full hp," \
        " damage is increased by 100% and apply Def Down for 24 turns, def is decreased by 10%."
        self.skill2_description = "Attack 1 enemy with lowest hp percentage with 320% atk 2 times, if target is at full hp," \
        " damage is increased by 200% and apply Heal Reduced for 24 turns, heal efficiency is reduced by 10%."
        self.skill3_description = "Normal attack attacks 2 times."
        self.skill1_description_jp = "最も高いHP割合の敵に攻撃力320%のダメージを2回与え、対象がHP満タンの場合、ダメージが100%増加し、24ターンの間防御力を10%減少させる。"
        self.skill2_description_jp = "最も低いHP割合の敵に攻撃力320%のダメージを2回与え、対象がHP満タンの場合、ダメージが200%増加し、24ターンの間回復効率を10%減少させる。"
        self.skill3_description_jp = "通常攻撃は2回攻撃する。"
        self.skill1_cooldown_max = 5
        self.skill2_cooldown_max = 4
        self.is_boss = False
        self.skill1_add_def_down = False
        self.skill2_add_unhealable = False

    def clear_others(self):
        self.skill1_add_def_down = False
        self.skill2_add_unhealable = False
        super().clear_others()

    

    def skill1_logic(self):
        def def_down(self, target):
            if self.skill1_add_def_down:
                target.apply_effect(StatsEffect('Def Down', 24, False, {'defense' : 0.9}))
                self.skill1_add_def_down = False
            else:
                pass
        def full_hp(self, target, final_damage):
            if target.hp == target.maxhp:
                final_damage *= 2.0
                self.skill1_add_def_down = True
            return final_damage
        damage_dealt = self.attack(multiplier=3.2, repeat=2, func_after_dmg=def_down, func_damage_step=full_hp, target_kw1="n_highest_hp_percentage_enemy", target_kw2="1")
        return damage_dealt

    def skill2_logic(self):
        def unhealable(self, target):
            if self.skill2_add_unhealable:
                target.apply_effect(StatsEffect('Heal Reduced', 24, False, {"heal_efficiency": -0.1}))
                self.skill2_add_unhealable = False
            else:
                pass
        def full_hp(self, target, final_damage):
            if target.hp == target.maxhp:
                final_damage *= 3.0
                self.skill2_add_unhealable = True
            return final_damage
        damage_dealt = self.attack(multiplier=3.2, repeat=2, func_after_dmg=unhealable, func_damage_step=full_hp, target_kw1="n_lowest_hp_percentage_enemy", target_kw2="1")
        return damage_dealt

        
    def skill3(self):
        pass

    def normal_attack(self):
        self.attack(repeat=2)


# ====================================
# End of hp related
# ====================================
# Maxhp related
# ====================================



class Wizard(Monster):
    def __init__(self, name, lvl, exp=0, equip=None, image=None):
        super().__init__(name, lvl, exp, equip, image)
        self.original_name = "Wizard"
        self.skill1_description = "Poison all enemies for 20 turns. Poison: takes 2% of lost hp status damage per turn."
        self.skill2_description = "Poison all enemies for 20 turns. Poison: takes 1% of maxhp status damage per turn."
        self.skill3_description = "Normal attack deals 100% more damage to poisoned enemies."
        self.skill1_description_jp = "全ての敵に20ターンの間毒を付与。毒:失ったHPの2%を状態ダメージとして毎ターン受ける。"
        self.skill2_description_jp = "全ての敵に20ターンの間毒を付与。毒:最大HPの1%を状態ダメージとして毎ターン受ける。"
        self.skill3_description_jp = "通常攻撃は毒状態の敵に100%追加ダメージを与える。"
        self.skill1_cooldown_max = 5
        self.skill2_cooldown_max = 5
        self.is_boss = False

    

    def skill1_logic(self):
        for e in self.enemy:
            e.apply_effect(ContinuousDamageEffect_Poison('Poison', duration=20, is_buff=False, ratio=0.02, imposter=self, base="losthp"))

    def skill2_logic(self):
        for e in self.enemy:
            e.apply_effect(ContinuousDamageEffect_Poison('Poison', duration=20, is_buff=False, ratio=0.01, imposter=self, base="maxhp"))
        
    def skill3(self):
        pass

    def normal_attack(self):
        def poison_damage(self, target, final_damage):
            if target.has_effect_that_named("Poison"):
                final_damage *= 2.0
            return final_damage
        self.attack(func_damage_step=poison_damage)


class WizardB(Monster):
    def __init__(self, name, lvl, exp=0, equip=None, image=None):
        super().__init__(name, lvl, exp, equip, image)
        self.original_name = "WizardB"
        self.skill1_description = "Poison all enemies for 24 turns. Poison: takes 1% of lost hp status damage per turn." \
        " Reduce their evasion by 110% for 16 turns."
        self.skill2_description = "Attack random enemies 5 times with 200% atk, damage increased by 4% of target maxhp."
        self.skill3_description = "Normal attack deals additional damage by 1.5% of target maxhp."
        self.skill1_description_jp = "全ての敵に24ターンの間毒を付与。毒:失ったHPの1%を状態ダメージとして毎ターン受ける。" \
        "回避率を16ターンの間110%減少。"
        self.skill2_description_jp = "全ての敵に攻撃力200%で5回攻撃し、ダメージは対象の最大HPの4%を追加する。"
        self.skill3_description_jp = "通常攻撃ダメージは対象の最大HPの1.5%追加する。"
        self.skill1_cooldown_max = 4
        self.skill2_cooldown_max = 5
        self.is_boss = False

    

    def skill1_logic(self):
        for e in self.enemy:
            e.apply_effect(ContinuousDamageEffect_Poison('Poison', duration=24, is_buff=False, ratio=0.01, imposter=self, base="losthp"))
            e.apply_effect(StatsEffect('Eva Down', 16, False, {'eva' : -1.1}))

    def skill2_logic(self):
        def maxhp_damage(self, target, final_damage):
            final_damage += 0.04 * target.maxhp
            return final_damage
        self.attack(multiplier=2.0, repeat=5, func_damage_step=maxhp_damage)
        
    def skill3(self):
        pass

    def normal_attack(self):
        def maxhp_damage(self, target, final_damage):
            final_damage += 0.015 * target.maxhp
            return final_damage
        self.attack(func_damage_step=maxhp_damage)


class General(Monster):
    """
    Can be countered by Cosmic eq set
    """
    def __init__(self, name, lvl, exp=0, equip=None, image=None):
        super().__init__(name, lvl, exp, equip, image)
        self.original_name = "General"
        self.skill1_description = "Attack 1 closest enemy with 300% atk 3 times, if target has lower maxhp than you,"
        " damage is increased by 40%, inflict Bleed for 20 turns. Bleed deals 50% of atk as status damage per turn."
        self.skill2_description = "Attack enemy of lowest hp percentage with 655% atk and inflict Destroy for 30 turns." \
        " Destroy: maxhp is reduced to current hp. This effect cannot be removed."
        self.skill3_description = "Before using a skill, heal hp by 400% atk. If hp is full before healing, increase atk and def by 30% for 10 turns."
        self.skill1_description_jp = "最も近い敵に攻撃力300%のダメージを3回与え、対象の最大HPが自分より低い場合、" \
        "ダメージが40%増加し、20ターンの間出血を付与。出血は攻撃力の50%を状態ダメージとして毎ターン受ける。"
        self.skill2_description_jp = "最も低いHP割合の敵に攻撃力655%のダメージを与え、30ターンの間壊滅を付与。" \
        "壊滅:最大HPが現在のHPに減少。この効果は解除されない。"
        self.skill3_description_jp = "スキル使用前に攻撃力400%分のHPを回復。HPが満タンの場合、10ターンの間攻撃力と防御力を30%増加。"
        self.skill1_cooldown_max = 3
        self.skill2_cooldown_max = 4
        self.is_boss = True

    

    def skill1_logic(self):
        if self.hp == self.maxhp:
            self.apply_effect(StatsEffect('Strong', 10, True, {'atk' : 1.3, 'defense' : 1.3}))
        self.heal_hp(4.0 * self.atk, self)
        def bleed_effect(self, target):
            target.apply_effect(ContinuousDamageEffect('Bleed', duration=20, is_buff=False, value=0.5 * self.atk, imposter=self))
        def maxhp_damage(self, target, final_damage):
            if target.maxhp < self.maxhp:
                final_damage *= 1.4
            return final_damage
        damage_dealt = self.attack(multiplier=3.0, repeat=3, func_after_dmg=bleed_effect, func_damage_step=maxhp_damage, target_kw1="enemy_in_front")
        return damage_dealt


    def skill2_logic(self):
        if self.hp == self.maxhp:
            self.apply_effect(StatsEffect('Strong', 10, True, {'atk' : 1.3, 'defense' : 1.3}))
        self.heal_hp(4.0 * self.atk, self)
        def destroy_effect(self, target):
            destory = StatsEffect('Destroy', 30, False, {'maxhp' : max(target.hp / target.maxhp, 0.01)})
            destory.apply_rule = "stack"
            destory.can_be_removed_by_skill = False
            if target.is_alive():
                target.apply_effect(destory)
        damage_dealt = self.attack(multiplier=6.55, repeat=1, func_after_dmg=destroy_effect, target_kw1="n_lowest_hp_percentage_enemy", target_kw2="1")
        return damage_dealt

        
    def skill3(self):
        pass


# ====================================
# End of Maxhp related
# ====================================
# spd related
# ====================================

class Merman(Monster):
    def __init__(self, name, lvl, exp=0, equip=None, image=None):
        super().__init__(name, lvl, exp, equip, image)
        self.original_name = "Merman"
        self.skill1_description = "Target 1 enemy with the lowest speed, attack 3 times with 250% atk."
        self.skill2_description = "Target 1 enemy of lowest speed, if it is the same enemy as in skill 1, attack 3 times with 250% atk and Stun the target for 8 turns. This skill has no effect otherwise."
        self.skill3_description = "Normal attack attacks 2 times, each attack has a 40% chance to remove 1 active buff from the target."
        self.skill1_description_jp = "最も低い速度の敵を対象に、攻撃力250%のダメージを3回与える。"
        self.skill2_description_jp = "最も低い速度の敵を対象に、スキル1と同じ敵の場合、攻撃力250%のダメージを3回与え、対象を8ターンの間スタンさせる。" \
        "それ以外の場合、このスキルは効果がない。"
        self.skill3_description_jp = "通常攻撃は2回攻撃する。各攻撃に40%確率で対象からアクティブなバフを1つ解除する。"
        self.skill1_cooldown_max = 5
        self.skill2_cooldown_max = 5
        self.is_boss = False
        self.s1target = None

    

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
                    target.apply_effect(StunEffect('Stun', duration=8, is_buff=False))
                damage_dealt = self.attack(multiplier=2.5, repeat=3, target_list=l, func_after_dmg=stun_effect)
                return damage_dealt
            else:
                return 0

    def skill3(self):
        pass

    def normal_attack(self):
        def remove_buff(self, target: character.Character):
            if random.random() < 0.4:
                target.remove_random_amount_of_buffs(1, False)
        self.attack(repeat=2, func_after_dmg=remove_buff)


class Wyvern(Monster):
    def __init__(self, name, lvl, exp=0, equip=None, image=None):
        super().__init__(name, lvl, exp, equip, image)
        self.original_name = "Wyvern"
        self.skill1_description = "Attack 3 closest enemies 2 times and deal 265% atk. For 70% chance each attack, reduce target spd by 10% for 18 turns."
        self.skill2_description = "Attack closest enemy with 200% atk, if target has lower spd than you, deal 120% more damage and reduce target spd by 10% for 18 turns."
        self.skill3_description = "Increase spd by 20%. Nearby allies have their spd increased by 20% for 15 turns."
        self.skill1_description_jp = "最も近い敵に攻撃力265%のダメージを2回与える。各攻撃につき、70%の確率で対象の速度18ターンで10%減少させる。"
        self.skill2_description_jp = "最も近い敵に攻撃力200%のダメージを与え、対象の速度が自分より低い場合、ダメージが120%増加し、対象の速度を18ターンで10%減少させる。"
        self.skill3_description_jp = "速度を20%増加。周囲の味方の速度を15ターンで20%増加。"
        self.skill1_cooldown_max = 4
        self.skill2_cooldown_max = 5
        self.is_boss = False

    

    def skill1_logic(self):
        def slow_effect(self, target):
            dice = random.randint(1, 100)
            if dice <= 70:
                target.apply_effect(StatsEffect('Slow', duration=18, is_buff=False, stats_dict={'spd' : 0.9}))
        damage_dealt = self.attack(multiplier=2.65, repeat_seq=2, func_after_dmg=slow_effect, target_kw1="n_enemy_in_front", target_kw2="3")
        return damage_dealt

    def skill2_logic(self):
        def slow_effect(self, target):
            if target.spd < self.spd:
                target.apply_effect(StatsEffect('Slow', duration=18, is_buff=False, stats_dict={'spd' : 0.9}))
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


class Agent(Monster):
    def __init__(self, name, lvl, exp=0, equip=None, image=None):
        super().__init__(name, lvl, exp, equip, image)
        self.original_name = "Agent"
        self.skill1_description = "Attack 1 enemy with lowest spd with 330% atk 3 times, each attack has 100% chance to inflict Bleed for 30 turns. Bleed deals 16% of atk as status damage per turn."
        self.skill2_description = "Increase evasion and accuracy by 20% for 17 turns."
        self.skill3_description = "Normal attack target enemy with lowest spd and deals 100% more damage."
        self.skill1_description_jp = "最も低い速度の敵を対象に、攻撃力330%のダメージを3回与え、各攻撃に100%の確率で出血を付与。出血は攻撃力の16%を状態ダメージとして毎ターン受ける。"
        self.skill2_description_jp = "回避率と命中率を17ターンで20%増加。"
        self.skill3_description_jp = "通常攻撃は最も低い速度の敵を対象に、100%追加ダメージを与える。"
        self.skill1_cooldown_max = 4
        self.skill2_cooldown_max = 5
        self.is_boss = False

    

    def skill1_logic(self):
        def bleed_effect(self, target):
            target.apply_effect(ContinuousDamageEffect('Bleed', duration=30, is_buff=False, value=0.16 * self.atk, imposter=self))
        damage_dealt = self.attack(multiplier=3.3, repeat=3, func_after_dmg=bleed_effect, target_kw1="n_lowest_attr", target_kw2="1", target_kw3="spd", target_kw4="enemy")
        return damage_dealt

    def skill2_logic(self):
        self.apply_effect(StatsEffect('Ready Up', 17, True, {'eva' : 0.2, 'acc' : 0.2}))
        return 0

    def skill3(self):
        pass

    def normal_attack(self):
        def damage_increase(self, target, final_damage):
            final_damage *= 2.0
            return final_damage
        self.attack(func_damage_step=damage_increase, target_kw1="n_lowest_attr", target_kw2="1", target_kw3="spd", target_kw4="enemy")


class Windspirit(Monster):
    def __init__(self, name, lvl, exp=0, equip=None, image=None):
        super().__init__(name, lvl, exp, equip, image)
        self.original_name = "Windspirit"
        self.skill1_description = "For 24 turns, all allies gain speed equal to 10% of your speed."
        self.skill2_description = "Attack all enemies with 200% atk, damage increased by 100% if target has lower spd than you. 50%" \
        " chance to inflict Spd Down for 20 turns, spd is decreased by 5%."
        self.skill3_description = "Increase spd by 20%, crit rate by 20%."
        self.skill1_description_jp = "24ターンの間、味方全員の速度を自分の速度の10%分増加。"
        self.skill2_description_jp = "全ての敵に攻撃力200%で攻撃し、対象の速度が自分より低い場合、ダメージが100%増加。50%の確率で20ターンの間速度を5%減少させる。"
        self.skill3_description_jp = "速度を20%増加。クリティカル率を20%増加。"
        self.skill1_cooldown_max = 5
        self.skill2_cooldown_max = 5
        self.is_boss = False

    

    def skill1_logic(self):
        for a in self.ally:
            a.apply_effect(StatsEffect('Wind', 24, True, main_stats_additive_dict={'spd' : self.spd * 0.1}))
        return 0

    def skill2_logic(self):
        def spd_penalty(self, target, final_damage):
            if target.spd < self.spd:
                final_damage *= 2.0
            return final_damage
        def spd_down(self, target):
            if random.random() < 0.5:
                target.apply_effect(StatsEffect('Against Wind', 20, False, {'spd' : 0.95}))
        damage_dealt = self.attack(multiplier=2.0, repeat=1, func_damage_step=spd_penalty, target_kw1="n_random_enemy", target_kw2="5", 
                                   func_after_dmg=spd_down)
        return damage_dealt

    def skill3(self):
        pass

    def battle_entry_effects(self):
        self.apply_effect(StatsEffect('Windspirit Passive', -1, True, {'spd' : 1.2, 'crit' : 0.2}, can_be_removed_by_skill=False))


# ====================================
# End of spd related
# ====================================
# Crit related
# ====================================


class SoldierB(Monster):
    def __init__(self, name, lvl, exp=0, equip=None, image=None):
        super().__init__(name, lvl, exp, equip, image)
        self.original_name = "SoldierB"
        self.skill1_description = "Attack random enemies 4 times with 300% atk."
        self.skill2_description = "Attack random enemies 4 times with 270% atk, each attack will trigger the same attack if critical."
        self.skill3_description = "Increase critical rate and critical damage by 30%."
        self.skill1_description_jp = "ランダムな敵に攻撃力300%のダメージを4回与える。"
        self.skill2_description_jp = "ランダムな敵に攻撃力270%のダメージを4回与え、各攻撃がクリティカルの場合、同じ攻撃が発動する。"
        self.skill3_description_jp = "クリティカル率とクリティカルダメージを30%増加。"
        self.skill1_cooldown_max = 5
        self.skill2_cooldown_max = 5
        self.is_boss = False

    

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


class Queen(Monster):
    """
    Can be countered by character like Tian, who decrease crit rate
    """
    def __init__(self, name, lvl, exp=0, equip=None, image=None):
        super().__init__(name, lvl, exp, equip, image)
        self.original_name = "Queen"
        self.skill1_description = "Attack random ememies with 230% atk 8 times, after each successful attack, increase critical damage by 80% for 3 turns."
        self.skill2_description = "Attack 3 front enemies with 300% atk, decrease their critical defense by 10%, for 24 turns. After this skill, increase critical damage by 80% for 6 turns."
        self.skill3_description = "Critical chance is increased by 60%. Speed is increased by 20%."
        self.skill1_description_jp = "ランダムな敵に230%の攻撃力で8回攻撃し、各攻撃後、3ターンの間クリティカルダメージを80%増加。"
        self.skill2_description_jp = "最も近い3体敵に攻撃力300%で攻撃し、クリティカル防御を24ターンで10%減少させる。このスキル後、6ターンの間クリティカルダメージを80%増加。"
        self.skill3_description_jp = "クリティカル率を60%増加。速度を20%増加。"
        self.skill1_cooldown_max = 5
        self.skill2_cooldown_max = 3
        self.is_boss = True

    

    def skill1_logic(self):
        def critdmg_increase(self, target):
            self.apply_effect(StatsEffect('Control', 3, True, {'critdmg' : 0.80}))
        damage_dealt = self.attack(multiplier=2.3, repeat=8, func_after_dmg=critdmg_increase)
        return damage_dealt

    def skill2_logic(self):
        def critdef_decrease(self, target):
            target.apply_effect(StatsEffect('Compliance', 24, False, {'critdef' : -0.1}))
        damage_dealt = self.attack(multiplier=3.0, repeat=1, func_after_dmg=critdef_decrease, target_kw1="n_enemy_in_front", target_kw2="3")
        if self.is_alive():
            self.apply_effect(StatsEffect('Control', 6, True, {'critdmg' : 0.80}))
        return damage_dealt

    def skill3(self):
        pass

    def battle_entry_effects(self):
        self.apply_effect(StatsEffect('Queen Passive', -1, True, {'crit' : 0.6, 'spd' : 1.2}, can_be_removed_by_skill=False))


class KungFuA(Monster):
    """
    Counter: Character with low crit defense but tanky
    Anti crit character like Tian
    """
    def __init__(self, name, lvl, exp=0, equip=None, image=None):
        super().__init__(name, lvl, exp, equip, image)
        self.original_name = "KungFuA"
        self.skill1_description = "Focus attack on enemy with lowest crit defense with 260% atk 4 times, each attack increases" \
        " self crit rate and critdmg by 12% and decrease target crit defense by 12% for 24 turns."
        self.skill2_description = "For 2 turns, increase critdmg by 100%, focus attack on enemy with lowest crit defense with 440% atk 2 times."
        self.skill3_description = "Increase accuracy and crit rate by 40%, all allies have increased accuracy by 20%."
        self.skill1_description_jp = "最も低いクリティカル防御の敵に攻撃力260%のダメージを4回与え、各攻撃後、24ターンの間、自分のクリティカル率とクリティカルダメージを12%増加し、対象のクリティカル防御を12%減少させる。"
        self.skill2_description_jp = "2ターンの間、クリティカルダメージを100%増加。最も低いクリティカル防御の敵に攻撃力440%で攻撃する。"
        self.skill3_description_jp = "命中率とクリティカル率を40%増加。周囲の味方の命中率を20%増加。"
        self.skill1_cooldown_max = 4
        self.skill2_cooldown_max = 4
        self.is_boss = True

    

    def skill1_logic(self):
        def critdmg_increase(self, target):
            self.apply_effect(StatsEffect('Crit Up', 24, True, {'critdmg' : 0.12, 'crit' : 0.12}))
            target.apply_effect(StatsEffect('Critdef Down', 24, False, {'critdef' : -0.12}))
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


class PaladinB(Monster):
    def __init__(self, name, lvl, exp=0, equip=None, image=None):
        super().__init__(name, lvl, exp, equip, image)
        self.original_name = "PaladinB"
        self.skill1_description = "Neighboring allies have their crit defense increased by 25% for 30 turns."
        self.skill2_description = "Attack 1 closest enemy 3 times with 300% atk, each attack decreases target crit rate by 20% for 22 turns." \
        " Recover hp by 100% of damage dealt."
        self.skill3_description = "Protect all allies. Damage taken is reduced 20%, 40% of damage taken is redirected to you."
        self.skill1_description_jp = "隣接する味方のクリティカル防御を30ターンで25%増加。"
        self.skill2_description_jp = "最も近い敵に攻撃力300%で3回攻撃し、各攻撃で対象のクリティカル率を22ターンで20%減少させる。" \
        "与えたダメージの100%を回復。"
        self.skill3_description_jp = "全ての味方を保護する。受けるダメージを20%減少し、味方が受けたダメージの40%を自分が受ける。"
        self.skill1_cooldown_max = 5
        self.skill2_cooldown_max = 5
        self.is_boss = False

    

    def skill1_logic(self):
        for neighbor in self.get_neighbor_allies_not_including_self():
            neighbor.apply_effect(StatsEffect('Crit Def Up', 30, True, {'critdef' : 0.25}))
        return 0

    def skill2_logic(self):
        def crit_down(self, target):
            target.apply_effect(StatsEffect('Crit Down', 22, False, {'crit' : -0.2}))
        damage_dealt = self.attack(multiplier=3.0, repeat=3, func_after_dmg=crit_down, target_kw1="enemy_in_front")
        if self.is_alive():
            self.heal_hp(damage_dealt * 1, self)
        return damage_dealt

        
    def skill3(self):
        pass

    def battle_entry_effects(self):
        allies = [x for x in self.ally if x != self]
        for ally in allies:
            e = ProtectedEffect("Royal Guard", -1, True, False, self, 0.80, 0.4)
            e.additional_name = "PaladinB_RoyalGuard"
            e.can_be_removed_by_skill = False
            ally.apply_effect(e)

         
class Bat(Monster):
    def __init__(self, name, lvl, exp=0, equip=None, image=None):
        super().__init__(name, lvl, exp, equip, image)
        self.original_name = "Bat"
        self.skill1_description = "Increase crit rate by 10% and crit damage by 60% for 20 turns."
        self.skill2_description = "Attack random ememy with 300% atk 3 times, 90% chance to poison the target for 3 turns," \
        " poison deals 2% of losthp as status damage per turn. Each attack has a 40% chance to remove 1 active buff from the target."
        self.skill3_description = "Normal attack deals 50% more damage."
        self.skill1_description_jp = "20ターンの間クリティカル率が10%、クリティカルダメージ60%増加。"
        self.skill2_description_jp = "ランダムな敵に攻撃力300%で3回攻撃し、90%の確率で対象に3ターンの間毒を付与。毒は失ったHPの2%を状態ダメージとして毎ターン受ける。" \
        "各攻撃に40%の確率で対象からアクティブなバフを1つ解除する。"
        self.skill3_description_jp = "通常攻撃ダメージは50%増加する。"
        self.skill1_cooldown_max = 3
        self.skill2_cooldown_max = 4
        self.is_boss = False

    

    def skill1_logic(self):
        self.apply_effect(StatsEffect('Bad Bat', 20, True, {'crit' : 0.1, 'critdmg' : 0.6}))
        return 0

    def skill2_logic(self):
        def poison_effect(self, target):
            if random.random() < 0.9:
                target.apply_effect(ContinuousDamageEffect_Poison('Poison', duration=3, is_buff=False, ratio=0.02, imposter=self, base="losthp"))
            if random.random() < 0.4:
                target.remove_random_amount_of_buffs(1, False)
        damage_dealt = self.attack(multiplier=3.0, repeat=3, func_after_dmg=poison_effect)
        return damage_dealt

    def skill3(self):
        pass

    def normal_attack(self):
        def damage_increase(self, target, final_damage):
            final_damage *= 1.5
            return final_damage
        self.attack(func_damage_step=damage_increase)


class Killerfish(Monster):
    def __init__(self, name, lvl, exp=0, equip=None, image=None):
        super().__init__(name, lvl, exp, equip, image)
        self.original_name = "Killerfish"
        self.skill1_description = "Attack 3 closest enemies with 500% atk, their crit defense is decreased by 25% for 24 turns."
        self.skill2_description = "For 20 turns, reduce atk and damage taken by 16%."
        self.skill3_description = "Increase crit rate by 100% if hp is more than 50%."
        self.skill1_description_jp = "最も近い3体の敵に攻撃力500%で攻撃し、対象のクリティカル防御を24ターンで25%減少。"
        self.skill2_description_jp = "20ターンの間、攻撃力と受けるダメージを16%減少。"
        self.skill3_description_jp = "HPが50%以上の場合、クリティカル率を100%増加。"
        self.skill1_cooldown_max = 4
        self.skill2_cooldown_max = 4
        self.is_boss = False

    

    def skill1_logic(self):
        def critdef_down(self, target):
            target.apply_effect(StatsEffect('Critdef Down', 24, False, {'critdef' : -0.25}))
        damage_dealt = self.attack(multiplier=5.0, repeat=1, func_after_dmg=critdef_down, target_kw1="n_enemy_in_front", target_kw2="3")
        return damage_dealt

    def skill2_logic(self):
        self.apply_effect(StatsEffect('Dive', 20, True, {'atk' : 0.84, 'final_damage_taken_multipler' : -0.16}))
        return 0

    def skill3(self):
        pass

    def battle_entry_effects(self):
        condiction_func = lambda x: x.hp > x.maxhp * 0.5
        self.apply_effect(StatsEffect('Killerfish Passive', -1, True, {'crit' : 1.0}, can_be_removed_by_skill=False,
                                        condition=condiction_func))


class Dryad(Monster):
    """
    Can be countered by non crit damage or heal block
    """
    def __init__(self, name, lvl, exp=0, equip=None, image=None):
        super().__init__(name, lvl, exp, equip, image)
        self.original_name = "Dryad"
        self.skill1_description = "Attack all enemies with 360% atk, 80% chance to reduce their crit rate by 30% for 26 turns."
        self.skill2_description = "Heal all allies by 340% of atk, 80% chance to increase their crit defense by 70% for 26 turns."
        self.skill3_description = "Increase maxhp by 100%. Every time you take critical damage, recover hp by 400% of atk."
        self.skill1_description_jp = "全ての敵に攻撃力360%で攻撃し、80%の確率で対象のクリティカル率を26ターンで40%減少。"
        self.skill2_description_jp = "全ての味方を攻撃力340%で回復し、80%の確率で味方のクリティカル防御を26ターンで80%増加。"
        self.skill3_description_jp = "最大HPを100%増加。クリティカルダメージを受けるたび、攻撃力の400%でHPを回復。"
        self.skill1_cooldown_max = 4
        self.skill2_cooldown_max = 4
        self.is_boss = True

    

    def skill1_logic(self):
        def critrate_down(self, target):
            if random.random() < 0.8:
                target.apply_effect(StatsEffect('Critrate Down', 26, False, {'crit' : -0.4}))
        damage_dealt = self.attack(multiplier=3.6, repeat=1, func_after_dmg=critrate_down, target_kw1="n_random_enemy", target_kw2="5")
        return damage_dealt


    def skill2_logic(self):
        allies = self.target_selection(keyword="n_random_ally", keyword2="5")
        for ally in allies:
            ally.heal_hp(self.atk * 3.4, self)
            if random.random() < 0.8:
                ally.apply_effect(StatsEffect('Critdef Up', 26, True, {'critdef' : 0.8}))
        return 0


    def skill3(self):
        pass

    def battle_entry_effects(self):
        self.apply_effect(StatsEffect('Dryad Passive', -1, True, {'maxhp' : 2.0}, can_be_removed_by_skill=False))
        heal_on_crit = lambda x: x.atk * 4.0
        e = EffectShield1_healoncrit('Tranquility', -1, True, 1.0, heal_on_crit, cc_immunity=False,
                                     effect_applier=self)
        e.can_be_removed_by_skill = False
        self.apply_effect(e)
        self.hp = self.maxhp


# ====================================
# End of Crit related
# ====================================
# Defence & Mitigation
# ====================================
        

class Paladin(Monster):
    def __init__(self, name, lvl, exp=0, equip=None, image=None):
        super().__init__(name, lvl, exp, equip, image)
        self.original_name = "Paladin"
        self.skill1_description = "Attack 1 closest enemy with 800% atk."
        self.skill2_description = "Attack 1 closest enemy 3 times with 300% atk."
        self.skill3_description = "When taking damage and damage is exceed 10% of maxhp, reduce damage taken by 50%. The attacker takes 30% of damage reduced."
        self.skill1_description_jp = "最も近い敵に攻撃力800%で攻撃。"
        self.skill2_description_jp = "最も近い敵に攻撃力300%で3回攻撃。"
        self.skill3_description_jp = "ダメージを受け、ダメージが最大HPの10%を超える場合、受けるダメージを50%減少。減少したダメージの30%を相手に反射する。"
        self.skill1_cooldown_max = 5
        self.skill2_cooldown_max = 5
        self.is_boss = False

    

    def skill1_logic(self):
        damage_dealt = self.attack(multiplier=8.0, repeat=1, target_kw1="enemy_in_front")
        return damage_dealt

    def skill2_logic(self):
        damage_dealt = self.attack(multiplier=3.0, repeat=3, target_kw1="enemy_in_front")
        return damage_dealt
        
    def skill3(self):
        pass

    def battle_entry_effects(self):
        shield = EffectShield2('Shielded', -1, True, False, damage_reduction=0.5, shrink_rate=0, hp_threshold=0.1, 
                               damage_reflect_function=lambda x: x * 0.3, damage_reflect_description="Reflect 30% of damage reduced.",
                               damage_reflect_description_jp="減少したダメージの30%を相手に反射する.")
        shield.can_be_removed_by_skill = False
        self.apply_effect(shield)
         

class Father(Monster):
    def __init__(self, name, lvl, exp=0, equip=None, image=None):
        super().__init__(name, lvl, exp, equip, image)
        self.original_name = "Father"
        self.skill1_description = "Apply Cancellation Shield on 3 allies with lowest hp, all damage lower than 10% of maxhp is reduced to 0. Shield last 4 turns and provide 4 uses."
        self.skill2_description = "Attack 3 closest enemies with 450% atk."
        self.skill3_description = "All damage taken is reduced by 20%, damage taken lower than 10% of maxhp is reduced to 0 for 300 times."
        self.skill1_description_jp = "最も低いHPの3体の味方にキャンセルシールドを付与。最大HPの10%以下のダメージは0になる。シールドは4ターン持続し、4回使用可能。"
        self.skill2_description_jp = "最も近い敵3体に攻撃力450%で攻撃。"
        self.skill3_description_jp = "受けるダメージを20%減少。最大HPの10%以下のダメージは300回まで0になる。"
        self.skill1_cooldown_max = 5
        self.skill2_cooldown_max = 5
        self.is_boss = False

    

    def skill1_logic(self):
        targets = self.target_selection(keyword="n_lowest_attr", keyword2="3", keyword3="hp", keyword4="ally")
        for target in targets:
            target.apply_effect(CancellationShield('Cancellation Shield', 4, True, 0.1, False, uses=4, cancel_below_instead=True))

    def skill2_logic(self):
        damage_dealt = self.attack(multiplier=4.5, repeat=1, target_kw1="n_enemy_in_front", target_kw2="3")
        return damage_dealt
        
    def skill3(self):
        pass

    def battle_entry_effects(self):
        shield = CancellationShield('Guidance', -1, True, 0.1, False, uses=300, cancel_below_instead=True)
        shield.can_be_removed_by_skill = False
        self.apply_effect(shield)
        self.apply_effect(StatsEffect('Father Passive', -1, True, {'final_damage_taken_multipler' : -0.20}, can_be_removed_by_skill=False))
         

class Kobold(Monster):
    def __init__(self, name, lvl, exp=0, equip=None, image=None):
        super().__init__(name, lvl, exp, equip, image)
        self.original_name = "Kobold"
        self.skill1_description = "Recover hp by 30% of maxhp and increase defense by 20% for 21 turns. If you are the only one alive, effect is increased by 100%."
        self.skill2_description = "Attack 1 closest enemy with 800% atk, if you are the only one alive, increase damage by 100%."
        self.skill3_description = "Defence and maxhp is increased by 25%."
        self.skill1_description_jp = "最大HPの30%回復し、防御を21ターンで20%増加。自分だけが生きている場合、効果は100%増加。"
        self.skill2_description_jp = "最も近い敵に攻撃力800%で攻撃。自分だけが生きている場合、ダメージを100%増加。"
        self.skill3_description_jp = "防御と最大HPを25%増加。"
        self.skill1_cooldown_max = 5
        self.skill2_cooldown_max = 5
        self.is_boss = False

    

    def skill1_logic(self):
        if len(self.ally) == 1:
            self.heal_hp(self.maxhp * 0.6, self)
            self.apply_effect(StatsEffect('Kobold Power', 21, True, {'defense' : 1.4}))
        else:
            self.heal_hp(self.maxhp * 0.3, self)
            self.apply_effect(StatsEffect('Kobold Power', 21, True, {'defense' : 1.2}))
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


class SoldierA(Monster):
    def __init__(self, name, lvl, exp=0, equip=None, image=None):
        super().__init__(name, lvl, exp, equip, image)
        self.original_name = "SoldierA"
        self.skill1_description = "Focus attack on enemy with highest defense with 360% atk 3 times, each attack will reduce target defense by 7% for 21 turns."
        self.skill2_description = "Attack all enemies with 200% atk and reduce defense by 12% for 21 turns."
        self.skill3_description = "Skill attack have 30% chance to inflict Bleed for 20 turns. Bleed: takes 10% of atk as status damage per turn."
        self.skill1_description_jp = "最も高い防御力の敵に攻撃力360%で3回攻撃し、各攻撃で対象の防御力を21ターンで7%減少。"
        self.skill2_description_jp = "全ての敵に攻撃力200%で攻撃し、防御力を21ターンで12%減少。"
        self.skill3_description_jp = "スキル攻撃で20%の確率で20ターンの間出血を付与。出血：攻撃力の10%を状態ダメージとして毎ターン受ける。"
        self.skill1_cooldown_max = 4
        self.skill2_cooldown_max = 4
        self.is_boss = False

    def skill1_logic(self):
        def bleed_effect_defence_break(self, target):
            dice = random.randint(1, 100)
            if dice <= 30:
                target.apply_effect(ContinuousDamageEffect('Bleed', duration=20, is_buff=False, value=0.1 * self.atk, imposter=self))
            target.apply_effect(StatsEffect('Defence Break', 21, False, {'defense' : 0.93}))
        damage_dealt = self.attack(multiplier=3.6, repeat_seq=3, func_after_dmg=bleed_effect_defence_break, target_kw1="n_highest_attr", target_kw2="1", target_kw3="defense", target_kw4="enemy")
        return damage_dealt

    def skill2_logic(self):
        def bleed_effect_defence_break(self, target):
            dice = random.randint(1, 100)
            if dice <= 30:
                target.apply_effect(ContinuousDamageEffect('Bleed', duration=20, is_buff=False, value=0.1 * self.atk, imposter=self))
            target.apply_effect(StatsEffect('Defence Break', 21, False, {'defense' : 0.88}))
        damage_dealt = self.attack(multiplier=2.0, repeat=1, func_after_dmg=bleed_effect_defence_break, target_kw1="n_random_enemy", target_kw2="5")
        return damage_dealt
        
    def skill3(self):
        pass


class FutureSoldier(Monster):

    def __init__(self, name, lvl, exp=0, equip=None, image=None):
        super().__init__(name, lvl, exp, equip, image)
        self.original_name = "FutureSoldier"
        self.skill1_description = "Attack random enemies 5 times with 200% atk, each attack reduces target defense by 8% for 24 turns."
        self.skill2_description = "Attack random enemies 7 times with 150% atk, if target has lower defense than self, increase damage by 100%."
        self.skill3_description = "Normal attack deals double damage if target has lower defense than self."
        self.skill1_description_jp = "ランダムな敵に攻撃力200%で5回攻撃し、各攻撃で対象の防御力を24ターンで8%減少。"
        self.skill2_description_jp = "ランダムな敵に攻撃力150%で7回攻撃し、対象の防御力が自分より低い場合、ダメージを100%増加。"
        self.skill3_description_jp = "通常攻撃は対象の防御力が自分より低い場合、ダメージが2倍になる。"
        self.skill1_cooldown_max = 4
        self.skill2_cooldown_max = 4
        self.is_boss = False

    def skill1_logic(self):
        def defence_break(self, target):
            target.apply_effect(StatsEffect('Defence Break', 24, False, {'defense' : 0.92}))
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


class FutureElite(Monster):
    """
    No specific counter avaliable, maybe partywide def buff and debuff removal and def down debuff
    """
    def __init__(self, name, lvl, exp=0, equip=None, image=None):
        super().__init__(name, lvl, exp, equip, image)
        self.original_name = "FutureElite"
        self.skill1_description = "Attack all enemies with 400% atk, reduce defense by 15% for 30 turns."
        self.skill2_description = "Attack random enemies 8 times with 200% atk, if target has lower defense than self, damage increased by a percentage equal to the ratio between self and target defense."
        # for example: self.defense = 100, target.defense = 50, damage increased by 100%
        self.skill3_description = "defense is increased by 30%."
        self.skill1_description_jp = "全ての敵に攻撃力400%で攻撃し、防御力を30ターンで15%減少させる。"
        self.skill2_description_jp = "ランダムな敵に攻撃力200%で8回攻撃し、対象の防御力が自分より低い場合、ダメージは自分と対象の防御力の比率に等しい割合で増加。"
        self.skill3_description_jp = "防御力を30%増加。"
        self.skill1_cooldown_max = 4
        self.skill2_cooldown_max = 4
        self.is_boss = True

    def skill1_logic(self):
        def defence_break(self, target):
            target.apply_effect(StatsEffect('Defence Break', 30, False, {'defense' : 0.85}))
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


class SkeletonB(Monster):
    def __init__(self, name, lvl, exp=0, equip=None, image=None):
        super().__init__(name, lvl, exp, equip, image)
        self.original_name = "SkeletonB"
        self.skill1_description = "Attack enemy with highest def with 300% atk 3 times."
        self.skill2_description = "Attack enemy with highest def with 900% atk, 80% chance to Stun for 8 turns."
        self.skill3_description = "Penetration is increased by 35%."
        self.skill1_description_jp = "最も高い防御力の敵に攻撃力300%で3回攻撃。"
        self.skill2_description_jp = "最も高い防御力の敵に攻撃力900%で攻撃し、8ターンの間80%の確率でスタンを付与。"
        self.skill3_description_jp = "貫通を35%増加。"
        self.skill1_cooldown_max = 5
        self.skill2_cooldown_max = 5
        self.is_boss = False

    def skill1_logic(self):
        damage_dealt = self.attack(multiplier=3.0, repeat=3, target_kw1="n_highest_attr", target_kw2="1", target_kw3="defense", target_kw4="enemy")
        return damage_dealt


    def skill2_logic(self):
        def stun(self, target):
            target.apply_effect(StunEffect('Stun', 8, False))
        damage_dealt = self.attack(multiplier=9.0, repeat=1, func_after_dmg=stun, target_kw1="n_highest_attr", target_kw2="1", target_kw3="defense", target_kw4="enemy")
        return damage_dealt

    def skill3(self):
        pass

    def battle_entry_effects(self):
        self.apply_effect(StatsEffect('SkeletonB Passive', -1, True, {'penetration' : 0.35}, can_be_removed_by_skill=False))


class Mandrake(Monster):
    def __init__(self, name, lvl, exp=0, equip=None, image=None):
        super().__init__(name, lvl, exp, equip, image)
        self.original_name = "Mandrake"
        self.skill1_description = "Heal 2 neighbor allies by 100% def and increase their defense by 8% for 24 turns."
        self.skill2_description = "2 neighbor allies gain regeneration for 24 turns, regeneration heal 25% of the allys def per turn." \
        " For 24 turns, their critical defense is increased by 12%."
        self.skill3_description = "Maxhp is increased by 15%, defense is increased by 150%."
        self.skill1_description_jp = "隣接する2体の味方を防御力100%で回復し、防御力を24ターンで12%増加。"
        self.skill2_description_jp = "隣接する2体の味方24ターンに再生を付与し、毎ターンその味方自分の防御力の25%でHPを回復する。24ターンの間、クリティカル防御を16%増加。"
        self.skill3_description_jp = "最大HPを15%増加し、防御力を150%増加。"
        self.skill1_cooldown_max = 5
        self.skill2_cooldown_max = 5
        self.is_boss = False

    def skill1_logic(self):
        neighbors = self.get_neighbor_allies_not_including_self()
        def effect(self, target, healing, overhealing):
            target.apply_effect(StatsEffect('Defense Up', 24, True, {'defense' : 1.12}))
        self.heal(target_list=neighbors, value=1.0 * self.defense, func_after_each_heal=effect)
        return 0

    def skill2_logic(self):
        neighbors = self.get_neighbor_allies_not_including_self()
        for n in neighbors:
            n.apply_effect(ContinuousHealEffect('Regeneration', 24, True, lambda char, healer: 0.25 * char.defense, self, "25% of defense",
                                                value_function_description_jp="防御力の25%"))
            n.apply_effect(StatsEffect('Critical Defense Up', 24, True, {'critdef' : 0.16}))
        return 0
    
    def skill3(self):
        pass

    def battle_entry_effects(self):
        self.apply_effect(StatsEffect('Mandrake Passive', -1, True, {'maxhp' : 1.15, 'defense' : 2.5}, can_be_removed_by_skill=False))
        self.hp = self.maxhp


class Thiefb(Monster):
    def __init__(self, name, lvl, exp=0, equip=None, image=None):
        super().__init__(name, lvl, exp, equip, image)
        self.original_name = "Thiefb"
        self.skill1_description = "Attack closest enemy 8 times with 160% atk, after all attack, apply Def Up on 3 allies with lowest defense,"
        " increase their defense by 20% for 24 turns."
        self.skill2_description = "Attack closest enemy 8 times with 150% atk, after all attack, target all allies who has lower defense than yourself," \
        " Apply Def Up on them, increase their defense by 20% for 24 turns."
        self.skill3_description = "Increase defense by 30%."
        self.skill1_description_jp = "最も近い敵に攻撃力の160%で8回攻撃し、攻撃後、防御力が最も低い3人の味方に「防御アップ」を付与し、24ターンの間、防御力を20%増加させる。"
        self.skill2_description_jp = "最も近い敵に攻撃力の150%で8回攻撃し、攻撃後、自分より防御力が低い全ての味方を対象に「防御アップ」を付与し、24ターンの間、防御力を20%増加させる。"
        self.skill3_description_jp = "防御力を30%増加させる。"
        self.skill1_cooldown_max = 5
        self.skill2_cooldown_max = 5
        self.is_boss = False


    def skill1_logic(self):
        damage_dealt = self.attack(multiplier=1.6, repeat=8, target_kw1="enemy_in_front")
        if self.is_alive():
            self.update_ally_and_enemy()
            allies = list(self.target_selection(keyword="n_lowest_attr", keyword2="3", keyword3="defense", keyword4="ally"))
            for ally in allies:
                ally.apply_effect(StatsEffect('Defense Up', 24, True, {'defense' : 1.2}))
        return damage_dealt


    def skill2_logic(self):
        damage_dealt = self.attack(multiplier=1.5, repeat=8, target_kw1="enemy_in_front")
        if self.is_alive():
            self.update_ally_and_enemy()
            allies = [x for x in self.ally if x.defense <= self.defense]
            for ally in allies:
                ally.apply_effect(StatsEffect('Defense Up', 24, True, {'defense' : 1.2}))
        return damage_dealt

    
    def skill3(self):
        pass

    def battle_entry_effects(self):
        self.apply_effect(StatsEffect('Thiefb Passive', -1, True, {'defense' : 1.3}, can_be_removed_by_skill=False))


class Dragon(Monster):
    # high def, protect allies, attack with def.
    def __init__(self, name, lvl, exp=0, equip=None, image=None):
        super().__init__(name, lvl, exp, equip, image)
        self.original_name = "Dragon"
        self.skill1_description = "Attack closest enemy 4 times with 300% def and recover hp by 50% of damage dealt."
        self.skill2_description = "Heal all allies by 300% of def and apply Def Up on them, increase their defense by 50% of your defense for 24 turns."
        self.skill3_description = "Defense is increased by 100%. Protect all allies, the allies damage taken is reduced by 50%, 50% of damage taken is" \
        " redirected to you."
        self.skill1_description_jp = "最も近い敵に防御力の300%で4回攻撃し、与えたダメージの50%分HPを回復する。"
        self.skill2_description_jp = "全ての味方のHPを防御力の300%分回復し、「防御アップ」を付与して、24ターンの間、自分の防御力の50%分防御力を増加させる。"
        self.skill3_description_jp = "防御力が100%増加する。全ての味方を保護し、味方が受けるダメージを50%減少させ、そのうち50%のダメージを自分が引き受ける。"
        self.skill1_cooldown_max = 4
        self.skill2_cooldown_max = 4
        self.is_boss = True


    def skill1_logic(self):
        damage_dealt = self.attack(multiplier=3.0, repeat=4, target_kw1="enemy_in_front", damage_is_based_on="def")
        if self.is_alive(): 
            self.heal_hp(damage_dealt * 0.5, self)
        return damage_dealt

    def skill2_logic(self):
        allies = [x for x in self.ally if x != self]
        for ally in allies:
            ally.heal_hp(self.defense * 3.0, self)
            ally.apply_effect(StatsEffect('Def Up', 24, True, main_stats_additive_dict={'defense' : self.defense * 0.5}))
        return 0
    
    def skill3(self):
        pass

    def battle_entry_effects(self):
        self.apply_effect(StatsEffect('Def Up', -1, True, {'defense' : 2.0}, can_be_removed_by_skill=False))
        allies = [x for x in self.ally if x != self]
        for ally in allies:
            e = ProtectedEffect("Subject Protect", -1, True, False, self, 0.50, 0.5)
            e.additional_name = "SubjectA_Protect"
            e.can_be_removed_by_skill = False
            ally.apply_effect(e)



# ====================================
# End of Defence & Mitigation
# ====================================
# Survival Effects
# For example, monsters that survives with 1 hp
# ====================================


class MinotaurB(Monster):
    def __init__(self, name, lvl, exp=0, equip=None, image=None):
        super().__init__(name, lvl, exp, equip, image)
        self.original_name = "MinotaurB"
        self.skill1_description = "Recover hp by 30% of maxhp and apply Resolve on yourself, when taking normal damage that would exceed" \
        " current hp, reduce damage taken to your current hp minus 1, effect last for 30 turns. When the same effect is applied, duration" \
        " is refreshed."
        self.skill2_description = "Attack one closest enemy with 800% atk and Stun the target for 8 turns."
        self.skill3_description = "Normal attack deals 100% more damage to enemy if they have less speed than you."
        self.skill1_description_jp = "最大HPの30%分のHPを回復し、自身に「決意」を付与する。通常ダメージを受けて現在のHPを超える場合、そのダメージを現在のHPから1を引いた値に減少させる。この効果は30ターン持続する。同じ効果が再度付与された場合、持続時間がリフレッシュされる。"
        self.skill2_description_jp = "最も近い敵1体に攻撃力の800%で攻撃し、8ターンの間スタンさせる。"
        self.skill3_description_jp = "通常攻撃時、敵の速度が自分より低い場合、与えるダメージが100%増加する。"
        # ResolveEffect
        self.skill1_cooldown_max = 4
        self.skill2_cooldown_max = 4
        self.is_boss = False


    def skill1_logic(self):
        self.heal_hp(self.maxhp * 0.3, self)
        if self.is_alive():
            resolve = ResolveEffect('Resolve', 30, True, cc_immunity=False, hp_to_leave=1)
            resolve.additional_name = "MinotaurB_Resolve"
            resolve.apply_rule = "stack"
            self.apply_effect(resolve)

    def skill2_logic(self):
        def stun(self, target):
            target.apply_effect(StunEffect('Stun', 8, False))
        damage_dealt = self.attack(multiplier=8.0, repeat=1, target_kw1="enemy_in_front", func_after_dmg=stun)
        return damage_dealt
    
    def skill3(self):
        pass

    def normal_attack(self):
        def dmg_amplify(self, target, final_damage):
            if target.spd < self.spd:
                final_damage *= 2.0
            return final_damage
        self.attack(func_damage_step=dmg_amplify)


class CaptainB(Monster):
    def __init__(self, name, lvl, exp=0, equip=None, image=None):
        super().__init__(name, lvl, exp, equip, image)
        self.original_name = "CaptainB"
        self.skill1_description = "Attack 1 closest enemy with 320% atk 2 times. If your hp is below 5%, damage is increased by 100%."
        self.skill2_description = "Attack 1 closest enemy with 320% atk 2 times. If your hp is below 5%, inflict Cripple for 20 turns." \
        " Cripple: atk decreased by 20%, spd decreased by 30%, evasion decreased by 40%."
        self.skill3_description = "Normal attack attacks 2 times. At start of battle, apply Resolve on all allies, when taking normal damage that would exceed" \
        " current hp, reduce damage taken to your current hp minus 1, effect last for 30 turns. When the same effect is applied, duration" \
        " is refreshed."
        self.skill1_description_jp = "最も近い敵1体に攻撃力の320%で2回攻撃する。自身のHPが5%未満の場合、ダメージが100%増加する。"
        self.skill2_description_jp = "最も近い敵1体に攻撃力の320%で2回攻撃する。自身のHPが5%未満の場合、20ターンの間「衰弱」を付与する。衰弱：攻撃力が20%減少、速度が30%減少、回避率が40%減少する。"
        self.skill3_description_jp = "通常攻撃が2回攻撃になる。戦闘開始時、全ての味方に「決意」を付与する。通常ダメージが現在のHPを超える場合、受けるダメージを現在のHPから1引いた値に軽減する。この効果は30ターン持続する。同じ効果が再度付与された場合、持続時間がリフレッシュされる。"
        self.skill1_cooldown_max = 4
        self.skill2_cooldown_max = 4
        self.is_boss = False

    def skill1_logic(self):
        def additional_damage(self, target, final_damage):
            if self.hp / self.maxhp < 0.05:
                final_damage *= 2.0
            return final_damage
        damage_dealt = self.attack(multiplier=3.2, repeat=2, target_kw1="enemy_in_front", func_damage_step=additional_damage)
        return damage_dealt

    def skill2_logic(self):
        def cripple(self, target):
            if self.hp / self.maxhp < 0.05:
                target.apply_effect(StatsEffect('Cripple', 20, False, {'atk' : 0.8, 'spd' : 0.7, 'eva' : -0.4}))
        damage_dealt = self.attack(multiplier=3.2, repeat=2, target_kw1="enemy_in_front", func_after_dmg=cripple)
        return damage_dealt

    def skill3(self):
        pass

    def normal_attack(self):
        self.attack(repeat=2)

    def battle_entry_effects(self):
        for ally in self.ally:
            resolve = ResolveEffect('Resolve', 30, True, cc_immunity=False, hp_to_leave=1)
            resolve.additional_name = "CaptainB_Resolve"
            resolve.apply_rule = "stack"
            ally.apply_effect(resolve)


class DarklordB(Monster):
    def __init__(self, name, lvl, exp=0, equip=None, image=None):
        super().__init__(name, lvl, exp, equip, image)
        self.original_name = "DarklordB"
        self.skill1_description = "Attack 1 closest enemy with 150% atk 9 times. Before attack, apply Sting on all enemies for 20 turns." \
            " Sting: When taking damage, take 30% of your atk as status damage."
        self.skill2_description = "Attack 1 closest enemy with 150% atk 9 times. Before attack, apply Evasion Up on all allies for 20 turns," \
            " increase evasion by 15%."
        self.skill3_description = "At start of battle, apply Resolve on all allies, when taking normal damage that would exceed" \
        " current hp, reduce damage taken to your current hp minus 1."
        self.skill1_description_jp = "最も近い敵1体に攻撃力の150%で9回攻撃する。攻撃前に全ての敵に20ターンの間「スティング」を付与する。スティング：ダメージを受けた時、攻撃力の30%分の状態異常ダメージを受ける。"
        self.skill2_description_jp = "最も近い敵1体に攻撃力の150%で9回攻撃する。攻撃前に全ての味方に20ターンの間「回避アップ」を付与し、回避率を15%増加させる。"
        self.skill3_description_jp = "戦闘開始時に全ての味方に「決意」を付与する。通常ダメージが現在のHPを超える場合、受けるダメージを現在のHPから1を引いた値に軽減する。"
        self.skill1_cooldown_max = 5
        self.skill2_cooldown_max = 5
        self.is_boss = True

    def skill1_logic(self):
        for e in self.enemy:
            e.apply_effect(StingEffect("Sting", 20, False, 0.30 * self.atk, imposter=self))
        damage_dealt = self.attack(multiplier=1.50, repeat=9, target_kw1="enemy_in_front")
        return damage_dealt

    def skill2_logic(self):
        for a in self.ally:
            a.apply_effect(StatsEffect('Evasion Up', 20, True, {'eva' : 0.15}))
        damage_dealt = self.attack(multiplier=1.50, repeat=9, target_kw1="enemy_in_front")
        # self.update_ally_and_enemy()
        # if self.is_alive():
        #     for a in self.ally:
        #         a.heal_hp(damage_dealt, self)
        return damage_dealt


    def skill3(self):
        pass

    def battle_entry_effects(self):
        for ally in self.ally:
            resolve = ResolveEffect('Resolve', -1, True, cc_immunity=False, hp_to_leave=1)
            resolve.additional_name = "DarklordB_Resolve"
            resolve.apply_rule = "stack"
            resolve.can_be_removed_by_skill = False
            ally.apply_effect(resolve)




# ====================================
# End of Survival Effects
# ====================================
# Protection Effects
# ====================================


class Coward(Monster):
    def __init__(self, name, lvl, exp=0, equip=None, image=None):
        super().__init__(name, lvl, exp, equip, image)
        self.original_name = "Coward"
        self.skill1_description = "Increase defense by 20% for 20 turns. Same effect cannot be applied twice."
        self.skill2_description = "Attack 1 closest enemy with 550% atk."
        self.skill3_description = "Protect all allies. Damage taken is reduced 20%, 50% of damage taken is redirected to you." \
        " Start the battle with a Absorption Shield covering 40% maxhp."
        self.skill1_description_jp = "20ターンの間、防御力を20%増加させる。同じ効果を重複して適用することはできない。"
        self.skill2_description_jp = "最も近い敵に攻撃力550%で攻撃。"
        self.skill3_description_jp = "全ての味方を守護する。受けるダメージを20%減少し、50%のダメージが自分が受ける。戦闘開始の時、最大HPの40%をカバーする吸収シールド自分に付与する。"
        self.skill1_cooldown_max = 5
        self.skill2_cooldown_max = 5
        self.is_boss = False

    def skill1_logic(self):
        if not self.has_effect_that_named("Concealed", "Coward_Concealed"):
            concealed = StatsEffect('Concealed', 20, True, {'defense' : 1.2})
            concealed.additional_name = "Coward_Concealed"
            self.apply_effect(concealed)
        return 0

    def skill2_logic(self):
        damage_dealt = self.attack(multiplier=5.5, repeat=1, target_kw1="enemy_in_front")
        return damage_dealt

    def skill3(self):
        pass

    def battle_entry_effects(self):
        allies = [x for x in self.ally if x != self]
        for ally in allies:
            e = ProtectedEffect("Dark Material", -1, True, False, self, 0.80, 0.5)
            e.additional_name = "Coward_Dark_Material"
            e.can_be_removed_by_skill = False
            ally.apply_effect(e)

        shield = AbsorptionShield('Cowardice', -1, True, int(self.maxhp * 0.4), False)
        shield.can_be_removed_by_skill = False
        self.apply_effect(shield)


class Yamatanoorochi(Monster):
    """
    Counter: Protection is generally countered by skill that target this monster specifically
    """
    def __init__(self, name, lvl, exp=0, equip=None, image=None):
        super().__init__(name, lvl, exp, equip, image)
        self.original_name = "Yamatanoorochi"
        self.skill1_description = "Attack random enemies 6 times with 300% atk. If your hp is above 80%, attack 8 times instead." \
        " Each attack has 50% chance to inflict Poison for 3 turns. Poison: takes 3% of max hp as status damage each turn."
        self.skill2_description = "Recovers hp by 30% of maxhp and increase defense by 8% for all allies for 24 turns."
        self.skill3_description = "Protect all allies. Damage taken is reduced by 30%, 70% of damage taken is redirected to you." \
        " Increase maxhp by 60%, defense by 30%."
        self.skill1_description_jp = "ランダムな敵に攻撃力300%で6回攻撃。自分のHPが80%以上の場合、8回攻撃。各攻撃で50%の確率で3ターンの間毒を付与。毒:毎ターン最大HPの3%を状態ダメージとして受ける。"
        self.skill2_description_jp = "最大HPの30%回復し、全ての味方の防御力を24ターンで8%増加。"
        self.skill3_description_jp = "全ての味方を守護する。受けるダメージを30%減少し、70%のダメージが自分が受ける。最大HPを60%、防御力を30%増加。"
        self.skill1_cooldown_max = 4
        self.skill2_cooldown_max = 4
        self.is_boss = True

    def skill1_logic(self):
        def poison_effect(self, target):
            dice = random.randint(1, 100)
            if dice <= 50:
                target.apply_effect(ContinuousDamageEffect_Poison('Poison', duration=3, is_buff=False, ratio=0.03, imposter=self, base="maxhp"))
        if self.hp > 0.8 * self.maxhp:
            damage_dealt = self.attack(multiplier=3.0, repeat=8, func_after_dmg=poison_effect)
        else:
            damage_dealt = self.attack(multiplier=3.0, repeat=6, func_after_dmg=poison_effect)
        return damage_dealt

    def skill2_logic(self):
        self.heal_hp(self.maxhp * 0.3, self)
        allies = [x for x in self.ally if x != self]
        for ally in allies:
            ally.apply_effect(StatsEffect('Def Up', 24, True, {'defense' : 1.08}))
        return 0

    def skill3(self):
        pass

    def battle_entry_effects(self):
        allies = [x for x in self.ally if x != self]
        for ally in allies:
            e = ProtectedEffect("Deep Water", -1, True, False, self, damage_after_reduction_multiplier=0.70, damage_redirect_percentage=0.70)
            e.additional_name = "Yamatanoorochi_Deep_Water"
            e.can_be_removed_by_skill = False
            ally.apply_effect(e)
        self.apply_effect(StatsEffect('Passive', -1, True, {'maxhp' : 1.6, 'defense' : 1.3}, can_be_removed_by_skill=False))
        self.hp = self.maxhp


class Hero(Monster):
    def __init__(self, name, lvl, exp=0, equip=None, image=None):
        super().__init__(name, lvl, exp, equip, image)
        self.original_name = "Hero"
        self.skill1_description = "Attack enemy of lowest hp with 350% atk 3 times. If this attack or additional attack takes down the enemy," \
        " attack again."
        self.skill2_description = "For 12 turns, you and your neighbor allies have their atk and def increased by the percentage of your lost hp."
        self.skill3_description = "Protect 2 neighboring allies. Damage taken is reduced by 60%, 80% of damage taken is redirected to you." \
        " Atk, def and spd is increased by 20%."
        self.skill1_description_jp = "最も低いHPの敵に攻撃力350%で3回攻撃。この攻撃または追加攻撃で敵を倒すと、再度攻撃。"
        self.skill2_description_jp = "12ターンの間、隣接する味方と自分の攻撃力と防御力が自分失ったHPの割合で増加する。"
        self.skill3_description_jp = "隣接する2体の味方を守護する。受けるダメージを60%減少し、80%のダメージが自分が受ける。攻撃力、防御力、速度を20%増加。"
        self.skill1_cooldown_max = 4
        self.skill2_cooldown_max = 3
        self.is_boss = True

    def skill1_logic(self):
        def additional_attacks(self, target, is_crit):
            if target.is_dead():
                return self.attack(target_kw1="n_lowest_attr", target_kw2="1", target_kw3="hp", target_kw4="enemy", multiplier=3.5, repeat=3, additional_attack_after_dmg=additional_attacks)
            else:
                return 0
        damage_dealt = self.attack(target_kw1="n_lowest_attr", target_kw2="1", target_kw3="hp", target_kw4="enemy", multiplier=3.5, repeat=3, additional_attack_after_dmg=additional_attacks)
        return damage_dealt


    def skill2_logic(self):
        def atk_def_increase(self, target):
            hp_lost = self.maxhp - self.hp
            target.apply_effect(StatsEffect('Heroic Power', 12, True, {'atk' : 1 + hp_lost / self.maxhp, 'defense' : 1 + hp_lost / self.maxhp}))
        allies = self.get_neighbor_allies_including_self()
        for ally in allies:
            atk_def_increase(self, ally)
        return 0


    def skill3(self):
        pass

    def battle_entry_effects(self):
        allies = self.get_neighbor_allies_not_including_self()
        for ally in allies:
            e = ProtectedEffect("Heroic Sacrifice", -1, True, False, self, damage_after_reduction_multiplier=0.40, damage_redirect_percentage=0.80)
            e.additional_name = "Hero_Heroic_Sacrifice"
            e.can_be_removed_by_skill = False
            ally.apply_effect(e)
        self.apply_effect(StatsEffect('Heroic Passive', -1, True, {'atk' : 1.2, 'defense' : 1.2, 'spd' : 1.2}, can_be_removed_by_skill=False))


class HeroB(Monster):
    def __init__(self, name, lvl, exp=0, equip=None, image=None):
        super().__init__(name, lvl, exp, equip, image)
        self.original_name = "HeroB"
        self.skill1_description = "Attack enemy of highest hp with 300% atk 3 times, if this skill does not take down the enemy, attack again."
        self.skill2_description = "Apply a shield on you and 2 neighboring allies for 12 turns," \
        " shield absorbs damage equal to your lost hp."
        self.skill3_description = "Protect 2 neighboring allies. Damage taken is reduced by 50%, 50% of damage taken is redirected to you." \
        " Atk, def and spd is increased by 10%."
        self.skill1_description_jp = "最も高いHPの敵に攻撃力300%で3回攻撃し、このスキルで敵を倒せない場合、再度攻撃。"
        self.skill2_description_jp = "自分と2体の隣接する味方に12ターンの間シールドを付与し、シールドは自分の失ったHPに等しいダメージを吸収。"
        self.skill3_description_jp = "隣接する2体の味方を守護。受けるダメージを50%減少し、50%のダメージが自分が受ける。攻撃力、防御力、速度を10%増加。"
        self.skill1_cooldown_max = 4
        self.skill2_cooldown_max = 3
        self.is_boss = True

    def skill1_logic(self):
        def additional_attacks(self, target, is_crit):
            if not target.is_dead():
                return self.attack(target_kw1="n_highest_attr", target_kw2="1", target_kw3="hp", target_kw4="enemy", multiplier=3.00, repeat=3)
            else:
                return 0
        damage_dealt = self.attack(target_kw1="n_highest_attr", target_kw2="1", target_kw3="hp", target_kw4="enemy", multiplier=3.00, repeat=3, additional_attack_after_dmg=additional_attacks)
        return damage_dealt


    def skill2_logic(self):
        allies = self.get_neighbor_allies_including_self()
        for ally in allies:
            shield = AbsorptionShield('Heroic Shield', 12, True, int((self.maxhp - self.hp) * 1.0), False)
            ally.apply_effect(shield)
        return 0


    def skill3(self):
        pass

    def battle_entry_effects(self):
        allies = self.get_neighbor_allies_not_including_self()
        for ally in allies:
            e = ProtectedEffect("Heroic Sacrifice", -1, True, False, self, damage_after_reduction_multiplier=0.50, damage_redirect_percentage=0.50)
            e.additional_name = "HeroB_Heroic_Sacrifice"
            e.can_be_removed_by_skill = False
            ally.apply_effect(e)
        self.apply_effect(StatsEffect('HeroicB Passive', -1, True, {'atk' : 1.10, 'defense' : 1.10, 'spd' : 1.10}, can_be_removed_by_skill=False))


class Puppet(Monster):
    def __init__(self, name, lvl, exp=0, equip=None, image=None):
        super().__init__(name, lvl, exp, equip, image)
        self.original_name = "Puppet"
        self.skill1_description = "For 20 turns, increase evasion by 50%."
        self.skill2_description = "Heal hp by 40% of maxhp."
        self.skill3_description = "Protect all allies. Damage taken is reduced 50%, 90% of damage taken is redirected to you."
        self.skill1_description_jp = "20ターンの間、回避率を50%増加。"
        self.skill2_description_jp = "最大HPの40%回復。"
        self.skill3_description_jp = "全ての味方を守護。受けるダメージを50%減少し、90%のダメージが自分が受ける。"
        self.skill1_cooldown_max = 4
        self.skill2_cooldown_max = 4
        self.is_boss = False

    def skill1_logic(self):
        self.apply_effect(StatsEffect('Floating Flag', 20, True, {'eva' : 0.5}))
        return 0

    def skill2_logic(self):
        self.heal_hp(self.maxhp * 0.4, self)
        return 0

    def skill3(self):
        pass

    def battle_entry_effects(self):
        allies = [x for x in self.ally if x != self]
        for ally in allies:
            e = ProtectedEffect("Puppet Strings", -1, True, False, self, damage_after_reduction_multiplier=0.50, damage_redirect_percentage=0.90)
            e.additional_name = "Puppet_Puppet_Strings"
            e.can_be_removed_by_skill = False
            ally.apply_effect(e)


class PuppetB(Monster):
    def __init__(self, name, lvl, exp=0, equip=None, image=None):
        super().__init__(name, lvl, exp, equip, image)
        self.original_name = "PuppetB"
        self.skill1_description = "For 20 turns, increase spd by 15%."
        self.skill2_description = "Apply absorption shield on your self, shield absorbs damage equal to 60% of maxhp."
        self.skill3_description = "Protect all allies. Damage taken is reduced 25%, 90% of damage taken is redirected to you."
        self.skill1_description_jp = "20ターンの間、速度を15%増加。"
        self.skill2_description_jp = "自分に吸収シールドを付与し、シールドは最大HPの60%のダメージを吸収。"
        self.skill3_description_jp = "全ての味方を守護。受けるダメージを25%減少し、90%のダメージが自分が受ける。"
        self.skill1_cooldown_max = 4
        self.skill2_cooldown_max = 4
        self.is_boss = False

    def skill1_logic(self):
        self.apply_effect(StatsEffect('Movement Control', 20, True, {'spd' : 1.15}))
        return 0


    def skill2_logic(self):
        shield = self.get_effect_that_named(effect_name="Puppet Shield", additional_name="PuppetB_Puppet_Shield")
        if not shield:
            shield = AbsorptionShield('Puppet Shield', -1, True, int(self.maxhp * 0.6), False)
            shield.additional_name = "PuppetB_Puppet_Shield"
            self.apply_effect(shield)
        else:
            shield.shield_value += int(self.maxhp * 0.6)
        return 0


    def skill3(self):
        pass

    def battle_entry_effects(self):
        allies = [x for x in self.ally if x != self]
        for ally in allies:
            e = ProtectedEffect("Puppet Movement", -1, True, False, self, damage_after_reduction_multiplier=0.75, damage_redirect_percentage=0.90)
            e.additional_name = "PuppetB_Puppet_Movement"
            e.can_be_removed_by_skill = False
            ally.apply_effect(e)



# ====================================
# End of Protection Effects
# ====================================
# Evasion related
# ====================================

# TODO: Add a monster for full party evasion buff


class Gryphon(Monster):
    def __init__(self, name, lvl, exp=0, equip=None, image=None):
        super().__init__(name, lvl, exp, equip, image)
        self.original_name = "Gryphon"
        self.skill1_description = "Self and 2 neighboring allies gain 10% evasion for 20 turns."
        self.skill2_description = "Attack 3 closest enemies with 250% atk 2 times, each attack has 70% chance to inflict Bleed for 20 turns." \
        "Bleed deals 15% of atk as status damage per turn."
        self.skill3_description = "Evasion is increased by 50%, speed is increased by 5%."
        self.skill1_description_jp = "自分と隣接する2体の味方に20ターンの間、回避率を10%増加。"
        self.skill2_description_jp = "最も近い敵3体に攻撃力250%で2回攻撃し、各攻撃で70%の確率で20ターンの間出血を付与。出血は攻撃力の15%を状態ダメージとして毎ターン受ける。"
        self.skill3_description_jp = "回避率を50%増加し、速度を5%増加。"
        self.skill1_cooldown_max = 5
        self.skill2_cooldown_max = 5
        self.is_boss = False

    def skill1_logic(self):
        self_and_neighbor = self.get_neighbor_allies_including_self() # list
        for ally in self_and_neighbor:
            ally.apply_effect(StatsEffect('Evasion Up', 20, True, {'eva' : 0.1}))
        return 0

    def skill2_logic(self):
        def bleed_effect(self, target):
            dice = random.randint(1, 100)
            if dice <= 70:
                target.apply_effect(ContinuousDamageEffect('Bleed', duration=20, is_buff=False, value=0.15 * self.atk, imposter=self))
        damage_dealt = self.attack(multiplier=2.5, repeat_seq=2, func_after_dmg=bleed_effect, target_kw1="n_enemy_in_front", target_kw2="3")
        return damage_dealt

    def skill3(self):
        pass

    def battle_entry_effects(self):
        self.apply_effect(StatsEffect('Gryphon Passive', -1, True, {'eva' : 0.5, 'spd' : 1.05}, can_be_removed_by_skill=False))


class Hermit(Monster):
    """
    Countered by buff removal, eva down
    """
    def __init__(self, name, lvl, exp=0, equip=None, image=None):
        super().__init__(name, lvl, exp, equip, image)
        self.original_name = "Hermit"
        self.skill1_description = "Attack 3 closest enemies with 235% atk 4 times, damage increased by the percentage of evasion rate." \
        " After the attack, increase evasion by 40% for 20 turns."
        self.skill2_description = "Attack closest enemy with 500% atk, if evasion rate is higher than 70%, this attack will not miss and guarantee" \
        " to be a critical hit, then Inflict Blind for 21 turns, Blind: reduce accuracy by 25%."
        self.skill3_description = "Evasion increased by 20%. Final damage taken is reduced by 15%."
        self.skill1_description_jp = "最も近い敵3体に攻撃力235%で4回攻撃し、回避率の割合でダメージを増加。攻撃後、20ターンの間回避率を40%増加。"
        self.skill2_description_jp = "最も近い敵に攻撃力500%で攻撃し、回避率が70%以上の場合、この攻撃は外れず、必ずクリティカルヒット。その後、21ターンの間老眼を付与。老眼:命中率を25%減少。"
        self.skill3_description_jp = "回避率を20%増加。最終ダメージ倍率を15%減少。"
        self.skill1_cooldown_max = 5
        self.skill2_cooldown_max = 5
        self.is_boss = True

    def skill1_logic(self):
        def damage_amplify(self, target, final_damage):
            final_damage *= max(1 + self.eva, 1.0)
            return final_damage
        damage_dealt = self.attack(multiplier=2.35, repeat_seq=4, func_damage_step=damage_amplify, target_kw1="n_enemy_in_front", target_kw2="3")
        self.apply_effect(StatsEffect('Evasion Up', 20, True, {'eva' : 0.40}))
        return damage_dealt

    def skill2_logic(self):
        if self.eva > 0.7:
            def blind_effect(self, target):
                target.apply_effect(StatsEffect('Blind', 21, False, {'acc' : -0.25}))
            damage_dealt = self.attack(multiplier=5.0, repeat=1, func_after_dmg=blind_effect, always_hit=True, always_crit=True, target_kw1="enemy_in_front")
        else:
            damage_dealt = self.attack(multiplier=5.0, repeat=1, target_kw1="enemy_in_front")
        return damage_dealt

    def skill3(self):
        pass

    def battle_entry_effects(self):
        self.apply_effect(StatsEffect('Hermit Passive', -1, True, {'eva' : 0.2, 'final_damage_taken_multipler' : -0.15}, can_be_removed_by_skill=False))


class KungFuB(Monster):
    """
    Countered buff removal, accuracy down, high evasion rate
    """
    def __init__(self, name, lvl, exp=0, equip=None, image=None):
        super().__init__(name, lvl, exp, equip, image)
        self.original_name = "KungFuB"
        self.skill1_description = "For 1 turn, increase accuracy by 25%," \
        " attack enemy with highest evasion with 240% atk 4 times. Each attack has 100% chance to Stun for 8 turns," \
        " 40% chance to inflict Bleed for 24 turns. Bleed: takes 10% of atk as status damage per turn."
        self.skill2_description = "For 20 turns, all allies gain atk equal to 30% of their current evasion rate if their evasion rate is higher than 0%."
        self.skill3_description = "All allies have increased evasion by 20% and accuracy by 40%."
        self.skill1_description_jp = "1ターンの間、命中率を25%増加し、最も高い回避率を持つ敵に攻撃力240%で4回攻撃。各攻撃で100%の確率で8ターンの間スタンを付与、40%の確率で24ターンの間出血を付与。出血:攻撃力の10%を状態ダメージとして毎ターン受ける。"
        self.skill2_description_jp = "20ターンの間、全ての味方の回避率が0%以上の場合、その味方が味方現在の回避率の30%分の攻撃力を増加。"
        self.skill3_description_jp = "全ての味方の回避率を20%、命中率を40%増加。"
        self.skill1_cooldown_max = 5
        self.skill2_cooldown_max = 5
        self.is_boss = True

    def skill1_logic(self):
        self.apply_effect(StatsEffect('KungFu', 1, True, {'acc' : 0.25}))
        def bleed_stun_effect(self, target):
            dice = random.randint(1, 100)
            if dice <= 40:
                target.apply_effect(ContinuousDamageEffect('Bleed', duration=24, is_buff=False, value=0.1 * self.atk, imposter=self))
            target.apply_effect(StunEffect('Stun', 8, False))
        damage_dealt = self.attack(multiplier=2.4, repeat=4, func_after_dmg=bleed_stun_effect, target_kw1="n_highest_attr", target_kw2="1", target_kw3="eva", target_kw4="enemy")
        return damage_dealt

    def skill2_logic(self):
        for a in self.ally:
            if a.eva > 0:
                a.apply_effect(StatsEffect('KungFu', 20, True, {'atk' : a.eva * 0.3 + 1.0}))
        return 0
        
    def skill3(self):
        pass

    def battle_entry_effects(self):
        for a in self.ally:
            a.apply_effect(StatsEffect('KungFu', -1, True, {'eva' : 0.2, 'acc' : 0.4}, can_be_removed_by_skill=False))


class HauntedTree(Monster):
    def __init__(self, name, lvl, exp=0, equip=None, image=None):
        super().__init__(name, lvl, exp, equip, image)
        self.original_name = "HauntedTree"
        self.skill1_description = "3 closest enemies are Rooted for 18 turns. Rooted: evasion is reduced by 55%, def and critdef is reduced by 20%." \
        " Effect duration refreshes if same effect is applied again."
        self.skill2_description = "If no enemy is Rooted, this skill has no effect." \
        " Attack all Rooted enemies with 320% atk 3 times, each attack deals additional damage equal to 5% of self maxhp."
        self.skill3_description = "Damage taken is reduced by 70% from Rooted enemies. maxhp, def and critdef is increased by 30%."
        self.skill1_description_jp = "最も近い敵3体を18ターンの間ルートする。ルート:回避率が55%減少、防御力とクリティカル防御力が20%減少。同じ効果が再度適用されると効果時間が更新される。"
        self.skill2_description_jp = "ルートした敵がいない場合、このスキルは効果がない。ルートした敵全てに攻撃力320%で3回攻撃し、各攻撃は自分の最大HPの5%の分ダメージを追加。"
        self.skill3_description_jp = "ルートした敵から受けるダメージを70%減少。最大HP、防御力、クリティカル防御力を30%増加。"
        self.skill1_cooldown_max = 4
        self.skill2_cooldown_max = 4
        self.is_boss = False

    def skill1_logic(self):
        targets = self.target_selection("n_enemy_in_front", "3")
        for target in targets:
            eff = StatsEffect('Rooted', 18, False, {'eva' : -0.55, 'defense' : 0.8, 'critdef' : -0.2})
            eff.additional_name = "HauntedTree_Rooted"
            eff.apply_rule = 'stack'
            target.apply_effect(eff)
        return 0

    def skill2_logic(self):
        rooted_enemies = list(self.target_selection("enemy_that_must_have_effect", "Rooted"))
        if not rooted_enemies:
            return 0
        def additional_damage(self, target, final_damage):
            final_damage += 0.05 * self.maxhp
            return final_damage
        damage_dealt = self.attack(multiplier=3.2, repeat=3, func_damage_step=additional_damage, target_list=rooted_enemies)
        return damage_dealt

    def skill3(self):
        pass

    def take_damage_before_calculation(self, damage, attacker):
        if attacker.has_effect_that_named('Rooted', additional_name='HauntedTree_Rooted'):
            global_vars.turn_info_string += f"{self.name} toke 70% less damage from {attacker.name}.\n"
            return damage * 0.3
        return damage

    def battle_entry_effects(self):
        self.apply_effect(StatsEffect('HauntedTree Passive', -1, True, {'defense' : 1.30, 'critdef' : 0.30, 'maxhp' : 1.30}))
        self.hp = self.maxhp


class Cobold(Monster):
    def __init__(self, name, lvl, exp=0, equip=None, image=None):
        super().__init__(name, lvl, exp, equip, image)
        self.original_name = "Cobold"
        self.skill1_description = "Attack enemy with lowest hp with 300% atk 3 times. This attack cannot miss."
        self.skill2_description = "Attack enemy with highest evasion with 300% atk 2 times, target evasion is reduced by 25% for 20 turns." \
        " This attack cannot miss."
        self.skill3_description = "Accuracy is increased by 50%."
        self.skill1_description_jp = "最も低いHPの敵に攻撃力300%で3回攻撃。この攻撃は外れない。"
        self.skill2_description_jp = "最も高い回避率を持つ敵に攻撃力300%で2回攻撃し、対象の回避率を20ターンの間25%減少。この攻撃は外れない。"
        self.skill3_description_jp = "命中率を50%増加。"
        self.skill1_cooldown_max = 4
        self.skill2_cooldown_max = 5
        self.is_boss = False

    def skill1_logic(self):
        damage_dealt = self.attack(multiplier=3.0, repeat=3, target_kw1="n_lowest_attr", target_kw2="1", target_kw3="hp", target_kw4="enemy", always_hit=True)
        return damage_dealt

    def skill2_logic(self):
        def evasion_reduction(self, target):
            target.apply_effect(StatsEffect('Evasion Down', 20, False, {'eva' : -0.25}))
        damage_dealt = self.attack(multiplier=3.0, repeat=2, func_after_dmg=evasion_reduction, target_kw1="n_highest_attr", target_kw2="1", target_kw3="eva", target_kw4="enemy", always_hit=True)
        return damage_dealt

    def skill3(self):
        pass

    def battle_entry_effects(self):
        self.apply_effect(StatsEffect('Cobold Passive', -1, True, {'acc' : 0.5}, can_be_removed_by_skill=False))


class MimicB(Monster):
    def __init__(self, name, lvl, exp=0, equip=None, image=None):
        super().__init__(name, lvl, exp, equip, image)
        self.original_name = "MimicB"
        self.skill1_description = "Attack 1 closest enemy with 800% atk. If this attack misses, reduce target's evasion by 40% for 20 turns."
        self.skill2_description = "Attack 1 closest enemy with 800% atk. This attack cannot miss."
        self.skill3_description = "When taking normal damage, 50% chance to reduce the target's evasion by 15% for 20 turns."
        self.skill1_description_jp = "最も近い敵に攻撃力800%で攻撃。この攻撃が外れた場合、対象の回避率を20ターンの間40%減少。"
        self.skill2_description_jp = "最も近い敵に攻撃力800%で攻撃。この攻撃は外れない。"
        self.skill3_description_jp = "通常ダメージを受けた際、50%の確率で対象の回避率を20ターンの間15%減少。"
        self.skill1_cooldown_max = 4
        self.skill2_cooldown_max = 4
        self.is_boss = False

    def skill1_logic(self):
        def evasion_reduction(self, target):
            target.apply_effect(StatsEffect('Evasion Down', 20, False, {'eva' : -0.4}))
        damage_dealt = self.attack(multiplier=8.0, repeat=1, func_after_miss=evasion_reduction, target_kw1="enemy_in_front", always_hit=False)
        return damage_dealt

    def skill2_logic(self):
        damage_dealt = self.attack(multiplier=8.0, repeat=1, target_kw1="enemy_in_front", always_hit=True)
        return damage_dealt
        
    def skill3(self):
        pass

    def take_damage_aftermath(self, damage, attacker):
        dice = random.randint(1, 100)
        if dice <= 50:
            attacker.apply_effect(StatsEffect('Evasion Down', 20, False, {'eva' : -0.15}))
        return damage


class Swordman(Monster):
    def __init__(self, name, lvl, exp=0, equip=None, image=None):
        super().__init__(name, lvl, exp, equip, image)
        self.original_name = "Swordman"
        self.skill1_description = "Increase accuracy by 120% for all allies for 20 turns."
        self.skill2_description = "Attack 1 closest enemy with 220% atk 6 times. This attack cannot miss." \
        " Deals 2% of target's maxhp as status damage per hit."
        self.skill3_description = "Atk and spd is increased by 10%."
        self.skill1_description_jp = "全ての味方の命中率を20ターンの間120%増加。"
        self.skill2_description_jp = "最も近い敵に攻撃力220%で6回攻撃。この攻撃は外れない。各攻撃で対象の最大HPの2%の追加状態異常ダメージを与える。"
        self.skill3_description_jp = "攻撃力と速度を10%増加。"
        self.skill1_cooldown_max = 4
        self.skill2_cooldown_max = 4
        self.is_boss = False

    def skill1_logic(self):
        allies = self.ally
        for ally in allies:
            ally.apply_effect(StatsEffect('Swordman', 20, True, {'acc' : 1.2}))
        return 0

    def skill2_logic(self):
        def status_damage(self, target):
            if target.is_alive():
                target.take_status_damage(0.02 * target.maxhp, self) 
        damage_dealt = self.attack(multiplier=2.2, repeat=6, func_after_dmg=status_damage, target_kw1="enemy_in_front", always_hit=True)
        return damage_dealt
        
    def skill3(self):
        pass

    def battle_entry_effects(self):
        self.apply_effect(StatsEffect('Swordman Passive', -1, True, {'atk' : 1.1, 'spd' : 1.1}, can_be_removed_by_skill=False))


# ====================================
# End of Evasion related
# ====================================
# Punish Negative Status
# ====================================
        
class Mage(Monster):
    def __init__(self, name, lvl, exp=0, equip=None, image=None):
        super().__init__(name, lvl, exp, equip, image)
        self.original_name = "Mage"
        self.skill1_description = "Attack 3 closest enemies with 300% atk and inflict Burn for 18 turns. Burn deals 13% of atk as status damage per turn. If target has negative status, inflict 3 Burn effects."
        self.skill2_description = "Attack closest enemy 3 times with 320% atk, if target has negative status, each attack inflict 3 Burn effects for 6 turns."
        self.skill3_description = "Increase atk by 10%"
        self.skill1_description_jp = "最も近い敵3体に攻撃力300%で攻撃し、18ターンの間出血を付与。出血は攻撃力の13%を状態ダメージとして毎ターン受ける。対象がデバフを持っている場合、3つの出血効果を付与。"
        self.skill2_description_jp = "最も近い敵に攻撃力320%で3回攻撃し、対象がデバフを持っている場合、各攻撃で6ターンの間3つの出血効果を付与。"
        self.skill3_description_jp = "攻撃力を10%増加。"
        self.skill1_cooldown_max = 5
        self.skill2_cooldown_max = 5
        self.is_boss = False

    def skill1_logic(self):
        def burn_effect(self, target):
            if len(target.debuffs) > 0:
                target.apply_effect(ContinuousDamageEffect('Burn', duration=18, is_buff=False, value=0.13 * self.atk, imposter=self))
                target.apply_effect(ContinuousDamageEffect('Burn', duration=18, is_buff=False, value=0.13 * self.atk, imposter=self))
                target.apply_effect(ContinuousDamageEffect('Burn', duration=18, is_buff=False, value=0.13 * self.atk, imposter=self))
            else:
                target.apply_effect(ContinuousDamageEffect('Burn', duration=18, is_buff=False, value=0.13 * self.atk, imposter=self))
        damage_dealt = self.attack(multiplier=3.0, repeat=1, func_after_dmg=burn_effect, target_kw1="n_enemy_in_front", target_kw2="3")
        return damage_dealt

    def skill2_logic(self):
        def burn_effect(self, target):
            if len(target.debuffs) > 0:
                target.apply_effect(ContinuousDamageEffect('Burn', duration=18, is_buff=False, value=0.13 * self.atk, imposter=self))
                target.apply_effect(ContinuousDamageEffect('Burn', duration=18, is_buff=False, value=0.13 * self.atk, imposter=self))
                target.apply_effect(ContinuousDamageEffect('Burn', duration=18, is_buff=False, value=0.13 * self.atk, imposter=self))
        damage_dealt = self.attack(multiplier=3.2, repeat=3, func_after_dmg=burn_effect, target_kw1="enemy_in_front")
        return damage_dealt

    def skill3(self):
        pass

    def battle_entry_effects(self):
        self.apply_effect(StatsEffect('Mage Passive', -1, True, {'atk' : 1.1}, can_be_removed_by_skill=False))


class Orklord(Monster):
    """
    Countered by debuff removal
    """
    def __init__(self, name, lvl, exp=0, equip=None, image=None):
        super().__init__(name, lvl, exp, equip, image)
        self.original_name = "Orklord"
        self.skill1_description = "Attack closest enemy with 220% atk 3 times. After all attack, if target has negative status effect, increase effect duration by 16 turns." \
        " For each debuff on target, attack with 440% atk."
        self.skill2_description = "Attack 5 enemies with 400% atk and inflict Bleed for 24 turns. Bleed deals 22% of atk as status damage per turn."
        self.skill3_description = "Normal attack deals 200% more damage to target with Bleed. Increase maxhp and defense by 50%."
        self.skill1_description_jp = "最も近い敵に攻撃力220%で3回攻撃。全ての攻撃後、対象がデバフを持っている場合、そのデバフの効果時間を16ターン増加。" \
        "対象に付与されているデバフの数に応じて、攻撃力の440%で攻撃する。"
        self.skill2_description_jp = "敵5体に攻撃力400%で攻撃し、24ターンの間出血を付与。出血は攻撃力の22%を状態ダメージとして毎ターン受ける。"
        self.skill3_description_jp = "通常攻撃は出血を持つ対象に対して200%の追加ダメージを与える。最大HPと防御力を50%増加。"
        self.skill1_cooldown_max = 3
        self.skill2_cooldown_max = 4
        self.is_boss = True

    def skill1_logic(self):
        target = next(self.target_selection(keyword="enemy_in_front"))
        damage_dealt = self.attack(multiplier=2.2, repeat=3, target_list=[target])
        if self.is_alive() and target.is_alive():
            for debuff in target.debuffs:
                if debuff.duration > 0:
                    debuff.duration += 16
            damage_dealt += self.attack(multiplier=4.4, repeat=len(target.debuffs), target_list=[target])    
        return damage_dealt

    def skill2_logic(self):
        def bleed_effect(self, target):
            target.apply_effect(ContinuousDamageEffect('Bleed', duration=24, is_buff=False, value=0.22 * self.atk, imposter=self))
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


# Poison instead of Burn
class MageB(Monster):
    def __init__(self, name, lvl, exp=0, equip=None, image=None):
        super().__init__(name, lvl, exp, equip, image)
        self.original_name = "MageB"
        self.skill1_description = "Attack 3 closest enemies with 280% atk and inflict Poison for 18 turns. Poison deals 0.7% of lost hp of atk as status damage per turn. If target has negative status, inflict 3 Poison effects" \
        " instead, the poison effects deal damage based on lost hp, maxhp and current hp."
        self.skill2_description = "Attack closest enemy 3 times with 300% atk, if target has negative status, each attack inflict 3 kind of Poison effects for 18 turns."
        self.skill3_description = "Increase accuracy by 70%"
        self.skill1_description_jp = "最も近い敵3体に攻撃力280%で攻撃し、18ターンの間毒を付与。毒は攻撃力の0.7%を失ったHPを状態ダメージとして毎ターン受ける。対象がデバフを持っている場合、3つの毒効果を付与し、毒効果は失ったHP、最大HP、現在HPに基づいてダメージを与える。"
        self.skill2_description_jp = "最も近い敵に攻撃力300%で3回攻撃し、対象がデバフを持っている場合、各攻撃で18ターンの間3種類の毒効果を付与。"
        self.skill3_description_jp = "命中率を70%増加。"
        self.skill1_cooldown_max = 5
        self.skill2_cooldown_max = 5
        self.is_boss = False

    def skill1_logic(self):
        def poison_effect(self, target):
            if len(target.debuffs) > 0:
                target.apply_effect(ContinuousDamageEffect_Poison('Poison A', duration=18, is_buff=False, ratio=0.007, imposter=self, base="losthp"))
                target.apply_effect(ContinuousDamageEffect_Poison('Poison B', duration=18, is_buff=False, ratio=0.007, imposter=self, base="maxhp"))
                target.apply_effect(ContinuousDamageEffect_Poison('Poison C', duration=18, is_buff=False, ratio=0.007, imposter=self, base="hp"))
            else:
                target.apply_effect(ContinuousDamageEffect_Poison('Poison A', duration=18, is_buff=False, ratio=0.007, imposter=self, base="losthp"))

        damage_dealt = self.attack(multiplier=2.8, repeat=1, func_after_dmg=poison_effect, target_kw1="n_enemy_in_front", target_kw2="3")
        return damage_dealt

    def skill2_logic(self):
        def poison_effect(self, target):
            if len(target.debuffs) > 0:
                target.apply_effect(ContinuousDamageEffect_Poison('Poison A', duration=18, is_buff=False, ratio=0.007, imposter=self, base="losthp"))
                target.apply_effect(ContinuousDamageEffect_Poison('Poison B', duration=18, is_buff=False, ratio=0.007, imposter=self, base="maxhp"))
                target.apply_effect(ContinuousDamageEffect_Poison('Poison C', duration=18, is_buff=False, ratio=0.007, imposter=self, base="hp"))
        damage_dealt = self.attack(multiplier=3.0, repeat=3, func_after_dmg=poison_effect, target_kw1="enemy_in_front")
        return damage_dealt

    def skill3(self):
        pass

    def battle_entry_effects(self):
        self.apply_effect(StatsEffect('MageB Passive', -1, True, {'acc' : 0.7}, can_be_removed_by_skill=False))


# TODO: Increase damage taken for debuffed target, always attack debuffed target
# class SubjectA2(Monster):
#     pass


# ====================================
# End of Punish Negative Status
# ====================================
# Positive Status
# Damage increases and others if target has active buffs
# ====================================
    

class Thief(Monster):
    def __init__(self, name, lvl, exp=0, equip=None, image=None):
        super().__init__(name, lvl, exp, equip, image)
        self.original_name = "Thief"
        self.skill1_description = "Attack 1 closest enemy with 600% atk."
        self.skill2_description = "Attack 2 closest enemies with 330% atk 2 times."
        self.skill3_description = "Skill damage increased by 60% for each active buff on target."
        self.skill1_description_jp = "最も近い敵に攻撃力600%で攻撃。"
        self.skill2_description_jp = "最も近い敵2体に攻撃力330%で2回攻撃。"
        self.skill3_description_jp = "対象がアクティブバフを持っている場合、スキルダメージを60%増加。" 
        self.skill1_cooldown_max = 4
        self.skill2_cooldown_max = 4
        self.is_boss = False

    def skill1_logic(self):
        def buffed_target_amplify(self, target: character.Character, final_damage):
            buffs = target.get_active_removable_effects(get_buffs=True, get_debuffs=False)
            new_final_damage = final_damage * (1 + 0.6 * len(buffs))
            # if len(buffs) > 0:
            #     print(f"Previous damage : {final_damage}, new damage : {new_final_damage}, buff count : {len(buffs)}")
            return new_final_damage
        damage_dealt = self.attack(multiplier=6.0, repeat=1, func_damage_step=buffed_target_amplify, target_kw1="enemy_in_front")
        return damage_dealt

    def skill2_logic(self):
        def buffed_target_amplify(self, target, final_damage):
            buffs = target.get_active_removable_effects(get_buffs=True, get_debuffs=False)
            return final_damage * (1 + 0.6 * len(buffs))
        damage_dealt = self.attack(target_kw1="n_enemy_in_front", target_kw2="2", multiplier=3.3, repeat_seq=2, func_damage_step=buffed_target_amplify)
        return damage_dealt
        
    def skill3(self):
        pass


class Goliath(Monster):
    """
    Countered by not setting main attacker to his front
    """
    def __init__(self, name, lvl, exp=0, equip=None, image=None):
        super().__init__(name, lvl, exp, equip, image)
        self.original_name = "Goliath"
        self.skill1_description = "Strike the closest enemy with 600% atk, for each active buff effect, strike again with 400% atk."
        self.skill2_description = "Reset skill cooldown of skill 1 and increase spd by 100% for 3 turns. Attack closest enemy 3 times with 300% atk. For each active buff on target, increase damage by 30%."
        self.skill3_description = "Increase atk, def, maxhp by 30%."
        self.skill1_description_jp = "最も近い敵に攻撃力600%で攻撃し、アクティブバフ効果がある場合、バフ1つにつき400%で再度攻撃。"
        self.skill2_description_jp = "スキル1のクールダウンをリセットし、3ターンの間速度を100%増加。最も近い敵に攻撃力300%で3回攻撃。対象がアクティブバフを持っている場合、バフ1つにつきダメージを30%増加。"
        self.skill3_description_jp = "攻撃力、防御力、最大HPを30%増加。"
        self.skill1_cooldown_max = 4
        self.skill2_cooldown_max = 2
        self.is_boss = True

    def skill1_logic(self):
        def buffed_target_amplify(self, target, is_crit):
            buffs = len(target.get_active_removable_effects(get_buffs=True, get_debuffs=False))
            return self.attack(multiplier=4.0, repeat=buffs, target_list=[target])
        damage_dealt = self.attack(multiplier=6.0, repeat=1, target_kw1="n_enemy_in_front", target_kw2="1", additional_attack_after_dmg=buffed_target_amplify)
        return damage_dealt


    def skill2_logic(self):
        self.skill1_cooldown = 0
        self.apply_effect(StatsEffect('Judgement', 3, True, {'spd' : 2.0}))
        def buff_amplify(self, target, final_damage):
            buffs = len(target.get_active_removable_effects(get_buffs=True, get_debuffs=False))
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
        

class ReconMecha(Monster): 
    def __init__(self, name, lvl, exp=0, equip=None, image=None):
        super().__init__(name, lvl, exp, equip, image)
        self.original_name = "ReconnaissanceMecha"
        self.skill1_description = "Attack closest enemy with 280% atk 2 times, if target has no active buff, increase damage by 100%."
        self.skill2_description = "Attack closest enemy with 280% atk 2 times, if target has no active buff, target defense is reduced by 20% for 24 turns."
        self.skill3_description = "Every turn, at the end of turn, if an enemy is fallen in this turn, recover hp by 30% of maxhp."
        self.skill1_description_jp = "最も近い敵に攻撃力280%で2回攻撃。対象がアクティブバフを持っていない場合、ダメージを100%増加。"
        self.skill2_description_jp = "最も近い敵に攻撃力280%で2回攻撃。対象がアクティブバフを持っていない場合、24ターンの間防御力を20%減少。"
        self.skill3_description_jp = "毎ターン、ターンの終わりに、このターンに敵が倒された場合、最大HPの30%回復。"
        self.skill1_cooldown_max = 4
        self.skill2_cooldown_max = 4
        self.is_boss = False
        self.enemycounter = len(self.enemy)

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
                target.apply_effect(StatsEffect('Defence Break', 24, False, {'defense' : 0.8}))
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


class SecurityRobot(Monster): 
    def __init__(self, name, lvl, exp=0, equip=None, image=None):
        super().__init__(name, lvl, exp, equip, image)
        self.original_name = "SecurityRobot"
        self.skill1_description = "All enemies that without active buffs have their defense reduced by 12% for 24 turns, critical defense reduced by 24% for 24 turns," \
        " evasion reduced by 36% for 24 turns."
        self.skill2_description = "Attack closest enemy for 300% atk 3 times, if target has no active buff, strike a critical hit."
        self.skill3_description = "Maxhp increased by 30%."
        self.skill1_description_jp = "アクティブバフを持っていない全ての敵の防御力を12%、クリティカル防御力を24%、回避36%減少させる。効果は24ターン持続する。"
        self.skill2_description_jp = "最も近い敵に攻撃力300%で3回攻撃。対象がアクティブバフを持っていない場合、必ずクリティカルヒット。"
        self.skill3_description_jp = "最大HPを30%増加。"
        self.skill1_cooldown_max = 4
        self.skill2_cooldown_max = 4
        self.is_boss = False
        self.enemycounter = len(self.enemy)

    def skill1_logic(self):
        for e in self.enemy:
            if len(e.get_active_removable_effects(get_buffs=True, get_debuffs=False)) == 0:
                e.apply_effect(StatsEffect('Analyzed', 8, False, {'defense' : 0.88, 'critdef' : -0.24, 'eva' : -0.36}))
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


class Thiefc(Monster):
    """
    Can confuse the target if no active buffs
    """
    def __init__(self, name, lvl, exp=0, equip=None, image=None):
        super().__init__(name, lvl, exp, equip, image)
        self.original_name = "Thiefc"
        self.skill1_description = "Attack 1 closest enemy with 160% atk 8 times, if target has no active buff, confuse the target for 12 turns."
        self.skill2_description = "Attack 1 closest enemy with 160% atk 9 times, each attack has a 9% chance to remove 1 active buff from target." 
        self.skill3_description = "At start of battle, apply Almost All Stats Up for 3 allies of highest atk for 30 turns," \
        " Almost All Stats Up increases all main stats except speed by 5%."
        self.skill1_description_jp = "最も近い敵1体に攻撃力の160%で8回攻撃し、対象にアクティブなバフがない場合、12ターンの間「混乱」を付与する。"
        self.skill2_description_jp = "最も近い敵1体に攻撃力の150%で9回攻撃し、各攻撃には9%の確率で対象のアクティブなバフを1つ解除する。"
        self.skill3_description_jp = "戦闘開始時、攻撃力が最も高い味方3人に30ターンの間「ほぼ全ステータスアップ」を付与する。ほぼ全ステータスアップは、速度を除く全ての主要ステータスを5%増加させる。"
        self.skill1_cooldown_max = 4
        self.skill2_cooldown_max = 4
        self.is_boss = False

    def skill1_logic(self):
        def confuse_target(self, target):
            if len(target.get_active_removable_effects(get_buffs=True, get_debuffs=False)) == 0:
                target.apply_effect(ConfuseEffect('Confuse', 12, False))
        damage_dealt = self.attack(multiplier=1.6, repeat=8, func_after_dmg=confuse_target, target_kw1="enemy_in_front")
        return damage_dealt


    def skill2_logic(self):
        def remove_buff(self, target: character.Character):
            if random.randint(1, 100) <= 9:
                target.remove_random_amount_of_buffs(1, False)
        damage_dealt = self.attack(multiplier=1.6, repeat=9, func_after_dmg=remove_buff, target_kw1="enemy_in_front")
        return damage_dealt


    def skill3(self):
        pass

    def battle_entry_effects(self):
        # "n_highest_attr", n, attr, party
        allies = list(self.target_selection(keyword="n_highest_attr", keyword2=3, keyword3="atk", keyword4="ally"))
        for ally in allies:
            ally.apply_effect(StatsEffect('AA Stats Up', 30, True, {'atk' : 1.05, 'defense' : 1.05, 'maxhp': 1.05}))





# ====================================
# End of No Status
# ====================================
# Stealth
# ====================================
        

class Cockatorice(Monster):
    def __init__(self, name, lvl, exp=0, equip=None, image=None):
        super().__init__(name, lvl, exp, equip, image)
        self.original_name = "Cockatorice"
        self.skill1_description = "Attack 3 closest enemies, with 300% atk."
        self.skill2_description = "Focus attack on closest enemy 3 times with 300% atk."
        self.skill3_description = "If not getting hit for 8 turns, increase atk by 77% and spd by 77% for 4 turns at the end of turn. Same effect cannot be applied twice."
        self.skill1_description_jp = "最も近い敵3体に攻撃力300%で攻撃。"
        self.skill2_description_jp = "最も近い敵に攻撃力300%で3回攻撃。"
        self.skill3_description_jp = "8ターンの間攻撃を受けていないと、ターンの終わりに攻撃力と速度を77%増加。同じ効果は2回同時に適用されない。"
        self.skill1_cooldown_max = 5
        self.skill2_cooldown_max = 5
        self.is_boss = False

    def skill1_logic(self):
        damage_dealt = self.attack(multiplier=3.0, repeat=1, target_kw1="n_enemy_in_front", target_kw2=3)
        return damage_dealt

    def skill2_logic(self):
        damage_dealt = self.attack(multiplier=3.0, repeat_seq=3, target_kw1="enemy_in_front")
        return damage_dealt
        
    def skill3(self):
        pass

    def battle_entry_effects(self):
        effect = StatsEffect("Cockatorice Madness", 4, True, {'atk' : 1.77, 'spd' : 1.77})
        effect.apply_rule = "stack"
        passive = NotTakingDamageEffect("Cockatorice Passive", -1, True, 8, effect)
        passive.can_be_removed_by_skill = False
        self.apply_effect(passive)


class Cockatrice(Monster):
    def __init__(self, name, lvl, exp=0, equip=None, image=None):
        super().__init__(name, lvl, exp, equip, image)
        self.original_name = "Cockatrice"
        self.skill1_description = "Attack 3 closest enemies, with 270% atk, their defense is reduced by 20% for 16 turns."
        self.skill2_description = "Focus attack on closest enemy 3 times with 270% atk, each attack reduces target critdmg by 30% for 16 turns."
        self.skill3_description = "For 8 turns, if not getting hit, increase crit def by 77% and def by 77% for 8 turns at the end of turn. Same effect cannot be applied twice."
        self.skill1_description_jp = "最も近い敵3体に攻撃力270%で攻撃し、16ターンの間防御力を20%減少させる。"
        self.skill2_description_jp = "最も近い敵に攻撃力270%で3回攻撃し、各攻撃で16ターンの間クリティカルダメージを30%減少させる。"
        self.skill3_description_jp = "8ターンの間攻撃を受けていない場合、ターンの終わりにクリティカル防御力と防御力を77%増加。同じ効果は2回同時に適用されない。"
        self.skill1_cooldown_max = 5
        self.skill2_cooldown_max = 5
        self.is_boss = False

    

    def skill1_logic(self):
        def defence_break(self, target):
            target.apply_effect(StatsEffect('Defence Down', 16, False, {'defense' : 0.8}))
        damage_dealt = self.attack(multiplier=2.7, repeat=1, target_kw1="n_enemy_in_front", target_kw2=3, func_after_dmg=defence_break)
        return damage_dealt

    def skill2_logic(self):
        def critdmg_reduction(self, target):
            target.apply_effect(StatsEffect('Critdmg Down', 16, False, {'critdmg' : -0.3}))
        damage_dealt = self.attack(multiplier=2.7, repeat_seq=3, target_kw1="enemy_in_front", func_after_dmg=critdmg_reduction)
        return damage_dealt
        
    def skill3(self):
        pass

    def battle_entry_effects(self):
        effect = StatsEffect("Cockatorice Madness", 8, True, {'critdef' : 0.77, 'defense' : 1.77})
        effect.apply_rule = "stack"
        passive = NotTakingDamageEffect("Cockatorice Passive", -1, True, 8, effect)
        passive.can_be_removed_by_skill = False
        self.apply_effect(passive)


class Fanatic(Monster):
    def __init__(self, name, lvl, exp=0, equip=None, image=None):
        super().__init__(name, lvl, exp, equip, image)
        self.original_name = "Fanatic"
        self.skill1_description = "Attack closest enemy with 340% atk 3 times. If has not getting hit for 6 turns, land critical strikes."
        self.skill2_description = "Attack closest enemy with 340% atk 3 times. If has not getting hit for 6 turns, damage is increased by 6% of target maxhp."
        self.skill3_description = "Recover hp by 30% of damage dealt in skill attacks."
        self.skill1_description_jp = "最も近い敵に攻撃力340%で3回攻撃。6ターン攻撃を受けていない場合、必ずクリティカルヒットになる。"
        self.skill2_description_jp = "最も近い敵に攻撃力340%で3回攻撃。6ターン攻撃を受けていない場合、ダメージは対象の最大HPの6%増加。"
        self.skill3_description_jp = "スキル攻撃で与えたダメージの30%でHPを回復する。"
        self.skill1_cooldown_max = 5
        self.skill2_cooldown_max = 5
        self.is_boss = False

    

    def skill1_logic(self):
        if self.get_num_of_turns_not_taken_damage() < 6:
            damage_dealt = self.attack(multiplier=3.4, repeat=3, target_kw1="enemy_in_front")
        else:
            damage_dealt = self.attack(multiplier=3.4, repeat=3, target_kw1="enemy_in_front", always_crit=True)
        if self.is_alive():
            self.heal_hp(damage_dealt * 0.3, self)
        return damage_dealt

    def skill2_logic(self):
        def damage_amplify(self, target, final_damage):
            if self.get_num_of_turns_not_taken_damage() >= 6:
                final_damage += target.maxhp * 0.06
            return final_damage
        damage_dealt = self.attack(multiplier=3.4, repeat=3, target_kw1="enemy_in_front", func_damage_step=damage_amplify)
        if self.is_alive():
            self.heal_hp(damage_dealt * 0.3, self)
        return damage_dealt

        
    def skill3(self):
        pass


class Emperor(Monster):
    """
    Stealth is countered by any continuous damage
    """
    def __init__(self, name, lvl, exp=0, equip=None, image=None):
        super().__init__(name, lvl, exp, equip, image)
        self.original_name = "Emperor"
        self.skill1_description = "Attack closest enemy with 280% atk 2 times, for each alive ally, damage increased by 20%."
        self.skill2_description = "Attack closest enemy with 560% atk, for each alive ally, damage increased by 20%."
        self.skill3_description = "If has not getting hit for 10 turns, apply Pride to all allies for 10 turns at end of turn. Pride: increase atk, def, spd by 60%"
        self.skill1_description_jp = "最も近い敵に攻撃力280%で2回攻撃し、生存している味方1体につき20%ダメージ増加。"
        self.skill2_description_jp = "最も近い敵に攻撃力560%で攻撃し、生存している味方1体につき20%ダメージ増加。"
        self.skill3_description_jp = "10ターン攻撃を受けていない場合、ターンの終わりに全ての味方に10ターン栄耀を付与。栄耀：攻撃力、防御力、速度を60%増加。"
        self.skill1_cooldown_max = 5
        self.skill2_cooldown_max = 5
        self.is_boss = True

    

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
        if self.get_num_of_turns_not_taken_damage() >= 10 and self.is_alive():
            for ally in self.ally:
                if not ally.has_effect_that_named('Emperor Pride'):
                    ally.apply_effect(StatsEffect('Emperor Pride', 10, True, {'atk' : 1.6, 'spd' : 1.6, 'defense' : 1.6}))
        super().status_effects_at_end_of_turn()


# ====================================
# End of Stealth
# ====================================
# Attack related
# ====================================
    

class Tanuki(Monster):
    def __init__(self, name, lvl, exp=0, equip=None, image=None):
        super().__init__(name, lvl, exp, equip, image)
        self.original_name = "Tanuki"
        self.skill1_description = "Boost atk for two allies of highest atk and accuracy by 20% for 24 turns."
        self.skill2_description = "Attack closest enemy with 1 damage, increase self evasion by 20% for 18 turns."
        self.skill3_description = "Normal attack resets cooldown of skill 1 and deals 400% atk damage instead of 200% and attack 2 times."
        self.skill1_description_jp = "最も攻撃力が高い2体の味方の攻撃力と命中率を20%増加させ、24ターン持続。"
        self.skill2_description_jp = "最も近い敵に1ダメージで攻撃し、18ターンの間自身の回避率を20%増加。"
        self.skill3_description_jp = "通常攻撃でスキル1のクールダウンをリセットし、攻撃力の400%で攻撃し、2回攻撃する。"
        self.skill1_cooldown_max = 5
        self.skill2_cooldown_max = 5
        self.is_boss = False

    

    def skill1_logic(self):
        self.update_ally_and_enemy()
        targets = self.target_selection(keyword="n_highest_attr", keyword2="2", keyword3="atk", keyword4="ally")
        for target in targets:
            target.apply_effect(StatsEffect('Tanuki Buff', 24, True, {'atk' : 1.2, 'acc' : 0.2}))

    def skill2_logic(self):
        damage_dealt = self.attack(repeat=1, target_kw1="enemy_in_front", func_damage_step=lambda self, target, final_damage : 1)
        self.apply_effect(StatsEffect('Tanuki Evasion', 20, True, {'eva' : 0.2}))
        return damage_dealt
        
    def skill3(self):
        pass

    def normal_attack(self):
        self.skill1_cooldown = 0
        self.attack(multiplier=4.0, repeat=2)
        

class Werewolf(Monster):
    def __init__(self, name, lvl, exp=0, equip=None, image=None):
        super().__init__(name, lvl, exp, equip, image)
        self.original_name = "Werewolf"
        self.skill1_description = "Focus attack 1 enemy with highest atk with 250% atk 3 times. Each attack decreases target atk by 3% for 20 turns."
        self.skill2_description = "Attack 3 enemies with highest atk with 220% atk 2 times. If target has lower atk than self, increase damage by 40%."
        self.skill3_description = "Increase atk by 15%. At start of battle, increase atk by 15% for 15 turns for self and neighboring allies."
        self.skill1_description_jp = "最も攻撃力が高い敵に攻撃力250%で3回集中攻撃。各攻撃で対象の攻撃力を3%減少させ、20ターン持続。"
        self.skill2_description_jp = "最も攻撃力が高い敵3体に攻撃力220%で2回攻撃。対象の攻撃力が自身より低い場合、ダメージを40%増加。"
        self.skill3_description_jp = "攻撃力を15%増加。戦闘開始時、自身と隣接する味方に15ターンの間攻撃力を15%増加。"
        self.skill1_cooldown_max = 5
        self.skill2_cooldown_max = 5
        self.is_boss = False

    

    def skill1_logic(self):
        def atk_down(self, target):
            target.apply_effect(StatsEffect('Atk Down', 20, False, {'atk' : 0.97}))
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


class Kunoichi(Monster):
    def __init__(self, name, lvl, exp=0, equip=None, image=None):
        super().__init__(name, lvl, exp, equip, image)
        self.original_name = "Kunoichi"
        self.skill1_description = "For 4 turns, increase accuracy by 20%, attack 3 closest enemies with 240% atk 2 times." \
        " For 24 turns, target has 10% decreased atk."
        self.skill2_description = "For 4 turns, increase atk by 20%, attack closest enemy with 450% atk." \
        " For 24 turns, target has 20% decreased atk."
        self.skill3_description = "Self and neighboring allies have increased penetration by 20%."
        self.skill1_description_jp = "4ターンの間、命中率を20%増加させ、最も近い敵3体に攻撃力240%で2回攻撃。24ターンの間、対象の攻撃力を10%減少。"
        self.skill2_description_jp = "4ターンの間、攻撃力を20%増加させ、最も近い敵に攻撃力450%で攻撃。24ターンの間、対象の攻撃力を20%減少。"
        self.skill3_description_jp = "自身と隣接する味方の貫通力を20%増加。"
        self.skill1_cooldown_max = 5
        self.skill2_cooldown_max = 5
        self.is_boss = False

    

    def skill1_logic(self):
        self.apply_effect(StatsEffect('Acc Up', 4, True, {'acc' : 0.2}))
        def atk_down(self, target):
            target.apply_effect(StatsEffect('Atk Down', 24, False, {'atk' : 0.90}))
        damage_dealt = self.attack(multiplier=2.4, repeat_seq=2, func_after_dmg=atk_down, target_kw1="n_enemy_in_front", target_kw2="3")
        return damage_dealt

    def skill2_logic(self):
        self.apply_effect(StatsEffect('Atk Up', 4, True, {'atk' : 1.2}))
        def atk_down(self, target):
            target.apply_effect(StatsEffect('Atk Down', 24, False, {'atk' : 0.80}))
        damage_dealt = self.attack(multiplier=4.5, repeat=1, func_after_dmg=atk_down, target_kw1="enemy_in_front")
        return damage_dealt

    def skill3(self):
        pass

    def battle_entry_effects(self):
        self_and_neighbors = self.get_neighbor_allies_including_self()
        for ally in self_and_neighbors:
            ally.apply_effect(StatsEffect('Sharp', -1, True, {'penetration' : 0.2}, can_be_removed_by_skill=False))


class ArabianSoldier(Monster):
    def __init__(self, name, lvl, exp=0, equip=None, image=None):
        super().__init__(name, lvl, exp, equip, image)
        self.original_name = "ArabianSoldier"
        self.skill1_description = "For 10 turns, increase atk by 20%, focus attack on enemy with highest atk with 300% atk 2 times."
        self.skill2_description = "For 10 turns, increase def by 20%, recover hp by 30% of maxhp."
        self.skill3_description = "At start of battle, increase atk and def by 20% for 15 turns for self and neighboring allies."
        self.skill1_description_jp = "10ターンの間、攻撃力を20%増加させ、最も攻撃力が高い敵に攻撃力300%で2回集中攻撃。"
        self.skill2_description_jp = "10ターンの間、防御力を20%増加させ、最大HPの30%回復。"
        self.skill3_description_jp = "戦闘開始時、自身と隣接する味方に15ターンの間攻撃力と防御力を20%増加。"
        self.skill1_cooldown_max = 4
        self.skill2_cooldown_max = 4
        self.is_boss = False

    

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


class Infantry(Monster):
    def __init__(self, name, lvl, exp=0, equip=None, image=None):
        super().__init__(name, lvl, exp, equip, image)
        self.original_name = "Infantry"
        self.skill1_description = "Attack closest enemy with 280% atk 3 times, each attack has a 30% chance to inflict Atk Down for 24 turns, atk is decreased by 8%."
        self.skill2_description = "Attack closest enemy with 280% atk 4 times."
        self.skill3_description = "Skill damage increased by 50% if target atk is lower than self."
        self.skill1_description_jp = "最も近い敵に攻撃力280%で3回攻撃。各攻撃30%確率で攻撃力を8%減少させる攻撃力ダウンを24ターン付与する。"
        self.skill2_description_jp = "最も近い敵に攻撃力280%で4回攻撃。"
        self.skill3_description_jp = "対象の攻撃力が自身より低い場合、スキルダメージを50%増加。"
        self.skill1_cooldown_max = 5
        self.skill2_cooldown_max = 5
        self.is_boss = False

    

    def skill1_logic(self):
        def atk_down(self, target):
            if random.random() < 0.3:
                target.apply_effect(StatsEffect('Atk Down', 24, False, {'atk' : 0.92}))
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


# ====================================
# End of Attack related
# ====================================
# Regeneration & Revival
# ====================================
        
class Mushroom(Monster):
    def __init__(self, name, lvl, exp=0, equip=None, image=None):
        super().__init__(name, lvl, exp, equip, image)
        self.original_name = "Mushroom"
        self.skill1_description = "Focus attack on 3 closest enemies with 240% atk 2 times."
        self.skill2_description = "Heal 30% hp of maxhp and increase defense by 20% for 7 turns."
        self.skill3_description = "After taking non zero damage and hp is lower than maxhp, recover hp by 5% of maxhp."
        self.skill1_description_jp = "最も近い敵3体に攻撃力240%で2回攻撃。"
        self.skill2_description_jp = "最大HPの30%回復し、防御力を20%増加させる。"
        self.skill3_description_jp = "0以上のダメージを受けた後、HPが最大HP未満の場合、最大HPの5%回復。"
        self.skill1_cooldown_max = 5
        self.skill2_cooldown_max = 5
        self.is_boss = False

    

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


class Vampire(Monster):
    """
    Countered by heal down
    """
    def __init__(self, name, lvl, exp=0, equip=None, image=None):
        super().__init__(name, lvl, exp, equip, image)
        self.original_name = "Vampire"
        self.skill1_description = "Focus attack on 3 closest enemies with 330% atk 2 times, recover hp by 60% of damage dealt."
        self.skill2_description = "Pay 20% of current hp, attack 3 closest enemies with 150% of the amount of hp paid as fixed damage. This skill has no effect if hp is lower than 20% of maxhp. Paying hp counts as taking status damage."
        self.skill3_description = "Every turn, recover hp by 6% of maxhp."
        self.skill1_description_jp = "最も近い敵3体に攻撃力330%で攻撃し、2回攻撃。与えたダメージの60%をHP回復。"
        self.skill2_description_jp = "現在のHPの20%を消費し、最も近い敵3体に現在のHPの150%の固定ダメージを与える。HPが最大HPの20%未満の場合、このスキルは効果がない。HP消費は状態異常ダメージとして扱われる。"
        self.skill3_description_jp = "毎ターン、HPが最大HPの6%を回復する。"
        self.skill1_cooldown_max = 5
        self.skill2_cooldown_max = 5
        self.is_boss = True

    

    def skill1_logic(self):
        damage_dealt = self.attack(multiplier=3.0, repeat_seq=2, target_kw1="n_enemy_in_front", target_kw2="3")
        if self.is_alive():
            self.heal_hp(damage_dealt * 0.6, self)
        return damage_dealt

    def skill2_logic(self):
        if self.hp < self.maxhp * 0.2:
            global_vars.turn_info_string += f"{self.name} tried to use skill 2 but has no effect.\n"
            return 0
        else:
            value = self.pay_hp(self.hp * 0.2)
            if self.is_alive():
                damage_dealt = self.attack(target_kw1="n_enemy_in_front", target_kw2="3", force_dmg=value * 1.5)
            return damage_dealt

    def skill3(self):
        pass

    def battle_entry_effects(self):
        heal = ContinuousHealEffect('Vampire Passive', -1, True, lambda x, y: x.maxhp * 0.06, self, "6% of maxhp",
                                    value_function_description_jp="最大HPの6%")
        heal.can_be_removed_by_skill = False
        self.apply_effect(heal)


class Lich(Monster):
    """
    Counter revive not yet exist
    """
    def __init__(self, name, lvl, exp=0, equip=None, image=None):
        super().__init__(name, lvl, exp, equip, image)
        self.original_name = "Lich"
        self.skill1_description = "Attack closest enemy with 400% atk 3 times."
        self.skill2_description = "Attack closest enemy with 900% atk, reduce target heal efficiency by 50% for 16 turns."
        self.skill3_description = "Gain immunity to CC effect as long as having Undead effect. Undead: when defeated, revive with 100% hp next turn." \
        " Maxhp is increased by 10%. At start of battle, apply Undead effect 3 times."
        self.skill1_description_jp = "最も近い敵に攻撃力400%で3回攻撃。"
        self.skill2_description_jp = "最も近い敵に攻撃力900%で攻撃し、16ターンの間対象の回復効率を50%減少。"
        self.skill3_description_jp = "アンデッド効果を持っている間、CC効果に対して免疫を獲得。アンデッド:撃破された場合、次のターンに100%のHPで復活。最大HPが10%増加。戦闘開始時、アンデッド効果を3回付与。"
        self.skill1_cooldown_max = 4
        self.skill2_cooldown_max = 4
        self.is_boss = True

    

    def skill1_logic(self):
        damage_dealt = self.attack(multiplier=4.0, repeat=3, target_kw1="enemy_in_front")
        return damage_dealt

    def skill2_logic(self):
        def heal_efficiency_down(self, target):
            target.apply_effect(StatsEffect('Heal Efficiency Down', 16, False, {'heal_efficiency' : -0.5}))
        damage_dealt = self.attack(multiplier=9.0, repeat=1, func_after_dmg=heal_efficiency_down, target_kw1="enemy_in_front")
        return damage_dealt

    def skill3(self):
        pass

    def battle_entry_effects(self):
        for i in range(3):
            reborn = RebornEffect('Undead', -1, True, 1.0, True, self)
            reborn.can_be_removed_by_skill = False
            self.apply_effect(reborn)
        self.apply_effect(StatsEffect('Lich Passive', -1, True, {'maxhp' : 1.1}, can_be_removed_by_skill=False))
        self.hp = self.maxhp


class Cleric(Monster):
    def __init__(self, name, lvl, exp=0, equip=None, image=None):
        super().__init__(name, lvl, exp, equip, image)
        self.original_name = "Cleric"
        self.skill1_description = "Heal 3 allies with lowest hp by 600% atk."
        self.skill2_description = "Target 3 allies with lowest hp, apply a shield that absorbs up to 300% atk damage for 12 turns."
        self.skill3_description = "Heal efficiency increased by 30%."
        self.skill1_description_jp = "最もHPが低い味方3体を攻撃力600%で回復する。"
        self.skill2_description_jp = "HPが最も低い味方3体に、最大攻撃力の300%のダメージを吸収するシールドを12ターン付与する。"
        self.skill3_description_jp = "回復効率が30%増加。"
        self.skill1_cooldown_max = 4
        self.skill2_cooldown_max = 4
        self.is_boss = False

    

    def skill1_logic(self):
        targets = list(self.target_selection(keyword="n_lowest_hp_percentage_ally", keyword2="3"))
        for target in targets:
            target.heal_hp(self.atk * 6, self)

    def skill2_logic(self):
        targets = list(self.target_selection(keyword="n_lowest_hp_percentage_ally", keyword2="3"))
        for target in targets:
            target.apply_effect(AbsorptionShield('Cleric Shield', 12, True, 3 * self.atk, False))

    def skill3(self):
        pass

    def battle_entry_effects(self):
        self.apply_effect(StatsEffect('Cleric Passive', -1, True, {'heal_efficiency' : 0.3}, can_be_removed_by_skill=False))


class Priest(Monster):
    def __init__(self, name, lvl, exp=0, equip=None, image=None):
        super().__init__(name, lvl, exp, equip, image)
        self.original_name = "Priest"
        self.skill1_description = "Heal 1 ally of lowest hp by 600% atk."
        self.skill2_description = "Heal all allies by 300% atk. Before healing, increase their heal efficiency by 10% for 22 turns."
        self.skill3_description = "Maxhp is increased by 20%. When you are defeated, heal all allies except you by 600% atk."
        self.skill1_description_jp = "最もHPが低い味方1体を攻撃力600%で回復。"
        self.skill2_description_jp = "全ての味方を攻撃力300%で回復。回復前に、22ターンの間回復効率を10%増加させる。"
        self.skill3_description_jp = "最大HPが20%増加。撃破された場合、自分以外の全ての味方を自分の攻撃力600%で回復させる。"
        self.skill1_cooldown_max = 4
        self.skill2_cooldown_max = 4
        self.is_boss = False

    

    def skill1_logic(self):
        self.heal(target_kw1="n_lowest_attr", target_kw2="1", target_kw3="hp", target_kw4="ally", value=self.atk * 6)


    def skill2_logic(self):
        for ally in self.ally:
            ally.apply_effect(StatsEffect('Heal Efficiency Up', 22, True, {'heal_efficiency' : 0.1}))
        self.heal(target_kw1="n_random_ally", target_kw2="5", value=self.atk * 3)


    def skill3(self):
        pass

    def defeated_by_taken_damage(self, damage, attacker):
        self.update_ally_and_enemy()
        for ally in self.ally:
            if ally != self:
                ally.heal_hp(self.atk * 6, self)

    def battle_entry_effects(self):
        self.apply_effect(StatsEffect('Priest Passive', -1, True, {'maxhp' : 1.2}, can_be_removed_by_skill=False))
        self.hp = self.maxhp


class Kyubi(Monster):
    """
    Countered by heal down
    """
    def __init__(self, name, lvl, exp=0, equip=None, image=None):
        super().__init__(name, lvl, exp, equip, image)
        self.original_name = "Kyubi"
        self.skill1_description = "Attack random enemies 6 times with 300% atk, recover hp by 100% of damage dealt."
        self.skill2_description = "Heal random allies 6 times with 900% atk each."
        self.skill3_description = "Cancels 90% of damage that exceeds 9% of maxhp when taking damage."
        self.skill1_description_jp = "ランダムな敵に攻撃力300%で6回攻撃し、与えたダメージの100%をHP回復。"
        self.skill2_description_jp = "ランダムな味方に攻撃力900%で6回回復。"
        self.skill3_description_jp = "ダメージを受けた際、最大HPの9%を超えるダメージの90%を無効化する。"
        self.skill1_cooldown_max = 3
        self.skill2_cooldown_max = 4
        self.is_boss = True

    

    def skill1_logic(self):
        damage_dealt = self.attack(multiplier=3.0, repeat=6)
        if self.is_alive():
            self.heal_hp(damage_dealt, self)
        return damage_dealt

    def skill2_logic(self):
        healing = 0
        for i in range(6):
            healing += self.heal(value=9.0 * self.atk)
        return 0

    def skill3(self):
        pass

    def battle_entry_effects(self):
        passive = EffectShield2('Passive', -1, True, cc_immunity=False, hp_threshold=0.09, damage_reduction=0.9, shrink_rate=0)
        passive.can_be_removed_by_skill = False
        self.apply_effect(passive)


# ====================================
# End of Regeneration & Revival
# ====================================
# Anti Heal
# ====================================

class Delf(Monster):
    def __init__(self, name, lvl, exp=0, equip=None, image=None):
        super().__init__(name, lvl, exp, equip, image)
        self.original_name = "Delf"
        self.skill1_description = "Attack all enemies with 220% atk, reduce their heal efficiency by 20% for 20 turns." \
        " If target has lower than 50% hp, heal efficiency is further reduced by 40%."
        self.skill2_description = "Attack random enemies 6 times with 220% atk, each attack reduce their heal efficiency by 15% for 20 turns."
        self.skill3_description = "Accuracy is increased by 30%."
        self.skill1_description_jp = "全ての敵に攻撃力220%で攻撃し、20ターンの間回復効率を20%減少させる。対象のHPが50%未満の場合、回復効率をさらに40%減少。"
        self.skill2_description_jp = "ランダムな敵に攻撃力220%で6回攻撃。各攻撃で20ターンの間回復効率を15%減少させる。"
        self.skill3_description_jp = "命中率が30%増加。"
        self.skill1_cooldown_max = 4
        self.skill2_cooldown_max = 4
        self.is_boss = False

    

    def skill1_logic(self):
        def heal_down(self, target):
            target.apply_effect(StatsEffect('Heal Efficiency Down', 20, False, {'heal_efficiency' : -0.2}))
            if target.hp < target.maxhp * 0.5:
                target.apply_effect(StatsEffect('Heal Efficiency Down', 20, False, {'heal_efficiency' : -0.4}))
        damage_dealt = self.attack(multiplier=2.2, repeat=1, func_after_dmg=heal_down, target_kw1="n_random_enemy", target_kw2="5")
        return damage_dealt

    def skill2_logic(self):
        def heal_down(self, target):
            target.apply_effect(StatsEffect('Heal Efficiency Down', 20, False, {'heal_efficiency' : -0.15}))
        damage_dealt = self.attack(multiplier=2.2, repeat=6, func_after_dmg=heal_down)
        return damage_dealt

    def skill3(self):
        pass

    def battle_entry_effects(self):
        self.apply_effect(StatsEffect('Delf Passive', -1, True, {'acc' : 0.3}, can_be_removed_by_skill=False))


class DelfB(Monster):
    def __init__(self, name, lvl, exp=0, equip=None, image=None):
        super().__init__(name, lvl, exp, equip, image)
        self.original_name = "DelfB"
        self.skill1_description = "Attack closest enemy 3 times with 250% atk, reduce their heal efficiency by 35% for 12 turns." \
        " Before attacking, increase accuracy by 30% for 12 turns."
        self.skill2_description = "Attack closest enemy with 400% atk, if target has lower than 30% hp, " \
        " apply poison, blind and heal efficiency down by 100% for 12 turns. Poison: deals 4% of lost hp each turn. Blind: reduce accuracy by 30%."
        self.skill3_description = "speed is increased by 20%, defense is increased by 20%."
        self.skill1_description_jp = "最も近い敵に攻撃力250%で3回攻撃し、12ターンの間回復効率を35%減少させる。攻撃前、12ターンの間命中率を30%増加。"
        self.skill2_description_jp = "最も近い敵に攻撃力400%で攻撃。対象のHPが30%未満の場合、毒、暗闇を付与し、回復効率を100%減少させる。毒:失ったHPの4%のダメージ。暗闇:命中率を30%減少。"
        self.skill3_description_jp = "速度が20%、防御力が20%増加。"
        self.skill1_cooldown_max = 4
        self.skill2_cooldown_max = 4
        self.is_boss = False

    

    def skill1_logic(self):
        self.apply_effect(StatsEffect('Accuracy Up', 12, True, {'acc' : 0.3}))
        def heal_down(self, target):
            target.apply_effect(StatsEffect('Heal Efficiency Down', 12, False, {'heal_efficiency' : -0.35}))
        damage_dealt = self.attack(multiplier=2.5, repeat=3, func_after_dmg=heal_down, target_kw1="enemy_in_front")
        return damage_dealt

    def skill2_logic(self):
        def massive_debuff(self, target):
            if target.hp < target.maxhp * 0.3:
                target.apply_effect(ContinuousDamageEffect_Poison('Poison', 10, False, ratio=0.04, imposter=self, base="losthp"))
                target.apply_effect(StatsEffect('Blind', 10, False, {'acc' : -0.3}))
                target.apply_effect(StatsEffect('Heal Efficiency Down', 12, False, {'heal_efficiency' : -1.0}))
        damage_dealt = self.attack(multiplier=4.0, repeat=1, func_after_dmg=massive_debuff, target_kw1="enemy_in_front")
        return damage_dealt


    def skill3(self):
        pass

    def battle_entry_effects(self):
        self.apply_effect(StatsEffect('DelfB Passive', -1, True, {'spd' : 1.2, 'defense': 1.2}, can_be_removed_by_skill=False))


class Darkpriest(Monster):
    def __init__(self, name, lvl, exp=0, equip=None, image=None):
        super().__init__(name, lvl, exp, equip, image)
        self.original_name = "Darkpriest"
        self.skill1_description = "Attack all enemies with 300% atk, reduce their heal efficiency by 60% for 12 turns." \
        " Before attacking, increase defense by 30% for 12 turns."
        self.skill2_description = "Attack closest enemy with 600% atk, reduce heal efficiency by 90% for 12 turns." \
        " Before attacking, increase accuracy by 30% for 12 turns."
        self.skill3_description = "Heal efficiency is reduced by 90%. When you are defeated, all allies except you take 300% atk status damage."
        self.skill1_description_jp = "全ての敵に攻撃力300%で攻撃し、12ターンの間回復効率を60%減少させる。攻撃前、12ターンの間防御力を30%増加。"
        self.skill2_description_jp = "最も近い敵に攻撃力600%で攻撃し、12ターンの間回復効率を90%減少させる。攻撃前、12ターンの間命中率を30%増加。"
        self.skill3_description_jp = "回復効率が90%減少。撃破された場合、自分以外の全ての味方に攻撃力300%の状態異常ダメージを与える。"
        self.skill1_cooldown_max = 4
        self.skill2_cooldown_max = 4
        self.is_boss = False

    

    def skill1_logic(self):
        self.apply_effect(StatsEffect('Def Up', 12, True, {'defense' : 1.3}))
        def heal_down(self, target):
            target.apply_effect(StatsEffect('Heal Down', 12, False, {'heal_efficiency' : -0.6}))
        damage_dealt = self.attack(multiplier=3.0, repeat=1, func_after_dmg=heal_down, target_kw1="n_random_enemy", target_kw2="5")
        return damage_dealt


    def skill2_logic(self):
        self.apply_effect(StatsEffect('Accuracy Up', 12, True, {'acc' : 0.3}))
        def heal_down(self, target):
            target.apply_effect(StatsEffect('Heal Down', 12, False, {'heal_efficiency' : -0.9}))
        damage_dealt = self.attack(multiplier=6.0, repeat=1, func_after_dmg=heal_down, target_kw1="enemy_in_front")
        return damage_dealt


    def skill3(self):
        pass

    def defeated_by_taken_damage(self, damage, attacker):
        self.update_ally_and_enemy()
        for ally in self.ally:
            if ally != self:
                ally.take_status_damage(self.atk * 3, self)

    def battle_entry_effects(self):
        self.apply_effect(StatsEffect('Darkpriest Passive', -1, False, {'heal_efficiency' : -0.9}, can_be_removed_by_skill=False))


class Chimera(Monster):
    """
    Countered by debuff removal
    """
    def __init__(self, name, lvl, exp=0, equip=None, image=None):
        super().__init__(name, lvl, exp, equip, image)
        self.original_name = "Chimera"
        self.skill1_description = "Attack 3 closest enemies with 360% atk, reduce their heal efficiency by 100% for 20 turns." \
        " Inflict Bleed for 10 turns, bleed deals 40% of atk status damage each turn."
        self.skill2_description = "Attack 1 closest enemy with 600% atk 2 times, each attack reduce heal efficiency by 60% for 20 turns." \
        " Each attack has 70% chance to inflict Bleed for 20 turns, bleed deals 40% of atk status damage each turn."
        self.skill3_description = "Increase maxhp by 30%. Normal attack deals 50% more damage, 60% chance to inflict Bleed for 20 turns" \
        " and 60% chance for Heal Down for 20 turns, heal efficiency is reduced by 30%."
        self.skill1_description_jp = "最も近い敵3体に攻撃力360%で攻撃し、20ターンの間回復効率を100%減少させる。" \
        "10ターンの間出血を付与し、出血は攻撃力の40%の状態異常ダメージを与える。"
        self.skill2_description_jp = "最も近い敵に攻撃力600%で2回攻撃。各攻撃で20ターンの間回復効率を60%減少させる。" \
        "各攻撃70%確率で20ターン出血を付与する。出血は攻撃力の40%の状態異常ダメージを与える。"
        self.skill3_description_jp = "最大HPが30%増加。通常攻撃が50%の追加ダメージを与える。" \
        "60%の確率で20ターン出血を付与し、60%の確率で20ターン治療効率を30%減少させる。"
        self.skill1_cooldown_max = 4
        self.skill2_cooldown_max = 4
        self.is_boss = True

    

    def skill1_logic(self):
        def heal_down(self, target):
            target.apply_effect(StatsEffect('Heal Down', 20, False, {'heal_efficiency' : -1.0}))
            target.apply_effect(ContinuousDamageEffect('Bleed', duration=10, is_buff=False, value=0.4 * self.atk, imposter=self))
        damage_dealt = self.attack(multiplier=3.0, repeat=1, func_after_dmg=heal_down, target_kw1="n_enemy_in_front", target_kw2="3")
        return damage_dealt

    def skill2_logic(self):
        def heal_down(self, target):
            target.apply_effect(StatsEffect('Heal Down', 20, False, {'heal_efficiency' : -0.6}))
            if random.random() < 0.7:
                target.apply_effect(ContinuousDamageEffect('Bleed', duration=20, is_buff=False, value=0.4 * self.atk, imposter=self))
        damage_dealt = self.attack(multiplier=6.0, repeat=2, func_after_dmg=heal_down, target_kw1="enemy_in_front")
        return damage_dealt

    def skill3(self):
        pass

    def battle_entry_effects(self):
        self.apply_effect(StatsEffect('Chimera Passive', -1, True, {'maxhp' : 1.3}, can_be_removed_by_skill=False))
        self.hp = self.maxhp

    def normal_attack(self):
        def damage_amplify(self, target, final_damage):
            return final_damage * 1.5
        def heal_down(self, target):
            if random.random() < 0.6:
                target.apply_effect(StatsEffect('Heal Down', 20, False, {'heal_efficiency' : -0.3}))
            if random.random() < 0.6:
                target.apply_effect(ContinuousDamageEffect('Bleed', duration=20, is_buff=False, value=0.4 * self.atk, imposter=self))
        damage_dealt = self.attack(func_after_dmg=heal_down, func_damage_step=damage_amplify)
        return damage_dealt


class Darklord(Monster):
    """
    Countered by debuff removal
    """
    def __init__(self, name, lvl, exp=0, equip=None, image=None):
        super().__init__(name, lvl, exp, equip, image)
        self.original_name = "Darklord"
        self.skill1_description = "For 1 turn, increase accuracy by 30%, attack all enemies with 400% atk and inflict Decay for 20 turns." \
        " Decay: all hp recovery effect becomes 0, take status damage equal to the recovery amount in the next turn. When the same effect is applied, the duration is refreshed. Apply Regen" \
        " for all allies for 20 turns, each turn recover 5% of maxhp."
        self.skill2_description = "For 1 turn, increase accuracy by 30%, attack all enemies with 400% atk," \
        " if there is only 1 enemy, attack with 2000% atk. Apply Def Up 2 times for all allies for 20 turns, increase defense by 30%."
        self.skill3_description = "After using skill 2, if there is a dead ally, revive it with 100% hp" \
        " and apply Decay and Poison for 20 turns. Poison: deals 10% of maxhp status damage each turn."
        self.skill1_description_jp = "1ターンの間、命中率を30%増加させ、全ての敵に攻撃力の400%で攻撃し、20ターンの間「腐敗」を付与する。腐敗:すべてのHP回復効果が無効化され、次のターンに回復量と同じ状態異常ダメージを受ける。同じ効果が再度付与された場合、持続時間が更新される。全ての味方に20ターンの間「リジェネ」を付与し、各ターンに最大HPの5%を回復する。"
        self.skill2_description_jp = "1ターンの間、命中率を30%増加させ、全ての敵に攻撃力の400%で攻撃する。敵が1体だけの場合、攻撃力の2000%で攻撃する。全ての味方に20ターンの間「防御力アップ」を2回付与し、防御力を30%増加させる。"
        self.skill3_description_jp = "スキル2を使用した後、味方が死亡している場合、その味方をHP100%で復活させ、20ターンの間「腐敗」と「毒」を付与する。毒:毎ターン最大HPの10%分の状態異常ダメージを与える。"
        self.skill1_cooldown_max = 4
        self.skill2_cooldown_max = 4
        self.is_boss = True

    

    def skill1_logic(self):
        self.apply_effect(StatsEffect('Accuracy Up', 1, True, {'acc' : 0.3}))
        def decay_effect(self, target):
            d = DecayEffect('Decay', 20, False, effect_applier=self)
            target.apply_effect(d)
        damage_dealt = self.attack(multiplier=4.0, repeat=1, func_after_dmg=decay_effect, target_kw1="n_enemy_in_front", target_kw2="5")
        if self.is_alive():
            for ally in self.ally:
                ally.apply_effect(ContinuousHealEffect('Regen', 20, True, lambda x, y: x.maxhp * 0.05, self, "5% of maxhp",
                                                        value_function_description_jp="最大HPの5%"))
        return damage_dealt

    def skill2_logic(self):
        self.apply_effect(StatsEffect('Accuracy Up', 1, True, {'acc' : 0.3}))
        if len(self.enemy) == 1:
            damage_dealt = self.attack(multiplier=20.0, repeat=1)
        else:
            damage_dealt = self.attack(multiplier=4.0, repeat=1, target_kw1="n_random_enemy", target_kw2="5")
        if self.is_alive():
            for ally in self.ally:
                ally.apply_effect(StatsEffect('Defense Up', 20, True, {'defense' : 1.3}))
            dead_ally: list[character.Character] = list(self.target_selection(keyword="n_dead_allies", keyword2="1"))
            if dead_ally:
                dead_ally[0].revive(hp_to_revive=0, hp_percentage_to_revive=1.0, healer=self)
                dead_ally[0].apply_effect(ContinuousDamageEffect_Poison('Poison', 20, False, ratio=0.10, imposter=self, base="maxhp"))
                dead_ally[0].apply_effect(DecayEffect('Decay', 20, False, effect_applier=self))
            
        return damage_dealt


    def skill3(self):
        pass







# ====================================
# End of Anti Heal
# ====================================
# Shield
# ====================================

class ClericB(Monster):
    def __init__(self, name, lvl, exp=0, equip=None, image=None):
        super().__init__(name, lvl, exp, equip, image)
        self.original_name = "ClericB"
        self.skill1_description = "Apply Absorption Shield for ally with lowest hp, shield absorbs up to 1000% atk damage for 20 turns."
        self.skill2_description = "Apply Absorption Shield for ally with highest atk, shield absorbs up to 1000% atk damage for 20 turns."
        self.skill3_description = "At start of battle, apply Absorption Shield for an ally with highest speed," \
        " shield absorbs up to 1000% atk damage for 20 turns."
        self.skill1_description_jp = "最もHPが低い味方に、最大攻撃力の1000%のダメージを吸収するシールドを20ターン付与。"
        self.skill2_description_jp = "最も攻撃力が高い味方に、最大攻撃力の1000%のダメージを吸収するシールドを20ターン付与。"
        self.skill3_description_jp = "戦闘開始時、最も速度が高い味方に、最大攻撃力の1000%のダメージを吸収するシールドを20ターン付与。"
        self.skill1_cooldown_max = 4
        self.skill2_cooldown_max = 4
        self.is_boss = False

    

    def skill1_logic(self):
        target = next(self.target_selection(keyword="n_lowest_hp_percentage_ally", keyword2="1"))
        target.apply_effect(AbsorptionShield('Shield', 20, True, 10 * self.atk, False))
        return 0

    def skill2_logic(self):
        target = next(self.target_selection(keyword="n_highest_attr", keyword2="1", keyword3="atk", keyword4="ally"))
        target.apply_effect(AbsorptionShield('Shield', 20, True, 10 * self.atk, False))
        return 0


    def skill3(self):
        pass

    def battle_entry_effects(self):
        target = next(self.target_selection(keyword="n_highest_attr", keyword2="1", keyword3="spd", keyword4="ally"))
        target.apply_effect(AbsorptionShield('Shield', -1, True, 10 * self.atk, False))


class ClericC(Monster):
    def __init__(self, name, lvl, exp=0, equip=None, image=None):
        super().__init__(name, lvl, exp, equip, image)
        self.original_name = "ClericC"
        self.skill1_description = "Apply Reduction Shield on all allies, shield reduces damage that would exceed 10% of maxhp by 50% for 12 turns."
        self.skill2_description = "Apply Cancelltion Shield on all allies, shield cancels all damage if damage is above 10% of maxhp for 12 turns," \
        " shield provides 5 uses."
        self.skill3_description = "Crit defense is increased by 20%, defense is increased by 10%."
        self.skill1_description_jp = "全ての味方に、最大HPの10%を超えるダメージを50%減少させるシールドを12ターン付与。"
        self.skill2_description_jp = "全ての味方に、最大HPの10%を超えるダメージのダメージを受けた時、そのダメージを無効化するシールドを12ターン付与。" \
        "シールドは5回使用可能。"
        self.skill3_description_jp = "クリティカル防御力が20%増加、防御力が10%増加。"
        self.skill1_cooldown_max = 4
        self.skill2_cooldown_max = 4
        self.is_boss = False

    

    def skill1_logic(self):
        for ally in self.ally:
            ally.apply_effect(EffectShield2('Shield', 12, True, cc_immunity=False, shrink_rate=0, damage_reduction=0.5, hp_threshold=0.1))
        return 0


    def skill2_logic(self):
        for ally in self.ally:
            ally.apply_effect(CancellationShield('Shield', 12, True, threshold=0.1, uses=5, cc_immunity=False))
        return 0


    def skill3(self):
        pass

    def battle_entry_effects(self):
        self.apply_effect(StatsEffect('ClericC Passive', -1, True, {'critdef' : 0.2, 'defense' : 1.1}, can_be_removed_by_skill=False))


class EarthSpirit(Monster):
    """
    Countered by shield attack shield ignore bypass damage, all of them not yet exist
    """
    def __init__(self, name, lvl, exp=0, equip=None, image=None):
        super().__init__(name, lvl, exp, equip, image)
        self.original_name = "EarthSpirit"
        self.skill1_description = "Attack enemy of lowest hp percentage with 500% atk, reduce target's heal efficiency by 200% for 8 turns."
        self.skill2_description = "Attack all enemies with 240% atk, 70% chance to apply Rooted for 12 turns." \
        " Rooted: eva reduced by 60%, def and critdef reduced by 25%."
        self.skill3_description = "At start of battle, apply Absorption Shield for all allies," \
        " shield absorbs up to 600% atk + 800% def damage for 40 turns. Defense is increased by 30%."
        self.skill1_description_jp = "HP割合が最も低い敵に攻撃力500%で攻撃し、8ターンの間回復効率を200%減少させる。"
        self.skill2_description_jp = "全ての敵に攻撃力240%で攻撃。70%の確率で12ターンの間ルートを付与。" \
        "ルート:回避率を60%減少、防御力とクリティカル防御力を25%減少。"
        self.skill3_description_jp = "戦闘開始時、全ての味方に最大攻撃力の600%+最大防御力の800%のダメージを吸収するシールドを40ターン付与。" \
        "防御力が30%増加。"
        self.skill1_cooldown_max = 5
        self.skill2_cooldown_max = 5
        self.is_boss = True

    

    def skill1_logic(self):
        def heal_down(self, target):
            target.apply_effect(StatsEffect('Heal Down', 8, False, {'heal_efficiency' : -2.0}))
        damage_dealt = self.attack(multiplier=5.0, repeat=1, func_after_dmg=heal_down, target_kw1="n_lowest_hp_percentage_enemy", target_kw2="1")
        return damage_dealt

    def skill2_logic(self):
        def root(self, target):
            if random.random() < 0.7:
                target.apply_effect(StatsEffect('Rooted', 12, False, {'eva' : -0.6, 'defense' : 0.75, 'critdef' : -0.25}))
        damage_dealt = self.attack(multiplier=2.4, repeat=1, func_after_dmg=root, target_kw1="n_random_enemy", target_kw2="5")
        return damage_dealt


    def skill3(self):
        pass

    def battle_entry_effects(self):
        for ally in self.ally:
            ally.apply_effect(AbsorptionShield('Shield', -1, True, 6.0 * self.atk + 8.0 * self.defense, False))
        self.apply_effect(StatsEffect('EarthSpirit Passive', -1, True, {'defense' : 1.3}, can_be_removed_by_skill=False))



# ====================================
# End of Shield
# ====================================
# All around Support
# ====================================
        

class ArchAngel(Monster):
    """
    Countered by buff removal
    """
    def __init__(self, name, lvl, exp=0, equip=None, image=None):
        super().__init__(name, lvl, exp, equip, image)
        self.original_name = "ArchAngel"
        self.skill1_description = "Heal all allies with 300% atk, for 20 turns, increase their atk by 30% and spd by 15%."
        self.skill2_description = "Target 1 ally with lowest hp, apply Absorption Shield that absorbs up to 600% atk damage for 8 turns." \
        " For 20 turns, increase target's defense by 30% and crit defense by 15%."
        self.skill3_description = "At start of battle, apply Absorption Shield that absorbs up to 1500% atk damage."
        self.skill1_description_jp = "全ての味方に攻撃力300%で回復し、20ターンの間攻撃力を30%、速度を15%増加させる。"
        self.skill2_description_jp = "HPが最も低い味方1体に、最大攻撃力の600%のダメージを吸収するシールドを8ターン付与。" \
        "20ターンの間防御力を30%、クリティカル防御力を15%増加させる。"
        self.skill3_description_jp = "戦闘開始時、最大攻撃力の1500%のダメージを吸収するシールドを付与。"
        self.skill1_cooldown_max = 4
        self.skill2_cooldown_max = 4
        self.is_boss = True

    

    def skill1_logic(self):
        self.update_ally_and_enemy()
        for target in self.ally:
            target.heal_hp(self.atk * 3.0, self)
            target.apply_effect(StatsEffect('Warfare', 20, True, {'atk' : 1.3, 'spd' : 1.15}))

    def skill2_logic(self):
        target = next(self.target_selection(keyword="n_lowest_hp_percentage_ally", keyword2="1"))
        target.apply_effect(AbsorptionShield('Shield', 8, True, 6 * self.atk, False))
        target.apply_effect(StatsEffect('Protection', 20, True, {'defense' : 1.3, 'critdef' : 0.15}))

    def skill3(self):
        pass

    def battle_entry_effects(self):
        shield = AbsorptionShield('Shield', -1, True, 15 * self.atk, False)
        shield.can_be_removed_by_skill = False
        self.apply_effect(shield)


class Unicorn(Monster):
    def __init__(self, name, lvl, exp=0, equip=None, image=None):
        super().__init__(name, lvl, exp, equip, image)
        self.original_name = "Unicorn"
        self.skill1_description = "Attack closest enemy with 555% atk and cause Deep Wound for 14 turns. Deep Wound: deals 50% atk status damage per turn, can be removed by healing."
        self.skill2_description = "Apply Absorption Shield for ally in the middle, shield absorbs up to 500% of self atk damage for 10 turns."
        self.skill3_description = "Increase hp by 30%."
        self.skill1_description_jp = "最も近い敵に攻撃力555%で攻撃し、14ターンの間重傷を付与。重傷:毎ターン攻撃力の50%の状態異常ダメージを与える。HP回復で解除可能。"
        self.skill2_description_jp = "中央の味方に、最大攻撃力の500%のダメージを吸収するシールドを10ターン付与。"
        self.skill3_description_jp = "HPが30%増加。"
        self.skill1_cooldown_max = 4
        self.skill2_cooldown_max = 4
        self.is_boss = False

    

    def skill1_logic(self):
        def deep_wound(self, target):
            target.apply_effect(ContinuousDamageEffect('Deep Wound', 14, False, self.atk * 0.5, self, remove_by_heal=True))
        damage_dealt = self.attack(multiplier=5.55, repeat=1, func_after_dmg=deep_wound, target_kw1="enemy_in_front")
        return damage_dealt

    def skill2_logic(self):
        t = next(self.target_selection(keyword="n_ally_in_middle", keyword2="1"))
        t.apply_effect(AbsorptionShield('Shield', 10, True, 5 * self.atk, False))

    def skill3(self):
        pass

    def battle_entry_effects(self):
        self.apply_effect(StatsEffect('Unicorn Passive', -1, True, {'maxhp' : 1.3}, can_be_removed_by_skill=False))
        self.hp = self.maxhp


class Zhenniao(Monster):
    def __init__(self, name, lvl, exp=0, equip=None, image=None):
        super().__init__(name, lvl, exp, equip, image)
        self.original_name = "Zhenniao"
        self.skill1_description = "Ally in the middle gains 20% evasion and 20% spd for 24 turns and recover hp by 200% of self atk."
        self.skill2_description = "Ally in the middle gains 20% crit rate and 40% crit damage for 24 turns and recover hp by 100% of self atk."
        self.skill3_description = "Normal attack damage increased by 120% and attack 2 times. maxhp is increased by 30%."
        self.skill1_description_jp = "中央の味方が24ターンの間回避率20%と速度20%を増加し、自身の攻撃力の200%回復。"
        self.skill2_description_jp = "中央の味方が24ターンの間クリティカル率20%とクリティカルダメージ40%を増加し、自身の攻撃力の100%回復。"
        self.skill3_description_jp = "通常攻撃のダメージが120%増加し、2回攻撃。最大HPが30%増加。"
        self.skill1_cooldown_max = 5
        self.skill2_cooldown_max = 5
        self.is_boss = False

    

    def skill1_logic(self):
        t = next(self.target_selection(keyword="n_ally_in_middle", keyword2="1"))
        t.apply_effect(StatsEffect('Evasion Buff', 24, True, {'eva' : 0.20, 'spd' : 1.20}))
        t.heal_hp(self.atk * 2, self)
        return 0

    def skill2_logic(self):
        t = next(self.target_selection(keyword="n_ally_in_middle", keyword2="1"))
        t.apply_effect(StatsEffect('Crit Rate Buff', 24, True, {'crit' : 0.20, 'critdmg' : 0.40}))
        t.heal_hp(self.atk, self)
        return 0

    def skill3(self):
        pass

    def normal_attack(self):
        self.attack(multiplier=2.0, repeat=2, func_damage_step=lambda self, target, final_damage : final_damage * 2.2)

    def battle_entry_effects(self):
        self.apply_effect(StatsEffect('Zhenniao Passive', -1, True, {'maxhp' : 1.3}, can_be_removed_by_skill=False))
        self.hp = self.maxhp


class YataGarasu(Monster):
    def __init__(self, name, lvl, exp=0, equip=None, image=None):
        super().__init__(name, lvl, exp, equip, image)
        self.original_name = "YataGarasu"
        self.skill1_description = "Ally in the middle gains 100% speed for 4 turns. For 20 turns, increase crit defense by 30% for that ally."
        self.skill2_description = "Apply Shield to 3 allies in the middle for 20 turns. Shield: the part of damage that exceeds 10% of maxhp is reduced by 50%."
        self.skill3_description = "Speed is increased by 10%. Normal attack inflict Burn for 20 turns. Burn: deals 35% atk status damage per turn."
        self.skill1_description_jp = "中央の味方に、4ターンの間速度を100%増加。20ターンの間その味方のクリティカル防御力を30%増加。"
        self.skill2_description_jp = "中央の味方3体に、20ターンの間シールドを付与。シールド:ダメージが最大HPの10%を超える部分を50%減少。"
        self.skill3_description_jp = "速度が10%増加。通常攻撃で20ターンの間燃焼を付与。燃焼:毎ターン攻撃力の35%の状態異常ダメージを与える。"
        self.skill1_cooldown_max = 5
        self.skill2_cooldown_max = 5
        self.is_boss = False

    

    def skill1_logic(self):
        t = next(self.target_selection(keyword="n_ally_in_middle", keyword2="1"))
        t.apply_effect(StatsEffect('Speed Buff', 4, True, {'spd' : 2.0}))
        t.apply_effect(StatsEffect('Crit Defense Buff', 20, True, {'critdef' : 0.3}))
        return 0

    def skill2_logic(self):
        targets = list(self.target_selection(keyword="n_ally_in_middle", keyword2="3"))
        for target in targets:
            target.apply_effect(EffectShield2('Shield', 20, True, False, damage_reduction=0.5, shrink_rate=0, hp_threshold=0.1))
        return 0

    def skill3(self):
        pass

    def normal_attack(self):
        def burn(self, target):
            target.apply_effect(ContinuousDamageEffect('Burn', 20, False, self.atk * 0.35, self))
        self.attack(multiplier=2.0, repeat=1, func_after_dmg=burn)

    def battle_entry_effects(self):
        self.apply_effect(StatsEffect('YataGarasu Passive', -1, True, {'spd' : 1.1}, can_be_removed_by_skill=False))


class Anubis(Monster):
    def __init__(self, name, lvl, exp=0, equip=None, image=None):
        super().__init__(name, lvl, exp, equip, image)
        self.original_name = "Anubis"
        self.skill1_description = "Attack 3 closest enemies with 270% atk, increase atk and def for all allies by 10% for 20 turns."
        self.skill2_description = "Attack random enemies 3 times with 240% atk, increase penetration for all allies by 10% for 20 turns."
        self.skill3_description = "When taking non zero damage, 12% chance to increase def for all allies by 12% for 20 turns."
        self.skill1_description_jp = "最も近い敵3体に攻撃力270%で攻撃し、全ての味方が20ターンの間攻撃力と防御力を10%増加。"
        self.skill2_description_jp = "ランダムな敵に攻撃力240%で3回攻撃。全ての味方が20ターンの間貫通を10%増加。"
        self.skill3_description_jp = "ダメージを受けた時、12%の確率で全ての味方の防御力を20ターン12%増加。"
        self.skill1_cooldown_max = 4
        self.skill2_cooldown_max = 4
        self.is_boss = False

    

    def skill1_logic(self):
        damage_dealt = self.attack(multiplier=2.7, repeat=1, target_kw1="n_enemy_in_front", target_kw2="3")
        for a in self.ally:
            a.apply_effect(StatsEffect('Anubis Buff', 20, True, {'atk' : 1.1, 'defense' : 1.1}))
        return damage_dealt

    def skill2_logic(self):
        damage_dealt = self.attack(multiplier=2.4, repeat=3)
        for a in self.ally:
            a.apply_effect(StatsEffect('Anubis Buff', 20, True, {'penetration' : 0.1}))
        return damage_dealt

    def skill3(self):
        pass

    def take_damage_aftermath(self, damage, attacker):
        if random.randint(1, 100) <= 12 and damage > 0:
            # print(f"{self.name} triggers skill 3.")
            for a in self.ally:
                a.apply_effect(StatsEffect('Anubis Buff', 20, True, {'defense' : 1.12}))


# ====================================
# End of All around Support
# ====================================
# Many Much Buffer
# ====================================


class Garuda(Monster):
    def __init__(self, name, lvl, exp=0, equip=None, image=None):
        super().__init__(name, lvl, exp, equip, image)
        self.original_name = "Garuda"
        self.skill1_description = "Apply random buffs to all allies until each ally has at least 4 buffs." \
        " Buff duration is random between 10 and 30 turns."
        self.skill2_description = "Attack all enemies with 400% atk."
        self.skill3_description = "At start of battle, apply 1 random buff to all allies."
        self.skill1_description_jp = "全ての味方にランダムなバフを付与し、各味方が最低4つのバフを持つまで付与する。バフの持続時間は10ターンから30ターンの間でランダムで決定される。"
        self.skill2_description_jp = "全ての敵に攻撃力の400%で攻撃する。"
        self.skill3_description_jp = "戦闘開始時に全ての味方にランダムなバフを1つ付与する。"
        self.skill1_cooldown_max = 4
        self.skill2_cooldown_max = 4
        self.is_boss = True

    

    def generate_random_buff(self):
        b1 = StatsEffect('Atk Up', 20, True, {'atk' : 1.3})
        b2 = StatsEffect('Def Up', 20, True, {'defense' : 1.3})
        b3 = StatsEffect('Spd Up', 20, True, {'spd' : 1.3})
        b4 = StatsEffect('Crit Up', 20, True, {'crit' : 0.3})
        b5 = StatsEffect('Critdmg Up', 20, True, {'critdmg' : 0.3})
        b6 = StatsEffect('Penetration Up', 20, True, {'penetration' : 0.3})
        b7 = StatsEffect('Evasion Up', 20, True, {'eva' : 0.3})
        b8 = StatsEffect('Heal Efficiency Up', 20, True, {'heal_efficiency' : 0.3})
        b9 = StatsEffect('Crit Def Up', 20, True, {'critdef' : 0.3})

        all_buffs = [b1, b2, b3, b4, b5, b6, b7, b8, b9]
        # select a random buff and return it
        final_buff = random.choice(all_buffs)
        final_buff.duration = random.randint(10, 30)
        return final_buff

    def skill1_logic(self):
        for a in self.ally:
            actual_buffs = [buff for buff in a.buffs if buff.duration > 0]
            while len(actual_buffs) < 4:
                new_buff = self.generate_random_buff()
                a.apply_effect(new_buff)
                actual_buffs.append(new_buff)
        return 0

    def skill2_logic(self):
        damage_dealt = self.attack(multiplier=4.0, repeat=1, target_kw1="n_random_enemy", target_kw2="5")
        return damage_dealt

    def skill3(self):
        pass

    def battle_entry_effects(self):
        for a in self.ally:
            a.apply_effect(self.generate_random_buff())








# ====================================
# End of Many Much Buffer
# ====================================
# Early Game Powercreep
# ====================================
        
class FootSoldier(Monster):
    def __init__(self, name, lvl, exp=0, equip=None, image=None):
        super().__init__(name, lvl, exp, equip, image)
        self.original_name = "FootSoldier"
        self.skill1_description = "Attack closest enemy with 250% atk 3 times."
        self.skill2_description = "Attack closest enemy with 550% atk, 80% chance to Cripple for 21 turns,"
        " Cripple: atk decreased by 5%, spd decreased by 10%, evasion decreased by 15%."
        self.skill3_description = "Increase atk and spd by 100%, every turn pass, effect decreases by 4% until 35th turn."
        self.skill1_description_jp = "最も近い敵に攻撃力250%で3回攻撃。"
        self.skill2_description_jp = "最も近い敵に攻撃力550%で攻撃し、80%の確率で21ターンの間障害を付与。" \
        "障害:攻撃力が5%減少、速度が10%減少、回避率が15%減少。"
        self.skill3_description_jp = "攻撃力と速度が100%増加。1ターン経過する度に効果が4%減少し、35ターン目で効果が消失する。"
        self.skill1_cooldown_max = 5
        self.skill2_cooldown_max = 5
        self.is_boss = False

    

    def skill1_logic(self):
        damage_dealt = self.attack(multiplier=2.5, repeat=3, target_kw1="enemy_in_front")
        return damage_dealt

    def skill2_logic(self):
        def cripple(self, target):
            if random.random() < 0.8:
                target.apply_effect(StatsEffect('Cripple', 7, False, {'atk' : 0.95, 'spd' : 0.9, 'eva' : -0.15}))
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


class Daji(Monster):
    """
    Buff removal is required. Divination is a ridiculous early game powercreep.
    """
    def __init__(self, name, lvl, exp=0, equip=None, image=None):
        super().__init__(name, lvl, exp, equip, image)
        self.original_name = "Daji"
        self.skill1_description = "Increase atk by 111%, accuracy by 10%, penetration by 10% for 20 turns for all allies." \
        " Every time this skill is used, atk bonus is decreased by 33%."
        self.skill2_description = "All allies are healed by 200% of atk, apply a shield that absorbs up to 300% of atk damage for 8 turns." \
        " Every time this skill is used, shield amount is decreased by 100% of atk."
        self.skill3_description = "At end of turn, if the alive allies are more than the alive enemies, apply Pride to all allies for 8 turns." \
        " Pride: increase atk by 45%. The same effect cannot be applied more than once."
        self.skill1_description_jp = "全ての味方の攻撃力を111%、命中率を10%、貫通を10%増加。" \
        "このスキルを使用する度に、攻撃力ボーナスが33%減少。"
        self.skill2_description_jp = "全ての味方を攻撃力の200%で回復し、最大攻撃力の300%のダメージを吸収するシールドを8ターン付与。" \
        "このスキルを使用する度に、シールドの量が最大攻撃力の100%減少。"
        self.skill3_description_jp = "ターン終了時、生存している味方が生存している敵より多い場合、全ての味方に8ターンの間栄耀を付与。" \
        "栄耀:攻撃力が45%増加。同じ効果は複数回適用されない。"
        self.skill1_cooldown_max = 4
        self.skill2_cooldown_max = 4
        self.is_boss = True
        self.current_atk_bonus = 1.11
        self.current_shield_bonus = 3

    

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
                a.apply_effect(StatsEffect('Divination', 20, True, {'atk' : 1.0 + self.get_atk_bonus(), 'acc' : 0.1, 'penetration' : 0.1}))
            self.current_atk_bonus -= 0.33
        else:
            for a in self.ally:
                a.apply_effect(StatsEffect('Divination', 20, True, {'acc' : 0.1, 'penetration' : 0.1}))
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
# We can either have insane damage or insane survivability that requires damage check
# ====================================
        
class EvilKing(Monster):
    """
    For late game powercreep, just take him down as fast as possible.
    """
    def __init__(self, name, lvl, exp=0, equip=None, image=None):
        super().__init__(name, lvl, exp, equip, image)
        self.original_name = "EvilKing"
        self.skill1_description = "Attack 3 closest enemies with 234% atk 3 times, multiplier increases by 2.5% for each turn passed."
        self.skill2_description = "Attack 1 cloeset enemy with 600% atk, inflict cripple for 12 turns, Cripple: atk decreased by 20%, spd decreased by 30%, evasion decreased by 40%."
        self.skill3_description = "Increase atk, defense, crit and crit damage by 1% every turn."
        self.skill1_description_jp = "最も近い敵3体に攻撃力234%で3回攻撃。ターン経過する度に倍率が2.5%増加。"
        self.skill2_description_jp = "最も近い敵に攻撃力600%で攻撃し、12ターンの間障害を付与。" \
        "障害:攻撃力が20%減少、速度が30%減少、回避率が40%減少。"
        self.skill3_description_jp = "1ターン経過する度に攻撃力、防御力、クリティカル率、クリティカルダメージが1%増加。"
        self.skill1_cooldown_max = 4
        self.skill2_cooldown_max = 4
        self.is_boss = True

    

    def skill1_logic(self):
        base_multiplier = 2.34
        turn_passed = self.battle_turns
        multiplier = base_multiplier + 0.025 * turn_passed
        damage_dealt = self.attack(multiplier=multiplier, repeat=3, target_kw1="n_enemy_in_front", target_kw2="3")
        return damage_dealt


    def skill2_logic(self):
        def cripple(self, target):
            target.apply_effect(StatsEffect('Cripple', 12, False, {'atk' : 0.8, 'spd' : 0.7, 'eva' : 0.6}))
        damage_dealt = self.attack(multiplier=6.0, repeat=1, func_after_dmg=cripple, target_kw1="enemy_in_front")
        return damage_dealt


    def skill3(self):
        pass

    def battle_entry_effects(self):
        def condition(self) -> bool:
            return True
        self.apply_effect(StatsEffect('EvilKing Passive', -1, True, {'atk' : 1.01, 'critdmg' : 0.01, 'crit' : 0.01, 'defense' : 1.01},
                                      use_active_flag=False,  condition=condition, can_be_removed_by_skill=False))


class RoyalPriest(Monster):
    """
    Very high maxhp
    """
    def __init__(self, name, lvl, exp=0, equip=None, image=None):
        super().__init__(name, lvl, exp, equip, image)
        self.original_name = "RoyalPriest"
        self.skill1_description = "Increase maxhp by 25% for all allies and heal 10% of maxhp for all allies. This effect is not removable."
        self.skill2_description = "For 25 turns, all allies have their main stats except maxhp (atk, def, spd) increased by 1% of their own maxhp."
        self.skill3_description = "Maxhp is increased by 30%, normal attack attack 4 times."
        self.skill1_description_jp = "全ての味方の最大HPを25%増加させ、最大HPの10%分HPを回復する。この効果は解除されない。"
        self.skill2_description_jp = "全ての味方の最大HPを除く主要ステータス（攻撃力、防御力、速度）が、25ターンの間、自分の最大HPの1%分増加する。"
        self.skill3_description_jp = "最大HPが30%増加し、通常攻撃が4回攻撃になる。"
        self.skill1_cooldown_max = 2
        self.skill2_cooldown_max = 4
        self.is_boss = True

    def skill1_logic(self):
        for ally in self.ally:
            ally.apply_effect(StatsEffect('Infinity', -1, True, {'maxhp' : 1.25}, can_be_removed_by_skill=False))
            ally.heal_hp(ally.maxhp * 0.1, self)
        return 0

    def skill2_logic(self):
        for ally in self.ally:
            ally.apply_effect(StatsEffect('AA Stats Up', 25, True, main_stats_additive_dict={'atk': ally.maxhp * 0.01, 'defense': ally.maxhp * 0.01, 'spd': ally.maxhp * 0.01}))
        return 0

    def skill3(self):
        pass

    def normal_attack(self):
        self.attack(repeat=4)

    def battle_entry_effects(self):
        self.apply_effect(StatsEffect('Infinity', -1, True, {'maxhp' : 1.3}, can_be_removed_by_skill=False))
        self.hp = self.maxhp


# ====================================
# End of Late Game Powercreep
# ====================================
# No ally
# ====================================
# Monster in this category either punish for being solo alive or gain benefit for being solo alive
# TODO: Add at least 1 monster in this category