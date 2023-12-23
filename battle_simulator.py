import os
from equip import *
from character import *
import copy
running = False
logging = True
text_box = None


# TODO:
# 1. Add attributes to character to get info on damage dealt and healing done # Too difficult to implement, abandoning...Done
# 2. Create graph to show damage dealt and healing done # Ignored
# 3. Add equipment set effect # Implementing...Done
# 4. Redesign UI, the location of the buttons are not good # Waiting...Delayed...Partially Done...Delayed
# 5. Add 'Guard' attribute as a counter to 'Penetration', equipment should have 'Guard' attribute # Waiting...Delayed
# Reason: We will add this when damage is becoming uncontrollablly high, due to inflation of stats and effects.
# 6. Equipment should have level attribute, allow scaling with characters. Minimum level is 1, maximum level is 1000. # Implementing...Done
# 7. Design web UI instead of pygame # Searching for a good framework...React...Delayed

#--------------------------------------------------------- 
#---------------------------------------------------------
def is_someone_alive(party):
    for character in party:
        if character.isAlive():
            return True
    return False

def start_of_battle_effects(party):
    # Iris effect
    if any(isinstance(character, Iris) for character in party):
        character_with_highest_atk = max(party, key=lambda char: getattr(char, 'atk', 0))
        character_with_highest_atk.applyEffect(CancellationShield("Cancellation Shield", -1, True, 0.1, cc_immunity=True, running=running, logging=logging, text_box=text_box))
    for character in party:
        # Equipment set effect
        # Already handled elsewhere.
        # Pheonix effect
        if isinstance(character, Pheonix):
            character.applyEffect(RebornEffect("Reborn", -1, True, 0.4, False))
        # Seth effect
        if isinstance(character, Seth):
            character.applyEffect(SethEffect("Passive Effect", -1, True, 0.01))
    # Taily effect
    taily = next((character for character in party if isinstance(character, Taily)), None)
    if taily:
        for c in party:
            if c != taily:
                c.applyEffect(ProtectedEffect("Blessing of Firewood", -1, True, False, taily, 0.6))
        

def mid_turn_effects(party1, party2): 
    # Fenrir effect
    for party in [party1, party2]:
        for character in party:
            neighbors = character.get_neighbor_allies_not_including_self()
            fenrir = next((ally for ally in neighbors if isinstance(ally, Fenrir)), None)
            if fenrir:
                if not character.hasEffect("Fluffy Protection"):
                    character.applyEffect(EffectShield1("Fluffy Protection", -1, True, 0.4, fenrir.atk, False))
            else:
                for buff in character.buffs:
                    if buff.name == "Fluffy Protection":
                        character.removeEffect(buff) 

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

#--------------------------------------------------------- 
#---------------------------------------------------------

average_party_level = 40
character1 = Cerberus("Cerberus", average_party_level)
character2 = Fenrir("Fenrir", average_party_level)
character3 = Clover("Clover", average_party_level)
character4 = Ruby("Ruby", average_party_level)
character5 = Olive("Olive", average_party_level)
character6 = Luna("Luna", average_party_level)
character7 = Freya("Freya", average_party_level)
character8 = Poppy("Poppy", average_party_level)
character9 = Lillia("Lillia", average_party_level)
character10 = Iris("Iris", average_party_level)
character11 = Pepper("Pepper", average_party_level)
character12 = Cliffe("Cliffe", average_party_level)
character13 = Pheonix("Pheonix", average_party_level)
character14 = Bell("Bell", average_party_level)
character15 = Taily("Taily", average_party_level)
character16 = Seth("Seth", average_party_level)

all_characters = [character1, character2, character3, character4, character5,
                    character6, character7, character8, character9, character10,
                        character11, character12, character13, character14, character15
                            , character16]

for character in all_characters:
    character.equip = generate_equips_list(4, random_full_eqset=True)
    character.running = running
    character.logging = logging
    character.text_box = text_box

