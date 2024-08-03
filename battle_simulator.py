import inspect
import os, json
from character import *
import monsters
from item import *
from consumable import *
import copy
running = False
text_box = None
start_with_max_level = False


# NOTE:
# 1. We cannot have character with the same name.
# 2. We better not have effects with the same name.
# 3. Because we now have save feature, make sure to shut down instead of quit for debugging. Delete player_data.json if necessary.
# 4, Every time we add a new item type for inventory, we have to add it to a certain list. See Nine.sort_inventory_by_type
# 5. load_player() is only partially implemented. We have to add more code to load consumables and items.
# 6. If there is bug unsolvable, refer to 3.
# 7. explore_generate_package_of_items_to_desired_value need more items to be added.

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
            case ("<class 'equip.Equip'>", _):
                item = Equip("foo", "Weapon", "Common")
                for attr, value in item_data.items():
                    if hasattr(item, attr):
                        setattr(item, attr, value)
                item.estimate_market_price()
            case (_, "Food"): 
                item_class = globals().get(item_data['name'])
                if item_class:
                    item = item_class(item_data['current_stack'])
                else:
                    raise ValueError(f"Unknown item type: {item_data['name']}")
            case _:
                continue

        player.inventory.append(item)
        player.get_cash()
    player.cleared_stages = data["cleared_stages"]
    return player, dict_character_name_lvl_exp_equip

def is_someone_alive(party):
    for character in party:
        if character.is_alive():
            return True
    return False

# Reset characters.ally and characters.enemy
def reset_ally_enemy_attr(party1, party2):
    for character in party1:
        character.ally = copy.copy(party1)
        character.enemy = copy.copy(party2)
        character.party = party1
        character.enemyparty = party2
    for character in party2:
        character.ally = copy.copy(party2)
        character.enemy = copy.copy(party1)
        character.party = party2
        character.enemyparty = party1

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
        self.selected_item = {} # {image_slot: UIImage : (image: Surface, is_highlighted: bool, the_actual_item: Block)}
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
        global cheap_inventory_show_current_option
        self.selected_item = {}
        page = self.current_page
        try: # I do not think it is the best way to do this.
            only_include = cheap_inventory_show_current_option
        except NameError:
            only_include = "Equip"
        match only_include:
            case "Equip":
                filtered_inventory = [x for x in self.inventory if isinstance(x, Equip)]
            case "Consumable":
                filtered_inventory = [x for x in self.inventory if isinstance(x, Consumable)]
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
                    create_yellow_text(image_to_process, str(item.current_stack), 215, (0, 0, 0), add_background=True)
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

    def use_1_selected_item(self, rebuild_inventory_slots: bool):
        # self.selected_item = {} # {image_slot: UIImage : (image: Surface, is_highlighted: bool, the_actual_item)}
        """Can be used for stackable items"""
        if not self.selected_item:
            return
        for a, b, item in self.selected_item.values():
            if b: # is_highlighted
                self.remove_from_inventory(type(item), 1, False)
        if rebuild_inventory_slots:
            self.build_inventory_slots()

    def add_package_of_items_to_inventory(self, package_of_items: list):
        for item in package_of_items:
            self.add_to_inventory(item, False)
        self.build_inventory_slots()

    def sort_inventory_by_rarity(self):
        all_possible_types = ["Weapon", "Armor", "Accessory", "Boots", "None", "Food"]
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
        all_possible_types = ["Weapon", "Armor", "Accessory", "Boots", "None", "Food"]
        type_order = dict(mit.zip_equal(all_possible_types, range(len(all_possible_types))))
        self.inventory.sort(key=lambda x: type_order[x.type], reverse=False)
        self.current_page = 0
        self.build_inventory_slots()

    def sort_inventory_by_set(self):
        all_possible_types = ["Weapon", "Armor", "Accessory", "Boots", "None", "Food"]
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

    def lose_cash(self, amount: int, rebuild_inventory_slots: bool = True):
        self.remove_from_inventory(Cash, amount, rebuild_inventory_slots)


try:
    player, character_info_dict = load_player()
    print("Player and character data loaded.")
except FileNotFoundError:
    print("Player data not found, creating a new one...")
    if start_with_max_level:
        player = Nine(50000000)
        player.cleared_stages = 2199
    else:
        player = Nine(123456)
        player.cleared_stages = 0

# =====================================
# End of Player Section
# =====================================
# Character Creation Section
# =====================================

def get_all_characters():
    global start_with_max_level
    character_names = ["Cerberus", "Fenrir", "Clover", "Ruby", "Olive", "Luna", "Freya", "Poppy", "Lillia", "Iris",
                       "Pepper", "Cliffe", "Pheonix", "Bell", "Taily", "Seth", "Ophelia", "Chiffon", "Requina", "Gabe", 
                       "Yuri", "Dophine", "Tian", "Don"]

    if start_with_max_level:
        all_characters = [eval(f"{name}('{name}', 1000)") for name in character_names]
    else:
        all_characters = [eval(f"{name}('{name}', 40)") for name in character_names]
    return all_characters

all_characters = get_all_characters()

try:
    character_info_dict
except NameError:
    pass
else:
    for c in all_characters:
        if not c.name in character_info_dict.keys():
            print(f"Character {c.name} not found in character_info_dict, skipped.") # When a new character is added, this will happen.
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
                c.equip_item(item)
                print(f"Equipped {str(item)} to {c.name}.")

def get_all_monsters():
    monster_names = [name for name in dir(monsters) 
                    if inspect.isclass(getattr(monsters, name)) and 
                    issubclass(getattr(monsters, name), Character) and 
                    name != "Character"]
    print("All monsters:")
    print(monster_names)
    all_monsters = [eval(f"monsters.{name}('{name}', 1)") for name in monster_names]
    return all_monsters

all_monsters = get_all_monsters()


