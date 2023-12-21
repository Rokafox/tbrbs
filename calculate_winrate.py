from battle_simulator import reset_ally_enemy_attr, start_of_battle_effects, mid_turn_effects, is_someone_alive, all_characters, generate_equips_list
import random, sys, csv


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

    # Print the result nicely
    max_key_length = max(len(key) for key in sorted_result)
    for k, v in sorted_result.items():
        print(f"{k:>{max_key_length}}: {v['wins']:>5} wins, {v['losses']:>5} losses, {v['winrate']:>6.2f}% winrate")

    return sorted_result


def simulate_battle_between_party(party1, party2) -> (list, int, list):
    # -> (winner_party, turns, loser_party)
    turn = 1
    if party1 == [] or party2 == []:
        print("One of the party is empty.")
        return None
    reset_ally_enemy_attr(party1, party2)
    start_of_battle_effects(party1)
    start_of_battle_effects(party2)
    while turn < 300 and is_someone_alive(party1) and is_someone_alive(party2):
        print("=====================================")
        print(f"Turn {turn}")
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

        if not is_someone_alive(party1) or not is_someone_alive(party2):
            break
        alive_characters = [x for x in party1 + party2 if x.isAlive()]
        weight = [x.spd for x in alive_characters]
        the_chosen_one = random.choices(alive_characters, weights=weight, k=1)[0]
        print(f"{the_chosen_one.name}'s turn.")
        the_chosen_one.action()
        print("")
        print("Party 1:")
        for character in party1:
            print(character)
        print("")
        print("Party 2:")
        for character in party2:
            print(character)
        turn += 1
    if turn > 300:
        print("Battle is taking too long.")
        return None, 300, None
    if is_someone_alive(party1) and not is_someone_alive(party2):
        print("Party 1 win!")
        return party1, turn, party2
    elif is_someone_alive(party2) and not is_someone_alive(party1):
        print("Party 2 win!")
        return party2, turn, party1
    else:
        print("Draw!")
        return None, turn, None


def calculate_winrate_for_character(sample): 
    win_counts = {c.name: 0 for c in all_characters}
    total_games = {c.name: 0 for c in all_characters}
    turns_total = 0
    character_and_eqset_wins = []
    character_and_eqset_losses = []

    for i in range(sample):
        for character in all_characters:
            character.equip = generate_equips_list(4, random_full_eqset=True)
            character.reset_stats()

        random.shuffle(all_characters)
        party1 = all_characters[:5]
        party2 = all_characters[5:10]

        for character in party1 + party2:
            total_games[character.name] += 1

        winner_party, turns, loser_party = simulate_battle_between_party(party1, party2)
        turns_total += turns
        if winner_party is not None:
            for character in winner_party:
                win_counts[character.name] += 1
                character_and_eqset_wins.append((character.name, character.eq_set))
        if loser_party is not None:
            for character in loser_party:
                character_and_eqset_losses.append((character.name, character.eq_set))

    print("=====================================")
    print("Average turns:", turns_total / sample) # Ideal range: 55-60
    print("=====================================")

    return character_and_eqset_wins, character_and_eqset_losses


if __name__ == "__main__":
    if len(sys.argv) > 1:
        sample = int(sys.argv[1])
    else:
        sample = 1000 # more enough to analyze
    a, b = calculate_winrate_for_character(sample)
    c = calculate_win_loss_rate(a, b, write_csv=True)