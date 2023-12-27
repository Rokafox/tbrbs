from collections import Counter
from fine_print import fine_print


class Effect:
    def __init__(self, name, duration, is_buff, cc_immunity=False, delay_trigger=0, is_set_effect=False):
        self.name = name
        self.duration = duration
        self.is_buff = bool(is_buff)
        self.cc_immunity = bool(cc_immunity)
        self.delay_trigger = delay_trigger # number of turns before effect is triggered
        self.flag_for_remove = False # If True, will be removed at the beginning of the next turn.
        self.secondary_name = None
        self.is_set_effect = is_set_effect
    
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

    def apply_effect_at_end_of_turn(self, character):
        # This method is usually used for effects that need to toggle flag_for_remove on.
        # As effect is removed at the beginning of the next turn.
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
    
# Protected effect
# When a protected character is about to take damage, that damage is taken by the protector instead. Does not apply to status damage.
class ProtectedEffect(Effect):
    def __init__(self, name, duration, is_buff, cc_immunity=False, protector=None, multiplier=1.0):
        super().__init__(name, duration, is_buff, cc_immunity=False)
        self.cc_immunity = cc_immunity
        self.protector = protector
        self.multiplier = multiplier

    def protected_applyEffectDuringDamageStep(self, character, damage, attacker, func_after_dmg):
        if self.protector is None:
            raise Exception
        if self.protector.isAlive():
            damage = damage * self.multiplier
            self.protector.takeDamage(damage, attacker, func_after_dmg)
            return 0
        else:
            return damage
    
    def applyEffectOnTrigger(self, character):
        # Double check, the first is to handle cases of leaving party unexpectedly.
        if self.protector not in character.ally or self.protector.isDead():
            self.flag_for_remove = True

    def apply_effect_at_end_of_turn(self, character):
        if self.protector.isDead():
            self.flag_for_remove = True

    def tooltip_description(self):
        return f"Protected by {self.protector.name}."


# Stun effect
class StunEffect(Effect):
    def __init__(self, name, duration, is_buff, cc_immunity=False, delay_trigger=0):
        super().__init__(name, duration, is_buff, cc_immunity=False, delay_trigger=0)
        self.name = "Stun"
        self.is_buff = False
        self.cc_immunity = cc_immunity
        self.delay_trigger = delay_trigger
    
    def applyEffectOnApply(self, character):
        stats_dict = {"eva": -1.00}
        character.updateStats(stats_dict, reversed=False) # Eva can be lower than 0, which makes sense.

    def applyEffectOnRemove(self, character):
        stats_dict = {"eva": 1.00}
        character.updateStats(stats_dict, reversed=False)
    
    def tooltip_description(self):
        return "Cannot take action and evade is reduced by 100%."


# Sleep effect
class SleepEffect(Effect):
    def __init__(self, name, duration, is_buff, cc_immunity=False, delay_trigger=0):
        super().__init__(name, duration, is_buff, cc_immunity=False, delay_trigger=0)
        self.name = "Sleep"
        self.is_buff = False
        self.cc_immunity = cc_immunity
        self.delay_trigger = delay_trigger
    
    def applyEffectDuringDamageStep(self, character, damage):
        self.flag_for_remove = True
        return damage

    def tooltip_description(self):
        return "Cannot act, effect is removed when taking damage."


