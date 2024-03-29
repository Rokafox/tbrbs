from collections import Counter
import random
import global_vars


class Effect:
    def __init__(self, name, duration, is_buff, cc_immunity=False, delay_trigger=0, is_set_effect=False, 
                 tooltip_str=None, can_be_removed_by_skill=True):
        self.name = name
        self.duration = duration
        self.is_buff = bool(is_buff)
        self.cc_immunity = bool(cc_immunity)
        self.delay_trigger = delay_trigger # number of turns before effect is triggered
        self.flag_for_remove = False # If True, will be removed at the beginning of the next turn.
        self.secondary_name = None
        self.is_set_effect = is_set_effect
        self.sort_priority = 1000 # The lower the number, the higher the priority. Default is 1000.
        self.stacks = 1 
        self.apply_rule = "default" # "default", "stack"
        self.is_cc_effect = False
        self.tooltip_str = tooltip_str
        self.can_be_removed_by_skill = can_be_removed_by_skill
    
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

    def apply_effect_when_adding_stacks(self, character, stats_income):
        pass

    def apply_effect_on_expire(self, character):
        pass
    
    def apply_effect_on_remove(self, character):
        pass

    def apply_effect_in_attack_before_damage_step(self, character, target, final_damage):
        return final_damage

    def apply_effect_during_damage_step(self, character, damage, attacker):
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

    def apply_effect_after_heal_step(self, character, heal_value):
        pass


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
            string += "Grants CC immunity.\n"
        if not self.can_be_removed_by_skill or self.is_set_effect:
            string += "Cannot be removed by skill.\n"
        if self.delay_trigger > 0:
            string += "Trigger in " + str(self.delay_trigger) + " turn(s)\n"
        string += self.tooltip_description()
        return string
    
    def tooltip_description(self):
        if self.tooltip_str:
            return self.tooltip_str
        else:
            return "No description available."


# =========================================================
# Protected effects
# =========================================================

# Protected effect
# When a protected character is about to take damage, that damage is taken by the protector instead. Does not apply to status damage.
class ProtectedEffect(Effect):
    def __init__(self, name, duration, is_buff, cc_immunity=False, protector=None, multiplier=1.0):
        super().__init__(name, duration, is_buff, cc_immunity=False)
        self.cc_immunity = cc_immunity
        self.protector = protector
        self.multiplier = multiplier
        self.sort_priority = 100
        self.is_protected_effect = True

    def protected_apply_effect_during_damage_step(self, character, damage, attacker, func_after_dmg):
        if self.protector is None:
            raise Exception
        if self.protector.is_alive():
            damage = damage * self.multiplier
            self.protector.take_damage(damage, attacker, func_after_dmg, disable_protected_effect=True)
            return 0
        else:
            return damage
    
    def apply_effect_on_trigger(self, character):
        # Double check, the first is to handle cases of leaving party unexpectedly.
        if self.protector not in character.ally or self.protector.is_dead():
            character.remove_effect(self)

    def apply_effect_at_end_of_turn(self, character):
        if self.protector.is_dead():
            character.remove_effect(self)

    def tooltip_description(self):
        return f"Protected by {self.protector.name}."


# =========================================================
# End of Protected effects
# =========================================================
# CC effects
# =========================================================
    
# Stun effect
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


# Silence effect
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


# Sleep effect
class SleepEffect(Effect):
    def __init__(self, name, duration, is_buff, cc_immunity=False, delay_trigger=0):
        super().__init__(name, duration, is_buff)
        self.name = "Sleep"
        self.is_buff = False
        self.cc_immunity = cc_immunity
        self.delay_trigger = delay_trigger
        self.apply_rule = "stack"
        self.is_cc_effect = True
    
    def apply_effect_during_damage_step(self, character, damage, attacker):
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


# Confusion effect
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
        return "Attack random ally or enemy."


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
                str += f"{key} is scaled to {value*100}%."
            else:
                if value > 0:
                    str += f"{key} is increased by {value*100}%."
                else:
                    str += f"{key} is decreased by {-value*100}%."
        return str

# =========================================================
# End of CC effects
# =========================================================
# Stats effects
# =========================================================


