import traceback
import character
import inspect
import monsters
from equip import generate_equips_list
import random, sys, csv, copy, time, itertools
import global_vars


class FinePrinter:
    def __init__(self, mode="default"):
        self.mode = mode
        if self.mode not in ["default", "file", "suppress"]:
            raise ValueError("Invalid mode.")
        self.page = 1

    def go_to_next_page(self):
        self.page += 1

    def fine_print(self, *args, **kwargs):
        if self.mode == "file":
            with open("logs/log_page" + str(self.page) + ".txt", "a") as f:
                print(*args, file=f, **kwargs)
        elif self.mode == "suppress":
            pass
        else:
            print(*args, **kwargs)


def get_all_characters(test_mode: int) -> tuple[list[character.Character], str]:
    all_characters = [cls(name, 40) for name, cls in character.__dict__.items() 
                    if inspect.isclass(cls) and issubclass(cls, character.Character) and cls != character.Character]
    all_monsters = [cls(name, 40) for name, cls in monsters.__dict__.items() 
                    if inspect.isclass(cls) and issubclass(cls, character.Character) and cls != character.Character and cls != monsters.Monster]
    all_characters_names = [x.name for x in all_characters]
    all_monsters_names = [x.name for x in all_monsters]
    print(f"All characters: {all_characters_names}")
    print(f"All monsters: {all_monsters_names}")

    match (test_mode, type(test_mode)):
        case (1, int):
            return all_characters, None
        case (2, int):
            return all_monsters, None
        case (3, int):
            return all_characters + all_monsters, None
        case (_, str):
            # Case of must include of certain character or monster
            the_character = None
            for char in all_characters:
                if char.name == test_mode:
                    the_character = char
                    return all_characters, the_character

            for mons in all_monsters:
                if mons.name == test_mode:
                    the_character = mons
                    return all_monsters, the_character
            raise ValueError("Character or monster not found.")

def is_someone_alive(party: list[character.Character]):
    for character in party:
        # if character.has_effect_that_named(class_name="RebornEffect"):
        #     print(f"{character.name} is considered alive because of RebornEffect.")
        if character.is_alive() or character.has_effect_that_named(class_name="RebornEffect"):
            return True
    return False

# Reset characters.ally and characters.enemy
def reset_ally_enemy_attr(party1: list[character.Character], party2: list[character.Character]):
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

def calculate_win_loss_rate(wins_data, losses_data, write_csv=False):
    """
    Calculate the win, loss, and win rate for each character with their equipment set.

    :param wins_data: List of tuples (character_name, equipment_set) for wins.
    :param losses_data: List of tuples (character_name, equipment_set) for losses.
    :param write_csv: If True, write the results to a CSV file.
    :return: Dictionary of {character_name_with_equipment_set: (wins, losses, winrate)}.
    """
    result = {}

    # Process wins data
    for character, equipment in wins_data:
        key = f"{character}_{equipment}"
        if key not in result:
            result[key] = {'wins': 0, 'losses': 0}
        result[key]['wins'] += 1

    # Process losses data
    for character, equipment in losses_data:
        key = f"{character}_{equipment}"
        if key not in result:
            result[key] = {'wins': 0, 'losses': 0}
        result[key]['losses'] += 1

    # Calculate winrate
    for key in result:
        wins = result[key]['wins']
        losses = result[key]['losses']
        total_games = wins + losses
        winrate = wins / total_games * 100 if total_games > 0 else 0
        character, equipment = key.split("_")
        
        is_boss = False
        hack = False
        try: 
            hack = eval(f"monsters.{character}('{character}', 40)").is_boss
        except Exception:
            pass
        if hack:
            is_boss = True
        
        result[key] = {
            'character_name': character,
            'equipment_set': equipment,
            'wins': wins,
            'losses': losses,
            'winrate': winrate,
            'is_boss': is_boss
        }

    # Sort the result, sort by A-Z of keys
    sorted_result = {k: v for k, v in sorted(result.items(), key=lambda item: item[0])}

    # Write to CSV if enabled
    if write_csv:
        with open('./reports/win_loss_data.csv', 'w', newline='', encoding='utf-8') as file:
            writer = csv.DictWriter(file, fieldnames=['character_name', 'equipment_set', 'wins', 'losses', 'winrate', 'is_boss'])
            writer.writeheader()
            for k, v in sorted_result.items():
                writer.writerow(v)

    return sorted_result