class StatsEffect(Effect):
    def __init__(self, name, duration, is_buff, stats_dict=None, condition=None, use_active_flag=True, stats_dict_function=None, is_set_effect=False):
        super().__init__(name, duration, is_buff, cc_immunity=False, delay_trigger=0)
        self.stats_dict = stats_dict
        # Condition function. If condition is not None, effect applys normally, but will not immediately trigger until condition is met,
        # triggers if a line cross is detected.
        self.condition = condition
        self.flag_is_active = False
        # If use_active_flag is False, effect applys normally, trigger every turn as long as condition is met.
        self.use_active_flag = use_active_flag
        # Stats dict manipulation function. For when use_active_flag is False, dynamiclly update stats_dict.
        self.stats_dict_function = stats_dict_function
        # Pay attention here:
        if self.stats_dict_function:
            self.stats_dict = self.stats_dict_function()
        self.is_set_effect = is_set_effect

    def applyEffectOnApply(self, character):
        if self.condition is None:
            character.updateStats(self.stats_dict, reversed=False)
            self.flag_is_active = True

    def applyEffectOnRemove(self, character):
        if self.condition is None:
            character.updateStats(self.stats_dict, reversed=True)

    def applyEffectOnTrigger(self, character):
        if self.condition is not None and self.use_active_flag:
            if self.condition(character) and self.flag_is_active == False:
                character.updateStats(self.stats_dict, reversed=False)
                self.flag_is_active = True
            elif self.condition(character) and self.flag_is_active == True:
                return
            elif not self.condition(character) and self.flag_is_active == False:
                fine_print(f"The effect of {self.name} is not triggered because condition is not met.", mode=character.fineprint_mode)
                return
            elif not self.condition(character) and self.flag_is_active == True:
                character.updateStats(self.stats_dict, reversed=True)
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
                        character.updateStats(old_stats_dict, reversed=True)
                        self.stats_dict = new_stats_dict
                        character.updateStats(self.stats_dict, reversed=False)
                else:
                    character.updateStats(self.stats_dict, reversed=False)
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
            if not self.use_active_flag:
                string += "Effect applys every turn as long as being active.\n"
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
    def __init__(self, name, duration, is_buff, value):
        super().__init__(name, duration, is_buff)
        self.value = value
    
    def applyEffectOnTrigger(self, character):
        # Every turn, raise by 0.01(1%).
        stats_dict = {"crit": 0.01, "critdmg": 0.01}
        character.updateStats(stats_dict, reversed=False)
    
    def tooltip_description(self):
        return f"Critical rate and critical damage is increased by {self.value*100}% each turn."


# ---------------------------------------------------------
# Continuous Damage effect
class ContinuousDamageEffect(Effect):
    def __init__(self, name, duration, is_buff, value):
        super().__init__(name, duration, is_buff)
        self.value = float(value)
        self.is_buff = is_buff
    
    def applyEffectOnTrigger(self, character):
        character.takeStatusDamage(self.value, self)
    
    def tooltip_description(self):
        return f"Take {int(self.value)} status damage each turn."


# ---------------------------------------------------------
# Continuous Heal effect
class ContinuousHealEffect(Effect):
    def __init__(self, name, duration, is_buff, value, is_percent=False):
        super().__init__(name, duration, is_buff)
        self.value = float(value)
        self.is_buff = is_buff
        self.is_percent = is_percent
    
    def applyEffectOnTrigger(self, character):
        if character.isDead():
            return
        if self.is_percent:
            character.healHp(character.maxhp * self.value, self)
        else:
            character.healHp(self.value, self)
    
    def tooltip_description(self):
        if self.is_percent:
            return f"Heal for {int(self.value*100)}% hp each turn."
        else:
            return f"Heal for {int(self.value)} hp each turn."


#---------------------------------------------------------
# Absorption Shield effect
class AbsorptionShield(Effect):
    def __init__(self, name, duration, is_buff, shield_value, cc_immunity, running=False, logging=False, text_box=None):
        super().__init__(name, duration, is_buff, cc_immunity=False)
        self.shield_value = shield_value
        self.is_buff = is_buff
        self.cc_immunity = cc_immunity
        self.running = running
        self.logging = logging
        self.text_box = text_box

    def applyEffectDuringDamageStep(self, character, damage):
        if damage > self.shield_value:
            remaining_damage = damage - self.shield_value
            if self.running and self.logging:
                self.text_box.append_html_text(f"{character.name}'s shield is broken!\n{remaining_damage} damage is dealt to {character.name}.\n")
            fine_print(f"{character.name}'s shield is broken! {remaining_damage} damage is dealt to {character.name}.", mode=character.fineprint_mode)
            character.removeEffect(self)
            return remaining_damage
        else:
            self.shield_value -= damage
            if self.running and self.logging:
                self.text_box.append_html_text(f"{character.name}'s shield absorbs {damage} damage.\nRemaining shield: {self.shield_value}\n")
            fine_print(f"{character.name}'s shield absorbs {damage} damage. Remaining shield: {self.shield_value}", mode=character.fineprint_mode)
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
# Only used by Fenrir
class EffectShield1(Effect):
    def __init__(self, name, duration, is_buff, threshold, heal_value, cc_immunity):
        super().__init__(name, duration, is_buff, cc_immunity=False)
        self.is_buff = is_buff
        self.threshold = threshold
        self.heal_value = heal_value
        self.cc_immunity = cc_immunity

    def apply_effect_at_end_of_turn(self, character):
        character.updateAllyEnemy()
        if character.has_neighbor("Fenrir") == False:
            self.flag_for_remove = True

    def applyEffectDuringDamageStep(self, character, damage):
        if character.hp < character.maxhp * self.threshold:
            character.healHp(self.heal_value, self)
        return damage
    
    def tooltip_description(self):
        return f"When hp is below {self.threshold*100}%, heal for {self.heal_value} hp before damage calculation."


