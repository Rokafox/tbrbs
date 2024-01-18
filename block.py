import random
# The top level class for any and all objects, as a reference to Minecraft blocks and Blender starting block.
# The following classes inherit from this class:
# Equip, Consumable, Item

class Block:
    def __init__(self, name, description):
        self.name = name
        self.description = description
        self.rarity_list = ["Common", "Uncommon", "Rare", "Epic", "Unique", "Legendary"]
        self.type_list = ["None"]
        self.eq_set_list = ["None"]
        self.type = "None"
        self.rarity = "Common"
        self.eq_set = "None"
        self.level = 1
        self.market_value = 1
        self.image = None
        self.can_be_stacked = True
        self.current_stack = 1
        self.max_stack = 99999 # If too high, cannot be shown on icon.

    def __str__(self):
        return self.name

    def to_dict(self):
        return {
            "object": str(self.__class__),
            "name": self.name,
            "description": self.description,
            "rarity": self.rarity,
            "type": self.type,
            "eq_set": self.eq_set,
            "level": self.level,
            "market_value": self.market_value,
            "image": self.image,
            "can_be_stacked": self.can_be_stacked,
            "current_stack": self.current_stack,
            "max_stack": self.max_stack
        }

    def E(self, user, player): # When item is being used, as a common shortcut in Counter-Strike
        """Returns a string describing what happened when the item is being used."""
        if user:
            return f"{user.name} used {self.name} but nothing happened."
        else:
            return f"Used {self.name} but nothing happened."
        
    def print_stats_html(self, include_market_price=True):
        match self.rarity:
            case "Common":
                color = "#2c2c2c"
            case "Uncommon":
                color = "#B87333"
            case "Rare":
                color = "#FF0000"
            case "Epic":
                color = "#659a00"
            case "Unique":
                color = "#9966CC"
            case "Legendary":
                color = "#21d6ff"
        market_color = "#202d82" # blue
        str = f"<font color={color}>{self.name}</font>\n"
        str += f"{self.description} \nCurrent stack: {self.current_stack}\n"
        if include_market_price:
            str += f"<font color={market_color}>Market price: {self.market_value}</font>\n"
        return str
    
    def is_full(self):
        return self.current_stack >= self.max_stack
    
    def total_market_value(self):
        return self.market_value * self.current_stack