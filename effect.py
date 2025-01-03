from abc import abstractmethod
from collections import Counter
import copy
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
        self.apply_rule = "default" # "default", "stack", "replace"
        self.is_cc_effect = False
        self.tooltip_str = tooltip_str
        self.tooltip_str_jp = tooltip_str_jp
        self.can_be_removed_by_skill = can_be_removed_by_skill
        self.show_stacks = show_stacks
        self.is_protected_effect = False
        self.original_duration = duration
        self.already_applied = False
        self.is_reserved_effect = False
    
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

    def apply_effect_when_replacing_old_same_effect(self, old_effect):
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

    def apply_effect_after_heal_step(self, character, heal_value, overheal_value):
        pass

    def apply_effect_when_missing_attack(self, character, target):
        pass

    def apply_effect_before_action(self, character):
        pass

    def apply_effect_after_action(self, character):
        pass

    def apply_effect_when_taking_friendly_fire(self, character, damage, attacker):
        return damage


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
        color_special = "#9292ff"
        string_unremovable = ""
        if not self.can_be_removed_by_skill or self.is_set_effect:
            string_unremovable += ": Unremovable"
        if self.can_be_removed_by_skill == False and self.is_set_effect == False and self.duration == -1:
            string = "<font color=" + color_special + ">" + self.name + ": Permanent" + string_unremovable + "</font>" + "\n"
        elif self.is_buff:
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
        color_special = "#a6a6ff"
        string_unremovable = ""
        if not self.can_be_removed_by_skill or self.is_set_effect:
            string_unremovable += ":解除不可"
        if self.can_be_removed_by_skill == False and self.is_set_effect == False and self.duration == -1:
            string = "<font color=" + color_special + ">" + self.name + ":永続" + string_unremovable + "</font>" + "\n"
        elif self.is_buff:
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
            string += "現在のスタック数:" + str(self.stacks) + "。"
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



class ReservedEffect(Effect):
    """
    This effect utilizes apply_effect_on_expire() method to trigger a reserved effect or other events.
    """
    def __init__(self, name, duration, is_buff, cc_immunity, effect_applier ,effect_to_apply=None,
                 heal_hp=0, take_damage=0, take_status_damage=0, heal_hp_percentage=0, take_bypass_damage=0,
                 event_function=None, event_description=None, event_description_jp=None):
        super().__init__(name, duration, is_buff, cc_immunity)
        self.is_reserved_effect = True
        self.effect_applier = effect_applier
        self.effect_to_apply = effect_to_apply
        self.heal_hp = heal_hp
        self.take_damage = take_damage
        self.take_status_damage = take_status_damage
        self.heal_hp_percentage = heal_hp_percentage
        self.take_bypass_damage = take_bypass_damage
        self.event_function = event_function
        self.event_description = event_description
        self.event_description_jp = event_description_jp
        
    def apply_effect_on_expire(self, character):
        if character.is_dead():
            return
        if self.effect_to_apply:
            character.apply_effect(self.effect_to_apply)
        if self.heal_hp > 0:
            character.heal_hp(self.heal_hp, self.effect_applier)
        if self.take_damage > 0:
            character.take_damage(self.take_damage, None)
        if self.take_status_damage > 0:
            character.take_status_damage(self.take_status_damage, None)
        if self.heal_hp_percentage > 0:
            character.heal_hp(character.maxhp * self.heal_hp_percentage, self.effect_applier)
        if self.take_bypass_damage > 0:
            character.take_bypass_damage(self.take_bypass_damage, None)
        if self.event_function:
            self.event_function(character)

    def tooltip_description(self):
        s = "When this effect expires: "
        if self.effect_to_apply:
            s += f"Apply effect: {self.effect_to_apply.name}. "
        if self.heal_hp > 0:
            s += f"Heal {self.heal_hp} HP. "
        if self.take_damage > 0:
            s += f"Take {self.take_damage} damage. "
        if self.take_status_damage > 0:
            s += f"Take {self.take_status_damage} status damage. "
        if self.heal_hp_percentage > 0:
            s += f"Heal {self.heal_hp_percentage*100}% of max HP. "
        if self.take_bypass_damage > 0:
            s += f"Take {self.take_bypass_damage} bypass damage. "
        if self.event_description:
            s += self.event_description
        return s

    def tooltip_description_jp(self):
        s = "この効果が終了すると:"
        if self.effect_to_apply:
            s += f"{self.effect_to_apply.name}効果を適用される。"
        if self.heal_hp > 0:
            s += f"{self.heal_hp}HPを回復される。"
        if self.take_damage > 0:
            s += f"{self.take_damage}ダメージを受ける。"
        if self.take_status_damage > 0:
            s += f"{self.take_status_damage}状態異常ダメージを受ける。"
        if self.heal_hp_percentage > 0:
            s += f"{self.heal_hp_percentage * 100}%HPを回復される。"
        if self.take_bypass_damage > 0:
            s += f"{self.take_bypass_damage}状態異常無視ダメージを受ける。"
        if self.event_description_jp:
            s += self.event_description_jp
        return s


# =========================================================
# Protected effects
# =========================================================

# Protected effect
# When a protected character is about to take damage, that damage is taken by the protector instead. Does not apply to status damage.
class ProtectedEffect(Effect):
    def __init__(self, name, duration, is_buff, cc_immunity=False, protector=None, damage_after_reduction_multiplier=1.0, 
                 damage_redirect_percentage=1.0, can_be_removed_by_skill=True):
        super().__init__(name, duration, is_buff, cc_immunity=False)
        self.cc_immunity = cc_immunity
        self.protector = protector
        self.damage_after_reduction_multiplier = damage_after_reduction_multiplier
        self.damage_redirect_percentage = damage_redirect_percentage
        self.sort_priority = self.calculate_sort_priority()
        self.is_protected_effect = True
        self.can_be_removed_by_skill = can_be_removed_by_skill

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
    # NOTE: apply_effect() method on Character class has a apply rule for this effect.
    """
    Absorb [shield_value] amount of damage.
    """
    def __init__(self, name, duration, is_buff, shield_value, cc_immunity):
        super().__init__(name, duration, is_buff, cc_immunity=False)
        self.shield_value = shield_value
        assert self.shield_value > 0 
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


class EffectShield2_HealonDamage(Effect):
    """
    A variant of EffectShield2 that heals the character if damage exceeds a certain threshold.
    """
    def __init__(self, name, duration, is_buff, cc_immunity, hp_threshold, effect_applier, heal_with_self_maxhp_percentage=0):
        super().__init__(name, duration, is_buff, cc_immunity=False)
        self.is_buff = is_buff
        self.cc_immunity = cc_immunity
        self.hp_threshold = hp_threshold
        self.effect_applier = effect_applier
        self.heal_with_self_maxhp_percentage = heal_with_self_maxhp_percentage

    def apply_effect_during_damage_step(self, character, damage, attacker, which_ds, **keywords):
        damage_threshold = character.maxhp * self.hp_threshold
        if damage > damage_threshold:
            heal_amount = 0
            if self.heal_with_self_maxhp_percentage > 0:
                heal_amount += character.maxhp * self.heal_with_self_maxhp_percentage
            character.heal_hp(heal_amount, self.effect_applier)
        return damage

    def tooltip_description(self):
        return f"Heals for {self.heal_with_self_maxhp_percentage*100:.1f}% of max HP if damage exceeds {self.hp_threshold*100:.1f}% of max HP."
    
    def tooltip_description_jp(self):
        return f"ダメージが最大HPの{self.hp_threshold*100:.1f}%を超えると、最大HPの{self.heal_with_self_maxhp_percentage*100:.1f}%回復する。"