#---------------------------------------------------------
# Effect shield 2 (When taking damage that would exceed 10% of maxhp, reduce damage above 10% of maxhp by 50%. 
# For every turn passed, damage reduction effect is reduced by 2%.)
# Only used by Chiffon
class EffectShield2(Effect):
    def __init__(self, name, duration, is_buff, cc_immunity, damage_reduction=0.5, shrink_rate=0.02):
        super().__init__(name, duration, is_buff, cc_immunity=False)
        self.is_buff = is_buff
        self.cc_immunity = cc_immunity
        self.damage_reduction = damage_reduction
        self.shrink_rate = shrink_rate

    def applyEffectDuringDamageStep(self, character, damage):
        if damage > character.maxhp * 0.1:
            damage = character.maxhp * 0.1 + (damage - character.maxhp * 0.1) * self.damage_reduction
        return damage
    
    def applyEffectOnTrigger(self, character):
        self.damage_reduction = max(self.damage_reduction - self.shrink_rate, 0)
        if self.damage_reduction == 0:
            self.flag_for_remove = True
    
    def tooltip_description(self):
        return f"Current damage reduction: {self.damage_reduction*100}%."



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
            if hasattr(character, "after_revive"):
                character.after_revive()
            character.removeEffect(self)

    def tooltip_description(self):
        return f"Revive with {self.effect_value*100}% hp the turn after fallen."

