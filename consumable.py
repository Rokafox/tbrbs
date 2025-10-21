from block import *
from effect import *
import random

from equip import generate_equips_list, adventure_generate_random_equip_with_weight


# NOTE:
# 1. name must be equal to class name, see load_player() in bs
# 2. Every time a new consumable is added, add it to get_1_random_consumable() in consumable.py, and also in shop.py.


def food_package_distribute_sum(objects: list, target_sum=100, min_value=1):
    """
    Modify objects in place so that the sum of their current_stack attributes equals target_sum.
    Each current_stack value will be at least min_value and appear random.
    Function by AI.
    """
    n = len(objects)
    if n == 0:
        raise ValueError("No objects to distribute values to.")
    if n * min_value > target_sum:
        raise ValueError(f"Cannot distribute {target_sum} among {n} objects with minimum {min_value}")
    values = [min_value] * n
    remaining = target_sum - sum(values)
    # Distribute remaining using random partition
    if remaining > 0:
        # Generate n-1 random split points
        splits = sorted([random.randint(0, remaining) for _ in range(n - 1)])
        partition = [splits[0]] + [splits[i] - splits[i-1] for i in range(1, n-1)] + [remaining - splits[-1]]
        for i in range(n):
            values[i] += partition[i]
    for i, obj in enumerate(objects):
        obj.current_stack = values[i]


# Price : common < uncommon < rare < epic < unique < legendary, 50, 100, 250, 500, 1000, 2500
class Consumable(Block):
    def __init__(self, name, description):
        super().__init__(name, description)
        self.can_use_for_auto_battle = True
        self.can_use_on_dead = False
        self.mark_for_removal = False

    def auto_E_condition(self, user, player):
        """
        Returns True if the item should be used automatically.
        """
        if not self.can_use_on_dead and user.is_dead():
            return False
        else:
            return True

#==================================================================================================
# Equip Chests
#==================================================================================================
class EquipPackage(Consumable):
    def __init__(self, stack: int):
        super().__init__("Common Chest", "Obtain 100 random common rarity equipment.")
        self.image = "wood_chest_birch"
        self.rarity = "Common"
        self.type = "Eqpackage"
        self.current_stack = max(1, stack)
        self.current_stack = min(self.current_stack, self.max_stack)
        self.market_value = 5000
        self.can_use_for_auto_battle = False

    def E(self, user, player):
        return f"{user.name} obtained a bunch of equipment from {self.name}."

    def E_actual(self, user, player):
        equips = generate_equips_list(100, eq_level=1, locked_rarity="Common")
        player.add_package_of_items_to_inventory(equips)
        return None

    def auto_E_condition(self, user, player):
        return False


class EquipPackage2(Consumable):
    def __init__(self, stack: int):
        super().__init__("Uncommon Chest", "Obtain 100 random uncommon rarity equipment.")
        self.image = "wood_chest"
        self.rarity = "Uncommon"
        self.type = "Eqpackage"
        self.current_stack = max(1, stack)
        self.current_stack = min(self.current_stack, self.max_stack)
        self.market_value = 10000
        self.can_use_for_auto_battle = False

    def E(self, user, player):
        return f"{user.name} obtained a bunch of equipment from {self.name}."

    def E_actual(self, user, player):
        equips = generate_equips_list(100, eq_level=1, locked_rarity="Uncommon")
        player.add_package_of_items_to_inventory(equips)
        return None

    def auto_E_condition(self, user, player):
        return False


class EquipPackage3(Consumable):
    def __init__(self, stack: int):
        super().__init__("Rare Chest", "Obtain 100 random rare rarity equipment.")
        self.image = "wood_chest_maple"
        self.rarity = "Rare"
        self.type = "Eqpackage"
        self.current_stack = max(1, stack)
        self.current_stack = min(self.current_stack, self.max_stack)
        self.market_value = 25000
        self.can_use_for_auto_battle = False

    def E(self, user, player):
        return f"{user.name} obtained a bunch of equipment from {self.name}."

    def E_actual(self, user, player):
        equips = generate_equips_list(100, eq_level=1, locked_rarity="Rare")
        player.add_package_of_items_to_inventory(equips)
        return None

    def auto_E_condition(self, user, player):
        return False


