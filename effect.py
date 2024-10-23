from abc import abstractmethod
from collections import Counter
import random
import global_vars


class Effect:
    def __init__(self, name, duration, is_buff, cc_immunity=False, delay_trigger=0, is_set_effect=False, 
                 tooltip_str=None, tooltip_str_jp=None, can_be_removed_by_skill=True, show_stacks=False):
        self.name = name
        self.duration = duration
        self.is_buff = bool(is_buff)
        self.cc_immunity = bool(cc_immunity)
        self.delay_trigger = delay_trigger # number of turns before effect is triggered
        self.flag_for_remove = False # If True, will be removed at the beginning of the next turn.
        self.secondary_name = None
        self.is_set_effect = is_set_effect
        self.sort_priority = 1000 # The lower the number, the higher the priority.
        # priority 100-199 is used by Protected Effect.
        # priority 200-299 is used by Shield related effects.
        # priority 1800-1999 is reserved for special effects.
        # Equipments have priority 2000-2200.
        self.stacks = 1 
        self.apply_rule = "default" # "default", "stack"
        self.is_cc_effect = False
        self.tooltip_str = tooltip_str
        self.tooltip_str_jp = tooltip_str_jp
        self.can_be_removed_by_skill = can_be_removed_by_skill
        self.show_stacks = show_stacks
        self.is_protected_effect = False
    
    def is_permanent(self):
        return self.duration == -1
    
    def is_expired(self):
        return self.duration == 0
    
    def decrease_duration(self):
        if self.duration > 0:
            self.duration -= 1
    
    def apply_effect_on_apply(self, character):
        pass
    
    def apply_effect_on_turn(self, character):
        self.delay_trigger = max(self.delay_trigger - 1, 0)
        if self.delay_trigger == 0:
            self.apply_effect_on_trigger(character)

    def apply_effect_on_trigger(self, character):
        pass

    def apply_effect_at_end_of_turn(self, character):
        # This method is usually used for effects that need to toggle flag_for_remove on.
        # As effect is removed at the beginning of the next turn.
        pass

    def apply_effect_after_damage_record(self, character):
        # Please DO NOT trigger and damage related effect in this process.
        pass

    def apply_effect_when_adding_stacks(self, character, stats_income):
        pass

    def apply_effect_on_expire(self, character):
        pass
    
    def apply_effect_on_remove(self, character):
        pass

    def apply_effect_in_attack_before_damage_step(self, character, target, final_damage):
        return final_damage

    def apply_effect_during_damage_step(self, character, damage, attacker, which_ds, **keywords):
        """
        Triggers when character with this effect is about to take damage.
        Include both damage step and status damage step.
        """
        return damage

    def apply_effect_after_damage_step(self, character, damage, attacker):
        """
        Only include damage step, does not include status damage step.
        """
        pass

    def apply_effect_after_status_damage_step(self, character, damage, attacker):
        """
        Only include status damage step, does not include damage step.
        Not implemented in Character class.
        """
        pass

    def apply_effect_during_heal_step(self, character, heal_value, healer, overheal_value):
        return heal_value

    def apply_effect_after_heal_step(self, character, heal_value):
        pass


    def __str__(self):
        return self.name

    def translate_key(self, key):
        translations = {
            "maxhp": "最大HP",
            "hp": "HP",
            "atk": "攻撃力",
            "defense": "防御力",
            "spd": "速度",
            "eva": "回避",
            "acc": "命中",
            "crit": "クリティカル",
            "critdmg": "クリティカルダメージ",
            "critdef": "クリティカル防御",
            "penetration": "貫通",
            "heal efficiency": "回復効率",
            "final damage taken multipler": "最終ダメージ倍率"
        }
        return translations.get(key, key)

    def print_stats_html(self):
        color_buff = "#659a00"
        color_debuff = "#ff0000"
        string_unremovable = ""
        if not self.can_be_removed_by_skill or self.is_set_effect:
            string_unremovable += ": Unremovable"
        if self.is_buff:
            if self.duration == -1:
                string = "<font color=" + color_buff + ">" + self.name + ": Permanent" + string_unremovable + "</font>" + "\n"
            else:
                string = "<font color=" + color_buff + ">" + self.name + ": " + str(self.duration) + " turn(s)" + string_unremovable + "</font>" + "\n"
        else:
            if self.duration == -1:
                string = "<font color=" + color_debuff + ">" + self.name + ": Permanent" + string_unremovable + "</font>" + "\n"
            else:
                string = "<font color=" + color_debuff + ">" + self.name + ": " + str(self.duration) + " turn(s)" + string_unremovable + "</font>" + "\n"
        if self.cc_immunity:
            string += "Grants CC immunity. "
        if self.delay_trigger > 0:
            string += "Trigger in " + str(self.delay_trigger) + " turn(s) "
        if self.show_stacks:
            string += "Currently has " + str(self.stacks) + " stack(s) "
        string += self.tooltip_description()
        return string
    
    def print_stats_html_jp(self):
        color_buff = "#659a00"
        color_debuff = "#ff0000"
        string_unremovable = ""
        if not self.can_be_removed_by_skill or self.is_set_effect:
            string_unremovable += ":解除不可"
        if self.is_buff:
            if self.duration == -1:
                string = "<font color=" + color_buff + ">" + self.name + ":永続" + string_unremovable + "</font>" + "\n"
            else:
                string = "<font color=" + color_buff + ">" + self.name + ":" + str(self.duration) + "ターン" + string_unremovable + "</font>" + "\n"
        else:
            if self.duration == -1:
                string = "<font color=" + color_debuff + ">" + self.name + ":永続" + string_unremovable + "</font>" + "\n"
            else:
                string = "<font color=" + color_debuff + ">" + self.name + ":" + str(self.duration) + "ターン" + string_unremovable + "</font>" + "\n"
        if self.cc_immunity:
            string += "CC無効。"
        if self.delay_trigger > 0:
            string += str(self.delay_trigger) + "ターン後に発動。"
        if self.show_stacks:
            string += "現在のスタック数:" + str(self.stacks)
        if hasattr(self, "tooltip_description_jp"):
            s = self.tooltip_description_jp()
            es = self.tooltip_description()
            if s == "説明なし。" and es != "No description available.":
                string += es
            else:
                if s is not None:
                    string += s
                else:
                    string += es

        else:
            string += self.tooltip_description()
        return string


    def tooltip_description(self):
        if self.tooltip_str:
            return self.tooltip_str
        else:
            return "No description available."

    def tooltip_description_jp(self):
        if self.tooltip_str_jp:
            return self.tooltip_str_jp
        else:
            return "説明なし。"



# =========================================================
# Protected effects
# =========================================================

# Protected effect
# When a protected character is about to take damage, that damage is taken by the protector instead. Does not apply to status damage.
class ProtectedEffect(Effect):
    def __init__(self, name, duration, is_buff, cc_immunity=False, protector=None, damage_after_reduction_multiplier=1.0, 
                 damage_redirect_percentage=1.0):
        super().__init__(name, duration, is_buff, cc_immunity=False)
        self.cc_immunity = cc_immunity
        self.protector = protector
        self.damage_after_reduction_multiplier = damage_after_reduction_multiplier
        self.damage_redirect_percentage = damage_redirect_percentage
        self.sort_priority = self.calculate_sort_priority()
        self.is_protected_effect = True

    def calculate_sort_priority(self):
        return int(100 + self.damage_redirect_percentage * 99)

    def protected_apply_effect_during_damage_step(self, character, damage, attacker, func_after_dmg):
        if self.protector is None:
            raise Exception
        if damage == 0:
            return 0
        if self.protector.is_alive():
            new_damage = damage * self.damage_after_reduction_multiplier
            redirect_damage = new_damage * self.damage_redirect_percentage

            self.protector.take_damage(redirect_damage, attacker, func_after_dmg, disable_protected_effect=True)
            return new_damage - redirect_damage
        else:
            return damage
    
    def apply_effect_on_trigger(self, character):
        if self.protector not in character.ally or self.protector.is_dead():
            character.remove_effect(self)

    def apply_effect_at_end_of_turn(self, character):
        if self.protector.is_dead():
            character.remove_effect(self)

    def tooltip_description(self):
        reduction_info = f"Damage reduction: {(1 - self.damage_after_reduction_multiplier) * 100:.1f}%."
        redirect_info = f"{self.damage_redirect_percentage * 100}% of the damage is redirected."
        return f"Protected by {self.protector.name}. {reduction_info} {redirect_info}"
    
    def tooltip_description_jp(self):
        reduction_info = f"ダメージ軽減:{(1 - self.damage_after_reduction_multiplier) * 100:.1f}%。"
        redirect_info = f"ダメージの{self.damage_redirect_percentage * 100:.1f}%が引き受けてくれる。"
        return f"{self.protector.name}に保護されている。{reduction_info}{redirect_info}"


# =========================================================
# End of Protected effects
# Various Shield effects
# =========================================================

class AbsorptionShield(Effect):
    """
    Absorb [shield_value] amount of damage.
    """
    def __init__(self, name, duration, is_buff, shield_value, cc_immunity):
        super().__init__(name, duration, is_buff, cc_immunity=False)
        self.shield_value = shield_value
        self.is_buff = is_buff
        self.cc_immunity = cc_immunity
        self.sort_priority = 299

    def apply_effect_during_damage_step(self, character, damage, attacker, which_ds, **keywords):
        if damage > self.shield_value:
            remaining_damage = damage - self.shield_value
            global_vars.turn_info_string += f"{character.name}'s shield is broken! {remaining_damage} damage is dealt to {character.name}.\n"
            character.remove_effect(self)
            return remaining_damage
        else:
            self.shield_value -= damage
            global_vars.turn_info_string += f"{character.name}'s shield absorbs {damage} damage.\nRemaining shield: {self.shield_value}\n"
            return 0
        
    def tooltip_description(self):
        return f"Absorbs up to {self.shield_value:.1f} damage."
    
    def tooltip_description_jp(self):
        return f"{self.shield_value:.1f}ダメージを吸収する。"

#---------------------------------------------------------

