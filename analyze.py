import io
import warnings
import pygame
warnings.simplefilter(action='ignore', category=FutureWarning) # No future, now is eternal
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import ast
import numpy as np


def create_report():
    file_path = './reports/win_loss_data.csv'
    data = pd.read_csv(file_path)
    data['character_name'] = data.apply(
        lambda row: f"{row['character_name']} (Boss)" if row['is_boss'] else row['character_name'], axis=1
    )
    character_performance = data.groupby('character_name')['winrate'].mean().sort_values(ascending=False)
    equipment_performance = data.groupby('equipment_set')['winrate'].mean().sort_values(ascending=False)
    with open('./reports/performance.txt', 'w') as file:
        file.write("Character Performance:\n")
        for character, performance in character_performance.items():
            file.write(f"{character}: {performance}\n")
        file.write("\nEquipment Performance:\n")
        for equipment, performance in equipment_performance.items():
            file.write(f"{equipment}: {performance}\n")
    return data


def report_generate_heatmap(data):
    heatmap_data = data.pivot(index='character_name', columns='equipment_set', values='winrate')
    plt.figure(figsize=(20, 32))
    sns.heatmap(heatmap_data, annot=True, fmt=".1f", cmap="coolwarm")
    plt.title("Win Rates of Characters with Different Equipment Sets")
    plt.xlabel("Equipment Set")
    plt.ylabel("Character Name")
    plt.savefig('./reports/heatmap.png')


def create_damage_summary_new(sort_reference_list=None, dataframe=None):
    if dataframe is None:
        file_path = './.tmp/tmp_damage_data.csv'
        damage_data = pd.read_csv(file_path)
        # print(damage_data)
    else:
        damage_data = dataframe
        # print(damage_data)

    damage_dealt_summary = {}
    damage_received_summary = []

    def process_damage_entry(damage, attacker, damage_type):
        if attacker not in damage_dealt_summary:
            damage_dealt_summary[attacker] = {'total': 0, 'normal': 0, 'normal_critical': 0, 'status': 0, 'bypass': 0, 'friendlyfire': 0}
        
        damage_dealt_summary[attacker]['total'] += damage
        damage_dealt_summary[attacker][damage_type] += damage

    def process_damage_history(damage_history_input):
        # print(damage_history_input)
        if isinstance(damage_history_input, str):
            damage_history = ast.literal_eval(damage_history_input)
        else:
            damage_history = damage_history_input

        damage_summary = {'total': 0, 'normal': 0, 'normal_critical': 0, 'status': 0, 'bypass': 0, 'friendlyfire': 0}

        for entry in damage_history:
            if not entry:  # Skip empty entries
                continue
            damage, attacker, damage_type = entry
            process_damage_entry(damage, attacker, damage_type)
            damage_summary['total'] += damage
            damage_summary[damage_type] += damage

        return damage_summary

    for _, row in damage_data.iterrows():
        damage_summary = process_damage_history(row['Damage Taken History'])
        damage_received_summary.append({'Character': row['Character'], **damage_summary})
    
    damage_received_df = pd.DataFrame(damage_received_summary)
    damage_dealt_df = pd.DataFrame.from_dict(damage_dealt_summary, orient='index').reset_index().rename(columns={'index': 'Character'})

    # print(damage_received_df)
    # print(damage_dealt_df)

    if damage_dealt_df.empty:
        damage_dealt_df = pd.DataFrame(columns=['Character', 'total', 'normal', 'normal_critical', 'status', 'bypass', 'friendlyfire'])


    combined_df = pd.merge(damage_received_df, damage_dealt_df, on='Character', how='outer', suffixes=('_received', '_dealt'))
    combined_df.fillna(0, inplace=True)


    # Remove the float, and convert to int
    combined_df = combined_df.astype({col: 'int' for col in combined_df.columns if col != 'Character'})

    if sort_reference_list:
        combined_df['Character'] = pd.Categorical(combined_df['Character'], categories=sort_reference_list, ordered=True)
        combined_df.sort_values('Character', inplace=True)
    
    # For performance reasons, we will not write the file here
    # combined_df.to_csv('./.tmp/damage_summary_combined_new.csv', index=False)

    return combined_df


