from battle_simulator import reset_ally_enemy_attr, start_of_battle_effects, mid_turn_effects, is_someone_alive, all_characters, generate_equips_list
import random, sys


def simulate_battle_between_party(party1, party2):
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
        return None, 300
    if is_someone_alive(party1) and not is_someone_alive(party2):
        print("Party 1 win!")
        return party1, turn
    elif is_someone_alive(party2) and not is_someone_alive(party1):
        print("Party 2 win!")
        return party2, turn
    else:
        print("Draw!")
        return None, turn


def calculate_winrate_for_character(sample): 
    win_counts = {c.name: 0 for c in all_characters}
    total_games = {c.name: 0 for c in all_characters}
    turns_total = 0

    for i in range(sample):
        for character in all_characters:
            character.equip = generate_equips_list(4, force_eqset="None")
            character.reset_stats()

        random.shuffle(all_characters)
        party1 = all_characters[:5]
        party2 = all_characters[5:10]

        for character in party1 + party2:
            total_games[character.name] += 1

        winner_party, turns = simulate_battle_between_party(party1, party2)
        turns_total += turns
        if winner_party is not None:
            for character in winner_party:
                win_counts[character.name] += 1

    print("=====================================")
    print("Average turns:", turns_total / sample) # Ideal range: 55-60
    print("Winrate:")
    winrate_dict = {}
    for character in all_characters:
        if total_games[character.name] > 0:
            try:
                winrate = win_counts[character.name] / total_games[character.name] * 100
            except ZeroDivisionError:
                winrate = 0
            loss_count = total_games[character.name] - win_counts[character.name]
            winrate_dict[character.name] = (win_counts[character.name], loss_count, winrate)
        else:
            winrate_dict[character.name] = (0, 0, 0)
    winrate_dict = {k: v for k, v in sorted(winrate_dict.items(), key=lambda item: item[1][2], reverse=True)}
    max_key_length = max(len(key) for key in winrate_dict)
    for k, v in winrate_dict.items():
        print(f"{k:>{max_key_length}}: {v[0]:>5} wins, {v[1]:>5} losses, {v[2]:>6.2f}% winrate")


if __name__ == "__main__":
    if len(sys.argv) > 1:
        sample = int(sys.argv[1])
    else:
        sample = 100 # fast enough to debug
    calculate_winrate_for_character(sample)