class EquipPackage4(Consumable):
    def __init__(self, stack: int):
        super().__init__("Epic Chest", "Obtain 100 random epic rarity equipment.")
        self.image = "wood_chest_mahogany"
        self.rarity = "Epic"
        self.type = "Eqpackage"
        self.current_stack = max(1, stack)
        self.current_stack = min(self.current_stack, self.max_stack)
        self.market_value = 50000
        self.can_use_for_auto_battle = False

    def E(self, user, player):
        return f"{user.name} obtained a bunch of equipment from {self.name}."

    def E_actual(self, user, player):
        equips = generate_equips_list(100, eq_level=1, locked_rarity="Epic")
        player.add_package_of_items_to_inventory(equips)
        return None

    def auto_E_condition(self, user, player):
        return False


class EquipPackage5(Consumable):
    def __init__(self, stack: int):
        super().__init__("Unique Chest", "Obtain 100 random unique rarity equipment.")
        self.image = "wood_chest_silver"
        self.rarity = "Unique"
        self.type = "Eqpackage"
        self.current_stack = max(1, stack)
        self.current_stack = min(self.current_stack, self.max_stack)
        self.market_value = 100000
        self.can_use_for_auto_battle = False

    def E(self, user, player):
        return f"{user.name} obtained a bunch of equipment from {self.name}."

    def E_actual(self, user, player):
        equips = generate_equips_list(100, eq_level=1, locked_rarity="Unique")
        player.add_package_of_items_to_inventory(equips)
        return None

    def auto_E_condition(self, user, player):
        return False


class EquipPackage6(Consumable):
    def __init__(self, stack: int):
        super().__init__("Legendary Chest", "Obtain 100 random legendary rarity equipment.")
        self.image = "wood_chest_gold"
        self.rarity = "Legendary"
        self.type = "Eqpackage"
        self.current_stack = max(1, stack)
        self.current_stack = min(self.current_stack, self.max_stack)
        self.market_value = 250000
        self.can_use_for_auto_battle = False

    def E(self, user, player):
        return f"{user.name} obtained a bunch of equipment from {self.name}."

    def E_actual(self, user, player):
        equips = generate_equips_list(100, eq_level=1, locked_rarity="Legendary")
        player.add_package_of_items_to_inventory(equips)
        return None

    def auto_E_condition(self, user, player):
        return False



class EquipPackageBrandSpecific(Consumable):
    def __init__(self, stack: int, brand: str):
        super().__init__(f"{brand} Chest", f"Obtain 100 random {brand} equipment.")
        self.brand = brand
        self.image = "special_chest"
        self.rarity = "Epic"
        self.type = "Eqpackage"
        self.eq_set = self.brand
        self.current_stack = max(1, stack)
        self.current_stack = min(self.current_stack, self.max_stack)
        self.market_value = 500000
        self.can_use_for_auto_battle = False

    def E(self, user, player):
        return f"{user.name} obtained a bunch of equipment from {self.name}."

    def E_actual(self, user, player):
        equips = generate_equips_list(100, eq_level=1, locked_eq_set=self.brand)
        player.add_package_of_items_to_inventory(equips)
        return None

    def auto_E_condition(self, user, player):
        return False





#==================================================================================================
# Food Sacks
#==================================================================================================

class FoodPackage(Consumable):
    def __init__(self, stack: int):
        super().__init__("Uncommon Sack", "Obtain 100 random common or uncommon rarity food.")
        self.image = "large_sack_old_worn"
        self.rarity = "Uncommon"
        self.type = "Foodpackage"
        self.current_stack = max(1, stack)
        self.current_stack = min(self.current_stack, self.max_stack)
        self.market_value = 120000
        self.can_use_for_auto_battle = False

    def E(self, user, player):
        return f"{user.name} obtained some food from {self.name}."

    def E_actual(self, user, player):
        # find in current module all classes that are subclass of Consumable, and type is "Food"
        # and rarity is "Common" or "Uncommon", create a list of 100 of them
        all_subclasses = Consumable.__subclasses__()
        food_list = []
        for c in all_subclasses:
            try:
                instance = c(1)
            except TypeError:
                # EquipPackageBrandSpecific needs 2 arguments
                continue
            if instance.type == "Food" and instance.rarity in ["Common", "Uncommon"]:
                food_list.append(instance)

        # Now we have for example [Banana(1), Kiwi(1)], but 100 is needed, so a random combination with the sum of 100,
        # for example [Banana(50), Kiwi(50)] is needed.
        food_package_distribute_sum(food_list, target_sum=100)
        player.add_package_of_items_to_inventory(food_list)
        return None

    def auto_E_condition(self, user, player):
        return False