class StatsEffect(Effect):
    def __init__(self, name, duration, is_buff, stats_dict=None, condition=None, use_active_flag=True, 
                 stats_dict_function=None, is_set_effect=False, can_be_removed_by_skill=True):
        """
        Initializes a StatsEffect object.

        Args:
            name (str): The name of the effect.
            duration (int): The duration of the effect.
            is_buff (bool): Indicates whether the effect is a buff or a debuff.
            stats_dict (dict, optional): A dictionary containing the stats to be modified and their corresponding values. Defaults to None.
            condition (function, optional): A condition function that determines when the effect should be triggered. Defaults to None.
            condition(character) -> bool: A function that returns True if the condition is met, and False otherwise.
            use_active_flag (bool, optional): Indicates whether the stats update should be triggered only when the condition is met. Defaults to True.
            stats_dict_function (function, optional): A function that dynamically updates the stats_dict when use_active_flag is False. Defaults to None.
            is_set_effect (bool, optional): Indicates whether the effect is a set effect. Defaults to False.
            can_be_removed_by_skill (bool, optional): Indicates whether the effect can be removed by a skill. Defaults to True.
        """
        super().__init__(name, duration, is_buff, cc_immunity=False, delay_trigger=0)
        self.stats_dict = stats_dict
        self.condition = condition
        self.flag_is_active = False
        self.use_active_flag = use_active_flag
        self.stats_dict_function = stats_dict_function
        if self.stats_dict_function:
            if not condition or use_active_flag:
                raise Exception("stats_dict_function can only be used when condition func is provided and use_active_flag are False.")
            self.stats_dict = self.stats_dict_function()
        self.is_set_effect = is_set_effect
        self.can_be_removed_by_skill = can_be_removed_by_skill

    def apply_effect_on_apply(self, character):
        if self.condition is None or self.condition(character):
            character.update_stats(self.stats_dict, reversed=False)
            self.flag_is_active = True

    def apply_effect_on_remove(self, character):
        if self.condition is None or self.condition(character):
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
                string += "Effect is active.\n"
            else:
                string += "Effect is not active.\n"
        for key, value in self.stats_dict.items():
            if key in ["maxhp", "hp", "atk", "defense", "spd"]:
                string += f"{key} is scaled to {value*100}%."
            else:
                if value > 0:
                    string += f"{key} is increased by {value*100}%."
                else:
                    string += f"{key} is decreased by {-value*100}%."
        return string

# ---------------------------------------------------------
# Critical rate and critical damage effect, for character Seth. Effect increases every turn.
class SethEffect(Effect):
    # A simpler version of StatsEffect.
    def __init__(self, name, duration, is_buff, value):
        super().__init__(name, duration, is_buff)
        self.value = value
    
    def apply_effect_on_trigger(self, character):
        # Every turn, raise by 0.01(1%).
        stats_dict = {"crit": 0.01, "critdmg": 0.01}
        character.update_stats(stats_dict, reversed=False)
    
    def tooltip_description(self):
        return f"Critical rate and critical damage is increased by {self.value*100}% each turn."
    

# Example : For 4 turns, if not taking damage, increase atk by 50% and spd by 50% for 4 turns used by Cockatorice.
class NotTakingDamageEffect(Effect):
    def __init__(self, name, duration, is_buff, stats_dict, apply_rule, require_turns_without_damage, 
                 buff_name, buff_duration):
        super().__init__(name, duration, is_buff)
        self.stats_dict = stats_dict
        self.apply_rule = apply_rule
        self.require_turns_without_damage = require_turns_without_damage
        self.buff_name = buff_name
        if self.buff_name == self.name:
            raise Exception("buff_name cannot be the same as name.")
        self.buff_duration = buff_duration

    def apply_effect_at_end_of_turn(self, character):
        twd = character.get_num_of_turns_not_taken_damage()
        if twd >= self.require_turns_without_damage and not character.has_effect_that_named(self.buff_name):
            character.apply_effect(StatsEffect(self.buff_name, self.buff_duration, self.is_buff, self.stats_dict))

# =========================================================
# End of Stats effects
# =========================================================
# Timed bomb effects
# Effect that trigger events when expired.
# =========================================================


