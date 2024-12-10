import difflib
import inspect
import os, json
import statistics
import sys
import pandas as pd
import analyze

from character import *
start_with_max_level = True

all_characters = [
    obj for name, obj in inspect.getmembers(sys.modules[__name__], inspect.isclass)
    if issubclass(obj, Character) and obj is not Character
]
# create instance of each character
if start_with_max_level:
    all_characters: list[Character] = [c("", 1000) for c in all_characters]
else:
    all_characters: list[Character] = [c("", 1) for c in all_characters]
all_characters_names: list[str] = [c.name for c in all_characters]
print(f"Loaded {len(all_characters)} characters.")

fwss_source_code_cache = {}
fwss_noinit_source_code_cache = {}

def fwss_cache_source_code() -> None:
    def fwss_remove_init_method(source_code: str) -> str:
        lines = source_code.split('\n')
        filtered_lines = []
        inside_init = False
        for line in lines:
            if line.strip().startswith('def __init__'):
                inside_init = True
            if inside_init and line.strip().startswith('def ') and not line.strip().startswith('def __init__'):
                inside_init = False
            if not inside_init:
                filtered_lines.append(line)
        return '\n'.join(filtered_lines)

    print("Caching source code for all characters...")
    for x in all_characters:
        class_name = x.__class__.__name__
        if class_name not in fwss_source_code_cache:
            source_code = inspect.getsource(x.__class__)
            fwss_source_code_cache[class_name] = source_code
            fwss_noinit_source_code_cache[class_name] = fwss_remove_init_method(source_code)
    print("Caching source code for all characters complete.")

import monsters

all_monsters: list[Character] = [cls(name, 1) for name, cls in monsters.__dict__.items() 
                if inspect.isclass(cls) and issubclass(cls, Character) and cls != Character and cls != monsters.Monster]
all_monsters_names: list[str] = [m.name for m in all_monsters]
all_monsters_names.sort()
print(f"Loaded {len(all_monsters)} monsters.")

from item import *
from consumable import *
from calculate_winrate import is_someone_alive, reset_ally_enemy_attr
import shop
import csv
running = False
text_box = None



# A hack to disable DPI scaling on Windows systems
import ctypes
try:
    ctypes.windll.user32.SetProcessDPIAware()
except AttributeError:
    pass


# NOTE:
"""
1. We cannot have character with the same name.
2. We cannot have effects with the same name.
3. Because we now have save feature, make sure to shut down instead of quit for debugging. Delete player_data.json if necessary.
4, Every time we add a new item type for inventory, we MUST to add it to a certain list for sort feature. See Nine.sort_inventory_by_type
5. load_player() is only partially implemented. We have to add more code to load more consumables and items.
   Make sure to check it if there is something run after loading player data.
6. If there is bug unsolvable, refer to 3.
7. If we want to sell a item in the shop, we must add it somewhere in shop module.
"""

# =====================================
# Helper Functions
# =====================================

def save_player(player, filename="player_data.json"):
    player.owned_characters = all_characters
    player_data = player.to_dict()
    with open(filename, "w") as file:
        json.dump(player_data, file, indent=4)

def load_player(filename="player_data.json"):
    with open(filename, "r") as file:
        data = json.load(file)
    player = Nine(0)
    # player.attribute = data["attribute"]
    cash_in_data = data["cash"]

    dict_character_name_lvl_exp_equip = {}
    for item_data in data["owned_characters"]:
        dict_character_name_lvl_exp_equip[item_data["name"]] = (item_data["lvl"], item_data["exp"], item_data["equip"])

    for item_data in data["inventory_equip"]:
        item = Equip("foo", "Weapon", "Common")
        for attr, value in item_data.items():
            if hasattr(item, attr):
                setattr(item, attr, value)
        item.estimate_market_price()
        item.four_set_effect_description = item.assign_four_set_effect_description()
        item.four_set_effect_description_jp = item.assign_four_set_effect_description_jp()
        item.for_attacker_value = item.estimate_value_for_attacker()
        item.for_support_value = item.estimate_value_for_support()
        player.inventory_equip.append(item)

    for item_data in data["inventory_consumable"]:
        class_name = item_data['object'].split("'")[1].split('.')[-1]
        item_class = globals().get(class_name)
        # print(item_class)
        # <class 'consumable.FoodPackage3'>
        # <class 'consumable.EquipPackage6'>
        # <class 'consumable.EquipPackage5'>
        # <class 'consumable.Mantou'>
        # <class 'consumable.Orange'>
        # <class 'consumable.FoodPackage2'>
        # <class 'consumable.EquipPackage4'>
        # <class 'consumable.Pancake'>
        # <class 'consumable.EquipPackage3'>
        # <class 'consumable.Strawberry'>
        # <class 'consumable.FoodPackage'>
        # <class 'consumable.EquipPackage2'>
        # <class 'consumable.EquipPackage'>
        if item_class is None:
            raise ValueError(f"Unknown item type: {item_data['name']}")
        if class_name == "EquipPackageBrandSpecific":
            item = item_class(item_data['current_stack'], item_data['eq_set'])
        else:
            item = item_class(item_data['current_stack'])
        if not item.is_full():
            player._add_non_full_stack(item)
        player.inventory_consumable.append(item)

    for item_data in data["inventory_item"]:
        class_name = item_data['object'].split("'")[1].split('.')[-1]
        item_class = globals().get(class_name)
        if item_class is None:
            raise ValueError(f"Unknown item type: {item_data['name']}")
        item = item_class(item_data['current_stack'])
        if not item.is_full():
            player._add_non_full_stack(item)
        player.inventory_item.append(item)

    cash_actual = player.refresh_cash()
    if cash_in_data != cash_actual:
        print(f"Warning: Cash recorded does not match the actual Cash in inventory: {cash_in_data} != {cash_actual}, {cash_actual} is used.")
    player.cleared_stages = data["cleared_stages"]
    player.cheems = data["cheems"]
    player.settings_language = data["settings_language"]
    player.settings_theme = data["settings_theme"]
    return player, dict_character_name_lvl_exp_equip


# =====================================
# End of Helper Functions
# =====================================
# Player Section
# =====================================

class Nine(): # A reference to 9Nine, Nine is just the player's name
    def __init__(self, cash: int):
        self.cash_initial = cash
        self.cash = 0 
        self.owned_characters = []
        # We could have multiple types of items in inventory, Equip, Consumable, Item.
        self.inventory_equip = []
        self.inventory_consumable = []
        self.inventory_item = []
        self.current_page = 0
        self.max_pages = 0
        self.dict_image_slots_items: dict[pygame_gui.elements.UIImage, Block] = {}
        self.dict_image_slots_rects: dict[pygame_gui.elements.UIImage, pygame.Rect] = {}
        # {image_slot: UIImage : (image: Surface, is_highlighted: bool, the_actual_item: Block)}
        self.selected_item: dict[pygame_gui.elements.UIImage, tuple[pygame.Surface, bool, Block]] = {}
        self.cleared_stages = 0
        # cheems: player can create custom teams for battle, each entry is a list of 5 character names: ["Cerberus", "Fenrir", "Clover", 'Ruby', 'Olive']
        # each team also has a name, like "Team AAA", "Team BBB"
        self.cheems: dict[str, list[str]] = {}
        self.settings_language = "English"
        self.settings_theme = "Yellow Theme"

        # A dictionary to keep track of partially filled stackable items:
        # Key: (ItemClass, brand or None)
        # Value: list of references to items in the inventory that are not full
        self.non_full_stacks = {}

        if self.cash_initial > 0:
            self.add_cash(cash, False)


    def _get_stack_key(self, item):
        """Return the key used to store stacks of this item in non_full_stacks."""
        brand = getattr(item, 'brand', None)
        return (item.__class__, brand)

    def _add_non_full_stack(self, item):
        """Add an item to the non_full_stacks dictionary if it's stackable and not full."""
        if item.can_be_stacked and not item.is_full():
            key = self._get_stack_key(item)
            if key not in self.non_full_stacks:
                self.non_full_stacks[key] = []
            self.non_full_stacks[key].append(item)

    def _remove_non_full_stack(self, item):
        """Remove an item from the non_full_stacks dictionary if it is now full or removed."""
        if item.can_be_stacked:
            key = self._get_stack_key(item)
            if key in self.non_full_stacks:
                # Attempt to remove it if present
                if item in self.non_full_stacks[key]:
                    self.non_full_stacks[key].remove(item)
                # If no more partial stacks remain under this key, remove the key
                if not self.non_full_stacks[key]:
                    del self.non_full_stacks[key]


    def to_dict(self):
        return {
            "cash": self.cash,
            "owned_characters": [character.to_dict() for character in self.owned_characters],
            "inventory_equip": [item.to_dict() for item in self.inventory_equip],
            "inventory_consumable": [item.to_dict() for item in self.inventory_consumable],
            "inventory_item": [item.to_dict() for item in self.inventory_item],
            "settings_language": self.settings_language,
            "settings_theme": self.settings_theme,
            "cleared_stages": self.cleared_stages,
            "cheems": self.cheems,
        }

    def build_inventory_slots(self):
        self.selected_item = {}
        page = self.current_page
        # try:
        only_include = global_vars.cheap_inventory_show_current_option
        # except NameError:
        #     only_include = "Equip"
        match only_include:
            case "Equip":
                filtered_inventory = self.inventory_equip
                if global_vars.cheap_inventory_filter_have_owner == "Has Owner":
                    filtered_inventory = [x for x in filtered_inventory if hasattr(x, "owner") and x.owner is not None]
                elif global_vars.cheap_inventory_filter_have_owner == "No Owner":
                    filtered_inventory = [x for x in filtered_inventory if hasattr(x, "owner") and x.owner is None]

                if global_vars.cheap_inventory_filter_owned_by_char not in ["Not Specified", "Currently Selected"]:
                    filtered_inventory = [x for x in filtered_inventory if hasattr(x, "owner") and x.owner == global_vars.cheap_inventory_filter_owned_by_char]
                elif global_vars.cheap_inventory_filter_owned_by_char == "Currently Selected":
                    s = character_selection_menu.selected_option[0].split(" ")[-1]
                    filtered_inventory = [x for x in filtered_inventory if hasattr(x, "owner") and x.owner == s]

                if global_vars.cheap_inventory_filter_eqset != "Not Specified":
                    filtered_inventory = [x for x in filtered_inventory if hasattr(x, "eq_set") and x.eq_set == global_vars.cheap_inventory_filter_eqset]

                if global_vars.cheap_inventory_filter_type != "Not Specified":
                    filtered_inventory = [x for x in filtered_inventory if isinstance(x, Equip) and x.type == global_vars.cheap_inventory_filter_type]

            case "Consumable":
                filtered_inventory = self.inventory_consumable
                # check if item have flag mark_for_removal, if so, remove it from inventory
                # filtered_inventory = [x for x in filtered_inventory if not x.mark_for_removal]
            case "Item":
                filtered_inventory = self.inventory_item
            case _:
                filtered_inventory = self.inventory_equip + self.inventory_consumable + self.inventory_item

        # inventory filter, global_vars have the following 3 attributes:
        # cheap_inventory_filter_have_owner = "Not Specified" | "Has Owner" | "No Owner"
        # cheap_inventory_filter_owned_by_char = "Not Specified" | "Character Name"
        # cheap_inventory_filter_eqset = "Not Specified" | "Equipment Set Name"


        chunked_inventory = list(mit.chunked(filtered_inventory, 24)) # The value must equal to n argument of create_inventory_image_slots()
        max_pages = max(0, len(chunked_inventory) - 1)
        self.max_pages = max_pages
        # print(f"max_pages = {max_pages}")
        page = max(0, page)
        page = min(page, len(chunked_inventory) - 1)
        self.current_page = page
        # print(f"Building page {page} of inventory...")
        try:
            amount_of_slots_to_build = len(chunked_inventory[page])
        except IndexError:
            amount_of_slots_to_build = 0
        # print(f"Building {amount_of_slots_to_build} slots...")
        gutted_slots, b = show_n_slots_of_inventory_image_slots(amount_of_slots_to_build)
        self.dict_image_slots_rects = b

        # maps UIImage to actual inventory item
        try:
            dict_image_slots_items = {k: v for k, v in mit.zip_equal(gutted_slots, chunked_inventory[page])} # UIImage : Equip
        except IndexError:
            dict_image_slots_items = {}
        self.dict_image_slots_items = dict_image_slots_items
        # set up image and tooltip to UIImage based on item info
        for ui_image, item in dict_image_slots_items.items():
            if item.image:
                # If stackable, process the image and show amount
                if item.can_be_stacked:
                    try:
                        image_to_process = images_item[item.image].copy()
                    except KeyError:
                        image_to_process = images_item["404"].copy()
                    # scale the image to 800 x 800
                    image_to_process = pygame.transform.scale(image_to_process, (800, 800))
                    create_yellow_text(image_to_process, str(item.current_stack), 310, (0, 0, 0), add_background=True)
                    ui_image.set_image(image_to_process)
                else:
                    try:
                        ui_image.set_image(images_item[item.image])
                    except KeyError:
                        print(f"Warning: Image not found: {item.image} in Nine.build_inventory_slots()")
                        match (type(item).__name__, item.type):    
                            case ("Equip", "Weapon"):
                                ui_image.set_image(images_item["Generic_Weapon"])
                            case ("Equip", "Armor"):
                                ui_image.set_image(images_item["Generic_Armor"])
                            case ("Equip", "Accessory"):
                                ui_image.set_image(images_item["Generic_Accessory"])
                            case ("Equip", "Boots"):
                                ui_image.set_image(images_item["Generic_Boots"])
                            case _:
                                print(f"Warning: Unknown item type: {item.type} in Nine.build_inventory_slots()")
                                ui_image.set_image(images_item["404"])
            if global_vars.language == "日本語" and hasattr(item, "print_stats_html_jp"):
                ui_image.set_tooltip(item.print_stats_html_jp(), delay=0.1, wrap_width=400)
            else:
                ui_image.set_tooltip(item.print_stats_html(), delay=0.1, wrap_width=400)
        update_inventory_section(self)

    def add_to_inventory(self, item, rebuild_inventory_slots=True):
        if not item:
            raise ValueError("Item is None")

        if item.can_be_stacked:
            base_class = item.__class__.__bases__[0].__name__.lower()  # "consumable" or "item"
            inv_ref = eval(f"self.inventory_{base_class}")

            # First, try to fill from the non_full_stacks dictionary
            key = self._get_stack_key(item)
            amount_to_add = item.current_stack

            # If we have partially filled stacks of this type, fill them first
            if key in self.non_full_stacks:
                stacks = self.non_full_stacks[key]
                # Use a while loop or for loop to distribute the stack among partially filled stacks
                i = 0
                while amount_to_add > 0 and i < len(stacks):
                    stack_item = stacks[i]
                    space_left = stack_item.max_stack - stack_item.current_stack
                    to_fill = min(space_left, amount_to_add)
                    stack_item.current_stack += to_fill
                    amount_to_add -= to_fill
                    if stack_item.is_full():
                        self._remove_non_full_stack(stack_item)
                    else:
                        # Still not full, so leave it in the dictionary
                        pass
                    i += 1

                # Clean out empty lists if needed
                if key in self.non_full_stacks and not self.non_full_stacks[key]:
                    del self.non_full_stacks[key]

            # If there's still some amount left, create a new stack
            while amount_to_add > 0:
                # Decide how much to put in a new stack
                stack_size = min(amount_to_add, item.max_stack)
                new_item = type(item)(stack_size)
                # If the item has brand, copy that as well
                if hasattr(item, 'brand'):
                    new_item.brand = item.brand

                inv_ref.append(new_item)
                amount_to_add -= stack_size

                if not new_item.is_full():
                    self._add_non_full_stack(new_item)

        else:
            # Non-stackable items are straightforward
            match (item.__class__.__name__, item.__class__.__bases__[0].__name__):
                case ("Equip", "Block"):
                    self.inventory_equip.append(item)
                case (_, "Consumable"):
                    self.inventory_consumable.append(item)
                case (_, "Item"):
                    self.inventory_item.append(item)
                case _:
                    raise ValueError(f"Unknown item type: {type(item)}")

        if rebuild_inventory_slots:
            self.build_inventory_slots()

    def remove_from_inventory(self, item_type, amount_to_remove, rebuild_inventory_slots=True, item_brand=None):
        if amount_to_remove <= 0:
            raise ValueError("Amount to remove must be positive")

        # Non-stackable items still require a linear search, but these should be relatively rare
        # For stackable items:
        create_instance = item_type(1)
        what_is_this = create_instance.__class__.__bases__[0].__name__.lower()
        inv_ref = eval(f"self.inventory_{what_is_this}")

        removed_count = 0
        i = 0
        while i < len(inv_ref) and removed_count < amount_to_remove:
            inv_item = inv_ref[i]
            if isinstance(inv_item, item_type):
                # Check brand if applicable
                if hasattr(inv_item, 'brand') and item_brand is not None:
                    if inv_item.brand != item_brand:
                        i += 1
                        continue

                if inv_item.can_be_stacked:
                    amount_removed = min(amount_to_remove - removed_count, inv_item.current_stack)
                    inv_item.current_stack -= amount_removed
                    removed_count += amount_removed

                    if inv_item.current_stack == 0:
                        # The stack is empty, remove it entirely
                        self._remove_non_full_stack(inv_item)
                        inv_ref.pop(i)
                        # Don't increment i because we removed this item
                    else:
                        # It's partially filled now, ensure it's in non_full_stacks
                        if inv_item.is_full():
                            self._remove_non_full_stack(inv_item)
                        else:
                            # Make sure it's recorded as non-full
                            if inv_item not in self.non_full_stacks.get(self._get_stack_key(inv_item), []):
                                self._add_non_full_stack(inv_item)
                        i += 1
                else:
                    # Non-stackable, remove it entirely
                    inv_ref.pop(i)
                    removed_count += 1
                    # Don't increment i due to removal
            else:
                i += 1

        if removed_count < amount_to_remove:
            raise ValueError("Not enough items in inventory to remove")

        if rebuild_inventory_slots:
            self.build_inventory_slots()

    def remove_selected_item_from_inventory(self, rebuild_inventory_slots: bool):
        # self.selected_item = {} # {image_slot: UIImage : (image: Surface, is_highlighted: bool, the_actual_item)}
        """
        Do not use for stackable items. Returns the amount of items removed.
        """
        if not self.selected_item:
            return
        amount_to_remove = len(self.selected_item)
        for a, b, item in self.selected_item.values():
            if b: # is_highlighted
                assert not item.can_be_stacked
                match (item.__class__.__name__, item.__class__.__bases__[0].__name__):
                    case ("Equip", "Block"):
                        self.inventory_equip.remove(item)
                    case (_, "Consumable"):
                        self.inventory_consumable.remove(item)
                    case (_, "Item"):
                        self.inventory_item.remove(item)
                    case _:
                        raise ValueError(f"Unknown item type: {type(item)}")
        if rebuild_inventory_slots:
            self.build_inventory_slots()
        return amount_to_remove 

    def use_1_selected_item(self, rebuild_inventory_slots: bool, use_how_many_times: int = 1, who_the_character: Character = None):
        # self.selected_item = {} # {image_slot: UIImage : (image: Surface, is_highlighted: bool, the_actual_item)}
        # use_how_many_times is contradicting with the name of the method. Whatever.
        """Can be used for stackable items"""
        if not self.selected_item:
            print("No item selected.")
            return
        for a, b, item in self.selected_item.values():
            if b: # is_highlighted
                # cannot use 7 bananas when we only have 5
                uhmt_fixed = min(use_how_many_times, item.current_stack)
                if hasattr(item, 'brand'):
                    self.remove_from_inventory(type(item), uhmt_fixed, False, item.brand)
                else:
                    self.remove_from_inventory(type(item), uhmt_fixed, False)
                for i in range(uhmt_fixed):
                    item.E_actual(who_the_character, self)

        if rebuild_inventory_slots:
            self.build_inventory_slots()


    def add_package_of_items_to_inventory(self, package_of_items: list):
        for item in package_of_items:
            self.add_to_inventory(item, False)
        self.build_inventory_slots()


    def sort_inventory_abc(self, first: str, second: str, third: str):
        """
        Given 3 attributes, sort by first, then second, then third.
        """
        def convert_for_eval(s: str):
            # "Rarity", "Type", "Set", "Level", "Market Value", "BOGO"
            match s:
                case "Rarity":
                    return "rarity_order"
                case "Type":
                    return "type"
                case "Set":
                    return "eq_set"
                case "Level":
                    return "level"
                case "Market Value":
                    return "market_value"
                case "BOGO":
                    return "bogo"
                case "Attacker":
                    return "for_attacker_value"
                case "Support":
                    return "for_support_value"
                case _:
                    return s
        first = convert_for_eval(first)
        second = convert_for_eval(second)
        third = convert_for_eval(third)

        sort_what = global_vars.cheap_inventory_show_current_option

        if "bogo" in [first, second, third]:
            # we have to generate a bogo value for each item
            for item in eval(f"self.inventory_{sort_what.lower()}"):
                item.bogo = random.random()
        for item in eval(f"self.inventory_{sort_what.lower()}"):
            item.rarity_order = item.get_rarity_order()

        try:
            eval_string = f"self.inventory_{sort_what.lower()}.sort(key=lambda x: (getattr(x, '{first}', 0), getattr(x, '{second}', 0), getattr(x, '{third}', 0)), reverse=True)"
            eval(eval_string)
        except Exception as e:
            print(f"Error sorting inventory: {e}")
        self.current_page = 0
        self.build_inventory_slots()


    def to_next_page(self):
        if self.current_page == self.max_pages:
            return
        else:
            self.current_page += 1
        self.build_inventory_slots()

    def to_last_page(self):
        if self.current_page == self.max_pages:
            return
        else:
            self.current_page = self.max_pages
        self.build_inventory_slots()

    def to_previous_page(self):
        if self.current_page == 0:
            return
        else:
            self.current_page -= 1
        self.build_inventory_slots()

    def to_first_page(self):
        if self.current_page == 0:
            return
        else:
            self.current_page = 0
        self.build_inventory_slots()
        
    def to_next_page_jump_n(self, n: int):
        if self.current_page + n > self.max_pages:
            self.current_page = self.max_pages
        else:
            self.current_page += n
        self.build_inventory_slots()

    def to_previous_page_jump_n(self, n: int):
        if self.current_page - n < 0:
            self.current_page = 0
        else:
            self.current_page -= n
        self.build_inventory_slots()

    def refresh_cash(self):
        self.cash = 0
        for item in self.inventory_item:
            if isinstance(item, Cash):
                self.cash += item.current_stack
        return self.cash

    def add_cash(self, amount: int, rebuild_inventory_slots: bool = True):
        if amount <= 0:
            if amount == 0:
                return
            else:
                raise ValueError("Amount must be positive")
        self.cash += amount
        while amount > 0:
            if amount <= 999999:
                self.add_to_inventory(Cash(amount), rebuild_inventory_slots)
                amount = 0
            else:
                self.add_to_inventory(Cash(999999), False)
                amount -= 999999
        try:
            set_currency_on_icon_and_label(self, the_shop.currency, shop_player_owned_currency, shop_player_owned_currency_icon)
        except NameError:
            pass


    def lose_cash(self, amount: int, rebuild_inventory_slots: bool = True):
        self.remove_from_inventory(Cash, amount, rebuild_inventory_slots)
        self.cash -= amount
        try:
            set_currency_on_icon_and_label(self, the_shop.currency, shop_player_owned_currency, shop_player_owned_currency_icon)
        except NameError:
            pass

    def get_currency(self, currency: str):
        if currency.lower() == "cash":
            return self.cash
        else:
            c = 0
            for item in self.inventory_item:
                if item.__class__.__name__.lower() == currency or item.__class__.__name__ == currency:
                    c += item.current_stack
            return c


# =====================================
# End of Player Section
# =====================================