# ---------------------------------------------------------
# ---------------------------------------------------------
if __name__ == "__main__":
    import pygame, pygame_gui
    pygame.init()
    clock = pygame.time.Clock()

    antique_white = pygame.Color("#FAEBD7")
    deep_dark_blue = pygame.Color("#000022")
    light_yellow = pygame.Color("#FFFFE0")

    display_surface = pygame.display.set_mode((1600, 900), flags=pygame.RESIZABLE)
    ui_manager = pygame_gui.UIManager((1600, 900), "theme_light_yellow.json", starting_language='ja')
    debug_ui_manager = pygame_gui.UIManager((1600, 900), "theme_light_yellow.json", starting_language='ja')

    pygame.display.set_caption("Battle Simulator")

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
    button1.set_tooltip("パーティをシャッフルしてバトルを再開する。", delay=0.1, wrap_width=300)

    button4 = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((100, 360), (156, 50)),
                                        text='Restart Battle',
                                        manager=ui_manager,
                                        tool_tip_text = "Restart battle")
    button4.set_tooltip("バトル再開", delay=0.1)

    button3 = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((100, 420), (156, 50)),
                                        text='All Turns',
                                        manager=ui_manager,
                                        tool_tip_text = "Skip to the end of the battle.")
    button3.set_tooltip("バトルの終わりまでスキップするが、報酬はなしです。", delay=0.1, wrap_width=300)

    button_left_clear_board = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((100, 480), (156, 50)),
                                        text='Clear Board',
                                        manager=ui_manager,
                                        tool_tip_text = "Remove all text from the text box, text box will be slower if there are too many text.")
    button_left_clear_board.set_tooltip("テキストボックスのテキストをすべて削除する。テキストが多いとテキストボックスが遅くなる。", delay=0.1, wrap_width=300)
    
    button_quit_game = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((100, 540), (156, 50)),
                                        text='Quit',
                                        manager=ui_manager,
                                        tool_tip_text = "Quit")
    button_quit_game.set_tooltip("プレイヤーデータをplayer_data.jsonとして保存し、終了する。", delay=0.1, wrap_width=300)

    # =====================================
    # Right Side

    next_turn_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((900, 300), (156, 50)),
                                        text='Next Turn',
                                        manager=ui_manager,
                                        tool_tip_text = "Simulate the next turn")
    next_turn_button_tooltip_str = "次のターン。冒険モードでバトルが勝利した場合に経験値と現金を獲得できる。"
    next_turn_button_tooltip_str += "ステージレベルが平均パーティのレベルよりも高い場合、報酬が増える。"
    next_turn_button.set_tooltip(next_turn_button_tooltip_str, delay=0.1, wrap_width=300)

    button_auto_battle = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((1080, 300), (156, 50)),
                                        text='Auto',
                                        manager=ui_manager,
                                        tool_tip_text = "Auto battle")
    button_auto_battle.set_tooltip("プログレスバーが満タンになったら自動的に次のターンに進む。バトルが終了した場合に報酬を獲得できる。", delay=0.1, wrap_width=300)


    auto_battle_bar = pygame_gui.elements.UIStatusBar(pygame.Rect((1080, 290), (156, 10)),
                                               ui_manager,
                                               None)

    # If these options are changed, make sure to change the corresponding functions by searching for the function name
    auto_battle_speed_selection_menu = pygame_gui.elements.UIDropDownMenu(["遅い", "普通", "速い", "とても速い", "即時"],
                                                            "普通",
                                                            pygame.Rect((1080, 260), (156, 35)),
                                                            ui_manager)

    auto_battle_speed_label = pygame_gui.elements.UILabel(pygame.Rect((1080, 220), (156, 35)),
                                        "自動バトル速度: ",
                                        ui_manager)

    after_auto_battle_selection_menu = pygame_gui.elements.UIDropDownMenu(["何もしない", "バトル再開", "パーティシャッフル"],
                                                            "何もしない",
                                                            pygame.Rect((1080, 180), (156, 35)),
                                                            ui_manager)

    after_auto_battle_label = pygame_gui.elements.UILabel(pygame.Rect((1080, 140), (156, 35)),
                                        "自動バトル後の処理: ",
                                        ui_manager)

    def decide_auto_battle_speed():
        speed = auto_battle_speed_selection_menu.selected_option
        match speed:
            case "遅い":
                return 10.0
            case "普通":
                return 5.0
            case "速い":
                return 2.5
            case "とても速い":
                return 1.25
            case "即時":
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
    switch_game_mode_button.set_tooltip("アドベンチャーモードとトレーニングモードを切り替える。", delay=0.1, wrap_width=300)

    def adventure_mode_generate_stage():
        global current_game_mode, adventure_mode_current_stage, adventure_mode_stages
        for m in all_monsters:
            m.lvl = adventure_mode_current_stage
        # Boss monsters have attribute is_boss = True, every 10 stages, starting from stage 10, summon a boss monster
        # There can only be 1 boss monster in a stage
        if adventure_mode_current_stage % 10 == 0 or adventure_mode_current_stage > 1000:
            new_selection_of_monsters = random.sample([x for x in all_monsters if not x.is_boss], k=4)
            boss_monster = random.choice([x for x in all_monsters if x.is_boss])
            new_selection_of_monsters.insert(2, boss_monster)
        else:
            new_selection_of_monsters = random.sample([x for x in all_monsters if not x.is_boss], k=5)
        if not adventure_mode_stages.get(adventure_mode_current_stage):
            adventure_mode_stages[adventure_mode_current_stage] = new_selection_of_monsters
        if adventure_mode_current_stage > 1000:
            for m in adventure_mode_stages[adventure_mode_current_stage]:
                m.equip_item_from_list(generate_equips_list(4, locked_eq_set="Void", include_void=True, locked_rarity="Common", 
                                                            eq_level=int(adventure_mode_current_stage - 1000)))

    def adventure_mode_stage_increase():
        global current_game_mode, adventure_mode_current_stage
        if current_game_mode == "Training Mode":
            raise Exception("Cannot change stage in Training Mode. See Game Mode Section.")
        if adventure_mode_current_stage == 2200:
            text_box.set_text("世界の終末に到達した。\n")
            return
        if player.cleared_stages < adventure_mode_current_stage:
            text_box.set_text("現在のステージはクリアしていない。\n")
            return
        adventure_mode_current_stage += 1
        adventure_mode_generate_stage()
        set_up_characters_adventure_mode()

    def adventure_mode_stage_decrease():
        global current_game_mode, adventure_mode_current_stage
        if current_game_mode == "Training Mode":
            raise Exception("Cannot change stage in Training Mode. See Game Mode Section.")
        if adventure_mode_current_stage == 1:
            text_box.set_text("このステージが旅の始まりだ。\n")
            return
        adventure_mode_current_stage -= 1
        adventure_mode_generate_stage()
        set_up_characters_adventure_mode()


    adventure_mode_stages = {} # int : list of monsters
    if player.cleared_stages > 0:
        print(f"Loading adventure mode stages from player data. Current stage: {player.cleared_stages}")
        adventure_mode_current_stage = min(player.cleared_stages + 1, 2200)
    else:
        adventure_mode_current_stage = 1
    adventure_mode_generate_stage()


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
        str = f"現在のステージ: {adventure_mode_current_stage}\n"
        if adventure_mode_current_stage > sum([x.lvl for x in party1]) / 5:
            str += f"敵のレベルが平均パーティのレベルよりも高いため、報酬が{(adventure_mode_current_stage / (sum([x.lvl for x in party1]) / 5) - 1) * 100:.2f}%増加します\n"
        if adventure_mode_current_stage % 10 == 0 or adventure_mode_current_stage > 1000: # ボスステージ
            str += "ボスステージです。報酬が50%増加します。\n"
        str += f"経験値報酬: {adventure_mode_exp_reward()}\n"
        a, b = adventure_mode_cash_reward()
        str += f"現金報酬: 約{b}\n"
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
    label_character_selection_menu.set_tooltip("選択したキャラクター。キャラクター画像をクリックしても選択できます。", delay=0.1)

    reserve_character_selection_menu = pygame_gui.elements.UIDropDownMenu(["Option1"],
                                                            "Option1",
                                                            pygame.Rect((900, 400), (156, 35)),
                                                            ui_manager)

    label_reserve_character_selection_menu = pygame_gui.elements.UILabel(pygame.Rect((870, 400), (25, 35)),
                                        "→",
                                        ui_manager)
    label_reserve_character_selection_menu.set_tooltip("控えメンバー、キャラクターのレベルでソートされてる。", delay=0.1)

    character_replace_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((900, 440), (156, 35)),
                                        text='Replace',
                                        manager=ui_manager,
                                        tool_tip_text = "Replace selected character with reserve character")
    character_replace_button.set_tooltip("選択したキャラクターを控えメンバーで置き換える。", delay=0.1, wrap_width=300)

    use_item_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((900, 480), (156, 35)),
                                        text='Equip Item',
                                        manager=ui_manager,
                                        tool_tip_text = "Use selected item for selected character.")
    use_item_button.set_tooltip("選択したアイテムを選択したキャラクターに使用する。選択したアイテムが装備品の場合は、選択したキャラクターに装備する。一度に複数のアイテムを装備または使用することもできる。",
                                delay=0.1, wrap_width=300)
    item_sell_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((900, 520), (156, 35)),
                                        text='Sell Item',
                                        manager=ui_manager,
                                        tool_tip_text = "Sell selected item in inventory.")
    item_sell_button.set_tooltip("選択したアイテムをインベントリから一つ売却する。", delay=0.1, wrap_width=300)
    item_sell_button.hide()
    item_sell_half_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((900, 560), (156, 35)),
                                        text='Sell Half',
                                        manager=ui_manager,
                                        tool_tip_text = "Sell half stack of selected item in inventory.")
    item_sell_half_button.set_tooltip("選択したアイテムの半分のスタックを売却する。", delay=0.1, wrap_width=300)
    item_sell_half_button.hide()
    use_random_consumable_label = pygame_gui.elements.UILabel(pygame.Rect((1080, 420), (156, 35)),
                                        "Random Use:",
                                        ui_manager)
    use_random_consumable_label.set_tooltip("自動バトル中に毎ターン、一つの適切な消耗品を使用する。", delay=0.1, wrap_width=300)
    use_random_consumable_label.hide()
    use_random_consumable_selection_menu = pygame_gui.elements.UIDropDownMenu(["True", "False"],
                                                            "False",
                                                            pygame.Rect((1080, 460), (156, 35)),
                                                            ui_manager)
    use_random_consumable_selection_menu.hide()
    sliver_ingot_exchange_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((1080, 420), (156, 35)),
                                        text='Buy Sliver Ingot',
                                        manager=ui_manager,
                                        tool_tip_text = "Exchange Sliver Ingot")
    sliver_ingot_exchange_button.set_tooltip("スライバー・インゴットを現金で買う、価格：111000", delay=0.1, wrap_width=300)
    sliver_ingot_exchange_button.hide()
    gold_ingot_exchange_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((1080, 460), (156, 35)),
                                        text='Buy Gold Ingot',
                                        manager=ui_manager,
                                        tool_tip_text = "Exchange Gold Ingot")
    gold_ingot_exchange_button.set_tooltip("現金で金のインゴットを買う, 価格: 9820000", delay=0.1, wrap_width=300)
    gold_ingot_exchange_button.hide()


    def use_item():
        # Nine.selected_item = {} # {image_slot: UIImage : (image: Surface, is_highlighted: bool, the_actual_item: Equip|Consumable|Item)})}
        # get all selected items
        text_box.set_text("==============================\n")
        text_box_text_to_append = ""
        selected_items = []
        # print(player.selected_item)
        if not player.selected_item:
            text_box_text_to_append += "アイテムが選択されていない。\n"
            text_box.append_html_text(text_box_text_to_append)
            return
        for a, b, c in player.selected_item.values():
            if b:
                selected_items.append(c) 
        # print(f"use_item() Selected items: {selected_items}")
        if not selected_items:
            text_box_text_to_append += "アイテムが選択されていない。\n"
            text_box.append_html_text(text_box_text_to_append)
            return
        if cheap_inventory_show_current_option == "Equip":
            if not is_in_manipulatable_game_states():
                text_box_text_to_append += "最初のターンでないときや戦闘終了後はアイテムを装備できない。\n"
                text_box.append_html_text(text_box_text_to_append)
                return
            for character in all_characters:
                if character.name == character_selection_menu.selected_option.split()[-1] and character.is_alive():
                    # check if selected items have more than 1 of the same type
                    item_types_seen = []
                    for item in selected_items:
                        if item.type in item_types_seen:
                            text_box_text_to_append += f"同じ種類のアイテムを一度に複数装備することはできない。\n"
                            text_box.append_html_text(text_box_text_to_append)
                            return
                        else:
                            item_types_seen.append(item.type)

                    for equip in selected_items:
                        text_box_text_to_append += f"{str(equip)}が{character.name}に装備した。\n"
                    old_items = character.equip_item_from_list(selected_items)
                    # remove all None in old_items, this happens when trying to equip to an empty slot, so None is returned
                    old_items = [x for x in old_items if x]
                    if old_items:
                        for items in old_items:
                            text_box_text_to_append += f"{str(items)}が在庫に追加された。\n"
                        player.remove_selected_item_from_inventory(False) # False because handled next line
                        player.add_package_of_items_to_inventory(old_items)
                    else:
                        player.remove_selected_item_from_inventory(True)
                elif character.name == character_selection_menu.selected_option.split()[-1] and not character.is_alive():
                    text_box_text_to_append += f"アイテムは生きているキャラクターにしか装備できない。\n"
                    text_box.append_html_text(text_box_text_to_append)
                    return
        elif cheap_inventory_show_current_option == "Consumable":
            for character in all_characters:
                if character.name == character_selection_menu.selected_option.split()[-1]:
                    for consumable in selected_items:
                        if not consumable.can_use_on_dead and not character.is_alive():
                            text_box_text_to_append += f"死んだキャラクターに{str(consumable)}は使えない。\n"
                            text_box.append_html_text(text_box_text_to_append)
                            return
                        event_str = consumable.E(character, player)
                        text_box_text_to_append += event_str + "\n"
                    player.use_1_selected_item(True)
        # Remember to change this if decided item can also be used on characters
        elif cheap_inventory_show_current_option == "Item":
            for item in selected_items:
                event_str = item.E(None, player)
                text_box_text_to_append += event_str + "\n"
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
            if not all_consumables:
                global_vars.turn_info_string += f"ランダム使用失敗：インベントリに消耗品が不足している。\n"
                return
            for consumable in all_consumables:
                if consumable.auto_E_condition(character, player):
                    event_str = consumable.E(character, player)
                    global_vars.turn_info_string += event_str + "\n"
                    player.remove_from_inventory(type(consumable), 1, True)
                    return
        global_vars.turn_info_string += f"ランダム使用失敗： どのキャラクターにも適した消耗品がない。\n"


    def item_sell_selected():
        text_box.set_text("==============================\n")
        selected_items = []
        if not player.selected_item:
            text_box.append_html_text("アイテムが選択されていない。\n")
            return
        for a, b, c in player.selected_item.values():
            if b:
                selected_items.append(c)
        if not selected_items:
            text_box.append_html_text("アイテムが選択されていない。\n")
            return

        for item_to_sell in selected_items:
            eq_market_value = int(item_to_sell.market_value)
            player.add_cash(eq_market_value, False)
            text_box.append_html_text(f"在庫の{item_to_sell.name}が売り、{eq_market_value}現金が入手した。\n")
            player.remove_from_inventory(type(item_to_sell), 1, False)
        player.build_inventory_slots()


    def item_sell_half():
        """
        Sell half stack of selected items in inventory
        """
        text_box.set_text("==============================\n")
        selected_items = []
        if not player.selected_item:
            text_box.append_html_text("アイテムが選択されていない。\n")
            return
        for a, b, c in player.selected_item.values():
            if b:
                selected_items.append(c)
        if not selected_items:
            text_box.append_html_text("アイテムが選択されていない。\n")
            return

        total_income = 0
        for item_to_sell in selected_items:
            amount_to_sell = item_to_sell.current_stack // 2
            if amount_to_sell == 0:
                text_box.append_html_text(f"{item_to_sell.name}が数量不足のため売ることができない。\n")
                continue
            item_market_value = int(item_to_sell.market_value)
            this_item_income = item_market_value * amount_to_sell
            total_income += this_item_income
            text_box.append_html_text(f"在庫の{amount_to_sell}{item_to_sell.name}が売り、{this_item_income}の現金を得た。\n")
            player.remove_from_inventory(type(item_to_sell), amount_to_sell, False)
        
        text_box.append_html_text(f"合計所得：{total_income}現金。\n")
        player.add_cash(total_income, True)


    def item_trade(item: str, amount: int=1):
        text_box.set_text("==============================\n")
        match item:
            case "Sliver Ingot":
                if player.get_cash() < 111000 * amount:
                    text_box.append_html_text(f"スライバー・インゴットを{amount}個買うのに十分な現金がありません。\n")
                    return
                player.add_to_inventory(SliverIngot(amount), False)
                player.lose_cash(111000 * amount, True)
                text_box.append_html_text(f"{amount}個のスライバー・インゴットを{111000 * amount}現金で購入しました。\n")
            case "Gold Ingot":
                if player.get_cash() < 9820000 * amount:
                    text_box.append_html_text(f"金のインゴットを{amount}個買うのに十分な現金がありません。\n")
                    return
                player.add_to_inventory(GoldIngot(amount), False)
                player.lose_cash(9820000 * amount, True)
                text_box.append_html_text(f"{amount}個の金のインゴットを{9820000 * amount}現金で購入しました。\n")
            case _:
                raise ValueError(f"Invalid item: {item}")


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
    character_eq_unequip_button.set_tooltip("選択したキャラクターから装備品を外す。", delay=0.1, wrap_width=300)

    def unequip_item():
        text_box.set_text("==============================\n")
        if not is_in_manipulatable_game_states():
            text_box.append_html_text("最初のターンでないときや戦闘終了後はアイテムを外せない。\n")
            return
        for character in all_characters:
            if character.name == character_selection_menu.selected_option.split()[-1] and character.is_alive():
                item_type = eq_selection_menu.selected_option
                unequipped_item = character.unequip_item(item_type, False)
                if unequipped_item:
                    text_box.append_html_text(f"{character.name}から{item_type}を外した。\n")
                    player.add_to_inventory(unequipped_item)
                else:
                    text_box.append_html_text(f"{character.name}が{item_type}を装備していない。\n")
                redraw_ui(party1, party2)
                return
            elif character.name == character_selection_menu.selected_option.split()[-1] and not character.is_alive():
                text_box.append_html_text(f"生きているキャラクターからしかアイテムを装備解除できない。\n")
                return


    eq_stars_upgrade_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((1080, 420), (156, 35)),
                                        text='Star Enhancement',
                                        manager=ui_manager,
                                        tool_tip_text = "Upgrade stars for item")
    eq_stars_upgrade_button.set_tooltip("インベントリ内の選択した装備品のスターランクを上げる。", delay=0.1, wrap_width=300)

    def eq_stars_upgrade(is_upgrade: bool):
        text_box.set_text("==============================\n")
        text_box_text_to_append = ""
        selected_items = []
        # print(player.selected_item)
        if not player.selected_item:
            text_box_text_to_append += "アイテムが選択されていない。\n"
            text_box.append_html_text(text_box_text_to_append)
            return
        for a, b, c in player.selected_item.values():
            if b:
                selected_items.append(c) 
        if not selected_items:
            text_box_text_to_append += "アイテムが選択されていない。\n"
            text_box.append_html_text(text_box_text_to_append)
            return
        
        cost_total = int(sum([item_to_upgrade.star_enhence_cost for item_to_upgrade in selected_items]))
        if player.get_cash() < cost_total:
            text_box_text_to_append += "スターランクの強化に必要な現金が足りません。\n"
            text_box.append_html_text(text_box_text_to_append)
            return
        
        for item_to_upgrade in selected_items:
            if item_to_upgrade.stars_rating == item_to_upgrade.stars_rating_max and is_upgrade:
                text_box_text_to_append += f"最大スターランクに到達した: {str(item_to_upgrade)}\n"
                continue
            if item_to_upgrade.stars_rating == 0 and not is_upgrade:
                text_box_text_to_append += f"最小スターランクに到達した: {str(item_to_upgrade)}\n"
                continue
            a, b = item_to_upgrade.upgrade_stars_func(is_upgrade) 
            text_box_text_to_append += f"{item_to_upgrade}をアップグレードする。\n"
            text_box_text_to_append += f"スターランク: {int(a)} -> {int(b)}\n"
            for k, (a, b, c) in player.selected_item.items():
                if c == item_to_upgrade:
                    k.set_tooltip(item_to_upgrade.print_stats_html(), delay=0.1, wrap_width=300)
        if cost_total > 0:
            player.lose_cash(cost_total, False)
            text_box_text_to_append += f"{cost_total}現金で{len(selected_items)}個のアイテムをアップグレードした。\n"
        text_box.append_html_text(text_box_text_to_append)

    eq_levelup_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((1080, 460), (156, 35)),
                                        text='Level Up',
                                        manager=ui_manager,
                                        tool_tip_text = "Level up selected item.")
    eq_levelup_button.set_tooltip("インベントリ内の選択した装備品をレベルアップする。", delay=0.1, wrap_width=300)

    def eq_level_up(is_level_up: bool = True):
        text_box.set_text("==============================\n")
        text_box_text_to_append = ""
        selected_items = []
        if not player.selected_item:
            text_box_text_to_append += "アイテムが選択されていない。\n"
            text_box.append_html_text(text_box_text_to_append)
            return
        for a, b, c in player.selected_item.values():
            if b:
                selected_items.append(c)
        if not selected_items:
            text_box_text_to_append += "アイテムが選択されていない。\n"
            text_box.append_html_text(text_box_text_to_append)
            return

        cost_total = int(sum([item_to_upgrade.level_cost for item_to_upgrade in selected_items]))
        if player.get_cash() < cost_total:
            text_box_text_to_append += "装備のレベルアップのための資金が足りない。\n"
            text_box.append_html_text(text_box_text_to_append)
            return

        for item_to_level_up in selected_items:
            if item_to_level_up.level >= item_to_level_up.level_max and is_level_up:
                text_box_text_to_append += f"最大レベルに到達した：{str(item_to_level_up)}\n"
                continue
            if item_to_level_up.level <= 0 and not is_level_up:
                text_box_text_to_append += f"最少レベルに到達した：{str(item_to_level_up)}\n"
                continue
            text_box_text_to_append += f"レベリング{'アップ' if is_level_up else 'ダウン'} {item_to_level_up}。\n"
            a, b = item_to_level_up.level_change(1 if is_level_up else -1)
            text_box_text_to_append += f"レベル：{int(a)} -> {int(b)}\n"
            for k, (a, b, c) in player.selected_item.items():
                if c == item_to_level_up:
                    k.set_tooltip(item_to_level_up.print_stats_html(), delay=0.1, wrap_width=300)
        if cost_total > 0:
            player.lose_cash(cost_total, False)
            text_box_text_to_append += f"{len(selected_items)}個のアイテムが{cost_total}現金でレベルアップした。\n"
        text_box.append_html_text(text_box_text_to_append)

    
    eq_sell_selected_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((1080, 500), (156, 35)),
                                        text='Sell Selected',
                                        manager=ui_manager,
                                        tool_tip_text = "Sell selected item.")
    eq_sell_selected_button.set_tooltip("インベントリ内の選択した装備品を売却する。", delay=0.1, wrap_width=300)

    def eq_sell_selected():
        text_box.set_text("==============================\n")
        selected_items = []
        if not player.selected_item:
            text_box.append_html_text("アイテムが選択されていない。\n")
            return
        for a, b, c in player.selected_item.values():
            if b:
                selected_items.append(c)
        if not selected_items:
            text_box.append_html_text("アイテムが選択されていない。\n")
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
    eq_sell_low_value_button.set_tooltip("インベントリ内の装備品が市場価値以下のものを売却する。", delay=0.1, wrap_width=300)


    def eq_sell_low_value(sell_value_below: int):
        # sell half of all equipment, sorted by market value
        text_box.set_text("==============================\n")
        eq_to_sell = [x for x in player.inventory if isinstance(x, Equip) and x.market_value <= sell_value_below]
        total_income = 0
        if not eq_to_sell:
            text_box.append_html_text(f"市場価格{sell_value_below}以下の装備品がない。\n")
            return
        for eq in eq_to_sell.copy():
            total_income += int(eq.market_value)
            player.inventory.remove(eq)
        player.add_cash(total_income, False)
        text_box.append_html_text(f"{len(eq_to_sell)}装備品が{total_income}現金で売却された。\n")
        player.build_inventory_slots()


    eq_level_up_to_max_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((1080, 620), (156, 35)),
                                        text='Level Up To Max',
                                        manager=ui_manager,
                                        tool_tip_text = "Try level up selected item to max level until Cash is exhausted.")
    eq_level_up_to_max_button.set_tooltip("インベントリ内の選択した装備品を最大レベルまでレベルアップする。", delay=0.1, wrap_width=300)

    def eq_level_up_to_max():
        text_box.set_text("==============================\n")
        selected_items = []
        if not player.selected_item:
            text_box.append_html_text("アイテムが選択されていない。\n")
            return
        for a, b, c in player.selected_item.values():
            if b:
                selected_items.append(c)
        if not selected_items:
            text_box.append_html_text("アイテムが選択されていない。\n")
            return

        for item_to_level_up in selected_items:
            available_cash = player.get_cash()
            remaining_funds, cost = item_to_level_up.level_up_as_possible(available_cash)
            if cost:
                player.lose_cash(cost, False)
                text_box.append_html_text(f"インベントリ内の{item_to_level_up}を{cost}現金でレベルアップしました。\n")
            else:
                text_box.append_html_text(f"インベントリ内の{item_to_level_up}をレベルアップできません。\n")
            for k, (a, b, c) in player.selected_item.items():
                if c == item_to_level_up:
                    k.set_tooltip(item_to_level_up.print_stats_html(), delay=0.1, wrap_width=300)




    # =====================================
    # End of Equip Section
    # =====================================
    # Cheap Inventory Section
    # =====================================

    # Cheap inventory system is just a bunch of 32 by 32 image slots pointing to player's inventory
    # 10 rows, 6 columns
    # each row and column have a empty space of 8 pixels

    cheap_inventory_show_equipment_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((1080, 20), (156, 35)),
                                        text='Show Equipment',
                                        manager=ui_manager,
                                        tool_tip_text = "Show equipment in inventory")
    cheap_inventory_show_equipment_button.set_tooltip("インベントリ内の装備品を表示する。", delay=0.1, wrap_width=300)

    cheap_inventory_show_items_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((1080, 60), (156, 35)),
                                        text='Show Items',
                                        manager=ui_manager,
                                        tool_tip_text = "Show items in inventory")
    cheap_inventory_show_items_button.set_tooltip("インベントリ内のアイテムを表示する。", delay=0.1, wrap_width=300)
    
    cheap_inventory_show_consumables_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((1080, 100), (156, 35)),
                                        text='Show Consumables',
                                        manager=ui_manager,
                                        tool_tip_text = "Show consumables in inventory")
    cheap_inventory_show_consumables_button.set_tooltip("インベントリ内の消耗品を表示する。", delay=0.1, wrap_width=300)
    cheap_inventory_show_current_option = "Equip"

    cheap_inventory_sort_by_selection_menu = pygame_gui.elements.UIDropDownMenu(["Rarity", "Type", "Set", "Level", "Market Value", "BOGO"],
                                                            "Rarity",
                                                            pygame.Rect((1300, 20), (230, 35)),
                                                            ui_manager)

    cheap_inventory_sort_by_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((1300, 60), (230, 35)),
                                        text='Sort',
                                        manager=ui_manager,
                                        tool_tip_text = "Sort inventory by selected option")
    cheap_inventory_sort_by_button.set_tooltip("選択したオプションでインベントリをソートする。", delay=0.1, wrap_width=300)

    def cheap_inventory_sort():
        match cheap_inventory_sort_by_selection_menu.selected_option:
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
                print(f"Warning: Unknown option: {cheap_inventory_sort_by_selection_menu.selected_option}")


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
    cheap_inventory_skip_to_first_page_button.set_tooltip("インベントリの最初のページに移動する。", delay=0.1, wrap_width=300)
    cheap_inventory_previous_page_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((1300, 100), (50, 35)),
                                        text='<',
                                        manager=ui_manager,
                                        tool_tip_text = "Previous page of inventory")
    cheap_inventory_previous_page_button.set_tooltip("インベントリの前のページに移動する。", delay=0.1, wrap_width=300)
    cheap_inventory_skip_to_last_page_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((1480, 140), (50, 35)),
                                        text='>>',
                                        manager=ui_manager,
                                        tool_tip_text = "Skip to last page of inventory")
    cheap_inventory_skip_to_last_page_button.set_tooltip("インベントリの最後のページに移動する。", delay=0.1, wrap_width=300)
    cheap_inventory_next_page_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((1480, 100), (50, 35)),
                                        text='>',
                                        manager=ui_manager,
                                        tool_tip_text = "Next page of inventory")
    cheap_inventory_next_page_button.set_tooltip("インベントリの次のページに移動する。", delay=0.1, wrap_width=300)

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


    def next_turn(party1, party2):
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
        if auto_battle_active and use_random_consumable_selection_menu.selected_option == "True":
            use_random_consumable()

        reset_ally_enemy_attr(party1, party2)
        for character in itertools.chain(party1, party2):
            character.update_ally_and_enemy()
            character.status_effects_start_of_turn()
            character.record_battle_turns()

        if not is_someone_alive(party1) or not is_someone_alive(party2):

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
                    shield_value_diff_dict=shield_value_diff)

            for character in itertools.chain(party1, party2):
                character.record_damage_taken() # Empty damage_taken this turn and add to damage_taken_history
                character.record_healing_received() 

            if not is_someone_alive(party1):
                if current_game_mode == "Adventure Mode":
                    global_vars.turn_info_string += "失敗。\n"
                else:
                    global_vars.turn_info_string += "パーティ1が敗北しました。\n"
            elif not is_someone_alive(party2):
                if current_game_mode == "Adventure Mode":
                    global_vars.turn_info_string += "勝利！\n"
                    player.cleared_stages = adventure_mode_current_stage
                    # パーティ1の生存キャラクターに経験値を与える
                    for character in party1:
                        if character.is_alive():
                            character.gain_exp(adventure_mode_exp_reward())
                            global_vars.turn_info_string += f"{character.name}は{adventure_mode_exp_reward()}の経験値を獲得しました。\n"
                    cash_reward, cash_reward_no_random = adventure_mode_cash_reward()
                    player.add_cash(cash_reward)
                    global_vars.turn_info_string += f"{cash_reward}現金を獲得しました。\n"
                else:
                    global_vars.turn_info_string += "パーティ2が敗北しました。\n"
            text_box.append_html_text(global_vars.turn_info_string)
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

        if not is_someone_alive(party1) or not is_someone_alive(party2):

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
                    shield_value_diff_dict=shield_value_diff)

            for character in itertools.chain(party1, party2):
                character.record_damage_taken() # Empty damage_taken this turn and add to damage_taken_history
                character.record_healing_received() 

            if not is_someone_alive(party1):
                if current_game_mode == "Adventure Mode":
                    global_vars.turn_info_string += "失敗。\n"
                else:
                    global_vars.turn_info_string += "パーティ1が敗北しました。\n"    
            elif not is_someone_alive(party2):
                if current_game_mode == "Adventure Mode":
                    text_box.append_html_text("勝利！\n")
                    player.cleared_stages = adventure_mode_current_stage
                    # gain exp for alive characters in party 1
                    for character in party1:
                        if character.is_alive():
                            character.gain_exp(adventure_mode_exp_reward())
                            global_vars.turn_info_string += f"{character.name}は{adventure_mode_exp_reward()}の経験値を獲得しました。\n"
                    cash_reward, cash_reward_no_random = adventure_mode_cash_reward()
                    player.add_cash(cash_reward)
                    global_vars.turn_info_string += f"{cash_reward}現金を獲得しました。\n"
                else:
                    global_vars.turn_info_string += "パーティ2が敗北しました。\n"
            text_box.append_html_text(global_vars.turn_info_string)
            return False
        
        alive_characters = [x for x in itertools.chain(party1, party2) if x.is_alive()]
        weight = [x.spd for x in alive_characters]
        the_chosen_one = random.choices(alive_characters, weights=weight, k=1)[0]
        global_vars.turn_info_string += f"{the_chosen_one.name}のターン.\n"
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

        redraw_ui(party1, party2, refill_image=True, main_char=the_chosen_one, 
                  buff_added_this_turn=buff_applied_this_turn, debuff_added_this_turn=debuff_applied_this_turn,
                  shield_value_diff_dict=shield_value_diff, redraw_eq_slots=False)

        for character in itertools.chain(party1, party2):
            character.record_damage_taken() # Empty damage_taken this turn and add to damage_taken_history
            character.record_healing_received() 

        if not is_someone_alive(party1) or not is_someone_alive(party2):

            if not is_someone_alive(party1):
                if current_game_mode == "Adventure Mode":
                    global_vars.turn_info_string += "失敗。\n"
                else:
                    global_vars.turn_info_string += "パーティ1が敗北しました。\n"
            elif not is_someone_alive(party2):
                if current_game_mode == "Adventure Mode":
                    global_vars.turn_info_string += "勝利！\n"
                    player.cleared_stages = adventure_mode_current_stage
                    # gain exp for alive characters in party 1
                    for character in party1:
                        if character.is_alive():
                            character.gain_exp(adventure_mode_exp_reward())
                            text_box.append_html_text(f"{character.name}は{adventure_mode_exp_reward()}の経験値を獲得しました。\n")
                    cash_reward, cash_reward_no_random = adventure_mode_cash_reward()
                    player.add_cash(cash_reward)
                    global_vars.turn_info_string += f"{cash_reward}現金を獲得しました。\n"
                else:
                    global_vars.turn_info_string += "パーティ2が敗北しました。\n"
            text_box.append_html_text(global_vars.turn_info_string)
            return False
        text_box.append_html_text(global_vars.turn_info_string)
        return True


    def all_turns(party1, party2):
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

            turn += 1

        redraw_ui(party1, party2, redraw_eq_slots=False)

        text_box.set_text("=====================================\n")
        text_box.append_html_text(f"Turn {turn}\n")

        if turn >= 300:
            text_box.append_html_text("Battle is taking too long.\n")
        elif not is_someone_alive(party1) and not is_someone_alive(party2):
            text_box.append_html_text("Both parties are defeated.\n")
        elif not is_someone_alive(party1):
            if current_game_mode == "Adventure Mode":
                text_box.append_html_text("失敗。\n")
            else:
                text_box.append_html_text("パーティー1が敗れた。\n")
        elif not is_someone_alive(party2):
            if current_game_mode == "Adventure Mode":
                text_box.append_html_text("勝利！\n")
            else:
                text_box.append_html_text("パーティー2が敗れた。\n")


    def restart_battle():
        global turn
        global_vars.turn_info_string = ""
        for character in all_characters + all_monsters:
            character.reset_stats()
        reset_ally_enemy_attr(party1, party2)
        global_vars.turn_info_string += "戦闘開始効果：\n"
        for character in party1:
            character.battle_entry_effects_activate()
        for character in party2:
            character.battle_entry_effects_activate()
        redraw_ui(party1, party2, redraw_eq_slots=False)
        turn = 1
        text_box.append_html_text(global_vars.turn_info_string)

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
        global_vars.turn_info_string += "戦闘開始効果：\n"
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
        global_vars.turn_info_string += "戦闘開始効果：\n"
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
        text_box.append_html_text(f"{character_name}は{new_character_name}に置き換えられました。\n")

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
        font = pygame.font.Font('./NotoSansJP-Regular.ttf', font_size)
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
                         shield_bar_color=(252, 248, 15)) -> pygame.Surface:
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
        """
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

        create_yellow_text(surface, f"{hp}/{maxhp}", 20, position_type='center', text_color=(0, 0, 0))

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


    def redraw_ui(party1, party2, *, refill_image=True, main_char=None,
                  buff_added_this_turn=None, debuff_added_this_turn=None, shield_value_diff_dict=None, redraw_eq_slots=True,
                  ):

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
                    equip_effect_slots[i].set_tooltip(character.equipment_set_effects_tooltip(), delay=0.1, wrap_width=300)
                else:
                    equip_effect_slots[i].hide()

                labels[i].set_text(f"lv {character.lvl} {character.name}")
                labels[i].set_tooltip(character.skill_tooltip(), delay=0.1, wrap_width=500)
                labels[i].set_text_alpha(255) if character.is_alive() else labels[i].set_text_alpha(125)
                healthbar[i].set_image(create_healthbar(character.hp, character.maxhp, 176, 30, shield_value=character.get_shield_value()))
                healthbar[i].set_tooltip(character.tooltip_status_effects(), delay=0.1, wrap_width=300)

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
                                create_yellow_text(new_image, str(a), 20, (255, 0, 0), current_offset_for_damage_and_healing)
                            case "status":
                                # orange text
                                create_yellow_text(new_image, str(a), 20, (255, 165, 0), current_offset_for_damage_and_healing)
                            case "normal_critical":
                                create_yellow_text(new_image, str(a), 20, (255, 0, 0), current_offset_for_damage_and_healing, bold=True, italic=True)
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
                        create_yellow_text(new_image, str(healing), 20, (0, 255, 0), current_offset_for_damage_and_healing)
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
                        create_yellow_text(image_slots[i].image, str(int(value)), 20, (192, 192, 192), 10, 'bottomleft')

                if character.is_alive():
                    top_right_offset = 10
                    if character.is_charmed():
                        create_yellow_text(image_slots[i].image, "魅了", 15, (255, 0, 0), top_right_offset, 'topright')
                        top_right_offset += 10
                    if character.is_confused():
                        create_yellow_text(image_slots[i].image, "混乱", 15, (255, 0, 0), top_right_offset, 'topright')
                        top_right_offset += 10
                    if character.is_stunned():
                        create_yellow_text(image_slots[i].image, "スタン", 15, (255, 0, 0), top_right_offset, 'topright')
                        top_right_offset += 10
                    if character.is_silenced():
                        create_yellow_text(image_slots[i].image, "沈黙", 15, (255, 0, 0), top_right_offset, 'topright')
                        top_right_offset += 10
                    if character.is_sleeping():
                        create_yellow_text(image_slots[i].image, "睡眠", 15, (255, 0, 0), top_right_offset, 'topright')
                        top_right_offset += 10
                    if character.is_frozed():
                        create_yellow_text(image_slots[i].image, "凍結", 15, (255, 0, 0), top_right_offset, 'topright')
                        top_right_offset += 10



        redraw_party(party1, image_slots_party1, equip_slot_party1_weapon, equip_slot_party1_armor, equip_slot_party1_accessory, equip_slot_party1_boots,
                     label_party1, health_bar_party1, equip_set_slot_party1)
        redraw_party(party2, image_slots_party2, equip_slot_party2_weapon, equip_slot_party2_armor, equip_slot_party2_accessory, equip_slot_party2_boots,
                     label_party2, health_bar_party2, equip_set_slot_party2)

    # =====================================
    # Text Entry Box Section
    # =====================================
    text_box = pygame_gui.elements.UITextEntryBox(pygame.Rect((300, 300), (556, 295)),"", ui_manager)
    text_box_introduction_text = "キャラクター名にカーソルを合わせるとスキル情報が表示されます。\n"
    text_box_introduction_text += "小文字の character_name.jpg または png ファイルが ./image/character ディレクトリに見つからない場合、404.png が使用されます。\n"
    text_box_introduction_text += "小文字の item_name.jpg または png ファイルが ./image/item ディレクトリに見つからない場合、404.png が使用されます。\n"
    text_box_introduction_text += "小文字の monster_original_name.jpg または png ファイルが ./image/monster ディレクトリに見つからない場合、404.png が使用されます。\n"
    text_box_introduction_text += "キャラクター画像にカーソルを合わせるとキャラクターステータスが表示されます。\n"
    text_box_introduction_text += "キャラクターのHPバーにカーソルを合わせると異常状態効果が表示されます。\n"
    text_box.set_text(text_box_introduction_text)

    box_submenu_previous_stage_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((300, 560), (120, 35)),
                                                                    text='Previous Stage',
                                                                    manager=ui_manager)
    box_submenu_previous_stage_button.set_tooltip("前のステージに戻る。", delay=0.1)

    box_submenu_next_stage_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((425, 560), (120, 35)),
                                                                    text='Next Stage',
                                                                    manager=ui_manager)
    box_submenu_next_stage_button.set_tooltip("次のステージに進む。現在のステージがクリアされている場合のみ進むことができます。", delay=0.1)
    box_submenu_previous_stage_button.hide()
    box_submenu_next_stage_button.hide()
    box_submenu_stage_info_label = pygame_gui.elements.UILabel(relative_rect=pygame.Rect((550, 560), (80, 35)),
                                                                    text='Current Stage: 1',
                                                                    manager=ui_manager)
    box_submenu_stage_info_label.hide()
    box_submenu_explore_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((635, 560), (120, 35)),
                                                                    text='Explore',
                                                                    manager=ui_manager)
    box_submenu_explore_button.set_tooltip("選択した資金で世界を探索する。ランダムなアイテムを報酬として獲得しますが、1つのアイテムの価値は資金の2倍以上になることはない。", delay=0.1, wrap_width=300)
    box_submenu_explore_button.hide()

    box_submenu_explore_funds_selection = pygame_gui.elements.UIDropDownMenu(["50", "100", "200", "500", "1000", "5000", "10000"],
                                                                    "200",
                                                                    pygame.Rect((760, 560), (100, 35)),
                                                                    ui_manager)
    box_submenu_explore_funds_selection.hide()

    def explore_generate_package_of_items_to_desired_value(desired_market_value: float) -> list:
        package = []
        while True:
            while True:
                # single item cannot be twice more valueable than the funds
                coin = random.choice([1, 2])
                match coin:
                    case 1:
                        new_item = adventure_generate_random_equip_with_weight() # This function is incredibly greedy, we should consider using the next line.
                        # new_item = generate_equips_list(1, eq_level=1)[0] # Good gacha
                    case 2:
                        new_item = get_1_random_consumable()
                if new_item.market_value <= desired_market_value * 2:
                    break
            package.append(new_item)
            if sum([x.market_value for x in package]) >= desired_market_value:
                break
        return package

    def explore_brave_new_world():
        global player, text_box
        if player.get_cash() < int(box_submenu_explore_funds_selection.selected_option):
            text_box.set_text("現金が足りない。\n")
            return

        desired_market_value = int(box_submenu_explore_funds_selection.selected_option)
        package = explore_generate_package_of_items_to_desired_value(desired_market_value)
        text_box.set_text("下記のアイテムを獲得した：\n")
        text_box_text = ""
        for item in package:
            text_box_text += f"{str(item)}、価値：現金{int(item.market_value)}。\n"
        player.add_package_of_items_to_inventory(package)

        text_box_text += f"{int(box_submenu_explore_funds_selection.selected_option)}現金を消費し、獲得したアイテムの合計価値は現金{int(sum([x.market_value for x in package]))}。\n"
        text_box.append_html_text(text_box_text)
        player.lose_cash(int(box_submenu_explore_funds_selection.selected_option))


    # =====================================
    # End of Text Entry Box Section
    # =====================================

    # Event loop
    # ==========================
    running = True 
    # for c in all_characters + all_monsters:
        # c.equip_item_from_list(generate_equips_list(4, random_full_eqset=True)) 

    party1 = []
    party2 = []
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
                if image_slot10.get_abs_rect().collidepoint(event.pos):
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
                if event.ui_element == button_left_clear_board:
                    text_box.set_text("==============================\n")
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
                        box_submenu_explore_button.show()
                        box_submenu_explore_funds_selection.show()
                    elif current_game_mode == "Adventure Mode":
                        current_game_mode = "Training Mode"
                        party1, party2 = set_up_characters()
                        turn = 1
                        switch_game_mode_button.set_text("Adventure Mode")
                        text_box.set_dimensions((556, 295))
                        box_submenu_previous_stage_button.hide()
                        box_submenu_next_stage_button.hide()
                        box_submenu_stage_info_label.hide()
                        box_submenu_explore_button.hide()
                        box_submenu_explore_funds_selection.hide()
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
                    replace_character_with_reserve_member(character_selection_menu.selected_option.split()[-1], reserve_character_selection_menu.selected_option.split()[-1])
                if event.ui_element == eq_levelup_button:
                    eq_level_up()
                if event.ui_element == eq_level_up_to_max_button:
                    eq_level_up_to_max()
                if event.ui_element == eq_sell_selected_button:
                    eq_sell_selected()
                if event.ui_element == eq_sell_low_value_button:
                    eq_sell_low_value(int(eq_sell_low_value_selection_menu.selected_option))
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
                if event.ui_element == cheap_inventory_show_equipment_button:
                    player.current_page = 0
                    cheap_inventory_show_current_option = "Equip"
                    player.build_inventory_slots()
                    use_item_button.set_text("Equip Item")
                    eq_selection_menu.show()
                    character_eq_unequip_button.show()
                    eq_levelup_button.show()
                    eq_level_up_to_max_button.show()
                    eq_stars_upgrade_button.show()
                    eq_sell_selected_button.show()
                    eq_sell_low_value_selection_menu.show()
                    eq_sell_low_value_button.show()
                    item_sell_button.hide()
                    item_sell_half_button.hide()
                    use_random_consumable_label.hide()
                    use_random_consumable_selection_menu.hide()
                    sliver_ingot_exchange_button.hide()
                    gold_ingot_exchange_button.hide()
                if event.ui_element == cheap_inventory_show_items_button:
                    player.current_page = 0
                    cheap_inventory_show_current_option = "Item"
                    player.build_inventory_slots()
                    use_item_button.set_text("Use Item")
                    eq_selection_menu.hide()
                    character_eq_unequip_button.hide()
                    eq_levelup_button.hide()
                    eq_level_up_to_max_button.hide()
                    eq_stars_upgrade_button.hide()
                    eq_sell_selected_button.hide()
                    eq_sell_low_value_selection_menu.hide()
                    eq_sell_low_value_button.hide()
                    item_sell_button.show()
                    item_sell_half_button.show()
                    use_random_consumable_label.hide()
                    use_random_consumable_selection_menu.hide()
                    sliver_ingot_exchange_button.show()
                    gold_ingot_exchange_button.show()
                if event.ui_element == cheap_inventory_show_consumables_button:
                    player.current_page = 0
                    cheap_inventory_show_current_option = "Consumable"
                    player.build_inventory_slots()
                    use_item_button.set_text("Use Item")
                    eq_selection_menu.hide()
                    character_eq_unequip_button.hide()
                    eq_levelup_button.hide()
                    eq_level_up_to_max_button.hide()
                    eq_stars_upgrade_button.hide()
                    eq_sell_selected_button.hide()
                    eq_sell_low_value_selection_menu.hide()
                    eq_sell_low_value_button.hide()
                    item_sell_button.show()
                    item_sell_half_button.show()
                    use_random_consumable_label.show()
                    use_random_consumable_selection_menu.show()
                    sliver_ingot_exchange_button.hide()
                    gold_ingot_exchange_button.hide()
                if event.ui_element == use_item_button:
                    use_item()
                if event.ui_element == item_sell_button:
                    item_sell_selected()
                if event.ui_element == item_sell_half_button:
                    item_sell_half()
                if event.ui_element == sliver_ingot_exchange_button:
                    item_trade("Sliver Ingot")
                if event.ui_element == gold_ingot_exchange_button:
                    item_trade("Gold Ingot")
                if event.ui_element == character_eq_unequip_button:
                    unequip_item()
                if event.ui_element == box_submenu_previous_stage_button:
                    adventure_mode_stage_decrease()
                    box_submenu_stage_info_label.set_text(f"Stage {adventure_mode_current_stage}")
                    box_submenu_stage_info_label.set_tooltip(adventure_mode_info_tooltip(), delay=0.1, wrap_width=300)
                if event.ui_element == box_submenu_next_stage_button:
                    adventure_mode_stage_increase()
                    box_submenu_stage_info_label.set_text(f"Stage {adventure_mode_current_stage}")
                    box_submenu_stage_info_label.set_tooltip(adventure_mode_info_tooltip(), delay=0.1, wrap_width=300)
                if event.ui_element == box_submenu_explore_button:
                    explore_brave_new_world()


            ui_manager.process_events(event)

        ui_manager.update(time_delta)
        display_surface.fill(light_yellow)
        ui_manager.draw_ui(display_surface)

        debug_ui_manager.update(time_delta)
        debug_ui_manager.draw_ui(display_surface)

        if auto_battle_active:
            time_acc += time_delta
            auto_battle_bar_progress = (time_acc/decide_auto_battle_speed()) # May impact performance
            if auto_battle_bar_progress > 1.0:
                time_acc = 0.0
                if not next_turn(party1, party2):
                    auto_battle_active = False
                    instruction = after_auto_battle_selection_menu.selected_option
                    if instruction == "何もしない":
                        pass
                    elif instruction == "バトル再開":
                        text_box.set_text("==============================\n")
                        restart_battle()
                        auto_battle_active = True
                    elif instruction == "パーティシャッフル":
                        text_box.set_text("==============================\n")
                        if current_game_mode == "Training Mode":
                            party1, party2 = set_up_characters()
                        elif current_game_mode == "Adventure Mode":
                            party1, party2 = set_up_characters_adventure_mode(True)
                        turn = 1
                        auto_battle_active = True
                else:
                    turn += 1
            auto_battle_bar.percent_full = auto_battle_bar_progress

        pygame.display.update()

    pygame.quit()
