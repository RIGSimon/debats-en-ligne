# Projet : Evaluation de débats en ligne par comparaison d'arguments


## Contributeurs

Simon RIGOLLIER, Michelle SONG et Aurélien CHAMBOLLE-SOLAZ.

Encadrant : Nicolas MAUDET


## Organisation des fichiers et commandes à éxécuter

```
debats-en-ligne
├── app.py
├── graph.py
├── README.md
├── Rapport_PANDRO.pdf
├── data
│   ├── 1229.json
│   ├── 27596.json
│   └── 30339.json
└── db
    ├── user_db.json
    ├── feedback_db.json
    └── user_stats.json
```

Pour démarrer l'application, exécutez le fichier `app.py`. Pour générer un débat, vous pouvez choisir un des fichiers du dossier `data`.

Le fichier `graph.py` contient l'implémentation du graphe associé au débat choisi. Si vous l'excécutez, vous pourrez visualiser ce graphe.

Pour plus de détails, veuillez consuler le fichier `Rapport_PANDRO.pdf`.


## Contexte

Les débats en ligne sont souvent influencés par la manière dont les arguments sont formulés, présentés et évalués. Sur des plateformes comme Kialo, les utilisateurs votent pour ou contre des arguments, mais ces votes ne permettent pas toujours de clarifier l'intention exacte des participants. Il est souvent difficile de savoir si un vote exprime un soutien à l'argument ou s'il reflète simplement une évaluation de sa pertinence.  
L'idée est donc de développer une méthode d'analyse plus précise en remplaçant le vote traditionnel par une approche de comparaison directe entre arguments.  
  
  
## Objectifs

Le principal objectif du projet est de créer une application permettant de charger des débats sous forme de graphes d'arguments et de faire des comparaisons pair-à-pair entre ces arguments.  
L'application proposera deux arguments à comparer et permettra aux utilisateurs de choisir celui qu'ils jugent le plus convaincant. Ce processus sera répété pour affiner les résultats.  
Elle devra aussi enregistrer les réponses des utilisateurs et permettre une analyse des résultats afin de tirer des conclusions sur la manière dont les différents arguments soutiennent ou attaquent la question principale du débat.  
  
  
## Fonctionnalités

L'interface du prototype sera organisée en trois principaux modules :

### Chargement d'un débat et lancement de la séquence de questions

Le système devra être capable d'importer un débat au format JSON, préalablement structuré et extrait de Kialo. Cette base de données servira de support pour toutes les interactions et analyses menées par l'application.  
Les métadonnées associées aux arguments pourront également être prises en compte pour enrichir les comparaisons.  
Une fois le débat chargé, l'utilisateur pourra initier une séquence de questions permettant d'évaluer les arguments de manière comparative. Plusieurs stratégies seront mises en place pour poser ces questions :
- Présenter deux arguments en faveur d'une même position et demander lequel est le plus convaincant.
- Comparer deux arguments opposés (un pour et un contre) afin de mieux cerner l'impact des points de vue divergents.

Chaque utilisateur devra répondre à plusieurs comparaisons successives, permettant ainsi d'établir une hiérarchie des arguments en fonction de leur pouvoir de persuasion.  
Il sera également envisageable d'ajouter un module de retour utilisateur pour recueillir leur feedback sur un argument, ainsi qu'un module permettant de remonter dans l'arborescence des arguments s'ils souhaitent connaître le contexte de l'argument courant.

### Enregistrement et gestion des votes

Les utilisateurs devront se connecter via un identifiant afin de garantir la traçabilité des réponses. Chaque vote sera enregistré et associé à un utilisateur pour permettre une analyse approfondie des préférences et tendances argumentatives. Le système devra permettre l'accumulation des votes et leur récupération pour une exploitation ultérieure.  
Pour favoriser l'engagement, une représentation visuelle des tendances argumentatives pourra être intégrée, permettant aux participants de situer leurs choix par rapport à l'ensemble des réponses collectées.

### Analyse des résultats

Une fois les votes collectés, un module d'analyse proposera plusieurs axes d'interprétation :
- Étudier la répartition des préférences et mettre en évidence les arguments les plus convaincants.
- Évaluer dans quelle mesure la question principale du débat est soutenue ou contestée.
  
On pourra explorer différentes méthodologies pour quantifier l'impact des comparaisons par paires par rapport aux méthodes traditionnelles de pondération des arguments.