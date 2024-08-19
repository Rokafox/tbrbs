import warnings
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


def create_damage_summary_new(sort_reference_list=None):
    file_path = './.tmp/tmp_damage_data.csv'
    damage_data = pd.read_csv(file_path)
    damage_dealt_summary = {}
    damage_received_summary = []

    def process_damage_entry(damage, attacker, damage_type):
        if attacker not in damage_dealt_summary:
            damage_dealt_summary[attacker] = {'total': 0, 'normal': 0, 'normal_critical': 0, 'status': 0, 'bypass': 0}
        
        damage_dealt_summary[attacker]['total'] += damage
        damage_dealt_summary[attacker][damage_type] += damage

    def process_damage_history(damage_history_str):
        damage_history = ast.literal_eval(damage_history_str)
        damage_summary = {'total': 0, 'normal': 0, 'normal_critical': 0, 'status': 0, 'bypass': 0}

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
        damage_dealt_df = pd.DataFrame(columns=['Character', 'total', 'normal', 'normal_critical', 'status', 'bypass'])


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


def damage_summary_visualize(df):
    data = df
    # for performance reasons, we will not read
    # file_path = './.tmp/damage_summary_combined_new.csv'
    # data = pd.read_csv(file_path)
    
    # Preparing data for the stacked bar chart
    damage_received = data[['Character', 'normal_received', 'normal_critical_received', 'status_received', 'bypass_received']].copy()
    damage_dealt = data[['Character', 'normal_dealt', 'normal_critical_dealt', 'status_dealt', 'bypass_dealt']].copy()

    # Shorten character names if they are too long using .loc to avoid SettingWithCopyWarning
    damage_received.loc[:, 'Character'] = damage_received['Character'].apply(lambda x: x[:7] if len(x) > 7 else x)
    damage_dealt.loc[:, 'Character'] = damage_dealt['Character'].apply(lambda x: x[:7] if len(x) > 7 else x)

    # Plotting the stacked bar chart for Damage Received
    plt.figure(figsize=(14, 6))
    plt.bar(damage_received['Character'], damage_received['normal_received'], label='Normal Damage Received', color='deepskyblue')
    plt.bar(damage_received['Character'], damage_received['normal_critical_received'], bottom=damage_received['normal_received'], label='Normal Critical Damage Received', color='darkturquoise')
    plt.bar(damage_received['Character'], damage_received['status_received'], bottom=damage_received['normal_received'] + damage_received['normal_critical_received'], label='Status Damage Received', color='lightblue')
    plt.bar(damage_received['Character'], damage_received['bypass_received'], bottom=damage_received['normal_received'] + damage_received['normal_critical_received'] + damage_received['status_received'], label='Bypass Damage Received', color='cadetblue')
    plt.xticks(fontsize=22)
    plt.yticks(fontsize=22)
    plt.subplots_adjust(left=0, right=1, top=1, bottom=0)
    plt.savefig('./.tmp/damage_taken.png', bbox_inches='tight', pad_inches=0, transparent=True)
    plt.close()

    # Plotting the stacked bar chart for Damage Dealt
    plt.figure(figsize=(14, 6))
    plt.bar(damage_dealt['Character'], damage_dealt['normal_dealt'], label='Normal Damage Dealt', color='tomato')
    plt.bar(damage_dealt['Character'], damage_dealt['normal_critical_dealt'], bottom=damage_dealt['normal_dealt'], label='Normal Critical Damage Dealt', color='firebrick')
    plt.bar(damage_dealt['Character'], damage_dealt['status_dealt'], bottom=damage_dealt['normal_dealt'] + damage_dealt['normal_critical_dealt'], label='Status Damage Dealt', color='orange')
    plt.bar(damage_dealt['Character'], damage_dealt['bypass_dealt'], bottom=damage_dealt['normal_dealt'] + damage_dealt['normal_critical_dealt'] + damage_dealt['status_dealt'], label='Bypass Damage Dealt', color='cadetblue')
    plt.xticks(fontsize=22)
    plt.yticks(fontsize=22)
    plt.subplots_adjust(left=0, right=1, top=1, bottom=0)
    plt.savefig('./.tmp/damage_dealt.png', bbox_inches='tight', pad_inches=0, transparent=True)
    plt.close()


def create_healing_summary(sort_reference_list=None):
    file_path = './.tmp/tmp_healing_data.csv'
    df = pd.read_csv(file_path)
    # Initialize dictionaries to accumulate healing received and given
    healing_received = {}
    healing_given = {}

    # Iterate over each character and their healing history
    for _, row in df.iterrows():
        character = row['Character']
        healing_history = eval(row['Healing Received History'])

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
    # file_path = './.tmp/healing_summary.csv'
    # data = pd.read_csv(file_path)
    data = df
    # Character,healing_received,healing_given
    # Cliffe,48500,0
    # Fenrir,0,35000
    # Gabe,20000,20000
    # Olive,13500,40500
    # Dophine,13500,0
    # Cerberus,30000,30000
    # Pheonix,0,0
    # Taily,60529,25001
    # Lillia,0,0
    # Clover,0,35528

    # Given the nature of data, use grouped bar chart

    # Preparing data for the grouped bar chart
    healing_received = data[['Character', 'healing_received']].copy()
    healing_given = data[['Character', 'healing_given']].copy()

    healing_received['Character'] = healing_received['Character'].astype(str).apply(lambda x: x[:7] if len(x) > 7 else x)
    healing_given['Character'] = healing_given['Character'].astype(str).apply(lambda x: x[:7] if len(x) > 7 else x)


    # Set the positions and width for the bars
    bar_width = 0.40
    index = np.arange(len(healing_received))

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
    plt.savefig('./.tmp/healing_summary.png', bbox_inches='tight', pad_inches=0, transparent=True)
    plt.close()
