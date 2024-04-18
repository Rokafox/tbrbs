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
        self.skill1_description = "最も近い敵1体に攻撃力の800%のダメージを与える。"
        self.skill2_description = "最も近い敵1体に攻撃力の700%のダメージを与え、70%の確率で対象を5ターンの間スタン状態にする。"
        self.skill3_description = "最大HPを50%増加する。"
        self.skill1_cooldown_max = 5
        self.skill2_cooldown_max = 5
        self.is_boss = False
        self.monster_role = "Heavy Attack"

    def skill_tooltip(self):
        return f"スキル 1 : {self.skill1_description}\nクールダウン : {self.skill1_cooldown} 行動\n\nスキル 2 : {self.skill2_description}\nクールダウン : {self.skill2_cooldown} 行動\n\nスキル 3 : {self.skill3_description}\n"

    def skill1_logic(self):
        damage_dealt = self.attack(multiplier=8.0, repeat=1, target_kw1="enemy_in_front")
        return damage_dealt

    def skill2_logic(self):
        def stun_effect(self, target):
            dice = random.randint(1, 100)
            if dice <= 70:
                target.apply_effect(StunEffect('スタン', duration=5, is_buff=False))
        damage_dealt = self.attack(multiplier=7.0, repeat=1, func_after_dmg=stun_effect, target_kw1="enemy_in_front")
        return damage_dealt
        
    def skill3(self):
        pass

    def battle_entry_effects(self):
        self.apply_effect(StatsEffect('パッシブ効果', -1, True, {'maxhp' : 1.5}, can_be_removed_by_skill=False))
        self.hp = self.maxhp


class Mimic(character.Character):
    def __init__(self, name, lvl, exp=0, equip=None, image=None):
        super().__init__(name, lvl, exp, equip, image)
        self.original_name = "Mimic"
        self.skill1_description = "最も近い敵1体に攻撃力の1000%のダメージを与える。"
        self.skill2_description = "最も近い敵1体に攻撃力の1000%のダメージを与える。"
        self.skill3_description = "スキル攻撃に10%の確率で対象を3ターンの間スタンさせる。"
        self.skill1_cooldown_max = 4
        self.skill2_cooldown_max = 4
        self.is_boss = False
        self.monster_role = "Heavy Attack"

    def skill_tooltip(self):
        return f"スキル 1 : {self.skill1_description}\nクールダウン : {self.skill1_cooldown} 行動\n\nスキル 2 : {self.skill2_description}\nクールダウン : {self.skill2_cooldown} 行動\n\nスキル 3 : {self.skill3_description}\n"

    def skill1_logic(self):
        def stun_effect(self, target):
            dice = random.randint(1, 100)
            if dice <= 10:
                target.apply_effect(StunEffect('スタン', duration=3, is_buff=False))
        damage_dealt = self.attack(multiplier=10.0, repeat=1, func_after_dmg=stun_effect, target_kw1="enemy_in_front")
        return damage_dealt

    def skill2_logic(self):
        def stun_effect(self, target):
            dice = random.randint(1, 100)
            if dice <= 10:
                target.apply_effect(StunEffect('スタン', duration=3, is_buff=False))
        damage_dealt = self.attack(multiplier=10.0, repeat=1, func_after_dmg=stun_effect, target_kw1="enemy_in_front")
        return damage_dealt
        
    def skill3(self):
        pass


class MoHawk(character.Character):
    def __init__(self, name, lvl, exp=0, equip=None, image=None):
        super().__init__(name, lvl, exp, equip, image)
        self.original_name = "MoHawk"
        self.skill1_description = "最も近い敵1体に攻撃し、攻撃力の680%を与え、4ターンの出血効果を与える。出血効果: 毎ターン、発動者の攻撃力の120%を状態ダメージとして受ける。"
        self.skill2_description = "最も近い敵1体に攻撃し、攻撃力の680%を与え、4ターンの出血効果を与える。"
        self.skill3_description = "攻撃力を20%増加する。"
        self.skill1_cooldown_max = 5
        self.skill2_cooldown_max = 5
        self.is_boss = False
        self.monster_role = "Heavy Attack"

    def skill_tooltip(self):
        return f"スキル 1 : {self.skill1_description}\nクールダウン : {self.skill1_cooldown} 行動\n\nスキル 2 : {self.skill2_description}\nクールダウン : {self.skill2_cooldown} 行動\n\nスキル 3 : {self.skill3_description}\n"

    def skill1_logic(self):
        def bleed_effect(self, target):
            target.apply_effect(ContinuousDamageEffect('出血', duration=4, is_buff=False, value=1.2 * self.atk, imposter=self))
        damage_dealt = self.attack(multiplier=6.8, repeat=1, func_after_dmg=bleed_effect, target_kw1="enemy_in_front")
        return damage_dealt

    def skill2_logic(self):
        def bleed_effect(self, target):
            target.apply_effect(ContinuousDamageEffect('出血', duration=4, is_buff=False, value=1.2 * self.atk, imposter=self))
        damage_dealt = self.attack(multiplier=6.8, repeat=1, func_after_dmg=bleed_effect, target_kw1="enemy_in_front")
        return damage_dealt
        
    def skill3(self):
        pass

    def battle_entry_effects(self):
        self.apply_effect(StatsEffect('パッシブ効果', -1, True, {'atk' : 1.2}, can_be_removed_by_skill=False))


class Earth(character.Character):
    def __init__(self, name, lvl, exp=0, equip=None, image=None):
        super().__init__(name, lvl, exp, equip, image)
        self.original_name = "Earth"
        self.skill1_description = "全ての敵に攻撃力の240%のダメージを与え、50%の確率で3ターンの間、スタンを与える。"
        self.skill2_description = "最も近い敵1体に攻撃力の700%のダメージを与え、70%の確率で3ターンの間、スタンを与える。"
        self.skill3_description = "HPが100%増加する。"
        self.skill1_cooldown_max = 5
        self.skill2_cooldown_max = 5
        self.is_boss = False
        self.monster_role = "Heavy Attack"

    def skill_tooltip(self):
        return f"スキル 1 : {self.skill1_description}\nクールダウン : {self.skill1_cooldown} 行動\n\nスキル 2 : {self.skill2_description}\nクールダウン : {self.skill2_cooldown} 行動\n\nスキル 3 : {self.skill3_description}\n"

    def skill1_logic(self):
        def stun_effect(self, target):
            dice = random.randint(1, 100)
            if dice <= 50:
                target.apply_effect(StunEffect('スタン', duration=3, is_buff=False))
        damage_dealt = self.attack(multiplier=2.4, repeat=1, func_after_dmg=stun_effect, target_kw1="n_random_enemy", target_kw2="5")
        return damage_dealt


    def skill2_logic(self):
        def stun_effect(self, target):
            dice = random.randint(1, 100)
            if dice <= 70:
                target.apply_effect(StunEffect('スタン', duration=3, is_buff=False))
        damage_dealt = self.attack(multiplier=7.0, repeat=1, func_after_dmg=stun_effect, target_kw1="enemy_in_front")
        return damage_dealt

    def skill3(self):
        pass

    def battle_entry_effects(self):
        self.apply_effect(StatsEffect('パッシブ効果', -1, True, {'maxhp' : 2.0}, can_be_removed_by_skill=False))
        self.hp = self.maxhp


class Golem(character.Character):
    def __init__(self, name, lvl, exp=0, equip=None, image=None):
        super().__init__(name, lvl, exp, equip, image)
        self.original_name = "Golem"
        self.skill1_description = "全ての敵に攻撃力の500%のダメージを与える。"
        self.skill2_description = "最も近い敵1体に攻撃力の700%のダメージを与える。ダメージは対象のHP割合によって増加する。最大ボーナスダメージ：100%。"
        self.skill3_description = "HPを200%増加する。"
        self.skill1_cooldown_max = 5
        self.skill2_cooldown_max = 5
        self.is_boss = True
        self.monster_role = "Heavy Attack"

    def skill_tooltip(self):
        return f"スキル 1 : {self.skill1_description}\nクールダウン : {self.skill1_cooldown} 行動\n\nスキル 2 : {self.skill2_description}\nクールダウン : {self.skill2_cooldown} 行動\n\nスキル 3 : {self.skill3_description}\n"

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
        self.apply_effect(StatsEffect('パッシブ効果', -1, True, {'maxhp' : 3.0}, can_be_removed_by_skill=False))
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
        self.skill1_description = "最も近い3体の敵に攻撃力の300%のダメージを与える。"
        self.skill2_description = "5体の敵に攻撃力の200%のダメージを与え、50%の確率で6ターンの間、呪縛を付与する。呪縛：攻撃力が40%減少し、重複不可。"
        self.skill3_description = "ダメージを受けた時、30%の確率で攻撃者に4ターンの間、呪いを付与する。呪縛：攻撃力が40%減少し、重複不可。"
        self.skill1_cooldown_max = 5
        self.skill2_cooldown_max = 5
        self.is_boss = False

    def skill_tooltip(self):
        return f"スキル 1 : {self.skill1_description}\nクールダウン : {self.skill1_cooldown} 行動\n\nスキル 2 : {self.skill2_description}\nクールダウン : {self.skill2_cooldown} 行動\n\nスキル 3 : {self.skill3_description}\n"

    def skill1_logic(self):
        damage_dealt = self.attack(target_kw1="n_enemy_in_front",target_kw2="3", multiplier=3.0, repeat=1)
        return damage_dealt

    def skill2_logic(self):
        def curse_effect(self, target):
            dice = random.randint(1, 100)
            if dice <= 50:
                curse = StatsEffect('呪縛', duration=6, is_buff=False, stats_dict={'atk' : 0.6})
                curse.apply_rule = "stack"
                target.apply_effect(curse)
        damage_dealt = self.attack(target_kw1="n_random_enemy",target_kw2="5", multiplier=2.0, repeat=1, func_after_dmg=curse_effect)
        return damage_dealt
        
    def skill3(self):
        pass

    def take_damage_aftermath(self, damage, attacker):
        if random.randint(1, 100) <= 30:
            curse = StatsEffect('呪縛', duration=4, is_buff=False, stats_dict={'atk' : 0.6})
            curse.apply_rule = "stack"
            attacker.apply_effect(curse)


class Pharaoh(character.Character):
    def __init__(self, name, lvl, exp=0, equip=None, image=None):
        super().__init__(name, lvl, exp, equip, image)
        self.original_name = "Pharaoh"
        self.skill1_description = "最も近い3体の敵に攻撃力の320%で攻撃する。対象が呪い状態の場合、ダメージが100%増加する。"
        self.skill2_description = "最も近い3体の敵に攻撃力の320%で攻撃し、80%の確率で8ターンの間呪縛を付与する。対象が呪縛状態の場合、ダメージが100%増加する。呪縛：攻撃力が40%減少する、重複なし。"
        self.skill3_description = "HP、攻撃力、防御力、速度が20%増加する。ダメージを受けたとき、40%の確率で攻撃者に3ターンの間呪縛を付与する。ターンの終わりに、呪縛状態の敵がいる場合、3ターンの間攻撃力を30%増加する。"
        self.skill1_cooldown_max = 5
        self.skill2_cooldown_max = 3
        self.is_boss = True

    def skill_tooltip(self):
        return f"スキル 1 : {self.skill1_description}\nクールダウン : {self.skill1_cooldown} 行動\n\nスキル 2 : {self.skill2_description}\nクールダウン : {self.skill2_cooldown} 行動\n\nスキル 3 : {self.skill3_description}\n"

    def skill1_logic(self):
        def curse_amplify(self, target, final_damage):
            if target.has_effect_that_named("呪縛"):
                final_damage *= 2.0
            return final_damage
        damage_dealt = self.attack(target_kw1="n_enemy_in_front",target_kw2="3", multiplier=3.2, repeat=1, func_damage_step=curse_amplify)
        return damage_dealt

    def skill2_logic(self):
        def curse_amplify(self, target, final_damage):
            if target.has_effect_that_named("呪縛"):
                final_damage *= 2.0
            return final_damage
        def curse_effect(self, target):
            dice = random.randint(1, 100)
            if dice <= 80:
                curse = StatsEffect('呪縛', duration=8, is_buff=False, stats_dict={'atk' : 0.7})
                curse.apply_rule = "stack"
                target.apply_effect(curse)
        damage_dealt = self.attack(target_kw1="n_enemy_in_front",target_kw2="3", multiplier=3.2, repeat=1, func_damage_step=curse_amplify, func_after_dmg=curse_effect)
        return damage_dealt
        
    def skill3(self):
        pass

    def take_damage_aftermath(self, damage, attacker):
        if random.randint(1, 100) <= 40:
            curse = StatsEffect('呪縛', duration=3, is_buff=False, stats_dict={'atk' : 0.7})
            curse.apply_rule = "stack"
            attacker.apply_effect(curse)

    def battle_entry_effects(self):
        self.apply_effect(StatsEffect('強靭', -1, True, {'maxhp' : 1.2, 'atk' : 1.2, 'defense' : 1.2, 'spd' : 1.2}, can_be_removed_by_skill=False))
        self.hp = self.maxhp
        passive = PharaohPassiveEffect('パッシブ効果', -1, True, 1.3)
        passive.can_be_removed_by_skill = False
        self.apply_effect(passive)


class PoisonSlime(character.Character):
    def __init__(self, name, lvl, exp=0, equip=None, image=None):
        super().__init__(name, lvl, exp, equip, image)
        self.original_name = "Poison_Slime"
        self.skill1_description = "5体の敵に攻撃力の150%のダメージを与え、66%の確率で6ターンの間、毒を付与する。毒：ターンごとに現在のHPの7%の状態ダメージを受ける。"
        self.skill2_description = "5体の敵に攻撃力の150%のダメージを与え、66%の確率で6ターンの間、毒を付与する。毒：ターンごとに失ったHPの7%の状態ダメージを受ける。"
        self.skill3_description = "受けるダメージを10%減少させる。"
        self.skill1_cooldown_max = 5
        self.skill2_cooldown_max = 5
        self.is_boss = False

    def skill_tooltip(self):
        return f"スキル 1 : {self.skill1_description}\nクールダウン : {self.skill1_cooldown} 行動\n\nスキル 2 : {self.skill2_description}\nクールダウン : {self.skill2_cooldown} 行動\n\nスキル 3 : {self.skill3_description}\n"

    def skill1_logic(self):
        def poison_effect(self, target):
            dice = random.randint(1, 100)
            if dice <= 66:
                target.apply_effect(PoisonDamageEffect('毒', duration=6, is_buff=False, value=0.07, imposter=self, base="hp"))
        damage_dealt = self.attack(target_kw1="n_random_enemy",target_kw2="5", multiplier=1.5, repeat=1, func_after_dmg=poison_effect)
        return damage_dealt

    def skill2_logic(self):
        def poison_effect(self, target):
            dice = random.randint(1, 100)
            if dice <= 66:
                target.apply_effect(PoisonDamageEffect('毒', duration=6, is_buff=False, value=0.07, imposter=self, base="losthp"))
        damage_dealt = self.attack(target_kw1="n_random_enemy",target_kw2="5", multiplier=1.5, repeat=1, func_after_dmg=poison_effect)
        return damage_dealt
        
    def skill3(self):
        pass

    def battle_entry_effects(self):
        self.apply_effect(StatsEffect('パッシブ効果', -1, True, {'final_damage_taken_multipler' : -0.1}, can_be_removed_by_skill=False))