class FoodPackage2(Consumable):
    def __init__(self, stack: int):
        super().__init__("Rare Sack", "Obtain 100 random rare or epic rarity food.")
        self.image = "large_sack"
        self.rarity = "Epic"
        self.type = "Foodpackage"
        self.current_stack = max(1, stack)
        self.current_stack = min(self.current_stack, self.max_stack)
        self.market_value = 400000
        self.can_use_for_auto_battle = False

    def E(self, user, player):
        return f"{user.name} obtained some food from {self.name}."

    def E_actual(self, user, player):
        all_subclasses = Consumable.__subclasses__()
        food_list = []
        for c in all_subclasses:
            try:
                instance = c(1)
            except TypeError:
                # EquipPackageBrandSpecific needs 2 arguments
                continue
            if instance.type == "Food" and instance.rarity in ["Rare", "Epic"]:
                food_list.append(instance)

        food_package_distribute_sum(food_list, target_sum=100)
        player.add_package_of_items_to_inventory(food_list)
        return None

    def auto_E_condition(self, user, player):
        return False


class FoodPackage3(Consumable):
    def __init__(self, stack: int):
        super().__init__("Unique Sack", "Obtain 100 random unique or legendary rarity food.")
        self.image = "food_basket"
        self.rarity = "Legendary"
        self.type = "Foodpackage"
        self.current_stack = max(1, stack)
        self.current_stack = min(self.current_stack, self.max_stack)
        self.market_value = 1000000
        self.can_use_for_auto_battle = False

    def E(self, user, player):
        return f"{user.name} obtained some food from {self.name}."

    def E_actual(self, user, player):
        all_subclasses = Consumable.__subclasses__()
        food_list = []
        for c in all_subclasses:
            try:
                instance = c(1)
            except TypeError:
                # EquipPackageBrandSpecific needs 2 arguments
                continue
            if instance.type == "Food" and instance.rarity in ["Unique", "Legendary"]:
                food_list.append(instance)

        food_package_distribute_sum(food_list, target_sum=100)
        player.add_package_of_items_to_inventory(food_list)
        return None

    def auto_E_condition(self, user, player):
        return False



#==================================================================================================
# Food
#==================================================================================================
# Common
class Apple(Consumable):
    def __init__(self, stack: int):
        super().__init__("Apple", "ATK + 10% for 16-20 turns.")
        self.description += " When same effect is applied, duration is refreshed."
        self.image = "food_apple"
        self.rarity = "Common"
        self.type = "Food"
        self.current_stack = max(1, stack)
        self.current_stack = min(self.current_stack, self.max_stack)
        self.market_value = 800

    def E(self, user, player):
        d = random.randint(16, 20)
        apple_effect = StatsEffect('Apple', d, True, {"atk": 1.1})
        apple_effect.additional_name = "Food_Apple"
        apple_effect.set_apply_rule("stack")
        user.apply_effect(apple_effect)
        return f"{user.name} applied Apple for {d} turns."
    
    def auto_E_condition(self, user, player):
        if not self.can_use_on_dead and user.is_dead():
            return False
        else:
            if user.has_effect_that_named(effect_name="Apple", additional_name="Food_Apple"):
                return False
            else:
                return True


class Coconuts(Consumable):
    def __init__(self, stack: int):
        super().__init__("Coconuts", "DEF + 10% for 16-20 turns.")
        self.description += " When same effect is applied, duration is refreshed."
        self.image = "food_coconuts"
        self.rarity = "Common"
        self.type = "Food"
        self.current_stack = max(1, stack)
        self.current_stack = min(self.current_stack, self.max_stack)
        self.market_value = 800

    def E(self, user, player):
        d = random.randint(16, 20)
        coconuts_effect = StatsEffect('Coconuts', d, True, {"defense": 1.1})
        coconuts_effect.additional_name = "Food_Coconuts"
        coconuts_effect.set_apply_rule("stack")
        user.apply_effect(coconuts_effect)
        return f"{user.name} applied Coconuts for {d} turns."
    
    def auto_E_condition(self, user, player):
        if not self.can_use_on_dead and user.is_dead():
            return False
        else:
            if user.has_effect_that_named(effect_name="Coconuts", additional_name="Food_Coconuts"):
                return False
            else:
                return True


