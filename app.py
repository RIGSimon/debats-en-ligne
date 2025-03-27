import json
import tkinter as tk
from tkinter import filedialog, messagebox
from graph import DebateGraph


class DebateApp:
    def __init__(self, root, filename):
        self.root = root
        self.root.title("Comparaison d'arguments")
        self.root.geometry("600x500") 
        self.score = 0

        graph = DebateGraph(filename)

        self.graph = graph.G.copy()
        self.order = graph.order.copy()
        self.index = 0 
        
        self.label = tk.Label(self.root, 
                              text=self.graph.nodes[graph.main_arg].get("text", graph.main_arg), 
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
        
        # Pour voir la comparaison precedente
        self.back_button = tk.Button(self.root, 
                                     text="↩️",
                                     command=lambda: self.next_step(self.index - 1), 
                                     width=2, 
                                     height=2) 
        self.back_button.place(x=10, y=10)  # Position en haut à gauche

        self.arg1_button.pack(pady=5, fill="both", expand=True)
        self.arg2_button.pack(pady=5, fill="both", expand=True)
        self.unable_button.pack(pady=10)
        
        self.next_step(None)  # Afficher la première paire
    

    def update_score(self, node) :
        cur_node = node
        prev_node = list(self.graph.predecessors(cur_node))[0]
        score = 1
        done = False
        while not done :
            if int(self.graph.get_edge_data(prev_node, cur_node)["relation"]) == 0.0 :
                done = True
                break
            score = score * int(self.graph.get_edge_data(prev_node, cur_node)["relation"])
            cur_node = list(self.graph.predecessors(cur_node))[0]
            prev_node = list(self.graph.predecessors(prev_node))[0]
        self.score += score

    def next_step(self, choice):
        """
        Passe à la paire suivante d'arguments
        """

        if self.index >= len(self.order) - 1:
            self.label.config(text="Fin du débat")
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
            node1 = self.order[self.index]
            node2 = self.order[self.index + 1]
            
            
            self.arg1_button.config(text=self.graph.nodes[node1].get("text", node1), command=lambda: [self.next_step(None), self.update_score(node1)])
            self.arg2_button.config(text=self.graph.nodes[node2].get("text", node2), command=lambda: [self.next_step(None), self.update_score(node2)])
            
            self.index += 2  # Passer à la prochaine paire
        
        else:
            if choice >= 0:
                node1 = self.order[self.index - 1]
                node2 = self.order[self.index]
                
                self.arg1_button.config(text=self.graph.nodes[node1].get("text", node1))
                self.arg2_button.config(text=self.graph.nodes[node2].get("text", node2))
                
                self.index -= 2

def analyse_window(score) :
    root = tk.Tk()
    root.title("Résultats")

    if score >= 1 :
        label = tk.Label(root, text="Vous êtes en faveur de l'argument principal !")
        label.pack(padx=10, pady=10)
    else :
        label = tk.Label(root, text="Vous êtes opposé à l'argument principal !")
        label.pack(padx=10, pady=0)
    root.mainloop()
    return


def launch_home_window():
    """
    Page d'accueil
    """

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
    """
    Page principale
    """    

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
    """
    Page de selection d'une action
    """

    selection_root = tk.Tk()
    selection_root.title("Débat")
    selection_root.geometry("400x300")
    
    label = tk.Label(selection_root, 
                     text="Fichier sélectionné :\n" + filename, 
                     font=("Arial", 10), wraplength=380, 
                     justify="center")
    label.pack(pady=10)
    
    start_button = tk.Button(selection_root, 
                             text="Lancer le débat", 
                             command=lambda: launch_debate_window(selection_root, filename), 
                             width=20, 
                             height=2)
    start_button.pack(pady=10)
    
    results_button = tk.Button(selection_root, 
                               text="Voir les résultats", 
                               width=20, 
                               height=2)
    results_button.pack(pady=10)
    
    selection_root.mainloop()


def launch_debate_window(selection_root, filename):
    """
    Page de lancement du debat
    """

    selection_root.destroy()
    debate_root = tk.Tk()
    app = DebateApp(debate_root, filename)
    debate_root.mainloop()


def launch_login_window(root):
    """
    Page de connexion
    """

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

        #Vérification du login dans user_db.json
        if username and password: # Tout est valide sauf la chaine vide (a changer)
            with open('user_db.json', 'r') as file :
                user_db = json.load(file)
                #print(user_db)
            if username in user_db.keys() and user_db[username] == password :
                login_root.destroy()
                root.destroy()
                launch_main_window()
            else :
                messagebox.showerror("Erreur", "Nom d'utilisateur/Mot de passe incorrect")
            
        else:
            messagebox.showerror("Erreur", "Veuillez remplir tous les champs.")
    
    login_button = tk.Button(login_root, 
                             text="Se connecter", 
                             command=lambda: validate_login(root))
    login_button.pack(pady=10)


def launch_register_window(root):
    """
    Page d'inscription
    """

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

        if username and password and repassword and (password == repassword): # Tout est valide sauf la chaine vide (a changer)
            with open('user_db.json', 'r') as f1:
                log_dict = json.load(f1)
            #Vérification du nom d'utilisateur disponible (mais possible d'avoir le même password qu'un autre utilisateur)
            if username not in log_dict.keys() :
                log_dict[username] = password
                with open('user_db.json', 'w') as f2:
                    json.dump(log_dict, f2)
                login_root.destroy()
                root.destroy()
            

                launch_main_window()
            else : 
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