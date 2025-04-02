import json
import tkinter as tk
from tkinter import filedialog, messagebox
from graph import DebateGraph

class DebateApp:
    def __init__(self, root, filename, nb, strategy="random"):
        self.root = root
        self.root.title("Comparaison d'arguments")
        self.root.geometry("600x500") 
        self.score = 0

        graph = DebateGraph(filename, nb, strategy)

        self.graph = graph.G.copy()
        self.order = graph.order.copy()
        self.index = -2
        
        # Add settings menu
        menubar = tk.Menu(root)
        settings_menu = tk.Menu(menubar, tearoff=0)
        self.show_node_info = tk.BooleanVar(value=False)  
        settings_menu.add_checkbutton(label="Afficher les infos des nœuds", 
                            variable=self.show_node_info, 
                            command=self.toggle_node_info)
        menubar.add_cascade(label="Paramètres", menu=settings_menu)
        root.config(menu=menubar)
        
        self.label = tk.Label(self.root, 
                            text=self._format_node_text(graph.main_arg, graph.nodes[graph.main_arg].get("text", graph.main_arg)), 
                            font=("Arial", 14))
        self.label.pack(pady=10)
        
        
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

        self.arg1_button.pack(pady=5, fill="both", expand=True)
        self.arg2_button.pack(pady=5, fill="both", expand=True)
        self.unable_button.pack(pady=10)
        
        self.next_step(None)  # Afficher la première paire
    
    def _format_node_text(self, node_id, text):
        """Format node text with level info if setting is enabled"""
        if not self.show_node_info.get():
            return text
        
        level = self.graph.nodes[node_id].get('level', '?')
        return f"{text}\nNiveau: {level}"
    
    def _set_button_colors(self, button, node_id):
        """Set button color based on relation if show_info is active"""
        if not self.show_node_info.get():
            button.config(bg="light grey")  # Default color
            return
        
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
                    button.config(bg="light grey")
                
    def toggle_node_info(self):
        """Toggle node info display setting"""
        val = self.show_node_info.get()
        if (val == False):
            self.show_node_info.set(True)  
        else: 
            self.show_node_info.set(False)  
        print(f"Toggle node info - New value: {val}")  # Debug
        self._refresh_display()
    
    def _refresh_display(self):
        print('refresh', self.index)
        """Refresh all displayed text and colors with current settings"""
        # Refresh main argument
        main_arg = self.order[0] if self.order else ""
        if main_arg in self.graph.nodes:
            self.label.config(text=self._format_node_text(
                main_arg, 
                self.graph.nodes[main_arg].get("text", main_arg)
            ))
        
        # Refresh current buttons
        if self.index < len(self.order) - 1:
            #index = self.index-2 # (next step adds 2)
            node1 = self.order[self.index]
            node2 = self.order[self.index+1]
            
            self.arg1_button.config(text=self._format_node_text(node1, self.graph.nodes[node1].get("text", node1)))
            self.arg2_button.config(text=self._format_node_text(node2, self.graph.nodes[node2].get("text", node2)))
            
            self._set_button_colors(self.arg1_button, node1)
            self._set_button_colors(self.arg2_button, node2)



    def update_score(self, node):
        cur_node = node
        prev_node = list(self.graph.predecessors(cur_node))[0]
        score = 1
        done = False
        while not done:
            if int(self.graph.get_edge_data(prev_node, cur_node)["relation"]) == 0.0:
                done = True
                break
            score = score * int(self.graph.get_edge_data(prev_node, cur_node)["relation"])
            cur_node = list(self.graph.predecessors(cur_node))[0]
            prev_node = list(self.graph.predecessors(prev_node))[0]
        self.score += score


    def next_step(self, choice):
        print('next', self.index)
        if self.index >= len(self.order) - 1:
            self.label.config(text="Fin du débat")
            self.back_button.pack_forget()
            self.arg1_button.pack_forget()
            self.arg2_button.pack_forget()
            self.unable_button.pack_forget()
            
            arg_button = tk.Button(self.root, 
                                text="Analyse des résultats",  
                                command=lambda: analyse_window(self.score),
                                wraplength=500, 
                                justify="left")
            arg_button.pack(pady=5, expand=True)
            return
        
        if choice == None:
            self.index += 2
            self._refresh_display()
            
        else:
            if choice >= 0:
                if self.index >= 2:
                    self.index -= 2
                    self._refresh_display()
                
                

def analyse_window(score):
    root = tk.Tk()
    root.title("Résultats")

    if score >= 1:
        label = tk.Label(root, text="Vous êtes en faveur de l'argument principal !")
    else:
        label = tk.Label(root, text="Vous êtes opposé à l'argument principal !")
    label.pack(padx=10, pady=10)
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


def launch_main_window():
    root = tk.Tk()
    root.title("Page principale")
    root.geometry("400x300")
    
    label = tk.Label(root, 
                    text="Bienvenue dans l'application de débat", 
                    font=("Arial", 14))
    label.pack(pady=20)
    
    load_button = tk.Button(root, 
                          text="Charger un débat", 
                          command=lambda: load_debate_file(), 
                          width=20, 
                          height=2)
    load_button.pack(pady=10)
    
    root.mainloop()


def launch_selection_window(filename):
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
                    text="Sélectionner le nombre de questions", 
                    font=("Arial", 14), wraplength=380, 
                    justify="center")
    titre.pack(pady=10)

    num_questions_menu = tk.OptionMenu(selection_root, 
                                     selected_num_questions,
                                     *options)
    num_questions_menu.pack(pady=10)

    # Strategy selection
    strategies = ["random", "BFS", "DFS", "priority"]
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
                           command=lambda: launch_debate_window(selection_root, filename, selected_num_questions.get(), selected_strategy.get()),
                           width=20, 
                           height=2)
    start_button.pack(pady=10)

    selection_root.mainloop()


def launch_debate_window(selection_root, filename, nb, strategy):
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
        username = username_entry.get()
        password = password_entry.get()

        if username and password:
            with open('user_db.json', 'r') as file:
                user_db = json.load(file)
            if username in user_db.keys() and user_db[username] == password:
                login_root.destroy()
                root.destroy()
                launch_main_window()
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
                launch_main_window()
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


def load_debate_file():
    file_path = filedialog.askopenfilename(title="Sélectionner un fichier de débat", filetypes=[("Fichiers JSON", "*.json")])
    if file_path:
        launch_selection_window(file_path)


if __name__ == '__main__':
    launch_home_window()