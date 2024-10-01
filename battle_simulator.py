import inspect
import os, json

import pandas as pd
import analyze
from character import *
import monsters
from item import *
from consumable import *
from calculate_winrate import is_someone_alive, reset_ally_enemy_attr
import shop
import csv
running = False
text_box = None
start_with_max_level = True


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
    player.cash = data["cash"]

    dict_character_name_lvl_exp_equip = {}
    for item_data in data["owned_characters"]:
        dict_character_name_lvl_exp_equip[item_data["name"]] = (item_data["lvl"], item_data["exp"], item_data["equip"])

    for item_data in data["inventory"]:
        match (item_data["object"], item_data["type"]):
            case ("<class 'item.Cash'>", _):
                item = Cash(item_data["current_stack"])
            case ("<class 'item.SliverIngot'>", _):
                item = SliverIngot(item_data["current_stack"])
            case ("<class 'item.GoldIngot'>", _):
                item = GoldIngot(item_data["current_stack"])
            case ("<class 'item.DiamondIngot'>", _):
                item = DiamondIngot(item_data["current_stack"])
            case ("<class 'equip.Equip'>", _):
                item = Equip("foo", "Weapon", "Common")
                for attr, value in item_data.items():
                    if hasattr(item, attr):
                        setattr(item, attr, value)
                item.estimate_market_price()
                item.four_set_effect_description = item.assign_four_set_effect_description()
            case (_, "Food"): 
                item_class = globals().get(item_data['name'])
                if item_class:
                    item = item_class(item_data['current_stack'])
                else:
                    raise ValueError(f"Unknown item type: {item_data['name']}")
            case ("<class 'consumable.EquipPackage'>", _):
                # "object": "<class 'consumable.EquipPackage'>",
                item = EquipPackage(item_data["current_stack"])
            case ("<class 'consumable.EquipPackage2'>", _):
                # "object": "<class 'consumable.EquipPackage'>",
                item = EquipPackage2(item_data["current_stack"])
            case ("<class 'consumable.EquipPackage3'>", _):
                # "object": "<class 'consumable.EquipPackage'>",
                item = EquipPackage3(item_data["current_stack"])
            case ("<class 'consumable.EquipPackage4'>", _):
                # "object": "<class 'consumable.EquipPackage'>",
                item = EquipPackage4(item_data["current_stack"])
            case ("<class 'consumable.EquipPackage5'>", _):
                # "object": "<class 'consumable.EquipPackage'>",
                item = EquipPackage5(item_data["current_stack"])
            case ("<class 'consumable.EquipPackage6'>", _):
                # "object": "<class 'consumable.EquipPackage'>",
                item = EquipPackage6(item_data["current_stack"])
            # FoodPackage
            case ("<class 'consumable.FoodPackage'>", _):
                item = FoodPackage(item_data["current_stack"])
            case ("<class 'consumable.FoodPackage2'>", _):
                item = FoodPackage2(item_data["current_stack"])
            case ("<class 'consumable.FoodPackage3'>", _):
                item = FoodPackage3(item_data["current_stack"])
            case _:
                continue

        player.inventory.append(item)
        player.get_cash()
    player.cleared_stages = data["cleared_stages"]
    return player, dict_character_name_lvl_exp_equip


# =====================================
# End of Helper Functions
# =====================================
# Player Section
# =====================================

class Nine(): # A reference to 9Nine, Nine is just the player's name
    def __init__(self, cash: int, inventory: list=None):
        self.cash = cash 
        self.owned_characters = []
        # We could have multiple types of items in inventory, Equip, Consumable, Item.
        self.inventory = inventory if inventory is not None else []
        self.current_page = 0
        self.max_pages = 0
        self.dict_image_slots_items = {}
        self.dict_image_slots_rects = {}
        # {image_slot: UIImage : (image: Surface, is_highlighted: bool, the_actual_item: Block)}
        self.selected_item: dict[pygame_gui.elements.UIImage, tuple[pygame.Surface, bool, Block]] = {}
        self.cleared_stages = 0

        if cash > 0:
            self.add_cash(cash, False)

    def to_dict(self):
        return {
            "cash": self.cash,
            "owned_characters": [character.to_dict() for character in self.owned_characters],
            "inventory": [item.to_dict() for item in self.inventory],
            "cleared_stages": self.cleared_stages
        }

    def build_inventory_slots(self):
        # TODO: We have commented out the selected_item feature. TEST IT.
        self.selected_item = {}
        page = self.current_page
        try: # I do not think it is the best way to do this.
            only_include = global_vars.cheap_inventory_show_current_option
        except NameError:
            only_include = "Equip"
        match only_include:
            case "Equip":
                filtered_inventory = [x for x in self.inventory if isinstance(x, Equip)]
            case "Consumable":
                filtered_inventory = [x for x in self.inventory if isinstance(x, Consumable)]
                # check if item have flag mark_for_removal, if so, remove it from inventory
                # filtered_inventory = [x for x in filtered_inventory if not x.mark_for_removal]
            case "Item":
                filtered_inventory = [x for x in self.inventory if isinstance(x, Item)]
            case _:
                filtered_inventory = self.inventory
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
            ui_image.set_tooltip(item.print_stats_html(), delay=0.1, wrap_width=300)
        update_inventory_section(self)

    def add_to_inventory(self, item, rebuild_inventory_slots=True):
        if not item:
            raise ValueError("Item is None")
        # Check if the item type is already in the inventory
        if item.can_be_stacked:
            item_added = False
            for inv_item in self.inventory:
                if isinstance(inv_item, type(item)) and not inv_item.is_full():
                    # print(f"Adding {item.current_stack} {item.name} to existing stack...")
                    # Add to the existing stack
                    added_stack = min(item.current_stack, inv_item.max_stack - inv_item.current_stack)
                    inv_item.current_stack += added_stack
                    item.current_stack -= added_stack
                    if item.current_stack == 0:
                        item_added = True
                        break
            # If item still has stack and wasn't added to an existing stack, add it as a new item
            if not item_added and item.current_stack > 0:
                self.inventory.append(item)
        else:
            self.inventory.append(item)
        if rebuild_inventory_slots:
            self.build_inventory_slots()

    def remove_from_inventory(self, item_type, amount_to_remove, rebuild_inventory_slots=True):
        if amount_to_remove <= 0:
            raise ValueError("Amount to remove must be positive")

        removed_count = 0
        # print(f"Removing {amount_to_remove} {item_type.__name__} from inventory...")
        for inv_item in self.inventory.copy():
            if isinstance(inv_item, item_type):
                if inv_item.can_be_stacked:
                    amount_removed = min(amount_to_remove - removed_count, inv_item.current_stack)
                    inv_item.current_stack -= amount_removed
                    removed_count += amount_removed
                    # print(f"Removed {amount_removed} {item_type.__name__} from inventory...")
                    # print(f"Total removed: {removed_count} {item_type.__name__} from inventory...")

                    # Remove the item from inventory if the stack is empty
                    if inv_item.current_stack == 0:
                        self.inventory.remove(inv_item)

                else:
                    self.inventory.remove(inv_item)
                    removed_count += 1

                if removed_count >= amount_to_remove:
                    break

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
                self.inventory.remove(item)
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
                self.remove_from_inventory(type(item), uhmt_fixed, False)
                for i in range(uhmt_fixed):
                    item.E_actual(who_the_character, self)

        if rebuild_inventory_slots:
            self.build_inventory_slots()


    def add_package_of_items_to_inventory(self, package_of_items: list):
        for item in package_of_items:
            self.add_to_inventory(item, False)
        self.build_inventory_slots()

    def sort_inventory_by_rarity(self):
        all_possible_types = ["Weapon", "Armor", "Accessory", "Boots", "None", "Food", "Eqpackage", "Foodpackage"]
        item_sample = Block("Foo", "")
        # Create ordering dictionaries for rarity and types
        rarity_order = dict(mit.zip_equal(item_sample.rarity_list, range(len(item_sample.rarity_list))))
        type_order = dict(mit.zip_equal(all_possible_types, range(len(all_possible_types))))
        # Sort inventory first by rarity, then by type
        self.inventory.sort(key=lambda x: (rarity_order[x.rarity], type_order[x.type]), reverse=False)
        self.current_page = 0
        self.build_inventory_slots()

    def sort_inventory_by_type(self):
        # Certainly a little bit stupid. Every time we add a new type, we have to add it to this list.
        # Faster than dumping Equip to a new list, sort, then dump back to inventory
        # Slower than seperating Equip, Consumable, Item into 3 lists
        all_possible_types = ["Weapon", "Armor", "Accessory", "Boots", "None", "Food", "Eqpackage", "Foodpackage"]
        type_order = dict(mit.zip_equal(all_possible_types, range(len(all_possible_types))))
        self.inventory.sort(key=lambda x: type_order[x.type], reverse=False)
        self.current_page = 0
        self.build_inventory_slots()

    def sort_inventory_by_set(self):
        all_possible_types = ["Weapon", "Armor", "Accessory", "Boots", "None", "Food", "Eqpackage", "Foodpackage"]
        item_sample = Equip("Foo", "Weapon", "Common")
        # Create ordering dictionaries for sets and types
        set_order = dict(mit.zip_equal(item_sample.eq_set_list, range(len(item_sample.eq_set_list))))
        type_order = dict(mit.zip_equal(all_possible_types, range(len(all_possible_types))))
        # Sort inventory first by set, then by type
        self.inventory.sort(key=lambda x: (set_order[x.eq_set], type_order[x.type]), reverse=False)
        self.current_page = 0
        self.build_inventory_slots()

    def sort_inventory_by_level(self):
        self.inventory.sort(key=lambda x: x.level, reverse=True)
        self.current_page = 0
        self.build_inventory_slots()

    def sort_inventory_by_market_value(self):
        self.inventory.sort(key=lambda x: x.market_value, reverse=True)
        self.current_page = 0
        self.build_inventory_slots()

    def sort_inventory_bogo(self):
        # just a shuffle
        random.shuffle(self.inventory)
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

    def get_cash(self):
        self.cash = 0
        for item in self.inventory:
            if isinstance(item, Cash):
                self.cash += item.current_stack
        return self.cash

    def add_cash(self, amount: int, rebuild_inventory_slots: bool = True):
        if amount <= 0:
            if amount == 0:
                return
            else:
                raise ValueError("Amount must be positive")

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
        try:
            set_currency_on_icon_and_label(self, the_shop.currency, shop_player_owned_currency, shop_player_owned_currency_icon)
        except NameError:
            pass

    def get_currency(self, currency: str):
        if currency == "Cash" or "cash":
            return self.get_cash()
        else:
            c = 0
            for item in self.inventory:
                if item.__class__.__name__ == currency or item.__class__.__name__.lower() == currency:
                    c += item.current_stack
            return c


