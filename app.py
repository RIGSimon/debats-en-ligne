import json
import tkinter as tk
from tkinter import filedialog, messagebox
from graph import DebateGraph
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np
import platform
import os
import math

myUsername = None
path_to_dir = os.path.dirname(os.path.abspath(__file__))
path_to_db = path_to_dir + "/db/"


class DebateApp:
    def __init__(self, root, filename, nb, strategy="random"):
        self.root = root
        self.root.title("Comparaison d'arguments")
        self.root.geometry("600x500") 
        
        self.score = 0
        self.weighted_score = 0
        
        self.username = None

        self.debate_graph = DebateGraph(filename, nb, strategy)
        self.tab_score = np.zeros(self.debate_graph.height()) #tableau de taille hauteur de l'arbre
        self.graph = self.debate_graph.G.copy()
        self.order = self.debate_graph.order.copy()
        # print(self.order)
        self.index = -2

        self.pour = 0
        self.contre = 0
        
        #tournois
        self.waiting_var = tk.BooleanVar()
        
        self.chosen_node = None
        self.current_node1 = None
        self.current_node2 = None
        
        self.strategy = strategy
        self.is_tournoi = strategy == "tournoi"
        if self.is_tournoi:
            # print(self.order)
            self.parents = self.order[1]
            self.order = self.order[0]
        self.current_tournoi_index = 0

        menubar = tk.Menu(root)
        settings_menu = tk.Menu(menubar, tearoff=0)
        self.show_node_info = tk.BooleanVar(value=False)  
        settings_menu.add_checkbutton(label="Afficher les infos des nœuds", 
                            variable=self.show_node_info, 
                            command=self.toggle_node_info)
        menubar.add_cascade(label="Paramètres", menu=settings_menu)
        root.config(menu=menubar)

        self.label = tk.Label(self.root, 
                            text="Choisissez l'argument le plus convaincant", 
                            font=("Arial", 14))
        self.label.pack(pady=10, fill="both", expand=True)

        self.arg1_button = tk.Button(self.root, 
                                text="",  
                                command=lambda: self.next_step(None),
                                wraplength=500,
                                justify="left")
        self.arg2_button = tk.Button(self.root, 
                                text="", 
                                command=lambda: self.next_step(None), 
                                wraplength=500,
                                justify="left")

        self.unable_button = tk.Button(self.root, 
                                    text="Je ne peux pas décider", 
                                    command=lambda: self.next_step(None), 
                                    width=40, 
                                    height=3)

        """
        self.back_button = tk.Button(self.root, 
                                    text="↩️",
                                    command=lambda: self.next_step(1), 
                                    width=2, 
                                    height=2) 
        self.back_button.place(x=10, y=10)
        """

        self.context_button = tk.Button(self.root,
                                    text="Contexte",
                                    command=lambda: self.choose_arg(), 
                                    width=5, 
                                    height=2) 
        self.context_button.pack(side=tk.TOP, anchor = tk.NE)

        self.show = False
        self.show_label = None

        self.show_button = tk.Button(self.root, 
                                    text="?",
                                    command=lambda: self.show_main_arg(self.debate_graph), 
                                    width=2, 
                                    height=2)

        self.set_feedback = tk.Button(self.root, 
                                    text="Feedback",
                                    command=lambda: self.ask_feedback(self.root), 
                                    width=10, 
                                    height=2)

        self.arg1_button.pack(pady=5, fill="both", expand=True)
        self.arg2_button.pack(pady=5, fill="both", expand=True)
        self.unable_button.pack(pady=10)
        self.show_button.pack(side=tk.LEFT)
        self.set_feedback.pack()

        # Pour la transivité
        self.A = None
        self.B = None
        self.C = None
        self.D = None
        self.nb_transitions = round(len(self.order)*0.2,2)
        self.transition = False
        self.transitions_infos = [0, 0] # nb transitions valides / nb transitions non valides 
        self.compte = False
        self.stop = False

        self.next_step(None)  # Afficher la première paire
    
    def _format_node_text(self, node_id, text):
        """Format node text with level info if setting is enabled"""
        if not self.show_node_info.get():
            return text
        
        if platform.system() == "Darwin":
            predecessors = list(self.graph.predecessors(node_id))
            if predecessors:
                edge_data = self.graph.get_edge_data(predecessors[0], node_id)
                if edge_data:
                    relation = edge_data['relation']
                    if relation == 1:
                        arg = "[Pour]"

                    elif relation == -1:
                        arg = "[Contre]"

                    else:
                        arg = ""
        else:
            arg = ""
        
        level = self.graph.nodes[node_id].get('level', '?')
        return f"{text}\nNiveau: {level} {arg}"
    
    def _set_button_colors(self, button, node_id):
        """Set button color based on relation if show_info is active"""
        if not self.show_node_info.get():
            button.config(bg="light grey")  # Default color
            return
        
        if platform.system() != "Darwin":
            predecessors = list(self.graph.predecessors(node_id))
            if predecessors:
                edge_data = self.graph.get_edge_data(predecessors[0], node_id)
                if edge_data:
                    relation = edge_data['relation']
                    if relation == 1:
                        button.config(bg='#d4edda')  # Light green
                    elif relation == -1:
                        button.config(bg='#f8d7da')  # Light red
                    else:
                        button.config(bg='#d3d3d3')

    def toggle_node_info(self):
        """Toggle node info display setting"""
        self._refresh_display(None)
    
    def _refresh_display(self, feedback):
        global myUsername, path_to_db

        # print('refresh', self.index)
        """Refresh all displayed text and colors with current settings"""
        # Refresh main argument
        """
        main_arg = self.order[0] if self.order else ""
        if main_arg in self.graph.nodes:
            self.label.config(text=self._format_node_text(
                main_arg, 
                self.graph.nodes[main_arg].get("text", main_arg)
            ))
        """

        # print("index en dehors de la boucle :", self.index)
        
        if self.is_tournoi: #pour le tournois
            if self.current_node1 and self.current_node2:
                self.ask_user_to_choose(self.current_node1, self.current_node2)
            return
        

        n = ((len(self.order)//self.nb_transitions))*2 # pour 10 comp, n=10 (index)

        # Refresh current buttons
        if self.index >= 0 and (((len(self.order) % n == 0) and (self.index <= len(self.order))) or ((len(self.order) % n != 0) and (self.index < len(self.order)))):  
            
            if ((self.index + 2) % n == 0) and self.transition and self.stop:
                node1 = self.A
                node2 = self.C
                self.stop = False

            else:
                node1 = self.order[self.index]
                node2 = self.order[self.index+1]
                # print("self.index = ",self.index, "text = ",self.graph.nodes[node1].get("text", node1), "\n")
                # print("self.index+1 = ",self.index+1, "text = ", self.graph.nodes[node2].get("text", node2), "\n")

                if ((self.index + 2) % n == 0) and not self.stop:
                    self.stop = True
                
                if self.transition:
                    self.transition = False

            # print("index =", self.index)
            # print("transition ?", self.transition)
            
            idx1 = self.index
            idx2 = self.index + 1
            self.arg1_button.config(text=self._format_node_text(node1, self.graph.nodes[node1].get("text", node1)), command=lambda i=idx1, n=node1: [self.update_score(n, i), self.next_step(None)])
            self.arg2_button.config(text=self._format_node_text(node2, self.graph.nodes[node2].get("text", node2)), command=lambda i=idx2, n=node2: [self.update_score(n, i), self.next_step(None)])

            self._set_button_colors(self.arg1_button, node1)
            self._set_button_colors(self.arg2_button, node2)
            
            if (feedback != None):
                if not os.path.exists(path_to_db+'feedback_db.json'):
                    with open(path_to_db+'feedback_db.json', 'w') as f2:
                        f2.write("{}")

                with open(path_to_db+'feedback_db.json', 'r') as f1:
                    feedback_db = json.load(f1)

                    if myUsername in feedback_db.keys():
                        feedback_db[myUsername].append(str(node1) + ", " + str(node2) + " : " + feedback)

                    else:
                        feedback_db[myUsername] = [str(node1) + ", " + str(node2) + " : " + feedback]

                    with open(path_to_db+'feedback_db.json', 'w') as f2:
                        json.dump(feedback_db, f2)
                        
    def _get_best_argument(self, candidates):
        return candidates[0] if candidates else None

    def run_tournament(self, nodes):
        current_round = nodes[:]
        while len(current_round) > 1:
            next_round = []
            for i in range(0, len(current_round), 2):
                if i + 1 < len(current_round):
                    winner = self.ask_user_to_choose(current_round[i], current_round[i + 1])
                    next_round.append(winner)
                else:
                    next_round.append(current_round[i])  # Passe automatiquement au tour suivant
            current_round = next_round
        return current_round[0]

    def _display_arguments(self, node1, node2):
        if not node1 or not node2:
            return
        self.arg1_button.config(text=self._format_node_text(node1, self.graph.nodes[node1].get("text", node1)), 
                                command=lambda:[self.next_step(None), self.update_score(node1)])
        self.arg2_button.config(text=self._format_node_text(node2, self.graph.nodes[node2].get("text", node2)), 
                                command=lambda:[self.next_step(None), self.update_score(node2)])
        self._set_button_colors(self.arg1_button, node1)
        self._set_button_colors(self.arg2_button, node2)
        
    def ask_user_to_choose(self, node1, node2):
        self.current_node1 = node1
        self.current_node2 = node2
        self.chosen_node = None
        self.waiting_var.set(False)
    
        def choose_node(n):
            self.chosen_node = n
            #self.update_score(n) inutile pour le tournois
            self.waiting_var.set(True)
    
        self._display_arguments(node1, node2)
        self.arg1_button.config(command=lambda: choose_node(node1))
        self.arg2_button.config(command=lambda: choose_node(node2))
        self.unable_button.config(command=lambda: choose_node(None))
    
        self.root.wait_variable(self.waiting_var)
        return self.chosen_node

    def choose_arg (self):
        new_window = tk.Tk()
        new_window.title("Contexte")

        label = tk.Label(new_window, 
                            text="Pour quel argument voulez-vous le contexte ?", 
                            font=("Arial", 14))
        
        label.pack(pady=10, fill="both", expand=True)

        options = ["1", "2"]
        selected_option = tk.StringVar(new_window)
        selected_option.set(options[0])

        option_menu = tk.OptionMenu(new_window, 
                                    selected_option, 
                                    *options)
        option_menu.pack(pady=5)

        send_button = tk.Button(new_window, 
                           text="Envoyer", 
                           command=lambda: self.launch_context_window(new_window, selected_option.get()))
        
        send_button.pack(pady=10)

    
    def launch_context_window(self, root, selected_option):
        root.destroy()
        new_window = tk.Tk()
        new_window.title("Contexte de l'argument " + selected_option)

        if selected_option == "1":
            node = self.order[self.index]

        else:
            node = self.order[self.index+1]

        pred = list(self.graph.predecessors(node))[0]
        text = self.graph.nodes[pred].get("text", pred)

        label = tk.Label(new_window, 
                            text=text, 
                            font=("Arial", 14))
        
        label.pack(pady=10, fill="both", expand=True)


    def show_main_arg(self, graph):
        self.show = not self.show

        if (self.show):
            self.show_label = tk.Label(self.root, 
                            text=self._format_node_text(graph.main_arg, graph.nodes[graph.main_arg].get("text", graph.main_arg)),  
                            font=("Arial", 14))
            self.show_label.pack(pady=10, fill="both", expand=True)

        else:

            self.show_label.destroy()


    def ask_feedback(self, root):
        feedback_root = tk.Toplevel(root)
        feedback_entry = tk.Text(feedback_root, width=100, height=2)
        feedback_entry.pack(pady=5)

        send_button = tk.Button(feedback_root, 
                           text="Envoyer", 
                           command=lambda:[self._refresh_display(feedback_entry.get("1.0", tk.END).strip()), self.destroy_windows(feedback_root, send_button)])
        
        send_button.pack(pady=10)

    def destroy_windows(self, root, button):
        root.destroy()
        button.destroy()


    def update_score(self, node, chosen_node_index):
        # print("update ello:")
        # print(node, chosen_node_index)
        # print(self.order[chosen_node_index])
        # print(self.order, len(self.order))
        n = ((len(self.order)//self.nb_transitions))*2 
        # print(self.index, chosen_node_index, n)

        if (self.index + 4) % n == 0: # a 2 comp
            self.A = self.order[chosen_node_index] 

            if (chosen_node_index == self.index): 
                self.B = self.order[chosen_node_index+1]
            
            else: # on a choisi self.index+1
                self.B = self.order[chosen_node_index-1]
            
            # print("A =", self.graph.nodes[self.A].get("text", self.A))
            # print("B =", self.graph.nodes[self.B].get("text", self.B))
                
        if (self.index + 2) % n == 0: # a 1 comp
            self.C = self.order[chosen_node_index] 

            if chosen_node_index == self.index:
                self.D = self.order[chosen_node_index+1]
                
            else:
                self.D = self.order[chosen_node_index-1]

            # print("C =", self.graph.nodes[self.C].get("text", self.C))
            # print("D =", self.graph.nodes[self.D].get("text", self.D))
            self.transition = True
        
        if self.transition and not self.stop:
            self.compte = True

        if self.compte :
            if node == self.A:
                self.transitions_infos[0] += 1
            
            if node == self.C:
                self.transitions_infos[1] += 1

            self.compte = False
            print("Infos Transitions - Cohérence :", self.transitions_infos)    
        
        if not self.transition: # le test de la transitivité ne doit pas impacter le score
            cur_node = node
            prev_node = list(self.graph.predecessors(cur_node))[0]
            buffer_score = 1
            done = False
            while not done:
                if int(self.graph.get_edge_data(prev_node, cur_node)["relation"]) == 0.0:
                    done = True
                    break
                buffer_score = buffer_score * int(self.graph.get_edge_data(prev_node, cur_node)["relation"])
                cur_node = list(self.graph.predecessors(cur_node))[0]
                prev_node = list(self.graph.predecessors(prev_node))[0]
            
            if (self.graph.nodes[node].get('level', '?') == 0):
                self.weighted_score +=  buffer_score

            else:
                self.weighted_score +=  buffer_score / self.graph.nodes[node].get('level', '?') 
                self.tab_score[self.graph.nodes[node].get('level', '?')-1] += buffer_score 
                if (buffer_score == 1):
                    self.pour += buffer_score / self.graph.nodes[node].get('level', '?')

                else:
                    self.contre += buffer_score / self.graph.nodes[node].get('level', '?')*(-1)

            self.score += buffer_score

    def next_step(self, choice):
        # print('next', self.index)
        
        if self.is_tournoi: #tournois
            if self.current_tournoi_index >= len(self.order):
                self._end_debate()
                return
        
            pour_list, contre_list = self.order[self.current_tournoi_index]
            
            best_pour = self.run_tournament(pour_list)
            best_contre = self.run_tournament(contre_list)
        
            # Final match
            winner = self.ask_user_to_choose(best_pour, best_contre)
            self.current_tournoi_index += 1
            self.next_step(None)
            return
        
        if ((self.index + 2 >= len(self.order)) and not self.stop):
            self.label.config(text="Fin du débat")
            # self.back_button.destroy()
            self.arg1_button.pack_forget()
            self.arg2_button.pack_forget()
            self.unable_button.pack_forget()
            self.set_feedback.pack_forget()
            self.context_button.pack_forget()
            self.show_button.pack_forget()
            
            arg_button = tk.Button(self.root, 
                                text="Analyse des résultats",  
                                command=lambda: analyse_window(self.score, self.weighted_score, self.tab_score, self.pour, self.contre, self.transitions_infos, self.root, self.debate_graph.nodes[self.debate_graph.main_arg].get("text", self.debate_graph.main_arg), self.strategy, myUsername),
                                wraplength=500, 
                                justify="left")
            arg_button.pack(pady=5, expand=True)
            return
        
        if choice == None:

            if not self.stop:
                self.index += 2
            
            #print("refresh")
            self._refresh_display(None)
        
        """
        else:
            if choice >= 0:
                if self.index >= 2:
                    self.index -= 2
                    self._refresh_display(None)
        """
                
    def _end_debate(self):
        self.label.config(text="Fin du débat")
        # self.back_button.destroy()
        self.arg1_button.pack_forget()
        self.arg2_button.pack_forget()
        self.unable_button.pack_forget()
        self.set_feedback.pack_forget()
        self.context_button.pack_forget()
        self.show_button.pack_forget()
        
        node = self.chosen_node
        argument = self.graph.nodes[node].get("text", node)
        pour = self.graph.get_edge_data(self.parents[0], node).get("relation", 0) == 1
        
        arg_button = tk.Button(self.root, 
                               text="Analyse des résultats",  
                               command=lambda: analyse_tournoi(self.chosen_node, self.parents, self.graph, self.root, self.debate_graph.nodes[self.parents[0]].get("text", self.debate_graph.main_arg)),
                               wraplength=500, 
                               justify="left")
        arg_button.pack(pady=5, expand=True)

def analyse_tournoi(chosen_node, parents, graph, debate_root, pere):
    debate_root.destroy()
    root = tk.Tk()
    root.title("Résultats du Tournoi")

    # Bouton retour
    button = tk.Button(root,
                       text="Home", 
                       command=lambda: launch_main_window(root))
    button.pack(side=tk.TOP, expand=True, fill='both')

    # Texte de l'argument choisi
    argument = graph.nodes[chosen_node].get("text", chosen_node)
    argument_label = tk.Label(root,
                              text="Argument sélectionné :\n" + argument,
                              wraplength=500,
                              justify="left",
                              font=("Arial", 12))
    argument_label.pack(pady=10)

    # Déterminer la position par rapport à l'argument principal
    try:
        relation = graph.get_edge_data(parents[0], chosen_node).get("relation", 0)
    except:
        relation = 0

    if relation == 1:
        position = "Vous êtes en faveur de l'argument :"
        sizes = [100, 0]
        colors = ["lightgreen", "lightpink"]
    elif relation == -1:
        position = "Vous êtes opposé à l'argument :"
        sizes = [0, 100]
        colors = ["lightgreen", "lightpink"]
        
    position_label = tk.Label(root,
                              text=f"{position}\n{pere}",
                              font=("Arial", 12),
                              wraplength=500,
                              justify="center")
    position_label.pack(pady=10)

    root.mainloop()
            
def analyse_window(score, weighted_score, tab_score, pour, contre, transitions_infos, debate_root, main_arg, username, strategy):
    debate_root.destroy()
    root = tk.Tk()
    root.title("Résultats")
    # print(tab_score)
    button = tk.Button(root,
                        text="Home", 
                        command=lambda: launch_main_window(root), 
                        width=3,
                        height=2)

    button.place(x=10, y=10)

    # print(score)
    # print(weighted_score)
    save_user_score(username=username, strategy=strategy, score=tab_score.tolist())
    if weighted_score > 0:
        label = tk.Label(root, text="Vous êtes en faveur de l'argument : " + main_arg, height=5)

    elif weighted_score < 0:
        label = tk.Label(root, text="Vous êtes opposé à l'argument : " + main_arg, height=5)

    else:
        label = tk.Label(root, text="Vous êtes neutre vis-à-vis de l'argument : " + main_arg, height=5)

    label.pack(padx=10, pady=10)

    # === Cadre horizontal pour les deux figures côte à côte ===
    figures_frame = tk.Frame(root)
    figures_frame.pack()

    # --- Pie Chart ---
    fact = 100 / (pour + contre) if (pour + contre) > 0 else 0
    y = np.array([pour, contre]) * fact

    fig1, ax1 = plt.subplots()
    ax1.pie(y, labels=["Pour", "Contre"], colors=["lightgreen", "lightpink"], autopct='%1.1f%%')
    ax1.set_title("Répartition de vos choix")
    ax1.axis('equal')

    canvas1 = FigureCanvasTkAgg(fig1, master=figures_frame)
    canvas1.draw()
    canvas1.get_tk_widget().pack(side=tk.LEFT, padx=10)

    # --- Bar Chart for tab_score ---
    levels = [f"Niveau {i+1}" for i in range(len(tab_score))]
    colors = ["green" if val > 0 else "red" if val < 0 else "gray" for val in tab_score]

    fig2, ax2 = plt.subplots()
    ax2.bar(levels, tab_score, color=colors)
    ax2.set_title("Opinion par niveau")
    ax2.set_xlabel("Niveaux")
    ax2.set_ylabel("Score pondéré")
    min_val = min(0, np.min(tab_score))
    max_val = max(0.01, np.max(tab_score))
    ax2.set_ylim(min_val * 1.2, max_val * 1.2)

    canvas2 = FigureCanvasTkAgg(fig2, master=figures_frame)
    canvas2.draw()
    canvas2.get_tk_widget().pack(side=tk.LEFT, padx=10)

    # --- Transition Coherence ---
    total_transitions = transitions_infos[0] + transitions_infos[1]
    if total_transitions > 0:
        p = transitions_infos[0] / total_transitions * 100
    else:
        p = 0.0
    label_trans = tk.Label(root, text=f"Taux de cohérence par rapport aux tests de transitivité : {p:.1f} %")
    label_trans.pack(padx=10, pady=10)

    root.mainloop()

def save_user_score(username, strategy, score, filepath=path_to_db+"user_stats.json"):
    # Charger le fichier s'il existe, sinon démarrer avec un dict vide
    if os.path.exists(filepath):
        with open(filepath, "r") as f:
            data = json.load(f)
    else:
        data = {}

    # Créer les niveaux manquants dans la hiérarchie
    if username not in data:
        data[username] = {}
    if strategy not in data[username]:
        data[username][strategy] = []

    # Ajouter le score
    data[username][strategy].append(score)

    # Sauvegarder dans le fichier
    with open(filepath, "w") as f:
        json.dump(data, f, indent=4)


def launch_home_window():
    root = tk.Tk()
    root.title("Connexion")
    root.geometry("400x300")
    
    label = tk.Label(root, 
                    text="Bienvenue, veuillez vous connecter ou vous inscrire.", 
                    font=("Arial", 12))
    label.pack(pady=20)
    
    login_button = tk.Button(root, 
                            text="Se connecter", 
                            command=lambda: launch_login_window(root), 
                            width=20, 
                            height=2)
    register_button = tk.Button(root, 
                              text="S'inscrire",
                              command=lambda: launch_register_window(root),
                              width=20, 
                              height=2)
    login_button.pack(pady=5)
    register_button.pack(pady=5)
    
    root.mainloop()


def launch_main_window(analyse_root):

    if (analyse_root != None):
        analyse_root.destroy()

    root = tk.Tk()
    root.title("Page principale")
    root.geometry("400x300")
    
    label = tk.Label(root, 
                    text="Bienvenue dans l'application de débat", 
                    font=("Arial", 14))
    label.pack(pady=20)
    
    load_button = tk.Button(root, 
                          text="Charger un débat", 
                          command=lambda: load_debate_file(root), 
                          width=20, 
                          height=2)
    load_button.pack(pady=10)
    
    root.mainloop()


def launch_selection_window(filename, root):
    selection_root = tk.Tk()
    selection_root.title("Débat")
    selection_root.geometry("400x400")
    
    label = tk.Label(selection_root, 
                    text="Fichier sélectionné :\n" + filename, 
                    font=("Arial", 12), wraplength=380, 
                    justify="center")
    label.pack(pady=10)

    graph = DebateGraph(filename, -1, "BFS")  # Load full graph for info
    order_length = len(graph.order)
    nb_comp_tot = int(order_length/2)

    options = [i for i in range(10, nb_comp_tot + 1, 20)]
    options.append(nb_comp_tot)
    options_ajout = []

    for i in range (len(options)):
        nb_arg = options[i]*2
        nb_transitions = round(nb_arg*0.2, 2)
        n = nb_arg//nb_transitions*2
        nb_tot = options[i] + math.floor(nb_arg/n)
        options[i] = nb_tot
        options_ajout.append(math.floor(nb_arg/n))
        # print(nb_transitions, nb_arg, n, nb_tot)

    selected_num_questions = tk.IntVar(selection_root)
    selected_num_questions.set(options[-1])

    titre = tk.Label(selection_root, 
                    text="Sélectionnez le nombre de questions", 
                    font=("Arial", 14), wraplength=380, 
                    justify="center")
    titre.pack(pady=10)

    num_questions_menu = tk.OptionMenu(selection_root, 
                                     selected_num_questions,
                                     *options)
    num_questions_menu.pack(pady=10)

    # Strategy selection
    strategies = ["random", "BFS", "DFS", "priority", "tournoi"]
    selected_strategy = tk.StringVar(selection_root)
    selected_strategy.set(strategies[0])

    strategy_label = tk.Label(selection_root, 
                            text="Choisissez une stratégie:", 
                            font=("Arial", 12))
    strategy_label.pack(pady=5)

    strategy_menu = tk.OptionMenu(selection_root, 
                                selected_strategy, 
                                *strategies)
    strategy_menu.pack(pady=5)

    start_button = tk.Button(selection_root, 
                           text="Lancer le débat", 
                           command=lambda: launch_debate_window(selection_root, filename, options_ajout, options, selected_num_questions.get(), selected_strategy.get(), root),
                           width=20, 
                           height=2)
    start_button.pack(pady=10)

    selection_root.mainloop()


def launch_debate_window(selection_root, filename, options_ajout, options, nb, strategy, root):
    root.destroy()
    selection_root.destroy()
    debate_root = tk.Tk()
    ind = options.index(nb)
    nb_final = nb - options_ajout[ind]
    # print("nb =", nb_final)
    app = DebateApp(debate_root, filename, nb_final, strategy)
    debate_root.mainloop()


def launch_login_window(root):
    login_root = tk.Toplevel(root)
    login_root.title("Connexion")
    login_root.geometry("300x200")
    
    tk.Label(login_root, text="Pseudo").pack(pady=5)
    username_entry = tk.Entry(login_root)
    username_entry.pack(pady=5)
    
    tk.Label(login_root, text="Mot de passe").pack(pady=5)
    password_entry = tk.Entry(login_root, show="*")
    password_entry.pack(pady=5)
    
    def validate_login(root):
        global myUsername
        username = username_entry.get()
        password = password_entry.get()

        if username and password:
            if not os.path.exists(path_to_db+'user_db.json'):
                with open(path_to_db+'user_db.json', 'w') as f:
                    f.write("{}")

            with open(path_to_db+'user_db.json', 'r') as file:
                user_db = json.load(file)
            if username in user_db.keys() and user_db[username] == password:
                myUsername = username
                login_root.destroy()
                root.destroy()
                launch_main_window(None)
            else:
                messagebox.showerror("Erreur", "Nom d'utilisateur/Mot de passe incorrect")
        else:
            messagebox.showerror("Erreur", "Veuillez remplir tous les champs.")
    
    login_button = tk.Button(login_root, 
                           text="Se connecter", 
                           command=lambda: validate_login(root))
    login_button.pack(pady=10)


def launch_register_window(root):
    login_root = tk.Toplevel(root)
    login_root.title("Inscription")
    login_root.geometry("300x300")
    
    tk.Label(login_root, text="Pseudo").pack(pady=5)
    username_entry = tk.Entry(login_root)
    username_entry.pack(pady=5)
    
    tk.Label(login_root, text="Mot de passe").pack(pady=5)
    password_entry = tk.Entry(login_root, show="*")
    password_entry.pack(pady=5)

    tk.Label(login_root, text="Confirmation du mot de passe").pack(pady=5)
    repassword_entry = tk.Entry(login_root, show="*")
    repassword_entry.pack(pady=5)
    
    def validate_register(root):
        username = username_entry.get()
        password = password_entry.get()
        repassword = repassword_entry.get()

        if username and password and repassword and (password == repassword):
            with open(path_to_db+'user_db.json', 'r') as f1:
                log_dict = json.load(f1)
            if username not in log_dict.keys():
                log_dict[username] = password
                with open(path_to_db+'user_db.json', 'w') as f2:
                    json.dump(log_dict, f2)
                login_root.destroy()
                root.destroy()
                launch_main_window(None)
            else:
                messagebox.showerror("Erreur", "Ce nom d'utilisateur n'est pas disponible")
        else:
            if password != repassword:
                messagebox.showerror("Erreur", "Mots de passe différents !")
            else:
                messagebox.showerror("Erreur", "Veuillez remplir tous les champs.")
    
    login_button = tk.Button(login_root, 
                           text="S'inscrire", 
                           command=lambda: validate_register(root))
    login_button.pack(pady=10)


def load_debate_file(root):
    file_path = filedialog.askopenfilename(title="Sélectionner un fichier de débat", filetypes=[("Fichiers JSON", "*.json")])
    if file_path:
        launch_selection_window(file_path, root)


if __name__ == '__main__':
    launch_home_window()