class TimedBombEffect(Effect):
    def __init__(self, name, duration, is_buff, damage, imposter, cc_immunity):
        super().__init__(name, duration, is_buff)
        self.damage = damage
        self.imposter = imposter
        self.cc_immunity = cc_immunity

    def apply_effect_on_expire(self, character):
        if character.is_alive():
            character.take_status_damage(self.damage, self.imposter)

    def tooltip_description(self):
        return f"Deal {self.damage} status damage when expired."


class TimedStunBombEffect(Effect):
    def __init__(self, name, duration, is_buff, damage, imposter, cc_immunity, stun_duration):
        super().__init__(name, duration, is_buff)
        self.damage = damage
        self.imposter = imposter
        self.cc_immunity = cc_immunity
        self.stun_duration = stun_duration

    def apply_effect_on_expire(self, character):
        if character.is_alive():
            if self.damage > 0:
                character.take_status_damage(self.damage, self.imposter)
            character.apply_effect(StunEffect("Stun", self.stun_duration, False))

    def tooltip_description(self):
        return "Stun for 1 turn when expired."


# =========================================================
# End of Timed bomb effects
# =========================================================
# Continuous Damage/Healing effects
# =========================================================


# Continuous Damage effect
class ContinuousDamageEffect(Effect):
    def __init__(self, name, duration, is_buff, value, imposter, remove_by_heal=False):
        super().__init__(name, duration, is_buff)
        self.value = float(value)
        self.is_buff = is_buff
        self.imposter = imposter # The character that applies this effect
        self.remove_by_heal = remove_by_heal
    
    def apply_effect_on_trigger(self, character):
        character.take_status_damage(self.value, self.imposter)
    
    def apply_effect_after_heal_step(self, character, heal_value):
        if self.remove_by_heal:
            global_vars.turn_info_string += f"{character.name}'s {self.name} is removed by heal.\n"
            character.remove_effect(self)

    def tooltip_description(self):
        return f"Take {int(self.value)} status damage each turn."


# ---------------------------------------------------------
# Poison effect
# A variant of ContinuousDamageEffect, takes damage based on maxhp.
class PoisonDamageEffect(Effect):
    """
    base: "maxhp", "hp", "losthp"
    """
    def __init__(self, name, duration, is_buff, value, imposter, base):
        super().__init__(name, duration, is_buff)
        self.value = float(value)
        self.is_buff = is_buff
        self.imposter = imposter # The character that applies this effect
        self.base = base # "maxhp", "hp", "losthp"
    
    def apply_effect_on_trigger(self, character):
        if character.is_dead():
            return
        match self.base:
            case "maxhp":
                character.take_status_damage(self.value * character.maxhp, self.imposter)
            case "hp":
                character.take_status_damage(self.value * character.hp, self.imposter)
            case "losthp":
                character.take_status_damage(self.value * (character.maxhp - character.hp), self.imposter)
            case _:
                raise Exception("Invalid base.")
    
    def tooltip_description(self):
        return f"Take {int(self.value*100)}% {self.base} status damage each turn."


# ---------------------------------------------------------
# Plague effect
# A variant of PoisonDamageEffect, at end of turn, value% chance to apply the same effect to a neighbor ally
class PlagueEffect(Effect):
    """
    base: "maxhp", "hp", "losthp"
    transmission_chance: float, 0.0 to 1.0
    """
    def __init__(self, name, duration, is_buff, value, imposter, base, transmission_chance):
        super().__init__(name, duration, is_buff)
        self.original_duration = duration
        self.value = float(value)
        self.is_buff = is_buff
        self.imposter = imposter # The character that applies this effect
        self.base = base # "maxhp", "hp", "losthp"
        self.transmission_chance = transmission_chance
    
    def apply_effect_on_trigger(self, character):
        if character.is_dead():
            return
        match self.base:
            case "maxhp":
                character.take_status_damage(self.value * character.maxhp, self.imposter)
            case "hp":
                character.take_status_damage(self.value * character.hp, self.imposter)
            case "losthp":
                character.take_status_damage(self.value * (character.maxhp - character.hp), self.imposter)
            case _:
                raise Exception("Invalid base.")
    
    def apply_effect_at_end_of_turn(self, character):
        t = character.get_neighbor_allies_not_including_self()
        if t:
            a = random.choice(t)
            if a.has_effect_that_named(self.name, None, "PlagueEffect"):
                return
            if random.random() < self.transmission_chance:
                a.apply_effect(PlagueEffect(self.name, self.original_duration, self.is_buff, self.value, self.imposter, self.base, self.transmission_chance))

    def tooltip_description(self):
        return f"Take {int(self.value*100)}% {self.base} status damage each turn."


