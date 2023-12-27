from battle_simulator import reset_ally_enemy_attr, is_someone_alive, all_characters, generate_equips_list
import random, sys, csv
from fine_print import fine_print


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


def simulate_battle_between_party(party1, party2, fineprint_mode="default") -> (list, int, list):
    # -> (winner_party, turns, loser_party)
    turn = 1
    if party1 == [] or party2 == []:
        fine_print("One of the party is empty.", mode=fineprint_mode)
        return None
    reset_ally_enemy_attr(party1, party2)
    for c in party1 + party2:
        c.battle_entry_effects()
    while turn < 300 and is_someone_alive(party1) and is_someone_alive(party2):
        fine_print("=====================================", mode=fineprint_mode)
        fine_print(f"Turn {turn}", mode=fineprint_mode)

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

        # This part may not be efficient
        reset_ally_enemy_attr(party1, party2)
        for character in party1:
            character.updateAllyEnemy()
        for character in party2:
            character.updateAllyEnemy()

        if not is_someone_alive(party1) or not is_someone_alive(party2):
            break
        alive_characters = [x for x in party1 + party2 if x.isAlive()]
        weight = [x.spd for x in alive_characters]
        the_chosen_one = random.choices(alive_characters, weights=weight, k=1)[0]
        fine_print(f"{the_chosen_one.name}'s turn.", mode=fineprint_mode)
        the_chosen_one.action()

        for character in party1 + party2:
            character.status_effects_at_end_of_turn()

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


def calculate_winrate_for_character(sample, fineprint_mode="default"): 
    win_counts = {c.name: 0 for c in all_characters}
    total_games = {c.name: 0 for c in all_characters}
    turns_total = 0
    character_and_eqset_wins = []
    character_and_eqset_losses = []

    for i in range(sample):
        for character in all_characters:
            character.fineprint_mode = fineprint_mode
            character.equip = generate_equips_list(4, random_full_eqset=True)
            character.reset_stats()

        random.shuffle(all_characters)
        party1 = all_characters[:5]
        party2 = all_characters[5:10]

        for character in party1 + party2:
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

    print("=====================================")
    print(f"Average turns: {turns_total / sample}") # Ideal range: 55-60
    print("=====================================")

    return character_and_eqset_wins, character_and_eqset_losses


if __name__ == "__main__":
    if len(sys.argv) > 1:
        sample = int(sys.argv[1])
    else:
        sample = 4000
    a, b = calculate_winrate_for_character(sample, "suppress")
    c = calculate_win_loss_rate(a, b, write_csv=True)
    try:
        import analyze
        data = analyze.create_report()
        print("Report generated and saved to ./reports/performance.txt")
        analyze.generate_heatmap(data)
        print("Heatmap generated and saved to ./reports/heatmap.png")
    except Exception as e:
        print(e)