def simulate_battle_between_party(party1: list[character.Character], party2: list[character.Character], printer: FinePrinter,
                                  run_ucst=False):
    # -> (winner_party, turns, loser_party)

    turn = 1
    if party1 == [] or party2 == []:
        printer.fine_print("One of the party is empty.")
        return None
    reset_ally_enemy_attr(party1, party2)
    for c in itertools.chain(party1, party2):
        c.battle_entry_effects()
        c.battle_entry_effects_eqset()
    while turn < 300 and is_someone_alive(party1) and is_someone_alive(party2):
        printer.fine_print("=====================================")
        printer.fine_print(f"Turn {turn}")
        global_vars.turn_info_string = ""
        global_vars.turn_info_string += f"Turn {turn}\n"

        reset_ally_enemy_attr(party1, party2)
        for character in itertools.chain(party1, party2):
            character.update_ally_and_enemy()
            character.status_effects_start_of_turn()
            character.record_battle_turns()

        if not is_someone_alive(party1) or not is_someone_alive(party2):
            for character in itertools.chain(party1, party2):
                character.record_damage_taken() 
                character.record_healing_received() 
            printer.fine_print(global_vars.turn_info_string)
            break

        for character in party1:
            character.status_effects_midturn()

        for character in party2:
            character.status_effects_midturn()

        # This part may not be efficient
        reset_ally_enemy_attr(party1, party2)
        for character in party1:
            character.update_ally_and_enemy()
        for character in party2:
            character.update_ally_and_enemy()

        if not is_someone_alive(party1) or not is_someone_alive(party2):
            for character in itertools.chain(party1, party2):
                character.record_damage_taken() 
                character.record_healing_received()
            printer.fine_print(global_vars.turn_info_string) 
            break
        alive_characters = [x for x in itertools.chain(party1, party2) if x.is_alive()]
        if alive_characters != []:
            weight = [x.spd for x in alive_characters]
            the_chosen_one = random.choices(alive_characters, weights=weight, k=1)[0]
            global_vars.turn_info_string += f"{the_chosen_one.name}'s turn.\n"
            the_chosen_one.action()
        else:
            # This happens when 1 character in both side has Reborn, when makes is_someone_alive() of both sides True, but they are both dead this turn.
            global_vars.turn_info_string += "No one can be chosen to take action this turn.\n"

        for character in itertools.chain(party1, party2):
            character.status_effects_at_end_of_turn()

        for character in itertools.chain(party1, party2):
            character.record_damage_taken()
            character.record_healing_received()

        for character in itertools.chain(party1, party2):
            character.status_effects_after_damage_record()

        printer.fine_print(global_vars.turn_info_string)

        printer.fine_print("")
        printer.fine_print("Party 1:")
        for character in party1:
            printer.fine_print(character)
        printer.fine_print("")
        printer.fine_print("Party 2:")
        for character in party2:
            printer.fine_print(character)

        if run_ucst:
            # Unexpected Character Stats Test
            # Can help identifying debuffs mistakenly applied as buffs
            for character in itertools.chain(party1, party2):
                if not character.debuffs:
                    assert character.atk >= character.lvl * 5 * 0.5, f"{character.name} has atk less than {character.lvl * 5}"
                    # just nothing too crazy
                    assert character.heal_efficiency >= 0.99, f"{character.name} has heal efficiency less than 0.99"
                    assert character.crit >= 0, f"{character.name} has crit less than 0"


        turn += 1
    if turn > 300:
        printer.fine_print("Battle is taking too long.")
        printer.go_to_next_page()
        return None, 300, None
    if is_someone_alive(party1) and not is_someone_alive(party2):
        printer.fine_print("Party 1 win!")
        printer.go_to_next_page()
        return party1, turn, party2
    elif is_someone_alive(party2) and not is_someone_alive(party1):
        printer.fine_print("Party 2 win!")
        printer.go_to_next_page()
        return party2, turn, party1
    else:
        printer.fine_print("Draw!")
        printer.go_to_next_page()
        return None, turn, None


def build_parties_with_pairs(character_list, pairs_dict=None, character_must_include=None):
    # If pairs_dict is None or empty, treat all characters as individual units
    if not pairs_dict:
        pairs_dict = {}

    units = []
    processed_characters = set()

    for character in character_list:
        if character.name in processed_characters:
            continue
        pair_name_list = pairs_dict.get(character.name)
        # randomly choose a pair from the list
        pair_name = random.choice(pair_name_list) if pair_name_list else None
        if pair_name:
            if pair_name in processed_characters:
                continue  # Pair already processed
            # Find the pair character
            pair_character = next((ch for ch in character_list if ch.name == pair_name), None)
            if pair_character:
                units.append([character, pair_character])
                processed_characters.add(character.name)
                processed_characters.add(pair_name)
            else:
                # Pair character not found, treat as individual
                units.append([character])
                processed_characters.add(character.name)
        else:
            # Not part of a pair
            units.append([character])
            processed_characters.add(character.name)

    # Randomly shuffle units
    random.shuffle(units)
    party1 = []
    party2 = []

    units_to_assign = units.copy()

    # Find the unit that contains character_must_include
    unit_must_include = None
    if character_must_include:
        for unit in units:
            if character_must_include in unit:
                unit_must_include = unit
                break
        if not unit_must_include:
            # character_must_include is not in units, possibly not in character_list
            pass

    # pop the unit from units_to_assign that is unit_must_include, if unit_must_include is not None
    # then we move it to fairly end of units_to_assign, index > -10, so it will have a much greater chance to be assigned.
    if unit_must_include and unit_must_include in units_to_assign:
        units_to_assign.remove(unit_must_include)
        insertion_index = random.randint(-10, -1)
        units_to_assign.insert(insertion_index, unit_must_include)


    # Try to fill parties
    while len(party1) < 5 or len(party2) < 5:
        if not units_to_assign:
            break  # No more units to assign

        unit = units_to_assign.pop()
        unit_size = len(unit)

        # Randomly choose the order
        parties = [party1, party2]
        random.shuffle(parties)

        assigned = False
        for party in parties:
            if len(party) + unit_size <= 5:
                party.extend(unit)
                assigned = True
                break

        if not assigned:
            # Cannot assign unit to any party, discard unit
            continue

    return party1, party2



