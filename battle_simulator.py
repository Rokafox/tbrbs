import os
from equip import *
from character import *
import copy
running = False
logging = True
text_box = None


# TODO:
# 1. 
# 2. Create graph to show damage dealt and healing done # Ignored
# 3. 
# 4. Redesign UI, the location of the buttons are not good # Waiting...Delayed...Partially Done...Delayed
# 5. Add 'Guard' attribute as a counter to 'Penetration', equipment should have 'Guard' attribute # Waiting...Delayed
# Reason: We will add this when damage is becoming uncontrollablly high, due to inflation of stats and effects.
# 6. 
# 7. 

# NOTE:
# 1. We cannot have character with the same name.
# 2. We better not have effects with the same name.

#--------------------------------------------------------- 
#---------------------------------------------------------
def is_someone_alive(party):
    for character in party:
        if character.isAlive():
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
character17 = Ophelia("Ophelia", average_party_level)
character18 = Chiffon("Chiffon", average_party_level)

all_characters = [character1, character2, character3, character4, character5,
                    character6, character7, character8, character9, character10,
                        character11, character12, character13, character14, character15
                            , character16, character17, character18]

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

    display_surface = pygame.display.set_mode((1600, 900), flags=pygame.SCALED)
    ui_manager = pygame_gui.UIManager((1600, 900), "theme_light_yellow.json", starting_language='ja')

    pygame.display.set_caption("Battle Simulator")

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

    for k, v in images.items():
        prefix = k.split("_")[0]
        for character in all_characters:
            if character.name.lower() == prefix:
                character.image.append(v)
                
    for c in all_characters:
        c.set_up_featured_image()

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

    equip_slotsb1 = pygame_gui.elements.UIImage(pygame.Rect((275, 50), (20, 20)),pygame.Surface((20, 20)),ui_manager)
    equip_slotsb2 = pygame_gui.elements.UIImage(pygame.Rect((275, 75), (20, 20)),pygame.Surface((20, 20)),ui_manager)
    equip_slotsb3 = pygame_gui.elements.UIImage(pygame.Rect((275, 100), (20, 20)),pygame.Surface((20, 20)),ui_manager)

    equip_slotsc1 = pygame_gui.elements.UIImage(pygame.Rect((475, 50), (20, 20)),pygame.Surface((20, 20)),ui_manager)
    equip_slotsc2 = pygame_gui.elements.UIImage(pygame.Rect((475, 75), (20, 20)),pygame.Surface((20, 20)),ui_manager)
    equip_slotsc3 = pygame_gui.elements.UIImage(pygame.Rect((475, 100), (20, 20)),pygame.Surface((20, 20)),ui_manager)

    equip_slotsd1 = pygame_gui.elements.UIImage(pygame.Rect((675, 50), (20, 20)),pygame.Surface((20, 20)),ui_manager)
    equip_slotsd2 = pygame_gui.elements.UIImage(pygame.Rect((675, 75), (20, 20)),pygame.Surface((20, 20)),ui_manager)
    equip_slotsd3 = pygame_gui.elements.UIImage(pygame.Rect((675, 100), (20, 20)),pygame.Surface((20, 20)),ui_manager)

    equip_slotse1 = pygame_gui.elements.UIImage(pygame.Rect((875, 50), (20, 20)),pygame.Surface((20, 20)),ui_manager)
    equip_slotse2 = pygame_gui.elements.UIImage(pygame.Rect((875, 75), (20, 20)),pygame.Surface((20, 20)),ui_manager)
    equip_slotse3 = pygame_gui.elements.UIImage(pygame.Rect((875, 100), (20, 20)),pygame.Surface((20, 20)),ui_manager)

    equip_slotsf1 = pygame_gui.elements.UIImage(pygame.Rect((75, 650), (20, 20)),pygame.Surface((20, 20)),ui_manager)
    equip_slotsf2 = pygame_gui.elements.UIImage(pygame.Rect((75, 675), (20, 20)),pygame.Surface((20, 20)),ui_manager)
    equip_slotsf3 = pygame_gui.elements.UIImage(pygame.Rect((75, 700), (20, 20)),pygame.Surface((20, 20)),ui_manager)

    equip_slotsg1 = pygame_gui.elements.UIImage(pygame.Rect((275, 650), (20, 20)),pygame.Surface((20, 20)),ui_manager)
    equip_slotsg2 = pygame_gui.elements.UIImage(pygame.Rect((275, 675), (20, 20)),pygame.Surface((20, 20)),ui_manager)
    equip_slotsg3 = pygame_gui.elements.UIImage(pygame.Rect((275, 700), (20, 20)),pygame.Surface((20, 20)),ui_manager)

    equip_slotsh1 = pygame_gui.elements.UIImage(pygame.Rect((475, 650), (20, 20)),pygame.Surface((20, 20)),ui_manager)
    equip_slotsh2 = pygame_gui.elements.UIImage(pygame.Rect((475, 675), (20, 20)),pygame.Surface((20, 20)),ui_manager)
    equip_slotsh3 = pygame_gui.elements.UIImage(pygame.Rect((475, 700), (20, 20)),pygame.Surface((20, 20)),ui_manager)

    equip_slotsi1 = pygame_gui.elements.UIImage(pygame.Rect((675, 650), (20, 20)),pygame.Surface((20, 20)),ui_manager)
    equip_slotsi2 = pygame_gui.elements.UIImage(pygame.Rect((675, 675), (20, 20)),pygame.Surface((20, 20)),ui_manager)
    equip_slotsi3 = pygame_gui.elements.UIImage(pygame.Rect((675, 700), (20, 20)),pygame.Surface((20, 20)),ui_manager)

    equip_slotsj1 = pygame_gui.elements.UIImage(pygame.Rect((875, 650), (20, 20)),pygame.Surface((20, 20)),ui_manager)
    equip_slotsj2 = pygame_gui.elements.UIImage(pygame.Rect((875, 675), (20, 20)),pygame.Surface((20, 20)),ui_manager)
    equip_slotsj3 = pygame_gui.elements.UIImage(pygame.Rect((875, 700), (20, 20)),pygame.Surface((20, 20)),ui_manager)

                                            
    equip_slot_party1 = [equip_slota1, equip_slotsb1, equip_slotsc1, equip_slotsd1, equip_slotse1]
    equip_slot_party2 = [equip_slotsf1, equip_slotsg1, equip_slotsh1, equip_slotsi1, equip_slotsj1]
    for slot in equip_slot_party1 + equip_slot_party2:
        slot.set_image(images["chopper_knife"])

    equip_slot_ribbon_party1 = [equip_slota2, equip_slotsb2, equip_slotsc2, equip_slotsd2, equip_slotse2]
    equip_slot_ribbon_party2 = [equip_slotsf2, equip_slotsg2, equip_slotsh2, equip_slotsi2, equip_slotsj2]
    for slot in equip_slot_ribbon_party1 + equip_slot_ribbon_party2:
        slot.set_image(images["ribbon"])

    equip_set_slot_party1 = [equip_slota3, equip_slotsb3, equip_slotsc3, equip_slotsd3, equip_slotse3]
    equip_set_slot_party2 = [equip_slotsf3, equip_slotsg3, equip_slotsh3, equip_slotsi3, equip_slotsj3]
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
    # Left Side

    button1 = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((100, 300), (156, 50)),
                                        text='Shuffle Party',
                                        manager=ui_manager,
                                        tool_tip_text = "Shuffle party and restart the battle")

    button4 = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((100, 360), (156, 50)),
                                        text='Restart Battle',
                                        manager=ui_manager,
                                        tool_tip_text = "Restart battle")

    button3 = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((100, 420), (156, 50)),
                                        text='All Turns',
                                        manager=ui_manager,
                                        tool_tip_text = "Skip to the end of the battle. May take a while.")

    button_left_clear_board = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((100, 480), (156, 50)),
                                        text='Clear Board',
                                        manager=ui_manager,
                                        tool_tip_text = "Remove all text from the text box, text box will be slower if there are too many text.")
    
    button5 = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((100, 540), (156, 50)),
                                        text='Quit',
                                        manager=ui_manager,
                                        tool_tip_text = "Quit")

    # =====================================
    # Right Side

    button2 = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((900, 300), (156, 50)),
                                        text='Next Turn',
                                        manager=ui_manager,
                                        tool_tip_text = "Simulate the next turn")

    button_auto_battle = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((1080, 300), (156, 50)),
                                        text='Auto',
                                        manager=ui_manager,
                                        tool_tip_text = "Auto battle")
    
    auto_battle_bar = pygame_gui.elements.UIStatusBar(pygame.Rect((1080, 290), (156, 10)),
                                               ui_manager,
                                               None)

    auto_battle_speed_selection_menu = pygame_gui.elements.UIDropDownMenu(["Slow", "Normal", "Fast", "Very Fast", "Instant"],
                                                            "Normal",
                                                            pygame.Rect((1080, 260), (156, 35)),
                                                            ui_manager)

    auto_battle_speed_label = pygame_gui.elements.UILabel(pygame.Rect((1080, 220), (156, 35)),
                                        "Auto Battle Speed: ",
                                        ui_manager)

    after_auto_battle_selection_menu = pygame_gui.elements.UIDropDownMenu(["Do Nothing", "Restart Battle", "Shuffle Party"],
                                                            "Do Nothing",
                                                            pygame.Rect((1080, 180), (156, 35)),
                                                            ui_manager)

    after_auto_battle_label = pygame_gui.elements.UILabel(pygame.Rect((1080, 140), (156, 35)),
                                        "After Auto Battle: ",
                                        ui_manager)

    def decide_auto_battle_speed():
        speed = auto_battle_speed_selection_menu.selected_option
        if speed == "Slow":
            return 10.0
        elif speed == "Normal":
            return 5.0
        elif speed == "Fast":
            return 2.5
        elif speed == "Very Fast":
            return 1.25
        elif speed == "Instant":
            return 0.625
    # =====================================
    # Character
    # =====================================

    character_selection_menu = pygame_gui.elements.UIDropDownMenu(["Option 1", "Option 2", "Option 3", "Option 4", "Option 5"],
                                                            "Option 1",
                                                            pygame.Rect((900, 360), (156, 35)),
                                                            ui_manager)

    label_character_selection_menu = pygame_gui.elements.UILabel(pygame.Rect((870, 360), (25, 35)),
                                        "→",
                                        ui_manager)
    label_character_selection_menu.set_tooltip("Selected character. Many button effect will use selected character as target.", delay=0.1)

    reserve_character_selection_menu = pygame_gui.elements.UIDropDownMenu(["Option1"],
                                                            "Option1",
                                                            pygame.Rect((900, 400), (156, 35)),
                                                            ui_manager)

    label_reserve_character_selection_menu = pygame_gui.elements.UILabel(pygame.Rect((870, 400), (25, 35)),
                                        "→",
                                        ui_manager)
    label_reserve_character_selection_menu.set_tooltip("Reserve character.", delay=0.1)

    character_replace_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((900, 440), (156, 35)),
                                        text='Replace',
                                        manager=ui_manager,
                                        tool_tip_text = "Replace selected character with reserve character")

    levelup_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((900, 480), (76, 35)),
                                        text='Lv +',
                                        manager=ui_manager,
                                        tool_tip_text = "Level up selected character")

    leveldown_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((980, 480), (76, 35)),
                                        text='Lv -',
                                        manager=ui_manager,
                                        tool_tip_text = "Level down selected character")
    
    cheat_selection_menu = pygame_gui.elements.UIDropDownMenu(["The Assignment", "The Actor", "The Downfall", "The Redemption", "The Legend"],
                                                            "The Assignment",
                                                            pygame.Rect((900, 520), (156, 35)),
                                                            ui_manager)
    
    cheat_add_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((900, 560), (156, 35)),
                                        text='Add Debug Effect',
                                        manager=ui_manager,
                                        tool_tip_text = "Add selected cheat effect to selected character, useful for debugging")
    
    # =====================================
    # Item
    # =====================================

    eq_rarity_list, eq_types_list, eq_set_list = Equip("Foo", "Weapon", "Common").get_raritytypeeqset_list()

    eq_selection_menu = pygame_gui.elements.UIDropDownMenu(eq_types_list,
                                                            eq_types_list[0],
                                                            pygame.Rect((1080, 360), (156, 35)),
                                                            ui_manager)

    eq_rarity_selection_menu = pygame_gui.elements.UIDropDownMenu(["random"] + eq_rarity_list,
                                                            "random",
                                                            pygame.Rect((1080, 400), (156, 35)),
                                                            ui_manager)

    eq_set_list_selection_menu = pygame_gui.elements.UIDropDownMenu(["random"] + eq_set_list,
                                                            "random",
                                                            pygame.Rect((1080, 440), (156, 35)),
                                                            ui_manager)

    eq_reroll_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((1080, 480), (156, 35)),
                                        text='Generate',
                                        manager=ui_manager,
                                        tool_tip_text = "Reroll item")

    eq_upgrade_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((1080, 520), (76, 35)),
                                        text='Star +',
                                        manager=ui_manager,
                                        tool_tip_text = "Upgrade stars for item")

    eq_downgrade_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((1158, 520), (76, 35)),
                                            text='Star -',
                                            manager=ui_manager,
                                            tool_tip_text = "Downgrade stars for item")

    eq_levelup_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((1080, 560), (76, 35)),
                                        text='Lv +',
                                        manager=ui_manager,
                                        tool_tip_text = "Level up selected item for selected character")

    eq_leveldown_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((1158, 560), (76, 35)),
                                        text='Lv -',
                                        manager=ui_manager,
                                        tool_tip_text = "Level down selected item for selected character")

    def next_turn(party1, party2):
        global turn
        if not is_someone_alive(party1) or not is_someone_alive(party2):
            text_box.append_html_text("Battle is over.\n")
            return False
        
        # hp_before = {character.name: character.hp for character in party1 + party2}
        buff_before = {character.name: character.buffs for character in party1 + party2} # A dictionary of lists
        # character.buff is a list of objects, so we want to only get the buff.name
        buff_before = {k: [x.name for x in buff_before[k]] for k in buff_before.keys()}
        debuff_before = {character.name: character.debuffs for character in party1 + party2}
        debuff_before = {k: [x.name for x in debuff_before[k]] for k in debuff_before.keys()}
        shield_value_before = {character.name: character.get_shield_value() for character in party1 + party2}


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
            # if character.isAlive():
            #     character.regen()
        for character in party2:
            character.statusEffects()
            # if character.isAlive():
            #     character.regen()

        reset_ally_enemy_attr(party1, party2)
        for character in party1:
            character.updateAllyEnemy()
        for character in party2:
            character.updateAllyEnemy()

        if not is_someone_alive(party1) or not is_someone_alive(party2):
            return False
        alive_characters = [x for x in party1 + party2 if x.isAlive()]
        weight = [x.spd for x in alive_characters]
        the_chosen_one = random.choices(alive_characters, weights=weight, k=1)[0]
        text_box.append_html_text(f"{the_chosen_one.name}'s turn.\n")
        the_chosen_one.action()

        for character in party1 + party2:
            character.status_effects_at_end_of_turn()

        # hp_after = {character.name: character.hp for character in party1 + party2}
        # hp_diff = {k: hp_after[k] - hp_before[k] for k in hp_before.keys()}
        buff_after = {character.name: character.buffs for character in party1 + party2} 
        buff_after = {k: [x.name for x in buff_after[k]] for k in buff_after.keys()}
        buff_applied_this_turn = {k: [x for x in buff_after[k] if x not in buff_before[k]] for k in buff_before.keys()}
        # buff_removed_this_turn = {k: [x for x in buff_before[k] if x not in buff_after[k]] for k in buff_before.keys()}
        debuff_after = {character.name: character.debuffs for character in party1 + party2}
        debuff_after = {k: [x.name for x in debuff_after[k]] for k in debuff_after.keys()}
        debuff_applied_this_turn = {k: [x for x in debuff_after[k] if x not in debuff_before[k]] for k in debuff_before.keys()}
        shield_value_after = {character.name: character.get_shield_value() for character in party1 + party2}
        shield_value_diff = {k: shield_value_after[k] - shield_value_before[k] for k in shield_value_before.keys()}

        redraw_ui(party1, party2, refill_image=True, main_char=the_chosen_one, 
                  buff_added_this_turn=buff_applied_this_turn, debuff_added_this_turn=debuff_applied_this_turn,
                  shield_value_diff_dict=shield_value_diff)

        for character in party1 + party2:
            character.record_damage_taken() # Empty damage_taken this turn and add to damage_taken_history
            character.record_healing_received() 

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
                # if character.isAlive():
                #     character.regen()
            for character in party2:
                character.statusEffects()
                # if character.isAlive():
                #     character.regen()

            reset_ally_enemy_attr(party1, party2)
            for character in party1:
                character.updateAllyEnemy()
            for character in party2:
                character.updateAllyEnemy()

            alive_characters = [x for x in party1 + party2 if x.isAlive()]
            weight = [x.spd for x in alive_characters]
            the_chosen_one = random.choices(alive_characters, weights=weight, k=1)[0]
            text_box.append_html_text(f"{the_chosen_one.name}'s turn.\n")
            the_chosen_one.action()

            for character in party1 + party2:
                character.status_effects_at_end_of_turn()

            for character in party1 + party2:
                character.record_damage_taken()
                character.record_healing_received()

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
        reset_ally_enemy_attr(party1, party2)
        for character in party1:
            character.battle_entry_effects()
        for character in party2:
            character.battle_entry_effects()
        redraw_ui(party1, party2)
        turn = 1


    def set_up_characters():
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
        character_selection_menu.kill()
        character_selection_menu = pygame_gui.elements.UIDropDownMenu([character.name for character in party1] + [character.name for character in party2],
                                                                party1[0].name,
                                                                pygame.Rect((900, 360), (156, 35)),
                                                                ui_manager)

        reserve_character_selection_menu.kill()
        reserve_character_selection_menu = pygame_gui.elements.UIDropDownMenu([character.name for character in remaining_characters],
                                                                remaining_characters[0].name,
                                                                pygame.Rect((900, 400), (156, 35)),
                                                                ui_manager)
        reset_ally_enemy_attr(party1, party2)
        for character in party1:
            character.battle_entry_effects()
        for character in party2:
            character.battle_entry_effects()
        redraw_ui(party1, party2)
        return party1, party2


    def replace_character_with_reserve_member(character_name, new_character_name):
        global party1, party2, all_characters, character_selection_menu, reserve_character_selection_menu
        def replace_in_party(party):
            for i, character in enumerate(party):
                if character.name == character_name:
                    new_character = next((char for char in all_characters if char.name == new_character_name), None)
                    if new_character:
                        party[i] = new_character
                        return True, new_character
            return False, None
        replaced, new_character = replace_in_party(party1)
        if not replaced:
            replaced, new_character = replace_in_party(party2)
        character_selection_menu.kill()
        character_selection_menu = pygame_gui.elements.UIDropDownMenu([character.name for character in party1] + [character.name for character in party2],
                                                                party1[0].name,
                                                                pygame.Rect((900, 360), (156, 35)),
                                                                ui_manager)

        remaining_characters = [character for character in all_characters if character not in party1 and character not in party2]

        reserve_character_selection_menu.kill()
        reserve_character_selection_menu = pygame_gui.elements.UIDropDownMenu([character.name for character in remaining_characters],
                                                                remaining_characters[0].name,
                                                                pygame.Rect((900, 400), (156, 35)),
                                                                ui_manager)
        reset_ally_enemy_attr(party1, party2)
        new_character.battle_entry_effects()
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


    def create_yellow_text(surface, text, font_size, text_color=(255, 255, 0), offset=10, position_type='bottom'):
        """
        Creates text on the given surface.

        Parameters:
        surface (pygame.Surface): The surface on which to draw the text.
        text (str): The text to be rendered.
        font_size (int): The size of the text.
        text_color (tuple): RGB color of the text. Default is yellow (255, 255, 0).
        offset (int): The offset from the edge of the surface.
        position_type (str): The position type for the text ('bottom' or 'topleft').
        """
        font = pygame.font.Font(None, font_size)
        text_surface = font.render(text, True, text_color)
        text_rect = text_surface.get_rect()

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

        create_yellow_text(surface, f"{hp}/{maxhp}", 25, position_type='center', text_color=(0, 0, 0))

        return surface

    # test_ui_image_slot = pygame_gui.elements.UIImage(pygame.Rect((1300, 100), (200, 30)),
    #                                     pygame.Surface((200, 30)),
    #                                     ui_manager)
    # test_healthbar = create_healthbar(50, 100, 200, 30, shield_value=33)
    # test_ui_image_slot.set_image(test_healthbar)

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
                  buff_added_this_turn=None, debuff_added_this_turn=None, shield_value_diff_dict=None):

        def redraw_party(party, image_slots, equip_slots, ribbon_slots, labels, healthbar, equip_effect_slots):
            for i, character in enumerate(party):
                if refill_image:
                    try:
                        image_slots[i].set_image(character.featured_image)
                    except Exception:
                        image_slots[i].set_image(images["error"])

                image_slots[i].set_tooltip(character.tooltip_string(), delay=0.1, wrap_width=250)
                equip_slots[i].set_tooltip(character.get_equip_stats(), delay=0.1, wrap_width=300)
                ribbon_slots[i].set_tooltip(character.get_equip_stats(ribbon=True), delay=0.1, wrap_width=300)
                equip_effect_slots[i].set_tooltip(character.equipment_set_effects_tooltip(), delay=0.1, wrap_width=300)
                labels[i].set_text(f"lv {character.lvl} {character.name}")
                labels[i].set_tooltip(character.skill_tooltip(), delay=0.1, wrap_width=400)
                labels[i].set_text_alpha(255) if character.isAlive() else labels[i].set_text_alpha(125)
                healthbar[i].set_image(create_healthbar(character.hp, character.maxhp, 176, 30, shield_value=character.get_shield_value()))
                healthbar[i].set_tooltip(character.tooltip_status_effects(), delay=0.1, wrap_width=300)

                if main_char == character:
                    labels[i].set_text(f"--> lv {character.lvl} {character.name}")
                    image = image_slots[i].image
                    new_image = add_outline_to_image(image, (255, 215, 0), 6)
                    image_slots[i].set_image(new_image)

                # self.damage_taken_this_turn = [] # list of tuples (damage, attacker), damage is int, attacker is Character object
                current_offset_for_damage_and_healing = 10
                if character.damage_taken_this_turn:
                    image = image_slots[i].image
                    new_image = add_outline_to_image(image, (255, 0, 0), 4)
                    # get all damage from list of tuples
                    damage_list = [x[0] for x in character.damage_taken_this_turn]
                    # show damage on image
                    for damage in damage_list:
                        create_yellow_text(new_image, str(damage), 25, (255, 0, 0), current_offset_for_damage_and_healing)
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



        redraw_party(party1, image_slots_party1, equip_slot_party1, equip_slot_ribbon_party1, label_party1, health_bar_party1, equip_set_slot_party1)
        redraw_party(party2, image_slots_party2, equip_slot_party2, equip_slot_ribbon_party2, label_party2, health_bar_party2, equip_set_slot_party2)



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
                buff_copy = [effect for effect in character.buffs if not effect.is_set_effect]
                debuff_copy = [effect for effect in character.debuffs if not effect.is_set_effect]
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
                buff_copy = [effect for effect in character.buffs if not effect.is_set_effect]
                debuff_copy = [effect for effect in character.debuffs if not effect.is_set_effect]
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
        redraw_ui(party1, party2, refill_image=False)


    def add_cheat_effect():
        all_characters = party1 + party2
        for character in all_characters:
            if character.name == character_selection_menu.selected_option and character.isAlive():
                e = cheat_selection_menu.selected_option
                if e == "The Assignment":
                    character.try_remove_effect_with_name("The Assignment Cheat")
                    character.applyEffect(StatsEffect("The Assignment Cheat", 2, True, {"spd": 100}))
                    text_box.append_html_text(f"Added {e} cheat effect to {character.name}.\n")
                elif e == "The Actor":
                    character.try_remove_effect_with_name("The Actor Cheat")
                    character.applyEffect(StatsEffect("The Actor Cheat", -1, True, {"spd": 100}))
                    text_box.append_html_text(f"Added {e} cheat effect to {character.name}.\n")
                elif e == "The Downfall":
                    character.try_remove_effect_with_name("The Downfall Cheat")
                    character.applyEffect(ContinuousDamageEffect("The Downfall Cheat", -1, False, character.maxhp * 0.2))
                    text_box.append_html_text(f"Added {e} cheat effect to {character.name}.\n")
                else:
                    print("Unimplemented cheat effect")
        redraw_ui(party1, party2, refill_image=False)


    # Text entry box
    # ==========================
    text_box = pygame_gui.elements.UITextEntryBox(pygame.Rect((300, 300), (556, 290)),"", ui_manager)
    text_box.set_text("Hover over character name to show skill information.\n")
    text_box.append_html_text("If lower cased character_name.jpg or png file is not found in ./image directory, error.jpg will be used instead.\n")
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

    auto_battle_active = False
    auto_battle_bar_progress = 0
    time_acc = 0

    while running:
        time_delta = clock.tick(60)/1000.0
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame_gui.UI_BUTTON_PRESSED:
                if event.ui_element == button_left_clear_board:
                    text_box.set_text("Welcome to the battle simulator!\n")
                if event.ui_element == button1: # Shuffle party
                    text_box.set_text("Welcome to the battle simulator!\n")
                    party1, party2 = set_up_characters()
                    turn = 1
                if event.ui_element == button2:
                    text_box.set_text("Welcome to the battle simulator!\n")
                    if next_turn(party1, party2):
                        turn += 1
                if event.ui_element == button3:
                    all_turns(party1, party2)
                if event.ui_element == button4: # Restart battle
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
                if event.ui_element == cheat_add_button:
                    add_cheat_effect()
                if event.ui_element == eq_levelup_button:
                    eq_levelchange(increment=1)
                if event.ui_element == eq_leveldown_button:
                    eq_levelchange(increment=-1)
                if event.ui_element == button_auto_battle:
                    if auto_battle_active:
                        auto_battle_active = False
                    else:
                        auto_battle_active = True

            ui_manager.process_events(event)

        ui_manager.update(time_delta)
        display_surface.fill(light_yellow)
        ui_manager.draw_ui(display_surface)

        if auto_battle_active:
            time_acc += time_delta
            auto_battle_bar_progress = (time_acc/decide_auto_battle_speed()) # May impact performance
            if auto_battle_bar_progress > 1.0:
                time_acc = 0.0
                text_box.set_text("Welcome to the battle simulator!\n")
                if not next_turn(party1, party2):
                    auto_battle_active = False
                    instruction = after_auto_battle_selection_menu.selected_option
                    if instruction == "Do Nothing":
                        pass
                    elif instruction == "Restart Battle":
                        text_box.set_text("Welcome to the battle simulator!\n")
                        restart_battle()
                        auto_battle_active = True
                    elif instruction == "Shuffle Party":
                        text_box.set_text("Welcome to the battle simulator!\n")
                        party1, party2 = set_up_characters()
                        turn = 1
                        auto_battle_active = True
                else:
                    turn += 1
            auto_battle_bar.percent_full = auto_battle_bar_progress

        pygame.display.update()

    pygame.quit()
