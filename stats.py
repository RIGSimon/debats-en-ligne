import json
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path

file_path = Path('db/user_stats.json')
with open(file_path, 'r') as f:
    data = json.load(f)

avis_utilisateurs = { #entrer les avis des utilisateurs restants
    "Aurelien": "pour",
    "iona": "pour",
    "simon": "pour",
    "ms": "contre"
}

users = sorted({user for strat in data.values() for user in strat})
strategies = ['random', 'BFS', 'priority']

fig, axes = plt.subplots(len(users), len(strategies), figsize=(len(strategies)*2.5, len(users)*1.5))

if len(users) == 1:
    axes = [axes]  # garantir l’itérabilité si une seule ligne

for i, user in enumerate(users):
    for j, strategy in enumerate(strategies):
        ax = axes[i][j] if len(users) > 1 else axes[j]
        values = data.get(strategy, {}).get(user, [[None]*5])[0]
        values += [None] * (5 - len(values))
        safe_values = [v if v is not None else 0 for v in values]
        colors = ['green' if v is not None and v >= 0 else 'red' for v in values]

        ax.bar(range(1, 6), safe_values, color=colors)
        ax.set_xticks([])
        ax.set_yticks([])
        ax.set_ylim(-1, 1)
        ax.set_xlim(0.5, 5.5)
        if j == 0:
            ax.set_ylabel(user, rotation=0, labelpad=40, fontsize=10, va='center')
        if i == 0:
            ax.set_title(strategy, fontsize=10)

plt.tight_layout()
plt.show()

users = sorted({user for strat in data.values() for user in strat})
strategies = ['random', 'BFS', 'priority']
weights = np.array([1 / np.exp(i) for i in range(1, 6)])

rows = []
for user in users:
    row = {'Utilisateur': user}
    for strategy in strategies:
        values = data.get(strategy, {}).get(user, [[None]*5])[0]
        values += [None] * (5 - len(values))
        values_np = np.array([v if v is not None else 0 for v in values])
        weighted_average = np.dot(values_np, weights) / weights.sum()
        row[strategy] = weighted_average
    rows.append(row)

df_weighted = pd.DataFrame(rows)

# Création des subplots (2 lignes x 2 colonnes)
fig, axes = plt.subplots(2, 2, figsize=(10, 6))
axes = axes.flatten()

for i, (_, row) in enumerate(df_weighted.iterrows()):
    user = row['Utilisateur']
    values = [row[strat] for strat in strategies]
    mean_val = np.mean(values)

    ax = axes[i]
    ax.bar(strategies, values, color='skyblue')
    ax.axhline(mean_val, color='red', linestyle='--', label=f"Moyenne = {mean_val:.2f}")
    ax.set_ylim(0, 1)
    avis = avis_utilisateurs.get(user, "inconnu")
    ax.set_title(f"{user} (avis : {avis})")
    ax.set_ylabel("Moyenne pondérée")
    ax.legend()

plt.suptitle("Moyennes pondérées par utilisateur et par stratégie", fontsize=14)
plt.tight_layout(rect=[0, 0, 1, 0.95])
plt.show()