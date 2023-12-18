# handle cases of battle_simulator is partailly imported
try:
    from battle_simulator import running, logging, text_box
except ImportError:
    running = False
    logging = False
    text_box = None


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
    def __init__(self, duration, cc_immunity=False, delay_trigger=0):
        self.duration = duration
        self.name = "Stun"
        self.is_buff = False
        self.cc_immunity = cc_immunity
        self.delay_trigger = delay_trigger
        self.flag_for_remove = False
    
    def applyEffectOnApply(self, character):
        character.updateEva(-1, True) # Eva can be lower than 0, which makes sense.

    def applyEffectOnRemove(self, character):
        character.updateEva(1, True)
    
    def tooltip_description(self):
        return "Cannot take action and evade is reduced by 100%."


# Speed effect
class SpeedEffect(Effect):
    def __init__(self, name, duration, is_buff, value, is_flat):
        super().__init__(name, duration, is_buff)
        self.value = value
        self.is_flat = is_flat
    
    def applyEffectOnApply(self, character):
        character.updateSpd(self.value, self.is_flat)
    
    def applyEffectOnRemove(self, character):
        if self.is_flat:
            character.updateSpd(-self.value, self.is_flat)
        else:
            character.updateSpd(1/self.value, self.is_flat)

    def tooltip_description(self):
        if self.is_flat:
            return f"Speed is increased by {self.value}."
        else:
            return f"Speed is scaled to {self.value*100}%."


# ---------------------------------------------------------
# Critical rate and critical damage effect, for character Seth. Effect increases every turn.
class SethEffect(Effect):
    def __init__(self, name, duration, is_buff, value):
        super().__init__(name, duration, is_buff)
        self.value = value
    
    def applyEffectOnTrigger(self, character):
        # Every turn, raise by 0.01(1%).
        character.updateCrit(self.value, True)
        character.updateCritdmg(self.value, True)
    
    def tooltip_description(self):
        return f"Critical rate and critical damage is increased by {self.value*100}% each turn."

# ---------------------------------------------------------
# Attack effect
class AttackEffect(Effect):
    def __init__(self, name, duration, is_buff, value, is_flat):
        super().__init__(name, duration, is_buff)
        self.value = value
        self.is_flat = is_flat
    
    def applyEffectOnApply(self, character):
        character.updateAtk(self.value, self.is_flat)
    
    def applyEffectOnRemove(self, character):
        if self.is_flat:
            character.updateAtk(-self.value, self.is_flat)
        else:
            character.updateAtk(1/self.value, self.is_flat)
    
    def tooltip_description(self):
        if self.is_flat:
            return f"Attack is increased by {self.value}."
        else:
            return f"Attack is scaled to {self.value*100}%."

# ---------------------------------------------------------
# Defense effect
class DefenseEffect(Effect):
    def __init__(self, name, duration, is_buff, value, is_flat):
        super().__init__(name, duration, is_buff)
        self.value = value
        self.is_flat = is_flat
    
    def applyEffectOnApply(self, character):
        character.updateDef(self.value, self.is_flat)
    
    def applyEffectOnRemove(self, character):
        if self.is_flat:
            character.updateDef(-self.value, self.is_flat)
        else:
            character.updateDef(1/self.value, self.is_flat)

    def tooltip_description(self):
        if self.is_flat:
            return f"Defense is increased by {self.value}."
        else:
            return f"Defense is scaled to {self.value*100}%."


# ---------------------------------------------------------
# Continuous Damage effect
class ContinuousDamageEffect(Effect):
    def __init__(self, name, duration, is_buff, value):
        super().__init__(name, duration, is_buff)
        self.value = float(value)
        self.is_buff = is_buff
    
    def applyEffectOnTrigger(self, character):
        print(f"{character.name} is taking {self.value} status damage")
        character.takeStatusDamage(self.value, self)
    
    def tooltip_description(self):
        return f"Take {int(self.value)} status damage each turn."

#---------------------------------------------------------
# Absorption Shield effect
class AbsorptionShield(Effect):
    def __init__(self, name, duration, is_buff, shield_value, cc_immunity):
        super().__init__(name, duration, is_buff, cc_immunity=False)
        self.shield_value = shield_value
        self.is_buff = is_buff
        self.cc_immunity = cc_immunity

    def applyEffectDuringDamageStep(self, character, damage):
        if damage > self.shield_value:
            remaining_damage = damage - self.shield_value
            if running and logging:
                text_box.append_html_text(f"{character.name}'s shield is broken!\n{remaining_damage} damage is dealt to {character.name}.\n")
            print(f"{character.name}'s shield is broken! {remaining_damage} damage is dealt to {character.name}.")
            character.removeEffect(self)
            return remaining_damage
        else:
            self.shield_value -= damage
            if running and logging:
                text_box.append_html_text(f"{character.name}'s shield absorbs {damage} damage.\nRemaining shield: {self.shield_value}\n")
            print(f"{character.name}'s shield absorbs {damage} damage. Remaining shield: {self.shield_value}")
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
    def __init__(self, name, duration, is_buff, threshold, cc_immunity):
        super().__init__(name, duration, is_buff, cc_immunity=False)
        self.is_buff = is_buff
        self.threshold = threshold
        self.cc_immunity = cc_immunity

    def applyEffectDuringDamageStep(self, character, damage):
        if damage > character.maxhp * self.threshold:
            character.removeEffect(self)
            if running and logging:
                text_box.append_html_text(f"{character.name} shielded the attack!\n")
            print(f"{character.name} shielded the attack!")
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