class ReductionShield(Effect):
    """
    Reduction Shield and Damage Amplify effect, reduces/increase damage taken by [effect_value]*100%, 
    if the condition function of [requirement] is met.
    [damage_function] takes character, attacker, damage 3 arguments -> damage, if specified, after [effect_value] calculation,
    further calculate damage.
    """
    def __init__(self, name, duration, is_buff, effect_value, cc_immunity, *, requirement=None, 
                 requirement_description=None, requirement_description_jp=None, damage_function=None, 
                 cover_status_damage=True, cover_normal_damage=True):
        super().__init__(name, duration, is_buff, cc_immunity=False)
        self.is_buff = is_buff
        self.effect_value = effect_value
        self.cc_immunity = cc_immunity
        self.requirement = requirement
        self.requirement_description = requirement_description
        self.requirement_description_jp = requirement_description_jp
        self.sort_priority = 200
        self.damage_function = damage_function
        self.cover_status_damage = cover_status_damage
        self.cover_normal_damage = cover_normal_damage


    def apply_effect_during_damage_step(self, character, damage, attacker, which_ds, **keywords):
        prev_damage = damage
        if self.requirement is not None:
            if not attacker:
                global_vars.turn_info_string += f"{self.name} could not be triggered on {character.name}, attacker not found.\n"
                return damage
            elif not self.requirement(character, attacker):
                global_vars.turn_info_string += f"{self.name} could not be triggered on {character.name}, requirement not met.\n"
                return damage
        if self.is_buff:
            if self.cover_normal_damage and which_ds == "normal":
                damage = damage * (1 - self.effect_value)
            elif self.cover_status_damage and which_ds == "status":
                damage = damage * (1 - self.effect_value)
        else:
            if self.cover_normal_damage and which_ds == "normal":
                damage = damage * (1 + self.effect_value)
            elif self.cover_status_damage and which_ds == "status":
                damage = damage * (1 + self.effect_value)
        if self.damage_function:
            damage = self.damage_function(character, attacker, damage)
        delta = abs(damage - prev_damage)
        if delta != 0:
            if self.is_buff:
                global_vars.turn_info_string += f"Damage is reduced by {delta:.1f} by {self.name}.\n"
            else:
                global_vars.turn_info_string += f"Damage is increased by {delta:.1f} by {self.name}.\n"
        return damage
    
    def tooltip_description(self):
        str = ""
        if self.effect_value > 0:
            if self.is_buff:
                str += f"Reduces damage taken by {self.effect_value*100}%."
                if self.cover_normal_damage and self.cover_status_damage:
                    str += " Applies to all damage."
                elif self.cover_normal_damage:
                    str += " Applies to normal damage."
                elif self.cover_status_damage:
                    str += " Applies to status damage."
            else:
                str += f"Increases damage taken by {self.effect_value*100}%."
                if self.cover_normal_damage and self.cover_status_damage:
                    str += " Applies to all damage."
                elif self.cover_normal_damage:
                    str += " Applies to normal damage."
                elif self.cover_status_damage:
                    str += " Applies to status damage."
        elif self.damage_function:
            str += f" Damage reduction is further calculated by a function."
        if self.requirement_description is not None:
            str += f" Requirement: {self.requirement_description}"
        return str
    
    def tooltip_description_jp(self):
        str = ""
        if self.effect_value > 0:
            if self.is_buff:
                str += f"受けるダメージを{self.effect_value*100:.1f}%軽減。"
                if self.cover_normal_damage and self.cover_status_damage:
                    str += "全てのダメージに適用。"
                elif self.cover_normal_damage:
                    str += "通常ダメージに適用。"
                elif self.cover_status_damage:
                    str += "状態異常ダメージに適用。"
            else:
                str += f"受けるダメージを{self.effect_value*100:.1f}%増加。"
                if self.cover_normal_damage and self.cover_status_damage:
                    str += "全てのダメージに適用。"
                elif self.cover_normal_damage:
                    str += "通常ダメージに適用。"
                elif self.cover_status_damage:
                    str += "状態異常ダメージに適用。"
        elif self.damage_function:
            str += f"ダメージ軽減は関数によってさらに計算される。"
        if self.requirement_description_jp is not None:
            str += f"条件:{self.requirement_description_jp}"
        return str
    

#---------------------------------------------------------


class AntiMultiStrikeReductionShield(Effect):
    """
    AntiMultiStrikeReductionShield is an effect that reduces or increases the damage taken by a certain percentage.
    The effect is applied multiplicatively each time the character is damaged within the same turn.
    This means that the damage reduction (or increase) becomes stronger with each subsequent attack in the same turn.

    For example, if the effect reduces damage by 20% (effect_value = 0.2), and the character is attacked three times in the same turn,
    the damage taken from each attack will be multiplied by 0.8^n, where n is the number of times the character has been attacked.
    So the third attack would have its damage reduced by 1 - (0.8^3) = 48.8%.

    Parameters:
        name (str): The name of the effect.
        duration (int): The duration of the effect in turns.
        is_buff (bool): True if the effect is a buff (reduces damage), False if it's a debuff (increases damage).
        effect_value (float): The percentage reduction/increase per attack (as a decimal, e.g., 0.2 for 20%).
        cc_immunity (bool): Whether the effect grants crowd control immunity.
        requirement (callable, optional): A function that takes (character, attacker) and returns True if the effect should be applied.
        requirement_description (str, optional): A description of the requirement for the effect.
    """

    def __init__(self, name, duration, is_buff, effect_value, cc_immunity, *, requirement=None, 
                 requirement_description=None, effect_value_increase_per_attack=0):
        super().__init__(name, duration, is_buff, cc_immunity=False)
        self.is_buff = is_buff
        self.effect_value = effect_value
        self.cc_immunity = cc_immunity
        self.requirement = requirement
        self.requirement_description = requirement_description
        self.sort_priority = 200
        self.how_many_times_triggered_this_turn = 1
        self.character_current_turn = 0
        self.effect_value_increase_per_attack = effect_value_increase_per_attack

    def apply_effect_during_damage_step(self, character, damage, attacker, which_ds, **keywords):
        if self.requirement is not None:
            if not attacker:
                global_vars.turn_info_string += f"The effect of {self.name} could not be triggered on {character.name}, attacker not found.\n"
                return damage
            elif not self.requirement(character, attacker):
                global_vars.turn_info_string += f"The effect of {self.name} could not be triggered on {character.name}, requirement not met.\n"
                return damage
        if self.character_current_turn != character.battle_turns:
            self.character_current_turn = character.battle_turns
            self.how_many_times_triggered_this_turn = 1
        else:
            self.how_many_times_triggered_this_turn += 1
        reduction_value = self.effect_value + self.effect_value_increase_per_attack * (self.how_many_times_triggered_this_turn - 1)
        if self.is_buff:
            for i in range(self.how_many_times_triggered_this_turn):
                damage = damage * (1 - reduction_value)
        else:
            for i in range(self.how_many_times_triggered_this_turn):
                damage = damage * (1 + reduction_value)
        return damage

    def tooltip_description(self):
        description = ""
        if self.effect_value > 0:
            percentage = self.effect_value * 100
            if self.is_buff:
                description += f"Reduces damage taken by {percentage}% multiplicatively for each attack received in the same turn."
                if self.effect_value_increase_per_attack > 0:
                    description += f" Reduction increases by {self.effect_value_increase_per_attack * 100}% per attack."
            else:
                description += f"Increases damage taken by {percentage}% multiplicatively for each attack received in the same turn."
                if self.effect_value_increase_per_attack > 0:
                    description += f" Damage increases by {self.effect_value_increase_per_attack * 100}% per attack."
        if self.requirement_description is not None:
            description += f" Requirement: {self.requirement_description}"
        return description
    
    def tooltip_description_jp(self):
        description = ""
        if self.effect_value > 0:
            percentage = self.effect_value * 100
            if self.is_buff:
                description += f"同じターンに受けるダメージを{percentage}%ずつ減少させる。"
                if self.effect_value_increase_per_attack > 0:
                    description += f"ダメージ軽減は{self.effect_value_increase_per_attack * 100}%ずつ増加する。"
            else:
                description += f"同じターンに受けるダメージを{percentage}%ずつ増加させる。"
                if self.effect_value_increase_per_attack > 0:
                    description += f"ダメージ増加は{self.effect_value_increase_per_attack * 100}%ずつ増加する。"
        if self.requirement_description is not None:
            description += f"条件:{self.requirement_description}"
        return description







#---------------------------------------------------------
class EffectShield1(Effect):
    """
    Before damage calculation, if character hp is below [hp_threshold]*100%, heal hp for [heal_function] amount before damage calculation.
    """
    def __init__(self, name, duration, is_buff, hp_threshold, heal_function, cc_immunity,
                require_above_zero_dmg=False, effect_applier=None, cover_status_damage=False, cover_normal_damage=True,
                cancel_damage=False):
        super().__init__(name, duration, is_buff, cc_immunity=False)
        self.is_buff = is_buff
        self.hp_threshold = hp_threshold
        self.heal_function = heal_function
        self.cc_immunity = cc_immunity
        self.sort_priority = 200
        self.require_above_zero_dmg = require_above_zero_dmg
        self.effect_applier = effect_applier
        self.cover_status_damage = cover_status_damage
        self.cover_normal_damage = cover_normal_damage
        self.cancel_damage = cancel_damage

    def apply_effect_at_end_of_turn(self, character):
        if self.effect_applier.is_dead():
            self.flag_for_remove = True

    def apply_effect_during_damage_step(self, character, damage, attacker, which_ds, **keywords):
        if character.hp < character.maxhp * self.hp_threshold and (not self.require_above_zero_dmg or damage > 0):
            if self.cover_normal_damage and which_ds == "normal":
                character.heal_hp(self.heal_function(self.effect_applier), self.effect_applier)
                if self.cancel_damage:
                    return 0
            elif self.cover_status_damage and which_ds == "status":
                character.heal_hp(self.heal_function(self.effect_applier), self.effect_applier)
                if self.cancel_damage:
                    return 0
        return damage
    
    def tooltip_description(self):
        description = f"When HP is below {self.hp_threshold*100:.1f}%, heal for {self.heal_function(self.effect_applier):.1f} HP before damage calculation."
        
        # Determine which types of damage the effect applies to
        if self.cover_normal_damage and self.cover_status_damage:
            description += " Applies to all damage."
        else:
            if self.cover_normal_damage:
                description += " Applies to normal damage."
            if self.cover_status_damage:
                description += " Applies to status damage."
        
        # Include whether the effect cancels incoming damage
        if self.cancel_damage:
            description += " Incoming damage is canceled."
        
        # Include if the effect requires the incoming damage to be above zero
        if self.require_above_zero_dmg:
            description += " Only triggers if incoming damage is above zero."
        
        return description

    def tooltip_description_jp(self):
        description = f"HPが{self.hp_threshold*100:.1f}%未満の時、ダメージ計算前に{self.heal_function(self.effect_applier):.1f}回復する。"
        
        # Determine which types of damage the effect applies to
        if self.cover_normal_damage and self.cover_status_damage:
            description += "全てのダメージに適用。"
        else:
            if self.cover_normal_damage:
                description += "通常ダメージに適用。"
            if self.cover_status_damage:
                description += "状態異常ダメージに適用。"
        
        # Include whether the effect cancels incoming damage
        if self.cancel_damage:
            description += "受けるダメージを無効化。"
        
        # Include if the effect requires the incoming damage to be above zero
        if self.require_above_zero_dmg:
            description += "受けるダメージがゼロ以上の時のみ発動。"
        
        return description



#---------------------------------------------------------
class EffectShield1_healoncrit(Effect):
    """
    Before damage calculation, if character takes crit damage, heal hp for [heal_function] amount before damage calculation.
    """
    def __init__(self, name, duration, is_buff, hp_threshold, heal_function, cc_immunity, effect_applier,
                require_above_zero_dmg=False, critdmg_reduction=0):
        super().__init__(name, duration, is_buff, cc_immunity=False)
        self.is_buff = is_buff
        self.hp_threshold = hp_threshold
        self.heal_function = heal_function
        self.cc_immunity = cc_immunity
        self.sort_priority = 200
        self.require_above_zero_dmg = require_above_zero_dmg
        self.effect_applier = effect_applier
        self.critdmg_reduction = critdmg_reduction

    def apply_effect_at_end_of_turn(self, character):
        if self.effect_applier.is_dead():
            self.flag_for_remove = True

    def apply_effect_during_damage_step(self, character, damage, attacker, which_ds, **keywords):
        # check if the damage is crit damage, access with keywords['attack_is_crit']
        crit_condition = keywords.get('attack_is_crit', False) and keywords["attack_is_crit"]
        if crit_condition and (not self.require_above_zero_dmg or damage > 0) and character.hp < character.maxhp * self.hp_threshold:
            if character.is_alive():
                a,b,c = character.heal_hp(self.heal_function(self.effect_applier), self.effect_applier)
            else:
                print(f"Waring: {character.name} is dead when applying heal on {self.name}.")
            if self.critdmg_reduction > 0:
                damage = damage * (1 - self.critdmg_reduction)
        return damage
    
    def tooltip_description(self):
        s = f"When taking critical damage, heal for {self.heal_function(self.effect_applier):.1f} hp before damage calculation."
        if self.critdmg_reduction > 0:
            s += f" Reduces critical damage taken by {self.critdmg_reduction*100:.1f}%."
        return s

    def tooltip_description_jp(self):
        s = f"クリティカルダメージを受けた時、ダメージ計算前に{self.heal_function(self.effect_applier):.1f}回復する。"
        if self.critdmg_reduction > 0:
            s += f"受けるクリティカルダメージを{self.critdmg_reduction*100:.1f}%減少する。"
        return s


