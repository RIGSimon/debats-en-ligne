import json
import tkinter as tk
from tkinter import filedialog, messagebox
from graph import DebateGraph
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np
import platform
import sys
import os

if (platform.system() == "Darwin"):
    import tkmacosx as tkmac


myUsername = None

class DebateApp:
    def __init__(self, root, filename, nb, strategy="random"):
        self.root = root
        self.root.title("Comparaison d'arguments")
        self.root.geometry("600x500") 
        self.score = 0
        self.weighted_score = 0
        self.username = None

        self.debate_graph = DebateGraph(filename, nb, strategy)

        self.graph = self.debate_graph.G.copy()
        self.order = self.debate_graph.order.copy()
    
        self.waiting_var = tk.BooleanVar()
        self.chosen_node = None
        self.index = -2
        
        self.pour = 0
        self.contre = 0

        self.strategy = strategy
        self.is_tournoi = strategy == "tournoi"
        if self.is_tournoi:
            print(self.order)
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

        if platform.system() == "Darwin" :
            self.arg1_button = tkmac.Button(self.root, 
                                    text="",  
                                    command=lambda: self.next_step(None),
                                    justify="left")
            self.arg2_button = tkmac.Button(self.root, 
                                    text="", 
                                    command=lambda: self.next_step(None), 
                                    justify="left")
        else:
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

        self.back_button = tk.Button(self.root, 
                                    text="↩️",
                                    command=lambda: self.next_step(1), 
                                    width=2, 
                                    height=2) 
        self.back_button.place(x=10, y=10)

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

        self.next_step(None)

    def _format_node_text(self, node_id, text):
        if not self.show_node_info.get():
            return text
        level = self.graph.nodes[node_id].get('level', '?')
        return f"{text}\nNiveau: {level}"

    def _set_button_colors(self, button, node_id):
        if not self.show_node_info.get():
            button.config(bg="light grey")
            return
        predecessors = list(self.graph.predecessors(node_id))
        if predecessors:
            edge_data = self.graph.get_edge_data(predecessors[0], node_id)
            if edge_data:
                relation = edge_data['relation']
                if relation == 1:
                    button.config(bg='#d4edda')
                elif relation == -1:
                    button.config(bg='#f8d7da')
                else:
                    button.config(bg='#d3d3d3')

    def toggle_node_info(self):
        self._refresh_display(None)

    def _refresh_display(self, feedback):
        if self.is_tournoi:
            return
        if self.index < len(self.order) - 1:
            node1 = self.order[self.index]
            node2 = self.order[self.index+1]
            self._display_arguments(node1, node2)
            if feedback is not None:
                self._save_feedback(node1, node2, feedback)

    def _display_arguments(self, node1, node2):
        if not node1 or not node2:
            return
        self.arg1_button.config(text=self._format_node_text(node1, self.graph.nodes[node1].get("text", node1)), 
                                command=lambda:[self.next_step(None), self.update_score(node1)])
        self.arg2_button.config(text=self._format_node_text(node2, self.graph.nodes[node2].get("text", node2)), 
                                command=lambda:[self.next_step(None), self.update_score(node2)])
        self._set_button_colors(self.arg1_button, node1)
        self._set_button_colors(self.arg2_button, node2)

    def _save_feedback(self, node1, node2, feedback):
        global myUsername
        if not os.path.exists('feedback_db.json'):
            with open('feedback_db.json', 'w') as f:
                f.write("{}")
        with open('feedback_db.json', 'r') as f:
            feedback_db = json.load(f)
        if myUsername in feedback_db:
            feedback_db[myUsername].append(f"{node1}, {node2} : {feedback}")
        else:
            feedback_db[myUsername] = [f"{node1}, {node2} : {feedback}"]
        with open('feedback_db.json', 'w') as f:
            json.dump(feedback_db, f)

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

    def ask_user_to_choose(self, node1, node2):
        self.chosen_node = None
        self.waiting_var.set(False)
    
        def choose_node(n):
            self.chosen_node = n
            self.update_score(n)
            self.waiting_var.set(True)
    
        self._display_arguments(node1, node2)
        self.arg1_button.config(command=lambda: choose_node(node1))
        self.arg2_button.config(command=lambda: choose_node(node2))
        self.unable_button.config(command=lambda: choose_node(None))
    
        self.root.wait_variable(self.waiting_var)
        return self.chosen_node


    def next_step(self, choice):
        if self.is_tournoi:
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
        else:
            if self.index >= len(self.order) - 1:
                self._end_debate()
                return
            if choice is None:
                self.index += 2
                self._refresh_display(None)
            elif choice >= 0:
                if self.index >= 2:
                    self.index -= 2
                    self._refresh_display(None)

    def _end_debate(self):
        self.label.config(text="Fin du débat")
        self.back_button.destroy()
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

        send_button = tk.Button(root, 
                           text="Envoyer", 
                           command=lambda:[self._refresh_display(feedback_entry.get("1.0", tk.END).strip()), self.destroy_windows(feedback_root, send_button)])
        
        send_button.pack(pady=10)

    def destroy_windows(self, root, button):
        root.destroy()
        button.destroy()


    def update_score(self, node):
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

            if (buffer_score == 1):
                self.pour += buffer_score / self.graph.nodes[node].get('level', '?')

            else:
                self.contre += buffer_score / self.graph.nodes[node].get('level', '?')*(-1)

        self.score += buffer_score