def damage_summary_visualize(df: pd.DataFrame, what_to_visualize: str):
    if what_to_visualize == 'received':
        # Prepare data for Damage Received
        damage_data = df[['Character', 'normal_received', 'normal_critical_received', 'status_received', 'bypass_received', 'friendlyfire_received']].copy()
        # Shorten character names if they are too long
        damage_data['Character'] = damage_data['Character'].apply(lambda x: x[:7] if len(x) > 7 else x)
        # In-memory buffer for saving the image
        buffer = io.BytesIO()
        # Plotting the stacked bar chart for Damage Received
        plt.figure(figsize=(14, 6))
        plt.bar(damage_data['Character'], damage_data['normal_received'], label='Normal Damage Received', color='deepskyblue')
        plt.bar(damage_data['Character'], damage_data['normal_critical_received'], bottom=damage_data['normal_received'], label='Normal Critical Damage Received', color='darkturquoise')
        plt.bar(damage_data['Character'], damage_data['status_received'], bottom=damage_data['normal_received'] + damage_data['normal_critical_received'], label='Status Damage Received', color='lightblue')
        plt.bar(damage_data['Character'], damage_data['bypass_received'], bottom=damage_data['normal_received'] + damage_data['normal_critical_received'] + damage_data['status_received'], label='Bypass Damage Received', color='cadetblue')
        plt.bar(damage_data['Character'], damage_data['friendlyfire_received'], bottom=damage_data['normal_received'] + damage_data['normal_critical_received'] + damage_data['status_received'] + damage_data['bypass_received'], label='Friendly Fire Damage Received', color='gray')
        plt.xticks(fontsize=22)
        plt.yticks(fontsize=22)
        plt.subplots_adjust(left=0, right=1, top=1, bottom=0)
        plt.savefig(buffer, format='png', bbox_inches='tight', pad_inches=0, transparent=True)
        plt.close()
        # Move buffer to the beginning so it can be read
        buffer.seek(0)
        # Load the image directly into Pygame
        image_received = pygame.image.load(buffer, 'damage_received.png')
        # Clean up the buffer
        buffer.close()
        return image_received

    elif what_to_visualize == 'dealt':
        # Prepare data for Damage Dealt
        damage_data = df[['Character', 'normal_dealt', 'normal_critical_dealt', 'status_dealt', 'bypass_dealt', 'friendlyfire_dealt']].copy()
        # Shorten character names if they are too long
        damage_data['Character'] = damage_data['Character'].apply(lambda x: x[:7] if len(x) > 7 else x)
        # In-memory buffer for saving the image
        buffer = io.BytesIO()
        # Plotting the stacked bar chart for Damage Dealt
        plt.figure(figsize=(14, 6))
        plt.bar(damage_data['Character'], damage_data['normal_dealt'], label='Normal Damage Dealt', color='tomato')
        plt.bar(damage_data['Character'], damage_data['normal_critical_dealt'], bottom=damage_data['normal_dealt'], label='Normal Critical Damage Dealt', color='firebrick')
        plt.bar(damage_data['Character'], damage_data['status_dealt'], bottom=damage_data['normal_dealt'] + damage_data['normal_critical_dealt'], label='Status Damage Dealt', color='orange')
        plt.bar(damage_data['Character'], damage_data['bypass_dealt'], bottom=damage_data['normal_dealt'] + damage_data['normal_critical_dealt'] + damage_data['status_dealt'], label='Bypass Damage Dealt', color='cadetblue')
        plt.bar(damage_data['Character'], damage_data['friendlyfire_dealt'], bottom=damage_data['normal_dealt'] + damage_data['normal_critical_dealt'] + damage_data['status_dealt'] + damage_data['bypass_dealt'], label='Friendly Fire Damage Dealt', color='gray')
        plt.xticks(fontsize=22)
        plt.yticks(fontsize=22)
        plt.subplots_adjust(left=0, right=1, top=1, bottom=0)
        plt.savefig(buffer, format='png', bbox_inches='tight', pad_inches=0, transparent=True)
        plt.close()
        # Move buffer to the beginning so it can be read
        buffer.seek(0)
        # Load the image directly into Pygame
        image_dealt = pygame.image.load(buffer, 'damage_dealt.png')
        # Clean up the buffer
        buffer.close()
        return image_dealt

    else:
        raise ValueError("Invalid value for what_to_visualize. Choose 'received' or 'dealt'.")