#---------------------------------------------------------
class EffectShield2(Effect):
    """
    When taking damage that would exceed [hp_threshold]*100% of maxhp, reduce the part of excessive damage by [damage_reduction]*100%. 
    For every turn passed, damage reduction effect is reduced by [shrink_rate]*100%.
    If [damage_reflect_function] is specified, reflect damage to the attacker.
    Damage coming from reflect can not be reflected again.
    The max reflect damage cannot exceed character maxhp*[max_reflect_hp_percentage] 
    """
    def __init__(self, name, duration, is_buff, cc_immunity, damage_reduction=0.5, 
                 shrink_rate=0.02, hp_threshold=0.1, damage_reflect_function=None, 
                 damage_reflect_description=None, damage_reflect_description_jp=None,
                 max_reflect_hp_percentage=1):
        super().__init__(name, duration, is_buff, cc_immunity=False)
        self.is_buff = is_buff
        self.cc_immunity = cc_immunity
        self.damage_reduction = damage_reduction
        self.shrink_rate = shrink_rate
        self.sort_priority = 201
        self.hp_threshold = hp_threshold
        self.damage_reflect_function = damage_reflect_function
        self.damage_reflect_description = damage_reflect_description
        self.damage_reflect_description_jp = damage_reflect_description_jp
        self.max_reflect_hp_percentage = max_reflect_hp_percentage

    def apply_effect_during_damage_step(self, character, damage, attacker, which_ds, **keywords):
        damage_original = damage
        damage_threshold = character.maxhp * self.hp_threshold
        if damage > damage_threshold:
            damage = damage_threshold + (damage - damage_threshold) * (1 - self.damage_reduction)

        delta = abs(damage_original - damage)

        if delta != 0:
            global_vars.turn_info_string += f"{self.name} reduced {delta:.1f} damage for {character.name}.\n"

        # make no sense to reflect status damage.
        if which_ds != "normal":
            return damage

        if self.damage_reflect_function and delta > 0:
            damage_to_reflect = self.damage_reflect_function(delta)
            damage_to_reflect = min(damage_to_reflect, character.maxhp * self.max_reflect_hp_percentage)
            # If this is true, we know it is coming from reflect damage, so no reflect is allowed.
            is_reflect_damage_condition = keywords.get('damage_is_reflect', False) and keywords["damage_is_reflect"]
            # not reflect damage:
            if not is_reflect_damage_condition:
                # print(f"{character.name} reflects {damage_to_reflect} damage to {attacker.name}.")
                if attacker is not None:
                    attacker.take_status_damage(damage_to_reflect, character, is_reflect=True)
        return damage
    
    def apply_effect_on_trigger(self, character):
        self.damage_reduction = max(self.damage_reduction - self.shrink_rate, 0)
        if self.damage_reduction == 0:
            self.flag_for_remove = True

    def tooltip_description(self):
        str = f"Reduces damage exceeding {self.hp_threshold*100:.1f}% of max HP by {self.damage_reduction*100:.1f}%. "
        if self.shrink_rate > 0:
            str += f"Each turn, the damage reduction decreases by {self.shrink_rate*100:.1f}%. "
        if self.damage_reflect_description:
            str += self.damage_reflect_description
        return str

    def tooltip_description_jp(self):
        str = f"最大HPの{self.hp_threshold*100:.1f}%を超えるダメージを{self.damage_reduction*100:.1f}%減少させる。"
        if self.shrink_rate > 0:
            str += f"毎ターン、ダメージ軽減が{self.shrink_rate*100:.1f}%減少する。"
        if self.damage_reflect_description_jp:
            str += self.damage_reflect_description_jp
        return str


class DamageReflect(Effect):
    """
    Reflect [reflect_percentage]*100% of the damage taken to the attacker.
    """
    def __init__(self, name, duration, is_buff, cc_immunity, reflect_percentage=0.5):
        super().__init__(name, duration, is_buff, cc_immunity=False)
        self.is_buff = is_buff
        self.cc_immunity = cc_immunity
        self.reflect_percentage = reflect_percentage
        self.sort_priority = 202

    def apply_effect_during_damage_step(self, character, damage, attacker, which_ds, **keywords):
        if which_ds != "normal":
            return damage
        damage_to_reflect = damage * self.reflect_percentage
        if attacker is not None and damage_to_reflect > 0:
            attacker.take_status_damage(damage_to_reflect, character, is_reflect=True)
        return damage

    def tooltip_description(self):
        return f"Reflects {self.reflect_percentage*100:.1f}% of the damage taken back to the attacker."

    def tooltip_description_jp(self):
        return f"受けたダメージの{self.reflect_percentage*100:.1f}%を攻撃者に反射する。"


class ResolveEffect(Effect):
    """
    When taking damage, if damage exceed current hp, it is reduced to current hp - [hp_to_leave].
    """
    def __init__(self, name, duration, is_buff, cc_immunity, hp_to_leave=1, 
                    cover_status_damage=False, cover_normal_damage=True, same_turn_usage="unlimited"):
        super().__init__(name, duration, is_buff, cc_immunity=False)
        self.is_buff = is_buff
        self.cc_immunity = cc_immunity
        self.sort_priority = 203
        self.hp_to_leave = hp_to_leave
        self.cover_status_damage = cover_status_damage
        self.cover_normal_damage = cover_normal_damage
        self.same_turn_usage = same_turn_usage
        self.how_many_times_triggered_this_turn = 1
        self.character_current_turn = 0

    def apply_effect_during_damage_step(self, character, damage, attacker, which_ds, **keywords):
        if damage > character.hp and self.same_turn_usage == "unlimited":
            if self.cover_normal_damage and which_ds == "normal":
                return character.hp - self.hp_to_leave
            elif self.cover_status_damage and which_ds == "status":
                return character.hp - self.hp_to_leave
        elif damage > character.hp and type(self.same_turn_usage) == int:
            if self.character_current_turn != character.battle_turns:
                self.character_current_turn = character.battle_turns
                self.how_many_times_triggered_this_turn = 1
            else:
                self.how_many_times_triggered_this_turn += 1
            if self.how_many_times_triggered_this_turn <= self.same_turn_usage:
                if self.cover_normal_damage and which_ds == "normal":
                    return character.hp - self.hp_to_leave
                elif self.cover_status_damage and which_ds == "status":
                    return character.hp - self.hp_to_leave

    def tooltip_description(self):
        s = f"When taking damage that exceeds current HP, the damage is reduced so that HP becomes {self.hp_to_leave}."
        if self.cover_normal_damage and self.cover_status_damage:
            s += " Applies to all damage."
        elif self.cover_normal_damage:
            s += " Applies to normal damage."
        elif self.cover_status_damage:
            s += " Applies to status damage."
        if type(self.same_turn_usage) == int:
            s += f" Can be triggered {self.same_turn_usage} times per turn."
        return s
    
    def tooltip_description_jp(self):
        s = f"受けたダメージが現在のHPを上回る場合、ダメージがHPを{self.hp_to_leave}に残るように軽減される。"
        if self.cover_normal_damage and self.cover_status_damage:
            s += "全てのダメージに適用。"
        elif self.cover_normal_damage:
            s += "通常ダメージに適用。"
        elif self.cover_status_damage:
            s += "状態異常ダメージに適用。"
        if type(self.same_turn_usage) == int:
            s += f"1ターンに{self.same_turn_usage}回まで発動可能。"
        return s


class DecayEffect(Effect):
    """
    when healing hp, take damage in the next turn instead.
    """
    def __init__(self, name, duration, is_buff, effect_applier):
        super().__init__(name, duration, is_buff)
        self.effect_applier = effect_applier
        self.apply_rule = "stack" # Make no sense to have 2 decay effect on the same character.
        self.healing_accumulated = 0

    def apply_effect_on_trigger(self, character):
        damage_value = self.healing_accumulated
        global_vars.turn_info_string += f"Decay strikes! {character.name} suffers {damage_value} damage.\n"
        character.take_status_damage(damage_value, self.effect_applier)
        self.healing_accumulated = 0

    def apply_effect_during_heal_step(self, character, heal_value, healer, overheal_value):
        self.healing_accumulated += heal_value
        return 0
        
    def tooltip_description(self):
        return "When being healed, take the healing amount as status damage in the next turn."
    
    def tooltip_description_jp(self):
        return "回復を受けると、回復を無効し、次のターンに回復量の状態異常ダメージを受ける。"





#---------------------------------------------------------
class CancellationShield(Effect):
    """
    Cancel the damage to 0 if damage exceed character maxhp * [threshold], 
    provide [uses] times of uses,
    if [cancel_excessive_instead], cancel out the part of damage that exceed character maxhp * [threshold],
    if [cancel_below_instead], cancel out the part of damage below character maxhp * [threshold].

    """
    def __init__(self, name, duration, is_buff, threshold, cc_immunity, uses=1, cancel_excessive_instead=False, 
                 cancel_below_instead=False, remove_this_effect_when_use_is_zero=True,
                 cover_status_damage=True, cover_normal_damage=True):
        super().__init__(name, duration, is_buff, cc_immunity=False)
        self.is_buff = is_buff
        self.threshold = threshold
        self.cc_immunity = cc_immunity
        self.sort_priority = 250
        self.uses = uses
        self.cancel_excessive_instead = cancel_excessive_instead
        self.cancel_below_instead = cancel_below_instead
        self.remove_this_effect_when_use_is_zero = remove_this_effect_when_use_is_zero
        self.cover_status_damage = cover_status_damage
        self.cover_normal_damage = cover_normal_damage

    def apply_effect_during_damage_step(self, character, damage, attacker, which_ds, **keywords):
        if not self.remove_this_effect_when_use_is_zero and self.uses == 0:
            return damage
        if damage > character.maxhp * self.threshold:
            used = False

            if self.cancel_excessive_instead:
                if self.cover_normal_damage and which_ds == "normal":
                    damage = character.maxhp * self.threshold
                    used = True
                elif self.cover_status_damage and which_ds == "status":
                    damage = character.maxhp * self.threshold
                    used = True
                
            if self.cancel_below_instead:
                if self.cover_normal_damage and which_ds == "normal":
                    damage = damage - character.maxhp * self.threshold
                    used = True
                elif self.cover_status_damage and which_ds == "status":
                    damage = damage - character.maxhp * self.threshold
                    used = True

            if not self.cancel_below_instead and not self.cancel_excessive_instead:
                if self.cover_normal_damage and which_ds == "normal":
                    damage = 0
                    used = True

                elif self.cover_status_damage and which_ds == "status":
                    damage = 0
                    used = True

            if used:
                global_vars.turn_info_string += f"{character.name} shielded the attack!\n"
                self.uses -= 1
                if self.uses == 0 and self.remove_this_effect_when_use_is_zero:
                    character.remove_effect(self)
                elif self.uses < 0:
                    # raise Exception(f"Logic Error: {self.name} uses is negative. Character: {character.name}, attacker: {attacker.name}")
                    # This may happen on recursion. Take a close look at Character.take_damage() method, 
                    # effects are copied but during apply_effect_during_damage_step process damage may trigger.
                    character.remove_effect(self)


            return damage
        else:
            return damage
        
    def tooltip_description(self):
        string = f"Cancel attack {str(self.uses)} times if damage exceed {self.threshold*100}% of max hp."
        if self.cancel_excessive_instead:
            string += " Cancel the excessive damage."
        if self.cancel_below_instead:
            string += " Cancel the damage below."
        if self.cover_normal_damage and self.cover_status_damage:
            string += " Applies to all damage."
        elif self.cover_normal_damage:
            string += " Applies to normal damage."
        elif self.cover_status_damage:
            string += " Applies to status damage."
        return string

    def tooltip_description_jp(self):
        string = f"最大HPの{self.threshold*100:.1f}%を超えるダメージを{str(self.uses)}回まで無効化する。"
        if self.cancel_excessive_instead:
            string += "超過ダメージを無効化る。"
        if self.cancel_below_instead:
            string += "未満ダメージを無効化する。"
        if self.cover_normal_damage and self.cover_status_damage:
            string += "全てのダメージに適用。"
        elif self.cover_normal_damage:
            string += "通常ダメージに適用。"
        elif self.cover_status_damage:
            string += "状態異常ダメージに適用。"
        return string