class MadScientist(character.Character):
    def __init__(self, name, lvl, exp=0, equip=None, image=None):
        super().__init__(name, lvl, exp, equip, image)
        self.original_name = "MadScientist"
        self.skill1_description = "全ての敵に攻撃力の210%のダメージを与え、50%の確率で12ターンの間、疫病を感染させる。疫病：ターン終了時、30%の確率で隣接する味方に同じ効果を適用する。毎ターン、失われたHPの7%に相当する状態ダメージを受ける。"
        self.skill2_description = "最も近い3体の敵に攻撃力の300%のダメージを与える。対象が疫病に感染している場合、12ターンの間、回復効率が50%減少する。"
        self.skill3_description = "通常攻撃ダメージが30%増加、10%の確率で12ターンの間、疫病を付与する。"
        self.skill1_cooldown_max = 5
        self.skill2_cooldown_max = 4
        self.is_boss = True

    def skill_tooltip(self):
        return f"スキル 1 : {self.skill1_description}\nクールダウン : {self.skill1_cooldown} 行動\n\nスキル 2 : {self.skill2_description}\nクールダウン : {self.skill2_cooldown} 行動\n\nスキル 3 : {self.skill3_description}\n"

    def skill1_logic(self):
        def plague_effect(self, target):
            dice = random.randint(1, 100)
            if dice <= 50:
                target.apply_effect(PlagueEffect('疫病', duration=12, is_buff=False, value=0.07, imposter=self, base="losthp", transmission_chance=0.3))
        damage_dealt = self.attack(target_kw1="n_random_enemy", target_kw2="5", multiplier=2.1, repeat=1, func_after_dmg=plague_effect)
        return damage_dealt

    def skill2_logic(self):
        def plague_effect(self, target):
            if target.has_effect_that_named("疫病", None, "PlagueEffect"):
                target.apply_effect(StatsEffect('Healing Down', duration=12, is_buff=False, stats_dict={'heal_efficiency' : -0.5}))
        damage_dealt = self.attack(target_kw1="n_enemy_in_front", target_kw2="3", multiplier=3.0, repeat=1, func_after_dmg=plague_effect)
        return damage_dealt
        
    def skill3(self):
        pass

    def normal_attack(self):
        def plague_effect(self, target):
            dice = random.randint(1, 100)
            if dice <= 10:
                target.apply_effect(PlagueEffect('疫病', duration=12, is_buff=False, value=0.07, imposter=self, base="losthp", transmission_chance=0.3))
        def amplify(self, target, final_damage):
            final_damage *= 1.3
            return final_damage
        self.attack(func_after_dmg=plague_effect, func_damage_step=amplify)


class Ghost(character.Character):
    def __init__(self, name, lvl, exp=0, equip=None, image=None):
        super().__init__(name, lvl, exp, equip, image)
        self.original_name = "Ghost"
        self.skill1_description = "5体の敵に対して攻撃力の200%で攻撃し、7ターンの間、恐怖を適用する。適用確率は敵の味方の数に応じて100%、80%、60%、30%、0%であり、敵の味方が少ないほど確率は高くなる。"
        self.skill2_description = "最も近い敵に対して攻撃力の200%で4回攻撃する。8ターンの間、全味方は受けるダメージが40%減少する。"
        self.skill3_description = "通常攻撃は恐怖のある敵を優先的に狙う。ターゲットが恐怖を持っている場合、ダメージが100%増加する。自分が生存している限り、敵の恐怖効果は次の効果を得る：命中率 - 20%。"

        self.skill1_cooldown_max = 5
        self.skill2_cooldown_max = 5
        self.is_boss = False
        self.fear_effect_dict = {"acc": -0.20}

    def skill_tooltip(self):
        return f"スキル 1 : {self.skill1_description}\nクールダウン : {self.skill1_cooldown} 行動\n\nスキル 2 : {self.skill2_description}\nクールダウン : {self.skill2_cooldown} 行動\n\nスキル 3 : {self.skill3_description}\n"

    def skill1_logic(self):
        chance_dict = dict(zip_longest(range(1, 11), [100, 80, 60, 30, 0], fillvalue=0))
        def fear_effect(self, target):
            dice = random.randint(1, 100)
            if dice <= chance_dict[len(self.enemy)]:
                target.apply_effect(FearEffect('恐怖', duration=7, is_buff=False))
        damage_dealt = self.attack(target_kw1="n_random_enemy",target_kw2="5", multiplier=2.0, repeat=1, func_after_dmg=fear_effect)
        return damage_dealt

    def skill2_logic(self):
        damage_dealt = self.attack(target_kw1="enemy_in_front", multiplier=2.0, repeat=4)
        if self.is_alive():
            for a in self.ally:
                a.apply_effect(StatsEffect('霧', duration=8, is_buff=True, stats_dict={'final_damage_taken_multipler' : -0.40}))
        return damage_dealt
        
    def skill3(self):
        pass

    def normal_attack(self):
        def fear_amplify(self, target, final_damage):
            if target.has_effect_that_named("恐怖"):
                final_damage *= 2.0
            return final_damage
        self.attack(func_damage_step=fear_amplify, target_kw1="n_enemy_with_effect", target_kw2="1", target_kw3="Fear")


class Death(character.Character):
    def __init__(self, name, lvl, exp=0, equip=None, image=None):
        super().__init__(name, lvl, exp, equip, image)
        self.original_name = "Death"
        self.skill1_description = "攻撃力の360%で5体の敵を攻撃し、対象に9ターンの間、恐怖を適用する。適用確率は敵の味方の数に応じて100%、80%、60%、30%、0%となる。敵の味方が少ないほど、確率が高くなる。"
        self.skill2_description = "最もHPが低い3体の敵を攻撃力の400%で攻撃する。対象のHPが15%以下の場合、対象を即死させ、最大HPの20%に相当するHPを回復する。敵が攻撃を生き延び、恐怖状態にある場合、敵は5ターンの間混乱状態になる。"
        self.skill3_description = "通常攻撃が恐怖を9ターンの間付与するチャンスが15%あり、最大HP、防御力、攻撃力が20%増加する。自身が生存している限り、恐怖効果は次の効果を得る：攻撃力-40%、命中率-40%。"
        self.skill1_cooldown_max = 4
        self.skill2_cooldown_max = 4
        self.is_boss = True
        self.fear_effect_dict = {"acc": -0.40, "atk": 0.6}

    def skill_tooltip(self):
        return f"スキル 1 : {self.skill1_description}\nクールダウン : {self.skill1_cooldown} 行動\n\nスキル 2 : {self.skill2_description}\nクールダウン : {self.skill2_cooldown} 行動\n\nスキル 3 : {self.skill3_description}\n"

    def skill1_logic(self):
        chance_dict = dict(zip_longest(range(1, 11), [100, 80, 60, 30, 0], fillvalue=0))
        def fear_effect(self, target):
            dice = random.randint(1, 100)
            if dice <= chance_dict[len(self.enemy)]:
                target.apply_effect(FearEffect('恐怖', duration=9, is_buff=False))
        damage_dealt = self.attack(target_kw1="n_random_enemy",target_kw2="5", multiplier=3.6, repeat=1, func_after_dmg=fear_effect)
        return damage_dealt


    def skill2_logic(self):
        def execute(self, target):
            if target.hp < target.maxhp * 0.15 and not target.is_dead():
                target.take_bypass_status_effect_damage(target.hp, self)
                if self.is_alive():
                    self.heal_hp(self.maxhp * 0.2, self)
            else:
                if target.has_effect_that_named("恐怖"):
                    target.apply_effect(ConfuseEffect('混乱', duration=5, is_buff=False))
        damage_dealt = self.attack(target_kw1="n_lowest_attr",target_kw2="3",target_kw3="hp",target_kw4="enemy", multiplier=4.0, repeat=1, func_after_dmg=execute)
        return damage_dealt

        
    def skill3(self):
        pass

    def normal_attack(self):
        def fear_effect(self, target):
            dice = random.randint(1, 100)
            if dice <= 15:
                target.apply_effect(FearEffect('恐怖', duration=9, is_buff=False))
        self.attack(func_after_dmg=fear_effect)

    def battle_entry_effects(self):
        self.apply_effect(StatsEffect('パッシブ効果', -1, True, {'maxhp' : 1.2, 'atk' : 1.2, 'defense' : 1.2}, can_be_removed_by_skill=False))
        self.hp = self.maxhp


class Gargoyle(character.Character):
    def __init__(self, name, lvl, exp=0, equip=None, image=None):
        super().__init__(name, lvl, exp, equip, image)
        self.original_name = "Gargoyle"
        self.skill1_description = "最も近い敵を攻撃力の210%で3回攻撃する。"
        self.skill2_description = "最も近い敵を攻撃力の210%で3回攻撃する。"
        self.skill3_description = "被ダメージを10%軽減する。ダメージを受けると、60%の確率で攻撃者に5ターンの間出血と毒の効果を付与する。出血：ターンごとに適用者の攻撃力の80%の状態ダメージを受ける。毒：ターンごとに現在HPの5%の状態ダメージを受ける。"
        self.skill1_cooldown_max = 5
        self.skill2_cooldown_max = 5
        self.is_boss = False

    def skill_tooltip(self):
        return f"スキル 1 : {self.skill1_description}\nクールダウン : {self.skill1_cooldown} 行動\n\nスキル 2 : {self.skill2_description}\nクールダウン : {self.skill2_cooldown} 行動\n\nスキル 3 : {self.skill3_description}\n"

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
            attacker.apply_effect(PoisonDamageEffect('毒', duration=5, is_buff=False, value=0.05, imposter=self, base="hp"))
        if random.randint(1, 100) <= 60:
            attacker.apply_effect(ContinuousDamageEffect('出血', duration=5, is_buff=False, value=0.8 * self.atk, imposter=self))


class MachineGolem(character.Character):
    def __init__(self, name, lvl, exp=0, equip=None, image=None):
        super().__init__(name, lvl, exp, equip, image)
        self.original_name = "MachineGolem"
        self.skill1_description = "全ての敵に2つの時限爆弾を設置する。爆弾は8ターン後に爆発し、自身の攻撃力の400%に相当する状態ダメージを与える。"
        self.skill2_description = "全ての敵に攻撃力の275%で攻撃し、75%の確率で8ターンの間燃焼を付与する。燃焼は毎ターン自身の攻撃力の25%の状態ダメージを与える。"
        self.skill3_description = "攻撃力を20%、最大HPを20%増加させる。"
        self.skill1_cooldown_max = 5
        self.skill2_cooldown_max = 5
        self.is_boss = True

    def skill_tooltip(self):
        return f"スキル 1 : {self.skill1_description}\nクールダウン : {self.skill1_cooldown} 行動\n\nスキル 2 : {self.skill2_description}\nクールダウン : {self.skill2_cooldown} 行動\n\nスキル 3 : {self.skill3_description}\n"

    def skill1_logic(self):
        for e in self.enemy:
            e.apply_effect(TimedBombEffect('時限爆弾', duration=8, is_buff=False, damage=4.00 * self.atk, imposter=self, cc_immunity=False))
            e.apply_effect(TimedBombEffect('時限爆弾', duration=8, is_buff=False, damage=4.00 * self.atk, imposter=self, cc_immunity=False))
        return 0
    
    def skill2_logic(self):
        def burn_effect(self, target):
            dice = random.randint(1, 100)
            if dice <= 75:
                target.apply_effect(ContinuousDamageEffect('燃焼', duration=8, is_buff=False, value=0.25 * self.atk, imposter=self))
        damage_dealt = self.attack(multiplier=2.75, repeat=1, func_after_dmg=burn_effect, target_kw1="n_random_enemy", target_kw2="5")
        return damage_dealt
        
    def skill3(self):
        pass

    def battle_entry_effects(self):
        self.apply_effect(StatsEffect('パッシブ効果', -1, True, {'maxhp' : 1.2, 'atk' : 1.2}, can_be_removed_by_skill=False))
        self.hp = self.maxhp


class Dullahan(character.Character):
    def __init__(self, name, lvl, exp=0, equip=None, image=None):
        super().__init__(name, lvl, exp, equip, image)
        self.original_name = "Dullahan"
        self.skill1_description = "最も近い3体の敵に攻撃力の300%で攻撃し、対象に重傷を8ターンの間付与する。重傷：ターンごとに適用者の攻撃力の200%の状態ダメージを受けるが、治療によって除去可能。対象のHPが50%以下の場合、重傷を2つ付与する。"
        self.skill2_description = "最も近い3体の敵に攻撃力の300%で攻撃し、対象のHPが50%以下の場合、8ターンの間、その回復効率を30%減少させる。"
        self.skill3_description = "スピードを20%増加する。"
        self.skill1_cooldown_max = 5
        self.skill2_cooldown_max = 5
        self.is_boss = True

    def skill_tooltip(self):
        return f"スキル 1 : {self.skill1_description}\nクールダウン : {self.skill1_cooldown} 行動\n\nスキル 2 : {self.skill2_description}\nクールダウン : {self.skill2_cooldown} 行動\n\nスキル 3 : {self.skill3_description}\n"

    def skill1_logic(self):
        def wound(self, target):
            if target.hp < target.maxhp * 0.5:
                target.apply_effect(ContinuousDamageEffect('重傷', duration=8, is_buff=False, value=2.0 * self.atk, imposter=self, remove_by_heal=True))
                target.apply_effect(ContinuousDamageEffect('重傷', duration=8, is_buff=False, value=2.0 * self.atk, imposter=self, remove_by_heal=True))
            else:
                target.apply_effect(ContinuousDamageEffect('重傷', duration=8, is_buff=False, value=2.0 * self.atk, imposter=self, remove_by_heal=True))
        damage_dealt = self.attack(multiplier=3.0, repeat=1, func_after_dmg=wound, target_kw1="n_enemy_in_front", target_kw2="3")
        return damage_dealt
    
    def skill2_logic(self):
        def wound(self, target):
            if target.hp < target.maxhp * 0.5:
                target.apply_effect(StatsEffect('治癒効率減少', duration=8, is_buff=False, stats_dict={'heal_efficiency' : -0.3}))
        damage_dealt = self.attack(multiplier=3.0, repeat=1, func_after_dmg=wound, target_kw1="n_enemy_in_front", target_kw2="3")
        return damage_dealt

    def skill3(self):
        pass

    def battle_entry_effects(self):
        self.apply_effect(StatsEffect('パッシブ効果', -1, True, {'spd' : 1.2}, can_be_removed_by_skill=False))


class Salamander(character.Character):
    def __init__(self, name, lvl, exp=0, equip=None, image=None):
        super().__init__(name, lvl, exp, equip, image)
        self.original_name = "Salamander"
        self.skill1_description = "攻撃力の170%で敵に8回攻撃する。各攻撃には66%の確率で6ターンの間、燃焼を付与する。燃焼はターンごとに自身の攻撃力の33%に相当する状態ダメージを与える。"
        self.skill2_description = "全ての敵に攻撃力の170%で攻撃し、各攻撃には75%の確率で6ターンの間、燃焼を付与する。"
        self.skill3_description = "毎ターン、最大HPの3%に相当するHPを回復する。"
        self.skill1_cooldown_max = 5
        self.skill2_cooldown_max = 5
        self.is_boss = False

    def skill_tooltip(self):
        return f"スキル 1 : {self.skill1_description}\nクールダウン : {self.skill1_cooldown} 行動\n\nスキル 2 : {self.skill2_description}\nクールダウン : {self.skill2_cooldown} 行動\n\nスキル 3 : {self.skill3_description}\n"

    def skill1_logic(self):
        def burn_effect(self, target):
            dice = random.randint(1, 100)
            if dice <= 66:
                target.apply_effect(ContinuousDamageEffect('燃焼', duration=6, is_buff=False, value=0.33 * self.atk, imposter=self))
        damage_dealt = self.attack(multiplier=1.7, repeat=8, func_after_dmg=burn_effect)
        return damage_dealt

    def skill2_logic(self):
        def burn_effect(self, target):
            dice = random.randint(1, 100)
            if dice <= 75:
                target.apply_effect(ContinuousDamageEffect('燃焼', duration=6, is_buff=False, value=0.33 * self.atk, imposter=self))
        damage_dealt = self.attack(multiplier=1.7, repeat=1, func_after_dmg=burn_effect, target_kw1="n_random_enemy", target_kw2="5")
        return damage_dealt

    def skill3(self):
        pass

    def battle_entry_effects(self):
        e = ContinuousHealEffect('パッシブ効果', -1, True, 0.03, True)
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
        self.skill1_description = "最も近い敵に攻撃力の150%で12回攻撃する。"
        self.skill2_description = "4ターンの間、回避率を50%増加させる。最も近い敵に攻撃力の150%で8回攻撃する。"
        self.skill3_description = "通常攻撃は30%の確率で全スキルのクールダウンを1ターン短縮する。"
        self.skill1_cooldown_max = 4
        self.skill2_cooldown_max = 4
        self.is_boss = False

    def skill_tooltip(self):
        return f"スキル 1 : {self.skill1_description}\nクールダウン : {self.skill1_cooldown} 行動\n\nスキル 2 : {self.skill2_description}\nクールダウン : {self.skill2_cooldown} 行動\n\nスキル 3 : {self.skill3_description}\n"

    def skill1_logic(self):
        damage_dealt = self.attack(multiplier=1.5, repeat=12, target_kw1="enemy_in_front")
        return damage_dealt

    def skill2_logic(self):
        self.apply_effect(StatsEffect('回避率増加', 4, True, {'eva' : 0.5}))
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
        self.skill1_description = "最も近い敵に攻撃力の250%で4回攻撃する。"
        self.skill2_description = "敵5体に攻撃力の200%で攻撃する。"
        self.skill3_description = "スキル攻撃はターゲットに6ターンの間、スティングを付与する。スティング：ターゲットがダメージを受けるたびに、付与者の攻撃力の35%に相当する状態ダメージを受ける。状態ダメージによる発動はしない。"
        self.skill1_cooldown_max = 4
        self.skill2_cooldown_max = 4
        self.is_boss = False

    def skill_tooltip(self):
        return f"スキル 1 : {self.skill1_description}\nクールダウン : {self.skill1_cooldown} 行動\n\nスキル 2 : {self.skill2_description}\nクールダウン : {self.skill2_cooldown} 行動\n\nスキル 3 : {self.skill3_description}\n"

    def skill1_logic(self):
        def sting_effect(self, target):
            target.apply_effect(StingEffect('スティング', duration=6, is_buff=False, value=0.35 * self.atk, imposter=self))
        damage_dealt = self.attack(multiplier=3.0, repeat=4, func_after_dmg=sting_effect, target_kw1="enemy_in_front")
        return damage_dealt

    def skill2_logic(self):
        def sting_effect(self, target):
            target.apply_effect(StingEffect('スティング', duration=6, is_buff=False, value=0.35 * self.atk, imposter=self))
        damage_dealt = self.attack(target_kw1="n_random_enemy",target_kw2="5", multiplier=2.0, repeat=1, func_after_dmg=sting_effect)
        return damage_dealt
        
    def skill3(self):
        pass 