# ---------------------------------------------------------
# Great Poison effect
# used by Requina
class GreatPoisonEffect(Effect):
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
        return f"Great Poison stacks: {self.stacks}.\nTake {int(self.value_onestack * self.stacks * 100)}% max hp status damage each turn." \
            f"\nStats are decreased by {self.stacks}%."

# ---------------------------------------------------------
# Continuous Heal effect
class ContinuousHealEffect(Effect):
    """
    value: float, 0.0 to 1.0
    
    """
    def __init__(self, name, duration, is_buff, value, is_percent=False):
        super().__init__(name, duration, is_buff)
        self.value = float(value)
        self.is_buff = is_buff
        self.is_percent = is_percent
    
    def apply_effect_on_trigger(self, character):
        if character.is_dead():
            return
        if self.is_percent:
            character.heal_hp(character.maxhp * self.value, character)
        else:
            character.heal_hp(self.value, character)
    
    def tooltip_description(self):
        if self.is_percent:
            return f"Recovers {int(self.value*100)}% hp each turn."
        else:
            return f"Recovers {int(self.value)} hp each turn."


# =========================================================
# End of Continuous Damage/Healing effects
# =========================================================
# Various Shield effects
# =========================================================

# Absorption Shield effect
class AbsorptionShield(Effect):
    def __init__(self, name, duration, is_buff, shield_value, cc_immunity):
        super().__init__(name, duration, is_buff, cc_immunity=False)
        self.shield_value = shield_value
        self.is_buff = is_buff
        self.cc_immunity = cc_immunity

    def apply_effect_during_damage_step(self, character, damage, attacker):
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
        return f"Absorbs up to {self.shield_value} damage."

#---------------------------------------------------------
# Reduction Shield and Damage Amplify effect (reduces/increase damage taken by a certain percentage)
class ReductionShield(Effect):
    def __init__(self, name, duration, is_buff, effect_value, cc_immunity):
        super().__init__(name, duration, is_buff, cc_immunity=False)
        self.is_buff = is_buff
        self.effect_value = effect_value
        self.cc_immunity = cc_immunity

    def apply_effect_during_damage_step(self, character, damage, attacker):
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
# Only used by Fenrir
class EffectShield1(Effect):
    def __init__(self, name, duration, is_buff, threshold, heal_value, cc_immunity,
                require_above_zero_dmg=False):
        super().__init__(name, duration, is_buff, cc_immunity=False)
        self.is_buff = is_buff
        self.threshold = threshold
        self.heal_value = heal_value
        self.cc_immunity = cc_immunity
        self.sort_priority = 120
        self.require_above_zero_dmg = require_above_zero_dmg

    def apply_effect_at_end_of_turn(self, character):
        character.update_ally_and_enemy()
        if character.has_neighbor("Fenrir") == False:
            self.flag_for_remove = True

    def apply_effect_during_damage_step(self, character, damage, attacker):
        if character.hp < character.maxhp * self.threshold and (not self.require_above_zero_dmg or damage > 0):
            character.heal_hp(self.heal_value, self)
        return damage
    
    def tooltip_description(self):
        return f"When hp is below {self.threshold*100}%, heal for {self.heal_value} hp before damage calculation."