class RenkaEffect(Effect):
    """
    Renka has 15 stacks, each time when taking lethal damage, consume 1 stack, cancel the damage and recover 15% hp.
    When taking damage, reduce damage taken by 20% + 5% for each stack.
    """
    def __init__(self, name, duration, is_buff, cc_immunity, hp_recover_percentage=0.12, damage_reduction=0.06, stacks=15,
                 damage_reduction_per_stack=0.04):
        super().__init__(name, duration, is_buff, cc_immunity=False)
        self.is_buff = is_buff
        self.cc_immunity = cc_immunity
        self.hp_recover_percentage = hp_recover_percentage
        self.damage_reduction = damage_reduction
        self.sort_priority = 299
        self.stacks = stacks
        self.damage_reduction_per_stack = damage_reduction_per_stack

    def apply_effect_on_trigger(self, character):
        if self.stacks == 0:
            character.remove_effect(self)

    def apply_effect_during_damage_step(self, character, damage, attacker, which_ds, **keywords):
        if damage > character.hp:
            if self.stacks > 0:
                self.stacks -= 1
                character.heal_hp(character.maxhp * self.hp_recover_percentage, character)
                global_vars.turn_info_string += f"{character.name} Renka effect cancelled the damage and recovered {self.hp_recover_percentage*100:.1f}% hp.\n"
                return 0
            else:
                # No stacks left, remove the effect.
                character.remove_effect(self)
                return damage
        else:
            red = self.damage_reduction + self.stacks * self.damage_reduction_per_stack
            return damage * (1 - red)
    
    def tooltip_description(self):
        return f"Renka effect: When taking lethal damage, consume 1 stack, cancel the damage and recover {self.hp_recover_percentage*100:.1f}% hp. " \
        f"When taking damage, reduce damage taken by {self.damage_reduction*100:.1f}% + {self.stacks * self.damage_reduction_per_stack*100:.1f}%. " \
        f"Currently has {self.stacks} stack(s)."
    
    def tooltip_description_jp(self):
        return f"「連花」効果:致命的なダメージを受けた時、スタックを1消費し、ダメージを無効化し、HPを{self.hp_recover_percentage*100:.1f}%回復する。" \
        f"ダメージを受けた時、ダメージを{self.damage_reduction*100:.1f}%+{self.stacks * self.damage_reduction_per_stack*100:.1f}%軽減する。" \
        f"現在のスタック数:{self.stacks}。"



# =========================================================
# End of Various Shield effects
# =========================================================
# CC effects
# =========================================================
    
class StunEffect(Effect):
    def __init__(self, name, duration, is_buff, cc_immunity=False, delay_trigger=0):
        super().__init__(name, duration, is_buff, cc_immunity=False, delay_trigger=0)
        self.name = "Stun"
        self.is_buff = False
        self.cc_immunity = cc_immunity
        self.delay_trigger = delay_trigger
        self.apply_rule = "stack"
        self.is_cc_effect = True
    
    def apply_effect_on_apply(self, character):
        stats_dict = {"eva": -1.00}
        character.update_stats(stats_dict, reversed=False) # Eva can be lower than 0, which makes sense.

    def apply_effect_on_remove(self, character):
        stats_dict = {"eva": 1.00}
        character.update_stats(stats_dict, reversed=False)
    
    def tooltip_description(self):
        return "Cannot take action and evasion is reduced by 100%."
    
    def tooltip_description_jp(self):
        return "行動不可、回避率が100%減少。"

    
class FrozenEffect(Effect):
    def __init__(self, name, duration, is_buff, imposter, cc_immunity=False, delay_trigger=0):
        super().__init__(name, duration, is_buff)
        self.name = "Frozen"
        self.is_buff = False
        self.imposter = imposter
        self.cc_immunity = cc_immunity
        self.delay_trigger = delay_trigger
        self.apply_rule = "stack"
        self.is_cc_effect = True
    
    def apply_effect_on_apply(self, character):
        stats_dict = {"eva": -1.00}
        character.update_stats(stats_dict, reversed=False) # Eva can be lower than 0, which makes sense.

    def apply_effect_during_damage_step(self, character, damage, attacker, which_ds, **keywords):
        match which_ds:
            case "normal":
                return damage * 0.2
            case "status":
                return damage * 2.0
            case _:
                raise Exception("Invalid damage step.")

    def apply_effect_on_trigger(self, character):
        if character.is_dead():
            return
        character.take_status_damage(0.01 * character.maxhp, self.imposter)

    def apply_effect_on_remove(self, character):
        stats_dict = {"eva": 1.00}
        character.update_stats(stats_dict, reversed=False)
    
    def tooltip_description(self):
        return "Cannot take action and evasion is reduced by 100%, normal damage taken is reduced by 80%." \
        " Status damage taken is increased by 100%. Each turn, take status damage equal to 1% of max hp."


class PetrifyEffect(Effect):
    def __init__(self, name, duration, is_buff, imposter, delay_trigger=0):
        super().__init__(name, duration, is_buff)
        self.name = "Petrify"
        self.is_buff = False
        self.imposter = imposter
        self.cc_immunity = True
        self.delay_trigger = delay_trigger
        self.apply_rule = "stack"
        self.is_cc_effect = True
    
    def apply_effect_on_apply(self, character):
        stats_dict = {"eva": -1.00}
        character.update_stats(stats_dict, reversed=False) # Eva can be lower than 0, which makes sense.

    def apply_effect_during_damage_step(self, character, damage, attacker, which_ds, **keywords):
        match which_ds:
            case "normal":
                return damage * 2.0
            case "status":
                return 0
            case _:
                raise Exception("Invalid damage step.")

    def apply_effect_on_remove(self, character):
        stats_dict = {"eva": 1.00}
        character.update_stats(stats_dict, reversed=False)
    
    def tooltip_description(self):
        return "Cannot take action and evasion is reduced by 100%." \
        " Immune to status damage, normal damage taken is increased by 100%."


class SilenceEffect(Effect):
    def __init__(self, name, duration, is_buff, cc_immunity=False, delay_trigger=0):
        super().__init__(name, duration, is_buff)
        self.name = "Silence"
        self.is_buff = False
        self.cc_immunity = cc_immunity
        self.delay_trigger = delay_trigger
        self.apply_rule = "stack"
        self.is_cc_effect = True
    
    def tooltip_description(self):
        return "Cannot use skill."
    
    def tooltip_description_jp(self):
        return "スキルが使用不可。"


class SleepEffect(Effect):
    def __init__(self, name, duration, is_buff, cc_immunity=False, delay_trigger=0):
        super().__init__(name, duration, is_buff)
        self.name = "Sleep"
        self.is_buff = False
        self.cc_immunity = cc_immunity
        self.delay_trigger = delay_trigger
        self.apply_rule = "stack"
        self.is_cc_effect = True
    
    def apply_effect_during_damage_step(self, character, damage, attacker, which_ds, **keywords):
        character.remove_effect(self)
        return damage

    def apply_effect_on_apply(self, character):
        stats_dict = {"eva": -1.00}
        character.update_stats(stats_dict, reversed=False) # Eva can be lower than 0, which makes sense.

    def apply_effect_on_remove(self, character):
        stats_dict = {"eva": 1.00}
        character.update_stats(stats_dict, reversed=False)

    def tooltip_description(self):
        return "Cannot act, effect is removed when taking damage, evasion is reduced by 100%."
    
    def tooltip_description_jp(self):
        return "行動不可、ダメージを受けると解除される、回避率が100%減少。"


class ConfuseEffect(Effect):
    def __init__(self, name, duration, is_buff, cc_immunity=False, delay_trigger=0):
        super().__init__(name, duration, is_buff)
        self.name = "Confuse"
        self.is_buff = False
        self.cc_immunity = cc_immunity
        self.delay_trigger = delay_trigger
        self.apply_rule = "stack"
        self.is_cc_effect = True
    
    def tooltip_description(self):
        return "Target random ally or enemy."
    
    def tooltip_description_jp(self):
        return "ランダムな味方または敵をターゲットする。"



class CharmEffect(Effect):
    def __init__(self, name, duration, is_buff, cc_immunity=False, delay_trigger=0):
        super().__init__(name, duration, is_buff)
        self.name = "Charm"
        self.is_buff = False
        self.cc_immunity = cc_immunity
        self.delay_trigger = delay_trigger
        self.apply_rule = "stack"
        self.is_cc_effect = True
    
    def tooltip_description(self):
        return "Enemy is ally, ally is enemy."
    
    def tooltip_description_jp(self):
        return "敵は味方、味方は敵。"



# Fear effect
# This effect is dynamic, the actual effect is determined by character.enemy.
# If a enemy in character.enemy has attribue "fear_effect_dict", update self.stats_dict to that dict.
# If the key is same, the value will be added.
# Effects that update stats dynamically should use this as a template.
class FearEffect(Effect):
    def __init__(self, name, duration, is_buff, cc_immunity=False, delay_trigger=0):
        super().__init__(name, duration, is_buff)
        self.name = "Fear"
        self.is_buff = False
        self.cc_immunity = cc_immunity
        self.delay_trigger = delay_trigger
        self.apply_rule = "stack"
        self.is_cc_effect = True
        self.stats_dict = {}

    def stats_dict_function(self, character):
        stats_dict = {}
        for enemy in character.enemy:
            if hasattr(enemy, "fear_effect_dict"):
                for key, value in enemy.fear_effect_dict.items():
                    if key in stats_dict:
                        stats_dict[key] += value
                    else:
                        stats_dict[key] = value
        return stats_dict

    def apply_effect_on_remove(self, character):
        character.update_stats(self.stats_dict, reversed=True)

    def apply_effect_on_trigger(self, character):
        old_stats_dict = self.stats_dict
        new_stats_dict = self.stats_dict_function(character)
        if old_stats_dict and new_stats_dict: # Both are not empty
            if new_stats_dict != old_stats_dict:
                character.update_stats(old_stats_dict, reversed=True)
                self.stats_dict = new_stats_dict
                character.update_stats(self.stats_dict, reversed=False)
        elif old_stats_dict and not new_stats_dict: # old_stats_dict is not empty, new_stats_dict is empty
            character.update_stats(old_stats_dict, reversed=True)
            self.stats_dict = new_stats_dict
        elif not old_stats_dict and new_stats_dict: # old_stats_dict is empty, new_stats_dict is not empty
            character.update_stats(new_stats_dict, reversed=False)
            self.stats_dict = new_stats_dict
        else: # Both are empty
            return

    def tooltip_description(self):
        str = "Consumed by fear.\n"
        if not self.stats_dict:
            return str + "Currently have no effect."
        for key, value in self.stats_dict.items():
            if key in ["maxhp", "hp", "atk", "defense", "spd"]:
                str += f"{key} is scaled to {value*100:.2f}%."
            else:
                if value > 0:
                    str += f"{key} is increased by {value*100}%."
                else:
                    str += f"{key} is decreased by {-value*100}%."
        return str
    
    def tooltip_description_jp(self):
        str = "恐怖に取り憑かれた。\n"
        if not self.stats_dict:
            return str + "現在効果なし。"
        for key, value in self.stats_dict.items():
            if key in ["maxhp", "hp", "atk", "defense", "spd"]:
                key = self.translate_key(key)
                str += f"{key}が{value*100:.2f}%に調整される。"
            else:
                if value > 0:
                    key = self.translate_key(key)
                    str += f"{key}が{value*100}%増加する。"
                else:
                    key = self.translate_key(key)
                    str += f"{key}が{-value*100}%減少する。"
        return str
    