class Banana(Consumable):
    def __init__(self, stack: int):
        super().__init__("Banana", "Recover approximatly 30000 hp.")
        self.image = "banana"
        self.rarity = "Common"
        self.type = "Food"
        self.current_stack = max(1, stack)
        self.current_stack = min(self.current_stack, self.max_stack)
        self.market_value = 800

    def E(self, user, player):
        # random 0.8-1.2
        heal_amount = 30000 * random.uniform(0.8, 1.2)
        user.heal_hp(heal_amount, self)
        return f"{user.name} healed {heal_amount} hp by {self.name}."
    
    def auto_E_condition(self, user, player):
        if not self.can_use_on_dead and user.is_dead():
            return False
        else:
            return user.hp < user.maxhp - 30000


class Orange(Consumable):
    def __init__(self, stack: int):
        super().__init__("Orange", "Apply Shield to user for 8-9 turns. Shield absorbs approximatly 22500 damage.")
        self.description += " When same effect is applied, duration is refreshed."
        self.image = "food_orange"
        self.rarity = "Common"
        self.type = "Food"
        self.current_stack = max(1, stack)
        self.current_stack = min(self.current_stack, self.max_stack)
        self.market_value = 800

    def E(self, user, player):
        d = random.randint(8, 9)
        shield_amount = int(22500 * random.uniform(0.8, 1.2))
        orange_effect = AbsorptionShield('Orange', d, True, shield_amount, False)
        orange_effect.additional_name = "Food_Orange"
        orange_effect.set_apply_rule("stack")
        user.apply_effect(orange_effect)
        return f"{user.name} applied Orange for {d} turns."

    def auto_E_condition(self, user, player):
        if not self.can_use_on_dead and user.is_dead():
            return False
        else:
            if user.has_effect_that_named(effect_name="Orange", additional_name="Food_Orange"):
                return False
            else:
                return True


# Uncommon
class Kiwi(Consumable):
    def __init__(self, stack: int):
        super().__init__("Kiwi", "Recover approximatly 70000 hp.")
        self.image = "kiwi"
        self.rarity = "Uncommon"
        self.type = "Food"
        self.current_stack = max(1, stack)
        self.current_stack = min(self.current_stack, self.max_stack)
        self.market_value = 1500

    def E(self, user, player):
        # random 0.8-1.2
        heal_amount = 70000 * random.uniform(0.8, 1.2)
        user.heal_hp(heal_amount, self)
        return f"{user.name} healed {heal_amount} hp by {self.name}."
    
    def auto_E_condition(self, user, player):
        if not self.can_use_on_dead and user.is_dead():
            return False
        else:
            return user.hp < user.maxhp - 70000
        

class Fried_Shrimp(Consumable):
    def __init__(self, stack: int):
        super().__init__("Fried Shrimp", "ATK + 15% for 17-21 turns.")
        self.description += " When same effect is applied, duration is refreshed."
        self.image = "food_fried_shrimp"
        self.rarity = "Uncommon"
        self.type = "Food"
        self.current_stack = max(1, stack)
        self.current_stack = min(self.current_stack, self.max_stack)
        self.market_value = 1500

    def E(self, user, player):
        d = random.randint(17, 21)
        fs_effect = StatsEffect('Fried Shrimp', d, True, {"atk": 1.15})
        fs_effect.additional_name = "Food_Fried_Shrimp"
        fs_effect.set_apply_rule("stack")
        user.apply_effect(fs_effect)
        return f"{user.name} applied Fried Shrimp for {d} turns."
    
    def auto_E_condition(self, user, player):
        if not self.can_use_on_dead and user.is_dead():
            return False
        else:
            if user.has_effect_that_named(effect_name="Fried Shrimp", additional_name="Food_Fried_Shrimp"):
                return False
            else:
                return True


