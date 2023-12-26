import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns


def create_report():
    file_path = './win_loss_data.csv'
    data = pd.read_csv(file_path)
    character_performance = data.groupby('character_name')['winrate'].mean().sort_values(ascending=False)
    equipment_performance = data.groupby('equipment_set')['winrate'].mean().sort_values(ascending=False)
    with open('./reports/performance.txt', 'w') as file:
        file.write("Character Performance:\n")
        file.write(str(character_performance))
        file.write("\n\nEquipment Performance:\n")
        file.write(str(equipment_performance))
    return data

def generate_heatmap(data):
    heatmap_data = data.pivot(index='character_name', columns='equipment_set', values='winrate')
    plt.figure(figsize=(15, 8))
    sns.heatmap(heatmap_data, annot=True, fmt=".1f", cmap="coolwarm")
    plt.title("Win Rates of Characters with Different Equipment Sets")
    plt.xlabel("Equipment Set")
    plt.ylabel("Character Name")
    plt.savefig('./reports/heatmap.png')