#---------------------------------------------------------
# Cancellation Shield effect (cancel 1 attack if attack damage exceed certain amount of max hp)
class CancellationShield(Effect):
    def __init__(self, name, duration, is_buff, threshold, cc_immunity, running=False, logging=False, text_box=None):
        super().__init__(name, duration, is_buff, cc_immunity=False)
        self.is_buff = is_buff
        self.threshold = threshold
        self.cc_immunity = cc_immunity
        self.running = running
        self.logging = logging
        self.text_box = text_box

    def applyEffectDuringDamageStep(self, character, damage):
        if damage > character.maxhp * self.threshold:
            character.removeEffect(self)
            if self.running and self.logging:
                self.text_box.append_html_text(f"{character.name} shielded the attack!\n")
            fine_print(f"{character.name} shielded the attack!", mode=character.fineprint_mode)
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
# Arasaka
# Leave with 1 hp when taking fatal damage. Immune to damage for 3 turns.
class EquipmentSetEffect_Arasaka(Effect):
    def __init__(self, name, duration, is_buff, cc_immunity, running=False, logging=False, text_box=None):
        super().__init__(name, duration, is_buff, cc_immunity=False)
        self.is_buff = is_buff
        self.cc_immunity = cc_immunity
        self.is_set_effect = True
        self.onehp_effect_triggered = False
        self.running = running
        self.logging = logging
        self.text_box = text_box

    def applyEffectDuringDamageStep(self, character, damage):
        if self.onehp_effect_triggered:
            return 0
        if damage >= character.hp:
            character.hp = 1
            if self.running and self.logging:
                self.text_box.append_html_text(f"{character.name} survived with 1 hp!\n")
            fine_print(f"{character.name} survived with 1 hp!", mode=character.fineprint_mode)
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
    def __init__(self, name, duration, is_buff, shield_value, cc_immunity, running=False, logging=False, text_box=None):
        super().__init__(name, duration, is_buff, cc_immunity=False)
        self.shield_value = shield_value
        self.is_buff = is_buff
        self.cc_immunity = cc_immunity
        self.is_set_effect = True
        self.running = running
        self.logging = logging
        self.text_box = text_box

    def applyEffectDuringDamageStep(self, character, damage):
        if damage > self.shield_value:
            remaining_damage = damage - self.shield_value
            if self.running and self.logging:
                self.text_box.append_html_text(f"{character.name}'s shield is broken!\n{remaining_damage} damage is dealt to {character.name}.\n")
            fine_print(f"{character.name}'s shield is broken! {remaining_damage} damage is dealt to {character.name}.", mode=character.fineprint_mode)
            character.removeEffect(self)
            return remaining_damage
        else:
            self.shield_value -= damage
            if self.running and self.logging:
                self.text_box.append_html_text(f"{character.name}'s shield absorbs {damage} damage.\nRemaining shield: {self.shield_value}\n")
            fine_print(f"{character.name}'s shield absorbs {damage} damage. Remaining shield: {self.shield_value}", mode=character.fineprint_mode)
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

    def applyEffectOnTrigger(self, character):
        if self.condition is not None:
            if self.condition(character) and not self.flag_is_active:
                character.updateStats(self.stats_dict, reversed=False)
                self.flag_is_active = True
            elif self.condition(character) and self.flag_is_active:
                return
            elif not self.condition(character) and not self.flag_is_active:
                fine_print(f"The effect of {self.name} is not yet triggered because condition is not met.", mode=character.fineprint_mode)
                return
            elif not self.condition(character) and self.flag_is_active:
                character.updateStats(self.stats_dict, reversed=True)
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

    def applyEffectOnApply(self, character):
        # if self.stats_dict_function:
        #     self.stats_dict = self.stats_dict_function()
        # We do not call the function here, because in this specific case, character.ally() just got reset and is empty.
        character.updateStats(self.stats_dict, reversed=False)

    def applyEffectOnRemove(self, character):
        character.updateStats(self.stats_dict, reversed=True)

    def applyEffectOnTrigger(self, character):
        old_stats_dict = self.stats_dict
        new_stats_dict = self.stats_dict_function()
        if new_stats_dict != old_stats_dict:
            character.updateStats(old_stats_dict, reversed=True)
            self.stats_dict = new_stats_dict
            character.updateStats(self.stats_dict, reversed=False)

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
# Accumulate 1 stack of Sovereign when taking damage. Each stack increase atk by 20% and last 4 turns. Max 5 stacks.
class EquipmentSetEffect_Sovereign(Effect):
    def __init__(self, name, duration, is_buff, stats_dict=None, stats_dict_function=None):
        super().__init__(name, duration, is_buff, cc_immunity=False, delay_trigger=0)
        self.is_set_effect = True
        self.stats_dict = stats_dict
        self.flag_is_active = False
        self.stats_dict_function = stats_dict_function

    def applyEffectDuringDamageStep(self, character, damage):
        # count how many "Sovereign" in character.buffs, if less than 5, apply effect.
        if Counter([effect.name for effect in character.buffs])["Sovereign"] < 5:
            character.applyEffect(StatsEffect("Sovereign", 4, True, self.stats_dict, is_set_effect=True))
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

    def get_new_bonus_dict(self):
        new_bonus_dict = {}
        for key, value in self.bonus_stats_dict.items():
            new_bonus_dict[key] = value + self.activation_count * 0.25
        return new_bonus_dict

    def apply_effect_custom(self):
        self.collected_pieces += 1
        self.collected_pieces = min(self.collected_pieces, 6)

    def applyEffectOnTrigger(self, character):
        if character.isDead():
            return
        if self.collected_pieces >= 6:
            self.activation_count += 1
            character.applyEffect(StatsEffect("Snowflake", 6, True, self.get_new_bonus_dict(), is_set_effect=True))
            character.healHp(character.maxhp * 0.25 * self.activation_count, self)
            self.collected_pieces = 0

    def tooltip_description(self):
        return f"Collected pieces: {self.collected_pieces}, Activation count: {self.activation_count}. Collect 6 pieces to activate effect."