def create_healing_summary(sort_reference_list=None, dataframe=None):
    if dataframe is None:
        file_path = './.tmp/tmp_healing_data.csv'
        df = pd.read_csv(file_path)
    else:
        df = dataframe
    # print(df)

    # Initialize dictionaries to accumulate healing received and given
    healing_received = {}
    healing_given = {}

    # Iterate over each character and their healing history
    for _, row in df.iterrows():
        character = row['Character']
        # healing_history = eval(row['Healing Received History'])
        healing_history_input = row['Healing Received History']

        # Check if healing_history_input is a string
        if isinstance(healing_history_input, str):
            # Handle empty strings
            if not healing_history_input.strip():
                healing_history = []
            else:
                healing_history = ast.literal_eval(healing_history_input)
        else:
            healing_history = healing_history_input
        # Initialize the received healing counter for the character
        healing_received[character] = 0

        # Iterate through the healing history
        for entry in healing_history:
            if entry:  # Check if entry is not empty
                heal_amount, healer = entry
                healing_received[character] += heal_amount

                # Initialize the given healing counter for the healer
                if healer not in healing_given:
                    healing_given[healer] = 0
                healing_given[healer] += heal_amount

    # Create a dataframe from the results
    summary_df = pd.DataFrame({
        'Character': healing_received.keys(),
        'healing_received': healing_received.values(),
        'healing_given': [healing_given.get(char, 0) for char in healing_received.keys()]
    })

    summary_df.fillna(0, inplace=True)
    summary_df = summary_df.astype({'healing_received': 'int', 'healing_given': 'int'})
    # Sort the dataframe based on the reference list
    if sort_reference_list:
        summary_df['Character'] = pd.Categorical(summary_df['Character'], categories=sort_reference_list, ordered=True)
        summary_df.sort_values('Character', inplace=True)

    # summary_df.to_csv('./.tmp/healing_summary.csv', index=False)

    return summary_df


def healing_summary_visualize(df):
    data = df

    # Preparing data for the grouped bar chart
    healing_received = data[['Character', 'healing_received']].copy()
    healing_given = data[['Character', 'healing_given']].copy()

    # Shorten character names if they are too long
    healing_received['Character'] = healing_received['Character'].astype(str).apply(lambda x: x[:7] if len(x) > 7 else x)
    healing_given['Character'] = healing_given['Character'].astype(str).apply(lambda x: x[:7] if len(x) > 7 else x)

    # Set the positions and width for the bars
    bar_width = 0.40
    index = np.arange(len(healing_received))

    # In-memory buffer for saving the image
    buffer = io.BytesIO()

    # Plotting the bars
    fig, ax = plt.subplots(figsize=(14, 6))

    ax.bar(index, healing_received['healing_received'], bar_width, label='Healing Received', color='forestgreen')
    ax.bar(index + bar_width, healing_given['healing_given'], bar_width, label='Healing Given', color='springgreen')

    ax.set_xticks(index + bar_width / 2)
    ax.set_xticklabels(healing_received['Character'])
    ax.legend(fontsize=22)

    # Display the plot
    plt.tight_layout()
    plt.xticks(fontsize=22)
    plt.yticks(fontsize=22)

    # Save the plot to the buffer
    plt.savefig(buffer, format='png', bbox_inches='tight', pad_inches=0, transparent=True)
    plt.close()

    # Move the buffer to the beginning so it can be read
    buffer.seek(0)

    # Load the image directly into Pygame
    image = pygame.image.load(buffer, 'healing_summary.png')

    # Clean up the buffer
    buffer.close()

    return image