#---------------------------------------------------------
# Effect shield 2 (When taking damage that would exceed 10% of maxhp, reduce damage above 10% of maxhp by 50%. 
# For every turn passed, damage reduction effect is reduced by 2%.)
# Used by Chiffon
class EffectShield2(Effect):
    def __init__(self, name, duration, is_buff, cc_immunity, damage_reduction=0.5, shrink_rate=0.02, threshold=0.1):
        super().__init__(name, duration, is_buff, cc_immunity=False)
        self.is_buff = is_buff
        self.cc_immunity = cc_immunity
        self.damage_reduction = damage_reduction
        self.shrink_rate = shrink_rate
        self.sort_priority = 150
        self.threshold = threshold

    def apply_effect_during_damage_step(self, character, damage, attacker):
        if damage > character.maxhp * self.threshold:
            damage = character.maxhp * self.threshold + (damage - character.maxhp * self.threshold) * self.damage_reduction
        return damage
    
    def apply_effect_on_trigger(self, character):
        self.damage_reduction = max(self.damage_reduction - self.shrink_rate, 0)
        if self.damage_reduction == 0:
            self.flag_for_remove = True
    
    def tooltip_description(self):
        return f"Current damage reduction: {self.damage_reduction*100}%."


#---------------------------------------------------------
# Effect shield 3 (When taking damage that would exceed 10% of maxhp, reduce damage above 10% of maxhp by 50%, 
# The attacker takes 30% of damage that is reduced by this effect.)
# Used by monster Paladin
class EffectShield3(Effect):
    def __init__(self, name, duration, is_buff, cc_immunity, damage_reduction=0.5, damage_reflect=0.3):
        super().__init__(name, duration, is_buff, cc_immunity=False)
        self.is_buff = is_buff
        self.cc_immunity = cc_immunity
        self.damage_reduction = damage_reduction
        self.damage_reflect = damage_reflect
        self.sort_priority = 150

        self.attacker = None
        self.actual_reflect = 0

    def apply_effect_during_damage_step(self, character, damage, attacker):
        if damage > character.maxhp * 0.1:
            old_damge = damage
            damage = character.maxhp * 0.1 + (damage - character.maxhp * 0.1) * self.damage_reduction
            damage_to_reflect = (old_damge - damage) * self.damage_reflect
            attacker.take_status_damage(damage_to_reflect, character)
        return damage
    
    def tooltip_description(self):
        return f"Reduce damage above 10% of maxhp by {self.damage_reduction*100}%, reflect {self.damage_reflect*100}% of damage that is reduced."


#---------------------------------------------------------
# Cancellation Shield effect (cancel the damage to 0 if damage exceed certain amount of max hp)
class CancellationShield(Effect):
    def __init__(self, name, duration, is_buff, threshold, cc_immunity, uses=1):
        super().__init__(name, duration, is_buff, cc_immunity=False)
        self.is_buff = is_buff
        self.threshold = threshold
        self.cc_immunity = cc_immunity
        self.sort_priority = 150
        self.uses = uses

    def apply_effect_during_damage_step(self, character, damage, attacker):
        if damage > character.maxhp * self.threshold:
            self.uses -= 1
            if self.uses == 0:
                character.remove_effect(self)
            elif self.uses < 0:
                raise Exception("Logic Error")
            global_vars.turn_info_string += f"{character.name} shielded the attack!\n"
            return 0
        else:
            return damage
        
    def tooltip_description(self):
        return f"Cancel attack {str(self.uses)} times if damage exceed {self.threshold*100}% of max hp."


# Cancellation Shield 2 effect (cancel the part of damage that exceed certain amount of max hp)
class CancellationShield2(Effect):
    def __init__(self, name, duration, is_buff, threshold, cc_immunity):
        super().__init__(name, duration, is_buff, cc_immunity=False)
        self.is_buff = is_buff
        self.threshold = threshold
        self.cc_immunity = cc_immunity
        self.sort_priority = 180

    def apply_effect_during_damage_step(self, character, damage, attacker):
        damage = min(damage, character.maxhp * self.threshold)
        return damage

        
    def tooltip_description(self):
        return f"Cancel the damage that exceed {self.threshold*100}% of max hp."