# =====================================
# End of Player Section
# =====================================
# Character Creation Section
# =====================================

def get_all_characters():
    global start_with_max_level
    character_names = ["Cerberus", "Fenrir", "Clover", "Ruby", "Olive", "Luna", "Freya", "Poppy", "Lillia", "Iris",
                       "Pepper", "Cliffe", "Pheonix", "Bell", "Taily", "Seth", "Ophelia", "Chiffon", "Requina", "Gabe", 
                       "Yuri", "Dophine", "Tian", "Don", "Cate", "Roseiri", "Fox", "Season", "Air", "Raven", "April",
                       "Nata", "Chei", "Cocoa", "Beacon"]

    if start_with_max_level:
        all_characters = [eval(f"{name}('{name}', 1000)") for name in character_names]
    else:
        all_characters = [eval(f"{name}('{name}', 1)") for name in character_names]
    return all_characters

all_characters = get_all_characters()
all_monsters = [cls(name, 1) for name, cls in monsters.__dict__.items() 
                if inspect.isclass(cls) and issubclass(cls, Character) and cls != Character]






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
    light_pink = pygame.Color("#fae5fa")

    display_surface = pygame.display.set_mode((1600, 900), flags=pygame.SCALED)
    ui_manager = pygame_gui.UIManager((1600, 900), "theme_light_yellow.json", starting_language='ja')
    # debug_ui_manager = pygame_gui.UIManager((1600, 900), "theme_light_yellow.json", starting_language='ja')
    # ui_manager.get_theme().load_theme("theme_light_purple.json")
    # ui_manager.rebuild_all_from_changed_theme_data()

    pygame.display.set_caption("Battle Simulator")

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
    

    # Some buttons
    #  =====================================
    # Left Side

    button1 = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((100, 300), (156, 50)),
                                        text='Shuffle Party',
                                        manager=ui_manager,
                                        tool_tip_text = "Shuffle party and restart the battle")
    button1.set_tooltip("Shuffle the party and restart battle.", delay=0.1, wrap_width=300)

    button4 = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((100, 360), (156, 50)),
                                        text='Restart Battle',
                                        manager=ui_manager,
                                        tool_tip_text = "Restart battle")
    button4.set_tooltip("Restart battle.", delay=0.1)

    button3 = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((100, 420), (156, 50)),
                                        text='All Turns',
                                        manager=ui_manager,
                                        tool_tip_text = "Skip to the end of the battle.")
    button3.set_tooltip("Skip to the end of the battle but no reward.", delay=0.1, wrap_width=300)

    # button_left_clear_board = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((100, 480), (156, 50)),
    #                                     text='Clear Board',
    #                                     manager=ui_manager,
    #                                     tool_tip_text = "Remove all text from the text box, text box will be slower if there are too many text.")
    # button_left_clear_board.set_tooltip("Remove all text from the text box, text box will be slower if there are too many text.", delay=0.1, wrap_width=300)

    current_display_chart = "Damage Dealt Chart"
    button_left_change_chart = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((100, 480), (156, 50)),
                                        text='Switch Chart',
                                        manager=ui_manager,
                                        tool_tip_text = "")
    button_left_change_chart.set_tooltip(f"Switch between damage dealt chart, damage received chart or others if implemented. Current chart: {current_display_chart}", delay=0.1, wrap_width=300)

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
    next_turn_button_tooltip_str = "Next turn. Experience and cash will be earned if the battle is won in adventure mode."
    next_turn_button_tooltip_str += "If the stage level is higher than the average party level, the reward will increase."
    next_turn_button.set_tooltip(next_turn_button_tooltip_str, delay=0.1, wrap_width=300)

    button_auto_battle = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((1080, 300), (156, 50)),
                                        text='Auto',
                                        manager=ui_manager,
                                        tool_tip_text = "Auto battle")
    button_auto_battle.set_tooltip("Automatically proceed to the next turn when the progress bar is full. Rewards are earned when the battle is over.", delay=0.1, wrap_width=300)


    auto_battle_bar = pygame_gui.elements.UIStatusBar(pygame.Rect((1080, 290), (156, 10)),
                                               ui_manager,
                                               None)

    # If these options are changed, make sure to change the corresponding functions by searching for the function name
    auto_battle_speed_selection_menu = pygame_gui.elements.UIDropDownMenu(["Veryslow", "Slow", "Normal", "Fast", "Veryfast"],
                                                            "Normal",
                                                            pygame.Rect((1080, 260), (156, 35)),
                                                            ui_manager)

    auto_battle_speed_label = pygame_gui.elements.UILabel(pygame.Rect((1080, 220), (156, 35)),
                                        "Autobattle Speed: ",
                                        ui_manager)

    after_auto_battle_selection_menu = pygame_gui.elements.UIDropDownMenu(["Do Nothing", "Restart", "Shuffle Party", "Next Stage"],
                                                            "Do Nothing",
                                                            pygame.Rect((1080, 180), (156, 35)),
                                                            ui_manager)

    after_auto_battle_label = pygame_gui.elements.UILabel(pygame.Rect((1080, 140), (156, 35)),
                                        "After Autobattle: ",
                                        ui_manager)

    def decide_auto_battle_speed():
        speed = auto_battle_speed_selection_menu.selected_option[0]
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
    # Game Mode Section
    # =====================================

    current_game_mode = "Training Mode"
    switch_game_mode_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((1080, 360), (156, 50)),
                                        text='Adventure Mode',
                                        manager=ui_manager,
                                        tool_tip_text = "Switch between Casual Training Mode and Adventure Mode")
    switch_game_mode_button.set_tooltip("Switch between adventure mode and training mode.", delay=0.1, wrap_width=300)

    def adventure_mode_generate_stage():
        global current_game_mode, adventure_mode_current_stage, adventure_mode_stages
        for m in all_monsters:
            m.lvl = adventure_mode_current_stage
        # Boss monsters have attribute is_boss = True, every 10 stages, starting from stage 10, summon a boss monster
        # Stage 1000 to 2400, every stage has a boss monster in the middle of the stage.
        # Howerver, on stage 2400 and later, there will be no restriction on whether boss or not.
        if (adventure_mode_current_stage % 10 == 0 or adventure_mode_current_stage > 1000) and adventure_mode_current_stage < 2400:
            new_selection_of_monsters = random.sample([x for x in all_monsters if not x.is_boss], k=4)
            boss_monster = random.choice([x for x in all_monsters if x.is_boss])
            new_selection_of_monsters.insert(2, boss_monster)
        elif adventure_mode_current_stage >= 2400:
            new_selection_of_monsters = random.sample(all_monsters, k=5)
        else:
            new_selection_of_monsters = random.sample([x for x in all_monsters if not x.is_boss], k=5)
        if not adventure_mode_stages.get(adventure_mode_current_stage):
            adventure_mode_stages[adventure_mode_current_stage] = new_selection_of_monsters
        # if adventure_mode_current_stage > 1000:
        if adventure_mode_current_stage < 500:
            for m in adventure_mode_stages[adventure_mode_current_stage]:
                m.equip_item_from_list(generate_equips_list(4, locked_eq_set="Void", include_void=True, locked_rarity="Common", 
                                                            eq_level=int(adventure_mode_current_stage)))
        elif 500 <= adventure_mode_current_stage < 1000:
            for m in adventure_mode_stages[adventure_mode_current_stage]:
                m.equip_item_from_list(generate_equips_list(4, locked_eq_set="Void", include_void=True, locked_rarity="Uncommon", 
                                                            eq_level=int(adventure_mode_current_stage)))
        elif 1000 <= adventure_mode_current_stage < 1500:
            for m in adventure_mode_stages[adventure_mode_current_stage]:
                m.equip_item_from_list(generate_equips_list(4, locked_eq_set="Void", include_void=True, locked_rarity="Rare", 
                                                            eq_level=int(adventure_mode_current_stage)))
        elif 1500 <= adventure_mode_current_stage < 2000:
            for m in adventure_mode_stages[adventure_mode_current_stage]:
                m.equip_item_from_list(generate_equips_list(4, locked_eq_set="Void", include_void=True, locked_rarity="Epic", 
                                                            eq_level=int(adventure_mode_current_stage)))
        elif 2000 <= adventure_mode_current_stage:
            for m in adventure_mode_stages[adventure_mode_current_stage]:
                m.equip_item_from_list(generate_equips_list(4, locked_eq_set="Void", include_void=True, locked_rarity="Unique", 
                                                            eq_level=int(adventure_mode_current_stage)))

    def adventure_mode_stage_increase():
        global current_game_mode, adventure_mode_current_stage
        if current_game_mode == "Training Mode":
            raise Exception("Cannot change stage in Training Mode. See Game Mode Section.")
        if adventure_mode_current_stage == 2500:
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


    def adventure_mode_exp_reward():
        global adventure_mode_current_stage, party1
        average_party_level = sum([x.lvl for x in party1]) / 5
        enemy_average_level = adventure_mode_current_stage
        # if enemy level is above average party level, then exp reward is increased by a percentage
        exp_reward_multiplier = 1
        if enemy_average_level > average_party_level:
            exp_reward_multiplier = (enemy_average_level / average_party_level)
        if adventure_mode_current_stage % 10 == 0 or adventure_mode_current_stage > 1000: # boss stage
            exp_reward_multiplier *= 1.5
        return int(adventure_mode_current_stage * exp_reward_multiplier)

    def adventure_mode_cash_reward():
        global adventure_mode_current_stage, party1
        average_party_level = sum([x.lvl for x in party1]) / 5
        enemy_average_level = adventure_mode_current_stage
        cash_reward_multiplier = 1
        if enemy_average_level > average_party_level:
            cash_reward_multiplier = (enemy_average_level / average_party_level)
        random_factor = random.uniform(0.8, 1.2)
        cash_before_random = adventure_mode_current_stage * 2 * cash_reward_multiplier
        cash = cash_before_random * random_factor
        if adventure_mode_current_stage % 10 == 0 or adventure_mode_current_stage > 1000: # boss stage
            cash *= 1.5
            cash_before_random *= 1.5
        cash = max(1, cash)
        return int(cash), int(cash_before_random)
    
    def adventure_mode_info_tooltip() -> str:
        global adventure_mode_current_stage
        str = f"Current Stage: {adventure_mode_current_stage}\n"
        if adventure_mode_current_stage > sum([x.lvl for x in party1]) / 5:
            str += f"Enemy level is higher than average party level, reward is increased by {(adventure_mode_current_stage / (sum([x.lvl for x in party1]) / 5) - 1) * 100:.2f}%\n"
        if adventure_mode_current_stage % 10 == 0 or adventure_mode_current_stage > 1000: # boss stage
            str += "Boss Stage. Reward is increased by 50%.\n"
        str += f"Exp Reward: {adventure_mode_exp_reward()}\n"
        a, b = adventure_mode_cash_reward()
        str += f"Cash Reward: approxmately {b}\n"
        return str

    # =====================================
    # End of Game Mode Section
    # =====================================
    # Character Section
    # =====================================

    character_selection_menu = pygame_gui.elements.UIDropDownMenu(["Option 1", "Option 2", "Option 3", "Option 4", "Option 5"],
                                                            "Option 1",
                                                            pygame.Rect((900, 360), (156, 35)),
                                                            ui_manager)

    label_character_selection_menu = pygame_gui.elements.UILabel(pygame.Rect((870, 360), (25, 35)),
                                        "→",
                                        ui_manager)
    label_character_selection_menu.set_tooltip("Selected character. You can also select a character by clicking on the character image.", delay=0.1)

    reserve_character_selection_menu = pygame_gui.elements.UIDropDownMenu(["Option1"],
                                                            "Option1",
                                                            pygame.Rect((900, 400), (156, 35)),
                                                            ui_manager)

    label_reserve_character_selection_menu = pygame_gui.elements.UILabel(pygame.Rect((870, 400), (25, 35)),
                                        "→",
                                        ui_manager)
    label_reserve_character_selection_menu.set_tooltip("The reserve members, sorted by character level.", delay=0.1)

    character_replace_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((900, 440), (156, 35)),
                                        text='Replace',
                                        manager=ui_manager,
                                        tool_tip_text = "Replace selected character with reserve character")
    character_replace_button.set_tooltip("Replace the selected character with a reserve member.", delay=0.1, wrap_width=300)

    use_item_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((900, 480), (100, 35)),
                                        text='Equip Item',
                                        manager=ui_manager,
                                        tool_tip_text = "Use selected item for selected character.")
    use_item_button.set_tooltip("The selected item is used on the selected character. If the selected item is an equipment item, equip it to the selected character. Multiple items may be equipped or used at one time.",
                                delay=0.1, wrap_width=300)
    use_itemx10_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((1005, 480), (51, 35)),
                                        text='x10',
                                        manager=ui_manager,
                                        tool_tip_text = "Use selected item 10 times.")
    use_itemx10_button.set_tooltip("Use selected item 10 times, only effective on comsumables.", delay=0.1, wrap_width=300)

    item_sell_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((900, 520), (156, 35)),
                                        text='Sell Item',
                                        manager=ui_manager,
                                        tool_tip_text = "Sell selected item in inventory.")
    item_sell_button.set_tooltip("Sell one selected item from your inventory.", delay=0.1, wrap_width=300)
    item_sell_button.hide()
    item_sell_half_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((900, 560), (100, 35)),
                                        text='Sell Half',
                                        manager=ui_manager,
                                        tool_tip_text = "Sell half stack of selected item in inventory.")
    item_sell_half_button.set_tooltip("Sell half a stack of selected items.", delay=0.1, wrap_width=300)
    item_sell_half_button.hide()
    item_sell_all_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((1005, 560), (51, 35)),
                                        text='All',
                                        manager=ui_manager,
                                        tool_tip_text = "Sell all of selected item in inventory.")
    item_sell_all_button.set_tooltip("Sell all of selected items.", delay=0.1, wrap_width=300)
    item_sell_all_button.hide()
    use_random_consumable_label = pygame_gui.elements.UILabel(pygame.Rect((1080, 420), (156, 35)),
                                        "Random Use:",
                                        ui_manager)
    use_random_consumable_label.set_tooltip("Use one appropriate consumable each turn during auto battles.", delay=0.1, wrap_width=300)
    use_random_consumable_label.hide()
    use_random_consumable_selection_menu = pygame_gui.elements.UIDropDownMenu(["True", "False"],
                                                            "False",
                                                            pygame.Rect((1080, 460), (156, 35)),
                                                            ui_manager)
    use_random_consumable_selection_menu.hide()


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
            all_consumables = [x for x in player.inventory if isinstance(x, Consumable) and x.can_use_for_auto_battle]
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
            player.remove_from_inventory(type(item_to_sell), amount_to_sell, False)
        
        text_box.append_html_text(f"Total income: {total_income} cash.\n")
        player.add_cash(total_income, True)


    # def item_trade(item: str, amount: int=1):
    #     text_box.set_text("==============================\n")
    #     match item:
    #         case "Sliver Ingot":
    #             if player.get_cash() < 111000 * amount:
    #                 text_box.append_html_text(f"Not enough cash to buy {amount} Sliver Ingot.\n")
    #                 return
    #             player.add_to_inventory(SliverIngot(amount), False)
    #             player.lose_cash(111000 * amount, True)
    #             text_box.append_html_text(f"Bought {amount} Sliver Ingot for {111000 * amount} cash.\n")
    #         case "Gold Ingot":
    #             if player.get_cash() < 9820000 * amount:
    #                 text_box.append_html_text(f"Not enough cash to buy {amount} Gold Ingot.\n")
    #                 return
    #             player.add_to_inventory(GoldIngot(amount), False)
    #             player.lose_cash(9820000 * amount, True)
    #             text_box.append_html_text(f"Bought {amount} Gold Ingot for {9820000 * amount} cash.\n")
    #         case _:
    #             raise ValueError(f"Invalid item: {item}")

    def buy_one_item(player: Nine, item: Block, item_price: int) -> None:
        if player.get_cash() < item_price:
            print(f"Not enough cash to buy {item.name}.")
            return
        player.add_to_inventory(item, False)
        player.lose_cash(item_price, True)
        text_box.set_text(f"Bought {item.name} for {item_price} cash.\n")
        save_player(player)
        return


    # =====================================
    # End of Character Section
    # =====================================
    # Debug Section
    # =====================================



    # =====================================
    # End of Debug Section
    # =====================================
    # Equip Section
    # =====================================

    eq_rarity_list, eq_types_list, eq_set_list = Equip("Foo", "Weapon", "Common").get_raritytypeeqset_list()

    eq_selection_menu = pygame_gui.elements.UIDropDownMenu(eq_types_list,
                                                            eq_types_list[0],
                                                            pygame.Rect((900, 520), (156, 35)),
                                                            ui_manager)

    character_eq_unequip_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((900, 560), (156, 35)),
                                        text='Unequip',
                                        manager=ui_manager,
                                        tool_tip_text = "Unequip selected item from selected character")
    character_eq_unequip_button.set_tooltip("Remove equipment from the selected character.", delay=0.1, wrap_width=300)

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


    eq_stars_upgrade_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((1080, 420), (156, 35)),
                                        text='Star Enhancement',
                                        manager=ui_manager,
                                        tool_tip_text = "Upgrade stars for item")
    eq_stars_upgrade_button.set_tooltip("Increase the star rank of selected equipment in inventory.", delay=0.1, wrap_width=300)

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
        if player.get_cash() < cost_total:
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
                    k.set_tooltip(item_to_upgrade.print_stats_html(), delay=0.1, wrap_width=300)
        if cost_total > 0:
            player.lose_cash(cost_total, False)
            text_box_text_to_append += f"Upgraded {len(selected_items)} items for {cost_total} cash.\n"
        text_box.append_html_text(text_box_text_to_append)

    eq_levelup_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((1080, 460), (100, 35)),
                                        text='Level Up',
                                        manager=ui_manager,
                                        tool_tip_text = "Level up selected item.")
    eq_levelup_button.set_tooltip("Level up selected equipment in the inventory.", delay=0.1, wrap_width=300)

    eq_levelup_buttonx10 = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((1185, 460), (51, 35)),
                                        text='x10',
                                        manager=ui_manager,
                                        tool_tip_text = "Level up selected item.")
    eq_levelup_buttonx10.set_tooltip("Level up for 10 levels for selected equipment in the inventory.", delay=0.1, wrap_width=300)


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
        if player.get_cash() < cost_total:
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
                    k.set_tooltip(item_to_level_up.print_stats_html(), delay=0.1, wrap_width=300)
        if cost_total > 0:
            player.lose_cash(cost_total, False)
            text_box_text_to_append += f"Leveled {len(selected_items)} items for {cost_total} cash.\n"
        text_box.append_html_text(text_box_text_to_append)


    
    eq_sell_selected_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((1080, 500), (156, 35)),
                                        text='Sell Selected',
                                        manager=ui_manager,
                                        tool_tip_text = "Sell selected item.")
    eq_sell_selected_button.set_tooltip("Sell selected equipment in the inventory.", delay=0.1, wrap_width=300)

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

    eq_sell_low_value_selection_menu = pygame_gui.elements.UIDropDownMenu(["50", "60", "70", "80", "90", "100", "200", "500", "1000", "2000", "3000", "4000", "5000"],
                                                            "50",
                                                            pygame.Rect((1080, 540), (156, 35)),
                                                            ui_manager)


    eq_sell_low_value_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((1080, 580), (156, 35)),
                                        text='Sell Low Value',
                                        manager=ui_manager,
                                        tool_tip_text = "Sell all equipment that is below the selected market value.")
    eq_sell_low_value_button.set_tooltip("Sell equipment in inventory that is below market value.", delay=0.1, wrap_width=300)


    def eq_sell_low_value(sell_value_below: int):
        # sell half of all equipment, sorted by market value
        text_box.set_text("==============================\n")
        eq_to_sell = [x for x in player.inventory if isinstance(x, Equip) and x.market_value <= sell_value_below]
        total_income = 0
        if not eq_to_sell:
            text_box.append_html_text(f"No equipment below market value {sell_value_below} to sell.\n")
            return
        for eq in eq_to_sell.copy():
            total_income += int(eq.market_value)
            player.inventory.remove(eq)
        player.add_cash(total_income, False)
        text_box.append_html_text(f"Sold {len(eq_to_sell)} equipment for {total_income} cash.\n")
        player.build_inventory_slots()


    eq_level_up_to_max_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((1080, 620), (156, 35)),
                                        text='Level Up To Max',
                                        manager=ui_manager,
                                        tool_tip_text = "Try level up selected item to max level until Cash is exhausted.")
    eq_level_up_to_max_button.set_tooltip("Level up selected equipment in the inventory to the maximum level.", delay=0.1, wrap_width=300)

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
            available_cash = player.get_cash()
            remaining_funds, cost = item_to_level_up.level_up_as_possible(available_cash)
            if cost:
                player.lose_cash(cost, False)
                text_box.append_html_text(f"Leveled up {item_to_level_up} in inventory for {cost} cash.\n")
            else:
                text_box.append_html_text(f"Cannot level up {item_to_level_up} in inventory.\n")
            for k, (a, b, c) in player.selected_item.items():
                if c == item_to_level_up:
                    k.set_tooltip(item_to_level_up.print_stats_html(), delay=0.1, wrap_width=300)




    # =====================================
    # End of Equip Section
    # =====================================
    # Theme Selection
    # =====================================


    theme_selection_menu = pygame_gui.elements.UIDropDownMenu(["Yellow Theme", "Purple Theme", "Red Theme", "Blue Theme", "Green Theme", "Pink Theme"],
                                                            "Yellow Theme",
                                                            pygame.Rect((1080, 20), (156, 35)),
                                                            ui_manager)

    def change_theme():
        global_vars.theme = theme_selection_menu.selected_option[0]
        if global_vars.theme == "Yellow Theme":
            ui_manager.get_theme().load_theme("theme_light_yellow.json")
        elif global_vars.theme == "Purple Theme":
            ui_manager.get_theme().load_theme("theme_light_purple.json")
        elif global_vars.theme == "Red Theme":
            ui_manager.get_theme().load_theme("theme_light_red.json")
        elif global_vars.theme == "Blue Theme":
            ui_manager.get_theme().load_theme("theme_light_blue.json")
        elif global_vars.theme == "Green Theme":
            ui_manager.get_theme().load_theme("theme_light_green.json")
        elif global_vars.theme == "Pink Theme":
            ui_manager.get_theme().load_theme("theme_light_pink.json")
        else:
            raise ValueError(f"Unknown theme: {global_vars.theme}")
        
        ui_manager.rebuild_all_from_changed_theme_data()
        redraw_ui(party1, party2)
        player.build_inventory_slots()
        if global_vars.player_is_in_shop:
            redraw_ui_shop_edition()
    # =====================================
    # End of Theme Selection
    # =====================================
    # Cheap Inventory Section
    # =====================================

    # Cheap inventory system is just a bunch of 32 by 32 image slots pointing to player's inventory
    # 10 rows, 6 columns
    # each row and column have a empty space of 8 pixels

    cheap_inventory_what_to_show_label = pygame_gui.elements.UILabel(pygame.Rect((1080, 60), (156, 35)),
                                        "Inventory:",
                                        ui_manager)

    cheap_inventory_what_to_show_selection_menu = pygame_gui.elements.UIDropDownMenu(["Equip", "Consumable", "Item"],
                                                            "Equip",
                                                            pygame.Rect((1080, 100), (156, 35)),
                                                            ui_manager)

    cheap_inventory_sort_by_selection_menu = pygame_gui.elements.UIDropDownMenu(["Rarity", "Type", "Set", "Level", "Market Value", "BOGO"],
                                                            "Rarity",
                                                            pygame.Rect((1300, 20), (230, 35)),
                                                            ui_manager)

    cheap_inventory_sort_by_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((1300, 60), (230, 35)),
                                        text='Sort',
                                        manager=ui_manager,
                                        tool_tip_text = "Sort inventory by selected option")
    cheap_inventory_sort_by_button.set_tooltip("Sort inventory by selected option.", delay=0.1, wrap_width=300)

    def cheap_inventory_sort():
        match cheap_inventory_sort_by_selection_menu.selected_option[0]:
            case "Rarity":
                player.sort_inventory_by_rarity()
            case "Type":
                player.sort_inventory_by_type()
            case "Set":
                player.sort_inventory_by_set()
            case "Level":
                player.sort_inventory_by_level()
            case "Market Value":
                player.sort_inventory_by_market_value()
            case "BOGO":
                player.sort_inventory_bogo()
            case _:
                print(f"Warning: Unknown option: {cheap_inventory_sort_by_selection_menu.selected_option[0]}")


    cheap_inventory_cheap_label = pygame_gui.elements.UILabel(pygame.Rect((1372, 100), (72, 35)),
                                                              "Inventory",
                                                              ui_manager)

    cheap_inventory_page_label = pygame_gui.elements.UILabel(pygame.Rect((1372, 140), (72, 35)),
                                        "1/1",
                                        ui_manager)
    cheap_inventory_cheap_label.set_tooltip("ページ/最大ページ", delay=0.1)

    cheap_inventory_skip_to_first_page_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((1300, 140), (50, 35)),
                                        text='<<',
                                        manager=ui_manager,
                                        tool_tip_text = "Skip to first page of inventory")
    cheap_inventory_skip_to_first_page_button.set_tooltip("Jump to first page of inventory.", delay=0.1, wrap_width=300)
    cheap_inventory_previous_page_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((1300, 100), (50, 35)),
                                        text='<',
                                        manager=ui_manager,
                                        tool_tip_text = "Previous page of inventory")
    cheap_inventory_previous_page_button.set_tooltip("Previous page of inventory.", delay=0.1, wrap_width=300)
    cheap_inventory_skip_to_last_page_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((1480, 140), (50, 35)),
                                        text='>>',
                                        manager=ui_manager,
                                        tool_tip_text = "Skip to last page of inventory")
    cheap_inventory_skip_to_last_page_button.set_tooltip("Jump to last page of inventory.", delay=0.1, wrap_width=300)
    cheap_inventory_next_page_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((1480, 100), (50, 35)),
                                        text='>',
                                        manager=ui_manager,
                                        tool_tip_text = "Next page of inventory")
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
        return gutted_inventory_image_slots, dict_image_slots_rects

    inventory_image_slots = create_inventory_image_slots(24, 1278, 196, 64, 64, 8, ui_manager, column=4)
    show_n_slots_of_inventory_image_slots(0)

    def update_inventory_section(player):
        cheap_inventory_page_label.set_text(f"{player.current_page + 1}/{player.max_pages + 1}")

    # =====================================
    # End of Cheap Inventory Section
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
        weight = [x.spd for x in alive_characters]
        the_chosen_one = random.choices(alive_characters, weights=weight, k=1)[0]
        global_vars.turn_info_string += f"{the_chosen_one.name}'s turn.\n"
        the_chosen_one.action()

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

        # print(shield_value_diff)
        # {'Seth': 0, 'Air': 0, 'Yuri': 0, 'Lillia': 0, 'Cocoa': 0, 'Freya': 0, 'Fox': 0, 'Gabe': 0, 'Chei': 0, 'Luna': 0}

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


    def all_turns(party1: list[Character], party2: list[Character]):
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
            weight = [x.spd for x in alive_characters]
            the_chosen_one = random.choices(alive_characters, weights=weight, k=1)[0]
            the_chosen_one.action()

            for character in itertools.chain(party1, party2):
                character.status_effects_at_end_of_turn()

            for character in itertools.chain(party1, party2):
                character.record_damage_taken()
                character.record_healing_received()

            for character in itertools.chain(party1, party2):
                character.status_effects_after_damage_record()

            turn += 1

        create_tmp_damage_data_csv(party1, party2)
        create_healing_data_csv(party1, party2)
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
        global turn, auto_battle_active
        global_vars.turn_info_string = ""
        for character in all_characters + all_monsters:
            character.reset_stats()
        reset_ally_enemy_attr(party1, party2)
        global_vars.turn_info_string += "Battle entry effects:\n"
        for character in party1:
            character.battle_entry_effects_activate()
        for character in party2:
            character.battle_entry_effects_activate()
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


    def handle_UIDropDownMenu(party_show_in_menu, remaining_characters_show_in_menu, di=0):
        """
        remaining_characters_show_in_menu: Can be None, if so, it is not being rebuilt
        di: Default option index
        """
        global character_selection_menu, reserve_character_selection_menu, ui_manager

        character_selection_menu.kill()
        character_selection_menu = pygame_gui.elements.UIDropDownMenu(party_show_in_menu,
                                                                party_show_in_menu[di],
                                                                pygame.Rect((900, 360), (156, 35)),
                                                                ui_manager)

        if remaining_characters_show_in_menu:
            reserve_character_selection_menu.kill()
            reserve_character_selection_menu = pygame_gui.elements.UIDropDownMenu(remaining_characters_show_in_menu,
                                                                    remaining_characters_show_in_menu[0],
                                                                    pygame.Rect((900, 400), (156, 35)),
                                                                    ui_manager)

    def set_up_characters(is_start_of_app=False):
        global character_selection_menu, reserve_character_selection_menu, all_characters, party2, party1, text_box
        if not is_start_of_app:
            text_box.set_text("==============================\n")
        for character in all_characters:
            character.reset_stats()
        party1 = []
        party2 = []
        list_of_characters = random.sample(all_characters, 10)
        remaining_characters = [character for character in all_characters if character not in list_of_characters]
        remaining_characters.sort(key=lambda x: x.lvl, reverse=True)
        random.shuffle(list_of_characters)
        party1 = list_of_characters[:5]
        party2 = list_of_characters[5:]

        party_show_in_menu = [f" Lv.{character.lvl} {character.name}" for character in itertools.chain(party1, party2)]
        remaining_characters_show_in_menu = [f" Lv.{character.lvl} {character.name}" for character in remaining_characters]
        handle_UIDropDownMenu(party_show_in_menu, remaining_characters_show_in_menu)

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
        remaining_characters_show_in_menu = [f" Lv.{character.lvl} {character.name}" for character in remaining_characters]
        handle_UIDropDownMenu(party1_show_in_menu, remaining_characters_show_in_menu)

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


    def replace_character_with_reserve_member(character_name, new_character_name):
        global party1, party2, all_characters, character_selection_menu, reserve_character_selection_menu, current_game_mode
        def replace_in_party(party):
            for i, character in enumerate(party):
                if character.name == character_name:
                    new_character = next((char for char in all_characters if char.name == new_character_name), None)
                    if new_character:
                        party[i] = new_character
                        return True, new_character, i
            return False, None, 0
        replaced, new_character, nci = replace_in_party(party1)
        if not replaced:
            replaced, new_character, nci = replace_in_party(party2)
            nci += len(party1) # New character index
        if current_game_mode == "Adventure Mode":
            remaining_characters = [character for character in all_characters if character not in party1]
            remaining_characters.sort(key=lambda x: x.lvl, reverse=True)
            party1_show_in_menu = [f" Lv.{character.lvl} {character.name}" for character in party1]
            remaining_characters_show_in_menu = [f" Lv.{character.lvl} {character.name}" for character in remaining_characters]

            handle_UIDropDownMenu(party1_show_in_menu, remaining_characters_show_in_menu, nci)
        elif current_game_mode == "Training Mode":
            remaining_characters = [character for character in all_characters if character not in itertools.chain(party1, party2)]
            remaining_characters.sort(key=lambda x: x.lvl, reverse=True)
            party_show_in_menu = [f" Lv.{character.lvl} {character.name}" for character in itertools.chain(party1, party2)]
            remaining_characters_show_in_menu = [f" Lv.{character.lvl} {character.name}" for character in remaining_characters]
            handle_UIDropDownMenu(party_show_in_menu, remaining_characters_show_in_menu, nci)
        else:
            raise Exception(f"Unknown game mode: {current_game_mode} in replace_character_with_reserve_member()")
        reset_ally_enemy_attr(party1, party2)
        new_character.battle_entry_effects_activate()
        redraw_ui(party1, party2)
        text_box.append_html_text(f"{character_name} has been replaced with {new_character_name}.\n")

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
                    color_filled_bar = (255, 193, 7)
                    shield_bar_color = (252, 248, 15)
                case "Purple Theme":
                    color_unfilled_bar = (248, 231, 255)
                    color_filled_bar = (236, 192, 255)
                    shield_bar_color = (198,153,255)
                case "Blue Theme":
                    color_unfilled_bar = (220, 240, 255)  # 明るい青
                    shield_bar_color = (173, 216, 230)    # 薄い青
                    color_filled_bar = (200, 230, 255)    # ライトブルー
                case "Green Theme":
                    color_unfilled_bar = (230, 255, 230)  # 明るい緑
                    shield_bar_color = (144, 238, 144)    # ライトグリーン
                    color_filled_bar = (193, 255, 193)    # ライトな緑色
                case "Pink Theme":
                    color_unfilled_bar = (255, 238, 248)  # 明るいピンク
                    shield_bar_color = (255, 170, 207)    # 薄いピンク
                    color_filled_bar = (255, 209, 229)    # ライトピンク
                case "Red Theme":
                    color_unfilled_bar = (255, 220, 220)  # 明るい赤
                    color_filled_bar = (255, 160, 160)    # ライトレッド
                    shield_bar_color = (255, 128, 128)    # ライトレッド
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


    damage_graph_slot = pygame_gui.elements.UIImage(pygame.Rect((1080, 655), (500, 225)),
                                        pygame.Surface((500, 225)),
                                        ui_manager)
    # ./tmp/damage_dealt.png
    damage_graph_slot.set_image((images_item["405"]))


    def redraw_ui(party1, party2, *, refill_image=True, main_char=None,
                  buff_added_this_turn=None, debuff_added_this_turn=None, shield_value_diff_dict=None, redraw_eq_slots=True,
                  also_draw_chart=True, optimize_for_auto_battle=False):

        def redraw_party(party, image_slots, equip_slots_weapon, equip_slots_armor, equip_slots_accessory, equip_stats_boots, 
                         labels, healthbar, equip_effect_slots):
            for i, character in enumerate(party):
                if refill_image:
                    try:
                        image_slots[i].set_image(character.featured_image)
                    except Exception:
                        image_slots[i].set_image(images_item["404"])

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

                    if not ignore_draw_weapon:
                        equip_slots_weapon[i].set_tooltip(character.equip["Weapon"].print_stats_html(), delay=0.1, wrap_width=300)
                    if not ignore_draw_armor:
                        equip_slots_armor[i].set_tooltip(character.equip["Armor"].print_stats_html(), delay=0.1, wrap_width=300)
                    if not ignore_draw_accessory:
                        equip_slots_accessory[i].set_tooltip(character.equip["Accessory"].print_stats_html(), delay=0.1, wrap_width=300)
                    if not ignore_draw_boots:
                        equip_stats_boots[i].set_tooltip(character.equip["Boots"].print_stats_html(), delay=0.1, wrap_width=300)


                # This should always be redrawn
                if character.equipment_set_effects_tooltip() != "":
                    equip_effect_slots[i].show()
                    equip_effect_slots[i].set_tooltip(character.equipment_set_effects_tooltip(), delay=0.1, wrap_width=400)
                else:
                    equip_effect_slots[i].hide()

                labels[i].set_text(f"lv {character.lvl} {character.name}")
                labels[i].set_tooltip(character.skill_tooltip(), delay=0.1, wrap_width=500)
                # Doesn't work so commented out
                # labels[i].set_text_alpha(255) if character.is_alive() else labels[i].set_text_alpha(125)

                # redraw healthbar is fairly expensive process, so we need to optimize it
                # if optimize_for_auto_battle and shield_value_diff_dict[character.name] == 0 and not character.damage_taken_this_turn and not character.healing_received_this_turn:
                #     pass
                # else:
                # Edit on 2.2.9: Optimize is removed because we wont be able to catch skills that change maxhp or shield
                healthbar[i].set_image(create_healthbar(character.hp, character.maxhp, 176, 30, shield_value=character.get_shield_value(), auto_color=True))
                healthbar[i].set_tooltip(character.tooltip_status_effects(), delay=0.1, wrap_width=400)

                if main_char == character:
                    labels[i].set_text(f"--> lv {character.lvl} {character.name}")
                    image = image_slots[i].image
                    new_image = add_outline_to_image(image, (255, 215, 0), 6)
                    image_slots[i].set_image(new_image)

                # self.damage_taken_this_turn = [] # list of tuples (damage, attacker, damage_type)
                current_offset_for_damage_and_healing = 10
                if character.damage_taken_this_turn:
                    image = image_slots[i].image
                    new_image = add_outline_to_image(image, (255, 0, 0), 4)
                    for a, b, c in character.damage_taken_this_turn:
                        match c:
                            case "normal" | "bypass":
                                create_yellow_text(new_image, str(a), 25, (255, 0, 0), current_offset_for_damage_and_healing)
                            case "status":
                                # orange text
                                create_yellow_text(new_image, str(a), 25, (255, 165, 0), current_offset_for_damage_and_healing)
                            case "normal_critical":
                                create_yellow_text(new_image, str(a), 25, (255, 0, 0), current_offset_for_damage_and_healing, bold=True, italic=True)
                            case _:
                                raise Exception(f"Unknown damage type: {c}")
                        current_offset_for_damage_and_healing += 12
                    image_slots[i].set_image(new_image)
                if character.healing_received_this_turn:
                    image = image_slots[i].image
                    new_image = add_outline_to_image(image, (0, 255, 0), 4)
                    # get all healing from list of tuples
                    healing_list = [x[0] for x in character.healing_received_this_turn]
                    # show healing on image
                    for healing in healing_list:
                        create_yellow_text(new_image, str(healing), 25, (0, 255, 0), current_offset_for_damage_and_healing)
                        current_offset_for_damage_and_healing += 12
                    image_slots[i].set_image(new_image)

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
                     label_party1, health_bar_party1, equip_set_slot_party1)
        redraw_party(party2, image_slots_party2, equip_slot_party2_weapon, equip_slot_party2_armor, equip_slot_party2_accessory, equip_slot_party2_boots,
                     label_party2, health_bar_party2, equip_set_slot_party2)
        if also_draw_chart:
            draw_chart()



    def draw_chart():
        global current_display_chart, df_damage_summary
        match current_display_chart:
            case "Damage Dealt Chart":
                if plot_damage_d_chart:
                    damage_graph_slot.set_image(plot_damage_d_chart)
                    if df_damage_summary is not None:
                        tooltip_text = "Damage dealt summary:\n"
                        for line in df_damage_summary.values:
                            tooltip_text += f"{line[0]} dealt {line[6]} damage in total, {line[7]} normal damage, {line[8]} critical damage, {line[9]} status damage, and {line[10]} bypass damage.\n"
                        damage_graph_slot.set_tooltip(tooltip_text, delay=0.1, wrap_width=600)
                else:
                    damage_graph_slot.set_image(images_item["405"])
            case "Damage Taken Chart":
                if plot_damage_r_chart:
                    damage_graph_slot.set_image(plot_damage_r_chart)
                    if df_damage_summary is not None:
                        tooltip_text = "Damage taken summary:\n"
                        for line in df_damage_summary.values:
                            tooltip_text += f"{line[0]} received {line[1]} damage in total, {line[2]} normal damage, {line[3]} critical damage, {line[4]} status damage, and {line[5]} bypass damage.\n"
                        damage_graph_slot.set_tooltip(tooltip_text, delay=0.1, wrap_width=600)
                else:
                    damage_graph_slot.set_image(images_item["405"])
            case "Healing Chart":
                if plot_healing_chart:
                    damage_graph_slot.set_image(plot_healing_chart)
                    if df_healing_summary is not None:
                        tooltip_text = "Healing summary:\n"
                        for line in df_healing_summary.values:
                            tooltip_text += f"{line[0]} received {line[1]} healing in total, {line[2]} healing is given.\n"
                        damage_graph_slot.set_tooltip(tooltip_text, delay=0.1, wrap_width=600)
                else:
                    damage_graph_slot.set_image(images_item["405"])
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
    text_box_introduction_text += "Hover over character health bar to show status effects.\n"
    text_box.set_text(text_box_introduction_text)

    box_submenu_previous_stage_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((300, 560), (120, 35)),
                                                                    text='Previous Stage',
                                                                    manager=ui_manager)
    box_submenu_previous_stage_button.set_tooltip("Go to previous stage.", delay=0.1)

    box_submenu_next_stage_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((425, 560), (120, 35)),
                                                                    text='Next Stage',
                                                                    manager=ui_manager)
    box_submenu_next_stage_button.set_tooltip("Advance to the next stage. You can proceed only if the current stage has been cleared.", delay=0.1)
    box_submenu_previous_stage_button.hide()
    box_submenu_next_stage_button.hide()
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
    shop_select_a_shop = pygame_gui.elements.UIDropDownMenu(["Banana Armory", "Silver Wolf Company", "Big Food Market"],
                                                            "Banana Armory",
                                                            pygame.Rect((300, 500), (212, 35)),
                                                            ui_manager)
    shop_shop_introduction_sign = pygame_gui.elements.UIImage(pygame.Rect((815, 500), (35, 35)),
                                        pygame.Surface((35, 35)),
                                        ui_manager)
    shop_shop_introduction_sign.set_image(images_item["info_sign"])
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
                            shop_select_a_shop, shop_shop_introduction_sign, shop_refresh_items_button, shop_player_owned_currency_icon,
                            shop_player_owned_currency]
    for m in all_shop_ui_modules:
        m.hide()

    def redraw_ui_shop_edition():
        # we first need to get what shop it is
        shop_name = shop_select_a_shop.selected_option[0]
        # then we create a shop of Shop.[shop_name]
        match shop_name:
            case "Banana Armory":
                shop_instance = shop.Armory_Banana("Banana Armory", None)
            case "Silver Wolf Company":
                shop_instance = shop.Gulid_SliverWolf("Silver Wolf Company", None)
            case "Big Food Market":
                shop_instance = shop.Big_Food_Market("Big Food Market", None)
            case _:
                raise Exception(f"Unknown shop name: {shop_name}")
        shop_instance.get_items_from_manufacturers()
        shop_instance.decide_price()
        shop_instance.decide_discount()
        shop_instance.calculate_final_price()

        shop_image_slot_currency_icon.set_image(images_item[shop_instance.currency.lower()])
        shop_player_owned_currency_icon.set_image(images_item[shop_instance.currency.lower()])
        # shop_player_owned_currency.set_text(str(player.get_cash()))
        set_currency_on_icon_and_label(player, shop_instance.currency, shop_player_owned_currency, shop_player_owned_currency_icon)

        shop_shop_introduction_sign.set_tooltip(shop_instance.description, delay=0.1, wrap_width=300)

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
            ui_image.set_tooltip(item.print_stats_html(), delay=0.1, wrap_width=300)
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

        return shop_instance


    def shop_purchase_item(player: Nine, shop: shop.Shop, item_id: int) -> None:
        item_price = list(shop.inventory.values())[item_id][2]
        item = list(shop.inventory.keys())[item_id]
        copyed_item = copy.copy(item)
        # print(f"item: {item}, price: {item_price}")
        buy_one_item(player, copyed_item, item_price)
        set_currency_on_icon_and_label(player, shop.currency, shop_player_owned_currency, shop_player_owned_currency_icon)

    def set_currency_on_icon_and_label(player: Nine, currency: str, label: pygame_gui.elements.UILabel, icon: pygame_gui.elements.UIImage):
        icon.set_image(images_item[currency.lower()])
        label.set_text(str(player.get_currency(currency)))

    # Event loop
    # ==========================
    running = True 
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
                player.cleared_stages = 2199 # 2199
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
                    print(f"Trying to read equipment data and equip items for {c.name}...")
                    for d in character_info_dict[c.name][2]:
                        item = Equip("foo", "Weapon", "Common")
                        for attr, value in d.items():
                            if hasattr(item, attr):
                                setattr(item, attr, value)
                        item.estimate_market_price()
                        item.four_set_effect_description = item.assign_four_set_effect_description()
                        c.equip_item(item)
                        print(f"Equipped {str(item)} to {c.name}.")
        return player

    player = initiate_player_data()

    adventure_mode_stages = {} # int : list of monsters
    if player.cleared_stages > 0:
        print(f"Loading adventure mode stages from player data. Current stage: {player.cleared_stages}")
        adventure_mode_current_stage = min(player.cleared_stages + 1, 2500)
    else:
        adventure_mode_current_stage = 1
    adventure_mode_generate_stage()


    # party1 = []
    party1 : list[Character] = []
    party2 : list[Character] = []
    party1, party2 = set_up_characters(is_start_of_app=True)
    player.build_inventory_slots()
    turn = 1

    auto_battle_active = False
    auto_battle_bar_progress = 0
    time_acc = 0

    while running:
        time_delta = clock.tick(60)/1000.0
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                save_player(player)
                running = False
            # right click to deselect from inventory
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 3:
                for ui_image, rect in player.dict_image_slots_rects.items():
                    if ui_image in player.selected_item.keys():
                        a, b, c = player.selected_item[ui_image]
                        if b:
                            ui_image.set_image(a)
                            player.selected_item[ui_image] = (a, False, c)
                            

            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                # print(event.pos)
                if image_slot1.get_abs_rect().collidepoint(event.pos):
                    if current_game_mode == "Training Mode":
                        party_show_in_menu = [f" Lv.{character.lvl} {character.name}" for character in itertools.chain(party1, party2)]
                        handle_UIDropDownMenu(party_show_in_menu, None, 0)
                    elif current_game_mode == "Adventure Mode":
                        party1_show_in_menu = [f" Lv.{character.lvl} {character.name}" for character in party1]
                        handle_UIDropDownMenu(party1_show_in_menu, None, 0)
                if image_slot2.get_abs_rect().collidepoint(event.pos):
                    if current_game_mode == "Training Mode":
                        party_show_in_menu = [f" Lv.{character.lvl} {character.name}" for character in itertools.chain(party1, party2)]
                        handle_UIDropDownMenu(party_show_in_menu, None, 1)
                    elif current_game_mode == "Adventure Mode":
                        party1_show_in_menu = [f" Lv.{character.lvl} {character.name}" for character in party1]
                        handle_UIDropDownMenu(party1_show_in_menu, None, 1)
                if image_slot3.get_abs_rect().collidepoint(event.pos):
                    if current_game_mode == "Training Mode":
                        party_show_in_menu = [f" Lv.{character.lvl} {character.name}" for character in itertools.chain(party1, party2)]
                        handle_UIDropDownMenu(party_show_in_menu, None, 2)
                    elif current_game_mode == "Adventure Mode":
                        party1_show_in_menu = [f" Lv.{character.lvl} {character.name}" for character in party1]
                        handle_UIDropDownMenu(party1_show_in_menu, None, 2)
                if image_slot4.get_abs_rect().collidepoint(event.pos):
                    if current_game_mode == "Training Mode":
                        party_show_in_menu = [f" Lv.{character.lvl} {character.name}" for character in itertools.chain(party1, party2)]
                        handle_UIDropDownMenu(party_show_in_menu, None, 3)
                    elif current_game_mode == "Adventure Mode":
                        party1_show_in_menu = [f" Lv.{character.lvl} {character.name}" for character in party1]
                        handle_UIDropDownMenu(party1_show_in_menu, None, 3)
                if image_slot5.get_abs_rect().collidepoint(event.pos):
                    if current_game_mode == "Training Mode":
                        party_show_in_menu = [f" Lv.{character.lvl} {character.name}" for character in itertools.chain(party1, party2)]
                        handle_UIDropDownMenu(party_show_in_menu, None, 4)
                    elif current_game_mode == "Adventure Mode":
                        party1_show_in_menu = [f" Lv.{character.lvl} {character.name}" for character in party1]
                        handle_UIDropDownMenu(party1_show_in_menu, None, 4)
                if image_slot6.get_abs_rect().collidepoint(event.pos):
                    if current_game_mode == "Training Mode":
                        party_show_in_menu = [f" Lv.{character.lvl} {character.name}" for character in itertools.chain(party1, party2)]
                        handle_UIDropDownMenu(party_show_in_menu, None, 5)
                if image_slot7.get_abs_rect().collidepoint(event.pos):
                    if current_game_mode == "Training Mode":
                        party_show_in_menu = [f" Lv.{character.lvl} {character.name}" for character in itertools.chain(party1, party2)]
                        handle_UIDropDownMenu(party_show_in_menu, None, 6)
                if image_slot8.get_abs_rect().collidepoint(event.pos):
                    if current_game_mode == "Training Mode":
                        party_show_in_menu = [f" Lv.{character.lvl} {character.name}" for character in itertools.chain(party1, party2)]
                        handle_UIDropDownMenu(party_show_in_menu, None, 7)
                if image_slot9.get_abs_rect().collidepoint(event.pos):
                    if current_game_mode == "Training Mode":
                        party_show_in_menu = [f" Lv.{character.lvl} {character.name}" for character in itertools.chain(party1, party2)]
                        handle_UIDropDownMenu(party_show_in_menu, None, 8)
                # This is only a temporary solution, we should consider changing layering of UI elements
                if image_slot10.get_abs_rect().collidepoint(event.pos) and not reserve_character_selection_menu.are_contents_hovered():
                    if current_game_mode == "Training Mode":
                        party_show_in_menu = [f" Lv.{character.lvl} {character.name}" for character in itertools.chain(party1, party2)]
                        handle_UIDropDownMenu(party_show_in_menu, None, 9)

                for ui_image, rect in player.dict_image_slots_rects.items():
                    if rect.collidepoint(event.pos):
                        if ui_image in player.selected_item.keys():
                            a, b, c = player.selected_item[ui_image]
                            if b:
                                ui_image.set_image(a)
                                player.selected_item[ui_image] = (a, False, c)
                                break

                        player.selected_item[ui_image] = (ui_image.image, True, player.dict_image_slots_items[ui_image]) # Add newly clicked image to dict
                        ui_image.set_image(add_outline_to_image(ui_image.image, (255, 215, 0), 1))
                        break


            if event.type == pygame_gui.UI_BUTTON_PRESSED:
                if event.ui_element == button_left_change_chart:
                    if current_display_chart == "Damage Dealt Chart":
                        current_display_chart = "Damage Taken Chart"
                        create_plot_damage_r_chart()
                        draw_chart()
                        button_left_change_chart.set_tooltip(f"Switch between damage dealt chart, damage received chart or others if implemented. Current chart: {current_display_chart}", delay=0.1, wrap_width=300)
                    elif current_display_chart == "Damage Taken Chart":
                        current_display_chart = "Healing Chart"
                        create_plot_healing_chart()
                        draw_chart()
                        button_left_change_chart.set_tooltip(f"Switch between damage dealt chart, damage received chart or others if implemented. Current chart: {current_display_chart}", delay=0.1, wrap_width=300)
                    elif current_display_chart == "Healing Chart":
                        current_display_chart = "Damage Dealt Chart"
                        create_plot_damage_d_chart()
                        draw_chart()
                        button_left_change_chart.set_tooltip(f"Switch between damage dealt chart, damage received chart or others if implemented. Current chart: {current_display_chart}", delay=0.1, wrap_width=300)
                if event.ui_element == button1: # Shuffle party
                    text_box.set_text("==============================\n")
                    if current_game_mode == "Training Mode":
                        party1, party2 = set_up_characters()
                    elif current_game_mode == "Adventure Mode":
                        party1, party2 = set_up_characters_adventure_mode(True)
                    turn = 1
                if event.ui_element == switch_game_mode_button:
                    if current_game_mode == "Training Mode":
                        current_game_mode = "Adventure Mode"
                        party1, party2 = set_up_characters_adventure_mode()
                        turn = 1
                        switch_game_mode_button.set_text("Training Mode")
                        text_box.set_dimensions((556, 255))
                        box_submenu_previous_stage_button.show()
                        box_submenu_next_stage_button.show()
                        box_submenu_stage_info_label.show()
                        box_submenu_stage_info_label.set_text(f"Stage {adventure_mode_current_stage}")
                        box_submenu_stage_info_label.set_tooltip(adventure_mode_info_tooltip(), delay=0.1, wrap_width=300)
                        box_submenu_enter_shop_button.show()
                        box_submenu_exit_shop_button.show()
                        # box_submenu_explore_button.show()
                        # box_submenu_explore_funds_selection.show()
                    elif current_game_mode == "Adventure Mode":
                        current_game_mode = "Training Mode"
                        party1, party2 = set_up_characters()
                        turn = 1
                        switch_game_mode_button.set_text("Adventure Mode")
                        text_box.set_dimensions((556, 295))
                        box_submenu_previous_stage_button.hide()
                        box_submenu_next_stage_button.hide()
                        box_submenu_stage_info_label.hide()
                        box_submenu_enter_shop_button.hide()
                        box_submenu_exit_shop_button.hide()
                        for m in all_shop_ui_modules:
                            m.hide()
                        text_box.show()
                        global_vars.player_is_in_shop = False
                        # box_submenu_explore_button.hide()
                        # box_submenu_explore_funds_selection.hide()
                if event.ui_element == next_turn_button:
                    if next_turn(party1, party2):
                        turn += 1
                if event.ui_element == button3:
                    all_turns(party1, party2)
                if event.ui_element == button4: # Restart battle
                    text_box.set_text("==============================\n")
                    restart_battle()
                if event.ui_element == button_quit_game:
                    save_player(player)
                    running = False
                if event.ui_element == eq_stars_upgrade_button:
                    eq_stars_upgrade(True)
                if event.ui_element == character_replace_button:
                    replace_character_with_reserve_member(character_selection_menu.selected_option[0].split()[-1], reserve_character_selection_menu.selected_option[0].split()[-1])
                if event.ui_element == eq_levelup_button:
                    eq_level_up(amount_to_level=1)
                if event.ui_element == eq_levelup_buttonx10:
                    eq_level_up(amount_to_level=10)
                if event.ui_element == eq_level_up_to_max_button:
                    eq_level_up_to_max()
                if event.ui_element == eq_sell_selected_button:
                    eq_sell_selected()
                if event.ui_element == eq_sell_low_value_button:
                    eq_sell_low_value(int(eq_sell_low_value_selection_menu.selected_option[0]))
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
                if event.ui_element == cheap_inventory_next_page_button:
                    player.to_next_page()
                if event.ui_element == cheap_inventory_sort_by_button:
                    cheap_inventory_sort()
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
                if event.ui_element == box_submenu_enter_shop_button:
                    if not global_vars.player_is_in_shop:
                        text_box.hide()
                        for m in all_shop_ui_modules:
                            m.show()
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


            if event.type == pygame_gui.UI_DROP_DOWN_MENU_CHANGED:
                if event.ui_element == shop_select_a_shop:
                    # working correctly
                    print(f"Selected shop: {shop_select_a_shop.selected_option[0]}")
                    the_shop = redraw_ui_shop_edition()
                if event.ui_element == theme_selection_menu:
                    change_theme()
                if event.ui_element == cheap_inventory_what_to_show_selection_menu:
                    match cheap_inventory_what_to_show_selection_menu.selected_option[0]:
                        case "Equip":
                            player.current_page = 0
                            global_vars.cheap_inventory_show_current_option = "Equip"
                            player.build_inventory_slots()
                            
                            use_item_button.set_text("Equip Item")
                            eq_selection_menu.show()
                            character_eq_unequip_button.show()
                            eq_levelup_button.show()
                            eq_levelup_buttonx10.show()
                            eq_level_up_to_max_button.show()
                            eq_stars_upgrade_button.show()
                            eq_sell_selected_button.show()
                            eq_sell_low_value_selection_menu.show()
                            eq_sell_low_value_button.show()
                            item_sell_button.hide()
                            item_sell_half_button.hide()
                            item_sell_all_button.hide()
                            use_random_consumable_label.hide()
                            use_random_consumable_selection_menu.hide()
                        case "Item":
                            player.current_page = 0
                            global_vars.cheap_inventory_show_current_option = "Item"
                            player.build_inventory_slots()
                            use_item_button.set_text("Use Item")
                            eq_selection_menu.hide()
                            character_eq_unequip_button.hide()
                            eq_levelup_button.hide()
                            eq_levelup_buttonx10.hide()
                            eq_level_up_to_max_button.hide()
                            eq_stars_upgrade_button.hide()
                            eq_sell_selected_button.hide()
                            eq_sell_low_value_selection_menu.hide()
                            eq_sell_low_value_button.hide()
                            item_sell_button.show()
                            item_sell_half_button.show()
                            item_sell_all_button.show()
                            use_random_consumable_label.hide()
                            use_random_consumable_selection_menu.hide()
                        case "Consumable":
                            player.current_page = 0
                            global_vars.cheap_inventory_show_current_option = "Consumable"
                            player.build_inventory_slots()
                            use_item_button.set_text("Use Item")
                            eq_selection_menu.hide()
                            character_eq_unequip_button.hide()
                            eq_levelup_button.hide()
                            eq_levelup_buttonx10.hide()
                            eq_level_up_to_max_button.hide()
                            eq_stars_upgrade_button.hide()
                            eq_sell_selected_button.hide()
                            eq_sell_low_value_selection_menu.hide()
                            eq_sell_low_value_button.hide()
                            item_sell_button.show()
                            item_sell_half_button.show()
                            item_sell_all_button.show()
                            use_random_consumable_label.show()
                            use_random_consumable_selection_menu.show()
                        case _:
                            raise Exception("Unknown option selected in cheap_inventory_what_to_show_selection_menu")                                



            ui_manager.process_events(event)

        ui_manager.update(time_delta)
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
        ui_manager.draw_ui(display_surface)

        # debug_ui_manager.update(time_delta)
        # debug_ui_manager.draw_ui(display_surface)

        if auto_battle_active:
            time_acc += time_delta
            auto_battle_bar_progress = (time_acc/decide_auto_battle_speed()) # May impact performance
            if auto_battle_bar_progress > 1.0:
                time_acc = 0.0
                if not next_turn(party1, party2):
                    auto_battle_active = False
                    instruction = after_auto_battle_selection_menu.selected_option[0]
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