# =========================================================
# End of CC effects
# =========================================================
# Stats effects
# =========================================================


class StatsEffect(Effect):
    def __init__(self, name, duration, is_buff, stats_dict=None, condition=None, use_active_flag=True, 
                 stats_dict_function=None, is_set_effect=False, can_be_removed_by_skill=True,
                 main_stats_additive_dict=None):
        """
        [condition] function takes character as argument. if specified, this effect will trigger a stats update every turn, 
        use it with True [use_active_flag]: for example, increase atk by 20% if hp < 50%,
        use it with False [use_active_flag]: for example, every turn, increase critdmg by 1% if hp < 50%.
        [stats_dict_function] need [condition] and False [use_active_flag] (makes no sense to use the flag), 
        called when condition is met, revert the old stats and update with the new stats if anything changed.
        [main_stats_additive_dict] is a dictionary containing main stats, for example {'hp': 200, 'atk: 40'}, this dict is added to additive_main_stats
        of Character class on effect apply, and removed on effect removal. I do not want to implement a dynamic dict for this because it will be complex.
        """
        super().__init__(name, duration, is_buff, cc_immunity=False, delay_trigger=0)
        self.stats_dict = stats_dict
        self.condition = condition
        self.flag_is_active = False
        self.use_active_flag = use_active_flag
        self.stats_dict_function = stats_dict_function
        if self.stats_dict_function:
            if (not condition) or use_active_flag:
                raise Exception("stats_dict_function can only be used when condition func is provided and use_active_flag are False.")
            self.stats_dict = self.stats_dict_function()
        self.is_set_effect = is_set_effect
        self.can_be_removed_by_skill = can_be_removed_by_skill
        self.main_stats_additive_dict = main_stats_additive_dict

    def apply_effect_on_apply(self, character):
        if self.condition is None or self.condition(character):
            if self.main_stats_additive_dict:
                new_dict = {**self.main_stats_additive_dict, **{'effect_pointer': self}}
                character.additive_main_stats.append(new_dict)
                character.update_main_stats_additive(effect_pointer=self)

            if self.stats_dict:
                character.update_stats(self.stats_dict, reversed=False)
            self.flag_is_active = True

    def apply_effect_on_remove(self, character):
        if self.condition is None or self.condition(character):
            if self.main_stats_additive_dict:
                # find the dict in character.additive_main_stats which effect_pointer matchs self. Give exception if not found.
                matching_dict = None
                for dict_record in character.additive_main_stats:
                    if dict_record.get('effect_pointer') == self:
                        matching_dict = dict_record
                        break
                if matching_dict is None:
                    raise Exception("Effect not found in character's additive_main_stats.")

                character.update_main_stats_additive(reversed=True, effect_pointer=self)
                character.additive_main_stats.remove(matching_dict)

            if self.stats_dict:
                character.update_stats(self.stats_dict, reversed=True)

    def apply_effect_on_trigger(self, character):
        if self.condition is not None and self.use_active_flag:
            if self.condition(character) and self.flag_is_active == False:
                character.update_stats(self.stats_dict, reversed=False)
                self.flag_is_active = True
            elif self.condition(character) and self.flag_is_active == True:
                return
            elif not self.condition(character) and self.flag_is_active == False:
                return
            elif not self.condition(character) and self.flag_is_active == True:
                character.update_stats(self.stats_dict, reversed=True)
                self.flag_is_active = False
                return
            else:
                raise RuntimeError("Logic Error")
        elif self.condition is not None and not self.use_active_flag:
            if self.condition(character):
                if self.stats_dict_function is not None:
                    old_stats_dict = self.stats_dict
                    new_stats_dict = self.stats_dict_function()
                    # Only when stats_dict is changed, will we update stats.
                    if new_stats_dict != old_stats_dict:
                        character.update_stats(old_stats_dict, reversed=True)
                        self.stats_dict = new_stats_dict
                        character.update_stats(self.stats_dict, reversed=False)
                else:
                    character.update_stats(self.stats_dict, reversed=False)
            else:
                return
        else:
            # condition is None, will not do anything.
            return

    def tooltip_description(self):
        string = ""
        if self.condition is not None:
            if self.condition:
                string += "Effect is active."
            else:
                string += "Effect is not active."
            if self.use_active_flag:
                string += " When active,"
            else:
                string += " Every turn when active,"
        if self.stats_dict:
            for key, value in self.stats_dict.items():
                if key in ["maxhp", "hp", "atk", "defense", "spd"]:
                    string += f"{key} is scaled to {value*100:.2f}%."
                else:
                    processed_key = key.replace("_", " ")
                    if value > 0:
                        string += f"{processed_key} is increased by {value*100:.2f}%."
                    else:
                        string += f"{processed_key} is decreased by {-value*100:.2f}%."
        if self.main_stats_additive_dict:
            for key, value in self.main_stats_additive_dict.items():
                if key in ["maxhp", "hp", "atk", "defense", "spd"]:
                    if value > 0:
                        string += f"{key} is increased by {value}."
                    else:
                        string += f"{key} is decreased by {value}."
        return string
    
    def tooltip_description_jp(self):
        string = ""
        if self.condition is not None:
            if self.condition:
                string += "効果が発動中です。"
            else:
                string += "効果が発動していません。"
            if self.use_active_flag:
                string += "発動中は、"
            else:
                string += "各ターンで発動中は、"
        if self.stats_dict:
            for key, value in self.stats_dict.items():
                if key in ["maxhp", "hp", "atk", "defense", "spd"]:
                    japanese_key = self.translate_key(key)
                    string += f"{japanese_key}が{value*100:.2f}%に調整される。"
                else:
                    processed_key = key.replace("_", " ")
                    processed_key = self.translate_key(processed_key)
                    if value > 0:
                        string += f"{processed_key}が{value*100:.2f}%増加する。"
                    else:
                        string += f"{processed_key}が{-value*100:.2f}%減少する。"
        if self.main_stats_additive_dict:
            for key, value in self.main_stats_additive_dict.items():
                japanese_key = self.translate_key(key)
                if key in ["maxhp", "hp", "atk", "defense", "spd"]:
                    if value > 0:
                        string += f"{japanese_key}が{value}増加する。"
                    else:
                        string += f"{japanese_key}が{value}減少する。"
        return string


# =========================================================
# End of Stats effects
# =========================================================
# Timed bomb effects
# Effect that trigger events when expired.
# =========================================================


class TimedBombEffect(Effect):
    def __init__(self, name, duration, is_buff, damage, imposter, cc_immunity, new_effect=None):
        """
        character takes [damage] status damage when expired.
        then, add a [new_effect] effect to the character if specified.
        """
        super().__init__(name, duration, is_buff)
        self.damage = damage
        self.imposter = imposter
        self.cc_immunity = cc_immunity
        self.new_effect = new_effect

    def apply_effect_on_expire(self, character):
        if character.is_alive() and self.damage > 0:
            character.take_status_damage(self.damage, self.imposter)
        if self.new_effect:
            if character.is_alive():
                character.apply_effect(self.new_effect)

    def tooltip_description(self):
        if self.new_effect is None:
            return f"Take {int(self.damage)} status damage when expired."
        else:
            return f"Take {int(self.damage)} status damage when expired. {self.new_effect.name} effect is applied after damage."
        
    def tooltip_description_jp(self):
        if self.new_effect is None:
            return f"効果終了時に{int(self.damage)}の状態異常ダメージを受ける。"
        else:
            return f"効果終了時に{int(self.damage)}の状態異常ダメージを受ける。ダメージ後、{self.new_effect.name}効果が適用される。"


# =========================================================
# End of Timed bomb effects
# =========================================================
# Continuous Damage/Healing effects
# =========================================================

class ContinuousHealEffect(Effect):
    """
    heal hp returned by [value_function] each turn. [value_function] takes (character, buff_applier) as arguments and returns a value.
    """
    def __init__(self, name, duration, is_buff, value_function, buff_applier=None, value_function_description=None,
                 value_function_description_jp=None):
        super().__init__(name, duration, is_buff)
        self.is_buff = is_buff
        self.value_function = value_function
        self.buff_applier = buff_applier
        self.value_function_description = value_function_description
        self.value_function_description_jp = value_function_description_jp
    
    def apply_effect_on_trigger(self, character):
        amount_to_heal = self.value_function(character, self.buff_applier)
        if character.is_alive():
            character.heal_hp(amount_to_heal, self.buff_applier)
    
    def tooltip_description(self):
        return f"Recovers hp each turn, amount: {self.value_function_description}."
    
    def tooltip_description_jp(self):
        if self.value_function_description_jp:
            return f"毎ターンHPを回復する。回復量:{self.value_function_description_jp}。"
        else:
            return f"毎ターンHPを回復する。回復量:{self.value_function_description}。"


class ContinuousDamageEffect(Effect):
    """
    This effect is used by too many, I won't change the arguments for now. Only new arguments are added. 
    take [value] status damage each turn. [imposter] is the character that applies this effect.
    if [remove_by_heal] is True, this effect will be removed when character is healed.
    [damage_type] can be "status", "bypass", "normal".
    """
    def __init__(self, name, duration, is_buff, value, imposter, remove_by_heal=False,
                 damage_type="status"):
        super().__init__(name, duration, is_buff)
        self.value = float(value)
        self.is_buff = is_buff
        self.imposter = imposter # The character that applies this effect
        self.remove_by_heal = remove_by_heal
        self.damage_type = damage_type
        self.how_many_times_this_effect_is_triggered_lifetime = 0
    
    def apply_effect_on_trigger(self, character):
        match self.damage_type:
            case "status":
                character.take_status_damage(self.value, self.imposter)
            case "bypass":
                character.take_bypass_status_effect_damage(self.value, self.imposter)
            case "normal":
                character.take_damage(self.value, self.imposter)
            case _:
                raise Exception(f"Invalid damage type: {self.damage_type} in ContinuousDamageEffect.")
        self.how_many_times_this_effect_is_triggered_lifetime += 1
    
    def apply_effect_after_heal_step(self, character, heal_value):
        if self.remove_by_heal:
            global_vars.turn_info_string += f"{character.name}'s {self.name} is removed by heal.\n"
            character.remove_effect(self)

    def tooltip_description(self):
        s = f"Take {(self.value):.2f} {self.damage_type} damage each turn."
        if self.remove_by_heal:
            s += " This effect can be removed by healing."
        return s
    
    def tooltip_description_jp(self):
        damage_type_dict = {
            "status": "状態異常",
            "bypass": "状態異常無視",
            "normal": "通常"
        }
        damage_type = damage_type_dict.get(self.damage_type, self.damage_type)
        s = f"毎ターン{(self.value):.2f}{damage_type}ダメージを受ける。"
        if self.remove_by_heal:
            s += "この効果は回復によって解除できる。"
        return s


