from collections import Counter



def fine_print(*args, mode="default", **kwargs):
    if mode == "file":
        with open("logs.txt", "a") as f:
            print(*args, file=f, **kwargs)
    elif mode == "suppress":
        pass
    else:
        print(*args, **kwargs)

class Effect:
    def __init__(self, name, duration, is_buff, cc_immunity=False, delay_trigger=0):
        self.name = name
        self.duration = duration
        self.is_buff = bool(is_buff)
        self.cc_immunity = bool(cc_immunity)
        self.delay_trigger = delay_trigger # number of turns before effect is triggered
        self.flag_for_remove = False # If True, will be removed at the beginning of the next turn.
    
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

    def tooltip_description(self):
        return f"Normal and skill attack damage is taken by {self.protector.name} instead. Cannot protect against status effects and damage."


# Stun effect
class StunEffect(Effect):
    def __init__(self, name, duration, is_buff, cc_immunity=False, delay_trigger=0):
        super().__init__(name, duration, is_buff, cc_immunity=False, delay_trigger=0)
        self.name = "Stun"
        self.is_buff = False
        self.cc_immunity = cc_immunity
        self.delay_trigger = delay_trigger
        self.flag_for_remove = False
    
    def applyEffectOnApply(self, character):
        stats_dict = {"eva": -1.00}
        character.updateStats(stats_dict, reversed=False) # Eva can be lower than 0, which makes sense.

    def applyEffectOnRemove(self, character):
        stats_dict = {"eva": 1.00}
        character.updateStats(stats_dict, reversed=False)
    
    def tooltip_description(self):
        return "Cannot take action and evade is reduced by 100%."


class StatsEffect(Effect):
    def __init__(self, name, duration, is_buff, stats_dict=None, condition=None, use_active_flag=True, stats_dict_function=None):
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
                string += f"{key} is increased by {value*100}%."
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
class EffectShield1(Effect):
    def __init__(self, name, duration, is_buff, threshold, heal_value, cc_immunity):
        super().__init__(name, duration, is_buff, cc_immunity=False)
        self.is_buff = is_buff
        self.threshold = threshold
        self.heal_value = heal_value
        self.cc_immunity = cc_immunity

    def applyEffectDuringDamageStep(self, character, damage):
        if character.hp < character.maxhp * self.threshold:
            character.healHp(self.heal_value, self)
        return damage
    
    def tooltip_description(self):
        return f"When hp is below {self.threshold*100}%, heal for {self.heal_value} hp before damage calculation."


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
        return f"Leave with 1 hp when about to take fatal damage, after that, gain immunity to damage for 3 turns."


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
# Accumulate 1 stack of Sovereign when taking damage. Each stack increase atk by 5% and last 3 turns. Max 5 stacks.
class EquipmentSetEffect_Sovereign(Effect):
    def __init__(self, name, duration, is_buff, stats_dict=None, stats_dict_function=None):
        super().__init__(name, duration, is_buff, cc_immunity=False, delay_trigger=0)
        self.is_set_effect = True
        self.stats_dict = stats_dict
        self.flag_is_active = False
        self.stats_dict_function = stats_dict_function

    def applyEffectDuringDamageStep(self, character, damage):
        # count how many "Sovereign" in character.buffs, if less than 7, apply effect.
        if Counter([effect.name for effect in character.buffs])["Sovereign"] < 6:
            character.applyEffect(StatsEffect("Sovereign", 3, True, self.stats_dict))
        return damage
    
    def tooltip_description(self):
        return f"Accumulate 1 stack of Sovereign when taking damage. Each stack increase atk by {self.stats_dict['atk']*100}% and last 3 turns. Max 5 stacks."