def analyse_tournoi(chosen_node, parents, graph, debate_root, pere):
    debate_root.destroy()
    root = tk.Tk()
    root.title("Résultats du Tournoi")

    # Bouton retour
    button = tk.Button(root,
                       text="Home", 
                       command=lambda: launch_main_window(root), 
                       width=3,
                       height=2)
    button.place(x=10, y=10)

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
        position = "Vous êtes en faveur de l'argument principal :"
        sizes = [100, 0]
        colors = ["lightgreen", "lightpink"]
    elif relation == -1:
        position = "Vous êtes opposé à l'argument principal :"
        sizes = [0, 100]
        colors = ["lightgreen", "lightpink"]
        
    position_label = tk.Label(root,
                              text=f"{position}\n{pere}",
                              font=("Arial", 12),
                              wraplength=500,
                              justify="center")
    position_label.pack(pady=10)

    root.mainloop()


def analyse_window(score, weighted_score, pour, contre, debate_root, main_arg):
    debate_root.destroy()
    root = tk.Tk()
    root.title("Résultats")

    button = tk.Button(root,
                        text="Home", 
                        command=lambda: launch_main_window(root), 
                        width=3,
                        height=2)

    button.place(x=10, y=10)

    print(score)
    print(weighted_score)

    if weighted_score > 0:
        label = tk.Label(root, text="Vous êtes en faveur de l'argument : "+main_arg, height=5)

    elif weighted_score < 0:
        label = tk.Label(root, text="Vous êtes opposé à l'argument : "+main_arg, height=5)

    else:
        label = tk.Label(root, text="Vous êtes neutre vis-à-vis de l'argument : "+main_arg, height=5)

    label.pack(padx=10, pady=10)

    fact = 100 / (pour + contre)
    y = np.array([pour, contre])*fact

    # Création de la figure matplotlib
    fig, ax = plt.subplots()
    ax.pie(y, labels=["Pour", "Contre"], colors=["lightgreen", "lightpink"])
    ax.set_title("Répartition de vos choix")
    ax.axis('equal')
    ax.legend()

    # Intégration de la figure dans Tkinter
    canvas = FigureCanvasTkAgg(fig, master=root)
    canvas.draw()
    canvas.get_tk_widget().pack()

    root.mainloop()


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
                           command=lambda: launch_debate_window(selection_root, filename, selected_num_questions.get(), selected_strategy.get(), root),
                           width=20, 
                           height=2)
    start_button.pack(pady=10)

    selection_root.mainloop()


def launch_debate_window(selection_root, filename, nb, strategy, root):
    root.destroy()
    selection_root.destroy()
    debate_root = tk.Tk()
    app = DebateApp(debate_root, filename, nb, strategy)
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
            with open('user_db.json', 'r') as file:
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
            with open('user_db.json', 'r') as f1:
                log_dict = json.load(f1)
            if username not in log_dict.keys():
                log_dict[username] = password
                with open('user_db.json', 'w') as f2:
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