# ---------------------------------------------------------
# ---------------------------------------------------------
if __name__ == "__main__":
    import pygame, pygame_gui
    pygame.init()
    clock = pygame.time.Clock()

    antique_white = pygame.Color("#FAEBD7")
    deep_dark_blue = pygame.Color("#000022")
    light_yellow = pygame.Color("#FFFFE0")
    light_purple = pygame.Color("#f0eaf5")
    light_red = pygame.Color("#fbe4e4")
    light_green = pygame.Color("#e5fae5")
    light_blue = pygame.Color("#e6f3ff")
    light_pink = pygame.Color("#fae5eb")

    display_surface = pygame.display.set_mode((1600, 900), flags=pygame.SCALED | pygame.RESIZABLE)
    ui_manager_lower = pygame_gui.UIManager((1600, 900), "theme_light_yellow.json", starting_language='ja')
    ui_manager = pygame_gui.UIManager((1600, 900), "theme_light_yellow.json", starting_language='ja')
    ui_manager_overlay = pygame_gui.UIManager((1600, 900), "theme_light_yellow.json", starting_language='ja')
    # debug_ui_manager = pygame_gui.UIManager((1600, 900), "theme_light_yellow.json", starting_language='ja')
    # ui_manager.get_theme().load_theme("theme_light_purple.json")
    # ui_manager.rebuild_all_from_changed_theme_data()

    pygame.display.set_caption("Battle Simulator")
    # if there is icon, use it
    try:
        icon = pygame.image.load("icon.png")
        pygame.display.set_icon(icon)
    except Exception as e:
        print(f"Error loading icon: {e}")

    if not os.path.exists("./.tmp"):
        os.mkdir("./.tmp")

    # clean everything in ./.tmp, old data
    for file in os.listdir("./.tmp"):
        os.remove(f"./.tmp/{file}")

    # =====================================
    # Load Images
    # =====================================
    
    if not os.path.exists("./image"):
        os.mkdir("./image")
    if not os.path.exists("./image/character"):
        os.mkdir("./image/character")
    if not os.path.exists("./image/monster"):
        os.mkdir("./image/monster")
    if not os.path.exists("./image/item"):
        os.mkdir("./image/item")

    image_files_character = [x[:-4] for x in os.listdir("./image/character") if x.endswith((".jpg", ".png"))]
    image_files_monster = [x[:-4] for x in os.listdir("./image/monster") if x.endswith((".jpg", ".png"))]
    image_files_item = [x[:-4] for x in os.listdir("./image/item") if x.endswith((".jpg", ".png"))]
    images_character = {} # str : pygame.Surface
    images_monster = {} # str : pygame.Surface
    images_item = {} # str : pygame.Surface

    for name in image_files_character:
        image_path_jpg = f"image/character/{name}.jpg"
        image_path_png = f"image/character/{name}.png"

        try:
            if os.path.exists(image_path_jpg):
                images_character[name] = pygame.image.load(image_path_jpg)
            elif os.path.exists(image_path_png):
                images_character[name] = pygame.image.load(image_path_png)
            else:
                print(f"ファイル {name} は見つかりませんでした。")
        except Exception as e:
            print(f"画像 {name} の読み込み中にエラーが発生しました: {e}")

    for name in image_files_monster:
        image_path_jpg = f"image/monster/{name}.jpg"
        image_path_png = f"image/monster/{name}.png"

        try:
            if os.path.exists(image_path_jpg):
                images_monster[name] = pygame.image.load(image_path_jpg)
            elif os.path.exists(image_path_png):
                images_monster[name] = pygame.image.load(image_path_png)
            else:
                print(f"ファイル {name} は見つかりませんでした。")
        except Exception as e:
            print(f"画像 {name} の読み込み中にエラーが発生しました: {e}")

    for name in image_files_item:
        image_path_jpg = f"image/item/{name}.jpg"
        image_path_png = f"image/item/{name}.png"

        try:
            if os.path.exists(image_path_jpg):
                images_item[name] = pygame.image.load(image_path_jpg)
            elif os.path.exists(image_path_png):
                images_item[name] = pygame.image.load(image_path_png)
            else:
                print(f"ファイル {name} は見つかりませんでした。")
        except Exception as e:
            print(f"画像 {name} の読み込み中にエラーが発生しました: {e}")

    for k, v in images_character.items():
        prefix = k.split("_")[0] # "cerberus_1" -> "cerberus", "fenrir_2" -> "fenrir"
        for character in all_characters:
            if character.name.lower() == prefix:
                character.image.append(v)
                
    for c in all_characters:
        c.set_up_featured_image()


    for k, v in images_monster.items():
        for monster in all_monsters:
            if monster.original_name.lower() == k:
                monster.image.append(v)

    for m in all_monsters:
        m.set_up_featured_image()

    # =====================================
    # End of Loading Images
    # =====================================

    image_slot1 = pygame_gui.elements.UIImage(pygame.Rect((100, 50), (156, 156)),
                                        pygame.Surface((156, 156)),
                                        ui_manager)
    image_slot2 = pygame_gui.elements.UIImage(pygame.Rect((300, 50), (156, 156)),
                                        pygame.Surface((156, 156)),
                                        ui_manager)
    image_slot3 = pygame_gui.elements.UIImage(pygame.Rect((500, 50), (156, 156)),
                                        pygame.Surface((156, 156)),
                                        ui_manager)
    image_slot4 = pygame_gui.elements.UIImage(pygame.Rect((700, 50), (156, 156)),
                                        pygame.Surface((156, 156)),
                                        ui_manager)
    image_slot5 = pygame_gui.elements.UIImage(pygame.Rect((900, 50), (156, 156)),
                                        pygame.Surface((156, 156)),
                                        ui_manager)
    image_slot6 = pygame_gui.elements.UIImage(pygame.Rect((100, 650), (156, 156)),
                                        pygame.Surface((156, 156)),
                                        ui_manager)
    image_slot7 = pygame_gui.elements.UIImage(pygame.Rect((300, 650), (156, 156)),
                                        pygame.Surface((156, 156)),
                                        ui_manager)
    image_slot8 = pygame_gui.elements.UIImage(pygame.Rect((500, 650), (156, 156)),
                                        pygame.Surface((156, 156)),
                                        ui_manager)
    image_slot9 = pygame_gui.elements.UIImage(pygame.Rect((700, 650), (156, 156)),
                                        pygame.Surface((156, 156)),
                                        ui_manager)
    image_slot10 = pygame_gui.elements.UIImage(pygame.Rect((900, 650), (156, 156)),
                                        pygame.Surface((156, 156)),
                                        ui_manager)

    image_slots_party1 = [image_slot1, image_slot2, image_slot3, image_slot4, image_slot5]
    image_slots_party2 = [image_slot6, image_slot7, image_slot8, image_slot9, image_slot10]
    image_slots_all = [*image_slots_party1, *image_slots_party2]

    image_slot_overlay1 = pygame_gui.elements.UIImage(pygame.Rect((100, 0), (156, 210)),
                                        pygame.Surface((156, 210)),
                                        ui_manager_overlay)
    image_slot_overlay2 = pygame_gui.elements.UIImage(pygame.Rect((300, 0), (156, 210)),
                                        pygame.Surface((156, 210)),
                                        ui_manager_overlay)
    image_slot_overlay3 = pygame_gui.elements.UIImage(pygame.Rect((500, 0), (156, 210)),
                                        pygame.Surface((156, 210)),
                                        ui_manager_overlay)
    image_slot_overlay4 = pygame_gui.elements.UIImage(pygame.Rect((700, 0), (156, 210)),
                                        pygame.Surface((156, 210)),
                                        ui_manager_overlay)
    image_slot_overlay5 = pygame_gui.elements.UIImage(pygame.Rect((900, 0), (156, 210)),
                                        pygame.Surface((156, 210)),
                                        ui_manager_overlay)
    image_slot_overlay_party1 = [image_slot_overlay1, image_slot_overlay2, image_slot_overlay3, image_slot_overlay4, image_slot_overlay5]
    for i in image_slot_overlay_party1:
        i.set_image(images_item["405"])
    image_slot_overlay6 = pygame_gui.elements.UIImage(pygame.Rect((100, 550), (156, 256)),
                                        pygame.Surface((156, 256)),
                                        ui_manager_overlay)
    image_slot_overlay7 = pygame_gui.elements.UIImage(pygame.Rect((300, 550), (156, 256)),
                                        pygame.Surface((156, 256)),
                                        ui_manager_overlay)
    image_slot_overlay8 = pygame_gui.elements.UIImage(pygame.Rect((500, 550), (156, 256)),
                                        pygame.Surface((156, 256)),
                                        ui_manager_overlay)
    image_slot_overlay9 = pygame_gui.elements.UIImage(pygame.Rect((700, 550), (156, 256)),
                                        pygame.Surface((156, 256)),
                                        ui_manager_overlay)
    image_slot_overlay10 = pygame_gui.elements.UIImage(pygame.Rect((900, 550), (156, 256)),
                                        pygame.Surface((156, 256)),
                                        ui_manager_overlay)
    image_slot_overlay_party2 = [image_slot_overlay6, image_slot_overlay7, image_slot_overlay8, image_slot_overlay9, image_slot_overlay10]
    for i in image_slot_overlay_party2:
        i.set_image(images_item["405"])



    # Equip Slots
    # ==============================
    equip_slota1 = pygame_gui.elements.UIImage(pygame.Rect((75, 50), (20, 20)),pygame.Surface((20, 20)),ui_manager)
    equip_slota2 = pygame_gui.elements.UIImage(pygame.Rect((75, 75), (20, 20)),pygame.Surface((20, 20)),ui_manager)
    equip_slota3 = pygame_gui.elements.UIImage(pygame.Rect((75, 100), (20, 20)),pygame.Surface((20, 20)),ui_manager)
    equip_slota4 = pygame_gui.elements.UIImage(pygame.Rect((75, 125), (20, 20)),pygame.Surface((20, 20)),ui_manager)
    equip_slota5 = pygame_gui.elements.UIImage(pygame.Rect((75, 150), (20, 20)),pygame.Surface((20, 20)),ui_manager)

    equip_slotsb1 = pygame_gui.elements.UIImage(pygame.Rect((275, 50), (20, 20)),pygame.Surface((20, 20)),ui_manager)
    equip_slotsb2 = pygame_gui.elements.UIImage(pygame.Rect((275, 75), (20, 20)),pygame.Surface((20, 20)),ui_manager)
    equip_slotsb3 = pygame_gui.elements.UIImage(pygame.Rect((275, 100), (20, 20)),pygame.Surface((20, 20)),ui_manager)
    equip_slotsb4 = pygame_gui.elements.UIImage(pygame.Rect((275, 125), (20, 20)),pygame.Surface((20, 20)),ui_manager)
    equip_slotsb5 = pygame_gui.elements.UIImage(pygame.Rect((275, 150), (20, 20)),pygame.Surface((20, 20)),ui_manager)

    equip_slotsc1 = pygame_gui.elements.UIImage(pygame.Rect((475, 50), (20, 20)),pygame.Surface((20, 20)),ui_manager)
    equip_slotsc2 = pygame_gui.elements.UIImage(pygame.Rect((475, 75), (20, 20)),pygame.Surface((20, 20)),ui_manager)
    equip_slotsc3 = pygame_gui.elements.UIImage(pygame.Rect((475, 100), (20, 20)),pygame.Surface((20, 20)),ui_manager)
    equip_slotsc4 = pygame_gui.elements.UIImage(pygame.Rect((475, 125), (20, 20)),pygame.Surface((20, 20)),ui_manager)
    equip_slotsc5 = pygame_gui.elements.UIImage(pygame.Rect((475, 150), (20, 20)),pygame.Surface((20, 20)),ui_manager)

    equip_slotsd1 = pygame_gui.elements.UIImage(pygame.Rect((675, 50), (20, 20)),pygame.Surface((20, 20)),ui_manager)
    equip_slotsd2 = pygame_gui.elements.UIImage(pygame.Rect((675, 75), (20, 20)),pygame.Surface((20, 20)),ui_manager)
    equip_slotsd3 = pygame_gui.elements.UIImage(pygame.Rect((675, 100), (20, 20)),pygame.Surface((20, 20)),ui_manager)
    equip_slotsd4 = pygame_gui.elements.UIImage(pygame.Rect((675, 125), (20, 20)),pygame.Surface((20, 20)),ui_manager)
    equip_slotsd5 = pygame_gui.elements.UIImage(pygame.Rect((675, 150), (20, 20)),pygame.Surface((20, 20)),ui_manager)

    equip_slotse1 = pygame_gui.elements.UIImage(pygame.Rect((875, 50), (20, 20)),pygame.Surface((20, 20)),ui_manager)
    equip_slotse2 = pygame_gui.elements.UIImage(pygame.Rect((875, 75), (20, 20)),pygame.Surface((20, 20)),ui_manager)
    equip_slotse3 = pygame_gui.elements.UIImage(pygame.Rect((875, 100), (20, 20)),pygame.Surface((20, 20)),ui_manager)
    equip_slotse4 = pygame_gui.elements.UIImage(pygame.Rect((875, 125), (20, 20)),pygame.Surface((20, 20)),ui_manager)
    equip_slotse5 = pygame_gui.elements.UIImage(pygame.Rect((875, 150), (20, 20)),pygame.Surface((20, 20)),ui_manager)

    equip_slotsf1 = pygame_gui.elements.UIImage(pygame.Rect((75, 650), (20, 20)),pygame.Surface((20, 20)),ui_manager)
    equip_slotsf2 = pygame_gui.elements.UIImage(pygame.Rect((75, 675), (20, 20)),pygame.Surface((20, 20)),ui_manager)
    equip_slotsf3 = pygame_gui.elements.UIImage(pygame.Rect((75, 700), (20, 20)),pygame.Surface((20, 20)),ui_manager)
    equip_slotsf4 = pygame_gui.elements.UIImage(pygame.Rect((75, 725), (20, 20)),pygame.Surface((20, 20)),ui_manager)
    equip_slotsf5 = pygame_gui.elements.UIImage(pygame.Rect((75, 750), (20, 20)),pygame.Surface((20, 20)),ui_manager)

    equip_slotsg1 = pygame_gui.elements.UIImage(pygame.Rect((275, 650), (20, 20)),pygame.Surface((20, 20)),ui_manager)
    equip_slotsg2 = pygame_gui.elements.UIImage(pygame.Rect((275, 675), (20, 20)),pygame.Surface((20, 20)),ui_manager)
    equip_slotsg3 = pygame_gui.elements.UIImage(pygame.Rect((275, 700), (20, 20)),pygame.Surface((20, 20)),ui_manager)
    equip_slotsg4 = pygame_gui.elements.UIImage(pygame.Rect((275, 725), (20, 20)),pygame.Surface((20, 20)),ui_manager)
    equip_slotsg5 = pygame_gui.elements.UIImage(pygame.Rect((275, 750), (20, 20)),pygame.Surface((20, 20)),ui_manager)

    equip_slotsh1 = pygame_gui.elements.UIImage(pygame.Rect((475, 650), (20, 20)),pygame.Surface((20, 20)),ui_manager)
    equip_slotsh2 = pygame_gui.elements.UIImage(pygame.Rect((475, 675), (20, 20)),pygame.Surface((20, 20)),ui_manager)
    equip_slotsh3 = pygame_gui.elements.UIImage(pygame.Rect((475, 700), (20, 20)),pygame.Surface((20, 20)),ui_manager)
    equip_slotsh4 = pygame_gui.elements.UIImage(pygame.Rect((475, 725), (20, 20)),pygame.Surface((20, 20)),ui_manager)
    equip_slotsh5 = pygame_gui.elements.UIImage(pygame.Rect((475, 750), (20, 20)),pygame.Surface((20, 20)),ui_manager)

    equip_slotsi1 = pygame_gui.elements.UIImage(pygame.Rect((675, 650), (20, 20)),pygame.Surface((20, 20)),ui_manager)
    equip_slotsi2 = pygame_gui.elements.UIImage(pygame.Rect((675, 675), (20, 20)),pygame.Surface((20, 20)),ui_manager)
    equip_slotsi3 = pygame_gui.elements.UIImage(pygame.Rect((675, 700), (20, 20)),pygame.Surface((20, 20)),ui_manager)
    equip_slotsi4 = pygame_gui.elements.UIImage(pygame.Rect((675, 725), (20, 20)),pygame.Surface((20, 20)),ui_manager)
    equip_slotsi5 = pygame_gui.elements.UIImage(pygame.Rect((675, 750), (20, 20)),pygame.Surface((20, 20)),ui_manager)

    equip_slotsj1 = pygame_gui.elements.UIImage(pygame.Rect((875, 650), (20, 20)),pygame.Surface((20, 20)),ui_manager)
    equip_slotsj2 = pygame_gui.elements.UIImage(pygame.Rect((875, 675), (20, 20)),pygame.Surface((20, 20)),ui_manager)
    equip_slotsj3 = pygame_gui.elements.UIImage(pygame.Rect((875, 700), (20, 20)),pygame.Surface((20, 20)),ui_manager)
    equip_slotsj4 = pygame_gui.elements.UIImage(pygame.Rect((875, 725), (20, 20)),pygame.Surface((20, 20)),ui_manager)
    equip_slotsj5 = pygame_gui.elements.UIImage(pygame.Rect((875, 750), (20, 20)),pygame.Surface((20, 20)),ui_manager)

                                            
    equip_slot_party1_weapon = [equip_slota1, equip_slotsb1, equip_slotsc1, equip_slotsd1, equip_slotse1]
    equip_slot_party2_weapon = [equip_slotsf1, equip_slotsg1, equip_slotsh1, equip_slotsi1, equip_slotsj1]

    equip_slot_party1_armor = [equip_slota2, equip_slotsb2, equip_slotsc2, equip_slotsd2, equip_slotse2]
    equip_slot_party2_armor = [equip_slotsf2, equip_slotsg2, equip_slotsh2, equip_slotsi2, equip_slotsj2]

    equip_slot_party1_accessory = [equip_slota3, equip_slotsb3, equip_slotsc3, equip_slotsd3, equip_slotse3]
    equip_slot_party2_accessory = [equip_slotsf3, equip_slotsg3, equip_slotsh3, equip_slotsi3, equip_slotsj3]

    equip_slot_party1_boots = [equip_slota4, equip_slotsb4, equip_slotsc4, equip_slotsd4, equip_slotse4]
    equip_slot_party2_boots = [equip_slotsf4, equip_slotsg4, equip_slotsh4, equip_slotsi4, equip_slotsj4]

    equip_set_slot_party1 = [equip_slota5, equip_slotsb5, equip_slotsc5, equip_slotsd5, equip_slotse5]
    equip_set_slot_party2 = [equip_slotsf5, equip_slotsg5, equip_slotsh5, equip_slotsi5, equip_slotsj5]                            

    for slot in equip_set_slot_party1 + equip_set_slot_party2:
        slot.set_image(images_item["KKKKK"])

    # Character Names and Level Labels
    # ==========================
    label1 = pygame_gui.elements.UILabel(pygame.Rect((75, 10), (200, 50)),
                                        "label",
                                        ui_manager)

    label2 = pygame_gui.elements.UILabel(pygame.Rect((275, 10), (200, 50)),
                                        "label",
                                        ui_manager)

    label3 = pygame_gui.elements.UILabel(pygame.Rect((475, 10), (200, 50)),
                                        "label",
                                        ui_manager)

    label4 = pygame_gui.elements.UILabel(pygame.Rect((675, 10), (200, 50)),
                                        "label",
                                        ui_manager)

    label5 = pygame_gui.elements.UILabel(pygame.Rect((875, 10), (200, 50)),
                                        "label",
                                        ui_manager)

    label6 = pygame_gui.elements.UILabel(pygame.Rect((75, 610), (200, 50)),
                                        "label",
                                        ui_manager)

    label7 = pygame_gui.elements.UILabel(pygame.Rect((275, 610), (200, 50)),
                                        "label",
                                        ui_manager)

    label8 = pygame_gui.elements.UILabel(pygame.Rect((475, 610), (200, 50)),
                                        "label",
                                        ui_manager)

    label9 = pygame_gui.elements.UILabel(pygame.Rect((675, 610), (200, 50)),
                                        "label",
                                        ui_manager)

    label10 = pygame_gui.elements.UILabel(pygame.Rect((875, 610), (200, 50)),
                                        "label",
                                        ui_manager)

    label_party1 = [label1, label2, label3, label4, label5]
    label_party2 = [label6, label7, label8, label9, label10]
    

    # UI Components
    # =====================================
    # Left Side 

    button1 = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((100, 300), (156, 35)),
                                        text='Shuffle Party',
                                        manager=ui_manager,
                                        tool_tip_text = "Shuffle party and restart the battle")
    button1.set_tooltip("Shuffle the party members and restart battle. On adventure mode, only party 1 is shuffled.", delay=0.1, wrap_width=300)

    button4 = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((100, 340), (156, 35)),
                                        text='Restart Battle',
                                        manager=ui_manager,
                                        tool_tip_text = "Restart battle")
    button4.set_tooltip("Restart battle.", delay=0.1)

    button3 = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((100, 380), (156, 35)),
                                        text='All Turns',
                                        manager=ui_manager,
                                        tool_tip_text = "Skip to the end of the battle.")
    button3.set_tooltip("Skip to the end of the battle.", delay=0.1, wrap_width=300)

    button_left_simulate_current_battle = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((100, 420), (78, 50)),
                                        text='Simulate',
                                        manager=ui_manager)
    button_left_simulate_current_battle.set_tooltip("Simulate current battle n times and print the result.", delay=0.1, wrap_width=300)

    selection_simulate_current_battle = pygame_gui.elements.UIDropDownMenu(["100", "200", "500", "1000", "2000"],
                                                            "100",
                                                            pygame.Rect((180, 420), (76, 50)),
                                                            ui_manager)

    settings_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((100, 480), (156, 50)),
                                        text='Settings',
                                        manager=ui_manager,)
    settings_button.set_tooltip("Open settings window.", delay=0.1, wrap_width=300)


    button_quit_game = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((100, 540), (156, 50)),
                                        text='Quit',
                                        manager=ui_manager,
                                        tool_tip_text = "Quit")
    button_quit_game.set_tooltip("Save player data as player_data.json and exit.", delay=0.1, wrap_width=300)

    # =====================================
    # Right Side

    next_turn_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((900, 300), (156, 50)),
                                        text='Next Turn',
                                        manager=ui_manager,
                                        tool_tip_text = "Simulate the next turn")
    next_turn_button_tooltip_str = "Next turn. Rewards are earned if the battle is won in adventure mode." \
    " The details of rewards are shown when hovering over the stage number label."
    next_turn_button.set_tooltip(next_turn_button_tooltip_str, delay=0.1, wrap_width=300)

    auto_battle_bar = pygame_gui.elements.UIStatusBar(pygame.Rect((900, 355), (156, 10)),
                                               ui_manager,
                                               None)

    button_auto_battle = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((900, 365), (156, 50)),
                                        text='Auto Battle',
                                        manager=ui_manager,)
    button_auto_battle.set_tooltip("Automatically proceed to the next turn when the progress bar is full. Rewards are earned when the battle is over.", delay=0.1, wrap_width=300)

    # Cheems Button with height 50, Cheems is a meme dog = Teams
    button_cheems = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((900, 420), (156, 50)),
                                        text='Cheems',
                                        manager=ui_manager,)
    button_cheems.set_tooltip("Open team selection window.", delay=0.1, wrap_width=300)

    # Characters Button with height 50
    button_characters = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((900, 480), (156, 50)),
                                        text='Characters',
                                        manager=ui_manager,)
    button_characters.set_tooltip("Open character window.", delay=0.1, wrap_width=300)

    # About Button with height 50
    button_about = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((900, 540), (156, 50)),
                                        text='About',
                                        manager=ui_manager,)
    button_about.set_tooltip("Open about window.", delay=0.1, wrap_width=300)


    def decide_auto_battle_speed():
        speed = global_vars.autobattle_speed
        match speed:
            case "Veryslow":
                return 10.0
            case "Slow":
                return 5.0
            case "Normal":
                return 2.5
            case "Fast":
                return 1.25
            case "Veryfast":
                return 0.625
            case _:
                raise ValueError(f"Invalid speed: {speed}")

    # =====================================
    # Far Right

    current_display_chart = "Damage Dealt Chart"
    chart_selection_label = pygame_gui.elements.UILabel(pygame.Rect((1080, 20), (156, 35)),
                                        "Show Chart:",
                                        ui_manager)
    chart_selection_label.set_tooltip("Select the chart to display: Damage dealt, Damage received, Healing.", delay=0.1, wrap_width=300)

    button_change_chart_selection = pygame_gui.elements.UIDropDownMenu(["Damage Dealt", "Damage Received", "Healing"],
                                                            "Damage Dealt",
                                                            pygame.Rect((1080, 60), (156, 35)),
                                                            ui_manager)

    current_game_mode = "Training Mode"
    game_mode_selection_label = pygame_gui.elements.UILabel(pygame.Rect((1080, 100), (156, 35)),
                                        "Game Mode:",
                                        ui_manager)
    game_mode_selection_label.set_tooltip("Select the game mode: Training Mode, Adventure Mode.", delay=0.1, wrap_width=300)

    game_mode_selection_menu = pygame_gui.elements.UIDropDownMenu(["Training Mode", "Adventure Mode"],
                                                            "Training Mode",
                                                            pygame.Rect((1080, 140), (156, 50)),
                                                            ui_manager)

    label_character_selection_menu = pygame_gui.elements.UILabel(pygame.Rect((1080, 195), (156, 35)),
                                        "Selected Character:",
                                        ui_manager)
    label_character_selection_menu.set_tooltip("Selected character. Use items, equip, unequip and others use this character as target.", delay=0.1, wrap_width=300)

    character_selection_menu_pos = pygame.Rect((1080, 235), (156, 50))
    character_selection_menu = pygame_gui.elements.UIDropDownMenu(["Option 1", "Option 2", "Option 3", "Option 4", "Option 5"],
                                                            "Option 1",
                                                            character_selection_menu_pos,
                                                            ui_manager)

    use_item_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((1080, 290), (100, 35)),
                                        text='Equip Item',
                                        manager=ui_manager,
                                        tool_tip_text = "Use selected item for selected character.")
    use_item_button.set_tooltip("The selected item is used on the selected character. If the selected item is an equipment item, equip it to the selected character. Multiple items may be equipped or used at one time.",
                                delay=0.1, wrap_width=300)
    use_itemx10_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((1185, 290), (51, 35)),
                                        text='x10',
                                        manager=ui_manager,
                                        tool_tip_text = "Use selected item 10 times.")
    use_itemx10_button.set_tooltip("Use selected item 10 times, only effective on comsumables.", delay=0.1, wrap_width=300)

    eq_rarity_list, eq_types_list, eq_set_list = Equip("Foo", "Weapon", "Common").get_raritytypeeqset_list()
    eq_set_list_without_none_and_void = [x for x in eq_set_list if x != "None" and x != "Void"]
    eq_set_list_without_none_and_void.sort()
    print(f"Loaded {len(eq_set_list_without_none_and_void)} equipment sets.")

    eq_selection_menu = pygame_gui.elements.UIDropDownMenu(eq_types_list,
                                                            eq_types_list[0],
                                                            pygame.Rect((1080, 330), (156, 35)),
                                                            ui_manager)

    character_eq_unequip_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((1080, 370), (100, 35)),
                                        text='Unequip',
                                        manager=ui_manager,
                                        tool_tip_text = "Unequip selected item from selected character")
    character_eq_unequip_button.set_tooltip("Remove equipment from the selected character.", delay=0.1, wrap_width=300)

    character_eq_unequip_all_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((1185, 370), (51, 35)),
                                        text='All',
                                        manager=ui_manager,
                                        tool_tip_text = "Unequip all items from selected character")
    character_eq_unequip_all_button.set_tooltip("Remove all equipment from the selected character.", delay=0.1, wrap_width=300)

    eq_levelup_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((1080, 410), (100, 35)),
                                        text='Level Up',
                                        manager=ui_manager,
                                        tool_tip_text = "Level up selected item.")
    eq_levelup_button.set_tooltip("Level up selected equipment in the inventory.", delay=0.1, wrap_width=300)

    eq_levelup_buttonx10 = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((1185, 410), (51, 35)),
                                        text='x10',
                                        manager=ui_manager,
                                        tool_tip_text = "Level up selected item.")
    eq_levelup_buttonx10.set_tooltip("Level up for 10 levels for selected equipment in the inventory.", delay=0.1, wrap_width=300)


    eq_level_up_to_max_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((1080, 450), (156, 35)),
                                        text='Level Up To Max',
                                        manager=ui_manager,
                                        tool_tip_text = "Try level up selected item to max level until Cash is exhausted.")
    eq_level_up_to_max_button.set_tooltip("Level up selected equipment in the inventory to the maximum level.", delay=0.1, wrap_width=300)


    eq_stars_upgrade_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((1080, 490), (156, 35)),
                                        text='Star Enhancement',
                                        manager=ui_manager,
                                        tool_tip_text = "Upgrade stars for item")
    eq_stars_upgrade_button.set_tooltip("Increase the star rank of selected equipment in inventory.", delay=0.1, wrap_width=300)

    
    eq_sell_selected_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((1080, 530), (156, 35)),
                                        text='Sell Selected',
                                        manager=ui_manager,
                                        tool_tip_text = "Sell selected item.")
    eq_sell_selected_button.set_tooltip("Sell selected equipment in the inventory.", delay=0.1, wrap_width=300)

    eq_mass_sell_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((1080, 570), (156, 50)),
                                        text='Mass Sell',
                                        manager=ui_manager,
                                        tool_tip_text = "Sell equipment based on some attributes.")
    eq_mass_sell_button.set_tooltip("Sell equipment in inventory based on some attributes.", delay=0.1, wrap_width=300)

    # =====================================
    # Switches on when changing cheap_inventory_what_to_show to Consumables
    item_sell_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((1080, 330), (156, 35)),
                                        text='Sell Item',
                                        manager=ui_manager,
                                        tool_tip_text = "Sell selected item in inventory.")
    item_sell_button.set_tooltip("Sell one selected item from your inventory.", delay=0.1, wrap_width=300)
    item_sell_button.hide()
    item_sell_half_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((1080, 370), (100, 35)),
                                        text='Sell Half',
                                        manager=ui_manager,
                                        tool_tip_text = "Sell half stack of selected item in inventory.")
    item_sell_half_button.set_tooltip("Sell half a stack of selected items.", delay=0.1, wrap_width=300)
    item_sell_half_button.hide()
    item_sell_all_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((1185, 370), (51, 35)),
                                        text='All',
                                        manager=ui_manager,
                                        tool_tip_text = "Sell all of selected item in inventory.")
    item_sell_all_button.set_tooltip("Sell all of selected items.", delay=0.1, wrap_width=300)
    item_sell_all_button.hide()

    use_random_consumable_label = pygame_gui.elements.UILabel(pygame.Rect((1080, 410), (156, 35)),
                                        "Random Use:",
                                        ui_manager)
    use_random_consumable_label.set_tooltip("Use one appropriate consumable each turn during auto battles.", delay=0.1, wrap_width=300)
    use_random_consumable_label.hide()
    use_random_consumable_selection_menu = pygame_gui.elements.UIDropDownMenu(["True", "False"],
                                                            "False",
                                                            pygame.Rect((1080, 450), (156, 35)),
                                                            ui_manager)
    use_random_consumable_selection_menu.hide()


    # =====================================
    # Game Mode Section
    # =====================================

    def adventure_mode_generate_stage(force_regenerate_stage: bool = False):
        global current_game_mode, adventure_mode_current_stage, adventure_mode_stages
        for m in all_monsters:
            m.lvl = adventure_mode_current_stage
        # Boss monsters have attribute is_boss = True, every 10 stages, starting from stage 10, summon a boss monster
        # Stage 1000 to 2000, every stage has a boss monster in the middle of the stage.
        # Howerver, on stage 2000 and later, there will be no restriction on whether boss or not.
        if (adventure_mode_current_stage % 10 == 0 or adventure_mode_current_stage > 1000) and adventure_mode_current_stage < 2000:
            new_selection_of_monsters = random.sample([x for x in all_monsters if not x.is_boss], k=4)
            boss_monster = random.choice([x for x in all_monsters if x.is_boss])
            new_selection_of_monsters.insert(2, boss_monster)
        elif adventure_mode_current_stage >= 2000:
            new_selection_of_monsters = random.sample(all_monsters, k=5)
        else:
            new_selection_of_monsters = random.sample([x for x in all_monsters if not x.is_boss], k=5)

        if not adventure_mode_stages.get(adventure_mode_current_stage) or force_regenerate_stage:
            adventure_mode_stages[adventure_mode_current_stage] = new_selection_of_monsters

        # v3.3.0: Because we can easily edit party members now, generating for all monsters is needed.
        if adventure_mode_current_stage < 500:
            # for m in adventure_mode_stages[adventure_mode_current_stage]:
            for m in all_monsters:
                m.equip_item_from_list(generate_equips_list(4, locked_eq_set="Void", include_void=True, locked_rarity="Common", 
                                                            eq_level=int(adventure_mode_current_stage)))
        elif 500 <= adventure_mode_current_stage < 1000:
            for m in all_monsters:
                m.equip_item_from_list(generate_equips_list(4, locked_eq_set="Void", include_void=True, locked_rarity="Uncommon", 
                                                            eq_level=int(adventure_mode_current_stage)))
        elif 1000 <= adventure_mode_current_stage < 1500:
            for m in all_monsters:
                m.equip_item_from_list(generate_equips_list(4, locked_eq_set="Void", include_void=True, locked_rarity="Rare", 
                                                            eq_level=int(adventure_mode_current_stage)))
        elif 1500 <= adventure_mode_current_stage < 2000:
            for m in all_monsters:
                m.equip_item_from_list(generate_equips_list(4, locked_eq_set="Void", include_void=True, locked_rarity="Epic", 
                                                            eq_level=int(adventure_mode_current_stage)))
        elif 2000 <= adventure_mode_current_stage < 2500:
            for m in all_monsters:
                m.equip_item_from_list(generate_equips_list(4, locked_eq_set="Void", include_void=True, locked_rarity="Unique", 
                                                            eq_level=int(adventure_mode_current_stage)))
        elif 2500 <= adventure_mode_current_stage:
            for m in all_monsters:
                m.equip_item_from_list(generate_equips_list(4, locked_eq_set="Void", include_void=True, locked_rarity="Legendary", 
                                                            eq_level=int(adventure_mode_current_stage)))

    def adventure_mode_stage_increase():
        global current_game_mode, adventure_mode_current_stage
        if current_game_mode == "Training Mode":
            raise Exception("Cannot change stage in Training Mode. See Game Mode Section.")
        if adventure_mode_current_stage == 3000:
            text_box.set_text("We have reached the end of the world.\n")
            return False
        if player.cleared_stages < adventure_mode_current_stage:
            text_box.set_text("We have not cleared the current stage.\n")
            return False
        adventure_mode_current_stage += 1
        adventure_mode_generate_stage()
        set_up_characters_adventure_mode()
        return True

    def adventure_mode_stage_decrease():
        global current_game_mode, adventure_mode_current_stage
        if current_game_mode == "Training Mode":
            raise Exception("Cannot change stage in Training Mode. See Game Mode Section.")
        if adventure_mode_current_stage == 1:
            text_box.set_text("This stage is the start of the journey.\n")
            return
        adventure_mode_current_stage -= 1
        adventure_mode_generate_stage()
        set_up_characters_adventure_mode()

    def adventure_mode_stage_refresh():
        global current_game_mode, adventure_mode_current_stage
        if current_game_mode == "Training Mode":
            raise Exception("Cannot change stage in Training Mode. See Game Mode Section.")
        adventure_mode_generate_stage(force_regenerate_stage=True)
        set_up_characters_adventure_mode()

    def adventure_mode_exp_reward():
        global adventure_mode_current_stage, party1, party2
        average_party_level = sum([x.lvl for x in party1]) / 5
        enemy_average_level = adventure_mode_current_stage
        # if enemy level is above average party level, then exp reward is increased by a percentage
        exp_reward_multiplier = 1
        if enemy_average_level > average_party_level:
            exp_reward_multiplier = (enemy_average_level / average_party_level)
        if current_game_mode == "Adventure Mode":
            for m in party2:
                if m.is_boss:
                    exp_reward_multiplier *= 1.5

        return int(adventure_mode_current_stage * exp_reward_multiplier)

    def adventure_mode_cash_reward():
        global adventure_mode_current_stage, party1, party2
        average_party_level = sum([x.lvl for x in party1]) / 5
        enemy_average_level = adventure_mode_current_stage
        cash_reward_multiplier = 1
        if enemy_average_level > average_party_level:
            cash_reward_multiplier = (enemy_average_level / average_party_level)
        random_factor = random.uniform(0.8, 1.2)
        cash_before_random = adventure_mode_current_stage * 2 * cash_reward_multiplier
        cash = cash_before_random * random_factor
        if current_game_mode == "Adventure Mode":
            for m in party2:
                if m.is_boss:
                    cash *= 1.5
                    cash_before_random *= 1.5
        cash = max(1, cash)
        return int(cash), int(cash_before_random)
    
    def adventure_mode_info_tooltip() -> str:
        global adventure_mode_current_stage
        if global_vars.language == "日本語":
            return adventure_mode_info_tooltip_jp()
        str = f"Current Stage: {adventure_mode_current_stage}\n"
        if adventure_mode_current_stage > sum([x.lvl for x in party1]) / 5:
            str += f"Enemy level is higher than average party level, reward is increased by {(adventure_mode_current_stage / (sum([x.lvl for x in party1]) / 5) - 1) * 100:.2f}%."
        str += " Rewards are increased by 50% for each boss monsters."
        try:
            amount_of_bosses = len([x for x in party2 if x.is_boss])
        # sometimes someone in party2 is not a monster
        except AttributeError:
            amount_of_bosses = 0
        if amount_of_bosses > 0:
            str += f" Amount of Bosses: {amount_of_bosses}."
        str += f" Exp Reward: {adventure_mode_exp_reward()}."
        a, b = adventure_mode_cash_reward()
        str += f" Cash Reward: approxmately {b}."
        return str

    def adventure_mode_info_tooltip_jp() -> str:
        global adventure_mode_current_stage
        str = f"現在のステージ:{adventure_mode_current_stage}\n"
        if adventure_mode_current_stage > sum([x.lvl for x in party1]) / 5:
            str += f"敵のレベルがパーティーの平均レベルより高いため、報酬が{(adventure_mode_current_stage / (sum([x.lvl for x in party1]) / 5) - 1) * 100:.2f}%増加する。"
        str += "ボスモンスターごとに報酬が50%増加する。"
        try:
            amount_of_bosses = len([x for x in party2 if x.is_boss])
        # sometimes someone in party2 is not a monster
        except AttributeError:
            amount_of_bosses = 0
        if amount_of_bosses > 0:
            str += f"ボスの数:{amount_of_bosses}."
        str += f"経験値報酬:{adventure_mode_exp_reward()}。"
        a, b = adventure_mode_cash_reward()
        str += f"現金報酬:約{b}。"
        return str


    # =====================================
    # End of Game Mode Section
    # =====================================
    # Character Section
    # =====================================

    character_window = None
    character_window_command_line = None
    character_window_submit_button = None
    character_window_show_guide_button = None
    character_window_command_result_box = None


    def build_character_window():
        global character_window, character_window_command_line, character_window_submit_button
        global character_window_show_guide_button, character_window_command_result_box
        try:
            character_window.kill()
        except Exception as e:
            pass

        def local_translate(s: str) -> str:
            if global_vars.language == "English":
                return s
            elif global_vars.language == "日本語":
                match s:
                    case "Enter the command devoutly.":
                        return "敬虔な気持ちでコマンドを入力しなさい。"
                    case "Submit":
                        return "献上"
                    case "Guide":
                        return "指南"
                    case _:
                        return s
            else:
                raise ValueError(f"Unknown language: {global_vars.language}")


        character_window = pygame_gui.elements.UIWindow(pygame.Rect((300, 180), (500, 510)),
                                            ui_manager,
                                            window_display_title="Characters",
                                            object_id="#characters_window",
                                            resizable=False)

        character_window_command_line = pygame_gui.elements.UITextEntryLine(pygame.Rect((10, 10), (480, 35)),
                                            ui_manager,
                                            container=character_window,
                                            placeholder_text=local_translate("Enter the command devoutly."))
        
        character_window_submit_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((10, 50), (240, 50)),
                                        text=local_translate("Submit"),
                                        manager=ui_manager,
                                        container=character_window,
                                        command=lambda: advanced_character_command_add_to_result_box(character_window_command_line.get_text()))

        def result_box_add_guide():
            global eq_sell_window_command_result_box
            if global_vars.language == "English":
                result_box_guide = "This section provides functionality to quickly find or perform operations related to characters." \
                " Click on the character name link while holding either 12345 assigns the character to party1," \
                " while holding either qwert assigns the character to party2." \
                " The following commands are available:\n" \
                "<font color=#FF69B4>ls</font>\n" \
                "List all characters, ordered by level. This command is executed if no commands are given.\n" \
                "<font color=#FF69B4>cweqs [str]</font>\n" \
                "Print all characters with [str] equipment set, [str] allows lower case and partial matches. Use None to find characters without equipment set." \
                " If [str] is not specified, all equipment set and characters are printed.\n" \
                "<font color=#FF69B4>fwsd [str]</font>\n" \
                "Print all characters with skill description containing [str].\n" \
                "<font color=#FF69B4>fwss [str]</font>\n" \
                "Print all characters with skill source code containing [str]." \
                " This command is useful for finding characters with certain skill interactions, for example: AbsorptionShield." \
                " The first time this command and ss command is used, the source code is loaded and will take 10 to 30 seconds.\n" \
                "<font color=#FF69B4>ss (character_name)</font>\n" \
                "View source code of the character. If character_name is omitted, use selected character.\n" \
                "<font color=#FF69B4>ce</font>\n" \
                "Compare selected equipment with all characters equipment. Only the same equipment type and set are compared.\n" \
                "<font color=#FF69B4>euc</font>\n" \
                "This command functions the same as the ce command." \
                " Equipment upgrade to characters. For the selected equipment, find all equipment with the same type and set equipped on any character," \
                " but only when this equipment is better than the current equipment of the character. better: for_attacker_value is higher or for_support_value is higher.\n" \
                "<font color=#FF69B4>cue (equipment type)</font>\n" \
                "Character upgrade equipment. For the selected character and entered equipment type, find all equipment with the same set and type in the inventory," \
                " but only when the equipment found is better than the current equipment of the character. better: for_attacker_value is higher or for_support_value is higher." \
                " Equipment type can be omitted, in this case, use the equipment type from selection menu. Only the top 500 entries are shown.\n"
                character_window_command_result_box.set_text(html_text=result_box_guide)
            elif global_vars.language == "日本語":
                result_box_guide = "このセクションでは、キャラクターに関連する操作や検索を素早く行う機能を提供する。" \
                "12345キーを押しながらキャラクター名リンクをクリックすると、キャラクターがparty1に割り当てられ、" \
                "qwertキーを押しながらキャラクター名リンクをクリックすると、キャラクターがparty2に割り当てられる。" \
                "使用可能なコマンドは以下の通りです:\n" \
                "<font color=#FF69B4>ls</font>\n" \
                "レベル順に並べ替えられたすべてのキャラクターを一覧表示する。コマンドが指定されていない場合、このコマンドが実行される。\n" \
                "<font color=#FF69B4>cweqs [str]</font>\n" \
                "[str]装備セットを持つすべてのキャラクターを表示する。[str] は小文字や部分一致も可能です。Noneを使用すると装備セットがないキャラクターを検索できる。" \
                "[str]が指定されない場合、すべての装備セットとキャラクターが表示される。\n" \
                "<font color=#FF69B4>fwsd [str]</font>\n" \
                "[str]を含むスキル説明を持つすべてのキャラクターを表示する。\n" \
                "<font color=#FF69B4>fwss [str]</font>\n" \
                "[str]を含むスキルのソースコードを持つすべてのキャラクターを表示する。" \
                "このコマンドは特定のスキルの相互作用（例:AbsorptionShield）を持つキャラクターを検索する際に便利です。" \
                "このコマンドとssコマンドを初めて使用すると、ソースコードが読み込まれ、10から30秒かかります。\n" \
                "<font color=#FF69B4>ss (character_name)</font>\n" \
                "指定したキャラクターのソースコードを表示する。character_nameが省略さらた場合、選択したキャラクターを使用する。\n" \
                "<font color=#FF69B4>ce</font>\n" \
                "選択した装備とすべてのキャラクターの装備を比較する。同じ装備タイプとセットのみが比較される。\n" \
                "<font color=#FF69B4>euc</font>\n" \
                "このコマンドはceコマンドと同じ機能を持つ。選択した装備について、同じタイプとセットのキャラクター装備を検索し、" \
                "ただし、この装備がキャラクターの現在の装備よりも優れている場合にのみ表示される。優れているのは攻撃相性或いは防御相性が高い。\n" \
                "<font color=#FF69B4>cue (equipment type)</font>\n" \
                "キャラクターの装備をアップグレードする。選択したキャラクターと入力された装備タイプについて、インベントリ内の同じセットとタイプの装備を検索し、" \
                "ただし、検出された装備がキャラクターの現在の装備よりも優れている場合にのみ表示される。優れているのは攻撃相性或いは防御相性が高い。" \
                "装備タイプは省略可能で、この場合、選択メニューから装備タイプを使用します。上位500エントリのみ表示される。\n"

                character_window_command_result_box.set_text(html_text=result_box_guide)


        character_window_show_guide_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((260, 50), (230, 50)),
                                        text=local_translate("Guide"),
                                        manager=ui_manager,
                                        container=character_window,
                                        command=result_box_add_guide)

        character_window_command_result_box = pygame_gui.elements.UITextBox(html_text="",
                                        relative_rect=pygame.Rect((10, 110), (480, 350)),
                                        manager=ui_manager,
                                        container=character_window,
                                        object_id="#character_window_command_result_box")

        result_box_add_guide()

    def advanced_character_command_add_to_result_box(command: str):
        result = advanced_character_command(command)
        character_window_command_result_box.set_text(html_text=result)

    def advanced_character_command(command: str):
        global all_characters, eq_set_list
        if command == "":
            command = "ls"
        command_fragmented = command.split()
        
        if command_fragmented[0] == "ls":
            # get all characters, ordered by level and name
            all_characters_sorted = sorted(all_characters, key=lambda x: (x.lvl, x.name))
            string = ""
            for c in all_characters_sorted:
                string += f"level {c.lvl} <a href='{c.name}'>{c.name}</a>\n"
            return string
        
        elif command_fragmented[0] == "cweqs":
            if len(command_fragmented) < 2:
                # print all eqsets with characters
                eq_set_all_available = [s.lower() for s in eq_set_list]
                s = ""
                for es in eq_set_all_available:
                    characters_with_eq_set = [x for x in all_characters if x.get_equipment_set().lower() == es]
                    linked_names = [f"<a href='{x.name}'>{x.name}</a>" for x in characters_with_eq_set]
                    s += f"Characters with equipment set '{es}':\n" + ", ".join(linked_names)
                    s += "\n"
                return s
            eq_set = command_fragmented[1]
            
            # eq_set_list is a list of str of all equipment sets in the game
            eq_set_all_available = [s.lower() for s in eq_set_list]
            
            # Find close matches
            close_matches = difflib.get_close_matches(eq_set.lower(), eq_set_all_available, n=1, cutoff=0.6)
            if not close_matches:
                return f"Equipment set does not exist: {eq_set}."
            
            matched_eq_set = close_matches[0]
            characters_with_eq_set = [x for x in all_characters if x.get_equipment_set().lower() == matched_eq_set]
            if not characters_with_eq_set:
                return f"No character has equipment set {matched_eq_set}."
            
            linked_names = [f"<a href='{x.name}'>{x.name}</a>" for x in characters_with_eq_set]
            return f"Characters with equipment set '{matched_eq_set}':\n" + ", ".join(linked_names)
        
        elif command_fragmented[0] == "fwsd":
            # find certain characters with skill description
            if len(command_fragmented) < 2:
                return "No keyword entered."
            keyword: str = " ".join(command_fragmented[1:])
            matched_characters = [x for x in all_characters if keyword.lower() in x.skill_tooltip_jp().lower() + x.skill_tooltip().lower()]
            if not matched_characters:
                return f"No character has skill description containing '{keyword}'."
            linked_names = [f"<a href='{x.name}'>{x.name}</a>" for x in matched_characters]
            return f"Characters with skill description containing '{keyword}':\n" + ", ".join(linked_names)

        elif command_fragmented[0] == "fwss":
            # find with skill source code, useful to find certain interactions
            if len(command_fragmented) < 2:
                return "No keyword entered."
            if not fwss_source_code_cache or not fwss_noinit_source_code_cache:
                fwss_cache_source_code()
            keyword: str = " ".join(command_fragmented[1:])
            matched_characters = []
            for x in all_characters:
                source_code = fwss_noinit_source_code_cache[x.__class__.__name__]
                # source_code_without_init = remove_init_method(source_code)
                if keyword in source_code:
                    matched_characters.append(x)
            if not matched_characters:
                return f"No character has skill source code containing '{keyword}'."
            linked_names = [f"<a href='{x.name}'>{x.name}</a>" for x in matched_characters]
            return f"Characters with skill source code containing '{keyword}':\n" + ", ".join(linked_names)
        
        elif command_fragmented[0] == "ss":
            # print the character's source code
            if len(command_fragmented) < 2:
                character_name = character_selection_menu.selected_option[0].split()[-1]
            else:
                character_name = command_fragmented[1]
            if not fwss_source_code_cache or not fwss_noinit_source_code_cache:
                fwss_cache_source_code()
            
            matched_characters = [x for x in all_characters if x.name.lower() == character_name.lower()]
            if not matched_characters:
                return f"No character with name '{character_name}'."
            character = matched_characters[0]
            source_code = fwss_source_code_cache[character.__class__.__name__]
            return f"Source code for <a href='{character.name}'>{character.name}</a>:\n" + "<font color=#6495ed>" + source_code + "</font>"
        
        elif command_fragmented[0] == "ce":
            # compare equipment, get first equipment from selected by player, then get all same equipment (same eq set and same type) from all characters
            # then compare the stats
            selected_equipment: Equip | None = None
            for surface, selected, the_actual_item in player.selected_item.values():
                if selected:
                    selected_equipment = the_actual_item
                    break
            if not selected_equipment:
                return "No equipment selected."
            if not isinstance(selected_equipment, Equip):
                return "Selected item is not an equipment."
            # return_string = f"Selected equipment:\n{selected_equipment.print_stats_html()}"
            # return_string += "\n\n"
            return_string = "Characters with the same equipment:\n"
            for character in all_characters:
                # print(character.equip)
                # {'Weapon': <equip.Equip object at 0x7afa4c1fd4f0>, 'Accessory': <equip.Equip object at 0x7afa4c1fd580>, 'Boots': <equip.Equip object at 0x7afa4c1fd5e0>, 'Armor': <equip.Equip object at 0x7afa4c1fd640>}
                # if it has the same type equipped:
                if selected_equipment.type in character.equip:
                    if selected_equipment.eq_set == character.equip[selected_equipment.type].eq_set:
                        return_string += f"<a href='{character.name}'>{character.name}</a>"
                        if global_vars.language == "English":
                            return_string += f"\n{character.equip[selected_equipment.type].print_stats_html(item_to_compare=selected_equipment, include_set_effect=False)}\n"
                        elif global_vars.language == "日本語":
                            return_string += f"\n{character.equip[selected_equipment.type].print_stats_html_jp(item_to_compare=selected_equipment, include_set_effect=False)}\n"
                        else:
                            raise ValueError(f"Unknown language: {global_vars.language}")
            return return_string
        
        elif command_fragmented[0] == "euc":
            # similar to ce command.
            # equipment update characters. Select an equipment, find all characters with the same equipment,
            # however, only when this equipment is better than the character's current equipment, it is shown.
            # 'better': for_attacker_value is higher or for_support_value is higher
            selected_equipment: Equip | None = None
            for surface, selected, the_actual_item in player.selected_item.values():
                if selected:
                    selected_equipment = the_actual_item
                    break
            if not selected_equipment:
                return "No equipment selected."
            if not isinstance(selected_equipment, Equip):
                return "Selected item is not an equipment."
            
            # Prepare a list to hold characters and their upgrade priority (difference value)
            upgrade_list = []
            for character in all_characters:
                # if it has the same type equipped:
                if selected_equipment.type in character.equip:
                    if selected_equipment.eq_set == character.equip[selected_equipment.type].eq_set:
                        current_equip = character.equip[selected_equipment.type]
                        if selected_equipment.for_attacker_value > current_equip.for_attacker_value or \
                        selected_equipment.for_support_value > current_equip.for_support_value:
                            # Calculate the difference value
                            difference_value = (selected_equipment.for_attacker_value - current_equip.for_attacker_value) + \
                                            (selected_equipment.for_support_value - current_equip.for_support_value)
                            # Append to the list with the character and difference value
                            upgrade_list.append((character, difference_value, current_equip))
            
            # Sort the list by difference_value in descending order
            upgrade_list.sort(key=lambda x: x[1], reverse=True)
            
            # Construct the return string
            return_string = "Characters needing the most upgrade:\n"
            for character, diff_value, current_equip in upgrade_list:
                return_string += f"<a href='{character.name}'>{character.name}</a> (Upgrade Value: {diff_value})\n"
                if global_vars.language == "English":
                    return_string += f"{current_equip.print_stats_html(item_to_compare=selected_equipment, include_set_effect=False)}\n"
                elif global_vars.language == "日本語":
                    return_string += f"{current_equip.print_stats_html_jp(item_to_compare=selected_equipment, include_set_effect=False)}\n"
                else:
                    raise ValueError(f"Unknown language: {global_vars.language}")
            
            return return_string
        
        elif command_fragmented[0] == "cue":
            # character upgrade equipment. Target selected character, find all equipment of the entered type
            # from player.inventory, then compare the stats, if better, show them. A maximum of 500 entries are shown.
            if len(command_fragmented) < 2:
                selected_eq_type = eq_selection_menu.selected_option[0]
            else:
                selected_eq_type = command_fragmented[1]
                if selected_eq_type not in ["Weapon", "Armor", "Accessory", "Boots"]:
                    return f"Invalid equipment type entered: {selected_eq_type}."
            
            # Find selected character
            selected_character = None
            for character in party1 + party2:
                if character.name == character_selection_menu.selected_option[0].split()[-1]:
                    selected_character = character
                    break
            assert selected_character is not None, "No character selected."

            # Get current equipped item
            try:
                selected_character_eq = selected_character.equip[selected_eq_type]
            except KeyError:
                return f"{selected_character.name} does not have {selected_eq_type} equipped."

            # Filter inventory for matching equipment type and set
            filtered_eq_list = [
                eq for eq in player.inventory_equip
                if eq.type == selected_eq_type and eq.eq_set == selected_character_eq.eq_set
                and (eq.for_attacker_value > selected_character_eq.for_attacker_value or
                    eq.for_support_value > selected_character_eq.for_support_value)
            ]

            # Sort the filtered equipment by improvement value (difference)
            sorted_eq_list = sorted(
                filtered_eq_list,
                key=lambda eq: (eq.for_attacker_value - selected_character_eq.for_attacker_value) +
                            (eq.for_support_value - selected_character_eq.for_support_value),
                reverse=True
            )

            # Take only the best 500 entries
            best_500_eq_list = sorted_eq_list[:500]

            # Construct the return string
            return_string = f"Equipment for {selected_character.name} (Top 500 upgrades):\n"
            for i, eq in enumerate(best_500_eq_list):
                return_string += f"{eq.print_stats_html(item_to_compare=selected_character_eq, include_set_effect=False)}\n"

            if len(sorted_eq_list) > 500:
                return_string += "Showing the top 500 entries. Some entries were omitted.\n"

            return return_string


        else:
            return "Invalid command."




















    app_about_window = None

    def build_about_window():
        global app_about_window
        try:
            app_about_window.kill()
        except Exception as e:
            pass

        app_about_window = pygame_gui.elements.UIWindow(pygame.Rect((500, 300), (300, 100)),
                                            ui_manager,
                                            window_display_title="About",
                                            object_id="#about_window",
                                            resizable=False)


        aw_warning_label = pygame_gui.elements.UILabel(pygame.Rect((10, 10), (280, 35)),
                                        "App by Rokafox.",
                                        ui_manager,
                                        container=app_about_window)


    quit_game_window = None

    def build_quit_game_window():
        global quit_game_window, running
        try:
            quit_game_window.kill()
        except Exception as e:
            pass

        def local_translate(s: str) -> str:
            if global_vars.language == "English":
                return s
            elif global_vars.language == "日本語":
                match s:
                    case "Quit Game":
                        return "アプリ終了"
                    case "Save and Quit":
                        return "保存して終了"
                    case "Force Quit":
                        return "強制終了"
                    case _:
                        return s
            else:
                raise ValueError(f"Unknown language: {global_vars.language}")

        quit_game_window = pygame_gui.elements.UIWindow(
            pygame.Rect((500, 300), (300, 160)),
            ui_manager,
            window_display_title=local_translate("Quit Game"),
            object_id="#quit_game_window",
            resizable=False
        )

        def set_running_false():
            global running
            running = False

        def set_running_false_and_save():
            global running, player
            save_player(player)
            running = False

        quit_game_sq_button = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect((10, 10), (280, 50)),
            text=local_translate("Save and Quit"),
            manager=ui_manager,
            container=quit_game_window,
            command=set_running_false_and_save
        )

        quit_game_fq_button = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect((10, 70), (280, 50)),
            text=local_translate("Force Quit"),
            manager=ui_manager,
            container=quit_game_window,
            command=set_running_false
        )


    def use_item(how_many_times: int = 1):
        # Nine.selected_item = {} # {image_slot: UIImage : (image: Surface, is_highlighted: bool, the_actual_item: Equip|Consumable|Item)})}
        # get all selected items
        text_box.set_text("==============================\n")
        text_box_text_to_append = ""
        selected_items = []
        # print(player.selected_item)
        if not player.selected_item:
            text_box_text_to_append += "No item is selected.\n"
            text_box.append_html_text(text_box_text_to_append)
            return
        for a, b, c in player.selected_item.values():
            if b:
                selected_items.append(c) 
        # print(f"use_item() Selected items: {selected_items}")
        if not selected_items:
            text_box_text_to_append += "No item is selected.\n"
            text_box.append_html_text(text_box_text_to_append)
            return
        if global_vars.cheap_inventory_show_current_option == "Equip":
            if not is_in_manipulatable_game_states():
                text_box_text_to_append += "Cannot equip items when not in first turn or after the battle is concluded.\n"
                text_box.append_html_text(text_box_text_to_append)
                return
            for character in all_characters:
                if character.name == character_selection_menu.selected_option[0].split()[-1] and character.is_alive():
                    # check if selected items have more than 1 of the same type
                    item_types_seen = []
                    for item in selected_items:
                        if item.type in item_types_seen:
                            text_box_text_to_append += f"Cannot equip multiple items of the same type at once.\n"
                            text_box.append_html_text(text_box_text_to_append)
                            return
                        else:
                            item_types_seen.append(item.type)

                    for equip in selected_items:
                        text_box_text_to_append += f"Equipped {str(equip)} for {character.name}.\n"
                    old_items = character.equip_item_from_list(selected_items)
                    # remove all None in old_items, this happens when trying to equip to an empty slot, so None is returned
                    old_items = [x for x in old_items if x]
                    if old_items:
                        for items in old_items:
                            text_box_text_to_append += f"{str(items)} is added to inventory.\n"
                        player.remove_selected_item_from_inventory(False) # False because handled next line
                        player.add_package_of_items_to_inventory(old_items)
                    else:
                        player.remove_selected_item_from_inventory(True)
                elif character.name == character_selection_menu.selected_option[0].split()[-1] and not character.is_alive():
                    text_box_text_to_append += f"Can only equip items to alive characters.\n"
                    text_box.append_html_text(text_box_text_to_append)
                    return
        elif global_vars.cheap_inventory_show_current_option == "Consumable":
            for character in all_characters:
                if character.name == character_selection_menu.selected_option[0].split()[-1]:
                    for consumable in selected_items:
                        how_many_times_tmp = min(how_many_times, consumable.current_stack)
                        for i in range(how_many_times_tmp):
                            if not consumable.can_use_on_dead and not character.is_alive():
                                text_box_text_to_append += f"Dead character Cannot use {str(consumable)}.\n"
                                text_box.append_html_text(text_box_text_to_append)
                                return
                            # if comsumable is food, it takes effect in E() so this loop is enough for effect
                            # for else that uses E_actual(), E() only returns a string indicating what happened,
                            # then it is handled in player.use_1_selected_item() for actual effect.
                            # In conclusion, we should not have both E() and E_actual() for effects, although it is possible.
                            event_str = consumable.E(character, player)
                            text_box_text_to_append += event_str + "\n"
                    # player.use_1_selected_item will correctly handle cases when consumable.current_stack is less than how_many_times
                    player.use_1_selected_item(True, use_how_many_times=how_many_times, who_the_character=character)
        # Remember to change this if decided item can also be used on characters
        elif global_vars.cheap_inventory_show_current_option == "Item":
            for item in selected_items:
                event_str = item.E(None, player)
                text_box_text_to_append += event_str + "\n"
            if not "but nothing happened" in event_str:
                player.use_1_selected_item(True)

        redraw_ui(party1, party2) # slow but necessary. We could also consider only redraw the character that is selected,
        # but some equipment set effect may affact other characters.
        text_box.append_html_text(text_box_text_to_append)


    def use_random_consumable():
        """
        Feature for using one suitable consumable, for a random character in need.
        """
        if not auto_battle_active:
            raise Exception("Can only use random consumable when auto battle is active.")   
        characters_in_need = []
        if current_game_mode == "Adventure Mode":
            characters_in_need = [x for x in party1]
        elif current_game_mode == "Training Mode":
            characters_in_need = [x for x in itertools.chain(party1, party2)]
        random.shuffle(characters_in_need)
        for character in characters_in_need:
            all_consumables = [x for x in player.inventory_consumable if x.can_use_for_auto_battle]
            random.shuffle(all_consumables)
            if not all_consumables:
                global_vars.turn_info_string += f"Random use failed: No consumable in inventory.\n"
                return
            for consumable in all_consumables:
                if consumable.auto_E_condition(character, player):
                    event_str = consumable.E(character, player)
                    global_vars.turn_info_string += event_str + "\n"
                    player.remove_from_inventory(type(consumable), 1, True)
                    return
        global_vars.turn_info_string += f"Random use failed: No consumable suitable for any character.\n"


    def item_sell_selected():
        text_box.set_text("==============================\n")
        selected_items = []
        if not player.selected_item:
            text_box.append_html_text("No item is selected.\n")
            return
        for a, b, c in player.selected_item.values():
            if b:
                selected_items.append(c)
        if not selected_items:
            text_box.append_html_text("No item is selected.\n")
            return

        for item_to_sell in selected_items:
            eq_market_value = int(item_to_sell.market_value)
            player.add_cash(eq_market_value, False)
            text_box.append_html_text(f"Sold {item_to_sell.name} in inventory and gained {eq_market_value} cash.\n")
            if hasattr(item_to_sell, 'brand'):
                player.remove_from_inventory(type(item_to_sell), 1, False, item_to_sell.brand)
            else:
                player.remove_from_inventory(type(item_to_sell), 1, False)
        player.build_inventory_slots()


    def item_sell_half(all=False):
        """
        Sell half stack of selected items in inventory
        [all] if True, sell all selected items in inventory
        """
        text_box.set_text("==============================\n")
        selected_items = []
        if not player.selected_item:
            text_box.append_html_text("No item is selected.\n")
            return
        for a, b, c in player.selected_item.values():
            if b:
                selected_items.append(c)
        if not selected_items:
            text_box.append_html_text("No item is selected.\n")
            return

        total_income = 0
        for item_to_sell in selected_items:
            if all:
                amount_to_sell = item_to_sell.current_stack
            else:
                amount_to_sell = item_to_sell.current_stack // 2
            if amount_to_sell == 0:
                text_box.append_html_text(f"Cannot sell {item_to_sell.name} in inventory, stack is too small.\n")
                continue
            item_market_value = int(item_to_sell.market_value)
            this_item_income = item_market_value * amount_to_sell
            total_income += this_item_income
            text_box.append_html_text(f"Sold {amount_to_sell} {item_to_sell.name} in inventory and gained {this_item_income} cash.\n")
            if hasattr(item_to_sell, 'brand'):
                player.remove_from_inventory(type(item_to_sell), amount_to_sell, False, item_to_sell.brand)
            else:
                player.remove_from_inventory(type(item_to_sell), amount_to_sell, False)
        
        text_box.append_html_text(f"Total income: {total_income} cash.\n")
        player.add_cash(total_income, True)


    def buy_one_item(player: Nine, item: Block, item_price: int, currency: str) -> None:
        if currency == "Cash":
            if player.cash < item_price:
                text_box.set_text(f"Not enough cash to buy {item.name}.")
                return
            player.add_to_inventory(item, False)
            player.lose_cash(item_price, True)
            text_box.set_text(f"Bought {item.name} for {item_price} cash.\n")
        else:
            if player.get_currency(currency) < item_price:
                text_box.set_text(f"Not enough {currency} to buy {item.name}.")
                return
            player.add_to_inventory(item, False)
            player.remove_from_inventory(item_type=type(eval(f"{currency}(1)")), amount_to_remove=item_price, rebuild_inventory_slots=True)
            text_box.set_text(f"Bought {item.name} for {item_price} {currency}.\n")
        save_player(player)
        return


    # =====================================
    # End of Character Section
    # =====================================
    # =====================================
    # Equip Section
    # =====================================

    def unequip_item():
        text_box.set_text("==============================\n")
        if not is_in_manipulatable_game_states():
            text_box.append_html_text("Cannot unequip items when not in first turn or after the battle is concluded.\n")
            return
        for character in all_characters:
            if character.name == character_selection_menu.selected_option[0].split()[-1] and character.is_alive():
                item_type = eq_selection_menu.selected_option[0]
                unequipped_item = character.unequip_item(item_type, False)
                if unequipped_item:
                    text_box.append_html_text(f"Unequipped {item_type} from {character.name}.\n")
                    player.add_to_inventory(unequipped_item)
                else:
                    text_box.append_html_text(f"{character.name} does not have {item_type} equipped.\n")
                redraw_ui(party1, party2)
                return
            elif character.name == character_selection_menu.selected_option[0].split()[-1] and not character.is_alive():
                text_box.append_html_text(f"Can only unequip items from alive characters.\n")
                return


    def unequip_all_items():
        text_box.set_text("==============================\n")
        if not is_in_manipulatable_game_states():
            text_box.append_html_text("Cannot unequip items when not in first turn or after the battle is concluded.\n")
            return
        for character in all_characters:
            if character.name == character_selection_menu.selected_option[0].split()[-1] and character.is_alive():
                unequipped_items = character.unequip_all(False)
                if unequipped_items:
                    text_box.append_html_text(f"Unequipped all equipment from {character.name}.\n")
                    player.add_package_of_items_to_inventory(unequipped_items)
                else:
                    text_box.append_html_text(f"{character.name} does not have any equipment equipped.\n")
                redraw_ui(party1, party2)
                return
            elif character.name == character_selection_menu.selected_option[0].split()[-1] and not character.is_alive():
                text_box.append_html_text(f"Can only unequip items from alive characters.\n")
                return


    def eq_stars_upgrade(is_upgrade: bool):
        text_box.set_text("==============================\n")
        text_box_text_to_append = ""
        selected_items = []
        # print(player.selected_item)
        if not player.selected_item:
            text_box_text_to_append += "No item is selected.\n"
            text_box.append_html_text(text_box_text_to_append)
            return
        for a, b, c in player.selected_item.values():
            if b:
                selected_items.append(c) 
        if not selected_items:
            text_box_text_to_append += "No item is selected.\n"
            text_box.append_html_text(text_box_text_to_append)
            return
        
        cost_total = int(sum([item_to_upgrade.star_enhence_cost for item_to_upgrade in selected_items]))
        if player.cash < cost_total:
            text_box_text_to_append += f"Not enough cash for star enhancement.\n"
            text_box.append_html_text(text_box_text_to_append)
            return
        
        for item_to_upgrade in selected_items:
            if item_to_upgrade.stars_rating == item_to_upgrade.stars_rating_max and is_upgrade:
                text_box_text_to_append += f"Max stars reached: {str(item_to_upgrade)}\n"
                continue
            if item_to_upgrade.stars_rating == 0 and not is_upgrade:
                text_box_text_to_append += f"Min stars reached: {str(item_to_upgrade)}\n"
                continue
            a, b = item_to_upgrade.upgrade_stars_func(is_upgrade) 
            text_box_text_to_append += f"Upgrading {item_to_upgrade} in inventory.\n"
            text_box_text_to_append += f"Stars: {int(a)} -> {int(b)}\n"
            for k, (a, b, c) in player.selected_item.items():
                if c == item_to_upgrade:
                    if global_vars.language == "English":
                        k.set_tooltip(item_to_upgrade.print_stats_html(), delay=0.1, wrap_width=300)
                    elif global_vars.language == "日本語":
                        k.set_tooltip(item_to_upgrade.print_stats_html_jp(), delay=0.1, wrap_width=300)
        if cost_total > 0:
            player.lose_cash(cost_total, False)
            text_box_text_to_append += f"Upgraded {len(selected_items)} items for {cost_total} cash.\n"
        text_box.append_html_text(text_box_text_to_append)


    def eq_level_up(is_level_up: bool = True, amount_to_level: int = 1):
        """
        [action_loop]: int, number of times to level up the selected items
        """
        text_box.set_text("==============================\n")
        text_box_text_to_append = ""
        selected_items: list[Equip] = []
        if not player.selected_item:
            text_box_text_to_append += "No item is selected.\n"
            text_box.append_html_text(text_box_text_to_append)
            return
        for a, b, c in player.selected_item.values():
            if b:
                selected_items.append(c)
        if not selected_items:
            text_box_text_to_append += "No item is selected.\n"
            text_box.append_html_text(text_box_text_to_append)
            return

        cost_total = int(sum([item_to_upgrade.level_up_cost_multilevel(amount_to_level) for item_to_upgrade in selected_items]))
        if player.cash < cost_total:
            text_box_text_to_append += "Not enough cash for leveling up equipment.\n"
            text_box.append_html_text(text_box_text_to_append)
            return

        for item_to_level_up in selected_items:
            if item_to_level_up.level >= item_to_level_up.level_max and is_level_up:
                text_box_text_to_append += f"Max level reached: {str(item_to_level_up)}\n"
                continue
            if item_to_level_up.level <= 0 and not is_level_up:
                text_box_text_to_append += f"Min level reached: {str(item_to_level_up)}\n"
                continue
            text_box_text_to_append += f"Leveling {'up' if is_level_up else 'down'} {item_to_level_up} in inventory.\n"
            a, b = item_to_level_up.level_change(amount_to_level if is_level_up else amount_to_level * -1)
            text_box_text_to_append += f"Level: {int(a)} -> {int(b)}\n"
            for k, (a, b, c) in player.selected_item.items():
                if c == item_to_level_up:
                    if global_vars.language == "English":
                        k.set_tooltip(item_to_level_up.print_stats_html(), delay=0.1, wrap_width=300)
                    elif global_vars.language == "日本語":
                        k.set_tooltip(item_to_level_up.print_stats_html_jp(), delay=0.1, wrap_width=300)
        if cost_total > 0:
            player.lose_cash(cost_total, False)
            text_box_text_to_append += f"Leveled {len(selected_items)} items for {cost_total} cash.\n"
        text_box.append_html_text(text_box_text_to_append)


    eq_sell_window = None
    eq_sell_window_command_line = None
    eq_sell_window_command_result_box = None
    eq_sell_window_submit_button = None

    def build_eq_sell_window():
        global eq_sell_window, eq_sell_window_command_line, eq_sell_window_command_result_box, eq_sell_window_submit_button
        try:
            eq_sell_window.kill()
        except Exception as e:
            pass

        def local_translate(s: str) -> str:
            if global_vars.language == "English":
                return s
            elif global_vars.language == "日本語":
                match s:
                    case "Sell Equipment":
                        return "装備品販売"
                    case "Carefully enter the command to filter equipment.":
                        return "フィルターコマンドを慎重に入力してください。"
                    case "Submit":
                        return "確定"
                    case "Guide":
                        return "指南"
                    case _:
                        return s
            else:
                raise ValueError(f"Unknown language: {global_vars.language}")


        eq_sell_window = pygame_gui.elements.UIWindow(pygame.Rect((300, 200), (500, 510)),
                                            ui_manager,
                                            window_display_title=local_translate("Sell Equipment"),
                                            object_id="#eq_sell_window",
                                            resizable=False)

        eq_sell_window_command_line = pygame_gui.elements.UITextEntryLine(pygame.Rect((10, 10), (480, 35)),
                                            ui_manager,
                                            container=eq_sell_window,
                                            placeholder_text=local_translate("Carefully enter the command to filter equipment."))
        
        eq_sell_window_submit_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((10, 50), (240, 50)),
                                        text=local_translate("Submit"),
                                        manager=ui_manager,
                                        container=eq_sell_window,)

        def result_box_add_guide():
            global eq_sell_window_command_result_box
            if global_vars.language == "English":
                result_box_guide = "The following python code will be excuted:\n" \
                "[x for x in player.inventory_equip if isinstance(x, Equip) and <font color=#FF69B4>command</font>]\n" \
                "Example input:\n" \
                "<font color=#FF69B4>123</font>\n" \
                "This will sell all equipment, because any non zero number is evaluated as True.\n" \
                "<font color=#FF69B4>'roka is fox'</font>\n" \
                "This will sell all equipment, because any non empty string is evaluated as True.\n" \
                "<font color=#FF69B4>x.market_value <= 200</font>\n" \
                "This will sell all equipment with market value less than or equal to 200.\n" \
                "<font color=#FF69B4>x.rarity == 'Common'</font>\n" \
                "This will sell all equipment with rarity Common.\n" \
                "<font color=#FF69B4>(x.for_attacker_value < 18 and x.for_support_value < 18)</font>\n" \
                "This will sell all equipment with Attacker value and Support value less than 18.\n" \
                "<font color=#FF69B4>x.eq_set == 'Flute'</font>\n" \
                "This will sell all equipment with set Flute.\n" \
                "<font color=#FF69B4>x.type == 'Weapon'</font>\n" \
                "This will sell all equipment with type Weapon.\n"
                eq_sell_window_command_result_box.set_text(html_text=result_box_guide)
            elif global_vars.language == "日本語":
                result_box_guide = "以下のPythonコードが実行される:\n" \
                "[x for x in player.inventory_equip if isinstance(x, Equip) and <font color=#FF69B4>command</font>]\n" \
                "入力例:\n" \
                "<font color=#FF69B4>123</font>\n" \
                "すべての装備品を売却する。これはすべてのゼロ以外の数値は真と評価される。\n" \
                "<font color=#FF69B4>'roka is fox'</font>\n" \
                "すべての装備品を売却する。これはすべての空でない文字列は真と評価される。\n" \
                "<font color=#FF69B4>x.market_value <= 200</font>\n" \
                "市場価値が200以下のすべての装備品を売却する。\n" \
                "<font color=#FF69B4>x.rarity == 'Common'</font>\n" \
                "レアリティが'Common'のすべての装備品を売却する。\n" \
                "<font color=#FF69B4>(x.for_attacker_value < 18 and x.for_support_value < 18)</font>\n" \
                "攻撃相性かつ防御相性が18未満のすべての装備品を売却する。\n" \
                "<font color=#FF69B4>x.eq_set == 'Flute'</font>\n" \
                "セットが'Flute'のすべての装備品を売却する。\n" \
                "<font color=#FF69B4>x.type == 'Weapon'</font>\n" \
                "タイプが'Weapon'のすべての装備品を売却する。\n"
                eq_sell_window_command_result_box.set_text(html_text=result_box_guide)


        eq_sell_window_show_guide_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((260, 50), (230, 50)),
                                        text=local_translate("Guide"),
                                        manager=ui_manager,
                                        container=eq_sell_window,
                                        command=result_box_add_guide)

        eq_sell_window_command_result_box = pygame_gui.elements.UITextBox(html_text="",
                                        relative_rect=pygame.Rect((10, 110), (480, 350)),
                                        manager=ui_manager,
                                        container=eq_sell_window,)

        result_box_add_guide()


    def eq_sell_selected():
        text_box.set_text("==============================\n")
        selected_items = []
        if not player.selected_item:
            text_box.append_html_text("No item is selected.\n")
            return
        for a, b, c in player.selected_item.values():
            if b:
                selected_items.append(c)
        if not selected_items:
            text_box.append_html_text("No item is selected.\n")
            return

        for item_to_sell in selected_items:
            eq_market_value = int(item_to_sell.market_value)
            player.add_cash(eq_market_value, False)
            text_box.append_html_text(f"Sold {item_to_sell} in inventory and gained {eq_market_value} cash.\n")
        player.remove_selected_item_from_inventory(True)


    def eq_sell_advanced(command: str):
        # sell equipment according to the given command
        try:
            eq_to_sell = eval(f"[x for x in player.inventory_equip if isinstance(x, Equip) and {command}]")
        except Exception as e:
            eq_sell_window_command_result_box.set_text(f"{e}\n")
            return
        total_income = 0
        if not eq_to_sell:
            eq_sell_window_command_result_box.set_text(f"No equipment with condition {command} to sell.\n")
            return
        for eq in eq_to_sell.copy():
            total_income += int(eq.market_value)
            player.inventory_equip.remove(eq)
        player.add_cash(total_income, False)
        eq_sell_window_command_result_box.set_text(f"Sold {len(eq_to_sell)} equipment for {total_income} cash.\n")
        player.build_inventory_slots()


    def eq_level_up_to_max():
        text_box.set_text("==============================\n")
        selected_items = []
        if not player.selected_item:
            text_box.append_html_text("No item is selected.\n")
            return
        for a, b, c in player.selected_item.values():
            if b:
                selected_items.append(c)
        if not selected_items:
            text_box.append_html_text("No item is selected.\n")
            return

        for item_to_level_up in selected_items:
            available_cash = player.cash
            remaining_funds, cost = item_to_level_up.level_up_as_possible(available_cash)
            if cost:
                player.lose_cash(cost, False)
                text_box.append_html_text(f"Leveled up {item_to_level_up} in inventory for {cost} cash.\n")
            else:
                text_box.append_html_text(f"Cannot level up {item_to_level_up} in inventory.\n")
            for k, (a, b, c) in player.selected_item.items():
                if c == item_to_level_up:
                    if global_vars.language == "English":
                        k.set_tooltip(item_to_level_up.print_stats_html(), delay=0.1, wrap_width=300)
                    elif global_vars.language == "日本語":
                        k.set_tooltip(item_to_level_up.print_stats_html_jp(), delay=0.1, wrap_width=300)




    # =====================================
    # End of Equip Section
    # =====================================
    # Settings Section
    # =====================================

    def build_settings_window():
        global theme_selection_menu, settings_window, language_selection_menu, auto_battle_speed_selection_menu, after_auto_battle_selection_menu
        global settings_show_battle_chart_selection_menu
        try:
            settings_window.kill()
        except Exception as e:
            pass

        def local_translate(s: str) -> str:
            if global_vars.language == "English":
                return s
            elif global_vars.language == "日本語":
                match s:
                    case "Settings":
                        return "設定"
                    case "Theme:":
                        return "主題色:"
                    case "Language:":
                        return "言語:"
                    case "Autobattle Speed:":
                        return "自動戦闘速度:"
                    case "After Autobattle:":
                        return "自動戦闘後の処理:"
                    case "Draw Chart:":
                        return "戦闘チャートの描画:"
                    case _:
                        return s
            else:
                raise ValueError(f"Unknown language: {global_vars.language}")

        settings_window = pygame_gui.elements.UIWindow(pygame.Rect((500, 300), (400, 300)),
                                            ui_manager,
                                            window_display_title=local_translate("Settings"),
                                            object_id="#settings_window",
                                            resizable=False)

        theme_selection_label = pygame_gui.elements.UILabel(pygame.Rect((10, 10), (140, 35)),
                                            local_translate("Theme:"),
                                            ui_manager,
                                            container=settings_window)

        theme_selection_menu = pygame_gui.elements.UIDropDownMenu(["Yellow Theme", "Purple Theme", "Red Theme", "Blue Theme", "Green Theme", "Pink Theme"],
                                                                global_vars.theme,
                                                                pygame.Rect((180, 10), (156, 35)),
                                                                ui_manager,
                                                                container=settings_window,)

        language_selection_label = pygame_gui.elements.UILabel(pygame.Rect((10, 50), (140, 35)),
                                                               local_translate("Language:"),
                                                               ui_manager,
                                                                container=settings_window)

        language_selection_menu = pygame_gui.elements.UIDropDownMenu(["English", "日本語"],
                                                                global_vars.language,
                                                                pygame.Rect((180, 50), (156, 35)),
                                                                ui_manager,
                                                                container=settings_window,)


        auto_battle_speed_label = pygame_gui.elements.UILabel(pygame.Rect((10, 90), (140, 35)),
                                            local_translate("Autobattle Speed:"),
                                            ui_manager,
                                            container=settings_window)
        
        auto_battle_speed_selection_menu = pygame_gui.elements.UIDropDownMenu(["Veryslow", "Slow", "Normal", "Fast", "Veryfast"],
                                                                global_vars.autobattle_speed,
                                                                pygame.Rect((180, 90), (156, 35)),
                                                                ui_manager,
                                                                container=settings_window)


        after_auto_battle_label = pygame_gui.elements.UILabel(pygame.Rect((10, 130), (140, 35)),
                                            local_translate("After Autobattle:"),
                                            ui_manager,
                                            container=settings_window)

        after_auto_battle_selection_menu = pygame_gui.elements.UIDropDownMenu(["Do Nothing", "Restart", "Shuffle Party", "Next Stage"],
                                                                global_vars.after_autobattle,
                                                                pygame.Rect((180, 130), (156, 35)),
                                                                ui_manager,
                                                                container=settings_window)

        settings_show_battle_graph_label = pygame_gui.elements.UILabel(pygame.Rect((10, 170), (140, 35)),
                                            local_translate("Draw Chart:"),
                                            ui_manager,
                                            container=settings_window)
        
        settings_show_battle_chart_selection_menu = pygame_gui.elements.UIDropDownMenu(["True", "False"],
                                                                global_vars.draw_battle_chart,
                                                                pygame.Rect((180, 170), (156, 35)),
                                                                ui_manager,
                                                                container=settings_window)



    settings_window = None
    theme_selection_menu = None
    language_selection_menu = None
    auto_battle_speed_selection_menu = None
    after_auto_battle_selection_menu = None
    settings_show_battle_chart_selection_menu = None



    def change_theme(theme=None, reload_language=True):
        if theme:
            global_vars.theme = theme
        else:
            global_vars.theme = theme_selection_menu.selected_option[0]
            player.settings_theme = global_vars.theme
        if global_vars.theme == "Yellow Theme":
            ui_manager_lower.get_theme().load_theme("theme_light_yellow.json")
            ui_manager.get_theme().load_theme("theme_light_yellow.json")
            ui_manager_overlay.get_theme().load_theme("theme_light_yellow.json")
        elif global_vars.theme == "Purple Theme":
            ui_manager_lower.get_theme().load_theme("theme_light_purple.json")
            ui_manager.get_theme().load_theme("theme_light_purple.json")
            ui_manager_overlay.get_theme().load_theme("theme_light_purple.json")
        elif global_vars.theme == "Red Theme":
            ui_manager_lower.get_theme().load_theme("theme_light_red.json")
            ui_manager.get_theme().load_theme("theme_light_red.json")
            ui_manager_overlay.get_theme().load_theme("theme_light_red.json")
        elif global_vars.theme == "Blue Theme":
            ui_manager_lower.get_theme().load_theme("theme_light_blue.json")
            ui_manager.get_theme().load_theme("theme_light_blue.json")
            ui_manager_overlay.get_theme().load_theme("theme_light_blue.json")
        elif global_vars.theme == "Green Theme":
            ui_manager_lower.get_theme().load_theme("theme_light_green.json")
            ui_manager.get_theme().load_theme("theme_light_green.json")
            ui_manager_overlay.get_theme().load_theme("theme_light_green.json")
        elif global_vars.theme == "Pink Theme":
            ui_manager_lower.get_theme().load_theme("theme_light_pink.json")
            ui_manager.get_theme().load_theme("theme_light_pink.json")
            ui_manager_overlay.get_theme().load_theme("theme_light_pink.json")
        else:
            raise ValueError(f"Unknown theme: {global_vars.theme}")
        
        ui_manager_lower.rebuild_all_from_changed_theme_data()
        ui_manager.rebuild_all_from_changed_theme_data()
        ui_manager_overlay.rebuild_all_from_changed_theme_data()
        if reload_language:
            swap_language()


    def swap_language(language=None):
        if language:
            global_vars.language = language
        else:
            global_vars.language = language_selection_menu.selected_option[0]
            player.settings_language = global_vars.language
        redraw_ui(party1, party2)
        player.build_inventory_slots()
        if global_vars.player_is_in_shop:
            redraw_ui_shop_edition(reload_shop=False) 
        # print(f"Language changed to {global_vars.language}.")
        box_submenu_stage_info_label.set_tooltip(adventure_mode_info_tooltip(), delay=0.1, wrap_width=300)
        match global_vars.language:
            case "English":
                settings_button.set_text("Settings")
                settings_button.set_tooltip("Open settings window.", delay=0.1, wrap_width=300)
                button_quit_game.set_text("Quit")
                button_quit_game.set_tooltip("Save player data as player_data.json and exit.", delay=0.1, wrap_width=300)
                button_left_simulate_current_battle.set_text("Simulate")
                button_left_simulate_current_battle.set_tooltip("Simulate current battle n times and print the result.", delay=0.1, wrap_width=300)
                button3.set_text("All Turns")
                button3.set_tooltip("Skip to the end of the battle.", delay=0.1, wrap_width=300)
                button4.set_text("Restart Battle")
                button4.set_tooltip("Restart battle.", delay=0.1)
                button1.set_text('Shuffle Party')
                button1.set_tooltip("Shuffle the party members and restart battle. On adventure mode, only party 1 is shuffled.", delay=0.1, wrap_width=300)
                next_turn_button.set_text("Next Turn")
                next_turn_button_tooltip_str = "Next turn. Rewards are earned if the battle is won in adventure mode." \
                " The details of rewards are shown when hovering over the stage number label."
                next_turn_button.set_tooltip(next_turn_button_tooltip_str, delay=0.1, wrap_width=300)
                button_auto_battle.set_text("Auto Battle")
                button_auto_battle.set_tooltip("Automatically proceed to the next turn when the progress bar is full. Rewards are earned when the battle is over.", delay=0.1, wrap_width=300)
                cheap_inventory_sort_filter_button.set_text("Sort & Filter")
                cheap_inventory_sort_filter_button.set_tooltip("Open sort and filter window for inventory.", delay=0.1, wrap_width=300)
                chart_selection_label.set_text("Show Chart:")
                chart_selection_label.set_tooltip("Select the chart to display: Damage dealt, Damage received, Healing.", delay=0.1, wrap_width=300)
                game_mode_selection_label.set_text("Game Mode:")
                game_mode_selection_label.set_tooltip("Select the game mode: Training Mode, Adventure Mode.", delay=0.1, wrap_width=300)
                label_character_selection_menu.set_text("Selected Character:")
                label_character_selection_menu.set_tooltip("Selected character. Use items, equip, unequip and others use this character as target." \
                " S + left click on character image can also be used to select a character."
                , delay=0.1, wrap_width=300)
                use_item_button.set_text("Equip Item")
                use_item_button.set_tooltip("The selected item is used on the selected character. If the selected item is an equipment item, equip it to the selected character." \
                                            " Multiple items may be equipped or used at one time." \
                                            " Selection: left click to select an item, right click to deselect an item." \
                                            " Shift + left click to select multiple items."
                                            ,
                                            delay=0.1, wrap_width=300)
                use_itemx10_button.set_tooltip("Use selected item 10 times, only effective on comsumables.", delay=0.1, wrap_width=300)
                button_cheems.set_text("Cheems")
                button_cheems.set_tooltip("Open team selection window. Note: Shortcut key W + left click" \
                " on 2 characters images allow quick swapping without opening the menu and editing the team."
                , delay=0.1, wrap_width=300)
                button_characters.set_text("Characters")
                button_characters.set_tooltip("Open character window.", delay=0.1, wrap_width=300)
                button_about.set_text("About")
                button_about.set_tooltip("Open about window.", delay=0.1, wrap_width=300)
                character_eq_unequip_button.set_tooltip("Remove equipment from the selected character.", delay=0.1, wrap_width=300)
                character_eq_unequip_all_button.set_tooltip("Remove all equipment from the selected character.", delay=0.1, wrap_width=300)
                eq_levelup_button.set_text("Level Up")
                eq_levelup_button.set_tooltip("Level up selected equipment in the inventory.", delay=0.1, wrap_width=300)
                eq_levelup_buttonx10.set_tooltip("Level up for 10 levels for selected equipment in the inventory.", delay=0.1, wrap_width=300)
                eq_level_up_to_max_button.set_text("Level Up To Max")
                eq_level_up_to_max_button.set_tooltip("Level up selected equipment in the inventory to the maximum level.", delay=0.1, wrap_width=300)
                eq_stars_upgrade_button.set_text("Star Enhancement")
                eq_stars_upgrade_button.set_tooltip("Increase the star rank of selected equipment in inventory.", delay=0.1, wrap_width=300)
                eq_sell_selected_button.set_text("Sell Selected")
                eq_sell_selected_button.set_tooltip("Sell selected equipment in the inventory.", delay=0.1, wrap_width=300)
                eq_mass_sell_button.set_text("Mass Sell")
                eq_mass_sell_button.set_tooltip("Sell equipment in the inventory with a custom condition.", delay=0.1, wrap_width=300)
                item_sell_button.set_text("Sell Item")
                item_sell_button.set_tooltip("Sell one selected item from your inventory.", delay=0.1, wrap_width=300)
                item_sell_half_button.set_text("Sell Half")
                item_sell_half_button.set_tooltip("Sell half a stack of selected items.", delay=0.1, wrap_width=300)
                item_sell_all_button.set_text("All")
                item_sell_all_button.set_tooltip("Sell full stack of selected items.", delay=0.1, wrap_width=300)
                use_random_consumable_label.set_text("Random Use:")
                use_random_consumable_label.set_tooltip("Use one appropriate consumable each turn during auto battles.", delay=0.1, wrap_width=300)
                cheap_inventory_page_label.set_tooltip("page/max page", delay=0.1)
                cheap_inventory_skip_to_first_page_button.set_tooltip("Jump to first page of inventory.", delay=0.1, wrap_width=300)
                cheap_inventory_previous_page_button.set_tooltip("Previous page of inventory.", delay=0.1, wrap_width=300)
                cheap_inventory_previous_n_button.set_tooltip("Previous 5th page of inventory.", delay=0.1, wrap_width=300)
                cheap_inventory_skip_to_last_page_button.set_tooltip("Jump to last page of inventory.", delay=0.1, wrap_width=300)
                cheap_inventory_next_n_button.set_tooltip("Next 5th page of inventory.", delay=0.1, wrap_width=300)
                cheap_inventory_next_page_button.set_tooltip("Next page of inventory.", delay=0.1, wrap_width=300)
                box_submenu_enter_shop_button.set_text("Enter Shop")
                box_submenu_enter_shop_button.set_tooltip("Enter the shop to buy items.", delay=0.1)
                box_submenu_exit_shop_button.set_text("Exit Shop")
                box_submenu_exit_shop_button.set_tooltip("Exit the shop.", delay=0.1)
                box_submenu_previous_stage_button.set_text("Prev")
                box_submenu_previous_stage_button.set_tooltip("Go to previous stage.", delay=0.1)
                box_submenu_next_stage_button.set_text("Next")
                box_submenu_next_stage_button.set_tooltip("Advance to the next stage. You can proceed only if the current stage has been cleared.", delay=0.1)
                box_submenu_refresh_stage_button.set_text("Refresh")
                box_submenu_refresh_stage_button.set_tooltip("Refresh the current stage, get a new set of monsters.", delay=0.1)
            case "日本語":
                settings_button.set_text("心機一転")
                settings_button.set_tooltip("設定画面を開く。", delay=0.1, wrap_width=300)
                button_quit_game.set_text("曲終人散")
                button_quit_game.set_tooltip("プレイヤーデータをplayer_data.jsonとして保存し、アプリを終了する。", delay=0.1, wrap_width=300)
                button_left_simulate_current_battle.set_text("柳暗花明")
                button_left_simulate_current_battle.set_tooltip("現在の戦闘をn回シミュレートし、結果を表示する。", delay=0.1, wrap_width=300)
                button3.set_text("夢幻泡影")
                button3.set_tooltip("戦闘終了まで飛ばす。", delay=0.1, wrap_width=300)
                button4.set_text("東山再起")
                button4.set_tooltip("戦闘再開。", delay=0.1, wrap_width=300)
                button1.set_text('一期一会')
                button1.set_tooltip("パーティメンバーをランダムに編成してバトルを再開する。冒険モードではパーティ1のみ入れ替わる。", delay=0.1, wrap_width=300)
                next_turn_button.set_text("花鳥風月")
                next_turn_button_tooltip_str = "次のターン。冒険モードで勝利すると報酬を獲得できる。報酬の詳細は、ステージ番号のラベルにカーソルを合わせると表示される。"
                next_turn_button.set_tooltip(next_turn_button_tooltip_str, delay=0.1, wrap_width=300)
                button_auto_battle.set_text("一刻千金")
                button_auto_battle.set_tooltip("進行状況バーが埋まると自動的に次のターンに進む。戦闘終了時に報酬を獲得できる。", delay=0.1, wrap_width=300)
                cheap_inventory_sort_filter_button.set_text("ソートとフィルタ")
                cheap_inventory_sort_filter_button.set_tooltip("インベントリの並び替えと絞り込みウィンドウを開く。", delay=0.1, wrap_width=300)
                chart_selection_label.set_text("栄枯盛衰：")
                chart_selection_label.set_tooltip("表示するチャートを選択する：与えるダメージ、受けるダメージ、回復量。", delay=0.1, wrap_width=300)
                game_mode_selection_label.set_text("海闊天空：")
                game_mode_selection_label.set_tooltip("ゲームモードを選択する：訓練モード、冒険モード。", delay=0.1, wrap_width=300)
                label_character_selection_menu.set_text("天下無双：")
                label_character_selection_menu.set_tooltip("キャラクターを選択する。アイテムの使用、装備の使用、装備の解除、その他がこのキャラクターを対象として行われる。" \
                "キャラクター画像にS+左クリックでもキャラクターを選択できる。"
                , delay=0.1, wrap_width=300)
                use_item_button.set_text("鳳冠霞帔")
                use_item_button.set_tooltip("選択したアイテムを選択したキャラクターに使用する。選択したアイテムが装備アイテムの場合、選択したキャラクターに装備する。一度に複数のアイテムを装備・使用することができる。" \
                                            "選択方法：左クリックでアイテムを選択、右クリックでアイテムを選択解除。" \
                                            "Shift+左クリックで複数のアイテムを選択する。"
                                            ,
                                            delay=0.1, wrap_width=300)
                use_itemx10_button.set_tooltip("選択したアイテムを10回使用し、消耗品にのみ有効である。", delay=0.1, wrap_width=300)
                button_cheems.set_text("チームズ")
                button_cheems.set_tooltip("チーム選択画面を開く。注意事項：2匹キャラクター画像にW+左クリックで素早くこの2匹を入れ替える。チーム編成メニューを開かなくても。"
                , delay=0.1, wrap_width=300)
                button_characters.set_text("百花繚乱")
                button_characters.set_tooltip("キャラクター画面を開く。", delay=0.1, wrap_width=300)
                button_about.set_text("洞若觀火")
                button_about.set_tooltip("アプリ概要画面を開く。", delay=0.1, wrap_width=300)
                character_eq_unequip_button.set_text("衣衫襤褸")
                character_eq_unequip_button.set_tooltip("選択したキャラクターから装備を外す。", delay=0.1, wrap_width=300)
                character_eq_unequip_all_button.set_text("全")
                character_eq_unequip_all_button.set_tooltip("選択したキャラクターからすべての装備を外す。", delay=0.1, wrap_width=300)
                eq_levelup_button.set_text("日進月歩")
                eq_levelup_button.set_tooltip("インベントリで選択した装備をレベルアップさせる。", delay=0.1, wrap_width=300)
                eq_levelup_buttonx10.set_tooltip("インベントリで選択した装備品を10レベル分レベルアップさせる。", delay=0.1, wrap_width=300)
                eq_level_up_to_max_button.set_text("登峰造極")
                eq_level_up_to_max_button.set_tooltip("インベントリ内の選択した装備を最大レベルまでレベルアップさせる。", delay=0.1, wrap_width=300)
                eq_stars_upgrade_button.set_text("明星天外")
                eq_stars_upgrade_button.set_tooltip("インベントリ内の選択した装備品のスターランクを上げる。", delay=0.1, wrap_width=300)
                eq_sell_selected_button.set_text("指定販売")
                eq_sell_selected_button.set_tooltip("インベントリーの中から選択した装備品を販売する。", delay=0.1, wrap_width=300)
                eq_mass_sell_button.set_text("一括処分")
                eq_mass_sell_button.set_tooltip("特別な条件で装備品を大量販売する。", delay=0.1, wrap_width=300)
                item_sell_button.set_text("アイテム売却")
                item_sell_button.set_tooltip("在庫の中から選んだアイテムを1つ売る。", delay=0.1, wrap_width=300)
                item_sell_half_button.set_text("半分売却")
                item_sell_half_button.set_tooltip("選択したアイテムを半分ずつ売る。", delay=0.1, wrap_width=300)
                item_sell_all_button.set_text("全")
                item_sell_all_button.set_tooltip("選択したアイテムをすべて売る。", delay=0.1, wrap_width=300)
                use_random_consumable_label.set_text("ランダム使用：")
                use_random_consumable_label.set_tooltip("オートバトル中、毎ターン適切な消耗品を1つ使用する。", delay=0.1, wrap_width=300)
                cheap_inventory_page_label.set_tooltip("ページ/最大ページ", delay=0.1)
                cheap_inventory_skip_to_first_page_button.set_tooltip("インベントリーの最初のページに飛ぶ。", delay=0.1, wrap_width=300)
                cheap_inventory_previous_page_button.set_tooltip("インベントリーの前のページ。", delay=0.1, wrap_width=300)
                cheap_inventory_previous_n_button.set_tooltip("前の5ページ目のインベントリー。", delay=0.1, wrap_width=300)
                cheap_inventory_skip_to_last_page_button.set_tooltip("インベントリーの最後のページに飛ぶ。", delay=0.1, wrap_width=300)
                cheap_inventory_next_n_button.set_tooltip("次のインベントリの5ページ目。", delay=0.1, wrap_width=300)
                cheap_inventory_next_page_button.set_tooltip("インベントリーの次のページ。", delay=0.1, wrap_width=300)
                box_submenu_enter_shop_button.set_text("入店")
                box_submenu_enter_shop_button.set_tooltip("ショップに入って商品を買う。", delay=0.1)
                box_submenu_exit_shop_button.set_text("退店")
                box_submenu_exit_shop_button.set_tooltip("店から出る。", delay=0.1)
                box_submenu_previous_stage_button.set_text("過去")
                box_submenu_previous_stage_button.set_tooltip("前のステージに戻る。", delay=0.1)
                box_submenu_next_stage_button.set_text("未来")
                box_submenu_next_stage_button.set_tooltip("次のステージに進む。現在のステージがクリアされている場合のみ進むことができる。", delay=0.1)
                box_submenu_refresh_stage_button.set_text("捲土重来")
                box_submenu_refresh_stage_button.set_tooltip("現在のステージを一新し、新しいモンスターの一族を調達する。", delay=0.1)


    # =====================================
    # End of Settings Section
    # =====================================
    # Cheap Inventory Section
    # =====================================

    # Cheap inventory system is just a bunch of 32 by 32 image slots pointing to player's inventory
    # 10 rows, 6 columns
    # each row and column have a empty space of 8 pixels

    cheap_inventory_sort_filter_window = None
    cheap_inventory_sort_a_selection_menu = None
    cheap_inventory_sort_b_selection_menu = None
    cheap_inventory_sort_c_selection_menu = None
    cheap_inventory_filter_have_owner_selection_menu = None
    cheap_inventory_filter_owned_by_char_selection_menu = None
    cheap_inventory_filter_eqset_selection_menu = None
    cheap_inventory_filter_type_selection_menu = None
    cheap_inventory_sort_filter_confirm_button = None


    cheap_inventory_what_to_show_selection_menu = pygame_gui.elements.UIDropDownMenu(["Equip", "Consumable", "Item"],
                                                            "Equip",
                                                            pygame.Rect((1300, 20), (230, 35)),
                                                            ui_manager)
                                  
    cheap_inventory_sort_filter_button = pygame_gui.elements.UIButton(pygame.Rect((1300, 60), (230, 35)),
                                        text='Sort & Filter',
                                        manager=ui_manager)
    cheap_inventory_sort_filter_button.set_tooltip("Open sort and filter window for inventory.", delay=0.1, wrap_width=300)


    # 3.3.0: Use window for inventory sort and filter
    def build_cheap_inventory_sort_filter_window():
        global cheap_inventory_sort_filter_window, cheap_inventory_sort_a_selection_menu, cheap_inventory_sort_b_selection_menu, cheap_inventory_sort_c_selection_menu
        global cheap_inventory_filter_have_owner_selection_menu, cheap_inventory_filter_owned_by_char_selection_menu, cheap_inventory_filter_eqset_selection_menu
        global cheap_inventory_filter_type_selection_menu
        global cheap_inventory_sort_filter_confirm_button
        try:
            cheap_inventory_sort_filter_window.kill()
        except Exception as e:
            pass

        def local_translate(s: str) -> str:
            if global_vars.language == "English":
                return s
            elif global_vars.language == "日本語":
                match s:
                    case "Confirm":
                        return "確認"
                    case "Sort A:":
                        return "ソート A:"
                    case "Sort B:":
                        return "ソート B:"
                    case "Sort C:":
                        return "ソート C:"
                    case "Equipment Has Owner:":
                        return "装備所有:"
                    case "Equipment Owned By:":
                        return "装備所有者:"
                    case "Equipment Set:":
                        return "装備セット:"
                    case "Equipment Type:":
                        return "装備種類:"
                    case _:
                        return s
                    
            else:
                raise ValueError(f"Unknown language: {global_vars.language}")

        cheap_inventory_sort_filter_window = pygame_gui.elements.UIWindow(pygame.Rect((400, 200), (450, 500)),
                                                ui_manager,
                                                window_display_title="Sort & Filter",
                                                object_id="#cheap_inventory_sort_filter_window",
                                                resizable=False)

        # sort has 3 selection menus, for sorting further
        cheap_inventory_sort_a_label = pygame_gui.elements.UILabel(pygame.Rect((10, 10), (140, 35)),
                                            local_translate("Sort A:"),
                                            ui_manager,
                                            container=cheap_inventory_sort_filter_window)
        cheap_inventory_sort_a_selection_menu = pygame_gui.elements.UIDropDownMenu(["Rarity", "Type", "Set", "Level", "Market Value", "BOGO"],
                                                                global_vars.cheap_inventory_sort_a,
                                                                pygame.Rect((180, 10), (200, 35)),
                                                                ui_manager,
                                                                container=cheap_inventory_sort_filter_window)

        cheap_inventory_sort_b_label = pygame_gui.elements.UILabel(pygame.Rect((10, 50), (140, 35)),
                                            local_translate("Sort B:"),
                                            ui_manager,
                                            container=cheap_inventory_sort_filter_window)
        cheap_inventory_sort_b_selection_menu = pygame_gui.elements.UIDropDownMenu(["Rarity", "Type", "Set", "Level", "Market Value", "BOGO"],
                                                                global_vars.cheap_inventory_sort_b,
                                                                pygame.Rect((180, 50), (200, 35)),
                                                                ui_manager,
                                                                container=cheap_inventory_sort_filter_window)

        cheap_inventory_sort_c_label = pygame_gui.elements.UILabel(pygame.Rect((10, 90), (140, 35)),
                                            local_translate("Sort C:"),
                                            ui_manager,
                                            container=cheap_inventory_sort_filter_window)
        cheap_inventory_sort_c_selection_menu = pygame_gui.elements.UIDropDownMenu(["Rarity", "Type", "Set", "Level", "Market Value", "BOGO"],
                                                                global_vars.cheap_inventory_sort_c,
                                                                pygame.Rect((180, 90), (200, 35)),
                                                                ui_manager,
                                                                container=cheap_inventory_sort_filter_window)
        
        for selection_menu in [cheap_inventory_sort_a_selection_menu, cheap_inventory_sort_b_selection_menu, cheap_inventory_sort_c_selection_menu]:
            selection_menu.add_options(["Attacker", "Support", "maxhp_percent", "atk_percent", "def_percent", "spd", "eva", "acc", "crit", "critdmg", "critdef", "penetration", "heal_efficiency",
                                        "maxhp_flat", "atk_flat", "def_flat", "spd_flat"])

        cheap_inventory_filter_have_owner_label = pygame_gui.elements.UILabel(pygame.Rect((10, 130), (140, 35)),
                                            local_translate("Equipment Has Owner:"),
                                            ui_manager,
                                            container=cheap_inventory_sort_filter_window)
        cheap_inventory_filter_have_owner_selection_menu = pygame_gui.elements.UIDropDownMenu(["Not Specified", "No Owner", "Has Owner"],
                                                                global_vars.cheap_inventory_filter_have_owner,
                                                                pygame.Rect((180, 130), (200, 35)),
                                                                ui_manager,
                                                                container=cheap_inventory_sort_filter_window)

        cheap_inventory_filter_owned_by_char_label = pygame_gui.elements.UILabel(pygame.Rect((10, 170), (140, 35)),
                                            local_translate("Equipment Owned By:"),
                                            ui_manager,
                                            container=cheap_inventory_sort_filter_window)
        
        cheap_inventory_filter_owned_by_char_selection_menu = pygame_gui.elements.UIDropDownMenu(["Not Specified", "Currently Selected"] + all_characters_names,
                                                                global_vars.cheap_inventory_filter_owned_by_char,
                                                                pygame.Rect((180, 170), (200, 35)),
                                                                ui_manager,
                                                                container=cheap_inventory_sort_filter_window)

        cheap_inventory_filter_eqset_label = pygame_gui.elements.UILabel(pygame.Rect((10, 210), (140, 35)),
                                            local_translate("Equipment Set:"),
                                            ui_manager,
                                            container=cheap_inventory_sort_filter_window)

        cheap_inventory_filter_eqset_selection_menu = pygame_gui.elements.UIDropDownMenu(["Not Specified"] + eq_set_list_without_none_and_void,
                                                                global_vars.cheap_inventory_filter_eqset,
                                                                pygame.Rect((180, 210), (200, 35)),
                                                                ui_manager,
                                                                container=cheap_inventory_sort_filter_window)

        cheap_inventory_filter_type_selection_label = pygame_gui.elements.UILabel(pygame.Rect((10, 250), (140, 35)),
                                            local_translate("Equipment Type:"),
                                            ui_manager,
                                            container=cheap_inventory_sort_filter_window)

        cheap_inventory_filter_type_selection_menu = pygame_gui.elements.UIDropDownMenu(["Not Specified", "Weapon", "Armor", "Accessory", "Boots"],
                                                                global_vars.cheap_inventory_filter_type,
                                                                pygame.Rect((180, 250), (200, 35)),
                                                                ui_manager,
                                                                container=cheap_inventory_sort_filter_window)

        cheap_inventory_sort_filter_confirm_button = pygame_gui.elements.UIButton(pygame.Rect((10, 400), (200, 50)),
                                            local_translate("Confirm"),
                                            ui_manager,
                                            container=cheap_inventory_sort_filter_window)
        return None      

    def cheap_inventory_sort():
        player.sort_inventory_abc(global_vars.cheap_inventory_sort_a,
                                  global_vars.cheap_inventory_sort_b,
                                  global_vars.cheap_inventory_sort_c)


    cheap_inventory_page_label = pygame_gui.elements.UILabel(pygame.Rect((1372, 140), (72, 35)),
                                        "1/1",
                                        ui_manager)
    cheap_inventory_page_label.set_tooltip("page/max page", delay=0.1)

    cheap_inventory_skip_to_first_page_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((1300, 140), (50, 35)),
                                        text='<<<',
                                        manager=ui_manager,)
    cheap_inventory_skip_to_first_page_button.set_tooltip("Jump to first page of inventory.", delay=0.1, wrap_width=300)

    cheap_inventory_previous_page_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((1355, 100), (50, 35)),
                                        text='<',
                                        manager=ui_manager,)
    cheap_inventory_previous_page_button.set_tooltip("Previous page of inventory.", delay=0.1, wrap_width=300)

    cheap_inventory_previous_n_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((1300, 100), (50, 35)),
                                        text='<<',
                                        manager=ui_manager,)
    cheap_inventory_previous_n_button.set_tooltip("Previous 5th page of inventory.", delay=0.1, wrap_width=300)

    cheap_inventory_skip_to_last_page_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((1480, 140), (50, 35)),
                                        text='>>>',
                                        manager=ui_manager,)
    cheap_inventory_skip_to_last_page_button.set_tooltip("Jump to last page of inventory.", delay=0.1, wrap_width=300)

    cheap_inventory_next_n_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((1480, 100), (50, 35)),
                                        text='>>',
                                        manager=ui_manager,)
    cheap_inventory_next_n_button.set_tooltip("Next 5th page of inventory.", delay=0.1, wrap_width=300)

    cheap_inventory_next_page_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((1425, 100), (50, 35)),
                                        text='>',
                                        manager=ui_manager,)
    cheap_inventory_next_page_button.set_tooltip("Next page of inventory.", delay=0.1, wrap_width=300)


    def create_inventory_image_slots(n, start_x, start_y, slot_width, slot_height, spacing, ui_manager, column=6) -> list:
        # -> list of UIImage
        inventory_image_slots = []
        x = start_x
        y = start_y

        for i in range(n):
            slot_rect = pygame.Rect((x, y), (slot_width, slot_height))
            image_slot = pygame_gui.elements.UIImage(slot_rect, pygame.Surface((slot_width, slot_height)), ui_manager)
            inventory_image_slots.append(image_slot)

            x += slot_width + spacing
            if (i + 1) % column == 0:
                x = start_x
                y += slot_height + spacing

        return inventory_image_slots
    
    def show_n_slots_of_inventory_image_slots(n):
        if n > len(inventory_image_slots):
            print(f"Warning: n = {n} is larger than inventory_image_slots length = {len(inventory_image_slots)}")
            return
        for i in range(n, len(inventory_image_slots)):
            inventory_image_slots[i].hide()
        for i in range(n):
            inventory_image_slots[i].show()
        gutted_inventory_image_slots = inventory_image_slots[:n]
        # maps UIImage to Rect, used for collision detection in pygame event
        list_of_rects_for_inventory_image_slots = [x.get_abs_rect() for x in gutted_inventory_image_slots]
        dict_image_slots_rects = {k: v for k, v in mit.zip_equal(gutted_inventory_image_slots, list_of_rects_for_inventory_image_slots)} # UIImage : Rect
        dict_image_slots_rects: dict[pygame_gui.elements.UIImage, pygame.Rect]
        return gutted_inventory_image_slots, dict_image_slots_rects

    inventory_image_slots = create_inventory_image_slots(24, 1278, 196, 64, 64, 8, ui_manager, column=4)
    show_n_slots_of_inventory_image_slots(0)

    def update_inventory_section(player):
        cheap_inventory_page_label.set_text(f"{player.current_page + 1}/{player.max_pages + 1}")

    # =====================================
    # End of Cheap Inventory Section
    # =====================================
    # Cheems Section
    # =====================================


    cheems_window = None
    party1_member_a_selection_menu = None
    party1_member_b_selection_menu = None
    party1_member_c_selection_menu = None
    party1_member_d_selection_menu = None
    party1_member_e_selection_menu = None
    party2_member_a_selection_menu = None
    party2_member_b_selection_menu = None
    party2_member_c_selection_menu = None
    party2_member_d_selection_menu = None
    party2_member_e_selection_menu = None
    cheems_update_party_members_button = None
    cheems_create_new_team_name_entry = None
    cheems_save_party1_button = None
    cheems_save_party2_button = None
    cheems_response_label = None
    cheems_show_player_cheems_selection_menu = None
    cheems_player_cheems_char_img_slot_a = None
    cheems_player_cheems_char_img_slot_b = None
    cheems_player_cheems_char_img_slot_c = None
    cheems_player_cheems_char_img_slot_d = None
    cheems_player_cheems_char_img_slot_e = None
    cheems_apply_to_party1_button = None
    cheems_apply_to_party2_button = None
    cheems_delete_team_button = None
    cheems_rename_teams_entry = None
    cheems_rename_team_button = None
    cheems_update_with_party1_button = None
    cheems_update_with_party2_button = None
    cheems_meme_dog_image_slot = None

    def build_cheems_window():
        global cheems_window, party1, party2
        global party1_member_a_selection_menu, party1_member_b_selection_menu, party1_member_c_selection_menu, party1_member_d_selection_menu, party1_member_e_selection_menu
        global party2_member_a_selection_menu, party2_member_b_selection_menu, party2_member_c_selection_menu, party2_member_d_selection_menu, party2_member_e_selection_menu
        global cheems_update_party_members_button, cheems_create_new_team_name_entry
        global cheems_save_party1_button, cheems_save_party2_button, cheems_response_label
        global cheems_show_player_cheems_selection_menu, cheems_player_cheems_member_label
        global cheems_player_cheems_char_img_slot_a, cheems_player_cheems_char_img_slot_b, cheems_player_cheems_char_img_slot_c, cheems_player_cheems_char_img_slot_d, cheems_player_cheems_char_img_slot_e
        global cheems_apply_to_party1_button, cheems_apply_to_party2_button, cheems_delete_team_button
        global cheems_update_with_party1_button, cheems_update_with_party2_button
        global cheems_rename_teams_entry, cheems_rename_team_button
        global cheems_meme_dog_image_slot

        try:
            cheems_window.kill()
        except Exception as e:
            print(f"Error: {e}")
        cheems_window = pygame_gui.elements.UIWindow(pygame.Rect((200, 200), (810, 500)),
                                            ui_manager,
                                            window_display_title="Cheems",
                                            object_id="#cheems_window",
                                            resizable=False)

        def local_translate(s: str) -> str:
            if global_vars.language == "English":
                return s
            elif global_vars.language == "日本語":
                match s:
                    case "Update Party Members":
                        return "パーティーメンバー更新"
                    case "Save Party 1":
                        return "パーティ1保存"
                    case "Save Party 2":
                        return "パーティ2保存"
                    case "Enter a team name:":
                        return "チーム名を入力:"
                    case "Apply to Party 1":
                        return "パーティ1適用"
                    case "Apply to Party 2":
                        return "パーティ2適用"
                    case "Update with Party 1":
                        return "パーティ1で更新"
                    case "Update with Party 2":
                        return "パーティ2で更新"
                    case "Delete Team":
                        return "チーム削除"
                    case "Enter a new team name:":
                        return "新しいチーム名を入力:"
                    case "Rename Team":
                        return "チーム名変更"
                    case _:
                        return s
                    
            else:
                raise ValueError(f"Unknown language: {global_vars.language}")

        # cheems (teams) window allows editing characters from party 1 and party 2
        # on the left side, label party 1, then 5 selection menus for party 1, on middle, label party 2, then 5 selection menus for party 2
        # right side is reserved for later use

        party1_label = pygame_gui.elements.UILabel(pygame.Rect((0, 10), (200, 35)),
                                            "Party 1:",
                                            ui_manager,
                                            container=cheems_window)
        
        party2_label = pygame_gui.elements.UILabel(pygame.Rect((200, 10), (200, 35)),
                                            "Party 2:",
                                            ui_manager,
                                            container=cheems_window)
        
        random_plus_all_characters_names: list[str] = ["***Random***"] + all_characters_names
        random_plus_all_monsters_names: list[str] = ["***Random***"] + all_monsters_names
        party1_member_a_selection_menu = pygame_gui.elements.UIDropDownMenu(random_plus_all_characters_names,
                                                                party1[0].name,
                                                                pygame.Rect((10, 50), (180, 35)),
                                                                ui_manager,
                                                                container=cheems_window)
        
        party1_member_b_selection_menu = pygame_gui.elements.UIDropDownMenu(random_plus_all_characters_names,
                                                                party1[1].name,
                                                                pygame.Rect((10, 90), (180, 35)),
                                                                ui_manager,
                                                                container=cheems_window)
        
        party1_member_c_selection_menu = pygame_gui.elements.UIDropDownMenu(random_plus_all_characters_names,
                                                                party1[2].name,
                                                                pygame.Rect((10, 130), (180, 35)),
                                                                ui_manager,
                                                                container=cheems_window)
        
        party1_member_d_selection_menu = pygame_gui.elements.UIDropDownMenu(random_plus_all_characters_names,
                                                                party1[3].name,
                                                                pygame.Rect((10, 170), (180, 35)),
                                                                ui_manager,
                                                                container=cheems_window)
        
        party1_member_e_selection_menu = pygame_gui.elements.UIDropDownMenu(random_plus_all_characters_names,
                                                                party1[4].name,
                                                                pygame.Rect((10, 210), (180, 35)),
                                                                ui_manager,
                                                                container=cheems_window)

        list_of_names_for_p2 = None
        match current_game_mode:
            case "Adventure Mode":
                list_of_names_for_p2 = random_plus_all_monsters_names
            case "Training Mode":
                list_of_names_for_p2 = random_plus_all_characters_names
            case _:
                raise ValueError(f"Unknown game mode: {current_game_mode}")

        party2_member_a_selection_menu = pygame_gui.elements.UIDropDownMenu(list_of_names_for_p2,
                                                                party2[0].name,
                                                                pygame.Rect((210, 50), (180, 35)),
                                                                ui_manager,
                                                                container=cheems_window)
        
        party2_member_b_selection_menu = pygame_gui.elements.UIDropDownMenu(list_of_names_for_p2,
                                                                party2[1].name,
                                                                pygame.Rect((210, 90), (180, 35)),
                                                                ui_manager,
                                                                container=cheems_window)
        
        party2_member_c_selection_menu = pygame_gui.elements.UIDropDownMenu(list_of_names_for_p2,
                                                                party2[2].name,
                                                                pygame.Rect((210, 130), (180, 35)),
                                                                ui_manager,
                                                                container=cheems_window)
        
        party2_member_d_selection_menu = pygame_gui.elements.UIDropDownMenu(list_of_names_for_p2,
                                                                party2[3].name,
                                                                pygame.Rect((210, 170), (180, 35)),
                                                                ui_manager,
                                                                container=cheems_window)
        
        party2_member_e_selection_menu = pygame_gui.elements.UIDropDownMenu(list_of_names_for_p2,
                                                                party2[4].name,
                                                                pygame.Rect((210, 210), (180, 35)),
                                                                ui_manager,
                                                                container=cheems_window)

        cheems_update_party_members_button = pygame_gui.elements.UIButton(pygame.Rect((10, 260), (380, 50)),
                                            local_translate("Update Party Members"),
                                            ui_manager,
                                            container=cheems_window)

        cheems_create_new_team_name_entry = pygame_gui.elements.UITextEntryLine(pygame.Rect((10, 320), (380, 35)),
                                            ui_manager,
                                            container=cheems_window,
                                            placeholder_text=local_translate("Enter a team name:"))
        # cheems_create_new_team_name_entry.get_text()

        cheems_save_party1_button = pygame_gui.elements.UIButton(pygame.Rect((10, 365), (180, 50)),
                                            text=local_translate("Save Party 1"),
                                            manager=ui_manager,
                                            container=cheems_window)

        cheems_save_party2_button = pygame_gui.elements.UIButton(pygame.Rect((210, 365), (180, 50)),
                                            text=local_translate("Save Party 2"),
                                            manager=ui_manager,
                                            container=cheems_window)

        cheems_response_label = pygame_gui.elements.UILabel(pygame.Rect((10, 420), (810, 35)),
                                            text="",
                                            manager=ui_manager,
                                            container=cheems_window)

        # x 400 ~ 800: show the teams that player has saved here, the player can choose a team, apply it to either
        # party 1 or party 2, or delete the team

        cheems_show_player_cheems_label = pygame_gui.elements.UILabel(pygame.Rect((400, 10), (400, 35)),
                                            "Cheems:",
                                            ui_manager,
                                            container=cheems_window)
        
        cheems_show_player_cheems_selection_menu = pygame_gui.elements.UIDropDownMenu(["None"] + get_player_cheems_team_names(player),
                                                                "None",
                                                                pygame.Rect((400, 50), (400, 35)),
                                                                ui_manager,
                                                                container=cheems_window)
        
        cheems_player_cheems_member_label = pygame_gui.elements.UILabel(pygame.Rect((400, 90), (400, 35)),
                                            "",
                                            ui_manager,
                                            container=cheems_window)

        # image are shown for these 5 characters
        cheems_player_cheems_char_img_slot_a = pygame_gui.elements.UIImage(pygame.Rect((420, 130), (64, 64)), pygame.Surface((64, 64)), ui_manager, container=cheems_window)
        cheems_player_cheems_char_img_slot_b = pygame_gui.elements.UIImage(pygame.Rect((490, 130), (64, 64)), pygame.Surface((64, 64)), ui_manager, container=cheems_window)
        cheems_player_cheems_char_img_slot_c = pygame_gui.elements.UIImage(pygame.Rect((560, 130), (64, 64)), pygame.Surface((64, 64)), ui_manager, container=cheems_window)
        cheems_player_cheems_char_img_slot_d = pygame_gui.elements.UIImage(pygame.Rect((630, 130), (64, 64)), pygame.Surface((64, 64)), ui_manager, container=cheems_window)
        cheems_player_cheems_char_img_slot_e = pygame_gui.elements.UIImage(pygame.Rect((700, 130), (64, 64)), pygame.Surface((64, 64)), ui_manager, container=cheems_window)
        cheems_player_cheems_char_img_slot_a.set_image(images_item["405"])
        cheems_player_cheems_char_img_slot_b.set_image(images_item["405"])
        cheems_player_cheems_char_img_slot_c.set_image(images_item["405"])
        cheems_player_cheems_char_img_slot_d.set_image(images_item["405"])
        cheems_player_cheems_char_img_slot_e.set_image(images_item["405"])

        # Button to apply the selected team to party 1 or party 2
        cheems_apply_to_party1_button = pygame_gui.elements.UIButton(pygame.Rect((400, 210), (190, 45)),
                                            text=local_translate("Apply to Party 1"),
                                            manager=ui_manager,
                                            container=cheems_window)
        cheems_apply_to_party1_button.hide()

        cheems_apply_to_party2_button = pygame_gui.elements.UIButton(pygame.Rect((600, 210), (190, 45)),
                                            text=local_translate("Apply to Party 2"),
                                            manager=ui_manager,
                                            container=cheems_window)
        cheems_apply_to_party2_button.hide()

        # 260
        cheems_update_with_party1_button = pygame_gui.elements.UIButton(pygame.Rect((400, 265), (190, 45)),
                                            text=local_translate("Update with Party 1"),
                                            manager=ui_manager,
                                            container=cheems_window,)
        cheems_update_with_party1_button.hide()

        cheems_update_with_party2_button = pygame_gui.elements.UIButton(pygame.Rect((600, 265), (190, 45)),
                                            text=local_translate("Update with Party 2"),
                                            manager=ui_manager,
                                            container=cheems_window)
        cheems_update_with_party2_button.hide()

        cheems_rename_teams_entry = pygame_gui.elements.UITextEntryLine(pygame.Rect((400, 320), (390, 35)),
                                            ui_manager,
                                            container=cheems_window,
                                            placeholder_text=local_translate("Enter a new team name:"))
        cheems_rename_teams_entry.hide()

        cheems_rename_team_button = pygame_gui.elements.UIButton(pygame.Rect((400, 365), (190, 50)),
                                            text=local_translate("Rename Team"),
                                            manager=ui_manager,
                                            container=cheems_window)
        cheems_rename_team_button.hide()

        cheems_delete_team_button = pygame_gui.elements.UIButton(pygame.Rect((600, 365), (190, 50)),
                                            text=local_translate("Delete Team"),
                                            manager=ui_manager,
                                            container=cheems_window)
        cheems_delete_team_button.hide()

        # When None is selected, the right side is empty and lack beauty. To fix this, we show the image of the 
        # actual meme dog cheems

        cheems_meme_dog_image_slot = pygame_gui.elements.UIImage(pygame.Rect((438, 90), (322, 322)), 
                                                                 pygame.Surface((322, 322)), ui_manager, 
                                                                 container=cheems_window)
        cheems_meme_dog_image_slot.set_image(images_item["406cheems"])


    def apply_cheems_to_party(party: int):
        """
        We can simply add names get from player.cheems to
        party1_member_a_selection_menu and so on.
        """
        global player
        global party1_member_a_selection_menu, party1_member_b_selection_menu, party1_member_c_selection_menu, party1_member_d_selection_menu, party1_member_e_selection_menu
        global party2_member_a_selection_menu, party2_member_b_selection_menu, party2_member_c_selection_menu, party2_member_d_selection_menu, party2_member_e_selection_menu
        if party not in [1, 2]:
            raise ValueError(f"party must be 1 or 2, but got {party}")
        names = player.cheems[cheems_show_player_cheems_selection_menu.selected_option[0]]
        random_plus_all_characters_names: list[str] = ["***Random***"] + all_characters_names
        if party == 1:
            # This is extremely stupid, maybe there is a better implementation
            party1_member_a_selection_menu.kill()
            party1_member_a_selection_menu = pygame_gui.elements.UIDropDownMenu(random_plus_all_characters_names,
                                                                    names[0],
                                                                    pygame.Rect((10, 50), (180, 35)),
                                                                    ui_manager,
                                                                    container=cheems_window)
            party1_member_b_selection_menu.kill()
            party1_member_b_selection_menu = pygame_gui.elements.UIDropDownMenu(random_plus_all_characters_names,
                                                                    names[1],
                                                                    pygame.Rect((10, 90), (180, 35)),
                                                                    ui_manager,
                                                                    container=cheems_window)
            party1_member_c_selection_menu.kill()
            party1_member_c_selection_menu = pygame_gui.elements.UIDropDownMenu(random_plus_all_characters_names,
                                                                    names[2],
                                                                    pygame.Rect((10, 130), (180, 35)),
                                                                    ui_manager,
                                                                    container=cheems_window)
            party1_member_d_selection_menu.kill()
            party1_member_d_selection_menu = pygame_gui.elements.UIDropDownMenu(random_plus_all_characters_names,
                                                                    names[3],
                                                                    pygame.Rect((10, 170), (180, 35)),
                                                                    ui_manager,
                                                                    container=cheems_window)
            party1_member_e_selection_menu.kill()
            party1_member_e_selection_menu = pygame_gui.elements.UIDropDownMenu(random_plus_all_characters_names,
                                                                    names[4],
                                                                    pygame.Rect((10, 210), (180, 35)),
                                                                    ui_manager,
                                                                    container=cheems_window)
        else:
            if current_game_mode == "Adventure Mode":
                cheems_response_label.set_text("Party 2 is reserved for monsters in adventure mode.")
                return None
            party2_member_a_selection_menu.kill()
            party2_member_a_selection_menu = pygame_gui.elements.UIDropDownMenu(random_plus_all_characters_names,
                                                                    names[0],
                                                                    pygame.Rect((210, 50), (180, 35)),
                                                                    ui_manager,
                                                                    container=cheems_window)
            party2_member_b_selection_menu.kill()
            party2_member_b_selection_menu = pygame_gui.elements.UIDropDownMenu(random_plus_all_characters_names,
                                                                    names[1],
                                                                    pygame.Rect((210, 90), (180, 35)),
                                                                    ui_manager,
                                                                    container=cheems_window)
            party2_member_c_selection_menu.kill()
            party2_member_c_selection_menu = pygame_gui.elements.UIDropDownMenu(random_plus_all_characters_names,
                                                                    names[2],
                                                                    pygame.Rect((210, 130), (180, 35)),
                                                                    ui_manager,
                                                                    container=cheems_window)
            party2_member_d_selection_menu.kill()
            party2_member_d_selection_menu = pygame_gui.elements.UIDropDownMenu(random_plus_all_characters_names,
                                                                    names[3],
                                                                    pygame.Rect((210, 170), (180, 35)),
                                                                    ui_manager,
                                                                    container=cheems_window)
            party2_member_e_selection_menu.kill()
            party2_member_e_selection_menu = pygame_gui.elements.UIDropDownMenu(random_plus_all_characters_names,
                                                                    names[4],
                                                                    pygame.Rect((210, 210), (180, 35)),
                                                                    ui_manager,
                                                                    container=cheems_window)
            

    def save_cheems_team(team_name: str | None, party_one_or_two: int):
        """
        Save a team to player.cheems.
        player.cheems is dict[str, list[str]]  with default {}, team_name as key, and list of character names as value.
        """
        global player, text_box, cheems_show_player_cheems_selection_menu
        # player must be a subclass of Nine
        assert player is not None
        assert isinstance(player, Nine)
        assert cheems_response_label is not None

        # compile the party from selection menus
        if party_one_or_two == 1:
            party = [party1_member_a_selection_menu.selected_option[0],
                    party1_member_b_selection_menu.selected_option[0],
                    party1_member_c_selection_menu.selected_option[0],
                    party1_member_d_selection_menu.selected_option[0],
                    party1_member_e_selection_menu.selected_option[0]]
        else:
            party = [party2_member_a_selection_menu.selected_option[0],
                    party2_member_b_selection_menu.selected_option[0],
                    party2_member_c_selection_menu.selected_option[0],
                    party2_member_d_selection_menu.selected_option[0],
                    party2_member_e_selection_menu.selected_option[0]]

        if team_name is None:
            team_name = cheems_create_new_team_name_entry.get_text()

        if team_name == "":
            cheems_response_label.set_text("Team name cannot be empty.")
            return None

        if team_name == "None":
            cheems_response_label.set_text("Team name cannot be None.")
            return None

        if team_name in player.cheems:
            cheems_response_label.set_text(f"Team name {team_name} already exists.")
            return None

        # if the same team combination already exists, do not save
        for k, v in player.cheems.items():
            if v == party:
                cheems_response_label.set_text(f"Team {k} already has the exact same members.")
                return None

        # Saving a team that contains any character that is in all_monsters_names is not allowed
        for character_name in party:
            if character_name in all_monsters_names:
                cheems_response_label.set_text(f"Monsters are not allowed in teams.")
                return None

        player.cheems[team_name] = party
        # sort by key
        player.cheems = dict(sorted(player.cheems.items()))
        cheems_response_label.set_text(f"Team saved.")

        # Update the cheems selection menu
        cheems_show_player_cheems_selection_menu.kill()
        cheems_show_player_cheems_selection_menu = pygame_gui.elements.UIDropDownMenu(["None"] + get_player_cheems_team_names(player),
                                                                "None",
                                                                pygame.Rect((400, 50), (400, 35)),
                                                                ui_manager,
                                                                container=cheems_window)
        cheems_player_cheems_member_label.set_text("")
        img_slots = [cheems_player_cheems_char_img_slot_a, cheems_player_cheems_char_img_slot_b, 
        cheems_player_cheems_char_img_slot_c, cheems_player_cheems_char_img_slot_d, cheems_player_cheems_char_img_slot_e]
        for i in img_slots:
            i.set_image(images_item["405"])
        cheems_apply_to_party1_button.hide()
        cheems_apply_to_party2_button.hide()
        cheems_delete_team_button.hide()
        cheems_update_with_party1_button.hide()
        cheems_update_with_party2_button.hide()
        cheems_rename_teams_entry.hide()
        cheems_rename_team_button.hide()
        cheems_meme_dog_image_slot.show()         

    def update_cheems_team(with_party_one_or_two: int):
        # update the selected team with the current party 1 or party 2
        global player, text_box, cheems_show_player_cheems_selection_menu
        # player must be a subclass of Nine
        assert player is not None
        assert isinstance(player, Nine)
        assert cheems_response_label is not None

        if cheems_show_player_cheems_selection_menu.selected_option[0] == "None":
            cheems_response_label.set_text("Select a team to update.")
            return None
        
        if with_party_one_or_two == 1:
            party = [party1_member_a_selection_menu.selected_option[0],
                    party1_member_b_selection_menu.selected_option[0],
                    party1_member_c_selection_menu.selected_option[0],
                    party1_member_d_selection_menu.selected_option[0],
                    party1_member_e_selection_menu.selected_option[0]]
        else:
            party = [party2_member_a_selection_menu.selected_option[0],
                    party2_member_b_selection_menu.selected_option[0],
                    party2_member_c_selection_menu.selected_option[0],
                    party2_member_d_selection_menu.selected_option[0],
                    party2_member_e_selection_menu.selected_option[0]]
        
        for character_name in party:
            if character_name in all_monsters_names:
                cheems_response_label.set_text(f"Monsters are not allowed in teams.")
                return

        player.cheems[cheems_show_player_cheems_selection_menu.selected_option[0]] = party
        cheems_response_label.set_text(f"Team updated.")

        # Update the cheems selection menu

        cheems_show_player_cheems_selection_menu.kill()
        cheems_show_player_cheems_selection_menu = pygame_gui.elements.UIDropDownMenu(["None"] + get_player_cheems_team_names(player),
                                                                "None",
                                                                pygame.Rect((400, 50), (400, 35)),
                                                                ui_manager,
                                                                container=cheems_window)
        cheems_player_cheems_member_label.set_text("")
        img_slots = [cheems_player_cheems_char_img_slot_a, cheems_player_cheems_char_img_slot_b,
        cheems_player_cheems_char_img_slot_c, cheems_player_cheems_char_img_slot_d, cheems_player_cheems_char_img_slot_e]
        for i in img_slots:
            i.set_image(images_item["405"])
        cheems_apply_to_party1_button.hide()
        cheems_apply_to_party2_button.hide()
        cheems_delete_team_button.hide()
        cheems_update_with_party1_button.hide()
        cheems_update_with_party2_button.hide()
        cheems_rename_teams_entry.hide()
        cheems_rename_team_button.hide()
        cheems_meme_dog_image_slot.show()

    def delete_cheems_team(team_name: str):
        """
        Delete a team from player.cheems.
        """
        global player, text_box, cheems_show_player_cheems_selection_menu
        # player must be a subclass of Nine
        assert player is not None
        assert isinstance(player, Nine)
        assert cheems_response_label is not None

        if team_name == "None":
            cheems_response_label.set_text("Select a team to delete.")
            return None

        if team_name not in player.cheems:
            cheems_response_label.set_text(f"Team name {team_name} does not exist.")
            return None

        del player.cheems[team_name]
        player.cheems = dict(sorted(player.cheems.items()))
        cheems_response_label.set_text(f"Team {team_name} deleted.")

        # Update the cheems selection menu
        cheems_show_player_cheems_selection_menu.kill()
        cheems_show_player_cheems_selection_menu = pygame_gui.elements.UIDropDownMenu(["None"] + get_player_cheems_team_names(player),
                                                                "None",
                                                                pygame.Rect((400, 50), (400, 35)),
                                                                ui_manager,
                                                                container=cheems_window)
        cheems_player_cheems_member_label.set_text("")
        img_slots = [cheems_player_cheems_char_img_slot_a, cheems_player_cheems_char_img_slot_b, 
        cheems_player_cheems_char_img_slot_c, cheems_player_cheems_char_img_slot_d, cheems_player_cheems_char_img_slot_e]
        for i in img_slots:
            i.set_image(images_item["405"])
        cheems_apply_to_party1_button.hide()
        cheems_apply_to_party2_button.hide()
        cheems_delete_team_button.hide()
        cheems_update_with_party1_button.hide()
        cheems_update_with_party2_button.hide()
        cheems_rename_teams_entry.hide()
        cheems_rename_team_button.hide()
        cheems_meme_dog_image_slot.show()


    def rename_cheems_team(old_team_name: str, new_team_name: str):
        """
        Rename a team in player.cheems.
        """
        global player, text_box, cheems_show_player_cheems_selection_menu
        # player must be a subclass of Nine
        assert player is not None
        assert isinstance(player, Nine)
        assert cheems_response_label is not None
        assert old_team_name != "None"

        if old_team_name not in player.cheems:
            cheems_response_label.set_text(f"Team name {old_team_name} does not exist.")
            return None

        if new_team_name == "":
            cheems_response_label.set_text("New team name cannot be empty.")
            return None

        if new_team_name == "None":
            cheems_response_label.set_text("New team name cannot be None.")
            return None

        if new_team_name in player.cheems:
            cheems_response_label.set_text(f"Team name {new_team_name} already exists.")
            return None

        player.cheems[new_team_name] = player.cheems.pop(old_team_name)
        player.cheems = dict(sorted(player.cheems.items()))
        cheems_response_label.set_text(f"Team {old_team_name} renamed to {new_team_name}.")

        # Update the cheems selection menu
        cheems_show_player_cheems_selection_menu.kill()
        cheems_show_player_cheems_selection_menu = pygame_gui.elements.UIDropDownMenu(["None"] + get_player_cheems_team_names(player),
                                                                "None",
                                                                pygame.Rect((400, 50), (400, 35)),
                                                                ui_manager,
                                                                container=cheems_window)
        cheems_player_cheems_member_label.set_text("")
        img_slots = [cheems_player_cheems_char_img_slot_a, cheems_player_cheems_char_img_slot_b, 
        cheems_player_cheems_char_img_slot_c, cheems_player_cheems_char_img_slot_d, cheems_player_cheems_char_img_slot_e]
        for i in img_slots:
            i.set_image(images_item["405"])
        cheems_apply_to_party1_button.hide()
        cheems_apply_to_party2_button.hide()
        cheems_delete_team_button.hide()
        cheems_update_with_party1_button.hide()
        cheems_update_with_party2_button.hide()
        cheems_rename_teams_entry.hide()
        cheems_rename_team_button.hide()
        cheems_meme_dog_image_slot.show()




    def get_player_cheems_team_names(player: Nine) -> list[str]:
        """
        Get a list of team names from player.cheems.
        """
        assert player is not None
        assert isinstance(player, Nine)
        return list(player.cheems.keys())


    # =====================================
    # End of Cheems Section
    # =====================================
    # Core Battle System
    # =====================================

    def next_turn(party1: list[Character], party2: list[Character]):
        global turn, text_box, current_game_mode, player, adventure_mode_current_stage
        if not is_someone_alive(party1) or not is_someone_alive(party2):
            return 0
        
        buff_before = {character.name: character.buffs for character in itertools.chain(party1, party2)} # A dictionary of lists
        # character.buff is a list of objects, so we want to only get the buff.name
        buff_before = {k: [x.name for x in buff_before[k]] for k in buff_before.keys()}
        debuff_before = {character.name: character.debuffs for character in itertools.chain(party1, party2)}
        debuff_before = {k: [x.name for x in debuff_before[k]] for k in debuff_before.keys()}
        shield_value_before = {character.name: character.get_shield_value() for character in itertools.chain(party1, party2)}

        global_vars.turn_info_string = ""
        text_box.set_text("=====================================\n")
        global_vars.turn_info_string += f"Turn {turn}\n"

        # Use random consumable
        if auto_battle_active and use_random_consumable_selection_menu.selected_option[0] == "True":
            use_random_consumable()

        reset_ally_enemy_attr(party1, party2)
        for character in itertools.chain(party1, party2):
            character.update_ally_and_enemy()
            character.status_effects_start_of_turn()
            character.record_battle_turns()

        if not is_someone_alive(party1) or not is_someone_alive(party2) or turn > 300:

            buff_after = {character.name: character.buffs for character in itertools.chain(party1, party2)} 
            buff_after = {k: [x.name for x in buff_after[k]] for k in buff_after.keys()}
            buff_applied_this_turn = {k: [x for x in buff_after[k] if x not in buff_before[k]] for k in buff_before.keys()}
            # buff_removed_this_turn = {k: [x for x in buff_before[k] if x not in buff_after[k]] for k in buff_before.keys()}
            debuff_after = {character.name: character.debuffs for character in itertools.chain(party1, party2)}
            debuff_after = {k: [x.name for x in debuff_after[k]] for k in debuff_after.keys()}
            debuff_applied_this_turn = {k: [x for x in debuff_after[k] if x not in debuff_before[k]] for k in debuff_before.keys()}
            shield_value_after = {character.name: character.get_shield_value() for character in itertools.chain(party1, party2)}
            shield_value_diff = {k: shield_value_after[k] - shield_value_before[k] for k in shield_value_before.keys()}

            redraw_ui(party1, party2, refill_image=True, main_char=None, 
                    buff_added_this_turn=buff_applied_this_turn, debuff_added_this_turn=debuff_applied_this_turn,
                    shield_value_diff_dict=shield_value_diff, also_draw_chart=False)

            for character in itertools.chain(party1, party2):
                character.record_damage_taken() # Empty damage_taken this turn and add to damage_taken_history
                character.record_healing_received()

            if global_vars.draw_battle_chart == "True":
                create_tmp_damage_data_csv(party1, party2)
                create_healing_data_csv(party1, party2)
                draw_chart()

            if not is_someone_alive(party1):
                if current_game_mode == "Adventure Mode":
                    global_vars.turn_info_string += "Defeated.\n"
                else:
                    global_vars.turn_info_string += "Party 1 is defeated.\n"
            elif not is_someone_alive(party2):
                if current_game_mode == "Adventure Mode":
                    global_vars.turn_info_string += "Victory!\n"
                    player.cleared_stages = adventure_mode_current_stage
                    # gain exp for alive characters in party 1
                    for character in party1:
                        if character.is_alive():
                            character.gain_exp(adventure_mode_exp_reward())
                            global_vars.turn_info_string += f"{character.name} gained {adventure_mode_exp_reward()} exp.\n"
                    cash_reward, cash_reward_no_random = adventure_mode_cash_reward()
                    player.add_cash(cash_reward)
                    global_vars.turn_info_string += f"Gained {cash_reward} cash.\n"
                else:
                    global_vars.turn_info_string += "Party 2 is defeated.\n"
            else:
                global_vars.turn_info_string += "Battle ended with no result.\n"
            text_box.append_html_text(global_vars.turn_info_string)
            save_player(player)
            return False
        
        for character in itertools.chain(party1, party2):
            character.status_effects_midturn()
            # if character.is_alive():
            #     character.regen()

        reset_ally_enemy_attr(party1, party2)
        for character in party1:
            character.update_ally_and_enemy()
        for character in party2:
            character.update_ally_and_enemy()

        if not is_someone_alive(party1) or not is_someone_alive(party2) or turn > 300:

            buff_after = {character.name: character.buffs for character in itertools.chain(party1, party2)} 
            buff_after = {k: [x.name for x in buff_after[k]] for k in buff_after.keys()}
            buff_applied_this_turn = {k: [x for x in buff_after[k] if x not in buff_before[k]] for k in buff_before.keys()}
            # buff_removed_this_turn = {k: [x for x in buff_before[k] if x not in buff_after[k]] for k in buff_before.keys()}
            debuff_after = {character.name: character.debuffs for character in itertools.chain(party1, party2)}
            debuff_after = {k: [x.name for x in debuff_after[k]] for k in debuff_after.keys()}
            debuff_applied_this_turn = {k: [x for x in debuff_after[k] if x not in debuff_before[k]] for k in debuff_before.keys()}
            shield_value_after = {character.name: character.get_shield_value() for character in itertools.chain(party1, party2)}
            shield_value_diff = {k: shield_value_after[k] - shield_value_before[k] for k in shield_value_before.keys()}

            redraw_ui(party1, party2, refill_image=True, main_char=None, 
                    buff_added_this_turn=buff_applied_this_turn, debuff_added_this_turn=debuff_applied_this_turn,
                    shield_value_diff_dict=shield_value_diff, also_draw_chart=False)

            for character in itertools.chain(party1, party2):
                character.record_damage_taken() # Empty damage_taken this turn and add to damage_taken_history
                character.record_healing_received() 

            if global_vars.draw_battle_chart == "True":
                create_tmp_damage_data_csv(party1, party2)
                create_healing_data_csv(party1, party2)
                draw_chart()

            if not is_someone_alive(party1):
                if current_game_mode == "Adventure Mode":
                    global_vars.turn_info_string += "Defeated.\n"
                else:
                    global_vars.turn_info_string += "Party 1 is defeated.\n"    
            elif not is_someone_alive(party2):
                if current_game_mode == "Adventure Mode":
                    text_box.append_html_text("Victory!\n")
                    player.cleared_stages = adventure_mode_current_stage
                    # gain exp for alive characters in party 1
                    for character in party1:
                        if character.is_alive():
                            character.gain_exp(adventure_mode_exp_reward())
                            global_vars.turn_info_string += f"{character.name} gained {adventure_mode_exp_reward()} exp.\n"
                    cash_reward, cash_reward_no_random = adventure_mode_cash_reward()
                    player.add_cash(cash_reward)
                    global_vars.turn_info_string += f"Gained {cash_reward} cash.\n"
                else:
                    global_vars.turn_info_string += "Party 2 is defeated.\n"
            else:
                global_vars.turn_info_string += "Battle ended with no result.\n"
            text_box.append_html_text(global_vars.turn_info_string)
            save_player(player)
            return False
        
        alive_characters = [x for x in itertools.chain(party1, party2) if x.is_alive()]
        if alive_characters != []:
            weight = [x.spd for x in alive_characters]
            the_chosen_one = random.choices(alive_characters, weights=weight, k=1)[0]
            global_vars.turn_info_string += f"{the_chosen_one.name}'s turn.\n"
            the_chosen_one.action()
        else:
            global_vars.turn_info_string += "No one can be chosen to take action this turn.\n"

        for character in itertools.chain(party1, party2):
            character.status_effects_at_end_of_turn()

        buff_after = {character.name: character.buffs for character in itertools.chain(party1, party2)} 
        buff_after = {k: [x.name for x in buff_after[k]] for k in buff_after.keys()}
        buff_applied_this_turn = {k: [x for x in buff_after[k] if x not in buff_before[k]] for k in buff_before.keys()}
        # buff_removed_this_turn = {k: [x for x in buff_before[k] if x not in buff_after[k]] for k in buff_before.keys()}
        debuff_after = {character.name: character.debuffs for character in itertools.chain(party1, party2)}
        debuff_after = {k: [x.name for x in debuff_after[k]] for k in debuff_after.keys()}
        debuff_applied_this_turn = {k: [x for x in debuff_after[k] if x not in debuff_before[k]] for k in debuff_before.keys()}
        shield_value_after = {character.name: character.get_shield_value() for character in itertools.chain(party1, party2)}
        shield_value_diff = {k: shield_value_after[k] - shield_value_before[k] for k in shield_value_before.keys()}

        redraw_ui(party1, party2, refill_image=True, main_char=the_chosen_one, 
                  buff_added_this_turn=buff_applied_this_turn, debuff_added_this_turn=debuff_applied_this_turn,
                  shield_value_diff_dict=shield_value_diff, redraw_eq_slots=False, also_draw_chart=False,
                  optimize_for_auto_battle=True)

        does_anyone_taken_any_damage = False
        does_anyone_recieved_any_healing = False

        for character in itertools.chain(party1, party2):
            if character.record_damage_taken(): # Empty damage_taken this turn and add to damage_taken_history
                does_anyone_taken_any_damage = True
            if character.record_healing_received():
                does_anyone_recieved_any_healing = True

        for character in itertools.chain(party1, party2):
            character.status_effects_after_damage_record()

        if global_vars.draw_battle_chart == "True":
            if does_anyone_taken_any_damage:
                create_tmp_damage_data_csv(party1, party2)
                if current_display_chart == "Damage Dealt Chart":
                    create_plot_damage_d_chart()
                elif current_display_chart == "Damage Taken Chart":
                    create_plot_damage_r_chart()
            if does_anyone_recieved_any_healing:
                create_healing_data_csv(party1, party2)
                if current_display_chart == "Healing Chart":
                    create_plot_healing_chart()
            if does_anyone_taken_any_damage or does_anyone_recieved_any_healing:
                draw_chart()

        if not is_someone_alive(party1) or not is_someone_alive(party2) or turn > 300:
            if not is_someone_alive(party1) and not is_someone_alive(party2):
                global_vars.turn_info_string += "Both parties are defeated.\n"
            elif not is_someone_alive(party1):
                if current_game_mode == "Adventure Mode":
                    global_vars.turn_info_string += "Defeated.\n"
                else:
                    global_vars.turn_info_string += "Party 1 is defeated.\n"
            elif not is_someone_alive(party2):
                if current_game_mode == "Adventure Mode":
                    global_vars.turn_info_string += "Victory!\n"
                    player.cleared_stages = adventure_mode_current_stage
                    # gain exp for alive characters in party 1
                    for character in party1:
                        if character.is_alive():
                            character.gain_exp(adventure_mode_exp_reward())
                            text_box.append_html_text(f"{character.name} gained {adventure_mode_exp_reward()} exp.\n")
                    cash_reward, cash_reward_no_random = adventure_mode_cash_reward()
                    player.add_cash(cash_reward)
                    global_vars.turn_info_string += f"Gained {cash_reward} cash.\n"
                else:
                    global_vars.turn_info_string += "Party 2 is defeated.\n"
            else:
                global_vars.turn_info_string += "Battle ended with no result.\n"
            text_box.append_html_text(global_vars.turn_info_string)
            save_player(player)
            return False
        text_box.append_html_text(global_vars.turn_info_string)
        save_player(player)
        return True


    def all_turns(party1: list[Character], party2: list[Character], for_simulation: bool = False):
        # Warning: Constant logging on text_box is slowing down the simulation
        global turn, current_game_mode
        if not is_someone_alive(party1) or not is_someone_alive(party2):
            return 0
        while turn < 300 and is_someone_alive(party1) and is_someone_alive(party2):
            global_vars.turn_info_string = ""

            reset_ally_enemy_attr(party1, party2)
            for character in itertools.chain(party1, party2):
                character.update_ally_and_enemy()
                character.status_effects_start_of_turn()
                character.record_battle_turns()

            if not is_someone_alive(party1) or not is_someone_alive(party2):
                for character in itertools.chain(party1, party2):
                    character.record_damage_taken() 
                    character.record_healing_received()
                break

            for character in itertools.chain(party1, party2):
                character.status_effects_midturn()
                # if character.is_alive():
                #     character.regen()

            reset_ally_enemy_attr(party1, party2)
            for character in party1:
                character.update_ally_and_enemy()
            for character in party2:
                character.update_ally_and_enemy()

            if not is_someone_alive(party1) or not is_someone_alive(party2):
                for character in itertools.chain(party1, party2):
                    character.record_damage_taken() 
                    character.record_healing_received()
                break
            
            alive_characters = [x for x in itertools.chain(party1, party2) if x.is_alive()]
            if alive_characters != []:
                weight = [x.spd for x in alive_characters]
                the_chosen_one = random.choices(alive_characters, weights=weight, k=1)[0]
                the_chosen_one.action()
            else:
                pass

            for character in itertools.chain(party1, party2):
                character.status_effects_at_end_of_turn()

            for character in itertools.chain(party1, party2):
                character.record_damage_taken()
                character.record_healing_received()

            for character in itertools.chain(party1, party2):
                character.status_effects_after_damage_record()

            turn += 1

        if not for_simulation:
            create_tmp_damage_data_csv(party1, party2)
            create_healing_data_csv(party1, party2)
            create_plot_damage_d_chart()
            create_plot_damage_r_chart()
            create_plot_healing_chart()
            draw_chart()
            redraw_ui(party1, party2, redraw_eq_slots=False)

            text_box.set_text("=====================================\n")
            text_box.append_html_text(f"Turn {turn}\n")

            if turn >= 300:
                text_box.append_html_text("Battle is taking too long.\n")
            elif not is_someone_alive(party1) and not is_someone_alive(party2):
                text_box.append_html_text("Both parties are defeated.\n")
            elif not is_someone_alive(party1):
                if current_game_mode == "Adventure Mode":
                    text_box.append_html_text("Defeated.\n")
                else:
                    text_box.append_html_text("Party 1 is defeated.\n")
            elif not is_someone_alive(party2):
                if current_game_mode == "Adventure Mode":
                    text_box.append_html_text("Victory!\n")
                else:
                    text_box.append_html_text("Party 2 is defeated.\n")
            return None
        else:
            if turn >= 300:
                return None
            elif not is_someone_alive(party1) and not is_someone_alive(party2):
                return None
            elif not is_someone_alive(party1):
                return "party2"
            elif not is_someone_alive(party2):
                return "party1"
            else:
                raise ValueError("Unexpected result in all_turns simulation.")


    def all_turns_simulate_current_battle(party1: list[Character], party2: list[Character], n: int):
        """
        This function set on text_box the result of n simulations of the current battle.
        We want to know how many times party1 wins, party2 wins, or both parties are defeated.
        And the winrate of party1 and party2. 
        """
        global turn
        n = int(n)
        results = {"party1": 0, "party2": 0, "No Result": 0, "error": 0}
        turn_results = []
        for i in range(n):
            turn = 1
            for c in itertools.chain(party1, party2):
                c.reset_stats()
            reset_ally_enemy_attr(party1, party2)
            for c in itertools.chain(party1, party2):
                c.battle_entry_effects()
                c.battle_entry_effects_eqset()
            # for c in itertools.chain(party1, party2):
            #     print(c)
            try:
                result = all_turns(party1, party2, for_simulation=True)
            except Exception as e:
                results["error"] += 1
                print(e)
                continue
            turn_results.append(turn)
            if result == "party1":
                results["party1"] += 1
            elif result == "party2":
                results["party2"] += 1
            else:
                results["No Result"] += 1
        text_box.set_text("=====================================\n")
        total = sum(results.values())
        text_box.append_html_text(f"Simulated {n} games.\n")
        if results["error"]:
            text_box.append_html_text(f"Error occurred {results['error']} times.\n")
        text_box.append_html_text(f"Party 1: {party1[0].name} {party1[1].name} {party1[2].name} {party1[3].name} {party1[4].name}\n")
        text_box.append_html_text(f"Party 2: {party2[0].name} {party2[1].name} {party2[2].name} {party2[3].name} {party2[4].name}\n")
        text_box.append_html_text(f"Party 1 wins {results["party1"]} times ({results["party1"] / total:.2%}).\n")
        text_box.append_html_text(f"Party 2 wins {results["party2"]} times ({results["party2"] / total:.2%}).\n")
        text_box.append_html_text(f"No result {results['No Result']} times ({results['No Result'] / total:.2%}).\n")
        # The average number of turns in the simulation
        text_box.append_html_text(f"Average number of turns: {sum(turn_results) / n:.2f}.\n")
        # The median number of turns in the simulation
        text_box.append_html_text(f"Median number of turns: {statistics.median(turn_results)}.\n")
        # Fastest recorded game
        text_box.append_html_text(f"Fastest game: {min(turn_results)} turns.\n")
        # Slowest recorded game
        text_box.append_html_text(f"Slowest game: {max(turn_results)} turns.\n")
        redraw_ui(party1, party2)






    df_damage_summary = None
    df_healing_summary = None
    plot_damage_d_chart = None
    plot_damage_r_chart = None
    plot_healing_chart = None

    def create_tmp_damage_data_csv(p1, p2):
        """
        fetch data from p1 and p2 characters damage_taken_history and create a csv file
        then the csv is processed by analyze.py to create a summary of the damage taken df_damage_summary
        then the df_damage_summary is visualized by analyze.py to create a plot of the damage taken plot_damage_d_chart and plot_damage_r_chart
        """
        global df_damage_summary, plot_damage_d_chart, plot_damage_r_chart
        if not os.path.exists("./.tmp"):
            os.makedirs("./.tmp")
        data = {}
        original_character_list = [character.name for character in itertools.chain(p1, p2)]
        for character in itertools.chain(party1, party2):
            # print(character.damage_taken_history)
            # [[], [], [], [], [], [], [], [], [], [], [], [], [(8798, <character.Pheonix object at 0x7a1d667b4250>, 'normal_critical')], 
            # [(2500, <character.Pheonix object at 0x7a1d667b4250>, 'status')], [(2500, <character.Pheonix object at 0x7a1d667b4250>, 'status')], 
            # [(2500, <character.Pheonix object at 0x7a1d667b4250>, 'status')], [(2500, <character.Pheonix object at 0x7a1d667b4250>, 'status')], 
            # [(2500, <character.Pheonix object at 0x7a1d667b4250>, 'status')], [(2500, <character.Pheonix object at 0x7a1d667b4250>, 'status')], 
            # [(2500, <character.Pheonix object at 0x7a1d667b4250>, 'status')], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], 
            # [], [], [], [], [(0, <character.Yuri object at 0x7a1d667b43d0>, 'normal'), 
            # (2597, <character.Yuri object at 0x7a1d667b43d0>, 'normal'), (3243, <character.Yuri object at 0x7a1d667b43d0>, 'normal'), 
            # (2448, <character.Yuri object at 0x7a1d667b43d0>, 'normal'), (3213, <character.Yuri object at 0x7a1d667b43d0>, 'normal')], 
            # [(10441, <character.Requina object at 0x7a1d667b4370>, 'normal')], [(11222, <character.Yuri object at 0x7a1d667b43d0>, 'normal'), 
            # (2520, <character.Yuri object at 0x7a1d667b43d0>, 'normal'), (2459, <character.Yuri object at 0x7a1d667b43d0>, 'normal'), 
            # (2969, <character.Yuri object at 0x7a1d667b43d0>, 'normal'), (6193, <character.Yuri object at 0x7a1d667b43d0>, 'normal_critical')], 
            # [(6055, <character.Gabe object at 0x7a1d667b43a0>, 'normal')], [(5306, <character.Gabe object at 0x7a1d667b43a0>, 'normal')], [], 
            # [(4934, <character.Requina object at 0x7a1d667b4370>, 'normal')], [(500, <character.Requina object at 0x7a1d667b4370>, 'status')], 
            # [(500, <character.Requina object at 0x7a1d667b4370>, 'status'), (5146, <character.Requina object at 0x7a1d667b4370>, 'normal')], ...
            filtered_damage_taken_history = []
            for record in character.damage_taken_history:
                if not record:
                    continue
                else:
                    for abc_tuple in record:
                        if abc_tuple[1] is not None:
                            filtered_damage_taken_history.append((abc_tuple[0], abc_tuple[1].name, abc_tuple[2]))
              
            data[character.name] = filtered_damage_taken_history


        # Create the DataFrame directly from the data dictionary
        df_damage_taken_history = pd.DataFrame(list(data.items()), columns=['Character', 'Damage Taken History'])
        # print(df_damage_taken_history)

        # previous code
        # with open("./.tmp/tmp_damage_data.csv", "w", newline='') as f:
        #     writer = csv.writer(f)
        #     writer.writerow(["Character", "Damage Taken History"])

        #     for name, history in data.items():
        #         writer.writerow([name, history])
                
        # df_damage_taken_history = pd.read_csv("./.tmp/tmp_damage_data.csv")
        # print(df_damage_taken_history)

        df = analyze.create_damage_summary_new(original_character_list, dataframe=df_damage_taken_history)
        df_damage_summary = df
            
    def create_plot_damage_d_chart() -> None:
        global df_damage_summary, plot_damage_d_chart
        if df_damage_summary is None:
            return
        plot_damage_d_chart = analyze.damage_summary_visualize(df_damage_summary, what_to_visualize="dealt")

    def create_plot_damage_r_chart() -> None:
        global df_damage_summary, plot_damage_r_chart
        if df_damage_summary is None:
            return
        plot_damage_r_chart = analyze.damage_summary_visualize(df_damage_summary, what_to_visualize="received")

    def create_healing_data_csv(p1, p2):
        """
        Basically the same as create_tmp_damage_data_csv, but for healing_received_history
        """
        global df_healing_summary, plot_healing_chart
        if not os.path.exists("./.tmp"):
            os.makedirs("./.tmp")
        data = {}
        original_character_list = [character.name for character in itertools.chain(p1, p2)]
        for character in itertools.chain(party1, party2):
            # print(character.healing_received_history) # Basically the same as damage_taken_history, but only (healing, healer) tuple
            # [[], [], [], [], [], [], [], [], [], [(10066, <character.Clover object at 0x72c1b410d4b0>)], [], [], 
            # [(5952, <character.Clover object at 0x72c1b410d4b0>)], [], [], [], [], [], [], [], [], [], [], [], [], [], 
            # [], [], [], [], [], [], [], [], [(25957, <character.Clover object at 0x72c1b410d4b0>)], [], [], [], [], [], [], 
            # [], [], [], [], [], [], [], [], [], [], [], [], [(10500, <character.Clover object at 0x72c1b410d4b0>)], [], [], 
            # [], [(10332, <character.Clover object at 0x72c1b410d4b0>)], [], [], [], [], []]
            # We sometimes have a string as healer instead of a character object, i.e. "Equipment"
            filtered_healing_received_history = []
            for record in character.healing_received_history:
                if not record:
                    # filtered_healing_received_history.append(record)
                    continue
                else:
                    for ab_tuple in record:
                        if isinstance(ab_tuple[1], str):
                            filtered_healing_received_history.append((ab_tuple[0], ab_tuple[1]))
                        else:
                            filtered_healing_received_history.append((ab_tuple[0], ab_tuple[1].name))
            data[character.name] = filtered_healing_received_history

        # Create the DataFrame directly from the data dictionary
        df_healing_received_history = pd.DataFrame(list(data.items()), columns=['Character', 'Healing Received History'])
        # print(df_healing_received_history)

        df = analyze.create_healing_summary(original_character_list, dataframe=df_healing_received_history)
        df_healing_summary = df

    def create_plot_healing_chart() -> None:
        global df_healing_summary, plot_healing_chart
        if df_healing_summary is None:
            return
        plot_healing_chart = analyze.healing_summary_visualize(df_healing_summary)

            
    def restart_battle():
        global turn, auto_battle_active, plot_damage_d_chart, plot_damage_r_chart, plot_healing_chart
        global_vars.turn_info_string = ""
        for character in party1 + party2:
            character.reset_stats()
        reset_ally_enemy_attr(party1, party2)
        global_vars.turn_info_string += "Battle entry effects:\n"
        for character in party1 + party2:
            character.battle_entry_effects_activate()
        plot_damage_d_chart = None
        plot_damage_r_chart = None
        plot_healing_chart = None
        redraw_ui(party1, party2, redraw_eq_slots=False)
        turn = 1
        text_box.append_html_text(global_vars.turn_info_string)

        if auto_battle_active and use_random_consumable_selection_menu.selected_option[0] == "True":
            use_random_consumable()


    def is_in_manipulatable_game_states() -> bool:
        """
        Allows the following disruptive action:
        Equip/Unequip
        """
        if turn == 1:
            return True
        # When the game is concluded, allow the player to equip/unequip
        if not is_someone_alive(party1) or not is_someone_alive(party2): 
            return True
        return False


    def update_character_selection_menu(party_show_in_menu: list[str] | None, di: int=0):
        """
        party_show_in_menu: List of strings to show in the character selection menu
        di: Default option index
        """
        global character_selection_menu, ui_manager
        # if party_show_in_menu is not provided, we build from party1 and party2
        if not party_show_in_menu:
            if current_game_mode == "Training Mode":
                party_show_in_menu = [f" Lv.{character.lvl} {character.name}" for character in itertools.chain(party1, party2)]
            elif current_game_mode == "Adventure Mode":
                party_show_in_menu = [f" Lv.{character.lvl} {character.name}" for character in party1]

        if di >= len(party_show_in_menu):
            di = 0

        character_selection_menu.kill()
        character_selection_menu = pygame_gui.elements.UIDropDownMenu(party_show_in_menu,
                                                                party_show_in_menu[di],
                                                                character_selection_menu_pos,
                                                                ui_manager)


    def set_up_characters(is_start_of_app=False, reset_party1: bool = True, reset_party2: bool = True):
        global character_selection_menu, reserve_character_selection_menu, all_characters, party2, party1, text_box
        if not is_start_of_app:
            text_box.set_text("==============================\n")
        for character in all_characters:
            character.reset_stats()
        if not party1:
            reset_party1 = True
        if not party2:
            reset_party2 = True
        if reset_party1 and reset_party2:
            party1 = []
            party2 = []
            list_of_characters = random.sample(all_characters, 10)
            random.shuffle(list_of_characters)
            party1 = list_of_characters[:5]
            party2 = list_of_characters[5:]
        elif reset_party1 and not reset_party2:
            party1 = random.sample([character for character in all_characters if character not in party2], 5)
            random.shuffle(party1)
            
        elif not reset_party1 and reset_party2:
            party2 = random.sample([character for character in all_characters if character not in party1], 5)
            random.shuffle(party2)
        else:
            pass

        remaining_characters = [character for character in all_characters if character not in itertools.chain(party1, party2)]
        remaining_characters.sort(key=lambda x: x.lvl, reverse=True)

        party_show_in_menu = [f" Lv.{character.lvl} {character.name}" for character in itertools.chain(party1, party2)]
        update_character_selection_menu(party_show_in_menu)

        global_vars.turn_info_string = ""
        reset_ally_enemy_attr(party1, party2)
        global_vars.turn_info_string += "Battle entry effects:\n"
        for character in party1:
            character.battle_entry_effects_activate()
        for character in party2:
            character.battle_entry_effects_activate()
        redraw_ui(party1, party2)
        text_box.append_html_text(global_vars.turn_info_string)
        return party1, party2


    def set_up_characters_adventure_mode(shuffle_characters=False):
        global character_selection_menu, reserve_character_selection_menu, all_characters, all_monsters, party2, party1, text_box
        text_box.set_text("==============================\n")
        for character in all_characters + all_monsters:
            character.reset_stats()
        if shuffle_characters:
            party1 = random.sample(all_characters, 5)
        party2 = adventure_mode_stages[adventure_mode_current_stage]
        remaining_characters = [character for character in all_characters if character not in party1]
        remaining_characters.sort(key=lambda x: x.lvl, reverse=True)
        party1_show_in_menu = [f" Lv.{character.lvl} {character.name}" for character in party1]
        update_character_selection_menu(party1_show_in_menu)

        global_vars.turn_info_string = ""
        reset_ally_enemy_attr(party1, party2)
        global_vars.turn_info_string += "Battle entry effects:\n"
        for character in party1:
            character.battle_entry_effects_activate()
        for character in party2:
            character.battle_entry_effects_activate()
        redraw_ui(party1, party2)
        text_box.append_html_text(global_vars.turn_info_string)

        return party1, party2


    def cheems_edit_party():
        global cheems_response_label
        # selection menus in cheems_window gives the user the ability to edit the party
        assert party1_member_a_selection_menu is not None
        # this likely wont happen as the button triggers this function is in the cheems_window
        # when cheems_window opens, the selection menus are created
        party1_edited: list[str] = [party1_member_a_selection_menu.selected_option[0], party1_member_b_selection_menu.selected_option[0],
                                    party1_member_c_selection_menu.selected_option[0], party1_member_d_selection_menu.selected_option[0],
                                    party1_member_e_selection_menu.selected_option[0]]
        party2_edited: list[str] = [party2_member_a_selection_menu.selected_option[0], party2_member_b_selection_menu.selected_option[0],
                                    party2_member_c_selection_menu.selected_option[0], party2_member_d_selection_menu.selected_option[0],
                                    party2_member_e_selection_menu.selected_option[0]]
        # party1_edited and party2_edited are list of character names
        # 3.9.0: now party1_edited and party2_edited can take ***Random*** as a character name
        # In this case, the character will be randomly selected from the remaining characters
        if current_game_mode == "Training Mode":
            if "***Random***" in party1_edited or "***Random***" in party2_edited:
                remaining_characters = [character for character in all_characters_names if character not in party1_edited + party2_edited]
                # how many random characters to select
                n = party1_edited.count("***Random***") + party2_edited.count("***Random***")
                assert n <= len(remaining_characters), "Not enough characters to select from."
                random_characters = random.sample(remaining_characters, n)
                for i, character in enumerate(party1_edited):
                    if character == "***Random***":
                        party1_edited[i] = random_characters.pop()
                for i, character in enumerate(party2_edited):
                    if character == "***Random***":
                        party2_edited[i] = random_characters.pop()
        elif current_game_mode == "Adventure Mode":
            # party1 is characters, party2 is monsters
            if "***Random***" in party1_edited:
                remaining_characters = [character for character in all_characters_names if character not in party1_edited]
                n = party1_edited.count("***Random***")
                assert n <= len(remaining_characters), "Not enough characters to select from."
                random_characters = random.sample(remaining_characters, n)
                for i, character in enumerate(party1_edited):
                    if character == "***Random***":
                        party1_edited[i] = random_characters.pop()
            if "***Random***" in party2_edited:
                remaining_characters = [character for character in all_monsters_names if character not in party2_edited]
                n = party2_edited.count("***Random***")
                assert n <= len(remaining_characters), "Not enough monsters to select from."
                random_characters = random.sample(remaining_characters, n)
                for i, character in enumerate(party2_edited):
                    if character == "***Random***":
                        party2_edited[i] = random_characters.pop()

        character_counts = {}
        for character in party1_edited + party2_edited:
            if character in character_counts:
                character_counts[character] += 1
            else:
                character_counts[character] = 1

        duplicates = [character for character, count in character_counts.items() if count > 1]

        if duplicates:
            cheems_response_label.set_text(f"Same character cannot appear twice! Duplicates: {', '.join(duplicates)}")
            return

        for i, n in enumerate(party1_edited):
            party1[i] = next((c for c in all_characters if c.name == n), None)
        for i, n in enumerate(party2_edited):
            party2[i] = next((c for c in all_characters + all_monsters if c.name == n), None)

        cheems_response_label.set_text("Party members updated.")
        text_box.set_text("=====================================\n")
        restart_battle()
        redraw_ui(party1, party2)
        update_character_selection_menu(None)


    def swap_characters_in_party(two_index: set[int]):
        """
        Swaps two characters in the party.
        """
        global party1, party2
        # print(two_index) # {0, 1}
        indices = list(two_index)
        # if two index is both 0 to 5, then we are swapping party1 characters
        if all(0 <= i < 5 for i in indices):
            party1[indices[0]], party1[indices[1]] = party1[indices[1]], party1[indices[0]]
        # if two index is both 5 to 10, then we are swapping party2 characters
        elif all(5 <= i < 10 for i in indices):
            party2[indices[0] - 5], party2[indices[1] - 5] = party2[indices[1] - 5], party2[indices[0] - 5]
        # if one index is 0 to 5 and the other is 5 to 10, then we are swapping between party1 and party2
        elif 0 <= indices[0] < 5 and 5 <= indices[1] < 10 and current_game_mode == "Training Mode":
            party1[indices[0]], party2[indices[1] - 5] = party2[indices[1] - 5], party1[indices[0]]
        elif 0 <= indices[1] < 5 and 5 <= indices[0] < 10 and current_game_mode == "Training Mode":
            party1[indices[1]], party2[indices[0] - 5] = party2[indices[0] - 5], party1[indices[1]]
        else:
            return
        text_box.set_text("=====================================\n") 
        restart_battle()
        redraw_ui(party1, party2)
        update_character_selection_menu(None) 

    def replace_character_with_new(character_name: str, index: int):
        """
        Replaces a character in the party with a new character.
        """
        global party1, party2
        # if character already in party, return
        if any(character_name == character.name for character in itertools.chain(party1, party2)):
            return
        if 0 <= index < 5:
            party1[index] = next((c for c in all_characters if c.name == character_name), None)
        elif 5 <= index < 10:
            if current_game_mode == "Adventure Mode":
                return
            party2[index - 5] = next((c for c in all_characters if c.name == character_name), None)
        text_box.set_text("=====================================\n")
        restart_battle()
        redraw_ui(party1, party2)
        update_character_selection_menu(None)


    def add_outline_to_image(surface, outline_color, outline_thickness):
        """
        Adds an outline to the image at the specified index in the image_slots list.

        Parameters:
        image (pygame.Surface): Image to add the outline to.
        outline_color (tuple): Color of the outline in RGB format.
        outline_thickness (int): Thickness of the outline.
        """
        new_image = pygame.Surface(surface.get_size(), pygame.SRCALPHA)
        new_image.fill((255, 255, 255, 0)) 
        new_image.blit(surface, (0, 0))

        rect = pygame.Rect((0, 0), surface.get_size())
        pygame.draw.rect(new_image, outline_color, rect, outline_thickness)

        return new_image


    def create_yellow_text(surface, text, font_size, text_color=(255, 255, 0), offset=10, 
                           position_type='bottom', bold=False, italic=False, add_background=False):
        """
        Parameters:
        surface (pygame.Surface): The surface on which to draw the text.
        text (str): The text to be rendered.
        font_size (int): The size of the text.
        text_color (tuple): RGB color of the text. Default is yellow (255, 255, 0).
        offset (int): The offset from the edge of the surface.
        position_type (str): The position type for the text ('bottom' or 'topleft').
        add_background (bool): If True, adds a white background behind the text. Default is False.
        """
        font = pygame.font.Font(None, font_size)
        if bold:
            font.set_bold(True)
        if italic:
            font.set_italic(True)
        text_surface = font.render(text, True, text_color)
        text_rect = text_surface.get_rect()

        if add_background:
            background_surface = pygame.Surface(text_rect.size)
            background_surface.fill((255, 255, 255))

        if position_type == 'bottom':
            text_rect.centerx = surface.get_rect().centerx
            text_rect.bottom = surface.get_rect().bottom - offset
        elif position_type == 'bottomleft':
            text_rect.x = 10
            text_rect.bottom = surface.get_rect().bottom - offset
        elif position_type == 'bottomright':
            text_rect.right = surface.get_rect().right - 10
            text_rect.bottom = surface.get_rect().bottom - offset
        elif position_type == 'top':
            text_rect.centerx = surface.get_rect().centerx
            text_rect.y = offset
        elif position_type == 'topleft':
            text_rect.x = 10
            text_rect.y = offset
        elif position_type == 'topright':
            text_rect.right = surface.get_rect().right - 10
            text_rect.y = offset
        elif position_type == 'center':
            text_rect.center = surface.get_rect().center

        if add_background:
            surface.blit(background_surface, text_rect)
        surface.blit(text_surface, text_rect)


    def create_healthbar(hp, maxhp, width, height, color_unfilled_bar=(255, 238, 186), color_filled_bar=(255, 193, 7), shield_value=0,
                         shield_bar_color=(252, 248, 15), auto_color=False) -> pygame.Surface:
        """
        Creates a health bar.

        Parameters:
        hp (int): Current health.
        maxhp (int): Maximum health.
        width (int): Width of the health bar.
        height (int): Height of the health bar.
        color_unfilled_bar (tuple): RGB color of the unfilled part of the health bar.
        color_filled_bar (tuple): RGB color of the filled part of the health bar.
        shield_value (int): Shield value of the character. Default is 0.
        auto_color (bool): If True, the health bar color will change based on the global_vars.theme, theme change is not compatible
        with defined color_filled_bar and color_unfilled_bar and shield_bar_color. Default is False.
        """
        if auto_color:
            match global_vars.theme:
                case "Yellow Theme":
                    color_unfilled_bar = (255, 238, 186)
                    shield_bar_color = (255, 234, 7)
                    color_filled_bar = (252, 248, 15)
                case "Purple Theme":
                    color_unfilled_bar = (248, 231, 255)
                    color_filled_bar = (236, 192, 255)
                    shield_bar_color = (198,153,255)
                case "Blue Theme":
                    color_unfilled_bar = (220, 240, 255)  
                    shield_bar_color = (122, 194, 255)    
                    color_filled_bar = (200, 230, 255)   
                case "Green Theme":
                    color_unfilled_bar = (230, 255, 230)
                    shield_bar_color = (144, 238, 144)
                    color_filled_bar = (193, 255, 193)
                case "Pink Theme":
                    color_unfilled_bar = (255, 238, 248)
                    shield_bar_color = (255, 170, 207)
                    color_filled_bar = (255, 209, 229)
                case "Red Theme":
                    color_unfilled_bar = (255, 220, 220)
                    color_filled_bar = (255, 160, 160)
                    shield_bar_color = (255, 128, 128)
                case _:
                    raise Exception(f"Unknown theme: {global_vars.theme}")

        surface = pygame.Surface((width, height))
        surface.fill(color_unfilled_bar)

        if hp > 0 and hp + shield_value <= maxhp:
            hp_percentage = hp / maxhp
            hp_bar_width = int(width * hp_percentage)
            hp_bar_height = height
            hp_bar_rect = pygame.Rect((0, 0), (hp_bar_width, hp_bar_height))
            pygame.draw.rect(surface, color_filled_bar, hp_bar_rect)

            shield_percentage = shield_value / maxhp
            shield_bar_width = int(width * shield_percentage)
            shield_bar_height = height
            shield_bar_rect = pygame.Rect((hp_bar_width, 0), (shield_bar_width, shield_bar_height))
            pygame.draw.rect(surface, shield_bar_color, shield_bar_rect)
        elif hp > 0 and hp + shield_value > maxhp:
            new_maxhp = hp + shield_value
            hp_percentage = hp / new_maxhp
            hp_bar_width = int(width * hp_percentage)
            hp_bar_height = height
            hp_bar_rect = pygame.Rect((0, 0), (hp_bar_width, hp_bar_height))
            pygame.draw.rect(surface, color_filled_bar, hp_bar_rect)

            shield_percentage = shield_value / new_maxhp
            shield_bar_width = int(width * shield_percentage)
            shield_bar_height = height
            shield_bar_rect = pygame.Rect((hp_bar_width, 0), (shield_bar_width, shield_bar_height))
            pygame.draw.rect(surface, shield_bar_color, shield_bar_rect)

        create_yellow_text(surface, f"{hp}/{maxhp}", 25, position_type='center', text_color=(0, 0, 0))

        return surface


    character_healthbar_slot_top1 = pygame_gui.elements.UIImage(pygame.Rect((90, 220), (176, 30)),
                                        pygame.Surface((176, 30)),
                                        ui_manager)
    character_healthbar_slot_top2 = pygame_gui.elements.UIImage(pygame.Rect((290, 220), (176, 30)),
                                        pygame.Surface((176, 30)),
                                        ui_manager)
    character_healthbar_slot_top3 = pygame_gui.elements.UIImage(pygame.Rect((490, 220), (176, 30)),
                                        pygame.Surface((176, 30)),
                                        ui_manager)
    character_healthbar_slot_top4 = pygame_gui.elements.UIImage(pygame.Rect((690, 220), (176, 30)),
                                        pygame.Surface((176, 30)),
                                        ui_manager)
    character_healthbar_slot_top5 = pygame_gui.elements.UIImage(pygame.Rect((890, 220), (176, 30)),
                                        pygame.Surface((176, 30)),
                                        ui_manager)
    character_healthbar_slot_buttom1 = pygame_gui.elements.UIImage(pygame.Rect((90, 825), (176, 30)),
                                        pygame.Surface((176, 30)),
                                        ui_manager)
    character_healthbar_slot_buttom2 = pygame_gui.elements.UIImage(pygame.Rect((290, 825), (176, 30)),
                                        pygame.Surface((176, 30)),
                                        ui_manager)
    character_healthbar_slot_buttom3 = pygame_gui.elements.UIImage(pygame.Rect((490, 825), (176, 30)),
                                        pygame.Surface((176, 30)),
                                        ui_manager)
    character_healthbar_slot_buttom4 = pygame_gui.elements.UIImage(pygame.Rect((690, 825), (176, 30)),
                                        pygame.Surface((176, 30)),
                                        ui_manager)
    character_healthbar_slot_buttom5 = pygame_gui.elements.UIImage(pygame.Rect((890, 825), (176, 30)),
                                        pygame.Surface((176, 30)),
                                        ui_manager)

    health_bar_party1 = [character_healthbar_slot_top1, character_healthbar_slot_top2, character_healthbar_slot_top3, character_healthbar_slot_top4, character_healthbar_slot_top5]
    health_bar_party2 = [character_healthbar_slot_buttom1, character_healthbar_slot_buttom2, character_healthbar_slot_buttom3, character_healthbar_slot_buttom4, character_healthbar_slot_buttom5]


    # each healthbar is divided into 3 parts, a overlay is created on top of it.
    # this overlay will be used to show status effects tooltips,
    # we create 3 pages because often, status effects have too much text to be shown in one page
    character_healthbar_slot_top1_o1 = pygame_gui.elements.UIImage(pygame.Rect((90, 220), (58, 65)),
                                        pygame.Surface((58, 30)),
                                        ui_manager)
    character_healthbar_slot_top1_o2 = pygame_gui.elements.UIImage(pygame.Rect((90+58, 220), (59, 65)),
                                        pygame.Surface((59, 30)),
                                        ui_manager)
    character_healthbar_slot_top1_o3 = pygame_gui.elements.UIImage(pygame.Rect((90+58+59, 220), (58, 65)),
                                        pygame.Surface((58, 30)),
                                        ui_manager)
    character_healthbar_slot_top2_o1 = pygame_gui.elements.UIImage(pygame.Rect((290, 220), (58, 65)),
                                        pygame.Surface((58, 30)),
                                        ui_manager)
    character_healthbar_slot_top2_o2 = pygame_gui.elements.UIImage(pygame.Rect((290+58, 220), (59, 65)),
                                        pygame.Surface((59, 30)),
                                        ui_manager)
    character_healthbar_slot_top2_o3 = pygame_gui.elements.UIImage(pygame.Rect((290+58+59, 220), (58, 65)),
                                        pygame.Surface((58, 30)),
                                        ui_manager)
    character_healthbar_slot_top3_o1 = pygame_gui.elements.UIImage(pygame.Rect((490, 220), (58, 65)),
                                        pygame.Surface((58, 30)),
                                        ui_manager)
    character_healthbar_slot_top3_o2 = pygame_gui.elements.UIImage(pygame.Rect((490+58, 220), (59, 65)),
                                        pygame.Surface((59, 30)),
                                        ui_manager)
    character_healthbar_slot_top3_o3 = pygame_gui.elements.UIImage(pygame.Rect((490+58+59, 220), (58, 65)),
                                        pygame.Surface((58, 30)),
                                        ui_manager)
    character_healthbar_slot_top4_o1 = pygame_gui.elements.UIImage(pygame.Rect((690, 220), (58, 65)),
                                        pygame.Surface((58, 30)),
                                        ui_manager)
    character_healthbar_slot_top4_o2 = pygame_gui.elements.UIImage(pygame.Rect((690+58, 220), (59, 65)),
                                        pygame.Surface((59, 30)),
                                        ui_manager)
    character_healthbar_slot_top4_o3 = pygame_gui.elements.UIImage(pygame.Rect((690+58+59, 220), (58, 65)),
                                        pygame.Surface((58, 30)),
                                        ui_manager)
    character_healthbar_slot_top5_o1 = pygame_gui.elements.UIImage(pygame.Rect((890, 220), (58, 65)),
                                        pygame.Surface((58, 30)),
                                        ui_manager)
    character_healthbar_slot_top5_o2 = pygame_gui.elements.UIImage(pygame.Rect((890+58, 220), (59, 65)),
                                        pygame.Surface((59, 30)),
                                        ui_manager)
    character_healthbar_slot_top5_o3 = pygame_gui.elements.UIImage(pygame.Rect((890+58+59, 220), (58, 65)),
                                        pygame.Surface((58, 30)),
                                        ui_manager)
    character_healthbar_slot_buttom1_o1 = pygame_gui.elements.UIImage(pygame.Rect((90, 825), (58, 65)),
                                        pygame.Surface((58, 30)),
                                        ui_manager)
    character_healthbar_slot_buttom1_o2 = pygame_gui.elements.UIImage(pygame.Rect((90+58, 825), (59, 65)),
                                        pygame.Surface((59, 30)),
                                        ui_manager)
    character_healthbar_slot_buttom1_o3 = pygame_gui.elements.UIImage(pygame.Rect((90+58+59, 825), (58, 65)),
                                        pygame.Surface((58, 30)),
                                        ui_manager)
    character_healthbar_slot_buttom2_o1 = pygame_gui.elements.UIImage(pygame.Rect((290, 825), (58, 65)),
                                        pygame.Surface((58, 30)),
                                        ui_manager)
    character_healthbar_slot_buttom2_o2 = pygame_gui.elements.UIImage(pygame.Rect((290+58, 825), (59, 65)),
                                        pygame.Surface((59, 30)),
                                        ui_manager)
    character_healthbar_slot_buttom2_o3 = pygame_gui.elements.UIImage(pygame.Rect((290+58+59, 825), (58, 65)),
                                        pygame.Surface((58, 30)),
                                        ui_manager)
    character_healthbar_slot_buttom3_o1 = pygame_gui.elements.UIImage(pygame.Rect((490, 825), (58, 65)),
                                        pygame.Surface((58, 30)),
                                        ui_manager)
    character_healthbar_slot_buttom3_o2 = pygame_gui.elements.UIImage(pygame.Rect((490+58, 825), (59, 65)),
                                        pygame.Surface((59, 30)),
                                        ui_manager)
    character_healthbar_slot_buttom3_o3 = pygame_gui.elements.UIImage(pygame.Rect((490+58+59, 825), (58, 65)),
                                        pygame.Surface((58, 30)),
                                        ui_manager)
    character_healthbar_slot_buttom4_o1 = pygame_gui.elements.UIImage(pygame.Rect((690, 825), (58, 65)),
                                        pygame.Surface((58, 30)),
                                        ui_manager)
    character_healthbar_slot_buttom4_o2 = pygame_gui.elements.UIImage(pygame.Rect((690+58, 825), (59, 65)),
                                        pygame.Surface((59, 30)),
                                        ui_manager)
    character_healthbar_slot_buttom4_o3 = pygame_gui.elements.UIImage(pygame.Rect((690+58+59, 825), (58, 65)),
                                        pygame.Surface((58, 30)),
                                        ui_manager)
    character_healthbar_slot_buttom5_o1 = pygame_gui.elements.UIImage(pygame.Rect((890, 825), (58, 65)),
                                        pygame.Surface((58, 30)),
                                        ui_manager)
    character_healthbar_slot_buttom5_o2 = pygame_gui.elements.UIImage(pygame.Rect((890+58, 825), (59, 65)),
                                        pygame.Surface((59, 30)),
                                        ui_manager)
    character_healthbar_slot_buttom5_o3 = pygame_gui.elements.UIImage(pygame.Rect((890+58+59, 825), (58, 65)),
                                        pygame.Surface((58, 30)),
                                        ui_manager)
    health_bar_party1_overlay = [[character_healthbar_slot_top1_o1, character_healthbar_slot_top1_o2, character_healthbar_slot_top1_o3],
                                [character_healthbar_slot_top2_o1, character_healthbar_slot_top2_o2, character_healthbar_slot_top2_o3],
                                [character_healthbar_slot_top3_o1, character_healthbar_slot_top3_o2, character_healthbar_slot_top3_o3],
                                [character_healthbar_slot_top4_o1, character_healthbar_slot_top4_o2, character_healthbar_slot_top4_o3],
                                [character_healthbar_slot_top5_o1, character_healthbar_slot_top5_o2, character_healthbar_slot_top5_o3]]
    for t in health_bar_party1_overlay:
        for overlay in t:
            overlay.set_image((images_item["405"]))
            overlay.change_layer(1)
    
    health_bar_party2_overlay = [[character_healthbar_slot_buttom1_o1, character_healthbar_slot_buttom1_o2, character_healthbar_slot_buttom1_o3],
                                [character_healthbar_slot_buttom2_o1, character_healthbar_slot_buttom2_o2, character_healthbar_slot_buttom2_o3],
                                [character_healthbar_slot_buttom3_o1, character_healthbar_slot_buttom3_o2, character_healthbar_slot_buttom3_o3],
                                [character_healthbar_slot_buttom4_o1, character_healthbar_slot_buttom4_o2, character_healthbar_slot_buttom4_o3],
                                [character_healthbar_slot_buttom5_o1, character_healthbar_slot_buttom5_o2, character_healthbar_slot_buttom5_o3]]
    for t in health_bar_party2_overlay:
        for overlay in t:
            overlay.set_image((images_item["405"]))
            overlay.change_layer(1)





    damage_graph_slot = pygame_gui.elements.UIImage(pygame.Rect((1080, 645), (500, 235)),
                                        pygame.Surface((500, 235)),
                                        ui_manager)
    # ./tmp/damage_dealt.png
    damage_graph_slot.set_image((images_item["405"]))


    def redraw_ui(party1, party2, *, refill_image=True, main_char=None,
                  buff_added_this_turn=None, debuff_added_this_turn=None, shield_value_diff_dict=None, redraw_eq_slots=True,
                  also_draw_chart=True, optimize_for_auto_battle=False):

        def redraw_party(party, image_slots, equip_slots_weapon, equip_slots_armor, equip_slots_accessory, equip_stats_boots, 
                         labels, healthbar, equip_effect_slots, image_slots_overlays, healthbar_overlays):
            for i, character in enumerate(party):
                if refill_image:
                    try:
                        image_slots[i].set_image(character.featured_image)
                    except Exception:
                        image_slots[i].set_image(images_item["404"])


                if global_vars.language == "日本語" and hasattr(character, "tooltip_string_jp"):
                    image_slots[i].set_tooltip(character.tooltip_string_jp(), delay=0.1, wrap_width=250)
                else:
                    image_slots[i].set_tooltip(character.tooltip_string(), delay=0.1, wrap_width=250)
                

                if redraw_eq_slots:
                    ignore_draw_weapon = False
                    ignore_draw_armor = False
                    ignore_draw_accessory = False
                    ignore_draw_boots = False
                    try:
                        equip_slots_weapon[i].set_image(images_item[character.equip["Weapon"].image])
                        equip_slots_weapon[i].show()
                    except KeyError:
                        equip_slots_weapon[i].hide()
                        ignore_draw_weapon = True
                    try:
                        equip_slots_armor[i].set_image(images_item[character.equip["Armor"].image])
                        equip_slots_armor[i].show()
                    except KeyError:
                        equip_slots_armor[i].hide()
                        ignore_draw_armor = True
                    try:
                        equip_slots_accessory[i].set_image(images_item[character.equip["Accessory"].image])
                        equip_slots_accessory[i].show()
                    except KeyError:
                        equip_slots_accessory[i].hide()
                        ignore_draw_accessory = True
                    try:
                        equip_stats_boots[i].set_image(images_item[character.equip["Boots"].image])
                        equip_stats_boots[i].show()
                    except KeyError:
                        equip_stats_boots[i].hide()
                        ignore_draw_boots = True

                    if global_vars.language == "日本語":
                        if not ignore_draw_weapon:
                            equip_slots_weapon[i].set_tooltip(character.equip["Weapon"].print_stats_html_jp(), delay=0.1, wrap_width=400)
                        if not ignore_draw_armor:
                            equip_slots_armor[i].set_tooltip(character.equip["Armor"].print_stats_html_jp(), delay=0.1, wrap_width=400)
                        if not ignore_draw_accessory:
                            equip_slots_accessory[i].set_tooltip(character.equip["Accessory"].print_stats_html_jp(), delay=0.1, wrap_width=400)
                        if not ignore_draw_boots:
                            equip_stats_boots[i].set_tooltip(character.equip["Boots"].print_stats_html_jp(), delay=0.1, wrap_width=400)
                    elif global_vars.language == "English":
                        if not ignore_draw_weapon:
                            equip_slots_weapon[i].set_tooltip(character.equip["Weapon"].print_stats_html(), delay=0.1, wrap_width=400)
                        if not ignore_draw_armor:
                            equip_slots_armor[i].set_tooltip(character.equip["Armor"].print_stats_html(), delay=0.1, wrap_width=400)
                        if not ignore_draw_accessory:
                            equip_slots_accessory[i].set_tooltip(character.equip["Accessory"].print_stats_html(), delay=0.1, wrap_width=400)
                        if not ignore_draw_boots:
                            equip_stats_boots[i].set_tooltip(character.equip["Boots"].print_stats_html(), delay=0.1, wrap_width=400)


                # This should always be redrawn
                if character.equipment_set_effects_tooltip() != "":
                    equip_effect_slots[i].show()
                    equip_effect_slots[i].set_tooltip(character.equipment_set_effects_tooltip(), delay=0.1, wrap_width=400)
                else:
                    equip_effect_slots[i].hide()

                labels[i].set_text(f"lv {character.lvl} {character.name}")

                if global_vars.language == "日本語" and hasattr(character, "skill_tooltip_jp"):
                    labels[i].set_tooltip(character.skill_tooltip_jp(), delay=0.1, wrap_width=555)
                else:
                    labels[i].set_tooltip(character.skill_tooltip(), delay=0.1, wrap_width=555)
                # Doesn't work so commented out
                # labels[i].set_text_alpha(255) if character.is_alive() else labels[i].set_text_alpha(125)

                # redraw healthbar is fairly expensive process, so we need to optimize it
                # if optimize_for_auto_battle and shield_value_diff_dict[character.name] == 0 and not character.damage_taken_this_turn and not character.healing_received_this_turn:
                #     pass
                # else:
                # Edit on 2.2.9: Optimize is removed because we wont be able to catch skills that change maxhp or shield
                healthbar[i].set_image(create_healthbar(character.hp, character.maxhp, 176, 30, shield_value=character.get_shield_value(), auto_color=True))

                character_status_effect_str_sp, character_status_effect_str_buff, character_status_effect_str_debuff = character.tooltip_status_effects()
                healthbar_overlays[i][0].set_tooltip(character_status_effect_str_sp, delay=0.1, wrap_width=430)
                healthbar_overlays[i][1].set_tooltip(character_status_effect_str_buff, delay=0.1, wrap_width=430)
                healthbar_overlays[i][2].set_tooltip(character_status_effect_str_debuff, delay=0.1, wrap_width=430)
                # Create text on them to show how many status effect there are
                # character.get_the_amount_of_effect() returns a tuple of (sp, buff, debuff)
                healthbar_overlays[i][0].set_image((images_item["405"]))
                healthbar_overlays[i][1].set_image((images_item["405"]))
                healthbar_overlays[i][2].set_image((images_item["405"]))
                # if character.battle_turns > 0: # Keep it tidy
                healthbar_overlays_a = healthbar_overlays[i][0].image
                healthbar_overlays_b = healthbar_overlays[i][1].image
                healthbar_overlays_c = healthbar_overlays[i][2].image
                sp_count, buff_count, debuff_count = character.get_the_amount_of_effect()
                if sp_count:
                    create_yellow_text(healthbar_overlays_a, str(sp_count), 25, (186, 186, 255), 10)
                    healthbar_overlays[i][0].set_image(healthbar_overlays_a)
                if buff_count:
                    create_yellow_text(healthbar_overlays_b, str(buff_count), 25, (0, 255, 0), 10)
                    healthbar_overlays[i][1].set_image(healthbar_overlays_b)
                if debuff_count:
                    create_yellow_text(healthbar_overlays_c, str(debuff_count), 25, (255, 0, 0), 10)
                    healthbar_overlays[i][2].set_image(healthbar_overlays_c)


                if main_char == character:
                    labels[i].set_text(f"--> lv {character.lvl} {character.name}")
                    image = image_slots[i].image
                    new_image = add_outline_to_image(image, (255, 215, 0), 6)
                    image_slots[i].set_image(new_image)

                # self.damage_taken_this_turn = [] # list of tuples (damage, attacker, damage_type)
                image_slots_overlays[i].set_image(images_item["405"])
                character_image_overlay = image_slots_overlays[i].image
                current_offset_for_damage_and_healing = 10
                if character.damage_taken_this_turn:
                    image = image_slots[i].image
                    new_image = add_outline_to_image(image, (255, 0, 0), 4)
                    for a, b, c in character.damage_taken_this_turn:
                        match c:
                            case "normal":
                                create_yellow_text(character_image_overlay, str(a), 25, (255, 0, 0), current_offset_for_damage_and_healing)
                            case "status":
                                # orange text
                                create_yellow_text(character_image_overlay, str(a), 25, (255, 165, 0), current_offset_for_damage_and_healing)
                            case "normal_critical":
                                create_yellow_text(character_image_overlay, str(a), 25, (255, 0, 0), current_offset_for_damage_and_healing, bold=True, italic=True)
                            case "friendlyfire":
                                # grey text
                                create_yellow_text(character_image_overlay, str(a), 25, (153, 153, 153), current_offset_for_damage_and_healing)
                            case "bypass":
                                # cadetblue
                                create_yellow_text(character_image_overlay, str(a), 25, (95, 158, 160), current_offset_for_damage_and_healing)
                            case _:
                                raise Exception(f"Unknown damage type: {c}")
                        current_offset_for_damage_and_healing += 12
                    image_slots[i].set_image(new_image)
                    image_slots_overlays[i].set_image(character_image_overlay)
                if character.healing_received_this_turn:
                    image = image_slots[i].image
                    new_image = add_outline_to_image(image, (0, 255, 0), 4)
                    # get all healing from list of tuples
                    healing_list = [x[0] for x in character.healing_received_this_turn]
                    # show healing on image
                    for healing in healing_list:
                        create_yellow_text(character_image_overlay, str(healing), 25, (0, 255, 0), current_offset_for_damage_and_healing)
                        current_offset_for_damage_and_healing += 12
                    image_slots[i].set_image(new_image)
                    image_slots_overlays[i].set_image(character_image_overlay)

                if buff_added_this_turn:
                    value = buff_added_this_turn[character.name]
                    if value:
                        image = image_slots[i].image
                        new_image = add_outline_to_image(image, (0, 255, 0), 2)
                        image_slots[i].set_image(new_image)
                if debuff_added_this_turn:
                    value = debuff_added_this_turn[character.name]
                    if value:
                        image = image_slots[i].image
                        new_image = add_outline_to_image(image, (255, 0, 0), 1)
                        image_slots[i].set_image(new_image)
                if buff_added_this_turn and debuff_added_this_turn:
                    buff_strs = buff_added_this_turn[character.name]
                    debuff_strs = debuff_added_this_turn[character.name]
                    current_offset = 10
                    if buff_strs:
                        for buff_str in buff_strs:
                            create_yellow_text(image_slots[i].image, buff_str, 15, (0, 255, 0), current_offset, 'topleft')
                            current_offset += 15
                    if debuff_strs:
                        for debuff_str in debuff_strs:
                            create_yellow_text(image_slots[i].image, debuff_str, 15, (255, 0, 0), current_offset, 'topleft')
                            current_offset += 15
                if shield_value_diff_dict:
                    value = shield_value_diff_dict[character.name]
                    if value != 0:
                        create_yellow_text(image_slots[i].image, str(int(value)), 25, (192, 192, 192), 10, 'bottomleft')

                if character.is_alive():
                    top_right_offset = 10
                    if character.is_charmed():
                        create_yellow_text(image_slots[i].image, "Charmed", 15, (255, 0, 0), top_right_offset, 'topright')
                        top_right_offset += 10
                    if character.is_confused():
                        create_yellow_text(image_slots[i].image, "Confused", 15, (255, 0, 0), top_right_offset, 'topright')
                        top_right_offset += 10
                    if character.is_stunned():
                        create_yellow_text(image_slots[i].image, "Stunned", 15, (255, 0, 0), top_right_offset, 'topright')
                        top_right_offset += 10
                    if character.is_silenced():
                        create_yellow_text(image_slots[i].image, "Silenced", 15, (255, 0, 0), top_right_offset, 'topright')
                        top_right_offset += 10
                    if character.is_sleeping():
                        create_yellow_text(image_slots[i].image, "Sleeping", 15, (255, 0, 0), top_right_offset, 'topright')
                        top_right_offset += 10
                    if character.is_frozed():
                        create_yellow_text(image_slots[i].image, "Frozen", 15, (255, 0, 0), top_right_offset, 'topright')
                        top_right_offset += 10



        redraw_party(party1, image_slots_party1, equip_slot_party1_weapon, equip_slot_party1_armor, equip_slot_party1_accessory, equip_slot_party1_boots,
                     label_party1, health_bar_party1, equip_set_slot_party1, image_slot_overlay_party1, health_bar_party1_overlay)
        redraw_party(party2, image_slots_party2, equip_slot_party2_weapon, equip_slot_party2_armor, equip_slot_party2_accessory, equip_slot_party2_boots,
                     label_party2, health_bar_party2, equip_set_slot_party2, image_slot_overlay_party2, health_bar_party2_overlay)
        if also_draw_chart:
            draw_chart()



    def draw_chart():
        global current_display_chart, df_damage_summary, plot_damage_d_chart, plot_damage_r_chart, plot_healing_chart
        match current_display_chart:
            case "Damage Dealt Chart":
                if plot_damage_d_chart:
                    damage_graph_slot.set_image(plot_damage_d_chart)
                    if df_damage_summary is not None:
                        if global_vars.language == "日本語":
                            tooltip_text = "与えたダメージ合計:\n"
                            for line in df_damage_summary.values:
                                tooltip_text += f"{line[0]}は合計で{line[7]}のダメージを与えました。通常ダメージ{line[8]}、クリティカルダメージ{line[9]}、異常状態ダメージ{line[10]}、異常状態無視ダメージ{line[11]}、誤爆ダメージ{line[12]}。\n"
                        elif global_vars.language == "English":
                            tooltip_text = "Damage dealt summary:\n"
                            for line in df_damage_summary.values:
                                tooltip_text += f"{line[0]} dealt {line[7]} damage in total, {line[8]} normal damage, {line[9]} critical damage, {line[10]} status damage, {line[11]} bypass damage, {line[12]} friendly fire damage.\n"
                        damage_graph_slot.set_tooltip(tooltip_text, delay=0.1, wrap_width=700)
                else:
                    damage_graph_slot.set_image(images_item["405"])
                    damage_graph_slot.set_tooltip("", delay=0.1, wrap_width=100)
            case "Damage Taken Chart":
                if plot_damage_r_chart:
                    damage_graph_slot.set_image(plot_damage_r_chart)
                    if df_damage_summary is not None:
                        if global_vars.language == "日本語":
                            tooltip_text = "受けたダメージ合計:\n"
                            for line in df_damage_summary.values:
                                tooltip_text += f"{line[0]}は合計で{line[1]}のダメージを受けました。通常ダメージ{line[2]}、クリティカルダメージ{line[3]}、異常状態ダメージ{line[4]}、異常状態無視ダメージ{line[5]}、誤爆ダメージ{line[6]}。\n"
                        elif global_vars.language == "English":
                            tooltip_text = "Damage taken summary:\n"
                            for line in df_damage_summary.values:
                                tooltip_text += f"{line[0]} received {line[1]} damage in total, {line[2]} normal damage, {line[3]} critical damage, {line[4]} status damage, {line[5]} bypass damage, {line[6]} friendly fire damage.\n"
                        damage_graph_slot.set_tooltip(tooltip_text, delay=0.1, wrap_width=700)
                else:
                    damage_graph_slot.set_image(images_item["405"])
                    damage_graph_slot.set_tooltip("", delay=0.1, wrap_width=100)
            case "Healing Chart":
                if plot_healing_chart:
                    damage_graph_slot.set_image(plot_healing_chart)
                    if df_healing_summary is not None:
                        if global_vars.language == "日本語":
                            tooltip_text = "受けた回復合計:\n"
                            for line in df_healing_summary.values:
                                tooltip_text += f"{line[0]}は合計で{line[1]}の回復を受けました。{line[2]}の回復を行いました。\n"
                        elif global_vars.language == "English":
                            tooltip_text = "Healing summary:\n"
                            for line in df_healing_summary.values:
                                tooltip_text += f"{line[0]} received {line[1]} healing in total, {line[2]} healing is given.\n"
                        damage_graph_slot.set_tooltip(tooltip_text, delay=0.1, wrap_width=600)
                else:
                    damage_graph_slot.set_image(images_item["405"])
                    damage_graph_slot.set_tooltip("", delay=0.1, wrap_width=100)
            case _:
                raise Exception(f"Unknown current_display_chart: {current_display_chart}")

    # =====================================
    # Text Entry Box Section
    # =====================================
    text_box = pygame_gui.elements.UITextEntryBox(pygame.Rect((300, 300), (556, 295)),"", ui_manager)
    text_box_introduction_text = "Hover over character name to show skill information.\n"
    text_box_introduction_text += "If lower cased character_name.jpg or png file is not found in ./image/character directory, 404.png will be used instead.\n"
    text_box_introduction_text += "If lower cased item_name.jpg or png file is not found in ./image/item directory, 404.png will be used instead.\n"
    text_box_introduction_text += "If lower cased monster_original_name.jpg or png file is not found in ./image/monster directory, 404.png will be used instead.\n"
    text_box_introduction_text += "Hover over character image to show attributes.\n"
    text_box_introduction_text += "Hover over character status effect indicator to show status effects.\n"
    text_box.set_text(text_box_introduction_text)

    box_submenu_previous_stage_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((300, 560), (75, 35)),
                                                                    text='Prev',
                                                                    manager=ui_manager)
    box_submenu_previous_stage_button.set_tooltip("Go to previous stage.", delay=0.1)

    box_submenu_next_stage_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((380, 560), (75, 35)),
                                                                    text='Next',
                                                                    manager=ui_manager)
    box_submenu_next_stage_button.set_tooltip("Advance to the next stage. You can proceed only if the current stage has been cleared.", delay=0.1)

    box_submenu_refresh_stage_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((460, 560), (75, 35)),
                                                                    text='Refresh',
                                                                    manager=ui_manager)
    box_submenu_refresh_stage_button.set_tooltip("Refresh the current stage, get a new set of monsters.", delay=0.1)


    box_submenu_previous_stage_button.hide()
    box_submenu_next_stage_button.hide()
    box_submenu_refresh_stage_button.hide()

    box_submenu_stage_info_label = pygame_gui.elements.UILabel(relative_rect=pygame.Rect((550, 560), (80, 35)),
                                                                    text='Current Stage: 1',
                                                                    manager=ui_manager)
    box_submenu_stage_info_label.hide()

    box_submenu_enter_shop_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((635, 560), (120, 35)),
                                                                text='Enter Shop',
                                                                manager=ui_manager)
    box_submenu_enter_shop_button.set_tooltip("Enter the shop to buy items.", delay=0.1)
    box_submenu_enter_shop_button.hide()
    box_submenu_exit_shop_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((760, 560), (95, 35)),
                                                                text='Exit Shop',
                                                                manager=ui_manager)
    box_submenu_exit_shop_button.set_tooltip("Exit the shop.", delay=0.1)
    box_submenu_exit_shop_button.hide()

    # =====================================
    # End of Text Entry Box Section
    # =====================================
    # =====================================
    # Shop Section
    # =====================================


    shop_image_slota = pygame_gui.elements.UIImage(pygame.Rect((300, 300), (100, 100)),
                                        pygame.Surface((100, 100)),
                                        ui_manager)
    shop_image_slotb = pygame_gui.elements.UIImage(pygame.Rect((412, 300), (100, 100)),
                                        pygame.Surface((100, 100)),
                                        ui_manager)
    shop_image_slotc = pygame_gui.elements.UIImage(pygame.Rect((524, 300), (100, 100)),
                                        pygame.Surface((100, 100)),
                                        ui_manager)
    shop_image_slotd = pygame_gui.elements.UIImage(pygame.Rect((636, 300), (100, 100)),
                                        pygame.Surface((100, 100)),
                                        ui_manager)
    shop_image_slote = pygame_gui.elements.UIImage(pygame.Rect((748, 300), (100, 100)),
                                        pygame.Surface((100, 100)),
                                        ui_manager)
    
    shop_image_slot_currency_icon = pygame_gui.elements.UIImage(pygame.Rect((260, 400), (32, 32)),
                                        pygame.Surface((32, 32)),
                                        ui_manager)

    shop_price_labela = pygame_gui.elements.UILabel(relative_rect=pygame.Rect((300, 400), (100, 32)),
                                                                    text='17522443',
                                                                    manager=ui_manager)
    shop_price_labelb = pygame_gui.elements.UILabel(relative_rect=pygame.Rect((412, 400), (100, 32)),
                                                                    text='17522443',
                                                                    manager=ui_manager)
    shop_price_labelc = pygame_gui.elements.UILabel(relative_rect=pygame.Rect((524, 400), (100, 32)),
                                                                    text='17522443',
                                                                    manager=ui_manager)
    shop_price_labeld = pygame_gui.elements.UILabel(relative_rect=pygame.Rect((636, 400), (100, 32)),
                                                                    text='17522443',
                                                                    manager=ui_manager)
    shop_price_labele = pygame_gui.elements.UILabel(relative_rect=pygame.Rect((748, 400), (100, 32)),
                                                                    text='17522443',
                                                                    manager=ui_manager)
    shop_price_discount_labela = pygame_gui.elements.UILabel(relative_rect=pygame.Rect((300, 425), (100, 24)),
                                                                    text='-60%',
                                                                    manager=ui_manager)
    shop_price_discount_labelb = pygame_gui.elements.UILabel(relative_rect=pygame.Rect((412, 425), (100, 24)),
                                                                    text='-60%',
                                                                    manager=ui_manager)
    shop_price_discount_labelc = pygame_gui.elements.UILabel(relative_rect=pygame.Rect((524, 425), (100, 24)),
                                                                    text='-60%',
                                                                    manager=ui_manager)
    shop_price_discount_labeld = pygame_gui.elements.UILabel(relative_rect=pygame.Rect((636, 425), (100, 24)),
                                                                    text='-60%',
                                                                    manager=ui_manager)
    shop_price_discount_labele = pygame_gui.elements.UILabel(relative_rect=pygame.Rect((748, 425), (100, 24)),
                                                                    text='-60%',
                                                                    manager=ui_manager)
    shop_item_purchase_buttona = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((300, 450), (100, 35)),
                                                                    text='Purchase',
                                                                    manager=ui_manager)
    shop_item_purchase_buttonb = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((412, 450), (100, 35)),
                                                                    text='Purchase',
                                                                    manager=ui_manager)
    shop_item_purchase_buttonc = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((524, 450), (100, 35)),
                                                                    text='Purchase',
                                                                    manager=ui_manager)
    shop_item_purchase_buttond = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((636, 450), (100, 35)),
                                                                    text='Purchase',
                                                                    manager=ui_manager)
    shop_item_purchase_buttone = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((748, 450), (100, 35)),
                                                                    text='Purchase',
                                                                    manager=ui_manager)
    shop_select_a_shop = pygame_gui.elements.UIDropDownMenu(["Silver Wolf Company", "Big Food Market", "RoyalMint"],
                                                            "Silver Wolf Company",
                                                            pygame.Rect((300, 500), (212, 35)),
                                                            ui_manager)

    extra_shop_list = eq_set_list_without_none_and_void
    # Add "Forge" to each string in the list
    extra_shop_list_a = [f"{item} Forge" for item in extra_shop_list]
    extra_shop_list_b = [f"{item} Reforged" for item in extra_shop_list]
    if global_vars.allow_cheat:
        extra_shop_list_c = [f"{item} Premium" for item in extra_shop_list]
    else:
        extra_shop_list_c = None
    extra_shop_list = extra_shop_list_a + extra_shop_list_b
    if extra_shop_list_c:
        extra_shop_list += extra_shop_list_c
    extra_shop_list.sort()
    shop_select_a_shop.add_options(extra_shop_list)


    # shop_shop_introduction_sign = pygame_gui.elements.UIImage(pygame.Rect((815, 500), (35, 35)),
    #                                     pygame.Surface((35, 35)),
    #                                     ui_manager)
    # shop_shop_introduction_sign.set_image(images_item["info_sign"])
    shop_refresh_items_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((524, 500), (100, 35)),
                                                                    text='Refresh',
                                                                    manager=ui_manager)
    shop_player_owned_currency_icon = pygame_gui.elements.UIImage(pygame.Rect((625, 500), (32, 32)),
                                        pygame.Surface((32, 32)),
                                        ui_manager)
    shop_player_owned_currency = pygame_gui.elements.UILabel(relative_rect=pygame.Rect((660, 500), (100, 36)),
                                                                    text='17522443',
                                                                    manager=ui_manager)
    shop_player_owned_currency.set_tooltip("Owned currency. Different shops may accept different currency.", delay=0.1)

    all_shop_ui_modules = [shop_image_slota, shop_image_slotb, shop_image_slotc, shop_image_slotd, shop_image_slote,
                            shop_image_slot_currency_icon, shop_price_labela, shop_price_labelb, shop_price_labelc, shop_price_labeld, shop_price_labele,
                            shop_price_discount_labela, shop_price_discount_labelb, shop_price_discount_labelc, shop_price_discount_labeld, shop_price_discount_labele,
                            shop_item_purchase_buttona, shop_item_purchase_buttonb, shop_item_purchase_buttonc, shop_item_purchase_buttond, shop_item_purchase_buttone,
                            shop_select_a_shop, shop_refresh_items_button, shop_player_owned_currency_icon,
                            shop_player_owned_currency]
    for m in all_shop_ui_modules:
        m.hide()

    def redraw_ui_shop_edition(reload_shop: bool = True) -> shop.Shop:

        # translate
        if global_vars.language == "日本語":
            shop_refresh_items_button.set_text("商品更新")
            shop_player_owned_currency.set_tooltip("所有通貨。店によって使える通貨が異なる場合がある。", delay=0.1)
            shop_item_purchase_buttona.set_text("購入")
            shop_item_purchase_buttonb.set_text("購入")
            shop_item_purchase_buttonc.set_text("購入")
            shop_item_purchase_buttond.set_text("購入")
            shop_item_purchase_buttone.set_text("購入")
        elif global_vars.language == "English":
            shop_refresh_items_button.set_text("Refresh")
            shop_player_owned_currency.set_tooltip("Owned currency. Different shops may accept different currency.", delay=0.1)
            shop_item_purchase_buttona.set_text("Purchase")
            shop_item_purchase_buttonb.set_text("Purchase")
            shop_item_purchase_buttonc.set_text("Purchase")
            shop_item_purchase_buttond.set_text("Purchase")
            shop_item_purchase_buttone.set_text("Purchase")


        if reload_shop:
            # we first need to get what shop it is
            shop_name = shop_select_a_shop.selected_option[0]
            # then we create a shop of Shop.[shop_name]
            match shop_name:
                case "Silver Wolf Company":
                    shop_instance = shop.Gulid_SliverWolf("Silver Wolf Company", None)
                case "Big Food Market":
                    shop_instance = shop.Big_Food_Market("Big Food Market", None)
                case "RoyalMint":
                    shop_instance = shop.RoyalMint("RoyalMint", None)
                # case "CHEAT":
                #     shop_instance = shop.Dev_Cheat("CHEAT", None)
                case _:
                    if "Forge" in shop_name:
                        # class Armory_Brand_Specific(Shop):
                        #   def __init__(self, name, description, brand_name):
                        # dynamic creation of class
                        brand_name = shop_name.split(" ")[0]
                        # use eval to create a class
                        shop_instance = eval(f"shop.Armory_Brand_Specific")(shop_name, None, brand_name)
                    elif "Reforged" in shop_name:
                        brand_name = shop_name.split(" ")[0]
                        shop_instance = eval(f"shop.Armory_Brand_Specific_Reforged")(shop_name, None, brand_name)
                    elif "Premium" in shop_name:
                        brand_name = shop_name.split(" ")[0]
                        shop_instance = eval(f"shop.Armory_Brand_Specific_Premium")(shop_name, None, brand_name)
                    else:
                        raise Exception(f"Unknown shop name: {shop_name}")

            shop_instance.get_items_from_manufacturers()
            shop_instance.decide_price()
            shop_instance.decide_discount()
            shop_instance.calculate_final_price()
        
        else:
            shop_instance = global_vars.current_shop_instance

        shop_image_slot_currency_icon.set_image(images_item[eval(f"{shop_instance.currency}(1)").image])
        shop_player_owned_currency_icon.set_image(images_item[eval(f"{shop_instance.currency}(1)").image])
        set_currency_on_icon_and_label(player, shop_instance.currency, shop_player_owned_currency, shop_player_owned_currency_icon)

        # shop_shop_introduction_sign.set_tooltip(shop_instance.description, delay=0.1, wrap_width=300)

        image_slots = [shop_image_slota, shop_image_slotb, shop_image_slotc, shop_image_slotd, shop_image_slote]
        # Code here is copyed from Nine() class
        list_of_shop_items = list(shop_instance.inventory.keys())
        dict_image_slots_items = {k: v for k, v in mit.zip_equal(image_slots, list_of_shop_items)}
        # set up image and tooltip to UIImage based on item info
        for ui_image, item in dict_image_slots_items.items():
            if item.image:
                # If stackable, process the image and show amount
                if item.can_be_stacked:
                    try:
                        image_to_process = images_item[item.image].copy()
                    except KeyError:
                        image_to_process = images_item["404"].copy()
                    # scale the image to 800 x 800
                    image_to_process = pygame.transform.scale(image_to_process, (800, 800))
                    create_yellow_text(image_to_process, str(item.current_stack), 310, (0, 0, 0), add_background=True)
                    ui_image.set_image(image_to_process)
                else:
                    try:
                        ui_image.set_image(images_item[item.image])
                    except KeyError:
                        print(f"Warning: Image not found: {item.image} in redraw_ui_shop_edition()")
                        match (type(item).__name__, item.type):    
                            case ("Equip", "Weapon"):
                                ui_image.set_image(images_item["Generic_Weapon"])
                            case ("Equip", "Armor"):
                                ui_image.set_image(images_item["Generic_Armor"])
                            case ("Equip", "Accessory"):
                                ui_image.set_image(images_item["Generic_Accessory"])
                            case ("Equip", "Boots"):
                                ui_image.set_image(images_item["Generic_Boots"])
                            case _:
                                print(f"Warning: Unknown item type: {item.type} in redraw_ui_shop_edition()")
                                ui_image.set_image(images_item["404"])
            if global_vars.language == "日本語" and hasattr(item, "print_stats_html_jp"):
                ui_image.set_tooltip(item.print_stats_html_jp(), delay=0.1, wrap_width=400)
            else:
                ui_image.set_tooltip(item.print_stats_html(), delay=0.1, wrap_width=400)
        # set up prices
        price_labels = [shop_price_labela, shop_price_labelb, shop_price_labelc, shop_price_labeld, shop_price_labele]
        for price_label, (p, d, f) in mit.zip_equal(price_labels, list(shop_instance.inventory.values())): 
            price_label.set_text(str(f))
        # show discount
        discount_labels = [shop_price_discount_labela, shop_price_discount_labelb, shop_price_discount_labelc, shop_price_discount_labeld, shop_price_discount_labele]
        for discount_label, (p, d, f) in mit.zip_equal(discount_labels, list(shop_instance.inventory.values())):
            # if no discount, show nothing
            if d == 0:
                discount_label.set_text("")
            else:
                discount_label.set_text(f"(-{(d * 100):.1f}%)")

        global_vars.current_shop_instance = shop_instance
        return shop_instance


    def shop_purchase_item(player: Nine, shop: shop.Shop, item_id: int) -> None:
        item_price = list(shop.inventory.values())[item_id][2]
        item = list(shop.inventory.keys())[item_id]
        copyed_item = copy.copy(item)
        # print(f"item: {item}, price: {item_price}")
        buy_one_item(player, copyed_item, item_price, shop.currency)
        set_currency_on_icon_and_label(player, shop.currency, shop_player_owned_currency, shop_player_owned_currency_icon)

    def set_currency_on_icon_and_label(player: Nine, currency: str, label: pygame_gui.elements.UILabel, icon: pygame_gui.elements.UIImage):
        icon.set_image(images_item[eval(f"{currency}(1)").image])
        # print(f"Currency: {currency}")
        label.set_text(str(player.get_currency(currency)))



    # for c in all_characters + all_monsters:
        # c.equip_item_from_list(generate_equips_list(4, random_full_eqset=True)) 

    def initiate_player_data():
        try:
            player, character_info_dict = load_player()
            print("Player and character data loaded.")
        except FileNotFoundError:
            print("Player data not found, creating a new one...")
            if start_with_max_level:
                player = Nine(5000000000)
                player.cleared_stages = 2000
                package_of_equips = [EquipPackage(100), EquipPackage2(100), EquipPackage3(100), EquipPackage4(100), 
                                    EquipPackage5(100), EquipPackage6(100), FoodPackage(100), FoodPackage2(100), FoodPackage3(100)]
                player.add_package_of_items_to_inventory(package_of_equips)
                package_of_ingots = [SliverIngot(1), GoldIngot(1), DiamondIngot(1)]
                player.add_package_of_items_to_inventory(package_of_ingots)
            else:
                player = Nine(80000)
                player.cleared_stages = 0
                # new player reward
                starter_package = [EquipPackage(2)]
                player.add_package_of_items_to_inventory(starter_package)


        try:
            character_info_dict
        except NameError:
            pass
        else:
            for c in all_characters:
                if not c.name in character_info_dict.keys():
                    print(f"Character {c.name} not found in character_info_dict, skipped loading equip.") # When a new character is added, this will happen.
                    continue
                c.lvl = character_info_dict[c.name][0]
                c.exp = character_info_dict[c.name][1]
                if character_info_dict[c.name][2]:
                    # print(f"Trying to read equipment data and equip items for {c.name}...")
                    for d in character_info_dict[c.name][2]:
                        item = Equip("foo", "Weapon", "Common")
                        for attr, value in d.items():
                            if hasattr(item, attr):
                                setattr(item, attr, value)
                        item.estimate_market_price()
                        item.for_attacker_value = item.estimate_value_for_attacker()
                        item.for_support_value = item.estimate_value_for_support()
                        item.four_set_effect_description = item.assign_four_set_effect_description()
                        item.four_set_effect_description_jp = item.assign_four_set_effect_description_jp()
                        c.equip_item(item)
                        # print(f"Equipped {str(item)} to {c.name}.")
        return player

    player = initiate_player_data()

    adventure_mode_stages: dict[int, list[monsters.Monster]] = {}
    if player.cleared_stages > 0:
        print(f"Loaded adventure mode stages from player data. Current stage: {player.cleared_stages}")
        adventure_mode_current_stage = min(player.cleared_stages + 1, 3000)
    else:
        adventure_mode_current_stage = 1
    adventure_mode_generate_stage()

    party1 : list[Character] = []
    party2 : list[Character] = []
    party1, party2 = set_up_characters(is_start_of_app=True)
    player.build_inventory_slots()
    turn = 1

    change_theme(player.settings_theme, reload_language=False)
    swap_language(player.settings_language)

    auto_battle_active = False
    auto_battle_bar_progress = 0
    time_acc = 0

    shift_held = False  # Shiftキーが押下状態かを記録する
    s_key_held = False
    q_key_held = False
    w_key_held = False
    e_key_held = False
    r_key_held = False
    t_key_held = False
    one_key_held = False
    two_key_held = False
    three_key_held = False
    four_key_held = False
    five_key_held = False
    six_key_held = False
    seven_key_held = False
    eight_key_held = False
    nine_key_held = False
    zero_key_held = False

    last_clicked_slot = None  # 直前にクリックしたスロット(UIImage)を記録する
    character_swap_set = set()

    print("Starting!")
    running = True 

    while running:
        time_delta = clock.tick(60)/1000.0
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                # build_quit_game_window()
                running = False
            # right click to deselect from inventory
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 3:
                for ui_image, rect in player.dict_image_slots_rects.items():
                    if ui_image in player.selected_item.keys():
                        a, b, c = player.selected_item[ui_image]
                        if b:
                            ui_image.set_image(a)
                            player.selected_item[ui_image] = (a, False, c)
                            
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LSHIFT or event.key == pygame.K_RSHIFT:
                    shift_held = True
                if event.key == pygame.K_s:
                    s_key_held = True
                if event.key == pygame.K_q:
                    q_key_held = True
                if event.key == pygame.K_w:
                    w_key_held = True
                if event.key == pygame.K_e:
                    e_key_held = True
                if event.key == pygame.K_r:
                    r_key_held = True
                if event.key == pygame.K_t:
                    t_key_held = True
                if event.key == pygame.K_1:
                    one_key_held = True
                if event.key == pygame.K_2:
                    two_key_held = True
                if event.key == pygame.K_3:
                    three_key_held = True
                if event.key == pygame.K_4:
                    four_key_held = True
                if event.key == pygame.K_5:
                    five_key_held = True
                if event.key == pygame.K_6:
                    six_key_held = True
                if event.key == pygame.K_7:
                    seven_key_held = True
                if event.key == pygame.K_8:
                    eight_key_held = True
                if event.key == pygame.K_9:
                    nine_key_held = True
                if event.key == pygame.K_0:
                    zero_key_held = True

            if event.type == pygame.KEYUP:
                if event.key == pygame.K_LSHIFT or event.key == pygame.K_RSHIFT:
                    shift_held = False
                if event.key == pygame.K_s:
                    s_key_held = False
                if event.key == pygame.K_q:
                    q_key_held = False
                if event.key == pygame.K_w:
                    w_key_held = False
                if event.key == pygame.K_e:
                    e_key_held = False
                if event.key == pygame.K_r:
                    r_key_held = False
                if event.key == pygame.K_t:
                    t_key_held = False
                if event.key == pygame.K_1:
                    one_key_held = False
                if event.key == pygame.K_2:
                    two_key_held = False
                if event.key == pygame.K_3:
                    three_key_held = False
                if event.key == pygame.K_4:
                    four_key_held = False
                if event.key == pygame.K_5:
                    five_key_held = False
                if event.key == pygame.K_6:
                    six_key_held = False
                if event.key == pygame.K_7:
                    seven_key_held = False
                if event.key == pygame.K_8:
                    eight_key_held = False
                if event.key == pygame.K_9:
                    nine_key_held = False
                if event.key == pygame.K_0:
                    zero_key_held = False

            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:

                # character selection and party member swap
                for index, image_slot in enumerate(image_slots_all):
                    if image_slot.rect.collidepoint(event.pos):
                        if s_key_held:
                            update_character_selection_menu(None, di=index)
                        if w_key_held:
                            character_swap_set.add(index)
                            if len(character_swap_set) == 2:
                                swap_characters_in_party(character_swap_set)
                                character_swap_set.clear()

                # item selection from inventory
                clicked_ui_image = None
                for ui_image, rect in player.dict_image_slots_rects.items():
                    if rect.collidepoint(event.pos):
                        clicked_ui_image = ui_image
                        break

                if clicked_ui_image is not None:
                    # Shiftキーなし: 単一選択
                    if not shift_held:
                        # すべての選択解除
                        for sel_ui_image, (orig_img, is_highlighted, item) in player.selected_item.items():
                            if is_highlighted:
                                sel_ui_image.set_image(orig_img)
                        player.selected_item.clear()

                        # 新規選択
                        player.selected_item[clicked_ui_image] = (clicked_ui_image.image, True, player.dict_image_slots_items[clicked_ui_image])
                        clicked_ui_image.set_image(add_outline_to_image(clicked_ui_image.image, (255, 215, 0), 1))
                        last_clicked_slot = clicked_ui_image

                    # Shiftキーあり: 範囲選択
                    else:
                        if last_clicked_slot is None:
                            # 前回クリックがない場合は普通に単体選択扱い
                            player.selected_item[clicked_ui_image] = (clicked_ui_image.image, True, player.dict_image_slots_items[clicked_ui_image])
                            clicked_ui_image.set_image(add_outline_to_image(clicked_ui_image.image, (255, 215, 0), 1))
                            last_clicked_slot = clicked_ui_image
                        else:
                            # last_clicked_slotとclicked_ui_imageの間にあるスロットをまとめて選択
                            all_slots = list(player.dict_image_slots_rects.keys())
                            start_index = all_slots.index(last_clicked_slot)
                            end_index = all_slots.index(clicked_ui_image)

                            # start_index < end_index になるように並べ替え
                            if start_index > end_index:
                                start_index, end_index = end_index, start_index

                            # 範囲内のスロットをすべて選択状態にする
                            for ui_image in all_slots[start_index:end_index+1]:
                                if ui_image not in player.selected_item:
                                    player.selected_item[ui_image] = (ui_image.image, True, player.dict_image_slots_items[ui_image])
                                    ui_image.set_image(add_outline_to_image(ui_image.image, (255, 215, 0), 1))

                            # last_clicked_slotは特に更新しなくてもよいが、必要なら新たなクリックをlastとして記録
                            last_clicked_slot = clicked_ui_image

            if event.type == pygame_gui.UI_BUTTON_PRESSED:
                if event.ui_element == button1: # Shuffle party
                    if cheems_window is not None:
                        cheems_window.kill()
                    text_box.set_text("==============================\n")
                    if current_game_mode == "Training Mode":
                        party1, party2 = set_up_characters()
                    elif current_game_mode == "Adventure Mode":
                        party1, party2 = set_up_characters_adventure_mode(True)
                    turn = 1
                if event.ui_element == next_turn_button:
                    if next_turn(party1, party2):
                        turn += 1
                if event.ui_element == button3:
                    all_turns(party1, party2)
                if event.ui_element == button4: # Restart battle
                    text_box.set_text("==============================\n")
                    restart_battle()
                if event.ui_element == button_quit_game:
                    build_quit_game_window()
                if event.ui_element == button_left_simulate_current_battle:
                    all_turns_simulate_current_battle(party1, party2, selection_simulate_current_battle.selected_option[0])
                if event.ui_element == eq_stars_upgrade_button:
                    eq_stars_upgrade(True)
                # if event.ui_element == character_replace_button:
                #     replace_character_with_reserve_member(character_selection_menu.selected_option[0].split()[-1], reserve_character_selection_menu.selected_option[0].split()[-1])
                if event.ui_element == eq_levelup_button:
                    eq_level_up(amount_to_level=1)
                if event.ui_element == eq_levelup_buttonx10:
                    eq_level_up(amount_to_level=10)
                if event.ui_element == eq_level_up_to_max_button:
                    eq_level_up_to_max()
                if event.ui_element == eq_sell_selected_button:
                    eq_sell_selected()
                if event.ui_element == eq_mass_sell_button:
                    build_eq_sell_window()
                if event.ui_element == eq_sell_window_submit_button:
                    eq_sell_advanced(command=eq_sell_window_command_line.get_text())
                if event.ui_element == button_auto_battle:
                    if auto_battle_active:
                        auto_battle_active = False
                    else:
                        auto_battle_active = True
                if event.ui_element == cheap_inventory_skip_to_first_page_button:
                    player.to_first_page()
                if event.ui_element == cheap_inventory_skip_to_last_page_button:
                    player.to_last_page()
                if event.ui_element == cheap_inventory_previous_page_button:
                    player.to_previous_page()
                if event.ui_element == cheap_inventory_previous_n_button:
                    player.to_previous_page_jump_n(5)
                if event.ui_element == cheap_inventory_next_page_button:
                    player.to_next_page()
                if event.ui_element == cheap_inventory_next_n_button:
                    player.to_next_page_jump_n(5)
                if event.ui_element == use_item_button:
                    use_item()
                if event.ui_element == use_itemx10_button:
                    use_item(10)
                if event.ui_element == item_sell_button:
                    item_sell_selected()
                if event.ui_element == item_sell_half_button:
                    item_sell_half()
                if event.ui_element == item_sell_all_button:
                    item_sell_half(all=True)
                if event.ui_element == character_eq_unequip_button:
                    unequip_item()
                if event.ui_element == character_eq_unequip_all_button:
                    unequip_all_items()
                if event.ui_element == box_submenu_previous_stage_button:
                    adventure_mode_stage_decrease()
                    box_submenu_stage_info_label.set_text(f"Stage {adventure_mode_current_stage}")
                    box_submenu_stage_info_label.set_tooltip(adventure_mode_info_tooltip(), delay=0.1, wrap_width=300)
                    turn = 1
                if event.ui_element == box_submenu_next_stage_button:
                    adventure_mode_stage_increase()
                    box_submenu_stage_info_label.set_text(f"Stage {adventure_mode_current_stage}")
                    box_submenu_stage_info_label.set_tooltip(adventure_mode_info_tooltip(), delay=0.1, wrap_width=300)
                    turn = 1
                if event.ui_element == box_submenu_refresh_stage_button:
                    adventure_mode_stage_refresh()
                    box_submenu_stage_info_label.set_text(f"Stage {adventure_mode_current_stage}")
                    box_submenu_stage_info_label.set_tooltip(adventure_mode_info_tooltip(), delay=0.1, wrap_width=300)
                    turn = 1
                if event.ui_element == box_submenu_enter_shop_button:
                    if not global_vars.player_is_in_shop:
                        text_box.hide()
                        for m in all_shop_ui_modules:
                            m.show()
                        if global_vars.current_shop_instance:
                            the_shop = redraw_ui_shop_edition(reload_shop=False)
                        else:
                            the_shop = redraw_ui_shop_edition()
                    global_vars.player_is_in_shop = True
                if event.ui_element == box_submenu_exit_shop_button:
                    text_box.show()
                    for m in all_shop_ui_modules:
                        m.hide()
                    global_vars.player_is_in_shop = False
                if event.ui_element == shop_refresh_items_button:
                    the_shop = redraw_ui_shop_edition()
                if event.ui_element == shop_item_purchase_buttona:
                    shop_purchase_item(player, the_shop, 0)
                if event.ui_element == shop_item_purchase_buttonb:
                    shop_purchase_item(player, the_shop, 1)
                if event.ui_element == shop_item_purchase_buttonc:
                    shop_purchase_item(player, the_shop, 2)
                if event.ui_element == shop_item_purchase_buttond:
                    shop_purchase_item(player, the_shop, 3)
                if event.ui_element == shop_item_purchase_buttone:
                    shop_purchase_item(player, the_shop, 4)
                if event.ui_element == settings_button:
                    # print(settings_window)
                    # print(settings_window.groups())
                    # settings_window.add(ui_manager.get_sprite_group()) # Does not work
                    # settings_window.show()
                    build_settings_window()
                if event.ui_element == cheap_inventory_sort_filter_button:
                    build_cheap_inventory_sort_filter_window()
                if event.ui_element == cheap_inventory_sort_filter_confirm_button:
                    cheap_inventory_sort()
                if event.ui_element == button_cheems:
                    build_cheems_window()
                if event.ui_element == cheems_update_party_members_button:
                    cheems_edit_party()
                if event.ui_element == cheems_save_party1_button:
                    save_cheems_team(None, 1)
                if event.ui_element == cheems_save_party2_button:
                    save_cheems_team(None, 2)
                if event.ui_element == cheems_apply_to_party1_button:
                    apply_cheems_to_party(1)
                if event.ui_element == cheems_apply_to_party2_button:
                    apply_cheems_to_party(2)
                if event.ui_element == cheems_update_with_party1_button:
                    update_cheems_team(1)
                if event.ui_element == cheems_update_with_party2_button:
                    update_cheems_team(2)
                if event.ui_element == cheems_delete_team_button:
                    delete_cheems_team(cheems_show_player_cheems_selection_menu.selected_option[0])
                if event.ui_element == cheems_rename_team_button:
                    rename_cheems_team(cheems_show_player_cheems_selection_menu.selected_option[0], cheems_rename_teams_entry.get_text())
                if event.ui_element == button_characters:
                    build_character_window()
                if event.ui_element == button_about:
                    build_about_window()

            if event.type == pygame_gui.UI_TEXT_BOX_LINK_CLICKED:
                # print(event.link_target) # Brandon
                # print(event.ui_object_id)
                if event.ui_object_id == "#characters_window.#character_window_command_result_box":
                    if one_key_held:
                        replace_character_with_new(event.link_target, 0)
                    elif two_key_held:
                        replace_character_with_new(event.link_target, 1)
                    elif three_key_held:
                        replace_character_with_new(event.link_target, 2)
                    elif four_key_held:
                        replace_character_with_new(event.link_target, 3)
                    elif five_key_held:
                        replace_character_with_new(event.link_target, 4)

                    elif q_key_held:
                        replace_character_with_new(event.link_target, 5)
                    elif w_key_held:
                        replace_character_with_new(event.link_target, 6)
                    elif e_key_held:
                        replace_character_with_new(event.link_target, 7)
                    elif r_key_held:
                        replace_character_with_new(event.link_target, 8)
                    elif t_key_held:
                        replace_character_with_new(event.link_target, 9)


            if event.type == pygame_gui.UI_DROP_DOWN_MENU_CHANGED:
                if event.ui_element == game_mode_selection_menu:
                    if cheems_window is not None:
                        cheems_window.kill()
                    if game_mode_selection_menu.selected_option[0] == "Training Mode":
                        current_game_mode = "Training Mode"
                        party1, party2 = set_up_characters(reset_party1=False)
                        turn = 1
                        text_box.set_dimensions((556, 295))
                        box_submenu_previous_stage_button.hide()
                        box_submenu_next_stage_button.hide()
                        box_submenu_refresh_stage_button.hide()
                        box_submenu_stage_info_label.hide()
                        box_submenu_enter_shop_button.hide()
                        box_submenu_exit_shop_button.hide()
                        for m in all_shop_ui_modules:
                            m.hide()
                        text_box.show()
                        global_vars.player_is_in_shop = False
                    elif game_mode_selection_menu.selected_option[0] == "Adventure Mode":
                        current_game_mode = "Adventure Mode"
                        party1, party2 = set_up_characters_adventure_mode()
                        turn = 1
                        text_box.set_dimensions((556, 255))
                        box_submenu_previous_stage_button.show()
                        box_submenu_next_stage_button.show()
                        box_submenu_refresh_stage_button.show()
                        box_submenu_stage_info_label.show()
                        box_submenu_stage_info_label.set_text(f"Stage {adventure_mode_current_stage}")
                        box_submenu_stage_info_label.set_tooltip(adventure_mode_info_tooltip(), delay=0.1, wrap_width=300)
                        box_submenu_enter_shop_button.show()
                        box_submenu_exit_shop_button.show()
                if event.ui_element == auto_battle_speed_selection_menu:
                    global_vars.autobattle_speed = auto_battle_speed_selection_menu.selected_option[0]
                if event.ui_element == after_auto_battle_selection_menu:
                    global_vars.after_autobattle = after_auto_battle_selection_menu.selected_option[0]
                # settings_show_battle_chart_selection_menu
                if event.ui_element == settings_show_battle_chart_selection_menu:
                    global_vars.draw_battle_chart = settings_show_battle_chart_selection_menu.selected_option[0]
                    text_box.set_text("==============================\n")
                    restart_battle()
                if event.ui_element == cheap_inventory_sort_a_selection_menu:
                    global_vars.cheap_inventory_sort_a = cheap_inventory_sort_a_selection_menu.selected_option[0]
                if event.ui_element == cheap_inventory_sort_b_selection_menu:
                    global_vars.cheap_inventory_sort_b = cheap_inventory_sort_b_selection_menu.selected_option[0]
                if event.ui_element == cheap_inventory_sort_c_selection_menu:
                    global_vars.cheap_inventory_sort_c = cheap_inventory_sort_c_selection_menu.selected_option[0]
                if event.ui_element == cheap_inventory_filter_have_owner_selection_menu:
                    global_vars.cheap_inventory_filter_have_owner = cheap_inventory_filter_have_owner_selection_menu.selected_option[0]
                if event.ui_element == cheap_inventory_filter_owned_by_char_selection_menu:
                    global_vars.cheap_inventory_filter_owned_by_char = cheap_inventory_filter_owned_by_char_selection_menu.selected_option[0]
                if event.ui_element == cheap_inventory_filter_eqset_selection_menu:
                    global_vars.cheap_inventory_filter_eqset = cheap_inventory_filter_eqset_selection_menu.selected_option[0]
                if event.ui_element == cheap_inventory_filter_type_selection_menu:
                    global_vars.cheap_inventory_filter_type = cheap_inventory_filter_type_selection_menu.selected_option[0]
                if event.ui_element == language_selection_menu:
                    swap_language()
                    try:
                        settings_window.kill()
                    except Exception as e:
                        pass
                if event.ui_element == shop_select_a_shop:
                    the_shop = redraw_ui_shop_edition()
                if event.ui_element == theme_selection_menu:
                    change_theme()
                if event.ui_element == button_change_chart_selection:
                    match button_change_chart_selection.selected_option[0]:
                        # ["Damage Dealt", "Damage Received", "Healing"]
                        case "Damage Dealt":
                            current_display_chart = "Damage Dealt Chart"
                            create_plot_damage_d_chart()
                            draw_chart()
                        case "Damage Received":
                            current_display_chart = "Damage Taken Chart"
                            create_plot_damage_r_chart()
                            draw_chart()
                        case "Healing":
                            current_display_chart = "Healing Chart"
                            create_plot_healing_chart()
                            draw_chart()
                        case _:
                            raise Exception("Unknown option selected in button_change_chart_selection")
                if event.ui_element == cheap_inventory_what_to_show_selection_menu:
                    match cheap_inventory_what_to_show_selection_menu.selected_option[0]:
                        case "Equip":
                            player.current_page = 0
                            global_vars.cheap_inventory_show_current_option = "Equip"
                            player.build_inventory_slots()
                            if global_vars.language == "日本語":
                                use_item_button.set_text("鳳冠霞帔")
                            elif global_vars.language == "English":
                                use_item_button.set_text("Equip Item")
                            eq_selection_menu.show()
                            character_eq_unequip_button.show()
                            character_eq_unequip_all_button.show()
                            eq_levelup_button.show()
                            eq_levelup_buttonx10.show()
                            eq_level_up_to_max_button.show()
                            eq_stars_upgrade_button.show()
                            eq_sell_selected_button.show()
                            eq_mass_sell_button.show()
                            item_sell_button.hide()
                            item_sell_half_button.hide()
                            item_sell_all_button.hide()
                            use_random_consumable_label.hide()
                            use_random_consumable_selection_menu.hide()
                        case "Item":
                            player.current_page = 0
                            global_vars.cheap_inventory_show_current_option = "Item"
                            player.build_inventory_slots()
                            if global_vars.language == "日本語":
                                use_item_button.set_text("使う")
                            elif global_vars.language == "English":
                                use_item_button.set_text("Use Item")
                            eq_selection_menu.hide()
                            character_eq_unequip_button.hide()
                            character_eq_unequip_all_button.hide()
                            eq_levelup_button.hide()
                            eq_levelup_buttonx10.hide()
                            eq_level_up_to_max_button.hide()
                            eq_stars_upgrade_button.hide()
                            eq_sell_selected_button.hide()
                            eq_mass_sell_button.hide()
                            item_sell_button.show()
                            item_sell_half_button.show()
                            item_sell_all_button.show()
                            use_random_consumable_label.hide()
                            use_random_consumable_selection_menu.hide()
                        case "Consumable":
                            player.current_page = 0
                            global_vars.cheap_inventory_show_current_option = "Consumable"
                            player.build_inventory_slots()
                            if global_vars.language == "日本語":
                                use_item_button.set_text("使う")
                            elif global_vars.language == "English":
                                use_item_button.set_text("Use Item")
                            eq_selection_menu.hide()
                            character_eq_unequip_button.hide()
                            character_eq_unequip_all_button.hide()
                            eq_levelup_button.hide()
                            eq_levelup_buttonx10.hide()
                            eq_level_up_to_max_button.hide()
                            eq_stars_upgrade_button.hide()
                            eq_sell_selected_button.hide()
                            eq_mass_sell_button.hide()
                            item_sell_button.show()
                            item_sell_half_button.show()
                            item_sell_all_button.show()
                            use_random_consumable_label.show()
                            use_random_consumable_selection_menu.show()
                        case _:
                            raise Exception("Unknown option selected in cheap_inventory_what_to_show_selection_menu")  
                if event.ui_element == cheems_show_player_cheems_selection_menu:
                    img_slots = [cheems_player_cheems_char_img_slot_a,
                                    cheems_player_cheems_char_img_slot_b,
                                cheems_player_cheems_char_img_slot_c,
                                cheems_player_cheems_char_img_slot_d,
                                cheems_player_cheems_char_img_slot_e,]
                    if cheems_show_player_cheems_selection_menu.selected_option[0] != "None":
                        member_list = player.cheems[cheems_show_player_cheems_selection_menu.selected_option[0]]
                        text = ""
                        for i, m in enumerate(member_list):
                            if m != "***Random***":
                                text += f"{m}    "
                                actual_character = None
                                for c in all_characters:
                                    if c.name == m:
                                        actual_character = c
                                        break
                                try:
                                    img_slots[i].set_image(actual_character.featured_image)
                                except Exception:
                                    img_slots[i].set_image(images_item["404"])
                                finally:
                                    if global_vars.language == "日本語":
                                        img_slots[i].set_tooltip(actual_character.skill_tooltip_jp(), delay=0.1, wrap_width=800)
                                    elif global_vars.language == "English":
                                        img_slots[i].set_tooltip(actual_character.skill_tooltip(), delay=0.1, wrap_width=800)
                            else:
                                text += "Random    "
                                img_slots[i].set_image(images_item["406cheems"])
                                if global_vars.language == "日本語":
                                    img_slots[i].set_tooltip("ランダムに選ばれたキャラクター。", delay=0.1)
                                elif global_vars.language == "English":
                                    img_slots[i].set_tooltip("Randomly selected character.", delay=0.1)

                        cheems_player_cheems_member_label.set_text(text)
                        cheems_apply_to_party1_button.show()
                        cheems_apply_to_party2_button.show()
                        cheems_delete_team_button.show()
                        cheems_update_with_party1_button.show()
                        cheems_update_with_party2_button.show()
                        cheems_rename_teams_entry.show()
                        cheems_rename_team_button.show()
                        cheems_meme_dog_image_slot.hide()
                    else:
                        cheems_player_cheems_member_label.set_text("")
                        for i in img_slots:
                            i.set_image(images_item["405"])
                        cheems_apply_to_party1_button.hide()
                        cheems_apply_to_party2_button.hide()
                        cheems_delete_team_button.hide()
                        cheems_update_with_party1_button.hide()
                        cheems_update_with_party2_button.hide()
                        cheems_rename_teams_entry.hide()
                        cheems_rename_team_button.hide()
                        cheems_meme_dog_image_slot.show()                              


            ui_manager_lower.process_events(event)
            ui_manager.process_events(event)
            ui_manager_overlay.process_events(event)

        ui_manager_lower.update(time_delta)
        ui_manager.update(time_delta)
        ui_manager_overlay.update(time_delta)
        if global_vars.theme == "Yellow Theme":
            display_surface.fill(light_yellow)
        elif global_vars.theme == "Purple Theme":
            display_surface.fill(light_purple)
        elif global_vars.theme == "Red Theme":
            display_surface.fill(light_red)
        elif global_vars.theme == "Green Theme":
            display_surface.fill(light_green)
        elif global_vars.theme == "Blue Theme":
            display_surface.fill(light_blue)
        elif global_vars.theme == "Pink Theme":
            display_surface.fill(light_pink)
        ui_manager_lower.draw_ui(display_surface)
        ui_manager.draw_ui(display_surface)
        ui_manager_overlay.draw_ui(display_surface)
        # debug_ui_manager.update(time_delta)
        # debug_ui_manager.draw_ui(display_surface)

        if auto_battle_active:
            time_acc += time_delta
            auto_battle_bar_progress = (time_acc/decide_auto_battle_speed()) # May impact performance
            if auto_battle_bar_progress > 1.0:
                time_acc = 0.0
                if not next_turn(party1, party2):
                    auto_battle_active = False
                    instruction = global_vars.after_autobattle
                    # print(f"Auto Battle Finished. Instruction: {instruction}")
                    if instruction == "Do Nothing":
                        pass
                    elif instruction == "Restart":
                        text_box.set_text("==============================\n")
                        restart_battle()
                        auto_battle_active = True
                    elif instruction == "Shuffle Party":
                        text_box.set_text("==============================\n")
                        if current_game_mode == "Training Mode":
                            party1, party2 = set_up_characters()
                        elif current_game_mode == "Adventure Mode":
                            party1, party2 = set_up_characters_adventure_mode(True)
                        turn = 1
                        auto_battle_active = True
                    elif instruction == "Next Stage":
                        if current_game_mode == "Training Mode":
                            text_box.set_text("==============================\n")
                            restart_battle()
                        elif current_game_mode == "Adventure Mode":
                            if adventure_mode_stage_increase():
                                box_submenu_stage_info_label.set_text(f"Stage {adventure_mode_current_stage}")
                                box_submenu_stage_info_label.set_tooltip(adventure_mode_info_tooltip(), delay=0.1, wrap_width=300)
                                turn = 1
                            else:
                                restart_battle()
                        auto_battle_active = True
                    else:
                        raise Exception("Unknown Instruction")
                else:
                    turn += 1
            auto_battle_bar.percent_full = auto_battle_bar_progress

        pygame.display.update()

    pygame.quit()