# ---------------------------------------------------------
# ---------------------------------------------------------
if __name__ == "__main__":
    import pygame, pygame_gui
    pygame.init()
    clock = pygame.time.Clock()

    antique_white = pygame.Color("#FAEBD7")
    deep_dark_blue = pygame.Color("#000022")
    light_yellow = pygame.Color("#FFFFE0")

    display_surface = pygame.display.set_mode((1200, 900), flags=pygame.SCALED)
    ui_manager = pygame_gui.UIManager((1200, 900), "theme_light_yellow.json", starting_language='ja')

    pygame.display.set_caption("Battle Simulator")

    # Some Invisible Sprites for health bar, useless
    # =====================================
    class InvisibleSprite(pygame.sprite.Sprite):
        def __init__(self, color, width, height, health_capacity, current_health, *groups: pygame.sprite.AbstractGroup):
            super().__init__()
            self.image = pygame.Surface([width, height])
            self.image.fill(color)
            self.rect = self.image.get_rect()
            self.health_capacity = health_capacity
            self.current_health = current_health

        def update(self):
            pass


    invisible_sprites = [InvisibleSprite(deep_dark_blue, 1200, 900, 1000, 100) for _ in range(1, 11)]

    sprite_party1 = invisible_sprites[:5]
    sprite_party2 = invisible_sprites[5:]

    invisible_sprite1 = sprite_party1[0]
    invisible_sprite2 = sprite_party1[1]
    invisible_sprite3 = sprite_party1[2]
    invisible_sprite4 = sprite_party1[3]
    invisible_sprite5 = sprite_party1[4]
    invisible_sprite6 = sprite_party2[0]
    invisible_sprite7 = sprite_party2[1]
    invisible_sprite8 = sprite_party2[2]
    invisible_sprite9 = sprite_party2[3]
    invisible_sprite10 = sprite_party2[4]

    health_bar1 = pygame_gui.elements.UIScreenSpaceHealthBar(pygame.Rect((75, 220), (200, 30)),ui_manager,
                                                            invisible_sprite1)
    health_bar2 = pygame_gui.elements.UIScreenSpaceHealthBar(pygame.Rect((275, 220), (200, 30)),ui_manager,
                                                            invisible_sprite2)
    health_bar3 = pygame_gui.elements.UIScreenSpaceHealthBar(pygame.Rect((475, 220), (200, 30)),ui_manager,
                                                            invisible_sprite3)
    health_bar4 = pygame_gui.elements.UIScreenSpaceHealthBar(pygame.Rect((675, 220), (200, 30)),ui_manager,
                                                            invisible_sprite4)
    health_bar5 = pygame_gui.elements.UIScreenSpaceHealthBar(pygame.Rect((875, 220), (200, 30)),ui_manager,
                                                            invisible_sprite5)
    health_bar6 = pygame_gui.elements.UIScreenSpaceHealthBar(pygame.Rect((75, 825), (200, 30)),ui_manager,
                                                            invisible_sprite6)
    health_bar7 = pygame_gui.elements.UIScreenSpaceHealthBar(pygame.Rect((275, 825), (200, 30)),ui_manager,
                                                            invisible_sprite7)
    health_bar8 = pygame_gui.elements.UIScreenSpaceHealthBar(pygame.Rect((475, 825), (200, 30)),ui_manager,
                                                            invisible_sprite8)
    health_bar9 = pygame_gui.elements.UIScreenSpaceHealthBar(pygame.Rect((675, 825), (200, 30)),ui_manager,
                                                            invisible_sprite9)
    health_bar10 = pygame_gui.elements.UIScreenSpaceHealthBar(pygame.Rect((875, 825), (200, 30)),ui_manager,
                                                            invisible_sprite10)

    health_bar_party1 = [health_bar1, health_bar2, health_bar3, health_bar4, health_bar5]
    health_bar_party2 = [health_bar6, health_bar7, health_bar8, health_bar9, health_bar10]

    all_healthbar = health_bar_party1 + health_bar_party2

    # Some Images
    # =====================================
    # load all images in ./image directory
    image_files = [x[:-4] for x in os.listdir("./image") if x.endswith((".jpg", ".png"))]
    images = {}
    for name in image_files:
        image_path_jpg = f"image/{name}.jpg"
        image_path_png = f"image/{name}.png"

        try:
            if os.path.exists(image_path_jpg):
                images[name] = pygame.image.load(image_path_jpg)
            elif os.path.exists(image_path_png):
                images[name] = pygame.image.load(image_path_png)
            else:
                print(f"ファイル {name} は見つかりませんでした。")
        except Exception as e:
            print(f"画像 {name} の読み込み中にエラーが発生しました: {e}")


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

    equip_slotsb1 = pygame_gui.elements.UIImage(pygame.Rect((275, 50), (20, 20)),pygame.Surface((20, 20)),ui_manager)
    equip_slotsb2 = pygame_gui.elements.UIImage(pygame.Rect((275, 75), (20, 20)),pygame.Surface((20, 20)),ui_manager)

    equip_slotsc1 = pygame_gui.elements.UIImage(pygame.Rect((475, 50), (20, 20)),pygame.Surface((20, 20)),ui_manager)
    equip_slotsc2 = pygame_gui.elements.UIImage(pygame.Rect((475, 75), (20, 20)),pygame.Surface((20, 20)),ui_manager)

    equip_slotsd1 = pygame_gui.elements.UIImage(pygame.Rect((675, 50), (20, 20)),pygame.Surface((20, 20)),ui_manager)
    equip_slotsd2 = pygame_gui.elements.UIImage(pygame.Rect((675, 75), (20, 20)),pygame.Surface((20, 20)),ui_manager)

    equip_slotse1 = pygame_gui.elements.UIImage(pygame.Rect((875, 50), (20, 20)),pygame.Surface((20, 20)),ui_manager)
    equip_slotse2 = pygame_gui.elements.UIImage(pygame.Rect((875, 75), (20, 20)),pygame.Surface((20, 20)),ui_manager)

    equip_slotsf1 = pygame_gui.elements.UIImage(pygame.Rect((75, 650), (20, 20)),pygame.Surface((20, 20)),ui_manager)
    equip_slotsf2 = pygame_gui.elements.UIImage(pygame.Rect((75, 675), (20, 20)),pygame.Surface((20, 20)),ui_manager)

    equip_slotsg1 = pygame_gui.elements.UIImage(pygame.Rect((275, 650), (20, 20)),pygame.Surface((20, 20)),ui_manager)
    equip_slotsg2 = pygame_gui.elements.UIImage(pygame.Rect((275, 675), (20, 20)),pygame.Surface((20, 20)),ui_manager)

    equip_slotsh1 = pygame_gui.elements.UIImage(pygame.Rect((475, 650), (20, 20)),pygame.Surface((20, 20)),ui_manager)
    equip_slotsh2 = pygame_gui.elements.UIImage(pygame.Rect((475, 675), (20, 20)),pygame.Surface((20, 20)),ui_manager)

    equip_slotsi1 = pygame_gui.elements.UIImage(pygame.Rect((675, 650), (20, 20)),pygame.Surface((20, 20)),ui_manager)
    equip_slotsi2 = pygame_gui.elements.UIImage(pygame.Rect((675, 675), (20, 20)),pygame.Surface((20, 20)),ui_manager)

    equip_slotsj1 = pygame_gui.elements.UIImage(pygame.Rect((875, 650), (20, 20)),pygame.Surface((20, 20)),ui_manager)
    equip_slotsj2 = pygame_gui.elements.UIImage(pygame.Rect((875, 675), (20, 20)),pygame.Surface((20, 20)),ui_manager)

                                            
    equip_slot_party1 = [equip_slota1, equip_slotsb1, equip_slotsc1, equip_slotsd1, equip_slotse1]
    equip_slot_party2 = [equip_slotsf1, equip_slotsg1, equip_slotsh1, equip_slotsi1, equip_slotsj1]
    for slot in equip_slot_party1 + equip_slot_party2:
        slot.set_image(images["chopper_knife"])
    equip_set_slot_party1 = [equip_slota2, equip_slotsb2, equip_slotsc2, equip_slotsd2, equip_slotse2]
    equip_set_slot_party2 = [equip_slotsf2, equip_slotsg2, equip_slotsh2, equip_slotsi2, equip_slotsj2]
    for slot in equip_set_slot_party1 + equip_set_slot_party2:
        slot.set_image(images["KKKKK"])                                  

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

    button1 = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((100, 300), (156, 50)),
                                        text='Shuffle Party',
                                        manager=ui_manager,
                                        tool_tip_text = "Shuffle party and restart the battle")

    button2 = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((100, 360), (156, 50)),
                                        text='Next Turn',
                                        manager=ui_manager,
                                        tool_tip_text = "Simulate the next turn")

    button3 = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((100, 420), (156, 50)),
                                        text='All Turns',
                                        manager=ui_manager,
                                        tool_tip_text = "Skip to the end of the battle. May take a while.")

    button4 = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((100, 480), (156, 50)),
                                        text='Restart Battle',
                                        manager=ui_manager,
                                        tool_tip_text = "Restart battle")

    button5 = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((100, 540), (156, 50)),
                                        text='Quit',
                                        manager=ui_manager,
                                        tool_tip_text = "Quit")

    # =====================================
    # Character
    # =====================================

    character_selection_menu = pygame_gui.elements.UIDropDownMenu(["Option 1", "Option 2", "Option 3", "Option 4", "Option 5"],
                                                            "Option 1",
                                                            pygame.Rect((880, 300), (156, 35)),
                                                            ui_manager)

    reserve_character_selection_menu = pygame_gui.elements.UIDropDownMenu(["Option1"],
                                                            "Option1",
                                                            pygame.Rect((880, 340), (156, 35)),
                                                            ui_manager)

    character_replace_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((880, 380), (156, 35)),
                                        text='Replace',
                                        manager=ui_manager,
                                        tool_tip_text = "Replace selected character with reserve character")

    levelup_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((880, 420), (76, 35)),
                                        text='Lv +',
                                        manager=ui_manager,
                                        tool_tip_text = "Level up selected character")

    leveldown_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((958, 420), (76, 35)),
                                        text='Lv -',
                                        manager=ui_manager,
                                        tool_tip_text = "Level down selected character")
    
    # =====================================
    # Item
    # =====================================

    eq_rarity_list, eq_types_list, eq_set_list = Equip("Foo", "Weapon", "Common").get_raritytypeeqset_list()

    eq_selection_menu = pygame_gui.elements.UIDropDownMenu(eq_types_list,
                                                            eq_types_list[0],
                                                            pygame.Rect((880, 470), (156, 35)),
                                                            ui_manager)

    eq_rarity_selection_menu = pygame_gui.elements.UIDropDownMenu(["random"] + eq_rarity_list,
                                                            "random",
                                                            pygame.Rect((1040, 470), (156, 35)),
                                                            ui_manager)

    eq_set_list_selection_menu = pygame_gui.elements.UIDropDownMenu(["random"] + eq_set_list,
                                                            "random",
                                                            pygame.Rect((1040, 510), (156, 35)),
                                                            ui_manager)

    eq_reroll_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((1040, 550), (156, 35)),
                                        text='Generate',
                                        manager=ui_manager,
                                        tool_tip_text = "Reroll item")

    eq_upgrade_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((880, 510), (76, 35)),
                                        text='Star +',
                                        manager=ui_manager,
                                        tool_tip_text = "Upgrade stars for item")

    eq_downgrade_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((958, 510), (76, 35)),
                                            text='Star -',
                                            manager=ui_manager,
                                            tool_tip_text = "Downgrade stars for item")

    eq_levelup_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((880, 550), (76, 35)),
                                        text='Lv +',
                                        manager=ui_manager,
                                        tool_tip_text = "Level up selected item for selected character")

    eq_leveldown_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((958, 550), (76, 35)),
                                        text='Lv -',
                                        manager=ui_manager,
                                        tool_tip_text = "Level down selected item for selected character")

    def next_turn(party1, party2):
        global turn
        if not is_someone_alive(party1) or not is_someone_alive(party2):
            text_box.append_html_text("Battle is over.\n")
            return False
        text_box.append_html_text("=====================================\n")
        text_box.append_html_text(f"Turn {turn}\n")

        reset_ally_enemy_attr(party1, party2)
        for character in party1:
            character.updateAllyEnemy()
        for character in party2:
            character.updateAllyEnemy()

        for character in party1:
            character.updateEffects() # handle effect duration change and removal
        for character in party2:
            character.updateEffects()
        if not is_someone_alive(party1) or not is_someone_alive(party2):
            return False
        
        for character in party1:
            character.statusEffects() # for effects that have method applyEffectOnTrigger, trigger them
            if character.isAlive():
                character.regen()
        for character in party2:
            character.statusEffects()
            if character.isAlive():
                character.regen()

        reset_ally_enemy_attr(party1, party2)
        for character in party1:
            character.updateAllyEnemy()
        for character in party2:
            character.updateAllyEnemy()

        mid_turn_effects(party1, party2)

        if not is_someone_alive(party1) or not is_someone_alive(party2):
            return False
        alive_characters = [x for x in party1 + party2 if x.isAlive()]
        weight = [x.spd for x in alive_characters]
        the_chosen_one = random.choices(alive_characters, weights=weight, k=1)[0]
        text_box.append_html_text(f"{the_chosen_one.name}'s turn.\n")
        the_chosen_one.action()

        redraw_ui(party1, party2, refill_image=False, main_char=the_chosen_one)

        if not is_someone_alive(party1) or not is_someone_alive(party2):
            return False
        return True

    def all_turns(party1, party2):
        # Warning: Constant logging on text_box is slowing down the simulation
        global turn, logging
        while turn < 300 and is_someone_alive(party1) and is_someone_alive(party2):
            logging = False
            for c in all_characters:
                c.logging = False

            reset_ally_enemy_attr(party1, party2)
            for character in party1:
                character.updateAllyEnemy()
            for character in party2:
                character.updateAllyEnemy()

            for character in party1:
                character.updateEffects()
            for character in party2:
                character.updateEffects()
            if not is_someone_alive(party1) or not is_someone_alive(party2):
                break

            for character in party1:
                character.statusEffects()
                if character.isAlive():
                    character.regen()
            for character in party2:
                character.statusEffects()
                if character.isAlive():
                    character.regen()

            reset_ally_enemy_attr(party1, party2)
            for character in party1:
                character.updateAllyEnemy()
            for character in party2:
                character.updateAllyEnemy()
            
            mid_turn_effects(party1, party2)

            alive_characters = [x for x in party1 + party2 if x.isAlive()]
            weight = [x.spd for x in alive_characters]
            the_chosen_one = random.choices(alive_characters, weights=weight, k=1)[0]
            text_box.append_html_text(f"{the_chosen_one.name}'s turn.\n")
            the_chosen_one.action()
            turn += 1

        redraw_ui(party1, party2)

        logging = True
        for c in all_characters:
            c.logging = True
        text_box.set_text("Welcome to the battle simulator!\n")
        text_box.append_html_text("=====================================\n")
        text_box.append_html_text(f"Turn {turn}\n")

        if turn >= 300:
            text_box.append_html_text("Battle is taking too long.\n")
        elif not is_someone_alive(party1) and not is_someone_alive(party2):
            text_box.append_html_text("Both parties are defeated.\n")
        elif not is_someone_alive(party1):
            text_box.append_html_text("Party 1 is defeated.\n")
        elif not is_someone_alive(party2):
            text_box.append_html_text("Party 2 is defeated.\n")

    def restart_battle():
        global turn
        for character in all_characters:
            character.reset_stats()

        start_of_battle_effects(party1) # False as already handled in reset_stats()
        start_of_battle_effects(party2)

        redraw_ui(party1, party2)

        reset_ally_enemy_attr(party1, party2)
        turn = 1

    def set_up_characters() -> (list, list):
        global character_selection_menu, reserve_character_selection_menu, all_characters

        for character in all_characters:
            character.reset_stats()

        party1 = []
        party2 = []
        list_of_characters = random.sample(all_characters, 10)

        remaining_characters = [character for character in all_characters if character not in list_of_characters]

        random.shuffle(list_of_characters)

        party1 = list_of_characters[:5]
        party2 = list_of_characters[5:]

        start_of_battle_effects(party1)
        start_of_battle_effects(party2)

        character_selection_menu.kill()
        character_selection_menu = pygame_gui.elements.UIDropDownMenu([character.name for character in party1] + [character.name for character in party2],
                                                                party1[0].name,
                                                                pygame.Rect((880, 300), (156, 35)),
                                                                ui_manager)

        reserve_character_selection_menu.kill()
        reserve_character_selection_menu = pygame_gui.elements.UIDropDownMenu([character.name for character in remaining_characters],
                                                                remaining_characters[0].name,
                                                                pygame.Rect((880, 340), (156, 35)),
                                                                ui_manager)

        redraw_ui(party1, party2)
        reset_ally_enemy_attr(party1, party2)
        return party1, party2

    def replace_character_with_reserve_member(character_name, new_character_name):
        global party1, party2, all_characters, character_selection_menu, reserve_character_selection_menu

        def replace_in_party(party):
            for i, character in enumerate(party):
                if character.name == character_name:
                    new_character = next((char for char in all_characters if char.name == new_character_name), None)
                    if new_character:
                        party[i] = new_character
                        return True
            return False

        replaced = replace_in_party(party1)
        if not replaced:
            replace_in_party(party2)

        character_selection_menu.kill()
        character_selection_menu = pygame_gui.elements.UIDropDownMenu([character.name for character in party1] + [character.name for character in party2],
                                                                party1[0].name,
                                                                pygame.Rect((880, 300), (156, 35)),
                                                                ui_manager)

        remaining_characters = [character for character in all_characters if character not in party1 and character not in party2]

        reserve_character_selection_menu.kill()
        reserve_character_selection_menu = pygame_gui.elements.UIDropDownMenu([character.name for character in remaining_characters],
                                                                remaining_characters[0].name,
                                                                pygame.Rect((880, 340), (156, 35)),
                                                                ui_manager)
        redraw_ui(party1, party2)
        reset_ally_enemy_attr(party1, party2)
        text_box.append_html_text(f"{character_name} has been replaced with {new_character_name}.\n")

    def redraw_ui(party1, party2, refill_image=True, rebuild_healthbar=True, main_char=None):
        def redraw_party(party, image_slots, equip_slots, sprites, labels, healthbar, equip_effect_slots):
            for i, character in enumerate(party):
                if refill_image:
                    try:
                        image_slots[i].set_image(images[character.name.lower()])
                    except Exception:
                        image_slots[i].set_image(images["error"])

                image_slots[i].set_tooltip(character.tooltip_string(), delay=0.1, wrap_width=250)
                equip_slots[i].set_tooltip(character.get_equip_stats(), delay=0.1, wrap_width=300)
                equip_effect_slots[i].set_tooltip(character.equipment_set_effects_tooltip(), delay=0.1, wrap_width=250)
                sprites[i].current_health = character.hp
                sprites[i].health_capacity = character.maxhp
                labels[i].set_text(f"lv {character.lvl} {character.name}")
                labels[i].set_tooltip(character.skill_tooltip(), delay=0.1, wrap_width=300)
                healthbar[i].set_tooltip(character.tooltip_status_effects(), delay=0.1, wrap_width=300)
                if main_char == character:
                    labels[i].set_text(f"--> lv {character.lvl} {character.name}")

        redraw_party(party1, image_slots_party1, equip_slot_party1, sprite_party1, label_party1, health_bar_party1, equip_set_slot_party1)
        redraw_party(party2, image_slots_party2, equip_slot_party2, sprite_party2, label_party2, health_bar_party2, equip_set_slot_party2)

        if rebuild_healthbar:
            for healthbar in all_healthbar:
                healthbar.rebuild()

    def reroll_eq():
        all_characters = party1 + party2
        for character in all_characters:
            # Because of this, we can't have two characters with the same name
            if character.name == character_selection_menu.selected_option and character.isAlive():
                eq_to_gen = eq_selection_menu.selected_option
                rarity_to_gen = eq_rarity_selection_menu.selected_option
                rarity_to_gen = None if rarity_to_gen == "random" else rarity_to_gen
                set_to_gen = eq_set_list_selection_menu.selected_option
                set_to_gen = None if set_to_gen == "random" else set_to_gen
                # from character.equip get the index for given eq_to_gen string
                char_eq_index = [i for i, eq in enumerate(character.equip) if eq.type == eq_to_gen][0]
                character.equip[char_eq_index] = generate_equips_list(locked_type=eq_to_gen, eq_level=character.lvl, locked_eq_set=set_to_gen, locked_rarity=rarity_to_gen).pop()
                text_box.append_html_text("====================================\n")
                text_box.append_html_text(f"Rerolling {character.equip[char_eq_index].type} for {character.name}\n")
                text_box.append_html_text(character.equip[char_eq_index].print_stats())
                # The below is the same as level_up function, save the buffs and debuffs, reset stats, then reapply buffs and debuffs
                buff_copy = [effect for effect in character.buffs if not hasattr(effect, "is_set_effect") or not effect.is_set_effect]
                debuff_copy = [effect for effect in character.debuffs if not hasattr(effect, "is_set_effect") or not effect.is_set_effect]
                character.reset_stats(resethp=False, resetally=False, resetenemy=False)
                for effect in buff_copy:
                    character.applyEffect(effect)
                for effect in debuff_copy:
                    character.applyEffect(effect)
        redraw_ui(party1, party2)

    def eq_upgrade(is_upgrade):
        for character in all_characters:
            if character.name == character_selection_menu.selected_option and character.isAlive():
                char_eq_index = [i for i, eq in enumerate(character.equip) if eq.type == eq_selection_menu.selected_option][0]
                item_to_upgrade = character.equip[char_eq_index]
                a, b = item_to_upgrade.upgrade_stars_func(is_upgrade) 
                text_box.append_html_text("====================================\n")
                text_box.append_html_text(f"Upgrading equipment {character.equip[char_eq_index].type} for {character.name}\n")
                text_box.append_html_text(f"Stars: {int(a)} -> {int(b)}\n")
                if int(b) == 15:
                    text_box.append_html_text(f"Max stars reached\n")
                if int(b) == 0:
                    text_box.append_html_text(f"Min stars reached\n")
                buff_copy = [effect for effect in character.buffs if not hasattr(effect, "is_set_effect") or not effect.is_set_effect]
                debuff_copy = [effect for effect in character.debuffs if not hasattr(effect, "is_set_effect") or not effect.is_set_effect]
                character.reset_stats(resethp=False, resetally=False, resetenemy=False)
                for effect in buff_copy:
                    character.applyEffect(effect)
                for effect in debuff_copy:
                    character.applyEffect(effect)
        redraw_ui(party1, party2)

    def eq_levelchange(increment):
        for character in all_characters:
            if character.name == character_selection_menu.selected_option and character.isAlive():
                char_eq_index = [i for i, eq in enumerate(character.equip) if eq.type == eq_selection_menu.selected_option][0]
                item_to_levelchange = character.equip[char_eq_index]
                prev_level, new_level = item_to_levelchange.level_change(increment)
                text_box.append_html_text("====================================\n")
                text_box.append_html_text(f"Leveling equipment {character.equip[char_eq_index].type} for {character.name}\n")
                text_box.append_html_text(f"Level: {int(prev_level)} -> {int(new_level)}\n")
                if int(new_level) == 1000:
                    text_box.append_html_text(f"Max level reached\n")
                if int(new_level) == 1:
                    text_box.append_html_text(f"Min level reached\n")
                buff_copy = [effect for effect in character.buffs if not hasattr(effect, "is_set_effect") or not effect.is_set_effect]
                debuff_copy = [effect for effect in character.debuffs if not hasattr(effect, "is_set_effect") or not effect.is_set_effect]
                character.reset_stats(resethp=False, resetally=False, resetenemy=False)
                for effect in buff_copy:
                    character.applyEffect(effect)
                for effect in debuff_copy:
                    character.applyEffect(effect)
        redraw_ui(party1, party2)

    def character_level_button(up=True):
        all_characters = party1 + party2
        for character in all_characters:
            if character.name == character_selection_menu.selected_option and character.isAlive():
                if up:
                    character.level_change(1)
                    text_box.append_html_text(f"Leveling up {character.name}, New level: {character.lvl}\n")
                else:
                    character.level_change(-1)
                    text_box.append_html_text(f"Leveling down {character.name}. New level: {character.lvl}\n")
        redraw_ui(party1, party2, refill_image=False, rebuild_healthbar=True)

    # Text entry box
    # ==========================
    text_box = pygame_gui.elements.UITextEntryBox(pygame.Rect((300, 300), (556, 290)),"", ui_manager)
    text_box.set_text("Hover over character name to show skill information.\n")
    text_box.append_html_text("If lower cased character_name.jpg is not found in ./image directory, error.jpg will be used instead.\n")
    text_box.append_html_text("Hover over character image to show attributes.\n")
    text_box.append_html_text("Hover over character health bar to show status effects.\n")
    text_box.append_html_text("Hover over kkkkk icon to show item set information.\n")
    text_box.append_html_text("Hover over chopper knife icon to show item information.\n\n")

    # Event loop
    # ==========================
    running = True 
    for c in all_characters:
        c.running = running
        c.logging = logging
        c.text_box = text_box
        c.fineprint_mode = "suppress"
    party1 = []
    party2 = []
    party1, party2 = set_up_characters()
    turn = 1
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame_gui.UI_BUTTON_PRESSED:
                if event.ui_element == button1:
                    text_box.set_text("Welcome to the battle simulator!\n")
                    party1, party2 = set_up_characters()
                    turn = 1
                if event.ui_element == button2:
                    text_box.set_text("Welcome to the battle simulator!\n")
                    if next_turn(party1, party2):
                        turn += 1
                if event.ui_element == button3:
                    all_turns(party1, party2)
                if event.ui_element == button4:
                    text_box.set_text("Welcome to the battle simulator!\n")
                    restart_battle()
                if event.ui_element == button5:
                    running = False
                if event.ui_element == eq_reroll_button:
                    reroll_eq()
                if event.ui_element == eq_upgrade_button:
                    eq_upgrade(True)
                if event.ui_element == eq_downgrade_button:
                    eq_upgrade(False)
                if event.ui_element == character_replace_button:
                    replace_character_with_reserve_member(character_selection_menu.selected_option, reserve_character_selection_menu.selected_option)
                if event.ui_element == levelup_button:
                    character_level_button(up=True)
                if event.ui_element == leveldown_button:
                    character_level_button(up=False)
                if event.ui_element == eq_levelup_button:
                    eq_levelchange(increment=1)
                if event.ui_element == eq_leveldown_button:
                    eq_levelchange(increment=-1)

            ui_manager.process_events(event)

        ui_manager.update(1/60)
        display_surface.fill(light_yellow)
        ui_manager.draw_ui(display_surface)

        pygame.display.update()
        clock.tick(60)

    pygame.quit()