class ContinuousDamageEffect_Poison(Effect):
    """
    A variant of ContinuousDamageEffect, takes a proportion of characters [base] * [value] as status damage each turn.
    [base]: "maxhp", "hp", "losthp", value should be renamed as ratio. 
    if [remove_by_heal] is True, this effect will be removed when character is healed.
    [damage_type] can be "status", "bypass". 
    if [is_plague], transmit the same effect to a neighbor ally at the end of turn with [is_plague_transmission_chance*100]% chance.
    """
    def __init__(self, name, duration, is_buff, ratio, imposter, base: str, remove_by_heal=False, 
                 damage_type="status", is_plague=False, is_plague_transmission_chance=0.0,
                 is_plague_transmission_decay=0):
        super().__init__(name, duration, is_buff)
        self.ratio = float(ratio)
        self.is_buff = is_buff
        self.imposter = imposter # The character that applies this effect
        self.base = base # "maxhp", "hp", "losthp"
        self.remove_by_heal = remove_by_heal
        self.damage_type = damage_type
        self.is_plague = is_plague
        self.is_plague_transmission_chance = is_plague_transmission_chance
        self.is_plague_transmission_decay = is_plague_transmission_decay
    
    def apply_effect_on_trigger(self, character):
        if character.is_dead():
            return
        match self.base:
            # Stupid code but works.
            case "maxhp":
                if self.damage_type == "status":
                    character.take_status_damage(self.ratio * character.maxhp, self.imposter)
                elif self.damage_type == "bypass":
                    character.take_bypass_status_effect_damage(self.ratio * character.maxhp, self.imposter)
                else:
                    raise Exception("Invalid damage type.")
            case "hp":
                if self.damage_type == "status":
                    character.take_status_damage(self.ratio * character.hp, self.imposter)
                elif self.damage_type == "bypass":
                    character.take_bypass_status_effect_damage(self.ratio * character.hp, self.imposter)
                else:
                    raise Exception("Invalid damage type.")
            case "losthp":
                if self.damage_type == "status":
                    character.take_status_damage(self.ratio * (character.maxhp - character.hp), self.imposter)
                elif self.damage_type == "bypass":
                    character.take_bypass_status_effect_damage(self.ratio * (character.maxhp - character.hp), self.imposter)
                else:
                    raise Exception("Invalid damage type.")
            case _:
                raise Exception("Invalid base.")
    
    def apply_effect_after_heal_step(self, character, heal_value):
        if self.remove_by_heal:
            global_vars.turn_info_string += f"{character.name}'s {self.name} is removed by heal.\n"
            character.remove_effect(self)

    def apply_effect_at_end_of_turn(self, character):
        # NOTE: Because we are applying the same effect, if this effect is modified in place, the effect will be modified for all characters.
        # But this is probably how plagues work.
        if not self.is_plague:
            super().apply_effect_at_end_of_turn(character)
        else:
            t = character.get_neighbor_allies_not_including_self()
            if t:
                a = random.choice(t)
                # if a.is_dead():
                #     raise Exception("Logic Error")
                # Actually, plague can be transmitted to dead bodies.
                if a.has_effect_that_is(self):
                    return
                if random.random() < self.is_plague_transmission_chance:
                    self.is_plague_transmission_chance = max(0, self.is_plague_transmission_chance - self.is_plague_transmission_decay)
                    a.apply_effect(self)

    def tooltip_description(self):
        s = f"Take {(self.ratio*100):.2f}% {self.base} damage each turn."
        if self.remove_by_heal:
            s += " This effect can be removed by healing."
        if self.is_plague:
            s += f" At end of turn, {int(self.is_plague_transmission_chance*100)}% chance to apply the same effect to a neighbor ally."
        return s

    def tooltip_description_jp(self):
        base_dict = {
            "maxhp": "最大HP",
            "hp": "現在のHP",
            "losthp": "失ったHP"
        }
        base = base_dict.get(self.base, self.base)
        s = f"毎ターン{(self.ratio*100):.2f}%の{base}に応じたダメージを受ける。"
        if self.remove_by_heal:
            s += "この効果は回復されると解除される。"
        if self.is_plague:
            s += f"ターン終了時に、{int(self.is_plague_transmission_chance*100)}%の確率で隣接する味方に同じ効果が伝染する。"
        return s


# =========================================================
# End of Continuous Damage/Healing effects
# =========================================================
# =========================================================
# Special effects
# Effects in this section need special handling, or does not seem to fit into any other category.
# =========================================================


class NewYearFireworksEffect(Effect):
    """
    This effect is written on 2024 New Year's Eve.
    have 6 counters. Every turn, throw a dice, counter decreases by the dice number.
    When counter reaches 0, deal 600% of applier atk as damage to self.
    At the end of the turn, this effect is applied to a random enemy.
    """
    def __init__(self, name, duration, is_buff, max_counters, imposter):
        super().__init__(name, duration, is_buff)
        self.name = name
        self.is_buff = is_buff
        self.max_counters = max_counters
        self.current_counters = max_counters
        self.imposter = imposter
        self.should_trigger_end_of_turn_effect = True # We only want to trigger once per end of turn.
    
    def apply_effect_on_trigger(self, character):
        self.should_trigger_end_of_turn_effect = True
        number = character.fake_dice()
        self.current_counters -= number
        self.current_counters = max(self.current_counters, 0)
        if character.is_dead():
            character.remove_effect(self)
            return
        if self.current_counters == 0:
            damage = self.imposter.atk * 6
            global_vars.turn_info_string += f"{character.name} is about to take {int(damage)} damage from fireworks!\n"
            character.take_status_damage(damage, self.imposter)
            character.remove_effect(self)

    def apply_effect_at_end_of_turn(self, character):
        if not self.should_trigger_end_of_turn_effect:
            return
        available_enemies = character.enemy
        if not available_enemies:
            character.remove_effect(self)
        else:
            target = next(character.target_selection())
            new_effect = NewYearFireworksEffect(self.name, self.duration, self.is_buff, self.max_counters, self.imposter)
            new_effect.current_counters = self.current_counters
            new_effect.should_trigger_end_of_turn_effect = False
            target.apply_effect(new_effect)
            character.remove_effect(self)

    def tooltip_description(self):
        return f"Happy New Year! Get ready for some fireworks! The fireworks currently has {self.current_counters} counters." 
    
    def tooltip_description_jp(self):
        return f"あけましておめでとうございます！花火をお楽しみください！現在のカウンター数:{self.current_counters}。"


class RebornEffect(Effect):
    """
    revive with [effect_value*100]% hp the turn after defeated.
    """
    def __init__(self, name, duration, is_buff, effect_value, cc_immunity, buff_applier, effect_value_constant=0):
        super().__init__(name, duration, is_buff, cc_immunity=False)
        self.is_buff = is_buff
        self.effect_value = effect_value
        self.cc_immunity = cc_immunity
        self.buff_applier = buff_applier
        self.effect_value_constant = effect_value_constant
    
    def apply_effect_on_trigger(self, character):
        if character.is_dead():
            character.revive(self.effect_value_constant, self.effect_value, self.buff_applier)
            if hasattr(character, "after_revive"):
                character.after_revive()
            character.remove_effect(self)

    def tooltip_description(self):
        return f"Revive with {self.effect_value*100}% + {self.effect_value_constant} hp the next turn after fallen."
    
    def tooltip_description_jp(self):
        return f"倒れた次のターンに{self.effect_value*100}% + {self.effect_value_constant}HPで復活する。"


class StingEffect(Effect):
    """
    every time target take damage, take [value] status damage.
    """
    def __init__(self, name, duration, is_buff, value, imposter):
        super().__init__(name, duration, is_buff)
        self.name = name
        self.is_buff = is_buff
        self.value = value
        self.imposter = imposter

    def apply_effect_after_damage_step(self, character, damage, attacker):
        character.take_status_damage(self.value, self.imposter)

    def tooltip_description(self):
        return f"Take {self.value} status damage every time after taking damage."
    
    def tooltip_description_jp(self):
        return f"ダメージを受けた後、{self.value}の状態異常ダメージを受ける。"
    

class HideEffect(Effect):
    """
    cannot be targeted by enemy. Unless for n_random_targets and n_random_enemies where n >= 5.
    """
    def __init__(self, name, duration, is_buff, cc_immunity=False, remove_on_damage=False, effect_apply_to_character_on_remove: Effect=None):
        super().__init__(name, duration, is_buff, cc_immunity=False)
        self.name = "Hide"
        self.is_buff = is_buff
        self.cc_immunity = cc_immunity
        self.sort_priority = 2000
        self.is_active = True
        self.remove_on_damage = remove_on_damage
        self.effect_apply_to_character_on_remove = effect_apply_to_character_on_remove

    def apply_effect_on_trigger(self, character):
        if character.is_dead():
            character.remove_effect(self)
            return
        character.update_ally_and_enemy()
        all_allies_hidden_check = all([m.has_effect_that_named(self.name, None, "HideEffect") for m in character.party if m.is_alive()])
        if all_allies_hidden_check:
            global_vars.turn_info_string += f"All allies are hidden, {self.name} is no longer active.\n"
            # print(f"All allies are hidden, {self.name} is no longer active.")
            character.remove_effect(self)
        #     self.is_active = False
        # if not self.is_active:
        #     self.flag_for_remove = True
        
    def apply_effect_during_damage_step(self, character, damage, attacker, which_ds, **keywords):
        if self.remove_on_damage:
            global_vars.turn_info_string += f"{character.name} is no longer hidden!\n"
            character.remove_effect(self)
        return damage

    def apply_effect_on_remove(self, character):
        if self.effect_apply_to_character_on_remove:
            character.apply_effect(self.effect_apply_to_character_on_remove)


    def tooltip_description(self):
        string = f"Enemy attack and skill that target less than 5 enemies will not target this character. "
        string += f"Effect is no longer active when all allies are hidden and will be removed the start of the next turn. "
        if self.remove_on_damage:
            string += f"Effect is removed when taking damage."
        return string
    
    def tooltip_description_jp(self):
        string = f"5体未満の敵を対象とする攻撃やスキルはこのキャラクターを対象にできない。"
        string += f"全ての味方が隠れている場合、次のターンの開始時にこの効果は解除される。"
        if self.remove_on_damage:
            string += f"ダメージを受けると効果が解除されます。"
        return string


class SinEffect(StatsEffect):
    """
    When defeated, all allies take status damage equal to [value].
    """
    def __init__(self, name, duration, is_buff, value, stats_dict, applier):
        super().__init__(name, duration, is_buff, stats_dict)
        self.value = value
        self.sort_priority = 2000
        self.can_be_removed_by_skill = False
        self.applier = applier

    def apply_effect_on_trigger(self, character):
        if character.is_dead():
            for ally in character.ally:
                if ally.is_dead():
                    continue
                ally.take_status_damage(self.value, self.applier)
            global_vars.turn_info_string += f"{character.name} has been defeated!\n"
            character.remove_effect(self)
        return super().apply_effect_on_trigger(character)

    def apply_effect_at_end_of_turn(self, character):
        if character.is_dead():
            for ally in character.ally:
                if ally.is_dead():
                    continue
                ally.take_status_damage(self.value, self.applier)
            global_vars.turn_info_string += f"{character.name} has been defeated!\n"
            character.remove_effect(self)
        return super().apply_effect_at_end_of_turn(character)

    def tooltip_description(self):
        string = super().tooltip_description()
        return string + f"When defeated, all allies take status damage equal to {self.value}."
    
    def tooltip_description_jp(self):
        string = super().tooltip_description_jp()
        return string + f"倒された場合、全ての味方に{self.value}の状態異常ダメージを与える。"


class NotTakingDamageEffect(Effect):
    """
    On [require_turns_without_damage] turns without taking damage, apply a Effect to character.
    """
    def __init__(self, name, duration, is_buff, require_turns_without_damage, effect_to_apply: Effect):
        super().__init__(name, duration, is_buff)
        self.require_turns_without_damage = require_turns_without_damage
        self.effect_to_apply = effect_to_apply

    def apply_effect_after_damage_record(self, character):
        if character.is_dead():
            return
        twd = character.get_num_of_turns_not_taken_damage()
        if twd >= self.require_turns_without_damage:
            character.apply_effect(self.effect_to_apply)

    def tooltip_description(self):
        return f"Apply {self.effect_to_apply.name} effect after {self.require_turns_without_damage} turns without taking damage."
    
    def tooltip_description_jp(self):
        return f"{self.require_turns_without_damage}ターン攻撃を受けていないと{self.effect_to_apply.name}効果が付与される。"