class Pomegranate(Consumable):
    def __init__(self, stack: int):
        super().__init__("Pomegranate", "DEF + 15% for 17-21 turns.")
        self.description += " When same effect is applied, duration is refreshed."
        self.image = "food_pomegranate"
        self.rarity = "Uncommon"
        self.type = "Food"
        self.current_stack = max(1, stack)
        self.current_stack = min(self.current_stack, self.max_stack)
        self.market_value = 1500

    def E(self, user, player):
        d = random.randint(17, 21)
        pomo_effect = StatsEffect('Pomegranate', d, True, {"defense": 1.15})
        pomo_effect.additional_name = "Food_Pomegranate"
        pomo_effect.set_apply_rule("stack")
        user.apply_effect(pomo_effect)
        return f"{user.name} applied Pomegranate for {d} turns."

    def auto_E_condition(self, user, player):
        if not self.can_use_on_dead and user.is_dead():
            return False
        else:
            if user.has_effect_that_named(effect_name="Pomegranate", additional_name="Food_Pomegranate"):
                return False
            else:
                return True


# Rare
class Strawberry(Consumable):
    def __init__(self, stack: int):
        super().__init__("Strawberry", "")
        self.description = "Recover approximatly 150000 hp."
        self.image = "strawberry"
        self.rarity = "Rare"
        self.type = "Food"
        self.current_stack = max(1, stack)
        self.current_stack = min(self.current_stack, self.max_stack)
        self.market_value = 3000

    def E(self, user, player):
        # random 0.8-1.2
        heal_amount = 150000 * random.uniform(0.8, 1.2)
        user.heal_hp(heal_amount, self)
        # user.apply_effect(StatsEffect("Strawberry", 10, True, {"atk": 1.1}))
        return f"{user.name} healed {heal_amount} hp by {self.name}."
    
    def auto_E_condition(self, user, player):
        if not self.can_use_on_dead and user.is_dead():
            return False
        else:
            return user.hp < user.maxhp - 150000


class Orange_Juice_60(Consumable):
    def __init__(self, stack: int):
        super().__init__("60% Orange Juice", "Apply Shield to user for 8-10 turns. Shield absorbs approximatly 112500 damage.")
        self.description += " When same effect is applied, duration is refreshed."
        self.image = "food_orange_juice_60"
        self.rarity = "Rare"
        self.type = "Food"
        self.current_stack = max(1, stack)
        self.current_stack = min(self.current_stack, self.max_stack)
        self.market_value = 3000

    def E(self, user, player):
        d = random.randint(8, 10)
        shield_amount = int(112500 * random.uniform(0.8, 1.2))
        orangej_effect = AbsorptionShield('60% Orange Juice', d, True, shield_amount, False)
        orangej_effect.additional_name = "Food_Orange_Juice_60"
        orangej_effect.set_apply_rule("stack")
        user.apply_effect(orangej_effect)
        return f"{user.name} applied 60% Orange Juice for {d} turns."

    def auto_E_condition(self, user, player):
        if not self.can_use_on_dead and user.is_dead():
            return False
        else:
            if user.has_effect_that_named(effect_name="60% Orange Juice", additional_name="Food_Orange_Juice_60"):
                return False
            else:
                return True


class Milk(Consumable):
    def __init__(self, stack: int):
        super().__init__("Milk", "Gain EXP by approximately 20% of max EXP.")
        self.image = "food_milk"
        self.rarity = "Rare"
        self.type = "Food"
        self.current_stack = max(1, stack)
        self.current_stack = min(self.current_stack, self.max_stack)
        self.market_value = 3000
    def E(self, user, player):
        exp_gain = int(user.maxexp * 0.2 * random.uniform(0.8, 1.2))
        user.gain_exp(exp_gain)
        return f"{user.name} gained {exp_gain} EXP."
    def auto_E_condition(self, user, player):
        return False