# Cancellation Shield effect (cancel the damage to 0 if damage lower than certain amount of max hp)
class CancellationShield3(Effect):
    def __init__(self, name, duration, is_buff, threshold, cc_immunity, uses=1):
        super().__init__(name, duration, is_buff, cc_immunity=False)
        self.is_buff = is_buff
        self.threshold = threshold
        self.cc_immunity = cc_immunity
        self.sort_priority = 150
        self.uses = uses

    def apply_effect_during_damage_step(self, character, damage, attacker):
        if damage < character.maxhp * self.threshold:
            self.uses -= 1
            if self.uses == 0:
                character.remove_effect(self)
            elif self.uses < 0:
                raise Exception("Logic Error")
            global_vars.turn_info_string += f"{character.name} shielded the attack!\n"
            return 0
        else:
            return damage
        
    def tooltip_description(self):
        return f"Cancel attack {str(self.uses)} times if damage lower than {self.threshold*100}% of max hp."


# =========================================================
# End of Various Shield effects
# =========================================================
# Special effects
# Effects in this section need special handling, or does not seem to fit into any other category.
# =========================================================
# New Year Fireworks effect
# New Year Fireworks: Have 6 counters. Every turn, throw a dice, counter decreases by the dice number.
# When counter reaches 0, deal 600% of applier atk as damage to self.
# At the end of the turn, this effect is applied to a random enemy.
class NewYearFireworksEffect(Effect):
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


#---------------------------------------------------------
# Reborn effect (revive with certain amount of hp)
class RebornEffect(Effect):
    def __init__(self, name, duration, is_buff, effect_value, cc_immunity):
        super().__init__(name, duration, is_buff, cc_immunity=False)
        self.is_buff = is_buff
        self.effect_value = effect_value
        self.cc_immunity = cc_immunity
    
    def apply_effect_on_trigger(self, character):
        if character.is_dead():
            character.revive(1, hp_percentage_to_revive=self.effect_value)
            if hasattr(character, "after_revive"):
                character.after_revive()
            character.remove_effect(self)

    def tooltip_description(self):
        return f"Revive with {self.effect_value*100}% hp the turn after fallen."


# Sting: every time target take damage, take value status damage.
class StingEffect(Effect):
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
    

# Hide effect: cannot be targeted by enemy. Unless for n_random_targets and n_random_enemies where n >= 5.
class HideEffect(Effect):
    def __init__(self, name, duration, is_buff, cc_immunity=False, remove_on_damage=False):
        super().__init__(name, duration, is_buff, cc_immunity=False)
        self.name = "Hide"
        self.is_buff = is_buff
        self.cc_immunity = cc_immunity
        self.sort_priority = 2000
        self.is_active = True
        self.remove_on_damage = remove_on_damage

    def apply_effect_on_trigger(self, character):
        if character.is_dead():
            character.remove_effect(self)
            return
        hidden_allies = [ally for ally in character.ally if ally.has_effect_that_named(self.name, None, "HideEffect")]
        if len(hidden_allies) == len(character.ally):
            self.is_active = False
        if not self.is_active:
            self.flag_for_remove = True
        
    def apply_effect_during_damage_step(self, character, damage, attacker):
        if self.remove_on_damage:
            global_vars.turn_info_string += f"{character.name} is no longer hidden!\n"
            character.remove_effect(self)
        return damage

    def tooltip_description(self):
        string = f"Enemy attack and skill that target less than 5 enemies will not target this character. "
        string += f"Effect is no longer active when all allies are hidden and will be removed the start of the next turn. "
        if self.remove_on_damage:
            string += f"Effect is removed when taking damage."
        return string


# Sin Effect: when defeated, all allies take status damage equal to {value}.
class SinEffect(StatsEffect):
    def __init__(self, name, duration, is_buff, value, stats_dict):
        super().__init__(name, duration, is_buff, stats_dict)
        self.value = value
        self.sort_priority = 2000
        self.can_be_removed_by_skill = False

    def apply_effect_on_trigger(self, character):
        if character.is_dead():
            for ally in character.ally:
                if ally.is_dead():
                    continue
                ally.take_status_damage(self.value, character)
            global_vars.turn_info_string += f"Justice is served, {character.name} has been defeated!\n"
            character.remove_effect(self)
        return super().apply_effect_on_trigger(character)

    def apply_effect_at_end_of_turn(self, character):
        if character.is_dead():
            for ally in character.ally:
                if ally.is_dead():
                    continue
                ally.take_status_damage(self.value, character)
            global_vars.turn_info_string += f"Justice is served, {character.name} has been defeated!\n"
            character.remove_effect(self)
        return super().apply_effect_at_end_of_turn(character)

    def tooltip_description(self):
        string = super().tooltip_description()
        return string + f"When defeated, all allies take status damage equal to {self.value}."



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

    def apply_effect_during_damage_step(self, character, damage, attacker):
        if self.onehp_effect_triggered:
            return 0
        if damage >= character.hp:
            character.hp = 1
            global_vars.turn_info_string += f"{character.name} survived with 1 hp!\n"
            self.onehp_effect_triggered = True
            self.duration = 3
            return 0
        else:
            return damage

    def tooltip_description(self):
        return f"Leave with 1 hp when taking fatal damage."