class Samurai(character.Character):
    def __init__(self, name, lvl, exp=0, equip=None, image=None):
        super().__init__(name, lvl, exp, equip, image)
        self.original_name = "Samurai"
        self.skill1_description = "攻撃力の200%で一番近い敵に7回攻撃する。"
        self.skill2_description = "攻撃力の300%で最もHPが低い敵に3回攻撃する。"
        self.skill3_description = "スキル攻撃は30%の確率で対象に6ターンの間出血を付与する。出血はターンごとに攻撃力の30%のダメージを与える。"
        self.skill1_cooldown_max = 5
        self.skill2_cooldown_max = 5
        self.is_boss = False

    def skill_tooltip(self):
        return f"スキル 1 : {self.skill1_description}\nクールダウン : {self.skill1_cooldown} 行動\n\nスキル 2 : {self.skill2_description}\nクールダウン : {self.skill2_cooldown} 行動\n\nスキル 3 : {self.skill3_description}\n"

    def skill1_logic(self):
        def bleed_effect(self, target):
            dice = random.randint(1, 100)
            if dice <= 30:
                target.apply_effect(ContinuousDamageEffect('出血', duration=6, is_buff=False, value=0.3 * self.atk, imposter=self))
        damage_dealt = self.attack(multiplier=2.0, repeat=7, func_after_dmg=bleed_effect, target_kw1="enemy_in_front")
        return damage_dealt

    def skill2_logic(self):
        def bleed_effect(self, target):
            dice = random.randint(1, 100)
            if dice <= 30:
                target.apply_effect(ContinuousDamageEffect('出血', duration=6, is_buff=False, value=0.3 * self.atk, imposter=self))
        damage_dealt = damage_dealt = self.attack(target_kw1="n_lowest_attr",target_kw2="1",target_kw3="hp",target_kw4="enemy", multiplier=3.0, repeat=3, func_after_dmg=bleed_effect)
        return damage_dealt
        
    def skill3(self):
        pass