class Sandwich(Consumable):
    def __init__(self, stack: int):
        super().__init__("Sandwich", "All stats + 5% for 18-22 turns.")
        self.description += " When same effect is applied, duration is refreshed."
        self.image = "food_sandwich"
        self.rarity = "Rare"
        self.type = "Food"
        self.current_stack = max(1, stack)
        self.current_stack = min(self.current_stack, self.max_stack)
        self.market_value = 3000

    def E(self, user, player):
        d = random.randint(18, 22)
        sandwich_effect = StatsEffect('Sandwich', d, True, {"atk": 1.05, "defense": 1.05, "spd": 1.05, "maxhp": 1.05})
        sandwich_effect.additional_name = "Food_Sandwich"
        sandwich_effect.set_apply_rule("stack")
        user.apply_effect(sandwich_effect)
        return f"{user.name} applied Sandwich for {d} turns."
    
    def auto_E_condition(self, user, player):
        if not self.can_use_on_dead and user.is_dead():
            return False
        else:
            if user.has_effect_that_named(effect_name="Sandwich", additional_name="Food_Sandwich"):
                return False
            else:
                return True


# Epic
class Pancake(Consumable):
    def __init__(self, stack: int):
        super().__init__("Pancake", "Recover approximatly 230000 hp.")
        self.image = "pancake"
        self.rarity = "Epic"
        self.type = "Food"
        self.current_stack = max(1, stack)
        self.current_stack = min(self.current_stack, self.max_stack)
        self.market_value = 5000

    def E(self, user, player):
        # random 0.8-1.2
        heal_amount = 230000 * random.uniform(0.8, 1.2)
        user.heal_hp(heal_amount, self)
        return f"{user.name} healed {heal_amount} hp by {self.name}."

    def auto_E_condition(self, user, player):
        if not self.can_use_on_dead and user.is_dead():
            return False
        else:
            return user.hp < user.maxhp - 230000
        

class Swiss_Roll(Consumable):
    def __init__(self, stack: int):
        super().__init__("Swiss Roll", "Regenerate approximately 26450 hp each turn for 10 turns.")
        self.image = "food_swiss_roll"
        self.rarity = "Epic"
        self.type = "Food"
        self.current_stack = max(1, stack)
        self.current_stack = min(self.current_stack, self.max_stack)
        self.market_value = 5000

    def E(self, user, player):
        heal_func = lambda character, buff_applier: int(26450 * random.uniform(0.8, 1.2))
        swiss_roll_effect = ContinuousHealEffect('Swiss Roll', 10, True, heal_func, user,
                                                 value_function_description="approximatly 26450", 
                                                 value_function_description_jp="約26450")
        swiss_roll_effect.additional_name = "Food_Swiss_Roll"
        swiss_roll_effect.set_apply_rule("stack")
        user.apply_effect(swiss_roll_effect)
        return f"{user.name} applied Swiss Roll for 10 turns."
    
    def auto_E_condition(self, user, player):
        if user.hp >= user.maxhp:
            return False
        if not self.can_use_on_dead and user.is_dead():
            return False
        else:
            if user.has_effect_that_named(effect_name="Swiss Roll", additional_name="Food_Swiss_Roll"):
                return False
            else:
                return True


# Unique
class Mantou(Consumable):
    def __init__(self, stack: int):
        super().__init__("Mantou", "Recover approximatly 300000 hp.")
        self.image = "mantou"
        self.rarity = "Unique"
        self.type = "Food"
        self.current_stack = max(1, stack)
        self.current_stack = min(self.current_stack, self.max_stack)
        self.market_value = 8000

    def E(self, user, player):
        # random 0.8-1.2
        heal_amount = 300000 * random.uniform(0.8, 1.2)
        user.heal_hp(heal_amount, self)
        return f"{user.name} healed {heal_amount} hp by {self.name}."
    
    def auto_E_condition(self, user, player):
        if not self.can_use_on_dead and user.is_dead():
            return False
        else:
            return user.hp < user.maxhp - 300000


class Ramen(Consumable):
    def __init__(self, stack: int):
        super().__init__("Ramen", "Apply Shield to user for 9-12 turns. Damage is reduced by 25%, each subsequent damage taken on the same turn is further reduced by 25%.")
        self.description += " When same effect is applied, duration is refreshed."
        self.image = "food_ramen"
        self.rarity = "Unique"
        self.type = "Food"
        self.current_stack = max(1, stack)
        self.current_stack = min(self.current_stack, self.max_stack)
        self.market_value = 8000

    def E(self, user, player):
        d = random.randint(9, 12)
        ramen_effect = AntiMultiStrikeReductionShield('Ramen', d, True, 0.25, False)
        ramen_effect.additional_name = "Food_Ramen"
        ramen_effect.set_apply_rule("stack")
        user.apply_effect(ramen_effect)
        return f"{user.name} applied Ramen for {d} turns."

    def auto_E_condition(self, user, player):
        if not self.can_use_on_dead and user.is_dead():
            return False
        else:
            if user.has_effect_that_named(effect_name="Ramen", additional_name="Food_Ramen"):
                return False
            else:
                return True
        

