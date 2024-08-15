from character import *
import inspect
import monsters
from equip import generate_equips_list
import random, sys, csv, copy, time
import global_vars


def fine_print(*args, mode="default", **kwargs):
    if mode == "file":
        with open("logs.txt", "a") as f:
            print(*args, file=f, **kwargs)
    elif mode == "suppress":
        pass
    else:
        print(*args, **kwargs)


def get_all_characters(test_mode):
    character_names = ["Lillia", "Poppy", "Iris", "Freya", "Luna", "Clover", "Ruby", "Olive", "Fenrir", "Cerberus", "Pepper",
                       "Cliffe", "Pheonix", "Bell", "Taily", "Seth", "Chiffon", "Ophelia", "Requina", "Gabe", "Yuri", "Dophine",
                       "Tian", "Don", "Natasya", "Roseiri"]

    all_characters = [eval(f"{name}('{name}', 40)") for name in character_names]

    # get all monsters class names in monsters.py, search for all classes that is a subclass of Character
    monster_names = [name for name in dir(monsters) 
                    if inspect.isclass(getattr(monsters, name)) and 
                    issubclass(getattr(monsters, name), Character) and 
                    name != "Character"]
    print("All monsters:")
    print(monster_names)
    all_monsters = [eval(f"monsters.{name}('{name}', 40)") for name in monster_names]

    match (test_mode, type(test_mode)):
        case (1, int):
            return all_characters
        case (2, int):
            return all_monsters
        case (3, int):
            return all_characters + all_monsters
        case (_, str):
            # Case of must include of certain monster, we can simply get rid of all others in all_monsters
            print(f"Testing all characters and {test_mode} only")
            return [x for x in all_monsters if x.name == test_mode] + all_characters 

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
        result[key] = {'character_name': character, 'equipment_set': equipment, 'wins': wins, 'losses': losses, 'winrate': winrate}

    # Sort the result, sort by A-Z of keys
    sorted_result = {k: v for k, v in sorted(result.items(), key=lambda item: item[0])}

    # Write to CSV if enabled
    if write_csv:
        with open('win_loss_data.csv', 'w', newline='', encoding='utf-8') as file:
            writer = csv.DictWriter(file, fieldnames=['character_name', 'equipment_set', 'wins', 'losses', 'winrate'])
            writer.writeheader()
            for k, v in sorted_result.items():
                writer.writerow(v)

    # max_key_length = max(len(key) for key in sorted_result)
    # for k, v in sorted_result.items():
    #     print(f"{k:>{max_key_length}}: {v['wins']:>5} wins, {v['losses']:>5} losses, {v['winrate']:>6.2f}% winrate")

    return sorted_result


def simulate_battle_between_party(party1, party2, fineprint_mode="default"):
    # -> (winner_party, turns, loser_party)
    turn = 1
    if party1 == [] or party2 == []:
        fine_print("One of the party is empty.", mode=fineprint_mode)
        return None
    reset_ally_enemy_attr(party1, party2)
    for c in itertools.chain(party1, party2):
        c.battle_entry_effects()
    while turn < 300 and is_someone_alive(party1) and is_someone_alive(party2):
        fine_print("=====================================", mode=fineprint_mode)
        fine_print(f"Turn {turn}", mode=fineprint_mode)
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
            fine_print(global_vars.turn_info_string, mode=fineprint_mode)
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
            fine_print(global_vars.turn_info_string, mode=fineprint_mode) 
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

        fine_print(global_vars.turn_info_string, mode=fineprint_mode)

        fine_print("", mode=fineprint_mode)
        fine_print("Party 1:", mode=fineprint_mode)
        for character in party1:
            fine_print(character, mode=fineprint_mode)
        fine_print("", mode=fineprint_mode)
        fine_print("Party 2:", mode=fineprint_mode)
        for character in party2:
            fine_print(character, mode=fineprint_mode)
        turn += 1
    if turn > 300:
        fine_print("Battle is taking too long.", mode=fineprint_mode)
        return None, 300, None
    if is_someone_alive(party1) and not is_someone_alive(party2):
        fine_print("Party 1 win!", mode=fineprint_mode)
        return party1, turn, party2
    elif is_someone_alive(party2) and not is_someone_alive(party1):
        fine_print("Party 2 win!", mode=fineprint_mode)
        return party2, turn, party1
    else:
        fine_print("Draw!", mode=fineprint_mode)
        return None, turn, None


def calculate_winrate_for_character(sample, character_list, fineprint_mode="default"):
    start_time = time.time()  
    win_counts = {c.name: 0 for c in character_list}
    total_games = {c.name: 0 for c in character_list}
    turns_total = 0
    character_and_eqset_wins = []
    character_and_eqset_losses = []

    for i in range(sample):
        for character in character_list:
            character.fineprint_mode = fineprint_mode
            character.equip_item_from_list(generate_equips_list(4, random_full_eqset=True))
            character.reset_stats()

        random.shuffle(character_list)
        party1 = character_list[:5]
        party2 = character_list[5:10]

        for character in itertools.chain(party1, party2):
            total_games[character.name] += 1

        winner_party, turns, loser_party = simulate_battle_between_party(party1, party2, fineprint_mode=fineprint_mode)
        turns_total += turns
        if winner_party is not None:
            for character in winner_party:
                win_counts[character.name] += 1
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
    print(f"Average turns: {turns_total / sample}") # Ideal range: 55-60
    print("=====================================")

    return character_and_eqset_wins, character_and_eqset_losses


if __name__ == "__main__":
    if len(sys.argv) > 1:
        sample = int(sys.argv[1])
    else:
        sample = 10000
    a, b = calculate_winrate_for_character(sample, get_all_characters(1), "suppress")
    c = calculate_win_loss_rate(a, b, write_csv=True)
    try:
        import analyze
        data = analyze.create_report()
        print("Report generated and saved to ./reports/performance.txt")
        analyze.generate_heatmap(data)
        print("Heatmap generated and saved to ./reports/heatmap.png")
    except Exception as e:
        print(e)