class BlackKnight(character.Character):
    def __init__(self, name, lvl, exp=0, equip=None, image=None):
        super().__init__(name, lvl, exp, equip, image)
        self.original_name = "BlackKnight"
        self.skill1_description = "攻撃力の250%でランダムな敵に12回攻撃する。全ての攻撃終了後、HPが40%以下の場合、自身と隣接する味方の攻撃力とクリティカル率を40%増加させる。効果は6ターン続く。"
        self.skill2_description = "4ターンの間、攻撃力を30%増加する。最も近い敵に対して攻撃力の220%で6回攻撃する。"
        self.skill3_description = "HPが40%以下の場合、攻撃力が40%増加する。"
        self.skill1_cooldown_max = 4
        self.skill2_cooldown_max = 4
        self.is_boss = True

    def skill_tooltip(self):
        return f"スキル 1 : {self.skill1_description}\nクールダウン : {self.skill1_cooldown} 行動\n\nスキル 2 : {self.skill2_description}\nクールダウン : {self.skill2_cooldown} 行動\n\nスキル 3 : {self.skill3_description}\n"

    def skill1_logic(self):
        damage_dealt = self.attack(multiplier=2.5, repeat=12)
        if self.is_alive() and self.hp < self.maxhp * 0.4:
            self.apply_effect(StatsEffect('攻撃力増加', 6, True, {'atk' : 1.4, 'crit' : 0.4}))
            for n in self.get_neighbor_allies_not_including_self():
                n.apply_effect(StatsEffect('攻撃力増加', 6, True, {'atk' : 1.4, 'crit' : 0.4}))
        return damage_dealt

    def skill2_logic(self):
        self.apply_effect(StatsEffect('攻撃力増加', 4, True, {'atk' : 1.3}))
        damage_dealt = self.attack(multiplier=2.2, repeat=6, target_kw1="enemy_in_front")
        return damage_dealt

    def skill3(self):
        pass

    def battle_entry_effects(self):
        self.apply_effect(StatsEffect('パッシブ効果', -1, True, {'atk' : 1.4}, 
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
        self.skill1_description = "全ての敵に攻撃力の300%で攻撃する。"
        self.skill2_description = "全ての敵に50%の確率で睡眠を付与する。"
        self.skill3_description = "10ターンの間、回避率を50%増加する。"
        self.skill1_cooldown_max = 5
        self.skill2_cooldown_max = 5
        self.is_boss = False

    def skill_tooltip(self):
        return f"スキル 1 : {self.skill1_description}\nクールダウン : {self.skill1_cooldown} 行動\n\nスキル 2 : {self.skill2_description}\nクールダウン : {self.skill2_cooldown} 行動\n\nスキル 3 : {self.skill3_description}\n"

    def skill1_logic(self):
        damage_dealt = self.attack(multiplier=3.0, target_kw1="n_random_enemy",target_kw2="5", repeat=1)
        return damage_dealt

    def skill2_logic(self):
        for t in self.enemy:
            dice = random.randint(1, 100)
            if dice <= 50:
                t.apply_effect(SleepEffect('睡眠', duration=-1, is_buff=False))
        pass
        
    def skill3(self):
        pass

    def battle_entry_effects(self):
        self.apply_effect(StatsEffect('煙', 10, True, {'eva' : 0.5}))


# Stun machine
class MultiLegTank(character.Character):
    def __init__(self, name, lvl, exp=0, equip=None, image=None):
        super().__init__(name, lvl, exp, equip, image)
        self.original_name = "MultiLegTank"
        # self.skill1_description = "Attack all enemies with 130% atk and 80% chance to Stun for 4 turns."
        # self.skill2_description = "Attack 3 closest enemies with 190% atk and 80% chance to Stun for 4 turns."
        # self.skill3_description = "Normal attack target closest enemy with 270% atk and 80% chance to Stun for 4 turns."
        self.skill1_description = "全ての敵に攻撃力の130%で攻撃し、80%の確率で4ターンの間、スタンを付与する。"
        self.skill2_description = "最も近い敵3体に攻撃力の190%で攻撃し、80%の確率で4ターンの間、スタンを付与する。"
        self.skill3_description = "通常攻撃は最も近い敵にターゲットし、攻撃力の270%で攻撃し、80%の確率で4ターンの間、スタンを付与する。"
        self.skill1_cooldown_max = 5
        self.skill2_cooldown_max = 5
        self.is_boss = False

    def skill_tooltip(self):
        return f"スキル 1 : {self.skill1_description}\nクールダウン : {self.skill1_cooldown} 行動\n\nスキル 2 : {self.skill2_description}\nクールダウン : {self.skill2_cooldown} 行動\n\nスキル 3 : {self.skill3_description}\n"

    def skill1_logic(self):
        def stun_effect(self, target):
            dice = random.randint(1, 100)
            if dice <= 80:
                target.apply_effect(StunEffect('スタン', duration=4, is_buff=False))
        damage_dealt = self.attack(multiplier=1.3, repeat=1, func_after_dmg=stun_effect, target_kw1="n_random_enemy",target_kw2="5")
        return damage_dealt

    def skill2_logic(self):
        def stun_effect(self, target):
            dice = random.randint(1, 100)
            if dice <= 80:
                target.apply_effect(StunEffect('スタン', duration=4, is_buff=False))
        damage_dealt = self.attack(multiplier=1.9, repeat=1, func_after_dmg=stun_effect, target_kw1="n_enemy_in_front",target_kw2="3")
        return damage_dealt
        
    def skill3(self):
        pass

    def normal_attack(self):
        def stun_effect(self, target):
            dice = random.randint(1, 100)
            if dice <= 80:
                target.apply_effect(StunEffect('スタン', duration=4, is_buff=False))
        self.attack(multiplier=2.7, func_after_dmg=stun_effect, target_kw1="enemy_in_front")


class Assassin(character.Character):
    def __init__(self, name, lvl, exp=0, equip=None, image=None):
        super().__init__(name, lvl, exp, equip, image)
        self.original_name = "Assassin"
        self.skill1_description = "7ターンの間、攻撃力と速度を15%増加させ、攻撃力の200%に相当するHPを回復する。"
        self.skill2_description = "最も近い敵に攻撃力の321%で8回攻撃し、対象が自分より速度が低い場合、6ターンの間混乱状態にする。対象が混乱状態の場合、ダメージが100%増加する。"
        self.skill3_description = "通常攻撃で最も近い敵を対象に2回攻撃し、40%の確率で6ターンの間出血を付与する。出血はターンごとに攻撃力の40%のダメージを与える。"
        self.skill1_cooldown_max = 5
        self.skill2_cooldown_max = 3
        self.is_boss = True

    def skill_tooltip(self):
        return f"スキル 1 : {self.skill1_description}\nクールダウン : {self.skill1_cooldown} 行動\n\nスキル 2 : {self.skill2_description}\nクールダウン : {self.skill2_cooldown} 行動\n\nスキル 3 : {self.skill3_description}\n"

    def skill1_logic(self):
        self.apply_effect(StatsEffect('速い', 7, True, {'atk' : 1.15, 'spd' : 1.15}))
        self.heal_hp(2.0 * self.atk, self)

    def skill2_logic(self):
        def confuse_effect(self, target):
            if target.spd < self.spd:
                target.apply_effect(ConfuseEffect('混乱', duration=6, is_buff=False))
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
                target.apply_effect(ContinuousDamageEffect('出血', duration=6, is_buff=False, value=0.4 * self.atk, imposter=self))
        self.attack(target_kw1="enemy_in_front", func_after_dmg=bleed_effect, repeat=2)


class Shenlong(character.Character):
    def __init__(self, name, lvl, exp=0, equip=None, image=None):
        super().__init__(name, lvl, exp, equip, image)
        self.original_name = "Shenlong"
        self.skill1_description = "全ての敵を4ターンの間、スタン状態にする。全ての敵に対して220%/240%/260%の攻撃力で3回攻撃する。"
        self.skill2_description = "全ての味方の攻撃力と命中率を6ターンの間、30%増加させる。" \
        "最も近い敵に対して、同じ効果が既に適用されていない場合、12ターンの間「龍の試練」を適用する。" \
        "「龍の試練」: 攻撃力とクリティカル率が30%増加する。この効果が終了すると、対象は状態ダメージを1受け、12ターンの間スタンする。" \
        "「龍の試練」はスキルによって解除されない。"
        self.skill3_description = "HPを222%増加させる。"
        self.skill1_cooldown_max = 5
        self.skill2_cooldown_max = 5
        self.is_boss = True

    def skill_tooltip(self):
        return f"スキル 1 : {self.skill1_description}\nクールダウン : {self.skill1_cooldown} 行動\n\nスキル 2 : {self.skill2_description}\nクールダウン : {self.skill2_cooldown} 行動\n\nスキル 3 : {self.skill3_description}\n"

    def skill1_logic(self):
        for e in self.enemy:
            e.apply_effect(StunEffect('スタン', duration=4, is_buff=False))
        damage_dealt = self.attack(multiplier=2.2, repeat=1, target_kw1="n_random_enemy",target_kw2="5")
        damage_dealt += self.attack(multiplier=2.4, repeat=1, target_kw1="n_random_enemy",target_kw2="5")
        damage_dealt += self.attack(multiplier=2.6, repeat=1, target_kw1="n_random_enemy",target_kw2="5")
        return damage_dealt


    def skill2_logic(self):
        for a in self.ally:
            a.apply_effect(StatsEffect('攻撃命中増加', 6, True, {'atk' : 1.3, 'acc' : 1.3}))
        target = next(self.target_selection("enemy_in_front"))
        if not target.has_effect_that_named("龍の試練"):
            target.apply_effect(TrialofDragonEffect('龍の試練', duration=12, is_buff=False, stats_dict={'atk' : 1.3, 'crit' : 0.3},
                                                    damage=1, imposter=self, stun_duration=12))

    def skill3(self):
        pass

    def battle_entry_effects(self):
        self.apply_effect(StatsEffect('パッシブ効果', -1, True, {'maxhp' : 3.22}, can_be_removed_by_skill=False))
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
        self.skill1_description = "最大HPが最も高い敵に攻撃力の300%で3回攻撃する。"
        self.skill2_description = "最大HPが最も高い敵に攻撃力の900%で攻撃し、80%の確率で3ターンの間、スタン状態にする。"
        self.skill3_description = "通常攻撃は、スタンを引き起こす確率が5%で、そのスタンは2ターン持続する。"
        self.skill1_cooldown_max = 5
        self.skill2_cooldown_max = 4
        self.is_boss = False

    def skill_tooltip(self):
        return f"スキル 1 : {self.skill1_description}\nクールダウン : {self.skill1_cooldown} 行動\n\nスキル 2 : {self.skill2_description}\nクールダウン : {self.skill2_cooldown} 行動\n\nスキル 3 : {self.skill3_description}\n"

    def skill1_logic(self):
        damage_dealt = self.attack(multiplier=3.0, repeat=3, target_kw1="n_highest_attr", target_kw2="1", target_kw3="hp", target_kw4="enemy")
        return damage_dealt

    def skill2_logic(self):
        def stun_effect(self, target):
            dice = random.randint(1, 100)
            if dice <= 80:
                target.apply_effect(StunEffect('スタン', duration=3, is_buff=False))
        damage_dealt = self.attack(multiplier=9.0, repeat=1, func_after_dmg=stun_effect, target_kw1="n_highest_attr", target_kw2="1", target_kw3="hp", target_kw4="enemy")
        return damage_dealt
        
    def skill3(self):
        pass

    def normal_attack(self):
        def stun_effect(self, target):
            dice = random.randint(1, 100)
            if dice <= 5:
                target.apply_effect(StunEffect('スタン', duration=2, is_buff=False))
        self.attack(func_after_dmg=stun_effect)


class Ork(character.Character):
    def __init__(self, name, lvl, exp=0, equip=None, image=None):
        super().__init__(name, lvl, exp, equip, image)
        self.original_name = "Ork"
        self.skill1_description = "最もHPが低い敵に集中攻撃し攻撃力の300%のダメージを2回与える。"
        self.skill2_description = "最もHPが低い敵に集中攻撃し攻撃力の300%のダメージを2回与える。"
        self.skill3_description = "スキル攻撃は燃焼と出血を同時に引き起こし、5ターンの間、攻撃力の30%に相当する状態ダメージを毎ターン与える。"
        self.skill1_cooldown_max = 5
        self.skill2_cooldown_max = 5
        self.is_boss = False

    def skill_tooltip(self):
        return f"スキル 1 : {self.skill1_description}\nクールダウン : {self.skill1_cooldown} 行動\n\nスキル 2 : {self.skill2_description}\nクールダウン : {self.skill2_cooldown} 行動\n\nスキル 3 : {self.skill3_description}\n"

    def skill1_logic(self):
        def burn_effect(self, target):
            target.apply_effect(ContinuousDamageEffect('燃焼', duration=5, is_buff=False, value=0.3 * self.atk, imposter=self))
            target.apply_effect(ContinuousDamageEffect('出血', duration=5, is_buff=False, value=0.3 * self.atk, imposter=self))
        damage_dealt = self.attack(multiplier=3.0, repeat_seq=2, func_after_dmg=burn_effect, target_kw1="n_lowest_attr", target_kw2="1", target_kw3="hp", target_kw4="enemy")
        return damage_dealt

    def skill2_logic(self):
        def burn_effect(self, target):
            target.apply_effect(ContinuousDamageEffect('燃焼', duration=5, is_buff=False, value=0.3 * self.atk, imposter=self))
            target.apply_effect(ContinuousDamageEffect('出血', duration=5, is_buff=False, value=0.3 * self.atk, imposter=self))
        damage_dealt = self.attack(multiplier=3.0, repeat_seq=2, func_after_dmg=burn_effect, target_kw1="n_lowest_attr", target_kw2="1", target_kw3="hp", target_kw4="enemy")
        return damage_dealt
    
    def skill3(self):
        pass


class Minotaur(character.Character):
    def __init__(self, name, lvl, exp=0, equip=None, image=None):
        super().__init__(name, lvl, exp, equip, image)
        self.original_name = "Minotaur"
        self.skill1_description = "最もHPが低い敵に攻撃力の300%で2回集中攻撃する。"
        self.skill2_description = "最もHPが低い敵に攻撃力の200%で2回集中攻撃する。ダメージは対象の失われたHPの10%分増加する。"
        self.skill3_description = "対象のHPが50%未満の場合、スキルダメージが50%増加する。"
        self.skill1_cooldown_max = 4
        self.skill2_cooldown_max = 5
        self.is_boss = False

    def skill_tooltip(self):
        return f"スキル 1 : {self.skill1_description}\nクールダウン : {self.skill1_cooldown} 行動\n\nスキル 2 : {self.skill2_description}\nクールダウン : {self.skill2_cooldown} 行動\n\nスキル 3 : {self.skill3_description}\n"

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
        self.skill1_description = "最もHPが低い敵に対して攻撃力の340%で2回攻撃し、5ターンの間出血効果を付与する。出血効果はターンごとに攻撃力の50%の状態ダメージを与える。"
        self.skill2_description = "全ての敵に攻撃力の220%で攻撃し、HPが50%未満の全ての敵に5ターンの間燃焼を付与する。" \
        "対象のHPが25%未満の場合、追加で10ターンの燃焼を付与する。" \
        "燃焼はターンごとに攻撃力の100%の状態ダメージを与える。この攻撃は必ず命中する。"
        self.skill3_description = "HPを200%増加させる。"
        self.skill1_cooldown_max = 4
        self.skill2_cooldown_max = 4
        self.is_boss = True

    def skill_tooltip(self):
        return f"スキル 1 : {self.skill1_description}\nクールダウン : {self.skill1_cooldown} 行動\n\nスキル 2 : {self.skill2_description}\nクールダウン : {self.skill2_cooldown} 行動\n\nスキル 3 : {self.skill3_description}\n"

    def skill1_logic(self):
        def bleed_effect(self, target):
            target.apply_effect(ContinuousDamageEffect('出血', duration=5, is_buff=False, value=0.5 * self.atk, imposter=self))
        damage_dealt = self.attack(multiplier=3.4, repeat_seq=2, func_after_dmg=bleed_effect, target_kw1="n_lowest_attr", target_kw2="1", target_kw3="hp", target_kw4="enemy")
        return damage_dealt

    def skill2_logic(self):
        def burn_effect(self, target):
            if target.hp < target.maxhp * 0.5:
                target.apply_effect(ContinuousDamageEffect('燃焼', duration=5, is_buff=False, value=1.0 * self.atk, imposter=self))
            if target.hp < target.maxhp * 0.25:
                target.apply_effect(ContinuousDamageEffect('燃焼', duration=10, is_buff=False, value=1.0 * self.atk, imposter=self))
        damage_dealt = self.attack(multiplier=2.2, repeat=1, func_after_dmg=burn_effect, target_kw1="n_random_enemy", target_kw2="5", always_hit=True)
        return damage_dealt

    def skill3(self):
        pass

    def battle_entry_effects(self):
        self.apply_effect(StatsEffect('パッシブ効果', -1, True, {'maxhp' : 3.0}, can_be_removed_by_skill=False))
        self.hp = self.maxhp


class BakeNeko(character.Character):
    def __init__(self, name, lvl, exp=0, equip=None, image=None):
        super().__init__(name, lvl, exp, equip, image)
        self.original_name = "BakeNeko"
        self.skill1_description = "8ターンの間、全ての味方の最大HPを30%増加させ、攻撃力の300%でHPを回復される。"
        self.skill2_description = "最もHPが低い味方1人を攻撃力の200%で回復する。全ての味方に6ターンの間、抑制を適用する。抑制：ダメージ計算時、自分のHPが対象のHPより多い場合、HPの比率に応じてダメージが増加する。最大ボーナスダメージ：1000%。"
        self.skill3_description = "最大HPと防御力を30%、回避率を15%増加する。"
        self.skill1_cooldown_max = 5
        self.skill2_cooldown_max = 5
        self.is_boss = False

    def skill_tooltip(self):
        return f"スキル 1 : {self.skill1_description}\nクールダウン : {self.skill1_cooldown} 行動\n\nスキル 2 : {self.skill2_description}\nクールダウン : {self.skill2_cooldown} 行動\n\nスキル 3 : {self.skill3_description}\n"

    def skill1_logic(self):
        for a in self.ally:
            a.apply_effect(StatsEffect('最大HP増加', 8, True, {'maxhp' : 1.3}))
        self.heal("n_random_ally", "5", value=3.0 * self.atk)

    def skill2_logic(self):
        self.heal("n_lowest_attr", "1", "hp", "ally", value=2.0 * self.atk)
        for a in self.ally:
            a.apply_effect(BakeNekoSupressionEffect('抑制', 6, True))
    
    def skill3(self):
        pass

    def battle_entry_effects(self):
        self.apply_effect(StatsEffect('パッシブ効果', -1, True, {'maxhp' : 1.3, 'defense' : 1.3, 'eva' : 0.15}, can_be_removed_by_skill=False))
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
        self.skill1_description = "最も速度が低い敵1体を対象に、攻撃力の250%で3回攻撃する。"
        self.skill2_description = "最も速度が低い敵1体を対象に、それがスキル1で対象とした同じ敵である場合、攻撃力の250%で3回攻撃し、対象を4ターンの間、スタン状態にする。それ以外の場合、このスキルは効果がない。"
        self.skill3_description = "通常攻撃が2回攻撃する。"
        self.skill1_cooldown_max = 5
        self.skill2_cooldown_max = 5
        self.is_boss = False
        self.s1target = None

    def skill_tooltip(self):
        return f"スキル 1 : {self.skill1_description}\nクールダウン : {self.skill1_cooldown} 行動\n\nスキル 2 : {self.skill2_description}\nクールダウン : {self.skill2_cooldown} 行動\n\nスキル 3 : {self.skill3_description}\n"

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
                    target.apply_effect(StunEffect('スタン', duration=4, is_buff=False))
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
        self.skill1_description = "最も近い3体の敵を2回攻撃し、攻撃力の265%のダメージを与える。各攻撃に70%の確率で、対象の速度を6ターンの間30%減少させる。"
        self.skill2_description = "最も近い敵に攻撃力の200%で攻撃し、対象の速度が自分より低い場合、さらに120%のダメージを追加で与え、対象の速度を6ターンの間30%減少させる。"
        self.skill3_description = "速度を20%増加する。隣の味方は15ターンの間、速度が20%増加する。"
        self.skill1_cooldown_max = 4
        self.skill2_cooldown_max = 5
        self.is_boss = False

    def skill_tooltip(self):
        return f"スキル 1 : {self.skill1_description}\nクールダウン : {self.skill1_cooldown} 行動\n\nスキル 2 : {self.skill2_description}\nクールダウン : {self.skill2_cooldown} 行動\n\nスキル 3 : {self.skill3_description}\n"

    def skill1_logic(self):
        def slow_effect(self, target):
            dice = random.randint(1, 100)
            if dice <= 70:
                target.apply_effect(StatsEffect('スロー', duration=6, is_buff=False, stats_dict={'spd' : 0.7}))
        damage_dealt = self.attack(multiplier=2.65, repeat_seq=2, func_after_dmg=slow_effect, target_kw1="n_enemy_in_front", target_kw2="3")
        return damage_dealt

    def skill2_logic(self):
        def slow_effect(self, target):
            if target.spd < self.spd:
                target.apply_effect(StatsEffect('スロー', duration=6, is_buff=False, stats_dict={'spd' : 0.7}))
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
            neighbor.apply_effect(StatsEffect('速度増加', 15, True, {'spd' : 1.2}))


class Agent(character.Character):
    def __init__(self, name, lvl, exp=0, equip=None, image=None):
        super().__init__(name, lvl, exp, equip, image)
        self.original_name = "Agent"
        self.skill1_description = "最も速度が低い敵1体に対して、攻撃力の330%で3回攻撃する。各攻撃は出血効果を6ターンの間付与する。出血効果はターンごとに攻撃力の80%の状態ダメージを与える。"
        self.skill2_description = "5ターンの間、回避率と命中率を50%増加させる。"
        self.skill3_description = "最も速度が低い敵を通常攻撃し、ダメージを100%増加させる。"
        self.skill1_cooldown_max = 4
        self.skill2_cooldown_max = 5
        self.is_boss = False

    def skill_tooltip(self):
        return f"スキル 1 : {self.skill1_description}\nクールダウン : {self.skill1_cooldown} 行動\n\nスキル 2 : {self.skill2_description}\nクールダウン : {self.skill2_cooldown} 行動\n\nスキル 3 : {self.skill3_description}\n"

    def skill1_logic(self):
        def bleed_effect(self, target):
            target.apply_effect(ContinuousDamageEffect('出血', duration=6, is_buff=False, value=0.8 * self.atk, imposter=self))
        damage_dealt = self.attack(multiplier=3.3, repeat=3, func_after_dmg=bleed_effect, target_kw1="n_lowest_attr", target_kw2="1", target_kw3="spd", target_kw4="enemy")
        return damage_dealt

    def skill2_logic(self):
        self.apply_effect(StatsEffect('準備完了', 5, True, {'eva' : 0.5, 'acc' : 0.5}))
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
        self.skill1_description = "攻撃力の300%でランダムな敵を4回攻撃する。"
        self.skill2_description = "攻撃力の270%でランダムな敵を4回攻撃し、各攻撃がクリティカルだった場合、同じ攻撃を追加攻撃として発動する。"
        self.skill3_description = "クリティカル率とクリティカルダメージを30%増加する。"
        self.skill1_cooldown_max = 5
        self.skill2_cooldown_max = 5
        self.is_boss = False

    def skill_tooltip(self):
        return f"スキル 1 : {self.skill1_description}\nクールダウン : {self.skill1_cooldown} 行動\n\nスキル 2 : {self.skill2_description}\nクールダウン : {self.skill2_cooldown} 行動\n\nスキル 3 : {self.skill3_description}\n"

    def skill1_logic(self):
        damage_dealt = self.attack(multiplier=3.0, repeat=4)
        return damage_dealt

    def skill2_logic(self):
        def additional_attack(self, target, is_crit):
            if is_crit:
                global_vars.turn_info_string += f"{self.name}が追加攻撃を誘発しました。\n"
                return self.attack(multiplier=2.7, repeat=1)
            else:
                return 0
        damage_dealt = self.attack(multiplier=2.7, repeat=3, additional_attack_after_dmg=additional_attack)
        return damage_dealt
        
    def skill3(self):
        pass

    def battle_entry_effects(self):
        self.apply_effect(StatsEffect('パッシブ効果', -1, True, {'crit' : 0.3, 'critdmg' : 0.3}, can_be_removed_by_skill=False))


class Queen(character.Character):
    # Boss
    def __init__(self, name, lvl, exp=0, equip=None, image=None):
        super().__init__(name, lvl, exp, equip, image)
        self.original_name = "Queen"
        self.skill1_description = "ランダムな敵に攻撃力の260%で8回攻撃し、成功した攻撃の後にクリティカルダメージを3ターンの間20%増加する。"
        self.skill2_description = "最も近い3体の敵に攻撃力の300%で攻撃し、クリティカル防御を8ターンの間30%低下させる。このスキルの後、クリティカルダメージを6ターンの間20%増加させる。"
        self.skill3_description = "クリティカル確率が60%増加し、スピードが20%増加する。"
        self.skill1_cooldown_max = 5
        self.skill2_cooldown_max = 3
        self.is_boss = True

    def skill_tooltip(self):
        return f"スキル 1 : {self.skill1_description}\nクールダウン : {self.skill1_cooldown} 行動\n\nスキル 2 : {self.skill2_description}\nクールダウン : {self.skill2_cooldown} 行動\n\nスキル 3 : {self.skill3_description}\n"

    def skill1_logic(self):
        def critdmg_increase(self, target):
            self.apply_effect(StatsEffect('支配', 3, True, {'critdmg' : 0.20}))
        damage_dealt = self.attack(multiplier=2.6, repeat=8, func_after_dmg=critdmg_increase)
        return damage_dealt

    def skill2_logic(self):
        def critdef_decrease(self, target):
            target.apply_effect(StatsEffect('順守', 8, True, {'critdef' : -0.3}))
        damage_dealt = self.attack(multiplier=3.0, repeat=1, func_after_dmg=critdef_decrease, target_kw1="n_enemy_in_front", target_kw2="3")
        if self.is_alive():
            self.apply_effect(StatsEffect('支配', 6, True, {'critdmg' : 0.20}))
        return damage_dealt

    def skill3(self):
        pass

    def battle_entry_effects(self):
        self.apply_effect(StatsEffect('Queen Passive', -1, True, {'crit' : 0.6, 'spd' : 1.2}, can_be_removed_by_skill=False))


class KungFuA(character.Character):
    def __init__(self, name, lvl, exp=0, equip=None, image=None):
        super().__init__(name, lvl, exp, equip, image)
        self.original_name = "KungFuA"
        self.skill1_description = "最もクリティカル防御の低い敵に対して、攻撃力の280%で4回集中攻撃をする。各攻撃は自身のクリティカル率とクリティカルダメージを20%増加させ、ターゲットのクリティカル防御を6ターンの間に10%減少させる。"
        self.skill2_description = "2ターンの間、クリティカルダメージを100%増加させ、最もクリティカル防御の低い敵に対して、攻撃力の440%で2回集中攻撃する。"
        self.skill3_description = "命中率とクリティカル率を40%増加する、全味方の命中率を20%増加させる。"
        self.skill1_cooldown_max = 4
        self.skill2_cooldown_max = 4
        self.is_boss = True

    def skill_tooltip(self):
        return f"スキル 1 : {self.skill1_description}\nクールダウン : {self.skill1_cooldown} 行動\n\nスキル 2 : {self.skill2_description}\nクールダウン : {self.skill2_cooldown} 行動\n\nスキル 3 : {self.skill3_description}\n"

    def skill1_logic(self):
        def critdmg_increase(self, target):
            self.apply_effect(StatsEffect('クリ率とクリダメ増加', 6, True, {'critdmg' : 0.2, 'crit' : 0.2}))
            target.apply_effect(StatsEffect('クリ防御低下', 6, True, {'critdef' : -0.1}))
        damage_dealt = self.attack(multiplier=2.6, repeat_seq=4, func_after_dmg=critdmg_increase, 
                                   target_kw1="n_lowest_attr", target_kw2="1", target_kw3="critdef", target_kw4="enemy")
        return damage_dealt

    def skill2_logic(self):
        self.apply_effect(StatsEffect('クリダメ増加', 2, True, {'critdmg' : 1.0}))
        damage_dealt = self.attack(multiplier=4.4, repeat_seq=2, target_kw1="n_lowest_attr", target_kw2="1", target_kw3="critdef", target_kw4="enemy")
        return damage_dealt
        
    def skill3(self):
        pass

    def battle_entry_effects(self):
        self.apply_effect(StatsEffect('パッシブ効果', -1, True, {'acc' : 0.4, 'crit' : 0.4}, can_be_removed_by_skill=False))
        for a in self.ally:
            a.apply_effect(StatsEffect('パッシブ効果', -1, True, {'acc' : 0.2}, can_be_removed_by_skill=False))


# ====================================
# End of Crit
# ====================================
# Defence
# ====================================
        

class Paladin(character.Character):
    def __init__(self, name, lvl, exp=0, equip=None, image=None):
        super().__init__(name, lvl, exp, equip, image)
        self.original_name = "paladin"
        self.skill1_description = "最も近い敵1体に攻撃力の800%のダメージを与える。"
        self.skill2_description = "最も近い敵1体に攻撃力の300%のダメージを3回与える。"
        self.skill3_description = "ダメージを受け、そのダメージが最大HPの10%を超えた場合、受けるダメージを50%軽減する。攻撃者は軽減されたダメージの30%を受ける。"
        self.skill1_cooldown_max = 5
        self.skill2_cooldown_max = 5
        self.is_boss = False

    def skill_tooltip(self):
        return f"スキル 1 : {self.skill1_description}\nクールダウン : {self.skill1_cooldown} 行動\n\nスキル 2 : {self.skill2_description}\nクールダウン : {self.skill2_cooldown} 行動\n\nスキル 3 : {self.skill3_description}\n"

    def skill1_logic(self):
        damage_dealt = self.attack(multiplier=8.0, repeat=1, target_kw1="enemy_in_front")
        return damage_dealt

    def skill2_logic(self):
        damage_dealt = self.attack(multiplier=3.0, repeat=3, target_kw1="enemy_in_front")
        return damage_dealt
        
    def skill3(self):
        pass

    def battle_entry_effects(self):
        shield = EffectShield3('堅守', -1, True, 0.5, 0.3)
        shield.can_be_removed_by_skill = False
        self.apply_effect(shield)
         

class Father(character.Character):
    def __init__(self, name, lvl, exp=0, equip=None, image=None):
        super().__init__(name, lvl, exp, equip, image)
        self.original_name = "Father"
        self.skill1_description = "最もHPが低い3人の味方にキャンセルシールドを適用する。最大HPの10%未満のダメージは0にする。シールドは4ターン持続し、4回使用できる。"
        self.skill2_description = "最も近い3人の敵に攻撃力の450%のダメージを与える。"
        self.skill3_description = "受けるダメージを20%軽減し、最大HPの10%未満のダメージは300回まで0に減少する。"
        self.skill1_cooldown_max = 5
        self.skill2_cooldown_max = 5
        self.is_boss = False

    def skill_tooltip(self):
        return f"スキル 1 : {self.skill1_description}\nクールダウン : {self.skill1_cooldown} 行動\n\nスキル 2 : {self.skill2_description}\nクールダウン : {self.skill2_cooldown} 行動\n\nスキル 3 : {self.skill3_description}\n"

    def skill1_logic(self):
        targets = self.target_selection(keyword="n_lowest_attr", keyword2="3", keyword3="hp", keyword4="ally")
        for target in targets:
            target.apply_effect(CancellationShield3('キャンセルシールド', 4, True, 0.1, False, uses=4))

    def skill2_logic(self):
        damage_dealt = self.attack(multiplier=4.5, repeat=1, target_kw1="n_enemy_in_front", target_kw2="3")
        return damage_dealt
        
    def skill3(self):
        pass

    def battle_entry_effects(self):
        shield = CancellationShield3('キャンセルシールド', -1, True, 0.1, False, uses=300)
        shield.can_be_removed_by_skill = False
        self.apply_effect(shield)
        self.apply_effect(StatsEffect('パッシブ効果', -1, True, {'final_damage_taken_multipler' : -0.20}, can_be_removed_by_skill=False))
         

class Kobold(character.Character):
    def __init__(self, name, lvl, exp=0, equip=None, image=None):
        super().__init__(name, lvl, exp, equip, image)
        self.original_name = "Kobold"
        self.skill1_description = "最大HPの30%に相当するHPを回復し、7ターンの間、防御力を50%増加させる。自分だけが生き残っている場合、効果は100%増加する。"
        self.skill2_description = "最も近い敵1体に攻撃力の800%のダメージを与える。自分だけが生き残っている場合、ダメージは100%増加する。"
        self.skill3_description = "防御力と最大HPが25%増加する。"
        self.skill1_cooldown_max = 5
        self.skill2_cooldown_max = 5
        self.is_boss = False

    def skill_tooltip(self):
        return f"スキル 1 : {self.skill1_description}\nクールダウン : {self.skill1_cooldown} 行動\n\nスキル 2 : {self.skill2_description}\nクールダウン : {self.skill2_cooldown} 行動\n\nスキル 3 : {self.skill3_description}\n"

    def skill1_logic(self):
        if len(self.ally) == 1:
            self.heal_hp(self.maxhp * 0.6, self)
            self.apply_effect(StatsEffect('パワー', 7, True, {'defense' : 2.0}))
        else:
            self.heal_hp(self.maxhp * 0.3, self)
            self.apply_effect(StatsEffect('パワー', 7, True, {'defense' : 1.5}))
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
        self.apply_effect(StatsEffect('パッシブ効果', -1, True, {'defense' : 1.25, 'maxhp' : 1.25}, can_be_removed_by_skill=False))


class SoldierA(character.Character):
    def __init__(self, name, lvl, exp=0, equip=None, image=None):
        super().__init__(name, lvl, exp, equip, image)
        self.original_name = "SoldierA"
        self.skill1_description = "防御力が最も高い敵に対して攻撃力の360%で3回集中攻撃を行う。各攻撃は対象の防御力を20%低下させ、その効果は7ターン持続する。"
        self.skill2_description = "全ての敵に攻撃力の200%で攻撃し、防御力を35%低下させる。その効果は7ターン持続する。"
        self.skill3_description = "スキル攻撃は30%の確率で出血を引き起こす。出血は6ターンの間、攻撃力の30%に相当する状態ダメージを毎ターン受ける。"
        self.skill1_cooldown_max = 4
        self.skill2_cooldown_max = 4
        self.is_boss = False

    def skill_tooltip(self):
        return f"スキル 1 : {self.skill1_description}\nクールダウン : {self.skill1_cooldown} 行動\n\nスキル 2 : {self.skill2_description}\nクールダウン : {self.skill2_cooldown} 行動\n\nスキル 3 : {self.skill3_description}\n"

    def skill1_logic(self):
        def bleed_effect_defence_break(self, target):
            dice = random.randint(1, 100)
            if dice <= 30:
                target.apply_effect(ContinuousDamageEffect('出血', duration=6, is_buff=False, value=0.3 * self.atk, imposter=self))
            target.apply_effect(StatsEffect('防御力低下', 7, False, {'defense' : 0.80}))
        damage_dealt = self.attack(multiplier=3.6, repeat_seq=3, func_after_dmg=bleed_effect_defence_break, target_kw1="n_highest_attr", target_kw2="1", target_kw3="defense", target_kw4="enemy")
        return damage_dealt

    def skill2_logic(self):
        def bleed_effect_defence_break(self, target):
            dice = random.randint(1, 100)
            if dice <= 30:
                target.apply_effect(ContinuousDamageEffect('出血', duration=6, is_buff=False, value=0.3 * self.atk, imposter=self))
            target.apply_effect(StatsEffect('防御力低下', 7, False, {'defense' : 0.65}))
        damage_dealt = self.attack(multiplier=2.0, repeat=1, func_after_dmg=bleed_effect_defence_break, target_kw1="n_random_enemy", target_kw2="5")
        return damage_dealt
        
    def skill3(self):
        pass


class FutureSoldier(character.Character):
    def __init__(self, name, lvl, exp=0, equip=None, image=None):
        super().__init__(name, lvl, exp, equip, image)
        self.original_name = "FutureSoldier"
        self.skill1_description = "ランダムな敵に攻撃力の200%で5回攻撃し、各攻撃は対象の防御力を6ターンの間25%減少させる。"
        self.skill2_description = "ランダムな敵に攻撃力の150%で7回攻撃し、対象の防御力が自分より低い場合、ダメージが100%増加する。"
        self.skill3_description = "通常攻撃は、対象の防御力が自分より低い場合、ダメージが倍になる。"
        self.skill1_cooldown_max = 4
        self.skill2_cooldown_max = 4
        self.is_boss = False

    def skill_tooltip(self):
        return f"スキル 1 : {self.skill1_description}\nクールダウン : {self.skill1_cooldown} 行動\n\nスキル 2 : {self.skill2_description}\nクールダウン : {self.skill2_cooldown} 行動\n\nスキル 3 : {self.skill3_description}\n"

    def skill1_logic(self):
        def defence_break(self, target):
            target.apply_effect(StatsEffect('防御力低下', 6, False, {'defense' : 0.75}))
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
        self.skill1_description = "全ての敵に攻撃力の400%のダメージを与え、6ターンの間、敵の防御力を40%減少させる。"
        self.skill2_description = "ランダムな敵に対して攻撃力の200%で8回攻撃を行う。対象の防御力が自分より低い場合、自身と対象の防御力の比率に相当するパーセンテージでダメージが増加する。"
        # 例: self.defense = 100, target.defense = 50, ダメージ増加量 = 100%
        self.skill3_description = "防御力が30%増加する。"
        self.skill1_cooldown_max = 4
        self.skill2_cooldown_max = 4
        self.is_boss = True

    def skill_tooltip(self):
        return f"スキル 1 : {self.skill1_description}\nクールダウン : {self.skill1_cooldown} 行動\n\nスキル 2 : {self.skill2_description}\nクールダウン : {self.skill2_cooldown} 行動\n\nスキル 3 : {self.skill3_description}\n"

    def skill1_logic(self):
        def defence_break(self, target):
            target.apply_effect(StatsEffect('防御力低下', 6, False, {'defense' : 0.6}))
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
        self.apply_effect(StatsEffect('パッシブ効果', -1, True, {'defense' : 1.3}, can_be_removed_by_skill=False))


class Mandrake(character.Character):
    def __init__(self, name, lvl, exp=0, equip=None, image=None):
        super().__init__(name, lvl, exp, equip, image)
        self.original_name = "Mandrake"
        self.skill1_description = "隣接する2人の味方を自身の防御力の100%で回復し、6ターンの間、その防御力を30%増加させる。"
        self.skill2_description = "隣接する2人の味方に6ターンの間、再生効果を付与する。再生効果はターンごとに自身の防御力の100%を回復する。" \
        "さらに6ターンの間、クリティカル防御力を30%増加させる。"
        self.skill3_description = "最大HPを15%増加させ、防御力を150%増加させる。"
        self.skill1_cooldown_max = 5
        self.skill2_cooldown_max = 5
        self.is_boss = False

    def skill_tooltip(self):
        return f"スキル 1 : {self.skill1_description}\nクールダウン : {self.skill1_cooldown} 行動\n\nスキル 2 : {self.skill2_description}\nクールダウン : {self.skill2_cooldown} 行動\n\nスキル 3 : {self.skill3_description}\n"

    def skill1_logic(self):
        neighbors = self.get_neighbor_allies_not_including_self()
        def effect(self, target, healing, overhealing):
            target.apply_effect(StatsEffect('防御力増加', 6, True, {'defense' : 1.3}))
        self.heal(target_list=neighbors, value=1.0 * self.defense, func_after_each_heal=effect)
        return 0

    def skill2_logic(self):
        neighbors = self.get_neighbor_allies_not_including_self()
        for n in neighbors:
            n.apply_effect(ContinuousHealEffect('再生', 6, True, 1.0 * self.defense, False))
            n.apply_effect(StatsEffect('クリ防御力増加', 6, True, {'critdef' : 0.3}))
        return 0
    
    def skill3(self):
        pass

    def battle_entry_effects(self):
        self.apply_effect(StatsEffect('パッシブ効果', -1, True, {'maxhp' : 1.15, 'defense' : 2.5}, can_be_removed_by_skill=False))
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
        self.skill1_description = "自身および隣接する2人の味方が5ターンの間、回避率を40%上げる。"
        self.skill2_description = "最も近い3体の敵に対し攻撃力の250%で2回攻撃する。各攻撃には70%の確率で出血効果を4ターン間与える。出血効果はターン毎に攻撃力の50%の状態ダメージを与える。"
        self.skill3_description = "回避率が50%増加し、速度が5%上がる。"
        self.skill1_cooldown_max = 5
        self.skill2_cooldown_max = 5
        self.is_boss = False

    def skill_tooltip(self):
        return f"スキル 1 : {self.skill1_description}\nクールダウン : {self.skill1_cooldown} 行動\n\nスキル 2 : {self.skill2_description}\nクールダウン : {self.skill2_cooldown} 行動\n\nスキル 3 : {self.skill3_description}\n"

    def skill1_logic(self):
        self_and_neighbor = self.get_neighbor_allies_including_self() # list
        for ally in self_and_neighbor:
            ally.apply_effect(StatsEffect('回避率上昇', 5, True, {'eva' : 0.4}))
        return 0

    def skill2_logic(self):
        def bleed_effect(self, target):
            dice = random.randint(1, 100)
            if dice <= 70:
                target.apply_effect(ContinuousDamageEffect('出血', duration=4, is_buff=False, value=0.5 * self.atk, imposter=self))
        damage_dealt = self.attack(multiplier=2.5, repeat_seq=2, func_after_dmg=bleed_effect, target_kw1="n_enemy_in_front", target_kw2="3")
        return damage_dealt

    def skill3(self):
        pass

    def battle_entry_effects(self):
        self.apply_effect(StatsEffect('パッシブ効果', -1, True, {'eva' : 0.5, 'spd' : 1.05}, can_be_removed_by_skill=False))


class Hermit(character.Character):
    def __init__(self, name, lvl, exp=0, equip=None, image=None):
        super().__init__(name, lvl, exp, equip, image)
        self.original_name = "Hermit"
        self.skill1_description = "最も近い3体の敵に攻撃力の235%で4回攻撃し、回避率の割合に応じてダメージが増加する。攻撃後、4ターンの間、回避率を20%増加する。"
        self.skill2_description = "全ての敵に攻撃力の500%で攻撃し、回避率が70%以上の場合、この攻撃は必ず命中しクリティカルヒットとなる。5ターンの間、敵を盲目状態にする。盲目：命中率を50%減少させる。"
        self.skill3_description = "回避率が50%増加する。最終的に受けるダメージが15%減少する。"
        self.skill1_cooldown_max = 5
        self.skill2_cooldown_max = 5
        self.is_boss = True

    def skill_tooltip(self):
        return f"スキル 1 : {self.skill1_description}\nクールダウン : {self.skill1_cooldown} 行動\n\nスキル 2 : {self.skill2_description}\nクールダウン : {self.skill2_cooldown} 行動\n\nスキル 3 : {self.skill3_description}\n"

    def skill1_logic(self):
        def damage_amplify(self, target, final_damage):
            final_damage *= max(1 + self.eva, 1.0)
            return final_damage
        damage_dealt = self.attack(multiplier=2.35, repeat_seq=4, func_damage_step=damage_amplify, target_kw1="n_enemy_in_front", target_kw2="3")
        self.apply_effect(StatsEffect('回避率上昇', 4, True, {'eva' : 0.2}))
        return damage_dealt

    def skill2_logic(self):
        if self.eva > 0.7:
            def blind_effect(self, target):
                target.apply_effect(StatsEffect('盲目', 5, False, {'acc' : -0.5}))
            damage_dealt = self.attack(multiplier=5.0, repeat=1, func_after_dmg=blind_effect, always_hit=True, always_crit=True)
        else:
            def blind_effect(self, target):
                target.apply_effect(StatsEffect('盲目', 5, False, {'acc' : -0.5}))
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
        self.skill1_description = "1ターンの間、命中率を25%上げ、" \
        "回避率が最も高い敵に攻撃力の240%で4回攻撃する。各攻撃は100%の確率で4ターンの間、スタン効果を与え、" \
        "40%の確率で6ターンの間出血効果を付与する。出血：ターンごとに攻撃力の40%に相当する状態ダメージを受ける。"
        self.skill2_description = "5ターンの間、味方全体の回避率が0%より高い場合、現在の回避率の100%分の攻撃力を得る。"
        self.skill3_description = "全ての味方の回避率が20%、命中率が40%増加する。"
        self.skill1_cooldown_max = 5
        self.skill2_cooldown_max = 5
        self.is_boss = True

    def skill_tooltip(self):
        return f"スキル 1 : {self.skill1_description}\nクールダウン : {self.skill1_cooldown} 行動\n\nスキル 2 : {self.skill2_description}\nクールダウン : {self.skill2_cooldown} 行動\n\nスキル 3 : {self.skill3_description}\n"

    def skill1_logic(self):
        self.apply_effect(StatsEffect('功夫', 1, True, {'acc' : 0.25}))
        def bleed_stun_effect(self, target):
            dice = random.randint(1, 100)
            if dice <= 40:
                target.apply_effect(ContinuousDamageEffect('Bleed', duration=6, is_buff=False, value=0.4 * self.atk, imposter=self))
            target.apply_effect(StunEffect('スタン', 4, False))
        damage_dealt = self.attack(multiplier=2.4, repeat=4, func_after_dmg=bleed_stun_effect, target_kw1="n_highest_attr", target_kw2="1", target_kw3="eva", target_kw4="enemy")
        return damage_dealt

    def skill2_logic(self):
        for a in self.ally:
            if a.eva > 0:
                a.apply_effect(StatsEffect('功夫', 5, True, {'atk' : a.eva + 1.0}))
        return 0
        
    def skill3(self):
        pass

    def battle_entry_effects(self):
        for a in self.ally:
            a.apply_effect(StatsEffect('功夫', -1, True, {'eva' : 0.2, 'acc' : 0.4}, can_be_removed_by_skill=False))


class HauntedTree(character.Character):
    def __init__(self, name, lvl, exp=0, equip=None, image=None):
        super().__init__(name, lvl, exp, equip, image)
        self.original_name = "HauntedTree"
        self.skill1_description = "最も近い敵3体を9ターンの間ルート状態にする。ルート:回避が55%減少し、防御力とクリティカル防御力が20%減少する。" \
        "同じ効果が再度適用された場合、効果時間は更新される。"
        self.skill2_description = "ルートした敵がいない場合、このスキルは効果を持たない。" \
        "ルートした敵全てにAtk360%で3回攻撃し、各攻撃は自身の最大HPの5%に等しい追加ダメージを与える。"
        self.skill3_description="ルートした敵から受けるダメージが60%減少する。"
        self.skill1_cooldown_max = 4
        self.skill2_cooldown_max = 4
        self.is_boss = False

    def skill_tooltip(self):
        return f"スキル 1 : {self.skill1_description}\nクールダウン : {self.skill1_cooldown} 行動\n\nスキル 2 : {self.skill2_description}\nクールダウン : {self.skill2_cooldown} 行動\n\nスキル 3 : {self.skill3_description}\n"

    def skill1_logic(self):
        targets = self.target_selection("n_enemy_in_front", "3")
        eff = StatsEffect('ルート', 9, False, {'eva' : -0.55, 'defense' : 0.8, 'critdef' : -0.2})
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
        if attacker.has_effect_that_named('ルート', additional_name='HauntedTree_Rooted'):
            global_vars.turn_info_string += f"{self.name}は{attacker.name}からのダメージを60%軽減した。\n"
            return damage * 0.4
        return damage

    def battle_entry_effects(self):
        self.apply_effect(StatsEffect('パッシブ効果', -1, True, {'defense' : 1.30, 'critdef' : 0.30, 'maxhp' : 1.30}))
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
        self.skill1_description = "最も近い3つの敵に攻撃力の300%で攻撃し、6ターンの間燃焼を付与する。燃焼はターンごとに攻撃力の40%の状態ダメージを与える。対象がデバフの状態の場合、燃焼効果を3つ付与する。"
        self.skill2_description = "最も近い敵に攻撃力の320%で3回攻撃する。対象がデバフの状態の場合、各攻撃で6ターンの間燃焼効果を3つ付与する。"
        self.skill3_description = "攻撃力を10%増加する。"
        self.skill1_cooldown_max = 5
        self.skill2_cooldown_max = 5
        self.is_boss = False

    def skill_tooltip(self):
        return f"スキル 1 : {self.skill1_description}\nクールダウン : {self.skill1_cooldown} 行動\n\nスキル 2 : {self.skill2_description}\nクールダウン : {self.skill2_cooldown} 行動\n\nスキル 3 : {self.skill3_description}\n"

    def skill1_logic(self):
        def burn_effect(self, target):
            if len(target.debuffs) > 0:
                target.apply_effect(ContinuousDamageEffect('燃焼', duration=6, is_buff=False, value=0.4 * self.atk, imposter=self))
                target.apply_effect(ContinuousDamageEffect('燃焼', duration=6, is_buff=False, value=0.4 * self.atk, imposter=self))
                target.apply_effect(ContinuousDamageEffect('燃焼', duration=6, is_buff=False, value=0.4 * self.atk, imposter=self))
            else:
                target.apply_effect(ContinuousDamageEffect('燃焼', duration=6, is_buff=False, value=0.4 * self.atk, imposter=self))
        damage_dealt = self.attack(multiplier=3.0, repeat=1, func_after_dmg=burn_effect, target_kw1="n_enemy_in_front", target_kw2="3")
        return damage_dealt

    def skill2_logic(self):
        def burn_effect(self, target):
            if len(target.debuffs) > 0:
                target.apply_effect(ContinuousDamageEffect('燃焼', duration=6, is_buff=False, value=0.4 * self.atk, imposter=self))
                target.apply_effect(ContinuousDamageEffect('燃焼', duration=6, is_buff=False, value=0.4 * self.atk, imposter=self))
                target.apply_effect(ContinuousDamageEffect('燃焼', duration=6, is_buff=False, value=0.4 * self.atk, imposter=self))
        damage_dealt = self.attack(multiplier=3.2, repeat=3, func_after_dmg=burn_effect, target_kw1="enemy_in_front")
        return damage_dealt

    def skill3(self):
        pass

    def battle_entry_effects(self):
        self.apply_effect(StatsEffect('パッシブ効果', -1, True, {'atk' : 1.1}, can_be_removed_by_skill=False))


# Increase debuff duration
class Orklord(character.Character):
    def __init__(self, name, lvl, exp=0, equip=None, image=None):
        super().__init__(name, lvl, exp, equip, image)
        self.original_name = "Orklord"
        self.skill1_description = "最も近い敵に対して攻撃力の300%で3回攻撃する。対象がデバフの状態効果を持っている場合、効果の持続時間を4ターン延長する。"
        self.skill2_description = "5体の敵に攻撃力の400%で攻撃し、出血効果を10ターン付与する。出血は毎ターン攻撃力の55%に相当する状態ダメージを与える。"
        self.skill3_description = "通常攻撃が出血状態の対象に対して200%増加するダメージを与える。最大HPと防御力を50%増加させる。"
        self.skill1_cooldown_max = 3
        self.skill2_cooldown_max = 3
        self.is_boss = True

    def skill_tooltip(self):
        return f"スキル 1 : {self.skill1_description}\nクールダウン : {self.skill1_cooldown} 行動\n\nスキル 2 : {self.skill2_description}\nクールダウン : {self.skill2_cooldown} 行動\n\nスキル 3 : {self.skill3_description}\n"

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
            target.apply_effect(ContinuousDamageEffect('出血', duration=10, is_buff=False, value=0.55 * self.atk, imposter=self))
        damage_dealt = self.attack(multiplier=3.0, repeat=1, func_after_dmg=bleed_effect, target_kw1="n_random_enemy", target_kw2="5")
        return damage_dealt

    def skill3(self):
        pass

    def normal_attack(self):
        def damage_amplify(self, target, final_damage):
            if target.has_effect_that_named('出血'):
                final_damage *= 3.0
            return final_damage
        self.attack(func_damage_step=damage_amplify)

    def battle_entry_effects(self):
        self.apply_effect(StatsEffect('パッシブ効果', -1, True, {'maxhp' : 1.50, 'defense' : 1.50}, can_be_removed_by_skill=False))
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
        self.skill1_description = "最も近い敵1体に攻撃力の600%のダメージを与える。"
        self.skill2_description = "最も近い敵2体に攻撃力の330%のダメージを2回与える。"
        self.skill3_description = "ターゲットにかかっているバフの数に応じて、スキルダメージが各バフにつき60%増加する。"
        self.skill1_cooldown_max = 4
        self.skill2_cooldown_max = 4
        self.is_boss = False

    def skill_tooltip(self):
        return f"スキル 1 : {self.skill1_description}\nクールダウン : {self.skill1_cooldown} 行動\n\nスキル 2 : {self.skill2_description}\nクールダウン : {self.skill2_cooldown} 行動\n\nスキル 3 : {self.skill3_description}\n"

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
        self.skill1_description = "最もアクティブなバフ効果を持つ敵に攻撃力の600%で攻撃し、アクティブなバフ効果ごとに攻撃力の400%で再度攻撃する。"
        self.skill2_description = "スキル1のスキルクールダウンをリセットし、3ターンの間、速度を100%増加させる。最も近い敵に攻撃力の300%で3回攻撃する。ターゲットのアクティブなバフごとにダメージを30%増加させる。"
        self.skill3_description = "攻撃力、防御力、最大HPを30%増加する。"
        self.skill1_cooldown_max = 4
        self.skill2_cooldown_max = 2
        self.is_boss = True

    def skill_tooltip(self):
        return f"スキル 1 : {self.skill1_description}\nクールダウン : {self.skill1_cooldown} 行動\n\nスキル 2 : {self.skill2_description}\nクールダウン : {self.skill2_cooldown} 行動\n\nスキル 3 : {self.skill3_description}\n"

    def skill1_logic(self):
        def buffed_target_amplify(self, target, is_crit):
            buffs = len([e for e in target.buffs if not e.is_set_effect and not e.duration == -1])
            return self.attack(multiplier=4.0, repeat=buffs, target_list=[target])
        damage_dealt = self.attack(multiplier=6.0, repeat=1, target_kw1="n_enemy_with_most_buffs", target_kw2="1", additional_attack_after_dmg=buffed_target_amplify)
        return damage_dealt


    def skill2_logic(self):
        self.skill1_cooldown = 0
        self.apply_effect(StatsEffect('審判', 3, True, {'spd' : 2.0}))
        def buff_amplify(self, target, final_damage):
            buffs = len([e for e in target.buffs if not e.is_set_effect and not e.duration == -1])
            return final_damage * (1 + 0.3 * buffs)
        damage_dealt = self.attack(multiplier=3.0, repeat=3, target_kw1="enemy_in_front", func_damage_step=buff_amplify)
        return damage_dealt

        
    def skill3(self):
        pass

    def battle_entry_effects(self):
        self.apply_effect(StatsEffect('パッシブ効果', -1, True, {'atk' : 1.3, 'defense' : 1.3, 'maxhp' : 1.3}, can_be_removed_by_skill=False))
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
        self.skill1_description = "最も近い敵に攻撃力の280%で2回攻撃する。対象にアクティブなバフがない場合、ダメージを100%増加させる。"
        self.skill2_description = "最も近い敵に攻撃力の280%で2回攻撃する。対象にアクティブなバフがない場合、8ターンの間、対象の防御力を40%減少させる。"
        self.skill3_description = "毎ターンの終了時、そのターンに敵が倒れている場合、最大HPの30%に相当するHPを回復する。"
        self.skill1_cooldown_max = 4
        self.skill2_cooldown_max = 4
        self.is_boss = False
        self.enemycounter = len(self.enemy)

    def skill_tooltip(self):
        return f"スキル 1 : {self.skill1_description}\nクールダウン : {self.skill1_cooldown} 行動\n\nスキル 2 : {self.skill2_description}\nクールダウン : {self.skill2_cooldown} 行動\n\nスキル 3 : {self.skill3_description}\n"

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
                target.apply_effect(StatsEffect('防御力低下', 8, False, {'defense' : 0.6}))
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
        self.skill1_description = "アクティブバフがないすべての敵の防御力を8ターンの間に20%減少させ、クリティカル防御を8ターンの間に40%減少させる。"
        self.skill2_description = "最も近い敵に対して攻撃力の300%で3回攻撃する。対象にアクティブバフがない場合、クリティカルヒットを与える。"
        self.skill3_description = "最大HPが30%増加する。"
        self.skill1_cooldown_max = 4
        self.skill2_cooldown_max = 4
        self.is_boss = False
        self.enemycounter = len(self.enemy)

    def skill_tooltip(self):
        return f"スキル 1 : {self.skill1_description}\nクールダウン : {self.skill1_cooldown} 行動\n\nスキル 2 : {self.skill2_description}\nクールダウン : {self.skill2_cooldown} 行動\n\nスキル 3 : {self.skill3_description}\n"

    def skill1_logic(self):
        for e in self.enemy:
            if len([e for e in e.buffs if not e.is_set_effect and not e.duration == -1]) == 0:
                e.apply_effect(StatsEffect('測定済み', 8, False, {'defense' : 0.8, 'critdef' : -0.4}))
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
        self.apply_effect(StatsEffect('パッシブ効果', -1, True, {'maxhp' : 1.3}, can_be_removed_by_skill=False))
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
        self.skill1_description = "最も近い3人の敵に対して、攻撃力の330%のダメージを与える。"
        self.skill2_description = "最も近い敵に対して3回、攻撃力の330%で攻撃を集中する。"
        self.skill3_description = "4ターンの間、ダメージを受けない場合、ターン終了時に攻撃力を66%、速度を66%増加させる。同じ効果は2回適用されない。"
        self.skill1_cooldown_max = 5
        self.skill2_cooldown_max = 5
        self.is_boss = False

    def skill_tooltip(self):
        return f"スキル 1 : {self.skill1_description}\nクールダウン : {self.skill1_cooldown} 行動\n\nスキル 2 : {self.skill2_description}\nクールダウン : {self.skill2_cooldown} 行動\n\nスキル 3 : {self.skill3_description}\n"

    def skill1_logic(self):
        damage_dealt = self.attack(multiplier=3.3, repeat=1, target_kw1="n_enemy_in_front", target_kw2=3)
        return damage_dealt

    def skill2_logic(self):
        damage_dealt = self.attack(multiplier=3.3, repeat_seq=3, target_kw1="enemy_in_front")
        return damage_dealt
        
    def skill3(self):
        pass

    def battle_entry_effects(self):
        self.apply_effect(NotTakingDamageEffect("パッシブ効果", -1, True, {'atk' : 1.33, 'spd' : 1.33}, "default", 4, "熱狂", 4))


class Fanatic(character.Character):
    def __init__(self, name, lvl, exp=0, equip=None, image=None):
        super().__init__(name, lvl, exp, equip, image)
        self.original_name = "Fanatic"
        self.skill1_description = "最も近い敵に攻撃力の340%で3回攻撃する。4ターンダメージを受けていない場合、クリティカルヒットを発生させる。"
        self.skill2_description = "最も近い敵に攻撃力の340%で3回攻撃する。4ターンダメージを受けていない場合、ターゲットの最大HPの5%分ダメージが増加する。"
        self.skill3_description = "スキル攻撃によるダメージの30%分、HPを回復する。"
        self.skill1_cooldown_max = 5
        self.skill2_cooldown_max = 5
        self.is_boss = False

    def skill_tooltip(self):
        return f"スキル 1 : {self.skill1_description}\nクールダウン : {self.skill1_cooldown} 行動\n\nスキル 2 : {self.skill2_description}\nクールダウン : {self.skill2_cooldown} 行動\n\nスキル 3 : {self.skill3_description}\n"

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
        self.skill1_description = "最も近い敵に攻撃力の280%で2回攻撃する。生存している味方1人につきダメージが20%増加する。"
        self.skill2_description = "最も近い敵に攻撃力の560%で攻撃する。生存している味方1人につきダメージが20%増加する。"
        self.skill3_description = "5ターンの間ダメージを受けていない場合、ターンの終わりに全味方に6ターンの間プライドを適用する。プライド：攻撃力が30%増加し、速度も30%増加する。"
        self.skill1_cooldown_max = 5
        self.skill2_cooldown_max = 5
        self.is_boss = True

    def skill_tooltip(self):
        return f"スキル 1 : {self.skill1_description}\nクールダウン : {self.skill1_cooldown} 行動\n\nスキル 2 : {self.skill2_description}\nクールダウン : {self.skill2_cooldown} 行動\n\nスキル 3 : {self.skill3_description}\n"

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
                if not ally.has_effect_that_named('帝王のプライド'):
                    ally.apply_effect(StatsEffect('帝王のプライド', 6, True, {'atk' : 1.3, 'spd' : 1.3}))
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
        self.skill1_description = "攻撃力が最も高い2人の味方の攻撃力を8ターンの間に60%増加させる。"
        self.skill2_description = "最も近い敵に1ダメージを与え、自身の回避率を6ターンの間に50%増加させる。"
        self.skill3_description = "通常攻撃がスキル1のクールダウンをリセットし、攻撃力の200%ではなく400%のダメージを与え、2回攻撃する。"
        self.skill1_cooldown_max = 5
        self.skill2_cooldown_max = 5
        self.is_boss = False

    def skill_tooltip(self):
        return f"スキル 1 : {self.skill1_description}\nクールダウン : {self.skill1_cooldown} 行動\n\nスキル 2 : {self.skill2_description}\nクールダウン : {self.skill2_cooldown} 行動\n\nスキル 3 : {self.skill3_description}\n"

    def skill1_logic(self):
        self.update_ally_and_enemy()
        targets = self.target_selection(keyword="n_highest_attr", keyword2="2", keyword3="atk", keyword4="ally")
        for target in targets:
            target.apply_effect(StatsEffect('攻撃力増加', 8, True, {'atk' : 1.6}))

    def skill2_logic(self):
        damage_dealt = self.attack(repeat=1, target_kw1="enemy_in_front", func_damage_step=lambda self, target, final_damage : 1)
        self.apply_effect(StatsEffect('回避力増加', 6, True, {'eva' : 0.5}))
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
        self.skill1_description = "攻撃力の最も高い敵1体に対し、攻撃力の250%で3回集中攻撃する。各攻撃は対象の攻撃力を4ターンの間15%減少させる。"
        self.skill2_description = "攻撃力の最も高い3体の敵に対し、攻撃力の220%で2回攻撃する。対象の攻撃力が自身より低い場合、ダメージを40%増加させる。"
        self.skill3_description = "攻撃力を15%増加させる。戦闘開始時、自身および隣接する味方の攻撃力を15ターンの間15%増加させる。"
        self.skill1_cooldown_max = 5
        self.skill2_cooldown_max = 5
        self.is_boss = False

    def skill_tooltip(self):
        return f"スキル 1 : {self.skill1_description}\nクールダウン : {self.skill1_cooldown} 行動\n\nスキル 2 : {self.skill2_description}\nクールダウン : {self.skill2_cooldown} 行動\n\nスキル 3 : {self.skill3_description}\n"

    def skill1_logic(self):
        def atk_down(self, target):
            target.apply_effect(StatsEffect('攻撃力減少', 4, False, {'atk' : 0.85}))
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
        self.apply_effect(StatsEffect('パッシブ効果', -1, True, {'atk' : 1.15}, can_be_removed_by_skill=False))
        self_and_neighbors = self.get_neighbor_allies_including_self()
        for ally in self_and_neighbors:
            ally.apply_effect(StatsEffect('元気', 15, True, {'atk' : 1.15}))


class Kunoichi(character.Character):
    def __init__(self, name, lvl, exp=0, equip=None, image=None):
        super().__init__(name, lvl, exp, equip, image)
        self.original_name = "Kunoichi"
        self.skill1_description = "4ターンの間、命中率を20%上げ、最も近い3体の敵に攻撃力の240%で2回攻撃する。" \
                                "8ターンの間、対象の攻撃力を15%下げる。"
        self.skill2_description = "4ターンの間、攻撃力を20%上げ、最も近い敵に攻撃力の450%で攻撃する。" \
                                "8ターンの間、対象の攻撃力を30%下げる。"
        self.skill3_description = "自身と隣接する味方は、貫通力が20%増加する。"
        self.skill1_cooldown_max = 5
        self.skill2_cooldown_max = 5
        self.is_boss = False

    def skill_tooltip(self):
        return f"スキル 1 : {self.skill1_description}\nクールダウン : {self.skill1_cooldown} 行動\n\nスキル 2 : {self.skill2_description}\nクールダウン : {self.skill2_cooldown} 行動\n\nスキル 3 : {self.skill3_description}\n"

    def skill1_logic(self):
        self.apply_effect(StatsEffect('命中率増加', 4, True, {'acc' : 0.2}))
        def atk_down(self, target):
            target.apply_effect(StatsEffect('攻撃力減少', 8, False, {'atk' : 0.85}))
        damage_dealt = self.attack(multiplier=2.4, repeat_seq=2, func_after_dmg=atk_down, target_kw1="n_enemy_in_front", target_kw2="3")
        return damage_dealt

    def skill2_logic(self):
        self.apply_effect(StatsEffect('攻撃力増加', 4, True, {'atk' : 1.2}))
        def atk_down(self, target):
            target.apply_effect(StatsEffect('攻撃力減少', 8, False, {'atk' : 0.70}))
        damage_dealt = self.attack(multiplier=4.5, repeat=1, func_after_dmg=atk_down, target_kw1="enemy_in_front")
        return damage_dealt

    def skill3(self):
        pass

    def battle_entry_effects(self):
        self_and_neighbors = self.get_neighbor_allies_including_self()
        for ally in self_and_neighbors:
            ally.apply_effect(StatsEffect('シャープ', -1, True, {'penetration' : 0.2}, can_be_removed_by_skill=False))


class ArabianSoldier(character.Character):
    def __init__(self, name, lvl, exp=0, equip=None, image=None):
        super().__init__(name, lvl, exp, equip, image)
        self.original_name = "ArabianSoldier"
        self.skill1_description = "10ターンの間、攻撃力を20%増加させ、攻撃力が最も高い敵に対して攻撃力の300%で2回攻撃する。"
        self.skill2_description = "10ターンの間、防御力を20%増加させ、最大HPの30%に相当するHPを回復する。"
        self.skill3_description = "戦闘開始時、自分と隣接する味方の攻撃力と防御力を15ターンの間20%増加させる。"
        self.skill1_cooldown_max = 4
        self.skill2_cooldown_max = 4
        self.is_boss = False

    def skill_tooltip(self):
        return f"スキル 1 : {self.skill1_description}\nクールダウン : {self.skill1_cooldown} 行動\n\nスキル 2 : {self.skill2_description}\nクールダウン : {self.skill2_cooldown} 行動\n\nスキル 3 : {self.skill3_description}\n"

    def skill1_logic(self):
        self.apply_effect(StatsEffect('攻撃力増加', 10, True, {'atk' : 1.20}))
        damage_dealt = self.attack(multiplier=3.0, repeat_seq=2, target_kw1="n_highest_attr", target_kw2="1", target_kw3="atk", target_kw4="enemy")
        return damage_dealt

    def skill2_logic(self):
        self.apply_effect(StatsEffect('防御力増加', 10, True, {'defense' : 1.20}))
        self.heal_hp(self.maxhp * 0.3, self)
        return 0

    def skill3(self):
        pass

    def battle_entry_effects(self):
        self_and_neighbors = self.get_neighbor_allies_including_self()
        for ally in self_and_neighbors:
            ally.apply_effect(StatsEffect('攻撃防御増加', 15, True, {'atk' : 1.20, 'defense' : 1.20}))


# ====================================
# End of Attack
# ====================================
# Regeneration & Revival
# ====================================
        
class Mushroom(character.Character):
    def __init__(self, name, lvl, exp=0, equip=None, image=None):
        super().__init__(name, lvl, exp, equip, image)
        self.original_name = "Mushroom"
        self.skill1_description = "最も近い3体の敵に対して攻撃力の240%で2回集中攻撃する。"
        self.skill2_description = "最大HPの30%を回復し、7ターンの間、防御力を20%増加させる。"
        self.skill3_description = "HPが最大HP未満で非ゼロダメージを受けた後、最大HPの5%分のHPを回復する。"
        self.skill1_cooldown_max = 5
        self.skill2_cooldown_max = 5
        self.is_boss = False

    def skill_tooltip(self):
        return f"スキル 1 : {self.skill1_description}\nクールダウン : {self.skill1_cooldown} 行動\n\nスキル 2 : {self.skill2_description}\nクールダウン : {self.skill2_cooldown} 行動\n\nスキル 3 : {self.skill3_description}\n"

    def skill1_logic(self):
        damage_dealt = self.attack(multiplier=2.4, repeat_seq=2, target_kw1="n_enemy_in_front", target_kw2="3")
        return damage_dealt

    def skill2_logic(self):
        self.heal_hp(self.maxhp * 0.3, self)
        self.apply_effect(StatsEffect('防御力増加', 7, True, {'defense' : 1.2}))
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
        self.skill1_description = "最も近い3体の敵に対して、攻撃力の300%で2回集中攻撃を行い、与えたダメージの30%に相当するHPを回復する。"
        self.skill2_description = "現在のHPの20%を支払い、支払ったHPの量に相当する100%の固定ダメージで最も近い3人の敵を攻撃する。このスキルはHPが最大HPの20%未満の場合、効果がない。HPを支払うことは状態ダメージとして扱う。"
        self.skill3_description = "毎ターン、最大HPの5%に相当するHPを回復する。"
        self.skill1_cooldown_max = 5
        self.skill2_cooldown_max = 5
        self.is_boss = True

    def skill_tooltip(self):
        return f"スキル 1 : {self.skill1_description}\nクールダウン : {self.skill1_cooldown} 行動\n\nスキル 2 : {self.skill2_description}\nクールダウン : {self.skill2_cooldown} 行動\n\nスキル 3 : {self.skill3_description}\n"

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
        heal = ContinuousHealEffect('パッシブ効果', -1, True, 0.05, True)
        heal.can_be_removed_by_skill = False
        self.apply_effect(heal)


class Lich(character.Character):
    def __init__(self, name, lvl, exp=0, equip=None, image=None):
        super().__init__(name, lvl, exp, equip, image)
        self.original_name = "Lich"
        self.skill1_description = "最も近い敵に対して攻撃力の400%で3回攻撃する。"
        self.skill2_description = "最も近い敵に攻撃力の900%で攻撃し、対象の回復効率を5ターンの間50%減少させる。"
        self.skill3_description = "倒れた場合、次のターンにHP100%で復活する。この不死効果がある限り、CC効果に対する免疫を得る。"
        self.skill1_cooldown_max = 4
        self.skill2_cooldown_max = 4
        self.is_boss = True

    def skill_tooltip(self):
        return f"スキル 1 : {self.skill1_description}\nクールダウン : {self.skill1_cooldown} 行動\n\nスキル 2 : {self.skill2_description}\nクールダウン : {self.skill2_cooldown} 行動\n\nスキル 3 : {self.skill3_description}\n"

    def skill1_logic(self):
        damage_dealt = self.attack(multiplier=4.0, repeat=3, target_kw1="enemy_in_front")
        return damage_dealt

    def skill2_logic(self):
        def heal_efficiency_down(self, target):
            target.apply_effect(StatsEffect('回復効率減少', 5, False, {'heal_efficiency' : -0.5}))
        damage_dealt = self.attack(multiplier=9.0, repeat=1, func_after_dmg=heal_efficiency_down, target_kw1="enemy_in_front")
        return damage_dealt

    def skill3(self):
        pass

    def battle_entry_effects(self):
        reborn = RebornEffect('不死', -1, True, 1.0, True)
        reborn.can_be_removed_by_skill = False
        self.apply_effect(reborn)


class Cleric(character.Character):
    def __init__(self, name, lvl, exp=0, equip=None, image=None):
        super().__init__(name, lvl, exp, equip, image)
        self.original_name = "Cleric"
        self.skill1_description = "HPが最も低い3人の味方を攻撃力の600%で回復する。"
        self.skill2_description = "HPが最も低い3人の味方を対象に、6ターンの間、攻撃力の300%までのダメージを吸収するシールドを適用する。"
        self.skill3_description = "回復効率が30%増加する。"
        self.skill1_cooldown_max = 4
        self.skill2_cooldown_max = 4
        self.is_boss = False

    def skill_tooltip(self):
        return f"スキル 1 : {self.skill1_description}\nクールダウン : {self.skill1_cooldown} 行動\n\nスキル 2 : {self.skill2_description}\nクールダウン : {self.skill2_cooldown} 行動\n\nスキル 3 : {self.skill3_description}\n"

    def skill1_logic(self):
        targets = list(self.target_selection(keyword="n_lowest_hp_percentage_ally", keyword2="3"))
        for target in targets:
            target.heal_hp(self.atk * 6, self)

    def skill2_logic(self):
        targets = list(self.target_selection(keyword="n_lowest_hp_percentage_ally", keyword2="3"))
        for target in targets:
            target.apply_effect(AbsorptionShield('シールド', 6, True, 3 * self.atk, self))

    def skill3(self):
        pass

    def battle_entry_effects(self):
        self.apply_effect(StatsEffect('パッシブ効果', -1, True, {'heal_efficiency' : 0.3}, can_be_removed_by_skill=False))



# ====================================
# End of Regeneration & Revival
# ====================================
# Benefit from attribute condition
# ====================================
        

class Infantry(character.Character):
    def __init__(self, name, lvl, exp=0, equip=None, image=None):
        super().__init__(name, lvl, exp, equip, image)
        self.original_name = "Infantry"
        self.skill1_description = "最も近い敵に攻撃力の280%で3回攻撃し、30%の確率で6ターンの間、攻撃力を30%下げる攻撃力減少を付与する。"
        self.skill2_description = "最も近い敵に攻撃力の280%で4回攻撃する。"
        self.skill3_description = "対象の攻撃力が自身より低い場合、スキルダメージが50%増加する。"
        self.skill1_cooldown_max = 5
        self.skill2_cooldown_max = 5
        self.is_boss = False

    def skill_tooltip(self):
        return f"スキル 1 : {self.skill1_description}\nクールダウン : {self.skill1_cooldown} 行動\n\nスキル 2 : {self.skill2_description}\nクールダウン : {self.skill2_cooldown} 行動\n\nスキル 3 : {self.skill3_description}\n"

    def skill1_logic(self):
        def atk_down(self, target):
            if random.random() < 0.3:
                target.apply_effect(StatsEffect('攻撃力減少', 6, False, {'atk' : 0.7}))
        def high_atk(self, target, final_damage):
            if target.atk < self.atk:
                global_vars.turn_info_string += f"{self.name}は{target.name}に追加で50%のダメージを与えた。\n"
                final_damage *= 1.5
            return final_damage
        damage_dealt = self.attack(multiplier=2.8, repeat=3, func_after_dmg=atk_down, func_damage_step=high_atk, target_kw1="enemy_in_front")
        return damage_dealt

    def skill2_logic(self):
        def high_atk(self, target, final_damage):
            if target.atk < self.atk:
                global_vars.turn_info_string += f"{self.name}は{target.name}に追加で50%のダメージを与えた。\n"
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
        self.skill1_description = "最も近い敵に攻撃力の400%で2回攻撃し、35%の確率で防御力ダウンを6ターンの間付与する。防御力は30%減少する。"
        self.skill2_description = "最も近い敵に攻撃力の400%で2回攻撃する。HPが20%以下の場合、10ターンの間、最大HPを40%増加させ、毎ターン最大HPの8%回復する。"
        self.skill3_description = "HPが20%以下の場合、スキルダメージが100%増加する。"
        self.skill1_cooldown_max = 5
        self.skill2_cooldown_max = 5
        self.is_boss = False

    def skill_tooltip(self):
        return f"スキル 1 : {self.skill1_description}\nクールダウン : {self.skill1_cooldown} 行動\n\nスキル 2 : {self.skill2_description}\nクールダウン : {self.skill2_cooldown} 行動\n\nスキル 3 : {self.skill3_description}\n"

    def skill1_logic(self):
        def def_down(self, target):
            if random.random() < 0.35:
                target.apply_effect(StatsEffect('防御力減少', 6, False, {'defense' : 0.7}))
        def low_hp(self, target, final_damage):
            if self.hp < self.maxhp * 0.2:
                global_vars.turn_info_string += f"{self.name}は{target.name}に100%の追加ダメージを与えた。\n"
                final_damage *= 2.0
            return final_damage
        damage_dealt = self.attack(multiplier=4.0, repeat=2, func_after_dmg=def_down, func_damage_step=low_hp, target_kw1="enemy_in_front")
        return damage_dealt


    def skill2_logic(self):
        def low_hp(self, target, final_damage):
            if self.hp < self.maxhp * 0.2:
                global_vars.turn_info_string += f"{self.name}は{target.name}に100%の追加ダメージを与えた。\n"
                final_damage *= 2.0
            return final_damage
        damage_dealt = self.attack(multiplier=4.0, repeat=2, target_kw1="enemy_in_front", func_damage_step=low_hp)
        if self.is_alive() and self.hp < self.maxhp * 0.2:
            self.apply_effect(StatsEffect('最大HP増加', 10, True, {'maxhp' : 1.4}))
            self.apply_effect(ContinuousHealEffect('再生', 10, True, 0.08, True))
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
        self.skill1_description = "全ての味方を攻撃力の300%で回復し、9ターンの間、攻撃力を40%、速度を20%増加させる。"
        self.skill2_description = "最もHPが低い味方1体にシールドを適用する。このシールドは攻撃力の600%のダメージを8ターンの間吸収する。"
        self.skill3_description = "通常攻撃は400%のダメージを与え、ランダムな敵ペアを攻撃する。戦闘開始時に、攻撃力の1500%のダメージを吸収するシールドを適用する。"
        self.skill1_cooldown_max = 4
        self.skill2_cooldown_max = 4
        self.is_boss = True

    def skill_tooltip(self):
        return f"スキル 1 : {self.skill1_description}\nクールダウン : {self.skill1_cooldown} 行動\n\nスキル 2 : {self.skill2_description}\nクールダウン : {self.skill2_cooldown} 行動\n\nスキル 3 : {self.skill3_description}\n"

    def skill1_logic(self):
        self.update_ally_and_enemy()
        for target in self.ally:
            target.heal_hp(self.atk * 3.0, self)
            target.apply_effect(StatsEffect('速度攻撃増加', 9, True, {'atk' : 1.4, 'spd' : 1.2}))

    def skill2_logic(self):
        target = next(self.target_selection(keyword="n_lowest_hp_percentage_ally", keyword2="1"))
        target.apply_effect(AbsorptionShield('シールド', 8, True, 6 * self.atk, False))

    def skill3(self):
        pass

    def normal_attack(self):
        self.attack(multiplier=4.0, repeat=1, target_kw1="random_enemy_pair")

    def battle_entry_effects(self):
        shield = AbsorptionShield('シールド', -1, True, 15 * self.atk, False)
        shield.can_be_removed_by_skill = False
        self.apply_effect(shield)


class Unicorn(character.Character):
    def __init__(self, name, lvl, exp=0, equip=None, image=None):
        super().__init__(name, lvl, exp, equip, image)
        self.original_name = "Unicorn"
        self.skill1_description = "最も近い敵に攻撃力の555%で攻撃し、重傷を7ターンの間与える。重傷：ターンごとに攻撃力の100%の状態ダメージを与え、回復によって除去可能。"
        self.skill2_description = "中央の味方にシールドを適用する。シールドは自身の攻撃力の500%までのダメージを5ターンの間吸収する。"
        self.skill3_description = "HPを30%増加させる。"
        self.skill1_cooldown_max = 4
        self.skill2_cooldown_max = 4
        self.is_boss = False

    def skill_tooltip(self):
        return f"スキル 1 : {self.skill1_description}\nクールダウン : {self.skill1_cooldown} 行動\n\nスキル 2 : {self.skill2_description}\nクールダウン : {self.skill2_cooldown} 行動\n\nスキル 3 : {self.skill3_description}\n"

    def skill1_logic(self):
        def deep_wound(self, target):
            target.apply_effect(ContinuousDamageEffect('重傷', 7, False, self.atk, self, remove_by_heal=True))
        damage_dealt = self.attack(multiplier=5.55, repeat=1, func_after_dmg=deep_wound, target_kw1="enemy_in_front")
        return damage_dealt

    def skill2_logic(self):
        t = next(self.target_selection(keyword="n_ally_in_middle", keyword2="1"))
        t.apply_effect(AbsorptionShield('シールド', 5, True, 5 * self.atk, False))

    def skill3(self):
        pass

    def battle_entry_effects(self):
        self.apply_effect(StatsEffect('パッシブ効果', -1, True, {'maxhp' : 1.3}, can_be_removed_by_skill=False))
        self.hp = self.maxhp


class Zhenniao(character.Character):
    def __init__(self, name, lvl, exp=0, equip=None, image=None):
        super().__init__(name, lvl, exp, equip, image)
        self.original_name = "Zhenniao"
        self.skill1_description = "真ん中の味方の回避率を20%、速度を20%上げ、10ターンの間持続し、自身の攻撃力の200%に相当するHPを回復する。"
        self.skill2_description = "真ん中の味方のクリティカル率を20%、クリティカルダメージを40%上げ、10ターンの間持続し、自身の攻撃力の100%に相当するHPを回復する。"
        self.skill3_description = "通常攻撃のダメージを120%増加させ、2回攻撃する。最大HPを30%増加させる。"
        self.skill1_cooldown_max = 5
        self.skill2_cooldown_max = 5
        self.is_boss = False

    def skill_tooltip(self):
        return f"スキル 1 : {self.skill1_description}\nクールダウン : {self.skill1_cooldown} 行動\n\nスキル 2 : {self.skill2_description}\nクールダウン : {self.skill2_cooldown} 行動\n\nスキル 3 : {self.skill3_description}\n"

    def skill1_logic(self):
        t = next(self.target_selection(keyword="n_ally_in_middle", keyword2="1"))
        t.apply_effect(StatsEffect('速度回避増加', 10, True, {'eva' : 0.20, 'spd' : 1.20}))
        t.heal_hp(self.atk * 2, self)
        return 0

    def skill2_logic(self):
        t = next(self.target_selection(keyword="n_ally_in_middle", keyword2="1"))
        t.apply_effect(StatsEffect('クリ率クリダメ増加', 10, True, {'crit' : 0.20, 'critdmg' : 0.40}))
        t.heal_hp(self.atk, self)
        return 0

    def skill3(self):
        pass

    def normal_attack(self):
        self.attack(multiplier=2.0, repeat=2, func_damage_step=lambda self, target, final_damage : final_damage * 2.2)

    def battle_entry_effects(self):
        self.apply_effect(StatsEffect('パッシブ効果', -1, True, {'maxhp' : 1.3}, can_be_removed_by_skill=False))
        self.hp = self.maxhp


class YataGarasu(character.Character):
    def __init__(self, name, lvl, exp=0, equip=None, image=None):
        super().__init__(name, lvl, exp, equip, image)
        self.original_name = "YataGarasu"
        self.skill1_description = "中央の味方の速度を4ターンの間、100%上昇させる。"
        self.skill2_description = "中央の3人の味方に6ターンの間、シールドを適用する。シールド：最大HPの10%を超えるダメージの部分が50%減少する。"
        self.skill3_description = "速度が10%上昇する。通常攻撃は5ターンの間、燃焼させる。燃焼：ターンごとに攻撃力の150%の状態ダメージを与える。"
        self.skill1_cooldown_max = 5
        self.skill2_cooldown_max = 5
        self.is_boss = False

    def skill_tooltip(self):
        return f"スキル 1 : {self.skill1_description}\nクールダウン : {self.skill1_cooldown} 行動\n\nスキル 2 : {self.skill2_description}\nクールダウン : {self.skill2_cooldown} 行動\n\nスキル 3 : {self.skill3_description}\n"

    def skill1_logic(self):
        t = next(self.target_selection(keyword="n_ally_in_middle", keyword2="1"))
        t.apply_effect(StatsEffect('速度増加', 4, True, {'spd' : 2.0}))
        return 0

    def skill2_logic(self):
        targets = list(self.target_selection(keyword="n_ally_in_middle", keyword2="3"))
        for target in targets:
            target.apply_effect(EffectShield2('シールド', 6, True, False, damage_reduction=0.5, shrink_rate=0, threshold=0.1))
        return 0

    def skill3(self):
        pass

    def normal_attack(self):
        def burn(self, target):
            target.apply_effect(ContinuousDamageEffect('燃焼', 5, False, self.atk * 1.5, self))
        self.attack(multiplier=2.0, repeat=1, func_after_dmg=burn)

    def battle_entry_effects(self):
        self.apply_effect(StatsEffect('パッシブ効果', -1, True, {'spd' : 1.1}, can_be_removed_by_skill=False))


class Anubis(character.Character):
    def __init__(self, name, lvl, exp=0, equip=None, image=None):
        super().__init__(name, lvl, exp, equip, image)
        self.original_name = "Anubis"
        self.skill1_description = "最も近い3体の敵に攻撃力の270%のダメージを与え、全ての味方の攻撃力と防御力を10ターンの間20%増加させる。"
        self.skill2_description = "ランダムな敵に攻撃力の240%のダメージを3回与え、全ての味方の貫通率を10ターンの間20%増加させる。"
        self.skill3_description = "0以上のダメージを受けた時、12%の確率で全ての味方の防御力を10ターンの間12%増加させる。"
        self.skill1_cooldown_max = 4
        self.skill2_cooldown_max = 4
        self.is_boss = False

    def skill_tooltip(self):
        return f"スキル 1 : {self.skill1_description}\nクールダウン : {self.skill1_cooldown} 行動\n\nスキル 2 : {self.skill2_description}\nクールダウン : {self.skill2_cooldown} 行動\n\nスキル 3 : {self.skill3_description}\n"

    def skill1_logic(self):
        damage_dealt = self.attack(multiplier=2.7, repeat=1, target_kw1="n_enemy_in_front", target_kw2="3")
        for a in self.ally:
            a.apply_effect(StatsEffect('攻撃防御増加', 10, True, {'atk' : 1.2, 'defense' : 1.2}))
        return damage_dealt

    def skill2_logic(self):
        damage_dealt = self.attack(multiplier=2.4, repeat=3)
        for a in self.ally:
            a.apply_effect(StatsEffect('貫通増加', 10, True, {'penetration' : 0.2}))
        return damage_dealt

    def skill3(self):
        pass

    def take_damage_aftermath(self, damage, attacker):
        if random.randint(1, 100) <= 12 and damage > 0:
            print(f"{self.name} triggers skill 3.")
            for a in self.ally:
                a.apply_effect(StatsEffect('防御増加', 10, True, {'defense' : 1.12}))


# ====================================
# End of Support
# ====================================
# Early Game Powercreep
# ====================================
        
class FootSoldier(character.Character):
    def __init__(self, name, lvl, exp=0, equip=None, image=None):
        super().__init__(name, lvl, exp, equip, image)
        self.original_name = "FootSoldier"
        self.skill1_description = "最も近い敵に攻撃力の250%で3回攻撃する。"
        self.skill2_description = "最も近い敵に攻撃力の550%で攻撃し、7ターンの間、80%の確率で足止め効果を付与する。足止め：攻撃力が10%減少、スピードが20%減少、回避率が30%減少。"
        self.skill3_description = "攻撃力とスピードを100%増加させる。ターンが経過するごとに効果が4%ずつ減少し、35ターン目まで続く。"
        self.skill1_cooldown_max = 5
        self.skill2_cooldown_max = 5
        self.is_boss = False

    def skill_tooltip(self):
        return f"スキル 1 : {self.skill1_description}\nクールダウン : {self.skill1_cooldown} 行動\n\nスキル 2 : {self.skill2_description}\nクールダウン : {self.skill2_cooldown} 行動\n\nスキル 3 : {self.skill3_description}\n"

    def skill1_logic(self):
        damage_dealt = self.attack(multiplier=2.5, repeat=3, target_kw1="enemy_in_front")
        return damage_dealt

    def skill2_logic(self):
        def cripple(self, target):
            if random.random() < 0.8:
                target.apply_effect(StatsEffect('足止め', 7, False, {'atk' : 0.9, 'spd' : 0.8, 'eva' : -0.3}))
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
        self.apply_effect(StatsEffect('パッシブ効果', -1, True, {'atk' : 2.0, 'spd' : 2.0}, use_active_flag=False, 
                                      stats_dict_function=decrease_func, condition=condition, can_be_removed_by_skill=False))


class Daji(character.Character):
    def __init__(self, name, lvl, exp=0, equip=None, image=None):
        super().__init__(name, lvl, exp, equip, image)
        self.original_name = "Daji"
        self.skill1_description = "全ての味方の攻撃力を111%、命中率を10%、貫通率を10%アップさせ、8ターン持続する。このスキルを使用する度に、攻撃力ボーナスが33%減少する。"
        self.skill2_description = "全ての味方を攻撃力の200%で回復し、攻撃力の300%までのダメージを吸収するシールドを8ターンの間適用する。このスキルを使用する度に、シールドの量が攻撃力の100%減少する。"
        self.skill3_description = "ターン終了時に、生存している味方の数が敵より多い場合、全ての味方に8ターンの間、プライドを適用する。プライド：攻撃力を45%増加させる。同じ効果は一度以上適用されない。"
        self.skill1_cooldown_max = 4
        self.skill2_cooldown_max = 4
        self.is_boss = True
        self.current_atk_bonus = 1.0
        self.current_shield_bonus = 3

    def skill_tooltip(self):
        return f"スキル 1 : {self.skill1_description}\nクールダウン : {self.skill1_cooldown} 行動\n\nスキル 2 : {self.skill2_description}\nクールダウン : {self.skill2_cooldown} 行動\n\nスキル 3 : {self.skill3_description}\n"

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
                a.apply_effect(StatsEffect('攻撃力増加', 8, True, {'atk' : 1.0 + self.get_atk_bonus(), 'acc' : 0.1, 'penetration' : 0.1}))
            self.current_atk_bonus -= 0.33
        else:
            for a in self.ally:
                a.apply_effect(StatsEffect('攻撃力増加', 8, True, {'acc' : 0.1, 'penetration' : 0.1}))
        return 0

    def skill2_logic(self):
        if self.get_shield_bonus() > 0:
            def fun_after_heal(self, target, healing, overhealing):
                target.apply_effect(AbsorptionShield('シールド', 8, True, self.get_shield_bonus() * self.atk, False))
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
                if not ally.has_effect_that_named('プライド'):
                    ally.apply_effect(StatsEffect('プライド', 8, True, {'atk' : 1.45}))
        super().status_effects_at_end_of_turn()



# ====================================
# End of Early Game Powercreep
# ====================================
# Late Game Powercreep
# ====================================
        





# ====================================
# End of Late Game Powercreep
# ====================================