# =========================================================
# End of Special effects
# Effects in the above section need special handling.
# =========================================================
#---------------------------------------------------------
# Equipment set effects
#---------------------------------------------------------
# Arasaka
# Leave with 1 hp when taking fatal damage. Immune to damage for 3 turns.
class EquipmentSetEffect_Arasaka(Effect):
    def __init__(self, name, duration, is_buff, cc_immunity):
        super().__init__(name, duration, is_buff, cc_immunity=False)
        self.is_buff = is_buff
        self.cc_immunity = cc_immunity
        self.is_set_effect = True
        self.onehp_effect_triggered = False
        self.sort_priority = 2000

    def apply_effect_during_damage_step(self, character, damage, attacker, which_ds, **keywords):
        if self.onehp_effect_triggered:
            return 0
        if damage >= character.hp:
            character.hp = 1
            global_vars.turn_info_string += f"{character.name} survived with 1 hp!\n"
            self.onehp_effect_triggered = True
            self.duration = 6
            return 0
        else:
            return damage

    def tooltip_description(self):
        return f"Leave with 1 hp when taking fatal damage."
    
    def tooltip_description_jp(self):
        return f"致命的なダメージを受けたとき、1HPで生き残る。"


#---------------------------------------------------------
# KangTao
class EquipmentSetEffect_KangTao(Effect):
    def __init__(self, name, duration, is_buff, shield_value, cc_immunity):
        super().__init__(name, duration, is_buff, cc_immunity=False)
        self.shield_value = shield_value
        self.is_buff = is_buff
        self.cc_immunity = cc_immunity
        self.is_set_effect = True
        self.sort_priority = 2000

    def apply_effect_during_damage_step(self, character, damage, attacker, which_ds, **keywords):
        if damage > self.shield_value:
            remaining_damage = damage - self.shield_value
            global_vars.turn_info_string += f"{character.name}'s shield is broken!\n{remaining_damage} damage is dealt to {character.name}.\n"
            character.remove_effect(self)
            return remaining_damage
        else:
            self.shield_value -= damage
            global_vars.turn_info_string += f"{character.name}'s shield absorbs {damage} damage.\nRemaining shield: {self.shield_value}\n"  
            return 0
        
    def tooltip_description(self):
        return f"Shield that absorbs up to {self.shield_value} damage."
    
    def tooltip_description_jp(self):
        return f"{self.shield_value}ダメージを吸収する。"
    

#---------------------------------------------------------
# Militech
# Increase speed by 100% when hp falls below 20%.
class EquipmentSetEffect_Militech(Effect):
    def __init__(self, name, duration, is_buff, stats_dict=None, condition=None):
        super().__init__(name, duration, is_buff, cc_immunity=False, delay_trigger=0)
        self.is_set_effect = True
        self.stats_dict = stats_dict
        self.condition = condition
        self.flag_is_active = False
        self.sort_priority = 2000

    def apply_effect_on_trigger(self, character):
        if self.condition is not None:
            if self.condition(character) and not self.flag_is_active:
                character.update_stats(self.stats_dict, reversed=False)
                self.flag_is_active = True
            elif self.condition(character) and self.flag_is_active:
                return
            elif not self.condition(character) and not self.flag_is_active:
                return
            elif not self.condition(character) and self.flag_is_active:
                character.update_stats(self.stats_dict, reversed=True)
                self.flag_is_active = False
                return
            else:
                raise RuntimeError("Logic Error")
        else:
            # condition is None, will not do anything.
            return

    def tooltip_description(self):
        string = ""
        if self.condition is not None:
            if self.flag_is_active:
                string += "Effect is active. "
            else:
                string += "Effect is not active. "
        for key, value in self.stats_dict.items():
            if key in ["maxhp", "hp", "atk", "defense", "spd"]:
                string += f"{key} is scaled to {value*100:.2f}% on condition."
            else:
                string += f"{key} is increased by {value*100:.2f}% on condition."
        return string
    
    def tooltip_description_jp(self):
        string = ""
        if self.condition is not None:
            if self.flag_is_active:
                string += "効果が発動中。"
            else:
                string += "効果が発動していない。"
        for key, value in self.stats_dict.items():
            if key in ["maxhp", "hp", "atk", "defense", "spd"]:
                key_jp = self.translate_key(key)
                string += f"{key_jp}が{value*100:.2f}%に調整される。"
            else:
                key_jp = self.translate_key(key)
                string += f"{key_jp}が{value*100:.2f}%増加する。"
        return string


#---------------------------------------------------------
# NUSA
# Increase atk by 6%, def by 6%, and maxhp by 6% for each ally alive including self.
class EquipmentSetEffect_NUSA(Effect):
    def __init__(self, name, duration, is_buff, stats_dict=None, stats_dict_function=None):
        super().__init__(name, duration, is_buff, cc_immunity=False, delay_trigger=0)
        self.is_set_effect = True
        self.stats_dict = stats_dict
        self.flag_is_active = False
        self.stats_dict_function = stats_dict_function
        self.sort_priority = 2000

    def apply_effect_on_apply(self, character):
        # if self.stats_dict_function:
        #     self.stats_dict = self.stats_dict_function()
        # We do not call the function here, because in this specific case, character.ally() just got reset and is empty.
        character.update_stats(self.stats_dict, reversed=False)

    def apply_effect_on_remove(self, character):
        character.update_stats(self.stats_dict, reversed=True)

    def apply_effect_on_trigger(self, character):
        old_stats_dict = self.stats_dict
        new_stats_dict = self.stats_dict_function()
        if new_stats_dict != old_stats_dict:
            character.update_stats(old_stats_dict, reversed=True)
            self.stats_dict = new_stats_dict
            character.update_stats(self.stats_dict, reversed=False)

    def tooltip_description(self):
        string = ""
        for key, value in self.stats_dict.items():
            if key in ["maxhp", "hp", "atk", "defense", "spd"]:
                string += f"{key} is scaled to {value*100:.2f}%."
            else:
                string += f"{key} is increased by {value*100:.2f}%."
        return string
    
    def tooltip_description_jp(self):
        string = ""
        for key, value in self.stats_dict.items():
            if key in ["maxhp", "hp", "atk", "defense", "spd"]:
                japanese_key = self.translate_key(key)
                string += f"{japanese_key}が{value*100:.2f}%に調整される。"
            else:
                processed_key = key.replace("_", " ")
                processed_key = self.translate_key(processed_key)
                if value > 0:
                    string += f"{processed_key}が{value*100:.2f}%増加する。"
                else:
                    string += f"{processed_key}が{-value*100:.2f}%減少する。"
        return string


#---------------------------------------------------------
# Sovereign
# Apply Sovereign effect when taking damage, Sovereign increases atk by 20% and last 4 turns. Max 5 active effects.
class EquipmentSetEffect_Sovereign(Effect):
    def __init__(self, name, duration, is_buff, stats_dict=None, stats_dict_function=None):
        super().__init__(name, duration, is_buff, cc_immunity=False, delay_trigger=0)
        self.is_set_effect = True
        self.stats_dict = stats_dict
        self.flag_is_active = False
        self.stats_dict_function = stats_dict_function
        self.sort_priority = 2000

    def apply_effect_during_damage_step(self, character, damage, attacker, which_ds, **keywords):
        # count how many "Sovereign" in character.buffs, if less than 5, apply effect.
        if Counter([effect.name for effect in character.buffs])["Sovereign"] < 5:
            character.apply_effect(StatsEffect("Sovereign", 4, True, self.stats_dict, is_set_effect=True))
        return damage
    
    def tooltip_description(self):
        return f"Accumulate 1 stack of Sovereign when taking damage."

    def tooltip_description_jp(self):
        return f"ダメージを受けると主権のスタックが1つ蓄積される。"

# ---------------------------------------------------------
# Snowflake
# Gain 1 piece of Snowflake at the end of action. When 6 pieces are accumulated, heal 20% hp and gain the following effect for 6 turns:
# atk, def, maxhp, spd are increased by 20%. 
# Each activation of this effect increases the stats bonus and healing by 20%.
class EquipmentSetEffect_Snowflake(Effect):
    def __init__(self, name, duration, is_buff):
        super().__init__(name, duration, is_buff, cc_immunity=False, delay_trigger=0)
        self.is_set_effect = True
        self.collected_pieces = 0
        self.activation_count = 0
        self.bonus_stats_dict = {"atk": 1.0, "defense": 1.0, "maxhp": 1.0, "spd": 1.0}
        self.sort_priority = 2000

    def get_new_bonus_dict(self):
        new_bonus_dict = {}
        for key, value in self.bonus_stats_dict.items():
            new_bonus_dict[key] = value + self.activation_count * 0.25
        return new_bonus_dict

    def apply_effect_custom(self):
        self.collected_pieces += 1
        self.collected_pieces = min(self.collected_pieces, 6)

    def apply_effect_on_trigger(self, character):
        if character.is_dead():
            return
        if self.collected_pieces >= 6:
            self.activation_count += 1
            sf = StatsEffect("Snowflake", 6, True, self.get_new_bonus_dict(), is_set_effect=True)
            character.apply_effect(sf)
            character.heal_hp(character.maxhp * 0.25 * self.activation_count, self)
            self.collected_pieces = 0

    def tooltip_description(self):
        return f"Collected pieces: {self.collected_pieces}, Activation count: {self.activation_count}. Collect 6 pieces to activate effect."
    
    def tooltip_description_jp(self):
        return f"集めたピース:{self.collected_pieces}、発動回数:{self.activation_count}。6つのピースを集めて効果を発動する。"


# ---------------------------------------------------------
# Flute
class EquipmentSetEffect_Flute(Effect):
    def __init__(self, name, duration, is_buff):
        super().__init__(name, duration, is_buff)
        self.name = name
        self.is_buff = is_buff
        self.is_set_effect = True
        self.sort_priority = 2000

# ---------------------------------------------------------
# Rainbow
class EquipmentSetEffect_Rainbow(Effect):
    def __init__(self, name, duration, is_buff):
        super().__init__(name, duration, is_buff)
        self.name = name
        self.is_buff = is_buff
        self.is_set_effect = True
        self.sort_priority = 2000

# ---------------------------------------------------------
# Dawn
# Atk increased by 24%, crit increased by 12% when hp is full.
# One time only, when dealing damage, damage is increased by 120%.
class EquipmentSetEffect_Dawn(Effect):
    def __init__(self, name, duration, is_buff, stats_dict=None):
        super().__init__(name, duration, is_buff)
        self.is_set_effect = True
        self.stats_dict = stats_dict
        self.flag_is_active = True
        self.flag_onetime_damage_bonus_active = True
        self.sort_priority = 2000

    def apply_effect_on_apply(self, character):
        character.update_stats(self.stats_dict, reversed=False)

    def apply_effect_on_remove(self, character):
        character.update_stats(self.stats_dict, reversed=True)

    def apply_effect_on_trigger(self, character):
        if character.hp == character.maxhp and not self.flag_is_active:
            character.update_stats(self.stats_dict, reversed=False)
            self.flag_is_active = True
        elif character.hp < character.maxhp and self.flag_is_active:
            character.update_stats(self.stats_dict, reversed=True)
            self.flag_is_active = False
        else:
            return

    def tooltip_description(self):
        string = ""
        if self.flag_is_active:
            string += "Atk and crit bonus is active."
        if self.flag_onetime_damage_bonus_active:
            string += "Onetime damage bonus is active."
        if not self.flag_is_active and not self.flag_onetime_damage_bonus_active:
            string += "Effect is not active."
        return string
    
    def tooltip_description_jp(self):
        string = ""
        if self.flag_is_active:
            string += "攻撃力とクリティカルボーナスが有効です。"
        if self.flag_onetime_damage_bonus_active:
            string += "一度限りのダメージボーナスが有効です。"
        if not self.flag_is_active and not self.flag_onetime_damage_bonus_active:
            string += "効果は無効です。"
        return string

