from block import *
from effect import *
import random


# NOTE:
# 1. name must be equal to class name, see load_player() in bs
# 2. Every time a new consumable is added, add it to get_1_random_consumable() in consumable.py


# Price : common < uncommon < rare < epic < unique < legendary, 50, 100, 250, 500, 1000, 2500
class Consumable(Block):
    def __init__(self, name, description):
        super().__init__(name, description)
        self.can_use_for_auto_battle = True
        self.can_use_on_dead = False

    def auto_E_condition(self, user, player):
        """
        Returns True if the item should be used automatically.
        """
        if not self.can_use_on_dead and user.is_dead():
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

def get_1_random_consumable():
    consumable_list = [Banana(1), Kiwi(1), Strawberry(1), Pancake(1), Mantou(1)]
    return random.choice(consumable_list)