class FriendlyFireShield(Effect):
    """
    When taking damage from allies, reduce the damage by [damage_reduction]*100%.
    if [heal_by_damage] is more than 0, heal by damage*100% of the damage taken before reduction. 
    if [apply_shield_on_full_hp] is True, also apply shield on full hp, shield value is damage*100%
    """
    def __init__(self, name, duration, is_buff, cc_immunity, effect_applier , damage_reduction=0.5, heal_by_damage=0, 
                 apply_shield_on_full_hp=False):
        super().__init__(name, duration, is_buff, cc_immunity=False)
        self.is_buff = is_buff
        self.cc_immunity = cc_immunity
        self.effect_applier = effect_applier
        self.damage_reduction = damage_reduction
        self.heal_by_damage = heal_by_damage
        self.apply_shield_on_full_hp = apply_shield_on_full_hp
        self.sort_priority = 201 # Does not matter as this effect is calculated before damage step.

    def apply_effect_when_taking_friendly_fire(self, character, damage, attacker):
        if self.apply_shield_on_full_hp and character.hp == character.maxhp:
            shield_value = damage * 1.00
            if shield_value > 0:
                character.apply_effect(AbsorptionShield("Shield", -1, True, shield_value, False))
        if self.heal_by_damage > 0:
            character.heal_hp(damage * self.heal_by_damage, self.effect_applier)
        final_dmg = damage * (1 - self.damage_reduction)
        return final_dmg
    
    def tooltip_description(self):
        description = f"Reduces damage taken from allies by {self.damage_reduction * 100:.1f}%."
        if self.heal_by_damage > 0:
            description += f" Heals {self.heal_by_damage * 100:.1f}% of the damage taken from allies before reduction."
        if self.apply_shield_on_full_hp:
            description += " Grants a shield equal to the damage amount when at full health."
        return description
    
    def tooltip_description_jp(self):
        description = f"味方から受けるダメージを{self.damage_reduction * 100:.1f}%減少する。"
        if self.heal_by_damage > 0:
            description += f"ダメージの{self.heal_by_damage * 100:.1f}%でHPを回復する。"
        if self.apply_shield_on_full_hp:
            description += "最大HP時、ダメージ分のシールドを付与する。"
        return description






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
    NOTE: When calculating damage, buff is resolved before debuff, which means if a character has a debuff effect that increases damage
    during damage step, ResolveEffect will not be able to guarantee survival.
    """
    def __init__(self, name, duration, is_buff, cc_immunity, hp_to_leave=1, 
                    cover_status_damage=False, cover_normal_damage=True, same_turn_usage="unlimited"):
        super().__init__(name, duration, is_buff, cc_immunity=False)
        self.is_buff = is_buff
        self.cc_immunity = cc_immunity
        self.sort_priority = 204
        self.hp_to_leave = hp_to_leave
        self.cover_status_damage = cover_status_damage
        self.cover_normal_damage = cover_normal_damage
        self.same_turn_usage = same_turn_usage
        self.how_many_times_triggered_this_turn = 1
        self.character_current_turn = 0

    def apply_effect_during_damage_step(self, character, damage, attacker, which_ds, **keywords):
        if character.is_dead():
            return damage
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
        return damage

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


class ResolveEffectVariation1(Effect):
    """
    A variant of ResolveEffect, not reducing damage to 1, but set hp to 1 and return damage as 0.
    gurantee survival against debuffs that increase damage taken by a percentage, 
    """
    def __init__(self, name, duration, is_buff, cc_immunity, damage_immune_duration=1,):
        super().__init__(name, duration, is_buff, cc_immunity=False)
        self.is_buff = is_buff
        self.cc_immunity = cc_immunity
        self.sort_priority = 299
        self.onehp_effect_triggered = False
        self.damage_immune_duration = damage_immune_duration

    def apply_effect_during_damage_step(self, character, damage, attacker, which_ds, **keywords):
        if self.onehp_effect_triggered:
            return 0
        if damage >= character.hp:
            character.hp = 1
            global_vars.turn_info_string += f"{character.name} survived with 1 hp by {self.name}.\n"
            self.onehp_effect_triggered = True
            self.duration = self.damage_immune_duration
            return 0
        else:
            return damage

    def tooltip_description(self):
        if not self.onehp_effect_triggered:
            s = f"Leave with 1 hp when taking fatal damage. For {self.damage_immune_duration} turns, damage taken is reduced to 0."
        else:
            s = f"Damage taken is reduced to 0."
        return s
    
    def tooltip_description_jp(self):
        if not self.onehp_effect_triggered:
            s = f"致命ダメージを受けたとき、1HPで生き残る。{self.damage_immune_duration}ターンの間、受けるダメージが0になる。"
        else:
            s = f"受けるダメージが0になる。"
        return s


class DecayEffect(Effect):
    """
    when healing hp, take damage in the next turn instead.
    """
    def __init__(self, name, duration, is_buff, effect_applier, damage_transfer_rate=1):
        super().__init__(name, duration, is_buff)
        self.effect_applier = effect_applier
        self.apply_rule = "stack" # Make no sense to have 2 decay effect on the same character.
        self.healing_accumulated = 0
        self.damage_transfer_rate = damage_transfer_rate

    def apply_effect_on_trigger(self, character):
        if self.healing_accumulated > 0:
            damage_value = self.healing_accumulated * self.damage_transfer_rate
            assert damage_value > 0, f"Logic Error: {self.name} damage value is negative."
            global_vars.turn_info_string += f"{self.name} strikes! {character.name} is about to take {damage_value} damage.\n"
            character.take_status_damage(damage_value, self.effect_applier)
        self.healing_accumulated = 0

    def apply_effect_during_heal_step(self, character, heal_value, healer, overheal_value):
        self.healing_accumulated += heal_value
        return 0
        
    def tooltip_description(self):
        return f"When being healed, heal amount is reduced to 0, take the {self.damage_transfer_rate*100:.1f}% of the healing amount as status damage in the next turn."
    
    def tooltip_description_jp(self):
        return f"回復を受けると、回復量が0になり、次のターンに受けた治療量の{self.damage_transfer_rate*100:.1f}%の状態異常ダメージを受ける。"





#---------------------------------------------------------
class CancellationShield(Effect):
    # NOTE: apply_effect() method on Character class has a apply rule for this effect.
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

    def tooltip_description_jp(self):
        return "行動不可、回避率が100%減少。受ける通常ダメージを80%減少、状態異常ダメージを100%増加。" \
        "各ターン、最大HPの1%に相当する状態異常ダメージを受ける。"



class PetrifyEffect(Effect):
    def __init__(self, name, duration, is_buff, imposter, delay_trigger=0):
        super().__init__(name, duration, is_buff)
        self.name = "Petrify"
        self.is_buff = False
        self.imposter = imposter
        self.delay_trigger = delay_trigger
        self.apply_rule = "stack"
        self.is_cc_effect = True
        self.turns_passed = 0
    
    def apply_effect_on_apply(self, character):
        stats_dict = {"eva": -1.00}
        character.update_stats(stats_dict, reversed=False) # Eva can be lower than 0, which makes sense.

    def apply_effect_on_trigger(self, character):
        self.turns_passed += 1
        if self.turns_passed > 30 and not self.duration == -1:
            self.duration = -1
            self.can_be_removed_by_skill = False

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
        " Immune to status damage, normal damage taken is increased by 100%." \
        " After 30 turns, this effect can no longer be removed and last indefinitely."
    
    def tooltip_description_jp(self):
        return "行動不可、回避率が100%減少。" \
        "受ける状態異常ダメージを無効化、通常ダメージが100%増加。" \
        "30ターン後、この効果は解除できなくなり、持続時間が無限になる。"


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
        remove_effect = True
        if character.has_effect_that_named("Bubble World", "Qimon_Bubble_World", "BubbleWorldEffect"):
            # taken damage less than 10% of maxhp, do not wake up.
            if damage < character.maxhp * 0.1 and character.is_alive():
                global_vars.turn_info_string += f"Damage less than {character.maxhp * 0.1:.2f}, {character.name} still sleeping.\n"
                remove_effect = False
        if character.has_effect_that_named("Dream Invitation", "QimonNY_Dream_Invitation", "BubbleWorldEffect"):
            # wake up chance only 30%, damage taken is increased by 30%.
            if random.random() < 0.3:
                global_vars.turn_info_string += f"{character.name} wakes up from the dream.\n"
            else:
                remove_effect = False
                new_dmg = damage * 1.3
                global_vars.turn_info_string += f"{character.name} still sleeping, damage is increased by {new_dmg - damage:.2f}.\n"
                damage = new_dmg
                
        if remove_effect:
            character.remove_effect(self)
        return damage

    def apply_effect_on_apply(self, character):
        if character.has_effect_that_named("Bubble World", "Qimon_Bubble_World", "BubbleWorldEffect"):
            character.remove_random_amount_of_buffs(3, False)
        if character.has_effect_that_named("Dream Invitation", "QimonNY_Dream_Invitation", "BubbleWorldEffect"):
            character.remove_random_amount_of_buffs(3, False)
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
        str = "Consumed by fear."
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
        str = "恐怖に取り憑かれた。"
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
                 main_stats_additive_dict=None, stats_dict_value_increase_when_missing_attack=0):
        """
        [condition] function takes character as argument. if specified, this effect will trigger a stats update every turn, 
        use it with True [use_active_flag]: for example, increase atk by 20% if hp < 50%,
        use it with False [use_active_flag]: for example, every turn, increase critdmg by 1% if hp < 50%.
        [stats_dict_function] need [condition] and False [use_active_flag] (makes no sense to use the flag), 
        called when condition is met, revert the old stats and update with the new stats if anything changed.
        [main_stats_additive_dict] is a dictionary containing main stats, for example {'hp': 200, 'atk: 40'}, this dict is added to additive_main_stats
        of Character class on effect apply, and removed on effect removal. I do not want to implement a dynamic dict for this because it will be complex.
        [stats_dict_value_increase_when_missing_attack] is added to stats dict when attack is missing. For example, {'acc': 1.0} -> {'acc': 1.1},
        it does not support codition, use_active_flag, stats_dict_function.
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
        if self.is_set_effect:
            self.sort_priority = 2000
        self.can_be_removed_by_skill = can_be_removed_by_skill
        self.main_stats_additive_dict = main_stats_additive_dict
        self.stats_dict_value_increase_when_missing_attack = stats_dict_value_increase_when_missing_attack

    def apply_effect_on_apply(self, character):
        # print(f"Applying effect {self.name} on {character.name}")
        if self.condition is None or self.condition(character):
            if self.main_stats_additive_dict:
                # print(f"Adding main stats {self.main_stats_additive_dict} to {character.name}")
                new_dict = {**self.main_stats_additive_dict, **{'effect_pointer': self}}
                character.additive_main_stats.append(new_dict)
                character.update_main_stats_additive(effect_pointer=self)

            if self.stats_dict:
                # print(f"Adding stats {self.stats_dict} to {character.name}")
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

    def apply_effect_when_replacing_old_same_effect(self, old_effect: Effect):
        assert self.apply_rule == "replace", f"This rule is not supported: {self.apply_rule}"
        # for main_stats_additive_dict, we simply add the old dict to the new dict.

        if self.main_stats_additive_dict and old_effect.main_stats_additive_dict:
            result_dict = old_effect.main_stats_additive_dict.copy()
            for key, value in self.main_stats_additive_dict.items():
                if key in result_dict:
                    result_dict[key] += value
                else:
                    result_dict[key] = value
            self.main_stats_additive_dict = result_dict
        else:
            print(old_effect)
            print(self)
            print(self.main_stats_additive_dict)
            print(old_effect.main_stats_additive_dict)
            print(old_effect.stats_dict)
            raise Exception("Only main_stats_additive_dict is supported for now.")


    def apply_effect_when_missing_attack(self, character, target):
        if self.stats_dict_value_increase_when_missing_attack == 0:
            return
        if not self.stats_dict:
            return
        old_stats_dict = self.stats_dict.copy()  
        new_stats_dict = self.stats_dict.copy()  
        for key, value in self.stats_dict.items():
            new_stats_dict[key] = value + self.stats_dict_value_increase_when_missing_attack
        character.update_stats(old_stats_dict, reversed=True)
        self.stats_dict = new_stats_dict
        character.update_stats(self.stats_dict, reversed=False)
        global_vars.turn_info_string += f"Attack missed! {character.name}'s stats are increased by {self.stats_dict_value_increase_when_missing_attack * 100:.2f}%.\n"
        # if character.is_alive():
        #     character.heal_hp(character.maxhp * 0.10, self.buff_applier)


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
            # Group stats by their percentage change
            value_to_keys = {}
            for key, value in self.stats_dict.items():
                percentage_value = value * 100
                if key in ["maxhp", "hp", "atk", "defense", "spd"]:
                    # Scaling stats are handled differently
                    scaling_key = ("scaled", percentage_value)
                    value_to_keys.setdefault(scaling_key, []).append(key)
                else:
                    processed_key = key.replace("_", " ")
                    if value > 0:
                        change_key = ("increased", percentage_value)
                    else:
                        change_key = ("decreased", -percentage_value)
                    value_to_keys.setdefault(change_key, []).append(processed_key)
            # Construct the description
            for (change_type, percentage_value), keys in value_to_keys.items():
                keys_string = ", ".join(keys)
                if change_type == "scaled":
                    string += f"{keys_string} is scaled to {percentage_value:.2f}%."
                else:
                    string += f"{keys_string} is {change_type} by {percentage_value:.2f}%."
            if self.stats_dict_value_increase_when_missing_attack > 0:
                string += f" The above stats are increased by {self.stats_dict_value_increase_when_missing_attack*100:.2f}% when attack is missing."
        if self.main_stats_additive_dict:
            # Group additive stats
            value_to_keys = {}
            for key, value in self.main_stats_additive_dict.items():
                if value > 0:
                    change_key = ("increased", value)
                else:
                    change_key = ("decreased", -value)
                value_to_keys.setdefault(change_key, []).append(key)
            # Construct the description
            for (change_type, value), keys in value_to_keys.items():
                keys_string = ", ".join(keys)
                string += f"{keys_string} is {change_type} by {value:.2f}."
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
            # Group stats by their percentage change
            value_to_keys = {}
            for key, value in self.stats_dict.items():
                percentage_value = value * 100
                japanese_key = self.translate_key(key)
                if key in ["maxhp", "hp", "atk", "defense", "spd"]:
                    scaling_key = ("scaled", percentage_value)
                    value_to_keys.setdefault(scaling_key, []).append(japanese_key)
                else:
                    processed_key = key.replace("_", " ")
                    processed_key = self.translate_key(processed_key)
                    if value > 0:
                        change_key = ("増加する", percentage_value)
                    else:
                        change_key = ("減少する", -percentage_value)
                    value_to_keys.setdefault(change_key, []).append(processed_key)
            # Construct the description
            for (change_type, percentage_value), keys in value_to_keys.items():
                keys_string = "、".join(keys)
                if change_type == "scaled":
                    string += f"{keys_string}が{percentage_value:.2f}%に調整される。"
                else:
                    string += f"{keys_string}が{percentage_value:.2f}%{change_type}。"
            if self.stats_dict_value_increase_when_missing_attack > 0:
                string += f"攻撃が外れた時、上記のステータスが{self.stats_dict_value_increase_when_missing_attack*100:.2f}%増加する。"
        if self.main_stats_additive_dict:
            # Group additive stats
            value_to_keys = {}
            for key, value in self.main_stats_additive_dict.items():
                japanese_key = self.translate_key(key)
                if value > 0:
                    change_key = ("増加する", value)
                else:
                    change_key = ("減少する", -value)
                value_to_keys.setdefault(change_key, []).append(japanese_key)
            # Construct the description
            for (change_type, value), keys in value_to_keys.items():
                keys_string = "、".join(keys)
                string += f"{keys_string}が{value:.2f}{change_type}。"
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
        if character.is_alive():
            amount_to_heal = self.value_function(character, self.buff_applier)
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
        if character.is_dead():
            return
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
    
    def apply_effect_after_heal_step(self, character, heal_value, overheal_value):
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
    for each transmission, the next time transmission chance is multiplied by [is_plague_transmission_decay].
    """
    def __init__(self, name, duration, is_buff, ratio, imposter, base: str, remove_by_heal=False, 
                 damage_type="status", is_plague=False, is_plague_transmission_chance=0.0,
                 is_plague_transmission_decay=0.5):
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
    
    def apply_effect_after_heal_step(self, character, heal_value, overheal_value):
        if self.remove_by_heal:
            global_vars.turn_info_string += f"{character.name}'s {self.name} is removed by heal.\n"
            character.remove_effect(self)

    def apply_effect_at_end_of_turn(self, character):
        if not self.is_plague:
            super().apply_effect_at_end_of_turn(character)
        else:
            t = character.get_neighbor_allies_not_including_self()
            if t:
                a = random.choice(t)
                # if a.is_dead():
                #     raise Exception("Logic Error")
                # Actually, plague can be transmitted to dead bodies.
                # if a.has_effect_that_is(self):
                #     return
                if random.random() < self.is_plague_transmission_chance:
                    self.is_plague_transmission_chance = max(0, self.is_plague_transmission_chance * (1 - self.is_plague_transmission_decay))
                    new_plague = copy.copy(self)
                    a.apply_effect(new_plague)

    def tooltip_description(self):
        s = f"Take {(self.ratio*100):.2f}% {self.base} {self.damage_type} damage each turn."
        if self.remove_by_heal:
            s += " This effect can be removed by healing."
        if self.is_plague:
            # s += f" At end of turn, {int(self.is_plague_transmission_chance*100)}% chance to apply the same effect to a neighbor ally."
            s += f" At end of turn, some chance to apply the same effect to a neighbor ally."
            if self.is_plague_transmission_decay > 0:
                s += f" For each transmission, its chance is reduced by {int(self.is_plague_transmission_decay*100)}%."
        return s

    def tooltip_description_jp(self):
        base_dict = {
            "maxhp": "最大HP",
            "hp": "現在のHP",
            "losthp": "失ったHP"
        }
        damage_type_dict = {
            "status": "状態異常",
            "bypass": "状態異常無視",
            "normal": "通常"
        }
        base = base_dict.get(self.base, self.base)
        damage_type = damage_type_dict.get(self.damage_type, self.damage_type)
        s = f"毎ターン{(self.ratio*100):.2f}%の{base}に応じた{damage_type}ダメージを受ける。"
        if self.remove_by_heal:
            s += "この効果は回復されると解除される。"
        if self.is_plague:
            # s += f"ターン終了時に、{int(self.is_plague_transmission_chance*100)}%の確率で隣接する味方に伝染する。"
            s += f"ターン終了時に、一定の確率で隣接する味方に伝染する。"
            if self.is_plague_transmission_decay > 0:
                s += f"伝染するたびに、伝染確率が{int(self.is_plague_transmission_decay*100)}%減少する。"
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
            # if hasattr(character, "after_revive"):
            #     character.after_revive() # v3.2.4 Already handled in revive method.
            character.remove_effect(self)

    def tooltip_description(self):
        return f"Revive with {self.effect_value*100}% + {self.effect_value_constant} hp the next turn after fallen."
    
    def tooltip_description_jp(self):
        return f"倒れた次のターンに{self.effect_value*100}% + {self.effect_value_constant}HPで復活する。"


class StingEffect(Effect):
    """
    every time target take damage, take [value] status damage.
    take [value_s] bypass damage every time after taking status damage. If value function is provided, use that instead.
    """
    def __init__(self, name, duration, is_buff, value, imposter, value_function_normal_damage_step=None,
                        value_s=0, value_function_status_damage_step=None):

        super().__init__(name, duration, is_buff)
        self.name = name
        self.is_buff = is_buff
        self.value = value
        self.imposter = imposter
        self.value_function_normal_damage_step = value_function_normal_damage_step
        self.value_s = value_s
        self.value_function_status_damage_step = value_function_status_damage_step

    def apply_effect_after_damage_step(self, character, damage, attacker):
        if self.value == 0 and self.value_function_normal_damage_step is None:
            return
        if self.value_function_normal_damage_step:
            damage_to_take = self.value_function_normal_damage_step(character, damage, attacker, self.imposter)
        else:
            damage_to_take = self.value
        if damage_to_take > 0 and character.is_alive():
            global_vars.turn_info_string += f"{character.name} will take {damage_to_take:.2f} status damage from {self.name}.\n"
            character.take_status_damage(damage_to_take, self.imposter)

    def apply_effect_after_status_damage_step(self, character, damage, attacker):
        if self.value_s == 0 and self.value_function_status_damage_step is None:
            return
        if self.value_function_status_damage_step:
            damage_to_take = self.value_function_status_damage_step(character, damage, attacker, self.imposter)
        else:
            damage_to_take = self.value_s
        if damage_to_take > 0 and character.is_alive():
            global_vars.turn_info_string += f"{character.name} will take {damage_to_take:.2f} bypass damage from {self.name}.\n"
            character.take_bypass_status_effect_damage(damage_to_take, self.imposter)

    def tooltip_description(self):
        s = ""
        if self.value or self.value_function_normal_damage_step:
            if self.value:
                s += f"Take {self.value:.2f} status damage every time after taking damage."
            else:
                s += f"Take status damage every time after taking damage, damage is calculated by a function."
        if self.value_s or self.value_function_status_damage_step:
            if self.value_s:
                s += f"Take {self.value_s:.2f} bypass damage every time after taking status damage."
            else:
                s += f"Take bypass damage every time after taking status damage, damage is calculated by a function."
        return s
    
    def tooltip_description_jp(self):
        s = ""
        if self.value or self.value_function_normal_damage_step:
            if self.value:
                s += f"ダメージを受けた後、{self.value:.2f}の状態異常ダメージを受ける。"
            else:
                s += f"ダメージを受けた後、状態異常ダメージを受ける。ダメージは関数で計算される。"
        if self.value_s or self.value_function_status_damage_step:
            if self.value_s:
                s += f"状態異常ダメージを受けた後、{self.value_s:.2f}の状態異常無視ダメージを受ける。"
            else:
                s += f"状態異常ダメージを受けた後、状態異常無視ダメージを受ける。ダメージは関数で計算される。"
        return s

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
            # apply a copy of the effect.
            copyed = copy.copy(self.effect_to_apply)
            character.apply_effect(copyed)

    def tooltip_description(self):
        return f"Apply {self.effect_to_apply.name} effect after {self.require_turns_without_damage} turns without taking damage."
    
    def tooltip_description_jp(self):
        return f"{self.require_turns_without_damage}ターン攻撃を受けていないと{self.effect_to_apply.name}効果が付与される。"


class TauntEffect(Effect):
    """
    The character with this effect can only target [marked_character].
    """
    def __init__(self, name, duration, is_buff, cc_immunity, marked_character):
        super().__init__(name, duration, is_buff)
        self.cc_immunity = cc_immunity
        self.marked_character = marked_character
        self.apply_rule = "stack" # Make no sense to have multiple taunt effects.

    def apply_effect_on_trigger(self, character):
        if character.is_dead():
            character.remove_effect(self)
            return
        if self.marked_character.is_dead():
            character.remove_effect(self)
            return

    def tooltip_description(self):
        return f"When targeting enemies, only {self.marked_character.name} can be targeted."
    
    def tooltip_description_jp(self):
        return f"敵を対象とするとき、{self.marked_character.name}のみを対象とする。"


class OverhealEffect(Effect):
    """ 
    trigger effect when overheal
    """
    def __init__(self, name, duration, is_buff, buff_applier, overheal_bonus, cc_immunity=False, 
                        absorption_shield_ratio=0):
        super().__init__(name, duration, is_buff)
        self.buff_applier = buff_applier
        self.overheal_bonus = overheal_bonus
        self.cc_immunity = cc_immunity
        self.absorption_shield_ratio = absorption_shield_ratio

    def apply_effect_after_heal_step(self, character, heal_value, overheal_value):
        bonus = 0
        if overheal_value > 0:
            bonus = overheal_value * self.overheal_bonus
        if bonus <= 0:
            return
        if self.absorption_shield_ratio > 0:
            shield_value = bonus * self.absorption_shield_ratio
            shield_effect = AbsorptionShield("Shield", -1, True, shield_value, False)
            character.apply_effect(shield_effect)

    def tooltip_description(self):
        s = f"When overhealing, a bonus score is calculated by {self.overheal_bonus*100:.2f}% of the overheal."
        if self.absorption_shield_ratio > 0:
            s += f" Gain a shield that absorbs damage equal to {self.absorption_shield_ratio*100:.2f}% of the bonus." 
        return s

    def tooltip_description_jp(self):
        s = f"過剰回復時、ボーナススコアは過剰回復量の{self.overheal_bonus*100:.2f}%で計算される。"
        if self.absorption_shield_ratio > 0:
            s += f"ボーナスの{self.absorption_shield_ratio*100:.2f}%分のダメージを吸収するシールドを獲得する。"
        return s


class SmittenEffect(Effect):
    """
    After action, heal hp by [heal_value]
    """
    def __init__(self, name, duration, is_buff, cc_immunity, heal_value, effect_applier):
        super().__init__(name, duration, is_buff)
        self.cc_immunity = cc_immunity
        self.heal_value = heal_value
        self.effect_applier = effect_applier

    def apply_effect_after_action(self, character):
        if character.is_dead():
            return
        character.heal_hp(self.heal_value, self.effect_applier)

    def tooltip_description(self):
        return f"After action, heal {self.heal_value:.2f} hp."
    
    def tooltip_description_jp(self):
        return f"行動後、{self.heal_value:.2f}HP回復する。"


class DamageTypeConvertionEffect(Effect):
    """
    When attacking, convert damage type to [new_damage_type]
    """
    def __init__(self, name, duration, is_buff, cc_immunity, effect_applier, new_damage_type: str):
        super().__init__(name, duration, is_buff)
        self.cc_immunity = cc_immunity
        self.effect_applier = effect_applier
        assert new_damage_type in ["normal", "bypass", "status"], "Invalid new damage type."
        self.new_damage_type = new_damage_type
        self.apply_rule = "stack"

    def apply_effect_on_apply(self, character):
        character.damage_type_during_attack_method = self.new_damage_type

    def apply_effect_on_remove(self, character):
        character.damage_type_during_attack_method = "undefined"

    def tooltip_description(self):
        return f"When attacking, convert damage type to {self.new_damage_type}."
    
    def tooltip_description_jp(self):
        return f"攻撃時、ダメージタイプを{self.new_damage_type}に変換する。"


# " Falling Petal: The first time when hp falls below 50%, for 30 turns, damage taken is reduced by 90%, " \
# " when this effect triggers, you are silenced for 30 turns."
class FallingPetalEffect(Effect):
    """
    Apply effect the first time when hp falls below [at_what_hp_percentage]
    """
    def __init__(self, name, duration, is_buff, cc_immunity, effect_applier,
                 at_what_hp_percentage, effect_to_apply: Effect, another_effect_to_apply: Effect=None, 
                 more_effects_to_apply: list[Effect]=None, can_be_removed_by_skill=False):
        super().__init__(name, duration, is_buff)
        self.cc_immunity = cc_immunity
        self.effect_applier = effect_applier
        self.at_what_hp_percentage = at_what_hp_percentage
        self.effect_to_apply = effect_to_apply
        self.another_effect_to_apply = another_effect_to_apply
        self.more_effects_to_apply = more_effects_to_apply
        self.can_be_removed_by_skill = can_be_removed_by_skill
        self.apply_rule = "stack"

    def apply_effect_on_trigger(self, character):
        if character.is_dead():
            return
        if character.hp < character.maxhp * self.at_what_hp_percentage:
            # effect = ReductionShield("Falling Petal", 30, True, 0.9, False)
            # character.apply_effect(effect)
            # effect = SilenceEffect("Silence", self.silence_duration, False, False)
            # character.apply_effect(effect)
            character.apply_effect(copy.copy(self.effect_to_apply))
            if self.another_effect_to_apply:
                character.apply_effect(copy.copy(self.another_effect_to_apply))
            if self.more_effects_to_apply:
                for effect in self.more_effects_to_apply:
                    character.apply_effect(copy.copy(effect))
            character.remove_effect(self)

    def tooltip_description(self):
        list_of_effect_names = [self.effect_to_apply.name]
        if self.another_effect_to_apply:
            list_of_effect_names.append(self.another_effect_to_apply.name)
        if self.more_effects_to_apply:
            list_of_effect_names += [e.name for e in self.more_effects_to_apply]
        return f"The first time when hp falls below {self.at_what_hp_percentage*100}%, apply {', '.join(list_of_effect_names)}."
    
    def tooltip_description_jp(self):
        list_of_effect_names = [self.effect_to_apply.name]
        if self.another_effect_to_apply:
            list_of_effect_names.append(self.another_effect_to_apply.name)
        if self.more_effects_to_apply:
            list_of_effect_names += [e.name for e in self.more_effects_to_apply]
        return f"HPが{self.at_what_hp_percentage*100}%以下になったとき、{'、'.join(list_of_effect_names)}を付与する。"


# this effect is kinda similar, but does the following:
# given a dict of {hp_percentage: effect_to_apply}, apply the effect when hp falls below the percentage.
# each effect can only be used once. For example, 0.8: stun, 0.6: stun, if hp suddenly falls below 0.5, then 2 effects are applied at once.
class BirdShadowEffect(Effect):
    """
    Given a dict of {hp_percentage: effect_to_apply}, apply the effect when hp falls below the percentage.
    """
    def __init__(self, name, duration, is_buff, cc_immunity, effect_applier,
                 effect_dict: dict[float, Effect], can_be_removed_by_skill=False):
        super().__init__(name, duration, is_buff)
        self.cc_immunity = cc_immunity
        self.effect_applier = effect_applier
        self.effect_dict = effect_dict
        self.can_be_removed_by_skill = can_be_removed_by_skill
        self.apply_rule = "replace"

    def apply_effect_on_trigger(self, character):
        if character.is_dead():
            return
        for hp_percentage, effect in list(self.effect_dict.items()):
            if character.hp < character.maxhp * hp_percentage:
                character.apply_effect(copy.copy(effect))
                del self.effect_dict[hp_percentage]

    def apply_effect_at_end_of_turn(self, character):
        # if dict is empty, remove the effect.
        if not self.effect_dict:
            character.remove_effect(self)

    def tooltip_description(self):
        threshold_effects = [f"Below {int(hp_percentage * 100)}% HP: {effect.name}" for hp_percentage, effect in self.effect_dict.items()]
        return f"When HP first falls below each listed threshold, apply the corresponding effect(s) once: {', '.join(threshold_effects)}."

    def tooltip_description_jp(self):
        threshold_effects_jp = [f"HPが{int(hp_percentage * 100)}%未満になると{effect.name}" for hp_percentage, effect in self.effect_dict.items()]
        return f"HPが指定した割合を初めて下回ったとき、対応する効果を一度だけ適用する:{','.join(threshold_effects_jp)}。"


# effect duration bonus effect
# this effect adjusts duration_bonus_when_apply_effect_buff and duration_bonus_when_apply_effect_debuff,
# integer value, can be positive or negative.
# when removed, set them to 0.
class DurationBonusEffect(Effect):
    """
    Adjust duration_bonus_when_apply_effect_buff and duration_bonus_when_apply_effect_debuff.
    """
    def __init__(self, name, duration, is_buff, cc_immunity, effect_applier, buff_value=0, debuff_value=0):
        super().__init__(name, duration, is_buff)
        self.cc_immunity = cc_immunity
        self.effect_applier = effect_applier
        self.buff_value = buff_value
        self.debuff_value = debuff_value

    def apply_effect_on_apply(self, character):
        character.duration_bonus_when_apply_effect_buff += self.buff_value
        character.duration_bonus_when_apply_effect_debuff += self.debuff_value

    def apply_effect_on_remove(self, character):
        character.duration_bonus_when_apply_effect_buff -= self.buff_value
        character.duration_bonus_when_apply_effect_debuff -= self.debuff_value

    def tooltip_description(self):
        s = "When applying effect, "
        if self.buff_value > 0:
            s += f"buff effect duration is increased by {self.buff_value}. "
        elif self.buff_value < 0:
            s += f"buff effect duration is decreased by {-self.buff_value}. "
        if self.debuff_value > 0:
            s += f"debuff effect duration is increased by {self.debuff_value}. "
        elif self.debuff_value < 0:
            s += f"debuff effect duration is decreased by {-self.debuff_value}. "
        return s

    def tooltip_description_jp(self):
        s = "効果を適用するとき、"
        if self.buff_value > 0:
            s += f"バフ効果の持続時間が{self.buff_value}増加する。"
        elif self.buff_value < 0:
            s += f"バフ効果の持続時間が{-self.buff_value}減少する。"
        if self.debuff_value > 0:
            s += f"デバフ効果の持続時間が{self.debuff_value}増加する。"
        elif self.debuff_value < 0:
            s += f"デバフ効果の持続時間が{-self.debuff_value}減少する。"
        return s


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
        return f"Shield that absorbs up to {self.shield_value} damage. This effect does not treat as Absorption Shield."
    
    def tooltip_description_jp(self):
        return f"{self.shield_value}ダメージを吸収する。この効果は吸収シールドとして扱われない。"
    

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

    def apply_effect_after_action(self, character):
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

    def apply_effect_before_action(self, character):
        character.heal_hp(character.spd * 0.50, character)
        # for x turns, increase spd by 30%.
        spd_buff = StatsEffect("Freight", 4, True, {"spd": 1.30}, is_set_effect=True)
        character.apply_effect(spd_buff)


# ---------------------------------------------------------
# Runic
# See character.py for implementation.
class EquipmentSetEffect_Runic(Effect):
    def __init__(self, name, duration, is_buff):
        super().__init__(name, duration, is_buff)
        self.is_set_effect = True
        self.sort_priority = 2000


# ---------------------------------------------------------
# Grassland
# When you havent taken an action in battle yet, speed is increased by 100%.
class EquipmentSetEffect_Grassland(StatsEffect):
    def __init__(self, name, duration, is_buff, stats_dict=None, condition=None, use_active_flag=True, 
                 stats_dict_function=None, is_set_effect=False, can_be_removed_by_skill=True, 
                 main_stats_additive_dict=None):
        super().__init__(name, duration, is_buff, stats_dict, condition, use_active_flag, stats_dict_function, 
                         is_set_effect, can_be_removed_by_skill, main_stats_additive_dict)
        self.is_set_effect = True
        self.sort_priority = 2000

    def apply_effect_at_end_of_turn(self, character):
        if character.have_taken_action:
            character.remove_effect(self)

    def tooltip_description(self):
        return super().tooltip_description() + " After taking action, this effect is removed."
    
    def tooltip_description_jp(self):
        return super().tooltip_description_jp() + "行動を取った後、この効果が解除される。"


# ---------------------------------------------------------
# Tigris
# See character.py for implementation.
class EquipmentSetEffect_Tigris(Effect):
    """
    When targeting multiple enemies, for each enemy that is missing, damage is increased by x%.
    """
    def __init__(self, name, duration, is_buff):
        super().__init__(name, duration, is_buff)
        self.is_set_effect = True
        self.sort_priority = 2000


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
            character.take_status_damage(1, self.effect_applier)
        return super().apply_effect_on_remove(character)

    def apply_effect_during_damage_step(self, character, damage, attacker, which_ds, **keywords):
        # leaves character with 1 hp
        if attacker is not None and attacker.has_effect_that_named("Gold Arrow", additional_name="Cupid_Gold_Arrow") and attacker.name == "Cupid":
            damage *= 2.0
            if damage >= character.hp:
                damage = character.hp - 1
            # if attack_is_crit in keywords and its True, apply love fantasy effect.
            if "attack_is_crit" in keywords and keywords["attack_is_crit"]:
                love_fantasy = CupidLoveFantasyEffect("Love Fantasy", 4, False, False)
                character.apply_effect(love_fantasy)
                self.duration = love_fantasy.duration
        return damage


class CupidLoveFantasyEffect(Effect):
    def __init__(self, name, duration, is_buff, cc_immunity):
        super().__init__(name, duration, is_buff, cc_immunity)
        self.sort_priority = 1999
        self.additional_name = "Cupid_Love_Fantasy"
        self.apply_rule = "stack"
        self.is_cc_effect = True

    def tooltip_description(self):
        return f"This is love."
    
    def tooltip_description_jp(self):
        return f"これは愛です。"



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


class LesterBookofMemoryEffect(StatsEffect):
    def __init__(self, name, duration, is_buff, stats_dict=None, condition=None, use_active_flag=True, stats_dict_function=None, is_set_effect=False, can_be_removed_by_skill=True, main_stats_additive_dict=None,
                 buff_applier=None):
        super().__init__(name, duration, is_buff, stats_dict, condition, use_active_flag, stats_dict_function, is_set_effect, can_be_removed_by_skill, main_stats_additive_dict)
        self.buff_applier = buff_applier
        if self.buff_applier is None:
            raise RuntimeError("buff_applier cannot be None.")
        

    def apply_effect_when_missing_attack(self, character, target):
        old_stats_dict = self.stats_dict.copy()  # Create a copy of the original stats_dict
        new_stats_dict = self.stats_dict.copy()  # Create a copy for the new stats_dict
        for key, value in self.stats_dict.items():
            new_stats_dict[key] = value + 0.1
        character.update_stats(old_stats_dict, reversed=True)
        self.stats_dict = new_stats_dict
        character.update_stats(self.stats_dict, reversed=False)
        global_vars.turn_info_string += f"Book of Memory effect is triggered! {character.name}'s stats are increased by 10%.\n"
        if character.is_alive():
            character.heal_hp(character.maxhp * 0.10, self.buff_applier)



class LesterExcitingTimeEffect(Effect):
    """ 
    Exciting Time: Every time when a hp recovery is received, atk is increased by the amount of overheal,
    Atk bonus effect lasts for 10 turns.
    """
    def __init__(self, name, duration, is_buff, buff_applier):
        super().__init__(name, duration, is_buff)
        self.buff_applier = buff_applier

    def apply_effect_after_heal_step(self, character, heal_value, overheal_value):
        if overheal_value > 0:
            bonus = int(overheal_value * 0.15)
            bonus = max(bonus, 1)
            bonus = min(bonus, 5 * self.buff_applier.lvl)
            atkup = StatsEffect("Atk Up", 10, True, main_stats_additive_dict={"atk": bonus})
            atkup.apply_rule = "replace"
            atkup.additional_name = "Lester_Exciting_Time_Atk_Bonus"
            character.apply_effect(atkup)

    def tooltip_description(self):
        return f"Every time when overheal is received, atk is increased by 20% of the amount of overheal."
    
    def tooltip_description_jp(self):
        return f"過剰回復を受けるたび、攻撃力が過剰回復量の20%増加する。"


class LuFlappingSoundEffect(Effect):
    """ 
    Attack start of battle, apply unremovable Flapping Sound on the closest enemy,
    when the affected enemy takes action and a skill can be used, for 1 turn, silence the enemy and pay hp equal to n * level.
    Paying hp treats as taking status damage. If you are defeated, the effect on the enemy is removed.
    """
    def __init__(self, name, duration, is_buff, buff_applier, hp_cost):
        super().__init__(name, duration, is_buff)
        self.buff_applier = buff_applier
        self.hp_cost = hp_cost

    def apply_effect_on_trigger(self, character):
        if self.buff_applier.is_dead():
            character.remove_effect(self)

    def apply_effect_before_action(self, character):
        if character.is_dead():
            return
        if self.buff_applier.is_dead():
            character.remove_effect(self)
            return
        r, reason = character.can_take_action()
        r2 = character.can_use_a_skill()
        if r and r2:
            global_vars.turn_info_string += f"{character.name} is affected by Flapping Sound!\n"
            character.apply_effect(SilenceEffect("Silence", 1, False))
            self.buff_applier.take_status_damage(self.hp_cost, self.buff_applier)
            if self.buff_applier.is_dead():
                character.update_ally_and_enemy()
                character.remove_effect(self)
        else:
            return

    def tooltip_description(self):
        return "Be careful when taking action."
    
    def tooltip_description_jp(self):
        return "行動を取る際に注意が必要。"
       

class UlricInCloudEffect(StatsEffect):
    # When Full Cloud effect is applied when you have In Cloud, its duration is increased by 10 turns, and can no longer be removed by skill.
    def __init__(self, name, duration, is_buff, stats_dict=None, condition=None, use_active_flag=True, 
                 stats_dict_function=None, is_set_effect=False, can_be_removed_by_skill=True, 
                 main_stats_additive_dict=None):
        super().__init__(name, duration, is_buff, stats_dict, condition, use_active_flag, stats_dict_function, 
                         is_set_effect, can_be_removed_by_skill, main_stats_additive_dict)
        self.check_full_cloud = True


    def apply_effect_at_end_of_turn(self, character):
        if self.check_full_cloud:
            full_cloud = character.get_effect_that_named("Full Cloud")
            if full_cloud is not None:
                full_cloud.duration += 10
                full_cloud.can_be_removed_by_skill = False
                global_vars.turn_info_string += f"Full Cloud is extended by 10 turns and can no longer be removed by skill.\n"
                # print("Full Cloud is extended by 10 turns and can no longer be removed by skill.")
                self.check_full_cloud = False


class FreyaDuckySilenceEffect(SilenceEffect):
    """
    Ducky Silence: Functions the same as Silence, when this effect is removed, a new Ducky Silence is applied on a random ally.
    """
    def __init__(self, name, duration, is_buff, cc_immunity=False, delay_trigger=0):
        super().__init__(name, duration, is_buff, cc_immunity, delay_trigger)
        self.name = "Ducky Silence"

    def apply_effect_at_end_of_turn(self, character):
        if character.is_dead():
            character.remove_effect(self)

    def apply_effect_on_trigger(self, character):
        if character.is_dead():
            character.remove_effect(self)

    def apply_effect_on_remove(self, character):
        character.update_ally_and_enemy()
        if character.ally:
            ally = random.choice(character.ally)
            ally.apply_effect(FreyaDuckySilenceEffect("Ducky Silence", self.original_duration, False))


class CocoaSleepEffect(SleepEffect):
    def __init__(self, name, duration, is_buff, cc_immunity=False, delay_trigger=0):
        super().__init__(name, duration, is_buff, cc_immunity, delay_trigger)
        self.name = "Sleep"
        self.is_buff = True
        self.additional_name = "Cocoa_Sleep"

    def apply_effect_on_trigger(self, character):
        if character.is_dead():
            character.remove_effect(self)
            return
        character.heal_hp(character.maxhp * 0.08, character)

    def apply_effect_on_apply(self, character):
        pass

    def apply_effect_on_remove(self, character):
        sd = StatsEffect("Sweet Dreams", 6, True, {"atk": 2.2, "defense": 2.2, "spd": 2.2})
        sd.additional_name = "Cocoa_Sweet_Dreams"
        sd.cc_immunity = True
        character.apply_effect(sd)

    def tooltip_description(self):
        return "While asleep, recover 8% hp each turn. Apply Sweet Dreams when removed."

    def tooltip_description_jp(self):
        return "眠っている間、毎ターンHPを8%回復する。解除されると幻夢が適用される。"


class RikaResolveEffect(ResolveEffectVariation1):
    """
    When triggers, all allies also gains this effect.
    """
    def __init__(self, name, duration, is_buff, cc_immunity, damage_immune_duration=1):
        super().__init__(name, duration, is_buff, cc_immunity, damage_immune_duration)

    def apply_effect_during_damage_step(self, character, damage, attacker, which_ds, **keywords):
        if self.onehp_effect_triggered:
            return 0
        if damage >= character.hp:
            character.hp = 1
            global_vars.turn_info_string += f"{character.name} survived with 1 hp by {self.name}.\n"
            self.onehp_effect_triggered = True
            self.duration = self.damage_immune_duration
            character.update_ally_and_enemy()
            for a in character.ally:
                if a != character:
                    a.hp = 1
                    copy_effect = copy.copy(self)
                    copy_effect.can_be_removed_by_skill = True
                    a.apply_effect(copy_effect)
            return 0
        else:
            return damage


class ShintouEffect(Effect):
    """
    see class Inaba(Character) for details.
    """
    def __init__(self, name, duration, is_buff, max_counters, buff_applier):
        super().__init__(name, duration, is_buff)
        self.name = name
        self.is_buff = is_buff
        self.max_counters = max_counters
        self.current_counters = max_counters
        self.buff_applier = buff_applier
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
            heal_value = self.buff_applier.atk * 3
            character.heal_hp(heal_value, self.buff_applier)
            # Heal efficiency increased by 30%, evasion rate increased by 30%.
            blessing_effect = StatsEffect("Blessing", 20, True, {"heal_efficiency": 0.4})
            if character is self.buff_applier:
                bae = len(self.buff_applier.get_all_effect_that_named("Blessing"))
                if bae >= 4:
                    for a in self.buff_applier.party:
                        if a.is_dead():
                            a.revive(0, 100, self.buff_applier)
                        # if not dead, apply heal.
                        else:
                            r1, r2, r3 = a.heal_hp(heal_value, self.buff_applier)
                            # print(f"{r1} {r3}")
                    for e in self.buff_applier.enemy:
                        e.take_status_damage(self.buff_applier.atk * 5.0, self.buff_applier)
            # if character in self.buff_applier.party:
            #     global_vars.shintou_applied_on_ally += 1
            # else:
            #     global_vars.shintou_applied_on_enemy += 1
            character.apply_effect(blessing_effect)
            character.remove_effect(self)

    def apply_effect_at_end_of_turn(self, character):
        if not self.should_trigger_end_of_turn_effect:
            return
        available_enemies = character.enemy
        if not available_enemies:
            character.remove_effect(self)
        else:
            target = next(character.target_selection())
            new_effect = ShintouEffect(self.name, self.duration, self.is_buff, self.max_counters, self.buff_applier)
            new_effect.current_counters = self.current_counters
            new_effect.should_trigger_end_of_turn_effect = False
            target.apply_effect(new_effect)
            character.remove_effect(self)

    def tooltip_description(self):
        return f"Shintou has {self.current_counters} counters."
    
    def tooltip_description_jp(self):
        return f"神稲のカウンター数:{self.current_counters}。"
    

class PineQGEffect(ReductionShield):
    def __init__(self, name, duration, is_buff, effect_value, cc_immunity, *, requirement=None, 
                 requirement_description=None, requirement_description_jp=None, 
                 damage_function=None, cover_status_damage=True, 
                 cover_normal_damage=True):
        super().__init__(name, duration, is_buff, effect_value, cc_immunity, 
                         requirement=requirement, requirement_description=requirement_description, 
                         requirement_description_jp=requirement_description_jp, damage_function=damage_function, 
                         cover_status_damage=cover_status_damage, cover_normal_damage=cover_normal_damage)
        self.apply_rule = "stack"
        self.max_time_of_buff_copy = 10 # Not used

    def apply_effect_after_action(self, character):
        if character.is_dead():
            return
        # copy random 2 buffs, apply them to allies who has QC effect
        all_buffs: list[Effect] = character.get_active_removable_effects(get_buffs=True)
        if len(all_buffs) < 2:
            selected_buffs = all_buffs
        else:
            selected_buffs = random.sample(all_buffs, 2)
        for buff in selected_buffs:
            # if the buff is PineQGEffect or PineQCEffect, its duration is set to original duration.
            if buff.__class__.__name__ == "PineQGEffect" or buff.__class__.__name__ == "PineQCEffect":
                buff.duration = buff.original_duration
        # find all allies who has QC effect
        allies_with_qc = character.target_selection(keyword="ally_that_must_have_effect_full", keyword2="QC", keyword3="None", keyword4="PineQCEffect")
        allies_with_qc = list(allies_with_qc)
        if not allies_with_qc:
            return
        for a in allies_with_qc:
            for sb in selected_buffs:
                a.apply_effect(copy.copy(sb))


class PineQCEffect(ReductionShield):
    def __init__(self, name, duration, is_buff, effect_value, cc_immunity, *, requirement=None, 
                 requirement_description=None, requirement_description_jp=None, 
                 damage_function=None, cover_status_damage=True, 
                 cover_normal_damage=True):
        super().__init__(name, duration, is_buff, effect_value, cc_immunity, 
                         requirement=requirement, requirement_description=requirement_description, 
                         requirement_description_jp=requirement_description_jp, damage_function=damage_function, 
                         cover_status_damage=cover_status_damage, cover_normal_damage=cover_normal_damage)
        self.apply_rule = "stack"
        self.max_time_of_buff_copy = 10 # Not used

    def apply_effect_after_action(self, character):
        if character.is_dead():
            return
        # copy random 2 buffs, apply them to allies who has QG effect
        all_buffs: list[Effect] = character.get_active_removable_effects(get_buffs=True)
        if len(all_buffs) < 2:
            selected_buffs = all_buffs
        else:
            selected_buffs = random.sample(all_buffs, 2)
        # find all allies who has QG effect
        allies_with_qg = character.target_selection(keyword="ally_that_must_have_effect_full", keyword2="QG", keyword3="None", keyword4="PineQGEffect")
        allies_with_qg = list(allies_with_qg)
        if not allies_with_qg:
            return
        for a in allies_with_qg:
            for sb in selected_buffs:
                a.apply_effect(copy.copy(sb))





class BubbleWorldEffect(Effect):
    """
    When falling asleep, all active buffs are removed, damage taken that below 10% of maxhp
    cannot remove Sleep effect.
    [di]: Convert this effect to Dream Invitation effect for QimonNY
    """
    def __init__(self, name, duration, is_buff, imposter, di=False):
        super().__init__(name, duration, is_buff)
        self.name = name
        self.is_buff = is_buff
        self.imposter = imposter
        self.di = di

    def tooltip_description(self):
        if not self.di:
            return "When falling asleep, 3 active buffs are removed, damage taken that below 10% of maxhp cannot remove Sleep effect."
        else:
            return "When falling asleep, 3 active buffs are removed, damage taken only have 30% chance to remove Sleep effect."
    
    def tooltip_description_jp(self):
        if not self.di:
            return "睡眠状態になると、3つのアクティブなバフが解除され、最大HPの10%未満のダメージでは睡眠効果が解除されない。"
        else:
            return "睡眠状態になると、3つのアクティブなバフが解除され、ダメージを受けると睡眠効果が解除される確率は30%。"

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