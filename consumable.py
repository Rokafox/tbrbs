from block import *
from effect import *
import random

from equip import generate_equips_list, adventure_generate_random_equip_with_weight


# NOTE:
# 1. name must be equal to class name, see load_player() in bs
# 2. Every time a new consumable is added, add it to get_1_random_consumable() in consumable.py


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
    def __init__(self, stack: int, brand: str=""):
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
            instance = c(1)
            if instance.type == "Food" and instance.rarity in ["Common", "Uncommon"]:
                food_list.append(instance)

        # Now we have for example [Banana(1), Kiwi(1)], but 100 is needed, so a random combination with the sum of 100,
        # for example [Banana(50), Kiwi(50)], set food.current_stack to 50
        for f in food_list:
            f.current_stack = 100 // len(food_list)

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
            instance = c(1)
            if instance.type == "Food" and instance.rarity in ["Rare", "Epic"]:
                food_list.append(instance)

        for f in food_list:
            f.current_stack = 100 // len(food_list)

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
            instance = c(1)
            if instance.type == "Food" and instance.rarity in ["Unique", "Legendary"]:
                food_list.append(instance)

        for f in food_list:
            f.current_stack = 100 // len(food_list)

        player.add_package_of_items_to_inventory(food_list)
        return None

    def auto_E_condition(self, user, player):
        return False












#==================================================================================================
# Food
#==================================================================================================
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


class Orange(Consumable):
    def __init__(self, stack: int):
        super().__init__("Orange", "Apply Shield to user for 6-12 turns. Damage is reduced by 25%, each subsequent damage taken on the same turn is further reduced by 25%.")
        self.image = "orange"
        self.rarity = "Unique"
        self.type = "Food"
        self.current_stack = max(1, stack)
        self.current_stack = min(self.current_stack, self.max_stack)
        self.market_value = 8000

    def E(self, user, player):
        d = random.randint(6, 12)
        orange_effect = AntiMultiStrikeReductionShield('Orange', d, True, 0.25, False)
        orange_effect.additional_name = "Food_Orange"
        user.apply_effect(orange_effect)
        return f"{user.name} applied Orange Shield for {d} turns."
    
    def auto_E_condition(self, user, player):
        if not self.can_use_on_dead and user.is_dead():
            return False
        else:
            if user.has_effect_that_named(effect_name="Orange", additional_name="Food_Orange"):
                return False
            else:
                return True
        






def get_1_random_consumable():
    consumable_list = [Banana(1), Kiwi(1), Strawberry(1), Pancake(1), Mantou(1), Orange(1)]
    return random.choice(consumable_list)