def calculate_winrate_for_character(sample, character_list: list[character.Character], fineprint_mode="default",
                                    run_tests=False, character_must_include=None):
    start_time = time.time()  
    turns_total = 0
    character_and_eqset_wins = []
    character_and_eqset_losses = []
    printer = FinePrinter(mode=fineprint_mode)
    amount_of_error = 0

    # Commented out in 3.5.9
    # Some characters are paired together as this will give a better representation of their performance,
    # but is way too complicated.
    # Reused in 3.7.2
    pairs_dict = {
        "Fenrir": ["Taily", "Rubin", "RubinPF"],
        "Pinee": ["Pine"],
    }

    for i in range(sample):
        # If there are too many errors, we know it is not a hardware failure or cosmic rays bit flipping
        # We should stop the simulation if 1 in 1000 games are errors
        if amount_of_error > max(int(sample * 0.001), 1):
            print("Too many errors, stopping the simulation.")
            break

        random.shuffle(character_list)
        party1, party2 = build_parties_with_pairs(character_list, pairs_dict, character_must_include)
        # party1, party2 = character_list[:5], character_list[5:10]
        # if character_must_include:
        #     if character_must_include not in itertools.chain(party1, party2):
        #         # pop a random guy from party1 and replace with character_must_include
        #         party1.pop(random.randint(0, 4))
        #         party1.append(character_must_include)

        for character in itertools.chain(party1, party2):
            character.fineprint_mode = fineprint_mode
            character.equip_item_from_list(generate_equips_list(4, random_full_eqset=True, locked_rarity="Legendary"))
            character.reset_stats()

        try:
            winner_party, turns, loser_party = simulate_battle_between_party(party1, party2, printer, run_tests)
        except Exception as e:
            amount_of_error += 1
            print(f"Error: {e}")
            traceback.print_exc()

            winner_party, turns, loser_party = None, 300, None
            # dump global_vars.turn_info_string to a logs/error.log file
            current_party_info = ""
            current_party_info += "Party 1:\n"
            for character in party1:
                current_party_info += f"{character}\n"
            current_party_info += "\nParty 2:\n"
            for character in party2:
                current_party_info += f"{character}\n"
            
            with open("logs/error.log", "a") as f:
                f.write(global_vars.turn_info_string + "\n" + str(e) + "\n")
                f.write(traceback.format_exc())  # トレースバックをログファイルに書き込み
                f.write(current_party_info + "\n\n\n\n\n")

        turns_total += turns
        if winner_party is not None:
            for character in winner_party:
                character_and_eqset_wins.append((character.name, character.eq_set))
        if loser_party is not None:
            for character in loser_party:
                character_and_eqset_losses.append((character.name, character.eq_set))

        try:
            if i % (sample // 100) == 0:
                print(f"{i / sample * 100:.2f}% done, {i} out of {sample}")
        except Exception:
            pass

    elapsed_time = time.time() - start_time
    print("=====================================")
    print(f"Elapsed time: {elapsed_time} seconds")
    print("=====================================")
    print(f"Average turns: {turns_total / sample}") # Ideal range: 70-90
    print("=====================================")

    return character_and_eqset_wins, character_and_eqset_losses


if __name__ == "__main__":
    # if ./logs directory does not exist, create it
    import os
    if not os.path.exists("logs"):
        os.makedirs("logs")
    # clear the error.log file
    with open("logs/error.log", "w") as f:
        f.write("")
    if len(sys.argv) > 1:
        sample = int(sys.argv[1])
    else:
        sample = 80000
    character_list, character_must_include = get_all_characters(1)
    # "default", "file", "suppress"
    a, b = calculate_winrate_for_character(sample, character_list, "suppress", run_tests=False, character_must_include=character_must_include)
    c = calculate_win_loss_rate(a, b, write_csv=True)
    try:
        import analyze
        data = analyze.create_report()
        print("Report generated and saved to ./reports/performance.txt")
        analyze.report_generate_heatmap(data)
        print("Heatmap generated and saved to ./reports/heatmap.png")
        analyze.report_export_pivot_table(data)
        print("Pivot table generated and saved to ./reports/pivot_table.csv")
    except Exception as e:
        print(e)