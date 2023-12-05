from battle_simulator import reset_ally_enemy_attr, start_of_battle_effects, mid_turn_effects, is_someone_alive, all_characters, generate_equips_list
import random


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
        return None
    if is_someone_alive(party1) and not is_someone_alive(party2):
        print("Party 1 win!")
        return party1
    elif is_someone_alive(party2) and not is_someone_alive(party1):
        print("Party 2 win!")
        return party2
    else:
        print("Draw!")
        return None


def calculate_winrate_for_character(sample): 
    win_counts = {c.name: 0 for c in all_characters}
    total_games = {c.name: 0 for c in all_characters}

    for i in range(sample):
        for character in all_characters:
            character.__init__(character.name, character.lvl, equip=generate_equips_list(4))

        random.shuffle(all_characters)
        party1 = all_characters[:5]
        party2 = all_characters[5:10]

        for character in party1 + party2:
            total_games[character.name] += 1

        winner_party = simulate_battle_between_party(party1, party2)
        if winner_party is not None:
            for character in winner_party:
                win_counts[character.name] += 1

    print("=====================================")
    print("Winrate:")
    for character in all_characters:
        if total_games[character.name] > 0:
            winrate = win_counts[character.name] / total_games[character.name] * 100
            loss_count = total_games[character.name] - win_counts[character.name]
            print(f"{character.name} wins: {win_counts[character.name]}, losses: {loss_count}, winrate: {winrate:.2f}%")
        else:
            print(f"{character.name} has not played any games.")


if __name__ == "__main__":
    calculate_winrate_for_character(100)