# ---------------------------------------------------------
# Bamboo
# After taking down an enemy with normal or skill attack, for 5 turns,
# regenerates 16% of max hp each turn and increases atk, def, spd by 32%
    
class EquipmentSetEffect_Bamboo(Effect):
    def __init__(self, name, duration, is_buff, stats_dict=None):
        super().__init__(name, duration, is_buff)
        self.is_set_effect = True
        self.stats_dict = stats_dict
        self.flag_is_active = False
        self.sort_priority = 2000

    def apply_effect_custom(self, character):
        if character.is_dead():
            return
        if not character.has_effect_that_named("Bamboo", additional_name="EquipmentSetEffect_Bamboo"):
            effect_to_apply = StatsEffect("Bamboo", 7, True, self.stats_dict, is_set_effect=True)
            effect_to_apply.additional_name = "EquipmentSetEffect_Bamboo"
            character.apply_effect(effect_to_apply)
            e = ContinuousHealEffect("Bamboo", 7, True, lambda x, y: x.maxhp * 0.20, self, "20% maxhp",
                                     value_function_description_jp="最大HPの20%")
            e.is_set_effect = True
            character.apply_effect(e)

# ---------------------------------------------------------
# Rose
# Heal efficiency is increased by 20%. Before heal, increase target's heal efficiency by 40% for 2 turns.
# Cannot be triggered by hp recover.
class EquipmentSetEffect_Rose(Effect):
    def __init__(self, name, duration, is_buff, he_bonus_before_heal=0.4):
        super().__init__(name, duration, is_buff)
        self.is_set_effect = True
        self.he_bonus_before_heal = he_bonus_before_heal
        self.sort_priority = 2000


# ---------------------------------------------------------
# OldRusty
# See character.py for implementation.
class EquipmentSetEffect_OldRusty(Effect):
    def __init__(self, name, duration, is_buff):
        super().__init__(name, duration, is_buff)
        self.is_set_effect = True
        self.sort_priority = 2000

# ---------------------------------------------------------
# Purplestar
# See character.py for implementation.
class EquipmentSetEffect_Purplestar(Effect):
    def __init__(self, name, duration, is_buff):
        super().__init__(name, duration, is_buff)
        self.is_set_effect = True
        self.sort_priority = 2000


# ---------------------------------------------------------
# Liquidation
# When taking damage, for each of the following stats that is lower than attacker's, damage is reduced by 30%: hp, atk, def, spd.
class EquipmentSetEffect_Liquidation(Effect):
    def __init__(self, name, duration, is_buff, damage_reduction):
        super().__init__(name, duration, is_buff)
        self.is_set_effect = True
        self.sort_priority = 2000
        self.damage_reduction = damage_reduction

    def apply_effect_during_damage_step(self, character, damage, attacker, which_ds, **keywords):
        # if damage_taken_by_protector in keywords and its True, effect is reduced by 50%.
        damage_reduction_final = self.damage_reduction
        if "damage_taken_by_protector" in keywords and keywords["damage_taken_by_protector"]:
            damage_reduction_final *= 0.5
        if damage == 0:
            return 0
        if attacker is None:
            return damage
        for key in ["hp", "atk", "defense", "spd"]:
            if getattr(character, key) < getattr(attacker, key):
                damage = damage * (1 - damage_reduction_final)
                global_vars.turn_info_string += f"{character.name}'s {key} is lower than {attacker.name}'s, damage is reduced by {int(damage_reduction_final*100)}%.\n"
        return damage

# ---------------------------------------------------------
# Newspaper
# See character.py for implementation.
class EquipmentSetEffect_Newspaper(Effect):
    def __init__(self, name, duration, is_buff):
        super().__init__(name, duration, is_buff)
        self.is_set_effect = True
        self.sort_priority = 2000

# ---------------------------------------------------------
# Freight
# See character.py for implementation.
class EquipmentSetEffect_Freight(Effect):
    def __init__(self, name, duration, is_buff):
        super().__init__(name, duration, is_buff)
        self.is_set_effect = True
        self.sort_priority = 2000

    def apply_effect_custom(self, character):
        character.heal_hp(character.spd * 0.30, character)


#---------------------------------------------------------
# End of Equipment set effects
#---------------------------------------------------------
# Character Specific Effects
#---------------------------------------------------------

class RequinaGreatPoisonEffect(Effect):
    # Great Poison effect used by Requina
    def __init__(self, name, duration, is_buff, value_onestack, stats_dict, imposter, stacks):
        super().__init__(name, duration, is_buff)
        self.name = name
        self.value_onestack = float(value_onestack)
        self.is_buff = is_buff
        self.imposter = imposter
        self.stacks = stacks
        self.stats_dict = stats_dict 
        self.stats_dict_original = stats_dict.copy()
        self.apply_rule = "stack"

    def update_stats_dict(self):
        # 0.99 , 0.98 , 0.97 , 0.96 , 0.95...for each stack.
        self.stats_dict = {key: value - (0.01 * self.stacks) for key, value in self.stats_dict_original.items()}

    def apply_effect_on_apply(self, character):
        self.update_stats_dict()
        character.update_stats(self.stats_dict, reversed=False)

    def apply_effect_on_trigger(self, character):
        character.take_status_damage(character.maxhp * self.value_onestack * self.stacks, self.imposter)
    
    def apply_effect_on_remove(self, character):
        self.update_stats_dict()
        character.update_stats(self.stats_dict, reversed=True)

    def apply_effect_when_adding_stacks(self, character, stacks_income):
        self.apply_effect_on_remove(character)
        self.stacks += stacks_income
        self.stacks = min(self.stacks, 70)
        self.apply_effect_on_apply(character)

    def tooltip_description(self):
        return f"Great Poison stacks: {self.stacks}. Take {(self.value_onestack * self.stacks * 100):.2f}% max hp status damage each turn." \
            f" Stats are decreased by {self.stacks}%."
    
    def tooltip_description_jp(self):
        return f"猛毒のスタック数:{self.stacks}。毎ターン最大HPの{(self.value_onestack * self.stacks * 100):.2f}%の状態異常ダメージを受ける。" \
            f"ステータスが{self.stacks}%減少する。"


class CupidLeadArrowEffect(StatsEffect):
    def __init__(self, name, duration, is_buff, stats_dict=None, condition=None, 
                 use_active_flag=True, stats_dict_function=None, is_set_effect=False, 
                 can_be_removed_by_skill=True, main_stats_additive_dict=None,
                 effect_applier=None):
        super().__init__(name, duration, is_buff, stats_dict, condition, use_active_flag, stats_dict_function, is_set_effect, can_be_removed_by_skill, main_stats_additive_dict)
        self.effect_applier = effect_applier
        self.sort_priority = 1999
        self.original_duration = duration

    def apply_effect_on_remove(self, character):
        if character.is_alive():
            character.take_bypass_status_effect_damage(1, self.effect_applier)
        return super().apply_effect_on_remove(character)

    def apply_effect_during_damage_step(self, character, damage, attacker, which_ds, **keywords):
        # leaves character with 1 hp
        if attacker is not None and attacker.has_effect_that_named("Gold Arrow", additional_name="Cupid_Gold_Arrow") and attacker.name == "Cupid":
            damage *= 2.0
            if damage >= character.hp:
                damage = character.hp - 1
            # if attack_is_crit in keywords and its True, apply love fantasy effect.
            if "attack_is_crit" in keywords and keywords["attack_is_crit"]:
                love_fantasy = Effect("Love Fantasy", 4, False, False)
                love_fantasy.additional_name = "Cupid_Love_Fantasy"
                love_fantasy.apply_rule = "stack"
                character.apply_effect(love_fantasy)
                self.duration = love_fantasy.duration
        return damage


class EastBoilingWaterEffect(ContinuousDamageEffect):
    #  this effect is removed when the absorption shield no longer exists. When this effect is removed, deal status damage to the target,
    def __init__(self, name, duration, is_buff, value, imposter, remove_by_heal=False, damage_type="status"):
        super().__init__(name, duration, is_buff, value, imposter, remove_by_heal, damage_type)
        self.damage_dealt = 0

    def apply_effect_on_trigger(self, character):
        if not character.has_effect_that_named(None, None, "AbsorptionShield"):
            character.remove_effect(self)
        return super().apply_effect_on_trigger(character)

    def apply_effect_on_remove(self, character):
        self.damage_dealt = self.value * self.how_many_times_this_effect_is_triggered_lifetime
        character.take_status_damage(self.damage_dealt * 0.8, self.imposter)
        return super().apply_effect_on_remove(character)


class PharaohPassiveEffect(Effect):
    # Used by Pharaoh
    # At the end of turn, if there is a cursed enemy, increase atk by 30% for 3 turns
    def __init__(self, name, duration, is_buff, value):
        super().__init__(name, duration, is_buff)
        self.value = value
    
    def apply_effect_at_end_of_turn(self, character):
        for c in character.enemy:
            if c.has_effect_that_named('Curse'):
                character.apply_effect(StatsEffect("Greater Pharaoh", 3, True, {"atk": self.value}))
                return
    
    def tooltip_description(self):
        return f"At the end of turn, if there is a cursed enemy, increase atk by {self.value*100:.2f}% for 3 turns."
    
    def tooltip_description_jp(self):
        return f"ターン終了時、呪われた敵がいる場合、3ターンの間、攻撃力が{self.value*100:.2f}%増加する。"
    

class BakeNekoSupressionEffect(Effect):
    # Used by Bake Neko
    # During damage calculation,
    # damage increased by the ratio of self hp to target hp if self has more hp than target. Max bonus damage: 1000%.
    def __init__(self, name, duration, is_buff):
        super().__init__(name, duration, is_buff)

    def apply_effect_in_attack_before_damage_step(self, character, target, final_damage):
        if character.hp > target.hp:
            new_dmg = final_damage * min(character.hp / target.hp, 10)
            global_vars.turn_info_string += f"Supression effect increased damage by {int(min(character.hp / target.hp, 10)*100)}%.\n"
        else:
            new_dmg = final_damage
        return new_dmg

    def tooltip_description(self):
        return f"Attack damage increased by the ratio of self hp to target hp if self has more hp than target. Max bonus damage: 1000%."
    
    def tooltip_description_jp(self):
        return f"自分のHPがターゲットのHPよりも多い場合、ダメージが増加する。増加率は自分のHP/ターゲットのHP。最大増加率: 1000%。"


class TrialofDragonEffect(StatsEffect):
    # Used by Shenlong
    def __init__(self, name, duration, is_buff, stats_dict, damage, imposter, stun_duration):
        super().__init__(name, duration, is_buff, stats_dict)
        self.sort_priority = 2000
        self.damage = damage
        self.imposter = imposter
        self.stun_duration = stun_duration
        self.can_be_removed_by_skill = False

    def apply_effect_on_expire(self, character):
        if character.is_alive():
            if self.damage > 0:
                character.take_status_damage(self.damage, self.imposter)
            character.apply_effect(StunEffect("Stun", self.stun_duration, False))
        
    def tooltip_description(self):
        string = super().tooltip_description()
        return string + f"Deal {self.damage} status damage to self and stun for {self.stun_duration} turns when effect expires."
    
    def tooltip_description_jp(self):
        string = super().tooltip_description_jp()
        return string + f"効果終了時、{self.damage}の状態異常ダメージを受け、{self.stun_duration}ターンスタンする。"


# ---------------------------------------------------------
# End of Monster Passive effects and others
#---------------------------------------------------------
#---------------------------------------------------------
# Consumable effects
#---------------------------------------------------------
    

# ---------------------------------------------------------
# End of Consumable effects
#---------------------------------------------------------