class Orange_Juice(Consumable):
    def __init__(self, stack: int):
        super().__init__("100% Orange Juice", "Apply Shield to user for 9-12 turns. Shield absorbs approximatly 225000 damage.")
        self.description += " When same effect is applied, duration is refreshed."
        self.image = "food_orange_juice"
        self.rarity = "Unique"
        self.type = "Food"
        self.current_stack = max(1, stack)
        self.current_stack = min(self.current_stack, self.max_stack)
        self.market_value = 8000

    def E(self, user, player):
        d = random.randint(9, 12)
        shield_amount = int(225000 * random.uniform(0.8, 1.2))
        orangej_effect = AbsorptionShield('100% Orange Juice', d, True, shield_amount, False)
        orangej_effect.additional_name = "Food_Orange_Juice"
        orangej_effect.set_apply_rule("stack")
        user.apply_effect(orangej_effect)
        return f"{user.name} applied 100% Orange Juice for {d} turns."

    def auto_E_condition(self, user, player):
        if not self.can_use_on_dead and user.is_dead():
            return False
        else:
            if user.has_effect_that_named(effect_name="100% Orange Juice", additional_name="Food_Orange_Juice"):
                return False
            else:
                return True


# Legendary
class Matcha_Roll(Consumable):
    def __init__(self, stack: int):
        super().__init__("Matcha Roll", "All stats + 12% for 22-26 turns.")
        self.description += " When same effect is applied, duration is refreshed."
        self.image = "food_matcha_roll"
        self.rarity = "Legendary"
        self.type = "Food"
        self.current_stack = max(1, stack)
        self.current_stack = min(self.current_stack, self.max_stack)
        self.market_value = 12000

    def E(self, user, player):
        d = random.randint(22, 26)
        matcha_effect = StatsEffect('Matcha Roll', d, True, {"atk": 1.12, "defense": 1.12, "spd": 1.12, "maxhp": 1.12})
        matcha_effect.additional_name = "Food_Matcha_Roll"
        matcha_effect.set_apply_rule("stack")
        user.apply_effect(matcha_effect)
        return f"{user.name} applied Matcha Roll for {d} turns."

    def auto_E_condition(self, user, player):
        if not self.can_use_on_dead and user.is_dead():
            return False
        else:
            if user.has_effect_that_named(effect_name="Matcha Roll", additional_name="Food_Matcha_Roll"):
                return False
            else:
                return True


class Icecream(Consumable):
    def __init__(self, stack: int):
        super().__init__("Icecream", "Recover 222222 hp and remove 2 random debuffs.")
        self.image = "food_icecream"
        self.rarity = "Legendary"
        self.type = "Food"
        self.current_stack = max(1, stack)
        self.current_stack = min(self.current_stack, self.max_stack)
        self.market_value = 12000

    def E(self, user, player):
        heal_amount = 222222
        user.heal_hp(heal_amount, self)
        user.remove_random_amount_of_debuffs(2)
        return f"{user.name} healed {heal_amount} hp and removed 2 debuffs by {self.name}."

    def auto_E_condition(self, user, player):
        if not self.can_use_on_dead and user.is_dead():
            return False
        else:
            return user.hp < user.maxhp - 222222 and len(user.get_active_removable_effects(get_buffs=False, get_debuffs=True)) > 0



def get_1_random_consumable():
    consumable_list = [Apple(1), Coconuts(1), Banana(1), Orange(1),
                        Kiwi(1), Fried_Shrimp(1), Pomegranate(1), Strawberry(1), Orange_Juice_60(1),
                        Milk(1), Sandwich(1), Pancake(1), Swiss_Roll(1), Mantou(1), Ramen(1), Orange_Juice(1),
                        Matcha_Roll(1), Icecream(1)
                          ]
    return random.choice(consumable_list)