#---------------------------------------------------------
# KangTao
# Absorption Shield effect, separate from AbsorptionShield class to very slightly improve performance.
class EquipmentSetEffect_KangTao(Effect):
    def __init__(self, name, duration, is_buff, shield_value, cc_immunity):
        super().__init__(name, duration, is_buff, cc_immunity=False)
        self.shield_value = shield_value
        self.is_buff = is_buff
        self.cc_immunity = cc_immunity
        self.is_set_effect = True
        self.sort_priority = 2000

    def apply_effect_during_damage_step(self, character, damage, attacker):
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
                string += "Effect is active.\n"
            else:
                string += "Effect is not active.\n"
        for key, value in self.stats_dict.items():
            if key in ["maxhp", "hp", "atk", "defense", "spd"]:
                string += f"{key} is scaled to {value*100}% on condition."
            else:
                string += f"{key} is increased by {value*100}% on condition."
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
                string += f"{key} is scaled to {value*100}%."
            else:
                string += f"{key} is increased by {value*100}%."
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

    def apply_effect_during_damage_step(self, character, damage, attacker):
        # count how many "Sovereign" in character.buffs, if less than 5, apply effect.
        if Counter([effect.name for effect in character.buffs])["Sovereign"] < 5:
            character.apply_effect(StatsEffect("Sovereign", 4, True, self.stats_dict, is_set_effect=True))
        return damage
    
    def tooltip_description(self):
        return f"Accumulate 1 stack of Sovereign when taking damage."


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
        if not character.has_effect_that_named("Bamboo"):
            character.apply_effect(StatsEffect("Bamboo", 5, True, self.stats_dict, is_set_effect=True))
            e = ContinuousHealEffect("Bamboo", 5, True, 0.16, True)
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
# Liquidation
# When taking damage, for each of the following stats that is lower than attacker's, damage is reduced by 30%: hp, atk, def, spd.
class EquipmentSetEffect_Liquidation(Effect):
    def __init__(self, name, duration, is_buff, damage_reduction):
        super().__init__(name, duration, is_buff)
        self.is_set_effect = True
        self.sort_priority = 2000
        self.damage_reduction = damage_reduction

    def apply_effect_during_damage_step(self, character, damage, attacker):
        if damage == 0:
            return 0
        for key in ["hp", "atk", "defense", "spd"]:
            if getattr(character, key) < getattr(attacker, key):
                damage = damage * (1 - self.damage_reduction)
                global_vars.turn_info_string += f"{character.name}'s {key} is lower than {attacker.name}'s, damage is reduced by {int(self.damage_reduction*100)}%.\n"
        return damage



#---------------------------------------------------------
# End of Equipment set effects
#---------------------------------------------------------
#---------------------------------------------------------
# Monster Passive effects and others
#---------------------------------------------------------
class PharaohPassiveEffect(Effect):
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
        return f"At the end of turn, if there is a cursed enemy, increase atk by {self.value*100}% for 3 turns."
    

class BakeNekoSupressionEffect(Effect):
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


class TrialofDragonEffect(StatsEffect):
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


# ---------------------------------------------------------
# End of Monster Passive effects and others
#---------------------------------------------------------
#---------------------------------------------------------
# Consumable effects
#---------------------------------------------------------
    

# ---------------------------------------------------------
# End of Consumable effects
#---------------------------------------------------------