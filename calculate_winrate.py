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


def get_all_characters(test_mode: int):
    all_characters = [cls(name, 40) for name, cls in character.__dict__.items() 
                    if inspect.isclass(cls) and issubclass(cls, character.Character) and cls != character.Character]
    all_monsters = [cls(name, 40) for name, cls in monsters.__dict__.items() 
                    if inspect.isclass(cls) and issubclass(cls, character.Character) and cls != character.Character and cls != monsters.Monster]
    print(f"All characters: {[x.name for x in all_characters]}")
    print(f"All monsters: {[x.name for x in all_monsters]}")

    match (test_mode, type(test_mode)):
        case (1, int):
            return all_characters
        case (2, int):
            return all_monsters
        case (3, int):
            return all_characters + all_monsters
        case (_, str):
            # Case of must include of certain character
            print(f"Testing all characters and {test_mode} only")
            return [x for x in all_characters if x.name == test_mode] + all_monsters 

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


def simulate_battle_between_party(party1: list[character.Character], party2: list[character.Character], printer: FinePrinter):
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
            # if character.is_alive():
            #     character.regen()
        for character in party2:
            character.status_effects_midturn()
            # if character.is_alive():
            #     character.regen()

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
        weight = [x.spd for x in alive_characters]
        the_chosen_one = random.choices(alive_characters, weights=weight, k=1)[0]
        global_vars.turn_info_string += f"{the_chosen_one.name}'s turn.\n"
        the_chosen_one.action()

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


def calculate_winrate_for_character(sample, character_list, fineprint_mode="default"):
    start_time = time.time()  
    # win_counts = {c.name: 0 for c in character_list}
    # total_games = {c.name: 0 for c in character_list}
    turns_total = 0
    character_and_eqset_wins = []
    character_and_eqset_losses = []
    printer = FinePrinter(mode=fineprint_mode)
    amount_of_error = 0

    for i in range(sample):
        # If there are too many errors, we know it is not a hardware failure or cosmic rays bit flipping
        # We should stop the simulation if 1 in 1000 games are errors
        if amount_of_error > max(int(sample * 0.001), 1):
            print("Too many errors, stopping the simulation.")
            break

        # Sample 10 unique elements from character_list
        sampled_characters = random.sample(character_list, 10)
        party1 = sampled_characters[:5]
        party2 = sampled_characters[5:]

        for character in itertools.chain(party1, party2):
            # total_games[character.name] += 1
            character.fineprint_mode = fineprint_mode
            character.equip_item_from_list(generate_equips_list(4, random_full_eqset=True))
            character.reset_stats()

        try:
            winner_party, turns, loser_party = simulate_battle_between_party(party1, party2, printer)
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
                # エラーの詳細なトレースバックを記録
                f.write(global_vars.turn_info_string + "\n" + str(e) + "\n")
                f.write(traceback.format_exc())  # トレースバックをログファイルに書き込み
                f.write(current_party_info + "\n\n\n\n\n")

        turns_total += turns
        if winner_party is not None:
            for character in winner_party:
                # win_counts[character.name] += 1
                character_and_eqset_wins.append((character.name, character.eq_set))
        if loser_party is not None:
            for character in loser_party:
                character_and_eqset_losses.append((character.name, character.eq_set))

        # A simple progress bar
        try:
            if i % (sample // 100) == 0:
                print(f"{i / sample * 100:.2f}% done, {i} out of {sample}")
        except Exception:
            pass

    elapsed_time = time.time() - start_time  # Calculate the elapsed time
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
        sample = 3000
    a, b = calculate_winrate_for_character(sample, get_all_characters(1), "suppress")
    c = calculate_win_loss_rate(a, b, write_csv=True)
    try:
        import analyze
        data = analyze.create_report()
        print("Report generated and saved to ./reports/performance.txt")
        analyze.report_generate_heatmap(data)
        print("Heatmap generated and saved to ./reports/heatmap.png")
    except Exception as e:
        print(e)